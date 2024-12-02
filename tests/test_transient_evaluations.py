import unittest
from typing import List, Dict, Any
from parameterized import parameterized
import logging
import shutil
import os
from contextlib import contextmanager
import re
import numpy as np

import PyRth
from test_data import (
    test_cases_basic,
    test_cases_theoretical,
    test_cases_set,
    test_cases_bootstrap,
    test_cases_optimization,
)

logger = logging.getLogger("PyRthLogger")
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


@contextmanager
def log_to_file(log_file_path: str):
    logs_dir = os.path.join(os.path.dirname(log_file_path), "logs")
    os.makedirs(logs_dir, exist_ok=True)
    full_log_path = os.path.join(logs_dir, os.path.basename(log_file_path))

    logger = logging.getLogger("PyRthLogger")
    logger.setLevel(logging.DEBUG)

    # Remove existing handlers to avoid duplicates
    while logger.handlers:
        handler = logger.handlers.pop()
        handler.close()

    # Create a file handler for the log file
    fh = logging.FileHandler(full_log_path, mode="w")
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    try:
        yield
    finally:
        # Remove the handler after logging
        logger.removeHandler(fh)
        fh.close()


class TestTransientEvaluations(unittest.TestCase):
    test_cases_basic = test_cases_basic
    test_cases_theoretical = test_cases_theoretical
    test_cases_set = test_cases_set
    test_cases_bootstrap = test_cases_bootstrap
    test_cases_optimization = test_cases_optimization

    @classmethod
    def setUpClass(cls):
        # Clean up the entire tests/output directory before running any tests
        output_dir = "tests/output"
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir, exist_ok=True)  # Use os.makedirs

    def setUp(self):
        # Create specific output directories for each test
        for case_list in [self.test_cases_basic, self.test_cases_theoretical]:
            for case in case_list:
                output_dir = case["params"]["output_dir"]
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)

    def tearDown(self):
        # Optionally, clean up output directories after tests
        # Uncomment the following lines if you want to remove the output directories after each test
        # for case in self.test_cases:
        #     output_dir = case["params"]["output_dir"]
        #     if os.path.exists(output_dir):
        #         shutil.rmtree(output_dir)
        pass

    def _run_evaluation_test(
        self,
        name: str,
        params: Dict[str, Any],
        evaluation_method: str,
        additional_assertions: callable = None,
    ) -> None:
        """Helper method to run evaluation tests with common logic"""
        log_file_path = os.path.join(params["output_dir"], f"{name}.log")

        with log_to_file(log_file_path):
            try:
                # Perform evaluation
                eval_instance = PyRth.Evaluation()
                method = getattr(eval_instance, evaluation_method)
                modules = method(params)
                eval_instance.modules_output()
                eval_instance.save_all_figures(override_save=True)

                # Basic assertions
                self.assertTrue(modules, "Modules list is empty")

                # Run additional assertions if provided
                if additional_assertions:
                    for module in modules:
                        self.assertIn(module.label, eval_instance.modules)
                        additional_assertions(self, module)

            except Exception as e:
                logging.exception(f"Exception occurred during test '{name}': {e}")
                raise e

        # Check log file
        expected_log_path = os.path.join(params["output_dir"], "logs", f"{name}.log")
        self.assertTrue(
            os.path.exists(expected_log_path),
            f"Log file '{expected_log_path}' was not created.",
        )

        with open(expected_log_path, "r") as log_file:
            log_lines = log_file.readlines()
            error_pattern = re.compile(r"\b(ERROR|CRITICAL)\b")
            error_logs = [
                line.strip() for line in log_lines if error_pattern.search(line)
            ]
            has_error_logs = len(error_logs) > 0

        self.assertFalse(
            has_error_logs,
            f"Error level logs found in '{expected_log_path}':\n"
            + "\n".join(error_logs),
        )

    def _theoretical_assertions(
        self, test_case: unittest.TestCase, module: Any
    ) -> None:
        """Additional assertions for theoretical evaluation"""
        test_case.assertTrue(hasattr(module, "theo_log_time"))
        test_case.assertTrue(hasattr(module, "theo_delta"))
        test_case.assertTrue(hasattr(module, "theo_lengths"))
        test_case.assertTrue(hasattr(module, "theo_resistances"))
        test_case.assertTrue(hasattr(module, "theo_capacitances"))

    def _standard_assertions(self, test_case: unittest.TestCase, module: Any) -> None:
        """Additional assertions for standard evaluation"""
        # Basic data attributes
        test_case.assertTrue(hasattr(module, "data"), "Missing data attribute")
        test_case.assertTrue(hasattr(module, "time"), "Missing time attribute")
        test_case.assertTrue(
            hasattr(module, "impedance"), "Missing impedance attribute"
        )
        test_case.assertTrue(hasattr(module, "log_time"), "Missing log_time attribute")

        # time spectrum related attributes
        test_case.assertTrue(
            hasattr(module, "time_spec"), "Missing time_spec attribute"
        )

        # Structure function results
        test_case.assertTrue(hasattr(module, "cau_res"), "Missing cau_res attribute")
        test_case.assertTrue(hasattr(module, "cau_cap"), "Missing cau_cap attribute")
        test_case.assertTrue(
            hasattr(module, "int_cau_res"), "Missing int_cau_res attribute"
        )
        test_case.assertTrue(
            hasattr(module, "int_cau_cap"), "Missing int_cau_cap attribute"
        )
        test_case.assertTrue(
            hasattr(module, "diff_struc"), "Missing diff_struc attribute"
        )

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

    @parameterized.expand([(case["name"], case["params"]) for case in test_cases_basic])
    def test_standard_evaluation(self, name: str, params: Dict[str, Any]) -> None:
        """Test standard evaluation with different parameter sets"""
        self._run_evaluation_test(
            name, params, "standard_evaluation", self._standard_assertions
        )

    @parameterized.expand(
        [(case["name"], case["params"]) for case in test_cases_theoretical]
    )
    def test_theoretical_evaluation(self, name: str, params: Dict[str, Any]) -> None:
        """Test theoretical evaluation with different parameter sets"""
        self._run_evaluation_test(
            name, params, "add_theoretical_evaluation", self._theoretical_assertions
        )

    @parameterized.expand([(case["name"], case["params"]) for case in test_cases_set])
    def test_evaluation_set(self, name: str, params: Dict[str, Any]):
        self._run_evaluation_test(
            name, params, evaluation_method="standard_evaluation_set"
        )

    @parameterized.expand(
        [(case["name"], case["params"]) for case in test_cases_bootstrap]
    )
    def test_bootstrap_evaluation(self, name, params):
        self._run_evaluation_test(
            name=name, params=params, evaluation_method="bootstrap_evaluation"
        )

    @parameterized.expand(
        [(case["name"], case["params"]) for case in test_cases_optimization]
    )
    def test_optimization_evaluation(self, name, params):
        self._run_evaluation_test(
            name=name, params=params, evaluation_method="add_optimization_evaluation"
        )
