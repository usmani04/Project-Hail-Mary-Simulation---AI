from config import (
    CELL_EMPTY, CELL_ASTROPHAGE, CELL_PETROVA,
    ASTROPHAGE_ENERGY_DRAIN, PETROVA_ENERGY_DRAIN, RADIATION_HEALTH_DRAIN,
    CELL_RADIATION, CELL_DEBRIS, CELL_LABELS, CELL_COLORS,
    ASTROPHAGE_INTENSITY_MIN, ASTROPHAGE_INTENSITY_MAX
)


class Cell:

    def __init__(self, x: int, y: int, cell_type: int = CELL_EMPTY):
        self.x = x
        self.y = y
        self.cell_type = cell_type
        self.astrophage_intensity = 0
        self.contents = []

    def is_passable(self) -> bool:
        return True

    def energy_cost(self) -> int:
        cost = 0
        if self.cell_type == CELL_ASTROPHAGE:
            cost += ASTROPHAGE_ENERGY_DRAIN * max(1, self.astrophage_intensity)
        elif self.cell_type == CELL_PETROVA:
            cost += PETROVA_ENERGY_DRAIN * max(1, self.astrophage_intensity)
        elif self.cell_type == CELL_DEBRIS:
            cost += 3
        return cost

    def health_cost(self) -> int:
        if self.cell_type == CELL_RADIATION:
            return RADIATION_HEALTH_DRAIN
        return 0

    def has_astrophage(self) -> bool:
        return self.cell_type in (CELL_ASTROPHAGE, CELL_PETROVA)

    def set_type(self, cell_type: int):
        self.cell_type = cell_type

    def label(self) -> str:
        return CELL_LABELS.get(self.cell_type, "?")

    def color(self) -> str:
        return CELL_COLORS.get(self.cell_type, "#ffffff")

    def __repr__(self):
        return f"Cell({self.x},{self.y}, type={self.cell_type}, intensity={self.astrophage_intensity})"
