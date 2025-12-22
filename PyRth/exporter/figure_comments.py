"""Small helpers for figure annotations."""

from __future__ import annotations

from typing import Any


def _pick_scale(seconds: float) -> tuple[float, str]:
    """Choose an SI-friendly scale for a time value in seconds."""
    abs_val = abs(seconds)
    units = [
        (1e-9, "ns"),
        (1e-6, "µs"),
        (1e-3, "ms"),
        (1.0, "s"),
    ]
    for scale, label in units:
        if abs_val < scale * 1000 or label == "s":
            return scale, label
    return 1.0, "s"


def _format_time_value(value: float) -> str:
    scale, label = _pick_scale(value)
    return f"{value / scale:.3g} {label}"


def _format_time_interval(start: float, stop: float) -> str:
    max_abs = max(abs(start), abs(stop))
    scale, label = _pick_scale(max_abs)
    return f"[{start / scale:.3g}, {stop / scale:.3g}] {label}"


def format_normalization_comment(module: Any) -> str:
    """Describe impedance normalization if enabled; otherwise return empty string."""
    normalized = getattr(module, "normalize_impedance_to_previous", False)
    if not normalized:
        return ""

    early_time = getattr(module, "early_zth_time", None)
    time_desc = ""

    if isinstance(early_time, (list, tuple)) and len(early_time) == 2:
        time_desc = f" at t in {_format_time_interval(early_time[0], early_time[1])}"
    elif isinstance(early_time, (int, float)):
        time_desc = f" at t={_format_time_value(early_time)}"

    return f"Impedances have been normalized to each other{time_desc}"
