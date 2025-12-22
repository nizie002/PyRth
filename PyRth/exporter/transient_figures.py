"""Concrete StructureFigure subclasses used by the exporter handlers.

Each class encapsulates one plot type (voltage, impedance, structure
functions, bootstrap summaries, etc.) and is responsible for inserting the
module-specific data into shared Matplotlib axes created by
``StructureFigure``.  The exporter layer instantiates only the figures it
needs per evaluation run, so keeping this file declarative—one class per
plot—keeps the IO workflow predictable and makes it easy to extend with new
visualizations.
"""

import numpy as np
import numpy.polynomial.polynomial as poly
import scipy.integrate as sin
import scipy.interpolate as interp

from .transient_base_fig import StructureFigure
from . import figure_comments


class VoltageFigure(StructureFigure):
    def setup_axes(self):
        self.init_axes("Voltage response", r"time, $t$, in s", r"voltage, $U$, in V")

    def plot_module_data(self, module):
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
    def setup_axes(self):
        self.init_axes(
            "Raw Temperature Response", r"time, $t$, in s", r"temperature, $T$, in $^\circ\!$C"
        )

    def plot_module_data(self, module):
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
    def setup_axes(self):
        self.init_axes(
            "Cleaned Temperature Response", r"time, $t$, in s", r"temperature, $T$, in $^\circ\!$C"
        )

    def plot_module_data(self, module):
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
    def setup_axes(self):
        self.init_axes(
            "Thermal impedance",
            r"time, $t$, in s",
            r"thermal impedance, $Z_{\rm th}$, in K$\cdot$ W$^{-1}$",
        )

    def plot_module_data(self, module):
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

    def build_comment(self, module, plot_key: str | None = None) -> str:
        return figure_comments.format_normalization_comment(module)


class DerivFigure(StructureFigure):
    def setup_axes(self):
        self.init_axes(
            "Impulse response",
            r"time, $t$, in s",
            r"impulse response, $h$, in K$\cdot$ W$^{-1}$",
        )

    def plot_module_data(self, module):
        self.ax.semilogx(
            np.exp(module.log_time_pad),
            module.imp_deriv_interp,
            marker="o",
            lw=1.5,
            label=module.label,
            markersize=0.0,
            color=self.next_color(),
        )

    def build_comment(self, module, plot_key: str | None = None) -> str:
        return figure_comments.format_normalization_comment(module)


class BzFigure(StructureFigure):
    def setup_axes(self):
        self.init_axes(
            r"$B(z) = \log(h(z))$, log-derivative curve",
            r"time, $t$, in s",
            r"logarithmic derivative, $B(z)$",
        )

    def plot_module_data(self, module):
        bz_values = np.asarray(module.bz_curve if module.bz_curve is not None else [])
        log_time = np.asarray(
            module.log_time_pad if module.log_time_pad is not None else []
        )

        if bz_values.size == 0 or log_time.size == 0:
            return

        min_len = min(bz_values.size, log_time.size)
        bz_values = bz_values[:min_len]
        log_time = log_time[:min_len]

        mask = np.isfinite(bz_values)
        if not np.any(mask):
            return

        self.ax.semilogx(
            np.exp(log_time[mask]),
            bz_values[mask],
            marker="o",
            lw=1.5,
            label="B(z) " + module.label,
            markersize=0.0,
            color=self.next_color(),
        )

    def build_comment(self, module, plot_key: str | None = None) -> str:
        return figure_comments.format_normalization_comment(module)


class FFTFigure(StructureFigure):
    def setup_axes(self):
        self.ax.set_xlim(0, 7)
        self.ax.set_ylim(1e-6, 1e3)
        self.init_axes(
            "Fourier transform",
            r"angular frequency, $\omega$, in rad/s",
            r"power density, $|H|^2$, in (K $\cdot$ s W$^{-1})^2$",
        )

    def plot_module_data(self, module):
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
    def setup_axes(self):
        self.init_axes(
            "Time constant spectrum",
            r"time constant, $\tau$, in s",
            r"resistance, $R'$, in K$\cdot$ W$^{-1}$",
        )

    def plot_module_data(self, module):
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

    def build_comment(self, module, plot_key: str | None = None) -> str:
        return f"Deconvolution mode: {getattr(module, 'deconv_mode', 'unknown')}"


class SumTimeSpecFigure(StructureFigure):
    def setup_axes(self):
        self.init_axes(
            "Cumulative time constant spectrum",
            r"time constant, $\tau$, in s",
            r"cumulative resistance, $R'_\Sigma$, in K$\cdot$ W$^{-1}$",
        )

    def plot_module_data(self, module):
        self.ax.semilogx(
            np.exp(module.log_time_pad),
            module.sum_time_spec,
            label="spect." + module.label,
            lw=1.0,
            ms=1.5,
            color=self.next_color(),
        )


class CumulStrucFigure(StructureFigure):
    def setup_axes(self):
        self.ax.set_ylim(1e-6, 1e5)
        self.init_axes(
            "Cumulative structure function",
            r"cumulative thermal resistance, $R_\Sigma$, in K$\cdot$ W$^{-1}$",
            r"cumulative thermal capacity, $C_\Sigma$, in J$\cdot$ K$^{-1}$",
        )

    def plot_module_data(self, module):
        sliced = np.where(module.int_cau_cap <= 1e4)

        int_cau_res_sliced = module.int_cau_res[sliced]
        int_cau_cap_sliced = module.int_cau_cap[sliced]

        self.ax.semilogy(
            int_cau_res_sliced,
            int_cau_cap_sliced,
            color=self.next_color(),
            label="struc." + module.label,
            linewidth=1.0,
            markersize=1.5,
            marker="o",
        )


class DiffStrucFigure(StructureFigure):
    def setup_axes(self):
        self.ax.set_ylim(1e-5, 1e5)
        self.init_axes(
            "Differential structure function",
            r"thermal resistance, $R$, in K$\cdot$ W$^{-1}$",
            r"thermal capacity, $C$, in s$\cdot$ W$^2$ $\cdot$ K$^{-2}$",
        )

    def plot_module_data(self, module):
        int_cau_res_sliced = module.int_cau_res[:-1]

        self.ax.semilogy(
            int_cau_res_sliced,
            module.diff_struc,
            color=self.next_color(),
            label="dif. struc." + module.label,
            marker="o",
            markersize=2,
            linewidth=1.0,
        )


class LocalResistFigure(StructureFigure):
    def setup_axes(self):
        self.init_axes(
            "Local thermal resistance",
            r"thermal resistance, $R$, in K$\cdot$ W$^{-1}$",
            r"local thermal resistance, $R_{\rm loc}$, in K$\cdot$ W$^{-1}$",
        )

    def plot_module_data(self, module):
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
    def setup_axes(self):
        self.ax.set_xlim(1e-5, 1e2)
        self.init_axes(
            "Local gradient diagram",
            r"cumulative thermal capacity, $C_\Sigma$, in J$\cdot$ K$^{-1}$",
            r"thermal gradient, $R/C$, in K$^2$ $\cdot$ (s$\cdot$ W$^2$)$^{-1}$",
        )

    def plot_module_data(self, module):
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
    def setup_axes(self):
        self.init_axes(
            "Theoretical cumulative structure function",
            r"cumulative thermal resistance, $R_\Sigma$, in K$\cdot$ W$^{-1}$",
            r"cumulative thermal capacity, $C_\Sigma$, in J$\cdot$ K$^{-1}$",
        )

    def plot_module_data(self, module):
        self.ax.semilogy(
            module.theo_int_cau_res,
            module.theo_int_cau_cap,
            color=self.next_color(),
            label="opt. struc." + module.label,
            linewidth=3.0,
        )


class TheoDiffStrucFigure(StructureFigure):
    def setup_axes(self):
        self.init_axes(
            r"Theoretical differential structure function",
            r"thermal resistance, $R$, in K$\cdot$ W$^{-1}$",
            r"thermal capacity, $C$, in s$\cdot$ W$^2$ $\cdot$ K$^{-2}$",
        )

    def plot_module_data(self, module):
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
    def setup_axes(self):
        self.init_axes(
            "Theoretical local thermal resistance",
            r"cumulative thermal capacity, $C_\Sigma$, in J$\cdot$ K$^{-1}$",
            r"thermal resistance, $R$, in K$\cdot$ W$^{-1}$",
        )

    def plot_module_data(self, module):
        self.ax.semilogy(
            module.theo_int_cau_res,
            module.theo_int_cau_cap,
            label="opt. struc.",
            linewidth=3.0,
        )


class TheoTimeConstFigure(StructureFigure):
    def setup_axes(self):
        self.init_axes(
            "Theoretical time constant spectrum",
            r"time constant, $\tau$, in s",
            r"resistance, $R'$, in K$\cdot$ W$^{-1}$",
        )

    def plot_module_data(self, module):
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
    def setup_axes(self):
        self.init_axes(
            "Theoretical cumulative time constant spectrum",
            r"time constant, $\tau$, in s",
            r"cumulative resistance, $R'_\Sigma$, in K$\cdot$ W$^{-1}$",
        )

    def plot_module_data(self, module):
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
    def setup_axes(self):
        self.init_axes(
            "Theoretical impulse response",
            r"time, $t$, in s",
            r"impulse response, $h$, in K$\cdot$ W$^{-1}$",
        )

    def plot_module_data(self, module):
        self.ax.semilogx(
            np.exp(module.theo_log_time),
            module.theo_imp_deriv,
            linewidth=1.5,
            color=self.next_color(),
            label="theo. deriv. " + module.label,
            markersize=1.5,
        )


class TheoImpFigure(StructureFigure):
    def setup_axes(self):
        self.init_axes(
            "Theoretical thermal impedance",
            r"time, $t$, in s",
            r"thermal impedance, $Z_{\rm th}$, in K$\cdot$ W$^{-1}$",
        )

    def plot_module_data(self, module):
        self.ax.semilogx(
            np.exp(module.theo_log_time),
            module.theo_impedance,
            linewidth=1.5,
            label="theo. imp. " + module.label,
            color=self.next_color(),
        )


class BackwardsImpDerivFigure(StructureFigure):
    def setup_axes(self):
        self.init_axes(
            "Backwards impulse response comparison",
            r"time, $t$, in s",
            r"impulse response, $h$, in K$\cdot$ W$^{-1}$",
        )
        self.ax.set_ylabel(
            r"impulse response, $h$, in K$\cdot$ W$^{-1}$", color="blue"
        )

    def plot_module_data(self, module):
        self.ax.semilogx(
            np.exp(module.log_time_pad),
            module.imp_deriv_interp,
            linewidth=1.0,
            label="orig. deriv. " + module.label,
            markersize=0.0,
            color='blue',
        )
        self.ax.semilogx(
            np.exp(module.log_time_pad),
            module.back_imp_deriv,
            linewidth=0.0,
            marker="o",
            label="backwards deriv. " + module.label,
            markersize=1.5,
            color='lightblue',
        )
        self.ax.tick_params(axis='y', labelcolor='blue')

        ax2 = self.ax.twinx()
        ax2.set_ylabel(r"difference, $\Delta h$, in K$\cdot$ W$^{-1}$", color='red')

        difference = module.back_imp_deriv - module.imp_deriv_interp
        ax2.semilogx(
            np.exp(module.log_time_pad),
            difference,
            linewidth=0.75,
            marker="x",
            label="diff. (back - orig) " + module.label,
            markersize=1.5,
            color='red',
        )
        ax2.tick_params(axis='y', labelcolor='red')

        ax2.axhline(y=0, color='red', linestyle='--', alpha=0.3, linewidth=0.5)


class BackwardsImpFigure(StructureFigure):
    def setup_axes(self):
        self.init_axes(
            "Backwards thermal impedance comparison",
            r"time, $t$, in s",
            r"thermal impedance, $Z_{\rm th}$, in K$\cdot$ W$^{-1}$",
        )
        self.ax.set_ylabel(
            r"thermal impedance, $Z_{\rm th}$, in K$\cdot$ W$^{-1}$", color="blue"
        )

    def plot_module_data(self, module):
        time_orig = np.exp(module.log_time)
        time_pad = np.exp(module.log_time_pad)

        self.ax.semilogx(
            time_orig,
            module.impedance,
            linewidth=0.0,
            marker="o",
            markersize=1.0,
            label="orig. imp. " + module.label,
            color='blue',
        )
        self.ax.semilogx(
            time_pad,
            module.back_imp,
            linewidth=0.0,
            marker="x",
            markersize=2.0,
            label="backwards imp. " + module.label,
            color='lightblue',
        )
        self.ax.tick_params(axis='y', labelcolor='blue')

        ax2 = self.ax.twinx()
        ax2.set_ylabel(r"difference, $\Delta Z_{\rm th}$, in K$\cdot$ W$^{-1}$", color='red')

        overlap_min = max(time_orig.min(), time_pad.min())
        overlap_max = min(time_orig.max(), time_pad.max())

        orig_overlap_mask = (time_orig >= overlap_min) & (time_orig <= overlap_max)
        pad_overlap_mask = (time_pad >= overlap_min) & (time_pad <= overlap_max)

        if (
            overlap_min < overlap_max
            and np.any(orig_overlap_mask)
            and np.any(pad_overlap_mask)
        ):
            impedance_interp = interp.interp1d(
                time_orig[orig_overlap_mask],
                module.impedance[orig_overlap_mask],
                kind="linear",
                bounds_error=False,
                fill_value=np.nan,
            )(time_pad[pad_overlap_mask])

            back_imp_overlap = module.back_imp[pad_overlap_mask]
            difference_overlap = back_imp_overlap - impedance_interp

            ax2.semilogx(
                time_pad[pad_overlap_mask],
                difference_overlap,
                linewidth=0.75,
                marker="s",
                markersize=1.5,
                label="diff. (back - orig) " + module.label,
                color='red',
            )

        ax2.tick_params(axis='y', labelcolor='red')
        ax2.axhline(y=0, color='red', linestyle='--', alpha=0.3, linewidth=0.5)


class TheoBackwardsImpFigure(StructureFigure):
    def setup_axes(self):
        self.init_axes(
            "Theoretical backwards thermal impedance",
            r"time, $t$, in s",
            r"thermal impedance, $Z_{\rm th}$, in K$\cdot$ W$^{-1}$",
        )

    def plot_module_data(self, module):
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
    def setup_axes(self):
        self.init_axes(
            "Optimized structure function",
            r"cumulative thermal resistance / K$\cdot$ W$^{-1}$",
            r"cumulative thermal capacity / J$\cdot$ K$^{-1}$",
        )

    def plot_module_data(self, module):
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
    def setup_axes(self):
        self.init_axes(
            "Time constant accuracy comparison",
            self.module.mod_key_display_name.replace("_", " "),
            r"objective function time const",
        )

    def plot_module_data(self, module):
        self.ax.scatter(
            module.mod_value_list,
            module.time_const_comparison,
            label="time_const_comp." + module.label,
        )


class TotalResistComparisonFigure(StructureFigure):
    def setup_axes(self):
        self.init_axes(
            "Total resistance accuracy comparison",
            self.module.mod_key_display_name.replace("_", " "),
            r"total resistance difference",
        )

    def plot_module_data(self, module):
        self.ax.scatter(
            module.mod_value_list,
            module.total_resist_diff,
            label="resist_comp." + module.label,
        )


class StrucComparisonFigure(StructureFigure):
    def setup_axes(self):
        self.init_axes(
            "Structure function accuracy comparison",
            self.module.mod_key_display_name.replace("_", " "),
            r"objective function structure",
        )

    def plot_module_data(self, module):
        self.ax.scatter(
            module.mod_value_list,
            module.structure_comparison,
            label="struc_comp." + module.label,
        )


class BootZCurveFigure(StructureFigure):
    def setup_axes(self):
        self.init_axes(
            "Bootstrapped thermal impedance",
            r"time, $t$, in s",
            r"$Z_{\rm th}$ / K$\cdot$ W$^{-1}$",
        )

    def plot_module_data(self, module):
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
    def setup_axes(self):
        self.init_axes(
            "Bootstrapped impulse response",
            r"time, $t$, in s",
            r"impulse response, $h$, in K$\cdot$ W$^{-1}$",
        )

    def plot_module_data(self, module):
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
    def setup_axes(self):
        self.init_axes(
            "Bootstrapped time constant spectrum",
            r"time constant, $\tau$, in s",
            r"resistance, $R'$, in K$\cdot$ W$^{-1}$",
        )

    def plot_module_data(self, module):
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
    def setup_axes(self):
        self.init_axes(
            "Bootstrapped cumulative time constant spectrum",
            r"time constant, $\tau$, in s",
            r"cumulative resistance, $R'_\Sigma$, in K$\cdot$ W$^{-1}$",
        )

    def plot_module_data(self, module):
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
    def setup_axes(self):
        self.init_axes(
            "Bootstrapped cumulative structure function",
            r"cumulative thermal resistance, $R_\Sigma$, in K$\cdot$ W$^{-1}$",
            r"cumulative thermal capacity, $C_\Sigma$, in J$\cdot$ K$^{-1}$",
        )

    def plot_module_data(self, module):
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
    def setup_axes(self):
        self.init_axes("Residuals", r"count", r"residuals")

    def plot_module_data(self, module):
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
    def setup_axes(self):
        self.init_axes(
            "Predicted temperature",
            r"time, $t$, in s",
            r"temperature, $T$, in $^\circ\!$C",
        )

    def plot_module_data(self, module):
        self.ax.plot(
            module.lin_time_pos,
            module.predicted_temperature,
            linewidth=1.5,
            markersize=0.0,
            label="pred. temp." + module.label,
            color="blue",
        )

        self.ax2 = self.ax.twinx()
        self.ax2.set_ylabel(r"power, $P$, in W")

        self.ax2.plot(
            module.lin_time_pos,
            module.power_function_int,
            linewidth=1.0,
            marker="o",
            markersize=1.0,
            label="power" + module.label,
            color="red",
        )


class PredictionImpulseUsedFigure(StructureFigure):
    def setup_axes(self):
        self.init_axes(
            "Prediction Impulse Response Used",
            r"time, $t$, in s",
            r"impulse response, $h$, in K$\cdot$ W$^{-1}$",
        )

    def plot_module_data(self, module):
        self.ax.plot(
            module.lin_time,
            module.impulse_response_int,
            linewidth=1.0,
            label="lin. impulse resp." + module.label,
            markersize=1.5,
            marker="o",
        )


class PerfFigure(StructureFigure):
    def setup_axes(self):
        self.init_axes(
            "Performance profile",
            "duration (s)",
            "",
        )

    def plot_module_data(self, module):
        monitor = getattr(module, "perf_monitor", None)
        if monitor is None or not getattr(monitor, "enabled", False):
            return

        spans = monitor.spans()
        if not spans:
            return

        names, durations = zip(*spans)
        y_pos = np.arange(len(names))
        self.ax.barh(y_pos, durations, color=self.next_color())
        self.ax.set_yticks(y_pos, labels=names)
        self.ax.invert_yaxis()
