import numpy as np
import scipy.integrate as sin
import os
import logging

from . import transient_optimization as top
from .transient_figures import StructureFigure

logger = logging.getLogger("PyRthLogger")


class DataExporter(StructureFigure):

    disable_all_figures = False

    def perform_action(self, condition, action):
        """Execute action if condition is True and figures are not disabled.

        Args:
            condition: Boolean determining if action should execute
            action: Callable to execute if condition is True
        """
        if condition and not self.disable_all_figures:
            logger.debug(f"Executing action {action.__name__}")
            action()
        else:
            logger.debug(
                f"Skipping action {action.__name__}, condition={condition}, disable_figures={self.disable_all_figures}"
            )

    def save_csv(self, save_flag, filename, data1, data2):
        if save_flag:
            logger.debug(f"Saving CSV file: {filename}_{self.label}.csv")
            output_dir = os.path.join(self.output_dir, "csv")
            os.makedirs(output_dir, exist_ok=True)
            csv_path = os.path.join(output_dir, f"{filename}_{self.label}.csv")
            np.savetxt(
                csv_path,
                np.transpose([data1, data2]),
            )
        else:
            logger.debug(f"Skipping saving CSV file: {filename}_{self.label}.csv")

    def temp_data_handler(self):
        logger.debug("temp_data_handler called")
        if not self.read_mode in ["clean_csv", "clean", "none"]:
            self.perform_action(self.look_at_raw_data, self.make_raw_figure)
            self.perform_action(self.look_at_voltage, self.make_voltage_figure)

            self.save_csv(
                self.save_voltage,
                "voltage",
                self.time_raw,
                self.voltage,
            )

        self.perform_action(self.look_at_temp, self.make_temp_figure)

        if self.look_at_extrpl and self.conv_mode in {
            "TDIM",
            "volt_extr",
            "k_factor",
            "t3ster",
        }:
            self.perform_action(True, lambda: self.make_extrpl_figure(self.expl_ft_prm))

        self.save_csv(
            self.save_temperature,
            "temperature",
            np.exp(self.log_time),
            self.temperature,
        )

        if self.save_temperature and self.read_mode != "clean_csv":
            self.save_csv(
                True,
                "temp_raw",
                self.time_raw,
                self.temp_raw,
            )

    def impedance_data_handler(self):
        logger.debug("impedance_data_handler called")
        self.perform_action(self.look_at_z_curve, self.make_z_curve_figure)
        self.perform_action(self.look_at_deriv, self.make_deriv_figure)

        self.save_csv(
            self.save_impedance,
            "impedance",
            np.exp(self.log_time),
            self.impedance,
        )
        self.save_csv(
            self.save_impedance_smooth,
            "impedance_smooth",
            np.exp(self.log_time_interp),
            self.imp_smooth,
        )
        self.save_csv(
            self.save_derivative,
            "derivative",
            np.exp(self.log_time_pad),
            self.imp_deriv_interp,
        )

    def fft_data_handler(self):
        logger.debug("fft_data_handler called")
        if not self.bayesian:
            self.perform_action(self.look_at_fft, self.make_fft_figure)
            self.save_csv(
                self.save_frequency,
                "frequency",
                self.fft_freq,
                self.fft_idi,
            )

    def time_spec_data_handler(self):
        logger.debug("time_spec_data_handler called")
        if self.save_back_impedance or (
            (self.look_at_backwards_imp_deriv or self.look_at_backwards_impedance)
            and not self.disable_all_figures
        ):
            self.back_imp_deriv, self.back_imp = top.time_const_to_imp(
                self.log_time_pad, self.time_spec
            )

        actions = [
            (self.look_at_time_spec, self.make_time_spec_figure),
            (self.look_at_sum_time_spec, self.make_sum_time_spec_figure),
            (self.look_at_backwards_impedance, self.make_backwards_impedance_figure),
            (self.look_at_backwards_imp_deriv, self.make_backwards_imp_deriv_figure),
        ]

        for condition, method in actions:
            self.perform_action(condition, method)

        self.save_csv(
            self.save_back_impedance,
            "back_impedance",
            np.exp(self.log_time_pad),
            self.back_imp,
        )
        self.save_csv(
            self.save_back_derivative,
            "back_derivative",
            np.exp(self.log_time_pad),
            self.back_imp_deriv,
        )

        if self.save_time_spec:
            prefix = "time_spec_bay" if self.bayesian else "time_spec_fft"
            self.save_csv(
                True,
                prefix,
                np.exp(self.log_time_pad),
                self.time_spec,
            )

        if self.save_sum_time_spec:
            sum_time_spec = sin.cumulative_trapezoid(
                self.time_spec, x=self.log_time_pad, initial=0.0
            )
            prefix = "sum_time_spec_bay" if self.bayesian else "sum_time_spec_fft"
            self.save_csv(
                True,
                prefix,
                np.exp(self.log_time_pad),
                sum_time_spec,
            )

    def structure_function_data_handler(self):
        logger.debug("structure_function_data_handler called")
        figures = [
            (self.look_at_cumul_struc, self.make_cumul_struc_figure),
            (self.look_at_diff_struc, self.make_diff_struc_figure),
            (self.look_at_local_resist, self.make_local_resist_figure),
        ]

        for condition, method in figures:
            self.perform_action(condition, method)

        self.save_csv(
            self.save_cumul_struc,
            "cumul_struc",
            self.int_cau_res,
            self.int_cau_cap,
        )

        if self.save_diff_struc:
            self.save_csv(
                True,
                "diff_struc",
                self.int_cau_res[:-1],
                self.diff_struc,
            )

        if self.save_local_resist_struc:
            self.save_csv(
                True,
                "local_resist_struc",
                self.int_cau_cap,
                self.cau_res,
            )

    def theo_structure_function_data_handler(self):
        logger.debug("theo_structure_function_data_handler called")
        figures = [
            (self.look_at_theo_cstruc, self.make_theo_cstruc_figure),
            (self.look_at_theo_diff_struc, self.make_theo_diff_struc_figure),
        ]

        for condition, method in figures:
            self.perform_action(condition, method)

        self.save_csv(
            self.save_theo_struc,
            "theo_struc",
            self.theo_int_cau_res,
            self.theo_int_cau_cap,
        )
        self.save_csv(
            self.save_theo_diff_struc,
            "theo_diff_struc",
            self.theo_int_cau_res[:-1],
            self.theo_diff_struc,
        )

    def theo_data_handler(self):
        logger.debug("theo_data_handler called")
        sum_theo_time_spec = sin.cumulative_trapezoid(
            self.theo_time_const, x=self.theo_log_time, initial=0.0
        )
        theo_log_time_coarse = np.linspace(
            self.theo_log_time[0], self.theo_log_time[-1], 2000
        )

        data_to_interpolate = {
            "theo_time_spec_coarse": self.theo_time_const,
            "sum_theo_time_spec_coarse": sum_theo_time_spec,
            "theo_imp_deriv_coarse": self.theo_imp_deriv,
            "theo_impedance_coarse": self.theo_impedance,
        }

        interpolated_data = {}
        for key, data in data_to_interpolate.items():
            interpolated_data[key] = np.interp(
                theo_log_time_coarse, self.theo_log_time, data
            )

        figures = {
            self.look_at_theo_time_const: self.make_theo_time_const_figure,
            self.look_at_theo_sum_time_const: self.make_theo_sum_time_const_figure,
            self.look_at_theo_imp_deriv: self.make_theo_imp_deriv_figure,
            self.look_at_theo_impedance: self.make_theo_impedance_figure,
        }

        for condition, method in figures.items():
            self.perform_action(condition, method)

        data_pairs = [
            (np.exp(self.theo_log_time), self.theo_time_const),
            (np.exp(theo_log_time_coarse), interpolated_data["theo_time_spec_coarse"]),
            (np.exp(self.theo_log_time), sum_theo_time_spec),
            (
                np.exp(theo_log_time_coarse),
                interpolated_data["sum_theo_time_spec_coarse"],
            ),
            (np.exp(self.theo_log_time), self.theo_imp_deriv),
            (np.exp(theo_log_time_coarse), interpolated_data["theo_imp_deriv_coarse"]),
            (np.exp(self.theo_log_time), self.theo_impedance),
            (np.exp(theo_log_time_coarse), interpolated_data["theo_impedance_coarse"]),
        ]

        filenames = [
            "theo_time_const",
            "theo_coarse_time_const",
            "theo_sum_time_const",
            "theo_coarse_sum_time_const",
            "theo_imp_deriv",
            "theo_coarse_imp_deriv",
            "theo_impedance",
            "theo_coarse_impedance",
        ]

        save_flags = [
            self.save_theo_time_const,
            self.save_theo_time_const,
            self.save_theo_time_const,
            self.save_theo_time_const,
            self.save_theo_imp_deriv,
            self.save_theo_imp_deriv,
            self.save_theo_impedance,
            self.save_theo_impedance,
        ]

        for save_flag, filename, data in zip(save_flags, filenames, data_pairs):
            self.save_csv(save_flag, filename, *data)

    def theo_compare_data_handler(self):
        logger.debug("theo_compare_data_handler called")
        self.perform_action(
            self.look_at_theo_backwards_impedance,
            self.make_theo_backwards_impedance_figure,
        )

    def optimize_data_handler(self):
        logger.debug("optimize_data_handler called")
        self.perform_action(
            self.look_at_optimize_struc_figure, self.make_optimize_struc_figure
        )

    def comparison_data_handler(self):
        logger.debug("comparison_data_handler called")
        figures = [
            (self.look_at_time_const_comparison, self.make_time_const_comparison),
            (self.look_at_struc_comparison, self.make_struc_comparison),
            (self.look_at_total_resist_comparison, self.make_total_resist_comparison),
        ]

        for condition, method in figures:
            self.perform_action(condition, method)

        comparisons = [
            (self.time_const_comparison, "time_const_comparison"),
            (
                self.time_const_comparison / np.amax(self.time_const_comparison),
                "time_const_comparison_relative",
            ),
            (self.structure_comparison, "struc_comparison"),
            (
                self.structure_comparison / np.amax(self.structure_comparison),
                "struc_comparison_relative",
            ),
            (self.total_resist_diff, "total_resist_comparison"),
            (
                self.total_resist_diff / np.amax(self.total_resist_diff),
                "total_resist_comparison_relative",
            ),
        ]

        save_flags = [
            self.save_time_const_comparison,
            self.save_time_const_comparison,
            self.save_struc_comparison,
            self.save_struc_comparison,
            self.save_total_resist_comparison,
            self.save_total_resist_comparison,
        ]

        for save_flag, (data, filename) in zip(save_flags, comparisons):
            self.save_csv(
                save_flag,
                filename,
                self.mod_value_list,
                data,
            )

    def prediction_data_handler(self):
        logger.debug("prediction_data_handler called")
        self.perform_action(self.look_at_prediction_figure, self.make_prediction_figure)
        self.perform_action(
            self.look_at_prediction_figure, self.make_prediction_impulse_used_figure
        )

        if self.save_prediction:
            self.save_csv(
                True,
                "impedance_actual",
                self.actual_time,
                self.actual_impedance,
            )
            self.save_csv(
                True,
                "impedance_prediction",
                self.lin_time,
                self.predicted_impedance,
            )
            self.save_csv(
                True,
                "power_prediction",
                self.power_t,
                self.power_function,
            )

    def residual_data_handler(self):
        logger.debug("residual_data_handler called")
        self.perform_action(self.look_at_residual_figure, self.make_residual_figure)

        if self.save_residual:
            self.save_csv(
                True,
                "residual_bins",
                self.bins,
                self.hist,
            )
            self.save_csv(
                True,
                "residual_fit",
                self.bins,
                self.gaus_curve,
            )

    def boot_data_handler(self):
        logger.debug("boot_data_handler called")
        actions = [
            (self.look_at_boot_z_curve, self.make_boot_z_curve_figure),
            (self.look_at_boot_deriv, self.make_boot_deriv_figure),
            (self.look_at_boot_time_spec, self.make_boot_time_spec_figure),
            (self.look_at_boot_sum_time_spec, self.make_boot_sum_time_spec_figure),
            (self.look_at_boot_cumul_struc, self.make_boot_cumul_struc_figure),
        ]

        for condition, method in actions:
            self.perform_action(condition, method)

        boot_data = [
            (
                self.save_boot_z_curve_figure,
                "boot_z_curve_figure_av_coarse",
                np.exp(self.imp_z_coarse),
                self.imp_av_coarse,
            ),
            (
                self.save_boot_z_curve_figure,
                "boot_z_curve_figure_u_coarse",
                np.exp(self.imp_z_coarse),
                self.imp_perc_u_coarse,
            ),
            (
                self.save_boot_z_curve_figure,
                "boot_z_curve_figure_l_coarse",
                np.exp(self.imp_z_coarse),
                self.imp_perc_l_coarse,
            ),
            (
                self.save_boot_deriv_figure,
                "boot_deriv_figure_av",
                np.exp(self.deriv_time),
                self.deriv_av,
            ),
            (
                self.save_boot_deriv_figure,
                "boot_deriv_figure_u",
                np.exp(self.deriv_time),
                self.deriv_perc_u,
            ),
            (
                self.save_boot_deriv_figure,
                "boot_deriv_figure_l",
                np.exp(self.deriv_time),
                self.deriv_perc_l,
            ),
            (
                self.save_boot_time_spec,
                "boot_time_spec_av",
                np.exp(self.deriv_time),
                self.time_spec_av,
            ),
            (
                self.save_boot_time_spec,
                "boot_time_spec_u",
                np.exp(self.deriv_time),
                self.time_spec_perc_u,
            ),
            (
                self.save_boot_time_spec,
                "boot_time_spec_l",
                np.exp(self.deriv_time),
                self.time_spec_perc_l,
            ),
            (
                self.save_boot_sum_time_spec,
                "boot_sum_time_spec_av",
                np.exp(self.deriv_time),
                self.sum_time_spec_av,
            ),
            (
                self.save_boot_sum_time_spec,
                "boot_sum_time_spec_u",
                np.exp(self.deriv_time),
                self.sum_time_spec_perc_u,
            ),
            (
                self.save_boot_sum_time_spec,
                "boot_sum_time_spec_l",
                np.exp(self.deriv_time),
                self.sum_time_spec_perc_l,
            ),
            (
                self.save_boot_cumul_struc,
                "boot_cumul_struc_av",
                self.res_fine,
                self.struc_cap_av,
            ),
            (
                self.save_boot_cumul_struc,
                "boot_cumul_struc_u",
                self.res_fine,
                self.struc_cap_perc_u,
            ),
            (
                self.save_boot_cumul_struc,
                "boot_cumul_struc_l",
                self.res_fine,
                self.struc_cap_perc_l,
            ),
            (
                self.save_boot_cumul_struc_coarse,
                "boot_cumul_struc_av_coarse",
                self.res_coarse,
                self.struc_cap_av_coarse,
            ),
            (
                self.save_boot_cumul_struc_coarse,
                "boot_cumul_struc_u_coarse",
                self.res_coarse,
                self.struc_cap_perc_u_coarse,
            ),
            (
                self.save_boot_cumul_struc_coarse,
                "boot_cumul_struc_l_coarse",
                self.res_coarse,
                self.struc_cap_perc_l_coarse,
            ),
        ]

        for save_flag, filename, data1, data2 in boot_data:
            self.save_csv(save_flag, filename, data1, data2)
