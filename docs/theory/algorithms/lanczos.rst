Lanczos Algorithm
===================

The Lanczos algorithm is a specialized iterative method in PyRth for performing network transformation, specifically optimized for thermal structure function extraction from large-scale Foster networks.

Algorithm Description
-----------------------------------

The Lanczos algorithm is an iterative method that transforms a given matrix into a tridiagonal form. In PyRth, it is adapted for use in Foster-to-Cauer network conversion, particularly when dealing with large-scale networks where direct matrix methods might be computationally intensive.

Mathematical Foundation
------------------------------------

The Lanczos method applies an efficient Krylov subspace technique to progressively construct a sequence of orthogonal vectors and a tridiagonal matrix. This process efficiently extracts information about the dominant eigenvalues and eigenvectors of the system.

For thermal network transformation, the algorithm works with a symmetric matrix constructed from the Foster network elements:

.. math::

    \mathbf{T} = \mathbf{D}^{1/2} \mathbf{A} \mathbf{D}^{1/2}

where:
- :math:`\mathbf{A}` is a matrix derived from the Foster network
- :math:`\mathbf{D}` is a diagonal scaling matrix

The Lanczos iteration proceeds as follows:

1. Start with an initial vector :math:`\mathbf{q}_1`
2. For :math:`j = 1, 2, \ldots, m`:
   a. :math:`\mathbf{v} = \mathbf{T} \mathbf{q}_j`
   b. :math:`\alpha_j = \mathbf{q}_j^\top \mathbf{v}`
   c. :math:`\mathbf{v} = \mathbf{v} - \alpha_j \mathbf{q}_j`
   d. If :math:`j > 1`: :math:`\mathbf{v} = \mathbf{v} - \beta_{j-1} \mathbf{q}_{j-1}`
   e. :math:`\beta_j = \|\mathbf{v}\|_2`
   f. :math:`\mathbf{q}_{j+1} = \mathbf{v} / \beta_j`

This creates a tridiagonal matrix with diagonal elements :math:`\alpha_j` and off-diagonal elements :math:`\beta_j`.

Implementation in PyRth
------------------------------------

The Lanczos algorithm in PyRth is implemented with optimizations for thermal network applications:

.. code-block:: python

    @njit(cache=True)
    def lanczos_inner(A, v0, max_iter, reorthogonalize=True):
        """
        Core Lanczos iteration for tridiagonalization.
        
        Parameters:
        -----------
        A : ndarray
            The symmetric matrix to tridiagonalize.
        v0 : ndarray
            The initial vector.
        max_iter : int
            Maximum number of iterations.
        reorthogonalize : bool
            Whether to perform full reorthogonalization.
            
        Returns:
        --------
        T : ndarray
            Tridiagonal matrix.
        V : ndarray
            Matrix of Lanczos vectors.
        """
        n = A.shape[0]
        T = np.zeros((max_iter, max_iter))
        V = np.zeros((n, max_iter+1))
        
        # Normalize the initial vector
        beta = np.linalg.norm(v0)
        V[:, 0] = v0 / beta
        
        # Main Lanczos iteration
        for j in range(max_iter):
            # Compute A*v_j
            w = A @ V[:, j]
            
            # Alpha_j = v_j^T * A * v_j
            alpha = np.dot(V[:, j], w)
            T[j, j] = alpha
            
            # w = w - alpha*v_j - beta*v_{j-1}
            w = w - alpha * V[:, j]
            if j > 0:
                w = w - T[j-1, j] * V[:, j-1]
                
            # Optional full reorthogonalization for stability
            if reorthogonalize:
                for i in range(j+1):
                    w = w - np.dot(V[:, i], w) * V[:, i]
            
            # Beta_{j+1} = ||w||
            beta = np.linalg.norm(w)
            
            # Early termination check (breakdown)
            if beta < 1e-12:
                return T[:j+1, :j+1], V[:, :j+1]
            
            # v_{j+1} = w / beta
            V[:, j+1] = w / beta
            
            # Store beta in the tridiagonal matrix
            if j < max_iter-1:
                T[j, j+1] = beta
                T[j+1, j] = beta
                
        return T[:max_iter, :max_iter], V[:, :max_iter]

This implementation is then used for network transformation:

.. code-block:: python

    def lanczos_foster_to_cauer(self):
        """
        Convert Foster to Cauer network using the Lanczos method.
        """
        # Form the matrix from Foster elements
        n = len(self.foster_r)
        A = np.zeros((n, n))
        
        # Build the matrix using Foster network properties
        for i in range(n):
            tau_i = self.foster_r[i] * self.foster_c[i]
            for j in range(n):
                tau_j = self.foster_r[j] * self.foster_c[j]
                A[i, j] = np.sqrt(tau_i * tau_j) * np.sqrt(self.foster_r[i] * self.foster_r[j])
        
        # Initial vector for Lanczos (can be optimized based on problem)
        v0 = np.ones(n) / np.sqrt(n)
        
        # Perform Lanczos tridiagonalization
        T, V = lanczos_inner(A, v0, n)
        
        # Extract eigenvalues and eigenvectors from tridiagonal matrix
        eigenvalues, eigenvectors = np.linalg.eigh(T)
        
        # Convert to Cauer network elements
        total_r = np.sum(self.foster_r)
        
        # Calculate Cauer resistances
        self.cauer_r = np.zeros(n)
        for i in range(n):
            self.cauer_r[i] = total_r * V[0, i]**2
        
        # Calculate Cauer capacitances
        self.cauer_c = np.zeros(n-1)
        for i in range(n-1):
            self.cauer_c[i] = 1.0 / (eigenvalues[i+1] - eigenvalues[i]) / self.cauer_r[i+1]

Optimizations and Numerical Stability
--------------------------------------------------

The Lanczos method in PyRth includes several optimizations and stability enhancements:

1. **Reorthogonalization**: Full or selective reorthogonalization to combat loss of orthogonality
2. **Implicit Restart**: To enhance convergence to specific eigenvalues
3. **Breakdown Detection**: Early termination when the algorithm reaches numerical precision limits
4. **Thick Restart**: For extracting specific portions of the spectrum
5. **Preconditioning**: Optional preconditioning for ill-conditioned networks

Adaptive Precision Handling
----------------------------------------

For networks with widely varying time constants, PyRth implements precision adaptation:

.. code-block:: python

    def adaptive_lanczos(self):
        """
        Apply Lanczos algorithm with adaptive precision.
        """
        # Analyze network condition
        dynamic_range = self._estimate_network_dynamic_range()
        
        # Choose precision based on dynamic range
        if dynamic_range > 1e8:
            # Use high-precision implementation
            return self._lanczos_mpfr()
        else:
            # Use standard double-precision implementation
            return self._lanczos_standard()

Advantages and Limitations
----------------------------------------

**Advantages:**
- Memory-efficient for large networks
- Focuses computational effort on the most relevant eigenvalues
- Can terminate early when sufficient accuracy is reached
- Well-suited for networks with clustered eigenvalues
- Iterative approach allows for adaptive precision

**Limitations:**
- May suffer from loss of orthogonality without reorthogonalization
- Convergence depends on initial vector choice
- Less efficient than direct methods for small networks
- May require more iterations for networks with widely separated time constants

When to Use Lanczos Method
---------------------------------------

The Lanczos method is particularly advantageous in these scenarios:

1. **Large Networks**: When the Foster network contains many elements (>100)
2. **Limited Memory**: When memory constraints prevent using direct matrix methods
3. **Clustered Time Constants**: For systems with groups of similar time constants
4. **Incremental Refinement**: When progressive refinement of results is desired

Usage in PyRth
--------------------------------------------------

To use the Lanczos method for network transformation:

.. code-block:: python

    params = {
        "foster_to_cauer_algorithm": "lanczos",
        "lanczos_max_iter": 100,  # Maximum iterations
        "lanczos_tol": 1e-12,     # Tolerance for convergence
        "lanczos_reorthogonalize": True,  # Enable reorthogonalization
        # Other parameters...
    }
    
    analysis = StructureFunction(params)
    
    # Resulting network is accessible via:
    cauer_r = analysis.cauer_r  # Cauer resistances
    cauer_c = analysis.cauer_c  # Cauer capacitances