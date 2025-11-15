"""Utility helpers shared by PyRth's transient-processing pipeline.

The functions below cover lightweight numerical utilities (Gaussian kernels,
weighting functions), temperature/impedance conversions, and convenience
wrappers that keep the structure-function modules small and readable.
"""

import logging
import time

import numpy as np
import numpy.polynomial.polynomial as poly
import scipy.interpolate as interp
from scipy.integrate import cumulative_trapezoid
import numba

logger = logging.getLogger("PyRthLogger")


def get_iterator(value):
    """Return an iterator constructed from ``value``.
    """
    if callable(value):
        # Assume it's a generator function; call it to get a generator (lazy)
        return value()
    elif hasattr(value, "__iter__") and not isinstance(value, str):
        return iter(value)
    else:
        raise ValueError(
            "Value for an iterable keyword must be an iterable or generator function"
        )


def numba_preloader():
    """JIT-compile a tiny Numba kernel so later imports incur less latency.

    ``numba`` tends to pay the compilation cost on the first decorated call.
    Running this no-op function at module import primes the cache so that
    latency-sensitive routines do not surprise CLI users.
    """
    # This is a workaround to make numba work faster on the first function call
    # by preloading the JIT compiler with a dummy function.

    @numba.njit
    def dummy():
        pass

    dummy()


def format_time(seconds):
    """Format *seconds* with the most suitable SI unit for logging.
    """
    units = [("s", 1), ("ms", 1e3), ("us", 1e6), ("ns", 1e9)]
    for unit, factor in units:
        if seconds * factor >= 1:
            break
    return f"{seconds * factor:.3f} {unit}"


def timer_decorator(func):
    """Decorator that logs the minimum runtime of the wrapped function.

    The wrapper currently performs a single measurement but keeps the loop so
    future callers can increase ``reps`` without touching call sites.
    """
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
    """Return the analytical weighting kernel used for structure functions.

    The kernel corresponds to the derivative of temperature with respect to
    logarithmic time and serves as the convolution window in ``time_const_to_imp``.
    """
    return np.exp(x - np.exp(x))


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
    """Return the unit-variance Gaussian evaluated at ``x``.
    """
    return np.exp(-x * x / 2.0)


def generalized_gaussian(x, a, sigma, mu):
    """Return a scaled Gaussian with amplitude ``a``, width ``sigma``, and offset ``mu``.
    """
    return a * np.exp(-0.5 * ((x - mu) / sigma) ** 2)


def volt_to_temp_t3ster(dig, lsb, uref, kfac, span=(0.0, 150.0)):
    """Convert T3Ster ADC readings to temperatures using calibration arrays.
    """

    ndig = 4095.0  # number of digital values in t3ster

    u0 = uref - ndig / 2.0 * lsb

    vlt = dig * lsb + u0

    if len(kfac) == 2:
        tmp = (vlt - kfac[0]) / kfac[1]
    elif len(kfac) == 3:
        tmpint = np.linspace(span[0], span[1], num=int(1e5))
        vltint = poly.polyval(tmpint, kfac)

        tmp = np.interp(vlt, np.flip(vltint), np.flip(tmpint))
    else:
        raise ValueError("kfac must have length 2 or 3")

    return tmp, vlt


def volt_to_temp(vlt, calib, kfac_fit_deg):
    """Convert voltages to temperatures via a polynomial fit of ``calib``.
    """
    voltages = calib[:, 1]
    temperatures = calib[:, 0]
    coeffs = np.polyfit(voltages, temperatures, kfac_fit_deg)
    tmp = np.polyval(coeffs, vlt)
    return tmp


def tmp_to_z(
    tmp, t_zero, power_step, optical_power, power_scale_factor, is_heating=False
):
    """Translate a temperature transient into thermal impedance Zth.
    """

    power_step = abs(power_step)

    z = (t_zero - tmp) / ((power_step - optical_power) * power_scale_factor)

    if is_heating:
        z = -z

    return z


def get_early_zth(module):
    """Interpolate ``module.impedance`` to obtain Zth at 100 µs.

    The helper mirrors the reference-time sampling used when stitching
    bootstrap runs, ensuring extrapolated transients start from a comparable
    absolute impedance.
    """
    f = interp.interp1d(module.log_time, module.impedance)

    # Get the impedance value at np.log(1e-4)
    return f(np.log(1e-4))


def extrapolate_temperature(
    time_raw, temp_raw, lower_fit_index, upper_fit_index, additional_decades=4
):
    """
    Extrapolate temperature data using polynomial fitting.
    """

    total_decades = np.log10(time_raw[-1]) - np.log10(time_raw[0])

    extrapolation_decades = np.log10(time_raw[lower_fit_index]) - np.log10(
        time_raw[0] / (10**additional_decades)
    )

    fit_add_extrapolation = int(len(time_raw) * (extrapolation_decades / total_decades))

    time_combined = np.logspace(
        np.log10(time_raw[0] / (10**additional_decades)),
        np.log10(time_raw[lower_fit_index]),
        num=fit_add_extrapolation,
        endpoint=False,
    )

    expl_ft_prm = poly.polyfit(
        np.sqrt(time_raw[lower_fit_index:upper_fit_index]),
        temp_raw[lower_fit_index:upper_fit_index],
        1,
    )

    temp_combined = poly.polyval(np.sqrt(time_combined), expl_ft_prm)

    t_null = poly.polyval(0.0, expl_ft_prm)

    time_var = np.append(time_combined, time_raw[lower_fit_index:])
    temperature = np.concatenate((temp_combined, temp_raw[lower_fit_index:]))

    return time_var, temperature, expl_ft_prm, t_null