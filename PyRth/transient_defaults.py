import numpy as np

import logging

logger = logging.getLogger("PyRthLogger")


def figure_logic(boole):
    return (boole or global_look_at) and not suppress_all_figures


def validate_and_merge_defaults(params, self_parameters):

    # This function is used to integrate the standard evaluation defaults and the standard output defaults into the parameters dictionary.

    # reject any keys that are not in the standard evaluation defaults or the standard output defaults and warn the user

    for key in params.keys():
        if (
            key not in std_eval_defaults.keys()
            and key not in std_output_defaults.keys()
        ):
            logger.warning(
                f"Parameter {key} is not a standard parameter and will be ignored."
            )

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

    return params


std_eval_defaults = {
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
    "theo_log_time_size": 30000,  # number of points in the logtime array for the theoretical model
    "theo_delta": 0.5
    * (
        2 * np.pi / 360
    ),  # angle to rotate Z(s) into the complex plane to avoid singularities (smaller is better, but makes peaks sharper)
    #
    # K-factor and voltage conversion, and extrapolate settings
    "calib": None,  # 2-d array of calibration data [temps, voltages], user should provide this
    "kfac_fit_deg": 2,  # degree of the polynomial fit for the K-factor
    "extrapolate": True,  # whether to extrapolate the thermal response  using square root of time
    "lower_fit_limit": 450,  # index of the first point to be used in the fit
    "upper_fit_limit": 1100,  # index of the last point to be used in the fit
    "data_cut_lower": 0,  # cut data below this is not part of the transient
    "data_cut_upper": float("inf"),  # cut data above this is not part of the transient
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
    "opt_extrapolate": True,  # whether to extrapolate the impedance curve during optimization
    "opt_method": "Powell",  # optimization method to use
    "struc_init_method": "optimal_fit",  # method to determine the initial structure function approximation
    "opt_model_layers": 10,  # number of layers for the optimization model
    #
    # Procedural settings
    "read_mode": "none",  # used to read the data from a different format
    "conv_mode": "none",  # used to convert the data to a different format
    "calc_struc": True,  # calculate the structure function
    "only_make_z": False,  # only make the impedance curve, dont calculate the time constant spectrum or structure function
    "repetitions": 1000,  # number of repetitions for bootstrapping
    "random_seed": None,  # random seed for bootstrapping
    "bootstrap_mode": "from_data",  # method to generate the bootstrap samples, options are "from_theo", "from_data", "given", "given_with_opt"
    #
    # standard_evaluation_set settings
    "normalize_impedance_to_previous": False,  # normalize the impedance curve to the previous impedance curve during standard_evaluation_set
    "evaluation_type": "standard",  # for standard_evaluation_set to choose the type
    "iterable_keywords": [],  # keywords that can be iterated over in standard_evaluation_set. Each such specified keyword should be a list of values
    #
    # I/O settings
    "output_dir": "output\\csv",  # output directory for csv files
    "label": "no_label",  # default label for output files, should be changed to something meaningful by the user
    #
    # T3ster Interface Settings
    "infile": None,  # input directory for data files, default is None
    "infile_pwr": None,  # input directory for T3ster power files, default is None
    "infile_tconst": None,  # input directory for T3ster time constant files, default is None
    #
    # Image settings
    "total_calls": 1,
    "fig_total_calls": 1,
}


global_look_at = False  # whether to look at all figures or not
suppress_all_figures = False  # whether to suppress all figures or not

# This dictionary, std_output_defaults, controls the saving and output behavior of the system.
# Each key-value pair represents a specific operation, where a value of True enables the operation, and False disables it.
std_output_defaults = {
    "fig_save_on": False,
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
    "save_boot_z_curve_figure": True,
    "save_boot_deriv_figure": True,
    "save_boot_time_spec": True,
    "save_boot_sum_time_spec": True,
    "save_boot_cumul_struc": True,
    "save_boot_cumul_struc_coarse": True,
    "save_prediction": True,
    "save_residual": True,
    "look_at_raw_data": figure_logic(True),
    "look_at_extrpl": figure_logic(True),
    "look_at_temp": figure_logic(True),
    "look_at_voltage": figure_logic(True),
    "look_at_z_curve": figure_logic(True),
    "look_at_deriv": figure_logic(True),
    "look_at_fft": figure_logic(True),
    "look_at_fft_weight": figure_logic(True),
    "look_at_lomb": figure_logic(True),
    "look_at_deconv": figure_logic(True),
    "look_at_bay": figure_logic(True),
    "look_at_time_spec": figure_logic(True),
    "look_at_cumul_struc": figure_logic(True),
    "look_at_diff_struc": figure_logic(True),
    "look_at_local_resist": figure_logic(True),
    "look_at_theo_cstruc": figure_logic(True),
    "look_at_theo_diff_struc": figure_logic(True),
    "look_at_theo_time_const": figure_logic(True),
    "look_at_theo_sum_time_const": figure_logic(True),
    "look_at_theo_imp_deriv": figure_logic(True),
    "look_at_theo_impedance": figure_logic(True),
    "look_at_backwards_imp_deriv": figure_logic(True),
    "look_at_backwards_impedance": figure_logic(True),
    "look_at_sum_time_spec": figure_logic(True),
    "look_at_theo_backwards_impedance": figure_logic(True),
    "look_at_optimize_struc_figure": figure_logic(True),
    "look_at_time_const_comparison": figure_logic(True),
    "look_at_struc_comparison": figure_logic(True),
    "look_at_total_resist_comparison": figure_logic(True),
    "look_at_boot_z_curve": figure_logic(True),
    "look_at_boot_deriv": figure_logic(True),
    "look_at_boot_time_spec": figure_logic(True),
    "look_at_boot_sum_time_spec": figure_logic(True),
    "look_at_boot_cumul_struc": figure_logic(True),
    "look_at_prediction_figure": figure_logic(True),
    "look_at_residual_figure": figure_logic(True),
}
