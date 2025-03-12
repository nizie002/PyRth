PyRth Evaluation Functions
==========================

PyRth offers several evaluation methods to process thermal transient data. The main functions are:

- standard_module
  Provides a basic evaluation for processing input data to compute thermal impedance and structure functions.

- standard_module_set
  Enables batch processing over multiple parameter configurations. This method iterates over provided iterable keywords and generates a set of evaluation modules.

- bootstrap_module
  Applies statistical bootstrapping to estimate variability and compute confidence intervals for the calculated thermal properties.

- optimization_module
  Optimizes model parameters, refining the fit between the theoretical model and the measured data.

- theoretical_module
  Generates theoretical predictions based on given resistances and capacitances, computing the theoretical thermal impedance.

- comparison_module
  Compares evaluation results, e.g. between theoretical predictions and experimental data or between different evaluation strategies.

- temperature_prediction_module
  Predicts temperature profiles from measured power data using computed impulse responses and convolution.
