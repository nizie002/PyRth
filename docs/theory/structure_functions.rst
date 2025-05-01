Structure Functions
=====================

This document explains the theory and implementation of structure functions in PyRth. Structure functions are powerful representations that convert the time constant spectrum into a thermal equivalent circuit, enabling physical interpretation of the heat flow path.

Foster to Cauer Network Transformation
-------------------------------------------

After obtaining the time constant spectrum through deconvolution, PyRth transforms it into meaningful thermal structure functions through a Foster to Cauer network transformation.

Foster Thermal Network
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The time constant spectrum represents a Foster thermal network, which consists of parallel RC elements:

.. math::

   Z_{th}(s) = \sum_{i=1}^{n} \frac{R_i}{1 + s \tau_i} = \sum_{i=1}^{n} \frac{R_i}{1 + s R_i C_i}

Where:
- :math:`R_i` are the thermal resistances from the time constant spectrum
- :math:`C_i` are the thermal capacitances, calculated as :math:`C_i = \tau_i / R_i`
- :math:`s` is the Laplace variable

The Foster network has simple mathematical properties but lacks physical meaning in terms of heat flow paths.

Cauer Thermal Network
^^^^^^^^^^^^^^^^^^^^^^^

The Cauer (or continued fraction) network represents a ladder-type circuit that corresponds to the physical heat flow path:

.. math::

   Z_{th}(s) = \frac{1}{sC_1 + \frac{1}{R_1 + \frac{1}{sC_2 + \frac{1}{R_2 + \ldots}}}}

This representation provides a one-dimensional model of heat flow, where each RC pair corresponds to a physical layer along the heat path.

Structure Function Calculation Methods
----------------------------------------

PyRth implements multiple methods for transforming the Foster network to the Cauer representation. The method is selected through the `struc_method` parameter.


Practical Interpretation of Structure Functions
----------------------------------------------------

Structure functions provide valuable insights into the thermal system:

1. **Layer Identification**
   
   Peaks in the differential structure function often correspond to material interfaces or geometric changes in the thermal path.

2. **Thermal Bottlenecks**
   
   Steep rises in the cumulative structure function indicate high thermal resistance regions (thermal bottlenecks).

3. **Component Sizing**
   
   The thermal capacitance axis correlates with the volume of materials, helping identify component sizes.

4. **Boundary Conditions**
   
   The final plateau in the cumulative structure function represents the thermal resistance to ambient.