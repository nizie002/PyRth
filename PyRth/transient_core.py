import gmpy2 as gp
from gmpy2 import mpfr
import numpy as np
import numpy.fft as fftpack
import numpy.polynomial.polynomial as poly
import scipy.integrate as sin
import scipy.interpolate as interp

import logging


from . import transient_filter_functions as flt
from .utils import transient_utils as utl
from . import transient_mpfr_utils as mpu
from . import transient_engine as eng

logger = logging.getLogger("PyRthLogger")


# figures and data handling are split in transient_output
class StructureFunction:

    def __init__(self, params):

        self.io_manager = None

        # Set attributes
        for key, value in params.items():
            setattr(self, key, value)

        self.data_handlers = set()

        # Validate precision
        if not isinstance(self.precision, int) or self.precision <= 0:
            raise ValueError(
                f"Parameter 'precision' must be a positive integer, got {self.precision}"
            )

        gp.get_context().precision = self.precision

    def read_t3ster(self, f):
        self.data_header = [np.array(line.strip().split(" ")) for line in f]
        self.data = np.loadtxt(self.infile, delimiter=" ", skiprows=7)
        self.data_pwr = [
            [block.strip() for block in line.split("=")]
            for line in open(self.infile_pwr)
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
        valid_conv_modes = ["t3ster", "temp", "volt", "none"]

        if self.conv_mode not in valid_conv_modes:
            raise ValueError(
                f"Conversion mode '{self.conv_mode}' not recognised. Valid options are: {valid_conv_modes}"
            )

        # Data validation for non-t3ster modes
        if self.conv_mode != "t3ster":
            # Check if data exists and has correct shape
            if self.data is None:
                raise ValueError("Data has not been given.")

            self.data = np.array(self.data)

            # Validate data shape and length
            if self.data.shape[1] != 2:
                raise ValueError("Data has to have two columns. Maybe transpose?")

            min_data_length = 100
            if self.data.shape[0] < min_data_length:
                logger.warning(
                    f"Data length ({self.data.shape[0]}) is shorter than "
                    f"recommended minimum ({min_data_length} points). "
                    "Results may be unreliable."
                )

        if self.conv_mode in ["volt", "t3ster"]:
            self.data_handlers.add("volt")
        if self.conv_mode != "none":
            self.data_handlers.add("temp")

        if self.conv_mode == "t3ster":
            self.make_z_t3ster()
        elif self.conv_mode in ["temp", "volt"]:
            self._process_temp_volt_data()
        elif self.conv_mode == "none":
            self.time = self.data[:, 0]
            self.impedance = self.data[:, 1]
            logger.info("taking impedance data directly from data array")

        # all calculations are done in logarithmic time
        self.log_time = np.log(self.time)
        if hasattr(self, "stored_early_zth"):
            f = interp.interp1d(self.log_time, self.impedance)
            self.impedance *= self.stored_early_zth / f(np.log(1e-4))

    def _process_temp_volt_data(self):
        """Process temperature or voltage data with optional extrapolation"""
        if self.conv_mode == "volt" and self.calib is None:
            raise ValueError("Calibration data is required for voltage conversion")

        # Convert voltage to temperature if needed
        if self.conv_mode == "volt":
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

            # Extrapolate temperature data
            self.time, self.temperature, self.expl_ft_prm, t_null = (
                utl.extrapolate_temperature(
                    self.time_raw,
                    self.temp_raw,
                    self.lower_fit_index,
                    self.upper_fit_index,
                )
            )

        else:
            # Apply data cutting based on specified indices
            start_idx = max(0, self.data_cut_lower)
            end_idx = min(len(self.time_raw), self.data_cut_upper)

            if start_idx > 0:
                time_zero = self.time_raw[start_idx - 1]
            else:
                time_zero = 0.0

            self.time = self.time_raw[start_idx:end_idx] - time_zero

            self.temperature = self.temp_raw[start_idx:end_idx]

            # Calculate initial temperature, t_null, using average over specified range
            t0_start = max(0, self.temp_0_avg_range[0])
            t0_end = min(len(self.temp_raw), self.temp_0_avg_range[1])
            t_null = np.mean(self.temp_raw[t0_start:t0_end])

        # Calculate impedance
        self.impedance = utl.tmp_to_z(
            self.temperature,
            t_null,
            self.power_step,
            self.optical_power,
            self.power_scale_factor,
            is_heating=self.is_heating,
        )

    def make_z_t3ster(self):

        with open(self.infile) as f:
            self.read_t3ster(f)

        fnzi = utl.first_nonzero_index(self.data[:, 0])
        self.dig = self.data[fnzi:, 1]
        if self.kfac_fit_deg == 1:
            self.temp_raw, self.voltage = utl.volt_to_temp_t3ster(
                self.dig, self.t3_lsb, self.t3_uref, self.t3_kfac
            )
        elif self.kfac_fit_deg == 2:
            extrapol_limit = 20  # only allow extrapolation for 20 K beyond the range of the calibration
            span = (
                np.min(self.data_tco[:, 0]) - extrapol_limit,
                np.max(self.data_tco[:, 0]) + extrapol_limit,
            )
            self.temp_raw, self.voltage = utl.volt_to_temp_t3ster(
                self.dig, self.t3_lsb, self.t3_uref, self.t3_kfac, span=span
            )
        else:
            raise ValueError("kfac_fit_deg has to be 1 or 2")

        self.time_raw = self.data[fnzi:, 0] * 1e-6

        self.lower_fit_index = np.searchsorted(self.time_raw, self.lower_fit_limit)
        self.upper_fit_index = np.searchsorted(self.time_raw, self.upper_fit_limit)

        if self.extrapolate == True:
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
            t_null = np.average(self.temp_raw[self.av_range[0] : self.av_range[1]])
            self.impedance = utl.tmp_to_z(
                self.temp_raw,
                t_null,
                self.power_step,
                self.optical_power,
                self.power_scale_factor,
                is_heating=self.is_heating,
            )

    def make_z_temp(self):
        self.temperature = self.data[1:, 1]
        self.impedance = utl.tmp_to_z(
            self.temperature,
            self.data[0, 1],
            self.power_step,
            self.optical_power,
            self.power_scale_factor,
            is_heating=self.is_heating,
        )
        self.time = self.data[1:, 0] - self.data[0, 0]

    def make_z_volt(self):

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

    def make_z_volt_no_extr(self):

        if self.calib is None:
            raise ValueError(
                "Calibration data is missing. Calibration file is needed for the conversion from voltage to temperature."
            )

        self.time = self.data[1:, 0] - self.data[0, 0]
        self.time = self.time[self.lower_fit_limit :]
        self.time_raw = self.data[1:, 0]
        self.voltage = self.data[1:, 1]
        self.temp_raw = utl.volt_to_temp(self.voltage, self.calib, self.kfac_fit_deg)
        self.temperature = self.temp_raw[self.lower_fit_limit :]
        self.impedance = utl.tmp_to_z(
            self.temperature,
            self.temperature[0],
            self.power_step,
            self.optical_power,
            self.power_scale_factor,
            is_heating=self.is_heating,
        )

    def z_fit_deriv(self):

        (
            self.imp_smooth,
            self.imp_deriv_interp,
            self.log_time_interp,
            self.imp_smooth_full,
            self.log_time_pad,
            self.fft_delta,
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

    def fft_signal(self):
        # calculates the fourier transform and power periodogram
        self.fft_idi = fftpack.fft(self.imp_deriv_interp)
        self.fft_idi_pegrm = np.abs(self.fft_idi * self.fft_delta) ** 2

        self.fft_freq = fftpack.fftfreq(self.pad_time_size, self.fft_delta)

    def fft_weight(self):
        # calculates the fourier transform of the weight function
        null_index = np.searchsorted(self.log_time_pad, 0.0)

        self.trans_weight = np.roll(utl.weight_z(self.log_time_pad), -null_index)
        self.fft_wgt = fftpack.fft(self.trans_weight) * self.fft_delta
        self.fft_wgt_freq = fftpack.fftfreq(self.pad_time_size, self.fft_delta)

        if not np.array_equal(self.fft_freq, self.fft_wgt_freq):
            raise ValueError("Frequency ranges do not match up, check fouriertransform")

    def fft_time_spec(self):

        # calculates the deconvolution and returns the time constant spectrum with the selected filter

        self.current_filter = flt.give_current_filter(
            self.filter_name, self.fft_freq, self.filter_range, self.filter_parameter
        )
        self.deconv_t = (self.fft_idi / self.fft_wgt) * self.current_filter
        self.time_spec = np.real(fftpack.ifft(self.deconv_t))

        self.sum_time_spec = sin.cumulative_trapezoid(
            self.time_spec, x=self.log_time_pad, initial=0.0
        )

    def perform_bayesian_deconvolution(self):
        # calculates the bayesian deconvolution

        re_mat = eng.response_matrix(self.log_time_pad, self.pad_time_size)

        # # # Bayesian iteration core
        self.time_spec = eng.bayesian_deconvolution(
            re_mat, self.imp_deriv_interp, self.bay_steps
        )

        self.sum_time_spec = sin.cumulative_trapezoid(
            self.time_spec, x=self.log_time_pad, initial=0.0
        )

    def foster_network(self):
        # derives the foster thermal equivalent network, lumped from the time constant spectrum
        # remove all the zeros we padded to avoid bad numerics

        where = np.where(self.time_spec >= 1e-10)

        self.crop_time_spec = self.time_spec[where]
        self.crop_log_time = self.log_time_pad[where]

        if self.crop_time_spec.size == 0:
            raise ValueError("Time constant spectrum is empty after filtering.")

        factor = int(self.timespec_interpolate_factor)

        if factor > 1:
            # f = interpolate.interp1d(self.crop_log_time, self.crop_time_spec)
            f = interp.InterpolatedUnivariateSpline(
                self.crop_log_time, self.crop_time_spec
            )
            self.crop_log_time = np.linspace(
                self.crop_log_time.min(),
                self.crop_log_time.max(),
                len(self.crop_log_time) * factor,
            )
            self.crop_time_spec = f(self.crop_log_time)

        delta = self.crop_log_time[1:] - self.crop_log_time[0:-1]
        delta = np.insert(delta, 0, delta[0])
        self.therm_resist_fost = self.crop_time_spec * delta
        self.therm_capa_fost = np.exp(self.crop_log_time) / self.therm_resist_fost

    def mpfr_foster_impedance(self):
        # use gmp2 for arbitrary precision floating point arithmetic
        self.mpfr_resist_fost = [
            mpfr(num) for num in self.therm_resist_fost
        ]  # num[0] is the constant term in Z(s)
        self.mpfr_capa_fost = [
            mpfr(denom) for denom in self.therm_capa_fost
        ]  # num[i] is the a_i x^i term in Z(s)

        self.mpfr_z_num, self.mpfr_z_denom = mpu.make_z_s(
            self.mpfr_resist_fost, self.mpfr_capa_fost
        )

    def poly_long_div(self):
        # transforms the foster to the cauer thermal equivalent network

        ar_len = len(self.mpfr_z_denom) - 1

        self.cau_res = np.zeros(ar_len)
        self.cau_cap = np.zeros(ar_len)

        for i in range(ar_len):
            self.mpfr_z_num, self.mpfr_z_denom, cap, res = mpu.precision_step(
                self.mpfr_z_num, self.mpfr_z_denom
            )
            self.cau_res[i] = float(res)
            self.cau_cap[i] = float(cap)

        if np.any(self.cau_res[self.cau_res < 0.0]) or np.any(
            self.cau_res[self.cau_cap < 0.0]
        ):
            logger.error(
                "\n negative values in structure function encountered using N =",
                len(self.cau_cap),
            )

        self.int_cau_res = np.cumsum(self.cau_res)
        self.int_cau_cap = np.cumsum(self.cau_cap)

        self.diff_struc = np.zeros(ar_len - 1)

        for i in range(len(self.int_cau_res) - 1):
            if not (self.int_cau_res[i] - self.int_cau_res[i + 1]) == 0.0:
                self.diff_struc[i] = (self.int_cau_cap[i] - self.int_cau_cap[i + 1]) / (
                    self.int_cau_res[i] - self.int_cau_res[i + 1]
                )

    def boor_golub(self):

        poles = []

        for R, C in zip(self.mpfr_resist_fost, self.mpfr_capa_fost):
            if R > 0 and C > 0:
                poles.append(mpfr("-1.0") / (R * C))

        M = len(poles) - 1
        w_0 = [0] * (M + 1)

        for i in range(M + 1):
            w_0[i] = mpfr("1.0") / self.mpfr_capa_fost[i]

        k = [mpfr("0.0")] * (2 * (M + 1))

        w_sum = mpfr("0.0")
        for w in w_0:
            w_sum = w_sum + w

        k[1] = mpfr("1.0") / w_sum

        lmda = [mpfr("0.0")] * (M + 1)
        mu = [mpfr("0.0")] * (M + 1)
        l_mu_sum = [mpfr("0.0")] * (M)
        l_mu_prod = [mpfr("0.0")] * (M)
        B = [0] * (M + 1)

        B[0] = [mpfr("1.0")]

        for i in range(M + 1):
            lmda[0] = lmda[0] - w_0[i] * poles[i]
        lmda[0] = lmda[0] / w_sum

        k[2] = mpfr("1.0") / (k[1] * lmda[0])
        B[1] = [lmda[0], mpfr("1.0")]

        Bs1 = list(B[1])
        Bs1.insert(0, mpfr("0.0"))

        l_mu_prod[0] = mpu.mpfr_weighted_self_product(
            poles, B[1], w_0
        ) / mpu.mpfr_weighted_self_product(poles, B[0], w_0)

        mu[1] = l_mu_prod[0] / lmda[0]

        for i in range(2, M + 1):
            Bs = list(B[i - 1])
            Bs.insert(0, mpfr("0.0"))

            l_mu_sum[i - 1] = mpu.mpfr_weighted_inner_product(
                poles, B[i - 1], Bs, w_0
            ) / mpu.mpfr_weighted_self_product(poles, B[i - 1], w_0)

            lmda[i - 1] = l_mu_sum[i - 1] - mu[i - 1]

            fst = mpu.mpfr_pol_mul(([l_mu_sum[i - 1], mpfr("1.0")]), B[i - 1])
            snd = mpu.mpfr_pol_mul(([-l_mu_prod[i - 2]]), B[i - 2])
            B[i] = mpu.mpfr_pol_add(fst, snd)

            l_mu_prod[i - 1] = mpu.mpfr_weighted_self_product(
                poles, B[i], w_0
            ) / mpu.mpfr_weighted_self_product(poles, B[i - 1], w_0)
            mu[i] = l_mu_prod[i - 1] / lmda[i - 1]

        k[3] = (k[1] * lmda[0]) / mu[1]
        for i in range(2, M + 1):
            lambdas = k[1]
            mus = mu[1]
            for j in range(2, i):
                mus = mus * mu[j]
            for j in range(i):
                lambdas = lambdas * lmda[j]
            k[2 * i] = mus / lambdas
            k[2 * i + 1] = lambdas / (mus * mu[i])

        self.cau_res = np.zeros(M + 1)
        self.cau_cap = np.zeros(M + 1)

        for i in range(0, M):
            self.cau_res[i] = float(k[2 * i + 2])
            self.cau_cap[i] = float(k[2 * i + 1])
        self.cau_cap[M] = float(k[2 * M + 1])

        if np.any(self.cau_res[self.cau_res < 0.0]) or np.any(
            self.cau_res[self.cau_cap < 0.0]
        ):
            logger.error(
                "\n negative values in structure function encountered using N =",
                len(self.cau_cap),
            )

        self.int_cau_res = np.cumsum(self.cau_res)
        self.int_cau_cap = np.cumsum(self.cau_cap)

        self.diff_struc = np.zeros(M)

        for i in range(len(self.int_cau_res) - 1):
            if not (self.int_cau_res[i] - self.int_cau_res[i + 1]) == 0.0:
                self.diff_struc[i] = (self.int_cau_cap[i] - self.int_cau_cap[i + 1]) / (
                    self.int_cau_res[i] - self.int_cau_res[i + 1]
                )

    def j_fraction_methods(self):
        # use gmp2 for arbitrary precision floating point arithmetic

        inv = gp.div(mpfr("1.0"), self.mpfr_z_denom[-1])

        N = len(self.mpfr_z_denom)

        self.cleaned_mpfr_num = [
            mpfr("0.0"),
            *[gp.mul(inv, self.mpfr_z_num[N - i - 2]) for i in range(N - 1)],
        ]
        self.cleaned_mpfr_denom = [
            gp.mul(inv, self.mpfr_z_denom[N - i - 1]) for i in range(N)
        ]

        if self.struc_method == "khatwani":
            markov_parameters = self.generate_markov_params(N)
            large_h, small_h = self.khatwani_method(N, markov_parameters)

        if self.struc_method == "sobhy":
            large_h, small_h = self.sobhy_method(N)

        self.conti_frac_convers(N, large_h, small_h)

    def generate_markov_params(self, N):
        order = int(np.ceil(np.log2(N)) + 1)

        L = 1

        last_term = [mpfr("1.0")]
        last_error = self.cleaned_mpfr_denom[1:]

        for i in range(1, order + 1):
            pre_term = [mpfr("0.0")] * L
            pre_term = pre_term + last_term

            next_term = mpu.mpfr_pol_add(
                last_term, mpu.mpfr_neg_pol_mul(last_error, pre_term, maxorder=2 * N)
            )  # 2**(order)
            next_error = mpu.mpfr_neg_pol_mul(
                last_error, last_error, maxorder=2 * N
            )  # 2**(order)

            last_term = next_term
            last_error = next_error

            L = L * 2

        markov_parameters = mpu.mpfr_pol_mul(self.cleaned_mpfr_num, next_term)[
            1 : 2 * N + 1
        ]  # L+1

        return markov_parameters

    def khatwani_method(self, N, markov_parameters):
        a_matrix = [[None] * (2 * N) for i in range(N + 1)]
        a_matrix[0] = [mpfr("0.0")] * (2 * N)
        a_matrix[0][0] = mpfr("1.0")

        large_h = [None] * (N - 1)
        small_h = [None] * (N - 1)

        for i in range(2 * N):
            a_matrix[1][i] = markov_parameters[i]

        large_h[0] = a_matrix[0][0] / a_matrix[1][0]
        small_h[0] = (a_matrix[0][1] - large_h[0] * a_matrix[1][1]) / a_matrix[1][0]

        for i in range(2, N):
            for j in range(2 * N - (i - 1) * 2):
                a_matrix[i][j] = (
                    a_matrix[i - 2][j + 2]
                    - large_h[i - 2] * a_matrix[i - 1][j + 2]
                    - small_h[i - 2] * a_matrix[i - 1][j + 1]
                )

            large_h[i - 1] = a_matrix[i - 1][0] / a_matrix[i][0]
            small_h[i - 1] = (
                a_matrix[i - 1][1] - large_h[i - 1] * a_matrix[i][1]
            ) / a_matrix[i][0]

        return large_h, small_h

    def sobhy_method(self, N):
        A = [[mpfr("0.0")] * (N) for i in range(N + 1)]
        B = [[mpfr("0.0")] * (N) for i in range(N + 1)]

        for i in range(N):
            A[0][i] = self.cleaned_mpfr_denom[i]
            B[0][i] = self.cleaned_mpfr_denom[i]

        for i in range(N - 1):
            A[1][i] = self.cleaned_mpfr_num[i + 1]

        for k in range(N - 1):
            j = 1
            B[j][k] = A[j - 1][k + 1] - A[j - 1][0] / A[j][0] * A[j][k + 1]

        for j in range(2, N + 1):
            for k in range(N - j):
                A[j][k] = B[j - 1][k + 1] - B[j - 1][0] / A[j - 1][0] * A[j - 1][k + 1]
            for k in range(N - j):
                B[j][k] = A[j - 1][k + 1] - A[j - 1][0] / A[j][0] * A[j][k + 1]

        a = [None] * (N - 1)
        b = [None] * (N - 1)

        for m in range(1, N):
            a[m - 1] = A[m - 1][0] / A[m][0]
            b[m - 1] = B[m][0] / A[m][0]

        return a, b

    def conti_frac_convers(self, N, large_h, small_h):
        a_square = [None] * (N - 1)
        small_b = [None] * (N - 1)

        a_square[0] = mpfr("1.0") / large_h[0]
        small_b[0] = mpfr("-1.0") * small_h[0] / large_h[0]

        for i in range(1, N - 1):
            a_square[i] = mpfr("-1.0") / (large_h[i] * large_h[i - 1])
            small_b[i] = -small_h[i] / large_h[i]

        small_c = [None] * (2 * (N - 1))

        small_c[0] = mpfr("1.0") / a_square[0]
        small_c[1] = -a_square[0] / small_b[0]

        for i in range(1, N - 1):
            small_c[2 * i] = mpfr("1.0") / (
                small_c[2 * i - 2]
                * small_c[2 * i - 1]
                * small_c[2 * i - 1]
                * a_square[i]
            )
            small_c[2 * i + 1] = -small_c[2 * i - 1] / (
                mpfr("1.0") + small_c[2 * i] * small_c[2 * i - 1] * small_b[i]
            )

        self.cau_res = np.zeros(N - 1)
        self.cau_cap = np.zeros(N - 1)

        for i in range(0, N - 1):
            self.cau_cap[i] = float(small_c[2 * i])
            self.cau_res[i] = float(small_c[2 * i + 1])

        if np.any(self.cau_res[self.cau_res < 0.0]) or np.any(
            self.cau_res[self.cau_cap < 0.0]
        ):
            logger.error("\n negative values ecountered at length", len(self.cau_cap))

        self.int_cau_res = np.cumsum(self.cau_res)
        self.int_cau_cap = np.cumsum(self.cau_cap)

        self.diff_struc = np.zeros(N - 2)

        for i in range(len(self.int_cau_res) - 1):
            if not (self.int_cau_res[i] - self.int_cau_res[i + 1]) == 0.0:
                self.diff_struc[i] = (self.int_cau_cap[i] - self.int_cau_cap[i + 1]) / (
                    self.int_cau_res[i] - self.int_cau_res[i + 1]
                )

    def lanczos(self):

        res, cap = eng.lanczos_inner(self.therm_capa_fost, self.therm_resist_fost)

        self.cau_res = np.array(res)
        self.cau_cap = np.array(cap)

        if np.any(self.cau_res[self.cau_res < 0.0]) or np.any(
            self.cau_res[self.cau_cap < 0.0]
        ):
            logger.error("\n negative values encountered at length", len(self.cau_cap))

        if self.blockwise_sum_width > 1:

            # Calculate the number of blocks
            num_blocks = len(self.cau_res) // self.blockwise_sum_width

            # Create an array of indices for each block
            indices = np.arange(num_blocks) * self.blockwise_sum_width

            # Calculate the blockwise sum
            self.cau_res = np.add.reduceat(self.cau_res, indices)
            self.cau_cap = np.add.reduceat(self.cau_cap, indices)

        self.int_cau_res = np.cumsum(self.cau_res)
        self.int_cau_cap = np.cumsum(self.cau_cap)

        self.diff_struc = np.zeros(len(self.int_cau_res) - 1)

        for i in range(len(self.int_cau_res) - 1):
            if not (self.int_cau_res[i] - self.int_cau_res[i + 1]) == 0.0:
                self.diff_struc[i] = (self.int_cau_cap[i] - self.int_cau_cap[i + 1]) / (
                    self.int_cau_res[i] - self.int_cau_res[i + 1]
                )
