import unittest
import numpy as np
from typing import Any


def optimization_assertions(test_case: unittest.TestCase, module: Any) -> None:
    """Additional assertions for optimization evaluation."""

    # Check that the final resistance and capacitance arrays exist and are non-empty numpy arrays.
    test_case.assertTrue(
        hasattr(module, "fin_res"), "Module missing attribute 'fin_res'"
    )
    test_case.assertIsInstance(
        module.fin_res, np.ndarray, "'fin_res' should be a numpy array"
    )
    test_case.assertGreater(module.fin_res.size, 0, "'fin_res' must not be empty")

    test_case.assertTrue(
        hasattr(module, "fin_cap"), "Module missing attribute 'fin_cap'"
    )
    test_case.assertIsInstance(
        module.fin_cap, np.ndarray, "'fin_cap' should be a numpy array"
    )
    test_case.assertGreater(module.fin_cap.size, 0, "'fin_cap' must not be empty")

    # Check that the differences (if computed) are available.
    test_case.assertTrue(
        hasattr(module, "fin_res_diff"), "Module missing attribute 'fin_res_diff'"
    )
    test_case.assertTrue(
        hasattr(module, "fin_cap_diff"), "Module missing attribute 'fin_cap_diff'"
    )

    # Verify that structure function related outputs exist.
    test_case.assertTrue(
        hasattr(module, "theo_int_cau_res"),
        "Module missing attribute 'theo_int_cau_res'",
    )
    test_case.assertTrue(
        hasattr(module, "theo_int_cau_cap"),
        "Module missing attribute 'theo_int_cau_cap'",
    )
    test_case.assertTrue(
        hasattr(module, "theo_diff_struc"), "Module missing attribute 'theo_diff_struc'"
    )
    test_case.assertTrue(
        hasattr(module, "theo_time_const"), "Module missing attribute 'theo_time_const'"
    )
    test_case.assertTrue(
        hasattr(module, "theo_imp_deriv"), "Module missing attribute 'theo_imp_deriv'"
    )
    test_case.assertTrue(
        hasattr(module, "theo_impedance"), "Module missing attribute 'theo_impedance'"
    )

    # Inspect that required data handlers were set.
    required_handlers = ["theo_structure", "theo", "theo_compare", "optimize"]
    for handler in required_handlers:
        test_case.assertIn(
            handler,
            module.data_handlers,
            f"Data handler '{handler}' should be in module.data_handlers",
        )

    # Optionally, validate that the theoretical impedance derivative contains reasonable values.
    test_case.assertTrue(
        np.all(np.isfinite(module.theo_imp_deriv)),
        "Non-finite values found in 'theo_imp_deriv'",
    )
