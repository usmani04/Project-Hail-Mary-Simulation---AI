import time
from environment.grid import Grid
from environment.hazards import AstrophageManager
from agents.grace import Grace
from visualization.display import GridDisplay
from config import DEFAULT_TURNS, GRACE_START_X, GRACE_START_Y


def run_simulation(turns: int = DEFAULT_TURNS, visualize: bool = True, delay: float = 0.2):
    print("=" * 50)
    print("  PROJECT HAIL MARY SIMULATION")
    print("  Part B: Dr Ryland Grace Agent")
    print("=" * 50)

    grid = Grid()
    hazard_mgr = AstrophageManager(grid)
    grace = Grace(GRACE_START_X, GRACE_START_Y, grid, hazard_mgr)

    display = None
    if visualize:
        try:
            display = GridDisplay(grid)
        except Exception as e:
            print(f"Visualizer unavailable: {e}")
            visualize = False

    for turn in range(1, turns + 1):
        if not grace.is_alive():
            print(f"\nGrace has died on turn {turn}. Mission failed.")
            break

        action = grace.decide_action()
        hazard_mgr.step()

        status = grace.status()

        if turn % 10 == 0:
            print(f"Turn {turn:3d} | Action: {action:10s} | "
                  f"HP:{status['health']:3d} EN:{status['energy']:5.1f} | "
                  f"Knowledge:{status['knowledge']:5.1f}% | "
                  f"Samples:{status['samples']} Exp:{status['experiments']} "
                  f"Beetles:{status['beetles']}")

        if visualize and display:
            info = {
                "HP": status["health"],
                "EN": f"{status['energy']:.0f}",
                "K%": f"{status['knowledge']:.1f}",
            }
            display.render(turn=turn, info=info)
            time.sleep(delay)

        if grace.flashback_log:
            for fb in grace.flashback_log:
                print(f"\n  *** {fb} ***\n")
            grace.flashback_log.clear()

    print("\n--- Final Status ---")
    s = grace.status()
    print(f"Knowledge Score : {s['knowledge']}%")
    print(f"Samples Collected: {s['samples']}")
    print(f"Experiments Run : {s['experiments']} ({s['failures']} failed)")
    print(f"Beetle Probes   : {s['beetles']}/4 deployed")
    print(f"Beliefs         : {s['beliefs']}")

    if display:
        display.save("simulation_final.png")
        input("\nPress ENTER to close...")
        display.close()


if __name__ == "__main__":
    run_simulation(turns=100, visualize=True, delay=0.15)
