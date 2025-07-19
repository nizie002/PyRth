import os
import logging


from .transient_base_exporter import BaseExporter

# Import figure classes (ensure path is correct)
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

    type = "figure"

    # Combined figure registry with prefixes for ordering
    # Format: key: (prefix, condition_attribute, figure_class)
    # Ordered from basic input data (00) to advanced results (highest numbers)
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
        super().__init__()
        # figures is the dictionary managed by IOManager, passed by reference
        self.figures = figures  # Stores StructureFigure instances keyed by plot type (e.g., "impedance")

    def save_all_figures(self) -> None:
        """Save all figures (one per plot type) to PNG files."""

        logger.info("Saving figures")
        logger.debug(f"Number of figures to save: {len(self.figures)}")

        # Key is plot type (e.g., "impedance"), fig_obj is StructureFigure instance
        for plot_key, fig_obj in self.figures.items():
            try:
                # Use output_dir from the initial module stored in fig_obj
                base_output_dir = fig_obj.output_dir
                module_label = (
                    fig_obj.module.label
                )  # Get the label from the stored module
                png_output_dir = os.path.join(base_output_dir, module_label, "png")
                # Ensure the png output directory exists
                os.makedirs(png_output_dir, exist_ok=True)

                # Get prefix for ordering, default to "99" if not found
                prefix = "99"  # default fallback
                if plot_key in self.figure_registry:
                    prefix = self.figure_registry[plot_key][
                        0
                    ]  # First element is the prefix

                # Filename with prefix for sorting (e.g., "00_raw.png", "10_impedance.png")
                filename = os.path.join(png_output_dir, f"{prefix}_{plot_key}.png")

                fig_obj.add_legend()  # Add legend just before saving
                fig_obj.fig.savefig(
                    filename, bbox_inches="tight", dpi=300
                )  # Use bbox_inches='tight' and increased dpi
                fig_obj.close()  # Close the figure object
                logger.debug(f"Figure '{plot_key}' saved successfully to {filename}.")

            except Exception as e:
                logger.error(f"Error saving figure '{plot_key}': {str(e)}")
                # Optionally re-raise or handle more gracefully
                continue  # Continue with the next figure

        # Additional cleanup to ensure all matplotlib figures are closed
        import matplotlib.pyplot as plt

        plt.close("all")
        import gc

        gc.collect()  # Force garbage collection to free any remaining handles

    def initialize_registered_figures(self, keys, module):
        """Get or create figure object for key and plot module data."""
        for key in keys:
            if key in self.figure_registry:
                prefix, cond_attr, figure_class = self.figure_registry[
                    key
                ]  # Unpack 3-element tuple
                # Check if the module instance has the condition attribute and it's True
                condition = getattr(module, cond_attr, False)
                if condition:
                    plot_key = key  # e.g., "impedance"
                    if plot_key not in self.figures:
                        # Figure doesn't exist for this plot type, create it
                        logger.debug(
                            f"Creating figure for key '{plot_key}' using module '{module.label}'"
                        )
                        # Create the StructureFigure instance using the current module for context
                        fig_obj = figure_class(module)
                        # Store it in the shared dictionary using the plot_key
                        self.figures[plot_key] = fig_obj
                    else:
                        # Figure already exists, retrieve it
                        logger.debug(
                            f"Adding data from module '{module.label}' to existing figure '{plot_key}'"
                        )
                        fig_obj = self.figures[plot_key]

                    # Plot data for the current module onto the figure's axes
                    try:
                        fig_obj.plot_module_data(module)
                    except Exception as e:
                        logger.error(
                            f"Error plotting data for module '{module.label}' on figure '{plot_key}': {str(e)}"
                        )

                else:
                    # Log if the condition to plot is not met for this module
                    logger.debug(
                        f"Condition '{cond_attr}' for key '{key}' not met for module '{module.label}'."
                    )
            else:
                # Log error if the key is not found in the registry
                logger.error(f"Key '{key}' not found in figure registry")

    # --- Data Handlers remain structurally the same ---
    # They simply call initialize_registered_figures with the relevant keys

    def extrapol_data_handler(self, module):
        logger.debug("extrapol_data_handler called")
        self.initialize_registered_figures(["extrpl"], module)

    def voltage_data_handler(self, module):
        logger.debug("voltage_data_handler called")
        self.initialize_registered_figures(["voltage"], module)

    def temp_data_handler(self, module):
        logger.debug("temp_data_handler called")
        self.initialize_registered_figures(["raw", "temp"], module)

    def impedance_data_handler(self, module):
        logger.debug("impedance_data_handler called")
        self.initialize_registered_figures(["impedance", "deriv"], module)

    def fft_data_handler(self, module):
        logger.debug("fft_data_handler called")
        self.initialize_registered_figures(["fft"], module)

    def time_spec_data_handler(self, module):
        logger.debug("time_spec_data_handler called")
        self.initialize_registered_figures(
            ["time_spec", "sum_time_spec", "back_imp", "back_deriv"], module
        )

    def structure_function_data_handler(self, module):
        logger.debug("structure_function_data_handler called")
        self.initialize_registered_figures(
            ["cumul_struc", "diff_struc", "local_resist", "local_gradient"], module
        )

    def theo_structure_function_data_handler(self, module):
        logger.debug("theo_structure_function_data_handler called")
        self.initialize_registered_figures(["theo_cstruc", "theo_diff_struc"], module)

    def theo_data_handler(self, module):
        logger.debug("theo_data_handler called")
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
        logger.debug("theo_compare_data_handler called")
        self.initialize_registered_figures(["theo_back_imp"], module)

    def optimize_data_handler(self, module):
        logger.debug("optimize_data_handler called")
        self.initialize_registered_figures(["optimize_struc"], module)

    def comparison_data_handler(self, module):
        logger.debug("comparison_data_handler called")
        # Comparison figures likely plot aggregated results, check if they need module-specific data
        # Assuming they plot summary data from the 'module' passed (which might be a results_module)
        self.initialize_registered_figures(
            ["time_const_comparison", "struc_comparison", "total_resist_comparison"],
            module,
        )

    def prediction_data_handler(self, module):
        logger.debug("prediction_data_handler called")
        self.initialize_registered_figures(["prediction", "prediction_imp"], module)

    def residual_data_handler(self, module):
        logger.debug("residual_data_handler called")
        self.initialize_registered_figures(["residual"], module)

    def boot_data_handler(self, module):
        logger.debug("boot_data_handler called")
        # Bootstrapping figures usually show aggregated results (median, percentiles)
        # The current logic assumes the 'module' passed contains these aggregated results.
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
