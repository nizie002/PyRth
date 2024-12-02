import numpy as np


def read_measurement_data(filepath: str) -> np.ndarray:
    """Read measurement data from file, skipping header and calibration."""
    with open(filepath, "r") as f:
        lines = f.readlines()

    # Find the DATA section
    data_start = next(i for i, line in enumerate(lines) if line.strip() == "DATA") + 2

    # Convert the data section to numpy array
    data_lines = [line.strip() for line in lines[data_start:] if line.strip()]
    data = np.array([list(map(float, line.split())) for line in data_lines])

    return data


# Load data once at module level
MOSFET_DRY_DATA = read_measurement_data("tests/data/MOSFET_dry.txt")
MOSFET_TIM_DATA = read_measurement_data("tests/data/MOSFET_tim.txt")

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
]

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

test_cases_bootstrap = [
    {
        "name": "bootstrap_evaluation_from_theo",
        "params": {
            "output_dir": "tests/output/bootstrap_test",
            "label": "bootstrap_evaluation_from_theo",
            "repetitions": 10,
            "bayesian": True,
            "bay_steps": 100,
            "mode": "from_theo",
            "signal_to_noise_ratio": 50,
            "theo_log_time": [-17, 10],
            "theo_log_time_size": 10000,
            "theo_delta": 2 * (2 * np.pi / 360),
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
        "name": "bootstrap_evaluation_from_data",
        "params": {
            "data": MOSFET_DRY_DATA,
            "output_dir": "tests/output/bootstrap_test",
            "label": "bootstrap_evaluation_from_data",
            "repetitions": 10,
            "bayesian": True,
            "bay_steps": 100,
            "mode": "from_data",
            "signal_to_noise_ratio": 100,
            "conv_mode": "TDIM",
        },
    },
]

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
