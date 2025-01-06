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
