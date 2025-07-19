import numpy as np
import numpy.polynomial.polynomial as poly
import scipy.integrate as sin
from matplotlib.lines import Line2D

from .transient_base_fig import StructureFigure


class VoltageFigure(StructureFigure):
    def plot_module_data(self, module):
        if not self._axis_initialized:
            self.ax.set_title("Voltage response")
            self.ax.set_xlabel(r"time, $t$, in s")
            self.ax.set_ylabel(r"voltage, $U$, in V")
            self._axis_initialized = True

        self.ax.semilogx(
            module.time_raw,
            module.voltage,
            label=module.label,
            linewidth=0.0,
            markersize=1.5,
            marker="o",
            color=self.next_color(),
        )


class RawDataFigure(StructureFigure):
    def plot_module_data(self, module):
        if not self._axis_initialized:
            self.ax.set_title("Raw Temperature Response")
            self.ax.set_xlabel(r"time, $t$, in s")
            self.ax.set_ylabel(r"temperature, $T$, in $^\circ\!$C")
            self._axis_initialized = True

        self.ax.semilogx(module.time_raw, module.temp_raw, "x", label="raw data")


class ExtrapolationFigure(StructureFigure):
    def plot_module_data(self, module):
        self.ax.set_title("Square root extrapolation")
        self.ax.set_xlabel(r"square root of time, $\sqrt{s}$, in s$^{1/2}$")
        self.ax.set_ylabel(r"temperature, $T$, in $^\circ\!$C")

        self.ax.plot(
            np.sqrt(module.time),
            module.temperature,
            label="temp." + module.label,
            markersize=2.5,
            marker="o",
        )
        self.ax.plot(np.sqrt(module.time_raw), module.temp_raw, label="temp_raw")
        self.ax.plot(
            np.sqrt(module.time_raw[module.lower_fit_index : module.upper_fit_index]),
            module.temp_raw[module.lower_fit_index : module.upper_fit_index],
            markersize=1.5,
            marker="o",
        )
        self.ax.plot(
            np.sqrt(module.time_raw),
            poly.polyval(np.sqrt(module.time_raw), module.expl_ft_prm),
        )

        self.ax.set_xlim(
            0,
            np.sqrt(module.time_raw[module.upper_fit_index] * 2.5),
        )
        self.ax.set_ylim(
            module.temp_raw[module.lower_fit_index] * 0.75,
            module.temp_raw[module.upper_fit_index] * 1.25,
        )


class TempFigure(StructureFigure):
    def plot_module_data(self, module):
        if not self._axis_initialized:
            self.ax.set_title("Cleaned Temperature Response")
            self.ax.set_xlabel(r"time, $t$, in s")
            self.ax.set_ylabel(r"temperature, $T$, in $^\circ\!$C")
            self._axis_initialized = True

        self.ax.semilogx(
            module.time,
            module.temperature,
            label=module.label,
            linewidth=0.0,
            markersize=1.5,
            marker="o",
            color=self.next_color(),
        )


class ZCurveFigure(StructureFigure):
    def plot_module_data(self, module):
        if not self._axis_initialized:
            self.ax.set_title("Thermal impedance")
            self.ax.set_xlabel(r"time, $t$, in s")
            self.ax.set_ylabel(r"thermal impedance, $Z_{\rm th}$, in K$\cdot$ W$^{-1}$")
            self._axis_initialized = True

        self.ax.semilogx(
            np.exp(module.log_time),
            module.impedance,
            linewidth=0.0,
            marker="o",
            markersize=1.5,
            label="imp." + module.label,
            color=self.next_color(),
        )
        self.ax.semilogx(
            np.exp(module.log_time_interp),
            module.imp_smooth,
            linewidth=1.5,
            markersize=0.0,
            label="loc. av." + module.label,
            color=self.same_color(),
        )


class DerivFigure(StructureFigure):
    def plot_module_data(self, module):
        if not self._axis_initialized:
            self.ax.set_title("Impulse response")
            self.ax.set_xlabel(r"time, $t$, in s")
            self.ax.set_ylabel(r"impulse response, $h$, in K$\cdot$ W$^{-1}$")
            self._axis_initialized = True

        self.ax.semilogx(
            np.exp(module.log_time_pad),
            module.imp_deriv_interp,
            marker="o",
            lw=1.5,
            label=module.label,
            markersize=0.0,
            color=self.next_color(),
        )


class FFTFigure(StructureFigure):
    def plot_module_data(self, module):
        if not self._axis_initialized:
            self.ax.set_xlim(0, 7)
            self.ax.set_ylim(1e-6, 1e3)
            self.ax.set_title("Fourier transform")
            self.ax.set_xlabel(r"angular frequency, $\omega$, in rad/s")
            self.ax.set_ylabel(r"power density, $|H|^2$, in (K $\cdot$ s W$^{-1})^2$")
            self._axis_initialized = True

        angular_freq = 2 * np.pi * module.fft_freq
        self.ax.semilogy(
            angular_freq, module.fft_idi_pegrm, "o", markersize=3, label="fft"
        )
        self.ax.semilogy(
            angular_freq,
            module.current_filter,
            "o",
            markersize=3,
            label="cur. filter" + module.label,
        )
        self.ax.semilogy(
            angular_freq,
            module.fft_idi_pegrm * module.current_filter,
            "o",
            markersize=3,
            label="combined" + module.label,
        )


class TimeSpecFigure(StructureFigure):
    def plot_module_data(self, module):
        if not self._axis_initialized:
            self.ax.set_title("Time constant spectrum")
            self.ax.set_xlabel(r"time constant, $\tau$, in s")
            self.ax.set_ylabel(r"resistance, $R'$, in K$\cdot$ W$^{-1}$")
            self._axis_initialized = True

        self.ax.semilogx(
            np.exp(module.crop_log_time),
            module.crop_time_spec,
            label=module.label,
            lw=0.7,
            ms=3.0,
            marker="o",
            color=self.next_color(),
        )
        self.ax.semilogx(
            np.exp(module.crop_log_time),
            module.crop_time_spec,
            lw=0.0,
            ms=2.0,
            marker="o",
            color=self.same_color(),
        )


class SumTimeSpecFigure(StructureFigure):
    def plot_module_data(self, module):
        if not self._axis_initialized:
            self.ax.set_title("Cumulative time constant spectrum")
            self.ax.set_xlabel(r"time constant, $\tau$, in s")
            self.ax.set_ylabel(
                r"cumulative resistance, $R'_\Sigma$, in K$\cdot$ W$^{-1}$"
            )
            self._axis_initialized = True

        self.ax.semilogx(
            np.exp(module.log_time_pad),
            module.sum_time_spec,
            label="spect." + module.label,
            lw=1.0,
            ms=1.5,
            color=self.next_color(),
        )


class CumulStrucFigure(StructureFigure):
    def plot_module_data(self, module):
        if not self._axis_initialized:
            self.ax.set_ylim(1e-6, 1e5)
            self.ax.set_title("Cumulative structure function")
            self.ax.set_xlabel(
                r"cumulative thermal resistance, $R_\Sigma$, in K$\cdot$ W$^{-1}$"
            )
            self.ax.set_ylabel(
                r"cumulative thermal capacity, $C_\Sigma$, in J$\cdot$ K$^{-1}$"
            )
            self._axis_initialized = True

        sliced = np.where(module.int_cau_cap <= 1e4)

        self.int_cau_res = module.int_cau_res[sliced]
        self.int_cau_cap = module.int_cau_cap[sliced]

        self.ax.semilogy(
            self.int_cau_res,
            self.int_cau_cap,
            color=self.next_color(),
            label="struc." + module.label,
            linewidth=1.0,
            markersize=1.5,
            marker="o",
        )


class DiffStrucFigure(StructureFigure):
    def plot_module_data(self, module):
        if not self._axis_initialized:
            self.ax.set_ylim(1e-5, 1e5)
            self.ax.set_title("Differential structure function")
            self.ax.set_xlabel(r"thermal resistance, $R$, in K$\cdot$ W$^{-1}$")
            self.ax.set_ylabel(
                r"thermal capacity, $C$, in s$\cdot$ W$^2$ $\cdot$ K$^{-2}$"
            )
            self._axis_initialized = True

        self.int_cau_res = module.int_cau_res[:-1]
        self.diff_struc = module.diff_struc

        self.ax.semilogy(
            self.int_cau_res,
            self.diff_struc,
            color=self.next_color(),
            label="dif. struc." + module.label,
            marker="o",
            markersize=2,
            linewidth=1.0,
        )


class LocalResistFigure(StructureFigure):
    def plot_module_data(self, module):
        if not self._axis_initialized:
            self.ax.set_title("Local thermal resistance")
            self.ax.set_xlabel(r"thermal resistance, $R$, in K$\cdot$ W$^{-1}$")
            self.ax.set_ylabel(
                r"local thermal resistance, $R_{\rm loc}$, in K$\cdot$ W$^{-1}$"
            )
            self._axis_initialized = True

        self.ax.semilogx(
            (module.int_cau_cap),
            module.cau_res,
            color=self.next_color(),
            label="local_res." + module.label,
            marker="o",
            markersize=2,
            linewidth=1.0,
        )


class LocalGradientFigure(StructureFigure):
    def plot_module_data(self, module):
        if not self._axis_initialized:
            self.ax.set_xlim(1e-5, 1e2)

            self.ax.set_title("Local gradient diagram")
            self.ax.set_ylabel(
                r"thermal gradient, $R/C$, in K$^2$ $\cdot$ (s$\cdot$ W$^2$)$^{-1}$"
            )
            self.ax.set_xlabel(
                r"cumulative thermal capacity, $C_\Sigma$, in J$\cdot$ K$^{-1}$"
            )
            self._axis_initialized = True

        self.ax.semilogx(
            module.int_cau_cap,
            module.cau_res / module.cau_cap,
            color=self.next_color(),
            label="local_grad." + module.label,
            marker="o",
            markersize=2,
            linewidth=1.0,
        )


class TheoCStrucFigure(StructureFigure):
    def plot_module_data(self, module):
        if not self._axis_initialized:
            self.ax.set_title("Theoretical cumulative structure function")
            self.ax.set_xlabel(
                r"cumulative thermal resistance, $R_\Sigma$, in K$\cdot$ W$^{-1}$"
            )
            self.ax.set_ylabel(
                r"cumulative thermal capacity, $C_\Sigma$, in J$\cdot$ K$^{-1}$"
            )
            self._axis_initialized = True

        self.ax.semilogy(
            module.theo_int_cau_res,
            module.theo_int_cau_cap,
            color=self.next_color(),
            label="opt. struc." + module.label,
            linewidth=3.0,
        )


class TheoDiffStrucFigure(StructureFigure):
    def plot_module_data(self, module):
        if not self._axis_initialized:
            self.ax.set_title(r"Theoretical differential structure function")
            self.ax.set_xlabel(r"thermal resistance, $R$, in K$\cdot$ W$^{-1}$")
            self.ax.set_ylabel(
                r"thermal capacity, $C$, in s$\cdot$ W$^2$ $\cdot$ K$^{-2}$"
            )
            self._axis_initialized = True

        self.ax.semilogy(
            module.theo_int_cau_res[:-1],
            module.theo_diff_struc,
            color=self.next_color(),
            label="theo diff struc." + module.label,
            marker="o",
            markersize=3,
            linewidth=1.0,
        )


class TheoLocalResistFigure(StructureFigure):
    def plot_module_data(self, module):
        if not self._axis_initialized:
            self.ax.set_title("Theoretical local thermal resistance")
            self.ax.set_xlabel(
                r"cumulative thermal capacity, $C_\Sigma$, in J$\cdot$ K$^{-1}$"
            )
            self.ax.set_ylabel(r"thermal resistance, $R$, in K$\cdot$ W$^{-1}$")
            self._axis_initialized = True

        self.ax.semilogy(
            module.theo_int_cau_res,
            module.theo_int_cau_cap,
            label="opt. struc.",
            linewidth=3.0,
        )


class TheoTimeConstFigure(StructureFigure):
    def plot_module_data(self, module):
        if not self._axis_initialized:
            self.ax.set_title("Theoretical time constant spectrum")
            self.ax.set_xlabel(r"time constant, $\tau$, in s")
            self.ax.set_ylabel(r"resistance, $R'$, in K$\cdot$ W$^{-1}$")
            self._axis_initialized = True

        self.ax.semilogx(
            np.exp(module.theo_log_time),
            module.theo_time_const,
            marker="o",
            color=self.next_color(),
            label="opt. spect." + module.label,
            linewidth=1.0,
            markersize=1.5,
        )


class TheoSumTimeConstFigure(StructureFigure):
    def plot_module_data(self, module):
        if not self._axis_initialized:
            self.ax.set_title("Theoretical cumulative time constant spectrum")
            self.ax.set_xlabel(r"time constant, $\tau$, in s")
            self.ax.set_ylabel(
                r"cumulative resistance, $R'_\Sigma$, in K$\cdot$ W$^{-1}$"
            )
            self._axis_initialized = True

        sum_theo_time_spec = sin.cumulative_trapezoid(
            module.theo_time_const, x=module.theo_log_time, initial=0.0
        )

        self.ax.semilogx(
            np.exp(module.theo_log_time),
            sum_theo_time_spec,
            marker="o",
            color=self.next_color(),
            label="theo. int. spec. " + module.label,
            linewidth=1.0,
            markersize=1.5,
        )


class TheoImpDerivFigure(StructureFigure):
    def plot_module_data(self, module):
        if not self._axis_initialized:
            self.ax.set_title("Theoretical impulse response")
            self.ax.set_xlabel(r"time, $t$, in s")
            self.ax.set_ylabel(r"impulse response, $h$, in K$\cdot$ W$^{-1}$")
            self._axis_initialized = True

        self.ax.semilogx(
            np.exp(module.theo_log_time),
            module.theo_imp_deriv,
            linewidth=1.5,
            color=self.next_color(),
            label="theo. deriv. " + module.label,
            markersize=1.5,
        )


class TheoImpFigure(StructureFigure):
    def plot_module_data(self, module):
        if not self._axis_initialized:
            self.ax.set_title("Theoretical thermal impedance")
            self.ax.set_xlabel(r"time, $t$, in s")
            self.ax.set_ylabel(r"thermal impedance, $Z_{\rm th}$, in K$\cdot$ W$^{-1}$")
            self._axis_initialized = True

        self.ax.semilogx(
            np.exp(module.theo_log_time),
            module.theo_impedance,
            linewidth=1.5,
            label="theo. imp. " + module.label,
            color=self.next_color(),
        )


class BackwardsImpDerivFigure(StructureFigure):
    def plot_module_data(self, module):
        if not self._axis_initialized:
            self.ax.set_title("Backwards impulse response")
            self.ax.set_xlabel(r"time, $t$, in s")
            self.ax.set_ylabel(r"impulse response, $h$, in K$\cdot$ W$^{-1}$")
            self._axis_initialized = True

        self.ax.semilogx(
            np.exp(module.log_time_pad),
            module.imp_deriv_interp,
            linewidth=1.5,
            label="orig. deriv. " + module.label,
            markersize=1.5,
            color=self.next_color(),
        )
        self.ax.semilogx(
            np.exp(module.log_time_pad),
            module.back_imp_deriv,
            linewidth=0.0,
            marker="o",
            label="backwards deriv. " + module.label,
            markersize=1.5,
            color=self.same_color(),
        )


class BackwardsImpFigure(StructureFigure):
    def plot_module_data(self, module):
        if not self._axis_initialized:
            self.ax.set_title("Backwards thermal impedance")
            self.ax.set_xlabel(r"time, $t$, in s")
            self.ax.set_ylabel(r"thermal impedance, $Z_{\rm th}$, in K$\cdot$ W$^{-1}$")
            self._axis_initialized = True

        self.ax.semilogx(
            np.exp(module.log_time),
            module.impedance,
            linewidth=0.0,
            marker="o",
            markersize=1.0,
            label="orig. imp. " + module.label,
        )
        self.ax.semilogx(
            np.exp(module.log_time_pad),
            module.back_imp,
            linewidth=0.0,
            marker="x",
            markersize=2.0,
            label="backwards imp. " + module.label,
            color=self.next_color(),
        )
        self.ax.semilogx(
            np.exp(module.log_time_interp),
            module.imp_smooth,
            linewidth=1.5,
            markersize=0.0,
            label="loc. av." + module.label,
            color=self.same_color(),
        )


class TheoBackwardsImpFigure(StructureFigure):
    def plot_module_data(self, module):
        if not self._axis_initialized:
            self.ax.set_title("Theoretical backwards thermal impedance")
            self.ax.set_xlabel(r"time, $t$, in s")
            self.ax.set_ylabel(r"thermal impedance, $Z_{\rm th}$, in K$\cdot$ W$^{-1}$")
            self._axis_initialized = True

        self.ax.semilogx(
            np.exp(module.log_time_pad),
            module.back_imp,
            linewidth=3,
            marker="o",
            markersize=0.0,
            label="Bay. imp." + module.label,
            zorder=5,
        )
        self.ax.semilogx(
            np.exp(module.theo_log_time),
            module.theo_impedance,
            linewidth=3,
            marker="o",
            markersize=0.0,
            label="opt. imp." + module.label,
            zorder=10,
        )
        self.ax.semilogx(
            np.exp(module.opt_log_time),
            module.opt_imp,
            linewidth=0.0,
            marker="o",
            markersize=6,
            label="meas. imp." + module.label,
            zorder=0,
            fillstyle="none",
        )


class OptimizeStrucFigure(StructureFigure):
    def plot_module_data(self, module):
        if not self._axis_initialized:
            self.ax.set_title("Optimized structure function")
            self.ax.set_xlabel(r"cumulative thermal resistance / K$\cdot$ W$^{-1}$")
            self.ax.set_ylabel(r"cumulative thermal capacity / J$\cdot$ K$^{-1}$")
            self._axis_initialized = True

        self.ax.semilogy(
            module.int_cau_res,
            module.int_cau_cap,
            label="struc." + module.label,
            linewidth=1.0,
            markersize=1.5,
        )

        self.ax.semilogy(
            module.init_opt_imp_res,
            module.init_opt_imp_cap,
            lw=0.0,
            ms=3,
            marker="o",
            label="init_opt_imp_cap" + module.label,
        )

        if module.struc_init_method == "optimal_fit":
            self.ax.semilogy(
                module.init_opt_struc_res,
                module.init_opt_struc_cap,
                lw=0.0,
                ms=3,
                marker="o",
                label="init_opt_struc_cap" + module.label,
            )

        self.ax.semilogy(
            module.fin_res,
            module.fin_cap,
            lw=0.0,
            ms=3,
            marker="o",
            label="opt_cap" + module.label,
        )


class TimeConstComparisonFigure(StructureFigure):
    def plot_module_data(self, module):
        if not self._axis_initialized:
            self.ax.set_title("Time constant accuracy comparison")
            self.ax.set_xlabel(module.mod_key_display_name.replace("_", " "))
            self.ax.set_ylabel(r"objective function time const")
            self._axis_initialized = True

        self.ax.scatter(
            module.mod_value_list,
            module.time_const_comparison,
            label="time_const_comp." + module.label,
        )


class TotalResistComparisonFigure(StructureFigure):
    def plot_module_data(self, module):
        if not self._axis_initialized:
            self.ax.set_title("Total resistance accuracy comparison")
            self.ax.set_xlabel(module.mod_key_display_name.replace("_", " "))
            self.ax.set_ylabel(r"total resistance difference")
            self._axis_initialized = True

        self.ax.scatter(
            module.mod_value_list,
            module.total_resist_diff,
            label="resist_comp." + module.label,
        )


class StrucComparisonFigure(StructureFigure):
    def plot_module_data(self, module):
        if not self._axis_initialized:
            self.ax.set_title("Structure function accuracy comparison")
            self.ax.set_xlabel(module.mod_key_display_name.replace("_", " "))
            self.ax.set_ylabel(r"objective function structure")

            self._axis_initialized = True

        self.ax.scatter(
            module.mod_value_list,
            module.structure_comparison,
            label="struc_comp." + module.label,
        )


class BootZCurveFigure(StructureFigure):
    def plot_module_data(self, module):
        if not self._axis_initialized:
            self.ax.set_title("Bootstrapped thermal impedance")
            self.ax.set_ylabel(r"$Z_{\rm th}$ / K$\cdot$ W$^{-1}$")
            self.ax.set_xlabel(r"time, $t$, in s")
            self._axis_initialized = True

        self.ax.semilogx(
            np.exp(module.boot_imp_time),
            module.boot_imp_av,
            linewidth=1.5,
            markersize=0.0,
            label="median imp." + module.label,
            color=self.next_color(),
        )
        self.ax.fill_between(
            np.exp(module.boot_imp_time),
            module.boot_imp_perc_u,
            module.boot_imp_perc_l,
            alpha=0.5,
            label="confidence interval" + module.label,
            color=self.same_color(),
        )


class BootDerivFigure(StructureFigure):
    def plot_module_data(self, module):
        if not self._axis_initialized:
            self.ax.set_title("Bootstrapped impulse response")
            self.ax.set_xlabel(r"time, $t$, in s")
            self.ax.set_ylabel(r"impulse response, $h$, in K$\cdot$ W$^{-1}$")
            self._axis_initialized = True

        self.ax.semilogx(
            np.exp(module.boot_deriv_time),
            module.boot_deriv_av,
            linewidth=1.5,
            markersize=0.0,
            label="median deriv." + module.label,
            color=self.next_color(),
        )
        self.ax.fill_between(
            np.exp(module.boot_deriv_time),
            module.boot_deriv_perc_u,
            module.boot_deriv_perc_l,
            alpha=0.5,
            label="confidence interval" + module.label,
            color=self.same_color(),
        )


class BootTimeSpecFigure(StructureFigure):
    def plot_module_data(self, module):
        if not self._axis_initialized:
            self.ax.set_title("Bootstrapped time constant spectrum")
            self.ax.set_xlabel(r"time constant, $\tau$, in s")
            self.ax.set_ylabel(r"resistance, $R'$, in K$\cdot$ W$^{-1}$")
            self._axis_initialized = True

        self.ax.semilogx(
            np.exp(module.boot_deriv_time),
            module.boot_time_spec_av,
            linewidth=1.5,
            markersize=0.0,
            label="median spect." + module.label,
            color=self.next_color(),
        )
        self.ax.fill_between(
            np.exp(module.boot_deriv_time),
            module.boot_time_spec_perc_u,
            module.boot_time_spec_perc_l,
            alpha=0.5,
            label="confidence interval" + module.label,
            color=self.same_color(),
        )


class BootSumTimeSpecFigure(StructureFigure):
    def plot_module_data(self, module):
        if not self._axis_initialized:
            self.ax.set_title("Bootstrapped cumulative time constant spectrum")
            self.ax.set_xlabel(r"time constant, $\tau$, in s")
            self.ax.set_ylabel(
                r"cumulative resistance, $R'_\Sigma$, in K$\cdot$ W$^{-1}$"
            )
            self._axis_initialized = True

        self.ax.semilogx(
            np.exp(module.boot_deriv_time),
            module.boot_sum_time_spec_av,
            linewidth=1.5,
            markersize=0.0,
            label="median sum. spect." + module.label,
            color=self.next_color(),
        )
        self.ax.fill_between(
            np.exp(module.boot_deriv_time),
            module.boot_sum_time_spec_perc_u,
            module.boot_sum_time_spec_perc_l,
            alpha=0.5,
            label="confidence interval" + module.label,
            color=self.same_color(),
        )


class BootCumulStrucFigure(StructureFigure):
    def plot_module_data(self, module):
        if not self._axis_initialized:
            self.ax.set_title("Bootstrapped cumulative structure function")
            self.ax.set_xlabel(
                r"cumulative thermal resistance, $R_\Sigma$, in K$\cdot$ W$^{-1}$"
            )
            self.ax.set_ylabel(
                r"cumulative thermal capacity, $C_\Sigma$, in J$\cdot$ K$^{-1}$"
            )
            self._axis_initialized = True

        self.ax.semilogy(
            module.boot_struc_res_fine,
            module.boot_struc_cap_av,
            linewidth=1.5,
            markersize=0.0,
            label="median structure" + module.label,
            color=self.next_color(),
        )
        self.ax.fill_between(
            module.boot_struc_res_fine,
            module.boot_struc_cap_perc_u,
            module.boot_struc_cap_perc_l,
            alpha=0.5,
            label="confidence interval" + module.label,
            color=self.same_color(),
        )


class ResidualFigure(StructureFigure):
    def plot_module_data(self, module):
        if not self._axis_initialized:
            self.ax.set_title("Residuals")
            self.ax.set_ylabel(r"residuals")
            self.ax.set_xlabel(r"count")
            self._axis_initialized = True

        self.ax.scatter(module.bins, module.hist, label="bins")
        self.ax.plot(
            module.bins,
            module.gauss_curve,
            linewidth=1.5,
            markersize=0.0,
            label="Gaussian fit" + module.label,
            color="blue",
        )


class PredictionFigure(StructureFigure):
    def plot_module_data(self, module):
        if not self._axis_initialized:
            self.ax.set_title("Predicted temperature")
            self.ax.set_xlabel(r"time, $t$, in s")
            self.ax.set_ylabel(r"temperature, $T$, in $^\circ\!$C")
            self._axis_initialized = True

        # Plot temperature on primary y-axis
        self.ax.plot(
            module.lin_time,
            module.predicted_temperature,
            linewidth=1.5,
            markersize=0.0,
            label="pred. temp." + module.label,
            color="blue",
        )

        # Create secondary y-axis
        self.ax2 = self.ax.twinx()
        self.ax2.set_ylabel(r"power, $P$, in W")

        # Plot power function on secondary y-axis
        self.ax2.plot(
            module.lin_time,
            module.power_function_int,
            linewidth=1.0,
            marker="o",
            markersize=1.0,
            label="power" + module.label,
            color="red",
        )


class PredictionImpulseUsedFigure(StructureFigure):
    def plot_module_data(self, module):
        if not self._axis_initialized:
            self.ax.set_title("Prediction Impulse Response Used")
            self.ax.set_xlabel(r"time, $t$, in s")
            self.ax.set_ylabel(r"thermal impedance, $Z_{\rm th}$, in K$\cdot$ W$^{-1}$")
            self._axis_initialized = True

        self.ax.plot(
            module.reference_time,
            module.reference_impulse_response,
            linewidth=1.5,
            label="lin. impulse resp." + module.label,
            markersize=1.5,
        )
