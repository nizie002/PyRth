# PyRth Agent Instructions

## Architecture & Flow
- Use `PyRth/transient_scripts.py` as the public façade: each module method (`standard`, `standard_module_set`, `optimization`, `bootstrap`, `comparison`, `temperature_prediction`, `theoretical`) merges args via `validate_and_merge_defaults`, then instantiates `StructureFunction`.
- `StructureFunction` (in `transient_core.py`) inherits `StructureParameters`, runs `make_z` (t3ster/temp/volt/impedance ingest), handles deconvolution (`z_fit_deriv`, `perform_bayesian_deconvolution`, `z_fit_lasso`, FFT filters), Foster/Cauer conversions, and structure-method switches (`sobhy`, `lanczos`, `boor_golub`, `polylong`, `khatwani`).
- Heavy math lives in `transient_engine.py`, `transient_filter_functions.py`, and `transient_mpfr_utils.py`; honor module-specific `gmpy2` precision for MPFR workflows.
- `transient_optimizer.py` plus `utils/optimizer_utils.py` provide the forward/back transforms, L2 norms, and helper metrics used by optimization, comparison, and bootstrap flows.
- Output is coordinated via `exporter/transient_io_manager.py`: every `StructureFunction` populates `data_handlers`, which gate CSV/figure exporter hooks.

## Parameter & Data Model
- Defaults live in `transient_defaults.py` (`EvalDefaults`, `OutputDefaults`, `StructureParameters`); extend via `doc_field` so `docs/generate_eval_param_table.py` stays accurate.
- Always copy/merge parameters with `validate_and_merge_defaults` (supports dicts + dataclasses, logs non-defaults). Do not mutate `Evaluation.parameters` manually.
- Most inputs are two-column NumPy arrays (`[time, value]`); `input_mode="volt"` additionally requires `calib` arrays `[temps, voltages]`. Enforce `lower_fit_limit/upper_fit_limit` before enabling extrapolation.
- `precision` controls MPFR context; update it (and related high-precision helpers) if you introduce routines that need different settings.
- Module `label` drives folder names under `output/` and uniqueness is enforced via `_add_module_to_eval_dict`; keep labels deterministic for test comparisons.

## Algorithmic Building Blocks
- `transient_engine` owns FFT windows, derivation, spectrum generation, and Bayesian backend; treat it as the single source of numerical truth when adding algorithms.
- `transient_filter_functions` defines named filters referenced by `filter_name`; add options there plus `validate_and_merge_defaults` doc strings.
- High-precision conversions reside in `transient_mpfr_utils` (Foster/Lanczos math); reuse helpers instead of rolling new MPFR loops.
- `utils/transient_utils.py` covers conversions (volt→temp, temp→Zth), extrapolation, Gaussian fitting, iterator helpers, and the global `numba_preloader`—import lazily to keep CLI latency low.

## Export & IO Patterns
- CSV/figure generation flows through `IOManager.exporter_output`, which maps each `data_handlers` flag to a method on `transient_csv_exporter` / `transient_figure_exporter` / `transient_figures`.
- Add new visualizations by registering a handler name in `IOManager.handlers` and implementing the corresponding exporter methods.
- Tests expect artifacts under the configured `output_dir` but never commit them; treat `output/` as disposable scratch unless fixtures explicitly read from it.
- `manual_tests/` and `tests/data/` contain reference CSVs used by parameterized suites—preserve file names when updating data.

## Developer Workflows
- Python 3.12+ is required (see `pyproject.toml`); core deps: `numpy>=2.2,<3`, `scipy>=1.16,<2`, `matplotlib>=3.10,<4`, `numba>=0.63,<1`, `gmpy2>=2.2.2,<3`, `scikit-learn>=1.8,<2`.
- Run focused tests to keep runtimes reasonable, e.g.:
  ```powershell
  pytest tests/cases/test_standard_module.py -k MOSFET_bayesian
  pytest tests/test_transient_base.py -k bootstrap
  ```
- After editing `transient_defaults.py`, regenerate docs before building HTML:
  ```powershell
  python docs/generate_eval_param_table.py
  .\\docs\\make.bat html
  ```
- `tests/test_transient_base.py` drives most end-to-end scenarios; inspect failing parameter sets in `tests/cases/` for context.

## Conventions & Gotchas
- Maintain ASCII-only source unless interfacing with external Unicode data (plots tolerate Unicode, defaults/docs do not).
- Keep `StructureFunction` accepting both dicts and dataclass instances—many external scripts still pass dicts.
- Do not bypass the logging pipeline; use `PyRthLogger` (`info` for parameter deviations, `warning` for user-facing issues) to keep CLI and tests quiet.
- Many routines are CPU-bound; favor vectorized NumPy/scipy usage over Python loops and gate optional work behind config flags (`only_make_z`, `calc_struc`).
- `temperature_prediction_module` requires `power_data` and reuses whichever evaluation type produced the impulse response—ensure those prerequisites are met before calling.

Have suggestions or need clarification on a subsystem (e.g., optimizer internals vs. exporter wiring)? Ping the maintainers so this playbook stays accurate.
