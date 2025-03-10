import numpy as np
from parameterized import parameterized
from test_transient_base import TransientTestBase
from assertions.theoretical_assertions import theoretical_assertions

test_cases_theoretical = [
    {
        "name": "theoretical_case_1",
        "params": {
            "output_dir": "tests/output/theoretical_test",
            "label": "theoretical_case_1",
            "theo_time": [5e-9, 20],
            "theo_time_size": 10000,
            "theo_delta": 1.5 * (2 * np.pi / 360),
            "theo_resistances": [5, 15, 10, 10, 10],
            "theo_capacitances": [1e-5, 1e-3, 1e-4, 1e-2, 1e-1],
        },
    },
    {
        "name": "theoretical_case_2",
        "params": {
            "output_dir": "tests/output/theoretical_test",
            "label": "theoretical_case_2",
            "theo_time": [3e-7, 200],
            "theo_time_size": 30000,
            "theo_delta": 0.5 * (2 * np.pi / 360),
            "theo_resistances": [10, 10, 10, 10, 10],
            "theo_capacitances": [1e-4, 1e-1, 1e-4, 1e-3, 1e0],
        },
    },
    {
        "name": "theoretical_case_basic",
        "params": {
            "output_dir": "tests/output/theoretical_test",
            "label": "theoretical_case_basic",
            "theo_time": [5e-16, 0.02],
            "theo_time_size": 1000,
            "theo_delta": np.pi / 90,  # 2 degrees
            "theo_resistances": [0.1, 0.2, 0.3],
            "theo_capacitances": [1e-9, 1e-8, 1e-7],
        },
    },
    {
        "name": "theoretical_case_complex",
        "params": {
            "output_dir": "tests/output/theoretical_test",
            "label": "theoretical_case_complex",
            "theo_time": [5e-16, 0.02],
            "theo_time_size": 2000,
            "theo_delta": np.pi / 45,  # 4 degrees
            "theo_resistances": [0.1, 0.4, 0.3, 0.8, 0.5],
            "theo_capacitances": [1e-9, 2e-8, 1e-7, 2e-9, 1e-5],
        },
    },
]


class TestTheoreticalModule(TransientTestBase):
    test_cases = test_cases_theoretical

    @parameterized.expand([(case["name"], case["params"]) for case in test_cases])
    def test_theoretical_module(self, name: str, params: dict):
        self._run_evaluation_test(
            name,
            params,
            evaluation_module="theoretical_module",
            additional_assertions=theoretical_assertions,
        )
