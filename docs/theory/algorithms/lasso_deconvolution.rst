Lasso Deconvolution
======================

Lasso Deconvolution is a regularization-based approach in PyRth for calculating the time constant spectrum that promotes sparsity in the solution.

Algorithm Description
------------------------

The Lasso (Least Absolute Shrinkage and Selection Operator) deconvolution method treats the deconvolution problem as a regularized least squares optimization with L1 penalty. This approach is particularly effective when the underlying thermal system has a discrete set of time constants, as it naturally produces sparse solutions.

Mathematical Formulation
----------------------------

The Lasso method poses the deconvolution problem as:

.. math::

    \min_{R(\tau)} \frac{1}{2} \sum_{i} \left( Z_{th}(t_i) - \sum_{j} R(\tau_j) \cdot (1 - e^{-t_i/\tau_j}) \right)^2 + \alpha \sum_{j} |R(\tau_j)|

Where:
- The first term is the sum of squared errors between measured and reconstructed thermal impedance
- The second term is the L1 penalty that encourages sparsity
- :math:`\alpha` is the regularization parameter that controls the trade-off between fitting the data and promoting sparsity

Implementation Details
------------------------

In PyRth, the Lasso deconvolution is implemented using scikit-learn's `LassoCV` class, which automatically selects the optimal regularization parameter through cross-validation:

The main steps are:

1. Define a grid of time constants (tau values)
2. Construct a design matrix where each column represents the contribution of a specific time constant
3. Solve the Lasso regression problem with non-negativity constraints
4. Extract the coefficients, which directly represent the time constant spectrum

Code Example
---------------

.. code-block:: python

    def z_fit_lasso(self):
        # Choose a tau grid (log-spacing)
        tau_min = 2 * np.diff(self.time).min()
        tau_max = 1 * self.time.max()
        K = self.log_time_size
        tau_grid = np.logspace(np.log10(tau_min), np.log10(tau_max), K)
        
        # Design matrix Φ (n × K)
        phi_unnormalized = 1.0 - np.exp(-self.time[:, None] / tau_grid[None, :])
        
        # Calculate norms of the original columns
        phi_norms = np.linalg.norm(phi_unnormalized, axis=0, keepdims=True)
        phi_norms[phi_norms == 0] = 1.0
        
        # Normalize columns for numeric stability
        phi = phi_unnormalized / phi_norms
        
        # Fit a non-negative sparse model (Lasso, positive=True)
        lasso = LassoCV(
            alphas=np.logspace(-5, -2, 100),
            cv=5,
            positive=True,  # Enforces non-negativity
            fit_intercept=False,
            max_iter=10_000,
            n_jobs=-1,
            verbose=False,
        )
        
        lasso.fit(phi, self.impedance.ravel())
        
        # Get coefficients and rescale
        A_hat_normalized = lasso.coef_
        A_hat = A_hat_normalized / phi_norms.flatten()
        
        # Store results
        self.log_time_pad = np.log(tau_grid.copy())
        self.time_spec = A_hat.flatten()
        self.sum_time_spec = np.cumsum(self.time_spec)

Cross-Validation
-------------------

The Lasso method in PyRth uses cross-validation to automatically determine the optimal regularization parameter `alpha`. This process:

1. Divides the data into training and validation sets
2. Fits models with different `alpha` values on the training sets
3. Evaluates their performance on the validation sets
4. Selects the `alpha` that gives the best average performance

This automated approach eliminates the need for manual parameter tuning.

Advantages and Limitations
-------------------------------

**Advantages:**
- Produces sparse solutions with clearly identifiable peaks
- Directly optimizes the impedance fit rather than working with derivatives
- Naturally enforces non-negativity
- Automatic selection of regularization parameter via cross-validation
- Often better for systems with discrete thermal time constants

**Limitations:**
- Computationally intensive for large datasets
- May not capture continuous distributions of time constants well
- Sensitive to initial time constant grid selection
- Can miss small contributions if alpha is too large

Usage in PyRth
-------------------

The Lasso deconvolution method can be selected by setting the appropriate parameter in the configuration:

.. code-block:: python

    params = {
        "deconv_mode": "lasso",  # Use Lasso deconvolution
        # Other parameters...
    }
    
    # Create analysis instance with these parameters
    analysis = StructureFunction(params)

Practical Considerations
-----------------------------

When using Lasso deconvolution:

1. The time constant grid resolution affects the final spectrum resolution
2. Using too many time constants can slow down computation considerably
3. The method works best when there are truly distinct thermal pathways
4. Cross-validation helps prevent overfitting but increases computation time