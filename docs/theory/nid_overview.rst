.. _nid_overview:

Overview of Network Identification by Deconvolution
====================================================================

.. _nid_introduction:

Introduction
-----------------------------------------------
When a device suddenly receives **constant extra heating or cooling power** (a *power step*), its
temperature does **not** jump immediately.  
Instead it follows a characteristic curve that reveals the device’s thermal
properties.  *Network identification by deconvolution* (NID) reconstructs those
properties from the measured curve and expresses them as an **equivalent
electric RC network** (thermal resistance ↔ electrical resistance, thermal
capacity ↔ electrical capacitance).

The main ideas are sketched below.

.. _nid_step_and_impulse:

Step- and impulse-response
-----------------------------------------------
* **Step response**  
  The *thermal impedance*

  .. math::

     Z_\mathrm{th}(t) = \frac{T_0 - T(t)}{P}

  is the temperature rise (relative to the starting temperature :math:`T_0`)
  normalised by the applied power step :math:`P`.

* **Impulse response**  
  Differentiate the step response:

  .. math::

     h(t) \;=\; \frac{\partial Z_\mathrm{th}(t)}{\partial t} .

  Once :math:`h(t)` is known, any time-dependent power profile
  :math:`P(t)` produces

  .. math::

     T(t) = T_0 + \int_0^{t} P(t')\,h(t - t')\,\mathrm{d}\t'

  via convolution.

  .. note::
     Differentiation is numerically challenging due to the amplification of measurement noise.
     See :ref:`nid_derivation` for details on specialized algorithms that overcome these challenges.

* **Transfer function**  
  The Laplace transform :math:`Z(s)` of :math:`h(t)` is the impedance of the
  sought RC network.  Knowing :math:`Z(s)` numerically is **not** enough: the
  individual resistances and capacitances still have to be extracted.

.. _nid_logarithmic_time:

Logarithmic time axis
-----------------------------------------------
Thermal transients span microseconds to hours.  Calculations therefore switch
to a **logarithmic time axis**

.. math::

   z      &= \ln\!\bigl(t/t_0\bigr),\\
   \zeta  &= \ln\!\bigl(\tau/\tau_0\bigr),

usually with :math:`t_0=\tau_0=1\;\text{s}` so that :math:`z` and
:math:`\zeta` are *logarithmic* times.

**Notation**: The measured step response expressed on the :math:`z`-axis is written

  .. math::

     a(z) \;=\; Z_\mathrm{th}\!\bigl(e^{z}\bigr).

.. _nid_time_constant_spectrum:

Time-constant spectrum
-----------------------------------------------
A one-dimensional heat path can be modelled by a Foster ladder with
time-constants :math:`\tau_i = R_i C_i`.  
Its *logarithmic time-constant spectrum*

.. math::

   R(\zeta) \;=\; \sum_{i=1}^{n} R_i\,\delta\!\bigl(\zeta-\ln\tau_i\bigr)

collects the resistances as Dirac peaks.

.. figure:: /_static/foster_network.png
   :alt: Foster network
   :width: 600px
   :align: center

   Foster network with parallel RC branches.

On the logarithmic axis the step response becomes

.. math::

   a(z) \;=\; \int_{-\infty}^{\infty} R(\zeta)\,
              \bigl(1 - e^{-e^{\,z-\zeta}}\bigr)\,\mathrm{d}\zeta .

Differentiation yields the impulse response

.. math::

   h(z) \;=\; \int_{-\infty}^{\infty} R(\zeta)\,
              e^{\,z-\zeta - e^{\,z-\zeta}}\,\mathrm{d}\zeta ,
            \quad\Longrightarrow\quad
            h \;=\; R \;\ast\; w_z

with the **kernel**

.. math::

   w_z(z) \;=\; e^{\,z - e^{\,z}}.

Finding :math:`R(\zeta)` is therefore a *deconvolution problem*.

.. _nid_spectrum_to_rc:

From spectrum to RC network
-----------------------------------------------
1. **Discretise** the spectrum into bins of width :math:`\Delta\zeta_i`
   centred at :math:`\zeta_i`.

2. **Foster elements**

   .. math::

      R_i &= R(\zeta_i)\,\Delta\zeta_i,\\
      C_i &= \frac{e^{\,\zeta_i}}{R(\zeta_i)\,\Delta\zeta_i}.

3. **Cauer network**  
   Transform the Foster ladder to a Cauer (series) ladder iteratively
   (see standard Foster-↔-Cauer formulas).  
   The cumulative heat capacitance versus cumulative thermal resistance
   obtained from the Cauer ladder is the *structure function*.

.. figure:: /_static/cauer_network.png
    :alt: Cauer network
    :width: 600px
    :align: center

    Foster network with series RC branches.

.. _nid_alternative_route:

Inverse route starting from :math:`Z(s)`
-----------------------------------------------
If only the transfer function is given, the spectrum follows from

.. math::

   R(\zeta)
     \;=\;
   \frac{1}{\pi}\;
   \Im\!\bigl[Z\bigl(s = -e^{-\zeta}\bigr)\bigr].

Here, :math:`\Im\!\bigl[Z(s)\bigr]` is the imaginary part of the transfer function.

Because :math:`Z(s)` has poles on the negative real axis, evaluate instead
along a line tilted by a small angle :math:`\delta`

.. math::

   s(\zeta)
     \;=\;
   -\bigl(\cos\delta + \mathrm{i}\,\sin\delta\bigr)e^{-\zeta},

which broadens the delta peaks and avoids singularities.

With :math:`R(\zeta)` known, use the convolution above to recreate
:math:`h(z)` and :math:`Z_\mathrm{th}(t)`.

.. _nid_structure_functions:

Thermal Structure Functions
--------------------------------------
The structure function is a **strictly one-dimensional** representation.
Whenever lateral or parasitic heat flows grow significant, assigning its
resistances and capacitances to real device layers becomes ambiguous.  
Typical causes are:

* asymmetric cooling conditions,
* strong neighbouring heat sources,
* inadequate insulation,
* three-dimensional spreading (cylindrical, conical, spherical).

Even then the *spectrum*, *impulse response* and *thermal impedance* remain
well defined, because the Foster elements are **mathematical** and need not
match physical layers.
