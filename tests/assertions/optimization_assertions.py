import unittest
import numpy as np
from typing import Any


def optimization_assertions(test_case: unittest.TestCase, module: Any) -> None:
    """Additional assertions for optimization evaluation"""
    # Basic optimization attributes
    test_case.assertTrue(hasattr(module, "opt_model"))
    test_case.assertTrue(hasattr(module, "opt_results"))
    test_case.assertTrue(hasattr(module, "opt_parameters"))

    # Optimization results validation
    test_case.assertTrue(hasattr(module.opt_results, "success"))
    test_case.assertTrue(hasattr(module.opt_results, "x"))
    test_case.assertTrue(hasattr(module.opt_results, "fun"))

    # Parameter validation
    test_case.assertTrue(np.all(np.isfinite(module.opt_parameters)))
    test_case.assertTrue(np.all(module.opt_parameters >= 0))
