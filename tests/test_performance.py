"""Performance monitoring parameterized cases."""

import pytest

from tests.data.measurement_data import (
    MOSFET_CALIB_DATA,
    MOSFET_TIM_DATA,
)

from tests.test_transient_base import run_evaluation_test

perf_cases = [
    {
        "name": "bayesian_sobhy_perf_monitor",
        "params": {
            "data": MOSFET_TIM_DATA,
            "output_dir": "tests/output/basic_test",
            "label": "bayesian_sobhy_perf_monitor",
            "input_mode": "volt",
            "deconv_mode": "bayesian",
            "bay_steps": 1000,
            "struc_method": "sobhy",
            "calib": MOSFET_CALIB_DATA,
            "lower_fit_limit": 5e-4,
            "upper_fit_limit": 1e-3,
            "perf_eval": True,
        },
    }
]


def perf_assertions(assertions, module):
    """Assertions for performance monitoring."""
    spans = getattr(getattr(module, "perf_monitor", None), "spans", lambda: [])()
    assertions.assertTrue(len(spans) > 0, "Expected perf spans when perf_eval is enabled")
    names = [name for name, _ in spans]
    assertions.assertIn("make_z", names, "make_z should be timed")


@pytest.mark.parametrize("case", perf_cases, ids=lambda case: case["name"])
def test_perf_monitor(case):
    """Run perf-enabled standard_module and check spans."""
    run_evaluation_test(
        name=case["name"],
        params=case["params"],
        evaluation_module="standard_module",
        additional_assertions=perf_assertions,
    )
