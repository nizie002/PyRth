"""Base exporter class providing common functionality for all exporters.
"""
import logging

logger = logging.getLogger("PyRthLogger")

class BaseExporter:
    """
    Base exporter class providing common functionality for all exporters.
    """

    type = "base"

    def voltage_data_handler(self, module):
        "dummy data handler"

    def temp_data_handler(self, module):
        "dummy data handler"

    def impedance_data_handler(self, module):
        "dummy data handler"

    def fft_data_handler(self, module):
        "dummy data handler"

    def time_spec_data_handler(self, module):
        "dummy data handler"

    def structure_function_data_handler(self, module):
        "dummy data handler"

    def theo_structure_function_data_handler(self, module):
        "dummy data handler"

    def theo_data_handler(self, module):
        "dummy data handler"

    def theo_compare_data_handler(self, module):
        "dummy data handler"

    def optimize_data_handler(self, module):
        "dummy data handler"

    def comparison_data_handler(self, module):
        "dummy data handler"

    def prediction_data_handler(self, module):
        "dummy data handler"

    def residual_data_handler(self, module):
        "dummy data handler"

    def boot_data_handler(self, module):
        "dummy data handler"
