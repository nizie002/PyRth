"""Core implementation of PyRth's structure-function pipeline.

This module hosts the glue that turns raw temperature/voltage/impedance
measurements into structure functions and equivalent Foster/Cauer ladders.
It orchestrates ingest, deconvolution, spectrum conditioning, and the
conversion algorithms described throughout the theory docs.
"""
import logging
from typing import Any, Mapping
import gmpy2 as gp
import numpy as np
import numpy.fft as fftpack
import numpy.polynomial.polynomial as poly
import scipy.interpolate as interp

from sklearn.linear_model import Lasso, LassoCV
from sklearn.metrics import r2_score

from . import transient_filter_functions as flt
from .utils import transient_utils as utl
from . import transient_mpfr_utils as mpu
from . import transient_engine as eng
from . import transient_defaults as dbase

logger = logging.getLogger("PyRthLogger")


class StructureFunction(dbase.StructureParameters):
    """Orchestrates the end-to-end structure-function identification flow.

    The instance holds the merged evaluation parameters, ingests measurements,
    runs the selected deconvolution method, and emits the Foster/Cauer ladders
    that power PyRth's exporters.  Each method advances the pipeline by one
    conceptual stage.
    """

    def __init__(self, params: dbase.StructureParameters | Mapping[str, Any]):
        """Copy/validate parameters and program the MPFR precision context.

        Parameters can be provided as a ``StructureParameters`` dataclass (copied
        to keep the caller immutable) or as a plain mapping that is merged with
        defaults via ``validate_and_merge_defaults``.  After the configuration is
        frozen, the constructor validates ``precision`` and sets gmpy2's MPFR
        context so that all downstream arbitrary-precision algorithms share the
        same numerical budget.
        """

        if isinstance(params, dbase.StructureParameters):
            param_instance = dbase.copy_parameters(params)
        else:
            param_instance = dbase.validate_and_merge_defaults(params, None)

        super().__init__(**dbase.parameters_to_dict(param_instance))

        self.io_manager = None

        self.data_handlers = set()

        self.data_header = None
        self.data_pwr = None
        self.data_tco = None
        self.t3_lsb = None
        self.t3_uref = None
        self.t3_kfac = None

        # placeholders for attributes populated during pipeline steps
        self.time = None
        self.time_raw = None
        self.impedance = None
        self.temperature = None
        self.temp_raw = None
        self.voltage = None
        self.log_time = None
        self.log_time_pad = None
        self.log_time_interp = None
        self.log_time_delta = None
        self.imp_deriv_interp = None
        self.bz_curve = np.array([])
        self.imp_smooth = None
        self.imp_smooth_full = None
        self.time_spec = None
        self.sum_time_spec = None
        self.deconv_t = None
        self.fft_idi = None
        self.fft_idi_pegrm = None
        self.fft_wgt = None
        self.fft_freq = None
        self.fft_wgt_freq = None
        self.pad_time_size = 0
        self.lower_fit_index = None
        self.upper_fit_index = None
        self.expl_ft_prm = None
        self.trans_weight = None
        self.current_filter = None
        self.therm_resist_fost = None
        self.therm_capa_fost = None
        self.perf_monitor = None
        self.save_perf = False
        self.look_at_perf = False
        self.crop_time_spec = np.array([])
        self.crop_log_time = np.array([])
        self.cau_res = np.array([])
        self.cau_cap = np.array([])
        self.int_cau_res = np.array([])
        self.int_cau_cap = np.array([])
        self.diff_struc = np.array([])
        self.mpfr_resist_fost = None
        self.mpfr_capa_fost = None
        self.mpfr_z_num = None
        self.mpfr_z_denom = None

        if not isinstance(self.precision, int) or self.precision <= 0:
            raise ValueError(
                f"Parameter 'precision' must be a positive integer, got {self.precision}"
            )

        gp.get_context().precision = self.precision  # pylint: disable=no-member

    def read_t3ster(self, f):
        """Read the three T3Ster companion files and derive instrument meta-data.

        The raw files contain digitized temperatures, power calibration, and
        thermo-coefficient (TCO) tables.  This helper parses all of them,
        computes the LSB/UREF conversion constants, and prepares the polynomial
        TCO fit so that ``make_z_t3ster`` can immediately convert samples to
        absolute temperatures.
        The newer T3Ster SI series uses a proprietary file format and is
        no longer ingestible by PyRth, so this path only works with older
        instruments that still export the legacy companion files.
        """
        self.data_header = [np.array(line.strip().split(" ")) for line in f]
        self.data = np.loadtxt(self.infile, delimiter=" ", skiprows=7)
        self.data_pwr = [
            [block.strip() for block in line.split("=")]
            for line in open(self.infile_pwr, encoding="utf-8")
        ]
        self.data_tco = np.loadtxt(self.infile_tco, delimiter="\t", skiprows=7)
        self.power_step = next(
            (
                float(arr[1])
                for arr in self.data_pwr
                if arr[0] in ["Power", "POWERSTEP"]
            ),
            None,
        )
        self.t3_lsb = float(self.data_header[6][1])
        self.t3_uref = float(self.data_header[8][1])
        self.t3_kfac = poly.polyfit(
            self.data_tco[:, 0], self.data_tco[:, 1], self.kfac_fit_deg
        )

    def make_z(self):
        """Front-end dispatcher that converts the chosen input into Zth.

        Depending on ``input_mode`` this method routes to the appropriate
        ingestion helper (T3Ster, raw temperature, voltage+calibration, or
        direct impedance).  It enforces basic shape/length checks, flags which
        exporters should run, and ends by populating ``self.time``,
        ``self.impedance``, and the logarithmic time axis shared by every
        downstream deconvolution algorithm.
        """
        valid_input_modes = ["t3ster", "temp", "volt", "impedance"]

        if self.input_mode not in valid_input_modes:
            raise ValueError(
                f"Conversion mode '{self.input_mode}' not recognised. Valid options are: {valid_input_modes}"
            )

        if self.input_mode != "t3ster":
            if self.data is None:
                raise ValueError("Data has not been given.")

            self.data = np.array(self.data)

            if self.data.shape[1] != 2:
                raise ValueError("Data has to have two columns. Maybe transpose?")

            min_data_length = 100
            if self.data.shape[0] < min_data_length:
                logger.warning(
                    f"Data length ({self.data.shape[0]}) is shorter than "
                    f"recommended minimum ({min_data_length} points). "
                    "Results may be unreliable."
                )

        if self.input_mode in ["volt", "t3ster"]:
            self.data_handlers.add("volt")
        if self.input_mode != "impedance":
            self.data_handlers.add("temp")

        if self.input_mode == "t3ster":
            self.make_z_t3ster()
        elif self.input_mode in ["temp", "volt"]:
            self._process_temp_volt_data()
        elif self.input_mode == "impedance":
            self.time = self.data[:, 0]
            self.impedance = self.data[:, 1]
            logger.info("taking impedance data directly from data array")

        self.log_time = np.log(self.time)
        if hasattr(self, "stored_early_zth"):
            current_early_zth = utl.get_early_zth(self)
            self.impedance *= self.stored_early_zth / current_early_zth

    def _process_temp_volt_data(self):
        """Convert raw temperature/voltage traces into an impedance step.

        This path is used for lab data that already comes as temperature or
        voltage samples.  It optionally extrapolates the pre-heating tail,
        applies user-requested data cuts, estimates the reference temperature
        ``t_null``, and calls ``tmp_to_z`` so later stages see the same Zth
        representation produced by the T3Ster flow.
        """
        if self.input_mode == "volt" and self.calib is None:
            raise ValueError("Calibration data is required for voltage conversion")

        if self.input_mode == "volt":
            self.voltage = self.data[:, 1]
            self.temp_raw = utl.volt_to_temp(
                self.voltage, self.calib, self.kfac_fit_deg
            )
        else:
            self.temp_raw = self.data[:, 1]

        self.time_raw = self.data[:, 0]

        if self.extrapolate:
            self.data_handlers.add("extrpl")

            if self.lower_fit_limit is None or self.upper_fit_limit is None:
                raise ValueError(
                    "Extrapolation requires 'lower_fit_limit' and 'upper_fit_limit' to be set"
                )

            self.lower_fit_index = np.searchsorted(self.time_raw, self.lower_fit_limit)
            self.upper_fit_index = np.searchsorted(self.time_raw, self.upper_fit_limit)

            self.time, self.temperature, self.expl_ft_prm, t_null = (
                utl.extrapolate_temperature(
                    self.time_raw,
                    self.temp_raw,
                    self.lower_fit_index,
                    self.upper_fit_index,
                )
            )

        else:
            start_idx = max(0, self.data_cut_lower)
            end_idx = min(len(self.time_raw), self.data_cut_upper)

            if start_idx > 0:
                time_zero = self.time_raw[start_idx - 1]
            else:
                time_zero = 0.0

            self.time = self.time_raw[start_idx:end_idx] - time_zero

            self.temperature = self.temp_raw[start_idx:end_idx]

            t0_start = max(0, self.temp_0_avg_range[0])
            t0_end = min(len(self.temp_raw), self.temp_0_avg_range[1])
            t_null = np.mean(self.temp_raw[t0_start:t0_end])

        self.impedance = utl.tmp_to_z(
            self.temperature,
            t_null,
            self.power_step,
            self.optical_power,
            self.power_scale_factor,
            is_heating=self.is_heating,
        )

    def make_z_t3ster(self):
        """Convert a T3Ster recording to temperature, then to Zth.

        Uses ``read_t3ster`` outputs plus the calibrated k-factor polynomial to
        reconstruct temperature from digitized voltages, determines the fit
        window for extrapolation, and produces the impedance step response that
        drives deconvolution.
        """

        with open(self.infile, encoding="utf-8") as f:
            self.read_t3ster(f)

        fnzi = utl.first_nonzero_index(self.data[:, 0])
        dig = self.data[fnzi:, 1]
        if self.kfac_fit_deg == 1:
            self.temp_raw, self.voltage = utl.volt_to_temp_t3ster(
                dig, self.t3_lsb, self.t3_uref, self.t3_kfac
            )
        elif self.kfac_fit_deg == 2:
            extrapol_limit = 20  # only allow extrapolation for 20 K beyond the range of the calibration
            span = (
                np.min(self.data_tco[:, 0]) - extrapol_limit,
                np.max(self.data_tco[:, 0]) + extrapol_limit,
            )
            self.temp_raw, self.voltage = utl.volt_to_temp_t3ster(
                dig, self.t3_lsb, self.t3_uref, self.t3_kfac, span=span
            )
        else:
            raise ValueError("kfac_fit_deg has to be 1 or 2")

        self.time_raw = self.data[fnzi:, 0] * 1e-6

        self.lower_fit_index = np.searchsorted(self.time_raw, self.lower_fit_limit)
        self.upper_fit_index = np.searchsorted(self.time_raw, self.upper_fit_limit)

        if self.extrapolate:
            self.data_handlers.add("extrpl")
            self.time, self.temperature, self.expl_ft_prm, t_null = (
                utl.extrapolate_temperature(
                    self.time_raw,
                    self.temp_raw,
                    self.lower_fit_index,
                    self.upper_fit_index,
                )
            )
            self.impedance = utl.tmp_to_z(
                self.temperature,
                t_null,
                self.power_step,
                self.optical_power,
                self.power_scale_factor,
                is_heating=self.is_heating,
            )

        else:
            self.lower_fit_index = np.searchsorted(self.time_raw, self.lower_fit_limit)
            self.upper_fit_index = np.searchsorted(self.time_raw, self.upper_fit_limit)
            t_null = np.average(self.temp_raw[self.lower_fit_index : self.upper_fit_index])
            self.impedance = utl.tmp_to_z(
                self.temp_raw,
                t_null,
                self.power_step,
                self.optical_power,
                self.power_scale_factor,
                is_heating=self.is_heating,
            )

    def make_z_volt(self):
        """Convert voltage-only datasets into Zth using the stored calibration.

        This predates the modern ``make_z`` dispatcher but remains useful for
        quick experiments where voltages are already loaded into ``self.data``.
        """

        if self.calib is None:
            raise ValueError(
                "Calibration data is missing. Calibration data is needed for the conversion from voltage to temperature."
            )

        self.temperature = utl.volt_to_temp(
            self.data[:, 1], self.calib, self.kfac_fit_deg
        )
        self.impedance = utl.tmp_to_z(
            self.temperature,
            self.temperature[0],
            self.power_step,
            self.optical_power,
            self.power_scale_factor,
            is_heating=self.is_heating,
        )
        self.time = self.data[1:, 0] - self.data[0, 0]

    def z_fit_deriv(self):
        """Smooth the impedance step and compute its logarithmic derivative.

        This wraps ``eng.derivative`` which performs adaptive windowed
        smoothing, padding, and interpolation to obtain a stable derivative
        over logarithmic time.  The derivative is the common starting point
        for FFT and Bayesian deconvolution, so a failure here usually means
        the heating/cooling direction was swapped or the data is degenerate.
        """

        (
            self.imp_smooth,
            self.imp_deriv_interp,
            self.log_time_interp,
            self.imp_smooth_full,
            self.log_time_pad,
            self.log_time_delta,
        ) = eng.derivative(
            self.impedance,
            self.log_time,
            self.log_time_size,
            self.window_increment,
            self.minimum_window_length,
            self.maximum_window_length,
            self.minimum_window_size,
            self.min_index,
            self.expected_var,
            self.pad_factor_pre,
            self.pad_factor_after,
        )

        self.pad_time_size = np.size(self.log_time_pad)

        if not np.any(self.imp_deriv_interp):
            raise ValueError(
                "Impedance derivative is empty or contains all zeros. Maybe  heating / cooling transient interchanged?"
            )

        self._update_bz_curve()

    def _update_bz_curve(self):
        """Compute the B(z) signature as log of the derivative magnitude."""

        if self.imp_deriv_interp is None:
            self.bz_curve = np.array([])
            return

        deriv_abs = np.abs(self.imp_deriv_interp)
        with np.errstate(divide="ignore", invalid="ignore"):
            self.bz_curve = np.where(deriv_abs > 0.0, np.log(deriv_abs), np.nan)

    @utl.timer_decorator
    def z_fit_lasso(self):
        """Recover the time-constant spectrum via non-negative LASSO.

        Unlike FFT/Bayesian paths this method works directly in the impedance
        domain.  It constructs a design matrix of exponential responses, then
        solves an L1-regularised least-squares problem (with optional
        cross-validation or adaptive Bayesian weights) to produce a sparse
        spectrum.  The resulting ``time_spec`` feeds the same Foster/Cauer
        converters as every other deconvolution strategy.
        """
        if not np.any(self.impedance > 0):
            logger.error("z_fit_lasso: impedance must contain positive values")
            logger.error(f"Impedance: {self.impedance}")
            raise ValueError("z_fit_lasso: impedance must contain positive values")

        time = self.time.flatten()

        if self.deconv_mode == "lasso":
            tau_min = 0.5 * np.diff(time).min()
            tau_max = 1 * time.max()
            grid_size = self.log_time_size
            tau_grid = np.logspace(np.log10(tau_min), np.log10(tau_max), grid_size)

        elif self.deconv_mode == "adaptive":
            tau_grid = np.exp(self.log_time_pad.flatten())
        else:
            raise ValueError(
                f"z_fit_lasso: deconv_mode '{self.deconv_mode}' not recognised"
            )

        warm_start = self.deconv_mode == "adaptive"

        phi_unnormalized = 1.0 - np.exp(-time[:, None] / tau_grid[None, :])

        phi_norms = np.linalg.norm(phi_unnormalized, axis=0, keepdims=True)

        logger.debug(
            f"Condition number of unnormalized phi: {np.linalg.cond(phi_unnormalized):.4e}"
        )

        phi_norms[phi_norms == 0] = 1.0
        phi = phi_unnormalized / phi_norms

        logger.debug(f"Condition number of phi: {np.linalg.cond(phi):.4e}")

        if self.deconv_mode == "adaptive":
            epsilon = 1e-6
            gamma = 0.8
            weights = 1.0 / (np.abs(self.time_spec) + epsilon) ** gamma

            weights = np.clip(weights, 0.05, 20.0)

            phi = phi / weights[None, :]

            logger.debug(f"Condition number of weighted phi: {np.linalg.cond(phi):.4e}")

        if hasattr(self, "lasso_cv_folds") and self.lasso_cv_folds > 1:
            logger.debug(
                f"Performing Lasso with Cross-Validation (folds={self.lasso_cv_folds})..."
            )
            lasso = LassoCV(
                alphas=self.lasso_alpha,
                cv=self.lasso_cv_folds,
                positive=True,
                fit_intercept=False,
                max_iter=self.lasso_max_iter,
                tol=self.lasso_tol,
                n_jobs=-1,
                verbose=False,
                selection=self.lasso_selection,
                precompute=self.lasso_precompute,
            )
        else:
            if not isinstance(self.lasso_alpha, (int, float)):
                raise TypeError(
                    f"When not using CV, lasso_alpha must be a number, but got {type(self.lasso_alpha)}"
                )
            logger.debug(f"Performing Lasso with fixed alpha={self.lasso_alpha}...")
            lasso = Lasso(
                alpha=self.lasso_alpha,
                positive=True,
                fit_intercept=False,
                max_iter=self.lasso_max_iter,
                tol=self.lasso_tol,
                selection=self.lasso_selection,
                precompute=self.lasso_precompute,
                warm_start=warm_start,
            )

        if self.deconv_mode == "adaptive" and self.lasso_cv_folds > 1:
            lasso.coef_ = self.time_spec.copy()

        lasso.fit(phi, self.impedance.ravel())
        a_hat_normalized = lasso.coef_

        if self.deconv_mode == "adaptive":
            a_hat = a_hat_normalized / (phi_norms.flatten() * weights)
        else:
            a_hat = a_hat_normalized / phi_norms.flatten()

        y_fit_unnormalized = (phi_unnormalized @ a_hat).ravel()
        sigma_hat = np.sqrt(
            ((self.impedance.ravel() - y_fit_unnormalized) ** 2).mean()
        )

        r2 = r2_score(self.impedance.ravel(), y_fit_unnormalized)

        r_th_model = np.sum(a_hat)

        if hasattr(lasso, "alpha_"):
            used_alpha = lasso.alpha_
        else:
            used_alpha = lasso.alpha

        active_components = np.count_nonzero(a_hat > 0)
        logger.info(
            "Lasso results (mode=%s): R_meas=%.4f, R_model=%.4f, alpha=%.2e, RMSE=%.4f, R2=%.4f, active=%d",
            self.deconv_mode,
            self.impedance[-1],
            r_th_model,
            used_alpha,
            sigma_hat,
            r2,
            active_components,
        )

        if not np.any(a_hat > 0):
            raise ValueError(
                "z_fit_lasso: time constant spectrum is empty (no active Lasso components)"
            )

        self.time_spec = a_hat.flatten()
        self.sum_time_spec = np.cumsum(self.time_spec)

        if self.deconv_mode == "lasso":
            self.log_time_pad = np.log(tau_grid.copy())
            self.log_time_interp = self.log_time.copy()
            self.imp_smooth = y_fit_unnormalized.flatten()
            self.imp_smooth_full = y_fit_unnormalized.flatten()
            self.pad_time_size = np.size(self.log_time_pad)

            self.imp_deriv_interp, _ = utl.time_const_to_imp(
                self.log_time_pad, a_hat
            )
            self._update_bz_curve()

    def fft_signal(self):
        """Transform the impedance derivative into the frequency domain.

        Computes the FFT of ``imp_deriv_interp`` (the smoothed derivative) and
        stores the periodogram and frequency grid so that ``fft_time_spec`` can
        perform a frequency-domain deconvolution with the selected window.
        """
        self.fft_idi = fftpack.fft(self.imp_deriv_interp)
        self.fft_idi_pegrm = np.abs(self.fft_idi * self.log_time_delta) ** 2

        self.fft_freq = fftpack.fftfreq(self.pad_time_size, self.log_time_delta)

    def fft_weight(self):
        """FFT of the weighting kernel with alignment to the derivative grid.

        Rolls the analytical weight function so that zero time aligns with the
        FFT origin; this keeps ``fft_idi`` and ``fft_wgt`` on the same frequency
        grid before division and windowing.
        """
        null_index = np.searchsorted(self.log_time_pad, 0.0)

        self.trans_weight = np.roll(utl.weight_z(self.log_time_pad), -null_index)
        self.fft_wgt = fftpack.fft(self.trans_weight) * self.log_time_delta
        self.fft_wgt_freq = fftpack.fftfreq(self.pad_time_size, self.log_time_delta)

        if not np.array_equal(self.fft_freq, self.fft_wgt_freq):
            raise ValueError("Frequency ranges do not match up, check fouriertransform")

    def fft_time_spec(self):
        """Divide spectrum by the kernel and apply the requested filter.

        After the derivative and kernel are in the frequency domain this step
        performs the actual deconvolution, multiplies by the chosen window, and
        inverse-transforms back to logarithmic time to obtain ``time_spec`` and
        its cumulative sum.
        """

        self.current_filter = flt.give_current_filter(
            self.filter_name, self.fft_freq, self.filter_range, self.filter_parameter
        )
        self.deconv_t = (self.fft_idi / self.fft_wgt) * self.current_filter
        self.time_spec = np.real(fftpack.ifft(self.deconv_t))

        self.time_spec *= self.log_time_delta

        self.sum_time_spec = np.cumsum(self.time_spec)

    @utl.timer_decorator
    def perform_bayesian_deconvolution(self):
        """Run the iterative Bayesian solver described in the theory chapter.

        Builds the dense response matrix for the padded log-time axis and
        delegates to ``eng.bayesian_deconvolution`` which alternates between
        residual back-projection and spectrum updates.  The output spectrum is
        scaled to account for padding and then integrated so the later network
        synthesis code can treat it identically to FFT/LASSO results.
        """

        re_mat = eng.response_matrix(self.log_time_pad, self.pad_time_size)

        self.time_spec = eng.bayesian_deconvolution(
            re_mat, self.imp_deriv_interp, self.bay_steps
        )

        self.time_spec *= self.log_time_delta

        self.sum_time_spec = np.cumsum(self.time_spec)


    def foster_network(self):
        """Convert the time-constant spectrum into parallel Foster branches.

        Removes padded zeros, optionally oversamples the spectrum, culls tiny
        entries, and creates the resistance/capacitance arrays that represent
        each Foster branch.  These values are the shared starting point for the
        MPFR-based rational reconstruction and every Foster→Cauer converter.
        """

        factor = int(self.timespec_interpolate_factor)

        if factor > 1:
            f = interp.InterpolatedUnivariateSpline(self.log_time_pad, self.time_spec)
            int_log_time = np.linspace(
                self.log_time_pad.min(),
                self.log_time_pad.max(),
                len(self.log_time_pad) * factor,
            )
            int_time_spec = f(self.log_time_pad)
        else:
            int_log_time = self.log_time_pad.copy()
            int_time_spec = self.time_spec.copy()

        where = np.where(int_time_spec >= 1e-10)
        self.crop_time_spec = int_time_spec[where]
        self.crop_log_time = int_log_time[where]

        if self.crop_time_spec.size == 0:
            raise ValueError("Time constant spectrum is empty after filtering.")

        self.therm_resist_fost = self.crop_time_spec
        self.therm_capa_fost = np.exp(self.crop_log_time) / self.therm_resist_fost

    def mpfr_foster_impedance(self):
        """Lift the Foster ladder into arbitrary precision and build Z(s).

        Stores MPFR copies of the Foster elements and calls
        ``transient_mpfr_utils.make_z_s`` to obtain the numerator/denominator
        polynomials of the driving-point impedance.  The MPFR representation
        keeps the subsequent Euclidean conversions numerically stable even for
        ladders with dozens of elements.
        """
        (
            self.mpfr_resist_fost,
            self.mpfr_capa_fost,
            self.mpfr_z_num,
            self.mpfr_z_denom,
        ) = mpu.build_mpfr_foster_impedance(self.therm_resist_fost, self.therm_capa_fost)

    def poly_long_div(self):
        """Classical Euclidean Foster→Cauer conversion with MPFR arithmetic."""

        self.cau_res, self.cau_cap = mpu.poly_long_division_to_cauer(
            self.mpfr_z_num, self.mpfr_z_denom
        )

        self._finalize_cauer()

    def boor_golub(self):
        """Execute the Boor–Golub continued-fraction algorithm in MPFR space."""

        self.cau_res, self.cau_cap = mpu.boor_golub_cauer(
            self.mpfr_resist_fost, self.mpfr_capa_fost
        )

        self._finalize_cauer()

    def j_fraction_methods(self):
        """Select between the Khatwani or Sobhy J-fraction routes to Cauer.

        Uses MPFR copies of the rational impedance, then either builds Markov
        parameters (Khatwani) or interlaced A/B tables (Sobhy) to obtain the
        intermediate H–h fraction.  ``conti_frac_convers`` subsequently turns
        that J-fraction into the desired Cauer S-fraction.
        """

        cleaned_mpfr_num, cleaned_mpfr_denom = mpu.normalize_rational_polynomials(
            self.mpfr_z_num, self.mpfr_z_denom
        )

        n_terms = len(cleaned_mpfr_denom)

        if self.struc_method == "khatwani":
            markov_parameters = mpu.generate_markov_params(
                cleaned_mpfr_num, cleaned_mpfr_denom
            )
            large_h, small_h = mpu.khatwani_method(n_terms, markov_parameters)
        elif self.struc_method == "sobhy":
            large_h, small_h = mpu.sobhy_method(
                n_terms, cleaned_mpfr_num, cleaned_mpfr_denom
            )
        else:
            raise ValueError(
                f"Unsupported struc_method '{self.struc_method}' for J-fraction conversion"
            )

        self.cau_res, self.cau_cap = mpu.conti_frac_convers(n_terms, large_h, small_h)

        self._finalize_cauer()

    def lanczos(self):
        """Apply the Lanczos iteration to stream Cauer elements on the fly.

        Works directly on the diagonal Foster matrices through
        ``eng.lanczos_inner`` which orthogonalises with respect to the thermal
        capacitance metric.  The method is fast, numerically stable, and emits
        partial ladders early—ideal when only the front layers of the structure
        function are needed.
        """

        res, cap = eng.lanczos_inner(self.therm_capa_fost, self.therm_resist_fost)

        self.cau_res = np.array(res)
        self.cau_cap = np.array(cap)

        if self.blockwise_sum_width > 1:

            num_blocks = len(self.cau_res) // self.blockwise_sum_width

            indices = np.arange(num_blocks) * self.blockwise_sum_width

            self.cau_res = np.add.reduceat(self.cau_res, indices)
            self.cau_cap = np.add.reduceat(self.cau_cap, indices)

        self._finalize_cauer()

    def _compute_diff_structure(self):
        """Derive the differential structure function, guarding zero slopes."""

        if len(self.int_cau_res) < 2:
            self.diff_struc = np.array([])
            return

        delta_res = np.diff(self.int_cau_res)
        delta_cap = np.diff(self.int_cau_cap)

        self.diff_struc = np.zeros_like(delta_res)

        non_zero = delta_res != 0.0
        self.diff_struc[non_zero] = delta_cap[non_zero] / delta_res[non_zero]

    def _finalize_cauer(self):
        """Common post-processing after Cauer ladder generation."""

        if np.any(self.cau_res[self.cau_res < 0.0]) or np.any(
            self.cau_res[self.cau_cap < 0.0]
        ):
            logger.error(
                "negative structure-function values detected for n_terms=%d", len(self.cau_cap)
            )

        self.int_cau_res = np.cumsum(self.cau_res)
        self.int_cau_cap = np.cumsum(self.cau_cap)

        self._compute_diff_structure()
