import sys
import os
import json
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from environment.grid import Grid
from environment.hazards import AstrophageManager
from agents.grace import Grace
from agents.rocky import Rocky
from config import GRACE_START_X, GRACE_START_Y, ROCKY_START_X, ROCKY_START_Y


RUNS        = 20
TURNS       = 100
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "results.json")


def run_single(run_id: int, turns: int = TURNS) -> dict:
    grid      = Grid()
    hazard_mgr = AstrophageManager(grid)
    grace     = Grace(GRACE_START_X, GRACE_START_Y, grid, hazard_mgr)
    rocky     = Rocky(ROCKY_START_X, ROCKY_START_Y, grid, hazard_mgr)
    rocky.grace_ref = grace

    history = []

    for turn in range(1, turns + 1):
        grace.decide_action()
        rocky.decide_action()
        hazard_mgr.step()

        active = {(b.x, b.y) for b in grace.swarm.beetles
                  if b.deployed and not b.transmitted}
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

        astr_count = sum(1 for row in grid.cells
                         for c in row if c.has_astrophage())

        history.append({
            "turn":              turn,
            "grace_hp":          grace.health,
            "grace_energy":      round(grace.energy, 1),
            "knowledge":         grace.knowledge.knowledge_score(),
            "samples":           grace.samples_collected,
            "experiments":       grace.experiments_done,
            "exp_failed":        grace.experiments_failed,
            "taumoeba_samples":  grace.taumoeba_samples,
            "earth_fitness":     round(grace.best_earth_strain.fitness, 3)
                                 if grace.best_earth_strain else 0.0,
            "earth_viable":      grace.earth_viable,
            "beetles_deployed":  grace.beetles_deployed,
            "beetles_tx":        grace.swarm.transmitted_count(),
            "rocky_energy":      round(rocky.energy, 1),
            "rocky_erid":        rocky.erid_progress,
            "rocky_shared":      rocky.data_shared,
            "tunnel_open":       rocky.tunnel_connected,
            "vocab_size":        rocky.translation.vocab_size(),
            "decoded_words":     rocky.translation.decoded_size(),
            "astrophage_cells":  astr_count,
        })

        if not grace.is_alive():
            break

    gs = grace.status()
    rs = rocky.status()

    return {
        "run_id":           run_id,
        "turns_survived":   history[-1]["turn"],
        "grace_alive":      grace.is_alive(),
        "final_knowledge":  gs["knowledge"],
        "final_hp":         gs["health"],
        "samples":          gs["samples"],
        "experiments":      gs["experiments"],
        "exp_failed":       gs["failures"],
        "taumoeba_samples": gs["taumoeba_samples"],
        "earth_viable":     gs["earth_viable"],
        "earth_fitness":    gs["earth_fitness"],
        "erid_viable":      gs["erid_viable"],
        "beetles_deployed": gs["beetles"],
        "beetles_tx":       gs["swarm_transmitted"],
        "rocky_shared":     rs["data_shared"],
        "rocky_repairs":    rs["repairs"],
        "erid_progress":    rs["erid_progress"],
        "vocab_size":       rs["translation"].split("|")[0].split("=")[1].strip()
                            if "vocab=" in rs["translation"] else 0,
        "decoded_words":    rs["translation"].split("|")[1].split("=")[1].strip()
                            if "decoded=" in rs["translation"] else 0,
        "history":          history,
    }


def run_all(runs: int = RUNS, turns: int = TURNS) -> list:
    results = []
    for i in range(1, runs + 1):
        print(f"  Run {i:2d}/{runs} ... ", end="", flush=True)
        result = run_single(i, turns)
        results.append(result)
        status = "ALIVE" if result["grace_alive"] else "DEAD"
        viable = "V" if result["earth_viable"] else "X"
        print(f"K:{result['final_knowledge']:5.1f}%  "
              f"Earth:{result['earth_fitness']:.2f}({viable})  "
              f"Tx:{result['beetles_tx']}/4  "
              f"Erid:{result['erid_progress']:.1f}%  "
              f"[{status}]")
    return results


def save(results: list):
    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {OUTPUT_FILE}")


def summary(results: list):
    n = len(results)
    avg_k    = sum(r["final_knowledge"]  for r in results) / n
    avg_tx   = sum(r["beetles_tx"]       for r in results) / n
    avg_erid = sum(r["erid_progress"]    for r in results) / n
    viable   = sum(1 for r in results if r["earth_viable"])
    alive    = sum(1 for r in results if r["grace_alive"])
    avg_exp  = sum(r["experiments"]      for r in results) / n
    avg_fail = sum(r["exp_failed"]       for r in results) / n

    print("\n" + "=" * 55)
    print(f"  SUMMARY — {n} runs x {TURNS} turns")
    print("=" * 55)
    print(f"  Grace survived        : {alive}/{n} runs")
    print(f"  Earth strain viable   : {viable}/{n} runs")
    print(f"  Avg knowledge score   : {avg_k:.1f}%")
    print(f"  Avg beetles tx        : {avg_tx:.1f}/4")
    print(f"  Avg Erid progress     : {avg_erid:.1f}%")
    print(f"  Avg experiments       : {avg_exp:.1f} ({avg_fail:.1f} failed)")
    print("=" * 55)


if __name__ == "__main__":
    print(f"Running {RUNS} simulations x {TURNS} turns each...\n")
    results = run_all()
    save(results)
    summary(results)
    print("\nNow run:  python analysis/dashboard.py")
