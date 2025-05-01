Differentiation
=================

Differentiation is a fundamental preprocessing step in PyRth that converts thermal impedance data into a form suitable for deconvolution.

Algorithm Description
-----------------------

The differentiation algorithm calculates the derivative of the thermal impedance with respect to the logarithm of time. This transformation highlights the time constant distribution and is a necessary step before applying deconvolution methods.

Mathematical Formulation
--------------------------

The thermal impedance :math:`Z_{th}(t)` is related to the time constant spectrum :math:`R(\tau)` through a convolution:

.. math::

    Z_{th}(t) = \int_{0}^{\infty} R(\tau) \cdot (1 - e^{-t/\tau}) d\tau

Taking the derivative with respect to the logarithm of time yields:

.. math::

    \frac{dZ_{th}(t)}{d\ln(t)} = \int_{0}^{\infty} R(\tau) \cdot \frac{t}{\tau} \cdot e^{-t/\tau} d\tau

This form is particularly useful because:

1. It transforms the convolution kernel into a form that peaks at :math:`\tau = t`
2. It enhances the sensitivity to individual time constants
3. It prepares the data for deconvolution algorithms

Implementation Details
------------------------

PyRth implements several differentiation methods with various trade-offs between accuracy and noise sensitivity:

1. **Standard Numerical Differentiation**: Simple finite difference method
2. **Savitzky-Golay Filter**: Smooths data while differentiating
3. **Spline Interpolation**: Uses cubic splines for smoother derivatives

The core implementation uses Numba for performance optimization:

.. code-block:: python

    @njit(cache=True)
    def derivative(
        x=np.array([]),
        y=np.array([]),
        window_length=int(5),
        poly_order=int(2),
        method="savgol",
    ):
        """
        Calculate the derivative of y with respect to ln(x).
        
        Parameters:
        -----------
        x : array-like
            Time values.
        y : array-like
            Thermal impedance values.
        window_length : int
            Window length for Savitzky-Golay filter.
        poly_order : int
            Polynomial order for Savitzky-Golay filter.
        method : str
            Differentiation method ('savgol', 'spline', or 'standard').
            
        Returns:
        --------
        dy_dln : array-like
            Derivative of y with respect to ln(x).
        """
        # Calculate ln(x) for differentiation with respect to log time
        log_time = np.log(x)
        
        if method == "savgol":
            # Savitzky-Golay method (smoothed differentiation)
            dy_dln = savgol_derivative(log_time, y, window_length, poly_order)
            
        elif method == "spline":
            # Cubic spline interpolation method
            spline = CubicSpline(log_time, y)
            dy_dln = spline.derivative()(log_time)
            
        else:
            # Standard numerical differentiation
            dy_dln = standard_derivative(log_time, y)
            
        return dy_dln
        
Savitzky-Golay Method
-----------------------

The Savitzky-Golay filter fits local polynomials to segments of the data and differentiates the polynomials. This provides smooth derivatives even for noisy data:

.. code-block:: python

    @njit(cache=True)
    def savgol_derivative(x, y, window_length, poly_order):
        """
        Calculate derivative using Savitzky-Golay filter.
        """
        n = len(x)
        half_window = window_length // 2
        dy_dx = np.zeros_like(y)
        
        # Handle endpoints separately
        for i in range(half_window):
            # Use forward differences for start of array
            dy_dx[i] = (y[i+1] - y[i]) / (x[i+1] - x[i])
            
            # Use backward differences for end of array
            dy_dx[n-i-1] = (y[n-i-1] - y[n-i-2]) / (x[n-i-1] - x[n-i-2])
        
        # Apply Savitzky-Golay filter to central points
        for i in range(half_window, n - half_window):
            # Extract local window for polynomial fitting
            x_window = x[i-half_window:i+half_window+1]
            y_window = y[i-half_window:i+half_window+1]
            
            # Center x values for numerical stability
            x_center = x[i]
            x_norm = x_window - x_center
            
            # Fit polynomial to local window
            coeffs = polyfit(x_norm, y_window, poly_order)
            
            # Derivative of polynomial at center point
            dy_dx[i] = coeffs[1]  # First derivative coefficient
            
        return dy_dx

Spline Method
---------------

The spline method uses cubic spline interpolation for smoothness:

.. code-block:: python

    def spline_derivative(self, log_time, impedance):
        """
        Calculate derivative using cubic spline interpolation.
        """
        # Create cubic spline interpolator
        spline = interpolate.CubicSpline(log_time, impedance)
        
        # Evaluate derivative at original points
        dy_dln = spline.derivative()(log_time)
        
        return dy_dln

Handling of Data Extremities
------------------------------

Special care is taken at the boundaries of the data range where standard differentiation methods may produce artifacts:

1. **Start of Data**: Forward differences or custom polynomial extrapolation
2. **End of Data**: Backward differences or custom polynomial extrapolation
3. **Sparse Regions**: Adaptive window sizes or higher-order methods

Noise Considerations
----------------------

The differentiation process amplifies noise in the original data. PyRth addresses this through:

1. **Pre-filtering**: Optional data smoothing before differentiation
2. **Method Selection**: Automatically selecting the most appropriate method based on data quality
3. **Parameter Optimization**: Adaptive window sizing for optimal noise reduction while preserving features

Advantages and Limitations
----------------------------

**Advantages:**
- Enables the application of deconvolution methods to thermal data
- Highlights time constant distributions in the data
- Multiple methods available for different noise levels
- Optimized implementation for performance

**Limitations:**
- Inherently amplifies noise in the data
- Parameter selection can significantly affect results
- Trade-off between smoothness and preserving actual features
- May introduce artifacts at data boundaries

Usage in PyRth
-----------------

The differentiation method and parameters can be configured in the analysis setup:

.. code-block:: python

    params = {
        "diff_method": "savgol",  # Differentiation method
        "diff_window_size": 9,    # Window size for Savitzky-Golay
        "diff_poly_order": 3,     # Polynomial order for fitting
        # Other parameters...
    }
    
    analysis = StructureFunction(params)
    
    # The differentiated data is accessible via:
    imp_deriv = analysis.imp_deriv  # Differentiated impedance