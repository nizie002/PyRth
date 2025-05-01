Polynomial Long Division
=========================

Polynomial Long Division is a fundamental algorithm in PyRth for transforming a Foster thermal network into a Cauer network, which is required for structure function calculations.

Algorithm Description
-----------------------

The Polynomial Long Division method transforms the Foster network (parallel RC elements) into a Cauer network (series-parallel RC ladder) by performing polynomial division on the transfer function. This process is mathematically equivalent to a continued fraction expansion.

Mathematical Formulation
--------------------------

Starting with the thermal impedance transfer function in the Laplace domain:

.. math::

    Z_{th}(s) = \frac{N(s)}{D(s)} = \frac{b_0 + b_1 s + b_2 s^2 + \ldots + b_n s^n}{a_0 + a_1 s + a_2 s^2 + \ldots + a_n s^n}

The polynomial long division algorithm performs the following steps:

1. Divide :math:`N(s)` by :math:`D(s)` to get the first quotient term :math:`q_1`
2. Calculate the remainder :math:`R_1(s) = N(s) - q_1 \cdot D(s)`
3. Invert the problem and divide :math:`D(s)` by :math:`R_1(s)` to get the next quotient term :math:`q_2`
4. Continue this process recursively

This results in a continued fraction expansion:

.. math::

    Z_{th}(s) = q_1 + \frac{1}{q_2 + \frac{1}{q_3 + \ldots}}

Each quotient term corresponds to a Cauer network element:
- Even-indexed terms (:math:`q_1, q_3, \ldots`) represent thermal resistances
- Odd-indexed terms (:math:`q_2, q_4, \ldots`) represent thermal capacitances (after inverting)

Implementation Details
-------------------------

Due to the numerical sensitivity of polynomial division, PyRth implements this algorithm using arbitrary precision arithmetic through the `gmpy2` library:

.. code-block:: python

    def polynomial_long_division(self):
        """
        Convert Foster to Cauer network using polynomial long division.
        """
        # Start with transfer function numerator and denominator
        num = self.mpfr_z_num.copy()
        denom = self.mpfr_z_denom.copy()
        
        # Get the number of elements
        n = len(num)
        
        # Initialize lists for Cauer network elements
        self.cauer_r = []
        self.cauer_c = []
        
        # Perform long division n times (for n elements)
        for i in range(n):
            # Find the next resistance (numerator / denominator coefficient)
            r_i = num[0] / denom[0]
            self.cauer_r.append(float(r_i))
            
            # Compute the remainder after division
            remainder = num.copy()
            for j in range(len(remainder)):
                remainder[j] -= r_i * denom[j]
            
            # Shift the remainder (remove leading zero)
            remainder = remainder[1:]
            
            # Prepare for next iteration by swapping and inverting
            num, denom = denom, remainder
            
            # If there's another element to extract
            if i < n - 1:
                # Find the next capacitance (invert the relation)
                c_i = denom[0] / num[0]
                self.cauer_c.append(float(c_i))
                
                # Compute the remainder
                remainder = denom.copy()
                for j in range(len(remainder)):
                    remainder[j] -= c_i * num[j]
                
                # Shift and prepare for next iteration
                remainder = remainder[1:]
                denom, num = num, remainder

Numerical Stability Considerations
-----------------------------------------

Polynomial long division is highly sensitive to numerical errors, which can lead to incorrect results, especially for higher-order networks. PyRth addresses this issue through:

1. **Arbitrary Precision**: Using the MPFR library via `gmpy2` to perform calculations with significantly higher precision than standard floating-point
2. **Element Sorting**: Sorting Foster elements by time constants before conversion
3. **Coefficient Normalization**: Normalizing coefficients to prevent numerical overflow/underflow
4. **Precision Scaling**: Adaptively increasing precision for more complex networks

Code Example (Arbitrary Precision Implementation)
-------------------------------------------------------

.. code-block:: python

    # Before polynomial division, convert to multiple precision
    def convert_to_mpfr(self):
        # Convert Foster elements to MPFR format
        self.mpfr_resist_fost = np.array([mpfr(str(r)) for r in self.therm_resist_fost])
        self.mpfr_capa_fost = np.array([mpfr(str(c)) for c in self.therm_capa_fost])
        
        # Set precision for MPFR calculations
        mpfr.set_default_prec(512)  # Use 512 bits of precision
        
        # Generate transfer function coefficients
        self.create_mpfr_tf_coeffs()
        
        # Perform polynomial long division
        self.polynomial_long_division()

Advantages and Limitations
------------------------------

**Advantages:**
- Mathematically rigorous conversion from Foster to Cauer networks
- Produces exact results when calculated with sufficient precision
- Directly applicable to structure function generation
- Preserves the thermal impedance characteristics

**Limitations:**
- Computationally intensive, especially for high-order networks
- Requires arbitrary precision arithmetic
- Memory usage can be significant
- May still encounter numerical issues for extremely complex systems

Relationship to Other Methods
---------------------------------

Polynomial Long Division is one of several methods in PyRth for Foster-to-Cauer conversion:

- **Polynomial Long Division**: The most straightforward mathematical approach
- **Lanczos Method**: A matrix-based approach that may be more efficient for certain networks
- **de Boor-Golub Method**: Another matrix-based approach with different numerical properties
- **Khatwani Method**: A specialized algorithm designed for improved numerical stability
- **Sobhy Method**: A frequency-domain approach that can be more numerically stable

Usage in PyRth
--------------------

The Polynomial Long Division method can be selected using the `foster_to_cauer_algorithm` parameter:

.. code-block:: python

    params = {
        "foster_to_cauer_algorithm": "polynomial_division",
        # Other parameters...
    }
    
    analysis = Evaluation().standard_module(params)