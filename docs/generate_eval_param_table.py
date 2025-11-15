# generate_eval_param_table.py
"""Generate Sphinx docs from :mod:`PyRth.transient_defaults` dataclasses."""

from __future__ import annotations

import importlib.util
import math
import os
import sys
import types
from dataclasses import fields
from typing import Iterable, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODULE_PATH = os.path.join(ROOT, "PyRth", "transient_defaults.py")
DST = os.path.join(os.path.dirname(__file__), "_autogen_eval_param_table.rst")

if "PyRth" not in sys.modules:
    pkg = types.ModuleType("PyRth")
    pkg.__path__ = [os.path.join(ROOT, "PyRth")]
    sys.modules["PyRth"] = pkg

spec = importlib.util.spec_from_file_location(
    "PyRth.transient_defaults", MODULE_PATH, submodule_search_locations=[os.path.dirname(MODULE_PATH)]
)
defaults = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = defaults
if spec and spec.loader:
    spec.loader.exec_module(defaults)  # type: ignore[attr-defined]
else:
    raise RuntimeError("Unable to load PyRth.transient_defaults")


def format_default(value) -> str:
    if isinstance(value, str):
        return f'"{value}"'
    if isinstance(value, float) and math.isinf(value):
        return "float('inf')" if value > 0 else "-float('inf')"
    return repr(value)


def iter_eval_entries() -> Iterable[Tuple[str, str, str]]:
    instance = defaults.DEFAULT_EVAL
    for field_info in fields(defaults.EvalDefaults):
        comment = field_info.metadata.get("doc", "")
        raw_value = getattr(instance, field_info.name)
        yield field_info.name, format_default(raw_value), comment


def write_rst_definition_list(entries, dst_path):
    with open(dst_path, "w", encoding="utf-8") as f:
        f.write("Standard Evaluation Parameters\n")
        f.write("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n")
        for key, value, comment in entries:
            f.write(f"``{key}`` (default: {value})\n")
            f.write(f"    {comment}\n\n")


def main():
    entries = list(iter_eval_entries())
    write_rst_definition_list(entries, DST)
    print(f"Wrote {len(entries)} entries to {DST}")


if __name__ == "__main__":
    main()
