Structure Functions
=====================

This document explains the theory and implementation of structure functions in PyRth. Structure functions are powerful representations that convert the time constant spectrum into a thermal equivalent circuit, enabling physical interpretation of the heat flow path.

Foster to Cauer Network Transformation
-------------------------------------------

After obtaining the time constant spectrum through deconvolution, PyRth transforms it into meaningful thermal structure functions through a Foster to Cauer network transformation.

### Foster Thermal Network

The time constant spectrum represents a Foster thermal network, which consists of parallel RC elements:

.. math::

   Z_{th}(s) = \sum_{i=1}^{n} \frac{R_i}{1 + s \tau_i} = \sum_{i=1}^{n} \frac{R_i}{1 + s R_i C_i}

Where:
- :math:`R_i` are the thermal resistances from the time constant spectrum
- :math:`C_i` are the thermal capacitances, calculated as :math:`C_i = \tau_i / R_i`
- :math:`s` is the Laplace variable

The Foster network has simple mathematical properties but lacks physical meaning in terms of heat flow paths.

### Cauer Thermal Network

The Cauer (or continued fraction) network represents a ladder-type circuit that corresponds to the physical heat flow path:

.. math::

   Z_{th}(s) = \frac{1}{sC_1 + \frac{1}{R_1 + \frac{1}{sC_2 + \frac{1}{R_2 + \ldots}}}}

This representation provides a one-dimensional model of heat flow, where each RC pair corresponds to a physical layer along the heat path.

Structure Function Calculation Methods
----------------------------------------

PyRth implements multiple methods for transforming the Foster network to the Cauer representation. The method is selected through the `struc_method` parameter.

1. Polynomial Long Division (polylong)
----------------------------------------

The polynomial long division method directly performs the algebraic conversion between Foster and Cauer forms.

### Mathematical Approach

1. Express the Foster network as a ratio of polynomials in the Laplace domain
2. Perform successive polynomial divisions to extract Cauer elements

### Implementation in PyRth

```python
def poly_long_div(self):
    # Transforms the Foster to Cauer thermal equivalent network
    ar_len = len(self.mpfr_z_denom) - 1
    self.cau_res = np.zeros(ar_len)
    self.cau_cap = np.zeros(ar_len)
    
    for i in range(ar_len):
        self.mpfr_z_num, self.mpfr_z_denom, cap, res = mpu.precision_step(
            self.mpfr_z_num, self.mpfr_z_denom
        )
        self.cau_res[i] = float(res)
        self.cau_cap[i] = float(cap)
    
    # Calculate cumulative values for structure functions
    self.int_cau_res = np.cumsum(self.cau_res)
    self.int_cau_cap = np.cumsum(self.cau_cap)
```

The high-precision arithmetic is crucial for this method, as the polynomial division process is numerically sensitive. PyRth uses the MPFR library (via gmpy2) to perform arbitrary-precision calculations.

2. Sobhy Method
------------------

The Sobhy method uses continued fractions expansion to perform the Foster to Cauer transformation.

### Mathematical Approach

The method computes the continued fraction representation by:
1. Calculating the Foster transfer function coefficients
2. Applying a specific recurrence relation to obtain the Cauer elements

### Implementation in PyRth

```python
def sobhy_method(self, N):
    A = [[mpfr("0.0")] * (N) for i in range(N + 1)]
    B = [[mpfr("0.0")] * (N) for i in range(N + 1)]
    
    for i in range(N):
        A[0][i] = self.cleaned_mpfr_denom[i]
        B[0][i] = self.cleaned_mpfr_denom[i]
    
    for i in range(N - 1):
        A[1][i] = self.cleaned_mpfr_num[i + 1]
    
    # Apply the Sobhy recurrence relations
    for k in range(N - 1):
        j = 1
        B[j][k] = A[j - 1][k + 1] - A[j - 1][0] / A[j][0] * A[j][k + 1]
    
    for j in range(2, N + 1):
        for k in range(N - j):
            A[j][k] = B[j - 1][k + 1] - B[j - 1][0] / A[j - 1][0] * A[j - 1][k + 1]
        for k in range(N - j):
            B[j][k] = A[j - 1][k + 1] - A[j - 1][0] / A[j][0] * A[j][k + 1]
    
    # Extract the Cauer network parameters
    a = [None] * (N - 1)
    b = [None] * (N - 1)
    
    for m in range(1, N):
        a[m - 1] = A[m - 1][0] / A[m][0]
        b[m - 1] = B[m][0] / A[m][0]
    
    return a, b
```

3. Khatwani Method
------------------------

The Khatwani method uses Markov parameters to perform the transformation.

### Mathematical Approach

1. Generate Markov parameters from the Foster transfer function
2. Use these parameters to build a specific matrix
3. Apply recurrence relations to extract Cauer elements

### Implementation in PyRth

```python
def khatwani_method(self, N, markov_parameters):
    a_matrix = [[None] * (2 * N) for i in range(N + 1)]
    a_matrix[0] = [mpfr("0.0")] * (2 * N)
    a_matrix[0][0] = mpfr("1.0")
    
    large_h = [None] * (N - 1)
    small_h = [None] * (N - 1)
    
    for i in range(2 * N):
        a_matrix[1][i] = markov_parameters[i]
    
    large_h[0] = a_matrix[0][0] / a_matrix[1][0]
    small_h[0] = (a_matrix[0][1] - large_h[0] * a_matrix[1][1]) / a_matrix[1][0]
    
    # Apply Khatwani recurrence relations
    for i in range(2, N):
        for j in range(2 * N - (i - 1) * 2):
            a_matrix[i][j] = (
                a_matrix[i - 2][j + 2]
                - large_h[i - 2] * a_matrix[i - 1][j + 2]
                - small_h[i - 2] * a_matrix[i - 1][j + 1]
            )
        
        large_h[i - 1] = a_matrix[i - 1][0] / a_matrix[i][0]
        small_h[i - 1] = (
            a_matrix[i - 1][1] - large_h[i - 1] * a_matrix[i][1]
        ) / a_matrix[i][0]
    
    return large_h, small_h
```

4. Lanczos Method
----------------------

The Lanczos method is based on orthogonal polynomials and offers good numerical stability.

### Mathematical Approach

The method uses a sequence of orthogonal polynomials to find the Cauer network parameters. It avoids explicit polynomial division, making it more numerically stable.

### Implementation in PyRth

```python
def lanczos(self):
    res, cap = eng.lanczos_inner(self.therm_capa_fost, self.therm_resist_fost)
    
    self.cau_res = np.array(res)
    self.cau_cap = np.array(cap)
    
    # Optional: Combine small elements for smoothing
    if self.blockwise_sum_width > 1:
        # Calculate the number of blocks
        num_blocks = len(self.cau_res) // self.blockwise_sum_width
        # Create an array of indices for each block
        indices = np.arange(num_blocks) * self.blockwise_sum_width
        # Calculate the blockwise sum
        self.cau_res = np.add.reduceat(self.cau_res, indices)
        self.cau_cap = np.add.reduceat(self.cau_cap, indices)
    
    self.int_cau_res = np.cumsum(self.cau_res)
    self.int_cau_cap = np.cumsum(self.cau_cap)
```

The core implementation is in the `lanczos_inner` function, which is accelerated using Numba:

```python
@njit(cache=True)
def lanczos_inner(cap_fost=np.array([]), res_fost=np.array([])):
    C_diag = cap_fost
    K_diag = 1.0 / res_fost
    
    # Initialize g as a vector of ones
    g = np.ones_like(C_diag)
    # Solve Cr = g for r
    r = g / C_diag
    
    # Initialize variables
    beta = np.sqrt(np.dot(r.T, g))
    v = np.zeros_like(r)
    
    # Initialize lists for res and cap
    res = []
    cap = []
    
    # Compute the first Cauer elements
    u = r / beta
    alpha = -np.dot(u.T, K_diag * u)
    r = (-(K_diag + alpha * C_diag) * u - beta * C_diag * v) / C_diag
    beta_next = np.sqrt(np.dot(r.T, C_diag * r))
    v = u
    
    cap.append(1 / (beta**2))
    res.append(-1 / (alpha * cap[0]))
    
    # Iteratively compute remaining elements
    # (Implementation continues...)
```

5. de Boor–Golub Method
-----------------------------

The de Boor–Golub method is another approach based on orthogonal polynomials.

### Mathematical Approach

This method constructs a sequence of orthogonal polynomials with respect to a specific inner product. The recurrence coefficients of these polynomials directly give the Cauer network parameters.

### Implementation in PyRth

```python
def boor_golub(self):
    # Extract poles from Foster network
    poles = []
    for R, C in zip(self.mpfr_resist_fost, self.mpfr_capa_fost):
        if R > 0 and C > 0:
            poles.append(mpfr("-1.0") / (R * C))
    
    M = len(poles) - 1
    w_0 = [0] * (M + 1)
    
    for i in range(M + 1):
        w_0[i] = mpfr("1.0") / self.mpfr_capa_fost[i]
    
    # Apply the de Boor-Golub algorithm
    k = [mpfr("0.0")] * (2 * (M + 1))
    
    w_sum = mpfr("0.0")
    for w in w_0:
        w_sum = w_sum + w
    
    k[1] = mpfr("1.0") / w_sum
    
    # Compute Cauer elements using recurrence relations
    # (Implementation continues...)
```

Structure Function Types
-------------------------------

PyRth calculates and visualizes three types of structure functions:

1. **Cumulative Structure Function (CSF)**
   
   The cumulative structure function plots the cumulative thermal resistance against the cumulative thermal capacitance:
   
   .. math::
      
      CSF = \{(C_{th,cum}(i), R_{th,cum}(i))\}
   
   Where:
   - :math:`C_{th,cum}(i) = \sum_{j=1}^{i} C_j` is the cumulative thermal capacitance
   - :math:`R_{th,cum}(i) = \sum_{j=1}^{i} R_j` is the cumulative thermal resistance
   
   This function represents the one-dimensional heat flow path from the heat source to the ambient, where each point corresponds to a location along the path.

2. **Differential Structure Function (DSF)**
   
   The differential structure function is the derivative of the cumulative structure function, plotting the rate of change of resistance with respect to capacitance:
   
   .. math::
      
      DSF(i) = \frac{dR_{th,cum}(i)}{dC_{th,cum}(i)}
   
   In PyRth, this is calculated as:
   
   ```python
   for i in range(len(self.int_cau_res) - 1):
       if not (self.int_cau_res[i] - self.int_cau_res[i + 1]) == 0.0:
           self.diff_struc[i] = (self.int_cau_cap[i] - self.int_cau_cap[i + 1]) / (
               self.int_cau_res[i] - self.int_cau_res[i + 1]
           )
   ```
   
   The DSF represents the thermal resistance density, which correlates with material properties and cross-sectional area changes along the heat flow path.

3. **Time Constant Spectrum (TCS)**
   
   The time constant spectrum plots thermal resistance contributions against time constants:
   
   .. math::
      
      TCS = \{(\tau_i, R_i)\}
   
   This representation helps identify dominant thermal time constants in the system.

Choosing the Structure Function Method
------------------------------------

Each method has its advantages and limitations:

| Method | Advantages | Limitations | Best For |
| **Sobhy** | Good all-around performance<br>Default choice | Requires arbitrary precision | General use |
| **Lanczos** | Numerically stable<br>Fast computation | May smooth fine details | Large datasets |
| **Khatwani** | Robust for simple systems | Slower than Lanczos | Non-complex thermal paths |
| **de Boor-Golub** | Good numerical behavior | Requires arbitrary precision | Theoretical analysis |
| **Polynomial** | Direct implementation | Numerically sensitive | When other methods fail |

The method is selected using the `struc_method` parameter:

```python
params = {
    "data": measurement_data,
    "input_mode": "impedance",
    "struc_method": "sobhy",  # or "lanczos", "boor_golub", "khatwani", "polylong"
    # Other parameters
}

evaluator = Evaluation()
result = evaluator.standard_module(params)
```

Practical Interpretation of Structure Functions
----------------------------------------------------

Structure functions provide valuable insights into the thermal system:

1. **Layer Identification**
   
   Peaks in the differential structure function often correspond to material interfaces or geometric changes in the thermal path.

2. **Thermal Bottlenecks**
   
   Steep rises in the cumulative structure function indicate high thermal resistance regions (thermal bottlenecks).

3. **Component Sizing**
   
   The thermal capacitance axis correlates with the volume of materials, helping identify component sizes.

4. **Boundary Conditions**
   
   The final plateau in the cumulative structure function represents the thermal resistance to ambient.

References
--------------------

1. Székely, V. (1998). On the representation of infinite-length distributed RC one-ports. IEEE Transactions on Circuits and Systems I: Fundamental Theory and Applications, 45(7), 711-719.

2. Rencz, M., & Székely, V. (2004). Studies on the nonlinearity effects in dynamic compact model generation of packages. IEEE Transactions on Components and Packaging Technologies, 27(1), 124-130.

3. Sobhy, E. A., & Shaker, M. M. (1982). Method of computing the continuous fraction expansion coefficients for the Bode ideal transfer function. IEEE Transactions on Circuits and Systems, 29(10), 687-693.

4. Lanczos, C. (1952). An iteration method for the solution of the eigenvalue problem of linear differential and integral operators. Journal of Research of the National Bureau of Standards, 45, 255-282.

5. de Boor, C., & Golub, G. H. (1978). The numerically stable reconstruction of a Jacobi matrix from spectral data. Linear Algebra and Its Applications, 21(3), 245-260.