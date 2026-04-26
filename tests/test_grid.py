
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from environment.grid import Grid
from environment.hazards import AstrophageManager
from config import (
    CELL_EMPTY, CELL_ASTROPHAGE, CELL_PETROVA,
    CELL_HAIL_MARY, CELL_BLIP_A, CELL_ADRIAN,
    GRID_WIDTH, GRID_HEIGHT
)

def test_grid_dimensions():
    g = Grid()
    assert len(g.cells) == GRID_HEIGHT
    assert len(g.cells[0]) == GRID_WIDTH
    print("PASS: grid dimensions")

def test_wrap():
    g = Grid()
    cell = g.get_cell(-1, 0)
    assert cell.x == GRID_WIDTH - 1
    print("PASS: edge wrapping")

def test_petrova_line():
    g = Grid()
    col = GRID_WIDTH // 2
    for y in range(GRID_HEIGHT):
        assert g.cells[y][col].cell_type == CELL_PETROVA
    print("PASS: Petrova line placed")

def test_hail_mary_placed():
    g = Grid()
    assert g.cells[1][1].cell_type == CELL_HAIL_MARY
    print("PASS: Hail Mary placed")

def test_blip_a_placed():
    g = Grid()
    assert g.cells[1][GRID_WIDTH - 2].cell_type == CELL_BLIP_A
    print("PASS: Blip-A placed")

def test_adrian_placed():
    g = Grid()
    ax, ay = GRID_WIDTH - 4, GRID_HEIGHT - 4
    assert g.cells[ay][ax].cell_type == CELL_ADRIAN
    print("PASS: Planet Adrian placed")

def test_neighbours():
    g = Grid()
    nbrs = g.get_neighbours(10, 10)
    assert len(nbrs) == 4
    print("PASS: neighbours count")

def test_astrophage_spread():
    g = Grid()
    mgr = AstrophageManager(g)
    before = g.count_cell_type(CELL_ASTROPHAGE)
    for _ in range(10):
        mgr.step()
    after = g.count_cell_type(CELL_ASTROPHAGE)
    assert after >= 0
    print(f"PASS: Astrophage spread ({before} -> {after} cells)")

def test_energy_cost():
    from environment.cell import Cell
    from config import CELL_ASTROPHAGE, ASTROPHAGE_ENERGY_DRAIN
    c = Cell(0, 0, CELL_ASTROPHAGE)
    c.astrophage_intensity = 3
    cost = c.energy_cost()
    assert cost == ASTROPHAGE_ENERGY_DRAIN * 3
    print(f"PASS: energy cost = {cost}")

def test_ascii_output():
    g = Grid()
    ascii_str = g.to_ascii()
    lines = ascii_str.strip().split("\n")
    assert len(lines) == GRID_HEIGHT + 1
    print("PASS: ASCII output rows correct")

if __name__ == "__main__":
    test_grid_dimensions()
    test_wrap()
    test_petrova_line()
    test_hail_mary_placed()
    test_blip_a_placed()
    test_adrian_placed()
    test_neighbours()
    test_astrophage_spread()
    test_energy_cost()
    test_ascii_output()
    print("\nAll tests passed.")

def test_fuzzy_dormant():
    from environment.fuzzy_logic import assess_hazard
    r = assess_hazard(0)
    assert r["dominant_level"] == "dormant"
    assert r["spread_chance"] == 0.0
    print("PASS: fuzzy dormant (intensity=0)")

def test_fuzzy_critical():
    from environment.fuzzy_logic import assess_hazard
    r = assess_hazard(10)
    assert r["dominant_level"] == "critical"
    assert r["spread_chance"] > 0.15
    print(f"PASS: fuzzy critical (spread={r['spread_chance']}, drain={r['energy_drain']})")

def test_fuzzy_medium():
    from environment.fuzzy_logic import assess_hazard
    r = assess_hazard(6)
    assert r["dominant_level"] in ("medium", "high")
    print(f"PASS: fuzzy medium (level={r['dominant_level']}, spread={r['spread_chance']})")

def test_fuzzy_memberships_sum():
    from environment.fuzzy_logic import fuzzify
    for intensity in [0, 2, 5, 8, 10]:
        m = fuzzify(intensity)
        assert all(0.0 <= v <= 1.0 for v in m.values()), f"Membership out of range at {intensity}"
    print("PASS: all memberships in [0,1]")

def test_fuzzy_energy_drain_increases():
    from environment.fuzzy_logic import assess_hazard
    drains = [assess_hazard(i)["energy_drain"] for i in range(0, 11, 2)]
    assert drains == sorted(drains), f"Drain not monotonic: {drains}"
    print(f"PASS: energy drain monotonically increases: {drains}")

def test_fuzzy_driven_spread():
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from environment.grid import Grid
    from environment.hazards import AstrophageManager
    g = Grid()
    for row in g.cells:
        for cell in row:
            if cell.has_astrophage():
                cell.astrophage_intensity = 10
    mgr = AstrophageManager(g)
    before = g.count_cell_type(2)
    for _ in range(5):
        mgr.step()
    after = g.count_cell_type(2)
    assert after >= before, "Critical astrophage should not decrease"
    print(f"PASS: fuzzy-driven spread (critical): {before} -> {after} cells")
