import random


GENE_NAMES = [
    "nitrogen_tolerance",
    "oxygen_resistance",
    "temperature_range",
    "astrophage_consumption",
    "reproduction_rate",
    "pressure_adaptation",
    "moisture_tolerance",
    "radiation_hardiness",
]


class TaumoebStrain:
    """
    One Taumoeba strain — its properties defined by a chromosome
    of 8 float genes, each between 0.0 and 1.0.

    Genetic Algorithm uses these chromosomes to breed better strains
    that can survive in Earth's nitrogen-rich atmosphere while still
    consuming Astrophage.
    """

    def __init__(self, chromosome=None, generation=0):
        if chromosome:
            self.chromosome = chromosome[:]
        else:
            self.chromosome = [random.random() for _ in range(len(GENE_NAMES))]
        self.generation  = generation
        self.fitness     = 0.0
        self.alive       = True
        self.strain_id   = id(self)

    def gene(self, name: str) -> float:
        idx = GENE_NAMES.index(name)
        return self.chromosome[idx]

    def mutate(self, rate: float = 0.15, strength: float = 0.2):
        for i in range(len(self.chromosome)):
            if random.random() < rate:
                delta = random.gauss(0, strength)
                self.chromosome[i] = max(0.0, min(1.0, self.chromosome[i] + delta))

    def crossover(self, other: "TaumoebStrain") -> "TaumoebStrain":
        point = random.randint(1, len(self.chromosome) - 1)
        child_chrom = self.chromosome[:point] + other.chromosome[point:]
        return TaumoebStrain(chromosome=child_chrom, generation=self.generation + 1)

    def summary(self) -> dict:
        return {GENE_NAMES[i]: round(self.chromosome[i], 3)
                for i in range(len(GENE_NAMES))}

    def __repr__(self):
        return (f"Strain(gen={self.generation} "
                f"fit={self.fitness:.3f} "
                f"N={self.chromosome[0]:.2f} "
                f"O={self.chromosome[1]:.2f})")
