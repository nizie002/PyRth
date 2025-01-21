import numpy as np
import scipy.optimize as opt
import scipy.integrate as sin
import functools
import warnings
import cmath as cm
import logging


from . import transient_utils as utl

logger = logging.getLogger("PyRthLogger")

Nfeval = 1


def cm_tanh(arr):
    for i, val in enumerate(arr):
        arr[i] = cm.tanh(val)
    return arr


@functools.lru_cache(maxsize=80)
def give_rung_imp(res, cap):

    global complex_time

    gamma_l = np.sqrt(res * cap * complex_time)
    z_null = np.sqrt(res / (cap * complex_time))

    tanh_gamma_l = cm_tanh(gamma_l)

    return (z_null, tanh_gamma_l)


def l2_norm_time_const(theo_x, theo_y, compare_x, compare_y, sum_given=False):

    sum_theo_y = sin.cumulative_trapezoid(theo_y, x=theo_x, initial=0.0)

    if not sum_given:
        sum_compare_y = sin.cumulative_trapezoid(compare_y, x=compare_x, initial=0.0)
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


def struc_to_time_const(theo_log_time, delta, resistances, capacitances):

    global complex_time
    global delta_in_global_complex_time

    if not "complex_time" in globals():
        complex_time = -(complex(np.cos(delta), np.sin(delta))) * np.exp(-theo_log_time)
        delta_in_global_complex_time = delta
    else:
        if delta_in_global_complex_time != delta:
            complex_time = -(complex(np.cos(delta), np.sin(delta))) * np.exp(
                -theo_log_time
            )
            delta_in_global_complex_time = delta
            give_rung_imp.cache_clear()

    n = len(capacitances)
    last_z = 0.0

    for i in np.arange(n - 1, -1, -1):

        z_null, tanh_gamma_l = give_rung_imp(resistances[i], capacitances[i])

        z_result = (
            z_null * (last_z + tanh_gamma_l * z_null) / (last_z * tanh_gamma_l + z_null)
        )

        last_z = z_result

    global Nfeval
    Nfeval += 1

    return np.imag(z_result) / np.pi


def time_const_to_imp(theo_log_time, time_const):

    len_t = theo_log_time.size
    weight = utl.weight_z(theo_log_time)
    max_ar = np.argmax(weight)

    imp_deriv_long = np.convolve(time_const, utl.weight_z(theo_log_time), "full") * (
        theo_log_time[1] - theo_log_time[0]
    )

    fin = len_t - max_ar - 1
    start = max_ar
    imp_deriv = imp_deriv_long[start:-fin]

    imp = sin.cumulative_trapezoid(imp_deriv, theo_log_time, initial=0.0)

    return imp_deriv, imp


def struc_params_to_func(number, resistances, capacities):

    N = len(resistances)

    sum_res = np.zeros(N + 1)
    sum_cap = np.zeros(N + 1)

    for i in range(N):
        sum_res[i + 1] = sum_res[i] + resistances[i]
        sum_cap[i + 1] = sum_cap[i] + capacities[i]

    sum_res_int = np.linspace(sum_res[0], sum_res[-1], number)

    for mid_v in sum_res[1:-1]:
        sum_res_int = np.insert(sum_res_int, sum_res_int.searchsorted(mid_v), mid_v)

    sum_cap_int = np.interp(sum_res_int, sum_res, sum_cap)

    return sum_res_int, sum_cap_int


def opt_struc_params_to_func(args, r_org):

    args1 = np.sort(args[: len(args) // 2], kind="stable")
    args2 = np.sort(args[len(args) // 2 :], kind="stable")

    c_vals = np.interp(r_org, args1, np.exp(args2))

    return c_vals


def ext_weighted_diff(x_vals, y_1, y_2, weight):

    return np.sqrt(np.trapz(((y_1 - y_2) * weight) ** 2, x=x_vals))


def weighted_diff_sum(x_vals, y_1, y_2, weight):

    return np.sqrt(np.sum(((y_1 - y_2) * weight) ** 2))


def weighted_diff(x_vals, y_1, y_2):

    return np.sqrt(np.trapz((y_1 - y_2) ** 2, x=x_vals))


def log_log_weighted_diff(x_vals, y_1, y_2):
    safe_indices = np.where((y_1 > 0) & (y_2 > 0))
    y_1_filtered = y_1[safe_indices]
    y_2_filtered = y_2[safe_indices]
    x_vals_filtered = x_vals[safe_indices]

    if len(y_1_filtered) == 0 or len(y_2_filtered) == 0:
        logger.warning(
            "Warning: y_1 or y_2 contains no values greater than zero. This will cause issues with the logarithmic operation."
        )
        return np.nan

    return np.sqrt(
        np.trapz((np.log(y_1_filtered) - np.log(y_2_filtered)) ** 2, x=x_vals_filtered)
    )


def weighted_relativ_diff(x_vals, y_1, y_2):

    return np.sqrt(np.trapz(((y_1 - y_2) / (y_1 + y_2)) ** 2, x=x_vals))


def to_minimize_struc(arguments, r_org, c_org):

    c_2 = opt_struc_params_to_func(arguments, r_org)

    return weighted_diff(r_org, c_org, np.log(c_2))


def struc_x_sample(x, y, N):

    new_x = np.linspace(x[0], 0.03 * x[0] + 0.97 * x[-1], N, endpoint=True)

    new_y = np.interp(new_x, x, y)

    return new_x, new_y


def generate_init_vals(N, x, y):

    npts = len(x)
    arc = 0.0
    for k in range(0, npts - 1):
        arc = arc + np.sqrt((x[k] - x[k + 1]) ** 2 + (y[k] - y[k + 1]) ** 2)

    parts = (arc / (N - 1)) * 0.99
    next_stage = parts
    counter = 0

    init_stages_R = np.zeros(N)
    init_stages_C = np.zeros(N)

    init_stages_R[0] = x[0]
    init_stages_C[0] = y[0]

    segm = 0
    for k in range(0, npts - 1):
        increm = np.sqrt((x[k] - x[k + 1]) ** 2 + (y[k] - y[k + 1]) ** 2)
        segm += increm

        if segm > next_stage:
            delta = segm - next_stage
            next_stage += parts
            while delta > 0 and counter < N - 1:

                fraction = delta / increm
                counter += 1

                init_stages_R[counter] = x[k] + fraction * np.abs((x[k + 1] - x[k]))
                init_stages_C[counter] = y[k] + fraction * np.abs((y[k + 1] - y[k]))

                delta -= parts

    return init_stages_R, init_stages_C


def optimize_theo_struc(res_l, cap_l, N):

    cut_frac = 0.05  ## 0.03

    maxidx = np.searchsorted(res_l, cut_frac * res_l[0] + (1.0 - cut_frac) * res_l[-1])

    res = res_l[:maxidx]
    cap = cap_l[:maxidx]

    cap_log = np.log(cap)

    N_fine = int(1e4)
    res_fine = np.linspace(res[0], res[-1], N_fine)
    cap_log_fine = np.interp(res_fine, res, cap_log)

    r_init, c_init_log = generate_init_vals(N, res, cap_log)

    c_init = np.exp(c_init_log)

    init_vect = [*r_init, *c_init_log]

    bounds_res = [(res[0], res_l[-1])] * (N)
    bounds_cap = [(cap_log[0], cap_log[-1])] * (N)

    opt_result = opt.minimize(
        to_minimize_struc,
        init_vect,
        args=(res_fine, cap_log_fine),
        method="Powell",
        bounds=[*bounds_res, *bounds_cap],
        options={"ftol": 0.0001},
    )

    opt_res = np.sort(opt_result.x[:N], kind="stable")
    opt_cap = np.exp(np.sort(opt_result.x[N:], kind="stable"))

    opt_res[-1] = res_l[-1]

    struc_marker = (opt_res, opt_cap, r_init, c_init)

    return struc_marker, opt_result


def sort_and_lim_diff(arr):

    arr = np.sort(arr, kind="stable")

    arr[1:] = arr[1:] - arr[:-1]

    for i in range(len(arr)):
        if arr[i] < 1e-10:
            arr[i] = 1e-10  # avoid small differences that break the nummeric

    return arr


def to_minimize_imp(
    arguments,
    theo_log_time,
    impedance,
    log_time,
    global_weight,
    N,
    theo_delta,
):

    opt_res = sort_and_lim_diff(arguments[:N])
    opt_cap = sort_and_lim_diff(np.exp(arguments[N:]))

    theo_time_const = struc_to_time_const(theo_log_time, theo_delta, opt_res, opt_cap)

    theo_imp_deriv, theo_impedance = time_const_to_imp(theo_log_time, theo_time_const)

    theo_impedance_int = np.interp(log_time, theo_log_time, theo_impedance)

    global diff
    global diffloglog
    diff = weighted_diff(log_time, theo_impedance_int, impedance)
    diffloglog = log_log_weighted_diff(log_time, theo_impedance_int, impedance)

    return diff


def optimize_to_imp(
    res_init,
    cap_init,
    theo_log_time,
    impedance,
    log_time,
    global_weight,
    theo_delta,
    opt_method="COBYLA",
):

    global complex_time
    global delta_in_global_complex_time
    complex_time = -(complex(np.cos(theo_delta), np.sin(theo_delta))) * np.exp(
        -theo_log_time
    )
    delta_in_global_complex_time = theo_delta

    N = len(res_init)

    cap_init_log = np.log(cap_init)

    cap_min = np.amin(cap_init_log)
    cap_max = np.amax(cap_init_log)

    bounds_r = [(1e-4, 1.3 * impedance[-1])]  # no upper bound
    bounds_c = [
        (cap_min - 0.35 * (cap_max - cap_min), cap_max + 2.0 * (cap_max - cap_min))
    ]

    exceed_counter = 0
    for i in range(N - 1, -1, -1):
        if res_init[i] > bounds_r[0][1]:
            res_init[i] = bounds_r[0][1] - exceed_counter * (
                bounds_r[0][1] - bounds_r[0][0]
            ) / (N - 1)
            exceed_counter += 1

    init_vect = [*np.sort(res_init), *np.sort(cap_init_log)]

    global results_obj
    global results_res
    global results_cap

    results_obj = np.empty(0)
    results_res = np.empty(0)
    results_cap = np.empty(0)

    def callbackF(arguments):
        global Nfeval
        global diff
        global diffloglog
        global results_obj
        global results_res
        global results_cap

        opt_res = arguments[:N]
        opt_cap = np.exp(arguments[N:])

        opt_res = np.sort(opt_res, kind="stable")
        opt_cap = np.sort(opt_cap, kind="stable")

        results_obj = np.append(results_obj, diff)
        results_res = np.append(results_res, [opt_res])
        results_cap = np.append(results_cap, [opt_cap])

        print(
            "\r #function eval:",
            format(Nfeval, ".0f"),
            "\t objective:",
            format(diff, ".4f"),
            end="",
            flush=True,
        )

    global Nfeval
    Nfeval = 0

    if opt_method == "Powell":
        print("employing optimization method: Powell\n")
        opt_result = opt.minimize(
            to_minimize_imp,
            init_vect,
            args=(
                theo_log_time,
                impedance,
                log_time,
                global_weight,
                N,
                theo_delta,
            ),
            callback=callbackF,
            method="Powell",
            bounds=[*(bounds_r * N), *(bounds_c * N)],
            options={"ftol": 0.001},
        )

    if opt_method == "COBYLA":
        print("employing optimization method: COBYLA")

        rl = bounds_r[0][0]
        ru = bounds_r[0][1]
        cl = bounds_c[0][0]
        cu = bounds_c[0][1]

        cons = []
        cons.append({"type": "ineq", "fun": lambda x, lb=rl: x[0] - lb})
        cons.append({"type": "ineq", "fun": lambda x, ub=ru, num=N: ub - x[N - 1]})
        cons.append({"type": "ineq", "fun": lambda x, lb=cl, num=N: x[N] - lb})
        cons.append({"type": "ineq", "fun": lambda x, ub=cu: ub - x[-1]})
        for factor in range(N - 1):
            l = {"type": "ineq", "fun": lambda x, i=factor: x[i + 1] - x[i]}
            u = {
                "type": "ineq",
                "fun": lambda x, i=factor, num=N: x[i + 1 + num] - x[i + num],
            }
            cons.append(l)
            cons.append(u)

        opt_result = opt.minimize(
            to_minimize_imp,
            init_vect,
            args=(
                theo_log_time,
                impedance,
                log_time,
                global_weight,
                N,
                theo_delta,
            ),
            method="COBYLA",
            constraints=cons,
            tol=0.0001,
            options={"maxiter": 10000, "disp": True, "catol": 1},
        )

    opt_res = opt_result.x[:N]

    opt_cap = np.exp(opt_result.x[N:])

    opt_res = np.sort(opt_res, kind="stable")
    opt_cap = np.sort(opt_cap, kind="stable")

    results_obj = np.append(results_obj, diff)
    results_res = np.append(results_res, [opt_res])
    results_cap = np.append(results_cap, [opt_cap])

    results_res = np.reshape(results_res, (len(results_obj), N))
    results_cap = np.reshape(results_cap, (len(results_obj), N))

    min_at = np.argmin(results_obj)

    return results_res[min_at], results_cap[min_at], opt_result
