"""Shared calibration and measurement fixtures for tests."""

import numpy as np

MOSFET_CALIB_DATA = np.array(
    [
        [23.4, 0.55843],
        [37.625, 0.52536],
        [51.85, 0.49232],
        [66.075, 0.45927],
        [80.3, 0.42621],
    ]
)

LED_CALIB_DATA = np.array(
    [
        [20.0, 2.53473992],
        [30.0, 2.55473992],
        [40.0, 2.57473992],
        [50.0, 2.59473992],
        [60.0, 2.61473992],
    ]
)


def read_voltage_data(filepath: str) -> np.ndarray:
    """Read measurement data from file, skipping header and calibration."""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    data_start = next(i for i, line in enumerate(lines) if line.strip() == "DATA") + 2

    data_lines = [line.strip() for line in lines[data_start:] if line.strip()]
    data = np.array([list(map(float, line.split())) for line in data_lines])

    return data


def read_temp_data(file, column_1, column_2, sep="\t"):
    """Load temperature data and return time (s) with differential readings."""
    data = np.genfromtxt(
        file,
        delimiter=sep,
        encoding="utf-8",
        skip_header=1,
    )

    time_sec = data[:, 1] / 1000.0
    diff = data[:, column_1] - data[:, column_2]

    return np.column_stack((time_sec, diff))


# Load data once at module level
MOSFET_DRY_DATA = read_voltage_data("tests/data/MOSFET_dry.txt")
MOSFET_TIM_DATA = read_voltage_data("tests/data/MOSFET_tim.txt")
LED_DATA = read_voltage_data("tests/data/LED_data.txt")
TEMP_DATA = read_temp_data("tests/data/temp_transient.asc", 5, 2)
