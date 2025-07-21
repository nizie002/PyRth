import numpy as np

import logging

#: Module providing default configuration parameters for PyRth analysis.
#:
#: This module defines the default values for various settings used across
#: different evaluation functions in :py:mod:`~PyRth.transient_scripts`.
#: These defaults can be overridden by passing keyword arguments to the
#: respective evaluation methods when instantiating or calling methods
#: on the :py:class:`~PyRth.transient_scripts.Evaluation` class.
#:
#: See the :ref:`Default Configuration <default-configuration-label>` section
#: in the documentation for a rendered view of these parameters.

logger = logging.getLogger("PyRthLogger")


def deep_equals(val1, val2):

    if val1 is None or val2 is None:
        return val1 is val2
    # Check if both are numpy arrays
    if isinstance(val1, np.ndarray) and isinstance(val2, np.ndarray):
        return np.array_equal(val1, val2)
    # Check if both are dictionaries
    if isinstance(val1, dict) and isinstance(val2, dict):
        if set(val1.keys()) != set(val2.keys()):
            return False
        return all(deep_equals(val1[k], val2[k]) for k in val1)
    # Check if both are lists or tuples
    if isinstance(val1, (list, tuple)) and isinstance(val2, (list, tuple)):
        if len(val1) != len(val2):
            return False
        return all(deep_equals(a, b) for a, b in zip(val1, val2))
    # Fallback to standard equality
    return val1 == val2


def validate_and_merge_defaults(params: dict, self_parameters: dict) -> dict:

    # This function is used to integrate the standard evaluation defaults and the standard output defaults into the parameters dictionary.

    # reject any keys that are not in the standard evaluation defaults or the standard output defaults and warn the user and remove it

    params = params.copy()
    self_parameters = self_parameters.copy()

    all_defaults = {**std_eval_defaults, **std_output_defaults}

    for key in list(params.keys()):
        if key not in all_defaults.keys():
            logger.warning(
                f"Parameter {key} is not a standard parameter and will be ignored."
            )

            params.pop(key)

    # add self_parameters to the parameters dictionary
    for key in self_parameters.keys():
        if key not in params.keys():
            params[key] = self_parameters[key]

    # add the standard evaluation defaults to the parameters dictionary
    for key in std_eval_defaults.keys():
        if key not in params.keys():
            params[key] = std_eval_defaults[key]

    # add the standard output defaults to the parameters dictionary
    for key in std_output_defaults.keys():
        if key not in params.keys():
            params[key] = std_output_defaults[key]

    for key, value in params.items():
        default_value = all_defaults.get(key, None)
        if (key == "data" or key == "calib") and value is not None:
            try:
                logger.info(f"{key}: shape={value.shape}")
            except AttributeError:
                logger.info(f"{key}: object type={type(value)}")
        else:
            if key in all_defaults:
                is_equal = deep_equals(value, default_value)
                if isinstance(is_equal, np.ndarray):
                    is_equal = is_equal.all()
                if not bool(is_equal):
                    logger.info(f"using non-default {key}: {value}")

    return params


std_eval_defaults: dict = {
    # Numerical Settings
    "precision": 250,
    #: int: Number of points used for internal calculations involving the impedance curve.
    "log_time_size": 250,
    #: int: Number of points in the logarithmically spaced time array used for spectrum calculations.
    #
    # deconvolution settings
    "filter_name": "hann",
    #: str: Name of the filter for FFT deconvolution. Options: "fermi", "gauss", "nuttall", "blackman_nuttall", "hann", "blackman_harris", "rectangular".
    "filter_range": 0.60,
    #: float: Range parameter for the FFT deconvolution filter (if applicable).
    "filter_parameter": 0.0,
    #: float: Additional parameter for the FFT deconvolution filter (if applicable).
    "deconv_mode": "bayesian",
    #: str: Deconvolution method. Options: 'bayesian', 'fft', 'lasso'.
    "bay_steps": 1000,
    #: int: Number of steps for Bayesian deconvolution.
    "pad_factor_pre": 0.01,
    #: float: Padding factor to prepend zeros before deconvolution.
    "pad_factor_after": 0.01,
    #: float: Padding factor to append zeros after deconvolution.
    "lasso_alpha": 1e-4,
    #: array-like or float: Regularization parameter(s) for Lasso deconvolution. If ``lasso_cv_folds`` > 1, this should be an array-like object of alpha values to test. If ``lasso_cv_folds`` is 1, this must be a single float value.
    "lasso_max_iter": 10000,
    #: int: Maximum number of iterations for Lasso deconvolution.
    "lasso_tol": 1e-4,
    #: float: Tolerance for convergence in Lasso deconvolution.
    "lasso_cv_folds": 1,
    #: int: Number of cross-validation folds for Lasso deconvolution. If > 1, ``LassoCV`` is used to find the best alpha from the ``lasso_alpha`` array. If 1, standard ``Lasso`` is used with a single ``lasso_alpha`` value.
    "lasso_selection": "cyclic",
    #: str: Selection method for Lasso deconvolution. Options: "cyclic", "random".
    "lasso_precompute": True,
    #: bool: Whether to precompute the Gram matrix for Lasso deconvolution. This can speed up the process, especially for large datasets.
    #
    # Structure Function settings
    "struc_method": "sobhy",
    #: str: Method for structure function calculation. Options: "sobhy", "lanczos", "boor_golub", "khatwani", "polylong".
    "timespec_interpolate_factor": 1.0,
    #: float: Interpolation factor for the time constant spectrum (used by Lanczos).
    "blockwise_sum_width": 20,
    #: int: Number of RC rungs to combine for smoothing (used by Lanczos).
    #
    # Theoretical settings
    "theo_inverse_specs": None,
    #: dict | None: Dictionary of theoretical inverse specifications.
    "theo_resistances": None,
    #: list | None: List of resistances for the theoretical Foster network model.
    "theo_capacitances": None,
    #: list | None: List of capacitances for the theoretical Foster network model.
    "theo_time": [4e-8, 1e3],
    #: list[float, float]: Time range [start, end] in seconds for theoretical model calculation.
    "theo_time_size": 30000,
    #: int: Number of time points for the theoretical model calculation.
    "signal_to_noise_ratio": 100,
    #: float: Signal-to-noise ratio for adding noise to theoretical impedance data.
    "theo_delta": 0.5 * (2 * np.pi / 360),
    #: float: Angle (radians) to rotate Z(s) into the complex plane for theoretical calculations to avoid singularities.
    #
    # K-factor and voltage conversion, and extrapolate settings
    "calib": None,
    #: np.ndarray | None: 2D array of calibration data [temps, voltages]. Required if input_mode is 'voltage'.
    "kfac_fit_deg": 2,
    #: int: Degree of the polynomial fit for K-factor calculation from calibration data.
    "extrapolate": True,
    #: bool: Whether to extrapolate the thermal response using a sqrt(time) fit at early times.
    "lower_fit_limit": None,
    #: float | None: Lower time limit (seconds) for the extrapolation fit range. Defaults to the start of the data if None.
    "upper_fit_limit": None,
    #: float | None: Upper time limit (seconds) for the extrapolation fit range. Defaults to a fraction of the total time if None.
    "data_cut_lower": 0,
    #: int: Index to cut data; points below this index are excluded from the transient analysis.
    "data_cut_upper": float("inf"),
    #: int | float: Index to cut data; points above this index are excluded from the transient analysis.
    "temp_0_avg_range": (0, 1),
    #: tuple[int, int]: Index range (start, end) to average the initial temperature/voltage to determine the baseline.
    #
    # Power settings
    "power_step": 1.0,
    #: float: Power step [W] applied during the measurement. Used for impedance calculation.
    "power_scale_factor": 1.0,
    #: float: Scaling factor applied to power, useful for analyzing multiple DUTs in series to get per-component properties.
    "optical_power": 0.0,
    #: float: Optical power [W] to subtract, relevant for LED testing.
    "is_heating": False,
    #: bool: True if the transient corresponds to a heating step (positive power), False for cooling (negative power step).
    "power_data": None,
    #: np.ndarray | None: Excitation power curve for temperature prediction. 2D array: [time, power].
    "lin_sampling_period": 1e-6,
    #: float: Sampling period [s] for linear interpolation of the impulse response in temperature prediction. Should satisfy Nyquist criterion for the system's time constants.
    #
    # Window and derivative settings
    "minimum_window_length": 0.35,
    #: float: Minimum window length (in log10(time) units) for the adaptive derivative calculation.
    "maximum_window_length": 3.0,
    #: float: Maximum window length (in log10(time) units) for the adaptive derivative calculation.
    "minimum_window_size": 70,
    #: int: Minimum number of data points within the derivative calculation window.
    "window_increment": 0.1,
    #: float: Increment (+/-) applied to the window length during the adaptive derivative calculation update step.
    "expected_var": 0.09,
    #: float: Expected variance of the noise in the thermal transient data, used in derivative calculation.
    "min_index": 3,
    #: int: Minimum index from which to start the derivative calculation.
    #
    # Optimization settings
    "opt_recalc_forward": False,
    #: bool: Whether to recalculate the forward solution during optimization (relevant for specific NID methods).
    "opt_use_extrapolate": True,
    #: bool: Whether to use the extrapolated impedance curve during optimization.
    "opt_method": "Powell",
    #: str: Optimization method to use (passed to scipy.optimize.minimize).
    "struc_init_method": "optimal_fit",
    #: str: Method to determine the initial structure function approximation for optimization.
    "opt_model_layers": 10,
    #: int: Number of RC layers (Foster elements) for the optimization model.
    #
    # Procedural settings
    "input_mode": "impedance",
    #: str: Input data type. Options: 'impedance', 'temperature', 'voltage'. Determines initial processing steps.
    "calc_struc": True,
    #: bool: Whether to calculate the structure function after impedance calculation.
    "only_make_z": False,
    #: bool: If True, only calculate the impedance curve and skip spectrum/structure function steps.
    "repetitions": 1000,
    #: int: Number of repetitions for bootstrapping analysis.
    "random_seed": None,
    #: int | None: Random seed for bootstrapping to ensure reproducibility.
    "bootstrap_mode": "from_data",
    #: str: Method for generating bootstrap samples. Options: "from_theo", "from_data", "given", "given_with_opt".
    #
    # standard_evaluation_set settings
    "normalize_impedance_to_previous": False,
    #: bool: In batch processing, normalize subsequent impedance curves to the first one.
    "evaluation_type": "standard",
    #: str: Type of evaluation module to run within `standard_module_set`.
    "iterable_keywords": [],
    #: list[str]: List of keyword argument names that should be iterated over in `standard_module_set`. The corresponding values should be lists.
    #
    # I/O settings
    "data": None,
    #: np.ndarray | None: Input data. 2D array: [time, measurement (temp/voltage/impedance)]. Should be provided by the user.
    "output_dir": "output",
    #: str: Base directory for saving output files.
    "label": "no_label",
    #: str: Label used for naming output files and figures. Should be set by the user.
    #
    # T3ster Interface Settings
    "infile": None,
    #: str | None: Input file path for T3ster data files.
    "infile_pwr": None,
    #: str | None: Input file path for T3ster power files.
    "infile_tco": None,
    #: str | None: Input file path for T3ster calibration files.
    #
    # Image settings (Potentially related to plotting/figure generation counts)
    "total_calls": 1,
    #: int: Counter, possibly related to the number of analysis calls.
    "fig_total_calls": 1,
    #: int: Counter, possibly related to the number of figures generated.
}


std_output_defaults: dict = {
    "save_voltage": True,
    #: bool: Save calculated voltage data.
    "save_temperature": True,
    #: bool: Save calculated temperature data.
    "save_impedance": True,
    #: bool: Save calculated thermal impedance (Zth) data.
    "save_impedance_smooth": True,
    #: bool: Save smoothed thermal impedance data.
    "save_extrpl": True,
    #: bool: Save extrapolated impedance data.
    "save_derivative": True,
    #: bool: Save calculated logarithmic time derivative of Zth.
    "save_back_impedance": True,
    #: bool: Save impedance recalculated from the time constant spectrum.
    "save_back_derivative": True,
    #: bool: Save derivative recalculated from the time constant spectrum.
    "save_frequency": True,
    #: bool: Save frequency domain data (if applicable).
    "save_time_spec": True,
    #: bool: Save the calculated time constant spectrum (tau*Rth vs tau).
    "save_sum_time_spec": True,
    #: bool: Save the cumulative sum of the time constant spectrum.
    "save_diff_struc": True,
    #: bool: Save the differential structure function (dRth/dCth vs Cth).
    "save_cumul_struc": True,
    #: bool: Save the cumulative structure function (Rth vs Cth).
    "save_local_resist_struc": True,
    #: bool: Save local resistance structure function data.
    "save_theo_struc": True,
    #: bool: Save theoretical structure function data.
    "save_theo_diff_struc": True,
    #: bool: Save theoretical differential structure function data.
    "save_theo_time_const": True,
    #: bool: Save theoretical time constant spectrum data.
    "save_theo_imp_deriv": True,
    #: bool: Save theoretical impedance derivative data.
    "save_theo_impedance": True,
    #: bool: Save theoretical impedance data.
    "save_time_const_comparison": True,
    #: bool: Save data comparing time constant spectra (e.g., measured vs theoretical).
    "save_struc_comparison": True,
    #: bool: Save data comparing structure functions.
    "save_total_resist_comparison": True,
    #: bool: Save data comparing total thermal resistances.
    "save_boot_impedance": True,
    #: bool: Save bootstrapped impedance results.
    "save_boot_deriv": True,
    #: bool: Save bootstrapped derivative results.
    "save_boot_time_spec": True,
    #: bool: Save bootstrapped time constant spectrum results.
    "save_boot_sum_time_spec": True,
    #: bool: Save bootstrapped cumulative time constant spectrum results.
    "save_boot_cumul_struc": True,
    #: bool: Save bootstrapped cumulative structure function results.
    "save_prediction": True,
    #: bool: Save temperature prediction results.
    "save_residual": True,
    #: bool: Save residual data (e.g., difference between prediction and measurement).
    "look_at_raw_data": True,
    #: bool: Generate plot of raw input data.
    "look_at_extrpl": True,
    #: bool: Generate plot showing extrapolation fit.
    "look_at_temp": True,
    #: bool: Generate plot of temperature vs time.
    "look_at_voltage": True,
    #: bool: Generate plot of voltage vs time.
    "look_at_impedance": True,
    #: bool: Generate plot of thermal impedance vs time.
    "look_at_deriv": True,
    #: bool: Generate plot of logarithmic time derivative vs time.
    "look_at_fft": True,
    #: bool: Generate plot related to FFT processing (if used).
    "look_at_time_spec": True,
    #: bool: Generate plot of the time constant spectrum.
    "look_at_cumul_struc": True,
    #: bool: Generate plot of the cumulative structure function.
    "look_at_diff_struc": True,
    #: bool: Generate plot of the differential structure function.
    "look_at_local_resist": True,
    #: bool: Generate plot of the local resistance structure function.
    "look_at_local_gradient": True,
    #: bool: Generate plot of the local gradient structure function.
    "look_at_theo_cstruc": True,
    #: bool: Generate plot of the theoretical cumulative structure function.
    "look_at_theo_diff_struc": True,
    #: bool: Generate plot of the theoretical differential structure function.
    "look_at_theo_time_const": True,
    #: bool: Generate plot of the theoretical time constant spectrum.
    "look_at_theo_sum_time_const": True,
    #: bool: Generate plot of the theoretical cumulative time constant spectrum.
    "look_at_theo_imp_deriv": True,
    #: bool: Generate plot of the theoretical impedance derivative.
    "look_at_theo_impedance": True,
    #: bool: Generate plot of the theoretical impedance.
    "look_at_theo_backwards_impedance": True,
    #: bool: Generate plot of impedance recalculated from theoretical spectrum.
    "look_at_backwards_imp_deriv": True,
    #: bool: Generate plot of derivative recalculated from measured spectrum.
    "look_at_backwards_impedance": True,
    #: bool: Generate plot of impedance recalculated from measured spectrum.
    "look_at_sum_time_spec": True,
    #: bool: Generate plot of the cumulative time constant spectrum.
    "look_at_optimize_struc": True,
    #: bool: Generate plot related to optimization results (structure function).
    "look_at_time_const_comparison": True,
    #: bool: Generate plot comparing time constant spectra.
    "look_at_struc_comparison": True,
    #: bool: Generate plot comparing structure functions.
    "look_at_total_resist_comparison": True,
    #: bool: Generate plot comparing total thermal resistances.
    "look_at_boot_impedance": True,
    #: bool: Generate plot of bootstrapped impedance results (e.g., with confidence intervals).
    "look_at_boot_deriv": True,
    #: bool: Generate plot of bootstrapped derivative results.
    "look_at_boot_time_spec": True,
    #: bool: Generate plot of bootstrapped time constant spectrum results.
    "look_at_boot_sum_time_spec": True,
    #: bool: Generate plot of bootstrapped cumulative time constant spectrum results.
    "look_at_boot_cumul_struc": True,
    #: bool: Generate plot of bootstrapped cumulative structure function results.
    "look_at_prediction": True,
    #: bool: Generate plot comparing predicted temperature with measured data.
    "look_at_prediction_figure": True,
    #: bool: Generate a specific figure related to temperature prediction.
    "look_at_residual": True,
    #: bool: Generate plot of the residuals from temperature prediction.
}
