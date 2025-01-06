import unittest
import numpy as np
from typing import Any


def standard_assertions(test_case: unittest.TestCase, module: Any) -> None:
    """Additional assertions for standard evaluation"""
    # Basic data attributes
    test_case.assertTrue(hasattr(module, "data"), "Missing data attribute")
    test_case.assertTrue(hasattr(module, "time"), "Missing time attribute")
    test_case.assertTrue(hasattr(module, "impedance"), "Missing impedance attribute")
    test_case.assertTrue(hasattr(module, "log_time"), "Missing log_time attribute")

    # time spectrum related attributes
    test_case.assertTrue(hasattr(module, "time_spec"), "Missing time_spec attribute")

    # Structure function results
    test_case.assertTrue(hasattr(module, "cau_res"), "Missing cau_res attribute")
    test_case.assertTrue(hasattr(module, "cau_cap"), "Missing cau_cap attribute")
    test_case.assertTrue(
        hasattr(module, "int_cau_res"), "Missing int_cau_res attribute"
    )
    test_case.assertTrue(
        hasattr(module, "int_cau_cap"), "Missing int_cau_cap attribute"
    )
    test_case.assertTrue(hasattr(module, "diff_struc"), "Missing diff_struc attribute")

    # Strict non-negativity checks for Cauer network
    test_case.assertTrue(
        np.all(module.cau_res >= 0),
        f"Cauer resistances contain negative values: {module.cau_res[module.cau_res < 0]}",
    )
    test_case.assertTrue(
        np.all(module.cau_cap >= 0),
        f"Cauer capacitances contain negative values: {module.cau_cap[module.cau_cap < 0]}",
    )

    # Data validation
    test_case.assertTrue(len(module.time) > 0, "Time array is empty")
    test_case.assertTrue(len(module.impedance) > 0, "Impedance array is empty")
    test_case.assertTrue(len(module.log_time) > 0, "Log time array is empty")
    test_case.assertTrue(len(module.time_spec) > 0, "Time spectrum is empty")

    # Result validation
    test_case.assertTrue(
        np.all(np.isfinite(module.impedance)),
        "Impedance contains non-finite values",
    )
    test_case.assertTrue(
        np.all(np.isfinite(module.time_spec)),
        "Time spectrum contains non-finite values",
    )
    test_case.assertTrue(
        np.all(np.isfinite(module.cau_res)),
        "Cauer resistances contain non-finite values",
    )
    test_case.assertTrue(
        np.all(np.isfinite(module.cau_cap)),
        "Cauer capacitances contain non-finite values",
    )
