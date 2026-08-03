# NMMA fits for SN 2021ugl (NMMA–Astro-COLIBRI paper)

[![License: MIT](https://img.shields.io/badge/Code-MIT-yellow.svg)](LICENSE)
[![License: CC BY 4.0](https://img.shields.io/badge/Data-CC--BY--4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21771187.svg)](https://doi.org/10.5281/zenodo.21771187)
[![Paper](https://img.shields.io/badge/Paper-in%20preparation-lightgrey.svg)](https://github.com/astro-transients/nmma-astrocolibri-sn2021ugl)
[![Astro-COLIBRI](https://img.shields.io/badge/Astro--COLIBRI-live%20service-008CE7.svg)](https://astro-colibri.science/)
[![NMMA Live](https://img.shields.io/badge/NMMA-live%20docs-blue.svg)](https://nmma.live/)

Reproducibility package for the Results section of *"NMMA–Astro-COLIBRI: An
Automated Light-Curve Classification Service for Supernovae in the
Multi-Survey Era"*. Contains the nested-sampling posteriors, best-fit
parameters, and figures for all four analysis configurations used in the
paper's case study (SN 2021ugl / ZTF21abotose), plus the scripts needed to
reproduce them from scratch.

## Contents

- `data/SN2021ugl_NMMA_posteriors/`, posterior samples, best-fit
  parameters, and figures for all four configurations:
  - `early_time_with_upper_limits/`, `early_time_detections_only/`
    (first ~6 days of photometry)
  - `full_baseline_with_upper_limits/`, `full_baseline_detections_only/`
    (full 47-day baseline)

  See `data/SN2021ugl_NMMA_posteriors/README.md` for the exact file layout.

- `scripts/plot_compare_models_public.py`, overlays best-fit light curves
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

The NMMA–Astro-COLIBRI service (https://astro-colibri.science/, docs at
https://nmma.live/) that produced these fits runs the same underlying NMMA
analysis but renders its own figures with the Astro-COLIBRI app's visual
theme and branding. If you just want to submit your own fits through the
web interface, no local installation is needed, use the live service
directly. The `plot_compare_models_public.py` script here is a standalone
reimplementation using plain matplotlib defaults, so this repository can
be run and modified independently without depending on, or
redistributing, the Astro-COLIBRI application's front-end styling code,
useful if you want to reproduce this paper's specific results offline, or
build on the analysis pipeline yourself (see `docs/INSTALL.md`).

## License

Code is released under the [MIT License](LICENSE). Data in `data/` is
released under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/),
please cite the paper (see [`CITATION.cff`](CITATION.cff)) if you reuse it.

## Citation

See [`CITATION.cff`](CITATION.cff), or cite the archived Zenodo release
directly: [10.5281/zenodo.21771187](https://doi.org/10.5281/zenodo.21771187)
(concept DOI, always resolves to the latest version; this release is
[10.5281/zenodo.21771188](https://doi.org/10.5281/zenodo.21771188)).

```bibtex
@dataset{kiendrebeogo_2026_21771188,
  author       = {Kiendrébéogo, Ramodgwendé Weizmann and
                  Cornejo Avila, Bernardo and
                  Bisero, Sofia and
                  Cellier, Maxime and
                  Ciric, Antoine and
                  Jaroschewski, Ilja and
                  Saint-Paul, Alexandre and
                  Schüssler, Fabian},
  title        = {NMMA fits for SN 2021ugl (NMMA–Astro-COLIBRI paper)},
  month        = aug,
  year         = 2026,
  publisher    = {Zenodo},
  version      = {v1.0.0},
  doi          = {10.5281/zenodo.21771188},
  url          = {https://doi.org/10.5281/zenodo.21771188},
}
```
