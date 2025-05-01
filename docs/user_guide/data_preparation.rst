Data Preparation
=================

This guide explains how to prepare and format your data for analysis with PyRth.

Input Data Formats
---------------------

PyRth accepts various input data formats through the ``input_mode`` parameter:

1. **Voltage Measurements (input_mode="volt")**
   
   Raw voltage readings from a thermally sensitive parameter (TSP) like a diode forward voltage or thermistor resistance.
   
   * Requires calibration data to convert voltage to temperature
   * Format: ``data`` as numpy array with shape (n, 2) containing [time, voltage]
   * Format: ``calib`` as numpy array with shape (m, 2) containing [temperature, voltage]

2. **Temperature Measurements (input_mode="temperature")**
   
   Pre-processed temperature rise data.
   
   * Format: ``data`` as numpy array with shape (n, 2) containing [time, temperature]
   * Requires ``power_step`` parameter to calculate impedance (Zth = ΔT/P)

3. **Impedance Data (input_mode="impedance")**
   
   Directly using pre-calculated thermal impedance data.
   
   * Format: ``data`` as numpy array with shape (n, 2) containing [time, Zth]
   * Use when you already have processed Zth values

4. **T3Ster Files (input_mode="t3ster")**
   
   For users working with Mentor Graphics T3Ster equipment.
   
   * Specify paths to .raw, .pwr, and .tco files in parameters
   * Example: ``infile``, ``infile_pwr``, ``infile_tco``

Data Preparation Example
--------------------------

Here's an example of preparing data from a CSV file with TSP voltage measurements:

.. code-block:: python

   import numpy as np
   from PyRth import Evaluation
   
   # Load time and voltage data
   raw_data = np.loadtxt("voltage_transient.csv", delimiter=",", skiprows=1)
   
   # Extract time column (in seconds) and voltage column
   time = raw_data[:, 0]
   voltage = raw_data[:, 1]
   
   # Stack into the expected [time, voltage] format
   data = np.column_stack((time, voltage))
   
   # Prepare calibration data (temperature in °C, voltage in V)
   calib = np.array([
       [25.0, 0.550],
       [50.0, 0.525],
       [75.0, 0.500],
       [100.0, 0.475]
   ])
   
   # Configure parameters
   params = {
       "data": data,
       "calib": calib,
       "input_mode": "volt",
       "power_step": 0.5,  # power applied in Watts
       "kfac_fit_deg": 1,   # polynomial degree for calibration (1=linear)
       "output_dir": "results",
       "label": "my_device",
   }
   
   # Run analysis
   evaluator = Evaluation()
   result = evaluator.standard_module(params)
   evaluator.save_all()

Data Preprocessing Tips
-------------------------

1. **Time Origin**
   
   * Ensure time starts close to zero or at the heating/cooling transition
   * You can pre-shift your time array if needed: ``time = time - time[0]``

2. **Sampling Rate**
   
   * Logarithmic sampling is preferred but not required
   * 500-2000 data points typically provide good results
   * Include early time points (microseconds) for accurate structure function

3. **Noise Reduction**
   
   * If data is noisy, consider smoothing before analysis
   * PyRth includes built-in smoothing during derivative calculation

4. **Data Extrapolation**
   
   * Use the ``extrapolate=True`` parameter for early time extrapolation
   * Set ``lower_fit_limit`` and ``upper_fit_limit`` to define the extrapolation range

Working with T3Ster Data
--------------------------

For T3Ster users, specify the file paths:

.. code-block:: python

   params = {
       "input_mode": "t3ster",
       "infile": "measurement.raw",  
       "infile_pwr": "measurement.pwr", 
       "infile_tco": "measurement.tco",
       "output_dir": "results",
       "label": "t3ster_analysis"
   }

Next Step
-----------

Learn about the calibration process in the :doc:`Calibration Guide </user_guide/calibration_guide>`.