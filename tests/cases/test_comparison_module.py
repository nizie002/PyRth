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
            "label": "MOSFET_dry_",
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
