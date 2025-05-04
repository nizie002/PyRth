# Contributing to PyRth

Thank you for your interest in contributing to PyRth! This guide will help you get started with contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our code of conduct: be respectful, considerate, and collaborative.

## How to Contribute

### Reporting Bugs

- Check if the bug has already been reported in the [Issues](https://github.com/nizie002/PyRth/issues)
- If not, create a new issue with a clear title and description
- Include steps to reproduce, expected behavior, and actual behavior
- Add relevant code snippets or error messages

### Suggesting Features

- Check if the feature has already been suggested in the [Issues](https://github.com/nizie002/PyRth/issues)
- If not, create a new issue with a clear title and description
- Explain why this feature would be beneficial

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests to ensure your changes don't break existing functionality
5. Update documentation if necessary
6. Update the CHANGELOG.md file in the "Unreleased" section
7. Commit your changes with clear, descriptive commit messages
8. Push to your branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## Documentation Guidelines

### Code Documentation

- Use docstrings for functions, classes, and methods
- Follow NumPy/SciPy docstring format
- Include type hints where appropriate

### Documenting Changes

When making changes to the codebase, it's important to document them properly:

1. **CHANGELOG.md**: Add your changes under the "Unreleased" section, categorized as:

   - `Added` for new features
   - `Changed` for changes in existing functionality
   - `Deprecated` for soon-to-be removed features
   - `Removed` for now removed features
   - `Fixed` for any bug fixes
   - `Security` in case of vulnerabilities

2. **Documentation Updates**: If your changes affect user-facing functionality:

   - Update the relevant documentation in the `docs/` directory
   - Add examples if appropriate

3. **Version Bumping**: Do not bump version numbers in your PR. The maintainers will handle version bumps.

## Development Setup

1. Clone your fork of the repository
2. Install in development mode:
   ```
   pip install --editable .
   ```
3. Install development dependencies:
   ```
   pip install -r docs/requirements.txt
   ```

## Testing

- Run the test suite with unittest
- Add new tests for new functionality
- Ensure all tests pass before submitting a PR

## Questions?

Feel free to reach out if you have any questions about contributing to PyRth. Thank you for helping make PyRth better!
