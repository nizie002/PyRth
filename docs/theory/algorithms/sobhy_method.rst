.. _nid_sobhy:

Sobhy's Method
==============
**Sobhy's algorithm** also converts the rational impedance
:math:`Z(s)` (Equation :eq:`sobhy_zs`) to the :math:`H`–:math:`h` continued fraction of Equation :eq:`sobhy_h_h_frac`,
but it bypasses Markov parameters, which are calculated in Khatwani's method entirely.  
Instead it builds two interlaced triangular rows :math:`A` and :math:`B` whose first
columns yield :math:`H_i , h_i` directly.

Sobhy's method is faster than Khatwani's, but requires the same arbitrary-precision as polynomial long division.

Initialisation
------------------
Write again

.. math:: 
   :label: sobhy_zs

   Z(s)=
   \frac{\alpha_0+\alpha_1s+\dots+\alpha_{N-1}s^{N-1}}
        {\beta_0+\beta_1s+\dots+\beta_{N-1}s^{N-1}+\beta_N s^{N}} .

The :math:`H`–:math:`h` continued fraction for this is:

.. math::
   :label: sobhy_h_h_frac

   Z(s)=
   \cfrac{1}{
     H_1 s+h_1+
     \cfrac{1}{
       H_2 s+h_2+\ddots+
       \cfrac{1}{H_N s+h_N}}}


Create the calculation table (un-labelled positions are zero)

.. math::
   :label: sobhy_calc_table

   \begin{pmatrix}
   A_{0,1}&A_{0,2}&A_{0,3}&\dots&\dots&A_{0,N+1}\\
   B_{0,1}&B_{0,2}&B_{0,3}&\dots&\dots&B_{0,N+1}\\[2pt]
   A_{1,1}&A_{1,2}&A_{1,3}&\dots&A_{1,N}&\\
   B_{1,1}&B_{1,2}&B_{1,3}&\dots&B_{1,N}&\\
   \vdots &\vdots & &    &  &\\
   A_{N,1}\\
   B_{N,1}
   \end{pmatrix}\!.

Seed rows

.. math::
   :label: sobhy_seed_rows

   A_{0,j}=B_{0,j}= \beta_{N+1-j},\qquad
   A_{1,j}= \alpha_{N-j}.

Iterative filling rule
--------------------------

For :math:`i = 1,2,\dots, N` and :math:`j = 1,2,\dots`

.. math::
   :label: sobhy_iterative_a

   A_{i,j}=B_{\,i-1,j+1}-\frac{B_{\,i-1,1}}{A_{\,i-1,1}}\;A_{\,i-1,j+1},

.. math::
   :label: sobhy_iterative_b

   B_{i,j}=A_{\,i-1,j+1}-\frac{A_{\,i-1,1}}{A_{\,i,1}}\;A_{\,i,j+1}.

Proceed until every element needed for the first columns
:math:`A_{i,1},\,B_{i,1}` (*i* = 1…*N*) has been computed.

Extracting **H** and **h**
------------------------------
Simply

.. math::
   :label: sobhy_h_h_coef

   H_i=\frac{B_{i-1,1}}{A_{i,1}},\qquad
   h_i=\frac{B_{i,1}}  {A_{i,1}},\qquad i=1,\dots,N.

These coefficients give the :math:`H`–:math:`h` continued fraction (Equation :eq:`sobhy_h_h_frac`); convert
to J- and S-fractions with the formulas collected on the
:ref:`J-fraction` page to obtain the Cauer ladder.
