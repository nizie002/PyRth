"""Shared helpers for running evaluation module tests with logging."""

import logging
import os
import re
import shutil
import sys
from collections.abc import Callable
from contextlib import contextmanager

logger = logging.getLogger("PyRthLogger")
logger.setLevel(logging.DEBUG)
logger.propagate = False
if not logger.handlers:
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(stream_handler)


@contextmanager
def log_to_file(log_file_path: str):
    """Log to both stdout and a per-test file."""
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


class _AssertHelper:
    """Lightweight assertion helpers so existing assertion modules can be reused."""

    def assertTrue(self, expr, msg: str | None = None) -> None:
        assert expr, msg or "Expected expression to be truthy"

    def assertFalse(self, expr, msg: str | None = None) -> None:
        assert not expr, msg or "Expected expression to be falsy"

    def assertIn(self, member, container, msg: str | None = None) -> None:
        assert member in container, msg or f"{member!r} not found in container"

    def assertIsInstance(self, obj, cls, msg: str | None = None) -> None:
        assert isinstance(obj, cls), msg or f"{obj!r} is not an instance of {cls}"

    def assertEqual(self, first, second, msg: str | None = None) -> None:
        assert first == second, msg or f"{first!r} != {second!r}"

    def assertGreater(self, a, b, msg: str | None = None) -> None:
        assert a > b, msg or f"Expected {a!r} to be greater than {b!r}"


ASSERT = _AssertHelper()


def clean_output_root() -> None:
    """Ensure a clean tests/output directory."""
    output_dir = "tests/output"
    if os.path.exists(output_dir):
        try:
            shutil.rmtree(output_dir)
        except PermissionError as e:
            # On Windows, files might still be locked. Try to handle gracefully
            import time
            import gc

            gc.collect()
            time.sleep(0.1)

            try:
                shutil.rmtree(output_dir)
            except PermissionError:
                logger.warning(
                    f"Could not remove {output_dir} due to permission error: {e}"
                )
                logger.warning("Continuing with existing directory...")

    os.makedirs(output_dir, exist_ok=True)


def run_evaluation_test(
    name: str,
    params: dict,
    evaluation_module: str,
    additional_assertions: Callable | None = None,
) -> None:
    """Execute an evaluation module with provided params and assertions."""
    output_dir = params.get("output_dir", "tests/output")
    os.makedirs(output_dir, exist_ok=True)
    log_file_path = os.path.join(output_dir, f"{name}.log")

    # Run evaluation inside log context
    with log_to_file(log_file_path):
        try:
            from PyRth import Evaluation

            eval_instance = Evaluation()
            method = getattr(eval_instance, evaluation_module)
            modules = method(params)
            eval_instance.save_as_csv()
            eval_instance.save_figures()

            if not isinstance(modules, list):
                modules = [modules]

            assert modules, "Modules list is empty"

            if additional_assertions:
                for module in modules:
                    assert module.label in eval_instance.modules
                    additional_assertions(ASSERT, module)

        except Exception as e:
            logger.exception(f"Exception during test '{name}': {e}")
            raise e

    expected_log_path = os.path.join(output_dir, "logs", f"{name}.log")
    assert os.path.exists(
        expected_log_path
    ), f"Log file '{expected_log_path}' was not created."

    with open(expected_log_path, "r") as log_file:
        log_lines = log_file.readlines()
        error_logs = [
            line.strip()
            for line in log_lines
            if re.search(r"\b(ERROR|CRITICAL)\b", line)
        ]
    assert not error_logs, (
        f"Error logs found in '{expected_log_path}':\n" + "\n".join(error_logs)
    )


__all__ = ["run_evaluation_test", "ASSERT", "logger", "clean_output_root"]
