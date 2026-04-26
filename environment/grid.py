
import random
from environment.cell import Cell
from config import (
    GRID_WIDTH, GRID_HEIGHT, WRAP_EDGES,
    CELL_EMPTY, CELL_ADRIAN, CELL_ASTROPHAGE, CELL_HAIL_MARY,
    CELL_BLIP_A, CELL_RADIATION, CELL_DEBRIS, CELL_PETROVA,
    ASTROPHAGE_INTENSITY_MIN, ASTROPHAGE_INTENSITY_MAX
)

class Grid:
    """
    20x20 toroidal 2D grid representing space near Tau Ceti.
    Wraps at edges to simulate open space.
    """

    def __init__(self, width: int = GRID_WIDTH, height: int = GRID_HEIGHT):
        self.width = width
        self.height = height
        self.cells: list[list[Cell]] = [
            [Cell(x, y) for x in range(width)]
            for y in range(height)
        ]
        self._place_features()

    def _place_features(self):
        """Place all fixed and randomised features on the grid."""
        self._place_petrova_line()
        self._place_planet_adrian()
        self._place_hail_mary()
        self._place_blip_a()
        self._place_astrophage_clusters()
        self._place_hazards()

    def _place_petrova_line(self):
        """Dense Astrophage column running vertically through the grid."""
        col = self.width // 2
        for y in range(self.height):
            cell = self.cells[y][col]
            cell.set_type(CELL_PETROVA)
            cell.astrophage_intensity = random.randint(7, ASTROPHAGE_INTENSITY_MAX)

    def _place_planet_adrian(self):
        """Adrian is a 2x2 cluster in the lower-right quadrant."""
        ax, ay = self.width - 4, self.height - 4
        for dy in range(2):
            for dx in range(2):
                self.cells[ay + dy][ax + dx].set_type(CELL_ADRIAN)

    def _place_hail_mary(self):
        """Hail Mary starts top-left."""
        self.hail_mary_pos = (1, 1)
        self.cells[1][1].set_type(CELL_HAIL_MARY)

    def _place_blip_a(self):
        """Blip-A (Rocky's ship) starts top-right."""
        self.blip_a_pos = (self.width - 2, 1)
        self.cells[1][self.width - 2].set_type(CELL_BLIP_A)

    def _place_astrophage_clusters(self):
        """Scatter 4-6 small Astrophage clusters across the grid."""
        cluster_count = random.randint(4, 6)
        placed = 0
        attempts = 0
        while placed < cluster_count and attempts < 200:
            attempts += 1
            cx = random.randint(0, self.width - 1)
            cy = random.randint(0, self.height - 1)
            cell = self.cells[cy][cx]
            if cell.cell_type == CELL_EMPTY:
                cell.set_type(CELL_ASTROPHAGE)
                cell.astrophage_intensity = random.randint(
                    ASTROPHAGE_INTENSITY_MIN, 5
                )
                for _ in range(random.randint(1, 3)):
                    nx = (cx + random.randint(-2, 2)) % self.width
                    ny = (cy + random.randint(-2, 2)) % self.height
                    nc = self.cells[ny][nx]
                    if nc.cell_type == CELL_EMPTY:
                        nc.set_type(CELL_ASTROPHAGE)
                        nc.astrophage_intensity = random.randint(
                            ASTROPHAGE_INTENSITY_MIN, 4
                        )
                placed += 1

    def _place_hazards(self):
        """Scatter radiation zones and debris fields."""
        for _ in range(random.randint(3, 5)):
            rx, ry = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
            if self.cells[ry][rx].cell_type == CELL_EMPTY:
                self.cells[ry][rx].set_type(CELL_RADIATION)

        for _ in range(random.randint(3, 5)):
            dx, dy = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
            if self.cells[dy][dx].cell_type == CELL_EMPTY:
                self.cells[dy][dx].set_type(CELL_DEBRIS)

    def _wrap(self, x: int, y: int) -> tuple[int, int]:
        """Wrap coordinates for toroidal grid."""
        if WRAP_EDGES:
            return x % self.width, y % self.height
        return max(0, min(x, self.width - 1)), max(0, min(y, self.height - 1))

    def get_cell(self, x: int, y: int) -> Cell:
        wx, wy = self._wrap(x, y)
        return self.cells[wy][wx]

    def set_cell_type(self, x: int, y: int, cell_type: int):
        wx, wy = self._wrap(x, y)
        self.cells[wy][wx].set_type(cell_type)

    def get_neighbours(self, x: int, y: int) -> list[tuple[int, int]]:
        """Return the 4 cardinal neighbours (wrapped)."""
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        result = []
        for dx, dy in directions:
            nx, ny = self._wrap(x + dx, y + dy)
            result.append((nx, ny))
        return result

    def count_cell_type(self, cell_type: int) -> int:
        return sum(
            1
            for row in self.cells
            for cell in row
            if cell.cell_type == cell_type
        )

    def astrophage_cells(self) -> list[Cell]:
        return [
            cell
            for row in self.cells
            for cell in row
            if cell.has_astrophage()
        ]

    def to_ascii(self) -> str:
        """Return a simple ASCII representation of the grid."""
        lines = []
        header = "  " + "".join(str(x % 10) for x in range(self.width))
        lines.append(header)
        for y, row in enumerate(self.cells):
            row_str = f"{y:2d}" + "".join(cell.label() for cell in row)
            lines.append(row_str)
        return "\n".join(lines)

    def __repr__(self):
        return f"Grid({self.width}x{self.height})"
