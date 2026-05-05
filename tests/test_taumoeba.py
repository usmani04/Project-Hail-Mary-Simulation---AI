import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from science.taumoeba import TaumoebStrain, GENE_NAMES
from science.genetic_algorithm import run_ga, fitness, evolve_generation


def test_strain_has_8_genes():
    s = TaumoebStrain()
    assert len(s.chromosome) == 8 == len(GENE_NAMES)
    print("PASS: Strain has 8 genes")


def test_genes_in_range():
    s = TaumoebStrain()
    assert all(0.0 <= g <= 1.0 for g in s.chromosome)
    print("PASS: All genes in [0,1]")


def test_mutation_changes_chromosome():
    s = TaumoebStrain()
    original = s.chromosome[:]
    for _ in range(20):
        s.mutate(rate=1.0, strength=0.5)
    assert s.chromosome != original
    assert all(0.0 <= g <= 1.0 for g in s.chromosome)
    print("PASS: Mutation changes genes and stays in range")


def test_crossover_produces_child():
    a = TaumoebStrain()
    b = TaumoebStrain()
    child = a.crossover(b)
    assert len(child.chromosome) == 8
    assert child.generation == a.generation + 1
    print(f"PASS: Crossover produces child gen={child.generation}")


def test_fitness_earth_range():
    s = TaumoebStrain()
    f = fitness(s, target="earth")
    assert 0.0 <= f <= 1.0
    print(f"PASS: Earth fitness in range ({f:.3f})")


def test_fitness_erid_range():
    s = TaumoebStrain()
    f = fitness(s, target="erid")
    assert 0.0 <= f <= 1.0
    print(f"PASS: Erid fitness in range ({f:.3f})")


def test_optimal_earth_strain():
    perfect = TaumoebStrain(chromosome=[
        1.0, 1.0, 1.0, 1.0, 0.6, 1.0, 1.0, 1.0
    ])
    f = fitness(perfect, "earth")
    assert f > 0.85
    print(f"PASS: Optimal earth strain has high fitness ({f:.3f})")


def test_ga_improves_fitness():
    result = run_ga(generations=20, population_size=10, target="earth")
    history = result["history"]
    first_best = history[0]["best_fitness"]
    last_best  = history[-1]["best_fitness"]
    assert last_best >= first_best
    print(f"PASS: GA improves fitness ({first_best:.3f} -> {last_best:.3f})")


def test_ga_produces_viable_strain():
    result = run_ga(generations=30, population_size=15, target="earth")
    assert result["best_fitness"] > 0.5
    print(f"PASS: GA viable={result['viable']} fitness={result['best_fitness']:.3f}")


def test_ga_erid_target():
    result = run_ga(generations=20, population_size=10, target="erid")
    assert result["target"] == "erid"
    assert result["best_fitness"] > 0.0
    print(f"PASS: GA erid fitness={result['best_fitness']:.3f}")


def test_grace_breeds_taumoeba():
    from environment.grid import Grid
    from environment.hazards import AstrophageManager
    from agents.grace import Grace

    grid  = Grid()
    mgr   = AstrophageManager(grid)
    grace = Grace(1, 1, grid, mgr)

    grace.taumoeba_samples = 3
    grace.energy = 100
    grace.knowledge.beliefs = {k: 0.8 for k in grace.knowledge.beliefs}

    result = grace.breed_taumoeba(target="earth")
    assert result is not None
    assert grace.breeding_attempts == 1
    print(f"PASS: Grace breeds Taumoeba fitness={result['best_fitness']:.3f}")


def test_grace_needs_samples_to_breed():
    from environment.grid import Grid
    from environment.hazards import AstrophageManager
    from agents.grace import Grace

    grid  = Grid()
    mgr   = AstrophageManager(grid)
    grace = Grace(1, 1, grid, mgr)
    grace.taumoeba_samples = 0

    result = grace.breed_taumoeba()
    assert result is None
    print("PASS: Grace cannot breed without Taumoeba samples")


if __name__ == "__main__":
    test_strain_has_8_genes()
    test_genes_in_range()
    test_mutation_changes_chromosome()
    test_crossover_produces_child()
    test_fitness_earth_range()
    test_fitness_erid_range()
    test_optimal_earth_strain()
    test_ga_improves_fitness()
    test_ga_produces_viable_strain()
    test_ga_erid_target()
    test_grace_breeds_taumoeba()
    test_grace_needs_samples_to_breed()
    print("\nAll Part D tests passed.")
