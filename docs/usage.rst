
Basic Usage
==============


Overview
----------------

PyRth offers several evaluation methods to process thermal transient data. The main functions are:

- :py:meth:`~PyRth.transient_scripts.Evaluation.standard_module`
  Provides a basic evaluation for processing input data to compute thermal impedance and structure functions.

- :py:meth:`~PyRth.transient_scripts.Evaluation.standard_module_set`
  Enables batch processing over multiple parameter configurations. This method iterates over provided iterable keywords and generates a set of evaluation modules.

- :py:meth:`~PyRth.transient_scripts.Evaluation.bootstrap_module`
  Applies statistical bootstrapping to estimate variability and compute confidence intervals for the calculated thermal properties.

- :py:meth:`~PyRth.transient_scripts.Evaluation.optimization_module`
  Optimizes model parameters, refining the fit between the theoretical model and the measured data.

- :py:meth:`~PyRth.transient_scripts.Evaluation.theoretical_module`
  Generates theoretical predictions based on given resistances and capacitances, computing the theoretical thermal impedance.

- :py:meth:`~PyRth.transient_scripts.Evaluation.comparison_module`
  Compares evaluation results, e.g. between theoretical predictions and experimental data or between different evaluation strategies.

- :py:meth:`~PyRth.transient_scripts.Evaluation.temperature_prediction_module`
  Predicts temperature profiles from measured power data using computed impulse responses and convolution.



Data Sources
----------------

The following examples use measurement data provided under `tests/data` in the repository, loaded via the helper module `tests/data/measurement_data.py`:

- **MOSFET_DRY_DATA** and **MOSFET_TIM_DATA**: Voltage transients from MOSFET devices, with and without thermal interface material.
- **LED_DATA**: Voltage transients from LED devices for thermo-optical calibration testing.
- **TEMP_DATA**: Time and temperature differences extracted from ASCII data files (.asc) for thermal response.
- **Calibration arrays**: `MOSFET_CALIB_DATA` and `LED_CALIB_DATA`, used to convert voltage or resistance readings into temperature.

All data are returned as NumPy arrays of shape `(n, 2)`, with columns `[time, measurement]`. In your own workflows, replace these with your own arrays (e.g., from CSV, T3ster exports, or other sources) before passing to the evaluation methods.

Input Modes
----------------

PyRth supports four input modes to describe how raw measurement data is interpreted. Set the `input_mode` key in your parameter dictionary to one of the following:

- **impedance**
  - Data columns: `[time, Zth]` (thermal impedance vs. time).
  - No conversion applied; data are assumed to be impedance already.
  - Use when you have precomputed impedance values.

- **temperature**
  - Data columns: `[time, temperature_rise]`.
  - Converts ΔT to Zth = ΔT / P, where `power_step` (W) must be set.
  - Use when your measurement yields temperature vs. time.

- **volt**
  - Data columns: `[time, voltage]`.
  - Converts voltage to temperature via a calibration array (`calib`) and then to Zth.
  - Requires: `calib` array (e.g., `MOSFET_CALIB_DATA`), `kfac_fit_deg` to set polynomial fit degree.
  - Use when measuring a voltage-based temperature-sensitive parameter (TSP) (e.g., a MOSFET).

- **t3ster**
  - Specialized mode for Siemens T3Ster raw data files.
  - Parses `infile` (`.raw`), `infile_pwr` (`.pwr`), and `infile_tco` (`.tco`) to extract voltage and calibration.
  - Use when working directly with T3Ster instrument exports.


Examples of Evaluation Modules
-------------------------------------

This section provides examples of how to use the different evaluation
modules available in the :py:class:`~PyRth.transient_scripts.Evaluation` class.

For detailed descriptions of all configurable parameters and their default
values, please refer to the :ref:`Default Configuration <default-configuration-label>`
section. Parameters can be overridden by passing them as keyword arguments
to the module methods.

Standard Analysis (:py:meth:`~PyRth.transient_scripts.Evaluation.standard_module`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides a basic evaluation for processing input data to compute thermal impedance and structure functions.

.. code-block:: python

    from PyRth import Evaluation
    from tests.data.measurement_data import MOSFET_DRY_DATA, MOSFET_CALIB_DATA

    params = {
        "data": MOSFET_DRY_DATA,
        "output_dir": "results/basic",
        "label": "mosfet_standard",
        "input_mode": "volt",
        "calib": MOSFET_CALIB_DATA,
        "deconv_mode": "fourier",
        "lower_fit_limit": 5e-4,
        "upper_fit_limit": 1e-3,
    }
    evaluator = Evaluation()
    result = evaluator.standard_module(params)
    evaluator.save_all()


Batch Processing (:py:meth:`~PyRth.transient_scripts.Evaluation.standard_module_set`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Enables batch processing over multiple parameter configurations. This method iterates over provided iterable keywords and generates a set of evaluation modules.

.. code-block:: python

    from PyRth import Evaluation
    from tests.data.measurement_data import MOSFET_DRY_DATA, MOSFET_CALIB_DATA

    params_set = {
        "data": MOSFET_DRY_DATA,
        "output_dir": "results/set",
        "label": "set_bay_steps",
        "input_mode": "volt",
        "deconv_mode": "bayesian",
        "bay_steps": [100, 1000],
        "iterable_keywords": ["bay_steps"],
        "evaluation_type": "standard",
        "calib": MOSFET_CALIB_DATA,
        "lower_fit_limit": 5e-4,
        "upper_fit_limit": 1e-3,
    }
    evaluator = Evaluation()
    set_results = evaluator.standard_module_set(params_set)
    evaluator.save_all()


Bootstrapping (:py:meth:`~PyRth.transient_scripts.Evaluation.bootstrap_module`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Applies statistical bootstrapping to estimate variability and compute confidence intervals for the calculated thermal properties.

.. code-block:: python

    from PyRth import Evaluation
    from tests.data.measurement_data import MOSFET_DRY_DATA, MOSFET_CALIB_DATA

    bootstrap_params = {
        "data": MOSFET_DRY_DATA,
        "output_dir": "results/bootstrap",
        "label": "bootstrap_example",
        "input_mode": "volt",
        "calib": MOSFET_CALIB_DATA,
        "repetitions": 20,
        "deconv_mode": "bayesian",
        "evaluation_type": "bootstrap_standard",
        "lower_fit_limit": 5e-4,
        "upper_fit_limit": 1e-3,
    }
    evaluator = Evaluation()
    boot_result = evaluator.bootstrap_module(bootstrap_params)
    evaluator.save_all()


Optimization (:py:meth:`~PyRth.transient_scripts.Evaluation.optimization_module`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Optimizes model parameters, refining the fit between the theoretical model and the measured data.

.. code-block:: python

    from PyRth import Evaluation
    from tests.data.measurement_data import MOSFET_DRY_DATA, MOSFET_CALIB_DATA

    optimization_params = {
        "data": MOSFET_DRY_DATA,
        "output_dir": "results/optimization",
        "label": "mosfet_opt",
        "input_mode": "volt",
        "calib": MOSFET_CALIB_DATA,
        "opt_model_layers": 10,
        "opt_method": "Powell",
        "evaluation_type": "optimization",
        "lower_fit_limit": 5e-4,
        "upper_fit_limit": 1e-3,
        "theo_time": [1e-8, 5e2],
        "theo_time_size": 10000,
        "theo_delta": 1.0 * (2 * np.pi / 360),
    }
    evaluator = Evaluation()
    opt_result = evaluator.optimization_module(optimization_params)
    evaluator.save_all()


Theoretical Modeling (:py:meth:`~PyRth.transient_scripts.Evaluation.theoretical_module`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Generates theoretical predictions based on given resistances and capacitances, computing the theoretical thermal impedance.

.. code-block:: python

    from PyRth import Evaluation

    theoretical_params = {
        "output_dir": "results/theoretical",
        "label": "mosfet_theo",
        "theo_time": [5e-9, 20],
        "theo_time_size": 10000,
        "theo_delta": 1.5 * (2 * np.pi / 360),
        "theo_resistances": [5, 15, 10, 10, 10],
        "theo_capacitances": [1e-5, 1e-3, 1e-4, 1e-2, 1e-1],
    }
    evaluator = Evaluation()
    theo_result = evaluator.theoretical_module(theoretical_params)
    evaluator.save_all()


Comparison (:py:meth:`~PyRth.transient_scripts.Evaluation.comparison_module`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Compares evaluation results, e.g. between theoretical predictions and experimental data or between different evaluation strategies.

.. code-block:: python

    from PyRth import Evaluation
    from tests.data.measurement_data import MOSFET_DRY_DATA
    import numpy as np

    comparison_params = {
        "output_dir": "results/comparison",
        "label": "mosfet_compare",
        "input_mode": "volt",
        "deconv_mode": "fourier",
        "iterable_keywords": ["filter_range"],
        "filter_range": [0.1, 0.5, 0.9],
        "evaluation_type": "standard",
        "theo_inverse_specs": {
            "theo_time": [3e-7, 200],
            "theo_time_size": 30000,
            "theo_delta": 0.5 * (2 * np.pi / 360),
            "theo_resistances": [10, 10, 10, 10, 10],
            "theo_capacitances": [1e-4, 1e-1, 1e-4, 1e-3, 1e0],
        },
    }
    evaluator = Evaluation()
    comp_result = evaluator.comparison_module(comparison_params)
    evaluator.save_all()


Temperature Prediction (:py:meth:`~PyRth.transient_scripts.Evaluation.temperature_prediction_module`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Predicts temperature profiles from measured power data using computed impulse responses and convolution.

.. code-block:: python

    from PyRth import Evaluation
    from tests.data.measurement_data import TEMP_DATA, LED_CALIB_DATA
    import numpy as np

    prediction_params = {
        "data": TEMP_DATA,
        "output_dir": "results/prediction",
        "label": "temp_pred",
        "input_mode": "voltage",
        "calib": LED_CALIB_DATA,
        "power_data": np.column_stack((TEMP_DATA[:,0], TEMP_DATA[:,1] * 1e-3)),
        "lin_sampling_period": 1e-3,
        "evaluation_type": "standard",
    }
    evaluator = Evaluation()
    pred_result = evaluator.temperature_prediction_module(prediction_params)
    evaluator.save_all()
