"""Frequency-domain filter curves for transient processing."""

import numpy as np
from scipy import fftpack


def give_current_filter(name, frequency, filter_range, filter_parameter):
    """Return the selected filter curve in the original frequency ordering."""

    frequency = fftpack.fftshift(frequency)
    if name == "fermi":
        filter_curve = fermi_filter(frequency, filter_range, filter_parameter)
    elif name == "gauss":
        filter_curve = gauss_filter(frequency, filter_range, filter_parameter)
    elif name == "nuttall":
        filter_curve = nuttall_filter(frequency, filter_range)
    elif name == "blackman_nuttall":
        filter_curve = blackman_nuttall_filter(frequency, filter_range)
    elif name == "hann":
        filter_curve = hann_filter(frequency, filter_range)
    elif name == "blackman_harris":
        filter_curve = blackman_harris_filter(frequency, filter_range)
    elif name == "rectangular":
        filter_curve = rectangular_filter(frequency, filter_range)
    else:
        raise ValueError("Filter not recognised. It is currently set to: " + name)

    return fftpack.ifftshift(filter_curve)


def fermi_filter(vrange, bandw, sigm):
    """Build a Fermi-style roll-off filter curve."""

    exp = np.exp(-(np.abs(vrange) - bandw) / sigm)

    return exp / (1 + exp)


def nuttall_filter(vrange, ipt_freq):
    """Build a Nuttall window filter curve within the input frequency bounds."""

    maxfreq = np.abs(ipt_freq)

    idx_l = np.searchsorted(vrange, -maxfreq)
    idx_u = np.searchsorted(vrange, maxfreq)
    idx_max = vrange.size

    n_minus_one = idx_u - idx_l - 1

    index = np.arange(0, n_minus_one + 1)
    a_0 = 0.355768
    a_1 = 0.487396
    a_2 = 0.144232
    a_3 = 0.012604

    filter_curve = (
        a_0
        - a_1 * np.cos(2 * np.pi * index / n_minus_one)
        + a_2 * np.cos(4 * np.pi * index / n_minus_one)
        - a_3 * np.cos(6 * np.pi * index / n_minus_one)
    )

    filter_curve = np.append(np.zeros(idx_l), filter_curve)
    filter_curve = np.append(filter_curve, np.zeros(idx_max - idx_u))

    return filter_curve


def blackman_nuttall_filter(vrange, ipt_freq):
    """Build a Blackman-Nuttall window filter curve within the input frequency bounds."""

    maxfreq = np.abs(ipt_freq)

    idx_l = np.searchsorted(vrange, -maxfreq)
    idx_u = np.searchsorted(vrange, maxfreq)
    idx_max = vrange.size

    n_minus_one = idx_u - idx_l - 1

    index = np.arange(0, n_minus_one + 1)
    a_0 = 0.3635819
    a_1 = 0.4891775
    a_2 = 0.1365995
    a_3 = 0.0106411

    filter_curve = (
        a_0
        - a_1 * np.cos(2 * np.pi * index / n_minus_one)
        + a_2 * np.cos(4 * np.pi * index / n_minus_one)
        - a_3 * np.cos(6 * np.pi * index / n_minus_one)
    )

    filter_curve = np.append(np.zeros(idx_l), filter_curve)
    filter_curve = np.append(filter_curve, np.zeros(idx_max - idx_u))

    return filter_curve


def blackman_harris_filter(vrange, ipt_freq):
    """Build a Blackman-Harris window filter curve within the input frequency bounds."""

    maxfreq = np.abs(ipt_freq)

    idx_l = np.searchsorted(vrange, -maxfreq)
    idx_u = np.searchsorted(vrange, maxfreq)
    idx_max = vrange.size

    n_minus_one = idx_u - idx_l - 1

    index = np.arange(0, n_minus_one + 1)
    a_0 = 0.35875
    a_1 = 0.48829
    a_2 = 0.14128
    a_3 = 0.01168

    filter_curve = (
        a_0
        - a_1 * np.cos(2 * np.pi * index / n_minus_one)
        + a_2 * np.cos(4 * np.pi * index / n_minus_one)
        - a_3 * np.cos(6 * np.pi * index / n_minus_one)
    )

    filter_curve = np.append(np.zeros(idx_l), filter_curve)
    filter_curve = np.append(filter_curve, np.zeros(idx_max - idx_u))

    return filter_curve


def hann_filter(vrange, ipt_freq):
    """Build a Hann window filter curve within the input frequency bounds."""

    maxfreq = np.abs(ipt_freq)

    idx_l = np.searchsorted(vrange, -maxfreq)
    idx_u = np.searchsorted(vrange, maxfreq)
    idx_max = vrange.size

    n_minus_one = idx_u - idx_l - 1

    index = np.arange(0, n_minus_one + 1)

    filter_curve = np.sin(np.pi * index / n_minus_one) * np.sin(
        np.pi * index / n_minus_one
    )

    filter_curve = np.append(np.zeros(idx_l), filter_curve)
    filter_curve = np.append(filter_curve, np.zeros(idx_max - idx_u))

    return filter_curve


def rectangular_filter(vrange, ipt_freq):
    """Build a rectangular window filter curve within the input frequency bounds."""

    maxfreq = np.abs(ipt_freq)

    idx_l = np.searchsorted(vrange, -maxfreq)
    idx_u = np.searchsorted(vrange, maxfreq)
    idx_max = vrange.size

    n_minus_one = idx_u - idx_l - 1

    index = np.arange(0, n_minus_one + 1)

    filter_curve = np.ones(len(index))

    filter_curve = np.append(np.zeros(idx_l), filter_curve)
    filter_curve = np.append(filter_curve, np.zeros(idx_max - idx_u))

    return filter_curve


def gauss_filter(vrange, ipt_freq, sigm):
    """Build a Gaussian window filter curve within the input frequency bounds."""

    maxfreq = np.abs(ipt_freq)

    idx_l = np.searchsorted(vrange, -maxfreq)
    idx_u = np.searchsorted(vrange, maxfreq)
    idx_max = vrange.size

    n_minus_one = idx_u - idx_l - 1

    index = np.arange(0, n_minus_one + 1)

    filter_curve = np.exp(
        -0.5 * ((index - (n_minus_one / 2)) / (sigm * n_minus_one / 2)) ** 2
    )

    filter_curve = np.append(np.zeros(idx_l), filter_curve)
    filter_curve = np.append(filter_curve, np.zeros(idx_max - idx_u))

    return filter_curve
