import numpy as np
import numpy.polynomial.polynomial as poly
import scipy.integrate as sin

import matplotlib

matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.cm as cmp


class StructureFigure:

    def __init__(self, fig, ax, total_calls=6, colormap="nipy_spectral"):
        self.fig = fig
        self.ax = ax
        self.num_calles = 0
        self.total_calls = total_calls
        self.colormap = colormap
        self.colorlist = cmp.get_cmap(colormap)(np.linspace(0, 1, total_calls))

    def close(self):
        self.fig.clf()  # Clear the figure
        plt.close(self.fig)  # Just in case, ensure the figure is closed

    def base_fig(self):
        fig = Figure(figsize=(10, 6))
        FigureCanvas(fig)
        ax = fig.add_subplot(1, 1, 1)
        return fig, ax

    def next_color(self):

        self.last_call = self.num_calles

        self.num_calles += 1

        self.num_calles = self.num_calles % self.total_calls

        return self.colorlist[self.last_call]

    def same_color(self):
        return self.colorlist[self.last_call]

    def make_raw_figure(self):
        if "raw_data" in self.figures:
            plot = self.figures["raw_data"]
        else:
            plot = StructureFigure(
                *self.base_fig(),
                total_calls=self.fig_total_calls,
            )
            self.figures["raw_data"] = plot

            plot.ax.set_xlabel("time in s")
            plot.ax.set_ylabel("temperature in $^\circ\!$C")

        plot.ax.semilogx(self.time_raw, self.temp_raw, "x")
        plot.ax.semilogx(
            self.time_raw[:],
            self.temp_raw[:],
            "x",
        )

    def make_extrpl_figure(self, ft_prm):
        if "extrpl" in self.figures:
            plot = self.figures["extrpl"]
        else:
            plot = StructureFigure(
                *self.base_fig(),
                total_calls=self.fig_total_calls,
            )
            self.figures["extrpl"] = plot

            plot.ax.set_xlabel("square root of time $\sqrt{s}$")
            plot.ax.set_ylabel("temperature in $^\circ\!$C")

        plot.ax.plot(
            np.sqrt(self.time),
            self.temperature,
            label="temperatur",
            markersize=2.5,
            marker="o",
        )
        plot.ax.plot(np.sqrt(self.time_raw), self.temp_raw, label="temp_raw")
        plot.ax.plot(
            np.sqrt(self.time_raw[self.lower_fit_limit : self.upper_fit_limit]),
            self.temp_raw[self.lower_fit_limit : self.upper_fit_limit],
            label="fit window",
            markersize=1.5,
            marker="o",
        )
        plot.ax.plot(
            np.sqrt(self.time), poly.polyval(np.sqrt(self.time), ft_prm), label="fit"
        )

        plot.ax.set_xlim(
            -np.sqrt(self.time_raw[self.upper_fit_limit] * 0.5),
            np.sqrt(self.time_raw[self.upper_fit_limit] * 2.5),
        )
        plot.ax.set_ylim(
            self.temp_raw[self.lower_fit_limit] * 0.75,
            self.temp_raw[self.upper_fit_limit] * 1.25,
        )

    def make_voltage_figure(self):
        if "volt" in self.figures:
            plot = self.figures["volt"]
        else:
            plot = StructureFigure(
                *self.base_fig(),
                total_calls=self.fig_total_calls,
            )
            self.figures["volt"] = plot

            plot.ax.set_xlabel("time in s")
            plot.ax.set_ylabel("voltage in V")

        plot.ax.semilogx(
            self.time_raw,
            self.voltage,
            label=self.label,
            linewidth=0.0,
            markersize=1.5,
            marker="o",
            color=plot.next_color(),
        )

    def make_temp_figure(self):
        if "temp" in self.figures:
            plot = self.figures["temp"]
        else:
            plot = StructureFigure(
                *self.base_fig(),
                total_calls=self.fig_total_calls,
            )
            self.figures["temp"] = plot

            plot.ax.set_xlabel("time in s")
            plot.ax.set_ylabel("temperature in $^\circ\!$C")

        plot.ax.semilogx(
            self.time,
            self.temperature,
            label=self.label,
            linewidth=0.0,
            markersize=1.5,
            marker="o",
            color=plot.next_color(),
        )

    def make_z_curve_figure(self):
        if "z_curve" in self.figures:
            plot = self.figures["z_curve"]
        else:
            plot = StructureFigure(
                *self.base_fig(),
                total_calls=self.fig_total_calls,
            )
            self.figures["z_curve"] = plot

            plot.axup = plot.ax.twiny()
            plot.axup.set_position(
                [0.162, 1 - 0.6899 - 0.15, 0.676, 0.6899], which="both"
            )

            plot.axup.set_xlabel("logarithmic time $z$")
            plot.axup.xaxis.labelpad = 20
            plot.ax.set_ylabel(r"$Z_{\rm th}$ / K$\cdot$ W$^{-1}$")

            if "theo_impedance" in self.figures:
                theo_plot = self.figures["theo_impedance"]
                plot.ax.semilogx(
                    np.exp(theo_plot.theo_log_time),
                    theo_plot.theo_impedance,
                    label="theoretical impedance ",
                    linewidth=1.0,
                    markersize=1.5,
                )

        plot.ax.semilogx(
            np.exp(self.log_time),
            self.impedance,
            linewidth=0.0,
            marker="o",
            markersize=1.5,
            label="impedance",
            color=plot.next_color(),
        )
        plot.ax.semilogx(
            np.exp(self.log_time_interp),
            self.imp_smooth,
            linewidth=1.5,
            markersize=0.0,
            label="local average",
            color=plot.same_color(),
        )

        low, high = plot.ax.get_xlim()
        plot.axup.set_xlim(np.log(low), np.log(high))

    def make_deriv_figure(self):
        if "deriv" in self.figures:
            plot = self.figures["deriv"]
        else:
            plot = StructureFigure(
                *self.base_fig(),
                total_calls=self.fig_total_calls,
            )
            self.figures["deriv"] = plot

            plot.axup = plot.ax.twiny()
            plot.axup.set_position(
                [0.162, 1 - 0.6899 - 0.15, 0.676, 0.6899], which="both"
            )
            plot.axup.set_xlabel("logarithmic time $z$")
            plot.axup.xaxis.labelpad = 20
            plot.ax.set_xlabel("time $t$ / s")
            plot.ax.set_ylabel(
                r"derivative of $Z_{\rm th}$ / K$\cdot$ W$^{-1}$",
                usetex=False,
            )

            if "theo_imp_deriv" in self.figures:
                theo_plot = self.figures["theo_imp_deriv"]
                plot.ax.semilogx(
                    np.exp(theo_plot.theo_log_time),
                    theo_plot.theo_imp_deriv,
                    label="theoretical derivative ",
                    linewidth=1.0,
                    markersize=1.5,
                )

        plot.imp_deriv_interp = self.imp_deriv_interp
        plot.log_time_pad = self.log_time_pad
        plot.ax.semilogx(
            np.exp(self.log_time_pad),
            self.imp_deriv_interp,
            marker="o",
            lw=1.5,
            label=self.label,
            markersize=0.0,
            color=plot.next_color(),
        )

        low, high = plot.ax.get_xlim()
        plot.axup.set_xlim(np.log(low), np.log(high))

    def make_fft_figure(self):
        if "fft" in self.figures:
            plot = self.figures["fft"]
        else:
            plot = StructureFigure(
                *self.base_fig(),
                total_calls=self.fig_total_calls,
            )
            self.figures["fft"] = plot

            plot.ax.set_xlim(0, 7)
            plot.ax.set_ylim(1e-6, 1e3)
            plot.ax.set_xlabel(r"$\omega$")
            plot.ax.set_ylabel(r"Power density")

        plot.ax.semilogy(self.fft_freq, self.fft_idi_pegrm, "o", markersize=2)
        plot.ax.semilogy(self.fft_freq, self.current_filter, "o", markersize=2)
        plot.ax.semilogy(
            self.fft_freq, self.fft_idi_pegrm * self.current_filter, "o", markersize=2
        )

    def make_time_spec_figure(self):
        if "time_spec" in self.figures:
            plot = self.figures["time_spec"]
        else:
            plot = StructureFigure(
                *self.base_fig(),
                total_calls=self.fig_total_calls,
            )
            self.figures["time_spec"] = plot

            plot.axup = plot.ax.twiny()
            plot.axup.set_position(
                [0.162, 1 - 0.6899 - 0.15, 0.676, 0.6899], which="both"
            )
            plot.axup.set_xlabel("logarithmic time constant $\zeta$")
            plot.axup.xaxis.labelpad = 20
            plot.ax.set_xlabel(r"time constant $\tau$ / s")
            plot.ax.set_ylabel(r"resistance $R$ / $\Omega$")

            if "theo_time_const" in self.figures:
                theo_plot = self.figures["theo_time_const"]
                plot.ax.semilogx(
                    np.exp(theo_plot.theo_log_time),
                    theo_plot.theo_time_const,
                    label="theoretical spectrum ",
                    linewidth=1.0,
                    markersize=1.5,
                )

        plot.log_time_pad = self.log_time_pad
        plot.time_spec = self.time_spec
        plot.ax.semilogx(
            np.exp(self.log_time_pad),
            self.time_spec,
            label="spectrum " + self.label,
            lw=0.7,
            ms=3.0,
            marker="o",
            color=plot.next_color(),
        )
        plot.ax.semilogx(
            np.exp(self.crop_log_time),
            self.crop_time_spec,
            lw=0.0,
            ms=2.0,
            marker="o",
            color=plot.same_color(),
        )

        low, high = plot.ax.get_xlim()
        plot.axup.set_xlim(np.log(low), np.log(high))

    def make_sum_time_spec_figure(self):
        if "sum_time_spec" in self.figures:
            plot = self.figures["sum_time_spec"]
        else:
            plot = StructureFigure(
                *self.base_fig(),
                total_calls=self.fig_total_calls,
            )
            self.figures["sum_time_spec"] = plot

            plot.axup = plot.ax.twiny()
            plot.axup.set_position(
                [0.162, 1 - 0.6899 - 0.15, 0.676, 0.6899], which="both"
            )
            plot.axup.set_xlabel("logarithmic time constant $\zeta$")
            plot.axup.xaxis.labelpad = 20
            plot.ax.set_xlabel(r"time constant $\tau$ / s")
            plot.ax.set_ylabel(r"cumulative resistance $R$ / $\Omega$")

            if "theo_time_const" in self.figures:
                theo_plot = self.figures["theo_time_const"]
                sum_theo_time_spec = sin.cumulative_trapezoid(
                    theo_plot.theo_time_const, x=theo_plot.theo_log_time, initial=0.0
                )
                plot.ax.semilogx(
                    np.exp(theo_plot.theo_log_time),
                    sum_theo_time_spec,
                    label="theoretical spectrum ",
                    linewidth=1.0,
                    markersize=1.5,
                )

        sum_time_spec = sin.cumulative_trapezoid(
            self.time_spec, x=self.log_time_pad, initial=0.0
        )

        plot.ax.semilogx(
            np.exp(self.log_time_pad),
            sum_time_spec,
            label="spectrum " + self.label,
            lw=1.0,
            ms=1.5,
            color=plot.next_color(),
        )

        low, high = plot.ax.get_xlim()
        plot.axup.set_xlim(np.log(low), np.log(high))

    def make_cumul_struc_figure(self):
        if "cstruc" in self.figures:
            plot = self.figures["cstruc"]
        else:
            plot = StructureFigure(
                *self.base_fig(),
                total_calls=self.fig_total_calls,
            )
            self.figures["cstruc"] = plot

            plot.ax.set_ylim(1e-6, 1e5)
            plot.ax.set_xlabel(
                r"cumulative thermal resistance / K$\cdot$ W$^{-1}$",
                usetex=False,
            )
            plot.ax.set_ylabel(
                r"cumulative thermal capacity / J$\cdot$ K$^{-1}$",
                usetex=False,
            )

            if "theo_cstruc" in self.figures:
                theo_plot = self.figures["theo_cstruc"]
                plot.ax.semilogy(
                    theo_plot.theo_int_cau_res,
                    theo_plot.theo_int_cau_cap,
                    label="theoretical spectrum ",
                    linewidth=1.0,
                    markersize=1.5,
                )

        sliced = np.where(self.int_cau_cap <= 1e4)

        plot.int_cau_res = self.int_cau_res[sliced]
        plot.int_cau_cap = self.int_cau_cap[sliced]

        plot.ax.semilogy(
            self.int_cau_res[sliced],
            self.int_cau_cap[sliced],
            color=plot.next_color(),
            label="structure " + self.label,
            linewidth=1.0,
            markersize=1.5,
            marker="o",
        )

    def make_diff_struc_figure(self):
        if "dstruc" in self.figures:
            plot = self.figures["dstruc"]
        else:
            plot = StructureFigure(
                *self.base_fig(),
                total_calls=self.fig_total_calls,
            )
            self.figures["dstruc"] = plot

            plot.ax.set_ylim(1e-5, 1e5)
            plot.ax.set_xlabel(r"thermal resistance / K$\cdot$ W$^{-1}$")
            plot.ax.set_ylabel(r"thermal capacity / J$\cdot$ K$^{-1}$")

        plot.int_cau_res = self.int_cau_res[:-1]
        plot.diff_struc = self.diff_struc

        plot.ax.semilogy(
            plot.int_cau_res,
            plot.diff_struc,
            color=plot.next_color(),
            label="differential structure" + self.label,
            marker="o",
            markersize=2,
            linewidth=1.0,
        )

    def make_local_resist_figure(self):
        if "lresi" in self.figures:
            plot = self.figures["lresi"]
        else:
            plot = StructureFigure(
                *self.base_fig(),
                total_calls=self.fig_total_calls,
            )
            self.figures["lresi"] = plot

            plot.ax.set_xlim(1e-5, 1e2)
            plot.ax.set_ylabel(r"thermal resistance / K$\cdot$ W$^{-1}$")
            plot.ax.set_xlabel(
                r"cummulative thermal capacity / J$\cdot$ K$^{-1}$",
                usetex=False,
            )

        plot.cau_res = self.cau_res

        plot.ax.semilogx(
            (self.int_cau_cap),
            plot.cau_res,
            color=plot.next_color(),
            label="local_resistance_" + self.label,
            marker="o",
            markersize=2,
            linewidth=1.0,
        )

    def make_local_gradient_figure(self):
        if "lresi" in self.figures:
            plot = self.figures["lresi"]
        else:
            plot = StructureFigure(
                *self.base_fig(),
                total_calls=self.fig_total_calls,
            )
            self.figures["lresi"] = plot

            plot.ax.set_xlim(1e-5, 1e2)
            plot.ax.set_ylabel(r"thermal gradient")
            plot.ax.set_xlabel(
                r"cummulative thermal capacity / J$\cdot$ K$^{-1}$",
                usetex=False,
            )

        plot.cau_res = self.cau_res

        plot.ax.semilogx(
            (self.int_cau_cap),
            plot.cau_res / self.cau_cap,
            color=plot.next_color(),
            label="local_resistance_" + self.label,
            marker="o",
            markersize=2,
            linewidth=1.0,
        )

    def make_TDIM1_figure(self):
        if "TDIM1" in self.figures:
            plot = self.figures["TDIM1"]

            delta = np.mean(plot.reference_impedance[-20:]) - np.mean(
                self.impedance[-20:]
            )

            interp_deriv = np.interp(
                plot.reference_time, self.log_time_pad, self.imp_deriv_interp
            )
            w_deriv = np.abs((interp_deriv - self.imp_deriv_interp) / delta)

            plot.imp_deriv_interp = self.imp_deriv_interp
            plot.log_time_pad = self.log_time_pad

            plot.ax.semilogx(
                np.exp(plot.reference_time),
                w_deriv,
                marker="o",
                lw=1.5,
                label=self.label,
                markersize=0.0,
                color=plot.next_color(),
            )

        else:
            plot = StructureFigure(
                *self.base_fig(),
                total_calls=self.fig_total_calls,
            )
            self.figures["TDIM1"] = plot

            plot.axup = plot.ax.twiny()
            plot.axup.set_position(
                [0.162, 1 - 0.6899 - 0.15, 0.676, 0.6899], which="both"
            )
            plot.axup.set_xlabel("logarithmic time $z$")
            plot.axup.xaxis.labelpad = 20
            plot.ax.set_xlabel("time $t$ / s")
            plot.ax.set_ylabel(
                r"derivative of $Z_{\rm th}$ / K$\cdot$ W$^{-1}$",
                usetex=False,
            )

            plot.reference_deriv = self.imp_deriv_interp
            plot.reference_time = self.log_time_pad
            plot.reference_impedance = self.impedance

        low, high = plot.ax.get_xlim()
        plot.axup.set_xlim(np.log(low), np.log(high))

    def make_TDIM2_figure(self):
        if "TDIM2" in self.figures:
            plot = self.figures["TDIM2"]

            delta = np.mean(plot.reference_impedance[-20:]) - np.mean(
                self.impedance[-20:]
            )

            interp_deriv = np.interp(
                plot.reference_time, self.log_time_pad, self.imp_deriv_interp
            )
            w_deriv = np.abs((interp_deriv - self.imp_deriv_interp) / delta)

            plot.imp_deriv_interp = self.imp_deriv_interp
            plot.log_time_pad = self.log_time_pad

            plot.ax.semilogx(
                np.exp(plot.reference_time),
                w_deriv,
                marker="o",
                lw=1.5,
                label=self.label,
                markersize=0.0,
                color=plot.next_color(),
            )

        else:
            plot = StructureFigure(
                *self.base_fig(),
                total_calls=self.fig_total_calls,
            )
            self.figures["TDIM1"] = plot

            plot.axup = plot.ax.twiny()
            plot.axup.set_position(
                [0.162, 1 - 0.6899 - 0.15, 0.676, 0.6899], which="both"
            )
            plot.axup.set_xlabel("logarithmic time $z$")
            plot.axup.xaxis.labelpad = 20
            plot.ax.set_xlabel("time $t$ / s")
            plot.ax.set_ylabel(
                r"derivative of $Z_{\rm th}$ / K$\cdot$ W$^{-1}$",
                usetex=False,
            )

            plot.int_cau_res = self.int_cau_res
            plot.int_cau_cap = self.int_cau_cap

        low, high = plot.ax.get_xlim()
        plot.axup.set_xlim(np.log(low), np.log(high))

    def make_theo_cstruc_figure(self):
        if "theo_cstruc" in self.figures:
            plot = self.figures["theo_cstruc"]
        else:
            plot = StructureFigure(
                *self.base_fig(),
                total_calls=self.fig_total_calls,
            )
            self.figures["theo_cstruc"] = plot

            plot.ax.set_xlabel(r"cumulative resistance / arb. u.")
            plot.ax.set_ylabel(r"cumulative capacity / arb. u.")

        plot.theo_int_cau_res = self.theo_int_cau_res
        plot.theo_int_cau_cap = self.theo_int_cau_cap

        plot.ax.semilogy(
            self.theo_int_cau_res,
            self.theo_int_cau_cap,
            color=plot.next_color(),
            label="optimized structure" + self.label,
            linewidth=3.0,
        )

        if "cstruc" in self.figures:
            alt_plot = self.figures["cstruc"]
            plot.ax.semilogy(
                alt_plot.int_cau_res,
                alt_plot.int_cau_cap,
                color=plot.same_color(),
                label="forward structure ",
                linewidth=3.0,
            )

    def make_theo_diff_struc_figure(self):
        if "theo_dstruc" in self.figures:
            plot = self.figures["theo_dstruc"]
        else:
            plot = StructureFigure(
                *self.base_fig(),
                total_calls=self.fig_total_calls,
            )
            self.figures["theo_dstruc"] = plot

            plot.ax.set_xlabel(r"cumulative resistance / arb. u.")
            plot.ax.set_ylabel(r"cumulative capacity / arb. u.")

        plot.theo_int_cau_res = self.theo_int_cau_res[:-1]  # [sliced]
        plot.theo_diff_struc = self.theo_diff_struc  # [sliced]

        plot.ax.semilogy(
            plot.theo_int_cau_res,
            plot.theo_diff_struc,
            color=plot.next_color(),
            label="theo diff structure" + self.label,
            marker="o",
            markersize=3,
            linewidth=1.0,
        )

        if "dstruc" in self.figures:
            alt_plot = self.figures["dstruc"]
            plot.ax.semilogy(
                alt_plot.int_cau_res,
                alt_plot.diff_struc,
                color=plot.same_color(),
                label="forward diff struc",
                linewidth=3.0,
            )

    def make_theo_local_resist_figure(self):
        if "theo_lresi" in self.figures:
            plot = self.figures["theo_lresi"]
        else:
            plot = StructureFigure(
                *self.base_fig(),
                total_calls=self.fig_total_calls,
            )
            self.figures["theo_lresi"] = plot

            plot.ax.set_xlabel(r"cumulative resistance / arb. u.")
            plot.ax.set_ylabel(r"cumulative capacity / arb. u.")

            if "dstruc" in self.figures:
                alt_plot = self.figures["dstruc"]
                plot.ax.semilogy(
                    alt_plot.int_cau_res,
                    alt_plot.diff_struc,
                    label="forward diff struc",
                    linewidth=3.0,
                )

        plot.theo_cau_res = self.theo_cau_res
        plot.theo_int_cau_cap = self.theo_int_cau_cap

        plot.ax.semilogy(
            plot.theo_int_cau_res,
            plot.theo_int_cau_cap,
            label="optimized structure",
            linewidth=3.0,
        )

        sliced = np.where(
            (self.theo_diff_struc >= 1e-3) & (self.theo_diff_struc <= 1e8)
        )
        plot.ax.semilogy(
            (self.theo_int_cau_res[:-1])[sliced],
            self.theo_diff_struc[sliced],
            color=plot.next_color(),
            label="theo diff structure" + self.label,
            marker="o",
            markersize=3,
            linewidth=1.0,
        )

    def make_theo_time_const_figure(self):

        if "theo_time_const" in self.figures:
            plot = self.figures["theo_time_const"]
        else:
            plot = StructureFigure(
                *self.base_fig(),
                total_calls=self.fig_total_calls,
            )
            self.figures["theo_time_const"] = plot

            plot.axup = plot.ax.twiny()
            plot.axup.set_position(
                [0.162, 1 - 0.6899 - 0.15, 0.676, 0.6899], which="both"
            )
            plot.axup.xaxis.labelpad = 20
            plot.axup.set_xlabel(
                r"logarithmic time constant $\zeta = \ln(\tau)$",
                usetex=False,
            )
            plot.ax.set_xlabel(r"time constant $\tau$ / s")
            plot.ax.set_ylabel(r"thermal resistance / K$\cdot$ W$^{-1}$")

            if "time_spec" in self.figures:
                alt_plot = self.figures["time_spec"]
                plot.ax.semilogx(
                    np.exp(alt_plot.log_time_pad),
                    alt_plot.time_spec,
                    label="bayesian spectrum",
                    linewidth=1.0,
                    markersize=1.5,
                )

        plot.theo_log_time = self.theo_log_time
        plot.theo_time_const = self.theo_time_const
        plot.ax.semilogx(
            np.exp(self.theo_log_time),
            self.theo_time_const,
            marker="o",
            color=plot.next_color(),
            label="optimized spectrum" + self.label,
            linewidth=1.0,
            markersize=1.5,
        )
        low, high = plot.ax.get_xlim()
        plot.axup.set_xlim(np.log(low), np.log(high))

    def make_theo_sum_time_const_figure(self):

        if "theo_sum_time_const" in self.figures:
            plot = self.figures["theo_sum_time_const"]
        else:
            plot = StructureFigure(
                *self.base_fig(),
                total_calls=self.fig_total_calls,
            )
            self.figures["theo_sum_time_const"] = plot

            plot.axup = plot.ax.twiny()
            plot.axup.set_position(
                [0.162, 1 - 0.6899 - 0.15, 0.676, 0.6899], which="both"
            )
            plot.axup.xaxis.labelpad = 20
            plot.axup.set_xlabel(
                r"logarithmic time constant $\zeta = \ln(\tau)$",
                usetex=False,
            )
            plot.ax.set_xlabel(r"time constant $\tau$ / s")
            plot.ax.set_ylabel(r"thermal resistance / K$\cdot$ W$^{-1}$")

        plot.theo_log_time = self.theo_log_time
        plot.theo_time_const = self.theo_time_const

        sum_theo_time_spec = sin.cumulative_trapezoid(
            self.theo_time_const, x=self.theo_log_time, initial=0.0
        )
        plot.ax.semilogx(
            np.exp(self.theo_log_time),
            sum_theo_time_spec,
            marker="o",
            color=plot.next_color(),
            label="theoretical integrated spectrum " + self.label,
            linewidth=1.0,
            markersize=1.5,
        )

        if "time_spec" in self.figures:
            alt_plot = self.figures["time_spec"]
            sum_time_spec = sin.cumulative_trapezoid(
                alt_plot.time_spec, x=alt_plot.log_time_pad, initial=0.0
            )
            plot.ax.semilogx(
                np.exp(alt_plot.log_time_pad),
                sum_time_spec,
                color=plot.same_color(),
                label="forward integrated spectrum" + self.label,
                linewidth=1.0,
                markersize=1.5,
            )

        low, high = plot.ax.get_xlim()
        plot.axup.set_xlim(np.log(low), np.log(high))

    def make_theo_imp_deriv_figure(self):
        if "theo_imp_deriv" in self.figures:
            plot = self.figures["theo_imp_deriv"]
        else:
            plot = StructureFigure(
                *self.base_fig(),
                total_calls=self.fig_total_calls,
            )
            self.figures["theo_imp_deriv"] = plot

            plot.axup = plot.ax.twiny()
            plot.axup.set_position(
                [0.162, 1 - 0.6899 - 0.15, 0.676, 0.6899], which="both"
            )
            plot.axup.set_xlabel("logarithmic time $z$")
            plot.axup.xaxis.labelpad = 20
            plot.ax.set_xlabel("time / s")
            plot.ax.set_ylabel(
                r"derivative of the $Z_{\rm th}$-curves / K$\cdot$ W$^{-1}$",
                usetex=False,
            )

        plot.theo_log_time = self.theo_log_time
        plot.theo_imp_deriv = self.theo_imp_deriv

        plot.ax.semilogx(
            np.exp(self.theo_log_time),
            self.theo_imp_deriv,
            linewidth=1.5,
            color=plot.next_color(),
            label="theoretical derivative " + self.label,
            markersize=1.5,
        )

        if "deriv" in self.figures:
            alt_plot = self.figures["deriv"]
            plot.ax.semilogx(
                np.exp(alt_plot.log_time_pad),
                alt_plot.imp_deriv_interp,
                color=plot.same_color(),
                label="forward derivative " + self.label,
                linewidth=1.5,
                markersize=1.5,
            )
            plot.imp_deriv_interp = self.imp_deriv_interp
            plot.log_time_pad = self.log_time_pad

        low, high = plot.ax.get_xlim()
        plot.axup.set_xlim(np.log(low), np.log(high))

    def make_theo_impedance_figure(self):
        if "theo_impedance" in self.figures:
            plot = self.figures["theo_impedance"]
        else:
            plot = StructureFigure(
                *self.base_fig(),
                total_calls=self.fig_total_calls,
            )
            self.figures["theo_impedance"] = plot

            plot.axup = plot.ax.twiny()
            plot.axup.set_position(
                [0.162, 1 - 0.6899 - 0.15, 0.676, 0.6899], which="both"
            )
            plot.axup.set_xlabel("logarithmic time $z$")
            plot.axup.xaxis.labelpad = 20

            plot.ax.set_xlabel("time / s")
            plot.ax.set_ylabel(r"$Z_{\rm th}$ curve / K$\cdot$ W$^{-1}$")
        plot.theo_log_time = self.theo_log_time
        plot.theo_impedance = self.theo_impedance

        plot.ax.semilogx(
            np.exp(self.theo_log_time),
            self.theo_impedance,
            linewidth=1.5,
            label="theoretical impedance " + self.label,
        )

        low, high = plot.ax.get_xlim()
        plot.axup.set_xlim(np.log(low), np.log(high))

    def make_backwards_imp_deriv_figure(self):
        if "back_deriv" in self.figures:
            plot = self.figures["back_deriv"]
        else:
            plot = StructureFigure(
                *self.base_fig(),
                total_calls=self.fig_total_calls,
            )
            self.figures["back_deriv"] = plot

            plot.axup = plot.ax.twiny()
            plot.axup.set_position(
                [0.162, 1 - 0.6899 - 0.15, 0.676, 0.6899], which="both"
            )
            plot.axup.set_xlabel("logarithmic time $z$")
            plot.axup.xaxis.labelpad = 20
            plot.ax.set_xlabel("time / s")
            plot.ax.set_ylabel(
                r"derivative of the $Z_{\rm th}$-curves / K$\cdot$ W$^{-1}$",
                usetex=False,
            )

        plot.ax.semilogx(
            np.exp(self.log_time_pad),
            self.imp_deriv_interp,
            linewidth=1.5,
            label="original derivative " + self.label,
            markersize=1.5,
            color=plot.next_color(),
        )
        plot.ax.semilogx(
            np.exp(self.log_time_pad),
            self.back_imp_deriv,
            linewidth=0.0,
            marker="o",
            label="backwards derivative " + self.label,
            markersize=1.5,
            color=plot.same_color(),
        )

        low, high = plot.ax.get_xlim()
        plot.axup.set_xlim(np.log(low), np.log(high))

    def make_backwards_impedance_figure(self):
        if "back_impedance" in self.figures:
            plot = self.figures["back_impedance"]
        else:
            plot = StructureFigure(
                *self.base_fig(),
                total_calls=self.fig_total_calls,
            )
            self.figures["back_impedance"] = plot

            plot.axup = plot.ax.twiny()
            plot.axup.set_position(
                [0.162, 1 - 0.6899 - 0.15, 0.676, 0.6899], which="both"
            )
            plot.axup.set_xlabel("logarithmic time $z$")
            plot.axup.xaxis.labelpad = 20

            plot.ax.set_xlabel("time / s")
            plot.ax.set_ylabel(r"$Z_{\rm th}$ curve / K$\cdot$ W$^{-1}$")

            plot.ax.semilogx(
                np.exp(self.log_time),
                self.impedance,
                linewidth=0.0,
                marker="o",
                markersize=1.0,
                label="original impedance " + self.label,
            )
        plot.ax.semilogx(
            np.exp(self.log_time_pad),
            self.back_imp,
            linewidth=0.0,
            marker="o",
            markersize=2.0,
            label="backwards impedance " + self.label,
            color=plot.next_color(),
        )
        plot.ax.semilogx(
            np.exp(self.log_time_interp),
            self.imp_smooth,
            linewidth=1.5,
            markersize=0.0,
            label="local average",
            color=plot.same_color(),
        )

        low, high = plot.ax.get_xlim()
        plot.axup.set_xlim(np.log(low), np.log(high))

    def make_theo_backwards_impedance_figure(self):
        if "theo_back_impedance" in self.figures:
            plot = self.figures["theo_back_impedance"]
        else:
            plot = StructureFigure(
                *self.base_fig(),
                total_calls=self.fig_total_calls,
            )
            self.figures["theo_back_impedance"] = plot

            plot.axup = plot.ax.twiny()
            plot.axup.set_position(
                [0.162, 1 - 0.6899 - 0.15, 0.676, 0.6899], which="both"
            )
            plot.axup.set_xlabel("logarithmic time $z$")
            plot.ax.set_xlabel("time / s")
            plot.ax.set_ylabel(r"impedance curve / arb. u.")

        plot.ax.semilogx(
            np.exp(self.log_time_pad),
            self.back_imp,
            linewidth=3,
            marker="o",
            markersize=0.0,
            label="Bayesian impedance",
            zorder=5,
        )
        plot.ax.semilogx(
            np.exp(self.theo_log_time),
            self.theo_impedance,
            linewidth=3,
            marker="o",
            markersize=0.0,
            label="optimized impedance",
            zorder=10,
        )
        plot.ax.semilogx(
            np.exp(self.opt_log_time),
            self.opt_imp,
            linewidth=0.0,
            marker="o",
            markersize=6,
            label="measured impedance",
            zorder=0,
            fillstyle="none",
        )

        low, high = plot.ax.get_xlim()
        plot.axup.set_xlim(np.log(low), np.log(high))

    def make_optimize_struc_figure(self):
        if "optimize_struc" in self.figures:
            plot = self.figures["optimize_struc"]
        else:
            plot = StructureFigure(
                *self.base_fig(),
                total_calls=self.fig_total_calls,
            )
            self.figures["optimize_struc"] = plot

            plot.ax.set_xlabel(
                r"cumulative thermal resistance / K$\cdot$ W$^{-1}$",
                usetex=False,
            )
            plot.ax.set_ylabel(
                r"cumulative thermal capacity / J$\cdot$ K$^{-1}$",
                usetex=False,
            )

        plot.ax.semilogy(
            self.int_cau_res,
            self.int_cau_cap,
            label="structure " + self.label,
            linewidth=1.0,
            markersize=1.5,
        )

        plot.ax.semilogy(
            self.init_opt_imp_res,
            self.init_opt_imp_cap,
            lw=0.0,
            ms=3,
            marker="o",
            label="init_opt_imp_cap",
        )

        if self.struc_init_method == "optimal_fit":
            plot.ax.semilogy(
                self.init_opt_struc_res,
                self.init_opt_struc_cap,
                lw=0.0,
                ms=3,
                marker="o",
                label="init_opt_struc_cap",
            )

        plot.ax.semilogy(
            self.fin_res, self.fin_cap, lw=0.0, ms=3, marker="o", label="opt_cap"
        )

    def make_time_const_comparison(self):
        if "time_const_comparison" in self.figures:
            plot = self.figures["time_const_comparison"]
        else:
            plot = StructureFigure(
                *self.base_fig(),
                total_calls=self.fig_total_calls,
            )
            self.figures["time_const_comparison"] = plot

            plot.ax.set_xlabel(self.mod_key_display_name.replace("_", " "))
            plot.ax.set_ylabel(r"objective function time const")

        plot.ax.scatter(
            self.mod_value_list,
            self.time_const_comparison,
            label="time_const_comparison" + self.label,
        )

    def make_total_resist_comparison(self):
        if "total_resist_comparison" in self.figures:
            plot = self.figures["total_resist_comparison"]
        else:
            plot = StructureFigure(
                *self.base_fig(),
                total_calls=self.fig_total_calls,
            )
            self.figures["total_resist_comparison"] = plot

            plot.ax.set_xlabel(self.mod_key_display_name.replace("_", " "))
            plot.ax.set_ylabel(r"total resistance difference")

        plot.ax.scatter(
            self.mod_value_list,
            self.total_resist_diff,
            label="total_resist_comparison" + self.label,
        )

    def make_struc_comparison(self):
        if "struc_comparison" in self.figures:
            plot = self.figures["struc_comparison"]
        else:
            plot = StructureFigure(
                *self.base_fig(),
                total_calls=self.fig_total_calls,
            )
            self.figures["struc_comparison"] = plot

            plot.ax.set_xlabel(self.mod_key_display_name.replace("_", " "))
            plot.ax.set_ylabel(r"objective function structure")

        plot.ax.scatter(
            self.mod_value_list,
            self.structure_comparison,
            label="struc_comparison " + self.label,
        )

    def make_boot_z_curve_figure(self):
        if "boot_z_curve" in self.figures:
            plot = self.figures["boot_z_curve"]
        else:
            plot = StructureFigure(
                *self.base_fig(),
                total_calls=self.fig_total_calls,
            )
            self.figures["boot_z_curve"] = plot

            plot.axup = plot.ax.twiny()
            plot.axup.set_position(
                [0.162, 1 - 0.6899 - 0.15, 0.676, 0.6899], which="both"
            )

            plot.axup.set_xlabel("logarithmic time $z$")
            plot.axup.xaxis.labelpad = 20
            plot.ax.set_ylabel(r"$Z_{\rm th}$ / K$\cdot$ W$^{-1}$")

        plot.ax.semilogx(
            np.exp(self.reference_time_imp),
            self.reference_impedance,
            linewidth=1.0,
            label="reference impedance",
            color="black",
        )
        plot.ax.semilogx(
            np.exp(self.imp_time),
            self.imp_av,
            linewidth=1.5,
            markersize=0.0,
            label="median impedance" + self.label,
            color=plot.next_color(),
        )
        plot.axup.fill_between(
            self.imp_time,
            self.imp_perc_u,
            self.imp_perc_l,
            alpha=0.5,
            label="confidence intervall" + self.label,
            color=plot.same_color(),
        )

        low, high = plot.ax.get_xlim()
        plot.axup.set_xlim(np.log(low), np.log(high))

    def make_boot_deriv_figure(self):
        if "boot_deriv" in self.figures:
            plot = self.figures["boot_deriv"]
        else:
            plot = StructureFigure(
                *self.base_fig(),
                total_calls=self.fig_total_calls,
            )
            self.figures["boot_deriv"] = plot

            plot.axup = plot.ax.twiny()
            plot.axup.set_position(
                [0.162, 1 - 0.6899 - 0.15, 0.676, 0.6899], which="both"
            )
            plot.axup.set_xlabel("logarithmic time $z$")
            plot.axup.xaxis.labelpad = 20
            plot.ax.set_xlabel("time $t$ / s")
            plot.ax.set_ylabel(
                r"derivative of $Z_{\rm th}$ / K$\cdot$ W$^{-1}$",
                usetex=False,
            )

        plot.ax.semilogx(
            np.exp(self.reference_deriv_time),
            self.reference_derivative,
            linewidth=1.0,
            label="reference derivative",
            color="black",
        )
        plot.ax.semilogx(
            np.exp(self.deriv_time),
            self.deriv_av,
            linewidth=1.5,
            markersize=0.0,
            label="median derivative" + self.label,
            color=plot.next_color(),
        )
        plot.axup.fill_between(
            self.deriv_time,
            self.deriv_perc_u,
            self.deriv_perc_l,
            alpha=0.5,
            label="confidence intervall" + self.label,
            color=plot.same_color(),
        )

        low, high = plot.ax.get_xlim()
        plot.axup.set_xlim(np.log(low), np.log(high))

    def make_boot_time_spec_figure(self):
        if "boot_time_spec" in self.figures:
            plot = self.figures["boot_time_spec"]
        else:
            plot = StructureFigure(
                *self.base_fig(),
                total_calls=self.fig_total_calls,
            )
            self.figures["boot_time_spec"] = plot

            plot.axup = plot.ax.twiny()
            plot.axup.set_position(
                [0.162, 1 - 0.6899 - 0.15, 0.676, 0.6899], which="both"
            )
            plot.axup.set_xlabel("logarithmic time constant $\zeta$")
            plot.axup.xaxis.labelpad = 20
            plot.ax.set_xlabel(r"time constant $\tau$ / s")
            plot.ax.set_ylabel(r"resistance $R$ / $\Omega$")

        plot.ax.semilogx(
            np.exp(self.reference_deriv_time),
            self.reference_spectrum,
            linewidth=1.0,
            label="reference spectrum",
            color="black",
        )
        plot.ax.semilogx(
            np.exp(self.deriv_time),
            self.time_spec_av,
            linewidth=1.5,
            markersize=0.0,
            label="median spectrum" + self.label,
            color=plot.next_color(),
        )
        plot.axup.fill_between(
            self.deriv_time,
            self.time_spec_perc_u,
            self.time_spec_perc_l,
            alpha=0.5,
            label="confidence intervall" + self.label,
            color=plot.same_color(),
        )

        low, high = plot.ax.get_xlim()
        plot.axup.set_xlim(np.log(low), np.log(high))

    def make_boot_sum_time_spec_figure(self):
        if "boot_sum_time_spec" in self.figures:
            plot = self.figures["boot_sum_time_spec"]
        else:
            plot = StructureFigure(
                *self.base_fig(),
                total_calls=self.fig_total_calls,
            )
            self.figures["boot_sum_time_spec"] = plot

            plot.axup = plot.ax.twiny()
            plot.axup.set_position(
                [0.162, 1 - 0.6899 - 0.15, 0.676, 0.6899], which="both"
            )
            plot.axup.set_xlabel("logarithmic time constant $\zeta$")
            plot.axup.xaxis.labelpad = 20
            plot.ax.set_xlabel(r"time constant $\tau$ / s")
            plot.ax.set_ylabel(r"cumulative resistance $R$ / $\Omega$")

        plot.ax.semilogx(
            np.exp(self.reference_deriv_time),
            self.reference_sum_spectrum,
            linewidth=1.0,
            label="reference sum spectrum",
            color="black",
        )
        plot.ax.semilogx(
            np.exp(self.deriv_time),
            self.sum_time_spec_av,
            linewidth=1.5,
            markersize=0.0,
            label="median sum spectrum" + self.label,
            color=plot.next_color(),
        )
        plot.axup.fill_between(
            self.deriv_time,
            self.sum_time_spec_perc_u,
            self.sum_time_spec_perc_l,
            alpha=0.5,
            label="confidence intervall" + self.label,
            color=plot.same_color(),
        )

        low, high = plot.ax.get_xlim()
        plot.axup.set_xlim(np.log(low), np.log(high))

    def make_boot_cumul_struc_figure(self):
        if "boot_cstruc" in self.figures:
            plot = self.figures["boot_cstruc"]
        else:
            plot = StructureFigure(
                *self.base_fig(),
                total_calls=self.fig_total_calls,
            )
            self.figures["boot_cstruc"] = plot

            plot.ax.set_ylim(1e-8, 1e3)
            plot.ax.set_xlim(-5, self.reference_cum_res[-1] * 1.1)
            plot.ax.set_xlabel(
                r"cumulative thermal resistance / K$\cdot$ W$^{-1}$",
                usetex=False,
            )
            plot.ax.set_ylabel(
                r"cumulative thermal capacity / J$\cdot$ K$^{-1}$",
                usetex=False,
            )

        plot.ax.semilogy(
            self.reference_cum_res,
            self.reference_cum_cap,
            linewidth=1.0,
            label="reference structure",
            color="black",
        )
        plot.ax.semilogy(
            self.res_fine,
            self.struc_cap_av,
            linewidth=1.5,
            markersize=0.0,
            label="median structure" + self.label,
            color=plot.next_color(),
        )
        plot.ax.fill_between(
            self.res_fine,
            self.struc_cap_perc_u,
            self.struc_cap_perc_l,
            alpha=0.5,
            label="confidence intervall" + self.label,
            color=plot.same_color(),
        )

    def make_prediction_figure(self):
        if "predicted_z_curve" in self.figures:
            plot = self.figures["predicted_z_curve"]
        else:
            plot = StructureFigure(
                *self.base_fig(),
                total_calls=self.fig_total_calls,
            )
            self.figures["predicted_z_curve"] = plot

            plot.ax.set_ylabel(r"$Z_{\rm th}$ / K$\cdot$ W$^{-1}$")
            plot.ax.set_xlabel("time / s")

        plot.ax.plot(
            self.actual_time,
            self.actual_impedance,
            linewidth=0.0,
            marker="o",
            markersize=1.5,
            label="actual impedance",
            color="red",
        )
        plot.ax.plot(
            self.lin_time,
            self.predicted_impedance,
            linewidth=1.5,
            markersize=0.0,
            label="predicted impedance",
            color="blue",
        )

        low, high = plot.ax.get_xlim()

    def make_prediction_impulse_used_figure(self):
        if "prediction_impulse_used" in self.figures:
            plot = self.figures["prediction_impulse_used"]
        else:
            plot = StructureFigure(
                *self.base_fig(),
                total_calls=self.fig_total_calls,
            )
            self.figures["prediction_impulse_used"] = plot

            plot.ax.set_xlabel("time / s")
            plot.ax.set_ylabel(
                r"derivative of the $Z_{\rm th}$-curves / K$\cdot$ W$^{-1}$",
                usetex=False,
            )

        plot.ax.plot(
            self.reference_time,
            self.reference_impulse_response,
            linewidth=1.5,
            label="theoretical linear derivative" + self.label,
            markersize=1.5,
        )
        plot.ax.plot(
            self.lin_time,
            self.impulse_response_int,
            linewidth=1.5,
            label="interpolation" + self.label,
            markersize=1.5,
        )

    def make_residual_figure(self):
        if "residual" in self.figures:
            plot = self.figures["residual"]
        else:
            plot = StructureFigure(
                *self.base_fig(),
                total_calls=self.fig_total_calls,
            )
            self.figures["residual"] = plot

            plot.ax.set_ylabel(r"residuals")
            plot.ax.set_xlabel(r"count")

        plot.ax.scatter(self.bins, self.hist, label="bins")
        plot.ax.plot(
            self.bins,
            self.gaus_curve,
            linewidth=1.5,
            markersize=0.0,
            label="gaussian fit",
            color="blue",
        )
