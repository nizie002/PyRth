Advanced Workflows
===================

This guide covers advanced PyRth analysis workflows for complex thermal characterization tasks.

Comparing Multiple Measurements
---------------------------------

PyRth makes it easy to compare multiple measurements using the ``standard_module_set`` method:

.. code-block:: python

   from PyRth import Evaluation
   import numpy as np
   
   # Load multiple datasets
   data_set1 = np.loadtxt("sample1.csv", delimiter=",")
   data_set2 = np.loadtxt("sample2.csv", delimiter=",")
   data_set3 = np.loadtxt("sample3.csv", delimiter=",")
   
   # Prepare parameter dictionary with iterables
   params = {
       "output_dir": "comparison_results",
       "label": "comparison",
       "input_mode": "impedance",
       "evaluation_type": "standard",
       "iterable_keywords": ["data", "device_name"],  # Parameters to iterate over
       "data": [data_set1, data_set2, data_set3],     # List of datasets
       "device_name": ["sample1", "sample2", "sample3"]  # List of names
   }
   
   # Run the comparison
   evaluator = Evaluation()
   modules = evaluator.standard_module_set(params)
   evaluator.save_all()
   
   # Access and compare results
   for i, module in enumerate(modules):
       print(f"Device: {params['device_name'][i]}")
       print(f"Total Rth: {module.int_cau_res[-1]:.2f} K/W")

Bootstrapping for Uncertainty Analysis
----------------------------------------

Use bootstrapping to assess statistical confidence in your results:

.. code-block:: python

   params = {
       "data": measurement_data,
       "input_mode": "impedance",
       "output_dir": "bootstrap_results",
       "label": "bootstrap_analysis",
       "repetitions": 500,            # Number of bootstrap resamples
       "signal_to_noise_ratio": 100,  # S/N ratio for noise generation
       "evaluation_type": "bootstrap_standard", # or "bootstrap_optimization"
       "bootstrap_mode": "from_data", # Resample from measurement data
       "calc_struc": True,
       "random_seed": 42              # For reproducibility
   }
   
   evaluator = Evaluation()
   bootstrap_result = evaluator.bootstrap_module(params)
   evaluator.save_all()
   
   # Access bootstrap confidence intervals
   print("Thermal resistance with 80% confidence interval:")
   print(f"Rth = {bootstrap_result.int_cau_res[-1]:.2f} K/W")
   print(f"80% CI: [{bootstrap_result.boot_struc_cap_perc_l[-1]:.2f}, {bootstrap_result.boot_struc_cap_perc_u[-1]:.2f}]")

Structure Function Optimization
---------------------------------

For improved structure function accuracy, use optimization techniques:

.. code-block:: python

   params = {
       "data": measurement_data,
       "input_mode": "impedance",
       "output_dir": "optimized_results",
       "label": "optimized_analysis",
       "evaluation_type": "optimization",
       "theo_time": [1e-6, 1e3],      # Time range for theoretical model
       "theo_time_size": 10000,       # Resolution of theoretical model
       "opt_model_layers": 15,        # Number of Foster network layers
       "struc_init_method": "optimal_fit", # Initialization method
       "opt_method": "Powell"         # Optimization algorithm
   }
   
   evaluator = Evaluation()
   opt_result = evaluator.optimization_module(params)
   evaluator.save_all()

Generating Theoretical Structure Functions
--------------------------------------------

Create theoretical structure functions for modeling or comparison:

.. code-block:: python

   import numpy as np
   from PyRth import Evaluation
   
   # Define a theoretical structure with 3 layers
   params = {
       "output_dir": "theoretical_results",
       "label": "three_layer_model",
       "theo_time": [1e-6, 1e3],
       "theo_time_size": 10000,
       "theo_resistances": [0.5, 1.0, 2.0],         # K/W
       "theo_capacitances": [1e-4, 1e-3, 1e-2],     # J/K
   }
   
   evaluator = Evaluation()
   theo_result = evaluator.theoretical_module(params)
   evaluator.save_all()

Temperature Prediction from Power Profile
--------------------------------------------

Predict temperature response from arbitrary power profiles:

.. code-block:: python

   import numpy as np
   from PyRth import Evaluation
   
   # First run standard analysis to get thermal model
   model_params = {
       "data": measurement_data,
       "input_mode": "impedance",
       "output_dir": "prediction_results",
       "label": "thermal_model",
   }
   
   evaluator = Evaluation()
   model = evaluator.standard_module(model_params)
   
   # Create a power profile (time in seconds, power in watts)
   time = np.linspace(0, 100, 1000)
   power = np.zeros_like(time)
   power[100:300] = 1.0    # 1W from t=10s to t=30s
   power[500:700] = 0.5    # 0.5W from t=50s to t=70s
   power_data = np.column_stack((time, power))
   
   # Predict temperature
   pred_params = {
       "output_dir": "prediction_results",
       "label": "temp_prediction",
       "evaluation_type": "standard",
       "power_data": power_data,
       "lin_sampling_period": 1e-3,  # Sampling period for convolution
   }
   
   prediction = evaluator.temperature_prediction_module(pred_params)
   evaluator.save_all()
   
   # Access predicted temperature
   pred_time = prediction.lin_time
   pred_temp = prediction.predicted_temperature

Comparing Measured vs Theoretical Structure Functions
---------------------------------------------------------

Evaluate how well a measurement matches a theoretical model:

.. code-block:: python

   params = {
       "output_dir": "comparison_results",
       "label": "meas_vs_theo",
       "evaluation_type": "standard",
       
       # Theoretical model parameters
       "theo_resistances": [0.5, 1.0, 2.0],
       "theo_capacitances": [1e-4, 1e-3, 1e-2],
       
       # Parameters for generating multiple evaluation runs
       "iterable_keywords": ["deconv_mode"],
       "deconv_mode": ["bayesian", "fourier", "lasso"]
   }
   
   evaluator = Evaluation()
   comparison = evaluator.comparison_module(params)
   evaluator.save_all()
   
   # Access comparison metrics
   print("Time constant spectrum comparison metrics:")
   print(comparison.time_const_comparison)
   print("\nStructure function comparison metrics:")
   print(comparison.structure_comparison)

Advanced Parameter Customization
-------------------------------------

For fine-tuned control, customize deconvolution and structure function calculations:

.. code-block:: python

   # Advanced Fourier deconvolution parameters
   fourier_params = {
       "data": measurement_data,
       "input_mode": "impedance",
       "output_dir": "advanced_results",
       "label": "custom_fourier",
       "deconv_mode": "fourier",
       "filter_name": "gauss",        # Filter type
       "filter_range": 0.5,           # Filter cutoff parameter
       "pad_factor_pre": 0.1,         # Zero padding before data
       "pad_factor_after": 0.1,       # Zero padding after data
   }
   
   # Advanced structure function parameters
   structure_params = {
       "data": measurement_data,
       "input_mode": "impedance",
       "output_dir": "advanced_results",
       "label": "custom_structure",
       "struc_method": "sobhy",      # Structure function calculation method
       "precision": 500,             # MPFR precision for high-precision math
       "blockwise_sum_width": 10,    # For Lanczos method only
   }

Command-Line Batch Processing
-----------------------------------

For batch processing, you can create Python scripts that can be run from the command line:

.. code-block:: python
   :caption: process_batch.py
   
   import numpy as np
   import os
   import glob
   import argparse
   from PyRth import Evaluation
   
   def main():
       parser = argparse.ArgumentParser(description='Process multiple thermal measurements')
       parser.add_argument('--data_dir', required=True, help='Directory with data files')
       parser.add_argument('--output_dir', required=True, help='Output directory')
       args = parser.parse_args()
       
       # Find all CSV files in the data directory
       data_files = glob.glob(os.path.join(args.data_dir, "*.csv"))
       
       # Process each file
       for file_path in data_files:
           filename = os.path.basename(file_path)
           label = os.path.splitext(filename)[0]
           
           # Load data
           data = np.loadtxt(file_path, delimiter=",")
           
           # Configure parameters
           params = {
               "data": data,
               "input_mode": "impedance",
               "output_dir": args.output_dir,
               "label": label,
           }
           
           # Run analysis
           evaluator = Evaluation()
           evaluator.standard_module(params)
           evaluator.save_all()
           
           print(f"Processed {filename}")
   
   if __name__ == "__main__":
       main()

Run this script from the command line:

.. code-block:: bash

   python process_batch.py --data_dir=./measurement_data --output_dir=./batch_results