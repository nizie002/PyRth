PyRth documentation
====================

PyRth is a Python package for analyzing thermal transient measurements using Network Identification by Deconvolution (NID) methods as well as optimization approaches. It enables thermal characterization of electronic components and systems through time constant spectrum and structure function analysis.

The documentation provides a comprehensive guide to using the PyRth package, including installation instructions, usage examples, a guide for performing thermal transient analysis, and detailed API references. For those interested in the mathematical foundations, the theory section explains the algorithms and methods implemented in PyRth, including deconvolution methods, network construction, structure function algorithms, and optimization techniques.

If you spot any issues or have suggestions for improvements, please feel free to open an issue on the GitHub repository. We welcome contributions and feedback from the community.

For more information, please refer to the following sections:

.. |UserGuideText| replace:: **User Guide**
.. _UserGuideText: user_guide.html
.. |InstallationText| replace:: **Installation**
.. _InstallationText: installation.html
.. |UsageText| replace:: **Basic Usage**
.. _UsageText: usage.html
.. |EvaluationModulesText| replace:: **Evaluation Modules**
.. _EvaluationModulesText: evaluation_modules_overview.html
.. |ApiReferenceText| replace:: **API Reference**
.. _ApiReferenceText: api.html
.. |TheoryText| replace:: **Theory**
.. _TheoryText: theory.html
.. |ChangelogText| replace:: **Changelog**
.. _ChangelogText: changelog.html


Documentation Sections
--------------------------

|InstallationText|_: Get started with PyRth quickly by following the installation guide. This section covers prerequisites, installation methods, and troubleshooting tips to ensure you have PyRth properly set up in your environment, whether you're using pip, conda, or installing from source.

|UsageText|_: Learn the fundamental operations of PyRth through practical examples. This section introduces the core concepts and basic workflows for thermal transient analysis, providing code snippets to help you understand how to import data, run analyses, and visualize results.

|UserGuideText|_: Dive deeper into PyRth's capabilities with comprehensive tutorials covering various aspects of thermal analysis. From data preparation to advanced workflows, this section walks you through real-world applications and best practices to help you make the most of PyRth's features.

|EvaluationModulesText|_: Explore the different evaluation modules available in PyRth for specialized thermal analysis tasks. This section explains each module's purpose, capabilities, and appropriate use cases, helping you select the right tools for your specific thermal characterization needs.

|ApiReferenceText|_: Find detailed documentation of all PyRth's classes, methods, and functions. This comprehensive reference provides syntax, parameters, return values, and examples for each component of the library, serving as an essential resource for developers integrating PyRth into their own applications.

|TheoryText|_: Understand the mathematical foundations and algorithms that power PyRth. This section provides in-depth explanations of deconvolution methods, network construction techniques, structure function algorithms, and optimization approaches, giving you insights into the underlying principles of thermal analysis.

|ChangelogText|_: View the complete history of PyRth versions, including new features, improvements, bug fixes, and breaking changes. The changelog helps you stay informed about the project's evolution and understand what changes might affect your existing code.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   usage
   user_guide
   evaluation_modules_overview
   api
   theory
   changelog