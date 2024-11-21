# PyRth

<img src="assets/images/logo.png" alt="PyRth Logo" width="400"/>

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)](https://www.python.org/downloads/)
[![Documentation Status](https://readthedocs.org/projects/pyRth/badge/?version=latest)](https://pyRth.readthedocs.io/en/latest/?badge=latest)
[![Downloads](https://img.shields.io/pypi/dm/pyRth)](https://pypi.org/project/pyRth/)

---

## 📖 Table of Contents

- [Description](#description)
- [Publications](#relevant-publications)
- [Features](#features)
- [Evaluation Methods](#evaluation-methods)
- [Installation](#installation)
- [Usage](#usage)
  - [Quick Start](#quick-start)
  - [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)
- [Acknowledgements](#acknowledgements)

---

## 📚 Description

**PyRth** is an open-source Python package for evaluating thermal transient measurement data, such as those obtained from devices like the T3ster. It processes LED voltage data using specialized algorithms to extract detailed thermal characteristics such as the thermal structure function.

This tool serves as a modern and flexible alternative to proprietary evaluation software provided with thermal transient measurement equipment. PyRth optinally outputs results as images and CSV files, facilitating easy analysis and visualization.

---

## 📄 Publications

PyRth is based on extensive research. Below are key publications that demonstrate its capabilities and development. For further mathematical background, please refer to these publications.

1. N. J. Ziegeler and S. Schweizer, "Lanczos-based Foster-to-Cauer Transformation for Network Identification by Deconvolution," 2024 30th International Workshop on Thermal Investigations of ICs and Systems (THERMINIC), Toulouse, France, 2024, pp. 1-6, [doi: 10.1109/THERMINIC62015.2024.10732055](https://doi.org/10.1109/THERMINIC62015.2024.10732055).

2. N. J. Ziegeler, P. W. Nolte, and S. Schweizer, "Tridiagonal Approaches for Network Identification by Deconvolution," 2023 29th International Workshop on Thermal Investigations of ICs and Systems (THERMINIC), Budapest, Hungary, 2023, pp. 1-6, [doi: 10.1109/THERMINIC60375.2023.10325879](https://doi.org/10.1109/THERMINIC60375.2023.10325879).

3. N. J. Ziegeler, P. W. Nolte, and S. Schweizer, "Accuracy Comparison of T3ster-Master and Optimization-based Network Identification," 2023 29th International Workshop on Thermal Investigations of ICs and Systems (THERMINIC), Budapest, Hungary, 2023, pp. 1-6, [doi: 10.1109/THERMINIC60375.2023.10325681](https://doi.org/10.1109/THERMINIC60375.2023.10325681).

4. N. J. Ziegeler, P. W. Nolte, and S. Schweizer, "J-Fraction Approach for Calculating Thermal Structure Functions," 2022 28th International Workshop on Thermal Investigations of ICs and Systems (THERMINIC), Dublin, Ireland, 2022, pp. 1-4, [doi: 10.1109/THERMINIC57263.2022.9950656](https://doi.org/10.1109/THERMINIC57263.2022.9950656).

5. N. J. Ziegeler, P. W. Nolte, and S. Schweizer, "Optimization-Based Network Identification for Thermal Transient Measurements," *Energies*, vol. 14, no. 22, p. 7648, Nov. 2021, [doi: 10.3390/en14227648](https://doi.org/10.3390/en14227648).

6. N. J. Ziegeler, P. W. Nolte, and S. Schweizer, "Quantitative Performance Comparison of Thermal Structure Function Computations," *Energies*, vol. 14, no. 21, p. 7068, Oct. 2021, [doi: 10.3390/en14217068](https://doi.org/10.3390/en14217068).

---

## ✨ Features

- **Data Processing**: Analyze thermal transient measurement data from CSV files or passed as NumPy arrays.
- **Advanced Algorithms**: Utilize scientifically validated cutting-edge algorithms for precise thermal analysis.
- **Script Integration**: Easily embed PyRth into your Python scripts for automated processing.
- **Multiple Output Formats**: Generate results in images and CSV files for comprehensive examination.
- **Open Source**: Fully accessible source code for transparency and community contributions.
- **Cross-Platform**: Compatible with Windows, macOS, and Linux systems.

---

## 🔬 Evaluation Methods

Therminate offers a suite of evaluation methods for comprehensive thermal analysis:

1. **Standard Evaluation**
   - Performs default analysis to extract impedance and structure functions.
   - Ideal for quick assessments and initial data exploration.

2. **Evaluation Set**
   - Enables batch processing over various parameters or datasets.
   - Suitable for systematic studies requiring multiple evaluations.

3. **Bootstrap Evaluation**
   - Implements statistical bootstrap methods.
   - Assesses variability and confidence intervals of thermal properties.

4. **Optimization Evaluation**
   - Optimizes structure functions to fit impedance data.
   - Adjusts thermal resistance and capacitance for detailed layer-wise characterization.

5. **Theoretical Evaluation**
   - Generates theoretical thermal behavior models.
   - Aids in validating experimental data against expected results.

6. **Comparison Evaluation**
   - Compares multiple evaluation results or datasets.
   - Useful for benchmarking and identifying characteristic differences.

7. **Temperature Prediction Evaluation**
   - Predicts temperature profiles based on evaluated properties.
   - Essential for thermal management and design optimization.

---

## 🚀 Installation

not veryfied - does not work yet, unpublished

You can install PyRth using `pip`:

```bash
pip install PyRth
git clone https://github.com/yourusername/therminate.git
cd therminate
python setup.py install

```

## 🛠️ Usage

### Quick Start

```python
import PyRth as th

+++++

TODO


```


### Example

```bash
xyz

```


## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

## 📫 Contact

Email: ziegeler.nilsjonas@fh-swf.de
GitHub Issues: PyRth Issues

## 🌟 Acknowledgements

I would like to express my sincere gratitude to the Faculty of Electrical Power Engineering at the South Westphalia University of Applied Sciences (Fachhochschule Südwestfalen) in Soest for their academic support. My appreciation also extends to the Fraunhofer Application Center for Inorganic Phosphors in Soest, part of the Fraunhofer Institute for Microstructure of Materials and Systems IMWS, for their research collaboration. Additionally, I thank HELLA GmbH & Co. KGaA, now part of FORVIA, for their practical insights and support.



