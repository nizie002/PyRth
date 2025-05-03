.. _nid_khatwani:

Khatwani's Method
===================

**Khatwani's algorithm** converts the rational driving-point impedance
straight into the :math:`H_k,h_k` continued fraction (Equation :eq:`eq:simpler_form` of the
:ref:`J-fraction` page).  The scheme relies only on

1. The first :math:`2N` **Markov parameters** (Maclaurin coefficients) of
   :math:`Z(s)`,
2. A fast **polynomial inverse** built by Newton doubling,
3. A triangular **calculation table** that yields :math:`H_i, h_i`.

Khatwani's method requires arbitrary-precision floating-point arithmetic and for very large systems,
precision limitations can become even more severe than in polynomial long division.

Prerequisites
----------------

Start from the rational form (same as Equation :eq:`eq:rational_impedance` earlier)

.. math::
   :label: eq:khatwani_rational

   Z(s)=
   \frac{\alpha_0+\alpha_1s+\dots+\alpha_{N-1}s^{N-1}}
        {\beta_0+\beta_1s+\dots+\beta_{N-1}s^{N-1}+\beta_N s^{N}} .

Markov parameters
-------------------

Expand about :math:`s=\infty` (equivalently :math:`t=1/s\to 0`):

.. math::
   :label: eq:markov_expansion

   Z(s)=\sum_{i=1}^{\infty}\frac{y_i}{s^{\,i}}
        =\sum_{i=1}^{\infty}y_i t^{\,i} .

Write :math:`Z(t)` explicitly by dividing numerator and denominator by
:math:`\beta_N` and reversing the order of coefficients

.. math::
   :label: eq:zt_expanded

   \begin{aligned}
   Z(t)&=
   \frac{
     \gamma_1 t+\gamma_2 t^2+\dots+\gamma_{N-1}t^{N-1}+\gamma_N t^{N}}
        {1+\delta_1 t+\dots+\delta_{N-1}t^{N-1}+\delta_N t^{N}} ,
   \end{aligned}

where the new coefficients are

.. math::
   :label: eq:gamma_delta

   \gamma_i=\alpha_{N-i}/\beta_N ,
   \qquad
   \delta_i=\beta_{N-i}/\beta_N .


The strategy to obtain the Markov parameters is to invert the denominator of :eq:`eq:zt_expanded` and multiply
it with the numerator. In the following, an algorithm for polynomial inversion is described.

Polynomial inverse by Newton doubling
-------------------------------------

Let

.. math::
   :label: eq:poly_p

   P(t)=1+\delta_1 t+\dots+\delta_N t^N .

We need :math:`Q(t)=P(t)^{-1}` accurate up to degree :math:`2N` so that
:math:`Z(t)=Q(t)\,(\gamma_1 t+\dots+\gamma_N t^N)` reproduces the first
:math:`2N` Markov parameters.

For any integer :math:`i` we call
:math:`Q_i(t)` an :math:`i`-degree inverse if

.. math::
   :label: eq:i_degree_inverse

   P(t)\,Q_i(t)=1+\mathcal O\!\bigl(t^{\,i}\bigr) .

Set :math:`Q_1(t)=1` .  With

.. math::
   :label: eq:error_term

   E_i(t)=\frac{P(t)\,Q_i(t)-1}{t^{\,i}}

we obtain the **doubling update**

.. math::
   :label: eq:doubling_update

   \begin{aligned}
   Q_{2i}(t)&=Q_i(t)-t^{\,i}\,E_i(t)\,Q_i(t) ,\\
   E_{2i}(t)&=-\bigl[E_i(t)\bigr]^{2} .
   \end{aligned}

Iterate until the degree exceeds :math:`2N`; multiply
:math:`Q_{2N}(t)` with the numerator polynomial to read off the
Markov parameters :math:`y_1,\,\dots,\,y_{2N}` .

Triangular calculation table
----------------------------

Construct the matrix (only labelled entries shown)

.. math::
   :label: eq:triangular_matrix

   \begin{pmatrix}
     A_{1,1} \\[2pt]
     A_{2,1} & A_{2,2} & \dots & A_{2,j} & \dots & \dots & A_{2,2N}\\
     A_{3,1} & A_{3,2} & \dots & A_{3,j} & \dots  & A_{3,2N-2} &\\
     A_{4,1} & A_{4,2} & \dots & \dots & A_{4,2N-4} & & \\[-2pt]
     \vdots  & \vdots  & \vdots &  &  &  & \\
     A_{N+1,1}&A_{N+1,2}& & & & & \\
   \end{pmatrix}

* initialise :math:`A_{1,1}=1` , :math:`A_{2,j}=y_j` ;
* fill rows :math:`j = 1\ldots 2N` with

  .. math::
     :label: eq:fill_rows

     A_{i,j}=A_{i-2,j+2}-H_{i-2}\,A_{i-1,j+2}-h_{i-2}\,A_{i-1,j+1} .

Row by row the first two entries give

.. math::
   :label: eq:hi_hi_coefs

   H_i=\frac{A_{i,1}}{A_{i+1,1}} ,\qquad
   h_i=\frac{A_{i,2}-H_i\,A_{i+1,2}}{A_{i+1,1}} ,
   \qquad i=1,\dots,N .

These :math:`H_i , h_i` coefficients complete the **H–h fraction**
(Equation :eq:`eq:simpler_form`) .  Convert to the J-fraction via Equation :eq:`eq:j_conversion` and finally
to the Cauer S-fraction with the recurrence :eq:`eq:recursive_update` described in
:ref:`J-fraction` .
