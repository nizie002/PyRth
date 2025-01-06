import numpy as np
from data.measurement_data import MOSFET_DRY_DATA, MOSFET_TIM_DATA

test_cases_set = [
    {
        "name": f"bayesian_evaluation_set_bay_step",
        "params": {
            "data": MOSFET_DRY_DATA,
            "output_dir": "tests/output/set_test",
            "label": f"bayesian_evaluation_set_bay_step",
            "conv_mode": "TDIM",
            "bayesian": True,
            "bay_steps": [50, 1000, 10000],
            "iterable_keywords": ["bay_steps"],
            "evaluation_type": "standard",
        },
    }
]
