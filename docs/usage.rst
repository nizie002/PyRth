PyRth Evaluation Functions
==========================

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

Usage Examples
==============

This section provides examples of how to use the different evaluation
modules available in the :py:class:`~PyRth.transient_scripts.Evaluation` class.

For detailed descriptions of all configurable parameters and their default
values, please refer to the :ref:`Default Configuration <default-configuration-label>`
section. Parameters can be overridden by passing them as keyword arguments
to the module methods.

Standard Analysis (:py:meth:`~PyRth.transient_scripts.Evaluation.standard_module`)
-------------------------------------------------------------------------------------------------------------------------------------------------
Provides a basic evaluation for processing input data to compute thermal impedance and structure functions.

.. code-block:: python

    from PyRth import Evaluation
    import numpy as np

    # --- Setup ---
    evaluator = Evaluation()
    time = np.logspace(-6, 1, 100)
    temp = 10 * (1 - np.exp(-time / 0.1)) # Simulated data

    # --- Run Analysis ---
    # Override heating_power, keep other defaults
    results = evaluator.standard_module(
        time_data=time,
        meas_data=temp,
        power_step=5.0, # Corrected parameter name
        input_mode='temperature', # Corrected parameter name
        output_dir='results/my_standard_run' # Corrected parameter name
    )
    print("Standard analysis complete.")


Batch Processing (:py:meth:`~PyRth.transient_scripts.Evaluation.standard_module_set`)
----------------------------------------------------------------------------------------------------------------------------------------------------
Enables batch processing over multiple parameter configurations. This method iterates over provided iterable keywords and generates a set of evaluation modules.

*(...add description and example...)*


Bootstrapping (:py:meth:`~PyRth.transient_scripts.Evaluation.bootstrap_module`)
-----------------------------------------------------------------------------------------------------------------------------------------------
Applies statistical bootstrapping to estimate variability and compute confidence intervals for the calculated thermal properties.

*(...add description and example...)*


Optimization (:py:meth:`~PyRth.transient_scripts.Evaluation.optimization_module`)
------------------------------------------------------------------------------------------------------------------------------------------------
Optimizes model parameters, refining the fit between the theoretical model and the measured data.

*(...add description and example...)*


Theoretical Modeling (:py:meth:`~PyRth.transient_scripts.Evaluation.theoretical_module`)
-------------------------------------------------------------------------------------------------------------------------------------------------------
Generates theoretical predictions based on given resistances and capacitances, computing the theoretical thermal impedance.

*(...add description and example...)*


Comparison (:py:meth:`~PyRth.transient_scripts.Evaluation.comparison_module`)
---------------------------------------------------------------------------------------------------------------------------------------------
Compares evaluation results, e.g. between theoretical predictions and experimental data or between different evaluation strategies.

*(...add description and example...)*


Temperature Prediction (:py:meth:`~PyRth.transient_scripts.Evaluation.temperature_prediction_module`)
--------------------------------------------------------------------------------------------------------------------------------------------------------------------
Predicts temperature profiles from measured power data using computed impulse responses and convolution.

*(...add description and example...)*
