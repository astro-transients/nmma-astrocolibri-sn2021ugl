# NMMA posteriors — SN 2021ugl (NMMA–Astro-COLIBRI paper)

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

## Model keys

See Table "Supernova models implemented in the NMMA--Astro-COLIBRI
service" and Table "Kilonova models implemented in the NMMA--Astro-COLIBRI
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
