# Instructions

## Program Structure

- **transient_core.py**: Orchestrates the transient structure function computation.
- **transient_engine.py**: Serves as the core computation engine for transient analysis.
- **transient_utils.py**: Contains utility functions used throughout the transient analysis.
- **transient_defaults.py**: Defines default parameters and configurations for the analysis.
- **transient_optimization.py**: Implements optimization routines specific to transient thermal analysis.
- **transient_scripts.py**: Contains high-level scripts for executing transient analysis workflows.
- **transient_mpfr_utils.py**: Provides utilities for arbitrary-precision arithmetic using the MPFR library.
- **transient_figures.py**: Manages the creation and customization of figures and plots.
- **transient_data_export.py**: Manages data export and handling of figure generation logic.
- **transient_filter_functions.py**: Contains various filter functions used in transient analysis.

This project is organized into several Python modules, each responsible for different aspects of transient thermal analysis. Below is an overview of the key modules, reordered by their importance to the functionality of the code.

The `parameters` dictionary serves as a centralized configuration repository, encapsulating all settings and options required for transient thermal analysis. This ensures consistent and validated configurations across different modules, facilitating easy customization and parameter management.

The `Evaluation` class orchestrates the handling of various evaluation modules within the program. It manages the initialization, execution, and data aggregation processes, enabling a streamlined and efficient workflow for transient analysis.

## Inter-Module Interactions

- **Core Dependencies**: `transient_core.py` relies on utilities from `transient_utils.py` and computations from `transient_engine.py`.
- **Workflow Orchestration**: High-level scripts in `transient_scripts.py` use the `StructureFunction` class to manage evaluations.
- **Model Refinement**: Optimization routines in `transient_optimization.py` improve models used by `transient_core.py`.
- **Data Handling**: Data export and figure generation are managed by `transient_data_export.py` and `transient_figures.py`.

## Overview of Core Components

The project focuses on analyzing transient thermal responses using various computational methods. The key components work together as follows:

### Data Preprocessing

- **Raw Data Conversion**: Reads and converts raw temperature or voltage measurements into usable formats.
- **Calibration and Extrapolation**: Applies calibration data and extrapolation methods to ensure data accuracy.
- **Conversion Modes**: Supports multiple modes (e.g., t3ster, temp, volt) for flexibility.

### Impedance Calculation

- **Thermal Impedance Conversion**: Transforms temperature data into thermal impedance.
- **Factors Consideration**: Accounts for power steps, heating or cooling modes, and normalization.
- **Data Smoothing**: Handles smoothing and fitting to improve data quality.

### Derivative Computation

- **Impedance Derivative**: Calculates the derivative of impedance over logarithmic time.
- **Techniques Used**: Employs windowing and padding to enhance accuracy.
- **Preparation for Deconvolution**: Essential for subsequent deconvolution steps.

### Deconvolution Methods

- **Techniques Applied**: Uses Fourier transforms and Bayesian deconvolution.
- **Time Constant Spectra Extraction**: Reveals thermal characteristics by extracting spectra.
- **Noise Management**: Incorporates filters and weight functions to handle noise.

### Thermal Network Extraction

- **Model Derivation**: Creates Foster and Cauer thermal network models from time constant spectra.
- **Methods Used**: Employs polynomial long division, continued fraction expansions, or the Lanczos algorithm.
- **Behavior Conversion**: Transforms complex thermal behaviors into lumped parameter models.

### High-Precision Arithmetic

- **Arbitrary-Precision**: Utilizes the MPFR library for sensitive computations.
- **Numerical Stability**: Ensures accuracy in algorithms involving polynomials and rational functions.
- **Error Reduction**: Critical for computations prone to numerical errors in standard floating-point arithmetic.

### Visualization and Export

- **Figure Generation**: Creates visual representations to aid interpretation.
- **Configuration Support**: Allows saving figures and data based on user settings.
- **Data Export**: Provides exports for reporting and further analysis, including impedance curves and network parameters.

## Overall Behavior of the Project

The project provides a comprehensive toolset for transient thermal analysis of systems such as electronic devices. It enables users to:

- **Process Raw Data**: Handles thermal data from various sources.
- **Compute Thermal Impedance**: Analyzes thermal responses accurately.
- **Extract Time Constant Spectra**: Understands the distribution of thermal time constants.
- **Model Thermal Behavior**: Uses equivalent electrical networks (Foster and Cauer models).
- **Perform High-Precision Computations**: Ensures analysis accuracy.
- **Optimize Models**: Adjusts parameters to closely match experimental data.
- **Visualize Results**: Offers customizable figures and plots.
- **Export Data**: Provides data and figures for documentation and further analysis.

By integrating data processing, numerical computation, optimization, and visualization, the project allows for detailed thermal analysis essential in designing and understanding thermally sensitive systems.

## File Details

### `PyRth/transient_scripts.py`

**Purpose**: Contains high-level scripts for executing transient analysis workflows.

**Content**:

- **`Evaluation` Class**: Orchestrates the overall analysis process.

  - **Parameters**:

    - `label`
    - `output_dir`

  - Methods:

    - `save_figures`: Saves all generated figures to PNG files.

    - `save_as_csv`: Processes and saves output data as csv for all modules.

    - `save_all`: Calls `save_figures` and `save_as_csv`

    - `standard_module`: Creates a standard module for structure function computation.

      - **Parameters**:
        - `data`
        - `input_mode`

    - `bootstrap_module`: Performs bootstrapping to estimate confidence intervals.

      - **Parameters**:
        - `repetitions`
        - `random_seed`

    - `optimization_module`: Conducts optimization routines for parameter fitting.

      - **Parameters**:
        - `opt_method`
        - `opt_model_layers`

    - `theoretical_module`: Generates theoretical models for comparison.

      - **Parameters**:
        - `theo_time_size`

    - `temperature_prediction_module`: Predicts temperature profiles based on the analysis.

### `PyRth/transient_core.py`

**Purpose**: Orchestrates the transient structure function computation.

**Content**:

- **`StructureFunction` Class**: Integrates data processing, numerical computation, and result generation.

  - **Parameters**:

    - Inherits parameters from `transient_defaults.py` and accepts user-specified parameters.
    - Validates and sets attributes based on provided parameters.

  - Methods:

    - `make_z`: Computes thermal impedance from raw data based on the conversion mode.

      - Uses parameters such as `input_mode`, `extrapolate`, `calib`, `kfac_fit_deg`, `power_step`, `optical_power`, `power_scale_factor`, and `is_heating`.

    - `z_fit_deriv`: Calculates the derivative of impedance over logarithmic time.

      - Utilizes parameters like `log_time_size`, `window_increment`, `minimum_window_length`, `maximum_window_length`, `minimum_window_size`, `expected_var`, `pad_factor_pre`, and `pad_factor_after`.

    - `fft_signal`: Performs Fourier transform on the impedance derivative.

    - `time_spec`: Extracts the time constant spectrum using deconvolution methods.

      - Applies parameters such as `filter_name`, `filter_range`, and `filter_parameter`.

    - `foster_network`: Derives the Foster thermal network from the time constant spectrum.

      - May use `timespec_interpolate_factor`.

    - `mpfr_foster_impedance`: Computes impedance functions using arbitrary-precision arithmetic.

      - Relies on the `precision` parameter.

    - `poly_long_div`: Transforms the Foster network into a Cauer network using polynomial long division.

    - `boor_golub`: Implements the Boor–Golub algorithm for network conversion.

    - `j_fraction_methods`: Applies J-fraction methods to derive network parameters.

      - Uses `struc_method` to determine the method.

    - `lanczos`: Extracts thermal network parameters using the Lanczos algorithm.

      - Uses `blockwise_sum_width`.

### `PyRth/transient_engine.py`

**Purpose**: Serves as the core computation engine for transient analysis.

**Content**:

- Performance-critical numerical functions optimized with Numba's Just-In-Time (JIT) compilation:

  - `derivative`: Computes the derivative of impedance over logarithmic time.

    - **Parameters**:
      - `log_time_size`
      - `window_increment`
      - `minimum_window_length`
      - `maximum_window_length`
      - `minimum_window_size`
      - `expected_var`
      - `pad_factor_pre`
      - `pad_factor_after`

  - `bayesian_deconvolution`: Performs Bayesian deconvolution to extract time constant spectra.

    - **Parameters**:
      - `bay_steps`

  - `response_matrix`: Generates the response matrix for the deconvolution process.

  - `lanczos_inner`: Performs the Lanczos algorithm for thermal network extraction.

    - **Parameters**:
      - `blockwise_sum_width`

  - `weighted_self_product`: Computes weighted self-products for numerical methods.

### `PyRth/transient_utils.py`

**Purpose**: Contains utility functions used throughout the transient analysis.

**Content**:

- `volt_to_temp`: Converts voltage measurements to temperature using calibration data.

  - **Parameters**:
    - `calib`
    - `kfac_fit_deg`

- `extrapolate_temperature`: Performs extrapolation on temperature data for better accuracy.

  - **Parameters**:
    - `lower_fit_limit`
    - `upper_fit_limit`

- `tmp_to_z`: Converts temperature transients to thermal impedance.

  - **Parameters**:
    - `power_step`
    - `optical_power`
    - `power_scale_factor`
    - `is_heating`

- `weight_z`: Generates weight functions used in deconvolution processes.

### `PyRth/transient_defaults.py`

**Purpose**: Defines default parameters and configurations for the analysis.

**Content**:

- Default settings and parameter validation functions. Only parameters listed here are accepted during module execution.

- **Parameters**:

  - **Numerical Settings**:

    - `precision`
    - `log_time_size`

  - **Deconvolution Settings**:

    - `filter_name`
    - `filter_range`
    - `filter_parameter`
    - `deconv_mode`
    - `bay_steps`
    - `pad_factor_pre`
    - `pad_factor_after`

  - **Structure Function Settings**:

    - `struc_method`
    - `timespec_interpolate_factor`
    - `blockwise_sum_width`

  - **Theoretical Settings**:

    - `theo_time_size`
    - `theo_delta`

  - **K-Factor and Voltage Conversion Settings**:

    - `calib`
    - `kfac_fit_deg`
    - `extrapolate`
    - `lower_fit_limit`
    - `upper_fit_limit`
    - `data_cut_lower`
    - `data_cut_upper`
    - `temp_0_avg_range`

  - **Power Settings**:

    - `power_step`
    - `power_scale_factor`
    - `optical_power`
    - `is_heating`

  - **Window and Derivative Settings**:

    - `minimum_window_length`
    - `maximum_window_length`
    - `minimum_window_size`
    - `window_increment`
    - `expected_var`
    - `min_index`

  - **Optimization Settings**:

    - `opt_recalc_forward`
    - `opt_use_extrapolate`
    - `opt_method`
    - `struc_init_method`
    - `opt_model_layers`

  - **Procedural Settings**:

    - `input_mode`
    - `calc_struc`
    - `only_make_z`
    - `repetitions`
    - `random_seed`
    - `bootstrap_mode`

  - **I/O Settings**:
    - `data`
    - `output_dir`
    - `label`

- Logic to handle figure generation conditions.

### `PyRth/transient_optimization.py`

**Purpose**: Implements optimization routines specific to transient thermal analysis.

**Content**:

- Functions and classes for optimization tasks, such as fitting thermal models to data and minimizing errors.

  - **Parameters**:
    - `opt_recalc_forward`
    - `opt_use_extrapolate`
    - `opt_model_layers`
    - `opt_method`

### `PyRth/transient_mpfr_utils.py`

**Purpose**: Provides utilities for arbitrary-precision arithmetic using the MPFR library.

**Content**:

- `make_z_s`: Constructs the impedance function \( Z(s) \) using Foster network parameters.

- `precision_step`: Performs a single step in polynomial long division with high precision.

- `mpfr_pol_mul`: Multiplies polynomials using MPFR numbers.

- `mpfr_pol_add`: Adds polynomials using MPFR numbers.

### `PyRth/transient_figures.py`

**Purpose**: Manages the creation and customization of figures and plots.

**Content**:

- Classes and functions for visualizing data:

  - **Parameters**:

    - `look_at_*` (flags controlling which figures to generate and display)

  - Features:

    - Impedance plots

    - Time constant spectra

    - Structure functions

    - Thermal network representations

### `PyRth/transient_data_export.py`

**Purpose**: Manages data export and handling of figure generation logic.

**Content**:

- **`DataExporter` Class**:

  - Saves results to CSV files.

  - Handles data output based on user settings.

  - Integrates data handling into the analysis workflow.

  - **Parameters**:
    - Configuration flags such as `save_voltage`, `save_temperature`, `save_impedance`, etc.

### `PyRth/transient_filter_functions.py`

**Purpose**: Defines and implements various filter functions used in transient analysis for Fourier transformation filtering.

- **`give_current_filter` Function**: Selects and applies the appropriate filter based on the given name and parameters.

- **Filter Functions**:
  - `fermi_filter`
  - `gauss_filter`
  - `nuttall_filter`
  - `blackman_nuttall_filter`
  - `hann_filter`
  - `blackman_harris_filter`
  - `rectangular_filter`
