import numpy as np

import logging

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
    "precision": 250,  # number of points in the impedance curve
    "log_time_size": 250,  # number of points in the logtime array
    #
    # deconvolution settings
    "filter_name": "hann",  # name of the filter to use for deconvolution, options: "fermi", "gauss", "nuttall", "blackman_nuttall", "hann", "blackman_harris", "rectangular"
    "filter_range": 0.60,  # range of the filter for applicable during fft deconvolution
    "filter_parameter": 0.0,  # parameter for the filter of applicable during fft deconvolution
    "bayesian": True,  # whether to use bayesian deconvolution (recommended)
    "bay_steps": 1000,  # number of steps for the bayesian deconvolution
    "pad_factor_pre": 0.01,  # padding factor for the deconvolution to append zeros to the beginning
    "pad_factor_after": 0.01,  # padding factor for the deconvolution to append zeros to the end
    #
    # Structure Function settings
    "struc_method": "sobhy",  # method to calculate the structure function: options are "sobhy", "lanczos", "boor_golub", "khatwani", and "polylong"
    "timespec_interpolate_factor": 1.0,  # factor to interpolate the time constant spectrum using for lanczos
    "blockwise_sum_width": 20,  # number of rungs to combine during lanczos for smoothing
    #
    # Theoretical settings
    "theo_inverse_specs": None,  # dictionary of theoretical inverse specifications, optional to not get in conflict with the optimization parameters
    "theo_resistances": None,  # list of resistances for the theoretical model, user should provide this
    "theo_capacitances": None,  # list of capacitances for the theoretical model, user should provide this
    "theo_time": [4e-8, 1e3],  # range of the time for the theoretical model in seconds
    "theo_time_size": 30000,  # number of points in the time array for the theoretical model
    "signal_to_noise_ratio": 100,  # signal to noise ratio for added noise in theoretical impedances
    "theo_delta": 0.5
    * (
        2 * np.pi / 360
    ),  # angle to rotate Z(s) into the complex plane to avoid singularities (smaller is better, but makes peaks sharper)
    #
    # K-factor and voltage conversion, and extrapolate settings
    "calib": None,  # 2-d array of calibration data [temps, voltages], user should provide this
    "kfac_fit_deg": 2,  # degree of the polynomial fit for the K-factor
    "extrapolate": True,  # whether to extrapolate the thermal response using square root of time fit
    "lower_fit_limit": None,  # time in seconds where to start the extrapolation fit
    "upper_fit_limit": None,  # time in seconds where to end the extrapolation fit
    "data_cut_lower": 0,  # index to cut data, points below this are not part of the transient
    "data_cut_upper": float(
        "inf"
    ),  # index to cut data, points above this are not part of the transient
    "temp_0_avg_range": (
        0,
        1,
    ),  # range to average the temperature curve to determine the initial temperature
    #
    # Power settings
    "power_step": 1.0,  # power step in W
    "power_scale_factor": 1.0,  # used when analyzing multiple DUT in series and average per component properties are desired
    "optical_power": 0.0,  # used for LED testing to substract optical power in W
    "is_heating": False,  # whether the thermal transient is in repsonse to a negative or positive power step
    "power_data": None,  # excitation curves for temperature prediction evaluations, should be a 2-d array with time in the first column and power in the second
    "lin_sampling_period": 1e-6,  # sampling period for the linear interpolation of the impulse response. The sampling period should be at least twice as small as the smallest relevant time constant in your system (Nyquist criterion)
    #
    # Window and derivative settings
    "minimum_window_length": 0.35,  # minimum window length for the derivative calculation in units of logtime
    "maximum_window_length": 3.0,  # maximum window length for the derivative calculation in units of logtime
    "minimum_window_size": 70,  # minimum window size for the derivative calculation
    "window_increment": 0.1,  # +- window increment for derivative calculation in each update
    "expected_var": 0.09,  # expected variance of the thermal transient data
    "min_index": 3,  # minimum index for the derivative
    #
    # Optimization settings
    "opt_recalc_forward": False,  # whether to recalculate the forward solution during optimization (for smooth NID forward solution)
    "opt_use_extrapolate": True,  # whether to use extrapolate the impedance curve during optimization
    "opt_method": "Powell",  # optimization method to use
    "struc_init_method": "optimal_fit",  # method to determine the initial structure function approximation
    "opt_model_layers": 10,  # number of layers for the optimization model
    #
    # Procedural settings
    "conv_mode": "none",  # used to convert the data to a different format
    "calc_struc": True,  # calculate the structure function
    "only_make_z": False,  # only make the impedance curve, dont calculate the time constant spectrum or structure function
    "repetitions": 1000,  # number of repetitions for bootstrapping
    "random_seed": None,  # random seed for bootstrapping
    "bootstrap_mode": "from_data",  # method to generate the bootstrap samples, options are "from_theo", "from_data", "given", "given_with_opt"
    #
    # standard_evaluation_set settings
    "normalize_impedance_to_previous": False,  # normalize the impedance curve to the first impedance curve in the evaluation
    "evaluation_type": "standard",  # for standard_evaluation_set to choose the type
    "iterable_keywords": [],  # keywords that can be iterated over in standard_evaluation_set. Each such specified keyword should be a list of values
    #
    # I/O settings
    "data": None,  # data to be analyzed, should be a 2-d array with time in the first column and temperature or voltage in the second
    "output_dir": "output",  # output directory for files
    "label": "no_label",  # default label for output files, should be changed to something meaningful by the user
    #
    # T3ster Interface Settings
    "infile": None,  # input directory for data files, default is None
    "infile_pwr": None,  # input directory for T3ster power files, default is None
    "infile_tco": None,  # input directory for T3ster calibration files, default is None
    #
    # Image settings
    "total_calls": 1,
    "fig_total_calls": 1,
}


# This dictionary, std_output_defaults, controls the saving and output behavior of the system.
# Each key-value pair represents a specific operation, where a value of True enables the operation, and False disables it.
std_output_defaults: dict = {
    "save_voltage": True,
    "save_temperature": True,
    "save_impedance": True,
    "save_impedance_smooth": True,
    "save_derivative": True,
    "save_back_impedance": True,
    "save_back_derivative": True,
    "save_frequency": True,
    "save_time_spec": True,
    "save_sum_time_spec": True,
    "save_diff_struc": True,
    "save_cumul_struc": True,
    "save_local_resist_struc": True,
    "save_theo_struc": True,
    "save_theo_diff_struc": True,
    "save_theo_time_const": True,
    "save_theo_imp_deriv": True,
    "save_theo_impedance": True,
    "save_time_const_comparison": True,
    "save_struc_comparison": True,
    "save_total_resist_comparison": True,
    "save_boot_impedance": True,
    "save_boot_deriv": True,
    "save_boot_time_spec": True,
    "save_boot_sum_time_spec": True,
    "save_boot_cumul_struc": True,
    "save_prediction": True,
    "save_residual": True,
    "look_at_raw_data": True,
    "look_at_extrpl": True,
    "look_at_temp": True,
    "look_at_voltage": True,
    "look_at_impedance": True,
    "look_at_deriv": True,
    "look_at_fft": True,
    "look_at_time_spec": True,
    "look_at_cumul_struc": True,
    "look_at_diff_struc": True,
    "look_at_local_resist": True,
    "look_at_local_gradient": True,
    "look_at_theo_cstruc": True,
    "look_at_theo_diff_struc": True,
    "look_at_theo_time_const": True,
    "look_at_theo_sum_time_const": True,
    "look_at_theo_imp_deriv": True,
    "look_at_theo_impedance": True,
    "look_at_theo_backwards_impedance": True,
    "look_at_backwards_imp_deriv": True,
    "look_at_backwards_impedance": True,
    "look_at_sum_time_spec": True,
    "look_at_optimize_struc": True,
    "look_at_time_const_comparison": True,
    "look_at_struc_comparison": True,
    "look_at_total_resist_comparison": True,
    "look_at_boot_impedance": True,
    "look_at_boot_deriv": True,
    "look_at_boot_time_spec": True,
    "look_at_boot_sum_time_spec": True,
    "look_at_boot_cumul_struc": True,
    "look_at_prediction": True,
    "look_at_prediction_figure": True,
    "look_at_residual": True,
}
