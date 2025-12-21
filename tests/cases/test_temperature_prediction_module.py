"""Temperature prediction module parameterized cases."""

import numpy as np
import pytest
from tests.data.measurement_data import (
    MOSFET_CALIB_DATA,
    MOSFET_DRY_DATA,
)
from tests.test_transient_base import run_evaluation_test
from tests.assertions.temperature_prediction_assertions import (
    temperature_prediction_assertions,
)

# Create a rectangular power function (alternating between 0 and 2W) repeating every 5 seconds
t_values_rect = np.linspace(0, 20, 4000)  # 0-20 seconds with good resolution
p_values_rect = np.zeros_like(t_values_rect)

# Create rectangular pulses: 2W for 2.5s, then 0W for 2.5s, repeating every 5 seconds
for i in range(4):  # Create 4 complete cycles in 20 seconds
    start_idx = i * 1000  # Each cycle is 1000 points (5 seconds)
    mid_idx = start_idx + 500  # Midpoint of the cycle (2.5 seconds)
    if start_idx < len(p_values_rect):
        p_values_rect[start_idx : min(mid_idx, len(p_values_rect))] = 2.0  # 2W for 2.5s

rect_power_data = np.column_stack((t_values_rect, p_values_rect))

test_cases_prediction = [
    {
        "name": "MOSFET_dry_basic_temperature",
        "params": {
            "data": MOSFET_DRY_DATA,
            "output_dir": "tests/output/temp_pred_test",
            "label": "MOSFET_dry_basic_temperature",
            "input_mode": "volt",
            "calib": MOSFET_CALIB_DATA,
            "lower_fit_limit": 5e-4,
            "upper_fit_limit": 1e-3,
            "power_data": rect_power_data,
            "lin_sampling_period": 1e-3,
            "evaluation_type": "standard",
        },
    },
    {
        "name": "MOSFET_opt_temperature",
        "params": {
            "data": MOSFET_DRY_DATA,
            "output_dir": "tests/output/temp_pred_test",
            "label": "MOSFET_opt_temperature",
            "input_mode": "volt",
            "calib": MOSFET_CALIB_DATA,
            "lower_fit_limit": 5e-4,
            "upper_fit_limit": 1e-3,
            # Optimization parameters
            "evaluation_type": "optimization",
            "opt_method": "Powell",
            "theo_time": [1e-8, 5e2],
            "theo_time_size": 8000,
            "theo_delta": 1.5 * (2 * np.pi / 360),
            "opt_model_layers": 8,
            "power_data": rect_power_data,
            "lin_sampling_period": 1e-4,
        },
    },
]

@pytest.mark.parametrize(
    "case",
    test_cases_prediction,
    ids=lambda case: case["name"],
)
def test_temperature_prediction(case):
    """Run temperature_prediction_module for each parameter set."""
    run_evaluation_test(
        case["name"],
        case["params"],
        evaluation_module="temperature_prediction_module",
        additional_assertions=temperature_prediction_assertions,
    )
