.. _J-fraction:

J-fraction Route to the Cauer Ladder
=======================================

Polynomial long-division and Lanczos both produce the Cauer (Stieltjes)
continued fraction **directly**.  
A third family of algorithms—due to **Khatwani** and **Sobhy**—first casts
the impedance into a **J-fraction** and converts that to the desired
S-fraction.  This detour avoids explicit high-order divisions and relies
only on scalar recurrences.

Starting point: rational impedance
--------------------------------------
After deconvolution the driving-point impedance is known in rational form

.. math::
   :label: eq:rational_impedance

   Z(s)=
   \frac{\alpha_0+\alpha_1s+\dots+\alpha_{N-1}s^{N-1}}
        {\beta_0+\beta_1s+\dots+\beta_{N-1}s^{N-1}+\beta_Ns^{N}} .

The goal is to rewrite :eq:`eq:rational_impedance` as the Cauer (S-) fraction of length *2 N*
whose coefficients are the **thermal resistances** and
**thermal capacitances**.

J-fraction representation
-----------------------------
Both Khatwani's and Sobhy's schemes build the continued fraction

.. math::
   :label: eq:j_fraction

   Z(s)=
   \cfrac{a_1^{2}}{s-b_1-\cfrac{a_2^{2}}{s-b_2-\ddots-
   \cfrac{a_N^{2}}{s-b_N}}}\!,

known as a **J-fraction**.  
The *auxiliary* parameters :math:`a_i^2` and :math:`b_i` are obtained by
recursively expanding the simpler form

.. math::
   :label: eq:simpler_form

   Z(s)=
   \cfrac{1}{
     H_1 s+h_1+
     \cfrac{1}{
       H_2 s+h_2+\ddots+
       \cfrac{1}{H_N s+h_N}}}

with :math:`H_i , h_i` computed either from the **Markov parameters**
(Khatwani) or by Sobhy's direct iteration. This is referred to as the :math:`H`–:math:`h` continued fraction.

For :math:`i > 1` the conversion is

.. math::
   :label: eq:j_conversion

   \begin{aligned}
   a_1^{2}&=\frac{1}{H_1},
   &\;
   a_i^{2}&=-\frac{1}{H_i H_{i-1}},\\
   b_1&=-\frac{h_1}{H_1},
   &\;
   b_i&=-\frac{h_i}{H_i}.
   \end{aligned}

From J– to S-fraction
----------------------------
The J-fraction :eq:`eq:j_fraction` must be rearranged into the *Stieltjes* or
**S-fraction**

.. math::
   :label: eq:s_fraction

   Z(s)=\cfrac{1}{
          c_1 s+\cfrac{1}{
          c_2+\cfrac{1}{
          c_3 s+\ddots+\cfrac{1}{c_{2N}}}}}\!,

whose :math:`c_k` are **exactly** the Cauer  
:math:`R'_k,\,C'_k` in alternating order
(:math:`c_{2k-1}=C'_k`, :math:`c_{2k}=R'_k`).

Initial step

.. math::
   :label: eq:initial_step

   c_1=\frac{1}{a_1^{2}},\qquad
   c_2=-\frac{a_1^{2}}{b_1}.

Recursive update for :math:`i>0`

.. math::
   :label: eq:recursive_update

   \begin{aligned}
   c_{2i+1}&=
     \frac{1}{c_{2i-1}c_{2i}^{\,2}a_{i+1}^{2}},\\[4pt]
   c_{2i+2}&=
     -\frac{c_{2i}}{1+c_{2i+1}c_{2i}b_{i+1}} .
   \end{aligned}

Iterate until :math:`i=N-1` to obtain all :math:`2N` coefficients.

Algorithm outline
-------------------------

.. admonition:: J-fraction Algorithm for Foster-to-Cauer Conversion

    **Input:** :math:`\{\alpha_k\}`, :math:`\{\beta_k\}` (numerator / denominator of :math:`Z(s)`)

    **Output:** :math:`\{R'_k, C'_k\}` for :math:`k = 1 \ldots N` (Cauer ladder)

    #. Compute :math:`\{H_k, h_k\}`  (using Khatwani or Sobhy formulae)
    #. Convert :math:`(H, h) \rightarrow (a^2, b)` using :eq:`eq:j_conversion`
    #. Initialize :math:`c_1, c_2` using :eq:`eq:initial_step`
    #. **for** :math:`i = 1 \ldots N-1` **do**
        #. Compute :math:`c_{2i+1}, c_{2i+2}` using :eq:`eq:recursive_update`
    #. **end for**
    #. Map :math:`c_1, c_2, c_3, \ldots` to :math:`C'_1, R'_1, C'_2, R'_2, \ldots`
