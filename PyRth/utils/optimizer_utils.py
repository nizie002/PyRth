import numpy as np
from scipy.integrate import cumulative_trapezoid


def ext_weighted_diff(x_vals, y_1, y_2, weight):
    return np.sqrt(np.trapz(((y_1 - y_2) * weight) ** 2, x=x_vals))


def weighted_diff_sum(x_vals, y_1, y_2, weight):
    return np.sqrt(np.sum(((y_1 - y_2) * weight) ** 2))


def weighted_diff(x_vals, y_1, y_2):
    return np.sqrt(np.trapz((y_1 - y_2) ** 2, x=x_vals))


def log_log_weighted_diff(x_vals, y_1, y_2):
    safe = (y_1 > 0) & (y_2 > 0)
    y1_filt = y_1[safe]
    y2_filt = y_2[safe]
    x_filt = x_vals[safe]
    return np.sqrt(np.trapz((np.log(y1_filt) - np.log(y2_filt)) ** 2, x=x_filt))


def weighted_relativ_diff(x_vals, y_1, y_2):
    return np.sqrt(np.trapz(((y_1 - y_2) / (y_1 + y_2)) ** 2, x=x_vals))


def l2_norm_time_const(theo_x, theo_y, compare_x, compare_y, sum_given=False):
    sum_theo_y = cumulative_trapezoid(theo_y, x=theo_x, initial=0.0)
    if not sum_given:
        sum_compare_y = cumulative_trapezoid(compare_y, x=compare_x, initial=0.0)
    else:
        sum_compare_y = compare_y
    dex1 = np.searchsorted(theo_x, compare_x[0])
    dex2 = np.searchsorted(theo_x, compare_x[-1])
    theo_x_small = theo_x[dex1:dex2]
    sum_compare_y_fine = np.interp(theo_x_small, compare_x, sum_compare_y)
    return np.sqrt(
        np.trapz((sum_compare_y_fine - sum_theo_y[dex1:dex2]) ** 2, x=theo_x_small)
    )


def norm_structure(theo_x, theo_y, compare_x, compare_y):
    theo_x = theo_x[1:]
    theo_y = theo_y[1:]
    min_res = theo_x[0]
    max_res = compare_x[-1]
    res_fine = np.linspace(min_res, max_res, int(1e6))
    theo_y_fine = np.interp(res_fine, theo_x, theo_y)
    compare_y_fine = np.interp(res_fine, compare_x, compare_y)
    theo_y_fine = np.log(theo_y_fine)
    compare_y_fine = np.log(compare_y_fine)
    return np.trapz(np.abs(compare_y_fine - theo_y_fine), x=res_fine)
