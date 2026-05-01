import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from config import CELL_COLORS, CELL_LABELS, CELL_NAMES


def _hex_to_rgb(hex_color):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))


CELL_RGB = {k: _hex_to_rgb(v) for k, v in CELL_COLORS.items()}


class GridDisplay:

    def __init__(self, grid, title="Project Hail Mary Simulation"):
        self.grid  = grid
        self.title = title
        self.fig   = plt.figure(figsize=(18, 10))
        self.fig.patch.set_facecolor("#0a0a1a")

        self.ax      = self.fig.add_axes([0.01, 0.02, 0.58, 0.94])
        self.ax_leg  = self.fig.add_axes([0.62, 0.42, 0.36, 0.55])
        self.ax_stat = self.fig.add_axes([0.62, 0.02, 0.36, 0.38])

        for ax in [self.ax, self.ax_leg, self.ax_stat]:
            ax.set_facecolor("#0d0d1f")
            ax.axis("off")

        plt.ion()

    def _build_image(self):
        img = np.zeros((self.grid.height, self.grid.width, 3))
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                cell = self.grid.cells[y][x]
                rgb  = CELL_RGB.get(cell.cell_type, (1, 1, 1))
                if cell.has_astrophage() and cell.astrophage_intensity > 0:
                    f   = 0.5 + 0.5 * (cell.astrophage_intensity / 10.0)
                    rgb = tuple(min(1.0, c * f) for c in rgb)
                img[y][x] = rgb
        return img

    def _draw_grid(self):
        self.ax.clear()
        self.ax.set_facecolor("#0d0d1f")
        self.ax.axis("off")

        img = self._build_image()
        self.ax.imshow(img, interpolation="nearest", aspect="equal",
                       extent=[-0.5, self.grid.width - 0.5,
                                self.grid.height - 0.5, -0.5])

        for x in range(self.grid.width + 1):
            self.ax.axvline(x - 0.5, color="#1a1a2e", linewidth=0.4)
        for y in range(self.grid.height + 1):
            self.ax.axhline(y - 0.5, color="#1a1a2e", linewidth=0.4)

        for y in range(self.grid.height):
            for x in range(self.grid.width):
                cell  = self.grid.cells[y][x]
                label = CELL_LABELS.get(cell.cell_type, "")
                if label and label.strip():
                    self.ax.text(x, y, label,
                                 ha="center", va="center",
                                 fontsize=6.5, color="white",
                                 fontweight="bold")

        for i in range(self.grid.width):
            self.ax.text(i, self.grid.height - 0.05, str(i),
                         ha="center", va="top",
                         fontsize=5.5, color="#556677")
        for j in range(self.grid.height):
            self.ax.text(-0.6, j, str(j),
                         ha="right", va="center",
                         fontsize=5.5, color="#556677")

        self.ax.set_title(self.title, color="white",
                          fontsize=13, fontweight="bold", pad=6)

    def _draw_legend(self):
        self.ax_leg.clear()
        self.ax_leg.set_facecolor("#0d0d1f")
        self.ax_leg.axis("off")

        self.ax_leg.text(0.5, 0.97, "LEGEND", ha="center", va="top",
                         color="white", fontsize=12, fontweight="bold",
                         transform=self.ax_leg.transAxes)

        entries = [(CELL_LABELS[k], CELL_NAMES[k], CELL_COLORS[k])
                   for k in sorted(CELL_LABELS)
                   if CELL_LABELS[k].strip()]

        row_h = 0.085
        y0    = 0.88

        for i, (label, name, color) in enumerate(entries):
            y = y0 - i * row_h

            self.ax_leg.add_patch(mpatches.FancyBboxPatch(
                (0.03, y - 0.03), 0.14, 0.065,
                boxstyle="round,pad=0.01",
                facecolor=color, edgecolor="#ffffff44",
                linewidth=0.8,
                transform=self.ax_leg.transAxes,
                clip_on=False
            ))
            self.ax_leg.text(0.10, y + 0.002, label,
                             ha="center", va="center",
                             color="white", fontsize=8.5, fontweight="bold",
                             transform=self.ax_leg.transAxes)
            self.ax_leg.text(0.21, y + 0.002, name,
                             ha="left", va="center",
                             color="#ccddee", fontsize=9,
                             transform=self.ax_leg.transAxes)

    def _draw_status(self, turn, grace, rocky):
        self.ax_stat.clear()
        self.ax_stat.set_facecolor("#0d0d1f")
        self.ax_stat.axis("off")
        t = self.ax_stat.transAxes

        def line(y, txt, color="#ccddee", size=9, bold=False):
            self.ax_stat.text(0.04, y, txt, color=color,
                              fontsize=size, va="center",
                              fontweight="bold" if bold else "normal",
                              transform=t)

        line(0.96, f"STATUS  —  Turn {turn}", color="white", size=11, bold=True)
        line(0.89, "Dr Grace", color="#00e5ff", size=10, bold=True)

        if grace:
            line(0.82, f"  Health     :  {grace.health} / 100")
            line(0.75, f"  Energy     :  {grace.energy:.0f} / 150")
            line(0.68, f"  Knowledge  :  {grace.knowledge.knowledge_score():.1f}%")
            line(0.61, f"  Samples    :  {grace.samples_collected}")
            line(0.54, f"  Exps       :  {grace.experiments_done}  (failed: {grace.experiments_failed})")
            line(0.47, f"  Beetles    :  {grace.beetles_deployed} / 4")

        line(0.40, "- " * 20, color="#334455", size=7)
        line(0.34, "Rocky  (Eridian)", color="#00c853", size=10, bold=True)

        if rocky:
            tunnel = "OPEN" if rocky.tunnel_connected else f"Building {rocky.tunnel_build_progress}/15"
            line(0.27, f"  Health     :  {rocky.health} / 120")
            line(0.20, f"  Energy     :  {rocky.energy:.0f} / 180")
            line(0.13, f"  Erid K     :  {rocky.erid_progress:.1f}%")
            line(0.06, f"  Tunnel     :  {tunnel}")
            line(0.00, f"  Shared: {rocky.data_shared}   Repairs: {rocky.repairs_done}   Vocab: {rocky.translation.vocab_size()} / {rocky.translation.decoded_size()}")

    def render(self, turn=0, grace=None, rocky=None):
        self._draw_grid()
        self._draw_legend()
        self._draw_status(turn, grace, rocky)
        plt.pause(0.01)

    def save(self, filename="simulation_final.png"):
        self.fig.savefig(filename, dpi=150, bbox_inches="tight",
                         facecolor=self.fig.get_facecolor())
        print(f"Saved to {filename}")

    def close(self):
        plt.ioff()
        plt.close(self.fig)
