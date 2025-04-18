import numpy as np
from tests.data.measurement_data import (
    MOSFET_DRY_DATA,
    MOSFET_TIM_DATA,
    MOSFET_CALIB_DATA,
)
from parameterized import parameterized
from test_transient_base import TransientTestBase
from assertions.bootstrap_assertions import bootstrap_assertions

test_cases_bootstrap = [
    {
        "name": "bootstrap_evaluation_from_theo",
        "params": {
            "output_dir": "tests/output/bootstrap_test",
            "label": "bootstrap_evaluation_from_theo",
            "repetitions": 10,
            "bayesian": True,
            "bay_steps": 100,
            "bootstrap_mode": "from_theo",
            "evaluation_type": "bootstrap_standard",
            "signal_to_noise_ratio": 50,
            "theo_time": [4e-8, 500],
            "theo_time_size": 10000,
            "theo_delta": 2 * (2 * np.pi / 360),
            "theo_resistances": [10, 10, 10, 10, 10],
            "theo_capacitances": [1e-4, 1e-1, 1e-4, 1e-3, 1e0],
        },
    },
    {
        "name": "bootstrap_evaluation_from_data",
        "params": {
            "data": MOSFET_DRY_DATA,
            "output_dir": "tests/output/bootstrap_test",
            "label": "bootstrap_evaluation_from_data",
            "repetitions": 10,
            "bayesian": True,
            "bay_steps": 1000,
            "bootstrap_mode": "from_data",
            "evaluation_type": "bootstrap_standard",
            "conv_mode": "volt",
            "calib": MOSFET_CALIB_DATA,
            "lower_fit_limit": 5e-4,
            "upper_fit_limit": 1e-3,
        },
    },
]


class TestBootstrapModule(TransientTestBase):
    test_cases = test_cases_bootstrap

    @parameterized.expand([(case["name"], case["params"]) for case in test_cases])
    def test_bootstrap_module(self, name: str, params: dict):
        self._run_evaluation_test(
            name,
            params,
            evaluation_module="bootstrap_module",
            additional_assertions=bootstrap_assertions,
        )
