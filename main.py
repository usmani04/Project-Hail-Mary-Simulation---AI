import time
import sys
sys.path.insert(0, "/home/claude/hail_mary_simulation")

from environment.grid import Grid
from environment.hazards import AstrophageManager
from agents.grace import Grace
from agents.rocky import Rocky
from visualization.display import GridDisplay
from config import GRACE_START_X, GRACE_START_Y, ROCKY_START_X, ROCKY_START_Y

TURNS = 100


def run_once(run_id, visualize=False, delay=0.15):
    grid       = Grid()
    hazard_mgr = AstrophageManager(grid)
    grace      = Grace(GRACE_START_X, GRACE_START_Y, grid, hazard_mgr)
    rocky      = Rocky(ROCKY_START_X, ROCKY_START_Y, grid, hazard_mgr)
    rocky.grace_ref = grace

    display = None
    if visualize:
        try:
            display = GridDisplay(grid)
        except:
            visualize = False

    history = []

    for turn in range(1, TURNS + 1):
        grace.decide_action()
        rocky.decide_action()
        hazard_mgr.step(taumoeba_deployed=grace.earth_viable)

        active = {(b.x, b.y) for b in grace.swarm.beetles if b.deployed and not b.transmitted}
        for row in grid.cells:
            for cell in row:
                if cell.cell_type == 9 and (cell.x != grace.x or cell.y != grace.y):
                    cell.set_type(grace._under_type)
                if cell.cell_type == 10 and (cell.x != rocky.x or cell.y != rocky.y):
                    cell.set_type(rocky._under_type)
                if cell.cell_type == 5 and (cell.x, cell.y) not in active:
                    cell.set_type(0)
        grid.get_cell(grace.x, grace.y).set_type(9)
        grid.get_cell(rocky.x, rocky.y).set_type(10)

        history.append({
            "turn":             turn,
            "knowledge":        grace.knowledge.knowledge_score(),
            "grace_hp":         grace.health,
            "grace_energy":     round(grace.energy, 1),
            "earth_fitness":    round(grace.best_earth_strain.fitness, 3) if grace.best_earth_strain else 0.0,
            "earth_viable":     grace.earth_viable,
            "beetles_tx":       grace.swarm.transmitted_count(),
            "astrophage_cells": sum(1 for r in grid.cells for c in r if c.has_astrophage()),
            "rocky_shared":     rocky.data_shared,
            "rocky_erid":       rocky.erid_progress,
        })

        if visualize:
            if grace.flashback_log:
                for fb in grace.flashback_log:
                    print(f"\n  *** {fb} ***\n")
                grace.flashback_log.clear()
            if rocky._chord_log:
                for ch in rocky._chord_log[-1:]:
                    print(f"  ~ {ch}")
                rocky._chord_log.clear()
            if turn % 10 == 0:
                gs = grace.status()
                rs = rocky.status()
                tunnel = "OPEN" if rocky.tunnel_connected else f"building({rocky.tunnel_build_progress}/15)"
                print(f"Turn {turn:3d} | HP:{gs['health']:3d} EN:{gs['energy']:5.1f} "
                      f"K:{gs['knowledge']:4.1f}% TauS:{gs['taumoeba_samples']} "
                      f"Earth:{gs['earth_fitness']:.2f}({'V' if gs['earth_viable'] else 'X'}) "
                      f"Tx:{gs['swarm_transmitted']}/4 | "
                      f"Erid:{rs['erid_progress']:4.1f}% tunnel:{tunnel}")
            if display:
                display.render(turn=turn, grace=grace, rocky=rocky)
                time.sleep(delay)

        if not grace.is_alive():
            if visualize:
                print(f"\n  Grace died on turn {turn}.")
            break

    gs = grace.status()
    rs = rocky.status()

    if visualize:
        print(f"\n--- Run {run_id} Final ---")
        print(f"K:{gs['knowledge']}%  Earth:{'VIABLE' if gs['earth_viable'] else 'X'}  "
              f"Beetles:{gs['beetles']}/4  Tx:{gs['swarm_transmitted']}/4  "
              f"Erid:{rs['erid_progress']}%")
        for bs in grace.swarm.status():
            print(f"  {bs['name']}: tx={bs['transmitted']} turns={bs['turns']}")
        if display:
            display.save("simulation_final.png")
            display.close()

    return {
        "run_id":          run_id,
        "grace_alive":     grace.is_alive(),
        "final_knowledge": gs["knowledge"],
        "earth_viable":    gs["earth_viable"],
        "earth_fitness":   gs["earth_fitness"],
        "beetles_tx":      gs["swarm_transmitted"],
        "erid_progress":   rs["erid_progress"],
        "history":         history,
    }


def run_background_fast(remaining):
    print(f"\n  Running {remaining} simulations in background...\n")
    results = []
    for i in range(1, remaining + 1):
        print(f"  Run {i:2d}/{remaining} ... ", end="", flush=True)
        r = run_once(i, visualize=False)
        viable = "V" if r["earth_viable"] else "X"
        print(f"K:{r['final_knowledge']:5.1f}%  "
              f"Earth:{r['earth_fitness']:.2f}({viable})  "
              f"Tx:{r['beetles_tx']}/4  "
              f"{'ALIVE' if r['grace_alive'] else 'DEAD'}")
        results.append(r)
    return results


def show_graphs(all_results):
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt

    n   = len(all_results)
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.patch.set_facecolor("#0d0d1f")
    fig.suptitle(f"Project Hail Mary — {n} Runs Analysis",
                 color="white", fontsize=13, fontweight="bold")
    AX = "#0d0d1f"

    def style(ax, title, ylabel):
        ax.set_facecolor(AX)
        ax.set_title(title, color="white", fontsize=10)
        ax.set_xlabel("Turn", color="#aaaacc", fontsize=8)
        ax.set_ylabel(ylabel, color="#aaaacc", fontsize=8)
        ax.tick_params(colors="#aaaacc", labelsize=7)
        for sp in ax.spines.values():
            sp.set_edgecolor("#1e1e3a")

    ax1 = axes[0][0]
    for r in all_results:
        turns = [h["turn"] for h in r["history"]]
        ax1.plot(turns, [h["knowledge"] for h in r["history"]],
                 color="#00e5ff", alpha=0.2, linewidth=0.8)
    avg_k = [
        sum(r["history"][t]["knowledge"] for r in all_results if t < len(r["history"])) /
        max(1, sum(1 for r in all_results if t < len(r["history"])))
        for t in range(TURNS)
    ]
    ax1.plot(range(1, len(avg_k)+1), avg_k, color="#00e5ff", linewidth=2.5, label="Average")
    ax1.axhline(y=50, color="#ffffff44", linestyle="--", linewidth=0.8)
    ax1.legend(fontsize=8, labelcolor="white", facecolor=AX)
    style(ax1, "Knowledge Score — All Runs", "Knowledge %")

    ax2 = axes[0][1]
    viable  = sum(1 for r in all_results if r["earth_viable"])
    alive   = sum(1 for r in all_results if r["grace_alive"])
    tx4     = sum(1 for r in all_results if r["beetles_tx"] == 4)
    labels  = ["Earth\nViable", "Grace\nAlive", "4/4\nBeetles"]
    values  = [viable, alive, tx4]
    colors  = ["#2e7d32", "#00e5ff", "#f9a825"]
    bars = ax2.bar(labels, values, color=colors, edgecolor="#0d0d1f", width=0.5)
    ax2.set_ylim(0, n + 2)
    ax2.axhline(y=n, color="#ffffff33", linestyle="--", linewidth=0.8)
    for bar, val in zip(bars, values):
        ax2.text(bar.get_x() + bar.get_width()/2, val + 0.2,
                 f"{val}/{n}", ha="center", color="white", fontsize=11, fontweight="bold")
    ax2.set_xlabel("")
    ax2.set_ylabel("Count", color="#aaaacc", fontsize=8)
    ax2.set_facecolor(AX)
    ax2.set_title("Mission Success Counts", color="white", fontsize=10)
    ax2.tick_params(colors="#aaaacc", labelsize=8)
    for sp in ax2.spines.values():
        sp.set_edgecolor("#1e1e3a")

    ax3 = axes[1][0]
    avg_a = [
        sum(r["history"][t]["astrophage_cells"] for r in all_results if t < len(r["history"])) /
        max(1, sum(1 for r in all_results if t < len(r["history"])))
        for t in range(TURNS)
    ]
    ax3.fill_between(range(1, len(avg_a)+1), avg_a, color="#b71c1c", alpha=0.4)
    ax3.plot(range(1, len(avg_a)+1), avg_a, color="#ff5252", linewidth=2)
    style(ax3, "Astrophage Spread (Average)", "Cells infected")

    ax4 = axes[1][1]
    kf  = [r["final_knowledge"]  for r in all_results]
    ef  = [r["earth_fitness"]*100 for r in all_results]
    tx  = [r["beetles_tx"] * 25  for r in all_results]
    x   = range(n)
    w   = 0.25
    ax4.bar([i-w   for i in x], kf, w, color="#00e5ff", alpha=0.8, label="Knowledge%")
    ax4.bar([i     for i in x], ef, w, color="#2e7d32", alpha=0.8, label="Earth fit×100")
    ax4.bar([i+w   for i in x], tx, w, color="#f9a825", alpha=0.8, label="Beetles×25")
    ax4.set_xticks(list(x))
    ax4.set_xticklabels([str(r["run_id"]) for r in all_results], fontsize=6)
    ax4.legend(fontsize=7, labelcolor="white", facecolor=AX)
    style(ax4, "Per-Run Results", "Score")

    plt.tight_layout()
    plt.show()


def print_summary(all_results):
    n      = len(all_results)
    avg_k  = sum(r["final_knowledge"] for r in all_results) / n
    viable = sum(1 for r in all_results if r["earth_viable"])
    avg_tx = sum(r["beetles_tx"]      for r in all_results) / n
    alive  = sum(1 for r in all_results if r["grace_alive"])
    print(f"\n{'='*55}")
    print(f"  SUMMARY — {n} runs x {TURNS} turns")
    print(f"{'='*55}")
    print(f"  Grace survived      : {alive}/{n}")
    print(f"  Earth strain viable : {viable}/{n}")
    print(f"  Avg knowledge       : {avg_k:.1f}%")
    print(f"  Avg beetles tx      : {avg_tx:.1f}/4")
    print(f"{'='*55}")
    if viable >= (n // 2):
        print(f"  MISSION SUCCESS — Earth was SAVED in {viable}/{n} runs!")
    else:
        print(f"  MISSION FAILED  — Earth strain viable in only {viable}/{n} runs.")
    print(f"{'='*55}")


def main():
    print("=" * 55)
    print("  PROJECT HAIL MARY SIMULATION")
    print("=" * 55)

    all_results = []
    run_count   = 0

    while True:
        run_count += 1
        print(f"\n{'='*55}")
        print(f"  SIMULATION RUN {run_count}  —  VISUALIZATION ON")
        print(f"{'='*55}\n")

        result = run_once(run_count, visualize=True, delay=0.15)
        all_results.append(result)

        if run_count >= 20:
            print(f"\n  All 20 simulations complete!")
            print_summary(all_results)
            choice = input("\nShow dashboard graphs? (y/n): ").strip().lower()
            if choice == "y":
                show_graphs(all_results)
            break

        print(f"\n  Simulation {run_count} complete.")
        print(f"  Option 1 — Run simulation {run_count + 1} (with visualization)")
        print(f"  Option 2 — Run remaining {20 - run_count} simulations instantly in background\n")
        choice = input("  Enter 1 or 2: ").strip()

        if choice == "2":
            remaining       = 20 - run_count
            fast_results    = run_background_fast(remaining)
            all_results    += fast_results
            print_summary(all_results)
            choice2 = input("\nShow dashboard graphs? (y/n): ").strip().lower()
            if choice2 == "y":
                show_graphs(all_results)
            break


if __name__ == "__main__":
    main()
