.. _nid_foster_network:

From Spectrum to Foster Network
===============================
Once the logarithmic time-constant spectrum :math:`R(\zeta)`
is known (via Fourier, Bayesian or LASSO deconvolution) the *first* physical
network we construct is the **Foster ladder**.  

**Discrete Foster elements**

Discretise the spectrum into bins of width :math:`\Delta\zeta_i`
centred at :math:`\zeta_i=\ln\tau_i` (see
:ref:`nid_spectrum_to_rc`).  
For each bin

.. math::

   R_i = R(\zeta_i)\,\Delta\zeta_i,
   
.. math::

   C_i = \frac{e^{\zeta_i}}{R(\zeta_i)\,\Delta\zeta_i},


exactly the formulas used in network identification by deconvolution.
Every tuple :math:`(R_i,C_i)` corresponds to **one parallel RC branch** whose
time-constant is :math:`\tau_i=R_iC_i`.

**Piece-wise construction of the impedance**

.. list-table::
   :widths: 50 50
   :header-rows: 0
   :class: borderless

   * - .. figure:: /_static/parallel_rc_element.png
        :alt: Parallel RC element
        :width: 200px
        :align: center

        *Parallel RC element*

     - .. figure:: /_static/two_parallel_rc_elements.png
        :alt: Two parallel RC elements connected in series
        :width: 600px
        :align: center

        *Two parallel RC elements connected in series*

A single parallel RC branch driven in series has

.. math::

   Z_i(s)=\frac{R_i}{1+R_iC_i s}.

Because the branches are stacked **in series**, the input impedance of the
Foster ladder is the *sum* of the individual impedances:

.. math::
   :label: foster_sum

   Z(s)=\sum_{i=1}^{n}\frac{R_i}{1+R_iC_i s}.

Equation :eq:`foster_sum` is simply the partial-fraction form produced by
the pole–zero representation (§“Lumped element RC lines”).  Building
:math:`Z(s)` “piece by piece” is therefore trivial:

#. start with :math:`Z^{(1)}(s)=Z_1(s)`;
#. for *k* = 2 … *n*: :math:`Z^{(k)}(s)=Z^{(k-1)}(s)+Z_k(s)`.


**Pole–zero representation**

After summing the parallel branches (Equation :eq:`foster_sum`) the overall
impedance can also be written in *pole–zero* form

.. math::

   Z(s)
   \;=\;
   R_{\infty}\;
   \frac{\bigl(1+s/\sigma_{z,1}\bigr)
         \bigl(1+s/\sigma_{z,2}\bigr)\dotsm
         \bigl(1+s/\sigma_{z,n-1}\bigr)}
        {\bigl(1+s/\sigma_{p,1}\bigr)
         \bigl(1+s/\sigma_{p,2}\bigr)\dotsm
         \bigl(1+s/\sigma_{p,n}\bigr)},
   \qquad
   R_{\infty}=\sum_{i=1}^{n}R_i.

* **Poles**  
  Each Foster branch contributes a real pole

  .. math::

     \sigma_{p,i}=\frac{1}{\tau_i}
                 =\frac{1}{R_iC_i},

  located on the negative real axis.

* **Zeros**  
  The finite zeros :math:`\sigma_{z,k}` fall *between* adjacent poles; they
  arise automatically from the summation of terms in
  Equation :eq:`foster_sum`.  Pole–zero interlacing guarantees that
  :math:`Z(s)` is a **positive-real** function, hence physically admissible
  for a passive one-port.

* **Low- and high-frequency limits**

  .. math::

     Z(0)=R_{\infty},
     \qquad
     Z(\infty)=0,

  matching the expected behaviour of a purely diffusive thermal path.

The pole–zero picture provides an immediate diagnostic:
widely separated poles imply well-resolved thermal layers,
while closely spaced poles hint at a continuous-diffusion region that may be
better represented by a non-uniform RC line.
