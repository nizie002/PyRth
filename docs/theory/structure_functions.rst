
.. _structure_functions:

Structure Functions
==========================

The lumped Foster- and Cauer-ladders used so far can be viewed as *discrete*
approximations of a **one-dimensional distributed RC line**.  
This section shows how classical transmission-line theory maps onto thermal
structure functions and how the *cumulative* and *differential* structure
functions emerge naturally for **non-uniform** RC lines.

.. contents::
   :local:
   :depth: 1


Transmission-Line Basics
------------------------
A transmission line is a *distributed two-port*: its series impedance density
:math:`z(x)` and shunt admittance density :math:`y(x)` are smeared
continuously along the spatial coordinate :math:`x`.

.. figure:: /_static/transmission_line.png
   :width: 35 %
   :align: center

   Infinitesimal element of a general transmission line.

For an electrical wire

.. math::

   z(x)=r+l\,s,
   \qquad
   y(x)=g+c\,s,

with :math:`s` the complex Laplace variable.  The *Telegrapher* equation

.. math::

   \frac{\mathrm{d}^2 V}{\mathrm{d}x^2}-z\,y\,V=0

has the general solution

.. math::

   V(x)=V_1e^{-\gamma x}+V_2e^{\gamma x},
   \qquad
   \gamma=\sqrt{zy}=\alpha+\mathrm{i}\beta.

Here :math:`\alpha` describes attenuation, :math:`\beta` the phase shift,
and

.. math::

   Z_0=\sqrt{\frac{z}{y}}

is the *characteristic impedance*.  
Driving a load :math:`Z_L` through a length :math:`\Delta x` gives

.. math::

   Z_\text{in}=
   \overline{Z}_0\;
   \frac{Z_L\cosh(\gamma\Delta x)+\overline{Z}_0\sinh(\gamma\Delta x)}
        {\overline{Z}_0\cosh(\gamma\Delta x)+Z_L\sinh(\gamma\Delta x)}.


Uniform RC Line
---------------
For purely diffusive heat flow the electrical analogue keeps *resistance*
in series and *capacitance* in shunt:

.. math::

   z=r,\qquad y=s\,c
   \;\;\Longrightarrow\;\;
   \gamma=\sqrt{s\,r\,c},
   \quad
   Z_0=\sqrt{\frac{r}{s\,c}}.

On a uniform line the local relations are

.. math::

   \mathrm{d}V=-\,r\,I\,\mathrm{d}x,
   \qquad
   \mathrm{d}I=-\,c\,\frac{\partial V}{\partial t}\,\mathrm{d}x,

which combine to the *heat equation*

.. math::

   \frac{\partial V}{\partial t}=
   \frac{1}{r\,c}\,
   \frac{\partial^2 V}{\partial x^2}.

Injecting a charge :math:`Q` at :math:`x=0` gives

.. math::

   V(x,t)=\frac{Q/c}{
           2\,\sqrt{\pi t/(r\,c)}
          }\,
          \exp\!\Bigl[-x^2/(4t/(r\,c))\Bigr],

identical in shape to a thermal **Green’s function**.


Non-Uniform RC Line ⇔ Structure Function
------------------------------------------------
Real devices do *not* possess constant material properties; both resistance
density :math:`r(x)` and capacitance density :math:`c(x)` vary along the
heat path.  Define the *cumulative* quantities

.. math::

   R_\Sigma(x)=\int_0^x r(\xi)\,\mathrm{d}\xi,
   \qquad
   C_\Sigma(x)=\int_0^x c(\xi)\,\mathrm{d}\xi.

These are exactly the axes of the **cumulative structure function**
obtained from the Cauer ladder in network identification by deconvolution.

Differential and cumulative forms
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* **Differential structure function**

  .. math::

     \sigma\!\bigl(R_\Sigma(x)\bigr)=
     \frac{c(x)}{r(x)}.

  It equals the ratio of local densities expressed against cumulative
  resistance.

* **Cumulative structure function**  
  Also called the *Protonotarios–Wing* function,

  .. math::

     C_\Sigma(R_\Sigma)=
     \int_{0}^{R_\Sigma}\sigma(R'_\Sigma)\,\mathrm{d}R'_\Sigma
     \;=\;
     \int_{0}^{x(R_\Sigma)} c(x)\,\mathrm{d}x.

Voltage (temperature) evolution
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
With spatially varying densities the local balance becomes

.. math::

   \frac{\partial V}{\partial t}=
   \frac{1}{c(x)}
   \frac{\partial}{\partial x}
   \Bigl[\frac{1}{r(x)}\,
         \frac{\partial V}{\partial x}\Bigr].

In cumulative-resistance coordinates

.. math::

   \frac{\partial V}{\partial t}=
   \frac{1}{\sigma(R_\Sigma)}
   \frac{\partial^2 V}{\partial R_\Sigma^2}.

A closed-form solution is known only for special profiles
(:math:`\sigma=\text{const.}` recovers the uniform line),
but the equation underlies **structure-function analysis**:
the measured pair
:math:`\bigl(R_\Sigma,C_\Sigma\bigr)` summarises *all*
one-dimensional non-uniform RC lines that replicate the same
driving-point thermal behaviour.

Relation to NID workflow
^^^^^^^^^^^^^^^^^^^^^^^^
1. NID converts the step response to a **Foster ladder** (time-constant
   spectrum).
2. Foster → Cauer transformation produces a *series* RC ladder whose
   running sums reproduce :math:`R_\Sigma` and :math:`C_\Sigma`.
3. Plotting :math:`C_\Sigma(R_\Sigma)` yields the **cumulative structure
   function**; its slope is the differential structure function
   :math:`\sigma`.

Hence the structure function is *nothing else* than the physical picture
of heat flow through a **non-uniform RC line**.