import numpy as np
from numba import njit


@njit(cache=True)
def polyfit(X, y, weights):
    # Calculate weighted means
    weighted_mean_x = sum([w * x for w, x in zip(weights, X)]) / sum(weights)
    weighted_mean_y = sum([w * y_i for w, y_i in zip(weights, y)]) / sum(weights)

    # Calculate weighted sums for the slope calculation
    numerator = sum(
        [
            w * (x - weighted_mean_x) * (y_i - weighted_mean_y)
            for w, x, y_i in zip(weights, X, y)
        ]
    )
    denominator = sum([w * (x - weighted_mean_x) ** 2 for w, x in zip(weights, X)])

    if denominator == 0:
        raise ValueError("Denominator in slope calculation is zero")

    slope = numerator / denominator
    intercept = weighted_mean_y - slope * weighted_mean_x

    return (slope, intercept)


@njit(cache=True)
def derivative(
    impedance,
    log_time,
    log_time_size,
    window_increment,
    minimum_window_length,
    maximum_window_length,
    minimum_window_size,
    min_index,
    expected_var,
    pad_factor_pre,
    pad_factor_after,
    dummy=False,
):

    if dummy:
        return

    best_window_length = None
    minimum_window_length = minimum_window_length
    maximum_window_length = maximum_window_length
    minimum_window_size = minimum_window_size

    window_increment = window_increment
    full_window = [-window_increment, 0.0, window_increment]
    lower_window = [0.0, window_increment]
    upper_window = [-window_increment, 0.0]

    log_time_interp = np.linspace(
        log_time[0],
        log_time[-1],
        log_time_size + 1,
    )[:-1]

    fft_delta = (log_time[-1] - log_time[0]) / log_time_size

    lent = len(log_time)
    leni = len(log_time_interp)
    pad_number_pre = int(log_time_size * pad_factor_pre)
    pad_number_after = int(log_time_size * pad_factor_after)
    leng = leni + pad_number_pre + pad_number_after

    global_weight = np.append(
        (log_time[1:] - log_time[:-1]),
        (log_time[-1] - log_time[-2]),
    )

    imp_smooth = np.zeros(leni)
    imp_deriv_interp = np.zeros(leng)

    n = 0
    n_data = pad_number_pre

    for t_val in log_time_interp:

        best_poly_val = 1e200
        best_diff_val = 1e200
        best_estimator = 1e200
        last_window_length = best_window_length

        if last_window_length is not None:
            if minimum_window_length < last_window_length < maximum_window_length:
                bw_steps = full_window
            elif last_window_length >= maximum_window_length:
                bw_steps = upper_window
            elif last_window_length <= minimum_window_length:
                bw_steps = lower_window
        else:
            bw_steps = [
                minimum_window_length + i * window_increment
                for i in range(
                    int(
                        (maximum_window_length - minimum_window_length)
                        / window_increment
                    )
                    + 1
                )
            ]
            last_window_length = 0.0

        for bw in bw_steps:
            window_length = last_window_length + bw
            window_length = max(
                min(window_length, maximum_window_length), minimum_window_length
            )

            index = max(np.searchsorted(log_time, t_val), min_index)
            center_time = log_time[index]

            up_bound = np.searchsorted(log_time, t_val + window_length) + 1
            low_bound = np.searchsorted(log_time, t_val - window_length)

            while up_bound - low_bound < minimum_window_size:
                up_bound += 1
                low_bound -= 1

            while low_bound < 0:
                up_bound += 1
                low_bound += 1

            while up_bound > lent:
                up_bound -= 1
                low_bound -= 1

            t_frame = log_time[low_bound:up_bound]
            z_frame = impedance[low_bound:up_bound]

            center_index = np.searchsorted(t_frame, center_time)

            max_dist_cd1 = center_time - t_frame[0]
            max_dist_cd2 = t_frame[-1] - center_time
            max_dist = max_dist_cd1 if max_dist_cd1 > max_dist_cd2 else max_dist_cd2
            frame_weight = (1 - np.abs((t_frame - center_time) / max_dist) ** 3) ** 3

            spacing_weight = global_weight[low_bound:up_bound]
            weight = frame_weight * spacing_weight

            coefs = polyfit(t_frame, z_frame, weight)
            # poly_value = polyval(t_val, coefs)
            poly_value = coefs[0] * t_val + coefs[1]

            var = expected_var**2
            dif_spread = 0.1

            z_frame_copy = z_frame.copy()
            z_frame_copy[center_index] = impedance[index] - dif_spread * poly_value
            coefs_lower = polyfit(t_frame, z_frame_copy, weight)
            # polval_lower = polyval(t_val, coefs_lower)
            polval_lower = coefs_lower[0] * t_val + coefs_lower[1]

            z_frame_copy[center_index] = impedance[index] + dif_spread * poly_value
            coefs_upper = polyfit(t_frame, z_frame_copy, weight)
            # polval_upper = polyval(t_val, coefs_upper)
            polval_upper = coefs_upper[0] * t_val + coefs_upper[1]

            diff_term = abs(
                (polval_upper - polval_lower) / (2 * dif_spread * poly_value)
            )

            estimator = (
                poly_value**2
                - 2.0 * z_frame[center_index] * poly_value
                + 2.0 * var * diff_term
            )

            if estimator < best_estimator:
                best_estimator = estimator
                best_poly_val = poly_value
                best_diff_val = coefs[0]
                best_window_length = window_length

        imp_smooth[n] = best_poly_val
        imp_deriv_interp[n_data] = best_diff_val if best_diff_val > 0 else 0.0

        n += 1
        n_data += 1

    time_start = log_time_interp[0] - (pad_number_pre) * fft_delta
    time_stop = log_time_interp[-1] + (pad_number_after) * fft_delta

    prologue = np.linspace(
        time_start,
        log_time_interp[0],
        pad_number_pre + 1,
    )[:-1]

    epilogue = np.linspace(
        log_time_interp[-1] + fft_delta,
        time_stop,
        pad_number_after,
    )

    log_time_pad = np.concatenate((prologue, log_time_interp, epilogue))

    imp_smooth_full = np.interp(log_time, log_time_interp, imp_smooth)

    return (
        imp_smooth,
        imp_deriv_interp,
        log_time_interp,
        imp_smooth_full,
        log_time_pad,
        fft_delta,
    )


@njit(cache=True)
def bayesian_deconvolution(
    re_mat=np.array([[]]), imp_deriv_interp=np.array([]), N=float(1.0)
):

    true = imp_deriv_interp.copy().reshape(-1, 1)

    for step in range(N):

        denom = np.dot(re_mat, true).reshape(-1)

        denom[denom == 0.0] = np.inf

        q_vec = np.divide(imp_deriv_interp, denom).reshape(1, -1)

        k_sum = np.dot(q_vec, re_mat).reshape(-1, 1)

        true = np.multiply(k_sum, true)

    return true.flatten()


@njit(cache=True)
def response_matrix(domain=np.array([]), x_len=float(1.0)):

    response = np.zeros((x_len, x_len))

    norm = np.sum(np.exp(domain - np.exp(domain)))

    for it_line in range(x_len):
        for it_row in range(x_len):
            response[it_line, it_row] = domain[it_line] - domain[it_row]
    response = np.exp(response - np.exp(response))

    response /= norm

    return response


@njit(cache=True)
def lanczos_inner(cap_fost=np.array([]), res_fost=np.array([])):

    C_diag = cap_fost
    K_diag = 1.0 / res_fost

    # Initialize g as a vector of ones
    g = np.ones_like(C_diag)
    # Solve Cr = g for r
    r = g / C_diag

    # Initialize variables
    beta = np.sqrt(np.dot(r.T, g))
    v = np.zeros_like(r)

    # Initialize lists for res and cap
    res = []
    cap = []

    # Compute u, alpha, r, and beta for the first iteration
    u = r / beta
    alpha = -np.dot(u.T, K_diag * u)
    r = (-(K_diag + alpha * C_diag) * u - beta * C_diag * v) / C_diag
    beta_next = np.sqrt(np.dot(r.T, C_diag * r))
    v = u

    # Compute cap1 and res1
    cap.append(1 / (beta**2))
    res.append(-1 / (alpha * cap[0]))

    # Store previous values
    beta_prev = beta
    cap_prev = cap[0]
    res_prev = res[0]

    # Initialize res_sum and cap_sum
    res_sum = 0.0
    cap_sum = 0.0

    # Continue the loop until the divergence is reached
    while cap_sum < 1e4:
        u = r / beta_next
        alpha = -np.dot(u.T, K_diag * u)
        r = (-(K_diag + alpha * C_diag) * u - beta_next * C_diag * v) / C_diag
        beta_prev = beta_next
        beta_next = np.sqrt(np.dot(r.T, C_diag * r))

        v = u

        # Compute capi and resi
        cap_next = 1.0 / (beta_prev**2.0 * res_prev**2.0 * cap_prev)
        res_next = -1.0 / (alpha * cap_next + 1.0 / res_prev)

        if res_next <= 0.0 or cap_next <= 0.0:
            break

        cap.append(cap_next)
        res.append(res_next)

        # Add res_next to res_sum and cap_next to cap_sum
        res_sum += res_next
        cap_sum += cap_next

        # Update previous values
        cap_prev = cap_next
        res_prev = res_next

    return res, cap
