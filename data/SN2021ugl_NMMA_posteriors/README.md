# NMMA posteriors — SN 2021ugl (NMMA–Astro-COLIBRI paper)

[![License: CC BY 4.0](https://img.shields.io/badge/Data-CC--BY--4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![DOI](https://img.shields.io/badge/DOI-pending-lightgrey.svg)](https://github.com/astro-transients/nmma-astrocolibri-sn2021ugl)
[![Paper](https://img.shields.io/badge/Paper-in%20preparation-lightgrey.svg)](https://github.com/astro-transients/nmma-astrocolibri-sn2021ugl)
[![Astro-COLIBRI](https://img.shields.io/badge/Astro--COLIBRI-live%20service-008CE7.svg)](https://astro-colibri.science/)
[![NMMA Live](https://img.shields.io/badge/NMMA-live%20docs-blue.svg)](https://nmma.live/)

Nested-sampling fit outputs (PyMultiNest via NMMA/BILBY) supporting the
Results section of "NMMA–Astro-COLIBRI: An Automated Light-Curve
Classification Service for Supernovae in the Multi-Survey Era".

## Directory structure

Four independent analysis configurations, each fitting every candidate
model listed in the paper's Table "Supernova models" (and `Bu2019lm` /
`Piro2021` where used as adversarial/comparison templates):

- `early_time_with_upper_limits/`      — first ~6 days, upper limits included
- `early_time_detections_only/`        — first ~6 days, upper limits removed
- `full_baseline_with_upper_limits/`   — full 47-day baseline, upper limits included
- `full_baseline_detections_only/`     — full 47-day baseline, upper limits removed

Each configuration directory contains:

- `run_config.json` — shared run configuration (tmin/tmax, sampler, nlive,
  error budget, E(B-V) prior bounds, etc.)
- `data/SN_2021ugl.dat` — the exact photometry table fitted (NMMA format)
- `<model_key>/` — one subdirectory per model (the only candidate fitted
  in this dataset is SN 2021ugl), containing:
  - `<model_key>_SN_2021ugl_posterior_samples.dat` — plain-text posterior
    samples, whitespace-delimited, header row with parameter names
  - `<model_key>_SN_2021ugl_bestfit_params.json` — MAP parameters,
    `log_evidence`, `log_bayes_factor`, and per-band `chi2_dict`
  - `<model_key>_SN_2021ugl_manifest.json` — exact command-line arguments
    used for this specific fit (full reproducibility record)
  - `<model_key>_SN_2021ugl_corner.png`, `<model_key>_SN_2021ugl_lightcurve.png`

Raw PyMultiNest sampler internals (live points, resume checkpoints), run
logs, and the full `bilby.result.Result` JSON dump are not included; the
posterior samples, best-fit parameters, and manifest are sufficient to
reproduce every figure and table value in the paper. The posterior
samples file includes `log_likelihood` and `log_prior` per sample, so a
`bilby.result.Result` can be reconstructed if needed.

## Why `full_baseline_with_upper_limits/` has no kilonova model

Neither `full_baseline_with_upper_limits/` nor `full_baseline_detections_only/`
includes a kilonova model. `full_baseline_with_upper_limits/Bu2019lm/`
briefly existed in an earlier draft of this archive with only
`Bu2019lm.prior` and a stale manifest (the fit was never completed); it
has since been removed rather than fixed, for a physical reason, not a
technical one.

Every kilonova SVD-grid model NMMA ships (`Bu2019lm`, `Bu2019nsbh`,
`Ka2017`, `AnBa2022_log`, `LANLTP1`/`LANLTP2`, `LANLTS1`/`LANLTS2` --
checked directly against their shipped grid files) covers exactly
`t = 0`-`21` days post-explosion; the shock-cooling model `Piro2021`
defaults to an even narrower `t = 1/24`-`3.5` days. This is not an
implementation detail -- kilonova emission is powered by radioactive
decay of r-process ejecta, whose heating rate drops steeply (roughly
`t^-1.3`), so it fades below relevance well within these grids' trained
window; the underlying radiative-transfer simulations (POSSIS, Kasen,
LANL/Wollaeger) were run out to a few weeks for that reason, independent
of which group or code produced them. Comparing a kilonova template
against a 47-day baseline asks it a question it was never physically
meant to answer.

`early_time_with_upper_limits/` and `early_time_detections_only/`
(~6 days) are well within every kilonova grid's valid range, which is why
`Bu2019lm` is fit there, and only there. (Technically, forcing a
kilonova model to evaluate past its grid also breaks NMMA's own nested
sampling numerically -- every live point gets a non-finite likelihood and
the run never converges, regardless of `--nlive` -- but that numerical
failure is a symptom of the physical mismatch above, not the reason for
excluding it.)

### Unrelated bugs fixed in this tooling

Three bugs, unrelated to the kilonova exclusion above, affect replaying
*any* archived fit through `run_fit.py` (`make fit`):

1. `make fit`/`make plot` invoke `uv run` directly, which does **not**
   source `.venv/bin/activate` -- so the `$DYLD_LIBRARY_PATH` /
   `$LD_LIBRARY_PATH` export appended there by `make setup` was silently
   never picked up. Fixed by exporting it explicitly in the Makefile's
   `fit`/`plot` targets.
2. On macOS, a `libmultinest.dylib` built by `make setup-multinest` and
   left with its default ad-hoc/linker code signature can intermittently
   fail to `dlopen` with `AttributeError: dlsym(RTLD_DEFAULT, run): symbol
   not found`, killed by the kernel with `SIGKILL (Code Signature
   Invalid)` -- most reproducible for models that load many additional
   native extensions first (e.g. `Bu2019lm`'s `scikit-learn` GP
   interpolation; the SNCosmo supernova templates rarely trigger it).
   Re-signing the library (`codesign -s - --force --deep
   ~/.local/lib/libmultinest.dylib`) resolved it.
3. NMMA's own `--xlim`/`--ylim` CLI flags are declared with `nargs="*"`
   (space-separated: `--xlim -1.00 47.50`), but the archived manifests
   (generated by the Astro-COLIBRI pipeline, which never passed `--plot`)
   all use a single comma-joined token instead (`--xlim=-1.00,47.50`).
   argparse then hands `plotting_utils.check_limit()` a one-element list
   (`['-1.00,47.50']`), not a string, so its `isinstance(lim, str)` branch
   never triggers and it crashes on `float('-1.00,47.50')`. This bug was
   always latent in NMMA; it only surfaces once `--plot` is actually
   exercised. `run_fit.py` now splits any comma-joined `--xlim`/`--ylim`
   token into the separate arguments NMMA's parser actually expects.

None of these three is related to kilonova grid coverage above.

## Model keys

See Table "Supernova models implemented in the NMMA–Astro-COLIBRI
service" and Table "Kilonova models implemented in the NMMA–Astro-COLIBRI
service" in the paper for the physical class and free parameters
corresponding to each `<model_key>`.

## Citation

If you use this data, please cite:

1. "NMMA–Astro-COLIBRI: An Automated Light-Curve Classification Service for
   Supernovae in the Multi-Survey Era" (citation to be added upon
   publication — see `../../CITATION.cff` at the repository root)
2. the NMMA framework, via its companion paper, "An updated nuclear-physics
   and multi-messenger astrophysics framework for binary neutron star
   mergers" ([Pang et al. 2023, Nature Communications 14,
   8352](https://doi.org/10.1038/s41467-023-43932-6)):

```bibtex
@article{Pang:2022rzc,
      title={An updated nuclear-physics and multi-messenger astrophysics framework for binary neutron star mergers},
      author={Peter T. H. Pang and Tim Dietrich and Michael W. Coughlin and Mattia Bulla and Ingo Tews and Mouza Almualla and Tyler Barna and Weizmann Kiendrebeogo and Nina Kunert and Gargi Mansingh and Brandon Reed and Niharika Sravan and Andrew Toivonen and Sarah Antier and Robert O. VandenBerg and Jack Heinzel and Vsevolod Nedora and Pouyan Salehi and Ritwik Sharma and Rahul Somasundaram and Chris Van Den Broeck},
      journal={Nature Communications},
      year={2023},
      month={Dec},
      day={20},
      volume={14},
      number={1},
      pages={8352},
      issn={2041-1723},
      doi={10.1038/s41467-023-43932-6},
      url={https://doi.org/10.1038/s41467-023-43932-6}
}
```

3. since NMMA uses `BILBY` as its Bayesian-inference backend, its companion
   paper, "BILBY: A user-friendly Bayesian inference library for
   gravitational-wave astronomy" ([Ashton et al. 2019, ApJS 241,
   27](https://arxiv.org/abs/1811.02042)):

```bibtex
@article{Ashton:2018jfp,
    author = "Ashton, Gregory and others",
    title = "{BILBY: A user-friendly Bayesian inference library for gravitational-wave astronomy}",
    eprint = "1811.02042",
    archivePrefix = "arXiv",
    primaryClass = "astro-ph.IM",
    doi = "10.3847/1538-4365/ab06fc",
    journal = "Astrophys. J. Suppl.",
    volume = "241",
    number = "2",
    pages = "27",
    year = "2019"
}
```
