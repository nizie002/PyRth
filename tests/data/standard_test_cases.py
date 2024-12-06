import numpy as np
from data.measurement_data import MOSFET_DRY_DATA, MOSFET_TIM_DATA

test_cases_basic = [
    {
        "name": "MOSTFET_dry_basic_fft",
        "params": {
            "data": MOSFET_DRY_DATA,
            "output_dir": "tests/output/basic_test",
            "label": "MOSTFET_dry_basic_fft",
            "conv_mode": "TDIM",
            "filter_name": "hann",
            "filter_range": 0.60,
            "filter_parameter": 0.0,
            "pad_factor_pre": 0.15,
            "pad_factor_after": 0.15,
            "ASDASDSA": "asdasd",
        },
    },
    {
        "name": "MOSTFET_tim_basic_bayesian",
        "params": {
            "data": MOSFET_TIM_DATA,
            "output_dir": "tests/output/basic_test",
            "label": "MOSTFET_tim_basic_bayesian",
            "conv_mode": "TDIM",
            "bayesian": True,
            "bay_steps": 1000,
        },
    },
    {
        "name": "MOSTFET_tim_basic_polylong",
        "params": {
            "data": MOSFET_TIM_DATA,
            "output_dir": "tests/output/basic_test",
            "label": "MOSTFET_tim_basic_polylong",
            "read_mode": "clean",
            "conv_mode": "TDIM",
            "bayesian": True,
            "bay_steps": 1000,
            "struc_method": "polylong",
        },
    },
    {
        "name": "MOSTFET_tim_basic_khatwani",
        "params": {
            "data": MOSFET_TIM_DATA,
            "output_dir": "tests/output/basic_test",
            "label": "MOSTFET_tim_basic_khatwani",
            "conv_mode": "TDIM",
            "bayesian": True,
            "bay_steps": 1000,
            "struc_method": "khatwani",
            "log_time_size": 75,
            "precision": 2000,
        },
    },
    {
        "name": "MOSTFET_tim_basic_sobhy",
        "params": {
            "data": MOSFET_TIM_DATA,
            "output_dir": "tests/output/basic_test",
            "label": "MOSTFET_tim_basic_sobhy",
            "conv_mode": "TDIM",
            "bayesian": True,
            "bay_steps": 1000,
            "struc_method": "sobhy",
        },
    },
    {
        "name": "MOSTFET_tim_basic_boor_golub",
        "params": {
            "data": MOSFET_TIM_DATA,
            "output_dir": "tests/output/basic_test",
            "label": "MOSTFET_tim_basic_boor_golub",
            "conv_mode": "TDIM",
            "bayesian": True,
            "bay_steps": 1000,
            "struc_method": "boor_golub",
            "log_time_size": 75,
            "precision": 2000,
        },
    },
    {
        "name": "MOSTFET_tim_basic_lanczos",
        "params": {
            "data": MOSFET_TIM_DATA,
            "output_dir": "tests/output/basic_test",
            "label": "MOSTFET_tim_basic_lanczos",
            "conv_mode": "TDIM",
            "bayesian": True,
            "bay_steps": 1000,
            "struc_method": "lanczos",
        },
    },
]

# Removed test_cases_set to avoid duplication
