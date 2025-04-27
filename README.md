# PyRth

<img src="assets/images/logo.png" alt="PyRth Logo" width="400"/>

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![Documentation Status](https://readthedocs.org/projects/pyrth/badge/?version=latest)](https://pyrth.readthedocs.io/en/latest/?badge=latest)
[![Downloads](https://img.shields.io/pypi/dm/PyRth)](https://pypi.org/project/PyRth/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14965794.svg)](https://doi.org/10.5281/zenodo.14965794)

---

## 📖 Table of Contents

- [Description](#-description)
- [Why PyRth?](#-why-pyrth)
- [Vision and Rationale](#-vision-and-rationale)
- [Features](#-features)
- [Installation](#-installation)
- [Usage](#-usage)
  - [Quick Start](#quick-start)
  - [Examples](#examples)
  - [Plot Handling](#plot-handling)
  - [Basic Documentation](#basic-documentation)
- [Publications](#-publications)
- [Evaluation Methods](#-evaluation-methods)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](#-contact)
- [Acknowledgements](#-acknowledgements)

## 📚 Description

**PyRth** is an open-source Python package designed for evaluating thermal transient measurement data, such as those obtained from devices like the T3ster. It processes thermal transient data using specialized algorithms to extract detailed thermal characteristics, including the thermal structure function.

PyRth serves as a modern and flexible alternative to proprietary evaluation software provided with thermal transient measurement equipment. It optionally outputs results as images and CSV files, facilitating comprehensive analysis and visualization.

## ❓ Why PyRth?

**PyRth** stands out by offering:

- **Academic Rigor**: Rooted in PhD-level research, ensuring robust and reliable thermal analysis.
- **Reproducibility**: Open-source nature allows for transparent verification and replication of results.
- **Flexibility**: Supports both commercial and custom-built measurement setups, catering to diverse research needs.
- **Community-Driven**: Encourages contributions and collaborations to continuously enhance functionality and performance.

## 🔭 Vision and Rationale

Thermal management is critical to the performance, reliability, and longevity of semiconductor devices. By subjecting devices to controlled power steps and recording their thermal responses over time, thermal transient measurements yield deep insights into the device’s internal heat-flow paths. The resulting structure functions—as defined in standards like JEDEC JESD51-14—provide layer-by-layer thermal resistance and capacitance distributions, essential for diagnosing design inefficiencies and improving packaging strategies.

Commercial solutions, such as the Siemens T3STER, offer turnkey instrumentation for capturing high-fidelity transient data. However, as research needs grow beyond standardized workflows, scientists and engineers increasingly require open, adaptable analysis methods.

PyRth is built upon the comprehensive research conducted during my PhD, ensuring that it incorporates cutting-edge thermal analysis techniques and scientifically validated methodologies. It integrates directly with Python-based open-source research environments, supports data from both commercial and custom-built measurement setups, and applies state-of-the-art algorithms to produce reliable structure functions and related thermal metrics. As a result, PyRth empowers the scientific community to conduct reproducible, transparent, and innovative thermal analyses, advancing both fundamental research and applied device engineering.

## ✨ Features

- **Data Processing**: Analyze thermal transient measurement data from CSV files or passed as NumPy arrays.
- **Advanced Algorithms**: Utilize scientifically validated cutting-edge algorithms for precise thermal analysis.
- **Script Integration**: Easily embed PyRth into your Python scripts for automated processing.
- **Multiple Output Formats**: Generate results in images and CSV files for comprehensive examination.
- **Open Source**: Fully accessible source code for transparency and community contributions.
- **Cross-Platform**: Compatible with Windows, macOS, and Linux systems.

## 🚀 Installation

### For Normal Usage

You can install PyRth using `pip` directly from PyPI:

```bash
pip install PyRth
```

### For Development

If you want to contribute or modify the code, install PyRth in editable mode:

```bash
git clone https://github.com/nizie002/PyRth
cd PyRth
pip install --editable .
```

## 🛠️ Usage

### Quick Start

```python
import PyRth
```

### Examples

Below is a basic example to get you started with PyRth. The repository includes test data located in the tests/data directory. For this data, you can use a special input_mode to ensure proper processing. For more detailed examples please refer to the tests directory.

```python
params = {
                "data": data, # insert numpy array with test data here
                "output_dir": "tests/output/basic_test",
                "label": "MOSFET_tim_basic_sobhy",
                "input_mode": "volt",
                "deconv_mode": "bayesian",
                "bay_steps": 1000,
                "struc_method": "sobhy",
                "lower_fit_limit": 5e-4,
                "upper_fit_limit": 1e-3,
                "calib": calib # insert numpy array with calibration data here
            }

eval_instance = PyRth.Evaluation()
modules = eval_instance.standard_module(params)
eval_instance.save_as_csv()
eval_instance.save_figures()

```

### Plot Handling

PyRth generates and saves plots based on the processed data. To ensure efficient data processing, these plots are created in a non-interactive Matplotlib environment and closed immediately after generation.

If interactive plots are created before using PyRth, they will also be suppressed. However, if you want to display your plots, add the following code to your script:

```python
import matplotlib
matplotlib.use("TkAgg")
```

### Basic Documentation

**Usage Flow**

From a user's perspective, using PyRth involves the following steps:

1. **Import PyRth**: Start by importing the PyRth package into your Python script.
2. **Instantiate Evaluation**: Create an instance of the `Evaluation` class.
3. **Configure Parameters**: Define the parameters for your evaluation, such as input data, output directory, and analysis methods.
4. **Add Modules**: Incorporate various evaluation modules (e.g., theoretical, standard, bootstrap) using dedicated methods.
5. **Run Evaluation**: Execute the desired evaluation methods with the configured parameters.
6. **Generate Outputs**: Save and visualize the results, including CSV files and generated figures.

PyRth's streamlined workflow allows users to efficiently process and analyze thermal transient data with minimal setup.

**Parameter Configuration and Evaluation Management**

PyRth offers flexible configuration through various parameters, enabling users to tailor the evaluation process to their specific needs. Parameters are categorized into Data Processing, Input/Output, and Power Settings. For instance, `log_time_tize` controls the number of points in the impedance curve, `deconv_mode` chooses between Fourer and Bayesian Deconvolution and identification using the Lasso, and `struc_method` selects the method for structure function calculation. I/O parameters like `data`, `output_dir`, and `label` manage data sources and output destinations, while Power Settings such as `power_step`, `is_heating`, and `optical_power` adjust power-related measurements.

When conducting more complex analysis, PyRth offers the possibility to organize procedure into different evaluation, which can each be combined from different modules. In each `Evaluation` instance, PyRth handles the functionality independently through dedicated methods like `add_theoretical_module`, `add_standard_module`, `add_bootstrap_module`, and others. Within each `Evaluation` instance all results are combined into the same plot, to allow easy comparison of results if demanded. This modular approach ensures that each evaluation type operates with its specific parameters without conflict.

**Parameter Dictionaries**

PyRth offers flexible configuration through various parameters, e.g.:

**Data Processing Parameters:**

- `log_time_size`: Number of points in impedance curve (default: 250)
- `deconv_mode`: Enable Bayesian deconvolution (default: True)
- `struc_method`: Method for structure function calculation (options: "sobhy", "lanczos", "boor_golub", "khatwani", "polylong")

**Input/Output Parameters:**

- `data`: Field should contain the main data, as an example, use the data in the tests directory
- `output_dir`: Directory for output files
- `label`: Label for output files

**Power Settings:**

- `power_step`: Power step in Watts (default: 1.0)
- `is_heating`: Analyze Heating or Cooling transients
- `optical_power`: For LED testing to subtract optical power in W

For a complete list of parameters and their descriptions, refer to the `transient_defaults.py` file in the source code.

## 🔬 Evaluation Methods

PyRth offers a suite of evaluation modules for comprehensive thermal analysis:

1. **Standard Module**

   - Performs default analysis to extract impedance and structure functions.
   - Ideal for quick assessments and initial data exploration.

2. **Evaluation Set Module**

   - Enables batch processing over various parameters or datasets.
   - Suitable for systematic studies requiring multiple evaluations.

3. **Bootstrap Module**

   - Implements statistical bootstrap methods.
   - Assesses variability and confidence intervals of thermal properties.

4. **Optimization Module**

   - Optimizes structure functions to fit impedance data.
   - Adjusts thermal resistance and capacitance for detailed layer-wise characterization.

5. **Theoretical Module**

   - Generates theoretical thermal behavior models.
   - Aids in validating experimental data against expected results.

6. **Comparison Module**

   - Compares multiple evaluation results or datasets.
   - Useful for benchmarking and identifying characteristic differences.

7. **Temperature Prediction Module**
   - Predicts temperature profiles based on evaluated properties.
   - Essential for thermal management and design optimization.

## 🛠️ Contributing

Contributions are welcome! To contribute to PyRth, please follow these steps:

1. **Fork the Repository**: Click the fork button on the top right of this page to create your own copy.
2. **Clone the Fork**: Clone your forked repository to your local machine using:
   ```bash
   git clone https://github.com/your-username/PyRth.git
   ```
3. **Create a Branch**: Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Commit Changes**: Make your changes and commit them with clear messages:
   ```bash
   git commit -m "Add feature: your feature description"
   ```
5. **Push to Fork**: Push your changes to your forked repository:
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Submit a Pull Request**: Navigate to the original repository and submit a pull request detailing your changes.

### Guidelines

- **Code Standards**: Ensure your code follows the existing style and conventions.
- **Documentation**: Update or add documentation as necessary.
- **Tests**: Include tests for new features or bug fixes.
- **Issue Tracking**: Check existing issues or create a new one to discuss your proposed changes.

Thank you for contributing to PyRth!

## 📄 Publications

PyRth is based on extensive research. Below are key publications that demonstrate its capabilities and development. For further mathematical background, please refer to these publications.

1. N. J. Ziegeler and S. Schweizer, "Lanczos-based Foster-to-Cauer Transformation for Network Identification by Deconvolution," 2024 30th International Workshop on Thermal Investigations of ICs and Systems (THERMINIC), Toulouse, France, 2024, pp. 1-6, [doi: 10.1109/THERMINIC62015.2024.10732055](https://doi.org/10.1109/THERMINIC62015.2024.10732055).

2. N. J. Ziegeler, P. W. Nolte, and S. Schweizer, "Tridiagonal Approaches for Network Identification by Deconvolution," 2023 29th International Workshop on Thermal Investigations of ICs and Systems (THERMINIC), Budapest, Hungary, 2023, pp. 1-6, [doi: 10.1109/THERMINIC60375.2023.10325879](https://doi.org/10.1109/THERMINIC60375.2023.10325879).

3. N. J. Ziegeler, P. W. Nolte, and S. Schweizer, "Accuracy Comparison of T3ster-Master and Optimization-based Network Identification," 2023 29th International Workshop on Thermal Investigations of ICs and Systems (THERMINIC), Budapest, Hungary, 2023, pp. 1-6, [doi: 10.1109/THERMINIC60375.2023.10325681](https://doi.org/10.1109/THERMINIC60375.2023.10325681).

4. N. J. Ziegeler, P. W. Nolte, and S. Schweizer, "J-Fraction Approach for Calculating Thermal Structure Functions," 2022 28th International Workshop on Thermal Investigations of ICs and Systems (THERMINIC), Dublin, Ireland, 2022, pp. 1-4, [doi: 10.1109/THERMINIC57263.2022.9950656](https://doi.org/10.1109/THERMINIC57263.2022.9950656).

5. N. J. Ziegeler, P. W. Nolte, and S. Schweizer, "Optimization-Based Network Identification for Thermal Transient Measurements," _Energies_, vol. 14, no. 22, p. 7648, Nov. 2021, [doi: 10.3390/en14227648](https://doi.org/10.3390/en14227648).

6. N. J. Ziegeler, P. W. Nolte, and S. Schweizer, "Quantitative Performance Comparison of Thermal Structure Function Computations," _Energies_, vol. 14, no. 21, p. 7068, Oct. 2021, [doi: 10.3390/en14217068](https://doi.org/10.3390/en14217068).

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📫 Contact

Email: ziegeler.nilsjonas@fh-swf.de

## 🌟 Acknowledgements

I would like to express my sincere gratitude to the Faculty of Electrical Power Engineering at the South Westphalia University of Applied Sciences (Fachhochschule Südwestfalen) in Soest for their academic support. My appreciation also extends to the Fraunhofer Application Center for Inorganic Phosphors in Soest, part of the Fraunhofer Institute for Microstructure of Materials and Systems IMWS, for their research collaboration. Additionally, I thank HELLA GmbH & Co. KGaA, now part of FORVIA, for their practical insights and support.
