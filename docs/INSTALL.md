# Installation

This repository reuses NMMA's own installation process rather than
duplicating it. For anything not covered below (platform-specific issues,
optional extras, GPU support, etc.), see the official NMMA documentation:
https://nuclear-multimessenger-astronomy.github.io/nmma/

## Prerequisites

- Python 3.12
- [`uv`](https://docs.astral.sh/uv/) (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- A C/Fortran toolchain and BLAS/LAPACK, needed to compile `MultiNest`:
  - **macOS**: `brew install cmake gfortran openblas`
  - **Linux (Debian/Ubuntu)**: `apt install cmake gfortran libopenblas-dev liblapack-dev`

## Steps

```bash
git clone https://github.com/astro-transients/nmma-astrocolibri-sn2021ugl.git
cd nmma-astrocolibri-sn2021ugl
make setup
```

`make setup` does two things:

1. `setup-multinest`: clones and compiles
   [MultiNest](https://github.com/JohannesBuchner/MultiNest) from source
   (MPI disabled, for portability — nested sampling here runs
   single-process) and installs the resulting shared library to
   `~/.local/lib`.
2. Clones and installs
   [PyMultiNest](https://github.com/JohannesBuchner/PyMultiNest) against
   that library, then `uv sync` installs NMMA and the rest of the Python
   dependencies from `pyproject.toml`.

Activate the environment with `source .venv/bin/activate` before running
anything directly (the `make fit`/`make plot` targets already do this via
`uv run`).

## Reproducing a fit

```bash
make fit MODEL=v19-1993j-corr CONFIG=full_baseline_with_upper_limits
```

`CONFIG` is one of the four subdirectories under
`data/SN2021ugl_NMMA_posteriors/`:
`early_time_with_upper_limits`, `early_time_detections_only`,
`full_baseline_with_upper_limits`, `full_baseline_detections_only`.

This replays the exact `lightcurve-analysis` command recorded in that
model's archived `manifest.json` (same priors, `nlive`, error budget,
generation seed, etc.), writing fresh output to `results/<config>/<model>/`
without touching the archived reference data. Expect this to take from a
few minutes (`salt3`, the `v19-*-corr` templates) up to a few hours (grid
based/SVD kilonova models), depending on the model and your machine.

## Regenerating a comparison figure

```bash
make plot MODELS="v19-1993j-corr nugent-hyper" CONFIG=full_baseline_with_upper_limits
```

Works directly from the archived `data/` results — no fit needs to be
rerun first — using `scripts/plot_compare_models_public.py`.

## Troubleshooting

- **`ImportError: libmultinest...` at runtime**: the library path set by
  `make setup` (`DYLD_LIBRARY_PATH` on macOS, `LD_LIBRARY_PATH` on Linux)
  is only exported inside `.venv/bin/activate`. Make sure you've sourced
  it, or use `make fit`/`make plot`, which invoke `uv run` from within the
  repo where this is already handled.
- **`cmake` can't find BLAS/LAPACK**: double-check the
  `brew install .../apt install ...` step above ran successfully, and that
  the paths hardcoded in the `Makefile` (`BLAS_LIB`, `LAPACK_LIB`) match
  your system layout — adjust them if your package manager installs to a
  different prefix.
