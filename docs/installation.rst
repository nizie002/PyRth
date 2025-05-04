Installation
==============

PyRth is a Python package for analyzing thermal transient measurements using Network Identification by Deconvolution (NID) methods. It's compatible with Windows, macOS, and Linux systems.

Standard Installation
------------------------

Install PyRth with pip directly from PyPI:

.. code-block:: bash

   pip install PyRth

This is the recommended method for most users who want to use PyRth for thermal analysis.

Development Installation
---------------------------

If you want to contribute to PyRth or modify the code, install it in editable mode:

.. code-block:: bash

   git clone https://github.com/nizie002/PyRth
   cd PyRth
   pip install --editable .

This installation method allows you to make changes to the source code and have them immediately reflected without reinstalling the package.

Requirements
---------------

PyRth requires Python 3.11 or higher and depends on several scientific computing libraries.

**Core Dependencies**


These libraries are required for the core functionality of PyRth and will be automatically installed when using pip:

* numpy
* scipy
* matplotlib
* numba
* gmpy2
* scikit-learn

**Development Dependencies**

These libraries are needed for development, testing, and contributing to PyRth:

* parameterized - for parameterized testing

**Documentation Dependencies**

These libraries are needed for building and maintaining the documentation:

* sphinx - documentation generator
* sphinx_rtd_theme - Read the Docs theme for Sphinx
* sphinx_proof - for mathematical proofs in documentation
* sphinx.ext.autodoc - for API documentation generation
* sphinx.ext.napoleon - for NumPy/Google style docstrings
* sphinx.ext.intersphinx - for cross-referencing external documentation
* sphinx.ext.mathjax - for rendering mathematical equations

When installing via pip, the core dependencies will be automatically installed if not already present in your Python environment. Development and documentation dependencies may need to be installed separately if you plan to contribute to the project.

Verifying Installation
--------------------------

After installation, you can verify that PyRth is correctly installed by importing it in Python:

.. code-block:: python

   import PyRth
   
   # If no errors occur, the installation was successful
   print("PyRth successfully installed!")
