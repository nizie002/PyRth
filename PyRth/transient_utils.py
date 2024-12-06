# -*- coding: utf-8 -*-
"""
Created on Wed Dec 06 10:20:11 2017

@author: Nils Ziegeler
"""

import numpy as np
import scipy.interpolate as interp
import numpy.polynomial.polynomial as poly
import logging

logger = logging.getLogger("PyRthLogger")


def first_nonzero_index(array):
    """Return the index of the first non-zero element of array. If all elements are zero, return -1."""

    fnzi = -1  # first non-zero index
    indices = np.flatnonzero(array)

    if len(indices) > 0:
        fnzi = indices[0]

    return fnzi


def weight_z(x):
    return np.exp(x - np.exp(x))


def weight_z_int(x):
    return 1 - np.exp(-np.exp(x))


def gaussian(x):
    return np.exp(-x * x / 2.0)


def generalized_gaussian(x, a, sigma, mu):
    return a * np.exp(-0.5 * ((x - mu) / sigma) ** 2)


def k_factor_translation(vlt, name):

    data_raw = np.loadtxt(name, dtype="float", skiprows=1)

    x = data_raw[:, 1]
    y = data_raw[:, 2]

    s, m, b = np.polyfit(x, y, 2)

    return s * vlt * vlt + m * vlt + b


def volt_to_temp_TDIM(vlt):
    clb_t_high = 80.3
    clb_v_high = 4.2621e-01
    clb_t_low = 23.4
    clb_v_low = 5.5843e-01
    clb_grd = (clb_t_high - clb_t_low) / (clb_v_high - clb_v_low)

    tmp = (vlt - clb_v_low) * clb_grd + clb_t_low

    return tmp


def volt_to_temp_t3ster(dig, lsb, uref, kfac, span=(0.0, 150.0)):

    ndig = 4095.0  # number of digital values in t3ster

    u0 = uref - ndig / 2.0 * lsb

    vlt = dig * lsb + u0

    if len(kfac) == 2:
        tmp = (vlt - kfac[0]) / kfac[1]
    elif len(kfac) == 3:
        tmpint = np.linspace(span[0], span[1], num=int(1e5))
        vltint = poly.polyval(tmpint, kfac)

        tmp = np.interp(vlt, np.flip(vltint), np.flip(tmpint))

    return tmp, vlt


def volt_to_temp(vlt, calib, kfac_fit_deg):
    voltages = calib[:, 1]
    temperatures = calib[:, 0]
    coeffs = np.polyfit(voltages, temperatures, kfac_fit_deg)
    tmp = np.polyval(coeffs, vlt)
    return tmp


def tmp_to_z(
    tmp, t_zero, power_step, optical_power, power_scale_factor, is_heating="False"
):

    power_step = abs(power_step)

    z = (t_zero - tmp) / ((power_step - optical_power) * power_scale_factor)

    if is_heating:
        z = -z

    return z


def pl_curve(values, ft_prm):

    return ft_prm[1] + ft_prm[0] * np.sqrt(values)


def get_early_zth(module):
    # Create an interpolation function
    f = interp.interp1d(module.log_time, module.impedance)

    # Get the impedance value at np.log(1e-4)
    return f(np.log(1e-4))


def extrapolate_temperature(
    time_raw, temp_raw, lower_fit_limit, upper_fit_limit, additional_decades=4
):
    """
    Extrapolate temperature data using polynomial fitting.

    Parameters:
        time_raw (array): Raw time data.
        temp_raw (array): Raw temperature data.
        lower_fit_limit (int): Lower index for fitting.
        upper_fit_limit (int): Upper index for fitting.
        additional_decades (int): Number of additional decades to add to the time range.

    Returns:
        time (array): Combined time data after extrapolation.
        temperature (array): Combined temperature data after extrapolation.
        expl_ft_prm (array): Polynomial fit parameters.
        t_null (float): Temperature at time zero.
    """
    # Calculate the total number of decades for the entire range
    total_decades = np.log10(time_raw[-1]) - np.log10(time_raw[0])

    # Calculate the number of decades for the extrapolation
    extrapolation_decades = np.log10(time_raw[lower_fit_limit]) - np.log10(
        time_raw[0] / (10**additional_decades)
    )

    # Calculate the number of points for the extrapolation
    fit_add_extrapolation = int(len(time_raw) * (extrapolation_decades / total_decades))

    # Generate evenly distributed points in logarithmic time for the extrapolation range
    time_combined = np.logspace(
        np.log10(time_raw[0] / (10**additional_decades)),
        np.log10(time_raw[lower_fit_limit]),
        num=fit_add_extrapolation,
        endpoint=False,
    )

    # Fit the polynomial using the raw data
    expl_ft_prm = poly.polyfit(
        np.sqrt(time_raw[lower_fit_limit:upper_fit_limit]),
        temp_raw[lower_fit_limit:upper_fit_limit],
        1,
    )

    # Generate the corresponding temperature points for the combined time points
    temp_combined = poly.polyval(np.sqrt(time_combined), expl_ft_prm)

    # Temperature at time zero
    t_null = poly.polyval(0.0, expl_ft_prm)

    # Combine the extrapolated and raw data
    time = np.append(time_combined, time_raw[lower_fit_limit:])
    temperature = np.concatenate((temp_combined, temp_raw[lower_fit_limit:]))

    return time, temperature, expl_ft_prm, t_null
