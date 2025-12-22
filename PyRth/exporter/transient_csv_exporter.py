"""CSV exporter utilities shared across evaluation pipelines.

Files are written to ``<output_dir>/<label>/csv`` with optional numeric
prefixes that mirror the figure ordering so artifacts stay grouped and
deterministic:

    000–010: raw input (voltage/temperature)
    020–022: extrapolation helpers
    100–120: impedance, smoothed, derivative, B(z)
    130: FFT frequency data
    200–210: time spectra (forward/backwards, sum)
    300–320: structure functions (cumulative/diff/local)
    400–450: theoretical spectra/structure/impedance
    600–620: comparison outputs
    700–710: prediction outputs
    720–721: residuals
    800–842: bootstrap artifacts (all distinct)
    900: performance spans

Prefixes are applied via ``construct_filename(..., prefix=\"NNN\")`` so
semantically different files never share an ID, matching the figure exporter.
"""

import logging
import os

import numpy as np
import numpy.polynomial.polynomial as poly
import scipy.integrate as sin

from .transient_base_exporter import BaseExporter

logger = logging.getLogger("PyRthLogger")


class CSVExporter(BaseExporter):
    """Persist module outputs as CSV files grouped by handler."""

    type = "DataExporter"

    def save_csv(self, save_flag, filename, data1, data2):
        """Write paired vectors to CSV when the corresponding save flag is enabled."""
        if not save_flag:
            return None

        filename = f"{filename}.csv"

        data1_array = np.asarray(data1)
        data2_array = np.asarray(data2)

        has_strings = data1_array.dtype.kind in [
            "U",
            "S",
            "O",
        ] or data2_array.dtype.kind in ["U", "S", "O"]

        if has_strings:
            np.savetxt(
                filename,
                np.transpose([data1, data2]),
                fmt="%s %s",
                delimiter=" ",
            )
        else:
            np.savetxt(
                filename,
                np.transpose([data1, data2]),
            )

        return filename

    def construct_filename(self, module, name, prefix=None):
        """Return the full CSV path for a given module label and artifact name."""
        csv_output_dir = os.path.join(module.output_dir, module.label, "csv")
        os.makedirs(csv_output_dir, exist_ok=True)
        if prefix:
            name = f"{prefix}_{name}"
        return os.path.join(csv_output_dir, name)

    def extrapol_data_handler(self, module):
        """Persist extrapolation inputs, fit window, and fitted polynomial values."""
        saved = []
        saved.append(
            self.save_csv(
                module.save_extrpl,
                self.construct_filename(module, "exptrapolate_full", prefix="020"),
                np.sqrt(module.time_raw),
                module.temp_raw,
            )
        )
        saved.append(
            self.save_csv(
                module.save_extrpl,
                self.construct_filename(module, "exptrapolate_fitting_values", prefix="021"),
                np.sqrt(module.time_raw[module.lower_fit_index : module.upper_fit_index]),
                module.temp_raw[module.lower_fit_index : module.upper_fit_index],
            )
        )
        saved.append(
            self.save_csv(
                module.save_extrpl,
                self.construct_filename(module, "exptrapolate_polyval", prefix="022"),
                np.sqrt(module.time_raw),
                poly.polyval(np.sqrt(module.time_raw), module.expl_ft_prm),
            )
        )
        return saved

    def voltage_data_handler(self, module):
        """Export raw voltage trace."""
        return [
            self.save_csv(
                module.save_voltage,
                self.construct_filename(module, "voltage", prefix="000"),
                module.time_raw,
                module.voltage,
            )
        ]

    def temp_data_handler(self, module):
        """Export processed temperature signals (log-time and raw)."""
        return [
            self.save_csv(
                module.save_temperature,
                self.construct_filename(module, "temperature", prefix="030"),
                np.exp(module.log_time),
                module.temperature,
            ),
            self.save_csv(
                module.save_temperature,
                self.construct_filename(module, "temp_raw", prefix="010"),
                module.time_raw,
                module.temp_raw,
            ),
        ]

    def impedance_data_handler(self, module):
        """Export impedance step, smoothed impedance, derivative, and B(z)."""
        return [
            self.save_csv(
                module.save_impedance,
                self.construct_filename(module, "impedance", prefix="100"),
                np.exp(module.log_time),
                module.impedance,
            ),
            self.save_csv(
                module.save_impedance_smooth,
                self.construct_filename(module, "impedance_smooth", prefix="101"),
                np.exp(module.log_time_interp),
                module.imp_smooth,
            ),
            self.save_csv(
                module.save_derivative,
                self.construct_filename(module, "derivative", prefix="110"),
                np.exp(module.log_time_pad),
                module.imp_deriv_interp,
            ),
            self.save_csv(
                module.save_bz,
                self.construct_filename(module, "bz_log_derivative", prefix="120"),
                np.exp(module.log_time_pad),
                module.bz_curve,
            ),
        ]

    def fft_data_handler(self, module):
        """Export FFT-domain data."""
        return [
            self.save_csv(
                module.save_frequency,
                self.construct_filename(module, "frequency", prefix="130"),
                module.fft_freq,
                module.fft_idi,
            )
        ]

    def time_spec_data_handler(self, module):
        """Export time-constant spectrum and optional cumulative sum/back projections."""
        saved = [
            self.save_csv(
                module.save_back_impedance,
                self.construct_filename(module, "back_impedance", prefix="200"),
                np.exp(module.log_time_pad),
                module.back_imp,
            ),
            self.save_csv(
                module.save_back_derivative,
                self.construct_filename(module, "back_derivative", prefix="201"),
                np.exp(module.log_time_pad),
                module.back_imp_deriv,
            ),
            self.save_csv(
                module.save_time_spec,
                self.construct_filename(module, "time_spec", prefix="202"),
                np.exp(module.log_time_pad),
                module.time_spec,
            ),
        ]

        if module.save_sum_time_spec:
            saved.append(
                self.save_csv(
                    True,
                    self.construct_filename(module, "sum_time_spec", prefix="210"),
                    np.exp(module.log_time_pad),
                    module.sum_time_spec,
                )
            )

        return saved

    def structure_function_data_handler(self, module):
        """Export cumulative, differential, and local-resistance structure functions."""
        saved = [
            self.save_csv(
                module.save_cumul_struc,
                self.construct_filename(module, "cumul_struc", prefix="300"),
                module.int_cau_res,
                module.int_cau_cap,
            )
        ]

        if module.save_diff_struc:
            saved.append(
                self.save_csv(
                    True,
                    self.construct_filename(module, "diff_struc", prefix="310"),
                    module.int_cau_res[:-1],
                    module.diff_struc,
                )
            )

        if module.save_local_resist_struc:
            saved.append(
                self.save_csv(
                    True,
                    self.construct_filename(module, "local_resist_struc", prefix="320"),
                    module.int_cau_cap,
                    module.cau_res,
                )
            )

        return saved

    def theo_structure_function_data_handler(self, module):
        """Export theoretical structure-function curves."""
        return [
            self.save_csv(
                module.save_theo_struc,
                self.construct_filename(module, "theo_struc", prefix="400"),
                module.theo_int_cau_res,
                module.theo_int_cau_cap,
            ),
            self.save_csv(
                module.save_theo_diff_struc,
                self.construct_filename(module, "theo_diff_struc", prefix="410"),
                module.theo_int_cau_res[:-1],
                module.theo_diff_struc,
            ),
        ]

    def theo_data_handler(self, module):
        """Export theoretical spectra, cumulative spectrum, and impedance/derivative."""
        sum_theo_time_spec = sin.cumulative_trapezoid(
            module.theo_time_const, x=module.theo_log_time, initial=0.0
        )

        data_pairs = [
            (np.exp(module.theo_log_time), module.theo_time_const),
            (np.exp(module.theo_log_time), sum_theo_time_spec),
            (np.exp(module.theo_log_time), module.theo_imp_deriv),
            (np.exp(module.theo_log_time), module.theo_impedance),
        ]

        filenames = [
            self.construct_filename(module, "theo_time_const", prefix="420"),
            self.construct_filename(module, "theo_sum_time_const", prefix="430"),
            self.construct_filename(module, "theo_imp_deriv", prefix="440"),
            self.construct_filename(module, "theo_impedance", prefix="450"),
        ]

        save_flags = [
            module.save_theo_time_const,
            module.save_theo_time_const,
            module.save_theo_time_const,
            module.save_theo_time_const,
            module.save_theo_imp_deriv,
            module.save_theo_imp_deriv,
            module.save_theo_impedance,
            module.save_theo_impedance,
        ]

        saved = []
        for save_flag, filename, data in zip(save_flags, filenames, data_pairs):
            saved.append(self.save_csv(save_flag, filename, *data))
        return saved

    def comparison_data_handler(self, module):
        """Export comparison metrics across evaluated modules."""
        comparisons = [
            (module.time_const_comparison, "time_const_comparison", "600"),
            (module.structure_comparison, "struc_comparison", "610"),
            (module.total_resist_diff, "total_resist_comparison", "620"),
        ]

        save_flags = [
            module.save_time_const_comparison,
            module.save_struc_comparison,
            module.save_total_resist_comparison,
        ]

        saved = []
        for save_flag, (data, filename, prefix) in zip(save_flags, comparisons):
            saved.append(
                self.save_csv(
                    save_flag,
                    self.construct_filename(module, filename, prefix=prefix),
                    module.mod_value_list,
                    data,
                )
            )
        return saved

    def prediction_data_handler(self, module):
        """Export temperature and power predictions when enabled."""
        if not module.save_prediction:
            return []

        return [
            self.save_csv(
                True,
                self.construct_filename(module, "impedance_prediction", prefix="700"),
                module.lin_time_pos,
                module.predicted_temperature,
            ),
            self.save_csv(
                True,
                self.construct_filename(module, "power_prediction", prefix="710"),
                module.power_t,
                module.power_function,
            ),
        ]

    def residual_data_handler(self, module):
        """Export residual histogram and Gaussian fit."""
        if not module.save_residual:
            return []

        return [
            self.save_csv(
                True,
                self.construct_filename(module, "residual_bins", prefix="720"),
                module.bins,
                module.hist,
            ),
            self.save_csv(
                True,
                self.construct_filename(module, "residual_fit", prefix="721"),
                module.bins,
                module.gauss_curve,
            ),
        ]

    def perf_data_handler(self, module):
        """Export performance monitor spans as CSV."""
        if not getattr(module, "perf_eval", False) or not getattr(module, "save_perf", False):
            return []

        spans = getattr(getattr(module, "perf_monitor", None), "spans", lambda: [])()
        if not spans:
            return []

        names, durations = zip(*spans)
        return [
            self.save_csv(
                True,
                self.construct_filename(module, "performance_spans", prefix="900"),
                names,
                durations,
            )
        ]

    def boot_data_handler(self, module):
        """Export bootstrap-derived impedance, derivative, spectrum, and structure stats."""
        boot_data = [
            (
                module.save_boot_impedance,
                "boot_deriv_figure_av",
                "800",
                np.exp(module.boot_imp_time),
                module.boot_imp_av,
            ),
            (
                module.save_boot_impedance,
                "boot_deriv_figure_u",
                "801",
                np.exp(module.boot_imp_time),
                module.boot_imp_perc_u,
            ),
            (
                module.save_boot_impedance,
                "boot_deriv_figure_l",
                "802",
                np.exp(module.boot_imp_time),
                module.boot_imp_perc_l,
            ),
            (
                module.save_boot_deriv,
                "boot_deriv_figure_av",
                "810",
                np.exp(module.boot_deriv_time),
                module.boot_deriv_av,
            ),
            (
                module.save_boot_deriv,
                "boot_deriv_figure_u",
                "811",
                np.exp(module.boot_deriv_time),
                module.boot_deriv_perc_u,
            ),
            (
                module.save_boot_deriv,
                "boot_deriv_figure_l",
                "812",
                np.exp(module.boot_deriv_time),
                module.boot_deriv_perc_l,
            ),
            (
                module.save_boot_time_spec,
                "boot_time_spec_av",
                "820",
                np.exp(module.boot_deriv_time),
                module.boot_time_spec_av,
            ),
            (
                module.save_boot_time_spec,
                "boot_time_spec_u",
                "821",
                np.exp(module.boot_deriv_time),
                module.boot_time_spec_perc_u,
            ),
            (
                module.save_boot_time_spec,
                "boot_time_spec_l",
                "822",
                np.exp(module.boot_deriv_time),
                module.boot_time_spec_perc_l,
            ),
            (
                module.save_boot_sum_time_spec,
                "boot_sum_time_spec_av",
                "830",
                np.exp(module.boot_deriv_time),
                module.boot_sum_time_spec_av,
            ),
            (
                module.save_boot_sum_time_spec,
                "boot_sum_time_spec_u",
                "831",
                np.exp(module.boot_deriv_time),
                module.boot_sum_time_spec_perc_u,
            ),
            (
                module.save_boot_sum_time_spec,
                "boot_sum_time_spec_l",
                "832",
                np.exp(module.boot_deriv_time),
                module.boot_sum_time_spec_perc_l,
            ),
            (
                module.save_boot_cumul_struc,
                "boot_cumul_struc_av",
                "840",
                module.boot_struc_res_fine,
                module.boot_struc_cap_av,
            ),
            (
                module.save_boot_cumul_struc,
                "boot_cumul_struc_u",
                "841",
                module.boot_struc_res_fine,
                module.boot_struc_cap_perc_u,
            ),
            (
                module.save_boot_cumul_struc,
                "boot_cumul_struc_l",
                "842",
                module.boot_struc_res_fine,
                module.boot_struc_cap_perc_l,
            ),
        ]

        saved = []
        for save_flag, filename, prefix, data1, data2 in boot_data:
            constructed_filename = self.construct_filename(module, filename, prefix=prefix)
            saved.append(self.save_csv(save_flag, constructed_filename, data1, data2))
        return saved
