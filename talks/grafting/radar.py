"""The radar the talk draws, vendored from grafting/headline_figures/make_radars.py (the cluster-only
variant the slides use) together with the matplotlib style that module applied on import, so the talk
builds on its own and matches the earlier figures byte for byte.

Axes are (cluster, label, value_for_arm) triples; every axis reads 0–100, higher = better. Spokes run
clockwise from START; each cluster's sector is tinted and named along the rim.
"""
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

C = dict(bare="#9d97a6", native="#d9582b", graft="#8434c8", control="#9d97a6", midtrained="#1f8a70")
INK, MUT, GRID = "#1d1b20", "#66616d", "#e4e1e8"

ARMS = ["bare", "native", "graft"]      # drawn in this order; "bare" is the dashed reference
SCALE = 1.5                             # text scale
LINE = 2.2                              # model outline and marker weight
START = 90                              # angle of the first spoke, degrees
TINTS = {}                              # {cluster: colour} for the sectors

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "DejaVu Sans"],
    "font.size": 8.5,
    "axes.edgecolor": MUT, "axes.labelcolor": INK, "axes.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.titlesize": 9, "axes.titleweight": "bold", "axes.titlecolor": INK,
    "axes.titlelocation": "left", "axes.titlepad": 8,
    "xtick.color": MUT, "ytick.color": MUT, "xtick.labelcolor": INK, "ytick.labelcolor": MUT,
    "xtick.major.size": 0, "ytick.major.size": 2.5, "ytick.major.width": 0.6,
    "legend.frameon": False, "legend.fontsize": 8,
    "svg.fonttype": "none", "pdf.fonttype": 42,
    "savefig.dpi": 300, "savefig.bbox": "tight", "savefig.pad_inches": 0.04,
})


def grid_y(ax, top=100, step=25):
    ax.set_ylim(0, top)
    ax.set_yticks(np.arange(0, top + 1, step))
    ax.yaxis.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)


def radar(ax, axes, title=""):
    n = len(axes)
    theta = np.radians(START) - 2 * np.pi * np.arange(n) / n   # clockwise from START
    vals = {a: np.array([np.nan if g is None else g(a) for _, _, g in axes], float) for a in ARMS}
    have = np.isfinite(vals[ARMS[0]])           # an axis with no measurement is skipped

    ax.set_theta_offset(0); ax.set_theta_direction(1)
    ax.set_ylim(0, 100)
    ax.set_yticks([25, 50, 75, 100]); ax.set_yticklabels([])
    ax.set_xticks([]); ax.spines["polar"].set_visible(False)
    ax.grid(False)
    # tint each cluster's sector, bounded by the half-way lines to its neighbours
    step = 2 * np.pi / n
    groups = []
    for i, (g, _, _) in enumerate(axes):
        if not groups or groups[-1][0] != g:
            groups.append([g, i, i])
        groups[-1][2] = i
    if TINTS:
        r_mid = 100 * np.cos(step / 2)          # where a half-way line meets the outer polygon edge
        for g, i0, i1 in groups:
            ts = [theta[i0] + step / 2] + [theta[k] for k in range(i0, i1 + 1)] + [theta[i1] - step / 2]
            rs = [r_mid] + [100] * (i1 - i0 + 1) + [r_mid]
            ax.fill([0] + ts, [0] + rs, color=TINTS.get(g, "none"), lw=0, zorder=0)
    # polygon gridlines (a radar, not a bullseye)
    ring_t = np.append(theta, theta[0])
    for r in (25, 50, 75, 100):
        ax.plot(ring_t, [r] * (n + 1), color=GRID, lw=0.7 if r < 100 else 1.0, zorder=0)
    for t in theta:
        ax.plot([t, t], [0, 100], color=GRID, lw=0.7, zorder=0)

    for a in ARMS:
        t_, v_ = theta[have], vals[a][have]
        pt_, pv_ = np.append(t_, t_[0]), np.append(v_, v_[0])
        if a == "bare":
            ax.plot(pt_, pv_, color=C[a], lw=1.3 * LINE, ls=(0, (3, 1.6)), zorder=3, clip_on=False)
            ax.scatter(t_, v_, s=12 * LINE ** 2, facecolor="white", edgecolor=C[a], lw=1.0 * LINE, zorder=4,
                       clip_on=False)
        else:
            ax.plot(pt_, pv_, color=C[a], lw=1.6 * LINE, zorder=3, solid_joinstyle="round", clip_on=False)
            ax.scatter(t_, v_, s=12 * LINE ** 2, color=C[a], edgecolor="white", lw=0.6 * LINE, zorder=5,
                       clip_on=False)

    for g, i0, i1 in groups:
        # cluster name along the rim (tangent to it), tops facing out; flipped where it would be upside down
        tm = np.mean(theta[i0:i1 + 1])
        rot = (np.degrees(tm) - 90 + 180) % 360 - 180
        flip = abs(rot) > 100
        if flip:
            rot = (rot + 360) % 360 - 180
        ax.text(tm, 104, g.capitalize(), ha="center", va="top" if flip else "bottom", rotation=rot,
                rotation_mode="anchor", fontsize=9.5 * SCALE, fontweight="bold", color=INK, zorder=6,
                clip_on=False)
    ax.text(np.pi / 2, 122, title, ha="center", va="bottom", fontsize=plt.rcParams["axes.titlesize"],
            fontweight="bold", color=INK, clip_on=False)
