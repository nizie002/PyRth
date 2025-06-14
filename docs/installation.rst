Installation
============

PyRth is a Python package for analyzing thermal transient measurements using
:doc:`Network Identification by Deconvolution (NID) methods <theory/nid_overview>`.
It's compatible with Windows, macOS, and Linux systems.

.. hint::
   Not familiar with NID? See the :doc:`theory overview <theory/nid_overview>`.

Standard Installation
---------------------

Install PyRth with pip directly from PyPI:

.. code-block:: bash

   pip install PyRth

This command also works if you are using a Conda environment by using ``pip`` from within the Conda environment.

This is the recommended method for most users who want to use PyRth for thermal analysis. See :doc:`user_guide/usage` for a first walkthrough.

Development Installation
------------------------

If you want to contribute to PyRth or modify the code, install it in editable mode:

.. code-block:: bash

   git clone https://github.com/nizie002/PyRth
   cd PyRth
   pip install --editable .

This installation method allows you to make changes to the source code and have them immediately reflected without reinstalling the package.

To explore available modules, see the :doc:`API reference <api>`.

Requirements
------------

PyRth requires Python 3.11 or higher and depends on several scientific computing libraries.

Core Dependencies
-----------------

The following Python packages are installed automatically with PyRth. Each plays a specific role in the thermal transient analysis pipeline:

* :external+numpy:mod:`numpy` – for efficient array and matrix operations used throughout PyRth's data structures and numerical routines.
* :external+scipy:mod:`scipy` – provides certain algorithms needed during the analysis.
* :external+matplotlib:mod:`matplotlib` – used to visualize RC networks, temperature curves, evaluation results, and structure functions.
* :numba-doc:`numba <>` – accelerates core numerical loops (e.g., differentiation, deconvolution) with just-in-time (JIT) compilation.
* :gmpy2-doc:`gmpy2 <>` – allows PyRth to perform arbitrary-precision arithmetic for some Foster-to-Cauer transformations.
* :external+scikit-learn:mod:`sklearn` – used for sparse regression techniques such as :class:`sklearn.linear_model.LassoCV` to extract reduced models.

These are installed automatically when running ``pip install PyRth``.


**Development Dependencies**

For testing and contributing:

* :mod:`parameterized` — for parameterized testing

**Documentation Dependencies**

To build the documentation locally:

* :mod:`sphinx`
* :mod:`sphinx_rtd_theme`
* :mod:`sphinx_proof`
* :mod:`sphinx.ext.autodoc`
* :mod:`sphinx.ext.napoleon`
* :mod:`sphinx.ext.intersphinx`
* :mod:`sphinx.ext.mathjax`

You can install all of these with:

.. code-block:: bash

   pip install .[dev,docs]

Verifying Installation
----------------------

After installation, verify that PyRth is correctly installed:

.. code-block:: python

   import PyRth
   print("PyRth successfully installed!")

To run a test evaluation, see the :doc:`Getting Started Guide <user_guide/getting_started>`.
