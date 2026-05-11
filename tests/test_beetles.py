import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from environment.grid import Grid
from environment.hazards import AstrophageManager
from science.beetle_swarm import BeetleSwarm, Pheromone, BEETLE_NAMES


def make_swarm():
    grid  = Grid()
    swarm = BeetleSwarm(grid)
    return swarm, grid


def test_pheromone_deposit():
    p = Pheromone(20, 20)
    p.deposit(5, 5, 2.0)
    assert p.get(5, 5) == 2.0
    print("PASS: Pheromone deposits correctly")


def test_pheromone_decays():
    p = Pheromone(20, 20)
    p.deposit(5, 5, 10.0)
    p.decay()
    assert p.get(5, 5) < 10.0
    print(f"PASS: Pheromone decays ({10.0:.1f} -> {p.get(5,5):.2f})")


def test_deploy_beetle():
    swarm, _ = make_swarm()
    b = swarm.deploy(5, 5, {"test": 1})
    assert b is not None
    assert b.name == BEETLE_NAMES[0]
    assert b.deployed is True
    print(f"PASS: First beetle deployed as '{b.name}'")


def test_four_beetles_max():
    swarm, _ = make_swarm()
    for i in range(4):
        swarm.deploy(i, 0, {})
    result = swarm.deploy(5, 5, {})
    assert result is None
    print("PASS: Cannot deploy more than 4 beetles")


def test_beetle_names_in_order():
    swarm, _ = make_swarm()
    for i, name in enumerate(BEETLE_NAMES):
        b = swarm.deploy(i, 0, {})
        assert b.name == name
    print(f"PASS: Beetles named {BEETLE_NAMES}")


def test_beetle_moves_each_step():
    swarm, _ = make_swarm()
    b = swarm.deploy(10, 10, {})
    start = (b.x, b.y)
    for _ in range(10):
        swarm.step()
    assert (b.x, b.y) != start or len(b.path) > 1
    print(f"PASS: Beetle moved from {start} to ({b.x},{b.y})")


def test_beetle_loads_payload():
    swarm, _ = make_swarm()
    payload = {"knowledge": 75.0, "earth_viable": True, "strain": "test"}
    b = swarm.deploy(5, 5, payload)
    assert b.data_payload == payload
    print(f"PASS: Beetle loaded {len(payload)} payload items")


def test_beetle_transmits_near_earth():
    swarm, grid = make_swarm()
    b = swarm.deploy(1, 0, {"data": "test"})
    b._clear()
    b.x, b.y = 0, 0
    b._mark()
    for _ in range(5):
        swarm.step()
        if b.transmitted:
            break
    assert b.transmitted is True
    print("PASS: Beetle transmits when reaching Earth target")


def test_swarm_pso_convergence():
    swarm, _ = make_swarm()
    for i in range(4):
        swarm.deploy(19, 19, {"mission": "hail_mary"})
    for _ in range(80):
        swarm.step()
    tx = swarm.transmitted_count()
    assert tx >= 1
    print(f"PASS: PSO swarm convergence — {tx}/4 transmitted in 80 steps")


def test_grace_deploys_via_swarm():
    from agents.grace import Grace
    grid  = Grid()
    mgr   = AstrophageManager(grid)
    grace = Grace(1, 1, grid, mgr)
    grace.energy = 100
    grace.knowledge.beliefs = {k: 0.8 for k in grace.knowledge.beliefs}
    result = grace.deploy_beetle()
    assert result is True
    assert grace.beetles_deployed == 1
    assert len(grace.swarm.beetles) == 1
    print(f"PASS: Grace deploys beetle via swarm — '{grace.swarm.beetles[0].name}'")


if __name__ == "__main__":
    test_pheromone_deposit()
    test_pheromone_decays()
    test_deploy_beetle()
    test_four_beetles_max()
    test_beetle_names_in_order()
    test_beetle_moves_each_step()
    test_beetle_loads_payload()
    test_beetle_transmits_near_earth()
    test_swarm_pso_convergence()
    test_grace_deploys_via_swarm()
    print("\nAll Part E tests passed.")
