import numpy as np
from data.measurement_data import MOSFET_DRY_DATA, MOSFET_TIM_DATA

test_cases_optimization = [
    {
        "name": "optimization_case_1",
        "params": {
            "data": MOSFET_DRY_DATA,
            "output_dir": "tests/output/optimization_test",
            "label": "optimization_case_1",
            "conv_mode": "TDIM",
            "opt_model_layers": 5,
            "opt_method": "Powell",
        },
    },
    {
        "name": "optimization_case_2",
        "params": {
            "data": MOSFET_TIM_DATA,
            "output_dir": "tests/output/optimization_test",
            "label": "optimization_case_2",
            "conv_mode": "TDIM",
            "opt_model_layers": 10,
            "opt_method": "COBYLA",
        },
    },
]
