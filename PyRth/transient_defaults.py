"""Defaults and helpers for PyRth evaluation configuration.
This module defines dataclasses and utilities encapsulating the default
values for configuration options used across the PyRth evaluation pipeline.
The defaults can be overridden by passing keyword arguments to evaluation
methods (e.g., :py:meth:`~PyRth.transient_scripts.Evaluation.standard_module`).
See :ref:`Default Configuration <default-configuration-label>` for the rendered
documentation of every parameter."""

from __future__ import annotations

import logging
from dataclasses import MISSING, asdict, dataclass, field, replace
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import numpy as np

logger = logging.getLogger("PyRthLogger")
_last_logged_params: Dict[str, Any] = {}


def doc_field(*, default=MISSING, default_factory=MISSING, doc: str):
    """Attach documentation metadata to dataclass fields."""

    metadata = {"doc": doc}
    kwargs: Dict[str, Any] = {"metadata": metadata}
    if default is not MISSING:
        kwargs["default"] = default
    if default_factory is not MISSING:
        kwargs["default_factory"] = default_factory
    return field(**kwargs) # pylint: disable=invalid-field-call


@dataclass
class EvalDefaults:
    """Default parameters controlling evaluation routines."""

    precision: int = doc_field(
        default=250,
        doc="int: Number of points used for internal calculations involving the impedance curve.",
    )
    log_time_size: int = doc_field(
        default=250,
        doc="int: Number of points in the logarithmically spaced time array used for spectrum calculations.",
    )
    filter_name: str = doc_field(
        default="hann",
        doc='str: Name of the filter for FFT deconvolution. Options: "fermi", "gauss", "nuttall", "blackman_nuttall", "hann", "blackman_harris", "rectangular".',
    )
    filter_range: float = doc_field(
        default=0.60,
        doc="float: Range parameter for the FFT deconvolution filter (if applicable).",
    )
    filter_parameter: float = doc_field(
        default=0.0,
        doc="float: Additional parameter for the FFT deconvolution filter (if applicable).",
    )
    deconv_mode: str = doc_field(
        default="bayesian",
        doc="str: Deconvolution method. Options: 'bayesian', 'fft', 'lasso'.",
    )
    bay_steps: int = doc_field(
        default=1000,
        doc="int: Number of steps for Bayesian deconvolution.",
    )
    pad_factor_pre: float = doc_field(
        default=0.01,
        doc="float: Padding factor to prepend zeros before deconvolution.",
    )
    pad_factor_after: float = doc_field(
        default=0.01,
        doc="float: Padding factor to append zeros after deconvolution.",
    )
    lasso_alpha: float | Sequence[float] = doc_field(
        default=1e-4,
        doc="array-like or float: Regularization parameter(s) for Lasso deconvolution.",
    )
    lasso_max_iter: int = doc_field(
        default=10000,
        doc="int: Maximum number of iterations for Lasso deconvolution.",
    )
    lasso_tol: float = doc_field(
        default=1e-4,
        doc="float: Tolerance for convergence in Lasso deconvolution.",
    )
    lasso_cv_folds: int = doc_field(
        default=1,
        doc="int: Number of cross-validation folds for Lasso deconvolution.",
    )
    lasso_selection: str = doc_field(
        default="cyclic",
        doc='str: Selection method for Lasso deconvolution. Options: "cyclic", "random".',
    )
    lasso_precompute: bool = doc_field(
        default=True,
        doc="bool: Whether to precompute the Gram matrix for Lasso deconvolution.",
    )
    struc_method: str = doc_field(
        default="sobhy",
        doc='str: Method for structure function calculation. Options: "sobhy", "lanczos", "boor_golub", "khatwani", "polylong".',
    )
    timespec_interpolate_factor: float = doc_field(
        default=1.0,
        doc="float: Interpolation factor for the time constant spectrum (used by Lanczos).",
    )
    blockwise_sum_width: int = doc_field(
        default=20,
        doc="int: Number of RC rungs to combine for smoothing (used by Lanczos).",
    )
    theo_inverse_specs: Optional[Dict[str, Any]] = doc_field(
        default=None,
        doc="dict | None: Dictionary of theoretical inverse specifications.",
    )
    theo_resistances: Optional[List[float]] = doc_field(
        default=None,
        doc="list | None: List of resistances for the theoretical Foster network model.",
    )
    theo_capacitances: Optional[List[float]] = doc_field(
        default=None,
        doc="list | None: List of capacitances for the theoretical Foster network model.",
    )
    theo_time: List[float] = doc_field(
        default_factory=lambda: [4e-8, 1e3],
        doc="list[float, float]: Time range [start, end] in seconds for theoretical model calculation.",
    )
    theo_time_size: int = doc_field(
        default=30000,
        doc="int: Number of time points for the theoretical model calculation.",
    )
    signal_to_noise_ratio: float = doc_field(
        default=100.0,
        doc="float: Signal-to-noise ratio for adding noise to theoretical impedance data.",
    )
    theo_delta: float = doc_field(
        default=0.5 * (2 * np.pi / 360),
        doc="float: Angle (radians) to rotate Z(s) into the complex plane for theoretical calculations to avoid singularities.",
    )
    calib: Optional[np.ndarray] = doc_field(
        default=None,
        doc="np.ndarray | None: 2D array of calibration data [temps, voltages]. Required if input_mode is 'voltage'.",
    )
    kfac_fit_deg: int = doc_field(
        default=2,
        doc="int: Degree of the polynomial fit for K-factor calculation from calibration data.",
    )
    extrapolate: bool = doc_field(
        default=True,
        doc="bool: Whether to extrapolate the thermal response using a sqrt(time) fit at early times.",
    )
    lower_fit_limit: Optional[float] = doc_field(
        default=None,
        doc="float | None: Lower time limit (seconds) for the extrapolation fit range.",
    )
    upper_fit_limit: Optional[float] = doc_field(
        default=None,
        doc="float | None: Upper time limit (seconds) for the extrapolation fit range.",
    )
    data_cut_lower: int = doc_field(
        default=0,
        doc="int: Index to cut data; points below this index are excluded from the transient analysis.",
    )
    data_cut_upper: float = doc_field(
        default=float("inf"),
        doc="int | float: Index to cut data; points above this index are excluded from the transient analysis.",
    )
    temp_0_avg_range: Tuple[int, int] = doc_field(
        default=(0, 1),
        doc="tuple[int, int]: Index range (start, end) to average the initial temperature/voltage to determine the baseline.",
    )
    power_step: float = doc_field(
        default=1.0,
        doc="float: Power step [W] applied during the measurement. Used for impedance calculation.",
    )
    power_scale_factor: float = doc_field(
        default=1.0,
        doc="float: Scaling factor applied to power, useful for analyzing multiple DUTs in series to get per-component properties.",
    )
    optical_power: float = doc_field(
        default=0.0,
        doc="float: Optical power [W] to subtract, relevant for LED testing.",
    )
    is_heating: bool = doc_field(
        default=False,
        doc="bool: True if the transient corresponds to a heating step (positive power), False for cooling.",
    )
    power_data: Optional[np.ndarray] = doc_field(
        default=None,
        doc="np.ndarray | None: Excitation power curve for temperature prediction. 2D array: [time, power].",
    )
    lin_sampling_period: float = doc_field(
        default=1e-6,
        doc="float: Sampling period [s] for linear interpolation of the impulse response in temperature prediction.",
    )
    minimum_window_length: float = doc_field(
        default=0.35,
        doc="float: Minimum window length (in log10(time) units) for the adaptive derivative calculation.",
    )
    maximum_window_length: float = doc_field(
        default=3.0,
        doc="float: Maximum window length (in log10(time) units) for the adaptive derivative calculation.",
    )
    minimum_window_size: int = doc_field(
        default=70,
        doc="int: Minimum number of data points within the derivative calculation window.",
    )
    window_increment: float = doc_field(
        default=0.1,
        doc="float: Increment (+/-) applied to the window length during the adaptive derivative calculation update step.",
    )
    expected_var: float = doc_field(
        default=0.09,
        doc="float: Expected variance of the noise in the thermal transient data, used in derivative calculation.",
    )
    min_index: int = doc_field(
        default=3,
        doc="int: Minimum index from which to start the derivative calculation.",
    )
    opt_recalc_forward: bool = doc_field(
        default=False,
        doc="bool: Whether to recalculate the forward solution during optimization.",
    )
    opt_use_extrapolate: bool = doc_field(
        default=True,
        doc="bool: Whether to use the extrapolated impedance curve during optimization.",
    )
    opt_method: str = doc_field(
        default="Powell",
        doc="str: Optimization method to use (passed to scipy.optimize.minimize).",
    )
    struc_init_method: str = doc_field(
        default="optimal_fit",
        doc="str: Method to determine the initial structure function approximation for optimization.",
    )
    opt_model_layers: int = doc_field(
        default=10,
        doc="int: Number of RC layers (Foster elements) for the optimization model.",
    )
    input_mode: str = doc_field(
        default="impedance",
        doc="str: Input data type. Options: 'impedance', 'temperature', 'voltage'.",
    )
    calc_struc: bool = doc_field(
        default=True,
        doc="bool: Whether to calculate the structure function after impedance calculation.",
    )
    only_make_z: bool = doc_field(
        default=False,
        doc="bool: If True, only calculate the impedance curve and skip spectrum/structure function steps.",
    )
    repetitions: int = doc_field(
        default=1000,
        doc="int: Number of repetitions for bootstrapping analysis.",
    )
    random_seed: Optional[int] = doc_field(
        default=None,
        doc="int | None: Random seed for bootstrapping to ensure reproducibility.",
    )
    bootstrap_mode: str = doc_field(
        default="from_data",
        doc='str: Method for generating bootstrap samples. Options: "from_theo", "from_data", "given", "given_with_opt".',
    )
    normalize_impedance_to_previous: bool = doc_field(
        default=False,
        doc="bool: In batch processing, normalize subsequent impedance curves to the first one.",
    )
    evaluation_type: str = doc_field(
        default="standard",
        doc="str: Type of evaluation module to run within `standard_module_set`.",
    )
    iterable_keywords: List[str] = doc_field(
        default_factory=list,
        doc="list[str]: Keyword argument names that should be iterated over in `standard_module_set`.",
    )
    data: Optional[np.ndarray] = doc_field(
        default=None,
        doc="np.ndarray | None: Input data. 2D array: [time, measurement].",
    )
    output_dir: str = doc_field(
        default="output",
        doc="str: Base directory for saving output files.",
    )
    label: str = doc_field(
        default="no_label",
        doc="str: Label used for naming output files and figures.",
    )
    infile: Optional[str] = doc_field(
        default=None,
        doc="str | None: Input file path for T3ster data files.",
    )
    infile_pwr: Optional[str] = doc_field(
        default=None,
        doc="str | None: Input file path for T3ster power files.",
    )
    infile_tco: Optional[str] = doc_field(
        default=None,
        doc="str | None: Input file path for T3ster calibration files.",
    )
    total_calls: int = doc_field(
        default=1,
        doc="int: Counter, possibly related to the number of analysis calls.",
    )
    fig_total_calls: int = doc_field(
        default=1,
        doc="int: Counter, possibly related to the number of figures generated.",
    )


@dataclass
class OutputDefaults:
    """Output-related booleans controlling serialization and charting."""

    save_voltage: bool = doc_field(default=True, doc="bool: Save calculated voltage data.")
    save_temperature: bool = doc_field(
        default=True, doc="bool: Save calculated temperature data."
    )
    save_impedance: bool = doc_field(
        default=True, doc="bool: Save calculated thermal impedance (Zth) data."
    )
    save_impedance_smooth: bool = doc_field(
        default=True, doc="bool: Save smoothed thermal impedance data."
    )
    save_extrpl: bool = doc_field(
        default=True, doc="bool: Save extrapolated impedance data."
    )
    save_derivative: bool = doc_field(
        default=True, doc="bool: Save calculated logarithmic time derivative of Zth."
    )
    save_back_impedance: bool = doc_field(
        default=True, doc="bool: Save impedance recalculated from the time constant spectrum."
    )
    save_back_derivative: bool = doc_field(
        default=True, doc="bool: Save derivative recalculated from the time constant spectrum."
    )
    save_frequency: bool = doc_field(
        default=True, doc="bool: Save frequency domain data (if applicable)."
    )
    save_time_spec: bool = doc_field(
        default=True, doc="bool: Save the calculated time constant spectrum (tau*Rth vs tau)."
    )
    save_sum_time_spec: bool = doc_field(
        default=True, doc="bool: Save the cumulative sum of the time constant spectrum."
    )
    save_diff_struc: bool = doc_field(
        default=True, doc="bool: Save the differential structure function (dRth/dCth vs Cth)."
    )
    save_cumul_struc: bool = doc_field(
        default=True, doc="bool: Save the cumulative structure function (Rth vs Cth)."
    )
    save_local_resist_struc: bool = doc_field(
        default=True, doc="bool: Save local resistance structure function data."
    )
    save_theo_struc: bool = doc_field(
        default=True, doc="bool: Save theoretical structure function data."
    )
    save_theo_diff_struc: bool = doc_field(
        default=True, doc="bool: Save theoretical differential structure function data."
    )
    save_theo_time_const: bool = doc_field(
        default=True, doc="bool: Save theoretical time constant spectrum data."
    )
    save_theo_imp_deriv: bool = doc_field(
        default=True, doc="bool: Save theoretical impedance derivative data."
    )
    save_theo_impedance: bool = doc_field(
        default=True, doc="bool: Save theoretical impedance data."
    )
    save_time_const_comparison: bool = doc_field(
        default=True, doc="bool: Save data comparing time constant spectra."
    )
    save_struc_comparison: bool = doc_field(
        default=True, doc="bool: Save data comparing structure functions."
    )
    save_total_resist_comparison: bool = doc_field(
        default=True, doc="bool: Save data comparing total thermal resistances."
    )
    save_boot_impedance: bool = doc_field(
        default=True, doc="bool: Save bootstrapped impedance results."
    )
    save_boot_deriv: bool = doc_field(
        default=True, doc="bool: Save bootstrapped derivative results."
    )
    save_boot_time_spec: bool = doc_field(
        default=True, doc="bool: Save bootstrapped time constant spectrum results."
    )
    save_boot_sum_time_spec: bool = doc_field(
        default=True, doc="bool: Save bootstrapped cumulative time constant spectrum results."
    )
    save_boot_cumul_struc: bool = doc_field(
        default=True, doc="bool: Save bootstrapped cumulative structure function results."
    )
    save_prediction: bool = doc_field(
        default=True, doc="bool: Save temperature prediction results."
    )
    save_residual: bool = doc_field(
        default=True, doc="bool: Save residual data (e.g., difference between prediction and measurement)."
    )
    look_at_raw_data: bool = doc_field(
        default=True, doc="bool: Generate plot of raw input data."
    )
    look_at_extrpl: bool = doc_field(
        default=True, doc="bool: Generate plot showing extrapolation fit."
    )
    look_at_temp: bool = doc_field(
        default=True, doc="bool: Generate plot of temperature vs time."
    )
    look_at_voltage: bool = doc_field(
        default=True, doc="bool: Generate plot of voltage vs time."
    )
    look_at_impedance: bool = doc_field(
        default=True, doc="bool: Generate plot of thermal impedance vs time."
    )
    look_at_deriv: bool = doc_field(
        default=True, doc="bool: Generate plot of logarithmic time derivative vs time."
    )
    look_at_fft: bool = doc_field(
        default=True, doc="bool: Generate plot related to FFT processing (if used)."
    )
    look_at_time_spec: bool = doc_field(
        default=True, doc="bool: Generate plot of the time constant spectrum."
    )
    look_at_cumul_struc: bool = doc_field(
        default=True, doc="bool: Generate plot of the cumulative structure function."
    )
    look_at_diff_struc: bool = doc_field(
        default=True, doc="bool: Generate plot of the differential structure function."
    )
    look_at_local_resist: bool = doc_field(
        default=True, doc="bool: Generate plot of the local resistance structure function."
    )
    look_at_local_gradient: bool = doc_field(
        default=True, doc="bool: Generate plot of the local gradient structure function."
    )
    look_at_theo_cstruc: bool = doc_field(
        default=True, doc="bool: Generate plot of the theoretical cumulative structure function."
    )
    look_at_theo_diff_struc: bool = doc_field(
        default=True, doc="bool: Generate plot of the theoretical differential structure function."
    )
    look_at_theo_time_const: bool = doc_field(
        default=True, doc="bool: Generate plot of the theoretical time constant spectrum."
    )
    look_at_theo_sum_time_const: bool = doc_field(
        default=True, doc="bool: Generate plot of the theoretical cumulative time constant spectrum."
    )
    look_at_theo_imp_deriv: bool = doc_field(
        default=True, doc="bool: Generate plot of the theoretical impedance derivative."
    )
    look_at_theo_impedance: bool = doc_field(
        default=True, doc="bool: Generate plot of the theoretical impedance."
    )
    look_at_theo_backwards_impedance: bool = doc_field(
        default=True, doc="bool: Generate plot of impedance recalculated from theoretical spectrum."
    )
    look_at_backwards_imp_deriv: bool = doc_field(
        default=True, doc="bool: Generate plot of derivative recalculated from measured spectrum."
    )
    look_at_backwards_impedance: bool = doc_field(
        default=True, doc="bool: Generate plot of impedance recalculated from measured spectrum."
    )
    look_at_sum_time_spec: bool = doc_field(
        default=True, doc="bool: Generate plot of the cumulative time constant spectrum."
    )
    look_at_optimize_struc: bool = doc_field(
        default=True, doc="bool: Generate plot related to optimization results (structure function)."
    )
    look_at_time_const_comparison: bool = doc_field(
        default=True, doc="bool: Generate plot comparing time constant spectra."
    )
    look_at_struc_comparison: bool = doc_field(
        default=True, doc="bool: Generate plot comparing structure functions."
    )
    look_at_total_resist_comparison: bool = doc_field(
        default=True, doc="bool: Generate plot comparing total thermal resistances."
    )
    look_at_boot_impedance: bool = doc_field(
        default=True, doc="bool: Generate plot of bootstrapped impedance results."
    )
    look_at_boot_deriv: bool = doc_field(
        default=True, doc="bool: Generate plot of bootstrapped derivative results."
    )
    look_at_boot_time_spec: bool = doc_field(
        default=True, doc="bool: Generate plot of bootstrapped time constant spectrum results."
    )
    look_at_boot_sum_time_spec: bool = doc_field(
        default=True, doc="bool: Generate plot of bootstrapped cumulative time constant spectrum results."
    )
    look_at_boot_cumul_struc: bool = doc_field(
        default=True, doc="bool: Generate plot of bootstrapped cumulative structure function results."
    )
    look_at_prediction: bool = doc_field(
        default=True, doc="bool: Generate plot comparing predicted temperature with measured data."
    )
    look_at_prediction_figure: bool = doc_field(
        default=True, doc="bool: Generate a specific figure related to temperature prediction."
    )
    look_at_residual: bool = doc_field(
        default=True, doc="bool: Generate plot of the residuals from temperature prediction."
    )


@dataclass
class StructureParameters(EvalDefaults, OutputDefaults):
    """Combined defaults spanning evaluation and output settings."""


DEFAULT_EVAL = EvalDefaults()
DEFAULT_OUTPUT = OutputDefaults()
DEFAULT_PARAMETERS = StructureParameters()

std_eval_defaults: Dict[str, Any] = asdict(DEFAULT_EVAL)
std_output_defaults: Dict[str, Any] = asdict(DEFAULT_OUTPUT)
_ALL_DEFAULTS: Dict[str, Any] = asdict(DEFAULT_PARAMETERS)
_ALL_DEFAULT_KEYS = set(_ALL_DEFAULTS.keys())


def deep_equals(val1, val2):
    """Compare potentially nested values, supporting numpy arrays."""

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


def copy_parameters(
    params: Optional[StructureParameters | Mapping[str, Any]] = None,
) -> StructureParameters | Dict[str, Any]:
    """Clone a parameter container, returning a dataclass or dict copy."""

    if params is None:
        return replace(DEFAULT_PARAMETERS)
    if isinstance(params, StructureParameters):
        return replace(params)
    if isinstance(params, Mapping):
        return dict(params)
    raise TypeError("Unsupported parameter container" )


def parameters_to_dict(
    params: Optional[StructureParameters | Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Normalize a parameter container to a plain dictionary."""

    if params is None:
        return asdict(DEFAULT_PARAMETERS)
    if isinstance(params, StructureParameters):
        return asdict(params)
    if isinstance(params, Mapping):
        return dict(params)
    raise TypeError("Unsupported parameter container")


def validate_and_merge_defaults(
    params: Mapping[str, Any],
    self_parameters: Optional[StructureParameters | Mapping[str, Any]] = None,
) -> StructureParameters | Dict[str, Any]:
    """Merge overrides into the provided parameter container while logging deviations."""

    merged = copy_parameters(self_parameters)

    for key, value in params.items():
        if key not in _ALL_DEFAULT_KEYS:
            logger.warning(
                "Parameter %s is not a standard parameter and will be ignored.", key
            )
            continue

        if isinstance(merged, StructureParameters):
            setattr(merged, key, value)
        else:
            merged[key] = value
        default_value = _ALL_DEFAULTS.get(key)

        if key in {"data", "calib"} and value is not None:
            try:
                shape = value.shape
                sig = (shape, type(value))
                if _last_logged_params.get(key) != sig:
                    logger.debug("%s: shape=%s", key, shape)
                    _last_logged_params[key] = sig
            except AttributeError:
                sig = ("object", type(value))
                if _last_logged_params.get(key) != sig:
                    logger.debug("%s: object type=%s", key, type(value))
                    _last_logged_params[key] = sig
            continue

        is_equal = deep_equals(value, default_value)
        if isinstance(is_equal, np.ndarray):
            is_equal = is_equal.all()
        if not bool(is_equal):
            sig = ("value", repr(value))
            if _last_logged_params.get(key) != sig:
                logger.debug("using non-default %s: %s", key, value)
                _last_logged_params[key] = sig

    return merged


def iter_default_items(include_output: bool = True) -> Iterable[Tuple[str, Any]]:
    """Iterate over default key/value pairs, optionally including output flags."""

    for key, value in std_eval_defaults.items():
        yield key, value
    if include_output:
        for key, value in std_output_defaults.items():
            yield key, value
