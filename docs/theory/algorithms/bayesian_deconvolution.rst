.. _nid_bayes_deconv:

Bayesian Deconvolution
----------------------
Besides FFT filtering, the **Bayesian** or **maximum-likelihood**
deconvolution introduced by Kennett *et al.* (1978) offers a robust,
non-negative route to recover the logarithmic time-constant spectrum
:math:`R(\zeta)`.

**Idea in a nutshell**

*   Treat the convolution

    .. math::

       h(z)=\left(R\ast w_z\right)(z)

    as the **generation of observations** :math:`h` by a *source*
    distribution :math:`R` through a *blurring kernel* :math:`w_z`.
*   Apply **Bayes’ theorem** iteratively: update the current guess of
    :math:`R` by comparing the synthetic response produced through
    :math:`w_z` with the actually measured :math:`h`.

**Discretisation**

Bayesian deconvolution requires an *evenly spaced* logarithmic grid
(:math:`z`-axis).  The continuous integral becomes a sum

.. math::

   h[z] \;=\; \sum_{\zeta} w_z[z-\zeta]\;R[\zeta].

With square-bracket indices the kernel is a **Toeplitz matrix**
(:math:`W_{kj}=w_z[k-j]`):

.. math::

   h_k \;=\; W_{kj}\,R_j.

**Applying Bayes’ theorem**

For vectors Bayes’ rule reads

.. math::

   P(R_i\!\mid h_k)
     \;=\;
   \frac{
     P(h_k\!\mid R_i)\,P(R_i)
   }{
     \sum_j P(h_k\!\mid R_j)\,P(R_j)
   }.

Identify

* likelihood :math:`P(h_k\!\mid R_j)=W_{kj}`,
* prior on *data* :math:`P(h_k)=h_k`.

Choosing a **flat prior** on :math:`R` (initialised with :math:`h_k`)
and enforcing probability conservation gives the classic
*Richardson–Lucy* (RL) iteration specialised to NID:

.. math::

   R_i^{(n+1)}
     \;=\;
   R_i^{(n)}
   \sum_{k}
   \frac{h_k\,W_{ki}}
        {\sum_{j}W_{kj}\,R_j^{(n)}}.

**Key properties**
  
* **Energy (area) preserving**  
  Because :math:`\int w_z\,\mathrm{d}z=1`, the cumulative thermal
  resistance after deconvolution equals the original steady-state value.
* **Non-negativity**  
  All terms are positive; negative artefacts cannot occur.
* **No explicit regulariser needed** – early stopping of the iterations
  itself controls over-fitting to noise.

**Practical guidelines**

* **Initial guess** Set :math:`R^{(0)}=h` or any smooth positive
  approximation.  Convergence is monotonic but slow.
* **Even spacing** Resample the measured impulse response to a uniform
  :math:`\Delta z`; the LOWESS/SURE filter (see
  :ref:`nid_lowess`) can supply both smoothing and resampling.
* **Stopping criterion** Iterate until the synthetic step response

  .. math::

     h^{(n)} = W\,R^{(n)}

  matches the measured one within the estimated noise level (e.g.
  :math:`\chi^2` test) or until a fixed iteration count (1000 – 5000) is
  reached.
* **Zero handling** If the denominator
  :math:`\sum_j W_{kj} R_j^{(n)}` vanishes for wide spectra, skip the
  affected :math:`k` or add a tiny :math:`\varepsilon` to avoid division
  by zero.
* **Underflow** Late iterations may drive negligible bins below floating-
  point precision.  Mask them out to save computation without affecting
  the result.
