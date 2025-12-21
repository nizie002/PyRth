"""Figure exporting utilities that mirror the CSV handlers in IOManager."""

import logging
import os

from .transient_base_exporter import BaseExporter
from .transient_figures import (
    RawDataFigure,
    VoltageFigure,
    TempFigure,
    ExtrapolationFigure,
    ZCurveFigure,
    DerivFigure,
    FFTFigure,
    TimeSpecFigure,
    SumTimeSpecFigure,
    BackwardsImpFigure,
    BackwardsImpDerivFigure,
    CumulStrucFigure,
    DiffStrucFigure,
    LocalResistFigure,
    LocalGradientFigure,
    TheoCStrucFigure,
    TheoDiffStrucFigure,
    TheoTimeConstFigure,
    TheoSumTimeConstFigure,
    TheoImpDerivFigure,
    TheoImpFigure,
    TheoBackwardsImpFigure,
    OptimizeStrucFigure,
    TimeConstComparisonFigure,
    StrucComparisonFigure,
    TotalResistComparisonFigure,
    PredictionFigure,
    PredictionImpulseUsedFigure,
    ResidualFigure,
    BootZCurveFigure,
    BootDerivFigure,
    BootTimeSpecFigure,
    BootSumTimeSpecFigure,
    BootCumulStrucFigure,
)


logger = logging.getLogger("PyRthLogger")


class FigureExporter(BaseExporter):
    """Manage shared Matplotlib figures and persist them to disk."""

    type = "figure"
    # Prefixed registry ensures deterministic on-disk ordering.
    figure_registry = {
        # Raw input data
        "voltage": ("00", "look_at_voltage", VoltageFigure),
        "raw": ("01", "look_at_raw_data", RawDataFigure),
        "extrpl": ("02", "look_at_extrpl", ExtrapolationFigure),
        "temp": ("03", "look_at_temp", TempFigure),
        # Basic processing
        "impedance": ("10", "look_at_impedance", ZCurveFigure),
        "deriv": ("11", "look_at_deriv", DerivFigure),
        "fft": ("12", "look_at_fft", FFTFigure),
        # Time spectra and backwards processing
        "time_spec": ("20", "look_at_time_spec", TimeSpecFigure),
        "sum_time_spec": ("21", "look_at_sum_time_spec", SumTimeSpecFigure),
        "back_imp": ("22", "look_at_backwards_impedance", BackwardsImpFigure),
        "back_deriv": ("23", "look_at_backwards_imp_deriv", BackwardsImpDerivFigure),
        # Structure functions
        "cumul_struc": ("30", "look_at_cumul_struc", CumulStrucFigure),
        "diff_struc": ("31", "look_at_diff_struc", DiffStrucFigure),
        "local_resist": ("32", "look_at_local_resist", LocalResistFigure),
        "local_gradient": ("33", "look_at_local_gradient", LocalGradientFigure),
        # Theoretical results
        "theo_cstruc": ("40", "look_at_theo_cstruc", TheoCStrucFigure),
        "theo_diff_struc": ("41", "look_at_theo_diff_struc", TheoDiffStrucFigure),
        "theo_time_const": ("42", "look_at_theo_time_const", TheoTimeConstFigure),
        "theo_sum_time_const": (
            "43",
            "look_at_theo_sum_time_const",
            TheoSumTimeConstFigure,
        ),
        "theo_imp_deriv": ("44", "look_at_theo_imp_deriv", TheoImpDerivFigure),
        "theo_impedance": ("45", "look_at_theo_impedance", TheoImpFigure),
        "theo_back_imp": (
            "46",
            "look_at_theo_backwards_impedance",
            TheoBackwardsImpFigure,
        ),
        # Optimization
        "optimize_struc": ("50", "look_at_optimize_struc", OptimizeStrucFigure),
        # Comparisons
        "time_const_comparison": (
            "60",
            "look_at_time_const_comparison",
            TimeConstComparisonFigure,
        ),
        "struc_comparison": ("61", "look_at_struc_comparison", StrucComparisonFigure),
        "total_resist_comparison": (
            "62",
            "look_at_total_resist_comparison",
            TotalResistComparisonFigure,
        ),
        # Prediction and residuals
        "prediction": ("70", "look_at_prediction", PredictionFigure),
        "prediction_imp": (
            "71",
            "look_at_prediction_figure",
            PredictionImpulseUsedFigure,
        ),
        "residual": ("72", "look_at_residual", ResidualFigure),
        # Bootstrap (most advanced)
        "boot_impedance": ("80", "look_at_boot_impedance", BootZCurveFigure),
        "boot_deriv": ("81", "look_at_boot_deriv", BootDerivFigure),
        "boot_time_spec": ("82", "look_at_boot_time_spec", BootTimeSpecFigure),
        "boot_sum_time_spec": (
            "83",
            "look_at_boot_sum_time_spec",
            BootSumTimeSpecFigure,
        ),
        "boot_cumul_struc": ("84", "look_at_boot_cumul_struc", BootCumulStrucFigure),
    }

    def __init__(self, figures):
        """Keep a reference to the IOManager figure cache."""

        super().__init__()
        self.figures = figures
        self.module_fig_ops = {}

    def save_all_figures(self) -> None:
        """Persist every registered figure to a prefixed PNG file."""

        total = len(self.figures)
        saved = 0
        failed_keys = []

        for plot_key, fig_obj in self.figures.items():
            try:
                base_output_dir = fig_obj.output_dir
                module_label = fig_obj.module.label
                png_output_dir = os.path.join(base_output_dir, module_label, "png")
                os.makedirs(png_output_dir, exist_ok=True)

                prefix = "99"
                if plot_key in self.figure_registry:
                    prefix = self.figure_registry[plot_key][0]

                filename = os.path.join(png_output_dir, f"{prefix}_{plot_key}.png")

                fig_obj.add_legend()
                fig_obj.fig.savefig(filename, bbox_inches="tight", dpi=300)
                fig_obj.close()
                saved += 1

            except Exception as e:
                logger.error(f"Error saving figure '{plot_key}': {str(e)}")
                failed_keys.append(plot_key)
                continue

        if total == 0:
            logger.info("No figures to save")
        elif failed_keys:
            logger.info(
                "Saved %d/%d figures (failed: %s)",
                saved,
                total,
                ", ".join(failed_keys),
            )
        else:
            logger.info("Saved %d/%d figures", saved, total)

        import matplotlib.pyplot as plt

        plt.close("all")
        import gc

        gc.collect()

    def initialize_registered_figures(self, keys, module):
        """Ensure figures exist for ``keys`` and plot ``module`` data into them."""

        ops = self.module_fig_ops.setdefault(
            module.label, {"created": set(), "updated": set(), "skipped": set()}
        )

        for key in keys:
            if key in self.figure_registry:
                prefix, cond_attr, figure_class = self.figure_registry[key]
                condition = getattr(module, cond_attr, False)
                if condition:
                    plot_key = key
                    if plot_key not in self.figures:
                        fig_obj = figure_class(module)
                        self.figures[plot_key] = fig_obj
                        ops["created"].add(plot_key)
                    else:
                        fig_obj = self.figures[plot_key]
                        ops["updated"].add(plot_key)

                    try:
                        fig_obj.plot_module_data(module)
                    except Exception as e:
                        logger.error(
                            f"Error plotting data for module '{module.label}' on figure '{plot_key}': {str(e)}"
                        )

                else:
                    ops["skipped"].add(key)
            else:
                logger.error(f"Key '{key}' not found in figure registry")

    def log_module_summary(self, module_label: str):
        """Emit a single debug summary for the module's figure operations."""
        ops = self.module_fig_ops.pop(
            module_label, {"created": set(), "updated": set(), "skipped": set()}
        )
        if any(ops.values()):
            logger.debug(
                "Figure summary for '%s': created=%s updated=%s skipped=%s",
                module_label,
                sorted(ops["created"]) or "none",
                sorted(ops["updated"]) or "none",
                sorted(ops["skipped"]) or "none",
            )

    def extrapol_data_handler(self, module):
        """Plot extrapolated raw-data overlays."""

        self.initialize_registered_figures(["extrpl"], module)

    def voltage_data_handler(self, module):
        """Plot voltage-domain captures."""

        self.initialize_registered_figures(["voltage"], module)

    def temp_data_handler(self, module):
        """Plot both raw and processed temperature traces."""

        self.initialize_registered_figures(["raw", "temp"], module)

    def impedance_data_handler(self, module):
        """Plot impedance curves and their derivatives."""

        self.initialize_registered_figures(["impedance", "deriv"], module)

    def fft_data_handler(self, module):
        """Plot the FFT magnitude and window."""

        self.initialize_registered_figures(["fft"], module)

    def time_spec_data_handler(self, module):
        """Plot forward and backward time-spectrum figures."""

        self.initialize_registered_figures(
            ["time_spec", "sum_time_spec", "back_imp", "back_deriv"], module
        )

    def structure_function_data_handler(self, module):
        """Plot cumulative and local structure functions."""

        self.initialize_registered_figures(
            ["cumul_struc", "diff_struc", "local_resist", "local_gradient"], module
        )

    def theo_structure_function_data_handler(self, module):
        """Plot theoretical structure curves."""

        self.initialize_registered_figures(["theo_cstruc", "theo_diff_struc"], module)

    def theo_data_handler(self, module):
        """Plot theoretical impedance products."""

        self.initialize_registered_figures(
            [
                "theo_time_const",
                "theo_sum_time_const",
                "theo_imp_deriv",
                "theo_impedance",
            ],
            module,
        )

    def theo_compare_data_handler(self, module):
        """Plot backwards-theoretical comparisons."""

        self.initialize_registered_figures(["theo_back_imp"], module)

    def optimize_data_handler(self, module):
        """Plot optimisation overlays."""

        self.initialize_registered_figures(["optimize_struc"], module)

    def comparison_data_handler(self, module):
        """Plot module comparisons such as time constant or resistance deltas."""

        self.initialize_registered_figures(
            ["time_const_comparison", "struc_comparison", "total_resist_comparison"],
            module,
        )

    def prediction_data_handler(self, module):
        """Plot temperature and power predictions."""

        self.initialize_registered_figures(["prediction", "prediction_imp"], module)

    def residual_data_handler(self, module):
        """Plot residual histograms and fits."""

        self.initialize_registered_figures(["residual"], module)

    def boot_data_handler(self, module):
        """Plot bootstrap aggregates for every supported figure type."""

        self.initialize_registered_figures(
            [
                "boot_impedance",
                "boot_deriv",
                "boot_time_spec",
                "boot_sum_time_spec",
                "boot_cumul_struc",
            ],
            module,
        )
