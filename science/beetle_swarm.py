import random
import math
from config import CELL_EMPTY, CELL_BEETLE

BEETLE_NAMES      = ["John", "Paul", "George", "Ringo"]
PHEROMONE_DECAY   = 0.85
PHEROMONE_DEPOSIT = 1.0


class Pheromone:
    def __init__(self, width, height):
        self.width  = width
        self.height = height
        self.grid   = [[0.0] * width for _ in range(height)]

    def deposit(self, x, y, amount=PHEROMONE_DEPOSIT):
        self.grid[y][x] = min(10.0, self.grid[y][x] + amount)

    def decay(self):
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] *= PHEROMONE_DECAY
                if self.grid[y][x] < 0.01:
                    self.grid[y][x] = 0.0

    def get(self, x, y):
        return self.grid[y % self.height][x % self.width]


class BeetleProbe:
    """
    Autonomous beetle probe.

    Swarm Intelligence:
      - Deployed from Hail Mary ship
      - Moves directly toward grid edge (space exit point)
      - Pheromone trails shared with other beetles
      - Once at edge — TRANSMITTED (launched to Earth)
      - Does not wander — one-way mission like Grace herself
    """

    def __init__(self, name, x, y, grid, pheromone, swarm_ref):
        self.name       = name
        self.x          = x
        self.y          = y
        self.grid       = grid
        self.pheromone  = pheromone
        self.swarm_ref  = swarm_ref

        self.deploy_x   = x
        self.deploy_y   = y

        self.data_payload = {}
        self.deployed     = False
        self.transmitted  = False
        self.turns_active = 0
        self.path         = [(x, y)]
        self.action_log   = []
        self._under_type  = CELL_EMPTY

        self._exit_x, self._exit_y = self._pick_exit()

    def _pick_exit(self):
        edges = []
        for x in range(self.grid.width):
            edges.append((x, 0))
            edges.append((x, self.grid.height - 1))
        for y in range(self.grid.height):
            edges.append((0, y))
            edges.append((self.grid.width - 1, y))

        other_exits = [b._exit_x if hasattr(b,'_exit_x') else -1 for b in self.swarm_ref]
        unique = [e for e in edges if e[0] not in other_exits]
        candidates = unique if unique else edges

        dist_sorted = sorted(candidates,
            key=lambda e: math.sqrt((e[0]-self.x)**2 + (e[1]-self.y)**2))
        pick_idx = min(3, len(dist_sorted)-1)
        return dist_sorted[pick_idx]

    def _mark(self):
        cell = self.grid.get_cell(self.x, self.y)
        if cell.cell_type not in (9, 10):
            self._under_type = cell.cell_type
        cell.set_type(CELL_BEETLE)

    def _clear(self):
        self.grid.get_cell(self.x, self.y).set_type(self._under_type)

    def load_data(self, payload):
        self.data_payload = payload

    def _move_toward_exit(self):
        tx, ty = self._exit_x, self._exit_y

        dx = 0 if tx == self.x else (1 if tx > self.x else -1)
        dy = 0 if ty == self.y else (1 if ty > self.y else -1)

        if dx != 0 and dy != 0:
            if abs(tx - self.x) >= abs(ty - self.y):
                dy = 0
            else:
                dx = 0

        return dx, dy

    def step(self):
        if not self.deployed or self.transmitted:
            return

        self.turns_active += 1
        self._clear()

        dx, dy = self._move_toward_exit()
        nx = (self.x + dx) % self.grid.width
        ny = (self.y + dy) % self.grid.height

        self.x, self.y = nx, ny
        self.path.append((nx, ny))

        self.pheromone.deposit(nx, ny, 0.3)

        if (nx, ny) == (self._exit_x, self._exit_y) or self.turns_active >= 40:
            self._transmit()
        else:
            self._mark()

    def _transmit(self):
        self.transmitted = True
        self.grid.get_cell(self.x, self.y).set_type(self._under_type)
        self.action_log.append(
            f"{self.name}: LAUNCHED to Earth after {self.turns_active} turns "
            f"| payload: {list(self.data_payload.keys())}"
        )

    def status(self):
        return {
            "name":        self.name,
            "pos":         (self.x, self.y),
            "deploy_from": (self.deploy_x, self.deploy_y),
            "exit_target": (self._exit_x, self._exit_y),
            "deployed":    self.deployed,
            "transmitted": self.transmitted,
            "turns":       self.turns_active,
            "path_len":    len(self.path),
            "payload":     list(self.data_payload.keys()),
        }


class BeetleSwarm:
    """
    4 beetle probes deployed from Hail Mary ship.
    Each beetle takes a different exit point on the grid edge.
    Pheromone trails help beetles avoid clustering on same path.
    """

    def __init__(self, grid):
        self.grid            = grid
        self.pheromone       = Pheromone(grid.width, grid.height)
        self.beetles         = []
        self._deployed_count = 0

    def deploy(self, x, y, payload):
        if self._deployed_count >= len(BEETLE_NAMES):
            return None

        name   = BEETLE_NAMES[self._deployed_count]
        beetle = BeetleProbe(name, x, y, self.grid,
                             self.pheromone, self.beetles)
        beetle.load_data(payload)
        beetle.deployed    = True
        beetle.deploy_x    = x
        beetle.deploy_y    = y

        cell = self.grid.get_cell(x, y)
        beetle._under_type = cell.cell_type if cell.cell_type not in (9, 10) else CELL_EMPTY
        cell.set_type(CELL_BEETLE)

        self.beetles.append(beetle)
        self._deployed_count += 1
        return beetle

    def step(self):
        self.pheromone.decay()
        for beetle in self.beetles:
            beetle.step()

    def transmitted_count(self):
        return sum(1 for b in self.beetles if b.transmitted)

    def all_transmitted(self):
        return len(self.beetles) > 0 and all(b.transmitted for b in self.beetles)

    def status(self):
        return [b.status() for b in self.beetles]
