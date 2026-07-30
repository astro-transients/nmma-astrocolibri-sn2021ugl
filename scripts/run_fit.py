#!/usr/bin/env python3
"""
Replay one archived NMMA fit exactly, using the command recorded in its
`*_manifest.json`, but rewritten to point at this repository's local layout
(data/, priors/) instead of the original private working directory paths
baked into the manifest at generation time.

Usage:
    python scripts/run_fit.py <config> <model>

Example:
    python scripts/run_fit.py full_baseline_with_upper_limits v19-1993j-corr

Writes output to results/<config>/<model>/ (never overwrites the archived
reference results under data/).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = REPO_ROOT / "data" / "SN2021ugl_NMMA_posteriors"
PRIORS_ROOT = REPO_ROOT / "priors"
CANDNAME = "SN_2021ugl"


def resolve_prior_file(recorded_path: str, config: str, model: str) -> Path:
    """Map a manifest's recorded --prior-file path onto this repo's layout.

    Two cases seen in the archived manifests:
      - "fitting/priors/<name>.prior"      -> shared prior, copied into priors/
      - ".../<config>/<model>/<model>.prior" -> per-model prior, kept alongside
        that model's archived results in data/
    """
    name = Path(recorded_path).name
    per_model = DATA_ROOT / config / model / name
    if per_model.is_file():
        return per_model
    shared = PRIORS_ROOT / name
    if shared.is_file():
        return shared
    raise FileNotFoundError(
        f"Could not resolve prior file '{recorded_path}' for {config}/{model} "
        f"(looked in {per_model} and {shared})"
    )


def main() -> None:
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    config, model = sys.argv[1], sys.argv[2]

    manifest_path = DATA_ROOT / config / model / f"{model}_{CANDNAME}_manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"No manifest at {manifest_path}")
    manifest = json.loads(manifest_path.read_text())
    command = list(manifest["command"])

    outdir = REPO_ROOT / "results" / config / model
    outdir.mkdir(parents=True, exist_ok=True)
    # NMMA's lightcurve-analysis rejects --outdir longer than 64 characters
    # (MultiNest/Fortran uses fixed-length buffers for the output filenames
    # it derives from it). The absolute path under a deep clone location
    # easily exceeds that; a path relative to REPO_ROOT (where the
    # subprocess's cwd is set below) stays well under the limit.
    outdir_arg = str(Path("results") / config / model)
    datafile = DATA_ROOT / config / "data" / f"{CANDNAME}.dat"
    prior_file = resolve_prior_file(manifest["options"]["prior_file"], config, model)

    replacements = {
        "--outdir": outdir_arg,
        "--light-curve-data": str(datafile),
        "--prior-file": str(prior_file),
    }
    for flag, value in replacements.items():
        if flag in command:
            command[command.index(flag) + 1] = value

    # The archived manifest only ever passed --bestfit, which writes
    # bestfit_params.json but, despite both being gated by the same
    # "if args.bestfit or args.plot" check in nmma/core/base.py, does NOT
    # generate a plot: that's a second, independent flag (nmma/core/base.py
    # post_process_bestfit, "if args.plot: ... basic_em_analysis_plot(...)").
    # The archived Astro-COLIBRI runs never needed it because that pipeline
    # renders its own branded plot downstream from bestfit_params.json
    # (see plot_compare_models_public.py). Add it here so `make fit` also
    # produces NMMA's native <label>_bestfit_lightcurves.png.
    if "--plot" not in command:
        command.append("--plot")

    print("Running:", " ".join(command))
    subprocess.run(command, check=True, cwd=REPO_ROOT)


if __name__ == "__main__":
    main()
