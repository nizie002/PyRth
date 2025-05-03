LASSO Deconvolution
======================

LASSO (Least-Absolute-Shrinkage-and-Selection-Operator) Deconvolution is a regularization-based approach in PyRth for calculating the time constant spectrum that promotes sparsity in the solution.

While FFT and Bayesian techniques work directly on the
*impulse* response, **LASSO deconvolution**
solves the problem **in the impedance domain**.  
It casts the recovery of the time-constant spectrum as an
:math:`\ell_1`-regularised *least-squares* optimisation that
naturally favours *sparse* spectra – ideal when only a handful of distinct
thermal paths are present.

**Motivation**

Traditional methods require differentiation of the step response, amplifying
noise and forcing a bias–variance trade-off, while FFT filtering spreads energy
across neighbouring bins and Bayesian deconvolution can converge to broad distributions under noisy data.

LASSO deconvolution works directly in the impedance domain without numerical
differentiation, thus avoiding noise amplification and derivative bias. It also
explicitly drives small coefficients to **exactly zero**, isolating dominant
peaks and yielding a compact Foster network.

Mathematical Formulation
----------------------------

**Formulation**

Choose a fixed grid of trial time-constants
:math:`\tau_j` (logarithmically spaced is typical).
The predicted step response built from a
discrete spectrum :math:`R(\tau_j)` is

.. math::

   Z_\text{model}(t_i)
      \;=\;
   \sum_{j} R(\tau_j)\,\bigl(1-e^{-t_i/\tau_j}\bigr).

LASSO finds :math:`R(\tau_j)` by minimising

.. math::

   \frac12
   \sum_{i}
   \Bigl[
     Z_\text{meas}(t_i)
     -
     Z_\text{model}(t_i)
   \Bigr]^2
   \;+\;
   \alpha\sum_{j}\lvert R(\tau_j)\rvert,

subject to :math:`R(\tau_j)\ge 0`.  
Here

* the first term enforces fidelity to the measured impedance,
* the :math:`\ell_1` penalty (weight :math:`\alpha`) promotes sparsity.


Comments
----------------------------

**Implementation Details**

In PyRth, the LASSO deconvolution is implemented using scikit-learn's `LassoCV`
class, which automatically selects the optimal regularization parameter through
cross-validation. The process involves defining a grid of time constants (:math:`\tau`),
constructing a design matrix where each column represents the contribution of a specific
time constant, solving the LASSO regression problem with non-negativity constraints, and
finally extracting the coefficients which directly represent the time constant spectrum.

**Cross-Validation**

The LASSO method in PyRth utilizes cross-validation to automatically determine the
optimal regularization parameter :math:`\alpha`. This involves dividing the data
into training and validation sets, fitting models with different :math:`\alpha`
values on the training data, evaluating their performance on the validation sets,
and selecting the :math:`\alpha` that yields the best average performance. This
automated approach eliminates the need for manual parameter tuning.

**Practical Considerations**

When applying LASSO deconvolution, consider that the resolution of the
time constant grid directly impacts the final spectrum resolution. Using
an excessive number of time constants can significantly slow down computation.
The method performs best when the system exhibits truly distinct thermal pathways.
While cross-validation helps prevent overfitting, it does add to the
overall computation time.