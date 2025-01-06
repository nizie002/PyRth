import numpy as np
from data.measurement_data import MOSFET_DRY_DATA, MOSFET_TIM_DATA

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
            "signal_to_noise_ratio": 50,
            "theo_log_time": [-17, 10],
            "theo_log_time_size": 10000,
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
            "bay_steps": 100,
            "bootstrap_mode": "from_data",
            "signal_to_noise_ratio": 100,
            "conv_mode": "TDIM",
        },
    },
]
