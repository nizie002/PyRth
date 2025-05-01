Getting Started
===============

This guide will walk you through the basic steps to use PyRth for thermal transient analysis.

Installation
---------------

First, ensure you have PyRth installed. If not, follow the :doc:`installation instructions </installation>`.

.. code-block:: bash

   pip install PyRth

Basic Analysis Workflow
-------------------------

A standard thermal transient analysis workflow includes these steps:

1. **Prepare your data**: Load thermal transient data from your measurement system.
2. **Create an Evaluation instance**: Instantiate the main PyRth analysis object.
3. **Process with standard module**: Run the thermal impedance calculation and deconvolution.
4. **Save and visualize results**: Export data as CSV files and generate plots.

Example
---------

Here's a minimal example to process thermal transient data:

.. code-block:: python

   import numpy as np
   from PyRth import Evaluation
   
   # Load your measurement data (time and voltage columns)
   data = np.loadtxt("your_measurement.csv", delimiter=",")
   
   # Load your calibration data (temperature and voltage)
   calibration = np.array([
       [25.0, 0.55],
       [50.0, 0.50],
       [75.0, 0.45],
       [100.0, 0.40],
   ])
   
   # Set up parameters
   params = {
       "data": data,
       "output_dir": "results",
       "label": "my_first_analysis",
       "input_mode": "volt",
       "calib": calibration,
       "power_step": 1.0,  # power applied during measurement in Watts
       "deconv_mode": "bayesian",
       "lower_fit_limit": 1e-4,  # seconds
       "upper_fit_limit": 1e-3,  # seconds
   }
   
   # Run the analysis
   evaluator = Evaluation()
   result = evaluator.standard_module(params)
   
   # Save results
   evaluator.save_all()
   
   # Access computed data
   print(f"Total thermal resistance: {result.int_cau_res[-1]:.2f} K/W")

Next Steps
------------

After mastering the basics, explore more advanced features:

- Learn about :doc:`data preparation </user_guide/data_preparation>` for different input types
- Configure the analysis with :ref:`default-configuration-label`
- Try different deconvolution methods (fourier, bayesian, lasso)
- Explore bootstrapping for statistical analysis