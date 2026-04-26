
import random
from environment.fuzzy_logic import assess_hazard
from config import (
    CELL_ASTROPHAGE, CELL_EMPTY,
    ASTROPHAGE_INTENSITY_MIN, ASTROPHAGE_INTENSITY_MAX
)

class AstrophageManager:
    """
    Manages Astrophage spread and intensity across the grid.

    Fuzzy Logic Integration:
    ─────────────────────────────────────────────────────────────
    Each Astrophage cell's intensity (1-10) is passed through a
    Fuzzy Logic engine (fuzzy_logic.py) that classifies it as:

        DORMANT -> LOW -> MEDIUM -> HIGH -> CRITICAL

    The engine returns:
      * spread_chance  -- probability this cell infects a neighbour
      * energy_drain   -- crisp energy cost for agents in the cell

    This replaces the hardcoded ASTROPHAGE_SPREAD_CHANCE constant,
    making hazard behaviour continuous and non-linear.
    ─────────────────────────────────────────────────────────────
    """

    def __init__(self, grid):
        self.grid = grid
        self._spread_log = []

    def spread(self):
        new_infections = []

        for y in range(self.grid.height):
            for x in range(self.grid.width):
                cell = self.grid.get_cell(x, y)
                if not cell.has_astrophage():
                    continue

                hazard = assess_hazard(cell.astrophage_intensity)
                spread_chance = hazard["spread_chance"]
                level         = hazard["dominant_level"]

                for nx, ny in self.grid.get_neighbours(x, y):
                    ncell = self.grid.get_cell(nx, ny)
                    if ncell.cell_type == CELL_EMPTY:
                        if random.random() < spread_chance:
                            new_infections.append((nx, ny, level))

        for (x, y, level) in new_infections:
            cell = self.grid.get_cell(x, y)
            cell.set_type(CELL_ASTROPHAGE)
            cell.astrophage_intensity = ASTROPHAGE_INTENSITY_MIN
            self._spread_log.append(f"Cell ({x},{y}) infected [{level}]")

    def fluctuate_intensity(self):
        growth_map = {
            "dormant":  (0, 1),
            "low":      (0, 0, 1),
            "medium":   (-1, 0, 1),
            "high":     (0, 1, 1),
            "critical": (1, 1, 2),
        }
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                cell = self.grid.get_cell(x, y)
                if not cell.has_astrophage():
                    continue
                hazard = assess_hazard(cell.astrophage_intensity)
                level  = hazard["dominant_level"]
                delta  = random.choice(growth_map.get(level, (0,)))
                cell.astrophage_intensity = max(
                    ASTROPHAGE_INTENSITY_MIN,
                    min(ASTROPHAGE_INTENSITY_MAX, cell.astrophage_intensity + delta)
                )

    def fuzzy_energy_drain(self, x, y):
        cell = self.grid.get_cell(x, y)
        if not cell.has_astrophage():
            return 0.0
        return assess_hazard(cell.astrophage_intensity)["energy_drain"]

    def step(self):
        self.spread()
        self.fluctuate_intensity()

    def get_spread_log(self, last_n=5):
        return self._spread_log[-last_n:]
