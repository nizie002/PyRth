
Usage
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

