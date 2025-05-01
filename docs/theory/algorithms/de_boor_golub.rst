de Boor-Golub Algorithm
=======================

The de Boor-Golub algorithm is a matrix-based method in PyRth for transforming a Foster thermal network into a Cauer network, which is essential for structure function calculations.

Algorithm Description
------------------------

The de Boor-Golub method provides a numerically stable approach to Foster-to-Cauer conversion by reformulating the problem as a symmetric eigenvalue problem. This matrix-based technique avoids some of the numerical instabilities associated with polynomial division.

Mathematical Formulation
---------------------------

The de Boor-Golub algorithm leverages the observation that the Foster-to-Cauer conversion is mathematically equivalent to finding the eigenvalues and first components of the eigenvectors of a symmetric tridiagonal matrix.

Given Foster network elements (resistances :math:`R_i` and capacitances :math:`C_i`), the process involves:

1. Creating a symmetric tridiagonal Jacobi matrix :math:`J` from the Foster elements
2. Computing the eigenvalues and eigenvectors of this matrix
3. Extracting the Cauer network elements from these eigenvalues and eigenvectors

The Jacobi matrix is formed with:

.. math::

    J = \begin{pmatrix}
        a_1 & b_1 & 0 & 0 & \cdots & 0 \\
        b_1 & a_2 & b_2 & 0 & \cdots & 0 \\
        0 & b_2 & a_3 & b_3 & \cdots & 0 \\
        \vdots & \vdots & \vdots & \vdots & \ddots & \vdots \\
        0 & 0 & 0 & 0 & \cdots & a_n
    \end{pmatrix}

Where :math:`a_i` and :math:`b_i` are derived from the Foster network elements.

Implementation Details
------------------------

In PyRth, the de Boor-Golub algorithm is implemented using both standard precision and arbitrary precision arithmetic:

.. code-block:: python

    def de_boor_golub_method(self):
        """
        Convert Foster to Cauer network using the de Boor-Golub method.
        """
        # Get the number of Foster elements
        n = len(self.foster_r)
        
        # Initialize the tridiagonal Jacobi matrix elements
        a = np.zeros(n)  # Diagonal elements
        b = np.zeros(n-1)  # Off-diagonal elements
        
        # Calculate matrix coefficients from Foster elements
        for i in range(n):
            # Time constant for this element
            tau_i = self.foster_r[i] * self.foster_c[i]
            
            # Diagonal element contribution
            a[i] = tau_i
            
            # Off-diagonal element (for all but the last row)
            if i < n-1:
                b[i] = np.sqrt(tau_i * self.foster_r[i] * self.foster_r[i+1])
        
        # Create the tridiagonal matrix
        diagonals = [b, a, b]  # Off-diagonal, main diagonal, off-diagonal
        offsets = [-1, 0, 1]  # Positions of the diagonals
        J = sparse.diags(diagonals, offsets).toarray()
        
        # Compute eigenvalues and eigenvectors
        eigenvalues, eigenvectors = linalg.eigh(J)
        
        # Sort eigenvalues and eigenvectors (ascending order)
        idx = np.argsort(eigenvalues)
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]
        
        # Extract Cauer elements from eigenvalues and eigenvectors
        sum_r = np.sum(self.foster_r)  # Total resistance
        
        # Calculate Cauer resistances
        self.cauer_r = np.zeros(n)
        for i in range(n):
            # First component of eigenvector squared, scaled by total resistance
            self.cauer_r[i] = sum_r * eigenvectors[0, i]**2
        
        # Calculate Cauer capacitances
        self.cauer_c = np.zeros(n-1)
        for i in range(n-1):
            # Derived from eigenvalues and resistances
            self.cauer_c[i] = 1.0 / (eigenvalues[i+1] - eigenvalues[i]) / self.cauer_r[i+1]

Arbitrary Precision Implementation
----------------------------------------

For high-order networks or systems with widely varying time constants, PyRth provides an arbitrary precision implementation using the `gmpy2` library:

.. code-block:: python

    def de_boor_golub_mpfr(self):
        """
        Arbitrary precision implementation of the de Boor-Golub method.
        """
        # Get the number of Foster elements
        n = len(self.mpfr_resist_fost)
        
        # Set high precision for calculations
        mpfr.set_default_prec(512)
        
        # Initialize matrix elements
        a = np.array([mpfr("0.0")] * n)
        b = np.array([mpfr("0.0")] * (n-1))
        
        # Calculate matrix coefficients
        for i in range(n):
            tau_i = self.mpfr_resist_fost[i] * self.mpfr_capa_fost[i]
            a[i] = tau_i
            
            if i < n-1:
                b[i] = (tau_i * self.mpfr_resist_fost[i] * self.mpfr_resist_fost[i+1]) ** mpfr("0.5")
        
        # The eigenvalue problem is solved using a specialized high-precision algorithm
        # (implementation details omitted for brevity)
        
        # Convert results back to standard floating-point
        self.cauer_r = np.array([float(r) for r in cauer_r_mpfr])
        self.cauer_c = np.array([float(c) for c in cauer_c_mpfr])

Numerical Considerations
---------------------------

The de Boor-Golub method offers several numerical advantages:

1. **Symmetry Preservation**: The symmetric tridiagonal formulation helps maintain numerical stability
2. **Eigenvalue Computation**: Leverages highly optimized eigenvalue solvers
3. **Condition Number**: Generally better conditioned than polynomial division for networks with widely varying time constants
4. **Error Distribution**: Tends to distribute errors more evenly across the spectrum

The method is particularly effective for systems with:
- Large numbers of Foster elements
- Wide dynamic range of time constants
- Need for high accuracy in all parts of the spectrum

Advantages and Limitations
-----------------------------

**Advantages:**
- Generally more numerically stable than polynomial division
- Efficient for high-order networks
- Well-suited for systems with widely separated time constants
- Can leverage optimized eigenvalue solving libraries
- Error distribution tends to be more uniform

**Limitations:**
- Requires matrix operations, which can be more complex to implement
- May still require arbitrary precision for extreme cases
- Memory usage scales quadratically with the number of elements
- Eigenvalue calculation can be computationally intensive

Comparison to Other Methods
----------------------------

The de Boor-Golub method offers a middle ground between several approaches:

- More numerically stable than polynomial division
- Less specialized than the Khatwani method
- More general than the Lanczos method
- Potentially more accurate than the Sobhy method for certain networks

Usage in PyRth
-----------------

To use the de Boor-Golub method in PyRth, specify it in the configuration:

.. code-block:: python

    params = {
        "foster_to_cauer_algorithm": "de_boor_golub",
        # Other parameters...
    }
    
    analysis = Evaluation().standard_module(params)
    
    # Resulting Cauer network elements are accessible via:
    cauer_r = analysis.cauer_r  # Cauer resistances
    cauer_c = analysis.cauer_c  # Cauer capacitances