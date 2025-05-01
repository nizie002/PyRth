Data Extraction and Programmatic Access
=========================================

While PyRth provides comprehensive CSV export and visualization capabilities, many users need programmatic access to the data for custom analysis, processing, or integration with other tools. This guide explains how to directly access data from PyRth modules without relying on file exports.

Understanding the Module Structure
------------------------------------

Each PyRth module stores its data in attributes that correspond to specific aspects of the thermal analysis. When you run an evaluation, PyRth returns module objects that contain all calculated data:

.. code-block:: python

    from PyRth import Evaluation
    
    evaluator = Evaluation()
    result = evaluator.standard_module(params)
    
    # result is a module object containing all the data

Direct Data Access
--------------------

You can directly access any attribute of a module as follows:

.. code-block:: python

    # Access the impedance data
    time_values = result.time  # Time values (seconds)
    impedance_values = result.impedance  # Thermal impedance values (K/W)
    
    # Access structure function data
    cumulative_resistance = result.int_cau_res  # Cumulative thermal resistance (K/W)
    cumulative_capacitance = result.int_cau_cap  # Cumulative thermal capacitance (J/K)
    
    # Access time constant spectrum
    time_constants = np.exp(result.log_time_pad)  # Time constants (seconds)
    spectrum = result.time_spec  # Time constant spectrum values

Common Data Pairs
------------------

Here are the most common data pairs that should be used together:

1. **Thermal Impedance Curve**
   
   - ``result.time`` and ``result.impedance``
   - Represents the raw thermal impedance vs. time

2. **Smoothed Impedance**
   
   - ``np.exp(result.log_time_interp)`` and ``result.imp_smooth``
   - Smoothed version of thermal impedance used for analysis

3. **Impedance Derivative**
   
   - ``np.exp(result.log_time_pad)`` and ``result.imp_deriv_interp``
   - Logarithmic time derivative of the thermal impedance

4. **Time Constant Spectrum**
   
   - ``np.exp(result.log_time_pad)`` and ``result.time_spec``
   - Thermal resistance contribution vs. time constant

5. **Cumulative Structure Function**
   
   - ``result.int_cau_res`` and ``result.int_cau_cap``
   - Cumulative thermal resistance vs. thermal capacitance

6. **Differential Structure Function**
   
   - ``result.int_cau_res[:-1]`` and ``result.diff_struc``
   - Derivative of thermal resistance with respect to capacitance

Working with Multiple Modules
--------------------------------

For batch processing or comparison evaluations, you'll work with multiple modules:

.. code-block:: python

    # Run a comparison evaluation
    comparison_result = evaluator.comparison_module(params)
    
    # Access the modules dictionary
    modules = evaluator.modules
    
    # Get a specific module by its label
    module1 = modules["sample1"]
    module2 = modules["sample2"]
    
    # Extract data from each module
    impedance1 = module1.impedance
    impedance2 = module2.impedance

Accessing Derived Results
----------------------------

For specialized analyses like bootstrapping or theoretical evaluations, additional attributes are available:

.. code-block:: python

    # For bootstrap analysis
    bootstrap_result = evaluator.bootstrap_module(params)
    
    # Access bootstrap confidence intervals
    bootstrap_time = np.exp(bootstrap_result.boot_imp_time)
    bootstrap_average = bootstrap_result.boot_imp_av
    bootstrap_upper_ci = bootstrap_result.boot_imp_perc_u
    bootstrap_lower_ci = bootstrap_result.boot_imp_perc_l
    
    # For theoretical analysis
    theo_result = evaluator.theoretical_module(params)
    
    # Access theoretical model data
    theo_time = np.exp(theo_result.theo_log_time)
    theo_impedance = theo_result.theo_impedance

Example: Custom Analysis
---------------------------

Here's an example of custom analysis using direct data access:

.. code-block:: python

    import numpy as np
    import matplotlib.pyplot as plt
    from PyRth import Evaluation
    from scipy.interpolate import interp1d
    
    # Run the evaluation
    evaluator = Evaluation()
    result = evaluator.standard_module(params)
    
    # Extract time constant spectrum data
    tau = np.exp(result.log_time_pad)
    r_tau = result.time_spec
    
    # Find the dominant time constants (peaks in the spectrum)
    peaks = []
    for i in range(1, len(r_tau)-1):
        if r_tau[i] > r_tau[i-1] and r_tau[i] > r_tau[i+1] and r_tau[i] > 0.01*max(r_tau):
            peaks.append((tau[i], r_tau[i]))
    
    # Print the dominant time constants
    for i, (t, r) in enumerate(peaks):
        print(f"Peak {i+1}: tau = {t:.3e} s, R = {r:.3e} K/W")
    
    # Calculate total thermal resistance
    total_r_th = np.sum(result.time_spec)
    print(f"Total thermal resistance: {total_r_th:.3f} K/W")
    
    # Create interpolation function for the structure function
    struc_func = interp1d(
        result.int_cau_cap, 
        result.int_cau_res, 
        bounds_error=False, 
        fill_value="extrapolate"
    )
    
    # Estimate thermal capacitance at 50% of total thermal resistance
    half_r_th = total_r_th / 2
    cap_points = np.logspace(-6, 1, 1000)
    res_points = struc_func(cap_points)
    idx = np.argmin(np.abs(res_points - half_r_th))
    mid_cap = cap_points[idx]
    
    print(f"Thermal capacitance at half resistance: {mid_cap:.3e} J/K")

Understanding Data Handlers
-----------------------------

PyRth uses a system of data handlers to determine which data can be processed by different modules. These are stored in the ``data_handlers`` attribute of each module:

.. code-block:: python

    # Check what data handlers a module has
    print(result.data_handlers)

Common data handlers include:

- ``"volt"``: Module contains voltage data
- ``"temp"``: Module contains temperature data
- ``"impedance"``: Module contains thermal impedance data
- ``"time_spec"``: Module contains time constant spectrum
- ``"structure"``: Module contains structure function data
- ``"theo"``: Module contains theoretical model data
- ``"boot"``: Module contains bootstrap analysis data

This knowledge is useful when you want to check if a particular type of data is available in a module before attempting to access it.

Best Practices for Data Extraction
-------------------------------------

1. **Check if attributes exist**: Use ``hasattr(module, 'attribute_name')`` to check if the attribute exists before accessing it.

2. **Work with paired data**: Always use the correct x-axis values with their corresponding y-axis values.

3. **Transform logarithmic data**: Many time arrays are stored in logarithmic form. Use ``np.exp()`` to convert them back to seconds.

4. **Use NumPy operations**: PyRth data attributes are NumPy arrays, so you can use all NumPy functions for efficient data manipulation.

5. **Reference official parameters**: Refer to the ``transient_defaults.py`` module for a complete list of available parameters and their default values.

Example: Comparing Multiple Analyses
---------------------------------------

Here's a more complex example comparing different deconvolution methods:

.. code-block:: python

    from PyRth import Evaluation
    import matplotlib.pyplot as plt
    import numpy as np
    
    # Base parameters
    base_params = {
        "data": measurement_data,
        "input_mode": "impedance",
        "label": "comparison"
    }
    
    # Create evaluator
    evaluator = Evaluation()
    
    # Run analyses with different deconvolution methods
    methods = ["bayesian", "fourier", "lasso"]
    results = {}
    
    for method in methods:
        params = base_params.copy()
        params["deconv_mode"] = method
        params["label"] = f"{method}_method"
        results[method] = evaluator.standard_module(params)
    
    # Extract and compare structure functions
    plt.figure(figsize=(10, 6))
    
    for method, result in results.items():
        plt.plot(
            result.int_cau_cap, 
            result.int_cau_res, 
            label=f"{method.capitalize()} Method"
        )
    
    plt.xscale('log')
    plt.xlabel('Thermal Capacitance (J/K)')
    plt.ylabel('Thermal Resistance (K/W)')
    plt.title('Structure Function Comparison Between Deconvolution Methods')
    plt.legend()
    plt.grid(True, which="both", ls="--")
    plt.tight_layout()
    plt.show()