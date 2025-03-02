import numpy as np
from data.measurement_data import MOSFET_DRY_DATA, MOSFET_TIM_DATA, MOSFET_CALIB_DATA
from parameterized import parameterized
from test_transient_base import TransientTestBase
from assertions.standard_set_assertions import standard_set_assertions


test_cases_set = [
    {
        "name": f"bayesian_evaluation_set_bay_step",
        "params": {
            "data": MOSFET_DRY_DATA,
            "output_dir": "tests/output/set_test",
            "label": f"bayesian_evaluation_set_bay_step",
            "conv_mode": "volt",
            "bayesian": True,
            "bay_steps": [50, 1000, 10000],
            "iterable_keywords": ["bay_steps"],
            "evaluation_type": "standard",
            "calib": MOSFET_CALIB_DATA,
            "lower_fit_limit": 5e-4,
            "upper_fit_limit": 1e-3,
        },
    },
    {
        "name": f"optimization_evaluation_set_layers",
        "params": {
            "data": MOSFET_DRY_DATA,
            "output_dir": "tests/output/set_test",
            "label": f"optimization_evaluation_set_layers",
            "conv_mode": "volt",
            "iterable_keywords": ["opt_model_layers"],
            "opt_model_layers": [7, 8, 9],
            "evaluation_type": "optimization",
            "calib": MOSFET_CALIB_DATA,
            "lower_fit_limit": 5e-4,
            "upper_fit_limit": 1e-3,
            "opt_method": "Powell",
            "theo_time": [
                1e-8,
                5e2,
            ],
            "theo_time_size": 7500,
            "theo_delta": 1.5 * (2 * np.pi / 360),
        },
    },
    {
        "name": "standard_evaluation_set_gen_steps",
        "params": {
            "data": MOSFET_DRY_DATA,
            "output_dir": "tests/output/set_test",
            "label": "standard_evaluation_set_gen_steps",
            "conv_mode": "volt",
            "iterable_keywords": ["bay_steps"],
            "bay_steps": range(1000, 10001, 1000),
            "evaluation_type": "standard",
            "calib": MOSFET_CALIB_DATA,
            "lower_fit_limit": 5e-4,
            "upper_fit_limit": 1e-3,
        },
    },
    {
        "name": "standard_evaluation_set_gen_size",
        "params": {
            "data": MOSFET_DRY_DATA,
            "output_dir": "tests/output/set_test",
            "label": "standard_evaluation_set_gen_size",
            "conv_mode": "volt",
            "iterable_keywords": ["log_time_size"],
            "log_time_size": range(50, 251, 25),
            "evaluation_type": "standard",
            "calib": MOSFET_CALIB_DATA,
            "lower_fit_limit": 5e-4,
            "upper_fit_limit": 1e-3,
        },
    },
    {
        "name": "bootstrap_evaluation_set_from_data",
        "params": {
            "data": MOSFET_DRY_DATA,
            "output_dir": "tests/output/bootstrap_test",
            "label": "bootstrap_evaluation_set_from_data",
            "repetitions": 10,
            "bayesian": True,
            "iterable_keywords": ["log_time_size"],
            "log_time_size": range(300, 601, 100),
            "bay_steps": 1000,
            "evaluation_type": "bootstrap_standard",
            "bootstrap_mode": "from_data",
            "conv_mode": "volt",
            "calib": MOSFET_CALIB_DATA,
            "lower_fit_limit": 5e-4,
            "upper_fit_limit": 1e-3,
        },
    },
    {
        "name": "bootstrap_evaluation_set_from_theo",
        "params": {
            "output_dir": "tests/output/bootstrap_test",
            "label": "bootstrap_evaluation_set_from_theo",
            "repetitions": 2,
            "bayesian": True,
            "bay_steps": 1000,
            "iterable_keywords": ["signal_to_noise_ratio"],
            "bootstrap_mode": "from_theo",
            "signal_to_noise_ratio": range(10, 101, 50),
            "theo_time": [4e-8, 500],
            "evaluation_type": "bootstrap_optimization",
            "theo_time_size": 10000,
            "theo_delta": 2 * (2 * np.pi / 360),
            "theo_resistances": [10, 10, 10, 10, 10],
            "theo_capacitances": [1e-4, 1e-1, 1e-4, 1e-3, 1e0],
            "theo_inverse_specs": {
                "theo_time": [3e-7, 200],
                "theo_time_size": 30000,
                "theo_delta": 0.5 * (2 * np.pi / 360),
                "theo_resistances": [10, 10, 10, 10, 10],
                "theo_capacitances": [1e-4, 1e-1, 1e-4, 1e-3, 1e0],
            },
        },
    },
]


class TestStandardModuleSet(TransientTestBase):
    test_cases = test_cases_set

    @parameterized.expand([(case["name"], case["params"]) for case in test_cases])
    def test_standard_module_set(self, name: str, params: dict):
        self._run_evaluation_test(
            name,
            params,
            evaluation_module="standard_module_set",
            additional_assertions=standard_set_assertions,
        )
