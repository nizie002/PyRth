.. _polynomial_long_division:

Polynomial Long-Division
=========================================
The Foster ladder obtained from the time-constant spectrum is compact and
convenient for simulation, yet every branch lacks a *direct* physical
meaning.  To retrieve layer-by-layer thermal parameters we convert the
network into the **Cauer ladder** – a series chain in which each
:math:`R'_k,\,C'_k` pair maps to a consecutive portion of the heat path.

The conversion is an exercise in **network synthesis**: rewrite the Foster
impedance

.. math::
   :label: eq:foster_impedance

   Z(s)=\sum_{i=1}^{n}\frac{R_i}{1+sR_iC_i}

as the Stieltjes continued fraction

.. math::
   :label: eq:stieltjes_fraction

   Z(s)=
   \cfrac{1}{
     sC'_1+
     \cfrac{1}{
       R'_1+
       \cfrac{1}{
         sC'_2+
         \cfrac{1}{
           R'_2+\ddots+
           \cfrac{1}{sC'_n+\cfrac{1}{R'_n}}
         }
       }
     }
   }.


**Polynomial Long-Division algorithm**

The standard procedure extracts the Cauer elements **one at a time** via
repeated polynomial division (Euclid algorithm).

**Notation**

* Foster elements :math:`R_i,\,C_i`
* Cauer elements :math:`R'_k,\,C'_k`
* :math:`Z_k(s)` – remaining impedance after the first *k−1* Cauer pairs
  have been stripped (start with :math:`Z_n(s)=Z(s)`).

**Recursive step**

For each iteration :math:`k = n, n-1, \ldots, 1`:

#. **Split** :math:`Z_k(s)=p_k(s)/q_k(s)` with
   deg :math:`q_k` = deg :math:`p_k` + 1.
#. **Divide**

   .. math::
      :label: eq:division_step

      \frac{q_k(s)}{p_k(s)}
      \;=\;
      sC'_k\;+\;\frac{1}{R'_k}\;+\;\frac{r_k(s)}{p_k(s)}.

   The quotient coefficients give immediately  

   .. math::
      :label: eq:cauer_elements

      C'_k=\text{(coefficient of }s),
      \qquad
      R'_k=\bigl[\text{constant term}\bigr]^{-1}.

#. **Form new impedance**

   .. math::
      :nowrap:
      :label: eq:new_impedance

      \begin{aligned}
      p_{k-1}(s)&=-\,R'_k\,r_k(s),\\
      q_{k-1}(s)&=\dfrac{p_k(s)}{R'_k}+r_k(s),\\
      Z_{k-1}(s)&=\dfrac{p_{k-1}(s)}{q_{k-1}(s)}.
      \end{aligned}

#. **Stop** when :math:`p_0(s)=0`; all Cauer elements have been found.

**Why the division always works**

Because each branch in the Foster sum :eq:`eq:foster_impedance` adds one real **pole** but no new
zeros, deg :math:`q_k` is *exactly* one higher than deg :math:`p_k`
(see the pole–zero discussion in the previous section).  
Hence the quotient of polynomials always reduces to a *linear* term plus a
remainder, making the extraction of a single RC pair straightforward.

**Numerical considerations**

* **Coefficient growth** – Polynomial coefficients explode rapidly
  (typically beyond 50–100 terms).  Use arbitrary-precision arithmetic once
  double-precision runs out of mantissa bits.
* **Conditioning** – Rescale :math:`s` (e.g. by the dominant time-constant)
  before the first division to keep coefficients near unity.

**When to stop early?**

If only the front section of the structure function is required, terminate
the division once the cumulative resistance exceeds the target layer.  The
remaining high-order Foster branches can stay in parallel; accuracy at long
times is preserved while numerical effort is reduced.

**Summary**

The Foster-to-Cauer transformation is nothing more than **repeated Euclidean
division** of two polynomials whose degrees differ by one.  
Each quotient yields one thermal resistance and one thermal capacitance;
the remainder becomes the dividend of the next step.  Starting from the
positive-real Foster impedance guarantees convergence and keeps every
intermediate network physically meaningful.
