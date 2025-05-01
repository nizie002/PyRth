Calibration Guide
====================

This guide explains how to properly calibrate temperature-sensitive parameters (TSPs) for thermal transient analysis in PyRth.

Understanding Calibration
--------------------------

To accurately calculate thermal impedance, PyRth needs to convert voltage measurements from thermally sensitive parameters (TSPs) into temperature. This requires a calibration relationship between the measured electrical parameter and temperature.

Common calibration scenarios include:

* Forward voltage of a diode or transistor
* Resistance of a thermistor or RTD
* On-state voltage of an LED or MOSFET

Calibration Data Format
--------------------------

PyRth expects calibration data as a NumPy array with shape (n, 2) where:
* First column: Temperature values (°C)
* Second column: Corresponding voltage/resistance values

Example:

.. code-block:: python

   import numpy as np
   
   # Temperature (°C) vs. Forward Voltage (V) calibration for a diode
   calib_data = np.array([
       [25.0, 0.720],  # 25°C corresponds to 0.720V
       [50.0, 0.660],  # 50°C corresponds to 0.660V 
       [75.0, 0.600],  # 75°C corresponds to 0.600V
       [100.0, 0.540]  # 100°C corresponds to 0.540V
   ])

Calibration Measurement Procedure
-----------------------------------

For accurate calibration:

1. Place your device in a temperature-controlled environment (e.g., oven, hot plate, climate chamber)
2. Apply a small measurement current (typically 1mA for diodes) to prevent self-heating
3. Wait for thermal equilibrium at each temperature step
4. Record the voltage/resistance value at each temperature
5. Cover a temperature range that exceeds your expected measurement range

.. note::
   Use at least 4-5 temperature points for reliable calibration. More points provide better accuracy.

Calibration Polynomial Degree
-------------------------------

PyRth uses polynomial fitting to create the calibration curve. Control the polynomial degree with the ``kfac_fit_deg`` parameter:

* ``kfac_fit_deg=1``: Linear calibration (sufficient for narrow temperature ranges)
* ``kfac_fit_deg=2``: Quadratic calibration (better for wider temperature ranges)
* ``kfac_fit_deg=3+``: Higher-order polynomials (rarely needed, may cause overfitting)

Example with specified polynomial degree:

.. code-block:: python

   params = {
       "data": measurement_data,
       "calib": calibration_data,
       "input_mode": "volt",
       "kfac_fit_deg": 2,  # Quadratic calibration
       # ... other parameters
   }

Visualizing the Calibration
-----------------------------

To verify your calibration, you can create a simple visualization:

.. code-block:: python

   import numpy as np
   import matplotlib.pyplot as plt
   from scipy.polynomial.polynomial import polyval, polyfit
   
   # Your calibration data
   calib_data = np.array([
       [25.0, 0.720],
       [50.0, 0.660], 
       [75.0, 0.600],
       [100.0, 0.540]
   ])
   
   # Extract columns
   temp = calib_data[:, 0]
   voltage = calib_data[:, 1]
   
   # Fit polynomial (degree=2 for quadratic)
   coefs = polyfit(voltage, temp, 2)
   
   # Generate points for smooth curve
   v_fine = np.linspace(min(voltage), max(voltage), 100)
   t_fine = polyval(v_fine, coefs)
   
   # Plot
   plt.figure(figsize=(10, 6))
   plt.scatter(voltage, temp, color='red', s=50, label='Calibration points')
   plt.plot(v_fine, t_fine, 'b-', label=f'Polynomial fit (degree={2})')
   plt.xlabel('Voltage (V)')
   plt.ylabel('Temperature (°C)')
   plt.title('TSP Calibration')
   plt.grid(True)
   plt.legend()
   plt.show()

Using Calibration in PyRth
-----------------------------

Once you have your calibration data, use it in your PyRth analysis:

.. code-block:: python

   from PyRth import Evaluation
   
   # Prepare parameters with calibration data
   params = {
       "data": measurement_data,  # Your [time, voltage] measurements
       "calib": calibration_data, # Your [temperature, voltage] calibration
       "input_mode": "volt",      # Tell PyRth this is voltage data
       "kfac_fit_deg": 2,         # Polynomial degree
       "power_step": 1.0,         # Heating power in watts
       "output_dir": "results",
       "label": "calibrated_measurement"
   }
   
   # Run analysis
   evaluator = Evaluation()
   result = evaluator.standard_module(params)
   evaluator.save_all()

Common Calibration Issues
---------------------------

1. **Insufficient temperature range**
   
   * Always calibrate beyond your expected measurement range
   * Example: If you expect 20-80°C in your measurement, calibrate from 10-90°C or wider

2. **Self-heating during calibration**
   
   * Use small measurement current to prevent self-heating
   * Allow sufficient time for thermal stabilization at each point

3. **Non-linear behavior**
   
   * Some TSPs have non-linear temperature dependence
   * Use higher polynomial degree (`kfac_fit_deg=2` or `3`) for wider temperature ranges

4. **Extrapolation errors**
   
   * Avoid extrapolating far beyond your calibration range
   * PyRth will warn if temperature calculations exceed calibration range

Next Steps
-------------

Once your data is properly calibrated, explore :doc:`Advanced Workflows </user_guide/advanced_workflows>` to get the most from your thermal analysis.