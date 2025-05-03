.. _nid_boor_golub:

de Boor–Golub Algorithm
=======================
The **de Boor–Golub algorithm** (BG) offers a third,
numerically elegant route from the *parallel* Foster ladder to
the *series* Cauer ladder.
Unlike long-division, Khatwani, or Sobhy, BG works directly with the
**poles and weights** of the Foster impedance and never manipulates
high-order polynomials explicitly.  
The version given here follows Parthasarathy & Feldman, with the algebra
simplified for network identification by deconvolution (NID).


Two equivalent forms of the impedance
-----------------------------------------
* **S-fraction** (Cauer ladder with alternating thermal capacitances
  :math:`k_{1},k_{3},\dots` and resistances :math:`k_{2},k_{4},\dots`):

  .. math:: 
     :label: eq_s_fraction

     Z(s)=
     \cfrac{1}{
       k_{1}s+\cfrac{1}{
       k_{2}+\cfrac{1}{
       k_{3}s+\dots+\cfrac{1}{k_{2N+1}s}}}}

  See also the J-fraction to S-fraction conversion in :ref:`J-fraction`.

* **Pole–zero product**

  .. math::
     :label: eq_pole_zero

     Z(s)=
     \frac{1}{k_{1}}\;
     \frac{\displaystyle\prod_{k=1}^{N}\bigl(1+s/z_{k}\bigr)}
          {\displaystyle\prod_{k=1}^{N+1}\bigl(1+s/s_{k}\bigr)}
     \;=\;
     \frac{1}{k_{1}}\,
     \frac{A_{N}(s)}{B_{N+1}(s)}

  where the poles lie at :math:`-s_{1},\dots,-s_{N+1}` and the zeros at
  :math:`-z_{1},\dots,-z_{N}`. For details on the pole-zero representation in the Foster network, see :ref:`nid_foster_network`.

Recurrence relation
----------------------------------

Comparing :eq:`eq_s_fraction` and :eq:`eq_pole_zero` yields a three-term recurrence for
:math:`B_{n}(s)`:

.. math::
   :label: eq_recurrence

   \begin{aligned}
   B_{1}(s)&=(s+\lambda_{0})B_{0}(s),\\
   B_{n}(s)&=(s+\lambda_{n-1}+\mu_{n-1})B_{n-1}(s)
            -\lambda_{n-2}\mu_{n-1}B_{n-2}(s),
            && n=2,\dots,N,\\
   B_{N+1}(s)&=(s+\mu_{N})B_{N}(s)-\lambda_{N-1}\mu_{N}B_{N-1}(s).
   \end{aligned}

The unknown scalars :math:`\lambda_{n}` and :math:`\mu_{n}` are determined
on the fly by the scalar products that fix :math:`\lambda_{n}` and :math:`\mu_{n}`.

Define the weighted inner products

.. math::
   :label: eq_inner_product_norm

   \begin{aligned}
   \langle B_{n},B_{n}\rangle &=\sum_{k=0}^{N} B_{n}^{2}(s_{k})\,w_{0k}
   \end{aligned}

.. math::
   :label: eq_inner_product_moment

   \begin{aligned}
   \langle sB_{n},B_{n}\rangle &=\sum_{k=0}^{N} s_{k}\,B_{n}^{2}(s_{k})\,w_{0k}
   \end{aligned}

Then:

.. math::
   :label: eq_lambda_mu_product

   \begin{aligned}
   \lambda_{n-1}\mu_{n}&=\frac{\langle B_{n},B_{n}\rangle}
                              {\langle B_{n-1},B_{n-1}\rangle},
                              && n=1,\dots,N
   \end{aligned}\,.

.. math::
   :label: eq_lambda_mu_sum

   \begin{aligned}
   \lambda_{n}+\mu_{n}&=\frac{\langle sB_{n},B_{n}\rangle}
                             {\langle B_{n},B_{n}\rangle},
                              && n=1,\dots,N
   \end{aligned}


For a general pole–zero form the weights :math:`w_{0k}` are

.. math::
   :label: eq_weights

   w_{0k}=\frac{A_{N}(s_{k})}{B_{N+1}'(s_{k})}
          =
   \frac{\displaystyle\prod_{i=1}^{N}(z_{i}-s_{k})}
        {\displaystyle\prod_{i=0,i\ne k}^{N}(s_{i}-s_{k})}\,.

With the Foster sum

.. math::
   :label: eq_foster_sum

   Z(s)=\sum_{k=0}^{N}\frac{w_{0k}}{s+s_{k}}

the poles are :math:`s_{k}=1/(R_{k}C_{k})`
and the weights are simply :math:`w_{0k}=1/C_{k}`— 
no zeros need to be computed.

Initial value
Start the iteration with

.. math::
   :label: eq_initial_values

   B_{0}(s)=1,\qquad
   \lambda_{0}=\frac{\sum_{k=0}^{N}s_{k}w_{0k}}{\sum_{k=0}^{N}w_{0k}}

Recovering the Cauer coefficients
-------------------------------------
Once all :math:`\lambda_{n},\mu_{n}` are known the ladder elements follow:

.. math::
   :label: eq_cauer_k1_k2

   \begin{aligned}
   k_{1}&=\frac{1}{\sum_{k=0}^{N}w_{0k}},                                     & 
   k_{2}&=\frac{1}{k_{1}\lambda_{0}}
   \end{aligned}

.. math::
   :label: eq_cauer_k2n_k2n1

   \begin{aligned}
   k_{2n}&=\frac{\mu_{1}\mu_{2}\cdots\mu_{n-1}}
                {k_{1}\lambda_{0}\lambda_{1}\cdots\lambda_{n-1}},      & 
   k_{2n+1}&=\frac{k_{1}\lambda_{0}\lambda_{1}\cdots\lambda_{n-1}}
                  {\mu_{1}\mu_{2}\cdots\mu_{n}},               
                                                     \quad n=1,\dots,N
   \end{aligned}

Here :math:`k_{2n}` are **thermal resistances**,
:math:`k_{2n+1}` the **thermal capacitances**.

Algorithm summary
---------------------

.. admonition:: de Boor-Golub Algorithm for Foster-to-Cauer Conversion

    **Input:** Foster poles :math:`s_k = 1/(R_k C_k)` and weights :math:`w_{0k} = 1/C_k`
    
    **Output:** Cauer ladder elements :math:`\{k_1 \ldots k_{2N+1}\}`
    
    #. :math:`\lambda_0 = \frac{\sum_{k=0}^{N}s_k w_{0k}}{\sum_{k=0}^{N}w_{0k}}`  (weighted mean of poles)
    #. :math:`B_0(s) = 1`
    #. :math:`B_1(s) = s+\lambda_0`
    #. **for** :math:`n = 1 \ldots N` **do**
        
        #. Compute :math:`\langle B_n,B_n \rangle` and :math:`\langle sB_n,B_n \rangle`
        #. :math:`\lambda_{n-1} \mu_n = \frac{\langle B_n,B_n \rangle}{\langle B_{n-1},B_{n-1} \rangle}`
        #. :math:`\lambda_n + \mu_n = \frac{\langle sB_n,B_n \rangle}{\langle B_n,B_n \rangle}`
        #. Solve for :math:`\lambda_n, \mu_n` from the two equations above
        #. :math:`B_{n+1}(s) = (s+\lambda_n+\mu_n)B_n(s) - \lambda_{n-1}\mu_n B_{n-1}(s)`
        
    #. **end for**
    #. Compute Cauer elements:
        
        #. :math:`k_1 = \frac{1}{\sum_{k=0}^{N}w_{0k}}`
        #. :math:`k_2 = \frac{1}{k_1\lambda_0}`
        #. For :math:`n = 1 \ldots N`:
            
            #. :math:`k_{2n} = \frac{\mu_1\mu_2\cdots\mu_{n-1}}{k_1\lambda_0\lambda_1\cdots\lambda_{n-1}}`
            #. :math:`k_{2n+1} = \frac{k_1\lambda_0\lambda_1\cdots\lambda_{n-1}}{\mu_1\mu_2\cdots\mu_n}`
