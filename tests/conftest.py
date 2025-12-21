import pytest

from tests.test_transient_base import clean_output_root


@pytest.fixture(scope="session", autouse=True)
def _reset_output_dir():
    clean_output_root()
    yield
