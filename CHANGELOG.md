# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.0] - 2025-07-21

### Added

- CHANGELOG and CONTRIBUTING documentation files
- Right sidebar table of contents for improved documentation navigation
- DeepWiki badge to README
- Support for hybrid deconvolution mode in Evaluation class
- Cross-validation support for Lasso deconvolution with `lasso_cv_folds` parameter
- Enhanced Lasso deconvolution parameters: alpha, max iterations, tolerance, and cross-validation settings
- Support for saving non-numeric data in CSV format via CSVExporter
- Scikit-learn and numba to intersphinx mapping in documentation
- Secondary y-axis for differences in BackwardsImp figures
- Weighted Lasso support in hybrid mode processing

### Changed

- Enhanced documentation structure and styling throughout
- Improved README and changelog.rst for better clarity
- Updated documentation dependencies and removed obsolete requirements files
- Corrected extra_requirements syntax in .readthedocs.yaml
- Reorganized classifiers in pyproject.toml
- Refactored user guide structure with new sections: "Getting Started", "Usage", and "Troubleshooting"
- Removed outdated user guide sections: "Advanced Workflows", "Calibration Guide", "Data Extraction", and "Data Preparation"
- Enhanced installation instructions for clarity
- Increased DPI for saved figures to improve quality via FigureExporter
- Reorganized figure registry with prefixes for improved ordering and clarity in filenames
- Changed marker style to 'x' for BackwardsImpFigure plot
- Reduced linewidth in BackwardsImpDerivFigure and BackwardsImpFigure for improved visibility
- Updated BackwardsImp figures titles and labels to reflect differences and improve clarity
- Improved overlap handling in data plotting
- Enhanced error handling in tests with better directory cleanup for permission errors
- Updated deconvolution parameters and methods for MOSFET tests
- Refined alpha range and hybrid mode bay_steps for improved performance
- Updated time constant calculation in TransientOptimizer to scale with theoretical log time
- Lasso deconvolution tolerance adjusted from 1e-4 to 1e-5 for improved convergence

### Fixed

- DOI badge link in README.md now points to the latest identifier
- Corrected LaTeX formatting in y-axis label of DiffStrucFigure
- Added missing scikit-learn dependency in pyproject.toml
- Corrected typo from 'gaus_curve' to 'gauss_curve' in Evaluation class
- Bootstrap comparison time variable name changed from 'boot_imp_time' to 'boot_deriv_time'
- Renamed LED_lasso to TEMP_lasso in test cases for clarity
- Updated pyproject.toml license format to use modern PEP 639 SPDX format

### Removed

- instructions.md file to streamline documentation and reduce redundancy
- Obsolete requirements files

## [1.1.0] - 2025-05-03

### Added

- Support for Lasso deconvolution method using scikit-learn

### Changed

- Improved documentation organization
- Enhanced plotting capabilities
- conv_mode renamed to input_mode
- deconvolution is now controlled via deconv_mode parameter with "bayesian", "fourier", and "lasso"

### Fixed

- Various bug fixes and figure cleanup
- Multiple module in one evaluation now plot into the same window
- T3ster import mode works now

## [1.0.0] - 2025-03-02

### Added

- Initial release
- Support for thermal transient data analysis
- Network Identification by Deconvolution (NID) methods
- Structure function calculation methods: Sobhy, Lanczos, De Boor-Golub, Khatwani, and polynomial long division
- Support for Bayesian and Fourier deconvolution
- Multiple evaluation modules: Standard, Evaluation Set, Bootstrap, Optimization, Theoretical, Comparison
- CSV and image export capabilities
