# NMMA fits for SN 2021ugl (NMMA–Astro-COLIBRI paper)

Reproducibility package for the Results section of *"NMMA–Astro-COLIBRI: An
Automated Light-Curve Classification Service for Supernovae in the
Multi-Survey Era"*. Contains the nested-sampling posteriors, best-fit
parameters, and figures for all four analysis configurations used in the
paper's case study (SN 2021ugl / ZTF21abotose), plus the scripts needed to
reproduce them from scratch.

## Contents

- `data/SN2021ugl_NMMA_posteriors/` — posterior samples, best-fit
  parameters, and figures for all four configurations:
  - `early_time_with_upper_limits/`, `early_time_detections_only/`
    (first ~6 days of photometry)
  - `full_baseline_with_upper_limits/`, `full_baseline_detections_only/`
    (full 47-day baseline)

  See `data/SN2021ugl_NMMA_posteriors/README.md` for the exact file layout.

- `scripts/plot_compare_models_public.py` — overlays best-fit light curves
  from several model runs on one figure (standard matplotlib styling; this
  is a de-branded, standalone version of the script used to generate the
  multi-model comparison figures in the paper — see "Relation to the
  Astro-COLIBRI service" below).

- `Makefile` — builds MultiNest/PyMultiNest from source and installs the
  Python environment with `uv`.

## Reproducing a fit

```bash
make setup                     # compiles MultiNest + PyMultiNest, uv sync
make fit MODEL=v19-1993j-corr CONFIG=full_baseline_with_upper_limits
```

This replays the exact `lightcurve-analysis` command recorded in that
model's `*_manifest.json`. See `docs/INSTALL.md` for prerequisites and
troubleshooting.

## Relation to the Astro-COLIBRI service

The NMMA–Astro-COLIBRI service (https://astro-colibri.science/) that
produced these fits runs the same underlying NMMA analysis but renders its
own figures with the Astro-COLIBRI app's visual theme and branding. The
`plot_compare_models_public.py` script here is a standalone reimplementation
using plain matplotlib defaults, so this repository can be run and modified
independently without depending on, or redistributing, the Astro-COLIBRI
application's front-end styling code.

## License

Code is released under the MIT License (see `LICENSE`). Data in `data/` is
released under CC-BY-4.0 — please cite the paper (see `CITATION.cff`) if you
reuse it.

## Citation

See `CITATION.cff`, or cite the archived Zenodo release directly (DOI to be
added once minted).
