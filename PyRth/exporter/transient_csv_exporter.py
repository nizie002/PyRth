import numpy as np
import numpy.polynomial.polynomial as poly
import scipy.integrate as sin
import os
import logging

from .transient_base_exporter import BaseExporter

logger = logging.getLogger("PyRthLogger")


class CSVExporter(BaseExporter):

    type = "DataExporter"

    def save_csv(self, save_flag, filename, data1, data2):
        if save_flag:
            filename = f"{filename}.csv"
            logger.debug(f"Saving CSV file: {filename}")
            np.savetxt(
                filename,
                np.transpose([data1, data2]),
            )
        else:
            logger.debug(f"Skipping saving CSV file: {filename}")

    def construct_filename(self, module, name):
        csv_output_dir = os.path.join(module.output_dir, module.label, "csv")
        os.makedirs(csv_output_dir, exist_ok=True)
        return os.path.join(csv_output_dir, name)

    def extrapol_data_handler(self, module):
        logger.debug("extrapol_data_handler called")
        self.save_csv(
            module.save_extrpl,
            self.construct_filename(module, "exptrapolate_full"),
            np.sqrt(module.time_raw),
            module.temp_raw,
        )
        self.save_csv(
            module.save_extrpl,
            self.construct_filename(module, "exptrapolate_fitting_values"),
            np.sqrt(module.time_raw[module.lower_fit_index : module.upper_fit_index]),
            module.temp_raw[module.lower_fit_index : module.upper_fit_index],
        )
        self.save_csv(
            module.save_extrpl,
            self.construct_filename(module, "exptrapolate_polyval"),
            np.sqrt(module.time_raw),
            poly.polyval(np.sqrt(module.time_raw), module.expl_ft_prm),
        )

    def voltage_data_handler(self, module):
        logger.debug("voltage_data_handler called")

        self.save_csv(
            module.save_voltage,
            self.construct_filename(module, "voltage"),
            module.time_raw,
            module.voltage,
        )

    def temp_data_handler(self, module):
        logger.debug("temp_data_handler called")

        self.save_csv(
            module.save_temperature,
            self.construct_filename(module, "temperature"),
            np.exp(module.log_time),
            module.temperature,
        )

        self.save_csv(
            module.save_temperature,
            self.construct_filename(module, "temp_raw"),
            module.time_raw,
            module.temp_raw,
        )

    def impedance_data_handler(self, module):
        logger.debug("impedance_data_handler called")

        self.save_csv(
            module.save_impedance,
            self.construct_filename(module, "impedance"),
            np.exp(module.log_time),
            module.impedance,
        )
        self.save_csv(
            module.save_impedance_smooth,
            self.construct_filename(module, "impedance_smooth"),
            np.exp(module.log_time_interp),
            module.imp_smooth,
        )
        self.save_csv(
            module.save_derivative,
            self.construct_filename(module, "derivative"),
            np.exp(module.log_time_pad),
            module.imp_deriv_interp,
        )

    def fft_data_handler(self, module):
        logger.debug("fft_data_handler called")

        self.save_csv(
            module.save_frequency,
            self.construct_filename(module, "frequency"),
            module.fft_freq,
            module.fft_idi,
        )

    def time_spec_data_handler(self, module):
        logger.debug("time_spec_data_handler called")

        self.save_csv(
            module.save_back_impedance,
            self.construct_filename(module, "back_impedance"),
            np.exp(module.log_time_pad),
            module.back_imp,
        )
        self.save_csv(
            module.save_back_derivative,
            self.construct_filename(module, "back_derivative"),
            np.exp(module.log_time_pad),
            module.back_imp_deriv,
        )

        self.save_csv(
            module.save_time_spec,
            self.construct_filename(module, "time_spec"),
            np.exp(module.log_time_pad),
            module.time_spec,
        )

        if module.save_sum_time_spec:

            self.save_csv(
                True,
                self.construct_filename(module, "sum_time_spec"),
                np.exp(module.log_time_pad),
                module.sum_time_spec,
            )

    def structure_function_data_handler(self, module):
        logger.debug("structure_function_data_handler called")

        self.save_csv(
            module.save_cumul_struc,
            self.construct_filename(module, "cumul_struc"),
            module.int_cau_res,
            module.int_cau_cap,
        )

        if module.save_diff_struc:
            self.save_csv(
                True,
                self.construct_filename(module, "diff_struc"),
                module.int_cau_res[:-1],
                module.diff_struc,
            )

        if module.save_local_resist_struc:
            self.save_csv(
                True,
                self.construct_filename(module, "local_resist_struc"),
                module.int_cau_cap,
                module.cau_res,
            )

    def theo_structure_function_data_handler(self, module):
        logger.debug("theo_structure_function_data_handler called")

        self.save_csv(
            module.save_theo_struc,
            self.construct_filename(module, "theo_struc"),
            module.theo_int_cau_res,
            module.theo_int_cau_cap,
        )
        self.save_csv(
            module.save_theo_diff_struc,
            self.construct_filename(module, "theo_diff_struc"),
            module.theo_int_cau_res[:-1],
            module.theo_diff_struc,
        )

    def theo_data_handler(self, module):
        logger.debug("theo_data_handler called")
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
            self.construct_filename(module, "theo_time_const"),
            self.construct_filename(module, "theo_sum_time_const"),
            self.construct_filename(module, "theo_imp_deriv"),
            self.construct_filename(module, "theo_impedance"),
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

        for save_flag, filename, data in zip(save_flags, filenames, data_pairs):
            self.save_csv(save_flag, filename, *data)

    def comparison_data_handler(self, module):
        logger.debug("comparison_data_handler called")

        comparisons = [
            (module.time_const_comparison, "time_const_comparison"),
            (module.structure_comparison, "struc_comparison"),
            (module.total_resist_diff, "total_resist_comparison"),
        ]

        save_flags = [
            module.save_time_const_comparison,
            module.save_struc_comparison,
            module.save_total_resist_comparison,
        ]

        for save_flag, (data, filename) in zip(save_flags, comparisons):
            self.save_csv(
                save_flag,
                self.construct_filename(module, filename),
                module.mod_value_list,
                data,
            )

    def prediction_data_handler(self, module):
        logger.debug("prediction_data_handler called")

        if module.save_prediction:
            self.save_csv(
                True,
                self.construct_filename(module, "impedance_prediction"),
                module.lin_time,
                module.predicted_temperature,
            )
            self.save_csv(
                True,
                self.construct_filename(module, "power_prediction"),
                module.power_t,
                module.power_function,
            )

    def residual_data_handler(self, module):
        logger.debug("residual_data_handler called")

        if module.save_residual:
            self.save_csv(
                True,
                self.construct_filename(module, "residual_bins"),
                module.bins,
                module.hist,
            )
            self.save_csv(
                True,
                self.construct_filename(module, "residual_fit"),
                module.bins,
                module.gauss_curve,
            )

    def boot_data_handler(self, module):
        logger.debug("boot_data_handler called")

        boot_data = [
            (
                module.save_boot_impedance,
                "boot_deriv_figure_av",
                np.exp(module.boot_imp_time),
                module.boot_imp_av,
            ),
            (
                module.save_boot_impedance,
                "boot_deriv_figure_u",
                np.exp(module.boot_imp_time),
                module.boot_imp_perc_u,
            ),
            (
                module.save_boot_impedance,
                "boot_deriv_figure_l",
                np.exp(module.boot_imp_time),
                module.boot_imp_perc_l,
            ),
            (
                module.save_boot_deriv,
                "boot_deriv_figure_av",
                np.exp(module.boot_deriv_time),
                module.boot_deriv_av,
            ),
            (
                module.save_boot_deriv,
                "boot_deriv_figure_u",
                np.exp(module.boot_deriv_time),
                module.boot_deriv_perc_u,
            ),
            (
                module.save_boot_deriv,
                "boot_deriv_figure_l",
                np.exp(module.boot_deriv_time),
                module.boot_deriv_perc_l,
            ),
            (
                module.save_boot_time_spec,
                "boot_time_spec_av",
                np.exp(module.boot_deriv_time),
                module.boot_time_spec_av,
            ),
            (
                module.save_boot_time_spec,
                "boot_time_spec_u",
                np.exp(module.boot_deriv_time),
                module.boot_time_spec_perc_u,
            ),
            (
                module.save_boot_time_spec,
                "boot_time_spec_l",
                np.exp(module.boot_deriv_time),
                module.boot_time_spec_perc_l,
            ),
            (
                module.save_boot_sum_time_spec,
                "boot_sum_time_spec_av",
                np.exp(module.boot_deriv_time),
                module.boot_sum_time_spec_av,
            ),
            (
                module.save_boot_sum_time_spec,
                "boot_sum_time_spec_u",
                np.exp(module.boot_deriv_time),
                module.boot_sum_time_spec_perc_u,
            ),
            (
                module.save_boot_sum_time_spec,
                "boot_sum_time_spec_l",
                np.exp(module.boot_deriv_time),
                module.boot_sum_time_spec_perc_l,
            ),
            (
                module.save_boot_cumul_struc,
                "boot_cumul_struc_av",
                module.boot_struc_res_fine,
                module.boot_struc_cap_av,
            ),
            (
                module.save_boot_cumul_struc,
                "boot_cumul_struc_u",
                module.boot_struc_res_fine,
                module.boot_struc_cap_perc_u,
            ),
            (
                module.save_boot_cumul_struc,
                "boot_cumul_struc_l",
                module.boot_struc_res_fine,
                module.boot_struc_cap_perc_l,
            ),
        ]

        for save_flag, filename, data1, data2 in boot_data:
            constructed_filename = self.construct_filename(module, filename)
            self.save_csv(save_flag, constructed_filename, data1, data2)
