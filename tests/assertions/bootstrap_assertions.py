import unittest
import numpy as np
from typing import Any


def bootstrap_assertions(test_case: unittest.TestCase, module: Any) -> None:
    """Additional assertions for bootstrap evaluation."""

    # Bootstrap configuration assertions
    test_case.assertTrue(hasattr(module, "repetitions"), "Module missing 'repetitions'")
    test_case.assertTrue(
        hasattr(module, "boot_results_imp"), "Module missing 'boot_results_imp'"
    )
    test_case.assertTrue(
        hasattr(module, "boot_results_deriv"), "Module missing 'boot_results_deriv'"
    )
    test_case.assertTrue(
        hasattr(module, "boot_results_timeconst"),
        "Module missing 'boot_results_timeconst'",
    )
    test_case.assertTrue(
        hasattr(module, "boot_results_sum_timeconst"),
        "Module missing 'boot_results_sum_timeconst'",
    )

    # Type and shape assertions for bootstrap results
    test_case.assertIsInstance(
        module.boot_results_imp, np.ndarray, "'boot_results_imp' is not a numpy array"
    )
    test_case.assertEqual(
        module.boot_results_imp.shape[0],
        module.repetitions,
        "The first dimension of 'boot_results_imp' does not match 'repetitions'",
    )

    test_case.assertIsInstance(
        module.boot_results_deriv,
        np.ndarray,
        "'boot_results_deriv' is not a numpy array",
    )
    test_case.assertEqual(
        module.boot_results_deriv.shape[0],
        module.repetitions,
        "The first dimension of 'boot_results_deriv' does not match 'repetitions'",
    )

    test_case.assertIsInstance(
        module.boot_results_timeconst,
        np.ndarray,
        "'boot_results_timeconst' is not a numpy array",
    )
    test_case.assertEqual(
        module.boot_results_timeconst.shape[0],
        module.repetitions,
        "The first dimension of 'boot_results_timeconst' does not match 'repetitions'",
    )

    test_case.assertIsInstance(
        module.boot_results_sum_timeconst,
        np.ndarray,
        "'boot_results_sum_timeconst' is not a numpy array",
    )
    test_case.assertEqual(
        module.boot_results_sum_timeconst.shape[0],
        module.repetitions,
        "The first dimension of 'boot_results_sum_timeconst' does not match 'repetitions'",
    )
