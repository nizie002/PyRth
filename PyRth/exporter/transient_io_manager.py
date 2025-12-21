"""Central dispatcher coordinating CSV and figure exporters.

``IOManager`` is the glue between the evaluation façade in
``transient_scripts.py`` and the concrete exporter implementations.  Each
``Evaluation`` method populates ``modules`` with ``StructureFunction``
instances plus their requested ``data_handlers``.  ``IOManager`` inspects those
handler flags, routes them to :mod:`PyRth.exporter.transient_csv_exporter`
or :mod:`PyRth.exporter.transient_figure_exporter`, and the latter in turn
instantiates the figure subclasses declared in
``PyRth.exporter.transient_figures``.  When users run multiple evaluations or a
module set, every module is stored under a unique label; exporting iterates the
entire mapping, so CSV/PNG artifacts are emitted for each module and each
handler without collisions.  This keeps the public API in ``transient_scripts``
simple—callers only flip handler flags—and still yields a full suite of outputs
per evaluation run, even when dozens of modules are queued.
"""

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
        saved_files = []
        failed = []

        for module in self.modules.values():
            logger.debug(
                f"Processing {exporter.type} output for Module {module.label} capabilities: {module.data_handlers}"
            )

            capabilities = getattr(module, "data_handlers", [])

            for capability in capabilities:
                if capability in self.handlers:
                    try:
                        result = getattr(exporter, self.handlers[capability])(module)
                        if exporter.type == "DataExporter" and result is not None:
                            if isinstance(result, list):
                                saved_files.extend([path for path in result if path])
                            elif result:
                                saved_files.append(result)
                    except (AttributeError, ValueError, RuntimeError) as e:
                        logger.error(f"Error in {capability} data handler: {str(e)}")
                        failed.append((module.label, capability))
                else:
                    logger.error(f"Handler {capability} not found")
                    failed.append((module.label, capability))

            if exporter.type == "figure" and hasattr(exporter, "log_module_summary"):
                exporter.log_module_summary(module.label)

        if exporter.type == "DataExporter":
            total = len(saved_files)
            if failed:
                failed_desc = ", ".join([f"{mod}:{cap}" for mod, cap in failed])
                logger.info(
                    "Saved %d CSV file(s); %d handler(s) failed (%s)",
                    total,
                    len(failed),
                    failed_desc,
                )
            else:
                logger.info("Saved %d CSV file(s)", total)

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
