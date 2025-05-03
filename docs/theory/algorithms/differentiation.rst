.. _nid_derivation:

Differentiation
=================

.. _why_differentiation_is_hard:

**Why differentiation is hard**
------------------------------------
Network identification by deconvolution (NID) comprises three numerically
delicate stages: **differentiation**, **deconvolution**, and the
**Foster-to-Cauer** transform.  The first two are extremely sensitive to
noise; if the derivative is biased or noisy, all subsequent steps degrade.

A recorded step response :math:`a(t)` must be converted into its impulse
response :math:`h(t)=\partial a/\partial t`.  Finite-difference formulas
amplify every morsel of measurement noise, while wide averaging windows
suppress noise **and** small, rapid transients.  This compromise is the
*bias–variance trade-off*.  In practice, measuring clean :math:`Z_\mathrm{th}`
curves greatly reduces the noise problem, but it is still necessary to
balance the two extremes.


**Logarithmic timeline effects**
  
After converting to the logarithmic axis

.. math::

   z = \ln t ,

samples are far apart at early times and crammed together later.  Sparse
regions suffer most from differentiation errors.

**Simple differentiation schemes**

* **Straight-line fit** over a short window.  
* **Second-order Savitzky–Golay** filter over a longer window.

Both still require an informed choice of window length.


.. _nid_lowess:

Optimal regression filtering
------------------------------------
The implementation adopted here replaces ad-hoc windows by an **adaptive
LOWESS/SURE filter** that simultaneously smooths the logarithmic step
response and provides its derivative.

**Basic idea**

1. **Model** the samples

   .. math::

      x_i \;=\; s_i \;+\; w_i,

   where :math:`s_i` is the unknown true signal at :math:`z_i` and
   :math:`w_i` is white noise with variance :math:`\sigma^2`.

2. **Local regression**  
   Around each target position :math:`z_i` take the subset
   :math:`\mathbf{x}` that falls inside a window of logarithmic length
   :math:`L`.  
   Fit a *low-order* polynomial (first order performs best in practice)
   using **tricubic weights**

   .. math::

      w(\Delta z) \;=\;
      \begin{cases}
        \bigl(1 - |\Delta z|^3/L^3\bigr)^3, & |\Delta z| < L;\\[4pt]
        0,                                  & \text{otherwise}.
      \end{cases}

   Additional weights compensate for local sample density so that sparse
   early data are not undervalued.

3. **Derivative**  
   The slope of the fitted line at :math:`z_i` furnishes
   :math:`h(z_i)=\mathrm{d}a/\mathrm{d}z`.

**Choosing the window length**

For each location the *statistical risk*

.. math::

   \mathcal{R}_i \;=\;
      \mathbb{E}\Bigl[(f_i(\mathbf{x})-s_i)^2\Bigr]

measures the mean-square error of the estimator :math:`f_i`.  
Because :math:`s_i` is unknown, the risk is *estimated* with
**Stein's unbiased risk estimate** (SURE):

.. math::

   \widehat{\mathcal{R}}_i \;=\;
      f_i^2 - 2f_i x_i + 2\sigma^2
      \frac{\partial f_i}{\partial x_i}
      \;+\; \text{constant}.

The additive constant does not depend on the window, so
minimising :math:`\widehat{\mathcal{R}}_i` over :math:`L` yields the optimal
trade-off.  A practical algorithm:

* Define a reasonable interval :math:`L\in[L_{-},L_{+}]`.
* Pick an initial :math:`L_0` at the first grid point :math:`z'_0`, or find an optimal :math:`L_0` by
  minimising :math:`\widehat{\mathcal{R}}_0` over :math:`L`.
* At each subsequent regularised position :math:`z'_i`

  * evaluate the risk for :math:`L-\Delta L,\;L,\;L+\Delta L`,
  * move :math:`L` towards the lowest-risk candidate.

This *greedy* update avoids erratic jumps and accelerates computation.
Because a uniform :math:`z'`-grid is created on the fly, the data are
resampled, smoothed, and differentiated **in a single pass**—perfectly
suited for the fast Fourier and Bayesian steps that follow.
