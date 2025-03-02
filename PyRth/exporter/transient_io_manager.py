import numpy as np
import logging
import os

from .transient_csv_exporter import CSVExporter
from .transient_figure_exporter import FigureExporter
from .transient_base_exporter import BaseExporter

logger = logging.getLogger("PyRthLogger")


class IOManager:

    handlers = {
        "volt": "voltage_data_handler",
        "temp": "temp_data_handler",
        "impedance": "impedance_data_handler",
        "extrpl": "extrapol_data_handler",
        "time_spec": "time_spec_data_handler",
        "structure": "structure_function_data_handler",
        "fft": "fft_data_handler",
        "theo_structure": "theo_structure_function_data_handler",
        "theo": "theo_data_handler",
        "theo_compare": "theo_compare_data_handler",
        "optimize": "optimize_data_handler",
        "comparison": "comparison_data_handler",
        "prediction": "prediction_data_handler",
        "residual": "residual_data_handler",
        "boot": "boot_data_handler",
    }

    def __init__(self, modules):
        self.modules = modules
        self.figures = {}

        self.csv_exporter = CSVExporter()
        self.figure_exporter = FigureExporter(self.figures)

    def exporter_output(self, exporter: BaseExporter):
        """Process output data for all modules based on their capabilities."""
        logger.info("Saving output data")

        for key, module in self.modules.items():
            logger.debug(
                f"Processing {exporter.type} output for Module {module.label} capabilities: {module.data_handlers}"
            )

            # Get module's capabilities (defined in module class)
            capabilities = getattr(module, "data_handlers", [])

            # Call each available handler
            for capability in capabilities:
                if capability in self.handlers:
                    logger.debug(f"Executing {capability} data handler")
                    try:
                        getattr(exporter, self.handlers[capability])(module)
                    except Exception as e:
                        logger.error(f"Error in {capability} data handler: {str(e)}")
                else:
                    logger.error(f"Handler {capability} not found")

    def export_csv(self):
        """Export data for all modules."""
        self.exporter_output(self.csv_exporter)

    def export_figures(self):
        """Export figures for all modules."""
        self.exporter_output(self.figure_exporter)
        self.figure_exporter.save_all_figures()

    def export_all(self):
        """Export all data and figures for all modules."""
        self.export_csv()
        self.export_figures()
