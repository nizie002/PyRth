import numpy as np


def figure_logic(boole):
    return (boole or global_look_at) and not suppress_all_figures


std_eval_defaults = {
    # Numerical Settings
    "precision": 250,
    "log_time_size": 250,
    # deconvolution settings
    "filter_name": "hann",
    "filter_range": 0.60,
    "filter_parameter": 0.0,
    "bayesian": True,
    "bay_steps": 1000,
    "pad_factor_pre": 0.01,
    "pad_factor_after": 0.01,
    # Structure Function settings
    "timespec_interpolate_factor": 1.0,
    "blockwise_sum_width": 20,
    "struc_method": "sobhy",
    # Theoretical settings
    "theo_log_time_size": 30000,
    "theo_realistic_z": False,
    "theo_z_cut": [-20, 10],
    "theo_delta": 0.5 * (2 * np.pi / 360),
    "theo_added_noise": 0.0,
    # K-factor and voltage conversion settings
    "kfac_fit_deg": 2,
    "extrapolate": True,
    "lower_fit_limit": 450,
    "upper_fit_limit": 1100,
    # Power settings
    "power_step": 1.0,
    "power_scale_factor": 1.0,
    "optical_power": 0.0,
    "is_heating": False,
    # Window and derivative settings
    "best_window_length": None,
    "minimum_window_length": 0.35,
    "maximum_window_length": 3.0,
    "minimum_window_size": 70,
    "window_increment": 0.1,
    "expected_var": 0.09,
    "min_index": 3,
    # Optimization settings
    "opt_recalc_forward": False,
    "opt_extrapolate": True,
    "opt_method": "Powell",
    "struc_init_method": "optimal_fit",
    "opt_model_layers": 10,
    # Procedural settings
    "read_mode": "none",
    "conv_mode": "none",
    "calc_struc": True,
    "only_make_z": False,
    "normalize_impedance_to_previous": False,
    "crop_factor": int(1),
    # I/O settings
    "output_dir": "output\\csv",
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
