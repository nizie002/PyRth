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
        if chain[0][-1 - i] == 0:
            c0max -= 1
        else:
            break

    for i in range(c1max):
        if chain[1][-1 - i] == 0:
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


def build_mpfr_foster_impedance(therm_resist_fost, therm_capa_fost):
    """Lift Foster ladders into MPFR and return the rational impedance."""
    mpfr_resist_fost = [mpfr(num) for num in therm_resist_fost]
    mpfr_capa_fost = [mpfr(denom) for denom in therm_capa_fost]

    mpfr_z_num, mpfr_z_denom = make_z_s(mpfr_resist_fost, mpfr_capa_fost)

    return mpfr_resist_fost, mpfr_capa_fost, mpfr_z_num, mpfr_z_denom


def poly_long_division_to_cauer(mpfr_z_num, mpfr_z_denom):
    """Classical Euclidean Foster→Cauer conversion with MPFR arithmetic."""

    ar_len = len(mpfr_z_denom) - 1

    cau_res = np.zeros(ar_len)
    cau_cap = np.zeros(ar_len)

    num = list(mpfr_z_num)
    denom = list(mpfr_z_denom)

    for i in range(ar_len):
        num, denom, cap, res = precision_step(num, denom)
        cau_res[i] = float(res)
        cau_cap[i] = float(cap)

    return cau_res, cau_cap


def boor_golub_cauer(mpfr_resist_fost, mpfr_capa_fost):
    """Execute the Boor–Golub continued-fraction algorithm in MPFR space."""

    poles = []

    for R, C in zip(mpfr_resist_fost, mpfr_capa_fost):
        if R > 0 and C > 0:
            poles.append(mpfr("-1.0") / (R * C))

    M = len(poles) - 1
    w_0 = [0] * (M + 1)

    for i in range(M + 1):
        w_0[i] = mpfr("1.0") / mpfr_capa_fost[i]

    k = [mpfr("0.0")] * (2 * (M + 1))

    w_sum = mpfr("0.0")
    for w in w_0:
        w_sum = w_sum + w

    k[1] = mpfr("1.0") / w_sum

    lmda = [mpfr("0.0")] * (M + 1)
    mu = [mpfr("0.0")] * (M + 1)
    l_mu_sum = [mpfr("0.0")] * (M)
    l_mu_prod = [mpfr("0.0")] * (M)
    B = [0] * (M + 1)

    B[0] = [mpfr("1.0")]

    for i in range(M + 1):
        lmda[0] = lmda[0] - w_0[i] * poles[i]
    lmda[0] = lmda[0] / w_sum

    k[2] = mpfr("1.0") / (k[1] * lmda[0])
    B[1] = [lmda[0], mpfr("1.0")]

    l_mu_prod[0] = mpfr_weighted_self_product(poles, B[1], w_0) / mpfr_weighted_self_product(
        poles, B[0], w_0
    )

    mu[1] = l_mu_prod[0] / lmda[0]

    for i in range(2, M + 1):
        Bs = list(B[i - 1])
        Bs.insert(0, mpfr("0.0"))

        l_mu_sum[i - 1] = mpfr_weighted_inner_product(poles, B[i - 1], Bs, w_0) / mpfr_weighted_self_product(
            poles, B[i - 1], w_0
        )

        lmda[i - 1] = l_mu_sum[i - 1] - mu[i - 1]

        fst = mpfr_pol_mul(([l_mu_sum[i - 1], mpfr("1.0")]), B[i - 1])
        snd = mpfr_pol_mul(([-l_mu_prod[i - 2]]), B[i - 2])
        B[i] = mpfr_pol_add(fst, snd)

        l_mu_prod[i - 1] = mpfr_weighted_self_product(poles, B[i], w_0) / mpfr_weighted_self_product(
            poles, B[i - 1], w_0
        )
        mu[i] = l_mu_prod[i - 1] / lmda[i - 1]

    k[3] = (k[1] * lmda[0]) / mu[1]
    for i in range(2, M + 1):
        lambdas = k[1]
        mus = mu[1]
        for j in range(2, i):
            mus = mus * mu[j]
        for j in range(i):
            lambdas = lambdas * lmda[j]
        k[2 * i] = mus / lambdas
        k[2 * i + 1] = lambdas / (mus * mu[i])

    cau_res = np.zeros(M + 1)
    cau_cap = np.zeros(M + 1)

    for i in range(0, M):
        cau_res[i] = float(k[2 * i + 2])
        cau_cap[i] = float(k[2 * i + 1])
    cau_cap[M] = float(k[2 * M + 1])

    return cau_res, cau_cap


def normalize_rational_polynomials(mpfr_z_num, mpfr_z_denom):
    """Normalize numerator/denominator so the denominator's leading coefficient is one."""
    inv = mpfr("1.0") / mpfr_z_denom[-1]

    N = len(mpfr_z_denom)

    cleaned_mpfr_num = [
        mpfr("0.0"),
        *[inv * mpfr_z_num[N - i - 2] for i in range(N - 1)],
    ]
    cleaned_mpfr_denom = [inv * mpfr_z_denom[N - i - 1] for i in range(N)]

    return cleaned_mpfr_num, cleaned_mpfr_denom


def generate_markov_params(cleaned_mpfr_num, cleaned_mpfr_denom):
    """Produce the first ``2N`` Markov parameters via Newton doubling."""
    N = len(cleaned_mpfr_denom)
    order = int(np.ceil(np.log2(N)) + 1)

    L = 1

    last_term = [mpfr("1.0")]
    last_error = cleaned_mpfr_denom[1:]

    for _ in range(1, order + 1):
        pre_term = [mpfr("0.0")] * L
        pre_term = pre_term + last_term

        next_term = mpfr_pol_add(last_term, mpfr_neg_pol_mul(last_error, pre_term, maxorder=2 * N))
        next_error = mpfr_neg_pol_mul(last_error, last_error, maxorder=2 * N)

        last_term = next_term
        last_error = next_error

        L = L * 2

    markov_parameters = mpfr_pol_mul(cleaned_mpfr_num, next_term)[1 : 2 * N + 1]

    return markov_parameters


def khatwani_method(N, markov_parameters):
    """Build the triangular table that yields the H–h coefficients."""
    a_matrix = [[None] * (2 * N) for i in range(N + 1)]
    a_matrix[0] = [mpfr("0.0")] * (2 * N)
    a_matrix[0][0] = mpfr("1.0")

    large_h = [None] * (N - 1)
    small_h = [None] * (N - 1)

    for i in range(2 * N):
        a_matrix[1][i] = markov_parameters[i]

    large_h[0] = a_matrix[0][0] / a_matrix[1][0]
    small_h[0] = (a_matrix[0][1] - large_h[0] * a_matrix[1][1]) / a_matrix[1][0]

    for i in range(2, N):
        for j in range(2 * N - (i - 1) * 2):
            a_matrix[i][j] = (
                a_matrix[i - 2][j + 2]
                - large_h[i - 2] * a_matrix[i - 1][j + 2]
                - small_h[i - 2] * a_matrix[i - 1][j + 1]
            )

        large_h[i - 1] = a_matrix[i - 1][0] / a_matrix[i][0]
        small_h[i - 1] = (a_matrix[i - 1][1] - large_h[i - 1] * a_matrix[i][1]) / a_matrix[i][0]

    return large_h, small_h


def sobhy_method(N, cleaned_mpfr_num, cleaned_mpfr_denom):
    """Sobhy's interlaced A/B-table alternative to Khatwani."""
    A = [[mpfr("0.0")] * (N) for i in range(N + 1)]
    B = [[mpfr("0.0")] * (N) for i in range(N + 1)]

    for i in range(N):
        A[0][i] = cleaned_mpfr_denom[i]
        B[0][i] = cleaned_mpfr_denom[i]

    for i in range(N - 1):
        A[1][i] = cleaned_mpfr_num[i + 1]

    for k in range(N - 1):
        j = 1
        B[j][k] = A[j - 1][k + 1] - A[j - 1][0] / A[j][0] * A[j][k + 1]

    for j in range(2, N + 1):
        for k in range(N - j):
            A[j][k] = B[j - 1][k + 1] - B[j - 1][0] / A[j - 1][0] * A[j - 1][k + 1]
        for k in range(N - j):
            B[j][k] = A[j - 1][k + 1] - A[j - 1][0] / A[j][0] * A[j][k + 1]

    a = [None] * (N - 1)
    b = [None] * (N - 1)

    for m in range(1, N):
        a[m - 1] = A[m - 1][0] / A[m][0]
        b[m - 1] = B[m][0] / A[m][0]

    return a, b


def conti_frac_convers(N, large_h, small_h):
    """Map H–h coefficients to the Stieltjes (Cauer) continued fraction."""
    a_square = [None] * (N - 1)
    small_b = [None] * (N - 1)

    a_square[0] = mpfr("1.0") / large_h[0]
    small_b[0] = mpfr("-1.0") * small_h[0] / large_h[0]

    for i in range(1, N - 1):
        a_square[i] = mpfr("-1.0") / (large_h[i] * large_h[i - 1])
        small_b[i] = -small_h[i] / large_h[i]

    small_c = [None] * (2 * (N - 1))

    small_c[0] = mpfr("1.0") / a_square[0]
    small_c[1] = -a_square[0] / small_b[0]

    for i in range(1, N - 1):
        small_c[2 * i] = mpfr("1.0") / (
            small_c[2 * i - 2] * small_c[2 * i - 1] * small_c[2 * i - 1] * a_square[i]
        )
        small_c[2 * i + 1] = -small_c[2 * i - 1] / (
            mpfr("1.0") + small_c[2 * i] * small_c[2 * i - 1] * small_b[i]
        )

    cau_res = np.zeros(N - 1)
    cau_cap = np.zeros(N - 1)

    for i in range(0, N - 1):
        cau_cap[i] = float(small_c[2 * i])
        cau_res[i] = float(small_c[2 * i + 1])

    return cau_res, cau_cap
