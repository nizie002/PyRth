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


def read_voltage_data(filepath: str) -> np.ndarray:
    """Read measurement data from file, skipping header and calibration."""
    with open(filepath, "r") as f:
        lines = f.readlines()

    # Find the DATA section
    data_start = next(i for i, line in enumerate(lines) if line.strip() == "DATA") + 2

    # Convert the data section to numpy array
    data_lines = [line.strip() for line in lines[data_start:] if line.strip()]
    data = np.array([list(map(float, line.split())) for line in data_lines])

    return data


def read_temp_data(file, column_1, column_2, sep="\t"):
    # Load the file as a structured array using the header row.
    data = np.genfromtxt(
        file,
        delimiter=sep,
        encoding="utf-8",
        skip_header=1,
    )

    # Convert "Time [ms]" from milliseconds to seconds.
    time_sec = data[:, 1] / 1000.0
    # Compute the difference between R2 and R1.
    diff = data[:, column_1] - data[:, column_2]

    # Return a two-dimensional array with time and difference.
    return np.column_stack((time_sec, diff))


# Load data once at module level
MOSFET_DRY_DATA = read_voltage_data("tests/data/MOSFET_dry.txt")
MOSFET_TIM_DATA = read_voltage_data("tests/data/MOSFET_tim.txt")
TEMP_DATA = read_temp_data("tests/data/temp_transient.asc", 5, 2)
