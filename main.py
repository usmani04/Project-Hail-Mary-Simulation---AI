
import time
from environment.grid import Grid
from environment.hazards import AstrophageManager
from visualization.display import GridDisplay
from config import DEFAULT_TURNS

def run_simulation(turns: int = DEFAULT_TURNS, visualize: bool = True, delay: float = 0.3):
    print("=" * 50)
    print("  PROJECT HAIL MARY SIMULATION")
    print("  Part (a): Environment Grid")
    print("=" * 50)

    grid = Grid()
    hazard_mgr = AstrophageManager(grid)

    print(f"\nGrid initialised ({grid.width}x{grid.height}), wrapping: ON")
    print(grid.to_ascii())

    display = None
    if visualize:
        try:
            display = GridDisplay(grid)
        except Exception as e:
            print(f"[Warning] Visualizer unavailable: {e}")
            visualize = False

    for turn in range(1, turns + 1):
        hazard_mgr.step()

        astr_count = grid.count_cell_type(2)
        info = {"turn": turn, "astrophage_cells": astr_count}

        if visualize and display:
            display.render(turn=turn, info=info)
            time.sleep(delay)

        if turn % 20 == 0:
            print(f"Turn {turn:4d} | Astrophage cells: {astr_count}")

    print("\nSimulation complete.")
    if display:
        display.save("grid_final.png")
        input("Press ENTER to close...")
        display.close()

if __name__ == "__main__":
    run_simulation(turns=100, visualize=True, delay=0.2)
