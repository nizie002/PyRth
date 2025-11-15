"""Central dispatcher coordinating CSV and figure exporters."""

import logging

from .transient_csv_exporter import CSVExporter
from .transient_figure_exporter import FigureExporter
from .transient_base_exporter import BaseExporter

logger = logging.getLogger("PyRthLogger")


class IOManager:
    """Orchestrate which exporter handles which module artefacts."""

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
        """Run each module through the handlers supported by ``exporter``."""
        logger.info("Saving output data")

        for module in self.modules.values():
            logger.debug(
                f"Processing {exporter.type} output for Module {module.label} capabilities: {module.data_handlers}"
            )

            capabilities = getattr(module, "data_handlers", [])

            for capability in capabilities:
                if capability in self.handlers:
                    logger.debug(f"Executing {capability} data handler")
                    try:
                        getattr(exporter, self.handlers[capability])(module)
                    except (AttributeError, ValueError, RuntimeError) as e:
                        logger.error(f"Error in {capability} data handler: {str(e)}")
                else:
                    logger.error(f"Handler {capability} not found")

    def export_csv(self):
        """Trigger CSV exporter for every module."""
        self.exporter_output(self.csv_exporter)

    def export_figures(self):
        """Trigger figure exporter for every module and flush to disk."""
        self.exporter_output(self.figure_exporter)
        self.figure_exporter.save_all_figures()

    def export_all(self):
        """Run CSV and figure exporters sequentially."""
        self.export_csv()
        self.export_figures()
