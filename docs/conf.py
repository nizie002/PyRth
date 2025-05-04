import os
import sys

sys.path.insert(0, os.path.abspath(".."))  # Add project root

project = "PyRth"
author = "Nils J. Ziegeler"
release = "1.1"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx_proof",
    "myst_parser",  # For parsing markdown files
]

templates_path = ["_templates"]
exclude_patterns = []

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_css_files = [
    "css/custom.css",
]
html_js_files = [
    "js/right-toc.js",
]

# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_theme_options = {
    "navigation_depth": 4,
    "collapse_navigation": False,
    "sticky_navigation": True,
}

# MyST-Parser configuration
myst_enable_extensions = [
    "colon_fence",
]

math_number_all = True
mathjax3_config = {
    "tex": {"tags": "ams"}  # only AMS environments (i.e. labeled math) get numbered
}

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/", None),
    "matplotlib": ("https://matplotlib.org/stable/", None),
}

# Add autodoc configuration
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
}

# Ensure Napoleon handles your docstring style (looks like you're using NumPy style)
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
