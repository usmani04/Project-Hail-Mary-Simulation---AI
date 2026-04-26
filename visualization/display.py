
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from config import CELL_COLORS, CELL_LABELS, GRID_WIDTH, GRID_HEIGHT

def _hex_to_rgb(hex_color: str) -> tuple:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))

CELL_RGB = {k: _hex_to_rgb(v) for k, v in CELL_COLORS.items()}

class GridDisplay:
    """Matplotlib-based visualizer for the simulation grid."""

    def __init__(self, grid, title: str = "Project Hail Mary Simulation"):
        self.grid = grid
        self.title = title
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        self.fig.patch.set_facecolor("#050510")
        self.ax.set_facecolor("#050510")
        plt.ion()

    def _build_image(self) -> np.ndarray:
        img = np.zeros((self.grid.height, self.grid.width, 3))
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                cell = self.grid.cells[y][x]
                rgb = CELL_RGB.get(cell.cell_type, (1, 1, 1))
                if cell.has_astrophage() and cell.astrophage_intensity > 0:
                    factor = 0.5 + 0.5 * (cell.astrophage_intensity / 10.0)
                    rgb = tuple(min(1.0, c * factor) for c in rgb)
                img[y][x] = rgb
        return img

    def render(self, turn: int = 0, info: dict = None):
        """Render the current grid state."""
        self.ax.clear()
        img = self._build_image()
        self.ax.imshow(img, interpolation="nearest", aspect="equal")

        for x in range(self.grid.width + 1):
            self.ax.axvline(x - 0.5, color="#1a1a2e", linewidth=0.5)
        for y in range(self.grid.height + 1):
            self.ax.axhline(y - 0.5, color="#1a1a2e", linewidth=0.5)

        for y in range(self.grid.height):
            for x in range(self.grid.width):
                cell = self.grid.cells[y][x]
                lbl = cell.label()
                if lbl != ".":
                    self.ax.text(
                        x, y, lbl,
                        ha="center", va="center",
                        fontsize=7, color="white",
                        fontweight="bold"
                    )

        turn_info = f"Turn {turn}"
        if info:
            parts = [f"{k}: {v}" for k, v in info.items()]
            turn_info += "   |   " + "   ".join(parts)

        self.ax.set_title(
            f"{self.title}\n{turn_info}",
            color="white", fontsize=11, pad=10
        )
        self.ax.set_xticks(range(self.grid.width))
        self.ax.set_yticks(range(self.grid.height))
        self.ax.set_xticklabels(range(self.grid.width), color="#555577", fontsize=7)
        self.ax.set_yticklabels(range(self.grid.height), color="#555577", fontsize=7)
        self.ax.tick_params(length=0)

        patches = [
            mpatches.Patch(color=CELL_COLORS[k], label=v)
            for k, v in CELL_LABELS.items()
            if k in CELL_COLORS and v != "."
        ]
        self.ax.legend(
            handles=patches,
            loc="upper left",
            bbox_to_anchor=(1.01, 1),
            fontsize=8,
            facecolor="#0a0a1a",
            edgecolor="#333355",
            labelcolor="white"
        )

        self.fig.tight_layout()
        plt.pause(0.01)

    def save(self, filename: str = "grid_snapshot.png"):
        self.fig.savefig(filename, dpi=150, bbox_inches="tight",
                         facecolor=self.fig.get_facecolor())
        print(f"[Display] Saved to {filename}")

    def close(self):
        plt.ioff()
        plt.close(self.fig)
