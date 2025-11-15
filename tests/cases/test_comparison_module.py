import numpy as np
from tests.data.measurement_data import (
    MOSFET_DRY_DATA,
    MOSFET_TIM_DATA,
    MOSFET_CALIB_DATA,
)
from parameterized import parameterized
from test_transient_base import TransientTestBase
from assertions.comparison_assertions import comparison_assertions

test_cases_comparison = [
    {
        "name": "filter_range_comparison",
        "params": {
            "output_dir": "tests/output/comparison_test",
            "label": "filter_range_comparison",
            "filter_name": "hann",
            "deconv_mode": "fourier",
            "iterable_keywords": ["filter_range"],
            "filter_range": np.arange(0.1, 1.01, 0.1),
            "filter_parameter": 0.0,
            "pad_factor_pre": 0.15,
            "pad_factor_after": 0.15,
            "evaluation_type": "standard",
            "theo_inverse_specs": {
                "theo_time": [3e-7, 200],
                "theo_time_size": 30000,
                "theo_delta": 0.5 * (2 * np.pi / 360),
                "theo_resistances": [10, 10, 10, 10, 10],
                "theo_capacitances": [1e-4, 1e-1, 1e-4, 1e-3, 1e0],
            },
        },
    },
    {
        "name": "lasso_parameter_comparison",
        "params": {
            "output_dir": "tests/output/comparison_test",
            "label": "lasso_parameter_comparison",
            "deconv_mode": "lasso",
            "struc_method": "sobhy",
            "repetitions": 2000,
            "log_time_size": 75,
            "lasso_cv_folds": 5,
            "lasso_alpha": np.logspace(-5, -1, 5),
            "iterable_keywords": ["signal_to_noise_ratio"],
            "evaluation_type": "bootstrap_standard",
            "signal_to_noise_ratio": [25, 50, 75, 100, 150, 200, 350, 500, 750, 1000],
            "lasso_selection": "cyclic",
            "theo_inverse_specs": {
                "theo_time": [3e-7, 200],
                "theo_time_size": 10000,
                "theo_delta": 0.5 * (2 * np.pi / 360), 
                "theo_resistances": [10, 10, 10, 10, 10],
                "theo_capacitances": [1e-4, 1e-1, 1e-4, 1e-3, 1e0],
            },
        },
    },
    {
        "name": "adaptive_lasso_parameter_comparison",
        "params": {
            "output_dir": "tests/output/comparison_test",
            "label": "adaptive_lasso_parameter_comparison",
            "deconv_mode": "adaptive",
            "struc_method": "sobhy",
            "repetitions": 2000,
            "log_time_size": 75,
            "lasso_cv_folds": 5,
            "bay_steps": 10,
            "lasso_alpha": np.logspace(-5, -1, 5),
            "iterable_keywords": ["signal_to_noise_ratio"],
            "evaluation_type": "bootstrap_standard",
            "signal_to_noise_ratio": [25, 50, 75, 100, 150, 200, 350, 500, 750, 1000],
            "lasso_selection": "cyclic",
            "theo_inverse_specs": {
                "theo_time": [3e-7, 200],
                "theo_time_size": 10000,
                "theo_delta": 0.5 * (2 * np.pi / 360),
                "theo_resistances": [10, 10, 10, 10, 10],
                "theo_capacitances": [1e-4, 1e-1, 1e-4, 1e-3, 1e0],
            },
        },
    },
    {
        "name": "bayesian_parameter_comparison",
        "params": {
            "output_dir": "tests/output/comparison_test",
            "label": "bayesian_parameter_comparison",
            "deconv_mode": "bayesian",
            "struc_method": "sobhy",
            "repetitions": 2000,
            "lower_fit_limit": 3.3e-7,
            "upper_fit_limit": 7e-7,
            "iterable_keywords": ["signal_to_noise_ratio"],
            "evaluation_type": "bootstrap_standard",
            "signal_to_noise_ratio": [1000],
            # "signal_to_noise_ratio": [25, 50, 75, 100, 150, 200, 350, 500, 750, 1000],
            "theo_inverse_specs": {
                "theo_time": [3e-7, 200],
                "theo_time_size": 10000,
                "theo_delta": 0.5 * (2 * np.pi / 360),
                "theo_resistances": [10, 10, 10, 10, 10],
                "theo_capacitances": [1e-4, 1e-1, 1e-4, 1e-3, 1e0],
            },
        },
    },
]


class TestComparisonModule(TransientTestBase):
    test_cases = test_cases_comparison

    @parameterized.expand([(case["name"], case["params"]) for case in test_cases])
    def test_standard_module(self, name: str, params: dict):
        # 'standard_module' is the evaluation method specific to standard tests.
        self._run_evaluation_test(
            name,
            params,
            evaluation_module="comparison_module",
            additional_assertions=comparison_assertions,
        )
