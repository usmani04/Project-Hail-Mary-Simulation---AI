import random
from science.taumoeba import TaumoebStrain, GENE_NAMES


POPULATION_SIZE  = 20
ELITE_COUNT      = 4
MUTATION_RATE    = 0.15
MUTATION_STRENGTH = 0.2
MAX_GENERATIONS  = 50


def fitness(strain: TaumoebStrain, target: str = "earth") -> float:
    """
    Evaluate how well a strain survives in the target environment.

    Earth target:
      - High nitrogen_tolerance    (Earth is 78% nitrogen)
      - High oxygen_resistance     (Earth is 21% oxygen — toxic to Taumoeba)
      - High astrophage_consumption (must still eat Astrophage)
      - Moderate reproduction_rate (too fast = unstable)

    Erid target:
      - High pressure_adaptation
      - High moisture_tolerance
      - High astrophage_consumption
    """
    c = strain.chromosome
    n  = GENE_NAMES

    def g(name):
        return c[n.index(name)]

    if target == "earth":
        score = (
            g("nitrogen_tolerance")    * 0.25 +
            g("oxygen_resistance")     * 0.25 +
            g("astrophage_consumption")* 0.25 +
            g("temperature_range")     * 0.10 +
            (1 - abs(g("reproduction_rate") - 0.6)) * 0.10 +
            g("radiation_hardiness")   * 0.05
        )
    elif target == "erid":
        score = (
            g("pressure_adaptation")   * 0.30 +
            g("moisture_tolerance")    * 0.25 +
            g("astrophage_consumption")* 0.25 +
            (1 - abs(g("reproduction_rate") - 0.5)) * 0.10 +
            g("radiation_hardiness")   * 0.10
        )
    else:
        score = sum(c) / len(c)

    strain.fitness = round(score, 4)
    return strain.fitness


def select_parents(population: list, k: int = 3) -> TaumoebStrain:
    """Tournament selection — pick best of k random strains."""
    tournament = random.sample(population, min(k, len(population)))
    return max(tournament, key=lambda s: s.fitness)


def evolve_generation(population: list, target: str = "earth") -> list:
    """
    One GA generation:
    1. Evaluate fitness of all strains
    2. Keep elite survivors
    3. Breed new children via crossover
    4. Mutate non-elite children
    5. Return new population
    """
    for strain in population:
        fitness(strain, target)

    population.sort(key=lambda s: s.fitness, reverse=True)

    elites   = population[:ELITE_COUNT]
    children = []

    while len(children) < POPULATION_SIZE - ELITE_COUNT:
        parent_a = select_parents(population)
        parent_b = select_parents(population)
        child    = parent_a.crossover(parent_b)
        child.mutate(MUTATION_RATE, MUTATION_STRENGTH)
        fitness(child, target)
        children.append(child)

    return elites + children


def run_ga(generations: int = MAX_GENERATIONS,
           population_size: int = POPULATION_SIZE,
           target: str = "earth",
           knowledge_bonus: float = 0.0) -> dict:
    """
    Full GA run.
    knowledge_bonus: Grace's knowledge score (0-1) reduces mutation rate —
    more scientific understanding = more precise breeding.
    """
    adjusted_mutation = max(0.05, MUTATION_RATE - knowledge_bonus * 0.1)

    population = [TaumoebStrain() for _ in range(population_size)]
    for s in population:
        fitness(s, target)

    history = []

    for gen in range(generations):
        population = evolve_generation(population, target)
        best  = population[0]
        avg   = sum(s.fitness for s in population) / len(population)
        history.append({
            "generation": gen + 1,
            "best_fitness": round(best.fitness, 4),
            "avg_fitness":  round(avg, 4),
            "best_strain":  best,
        })

    best_strain = population[0]
    fitness(best_strain, target)

    return {
        "best_strain":   best_strain,
        "best_fitness":  best_strain.fitness,
        "generations":   generations,
        "history":       history,
        "target":        target,
        "viable":        best_strain.fitness >= 0.70,
    }
