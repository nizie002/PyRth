Evaluation Modules Overview
===========================

PyRth provides several specialized modules within the :py:class:`~PyRth.transient_scripts.Evaluation` class to perform different types of thermal transient analysis. Each module accepts a dictionary of parameters to control its behavior. Default parameters are defined in :py:mod:`~PyRth.transient_defaults` and can be overridden by including them in the dictionary passed to the module method.

See the :ref:`Default Configuration <default-configuration-label>` for a full list of parameters.

Click on the links below for detailed documentation on each module:

.. toctree::
   :maxdepth: 1

   evaluation_standard
   evaluation_set
   evaluation_bootstrap
   evaluation_optimization
   evaluation_theoretical
   evaluation_comparison
   evaluation_prediction

