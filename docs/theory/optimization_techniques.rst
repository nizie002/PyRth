.. _optimization_techniques:

Optimization Techniques
=======================

Network identification by deconvolution (NID) normally concludes once
the Foster ladder (see :ref:`nid_foster_network`) has been converted to a
structure function (:ref:`structure_functions`).  PyRth can extend that
flow with an optimisation stage that refines the structure function so
its forward-simulated thermal impedance matches the measurement as
closely as possible.  This page describes the optimisation workflow
implemented by :mod:`PyRth.transient_optimizer` and the
``optimization_module`` helpers.


Why Optimise?
-------------

Steps such as differentiation (:ref:`nid_derivation`), Fourier/Bayesian
deconvolution (:ref:`nid_fft_deconv`, :ref:`nid_bayes_deconv`) and the
Foster→Cauer conversions (:ref:`polynomial_long_division`,
:ref:`nid_khatwani`, :ref:`nid_sobhy`, :ref:`nid_lanczos`,
:ref:`nid_boor_golub`) amplify noise and sparsity in the raw data.  The
resulting structure function may show smeared peaks, few points in slow
regions, or a blurred divergence near steady state.  Optimisation-based
identification addresses these artefacts by fitting a simplified
structure function directly to the thermal impedance, which is a much
better-behaved quantity numerically.


Three-Stage Pipeline
--------------------

The optimisation workflow is split into three consecutive stages:

1. **Classical baseline.** Run a standard evaluation (FFT, Bayesian,
	 LASSO) to obtain a smooth derivative, a time-constant spectrum and an
	 initial Cauer ladder.  These artefacts provide a high-quality initial
	 guess and ensure the optimiser starts close to a feasible solution.
2. **Structure simplification.** Sample the cumulative structure
	 function at ``n`` sections, typically between 4 and 10.  Each section
	 represents a uniform RC slice (one resistance, one capacitance).
	 Truncating the far end of the structure prevents the steady-state
	 tail from dominating subsequent error metrics.
3. **Non-linear optimisation.** Adjust the ``2n`` section parameters so
	 the reconstructed impedance `a_opt(z)` minimises its distance to the
	 measured curve `a_measured(z)` on the logarithmic time axis.

All three steps are driven automatically by
``Evaluation.optimization_module`` or can be scripted manually through
``TransientOptimizer``.


Structure Simplification Objective
----------------------------------

The simplification step compares the logarithmic capacitance of the
conventional structure to that of the simplified one.  The objective

.. math::

	 o_\text{struc} = \biggl[ \int_{0}^{R}
	 \left( \ln C_{\Sigma,\text{conv}} - \ln C_{\Sigma,\text{opt}} \right)^2
	 \mathrm{d}R_\Sigma \biggr]^{1/2}

weights early and late sections equally even though their capacitances
can span many orders of magnitude.  The minimiser is free to reposition
the section breakpoints as long as the cumulative resistance remains
monotonic.


Impedance-Fitting Objective
---------------------------

Once a simplified structure function exists, the optimiser searches for
the best fit to the measured impedance via

.. math::

	 o_\text{imp} = \biggl[ \int_{z_\text{min}}^{z_\text{max}}
	 \bigl( a_\text{measured}(z) - a_\text{opt}(z) \bigr)^2
	 \mathrm{d} z \biggr]^{1/2}.

Important implementation notes:

* **Variables.** The solver operates on cumulative resistances (stored as
	positive differences) and the associated capacitances, giving `2n`
	scalar unknowns.
* **Constraints.** Positivity is enforced by parameterising resistances
	as cumulative sums of positive increments.  Capacitances are bounded
	away from zero to avoid degenerate time constants.
* **Solvers.** Derivative-free Powell search works well for smooth
	problems; COBYLA is available when explicit inequality constraints are
	desired.  Both are provided by SciPy and integrate cleanly with the
	PyRth optimiser wrapper.
* **Precision.** The forward impedance calculation honours the MPFR
	precision configured in :class:`PyRth.transient_defaults.StructureParameters`,
	ensuring consistency with high-precision Foster→Cauer routines.

Optimising in impedance space naturally produces smooth impulse
responses, spectra and structure functions without reintroducing the
noise associated with numerical differentiation.


Assessing Accuracy
------------------

PyRth uses three metrics when comparing optimisation runs to classical
deconvolution results or to synthetic reference data:

* :math:`m_R` – root-mean-square difference between *integrated*
	time-constant spectra.
* :math:`m_S` – integral of the absolute logarithmic deviation between
	cumulative structure functions over a shared resistance range.
* :math:`\Delta R_\Sigma` – absolute difference in total cumulative
	thermal resistance.

Together with the impedance objective :math:`o_\text{imp}`, these metrics
highlight whether residual error stems from the spectrum, the structure
function or the overall steady-state value.


Practical Tips
--------------

* **When to enable optimisation.** Use it for low signal-to-noise data,
	sparse sampling, or scenarios that demand a reconvolved impedance that
	closely matches measurements (for example, transient dual-interface
	tests).
* **Section count.** Begin with 6–8 sections for power packages and
	increase only if residuals point to missing layers.  Excess sections
	slow down convergence and may overfit noise.
* **Model limitations.** The piecewise-uniform structure function assumes a
	one-dimensional heat path.  When the measured transient shows significant
	lateral heat spreading—often near the end of the data—the optimiser may
	lack the degrees of freedom to reproduce that portion of the trace.
	In such cases the fit remains tight at early times but residuals grow in the
	tail, because the physical assumptions no longer hold.
* **Initial guess.** Feed the optimiser with the Bayesian or LASSO
	spectrum whenever possible; doing so keeps the search near a physically
	meaningful solution.
* **Frequency tilt and sampling.** The forward solver typically evaluates
	response matrices along a small complex tilt :math:`\delta \approx
	0.5^\circ` with 10⁴–10⁶ logarithmic samples so the impedance integral
	remains stable.
* **Validation.** Always reconvolve the optimised spectrum and compare it
	with the measured impedance and its derivative.  Large residuals or
	oscillations indicate that the section count or solver tolerances need
	adjustment.

Refer to :mod:`PyRth.transient_optimizer` for concrete API details and to
``Evaluation.optimization_module`` for the high-level orchestration used
by the CLI tooling.
