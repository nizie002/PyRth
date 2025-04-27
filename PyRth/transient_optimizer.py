import numpy as np
import scipy.optimize as opt
import functools
import logging
import cmath as cm
import math
from scipy.integrate import cumulative_trapezoid

from .utils import transient_utils as utl
from .utils import optimizer_utils as optu

logger = logging.getLogger("PyRthLogger")


class TransientOptimizer:
    def __init__(self, parameters=None):
        self.parameters = parameters or {}
        # Replace globals with instance attributes:
        self.complex_time = None
        self.delta_in_global_complex_time = None
        self.eval_count = 0
        self.results_obj = []
        self.results_res = []
        self.results_cap = []

    # ---------------------------
    # Structure Functions
    # ---------------------------

    def cm_tanh(self, arr):
        # Element-wise hyperbolic tangent using math.tanh
        return np.array([cm.tanh(val) for val in arr])

    @functools.lru_cache(maxsize=80)
    def give_rung_imp(self, res, cap):
        # Uses self.complex_time which must be set before calling this method.
        gamma_l = np.sqrt(res * cap * self.complex_time)
        z_null = np.sqrt(res / (cap * self.complex_time))
        tanh_gamma_l = self.cm_tanh(gamma_l)
        return (z_null, tanh_gamma_l)

    def struc_to_time_const(self, theo_log_time, delta, resistances, capacitances):
        # Update instance attributes instead of using globals
        if self.complex_time is None:
            self.complex_time = -complex(math.cos(delta), math.sin(delta)) * np.exp(
                -theo_log_time
            )
            self.delta_in_global_complex_time = delta
        else:
            if self.delta_in_global_complex_time != delta:
                self.complex_time = -complex(math.cos(delta), math.sin(delta)) * np.exp(
                    -theo_log_time
                )
                self.delta_in_global_complex_time = delta
                self.give_rung_imp.cache_clear()

        n = len(capacitances)
        last_z = 0.0
        for i in np.arange(n - 1, -1, -1):
            z_null, tanh_gamma_l = self.give_rung_imp(resistances[i], capacitances[i])
            z_result = (
                z_null
                * (last_z + tanh_gamma_l * z_null)
                / (last_z * tanh_gamma_l + z_null)
            )
            last_z = z_result
        self.eval_count += 1
        return np.imag(z_result) / np.pi

    def struc_params_to_func(self, number, resistances, capacities):
        N = len(resistances)
        sum_res = np.zeros(N + 1)
        sum_cap = np.zeros(N + 1)
        for i in range(N):
            sum_res[i + 1] = sum_res[i] + resistances[i]
            sum_cap[i + 1] = sum_cap[i] + capacities[i]
        sum_res_int = np.linspace(sum_res[0], sum_res[-1], number)
        for mid_v in sum_res[1:-1]:
            sum_res_int = np.insert(
                sum_res_int, np.searchsorted(sum_res_int, mid_v), mid_v
            )
        sum_cap_int = np.interp(sum_res_int, sum_res, sum_cap)
        return sum_res_int, sum_cap_int

    def opt_struc_params_to_func(self, args, r_org):
        args1 = np.sort(args[: len(args) // 2], kind="stable")
        args2 = np.sort(args[len(args) // 2 :], kind="stable")
        c_vals = np.interp(r_org, args1, np.exp(args2))
        return c_vals

    # ---------------------------
    # Structural Optimization Helpers
    # ---------------------------

    def to_minimize_struc(self, arguments, r_org, c_org):
        c_2 = self.opt_struc_params_to_func(arguments, r_org)
        return optu.weighted_diff(r_org, c_org, np.log(c_2))

    def struc_x_sample(self, x, y, N):
        new_x = np.linspace(x[0], 0.03 * x[0] + 0.97 * x[-1], N, endpoint=True)
        new_y = np.interp(new_x, x, y)
        return new_x, new_y

    def generate_init_vals(self, N, x, y):
        npts = len(x)
        arc = 0.0
        for k in range(npts - 1):
            arc += np.sqrt((x[k] - x[k + 1]) ** 2 + (y[k] - y[k + 1]) ** 2)
        parts = (arc / (N - 1)) * 0.99
        next_stage = parts
        counter = 0
        init_stages_R = np.zeros(N)
        init_stages_C = np.zeros(N)
        init_stages_R[0] = x[0]
        init_stages_C[0] = y[0]
        segm = 0
        for k in range(npts - 1):
            increm = np.sqrt((x[k] - x[k + 1]) ** 2 + (y[k] - y[k + 1]) ** 2)
            segm += increm
            if segm > next_stage:
                delta = segm - next_stage
                next_stage += parts
                while delta > 0 and counter < N - 1:
                    fraction = delta / increm
                    counter += 1
                    init_stages_R[counter] = x[k] + fraction * abs(x[k + 1] - x[k])
                    init_stages_C[counter] = y[k] + fraction * abs(y[k + 1] - y[k])
                    delta -= parts
        return init_stages_R, init_stages_C

    def optimize_theo_struc(self, res_l, cap_l, N):
        cut_frac = 0.05
        maxidx = np.searchsorted(
            res_l, cut_frac * res_l[0] + (1.0 - cut_frac) * res_l[-1]
        )
        res = res_l[:maxidx]
        cap = cap_l[:maxidx]
        cap_log = np.log(cap)
        N_fine = int(1e4)
        res_fine = np.linspace(res[0], res[-1], N_fine)
        cap_log_fine = np.interp(res_fine, res, cap_log)
        r_init, c_init_log = self.generate_init_vals(N, res, cap_log)
        c_init = np.exp(c_init_log)
        init_vect = np.concatenate([r_init, c_init_log])
        bounds_res = [(res[0], res_l[-1])] * N
        bounds_cap = [(cap_log[0], cap_log[-1])] * N
        opt_result = opt.minimize(
            self.to_minimize_struc,
            init_vect,
            args=(res_fine, cap_log_fine),
            method="Powell",
            bounds=bounds_res + bounds_cap,
            options={"ftol": 0.0001},
        )
        opt_res = np.sort(opt_result.x[:N], kind="stable")
        opt_cap = np.exp(np.sort(opt_result.x[N:], kind="stable"))
        opt_res[-1] = res_l[-1]
        struc_marker = (opt_res, opt_cap, r_init, c_init)
        return struc_marker, opt_result

    def sort_and_lim_diff(self, arr):
        arr = np.sort(arr, kind="stable")
        arr[1:] = arr[1:] - arr[:-1]
        arr[arr < 1e-10] = 1e-10
        # avoid small differences that break the nummerics
        return arr

    # ---------------------------
    # Impedance Optimization Functions
    # ---------------------------
    def to_minimize_imp(
        self,
        arguments,
        theo_log_time,
        impedance,
        log_time,
        global_weight,
        N,
        theo_delta,
    ):
        opt_res = self.sort_and_lim_diff(arguments[:N])
        opt_cap = self.sort_and_lim_diff(np.exp(arguments[N:]))
        theo_time_const = self.struc_to_time_const(
            theo_log_time, theo_delta, opt_res, opt_cap
        )
        theo_imp_deriv, theo_impedance = self.time_const_to_imp(
            theo_log_time, theo_time_const
        )
        theo_impedance_int = np.interp(log_time, theo_log_time, theo_impedance)
        diff_val = optu.weighted_diff(log_time, theo_impedance_int, impedance)
        # You may also compute diffloglog if needed.
        return diff_val

    def optimize_to_imp(
        self,
        res_init,
        cap_init,
        theo_log_time,
        impedance,
        log_time,
        global_weight,
        theo_delta,
        opt_method="COBYLA",
    ):
        # Set the complex_time based on theo_delta and theo_log_time
        self.complex_time = -complex(
            math.cos(theo_delta), math.sin(theo_delta)
        ) * np.exp(-theo_log_time)
        self.delta_in_global_complex_time = theo_delta
        N = len(res_init)
        cap_init_log = np.log(cap_init)
        cap_min = np.amin(cap_init_log)
        cap_max = np.amax(cap_init_log)
        bounds_r = [(1e-4, 1.3 * impedance[-1])]
        bounds_c = [
            (cap_min - 0.35 * (cap_max - cap_min), cap_max + 2.0 * (cap_max - cap_min))
        ]
        exceed_counter = 0
        res_init_copy = res_init.copy()
        for i in range(N - 1, -1, -1):
            if res_init_copy[i] > bounds_r[0][1]:
                res_init_copy[i] = bounds_r[0][1] - exceed_counter * (
                    bounds_r[0][1] - bounds_r[0][0]
                ) / (N - 1)
                exceed_counter += 1
        init_vect = np.concatenate([np.sort(res_init_copy), np.sort(cap_init_log)])
        self.results_obj = []
        self.results_res = []
        self.results_cap = []

        def callbackF(arguments):
            opt_res = np.sort(arguments[:N], kind="stable")
            opt_cap = np.sort(np.exp(arguments[N:]), kind="stable")
            self.results_obj.append(
                self.to_minimize_imp(
                    arguments,
                    theo_log_time,
                    impedance,
                    log_time,
                    global_weight,
                    N,
                    theo_delta,
                )
            )
            self.results_res.append(opt_res)
            self.results_cap.append(opt_cap)
            logger.info(
                f"#function eval: {self.eval_count} objective: {self.results_obj[-1]:.4f}"
            )
            self.eval_count += 1

        if opt_method == "Powell":
            logger.info("Employing optimization method: Powell")
            opt_result = opt.minimize(
                self.to_minimize_imp,
                init_vect,
                args=(theo_log_time, impedance, log_time, global_weight, N, theo_delta),
                callback=callbackF,
                method="Powell",
                bounds=bounds_r * N + bounds_c * N,
                options={"ftol": 0.001, "maxiter": N * 1000},
            )
        elif opt_method == "COBYLA":
            logger.info("Employing optimization method: COBYLA")
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
                cons.append(
                    {"type": "ineq", "fun": lambda x, i=factor: x[i + 1] - x[i]}
                )
                cons.append(
                    {
                        "type": "ineq",
                        "fun": lambda x, i=factor, num=N: x[i + 1 + num] - x[i + num],
                    }
                )
            opt_result = opt.minimize(
                self.to_minimize_imp,
                init_vect,
                args=(theo_log_time, impedance, log_time, global_weight, N, theo_delta),
                method="COBYLA",
                constraints=cons,
                tol=0.0001,
                options={"maxiter": 10000, "disp": True, "catol": 1},
            )
        else:
            logger.error(f"Unknown optimization method: {opt_method}")
            return None
        # Process final results
        opt_res = np.sort(opt_result.x[:N], kind="stable")
        opt_cap = np.sort(np.exp(opt_result.x[N:]), kind="stable")
        self.results_obj.append(
            self.to_minimize_imp(
                opt_result.x,
                theo_log_time,
                impedance,
                log_time,
                global_weight,
                N,
                theo_delta,
            )
        )
        self.results_res.append(opt_res)
        self.results_cap.append(opt_cap)
        self.results_res = np.reshape(np.array(self.results_res), (-1, N))
        self.results_cap = np.reshape(np.array(self.results_cap), (-1, N))
        min_idx = np.argmin(self.results_obj)
        return self.results_res[min_idx], self.results_cap[min_idx], opt_result

    def time_const_to_imp(self, theo_log_time, time_const):
        return utl.time_const_to_imp(theo_log_time, time_const)
