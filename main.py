import time
from environment.grid import Grid
from environment.hazards import AstrophageManager
from agents.grace import Grace
from agents.rocky import Rocky
from visualization.display import GridDisplay
from config import DEFAULT_TURNS, GRACE_START_X, GRACE_START_Y, ROCKY_START_X, ROCKY_START_Y


def run_simulation(turns=DEFAULT_TURNS, visualize=True, delay=0.15):
    print("=" * 60)
    print("  PROJECT HAIL MARY SIMULATION")
    print("  Part C: Grace + Rocky Multi-Agent")
    print("=" * 60)

    grid = Grid()
    hazard_mgr = AstrophageManager(grid)
    grace = Grace(GRACE_START_X, GRACE_START_Y, grid, hazard_mgr)
    rocky = Rocky(ROCKY_START_X, ROCKY_START_Y, grid, hazard_mgr)
    rocky.grace_ref = grace

    display = None
    if visualize:
        try:
            display = GridDisplay(grid)
        except Exception as e:
            print(f"Visualizer unavailable: {e}")
            visualize = False

    for turn in range(1, turns + 1):
        grace_action = grace.decide_action()
        rocky_action = rocky.decide_action()

        if not grace.is_alive():
            print(f"\nGrace died on turn {turn}. Mission failed.")
            break
        if not rocky.is_alive():
            print(f"\nRocky died on turn {turn}. Lost alien ally.")

        hazard_mgr.step()

<<<<<<< HEAD
=======
        active_beetle_positions = {(b.x, b.y) for b in grace.swarm.beetles if b.deployed and not b.transmitted}
        for row in grid.cells:
            for cell in row:
                if cell.cell_type == 9 and (cell.x != grace.x or cell.y != grace.y):
                    cell.set_type(grace._under_type)
                if cell.cell_type == 10 and (cell.x != rocky.x or cell.y != rocky.y):
                    cell.set_type(rocky._under_type)
                if cell.cell_type == 5 and (cell.x, cell.y) not in active_beetle_positions:
                    cell.set_type(0)

>>>>>>> ea58054867e1113558136a38e37341feaf69fb9b
        grid.get_cell(grace.x, grace.y).set_type(9)
        grid.get_cell(rocky.x, rocky.y).set_type(10)

        if grace.flashback_log:
            for fb in grace.flashback_log:
                print(f"\n  *** {fb} ***\n")
            grace.flashback_log.clear()

        if rocky._chord_log:
            for chord in rocky._chord_log[-1:]:
                print(f"  ~ {chord}")
            rocky._chord_log.clear()

        if turn % 10 == 0:
            gs = grace.status()
            rs = rocky.status()
            tunnel_str = "OPEN" if rs["tunnel"] else f"building({rs['tunnel_progress']}/15)"
            print(
                f"Turn {turn:3d} | "
                f"G: HP:{gs['health']:3d} EN:{gs['energy']:5.1f} K:{gs['knowledge']:4.1f}% "
<<<<<<< HEAD
                f"S:{gs['samples']} Exp:{gs['experiments']} B:{gs['beetles']} | "
=======
                f"S:{gs['samples']} Exp:{gs['experiments']} B:{gs['beetles']} "
                f"TauS:{gs['taumoeba_samples']} Earth:{gs['earth_fitness']:.2f}({'V' if gs['earth_viable'] else 'X'}) Tx:{gs['swarm_transmitted']}/4 | "
>>>>>>> ea58054867e1113558136a38e37341feaf69fb9b
                f"R: HP:{rs['health']:3d} EN:{rs['energy']:5.1f} "
                f"Erid:{rs['erid_progress']:4.1f}% "
                f"tunnel:{tunnel_str} shared:{rs['data_shared']}"
            )

        if visualize and display:
            rs = rocky.status()

            display.render(turn=turn, grace=grace, rocky=rocky)
            time.sleep(delay)

    print("\n--- Final Status ---")
    gs = grace.status()
    rs = rocky.status()
    print(f"Grace  | K:{gs['knowledge']}% | S:{gs['samples']} | Exp:{gs['experiments']} | Beetles:{gs['beetles']}/4")
    print(f"Rocky  | Erid:{rs['erid_progress']}% | Shared:{rs['data_shared']} | Repairs:{rs['repairs']} | Fuel given:{rs['energy_transferred']}")
    print(f"Tunnel | {rs['translation']}")
    print(f"Beliefs: {gs['beliefs']}")
    print(f"Erid K: {rocky.erid_knowledge}")

<<<<<<< HEAD
=======
    gs = grace.status()
    for bs in grace.swarm.status():
        print(f"  Beetle {bs['name']}: transmitted={bs['transmitted']} turns={bs['turns']} path={bs['path_len']} payload={bs['payload']}")

>>>>>>> ea58054867e1113558136a38e37341feaf69fb9b
    if display:
        display.save("simulation_final.png")
        input("\nPress ENTER to close...")
        display.close()


if __name__ == "__main__":
    run_simulation(turns=100, visualize=True, delay=0.15)
