import os
import re
import shutil
import unittest
import logging
from contextlib import contextmanager

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

    log_hdl = logging.FileHandler(full_log_path, mode="w")
    log_hdl.setLevel(logging.DEBUG)
    log_hdl.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(log_hdl)

    try:
        yield
    finally:
        logger.removeHandler(log_hdl)
        log_hdl.close()


class TransientTestBase(unittest.TestCase):
    # Each subclass can override test_cases with its own category.
    test_cases = []

    @classmethod
    def setUpClass(cls):
        output_dir = "tests/output"
        if os.path.exists(output_dir):
            try:
                shutil.rmtree(output_dir)
            except PermissionError as e:
                # On Windows, files might still be locked. Try to handle gracefully
                import time
                import gc
                
                # Force garbage collection to close any remaining file handles
                gc.collect()
                time.sleep(0.1)  # Brief pause
                
                try:
                    shutil.rmtree(output_dir)
                except PermissionError:
                    logger.warning(f"Could not remove {output_dir} due to permission error: {e}")
                    logger.warning("Continuing with existing directory...")
        
        os.makedirs(output_dir, exist_ok=True)

    def _run_evaluation_test(
        self,
        name: str,
        params: dict,
        evaluation_module: str,
        additional_assertions: callable = None,
    ) -> None:
        output_dir = params.get("output_dir", "tests/output")
        os.makedirs(output_dir, exist_ok=True)
        log_file_path = os.path.join(output_dir, f"{name}.log")

        # Run evaluation inside log context
        with log_to_file(log_file_path):
            try:
                # The evaluation call should be customized per category.
                # For example: PyRth.Evaluation(), followed by evaluation_module (a method name)
                from PyRth import Evaluation

                eval_instance = Evaluation()
                method = getattr(eval_instance, evaluation_module)
                modules = method(params)
                eval_instance.save_as_csv()
                eval_instance.save_figures()

                if not isinstance(modules, list):
                    modules = [modules]

                self.assertTrue(modules, "Modules list is empty")

                if additional_assertions:
                    for module in modules:
                        self.assertIn(module.label, eval_instance.modules)
                        additional_assertions(self, module)

            except Exception as e:
                logger.exception(f"Exception during test '{name}': {e}")
                raise e

        expected_log_path = os.path.join(output_dir, "logs", f"{name}.log")
        self.assertTrue(
            os.path.exists(expected_log_path),
            f"Log file '{expected_log_path}' was not created.",
        )

        with open(expected_log_path, "r") as log_file:
            log_lines = log_file.readlines()
            error_logs = [
                line.strip()
                for line in log_lines
                if re.search(r"\b(ERROR|CRITICAL)\b", line)
            ]
        self.assertFalse(
            len(error_logs) > 0,
            f"Error logs found in '{expected_log_path}':\n" + "\n".join(error_logs),
        )
