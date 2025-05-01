Foster Network Construction
===============================

Foster Network Construction is the process of building a thermal equivalent circuit from the time constant spectrum, which serves as an intermediate representation before deriving structure functions.

Algorithm Description
--------------------------------------

After obtaining the time constant spectrum through deconvolution, PyRth constructs a Foster thermal network, which consists of parallel RC elements. Each element in this network corresponds to a specific point in the time constant spectrum, where:

- The resistance value comes directly from the spectrum amplitude at that point
- The capacitance is calculated from the time constant and resistance

Mathematical Formulation
--------------------------------------

The Foster network is represented mathematically as a sum of first-order exponential terms:

.. math::

    Z_{th}(s) = \sum_{i=1}^{n} \frac{R_i}{1 + s \tau_i} = \sum_{i=1}^{n} \frac{R_i}{1 + s R_i C_i}

Where:
- :math:`Z_{th}(s)` is the thermal impedance in the Laplace domain
- :math:`R_i` are the thermal resistances from the time constant spectrum
- :math:`\tau_i` are the time constants
- :math:`C_i` are the thermal capacitances, calculated as :math:`C_i = \tau_i / R_i`
- :math:`s` is the Laplace variable

Implementation Details
-----------------------------------

In PyRth, the Foster network construction is implemented in several steps:

1. The time constant spectrum is obtained through deconvolution (Fourier, Bayesian, or Lasso)
2. Resistance values (:math:`R_i`) are taken directly from the spectrum amplitudes
3. Time constant values (:math:`\tau_i`) are the x-coordinates of the spectrum
4. Capacitance values are calculated as :math:`C_i = \tau_i / R_i`
5. The network elements are sorted in ascending order of time constants

Code Example
--------------------------

.. code-block:: python

    def calculate_foster_elements(self):
        """
        Calculate Foster network elements from the time constant spectrum.
        """
        # Get time constants (tau) and resistances (R) from the spectrum
        tau = np.exp(self.log_time_pad)
        resistance = self.time_spec
        
        # Filter out insignificant or negative components
        valid_indices = (resistance > self.min_r_threshold) & (resistance >= 0)
        tau_filtered = tau[valid_indices]
        resistance_filtered = resistance[valid_indices]
        
        # Sort by time constants (for numerical stability in later stages)
        sort_indices = np.argsort(tau_filtered)
        self.therm_resist_fost = resistance_filtered[sort_indices]
        self.therm_capa_fost = tau_filtered[sort_indices] / self.therm_resist_fost
        
        # Store for potential export or further processing
        self.foster_tau = tau_filtered[sort_indices]
        self.foster_r = self.therm_resist_fost
        self.foster_c = self.therm_capa_fost

Multiple Precision Handling
-----------------------------------------

For certain structure function algorithms (like Polynomial Long Division and de Boor-Golub), the Foster network elements require arbitrary precision mathematics. PyRth handles this through a multi-precision conversion step:

.. code-block:: python

    def convert_to_mp(self):
        """
        Convert Foster elements to arbitrary precision format.
        """
        # Create multi-precision arrays
        self.mpfr_resist_fost = np.array([mpfr(str(r)) for r in self.therm_resist_fost])
        self.mpfr_capa_fost = np.array([mpfr(str(c)) for c in self.therm_capa_fost])
        
        # Create transfer function coefficients in multi-precision
        self.create_mpfr_tf_coeffs()

Transfer Function Coefficient Generation
-----------------------------------------------------

The Foster network is also represented as a ratio of polynomials in the Laplace domain:

.. math::

    Z_{th}(s) = \frac{b_0 + b_1 s + b_2 s^2 + \ldots + b_n s^n}{a_0 + a_1 s + a_2 s^2 + \ldots + a_n s^n}

These coefficients are calculated in PyRth using a recursive algorithm:

.. code-block:: python

    def create_mpfr_tf_coeffs(self):
        """
        Calculate transfer function coefficients from Foster elements.
        """
        # Get the number of RC elements
        n = len(self.mpfr_resist_fost)
        
        # Pre-allocate coefficient arrays
        self.mpfr_z_num = np.array([mpfr("0.0")] * n)
        self.mpfr_z_denom = np.array([mpfr("0.0")] * (n + 1))
        self.mpfr_z_denom[0] = mpfr("1.0")
        
        # Calculate coefficients using recursive formulation
        for i in range(n):
            # Current RC element's time constant
            tau_i = self.mpfr_resist_fost[i] * self.mpfr_capa_fost[i]
            
            # Update numerator coefficients
            for j in range(i, -1, -1):
                if j == 0:
                    self.mpfr_z_num[j] += self.mpfr_resist_fost[i]
                else:
                    self.mpfr_z_num[j] += self.mpfr_resist_fost[i] * self.mpfr_z_denom[j]
            
            # Update denominator coefficients
            for j in range(i + 1, 0, -1):
                self.mpfr_z_denom[j] = self.mpfr_z_denom[j - 1] + tau_i * self.mpfr_z_denom[j]

Advantages and Limitations
----------------------------------------

**Advantages:**
- Direct correspondence with the time constant spectrum
- Simple mathematical representation
- Efficient implementation
- Straightforward computation of impedance response

**Limitations:**
- Does not directly represent the physical heat flow path
- Cannot be used directly for spatial thermal interpretation
- Requires further transformation (to Cauer form) for structure function analysis

Usage in PyRth
----------------------------

The Foster network construction is an automatic step in the standard analysis workflow. After deconvolution, PyRth builds the Foster network and then transforms it into a Cauer network for structure function calculation:

.. code-block:: python

    # Create analysis with default parameters
    params = {
        "data": measurement_data,
        "input_mode": "impedance"
    }
    
    # Run analysis, which will internally construct Foster network
    analysis = Evaluation().standard_module(params)
    
    # Foster network elements are accessible via:
    foster_r = analysis.foster_r  # Resistances
    foster_c = analysis.foster_c  # Capacitances
    foster_tau = analysis.foster_tau  # Time constants