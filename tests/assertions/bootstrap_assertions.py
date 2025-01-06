import unittest
import numpy as np
from typing import Any


def bootstrap_assertions(test_case: unittest.TestCase, module: Any) -> None:
    """Additional assertions for bootstrap evaluation"""
    # Basic bootstrap attributes
    test_case.assertTrue(hasattr(module, "repetitions"))
    test_case.assertTrue(hasattr(module, "bootstrap_results"))

    # Validate bootstrap results structure
    test_case.assertIsInstance(module.bootstrap_results, list)
    test_case.assertEqual(len(module.bootstrap_results), module.repetitions)

    # Check statistical properties
    for result in module.bootstrap_results:
        test_case.assertTrue(hasattr(result, "time_spec"))
        test_case.assertTrue(hasattr(result, "impedance"))
        test_case.assertTrue(np.all(np.isfinite(result.time_spec)))
        test_case.assertTrue(np.all(np.isfinite(result.impedance)))
