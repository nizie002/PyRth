# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Right-side floating table of contents in documentation

### Changed

- Enhanced installation documentation with clear separation of core, development, and documentation dependencies

### Fixed

- Documentation structure for better readability

## [1.1.0] - 2025-05-03

### Added

- Support for Lasso deconvolution method using scikit-learn
- J-Fraction approach for calculating thermal structure functions
- Temperature prediction module

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
