import gmpy2 as gp
from gmpy2 import mpfr
import numpy as np


def make_z_s(r_fos, c_fos):

    # calculates the rational function for the foster-cauer transformation

    denom_list = []
    num_list = []

    for i in range(len(r_fos)):
        sum_num = [r_fos[i]]
        sum_denom = [mpfr("1.0"), gp.mul(r_fos[i], c_fos[i])]
        denom_list.append(sum_denom)
        num_list.append(sum_num)

    chain = [[mpfr("0.0")], [mpfr("1.0")]]

    for i in range(len(denom_list)):
        chain = add_rationals(chain, num_list[i], denom_list[i])

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

    # helper function for make_z_s()

    temp_num_1 = mpfr_pol_mul(chain[0], denom)
    temp_num_2 = mpfr_pol_mul(numn, chain[1])
    temp_denom = mpfr_pol_mul(denom, chain[1])
    temp_num = mpfr_pol_add(temp_num_1, temp_num_2)
    temp_num = np.append(temp_num, mpfr("0.0"))

    return [temp_num, temp_denom]


def mpfr_pol_mul(mul_1, mul_2):

    ord_1 = len(mul_1) - 1
    ord_2 = len(mul_2) - 1

    prod = [mpfr("0.0")] * (ord_1 + ord_2 + 1)

    for m1 in range(ord_1 + 1):
        for m2 in range(ord_2 + 1):
            prod[m1 + m2] = prod[m1 + m2] + mul_1[m1] * mul_2[m2]

    return prod


def mpfr_neg_pol_mul(mul_1, mul_2, maxorder=None):

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
    prod = mpfr("0.0")
    N = len(poles)

    for i in range(N):
        p1val = mpfr_horner_poly_eval(poles[i], p1)
        p2val = mpfr_horner_poly_eval(poles[i], p2)
        prod = prod - p1val * p2val * weights[i]

    return prod


def mpfr_weighted_self_product(poles, p1, weights):

    prod = mpfr("0.0")
    N = len(poles)

    for i in range(N):
        p1val = mpfr_horner_poly_eval(poles[i], p1)
        prod = prod + p1val * p1val * weights[i]

    return prod


def mpfr_horner_poly_eval(val, poly):

    # print("evaluating point", val)

    N = len(poly)

    res = mpfr("0.0")

    for i in range(N - 1):
        res = (res + poly[N - i - 1]) * val

    return res + poly[0]


def mpfr_bisection(poly, lowr_brak, upr_brak):

    # print('looking between', lowr_brak, upr_brak)

    n = 1

    lowr_brak_val = mpfr_horner_poly_eval(lowr_brak, poly)
    # upr_brak_val = mpfr_horner_poly_eval(upr_brak, poly)
    if gp.sign(lowr_brak_val) > 0:
        pos = lowr_brak
        neg = upr_brak
    else:
        neg = lowr_brak
        pos = upr_brak
    npsum = neg + pos
    new_x = (npsum) / mpfr("2.0")

    # print('new x', new_x)

    acr = gp.sign(npsum) * npsum * mpfr("1e-80")
    new_val = mpfr("1.0")

    while ((gp.sign(new_val) * new_val) > acr) and (n < 50000):

        # print((gp.sign(diff) * diff), acr)

        n += 1
        new_x = (neg + pos) / mpfr("2.0")

        new_val = mpfr_horner_poly_eval(new_x, poly)

        if gp.sign(new_val) > 0:
            pos = new_x
        if gp.sign(new_val) < 0:
            neg = new_x

        # print((gp.sign(new_val) * new_val), acr)

    # print("bisection result", n, new_val)

    return (neg + pos) / mpfr("2.0")


def division_step(numerator, denominator):

    # helper function for foster_to_cauer()

    len_n = len(numerator)
    len_d = len(denominator)

    if len_n + 1 == len_d:

        # num and denom are exchanged because we are interested dividing 1/Z, but num and denom are named in reference to Z
        quotient, remainder = np.polynomial.polynomial.polydiv(denominator, numerator)
        if len(quotient) == 2:
            cap = quotient[1]
            res_inv = quotient[0]
        else:
            print("quotient, remainder")
            print(quotient, remainder)
            raise ValueError("Quotient does not have length 2")

        res = 1.0 / res_inv
        num_new = -res * remainder
        denom_new = np.polynomial.polynomial.polyadd(res_inv * numerator, remainder)

    else:
        print(numerator)
        print(denominator)
        raise ValueError(
            "Rational function has no proper Form -- num: "
            + str(len_n)
            + " denom: "
            + str(len_d)
        )

    return num_new, denom_new, cap, res


def precision_step(numerator, denominator):

    # helper function for foster_to_cauer()

    quotient, remainder = precision_polydiv(denominator, numerator)
    res_inv = quotient[0]
    cap = quotient[1]

    res = gp.div(mpfr("1.0"), res_inv)

    num_new = [gp.mul(-res, remainder[i]) for i in range(len(numerator))]
    denom_new = [
        gp.add(res_inv * numerator[i], remainder[i]) for i in range(len(numerator))
    ]

    return num_new, denom_new, cap, res


def precision_polydiv(numerator, denominator):

    nl = len(numerator) - 1
    dl = len(denominator) - 1

    while dl >= 0 and denominator[dl] == 0.0:
        dl = dl - 1
    if dl < 0:
        raise ValueError("polydiv divide by zero polynomial")

    remainder = numerator
    quotient = [mpfr("0.0") for i in range(len(numerator))]

    for k in range(nl - dl, -1, -1):
        quotient[k] = gp.div(remainder[dl + k], denominator[dl])
        # if k == 1:
        # print(quotient[k],'\n', remainder[dl+k],'\n', denominator[dl],'\n\n')
        for j in range(dl + k - 1, k - 1, -1):
            remainder[j] = gp.add(
                remainder[j], -gp.mul(quotient[k], denominator[j - k])
            )

    for l in range(dl, nl + 1, 1):
        remainder[l] = mpfr("0.0")

    return (quotient, remainder)
