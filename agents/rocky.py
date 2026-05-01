import random
from config import (
    CELL_EMPTY, CELL_BLIP_A, CELL_ASTROPHAGE,
    CELL_PETROVA, CELL_ADRIAN, CELL_ROCKY
)

ROCKY_MAX_HEALTH  = 120
ROCKY_MAX_ENERGY  = 180
ROCKY_MOVE_COST   = 1
ROCKY_REPAIR_COST = 12
ROCKY_SHARE_COST  = 5

TUNNEL_BUILD_TURNS = 15


class TranslationSystem:
    """
    Progressive shared language between Grace and Rocky.
    Rocky speaks in sonar chords. Grace learns meanings over time.
    Early turns: Rocky emits chords but Grace cannot decode them.
    As tunnel builds and interactions increase, Grace decodes more words.
    """

    def __init__(self):
        self._rocky_vocab   = {}
        self._grace_decoded = {}
        self._interaction_count = 0
        self.fluency = 0.0

        self._notes = ["do", "re", "mi", "fa", "sol", "la", "ti"]

    def rocky_emit(self, meaning: str) -> str:
        if meaning not in self._rocky_vocab:
            chord = "-".join(random.sample(self._notes, 3))
            self._rocky_vocab[meaning] = chord
        return self._rocky_vocab[meaning]

    def attempt_decode(self, chord: str, tunnel_active: bool) -> str:
        if not tunnel_active:
            return "???"
        self._interaction_count += 1
        self.fluency = min(1.0, self._interaction_count / 30.0)

        for meaning, c in self._rocky_vocab.items():
            if c == chord:
                if meaning not in self._grace_decoded:
                    if random.random() < self.fluency:
                        self._grace_decoded[meaning] = chord
                return self._grace_decoded.get(meaning, "???")
        return "???"

    def vocab_size(self) -> int:
        return len(self._rocky_vocab)

    def decoded_size(self) -> int:
        return len(self._grace_decoded)

    def summary(self) -> str:
        return (f"Rocky vocab={self.vocab_size()} | "
                f"Grace decoded={self.decoded_size()} | "
                f"fluency={self.fluency:.2f}")


class Rocky:
    """
    Rocky is an Eridian alien agent.

    Biological constraints:
      - Breathes ammonia at high pressure
      - Cannot enter Grace's oxygen cells without xenonite tunnel
      - Takes extra damage in non-ammonia environments

    Goals (aligned but not identical to Grace):
      - Primary: understand why Tau Ceti is Astrophage-resistant
      - Erid goal: find solution for 40 Eridani system independently
      - Secondary: help Grace so both civilisations survive

    Communication:
      - Emits sonar chord patterns
      - Translation system builds progressively via tunnel interactions
    """

    def __init__(self, x: int, y: int, grid, hazard_manager):
        self.x = x
        self.y = y
        self.grid = grid
        self.hazard_manager = hazard_manager

        self.health = ROCKY_MAX_HEALTH
        self.energy = ROCKY_MAX_ENERGY

        self.repairs_done        = 0
        self.data_shared         = 0
        self.energy_transferred  = 0
        self.recon_done          = 0

        self.tunnel_connected    = False
        self.tunnel_build_progress = 0
        self.grace_ref           = None

        self.erid_progress       = 0.0
        self.erid_knowledge      = {
            "astrophage_spread_model": 0.1,
            "taumoeba_applicability":  0.05,
            "erid_atmosphere_match":   0.08,
            "fuel_efficiency":         0.12,
        }

        self.action_log = []
        self._under_type = CELL_BLIP_A
        self._target     = None
        self._chord_log  = []

        self.translation = TranslationSystem()

        self._mark_position()

    def _mark_position(self):
        cell = self.grid.get_cell(self.x, self.y)
        if cell.cell_type != CELL_ROCKY:
            self._under_type = cell.cell_type
        cell.set_type(CELL_ROCKY)

    def _clear_position(self):
        self.grid.get_cell(self.x, self.y).set_type(self._under_type)

    def _log(self, msg):
        self.action_log.append(msg)

    def _emit(self, meaning: str):
        chord = self.translation.rocky_emit(meaning)
        if self.grace_ref and self.tunnel_connected:
            decoded = self.translation.attempt_decode(chord, self.tunnel_connected)
            self._chord_log.append(
                f"Rocky [{chord}] = '{meaning}' | Grace hears: '{decoded}'"
            )
        else:
            self._chord_log.append(
                f"Rocky [{chord}] | no tunnel — Grace cannot hear"
            )

    def _in_oxygen_zone(self) -> bool:
        return self._under_type not in (CELL_BLIP_A, CELL_ROCKY)

    def _atmosphere_damage(self):
        if self._in_oxygen_zone() and not self.tunnel_connected:
            self.health -= 3
            self.health = max(0, self.health)
            self._log("Rocky taking atmosphere damage — needs tunnel!")

    def build_tunnel(self):
        if self.tunnel_connected:
            return False
        self.tunnel_build_progress += 1
        self._emit("building_tunnel")
        self._log(f"Xenonite tunnel progress: {self.tunnel_build_progress}/{TUNNEL_BUILD_TURNS}")
        if self.tunnel_build_progress >= TUNNEL_BUILD_TURNS:
            self.tunnel_connected = True
            self._log("Xenonite tunnel COMPLETE — Grace and Rocky can now interact safely")
            if self.grace_ref:
                self.grace_ref.at_rocky_ship = True
        return True

    def move(self, dx: int, dy: int):
        if self.energy < ROCKY_MOVE_COST:
            return False

        self._clear_position()
        nx = (self.x + dx) % self.grid.width
        ny = (self.y + dy) % self.grid.height
        prev_type = self.grid.get_cell(nx, ny).cell_type

        self.x, self.y = nx, ny
        self.energy -= ROCKY_MOVE_COST

        if prev_type in (CELL_ASTROPHAGE, CELL_PETROVA):
            drain = self.hazard_manager.fuzzy_energy_drain(nx, ny) * 0.5
            self.energy -= drain
            self._log(f"Rocky hazard ({nx},{ny}) drain={drain:.1f}")
        else:
            self._log(f"Rocky moved ({nx},{ny})")

        self.energy = max(0, self.energy)
        self._mark_position()
        return True

    def _pick_target(self):
        candidates = []
        for row in self.grid.cells:
            for cell in row:
                if cell.cell_type in (CELL_ASTROPHAGE, CELL_PETROVA, CELL_ADRIAN):
                    dist = abs(cell.x - self.x) + abs(cell.y - self.y)
                    if dist > 3:
                        candidates.append((dist, cell.x, cell.y))
        if not candidates:
            return None
        candidates.sort()
        pick = candidates[min(4, len(candidates) - 1)]
        return (pick[1], pick[2])

    def _step_toward_target(self):
        if self._target is None:
            self._target = self._pick_target()
        if self._target is None:
            dx, dy = random.choice([(0,1),(0,-1),(1,0),(-1,0)])
            self.move(dx, dy)
            return

        tx, ty = self._target
        if (self.x, self.y) == (tx, ty):
            self._target = self._pick_target()
            return

        dx, dy = 0, 0
        if tx != self.x:
            dx = 1 if tx > self.x else -1
        elif ty != self.y:
            dy = 1 if ty > self.y else -1
        self.move(dx, dy)

    def share_knowledge(self):
        if not self.tunnel_connected:
            self._emit("want_to_share")
            self._log("Rocky wants to share but tunnel not ready")
            return False
        if self.energy < ROCKY_SHARE_COST or self.grace_ref is None:
            return False

        self.energy -= ROCKY_SHARE_COST
        self.data_shared += 1
        self.grace_ref.receive_rocky_data()

        topics = ["astrophage_properties", "star_map_erid",
                  "xenonite_engineering", "taumoeba_observation"]
        topic = topics[self.data_shared % len(topics)]
        self._emit(topic)
        self._log(f"Rocky shared '{topic}' with Grace (#{self.data_shared})")
        return True

    def repair(self):
        if self.energy < ROCKY_REPAIR_COST:
            return False
        self.energy -= ROCKY_REPAIR_COST
        self.repairs_done += 1
        self._emit("repair_complete")
        self._log(f"Rocky repair #{self.repairs_done}")
        return True

    def transfer_energy(self):
        if self.grace_ref is None or self.energy < 40:
            return False
        amount = min(25, self.energy - 30)
        self.energy -= amount
        self.grace_ref.energy = min(150, self.grace_ref.energy + amount)
        self.energy_transferred += amount
        self._emit("energy_gift")
        self._log(f"Rocky gave {amount:.0f} energy to Grace (Astrophage fuel)")
        return True

    def do_recon(self):
        self.recon_done += 1
        cell = self.grid.get_cell(self.x, self.y)
        self._emit("recon_data")
        self._log(f"Rocky recon #{self.recon_done} at ({self.x},{self.y}) cell={cell.cell_type}")

    def _update_erid_knowledge(self, event: str):
        updates = {
            "recon":          {"astrophage_spread_model": 0.06},
            "sample_nearby":  {"taumoeba_applicability":  0.08, "erid_atmosphere_match": 0.05},
            "grace_shared":   {"taumoeba_applicability":  0.10, "fuel_efficiency": 0.07},
            "experiment_done":{"astrophage_spread_model": 0.05, "fuel_efficiency": 0.04},
        }
        if event in updates:
            for k, v in updates[event].items():
                self.erid_knowledge[k] = min(0.99, self.erid_knowledge[k] + v)
        self.erid_progress = round(
            sum(self.erid_knowledge.values()) / len(self.erid_knowledge) * 100, 2
        )

    def _apply_passive_drain(self):
        if self._under_type in (CELL_ASTROPHAGE, CELL_PETROVA):
            drain = self.hazard_manager.fuzzy_energy_drain(self.x, self.y) * 0.2
            self.energy = max(0, self.energy - drain)

    def is_alive(self):
        return self.health > 0 and self.energy > 0

    def status(self):
        return {
            "pos":                (self.x, self.y),
            "health":             self.health,
            "energy":             round(self.energy, 1),
            "repairs":            self.repairs_done,
            "data_shared":        self.data_shared,
            "energy_transferred": round(self.energy_transferred, 1),
            "recon":              self.recon_done,
            "tunnel":             self.tunnel_connected,
            "tunnel_progress":    self.tunnel_build_progress,
            "erid_progress":      self.erid_progress,
            "translation":        self.translation.summary(),
        }

    def decide_action(self):
        self._apply_passive_drain()
        self._atmosphere_damage()

        if not self.is_alive():
            return "dead"

        if self.energy < 25:
            self.energy = min(ROCKY_MAX_ENERGY, self.energy + 20)
            self._log("Rocky resting")
            return "rest"

        if not self.tunnel_connected:
            self.build_tunnel()
            return "build_tunnel"

        if self.grace_ref is not None:
            if self.grace_ref.energy < 40 and self.energy > 60:
                self.transfer_energy()
                self._update_erid_knowledge("grace_shared")
                return "transfer_energy"

            dist = abs(self.x - self.grace_ref.x) + abs(self.y - self.grace_ref.y)

            if dist <= 5 and self.data_shared < 15:
                if random.random() < 0.6:
                    self.share_knowledge()
                    self._update_erid_knowledge("grace_shared")
                    return "share_knowledge"

            if self.tunnel_connected and dist > 5 and self.data_shared < 15:
                gx, gy = self.grace_ref.x, self.grace_ref.y
                dx = 0 if gx == self.x else (1 if gx > self.x else -1)
                dy = 0 if gy == self.y else (1 if gy > self.y else -1)
                if dx != 0:
                    self.move(dx, 0)
                elif dy != 0:
                    self.move(0, dy)
                return "move_to_grace"

        if random.random() < 0.15:
            self.repair()
            return "repair"

        if random.random() < 0.12:
            self.do_recon()
            self._update_erid_knowledge("recon")
            return "recon"

        self._step_toward_target()
        self._update_erid_knowledge("experiment_done")
        return "move"
