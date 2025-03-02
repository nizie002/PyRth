import unittest
from typing import Any


def standard_set_assertions(test_case: unittest.TestCase, module: Any) -> None:
    """Additional assertions for standard set evaluation"""
    # When using standard_module_set, the module itself might be part of a list
    if isinstance(module, list):
        for sub_module in module:
            _assert_module_structure(test_case, sub_module)
    else:
        _assert_module_structure(test_case, module)


def _assert_module_structure(test_case: unittest.TestCase, module: Any) -> None:
    """Assert the structure of a single module"""
    # Check basic required attributes
    test_case.assertTrue(hasattr(module, "data"), "Missing data attribute")
    test_case.assertTrue(
        hasattr(module, "time") or hasattr(module, "theo_log_time"),
        "Missing time attribute",
    )
    test_case.assertTrue(
        hasattr(module, "impedance") or hasattr(module, "theo_impedance"),
        "Missing impedance attribute",
    )
    test_case.assertTrue(hasattr(module, "label"), "Missing label attribute")
