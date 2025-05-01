API Reference
================

Parameter Configuration
--------------------------

.. _default-configuration-label:

Default Configuration Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following parameters define PyRth's default behavior and can be overridden by passing values in the parameter dictionary to evaluation methods.

.. automodule:: PyRth.transient_defaults
   :member-order: bysource
   :no-undoc-members:

Evaluation Methods
---------------------

.. autoclass:: PyRth.Evaluation
   :noindex:
   :no-members:
   :no-undoc-members:
   :no-special-members:

Core Methods
~~~~~~~~~~~~~~

.. automethod:: PyRth.Evaluation.standard_module
.. automethod:: PyRth.Evaluation.standard_module_set
.. automethod:: PyRth.Evaluation.bootstrap_module
.. automethod:: PyRth.Evaluation.optimization_module
.. automethod:: PyRth.Evaluation.theoretical_module
.. automethod:: PyRth.Evaluation.comparison_module
.. automethod:: PyRth.Evaluation.temperature_prediction_module

Utility Methods
~~~~~~~~~~~~~~~~~

.. automethod:: PyRth.Evaluation.save_as_csv
.. automethod:: PyRth.Evaluation.save_figures
.. automethod:: PyRth.Evaluation.save_all
