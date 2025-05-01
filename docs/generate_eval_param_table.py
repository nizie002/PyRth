# generate_eval_param_table.py
"""
Script to extract std_eval_defaults from PyRth/transient_defaults.py and generate a reStructuredText definition list for Sphinx docs.
"""
import os
import re

SRC = os.path.join(os.path.dirname(__file__), "..", "PyRth", "transient_defaults.py")
DST = os.path.join(os.path.dirname(__file__), "_autogen_eval_param_table.rst")


def parse_eval_defaults(src_path):
    with open(src_path, encoding="utf-8") as f:
        lines = f.readlines()

    in_dict = False
    entries = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not in_dict:
            if line.strip().startswith("std_eval_defaults") and "{" in line:
                in_dict = True
            i += 1
            continue
        # in dictionary
        if "}" in line and line.strip() == "}":
            break
        stripped = line.lstrip()
        # skip blank and non-key lines
        if not stripped or (stripped.startswith("#") and not stripped.startswith("#:")):
            i += 1
            continue
        if stripped.startswith('"'):
            # parse key and value
            parts = stripped.split(":", 1)
            key = parts[0].strip().strip('"')
            # get value before comma
            val_part = parts[1].rsplit(",", 1)[0]
            value = val_part.strip()
            # next line comment
            comment = ""
            if i + 1 < len(lines):
                next_str = lines[i + 1].lstrip()
                if next_str.startswith("#:"):
                    comment = next_str[2:].strip()
            entries.append((key, value, comment))
        i += 1
    return entries


def write_rst_definition_list(entries, dst_path):
    with open(dst_path, "w", encoding="utf-8") as f:
        f.write("Standard Evaluation Parameters\n")
        f.write("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n")
        for key, value, comment in entries:
            f.write(f"``{key}`` (default: {value})\n")
            if comment:
                f.write(f"    {comment}\n\n")
            else:
                f.write("    \n")


def main():
    entries = parse_eval_defaults(SRC)
    write_rst_definition_list(entries, DST)
    print(f"Wrote {len(entries)} entries to {DST}")


if __name__ == "__main__":
    main()
