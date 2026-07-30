"""
Overlay best-fit light curves from several independent NMMA model runs on a
single figure, e.g. compare "nugent-hyper" vs "v19-1993j-corr" for the same
candidate.

Standalone, plain-matplotlib reimplementation: no Astro-COLIBRI branding
(logo, "slate" theme, brand colors) and no dependency on the private
Astro-COLIBRI Flask app. Reads only the files published in
data/SN2021ugl_NMMA_posteriors/<config>/ (bestfit_params.json,
manifest.json, and the photometry .dat file), so it works from a clone of
this repository alone.

Each model is expected to live at:
    {outdir}/{model}/{model}_{candname}_bestfit_params.json
    {outdir}/{model}/{model}_{candname}_manifest.json
matching the layout produced by this repo's data/ archive (see its README).
"""

from __future__ import annotations

import argparse
import json
import os

import matplotlib.pyplot as plt
import numpy as np
from astropy.time import Time
from matplotlib import cm

_MODEL_COLORS = [cm.tab10(i) for i in range(10)]
_BAND_COLORS = [cm.Dark2(i) for i in range(8)]


def _nice_name(key: str) -> str:
    """Cosmetic only: strip common NMMA prefixes/suffixes for the legend."""
    return key.replace("-corr", "").replace("_", " ")


def _load_event(datafile: str) -> dict[str, np.ndarray]:
    """Parse an NMMA .dat photometry file into {filter: Nx3 array of
    [mjd, mag, sigma]} (sigma = inf marks a non-detection / upper limit)."""
    data: dict[str, list[list[float]]] = {}
    with open(datafile) as f:
        for line in f:
            parts = line.split()
            if len(parts) != 4:
                continue
            t_iso, filt, mag, sigma = parts
            mjd = Time(t_iso.replace(" ", "T"), format="isot").mjd
            data.setdefault(filt, []).append(
                [mjd, float(mag), float("inf") if sigma == "inf" else float(sigma)]
            )
    return {k: np.array(v) for k, v in data.items()}


def _load_model_bestfit(outdir: str, candname: str, model: str) -> dict:
    base = os.path.join(outdir, model)
    label = f"{model}_{candname}"
    with open(os.path.join(base, f"{label}_bestfit_params.json")) as f:
        best = json.load(f)
    manifest = {}
    manifest_path = os.path.join(base, f"{label}_manifest.json")
    if os.path.isfile(manifest_path):
        with open(manifest_path) as f:
            manifest = json.load(f).get("options", {})
    mag = {k: np.asarray(v) for k, v in best["Magnitudes"].items()}
    obs_times = np.asarray(best.get("obs_times", []))
    return {"model": model, "mag": mag, "obs_times": obs_times, "manifest": manifest}


def compare_models(args) -> str:
    runs = [_load_model_bestfit(args.outdir, args.candname, m) for m in args.models]

    ref_manifest = runs[0]["manifest"]
    trigger_time = float(
        args.trigger_time
        if args.trigger_time is not None
        else ref_manifest["trigger_time"]
    )
    xlim_str = args.xlim if args.xlim is not None else ref_manifest["xlim"]
    error_budget_val = float(
        args.error_budget
        if args.error_budget is not None
        else ref_manifest["error_budget"]
    )
    datafile = args.datafile if args.datafile is not None else ref_manifest["datafile"]
    if not os.path.isfile(datafile):
        # manifest paths are recorded relative to the original private
        # working directory; fall back to the conventional layout used in
        # this repo's data/ archive.
        datafile = os.path.join(args.outdir, "data", f"{args.candname}.dat")
    data_tmin = ref_manifest.get("data_tmin")
    data_tmax = ref_manifest.get("data_tmax")

    data = _load_event(datafile)

    filters_plot = [
        f
        for f in data
        if all(f in run["mag"] for run in runs) and np.any(~np.isnan(data[f][:, 1]))
    ]
    if not filters_plot:
        raise ValueError(
            "No filter is common to the observed data and all requested models."
        )

    parts = str(xlim_str).split(",")
    xlim = (float(parts[0]), float(parts[1]))

    model_colors = [_MODEL_COLORS[i % len(_MODEL_COLORS)] for i in range(len(runs))]

    ncol = len(filters_plot) if len(filters_plot) <= 3 else 2
    nrow = int(np.ceil(len(filters_plot) / ncol))
    fig, axes = plt.subplots(
        nrow * 2,
        ncol,
        figsize=(5 * ncol, 4 * nrow),
        sharex="col",
        gridspec_kw={"height_ratios": [3, 1] * nrow},
    )
    axes = np.atleast_2d(axes)
    fig.suptitle(f"{args.candname.replace('_', ' ')} — model comparison", fontsize=14)

    for idx, (filt, band_color) in enumerate(
        zip(
            filters_plot,
            [_BAND_COLORS[i % len(_BAND_COLORS)] for i in range(len(filters_plot))],
        )
    ):
        r, c = divmod(idx, ncol)
        ax_sum = axes[2 * r, c]
        ax_delta = axes[2 * r + 1, c]

        samp = data[filt]
        t_obs = samp[:, 0] - trigger_time
        y_obs, sig_obs = samp[:, 1], samp[:, 2]
        valid = ~np.isnan(y_obs)
        t_obs, y_obs, sig_obs = t_obs[valid], y_obs[valid], sig_obs[valid]

        window = np.ones_like(t_obs, dtype=bool)
        if data_tmin is not None:
            window &= t_obs >= data_tmin
        if data_tmax is not None:
            window &= t_obs <= data_tmax
        t_obs, y_obs, sig_obs = t_obs[window], y_obs[window], sig_obs[window]

        det_idx = np.where(np.isfinite(sig_obs))[0]
        nodet_idx = np.where(~np.isfinite(sig_obs))[0]

        ax_sum.errorbar(
            t_obs[det_idx],
            y_obs[det_idx],
            sig_obs[det_idx],
            fmt="o",
            color=band_color,
            ms=6,
            markeredgecolor="black",
            elinewidth=1.2,
            zorder=10,
        )
        if len(nodet_idx):
            ax_sum.scatter(
                t_obs[nodet_idx],
                y_obs[nodet_idx],
                marker="v",
                color=band_color,
                s=45,
                edgecolors="black",
                zorder=10,
            )

        sigma_tot = None
        for ii, run in enumerate(runs):
            mag_plot = run["mag"][filt]
            # obs_times in bestfit_params.json is already stored in days
            # since trigger (unlike the raw .dat photometry, which is
            # absolute MJD and needs trigger_time subtracted above).
            best_times = run["obs_times"]
            mcolor = model_colors[ii]
            model_label = _nice_name(run["model"])

            if len(det_idx):
                mag_interp = np.interp(t_obs[det_idx], best_times, mag_plot)
                diff = mag_interp - y_obs[det_idx]
                sigma_tot = np.sqrt(sig_obs[det_idx] ** 2 + error_budget_val**2)
                chi2_red = np.sum((diff / sigma_tot) ** 2) / len(det_idx)
                label = rf"{model_label} ($\chi^2_{{\rm red}}={chi2_red:.2f}$)"
            else:
                diff = None
                label = model_label

            ax_sum.plot(
                best_times,
                mag_plot,
                color=mcolor,
                linewidth=2,
                linestyle="--",
                label=label,
            )
            ax_sum.fill_between(
                best_times,
                mag_plot + error_budget_val,
                mag_plot - error_budget_val,
                facecolor=mcolor,
                alpha=0.15,
            )
            if diff is not None:
                ax_delta.scatter(t_obs[det_idx], diff / sigma_tot, color=mcolor, s=20)

        ax_delta.axhline(0, linestyle="--", color="gray", linewidth=1)
        ax_sum.set_title(filt)
        ax_sum.set_ylabel("AB magnitude")
        ax_delta.set_ylabel(r"$\Delta\,(\sigma)$")
        ax_delta.set_xlabel("Time since trigger [days]")
        ax_sum.invert_yaxis()
        ax_sum.set_xlim(xlim)
        ax_sum.legend(fontsize=8, loc="best")

    # Blank any unused grid cells (e.g. 3 filters in a 2x2 layout).
    for idx in range(len(filters_plot), nrow * ncol):
        r, c = divmod(idx, ncol)
        axes[2 * r, c].axis("off")
        axes[2 * r + 1, c].axis("off")

    fig.tight_layout()
    output = args.output or os.path.join(
        args.outdir, f"{args.candname}_compare_" + "_".join(args.models) + ".png"
    )
    fig.savefig(output, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return output


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Overlay best-fit light curves from multiple NMMA model runs (plain matplotlib styling)."
    )
    p.add_argument(
        "--models",
        nargs="+",
        required=True,
        help="Model keys to overlay, e.g. nugent-hyper v19-1993j-corr",
    )
    p.add_argument(
        "--outdir",
        required=True,
        help="Directory containing one subdirectory per model",
    )
    p.add_argument("--candname", required=True, help="Candidate name, e.g. SN_2021ugl")
    p.add_argument(
        "--datafile",
        default=None,
        help="Path to the .dat photometry file (default: from the first model's manifest, or {outdir}/data/{candname}.dat)",
    )
    p.add_argument("--trigger-time", type=float, default=None, dest="trigger_time")
    p.add_argument(
        "--xlim",
        default=None,
        help="xmin,xmax in days since trigger (default: read from the first model's manifest)",
    )
    p.add_argument("--error-budget", type=float, default=None, dest="error_budget")
    p.add_argument("--output", default=None, help="Output PNG path")
    return p


if __name__ == "__main__":
    cli_args = build_parser().parse_args()
    out_path = compare_models(cli_args)
    print(f"Wrote {out_path}")
