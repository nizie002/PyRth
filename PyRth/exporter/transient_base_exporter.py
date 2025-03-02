import os
import logging

logger = logging.getLogger("PyRthLogger")


class BaseExporter:
    """
    Base exporter class providing common functionality for all exporters.
    """

    type = "base"

    def voltage_data_handler(self, module):
        "dummy data handler"
        pass

    def temp_data_handler(self, module):
        "dummy data handler"
        pass

    def impedance_data_handler(self, module):
        "dummy data handler"
        pass

    def fft_data_handler(self, module):
        "dummy data handler"
        pass

    def time_spec_data_handler(self, module):
        "dummy data handler"
        pass

    def structure_function_data_handler(self, module):
        "dummy data handler"
        pass

    def theo_structure_function_data_handler(self, module):
        "dummy data handler"
        pass

    def theo_data_handler(self, module):
        "dummy data handler"
        pass

    def theo_compare_data_handler(self, module):
        "dummy data handler"
        pass

    def optimize_data_handler(self, module):
        "dummy data handler"
        pass

    def comparison_data_handler(self, module):
        "dummy data handler"
        pass

    def prediction_data_handler(self, module):
        "dummy data handler"
        pass

    def residual_data_handler(self, module):
        "dummy data handler"
        pass

    def boot_data_handler(self, module):
        "dummy data handler"
        pass
