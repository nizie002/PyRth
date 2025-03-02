import numpy as np
import numpy.polynomial.polynomial as poly
import scipy.integrate as sin
from matplotlib.lines import Line2D

from .transient_base_fig import StructureFigure


class RawDataFigure(StructureFigure):
    def make_figure(self):
        # Access data via self.module
        self.ax.set_title("Raw data")
        self.ax.set_xlabel(r"time, $t$, in s")
        self.ax.set_ylabel(r"temperature $T$, in $^\circ\!$C")

        self.ax.semilogx(
            self.module.time_raw, self.module.temp_raw, "x", label="raw data"
        )


class ExtrapolationFigure(StructureFigure):
    def make_figure(self):
        self.ax.set_title("Extrapolation")
        self.ax.set_xlabel(r"square root of time, $\sqrt{s}$, in s$^{1/2}$")
        self.ax.set_ylabel(r"temperature, $T$, in $^\circ\!$C")

        lower_fit_index = np.searchsorted(
            self.module.data[:, 0], self.module.lower_fit_limit
        )
        upper_fit_index = np.searchsorted(
            self.module.data[:, 0], self.module.upper_fit_limit
        )

        self.ax.plot(
            np.sqrt(self.time),
            self.module.temperature,
            label="temperatur",
            markersize=2.5,
            marker="o",
        )
        self.ax.plot(
            np.sqrt(self.module.time_raw), self.module.temp_raw, label="temp_raw"
        )
        self.ax.plot(
            np.sqrt(self.module.time_raw[lower_fit_index:upper_fit_index]),
            self.module.temp_raw[lower_fit_index:upper_fit_index],
            label="fit window",
            markersize=1.5,
            marker="o",
        )
        self.ax.plot(
            np.sqrt(self.module.time_raw),
            poly.polyval(np.sqrt(self.module.time_raw), self.module.expl_ft_prm),
            label="fit",
        )

        self.ax.set_xlim(
            0,
            np.sqrt(self.module.time_raw[upper_fit_index] * 2.5),
        )
        self.ax.set_ylim(
            self.module.temp_raw[lower_fit_index] * 0.75,
            self.module.temp_raw[upper_fit_index] * 1.25,
        )


class VoltageFigure(StructureFigure):
    def make_figure(self):
        self.ax.set_title("Voltage")
        self.ax.set_xlabel(r"time, $t$, in s")
        self.ax.set_ylabel(r"voltage, $U$, in V")

        self.ax.semilogx(
            self.module.time_raw,
            self.module.voltage,
            label=self.module.label,
            linewidth=0.0,
            markersize=1.5,
            marker="o",
            color=self.next_color(),
        )


class TempFigure(StructureFigure):
    def make_figure(self):
        self.ax.set_title("Temperature")
        self.ax.set_xlabel(r"time, $t$, in s")
        self.ax.set_ylabel(r"temperature, $T$, in $^\circ\!$C")

        self.ax.semilogx(
            self.module.time,
            self.module.temperature,
            label=self.module.label,
            linewidth=0.0,
            markersize=1.5,
            marker="o",
            color=self.next_color(),
        )


class ZCurveFigure(StructureFigure):
    def make_figure(self):
        self.ax.set_title("Thermal impedance")
        self.ax.set_xlabel(r"time, $t$, in s")
        self.ax.set_ylabel(r"thermal impedance, $Z_{\rm th}$, in K$\cdot$ W$^{-1}$")

        self.ax.semilogx(
            np.exp(self.module.log_time),
            self.module.impedance,
            linewidth=0.0,
            marker="o",
            markersize=1.5,
            label="impedance",
            color=self.next_color(),
        )
        self.ax.semilogx(
            np.exp(self.module.log_time_interp),
            self.module.imp_smooth,
            linewidth=1.5,
            markersize=0.0,
            label="local average",
            color=self.same_color(),
        )


class DerivFigure(StructureFigure):
    def make_figure(self):
        self.ax.set_title("Impulse response")
        self.ax.set_xlabel(r"time, $t$, in s")
        self.ax.set_ylabel(r"impulse response, $h$, in K$\cdot$ W$^{-1}$")

        self.ax.semilogx(
            np.exp(self.module.log_time_pad),
            self.module.imp_deriv_interp,
            marker="o",
            lw=1.5,
            label=self.module.label,
            markersize=0.0,
            color=self.next_color(),
        )


class FFTFigure(StructureFigure):
    def make_figure(self):
        self.ax.set_xlim(0, 7)
        self.ax.set_ylim(1e-6, 1e3)
        self.ax.set_title("Fourier transform")
        self.ax.set_xlabel(r"angular frequency, $\omega$,  in rad/s")
        self.ax.set_ylabel(r"power density, $|H|^2$, in (K $\cdot$ s W$^{-1})^2$")

        angular_freq = 2 * np.pi * self.module.fft_freq
        self.ax.semilogy(
            angular_freq, self.module.fft_idi_pegrm, "o", markersize=3, label="fft"
        )
        self.ax.semilogy(
            angular_freq,
            self.module.current_filter,
            "o",
            markersize=3,
            label="current filter",
        )
        self.ax.semilogy(
            angular_freq,
            self.module.fft_idi_pegrm * self.module.current_filter,
            "o",
            markersize=3,
            label="combined",
        )


class TimeSpecFigure(StructureFigure):
    def make_figure(self):

        self.ax.set_title("Time constant spectrum")
        self.ax.set_xlabel(r"time constant, $\tau$, in s")
        self.ax.set_ylabel(r"resistance, $R'$, in K$\cdot$ W$^{-1}$")

        self.ax.semilogx(
            np.exp(self.module.log_time_pad),
            self.module.time_spec,
            label="spectrum_" + self.module.label,
            lw=0.7,
            ms=3.0,
            marker="o",
            color=self.next_color(),
        )
        self.ax.semilogx(
            np.exp(self.module.crop_log_time),
            self.module.crop_time_spec,
            lw=0.0,
            ms=2.0,
            marker="o",
            color=self.same_color(),
        )


class SumTimeSpecFigure(StructureFigure):
    def make_figure(self):
        self.ax.set_title("Cumulative time constant spectrum")
        self.ax.set_xlabel(r"time constant, $\tau$, in s")
        self.ax.set_ylabel(r"cumulative resistance, $R'_\Sigma$, in K$\cdot$ W$^{-1}$")

        sum_time_spec = sin.cumulative_trapezoid(
            self.module.time_spec, x=self.module.log_time_pad, initial=0.0
        )

        self.ax.semilogx(
            np.exp(self.module.log_time_pad),
            sum_time_spec,
            label="spectrum_" + self.module.label,
            lw=1.0,
            ms=1.5,
            color=self.next_color(),
        )


class CumulStrucFigure(StructureFigure):
    def make_figure(self):
        self.ax.set_ylim(1e-6, 1e5)

        self.ax.set_title("Cumulative structure function")
        self.ax.set_xlabel(
            r"cumulative thermal resistance, $R_\Sigma$, in K$\cdot$ W$^{-1}$"
        )
        self.ax.set_ylabel(
            r"cumulative thermal capacity, $C_\Sigma$, in J$\cdot$ K$^{-1}$"
        )

        sliced = np.where(self.module.int_cau_cap <= 1e4)

        self.int_cau_res = self.module.int_cau_res[sliced]
        self.int_cau_cap = self.module.int_cau_cap[sliced]

        self.ax.semilogy(
            self.int_cau_res,
            self.int_cau_cap,
            color=self.next_color(),
            label="structure " + self.module.label,
            linewidth=1.0,
            markersize=1.5,
            marker="o",
        )


class DiffStrucFigure(StructureFigure):
    def make_figure(self):

        self.ax.set_ylim(1e-5, 1e5)

        self.ax.set_title("Differential structure function")
        self.ax.set_xlabel(r"thermal resistance, $R$, in K$\cdot$ W$^{-1}$")
        self.ax.set_ylabel(r"thermal capacity, $C$, in s$\cdot$ W$^2$ \cdot K$^{-2}$")

        self.int_cau_res = self.module.int_cau_res[:-1]
        self.diff_struc = self.module.diff_struc

        self.ax.semilogy(
            self.int_cau_res,
            self.diff_struc,
            color=self.next_color(),
            label="differential structure" + self.module.label,
            marker="o",
            markersize=2,
            linewidth=1.0,
        )


class LocalResistFigure(StructureFigure):
    def make_figure(self):
        self.ax.set_title("Local thermal resistance")
        self.ax.set_xlabel(r"thermal resistance, $R$, in K$\cdot$ W$^{-1}$")
        self.ax.set_ylabel(
            r"local thermal resistance, $R_{\rm loc}$, in K$\cdot$ W$^{-1}$"
        )

        self.ax.semilogx(
            (self.module.int_cau_cap),
            self.module.cau_res,
            color=self.next_color(),
            label="local_resistance_" + self.module.label,
            marker="o",
            markersize=2,
            linewidth=1.0,
        )


class LocalGradientFigure(StructureFigure):
    def make_figure(self):
        self.ax.set_xlim(1e-5, 1e2)

        self.ax.set_title("Local gradient diagram")
        self.ax.set_ylabel(
            r"thermal gradient, $R/C$, in K$^2$ $\cdot$ (s$\cdot$ W$^2$)$^{-1}$"
        )
        self.ax.set_xlabel(
            r"cumulative thermal capacity, $C_\Sigma$, in J$\cdot$ K$^{-1}$"
        )

        self.ax.semilogx(
            self.module.int_cau_cap,
            self.module.cau_res / self.module.cau_cap,
            color=self.next_color(),
            label="local_resistance_" + self.module.label,
            marker="o",
            markersize=2,
            linewidth=1.0,
        )


class TheoCStrucFigure(StructureFigure):
    def make_figure(self):
        self.ax.set_title("Theoretical cumulative structure function")
        self.ax.set_xlabel(
            r"cumulative thermal resistance, $R_\Sigma$, in K$\cdot$ W$^{-1}$"
        )
        self.ax.set_ylabel(
            r"cumulative thermal capacity, $C_\Sigma$, in J$\cdot$ K$^{-1}$"
        )

        self.ax.semilogy(
            self.module.theo_int_cau_res,
            self.module.theo_int_cau_cap,
            color=self.next_color(),
            label="optimized structure" + self.module.label,
            linewidth=3.0,
        )


class TheoDiffStrucFigure(StructureFigure):
    def make_figure(self):
        self.ax.set_title(r"Theoretical differential structure function")
        self.ax.set_xlabel(r"thermal resistance, $R$, in K$\cdot$ W$^{-1}$")
        self.ax.set_ylabel(r"thermal capacity, $C$, in s$\cdot$ W$^2$ $\cdot$ K$^{-2}$")

        self.ax.semilogy(
            self.module.theo_int_cau_res[:-1],
            self.module.theo_diff_struc,
            color=self.next_color(),
            label="theo diff structure" + self.module.label,
            marker="o",
            markersize=3,
            linewidth=1.0,
        )


class TheoLocalResistFigure(StructureFigure):
    def make_figure(self):
        self.ax.set_title("Theoretical local thermal resistance")
        self.ax.set_xlabel(
            r"cumulative thermal capacity, $C_\Sigma$, in J$\cdot$ K$^{-1}$"
        )
        self.ax.set_ylabel(r"thermal resistance, $R$, in K$\cdot$ W$^{-1}$")

        self.ax.semilogy(
            self.module.theo_int_cau_res,
            self.module.theo_int_cau_cap,
            label="optimized structure",
            linewidth=3.0,
        )


class TheoTimeConstFigure(StructureFigure):
    def make_figure(self):
        self.ax.set_title("Theoretical time constant spectrum")
        self.ax.set_xlabel(r"time constant, $\tau$, in s")
        self.ax.set_ylabel(r"resistance, $R'$, in K$\cdot$ W$^{-1}$")

        self.ax.semilogx(
            np.exp(self.module.theo_log_time),
            self.module.theo_time_const,
            marker="o",
            color=self.next_color(),
            label="optimized spectrum" + self.module.label,
            linewidth=1.0,
            markersize=1.5,
        )


class TheoSumTimeConstFigure(StructureFigure):
    def make_figure(self):
        self.ax.set_title("Theoretical cumulative time constant spectrum")
        self.ax.set_xlabel(r"time constant, $\tau$, in s")
        self.ax.set_ylabel(r"cumulative resistance, $R'_\Sigma$, in K$\cdot$ W$^{-1}$")

        sum_theo_time_spec = sin.cumulative_trapezoid(
            self.module.theo_time_const, x=self.module.theo_log_time, initial=0.0
        )

        self.ax.semilogx(
            np.exp(self.module.theo_log_time),
            sum_theo_time_spec,
            marker="o",
            color=self.next_color(),
            label="theoretical integrated spectrum " + self.module.label,
            linewidth=1.0,
            markersize=1.5,
        )


class TheoImpDerivFigure(StructureFigure):
    def make_figure(self):
        self.ax.set_title("Theoretical impulse response")
        self.ax.set_xlabel(r"time, $t$, in s")
        self.ax.set_ylabel(r"impulse response, $h$, in K$\cdot$ W$^{-1}$")

        self.ax.semilogx(
            np.exp(self.module.theo_log_time),
            self.module.theo_imp_deriv,
            linewidth=1.5,
            color=self.next_color(),
            label="theoretical derivative " + self.module.label,
            markersize=1.5,
        )


class TheoImpFigure(StructureFigure):
    def make_figure(self):
        self.ax.set_title("Theoretical thermal impedance")
        self.ax.set_xlabel(r"time, $t$, in s")
        self.ax.set_ylabel(r"thermal impedance, $Z_{\rm th}$, in K$\cdot$ W$^{-1}$")

        self.ax.semilogx(
            np.exp(self.module.theo_log_time),
            self.module.theo_impedance,
            linewidth=1.5,
            label="theoretical impedance " + self.module.label,
            color=self.next_color(),
        )


class BackwardsImpDerivFigure(StructureFigure):
    def make_figure(self):
        self.ax.set_title("Backwards impulse response")
        self.ax.set_xlabel(r"time, $t$, in s")
        self.ax.set_ylabel(r"impulse response, $h$, in K$\cdot$ W$^{-1}$")

        self.ax.semilogx(
            np.exp(self.module.log_time_pad),
            self.module.imp_deriv_interp,
            linewidth=1.5,
            label="original derivative " + self.module.label,
            markersize=1.5,
            color=self.next_color(),
        )
        self.ax.semilogx(
            np.exp(self.module.log_time_pad),
            self.module.back_imp_deriv,
            linewidth=0.0,
            marker="o",
            label="backwards derivative " + self.module.label,
            markersize=1.5,
            color=self.same_color(),
        )


class BackwardsImpFigure(StructureFigure):
    def make_figure(self):
        self.ax.set_title("Backwards thermal impedance")
        self.ax.set_xlabel(r"time, $t$, in s")
        self.ax.set_ylabel(r"thermal impedance, $Z_{\rm th}$, in K$\cdot$ W$^{-1}$")

        self.ax.semilogx(
            np.exp(self.module.log_time),
            self.module.impedance,
            linewidth=0.0,
            marker="o",
            markersize=1.0,
            label="original impedance " + self.module.label,
        )
        self.ax.semilogx(
            np.exp(self.module.log_time_pad),
            self.module.back_imp,
            linewidth=0.0,
            marker="o",
            markersize=2.0,
            label="backwards impedance " + self.module.label,
            color=self.next_color(),
        )
        self.ax.semilogx(
            np.exp(self.module.log_time_interp),
            self.module.imp_smooth,
            linewidth=1.5,
            markersize=0.0,
            label="local average",
            color=self.same_color(),
        )


class TheoBackwardsImpFigure(StructureFigure):
    def make_figure(self):
        self.ax.set_title("Theoretical backwards thermal impedance")
        self.ax.set_xlabel(r"time, $t$, in s")
        self.ax.set_ylabel(r"thermal impedance, $Z_{\rm th}$, in K$\cdot$ W$^{-1}$")

        self.ax.semilogx(
            np.exp(self.module.log_time_pad),
            self.module.back_imp,
            linewidth=3,
            marker="o",
            markersize=0.0,
            label="Bayesian impedance",
            zorder=5,
        )
        self.ax.semilogx(
            np.exp(self.module.theo_log_time),
            self.module.theo_impedance,
            linewidth=3,
            marker="o",
            markersize=0.0,
            label="optimized impedance",
            zorder=10,
        )
        self.ax.semilogx(
            np.exp(self.module.opt_log_time),
            self.module.opt_imp,
            linewidth=0.0,
            marker="o",
            markersize=6,
            label="measured impedance",
            zorder=0,
            fillstyle="none",
        )


class OptimizeStrucFigure(StructureFigure):
    def make_figure(self):
        self.ax.set_title("Optimized structure function")
        self.ax.set_xlabel(r"cumulative thermal resistance / K$\cdot$ W$^{-1}$")
        self.ax.set_ylabel(r"cumulative thermal capacity / J$\cdot$ K$^{-1}$")

        self.ax.semilogy(
            self.module.int_cau_res,
            self.module.int_cau_cap,
            label="structure " + self.module.label,
            linewidth=1.0,
            markersize=1.5,
        )

        self.ax.semilogy(
            self.module.init_opt_imp_res,
            self.module.init_opt_imp_cap,
            lw=0.0,
            ms=3,
            marker="o",
            label="init_opt_imp_cap",
        )

        if self.module.struc_init_method == "optimal_fit":
            self.ax.semilogy(
                self.module.init_opt_struc_res,
                self.module.init_opt_struc_cap,
                lw=0.0,
                ms=3,
                marker="o",
                label="init_opt_struc_cap",
            )

        self.ax.semilogy(
            self.module.fin_res,
            self.module.fin_cap,
            lw=0.0,
            ms=3,
            marker="o",
            label="opt_cap",
        )


class TimeConstComparisonFigure(StructureFigure):
    def make_figure(self):
        self.ax.set_title("Time constant accuracy comparison")
        self.ax.set_xlabel(self.module.mod_key_display_name.replace("_", " "))
        self.ax.set_ylabel(r"objective function time const")

        self.ax.scatter(
            self.module.mod_value_list,
            self.module.time_const_comparison,
            label="time_const_comparison" + self.module.label,
        )


class TotalResistComparisonFigure(StructureFigure):
    def make_figure(self):
        self.ax.set_title("Total resistance accuracy comparison")
        self.ax.set_xlabel(self.module.mod_key_display_name.replace("_", " "))
        self.ax.set_ylabel(r"total resistance difference")

        self.ax.scatter(
            self.module.mod_value_list,
            self.module.total_resist_diff,
            label="total_resist_comparison" + self.module.label,
        )


class StrucComparisonFigure(StructureFigure):
    def make_figure(self):
        self.ax.set_title("Structure function accuracy comparison")
        self.ax.set_xlabel(self.module.mod_key_display_name.replace("_", " "))
        self.ax.set_ylabel(r"objective function structure")

        self.ax.scatter(
            self.module.mod_value_list,
            self.module.structure_comparison,
            label="struc_comparison " + self.module.label,
        )


class BootZCurveFigure(StructureFigure):
    def make_figure(self):
        self.ax.set_title("Bootstrapped thermal impedance")
        self.ax.set_ylabel(r"$Z_{\rm th}$ / K$\cdot$ W$^{-1}$")
        self.ax.set_xlabel(r"time, $t$, in s")

        self.ax.semilogx(
            np.exp(self.module.boot_imp_time),
            self.module.boot_imp_av,
            linewidth=1.5,
            markersize=0.0,
            label="median impedance" + self.module.label,
            color=self.next_color(),
        )
        self.ax.fill_between(
            np.exp(self.module.boot_imp_time),
            self.module.boot_imp_perc_u,
            self.module.boot_imp_perc_l,
            alpha=0.5,
            label="confidence interval" + self.module.label,
            color=self.same_color(),
        )


class BootDerivFigure(StructureFigure):
    def make_figure(self):
        self.ax.set_title("Bootstrapped impulse response")
        self.ax.set_xlabel(r"time, $t$, in s")
        self.ax.set_ylabel(r"impulse response, $h$, in K$\cdot$ W$^{-1}$")

        self.ax.semilogx(
            np.exp(self.module.boot_deriv_time),
            self.module.boot_deriv_av,
            linewidth=1.5,
            markersize=0.0,
            label="median derivative" + self.module.label,
            color=self.next_color(),
        )
        self.ax.fill_between(
            np.exp(self.module.boot_deriv_time),
            self.module.boot_deriv_perc_u,
            self.module.boot_deriv_perc_l,
            alpha=0.5,
            label="confidence intervall" + self.module.label,
            color=self.same_color(),
        )


class BootTimeSpecFigure(StructureFigure):
    def make_figure(self):
        self.ax.set_title("Bootstrapped time constant spectrum")
        self.ax.set_xlabel(r"time constant, $\tau$, in s")
        self.ax.set_ylabel(r"resistance, $R'$, in K$\cdot$ W$^{-1}$")

        self.ax.semilogx(
            np.exp(self.module.boot_deriv_time),
            self.module.boot_time_spec_av,
            linewidth=1.5,
            markersize=0.0,
            label="median spectrum" + self.module.label,
            color=self.next_color(),
        )
        self.ax.fill_between(
            np.exp(self.module.boot_deriv_time),
            self.module.boot_time_spec_perc_u,
            self.module.boot_time_spec_perc_l,
            alpha=0.5,
            label="confidence intervall" + self.module.label,
            color=self.same_color(),
        )


class BootSumTimeSpecFigure(StructureFigure):
    def make_figure(self):
        self.ax.set_title("Bootstrapped cumulative time constant spectrum")
        self.ax.set_xlabel(r"time constant, $\tau$, in s")
        self.ax.set_ylabel(r"cumulative resistance, $R'_\Sigma$, in K$\cdot$ W$^{-1}$")

        self.ax.semilogx(
            np.exp(self.module.boot_deriv_time),
            self.module.boot_sum_time_spec_av,
            linewidth=1.5,
            markersize=0.0,
            label="median sum spectrum" + self.module.label,
            color=self.next_color(),
        )
        self.ax.fill_between(
            np.exp(self.module.boot_deriv_time),
            self.module.boot_sum_time_spec_perc_u,
            self.module.boot_sum_time_spec_perc_l,
            alpha=0.5,
            label="confidence interval" + self.module.label,
            color=self.same_color(),
        )


class BootCumulStrucFigure(StructureFigure):
    def make_figure(self):
        self.ax.set_title("Bootstrapped cumulative structure function")
        self.ax.set_xlabel(
            r"cumulative thermal resistance, $R_\Sigma$, in K$\cdot$ W$^{-1}$"
        )
        self.ax.set_ylabel(
            r"cumulative thermal capacity, $C_\Sigma$, in J$\cdot$ K$^{-1}$"
        )

        self.ax.semilogy(
            self.module.boot_struc_res_fine,
            self.module.boot_struc_cap_av,
            linewidth=1.5,
            markersize=0.0,
            label="median structure" + self.module.label,
            color=self.next_color(),
        )
        self.ax.fill_between(
            self.module.boot_struc_res_fine,
            self.module.boot_struc_cap_perc_u,
            self.module.boot_struc_cap_perc_l,
            alpha=0.5,
            label="confidence interval" + self.module.label,
            color=self.same_color(),
        )


class ResidualFigure(StructureFigure):
    def make_figure(self):
        self.ax.set_title("Residuals")
        self.ax.set_ylabel(r"residuals")
        self.ax.set_xlabel(r"count")

        self.ax.scatter(self.module.bins, self.module.hist, label="bins")
        self.ax.plot(
            self.module.bins,
            self.module.gaus_curve,
            linewidth=1.5,
            markersize=0.0,
            label="gaussian fit",
            color="blue",
        )


class PredictionFigure(StructureFigure):
    def make_figure(self):
        self.ax.set_title("Predicted temperature")
        self.ax.set_xlabel(r"time, $t$, in s")
        self.ax.set_ylabel(r"temperature, $T$, in $^\circ\!$C")

        # Plot temperature on primary y-axis
        self.ax.plot(
            self.module.lin_time,
            self.module.predicted_temperature,
            linewidth=1.5,
            markersize=0.0,
            label="predicted temperature",
            color="blue",
        )

        # Create secondary y-axis
        self.ax2 = self.ax.twinx()
        self.ax2.set_ylabel(r"power, $P$, in W")

        # Plot power function on secondary y-axis
        self.ax2.plot(
            self.module.lin_time,
            self.module.power_function_int,
            linewidth=1.0,
            marker="o",
            markersize=1.0,
            label="power function",
            color="red",
        )


class PredictionImpulseUsedFigure(StructureFigure):
    def make_figure(self):
        self.ax.set_title("Prediction Impulse Response Used")
        self.ax.set_xlabel(r"time, $t$, in s")
        self.ax.set_ylabel(r"thermal impedance, $Z_{\rm th}$, in K$\cdot$ W$^{-1}$")

        self.ax.plot(
            self.module.reference_time,
            self.module.reference_impulse_response,
            linewidth=1.5,
            label="linear time derivative" + self.module.label,
            markersize=1.5,
        )
