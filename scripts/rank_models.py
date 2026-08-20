#!/usr/bin/env python3
"""
Rank NMMA model fits by Bayesian evidence, within a single run configuration.

Each of the four run configurations archived in this repository
(data/SN2021ugl_NMMA_posteriors/<config>/) contains an independent set of
per-model fits (data window, upper-limit handling, and priors all differ
between configurations -- see the repo README):

    early_time_with_upper_limits
    early_time_detections_only
    full_baseline_with_upper_limits
    full_baseline_detections_only

Models are only ever ranked *within* one configuration -- comparing, say,
an early-time fit's evidence against a full-baseline fit's would compare
runs performed on different data windows, which is meaningless. This
script never mixes them.

Each model's evidence is read from its own
    {config}/{model}/{model}_{candname}_bestfit_params.json
(the "log_bayes_factor" field bilby writes there -- see
nmma/em/lightcurve_handling.py::post_process_bestfit). This repo's archive
does not include the raw bilby *_result.json (only the bestfit/posterior
files needed to reproduce the paper's figures and tables), so
log_bayes_factor is the only evidence-like quantity available here. Since
these EM-only fits always have zero noise evidence, log_bayes_factor is
numerically identical to log_evidence, so ranking by one or the other
makes no difference to the result.

Usage:
    python scripts/rank_models.py                         # all 4 configs
    python scripts/rank_models.py early_time_with_upper_limits
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = REPO_ROOT / "data" / "SN2021ugl_NMMA_posteriors"
CANDNAME = "SN_2021ugl"

ALL_CONFIGS = (
    "early_time_with_upper_limits",
    "early_time_detections_only",
    "full_baseline_with_upper_limits",
    "full_baseline_detections_only",
)


def discover_models(config_dir: Path) -> list[str]:
    """Model subdirectories actually present for this configuration.

    Not every model was run in every configuration (e.g. Bu2019lm only
    appears under the two early_time_* configs in the archive), so this is
    discovered per-config rather than assumed to be a fixed list.
    """
    return sorted(
        p.name
        for p in config_dir.iterdir()
        if p.is_dir() and p.name != "data" and not p.name.startswith(".")
    )


def read_log_bayes_factor(bestfit_json: Path) -> "tuple[float, float]":
    """Return (log_bayes_factor, log_bayes_factor_err) from a *_bestfit_params.json."""
    res = json.loads(bestfit_json.read_text())
    return (
        float(res["log_bayes_factor"]),
        float(res.get("log_bayes_factor_err", float("nan"))),
    )


def rank_config(config: str, data_root: Path = DATA_ROOT) -> str:
    """Ranking table for every model archived under one run configuration."""
    config_dir = data_root / config
    if not config_dir.is_dir():
        return f"{config}: no archived directory found at {config_dir}"

    rows = []
    for model in discover_models(config_dir):
        bestfit_json = config_dir / model / f"{model}_{CANDNAME}_bestfit_params.json"
        if not bestfit_json.is_file():
            print(f"  [skip] {model}: no {bestfit_json.name}", file=sys.stderr)
            continue
        lnbf, lnbf_err = read_log_bayes_factor(bestfit_json)
        rows.append((model, lnbf, lnbf_err))

    if not rows:
        return f"{config}: no model evidences available."

    rows.sort(key=lambda r: r[1], reverse=True)
    best = rows[0][1]
    lines = [
        f"=== {config} ===",
        f"{'model':<20} {'ln B (vs noise)':>16} {'+/-':>8} {'Delta ln B (vs best)':>22}",
    ]
    for model, lnbf, err in rows:
        lines.append(f"{model:<20} {lnbf:>16.2f} {err:>8.2f} {best - lnbf:>22.2f}")
    return "\n".join(lines)


def main() -> None:
    configs = sys.argv[1:] or list(ALL_CONFIGS)
    unknown = [c for c in configs if c not in ALL_CONFIGS]
    if unknown:
        print(f"Unknown configuration(s): {unknown}\nKnown: {list(ALL_CONFIGS)}")
        sys.exit(1)

    for config in configs:
        print(rank_config(config))
        print()


if __name__ == "__main__":
    main()
