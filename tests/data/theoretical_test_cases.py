import numpy as np

test_cases_theoretical = [
    {
        "name": "theoretical_case_1",
        "params": {
            "output_dir": "tests/output/theoretical_test",
            "label": "theoretical_case_1",
            "theo_log_time": [-10, 3],
            "theo_log_time_size": 10000,
            "theo_delta": 1.5 * (2 * np.pi / 360),
            "theo_lengths": [
                1e-2,
                1e-2,
                1e-2,
                1e-2,
                1e-2,
            ],
            "theo_resistances": [500, 1500, 1000, 1000, 1000],
            "theo_capacitances": [1e-3, 1e-1, 1e-2, 1e-0, 1e1],
        },
    },
    {
        "name": "theoretical_case_2",
        "params": {
            "output_dir": "tests/output/theoretical_test",
            "label": "theoretical_case_2",
            "theo_log_time": [-15, 5],
            "theo_log_time_size": 30000,
            "theo_delta": 0.5 * (2 * np.pi / 360),
            "theo_lengths": [
                1e-2,
                1e-2,
                1e-2,
                1e-2,
                1e-2,
            ],
            "theo_resistances": [1000, 1000, 1000, 1000, 1000],
            "theo_capacitances": [1e-2, 1e1, 1e-2, 1e-1, 1e2],
        },
    },
    {
        "name": "theoretical_case_basic",
        "params": {
            "output_dir": "tests/output/theoretical_test",
            "label": "theoretical_case_basic",
            "theo_log_time": [-10, 5],
            "theo_log_time_size": 1000,
            "theo_delta": np.pi / 90,  # 2 degrees
            "theo_lengths": [1e-3, 1e-3, 1e-3],
            "theo_resistances": [100, 200, 300],
            "theo_capacitances": [1e-6, 1e-5, 1e-4],
        },
    },
    {
        "name": "theoretical_case_complex",
        "params": {
            "output_dir": "tests/output/theoretical_test",
            "label": "theoretical_case_complex",
            "theo_log_time": [-15, 10],
            "theo_log_time_size": 2000,
            "theo_delta": np.pi / 45,  # 4 degrees
            "theo_lengths": [1e-3, 2e-3, 1e-3, 2e-3, 1e-3],
            "theo_resistances": [100, 200, 300, 400, 500],
            "theo_capacitances": [1e-6, 1e-5, 1e-4, 1e-3, 1e-2],
        },
    },
]
