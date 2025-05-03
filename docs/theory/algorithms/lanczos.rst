.. _nid_lanczos:

Lanczos Method
===============================

The Foster-to-Cauer Methods of the previous chapters yields exact Cauer
coefficients but can be slow and prone to round-off once the ladder grows
long.  The **Lanczos iteration** offers a fast, numerically stable
alternative that needs only vector operations and produces the Cauer
elements *on the fly*.

The Foster ladder that comes straight from the time-constant spectrum is a
**parallel** network whose branch voltages obey a *first-order differential
equation*. The **Lanczos iteration** turns that differential-equation view into a
numerically efficient recipe for building the equivalent **series** Cauer
ladder, one resistor–capacitor pair at a time.


.. figure:: /_static/foster_network.png
   :alt: Foster network
   :width: 600px
   :align: center

   Foster network with series RC branches.

Foster Network as Differential-Equation
-------------------------------------------------

For a Foster network with branch capacitances :math:`C_i` and resistances
:math:`R_i` the node voltages collected in
:math:`\mathbf u(t)=[u_1,\dots,u_N]^{\!\top}` satisfy

.. math::

   \mathbf C\,\dot{\mathbf u}(t)+\mathbf K\,\mathbf u(t)=\mathbf g\,I(t),

where :math:`I(t)` is the input current and 

.. math::
    
   \begin{aligned}
   \mathbf C&=\operatorname{diag}(C_i)\\[1ex]
   \mathbf K&=\operatorname{diag}\!\bigl(1/R_i\bigr)\\[1ex]
   \mathbf g&=\mathbf 1
    \end{aligned}\quad .

This is the *thermal analogue* of the semi-discrete heat equation
(without sources).  
After Laplace transformation we recover the driving-point impedance

.. math::

   Z(s)=\mathbf g^{\!\top}\bigl(s\mathbf C+\mathbf K\bigr)^{-1}\mathbf g,

exactly the quantity that network identification by deconvolution supplies.
Lanczos operates **directly** on the matrix pencil
:math:`(s\mathbf C+\mathbf K)` to recast it into the tridiagonal
continued-fraction form of a Cauer ladder, compare the equations in the section on :ref:`polynomial_long_division`.


Lanczos in a Nutshell
-------------------------
* Project the diagonal pair :math:`(\mathbf C,\mathbf K)` onto a Krylov
  sub-space that is orthogonal with respect to the
  :math:`\mathbf C`-weighted inner product.
* The projection produces a *tridiagonal* matrix :math:`\mathbf T`
  whose entries are the Cauer resistances and capacitances.
* One Lanczos iteration = one extra rung in the ladder.


During the iteration two scalars are produced at every step:

.. math::

   \begin{aligned}
   \alpha_k &= -\,\mathbf u_k^{\!\top}\mathbf K\,\mathbf u_k \\[1ex]
   \beta_k  &= \|\mathbf r_k\|_{\mathbf C} \\[1ex]
            &= \sqrt{\mathbf r_k^{\!\top}\mathbf C\,\mathbf r_k}
   \end{aligned}

where

* :math:`\mathbf u_k` – the *k*-th Lanczos vector (C-orthonormal),
* :math:`\mathbf r_k` – the residual used to build the next vector.

Algorithm
----------------------

.. admonition:: Lanczos Iteration for Foster-to-Cauer Conversion

    **Input:** :math:`\mathbf{C} = \text{diag}(C_1\ldots C_N)`, :math:`\mathbf{K} = \text{diag}(1/R_1\ldots 1/R_N)`

    **Output:** :math:`\{R'_k, C'_k\}` for :math:`k = 1 \ldots \nu` (Cauer ladder)

    #. Solve :math:`\mathbf{C}\,\mathbf{r} = \mathbf{1}_N`  (initial residual :math:`\mathbf{r}_0`)
    #. :math:`\beta_0 = \sqrt{\mathbf{r}^\top \mathbf{C}\,\mathbf{r}}`
    #. :math:`\mathbf{v} = \mathbf{0}`  ("previous" Lanczos vector)
    #. :math:`k = 0`
    #. **while** :math:`\beta_k \neq 0` **do**

        #. :math:`\mathbf{u} = \mathbf{r}/\beta_k`  (new Lanczos vector :math:`\mathbf{u}_k`)
        #. :math:`k = k + 1`
        #. :math:`\alpha_k = -\,\mathbf{u}^\top \mathbf{K}\,\mathbf{u}`
        #. Solve :math:`\mathbf{C}\,\mathbf{r} = -(\mathbf{K} + \alpha_k\mathbf{C})\,\mathbf{u} - \beta_{k-1}\,\mathbf{C}\,\mathbf{v}`
        #. :math:`\beta_k = \sqrt{\mathbf{r}^\top \mathbf{C}\,\mathbf{r}}`
        #. :math:`\mathbf{v} = \mathbf{u}`

    #. **end while**

Mapping to Cauer Elements
-----------------------------
Let :math:`r_k = 1/R'_k` and :math:`c_k = C'_k`.

First pair

.. math::

   C'_1 = \frac{1}{\beta_0^{2}},\qquad
   R'_1 = -\frac{1}{\alpha_1\,C'_1}.

Subsequent pairs  (:math:`k \ge 2`)

.. math::

   C'_k = \frac{1}{\beta_{k-1}^{2}\,r_{k-1}^{2}\,c_{k-1}},\qquad
   R'_k = -\frac{1}{\alpha_k c_k + 1/r_{k-1}}.

Each step adds one section to the series ladder; stop when the desired
cumulative resistance is reached or when :math:`\beta_k` underflows.

**Why Use Lanczos?**

The Lanczos method offers significant advantages: it's computationally
efficient with complexity linear in the number of Foster branches, avoiding
large matrix multiplications and high-order polynomial divisions; it provides
excellent numerical stability in ordinary double precision for hundreds of
ladder sections as coefficients remain :math:`\mathcal{O}(1)`; and it delivers
progressive output where the first few Cauer elements appear after only a
handful of iterations, making it particularly suitable for on-line identification.

**Practical Tips**

For optimal performance when implementing the Lanczos method, consider
rescaling :math:`s` by the geometric mean of all time-constants to keep
:math:`\alpha_k` near –1 … 0, and you can safely terminate the algorithm
when :math:`\beta_k/\beta_0 < 10^{-12}` as the remaining ladder will have
negligible influence on the impedance.
