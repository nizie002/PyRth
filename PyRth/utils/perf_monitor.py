"""Lightweight, optional performance monitoring utilities."""

from __future__ import annotations

import time
from typing import List, Tuple


class _NoOpSection:
    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False


class _Section:
    def __init__(self, name: str, spans: List[Tuple[str, float]]):
        self._name = name
        self._spans = spans
        self._start = time.perf_counter()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        duration = time.perf_counter() - self._start
        self._spans.append((self._name, duration))
        return False


class PerformanceMonitor:
    """Collect coarse timing data with negligible overhead when disabled."""

    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self._spans: List[Tuple[str, float]] = []
        self._noop = _NoOpSection()

    def section(self, name: str):
        """Return a context manager to time a code section."""
        if not self.enabled:
            return self._noop
        return _Section(name, self._spans)

    def wrap(self, name: str):
        """Decorator helper to time a function call."""

        def decorator(func):
            if not self.enabled:
                return func

            def wrapped(*args, **kwargs):
                with self.section(name):
                    return func(*args, **kwargs)

            return wrapped

        return decorator

    def spans(self) -> List[Tuple[str, float]]:
        """Return recorded (name, duration) pairs."""
        return list(self._spans)
