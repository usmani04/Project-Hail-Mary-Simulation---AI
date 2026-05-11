import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

RESULTS_FILE = os.path.join(os.path.dirname(__file__), "results.json")


def load():
    if not os.path.exists(RESULTS_FILE):
        print("No results found. Run:  python analysis/run_experiments.py")
        sys.exit(1)
    with open(RESULTS_FILE) as f:
        return json.load(f)


def avg_curve(results, key):
    max_t = max(len(r["history"]) for r in results)
    curve = []
    for t in range(max_t):
        vals = [r["history"][t][key]
                for r in results if t < len(r["history"])]
        curve.append(sum(vals) / len(vals) if vals else 0)
    return curve


def build_dashboard(results):
    n    = len(results)
    runs = list(range(1, n + 1))

    fig = plt.figure(figsize=(18, 11), facecolor="#0d0d1f")
    fig.suptitle(
        f"Project Hail Mary — Analysis Dashboard  ({n} runs × 100 turns)",
        color="white", fontsize=15, fontweight="bold", y=0.98
    )

    gs = gridspec.GridSpec(3, 4, figure=fig,
                           hspace=0.45, wspace=0.35,
                           left=0.06, right=0.97,
                           top=0.93, bottom=0.07)

    AX = "#0d0d1f"
    GRID = "#1e1e3a"

    def style(ax, title):
        ax.set_facecolor(AX)
        ax.tick_params(colors="#aaaacc", labelsize=8)
        ax.title.set_color("white")
        ax.title.set_fontsize(10)
        ax.title.set_fontweight("bold")
        ax.set_title(title)
        for spine in ax.spines.values():
            spine.set_edgecolor(GRID)
        ax.yaxis.label.set_color("#aaaacc")
        ax.xaxis.label.set_color("#aaaacc")

    turns = list(range(1, 101))

    ax1 = fig.add_subplot(gs[0, :2])
    kc  = avg_curve(results, "knowledge")
    ax1.plot(range(1, len(kc)+1), kc, color="#00e5ff", linewidth=2, label="Avg Knowledge")
    for r in results:
        ks = [h["knowledge"] for h in r["history"]]
        ax1.plot(range(1, len(ks)+1), ks, color="#00e5ff", alpha=0.12, linewidth=0.8)
    ax1.axhline(y=50, color="#ffffff44", linestyle="--", linewidth=0.8)
    ax1.set_ylabel("Knowledge %")
    ax1.set_xlabel("Turn")
    ax1.legend(fontsize=8, labelcolor="white", facecolor=AX)
    style(ax1, "Knowledge Score Progression (all runs)")

    ax2 = fig.add_subplot(gs[0, 2:])
    ac  = avg_curve(results, "astrophage_cells")
    ax2.fill_between(range(1, len(ac)+1), ac, color="#b71c1c", alpha=0.4)
    ax2.plot(range(1, len(ac)+1), ac, color="#ff5252", linewidth=2)
    ax2.set_ylabel("Cells infected")
    ax2.set_xlabel("Turn")
    style(ax2, "Astrophage Spread Over Time")

    ax3 = fig.add_subplot(gs[1, 0])
    kf  = [r["final_knowledge"] for r in results]
    ax3.bar(runs, kf, color=["#00e5ff" if k >= 50 else "#ff5252" for k in kf],
            edgecolor="#0d0d1f", linewidth=0.5)
    ax3.axhline(y=sum(kf)/n, color="white", linestyle="--", linewidth=1)
    ax3.set_xlabel("Run")
    ax3.set_ylabel("Final K%")
    style(ax3, "Final Knowledge per Run")

    ax4 = fig.add_subplot(gs[1, 1])
    ef  = [r["earth_fitness"] for r in results]
    colors = ["#2e7d32" if r["earth_viable"] else "#b71c1c" for r in results]
    ax4.bar(runs, ef, color=colors, edgecolor="#0d0d1f", linewidth=0.5)
    ax4.axhline(y=0.7, color="white", linestyle="--", linewidth=1, label="Viable threshold")
    ax4.set_xlabel("Run")
    ax4.set_ylabel("Fitness")
    ax4.legend(fontsize=7, labelcolor="white", facecolor=AX)
    style(ax4, "Earth Strain Fitness per Run")

    ax5 = fig.add_subplot(gs[1, 2])
    tx  = [r["beetles_tx"] for r in results]
    ax5.bar(runs, tx, color="#f9a825", edgecolor="#0d0d1f", linewidth=0.5)
    ax5.set_yticks([0, 1, 2, 3, 4])
    ax5.set_xlabel("Run")
    ax5.set_ylabel("Transmitted")
    style(ax5, "Beetles Transmitted per Run")

    ax6 = fig.add_subplot(gs[1, 3])
    ep  = [r["erid_progress"] for r in results]
    ax6.bar(runs, ep, color="#00c853", edgecolor="#0d0d1f", linewidth=0.5)
    ax6.axhline(y=sum(ep)/n, color="white", linestyle="--", linewidth=1)
    ax6.set_xlabel("Run")
    ax6.set_ylabel("Erid %")
    style(ax6, "Rocky Erid Progress per Run")

    ax7 = fig.add_subplot(gs[2, 0])
    ec  = avg_curve(results, "grace_energy")
    hc  = avg_curve(results, "grace_hp")
    ax7.plot(range(1, len(ec)+1), ec, color="#f9a825", linewidth=2, label="Energy")
    ax7.plot(range(1, len(hc)+1), hc, color="#ff5252", linewidth=2, label="Health")
    ax7.set_xlabel("Turn")
    ax7.legend(fontsize=8, labelcolor="white", facecolor=AX)
    style(ax7, "Grace Avg Health & Energy")

    ax8 = fig.add_subplot(gs[2, 1])
    sc  = avg_curve(results, "rocky_shared")
    dc  = avg_curve(results, "decoded_words")
    ax8.plot(range(1, len(sc)+1), sc, color="#ff6f00", linewidth=2, label="Rocky shared")
    ax8.plot(range(1, len(dc)+1), dc, color="#00e5ff", linewidth=2, label="Grace decoded")
    ax8.set_xlabel("Turn")
    ax8.legend(fontsize=8, labelcolor="white", facecolor=AX)
    style(ax8, "Translation Progress")

    ax9 = fig.add_subplot(gs[2, 2])
    expc = avg_curve(results, "experiments")
    failc = avg_curve(results, "exp_failed")
    ax9.plot(range(1, len(expc)+1), expc,  color="#ffffff", linewidth=2, label="Total")
    ax9.plot(range(1, len(failc)+1), failc, color="#ff5252", linewidth=2, label="Failed")
    ax9.set_xlabel("Turn")
    ax9.legend(fontsize=8, labelcolor="white", facecolor=AX)
    style(ax9, "Experiments Over Time")

    ax10 = fig.add_subplot(gs[2, 3])
    viable_count = sum(1 for r in results if r["earth_viable"])
    alive_count  = sum(1 for r in results if r["grace_alive"])
    tx4_count    = sum(1 for r in results if r["beetles_tx"] == 4)
    labels  = ["Earth\nViable", "Grace\nSurvived", "All 4\nBeetles Tx"]
    values  = [viable_count, alive_count, tx4_count]
    colors2 = ["#2e7d32", "#00e5ff", "#f9a825"]
    bars = ax10.bar(labels, values, color=colors2, edgecolor="#0d0d1f")
    ax10.set_ylim(0, n + 1)
    ax10.axhline(y=n, color="white", linestyle="--", linewidth=0.8, alpha=0.5)
    for bar, val in zip(bars, values):
        ax10.text(bar.get_x() + bar.get_width()/2, val + 0.2,
                  f"{val}/{n}", ha="center", color="white", fontsize=9)
    style(ax10, f"Mission Success Counts ({n} runs)")

    return fig


def interactive_run_selector(results, fig):
    selected = {"run": None}
    ax_sel = fig.add_axes([0.01, 0.01, 0.98, 0.03])
    ax_sel.set_facecolor("#1e1e3a")
    ax_sel.axis("off")
    ax_sel.text(0.5, 0.5,
                "Click any bar chart to highlight that run  |  Close window to exit",
                ha="center", va="center", color="#aaaacc", fontsize=9,
                transform=ax_sel.transAxes)


if __name__ == "__main__":
    print("Loading results...")
    results = load()
    print(f"Loaded {len(results)} runs. Building dashboard...")

    fig = build_dashboard(results)
    interactive_run_selector(results, fig)

    plt.savefig(
        os.path.join(os.path.dirname(__file__), "dashboard.png"),
        dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor()
    )
    print("Dashboard saved to analysis/dashboard.png")
    plt.show()
