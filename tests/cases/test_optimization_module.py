import numpy as np
from tests.data.measurement_data import (
    MOSFET_DRY_DATA,
    MOSFET_TIM_DATA,
    MOSFET_CALIB_DATA,
)
from parameterized import parameterized
from test_transient_base import TransientTestBase
from assertions.optimization_assertions import optimization_assertions

test_cases_optimization = [
    {
        "name": "optimization_case_1",
        "params": {
            "data": MOSFET_DRY_DATA,
            "output_dir": "tests/output/optimization_test",
            "label": "optimization_case_1",
            "input_mode": "volt",
            "opt_model_layers": 10,
            "opt_method": "Powell",
            "calib": MOSFET_CALIB_DATA,
            "lower_fit_limit": 5e-4,
            "upper_fit_limit": 1e-3,
            "theo_time": [
                1e-8,
                5e2,
            ],  # range of the time for the theoretical model in seconds
            "theo_time_size": 10000,  # number of points in the time array for the theoretical model
            "theo_delta": 1.0
            * (
                2 * np.pi / 360
            ),  # angle to rotate Z(s) into the complex plane to avoid singularities (smaller is better, but makes peaks sharper)
        },
    },
    {
        "name": "optimization_case_2",
        "params": {
            "data": MOSFET_TIM_DATA,
            "output_dir": "tests/output/optimization_test",
            "label": "optimization_case_2",
            "input_mode": "volt",
            "opt_model_layers": 10,
            "opt_method": "COBYLA",
            "calib": MOSFET_CALIB_DATA,
            "lower_fit_limit": 5e-4,
            "upper_fit_limit": 1e-3,
            "theo_time": [
                1e-8,
                5e2,
            ],  # range of the time for the theoretical model in seconds
            "theo_time_size": 3000,  # number of points in the time array for the theoretical model
            "theo_delta": 2.0
            * (
                2 * np.pi / 360
            ),  # angle to rotate Z(s) into the complex plane to avoid singularities (smaller is better, but makes peaks sharper)
        },
    },
]


class TestOptimizationModule(TransientTestBase):
    test_cases = test_cases_optimization

    @parameterized.expand([(case["name"], case["params"]) for case in test_cases])
    def test_optimization_module(self, name: str, params: dict):
        self._run_evaluation_test(
            name,
            params,
            evaluation_module="optimization_module",
            additional_assertions=optimization_assertions,
        )
