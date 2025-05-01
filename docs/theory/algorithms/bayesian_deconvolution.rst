Bayesian Deconvolution
=======================

Bayesian Deconvolution is an iterative method in PyRth for calculating the time constant spectrum that is particularly robust to noise.

Algorithm Description
-----------------------

Bayesian deconvolution uses an iterative approach to solve the ill-posed deconvolution problem by updating the time constant spectrum estimate at each step. The method is based on Bayes' theorem and provides a regularized solution that is less sensitive to noise than direct Fourier deconvolution.

Mathematical Formulation
---------------------------

The relationship between the impedance derivative and time constant spectrum can be expressed as:

.. math::

    \frac{dZ_{th}}{d\ln(t)} = \int_{0}^{\infty} R(\tau) \cdot k(t, \tau) d\tau

Where :math:`k(t, \tau)` is the kernel function.

The Bayesian deconvolution algorithm iteratively updates the estimate of :math:`R(\tau)` using:

.. math::

    R^{(n+1)}(\tau) = R^{(n)}(\tau) \cdot \frac{\int k(t, \tau) \cdot \frac{dZ_{th}(t)}{d\ln(t)} / \int k(t, \tau') \cdot R^{(n)}(\tau') d\tau' dt}{\int k(t, \tau) dt}

This can be simplified in the discrete case to the matrix form implemented in PyRth.

Implementation Details
-------------------------

In PyRth, Bayesian deconvolution is implemented in the `bayesian_deconvolution` function in `transient_engine.py`:

The main steps are:

1. Create a response matrix representing the kernel function
2. Initialize the time constant spectrum (often with a uniform distribution)
3. Iteratively update the spectrum using the Bayesian update formula
4. Normalize the result after a specified number of iterations

The implementation is optimized using Numba for significant performance improvements.

Code Example
----------------

.. code-block:: python

    @njit(cache=True)
    def bayesian_deconvolution(
        re_mat=np.array([[]]), imp_deriv_interp=np.array([]), N=float(1.0)
    ):
        true = imp_deriv_interp.copy().reshape(-1, 1)

        for step in range(N):
            denom = np.dot(re_mat, true).reshape(-1)
            denom[denom == 0.0] = np.inf
            q_vec = np.divide(imp_deriv_interp, denom).reshape(1, -1)
            k_sum = np.dot(q_vec, re_mat).reshape(-1, 1)
            true = np.multiply(k_sum, true)

        return true.flatten()

Response Matrix Generation
----------------------------

The response matrix is a critical component that represents how each time constant contributes to the impedance at each time point. It's generated using the `response_matrix` function:

.. code-block:: python

    @njit(cache=True)
    def response_matrix(domain=np.array([]), x_len=float(1.0)):
        response = np.zeros((x_len, x_len))
        norm = np.sum(np.exp(domain - np.exp(domain)))
        
        for it_line in range(x_len):
            for it_row in range(x_len):
                response[it_line, it_row] = domain[it_line] - domain[it_row]
        response = np.exp(response - np.exp(response))
        
        response /= norm
        
        return response

Advantages and Limitations
-----------------------------

**Advantages:**
- More robust to noise than Fourier deconvolution
- No need for explicit filter selection
- Naturally enforces non-negativity of the time constant spectrum
- Often produces smoother, more physically realistic spectra

**Limitations:**
- Computationally more intensive than Fourier methods
- Results may depend on the number of iterations
- May converge slowly for some problems
- Can potentially obscure fine details in the spectrum

Usage in PyRth
----------------

The Bayesian deconvolution method can be selected by setting the appropriate parameter in the configuration:

.. code-block:: python

    params = {
        "deconv_mode": "bayesian",  # Use Bayesian deconvolution
        "bay_steps": 1000,          # Number of iterations
        # Other parameters...
    }
    
    # Create analysis instance with these parameters
    analysis = StructureFunction(params)