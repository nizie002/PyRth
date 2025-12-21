"""Pytest configuration for evaluation tests."""

import pytest

from tests.test_transient_base import clean_output_root


@pytest.fixture(scope="session", autouse=True)
def _reset_output_dir():
    """Ensure the shared output directory is clean before the suite runs."""
    clean_output_root()
    yield
