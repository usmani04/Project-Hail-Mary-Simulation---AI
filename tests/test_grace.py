import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from environment.grid import Grid
from environment.hazards import AstrophageManager
from agents.grace import Grace
from agents.bayesian_knowledge import BayesianKnowledge


def make_grace():
    grid = Grid()
    mgr = AstrophageManager(grid)
    return Grace(1, 1, grid, mgr), grid, mgr


def test_grace_starts_alive():
    grace, _, _ = make_grace()
    assert grace.is_alive()
    print("PASS: Grace starts alive")


def test_grace_move_costs_energy():
    grace, _, _ = make_grace()
    before = grace.energy
    grace.move(1, 0)
    assert grace.energy < before
    print("PASS: Moving costs energy")


def test_grace_rest_restores_energy():
    grace, _, _ = make_grace()
    grace.energy = 20
    grace.rest()
    assert grace.energy > 20
    print("PASS: Rest restores energy")


def test_grace_collect_needs_sample_cell():
    grace, grid, mgr = make_grace()
    from config import CELL_EMPTY
    grace.x, grace.y = 0, 0
    grid.get_cell(0, 0).set_type(CELL_EMPTY)
    result = grace.collect_sample()
    assert result is False
    print("PASS: Cannot collect from empty cell")


def test_grace_experiment_needs_samples():
    grace, _, _ = make_grace()
    grace.samples_collected = 0
    result = grace.run_experiment()
    assert result is False
    print("PASS: Cannot experiment without samples")


def test_grace_experiment_updates_knowledge():
    grace, _, _ = make_grace()
    grace.samples_collected = 3
    grace.energy = 100
    before = grace.knowledge.knowledge_score()
    for _ in range(10):
        grace.run_experiment()
    after = grace.knowledge.knowledge_score()
    assert after != before
    print(f"PASS: Knowledge changed after experiments ({before:.2f} -> {after:.2f})")


def test_beetle_deploy():
    grace, _, _ = make_grace()
    grace.energy = 100
    result = grace.deploy_beetle()
    assert result is True
    assert grace.beetles_deployed == 1
    print("PASS: Beetle deployed successfully")


def test_max_four_beetles():
    grace, _, _ = make_grace()
    grace.energy = 100
    for _ in range(4):
        grace.deploy_beetle()
        grace.energy = 100
    result = grace.deploy_beetle()
    assert result is False
    print("PASS: Cannot deploy more than 4 beetles")


def test_bayesian_update_increases_belief():
    kb = BayesianKnowledge()
    before = kb.beliefs["astrophage_understood"]
    kb.update("experiment_success")
    after = kb.beliefs["astrophage_understood"]
    assert after > before
    print(f"PASS: Bayesian update raised belief ({before:.3f} -> {after:.3f})")


def test_bayesian_failure_lowers_belief():
    kb = BayesianKnowledge()
    kb.beliefs["astrophage_understood"] = 0.8
    kb.update("experiment_failure")
    after = kb.beliefs["astrophage_understood"]
    assert after < 0.8
    print(f"PASS: Bayesian failure lowers belief (-> {after:.3f})")


def test_knowledge_score_range():
    kb = BayesianKnowledge()
    score = kb.knowledge_score()
    assert 0 <= score <= 100
    print(f"PASS: Knowledge score in valid range ({score}%)")


def test_flashback_triggered():
    grace, _, _ = make_grace()
    grace.knowledge.beliefs = {k: 0.9 for k in grace.knowledge.beliefs}
    grace.move(1, 0)
    assert grace.memory_recovered is True
    print("PASS: Flashback triggered at high knowledge")


if __name__ == "__main__":
    test_grace_starts_alive()
    test_grace_move_costs_energy()
    test_grace_rest_restores_energy()
    test_grace_collect_needs_sample_cell()
    test_grace_experiment_needs_samples()
    test_grace_experiment_updates_knowledge()
    test_beetle_deploy()
    test_max_four_beetles()
    test_bayesian_update_increases_belief()
    test_bayesian_failure_lowers_belief()
    test_knowledge_score_range()
    test_flashback_triggered()
    print("\nAll Part B tests passed.")
