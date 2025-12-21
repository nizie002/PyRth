"""Front-end helpers that wire user parameters into PyRth evaluations.

This module exposes the high-level entrypoints (standard, optimization,
bootstrap, etc.) that users invoke from scripts or the CLI.  Each helper
instantiates a ``StructureFunction``, drives the configured pipeline, and
delegates exporting to ``IOManager`` so callers see a simple façade.
"""

import logging
from typing import Dict
from itertools import zip_longest

import numpy as np
import scipy.interpolate as ipl
import scipy.optimize as spo
import scipy.integrate as sin

from .utils import transient_utils as utl
from .utils import optimizer_utils as optu

from . import transient_optimizer as trop
from . import transient_defaults as dbase

from .exporter.transient_io_manager import IOManager

from .transient_core import StructureFunction

logger = logging.getLogger("PyRthLogger")


class Evaluation:
    """User-facing class for running thermal transient evaluations.

    The class owns the shared parameter dictionary, tracks generated modules,
    and offers convenience methods (``standard_module``, ``bootstrap_module``
    …) that apply the appropriate defaults before delegating to
    ``StructureFunction``.  It also centralizes exporter wiring so each module
    can materialize CSV/figure outputs consistently.
    """

    def __init__(self):
        """
        Initialize an Evaluation instance with default parameters.

        This class manages the evaluation of thermal transient data through
        different processing modules. It maintains a collection of modules
        and their results, and handles saving data to CSV and figures to files.

        The instance is created with default parameters that can be overridden
        when calling individual evaluation methods.
        """
        self.parameters: dict = {**dbase.std_eval_defaults, **dbase.std_output_defaults}
        self.modules: Dict[str, StructureFunction] = {}
        self.module_counters = {}
        self.set_length = 0
        self.io_manager = IOManager(self.modules)
        self.stored_early_zth: float | None = None

        utl.numba_preloader()
        logger.info("Evaluation initialized with standard defaults and IO manager ready.")

    def save_as_csv(self):
        """
        Export all evaluation results to CSV files.

        For each module stored in this Evaluation instance, saves all relevant
        data arrays (impedance, structure functions, time spectra, etc.) to
        separate CSV files in the configured output directories.
        """
        self.io_manager.export_csv()

    def save_figures(self):
        """
        Generate and save figures for all evaluation results.

        Creates visualizations of the data for each module stored in this
        Evaluation instance. Generates plots for impedance curves, structure
        functions, time constant spectra, etc., based on the output configuration.
        """
        self.io_manager.export_figures()

    def save_all(self):
        """
        Save both CSV data files and figures for all evaluation results.

        Convenience method that calls both save_as_csv() and save_figures().
        """
        self.save_as_csv()
        self.save_figures()

    def _add_module_to_eval_dict(self, module : StructureFunction):
        """
        Add a module to the internal storage dictionary with proper labeling.

        If a module with the same label already exists, appends a counter to
        the label to ensure uniqueness.

        Parameters
        ----------
        module : StructureFunction
            The module to add to the internal storage
        """
        original_label = module.label

        counter = self.module_counters.get(module.label, 0)
        if counter > 0:
            module.label = f"{module.label}_{counter}"

        self.module_counters[module.label] = counter + 1

        # Log a warning if the label changed
        if module.label != original_label:
            logger.warning(
                f"Module label '{original_label}' already exists. Renamed to '{module.label}'."
            )

        self.modules[module.label] = module
        logger.debug(
            "Registered module '%s' (instance #%s)", module.label, self.module_counters[module.label]
        )

    def standard_module(self, parameters):
        """
        Standard module for evaluation of the impedance function.
        This method compiles the necessary parameters and initializes the structure function based on validation and requirements.
        """

        if not isinstance(parameters, dict):
            raise TypeError("Parameters must be provided as a dictionary.")

        self.parameters = dbase.validate_and_merge_defaults(parameters, self.parameters)

        module = self._standard_module()
        self._add_module_to_eval_dict(module)

        return module

    def _standard_module(self):

        module: StructureFunction = StructureFunction(self.parameters)

        if not hasattr(module, "label"):
            raise AttributeError(
                "Module is missing 'label' attribute. It is used to identify the results in CSV and image output."
            )
        if not hasattr(module, "input_mode"):
            raise AttributeError(
                "Module is missing 'input_mode' attribute. It is used for converting input data to the correct thermal impedance."
            )

        logger.info(
            "Starting standard evaluation for '%s' (deconv_mode=%s, calc_struc=%s)",
            module.label,
            getattr(module, "deconv_mode", "unknown"),
            getattr(module, "calc_struc", False),
        )

        if module.normalize_impedance_to_previous:
            if self.stored_early_zth is not None:
                module.stored_early_zth = self.stored_early_zth
                logger.debug(
                    "Normalizing impedance for '%s' using stored early-Zth reference",
                    module.label,
                )
            else:
                logger.info(
                    "Normalization requested for '%s' but no baseline stored; "
                    "capturing this run as the future reference.",
                    module.label,
                )

        logger.debug("Computing impedance for '%s'", module.label)
        module.make_z()

        module.data_handlers.add("impedance")

        if not module.only_make_z:

            logger.info(
                "Running deconvolution for '%s' using mode '%s'",
                module.label,
                module.deconv_mode,
            )

            if module.deconv_mode == "lasso":
                module.z_fit_lasso()
                logger.debug("Lasso deconvolution complete for '%s'", module.label)
                module.data_handlers.add("time_spec")

            else:
                module.z_fit_deriv()
                logger.debug("Z fit derivative completed for '%s'", module.label)

                if module.deconv_mode == "fourier":
                    logger.debug("Performing Fourier transform for '%s'", module.label)
                    module.fft_signal()
                    module.fft_weight()
                    module.fft_time_spec()
                    # Add FFT and time_spec handlers
                    module.data_handlers.update(["fft", "time_spec"])
                elif module.deconv_mode == "bayesian":
                    logger.debug("Performing Bayesian deconvolution for '%s'", module.label)
                    module.perform_bayesian_deconvolution()
                    # Add time_spec handler for Bayesian
                    module.data_handlers.add("time_spec")
                elif module.deconv_mode == "adaptive":
                    logger.debug("Performing adaptive deconvolution for '%s'", module.label)
                    module.perform_bayesian_deconvolution()
                    module.z_fit_lasso()
                    # Add time_spec handler for adaptive
                    module.data_handlers.add("time_spec")

                else:
                    raise ValueError("Invalid deconvolution mode specified.")

            logger.debug("Synthesizing Foster network for '%s'", module.label)
            module.foster_network()

            if module.calc_struc:
                logger.info(
                    "Calculating structure function for '%s' using %s",
                    module.label,
                    module.struc_method,
                )

                if module.struc_method == "polylong":
                    logger.debug("Using poly long division for '%s'", module.label)
                    module.mpfr_foster_impedance()
                    module.poly_long_div()
                elif module.struc_method in ["khatwani", "sobhy"]:
                    logger.debug("Using continued fraction methods for '%s'", module.label)
                    module.mpfr_foster_impedance()
                    module.j_fraction_methods()
                elif module.struc_method == "boor_golub":
                    logger.debug("Using Boor-Golub method for '%s'", module.label)
                    module.mpfr_foster_impedance()
                    module.boor_golub()
                elif module.struc_method == "lanczos":
                    logger.debug("Using Lanczos method for '%s'", module.label)
                    module.lanczos()

                # Add structure handler after any structure calculation
                module.data_handlers.add("structure")

                logger.info(
                    "Structure function complete for '%s'; total resistance: %.2f K/W",
                    module.label,
                    module.int_cau_res[-1],
                )

        if module.normalize_impedance_to_previous and self.stored_early_zth is None:
            self.stored_early_zth = utl.get_early_zth(module)
            logger.debug(
                "Captured early-Zth reference from '%s' for future normalization",
                module.label,
            )

        if module.save_back_impedance or (
            (module.look_at_backwards_imp_deriv or module.look_at_backwards_impedance)
        ):
            inverse_module = trop.TransientOptimizer()

            logger.debug("Generating backward impedance for '%s'", module.label)
            module.back_imp_deriv, module.back_imp = inverse_module.time_const_to_imp(
                module.log_time_pad, module.time_spec
            )

        logger.info("Finished standard evaluation for '%s'", module.label)
        return module

    def standard_module_set(self, parameters):
        """
        Standard module set for evaluation of the impedance function. This method is used to evaluate multiple impedance approximations using different parameters.
        """

        if not isinstance(parameters, dict):
            raise TypeError("Parameters must be provided as a dictionary.")

        if "iterable_keywords" not in parameters:
            raise ValueError(
                "iterable_keywords must be provided in parameters. It is used to determine the keywords to iterate over."
            )

        if "evaluation_type" not in parameters:
            raise ValueError(
                "evaluation_type must be provided in parameters. It must be either 'standard' or 'optimization'. It is used to determine the type of evaluation to perform."
            )

        if "label" not in parameters:
            raise ValueError(
                "label must be provided in parameters. It is used as the base label for each module."
            )

        self.parameters = dbase.validate_and_merge_defaults(parameters, self.parameters)

        modules = self._standard_module_set()

        for module in modules:
            self._add_module_to_eval_dict(module)

        return modules

    def _standard_module_set(self):
        iterable_keywords = self.parameters.pop("iterable_keywords")
        evaluation_type = self.parameters.get("evaluation_type")
        base_label = self.parameters.get("label")

        iterators = [
            utl.get_iterator(self.parameters.get(keyword, []))
            for keyword in iterable_keywords
        ]

        fill_value = object()
        temp_iter = list(zip_longest(*iterators, fillvalue=fill_value))
        has_holes = any(
            fill_value is value
            for values in temp_iter
            for value in values
        )
        if has_holes:
            raise ValueError("Iterables do not have the same length")

        iterators = [
            utl.get_iterator(self.parameters.get(keyword, []))
            for keyword in iterable_keywords
        ]

        org_parameters = self.parameters.copy()
        modules_list = []

        self.set_length = 0

        logger.info(
            "Starting module set '%s' (%s) with %d variations over %s",
            base_label,
            evaluation_type,
            len(temp_iter),
            ", ".join(map(str, iterable_keywords)),
        )

        for counter, values in enumerate(zip(*iterators)):
            modified_parameters = org_parameters.copy()

            if iterable_keywords:
                first_keyword = iterable_keywords[0]
                label_suffix = f"{first_keyword}_{counter}"
            else:
                label_suffix = f"set_{counter}"

            modified_parameters["label"] = f"{base_label}_{label_suffix}"

            for keyword, value in zip(iterable_keywords, values):
                modified_parameters[keyword] = value

            self.parameters = dbase.validate_and_merge_defaults(
                modified_parameters, self.parameters
            )

            logger.debug(
                "Building variant %d/%d with label '%s'",
                counter + 1,
                len(temp_iter),
                modified_parameters["label"],
            )

            if evaluation_type == "standard":
                module = self._standard_module()
            elif evaluation_type == "optimization":
                module = self._optimization_module()
            elif evaluation_type in ["bootstrap_standard", "bootstrap_optimization"]:
                module = self._bootstrap_module()
            else:
                raise ValueError(
                    "Invalid evaluation_type. Choose either 'standard', 'optimization', or 'bootstrap_standard' or 'bootstrap_optimization'."
                )
            modules_list.append(module)
            self.set_length += 1

        logger.info(
            "Completed module set '%s'; generated %d module(s)", base_label, self.set_length
        )
        return modules_list

    def bootstrap_module(self, parameters: Dict):
        """
        Bootstrap module for evaluation with specified parameters. The module is used to evaluate the impedance approximation using a structure function. The structure function is calculated from a given set of resistances and capacitances.
        """

        self.parameters = dbase.validate_and_merge_defaults(parameters, self.parameters)
        module = self._bootstrap_module()
        self._add_module_to_eval_dict(module)
        return module

    def _bootstrap_module(self):

        mode = self.parameters.pop("bootstrap_mode", "from_data")

        if mode not in ["from_theo", "from_data"]:
            raise ValueError(
                f"Invalid mode '{mode}' for bootstrap evaluation. Valid options are: ['from_theo', 'from_data']"
            )
        repetitions = self.parameters["repetitions"]
        logger.info(
            "Starting bootstrap evaluation (%s) for '%s' with %d repetitions",
            mode,
            self.parameters.get("label", "no_label"),
            repetitions,
        )

        if not self.parameters["calc_struc"]:
            raise ValueError(
                "Structure function calculation must be enabled for bootstrapping."
            )

        time_name = deriv_time_name = time_const_name = None
        imp_name = deriv_name = None
        int_cau_res_name = int_cau_cap_name = None
        boot_method = None

        if self.parameters["evaluation_type"] == "bootstrap_optimization":
            time_name = "theo_log_time"
            imp_name = "theo_impedance"
            deriv_name = "theo_imp_deriv"
            deriv_time_name = "theo_log_time"
            time_const_name = "theo_time_const"
            int_cau_res_name = "theo_int_cau_res"
            int_cau_cap_name = "theo_int_cau_cap"
            boot_method = self._optimization_module
        elif self.parameters["evaluation_type"] == "bootstrap_standard":
            time_name = "log_time_interp"
            imp_name = "imp_smooth"
            deriv_name = "imp_deriv_interp"
            deriv_time_name = "log_time_pad"
            time_const_name = "time_spec"
            int_cau_res_name = "int_cau_res"
            int_cau_cap_name = "int_cau_cap"
            boot_method = self._standard_module
        else:
            raise ValueError(
                f"Invalid evaluation_type specified {self.parameters['evaluation_type']}. Must be 'bootstrap_standard' or 'bootstrap_optimization'."
            )

        if mode == "from_theo":
            module = self.theoretical_module(self.parameters)
            var = module.theo_impedance[-1] / self.parameters["signal_to_noise_ratio"]
            self.parameters["expected_var"] = var
            logger.debug(
                "Bootstrapping from theoretical data for '%s' with expected variance %.4e",
                module.label,
                var,
            )

        elif mode == "from_data":

            module = boot_method()

            module.hist, bin_edge = np.histogram(
                module.impedance - module.imp_smooth_full, bins=30
            )

            module.bins = (bin_edge[1:] + bin_edge[:-1]) / 2.0
            fit_result = spo.curve_fit(
                utl.generalized_gaussian,
                module.bins,
                module.hist,
                p0=(500, 0.1, 0.01),
                full_output=False,
            )
            popt = fit_result[0]

            module.gauss_curve = utl.generalized_gaussian(module.bins, *popt)

            module.data_handlers.add("residual")
            logger.debug(
                "Bootstrapping from measured data for '%s' with fitted variance %.4e",
                module.label,
                popt[1],
            )

        self.parameters["input_mode"] = "impedance"

        min_res = np.inf
        max_res = -np.inf

        # Set up the random number generator
        seed = self.parameters.get("random_seed")
        if seed is not None:
            rng = np.random.default_rng(seed)
        else:
            rng = np.random.default_rng()

        for n in range(repetitions):

            logger.debug("Bootstrap repetition %d/%d", n + 1, repetitions)

            if mode == "from_theo":
                impedance = module.theo_impedance + rng.normal(
                    0.0, var, len(module.theo_impedance)
                )

                self.parameters["data"] = np.column_stack(
                    (np.exp(module.theo_log_time), impedance)
                )

            elif mode == "from_data":

                self.parameters["expected_var"] = popt[1]
                resampled_imp = module.imp_smooth_full + rng.normal(
                    0.0, abs(popt[1]), len(module.imp_smooth_full)
                )

                self.parameters["data"] = np.column_stack(
                    (np.exp(module.log_time), resampled_imp)
                )

            boot_module = boot_method()

            if n == 0:
                module.boot_results_imp = np.zeros(
                    (repetitions, len(getattr(boot_module, imp_name)))
                )
                module.boot_results_deriv = np.zeros(
                    (repetitions, len(getattr(boot_module, deriv_name)))
                )
                module.boot_results_timeconst = np.zeros(
                    (repetitions, len(getattr(boot_module, time_const_name)))
                )
                module.boot_results_sum_timeconst = np.zeros(
                    (repetitions, len(getattr(boot_module, time_const_name)))
                )
                module.boot_results_struc_res = [0] * repetitions
                module.boot_results_struc_cap = [0] * repetitions

            module.boot_results_imp[n, :] = getattr(boot_module, imp_name).flatten()
            module.boot_results_deriv[n, :] = getattr(boot_module, deriv_name).flatten()
            module.boot_results_timeconst[n, :] = getattr(
                boot_module, time_const_name
            ).flatten()
            module.boot_results_sum_timeconst[n, :] = sin.cumulative_trapezoid(
                getattr(boot_module, time_const_name).flatten(),
                x=getattr(boot_module, deriv_time_name).flatten(),
                initial=0.0,
            )
            module.boot_results_struc_res[n] = getattr(
                boot_module, int_cau_res_name
            ).flatten()
            module.boot_results_struc_cap[n] = getattr(
                boot_module, int_cau_cap_name
            ).flatten()

            current_min = module.boot_results_struc_res[n][0]
            current_max = module.boot_results_struc_res[n][-1]
            min_res = min(min_res, current_min)
            max_res = max(max_res, current_max)

        logger.info("Calculating bootstrap confidence intervals for '%s'", module.label)

        module.boot_imp_time = getattr(boot_module, time_name).flatten()
        module.boot_deriv_time = getattr(boot_module, deriv_time_name).flatten()

        module.boot_imp_av = np.median(module.boot_results_imp, axis=0)
        module.boot_imp_perc_u, module.boot_imp_perc_l = np.percentile(
            module.boot_results_imp, [10, 90], axis=0
        )

        module.boot_deriv_av = np.median(module.boot_results_deriv, axis=0)
        module.boot_deriv_perc_u, module.boot_deriv_perc_l = np.percentile(
            module.boot_results_deriv, [10, 90], axis=0
        )

        module.boot_time_spec_av = np.median(module.boot_results_timeconst, axis=0)
        module.boot_time_spec_perc_u, module.boot_time_spec_perc_l = np.percentile(
            module.boot_results_timeconst, [10, 90], axis=0
        )

        module.boot_sum_time_spec_av = np.median(
            module.boot_results_sum_timeconst, axis=0
        )
        module.boot_sum_time_spec_perc_u, module.boot_sum_time_spec_perc_l = (
            np.percentile(module.boot_results_sum_timeconst, [10, 90], axis=0)
        )

        base_num_fine = int(1e4)

        module.boot_struc_res_fine = np.linspace(
            min_res, max_res, base_num_fine, endpoint=True
        )

        interp_func = [0] * repetitions
        for n in range(repetitions):
            interp_func[n] = ipl.interp1d(
                module.boot_results_struc_res[n], module.boot_results_struc_cap[n]
            )

        module.boot_struc_cap_av = np.zeros(base_num_fine)
        module.boot_struc_cap_perc_u = np.zeros(base_num_fine)
        module.boot_struc_cap_perc_l = np.zeros(base_num_fine)

        for res_idx, res in enumerate(module.boot_struc_res_fine):
            n_vals = 0
            vals = [0.0] * repetitions
            for m in range(repetitions):
                if res > module.boot_results_struc_res[m][-1]:
                    vals[n_vals] = module.boot_results_struc_cap[m][-1]
                    n_vals += 1
                elif (res >= module.boot_results_struc_res[m][0]) and (
                    res <= module.boot_results_struc_res[m][-1]
                ):
                    vals[n_vals] = interp_func[m](res)
                    n_vals += 1

            module.boot_struc_cap_av[res_idx] = np.median(vals[:n_vals])
            module.boot_struc_cap_perc_u[res_idx], module.boot_struc_cap_perc_l[res_idx] = (
                np.percentile(vals[:n_vals], [10, 90])
            )

        module.data_handlers.add("boot")

        logger.info("Bootstrap evaluation complete for '%s'", module.label)
        return module

    def optimization_module(self, parameters: dict):
        """
        Optimizes the impedance approximation using a structure function. The structure function is calculated from a given set of resistances and capacitances.
        """

        if not isinstance(parameters, dict):
            raise TypeError("Parameters must be provided as a dictionary.")

        self.parameters = dbase.validate_and_merge_defaults(parameters, self.parameters)

        module = self._optimization_module()

        self._add_module_to_eval_dict(module)

        return module

    def _optimization_module(self):

        module = self._standard_module()
        logger.info("Starting optimization refinement for '%s'", module.label)
        module.theo_log_time = np.linspace(
            np.log(self.parameters["theo_time"][0]),
            np.log(self.parameters["theo_time"][1]),
            self.parameters["theo_time_size"],
        )

        opt_module = trop.TransientOptimizer(self.parameters)

        if not module.opt_use_extrapolate:
            logger.debug(
                "Restricting optimization window for '%s' starting at %.3e s",
                module.label,
                module.lower_fit_limit,
            )

            lower_fit_index = np.searchsorted(
                module.theo_log_time, np.log(module.lower_fit_limit)
            )

            module.opt_log_time = module.log_time[lower_fit_index:]
            module.opt_imp = module.impedance[lower_fit_index:]

        elif module.opt_use_extrapolate:
            module.opt_log_time = module.log_time
            module.opt_imp = module.impedance
            logger.debug(
                "Using full impedance curve for '%s' during optimization", module.label
            )

        module.cau_res_opt = module.int_cau_res
        module.cau_cap_opt = module.int_cau_cap

        num_layers = self.parameters["opt_model_layers"]
        if self.parameters["struc_init_method"] == "optimal_fit":
            logger.info(
                "Initializing structure function via optimal_fit for '%s' with %d layers",
                module.label,
                num_layers,
            )

            struc_marker, init_opt_result = opt_module.optimize_theo_struc(
                module.cau_res_opt, module.cau_cap_opt, num_layers
            )
            (
                module.init_opt_imp_res,
                module.init_opt_imp_cap,
                module.init_opt_struc_res,
                module.init_opt_struc_cap,
            ) = struc_marker

            logger.info(
                "Initial optimization finished for '%s' (success=%s, message=%s)",
                module.label,
                init_opt_result.success,
                init_opt_result.message,
            )

        if self.parameters["struc_init_method"] == "x_sampling":

            logger.debug(
                "Initializing structure function via x_sampling for '%s'", module.label
            )
            module.init_opt_imp_res, module.init_opt_imp_cap = (
                opt_module.struc_x_sample(module.cau_res_opt, module.cau_cap_opt, num_layers)
            )

        module.init_opt_imp_res_diff = opt_module.sort_and_lim_diff(
            module.init_opt_imp_res
        )
        module.init_opt_imp_cap_diff = opt_module.sort_and_lim_diff(
            module.init_opt_imp_cap
        )

        logger.info(
            "Running impedance fit for '%s' using method '%s'",
            module.label,
            self.parameters["opt_method"],
        )

        module.fin_res, module.fin_cap, opt_result = opt_module.optimize_to_imp(
            module.init_opt_imp_res,
            module.init_opt_imp_cap,
            module.theo_log_time,
            module.opt_imp,
            module.opt_log_time,
            self.parameters["theo_delta"],
            self.parameters["opt_method"],
        )

        logger.info(
            "Optimization completed for '%s' (success=%s, message=%s)",
            module.label,
            opt_result.success,
            opt_result.message,
        )

        module.fin_res_diff = opt_module.sort_and_lim_diff(module.fin_res)
        module.fin_cap_diff = opt_module.sort_and_lim_diff(module.fin_cap)

        module.theo_int_cau_res, module.theo_int_cau_cap = (
            opt_module.struc_params_to_func(
                1000, module.fin_res_diff, module.fin_cap_diff
            )
        )

        module.theo_diff_struc = np.zeros(len(module.theo_int_cau_res) - 1)
        for i in range(len(module.theo_int_cau_res) - 1):
            if not (module.theo_int_cau_res[i] - module.theo_int_cau_res[i + 1]) == 0.0:
                module.theo_diff_struc[i] = (
                    module.theo_int_cau_cap[i] - module.theo_int_cau_cap[i + 1]
                ) / (module.theo_int_cau_res[i] - module.theo_int_cau_res[i + 1])

        module.theo_time_const = opt_module.struc_to_time_const(
            module.theo_log_time,
            self.parameters["theo_delta"],
            module.fin_res_diff,
            module.fin_cap_diff,
        )

        module.theo_imp_deriv, module.theo_impedance = opt_module.time_const_to_imp(
            module.theo_log_time, module.theo_time_const
        )

        module.init_theo_time_const = opt_module.struc_to_time_const(
            module.theo_log_time,
            self.parameters["theo_delta"],
            module.init_opt_imp_res_diff,
            module.init_opt_imp_cap_diff,
        )

        module.init_theo_imp_deriv, module.init_theo_impedance = (
            opt_module.time_const_to_imp(
                module.theo_log_time, module.init_theo_time_const
            )
        )

        module.back_imp_deriv, module.back_imp = opt_module.time_const_to_imp(
            module.log_time_pad, module.time_spec
        )

        init_theo_impedance_int = np.interp(
            module.opt_log_time, module.theo_log_time, module.init_theo_impedance
        )
        theo_impedance_int = np.interp(
            module.opt_log_time, module.theo_log_time, module.theo_impedance
        )
        back_imp_int = np.interp(
            module.opt_log_time, module.log_time_pad, module.back_imp
        )

        module.data_handlers.update(
            ["theo_structure", "theo", "theo_compare", "optimize"]
        )

        initial_diff = optu.weighted_diff(
            module.opt_log_time, module.opt_imp, init_theo_impedance_int
        )
        forward_diff = optu.weighted_diff(
            module.opt_log_time, module.opt_imp, back_imp_int
        )
        optimized_diff = optu.weighted_diff(
            module.opt_log_time, module.opt_imp, theo_impedance_int
        )

        logger.info(
            "Optimization metrics for '%s': initial=%.4e, forward=%.4e, optimized=%.4e",
            module.label,
            initial_diff,
            forward_diff,
            optimized_diff,
        )

        logger.info("Finished optimization refinement for '%s'", module.label)

        return module

    def theoretical_module(self, parameters: dict):
        """
        Calculates a thermal impedance from a structure function. The structure function is calculated from a given set of resistances and capacitances.
        Each resistance and capacitance is associated with constant RC-transmission line section, which is concatenated to the previous.

        Parameters
        ----------
        theo_resistances : list of size N
            List of total resistances for each constant sections for the piecewise-uniform structure function.

        theo_capacitances : list of size N
            List of total capacitances for each constant sections for the piecewise-uniform structure function.

        output_dir : string, default="output\\csv"
            Output directory for plots saved as PNG-files. Additionally a subfolder
            named "csv" is created where the CSV files are saved.

        label : string, default="no_label"
            Label of the given parameter set. The label is used for the output files.

        theo_time : list of size 2, default=[-4e-8, 1e3]
            The time range for the thermal impedance in seconds.

        theo_time_size : integer, default=30000
            Number of points evenly distributed over the logarithmic time domain.

        theo_delta : float, default=0.5
            Angle to rotate the integration path into the complex plane.

        theo_added_noise : float
            The added gaussian noise to the impedance.


        Examples
        --------
        The following example calculates a thermal impedance for structure function with the five sections. The
        thermal impedance, impulse response, time constant spectrum, as well as other results are saved as CSV-files in the folder "theoretical".

        >>> import PyRth
        >>> parameters = {
        ...     "output_dir": "theoretical/",
        ...     "label": "theoretical",
        ...     "theo_time": [3e-7, 200],
        ...     "theo_time_size": 10000,
        ...     "theo_delta": 1.5 * (2 * np.pi / 360),
        ...     "theo_resistances": [10, 10, 10, 10, 10],
        ...     "theo_capacitances": [1e-4, 1e-1, 1e-4, 1e-3, 1e0],
        ... }
        >>> eval_instance = PyRth.Evaluation()
        >>> eval_instance.theoretical_module(parameters)
        >>> eval_instance.save_as_csv()
        >>> eval_instance.save_figures()
        """

        if not isinstance(parameters, dict):
            raise TypeError("Parameters must be provided as a dictionary.")

        self.parameters = dbase.validate_and_merge_defaults(parameters, self.parameters)
        return self._theoretical_module()

    def _theoretical_module(self):

        saved_parameters = self.parameters.copy()

        if (
            "theo_inverse_specs" in self.parameters.keys()
            and self.parameters["theo_inverse_specs"] is not None
        ):
            logger.debug("Using theoretical inverse specs")
            inverse_specs = self.parameters.pop("theo_inverse_specs")
            self.parameters = dbase.validate_and_merge_defaults(
                inverse_specs, self.parameters
            )

        required_keys = {"theo_resistances", "theo_capacitances"}
        for key in required_keys:
            if key not in self.parameters or self.parameters[key] is None:
                raise ValueError(f"{key} must be provided in the parameters.")

        module: StructureFunction = StructureFunction(self.parameters)
        logger.info("Calculating theoretical impedance for '%s'", module.label)
        inv_module = trop.TransientOptimizer(self.parameters)

        module.theo_log_time = np.linspace(
            np.log(self.parameters["theo_time"][0]),
            np.log(self.parameters["theo_time"][1]),
            self.parameters["theo_time_size"],
        )

        logger.debug("Compiling theoretical structure function")

        module.theo_int_cau_res, module.theo_int_cau_cap = (
            inv_module.struc_params_to_func(
                1000, module.theo_resistances, module.theo_capacitances
            )
        )

        module.theo_int_cau_res = module.theo_int_cau_res[1:]
        module.theo_int_cau_cap = module.theo_int_cau_cap[1:]

        module.theo_diff_struc = np.zeros(len(module.theo_int_cau_res) - 1)
        for i in range(len(module.theo_int_cau_res) - 1):
            if not (module.theo_int_cau_res[i] - module.theo_int_cau_res[i + 1]) == 0.0:
                module.theo_diff_struc[i] = (
                    module.theo_int_cau_cap[i] - module.theo_int_cau_cap[i + 1]
                ) / (module.theo_int_cau_res[i] - module.theo_int_cau_res[i + 1])

        logger.debug("Calculating theoretical time constant spectrum")

        module.theo_time_const = inv_module.struc_to_time_const(
            module.theo_log_time,
            module.theo_delta,
            module.theo_resistances,
            module.theo_capacitances,
        )

        logger.debug("Calculating theoretical impedance")

        module.theo_imp_deriv, module.theo_impedance = inv_module.time_const_to_imp(
            module.theo_log_time, module.theo_time_const
        )

        module.data_handlers.add("theo_structure")
        module.data_handlers.add("theo")

        self._add_module_to_eval_dict(module)
        self.parameters = saved_parameters

        logger.info("Finished theoretical module '%s'", module.label)
        return module

    def comparison_module(self, parameters: dict):
        """
        Compares the impedance of a system to a theoretical impedance. The theoretical impedance is calculated from a given set of resistances and capacitances.
        Each resistance and capacitance is associated with constant RC-transmission line section, which is concatenated to the previous.

        """

        if not isinstance(parameters, dict):
            raise TypeError("Parameters must be provided as a dictionary.")

        self.parameters = dbase.validate_and_merge_defaults(parameters, self.parameters)

        if self.parameters["evaluation_type"] not in [
            "standard",
            "optimization",
            "bootstrap_standard",
            "bootstrap_optimization",
        ]:
            raise ValueError(
                "evaluation_type must be either 'standard', 'optimization', 'bootstrap_standard', or 'bootstrap_optimization'."
            )

        bootstraping = self.parameters["evaluation_type"] in [
            "bootstrap_standard",
            "bootstrap_optimization",
        ]

        results_module = StructureFunction(self.parameters)
        results_module.mod_key_display_name = "_".join(parameters["iterable_keywords"])

        iterators = [
            utl.get_iterator(self.parameters.get(keyword, []))
            for keyword in parameters["iterable_keywords"]
        ]

        results_module.mod_value_list = list(iterators[0])
        logger.info(
            "Starting comparison (%s) across %d variation(s) of %s",
            self.parameters["evaluation_type"],
            len(results_module.mod_value_list),
            results_module.mod_key_display_name,
        )

        time_name = time_const_name = int_cau_res_name = int_cau_cap_name = None

        if not bootstraping:
            logger.info(
                "Comparing against theoretical impedance using '%s' evaluation",
                self.parameters["evaluation_type"],
            )
            if self.parameters["evaluation_type"] == "optimization":
                time_name = "theo_log_time"
                time_const_name = "theo_time_const"
                int_cau_res_name = "theo_int_cau_res"
                int_cau_cap_name = "theo_int_cau_cap"
            elif self.parameters["evaluation_type"] == "standard":
                time_name = "log_time_pad"
                time_const_name = "time_spec"
                int_cau_res_name = "int_cau_res"
                int_cau_cap_name = "int_cau_cap"

            theo_module = self._theoretical_module()
            self.parameters["data"] = np.column_stack(
                (np.exp(theo_module.theo_log_time), theo_module.theo_impedance)
            )

        else:
            logger.info("Comparing bootstrap results to theoretical impedance")
            self.parameters["bootstrap_mode"] = "from_theo"
            time_name = "boot_deriv_time"
            time_const_name = "boot_time_spec_av"
            int_cau_res_name = "boot_struc_res_fine"
            int_cau_cap_name = "boot_struc_cap_av"

        comp_modules = self._standard_module_set()

        for module in comp_modules:
            self._add_module_to_eval_dict(module)

        # Set up arrays to store computed values.
        results_module.time_const_comparison = np.empty(self.set_length)
        results_module.structure_comparison = np.empty(self.set_length)
        results_module.total_resist_diff = np.empty(self.set_length)

        def _calc_comparison_metrics(module_1, module_2):
            """Calculate norm for time-constant, structure, and the total resistance difference."""
            norm_time_const = optu.l2_norm_time_const(
                module_1.theo_log_time,
                module_1.theo_time_const,
                getattr(module_2, time_name),
                getattr(module_2, time_const_name),
            )
            norm_structure = optu.norm_structure(
                module_1.theo_int_cau_res,
                module_1.theo_int_cau_cap,
                getattr(module_2, int_cau_res_name),
                getattr(module_2, int_cau_cap_name),
            )
            total_res_diff = np.abs(
                getattr(module_2, int_cau_res_name)[-1] - module_1.theo_int_cau_res[-1]
            )
            return norm_time_const, norm_structure, total_res_diff

        for n, module in enumerate(comp_modules):

            if bootstraping:
                norm_time, norm_struc, res_diff = _calc_comparison_metrics(
                    module, module
                )
                results_module.time_const_comparison[n] = norm_time
                results_module.structure_comparison[n] = norm_struc
                results_module.total_resist_diff[n] = res_diff
            else:
                norm_time, norm_struc, res_diff = _calc_comparison_metrics(
                    theo_module, module
                )
                results_module.time_const_comparison[n] = norm_time
                results_module.structure_comparison[n] = norm_struc
                results_module.total_resist_diff[n] = res_diff

            logger.info(
                "Comparison for '%s': l2_norm_time_const=%.4e, norm_structure=%.4e, total_resist_diff=%.4e",
                module.label,
                norm_time,
                norm_struc,
                res_diff,
            )

        results_module.data_handlers.add("comparison")

        self._add_module_to_eval_dict(results_module)

        logger.info("Completed comparison across %d module(s)", self.set_length)
        return results_module

    def temperature_prediction_module(self, parameters):
        """
        Predicts the temperature of a system given a power function and an impulse response.
        """

        for key, value in parameters.items():
            self.parameters[key] = value

        evaluation_type = self.parameters.get("evaluation_type")

        if parameters.get("power_data") is None:
            raise ValueError("power_data must be provided in parameters.")

        if evaluation_type == "standard":
            module = self._standard_module()
            module.reference_time = np.exp(module.log_time_pad)
            module.reference_impulse_response = module.imp_deriv_interp
        elif evaluation_type == "optimization":
            module = self._optimization_module()
            module.reference_time = np.exp(module.theo_log_time)
            module.reference_impulse_response = module.theo_imp_deriv
        else:
            raise ValueError("evaluation_type must be 'standard' or 'optimization'.")

        logger.info(
            "Starting temperature prediction for '%s' using '%s' evaluation",
            module.label,
            evaluation_type,
        )

        module.power_t = self.parameters.get("power_data")[:, 0]
        module.power_function = self.parameters.get("power_data")[:, 1]

        t_min = -(
            module.power_t[-1] + module.reference_time[-1]
        )  # Since impulse response is 0 for t < 0
        t_max = module.power_t[-1] + module.reference_time[-1]

        lin_t_number = int((t_max - t_min) / self.parameters["lin_sampling_period"])

        module.lin_time, dt = np.linspace(t_min, t_max, lin_t_number, retstep=True)

        logger.info("Interpolating power function and impulse response")

        module.power_function_int = np.interp(
            module.lin_time, module.power_t, module.power_function, left=0.0
        )
        module.impulse_response_int = np.interp(
            module.lin_time,
            module.reference_time,
            module.reference_impulse_response,
            left=0.0,
            right=0.0,
        )

        area_interp = np.trapezoid(module.impulse_response_int, x=module.lin_time)
        area_org = np.trapezoid(module.reference_impulse_response, x=module.reference_time)

        logger.debug("Original impulse area: %s", area_org)
        logger.debug("Interpolated impulse area: %s", area_interp)

        logger.info("Starting convolution")

        module.predicted_temperature = (
            np.convolve(
                module.power_function_int, module.impulse_response_int, mode="same"
            )
            * dt
        )
        module.predicted_temperature = module.predicted_temperature[
            lin_t_number // 2 - 1 :
        ]
        module.lin_time = module.lin_time[lin_t_number // 2 - 1 :]
        module.power_function_int = module.power_function_int[lin_t_number // 2 - 1 :]

        module.data_handlers.add("prediction")

        self._add_module_to_eval_dict(module)

        logger.info(
            "Temperature prediction complete for '%s' (%d samples)",
            module.label,
            len(module.predicted_temperature),
        )
        return module
