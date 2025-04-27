import numpy as np
import scipy.interpolate as interp
import numpy.polynomial.polynomial as poly
import logging
import time
import numba
from scipy.integrate import cumulative_trapezoid

logger = logging.getLogger("PyRthLogger")


def get_iterator(value):
    if callable(value):
        # Assume it's a generator function; call it to get a generator (lazy)
        return value()
    elif hasattr(value, "__iter__") and not isinstance(value, str):
        return iter(value)
    else:
        raise ValueError(
            f"Value for an iterable keyword must be an iterable or generator function"
        )


def numba_preloader():
    # This is a workaround to make numba work faster on the first function call
    # by preloading the JIT compiler with a dummy function.

    @numba.njit
    def dummy():
        pass

    dummy()


def format_time(seconds):
    units = [("s", 1), ("ms", 1e3), ("us", 1e6), ("ns", 1e9)]
    for unit, factor in units:
        if seconds * factor >= 1:
            break
    return f"{seconds * factor:.3f} {unit}"


def timer_decorator(func):
    def wrapper(*args, **kwargs):
        min_time = float("inf")
        reps = 1
        logger.info("\n" + func.__name__ + " is running")
        for _ in range(reps):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            end = time.perf_counter()
            min_time = min(min_time, end - start)
        formatted_time = format_time(min_time)
        logger.info(
            f"{func.__name__} took a minimum of {formatted_time} over {reps} runs\n"
        )
        return result

    return wrapper


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


def time_const_to_imp(log_time, time_const):
    """
    Convert a discrete time-constant distribution to time-domain impedance.
    Returns the derivative and the integrated impedance.
    """
    delta_t = log_time[1] - log_time[0]
    log_time_weight = np.arange(-7, 7 + delta_t, delta_t)
    weight = weight_z(log_time_weight)

    imp_deriv_long = np.convolve(time_const, weight, mode="full")
    start = np.argmax(weight)
    fin = start + log_time.size
    imp_deriv = imp_deriv_long[start:fin]
    imp = cumulative_trapezoid(imp_deriv, log_time, initial=0.0)

    return imp_deriv, imp


def gaussian(x):
    return np.exp(-x * x / 2.0)


def generalized_gaussian(x, a, sigma, mu):
    return a * np.exp(-0.5 * ((x - mu) / sigma) ** 2)


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
    time_raw, temp_raw, lower_fit_index, upper_fit_index, additional_decades=4
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
    extrapolation_decades = np.log10(time_raw[lower_fit_index]) - np.log10(
        time_raw[0] / (10**additional_decades)
    )

    # Calculate the number of points for the extrapolation
    fit_add_extrapolation = int(len(time_raw) * (extrapolation_decades / total_decades))

    # Generate evenly distributed points in logarithmic time for the extrapolation range
    time_combined = np.logspace(
        np.log10(time_raw[0] / (10**additional_decades)),
        np.log10(time_raw[lower_fit_index]),
        num=fit_add_extrapolation,
        endpoint=False,
    )

    # Fit the polynomial using the raw data
    expl_ft_prm = poly.polyfit(
        np.sqrt(time_raw[lower_fit_index:upper_fit_index]),
        temp_raw[lower_fit_index:upper_fit_index],
        1,
    )

    # Generate the corresponding temperature points for the combined time points
    temp_combined = poly.polyval(np.sqrt(time_combined), expl_ft_prm)

    # Temperature at time zero
    t_null = poly.polyval(0.0, expl_ft_prm)

    # Combine the extrapolated and raw data
    time = np.append(time_combined, time_raw[lower_fit_index:])
    temperature = np.concatenate((temp_combined, temp_raw[lower_fit_index:]))

    return time, temperature, expl_ft_prm, t_null
