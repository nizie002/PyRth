import unittest
from typing import Any


def standard_set_assertions(test_case: unittest.TestCase, module: Any) -> None:
    """Additional assertions for standard set evaluation"""
    # Check if the module has the set-specific attributes
    test_case.assertTrue(hasattr(module, "modules"), "Missing modules attribute")
    test_case.assertTrue(len(module.modules) > 0, "Modules list is empty")

    # Each sub-module should have basic attributes
    for sub_module in module.modules:
        test_case.assertTrue(hasattr(sub_module, "data"), "Missing data attribute")
        test_case.assertTrue(hasattr(sub_module, "time"), "Missing time attribute")
        test_case.assertTrue(
            hasattr(sub_module, "impedance"), "Missing impedance attribute"
        )
        test_case.assertTrue(hasattr(sub_module, "label"), "Missing label attribute")

        # Validate data arrays
        test_case.assertTrue(len(sub_module.time) > 0, "Time array is empty")
        test_case.assertTrue(len(sub_module.impedance) > 0, "Impedance array is empty")
