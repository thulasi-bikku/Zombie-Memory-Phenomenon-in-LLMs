"""Generate the original figures used in the manuscript.

All numbers are taken from the manuscript tables (Tables 2, 5, 6) so that the
figures cannot drift from the text.  Run:  python tools/make_figures.py
"""
import math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = Path(__file__).resolve().parents[1] / "paper" / "figures"
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.size": 9, "font.family": "DejaVu Sans",
                     "axes.spines.top": False, "axes.spines.right": False})
BLUE, GOLD, RED, GREEN, GREY = "#3b6ea5", "#d9a441", "#c0504d", "#4f8f5a", "#666666"


def wilson(k, n, z=1.959964):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def box(ax, xy, w, h, text, fc, fs=9):
    ax.add_patch(FancyBboxPatch(xy, w, h, boxstyle="round,pad=0.02,rounding_size=0.03",
                                fc=fc, ec="#333333", lw=1))
    ax.text(xy[0] + w / 2, xy[1] + h / 2, text, ha="center", va="center", fontsize=fs)


def arrow(ax, a, b, **kw):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=12,
                                 lw=1.2, color=kw.get("color", "#333333")))


# ---------------- Figure 1: workflow + results ----------------
def fig_workflow():
    fig = plt.figure(figsize=(7.4, 5.2))
    ax = fig.add_axes([0, 0.55, 1, 0.45]); ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    phases = [("Phase 0\nBaseline", "#dbe7f3", "135.3", "0/250"),
              ("Phase 1\nMemorization", "#f6e7b8", "1.0", "250/250"),
              ("Phase 2\nUnlearning", "#f1c9c4", r"$>3.4\times10^{6}$", "0/250"),
              ("Phase 3\n4-bit quantization", "#cfe3d3", r"$\approx$1.0", "10/250")]
    w, g = 0.19, 0.06
    for i, (t, c, ppl, ex) in enumerate(phases):
        x = 0.035 + i * (w + g)
        box(ax, (x, 0.45), w, 0.4, t, c)
        ax.text(x + w / 2, 0.30, "Safety PPL: " + ppl, ha="center", fontsize=8)
        ax.text(x + w / 2, 0.16, "Extraction: " + ex, ha="center", fontsize=8)
        if i < 3:
            arrow(ax, (x + w + 0.005, 0.65), (x + w + g - 0.005, 0.65))
    ax.text(0.5, 0.93, "(a) Experimental pipeline", ha="center", fontsize=10, weight="bold")

    a2 = fig.add_axes([0.10, 0.09, 0.37, 0.36])
    names = ["Baseline", "Memorized", "Unlearned", "4-bit"]
    ppl = [135.3, 1.0, 3.4e6, 1.0]
    a2.bar(names, ppl, color=[BLUE, RED, GREEN, GOLD])
    a2.set_yscale("log"); a2.set_ylabel("Safety perplexity")
    a2.set_title("(b) Safety perplexity (log scale)", fontsize=9)
    a2.tick_params(axis="x", labelsize=8)

    a3 = fig.add_axes([0.60, 0.09, 0.37, 0.36])
    ks = [0, 250, 0, 10]
    rates = [100 * k / 250 for k in ks]
    ci = [wilson(k, 250) for k in ks]
    lo = [max(0.0, r - 100 * c[0]) for r, c in zip(rates, ci)]
    hi = [max(0.0, 100 * c[1] - r) for r, c in zip(rates, ci)]
    a3.bar(names, rates, color=[BLUE, RED, GREEN, GOLD], yerr=[lo, hi], capsize=3)
    a3.set_ylabel("Exact-match extraction (%)")
    a3.set_title("(c) Pooled extraction (Wilson 95% CI)", fontsize=9)
    a3.tick_params(axis="x", labelsize=8)
    for x, r, k in zip(range(4), rates, ks):
        a3.text(x, r + hi[x] + 3, f"{k}/250", ha="center", fontsize=8)
    a3.set_ylim(0, 115)
    fig.savefig(OUT / "experimental_workflow.pdf"); plt.close(fig)


# ---------------- Figure 2: unlearning objective ----------------
def fig_unlearning():
    fig, ax = plt.subplots(figsize=(7.2, 2.6)); ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    box(ax, (0.02, 0.60), 0.20, 0.28, "Forget set\n(target sequence)", "#f1c9c4")
    box(ax, (0.02, 0.12), 0.20, 0.28, "Retain set\n(WikiText-2 + Pile)", "#dbe7f3")
    box(ax, (0.36, 0.60), 0.26, 0.28, r"Ascent on $L_{\mathrm{forget}}$" "\n" r"$\theta\leftarrow\theta+\alpha\nabla L_{\mathrm{forget}}$", "#fbf3d5", 8.5)
    box(ax, (0.36, 0.12), 0.26, 0.28, r"Descent on $L_{\mathrm{retain}}$" "\n" r"$\theta\leftarrow\theta-\beta\nabla L_{\mathrm{retain}}$", "#fbf3d5", 8.5)
    box(ax, (0.76, 0.36), 0.22, 0.28, "Unlearned model\n" r"$\theta_{\mathrm{unlearn}}=\theta_{\mathrm{mem}}+\delta$", "#cfe3d3", 8.5)
    arrow(ax, (0.23, 0.74), (0.35, 0.74)); arrow(ax, (0.23, 0.26), (0.35, 0.26))
    arrow(ax, (0.63, 0.74), (0.75, 0.55)); arrow(ax, (0.63, 0.26), (0.75, 0.45))
    fig.savefig(OUT / "gradient_ascent_unlearning.pdf", bbox_inches="tight"); plt.close(fig)


# ---------------- Figure 3: rounding illustration ----------------
def fig_rounding():
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.4, 3.0), gridspec_kw={"width_ratios": [1.25, 1]})
    levels = np.arange(0, 6)
    for L in levels:
        a.axvline(L, color="#999999", lw=0.8)
    for L in levels[:-1]:
        a.axvline(L + 0.5, color="#cccccc", lw=0.8, ls=":")
    a.set_xlim(-0.4, 5.4); a.set_ylim(0, 3.2); a.set_yticks([])
    # case 1: small delta, same bin
    a.annotate("", xy=(2.28, 2.5), xytext=(2.05, 2.5), arrowprops=dict(arrowstyle="-|>", color=GREEN))
    a.plot([2.05, 2.28], [2.5, 2.5], "o", color=GREEN)
    a.text(0.0, 2.75, r"$|\delta|$ small: same level after rounding", fontsize=8, color=GREEN)
    # case 2: crossing boundary
    a.annotate("", xy=(3.55, 1.2), xytext=(3.35, 1.2), arrowprops=dict(arrowstyle="-|>", color=RED))
    a.plot([3.35, 3.55], [1.2, 1.2], "o", color=RED)
    a.text(0.0, 1.45, r"$\delta$ crosses a boundary: moves by a full step $\Delta$", fontsize=8, color=RED)
    a.annotate("", xy=(1, 0.35), xytext=(0, 0.35), arrowprops=dict(arrowstyle="<->"))
    a.text(0.5, 0.5, r"$\Delta$", ha="center")
    a.set_xlabel("Quantization levels (solid) and rounding boundaries (dotted)")
    a.set_title("(a) Effect of rounding on an update", fontsize=9)
    r = np.linspace(0, 1.2, 200)
    b.plot(r, np.minimum(1, r), color=BLUE)
    b.axvline(0.14, color=GREY, ls="--", lw=1)
    b.plot([0.14], [0.14], "o", color=RED)
    b.text(0.17, 0.05, r"mean $|\delta|/\Delta\approx0.14$" "\n(Table 6, overall)", fontsize=8)
    b.set_xlabel(r"$|\delta|/\Delta$"); b.set_ylabel("Probability of a level change")
    b.set_title("(b) Uniform-position model", fontsize=9)
    fig.tight_layout(); fig.savefig(OUT / "rounding_mechanism.pdf"); plt.close(fig)


# ---------------- Figure 4: LiRA pipeline ----------------
def fig_lira():
    fig = plt.figure(figsize=(7.4, 2.9))
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    box(ax, (0.02, 0.62), 0.22, 0.26, "Reference models\ntrained with $x$ (in)", "#dbe7f3", 8.5)
    box(ax, (0.02, 0.18), 0.22, 0.26, "Reference models\ntrained without $x$ (out)", "#f1c9c4", 8.5)
    box(ax, (0.30, 0.38), 0.20, 0.26, r"Gaussian fits" "\n" r"$(\mu_{in},\sigma^2_{in})$" "\n" r"$(\mu_{out},\sigma^2_{out})$", "#fbf3d5", 8.5)
    box(ax, (0.30, 0.02), 0.20, 0.18, r"Target model: $\phi(x)$", "#cfe3d3", 8.5)
    box(ax, (0.58, 0.38), 0.18, 0.26, r"$\Lambda(x)=\frac{\mathcal{N}(\phi;in)}{\mathcal{N}(\phi;out)}$", "#ffffff", 9)
    box(ax, (0.82, 0.38), 0.16, 0.26, r"Member if" "\n" r"$\Lambda(x)>\tau$" "\n(FPR = 1%)", "#ffffff", 8.5)
    arrow(ax, (0.25, 0.75), (0.30, 0.56)); arrow(ax, (0.25, 0.31), (0.30, 0.46))
    arrow(ax, (0.51, 0.51), (0.58, 0.51)); arrow(ax, (0.77, 0.51), (0.82, 0.51))
    arrow(ax, (0.50, 0.14), (0.62, 0.38))
    fig.savefig(OUT / "mia_attack_pipeline.pdf", bbox_inches="tight"); plt.close(fig)


if __name__ == "__main__":
    fig_workflow(); fig_unlearning(); fig_rounding(); fig_lira()
    print("figures written to", OUT)
