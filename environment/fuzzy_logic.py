
def _trapezoid(x: float, a: float, b: float, c: float, d: float) -> float:
    """
    Trapezoidal membership function.
    Rises from a->b, flat b->c, falls c->d.
    """
    if x <= a or x >= d:
        return 0.0
    if b <= x <= c:
        return 1.0
    if a < x < b:
        return (x - a) / (b - a)
    if c < x < d:
        return (d - x) / (d - c)
    return 0.0

def _triangle(x: float, a: float, b: float, c: float) -> float:
    """Triangular membership function. Peaks at b."""
    if x <= a or x >= c:
        return 0.0
    if x == b:
        return 1.0
    if a < x < b:
        return (x - a) / (b - a)
    if b < x < c:
        return (c - x) / (c - b)
    return 0.0

def fuzz_dormant(intensity: float) -> float:
    """Dormant: very low intensity (0-2)"""
    return _trapezoid(intensity, -1, 0, 1, 3)

def fuzz_low(intensity: float) -> float:
    """Low: intensity around 2-4"""
    return _triangle(intensity, 1, 3, 5)

def fuzz_medium(intensity: float) -> float:
    """Medium: intensity around 4-7"""
    return _triangle(intensity, 4, 6, 8)

def fuzz_high(intensity: float) -> float:
    """High: intensity 7-9"""
    return _triangle(intensity, 6, 8, 10)

def fuzz_critical(intensity: float) -> float:
    """Critical: maximum intensity (9-10)"""
    return _trapezoid(intensity, 8, 9, 10, 11)

RULE_OUTPUTS = {
    "dormant":  (0.00, 0),
    "low":      (0.01, 4),
    "medium":   (0.04, 9),
    "high":     (0.08, 16),
    "critical": (0.14, 25),
}

def fuzzify(intensity: float) -> dict:
    """Return membership degrees for all linguistic levels."""
    return {
        "dormant":  fuzz_dormant(intensity),
        "low":      fuzz_low(intensity),
        "medium":   fuzz_medium(intensity),
        "high":     fuzz_high(intensity),
        "critical": fuzz_critical(intensity),
    }

def defuzzify(memberships: dict) -> tuple[float, float]:
    """
    Mamdani-style defuzzification using weighted average.
    Returns (spread_chance, energy_drain) as crisp values.
    """
    total_weight = sum(memberships.values())
    if total_weight == 0:
        return 0.0, 0

    spread_num = sum(
        memberships[level] * RULE_OUTPUTS[level][0]
        for level in memberships
    )
    drain_num = sum(
        memberships[level] * RULE_OUTPUTS[level][1]
        for level in memberships
    )

    spread_chance = spread_num / total_weight
    energy_drain  = drain_num  / total_weight
    return spread_chance, energy_drain

def assess_hazard(intensity: float) -> dict:
    """
    Full fuzzy pipeline for one cell's Astrophage intensity.

    Returns:
        {
          "memberships":    dict of level -> degree,
          "dominant_level": str  (highest membership level),
          "spread_chance":  float (0.0-0.30),
          "energy_drain":   float (crisp kcal/turn equivalent),
        }
    """
    memberships = fuzzify(intensity)
    spread_chance, energy_drain = defuzzify(memberships)
    dominant = max(memberships, key=memberships.get)

    return {
        "memberships":    memberships,
        "dominant_level": dominant,
        "spread_chance":  round(spread_chance, 4),
        "energy_drain":   round(energy_drain, 2),
    }

def hazard_label(intensity: float) -> str:
    """Quick label for display purposes."""
    result = assess_hazard(intensity)
    return result["dominant_level"].upper()
