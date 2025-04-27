import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import shutil
import logging
from PyRth import Evaluation
from tests.data.measurement_data import MOSFET_TIM_DATA, MOSFET_CALIB_DATA
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PyRthLogger")


def main():
    # Set up the parameters for the optimization test manually
    params = {
        "data": MOSFET_TIM_DATA,
        "output_dir": "tests/output/manual_optimization_test",
        "label": "manual_optimization_test",
        "input_mode": "volt",
        "opt_model_layers": 25,  # Adjust the complexity as needed
        "opt_method": "Powell",  # Or use "Powell" based on your case
        "calib": MOSFET_CALIB_DATA,
        "lower_fit_limit": 5e-4,
        "upper_fit_limit": 1e-3,
        "theo_time": [
            1e-8,
            5e2,
        ],  # range of the time for the theoretical model in seconds
        "theo_time_size": 6000,  # number of points in the time array for the theoretical model
        "theo_delta": 1.0
        * (
            2 * np.pi / 360
        ),  # angle to rotate Z(s) into the complex plane to avoid singularities (smaller is better, but makes peaks sharper)
    }

    # Ensure a clean output directory
    output_dir = params["output_dir"]
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    logger.info("Starting manual optimization test...")

    # Instantiate the evaluation and run the optimization module manually
    eval_instance = Evaluation()
    modules = eval_instance.optimization_module(params)

    # Process evaluation outputs and figures
    eval_instance.save_as_csv()
    eval_instance.save_figures()

    logger.info("Manual optimization test executed successfully.")
    print("Manual optimization test executed successfully.")


if __name__ == "__main__":
    main()
