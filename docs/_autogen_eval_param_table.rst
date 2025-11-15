Standard Evaluation Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``precision`` (default: 250)
    int: Number of points used for internal calculations involving the impedance curve.

``log_time_size`` (default: 250)
    int: Number of points in the logarithmically spaced time array used for spectrum calculations.

``filter_name`` (default: "hann")
    str: Name of the filter for FFT deconvolution. Options: "fermi", "gauss", "nuttall", "blackman_nuttall", "hann", "blackman_harris", "rectangular".

``filter_range`` (default: 0.6)
    float: Range parameter for the FFT deconvolution filter (if applicable).

``filter_parameter`` (default: 0.0)
    float: Additional parameter for the FFT deconvolution filter (if applicable).

``deconv_mode`` (default: "bayesian")
    str: Deconvolution method. Options: 'bayesian', 'fft', 'lasso'.

``bay_steps`` (default: 1000)
    int: Number of steps for Bayesian deconvolution.

``pad_factor_pre`` (default: 0.01)
    float: Padding factor to prepend zeros before deconvolution.

``pad_factor_after`` (default: 0.01)
    float: Padding factor to append zeros after deconvolution.

``lasso_alpha`` (default: 0.0001)
    array-like or float: Regularization parameter(s) for Lasso deconvolution.

``lasso_max_iter`` (default: 10000)
    int: Maximum number of iterations for Lasso deconvolution.

``lasso_tol`` (default: 0.0001)
    float: Tolerance for convergence in Lasso deconvolution.

``lasso_cv_folds`` (default: 1)
    int: Number of cross-validation folds for Lasso deconvolution.

``lasso_selection`` (default: "cyclic")
    str: Selection method for Lasso deconvolution. Options: "cyclic", "random".

``lasso_precompute`` (default: True)
    bool: Whether to precompute the Gram matrix for Lasso deconvolution.

``struc_method`` (default: "sobhy")
    str: Method for structure function calculation. Options: "sobhy", "lanczos", "boor_golub", "khatwani", "polylong".

``timespec_interpolate_factor`` (default: 1.0)
    float: Interpolation factor for the time constant spectrum (used by Lanczos).

``blockwise_sum_width`` (default: 20)
    int: Number of RC rungs to combine for smoothing (used by Lanczos).

``theo_inverse_specs`` (default: None)
    dict | None: Dictionary of theoretical inverse specifications.

``theo_resistances`` (default: None)
    list | None: List of resistances for the theoretical Foster network model.

``theo_capacitances`` (default: None)
    list | None: List of capacitances for the theoretical Foster network model.

``theo_time`` (default: [4e-08, 1000.0])
    list[float, float]: Time range [start, end] in seconds for theoretical model calculation.

``theo_time_size`` (default: 30000)
    int: Number of time points for the theoretical model calculation.

``signal_to_noise_ratio`` (default: 100.0)
    float: Signal-to-noise ratio for adding noise to theoretical impedance data.

``theo_delta`` (default: 0.008726646259971648)
    float: Angle (radians) to rotate Z(s) into the complex plane for theoretical calculations to avoid singularities.

``calib`` (default: None)
    np.ndarray | None: 2D array of calibration data [temps, voltages]. Required if input_mode is 'voltage'.

``kfac_fit_deg`` (default: 2)
    int: Degree of the polynomial fit for K-factor calculation from calibration data.

``extrapolate`` (default: True)
    bool: Whether to extrapolate the thermal response using a sqrt(time) fit at early times.

``lower_fit_limit`` (default: None)
    float | None: Lower time limit (seconds) for the extrapolation fit range.

``upper_fit_limit`` (default: None)
    float | None: Upper time limit (seconds) for the extrapolation fit range.

``data_cut_lower`` (default: 0)
    int: Index to cut data; points below this index are excluded from the transient analysis.

``data_cut_upper`` (default: float('inf'))
    int | float: Index to cut data; points above this index are excluded from the transient analysis.

``temp_0_avg_range`` (default: (0, 1))
    tuple[int, int]: Index range (start, end) to average the initial temperature/voltage to determine the baseline.

``power_step`` (default: 1.0)
    float: Power step [W] applied during the measurement. Used for impedance calculation.

``power_scale_factor`` (default: 1.0)
    float: Scaling factor applied to power, useful for analyzing multiple DUTs in series to get per-component properties.

``optical_power`` (default: 0.0)
    float: Optical power [W] to subtract, relevant for LED testing.

``is_heating`` (default: False)
    bool: True if the transient corresponds to a heating step (positive power), False for cooling.

``power_data`` (default: None)
    np.ndarray | None: Excitation power curve for temperature prediction. 2D array: [time, power].

``lin_sampling_period`` (default: 1e-06)
    float: Sampling period [s] for linear interpolation of the impulse response in temperature prediction.

``minimum_window_length`` (default: 0.35)
    float: Minimum window length (in log10(time) units) for the adaptive derivative calculation.

``maximum_window_length`` (default: 3.0)
    float: Maximum window length (in log10(time) units) for the adaptive derivative calculation.

``minimum_window_size`` (default: 70)
    int: Minimum number of data points within the derivative calculation window.

``window_increment`` (default: 0.1)
    float: Increment (+/-) applied to the window length during the adaptive derivative calculation update step.

``expected_var`` (default: 0.09)
    float: Expected variance of the noise in the thermal transient data, used in derivative calculation.

``min_index`` (default: 3)
    int: Minimum index from which to start the derivative calculation.

``opt_recalc_forward`` (default: False)
    bool: Whether to recalculate the forward solution during optimization.

``opt_use_extrapolate`` (default: True)
    bool: Whether to use the extrapolated impedance curve during optimization.

``opt_method`` (default: "Powell")
    str: Optimization method to use (passed to scipy.optimize.minimize).

``struc_init_method`` (default: "optimal_fit")
    str: Method to determine the initial structure function approximation for optimization.

``opt_model_layers`` (default: 10)
    int: Number of RC layers (Foster elements) for the optimization model.

``input_mode`` (default: "impedance")
    str: Input data type. Options: 'impedance', 'temperature', 'voltage'.

``calc_struc`` (default: True)
    bool: Whether to calculate the structure function after impedance calculation.

``only_make_z`` (default: False)
    bool: If True, only calculate the impedance curve and skip spectrum/structure function steps.

``repetitions`` (default: 1000)
    int: Number of repetitions for bootstrapping analysis.

``random_seed`` (default: None)
    int | None: Random seed for bootstrapping to ensure reproducibility.

``bootstrap_mode`` (default: "from_data")
    str: Method for generating bootstrap samples. Options: "from_theo", "from_data", "given", "given_with_opt".

``normalize_impedance_to_previous`` (default: False)
    bool: In batch processing, normalize subsequent impedance curves to the first one.

``evaluation_type`` (default: "standard")
    str: Type of evaluation module to run within `standard_module_set`.

``iterable_keywords`` (default: [])
    list[str]: Keyword argument names that should be iterated over in `standard_module_set`.

``data`` (default: None)
    np.ndarray | None: Input data. 2D array: [time, measurement].

``output_dir`` (default: "output")
    str: Base directory for saving output files.

``label`` (default: "no_label")
    str: Label used for naming output files and figures.

``infile`` (default: None)
    str | None: Input file path for T3ster data files.

``infile_pwr`` (default: None)
    str | None: Input file path for T3ster power files.

``infile_tco`` (default: None)
    str | None: Input file path for T3ster calibration files.

``total_calls`` (default: 1)
    int: Counter, possibly related to the number of analysis calls.

``fig_total_calls`` (default: 1)
    int: Counter, possibly related to the number of figures generated.

