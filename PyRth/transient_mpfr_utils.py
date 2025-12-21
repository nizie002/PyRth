"""MPFR-backed helpers for Foster→Cauer polynomial algebra.

This module wraps the GNU MPFR primitives exposed by gmpy2 so PyRth can run
all Foster/Cauer conversions at arbitrary precision.  MPFR in gmpy2 is a
multiple-precision floating-point type backed by the GNU MPFR (Multiple
Precision Floating-Point Reliable) library.  In other words: it is like
Python's ``float``—but with arbitrary precision and well-defined rounding, so
you can do numerics with far more than 53 bits of mantissa and with controlled
behavior.
"""

from typing import Any, cast

import gmpy2 as gp
from gmpy2 import mpfr # pylint: disable=no-name-in-module
import numpy as np

gp = cast(Any, gp)


def make_z_s(r_fos, c_fos):
    """Assemble the Foster ladder into a rational Z(s) with MPFR precision.

    Takes matching resistance/capacitance arrays from the Foster spectrum and
    returns the numerator/denominator polynomials of the driving-point
    impedance.  This is the common entry point for all MPFR-based
    Foster→Cauer conversions.
    """

    denom_list = []
    num_list = []

    for r_val, c_val in zip(r_fos, c_fos):
        sum_num = [r_val]
        sum_denom = [mpfr("1.0"), r_val * c_val]
        denom_list.append(sum_denom)
        num_list.append(sum_num)

    chain = [[mpfr("0.0")], [mpfr("1.0")]]

    for num, denom in zip(num_list, denom_list):
        chain = add_rationals(chain, num, denom)

    c0max = len(chain[0])
    c1max = len(chain[1])
    for i in range(c0max):
        if gp.is_zero(chain[0][-1 - i]):
            c0max -= 1
        else:
            break

    for i in range(c1max):
        if gp.is_zero(chain[1][-1 - i]):
            c1max -= 1
        else:
            break

    return chain[0][:c0max], chain[1][:c1max]


def add_rationals(chain, numn, denom):
    """Combine two rational functions expressed as (num, denom) pairs."""

    temp_num_1 = mpfr_pol_mul(chain[0], denom)
    temp_num_2 = mpfr_pol_mul(numn, chain[1])
    temp_denom = mpfr_pol_mul(denom, chain[1])
    temp_num = mpfr_pol_add(temp_num_1, temp_num_2)
    temp_num = np.append(temp_num, mpfr("0.0"))

    return [temp_num, temp_denom]


def mpfr_pol_mul(mul_1, mul_2):
    """Multiply two MPFR polynomials (dense coefficient arrays)."""

    ord_1 = len(mul_1) - 1
    ord_2 = len(mul_2) - 1

    prod = [mpfr("0.0")] * (ord_1 + ord_2 + 1)

    for m1 in range(ord_1 + 1):
        for m2 in range(ord_2 + 1):
            prod[m1 + m2] = prod[m1 + m2] + mul_1[m1] * mul_2[m2]

    return prod


def mpfr_neg_pol_mul(mul_1, mul_2, maxorder=None):
    """Multiply two polynomials but accumulate the negative product.

    ``maxorder`` caps the resulting polynomial degree so Newton-doubling steps
    in the J-fraction helpers can truncate intermediate results safely.
    """

    ord_1 = len(mul_1) - 1
    ord_2 = len(mul_2) - 1

    if maxorder is None:
        total_order = ord_1 + ord_2 + 1
    else:
        total_order = (
            (ord_1 + ord_2 + 1) if (ord_1 + ord_2 + 1) < maxorder else maxorder
        )

    prod = [mpfr("0.0")] * (total_order)

    for m1 in range(ord_1 + 1):
        for m2 in range(ord_2 + 1):
            if m1 + m2 < total_order:
                prod[m1 + m2] = prod[m1 + m2] - mul_1[m1] * mul_2[m2]

    return prod


def mpfr_pol_add(add_1, add_2):
    """Add two polynomials, padding the shorter list in-place."""

    ord_1 = len(add_1) - 1
    ord_2 = len(add_2) - 1

    if ord_1 > ord_2:
        order = ord_1
        add_2 += [mpfr("0.0")] * (ord_1 - ord_2)
    else:
        order = ord_2
        add_1 += [mpfr("0.0")] * (ord_2 - ord_1)

    summ = [mpfr("0.0")] * (order + 1)

    for m in range(order + 1):
        summ[m] = summ[m] + add_1[m] + add_2[m]

    return summ


def mpfr_weighted_inner_product(poles, p1, p2, weights):
    """Weighted inner product used by the Boor–Golub algorithm."""
    prod = mpfr("0.0")
    n = len(poles)

    for i in range(n):
        p1val = mpfr_horner_poly_eval(poles[i], p1)
        p2val = mpfr_horner_poly_eval(poles[i], p2)
        prod = prod - p1val * p2val * weights[i]

    return prod


def mpfr_weighted_self_product(poles, p1, weights):
    """Weighted self product counterpart to ``mpfr_weighted_inner_product``."""

    prod = mpfr("0.0")
    n = len(poles)

    for i in range(n):
        p1val = mpfr_horner_poly_eval(poles[i], p1)
        prod = prod + p1val * p1val * weights[i]

    return prod


def mpfr_horner_poly_eval(val, poly):
    """Evaluate a polynomial with Horner's rule using MPFR arithmetic."""

    n = len(poly)

    res = mpfr("0.0")

    for i in range(n - 1):
        res = (res + poly[n - i - 1]) * val

    return res + poly[0]


def precision_step(numerator, denominator):
    """Single Euclidean division step for Foster→Cauer conversion.

    Parameters are deliberately passed as ``(numerator, denominator)`` but fed
    into ``precision_polydiv`` as ``(denominator, numerator)`` because the
    current MPFR implementation expects the higher-degree polynomial first.
    This ordering triggers pylint's "positional arguments appear to be out
    of order" warning; the swap is intentional and mirrors the classic Cauer
    derivation where we repeatedly divide the denominator by the numerator.
    """

    quotient, remainder = precision_polydiv(denominator, numerator)  # pylint: disable=arguments-out-of-order
    res_inv = quotient[0]
    cap = quotient[1]

    res = mpfr("1.0") / res_inv

    num_new = [-res * remainder[i] for i in range(len(numerator))]
    denom_new = [res_inv * numerator[i] + remainder[i] for i in range(len(numerator))]

    return num_new, denom_new, cap, res


def precision_polydiv(numerator, denominator):
    """Long-division helper that works on MPFR coefficient arrays."""

    nl = len(numerator) - 1
    dl = len(denominator) - 1

    while dl >= 0 and denominator[dl] == 0.0:
        dl = dl - 1
    if dl < 0:
        raise ValueError("polydiv divide by zero polynomial")

    remainder = numerator
    quotient = [mpfr("0.0") for i in range(len(numerator))]

    for k in range(nl - dl, -1, -1):
        quotient[k] = remainder[dl + k] / denominator[dl]
        for j in range(dl + k - 1, k - 1, -1):
            remainder[j] = remainder[j] - quotient[k] * denominator[j - k]

    for l in range(dl, nl + 1, 1):
        remainder[l] = mpfr("0.0")

    return (quotient, remainder)
