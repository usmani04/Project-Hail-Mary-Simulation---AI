import random
from agents.bayesian_knowledge import BayesianKnowledge
<<<<<<< HEAD
=======
from science.genetic_algorithm import run_ga
from science.beetle_swarm import BeetleSwarm
>>>>>>> ea58054867e1113558136a38e37341feaf69fb9b
from config import (
    CELL_EMPTY, CELL_ASTROPHAGE, CELL_PETROVA,
    CELL_ADRIAN, CELL_HAIL_MARY, CELL_BLIP_A, CELL_DEBRIS, CELL_RADIATION,
    CELL_GRACE
)

GRACE_MAX_HEALTH = 100
GRACE_MAX_ENERGY = 150
MOVE_COST        = 1
EXPERIMENT_COST  = 8
REST_GAIN        = 25
IDLE_DRAIN_RATE  = 0.3


class Grace:

    def __init__(self, x: int, y: int, grid, hazard_manager):
        self.x = x
        self.y = y
        self.grid = grid
        self.hazard_manager = hazard_manager

        self.health  = GRACE_MAX_HEALTH
        self.energy  = GRACE_MAX_ENERGY

        self.samples_collected  = 0
        self.experiments_done   = 0
        self.experiments_failed = 0
        self.beetles_deployed   = 0

        self.memory_recovered = False
        self.at_rocky_ship    = False
        self.flashback_log    = []
        self.action_log       = []

        self._under_type = CELL_EMPTY
        self._target     = None

        self.knowledge = BayesianKnowledge()
<<<<<<< HEAD
=======

        self.taumoeba_samples    = 0
        self.breeding_attempts   = 0
        self.best_earth_strain   = None
        self.best_erid_strain    = None
        self.earth_viable        = False
        self.erid_viable         = False
        self.breeding_log        = []

        self.swarm = BeetleSwarm(grid)

>>>>>>> ea58054867e1113558136a38e37341feaf69fb9b
        self._mark_position()

    def _mark_position(self):
        cell = self.grid.get_cell(self.x, self.y)
        if cell.cell_type != CELL_GRACE:
            self._under_type = cell.cell_type
        cell.set_type(CELL_GRACE)

    def _clear_position(self):
        self.grid.get_cell(self.x, self.y).set_type(self._under_type)

    def _apply_cell_effects(self):
        if self._under_type in (CELL_ASTROPHAGE, CELL_PETROVA):
            cell = self.grid.get_cell(self.x, self.y)
            intensity = cell.astrophage_intensity if cell.astrophage_intensity else 3
            drain = self.hazard_manager.fuzzy_energy_drain(self.x, self.y)
            passive_drain = drain * IDLE_DRAIN_RATE
            self.energy -= passive_drain
            self.energy = max(0, self.energy)
            if self._under_type == CELL_PETROVA:
                self.health -= 1
                self.health = max(0, self.health)

        if self._under_type == CELL_RADIATION:
            self.health -= 2
            self.health = max(0, self.health)

    def _log(self, msg: str):
        self.action_log.append(msg)

    def move(self, dx: int, dy: int):
        if self.energy < MOVE_COST:
            self._log("Too tired to move")
            return False

        self._clear_position()
        nx = (self.x + dx) % self.grid.width
        ny = (self.y + dy) % self.grid.height
        dest_cell = self.grid.get_cell(nx, ny)
        prev_type = dest_cell.cell_type

        self.x, self.y = nx, ny
        self.energy -= MOVE_COST

        if prev_type in (CELL_ASTROPHAGE, CELL_PETROVA):
            entry_drain = self.hazard_manager.fuzzy_energy_drain(nx, ny)
            self.energy -= entry_drain
            self.knowledge.update("entered_astrophage_zone")
            self._log(f"Entered hazard zone ({nx},{ny}) entry_drain={entry_drain:.1f}")
        elif prev_type == CELL_ADRIAN:
            self.knowledge.update("reached_adrian")
            self._log(f"Reached Adrian ({nx},{ny})")
        elif prev_type == CELL_RADIATION:
            self.health -= 3
            self._log(f"Radiation exposure at ({nx},{ny})")
        else:
            self._log(f"Moved to ({nx},{ny})")

        self.energy = max(0, self.energy)
        self.health = max(0, self.health)
        self._mark_position()
        self._check_flashback()
        return True

    def _pick_new_target(self):
<<<<<<< HEAD
=======
        if self.taumoeba_samples < 3:
            for row in self.grid.cells:
                for cell in row:
                    if cell.cell_type == CELL_ADRIAN:
                        return (cell.x, cell.y)

>>>>>>> ea58054867e1113558136a38e37341feaf69fb9b
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
        pick = candidates[min(5, len(candidates) - 1)]
        return (pick[1], pick[2])

    def _step_toward_target(self):
        if self._target is None:
            self._target = self._pick_new_target()
        if self._target is None:
            dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
            self.move(dx, dy)
            return

        tx, ty = self._target
        if (self.x, self.y) == (tx, ty):
            self._target = self._pick_new_target()
            return

        dx, dy = 0, 0
        if tx != self.x:
            dx = 1 if tx > self.x else -1
        elif ty != self.y:
            dy = 1 if ty > self.y else -1

        self.move(dx, dy)

    def collect_sample(self):
<<<<<<< HEAD
        if self._under_type not in (CELL_ASTROPHAGE, CELL_PETROVA, CELL_ADRIAN):
            self._log("Nothing to collect here")
            return False
        self.samples_collected += 1
        self.knowledge.update("sample_collected")
        self._log(f"Sample #{self.samples_collected} at ({self.x},{self.y})")
        return True

=======
        real_type = self._under_type
        if real_type not in (CELL_ASTROPHAGE, CELL_PETROVA, CELL_ADRIAN):
            self._log("Nothing to collect here")
            return False
        self.samples_collected += 1
        if real_type == CELL_ADRIAN:
            self.taumoeba_samples += 1
            self._log(f"Taumoeba sample #{self.taumoeba_samples} from Adrian at ({self.x},{self.y})")
        else:
            self._log(f"Astrophage sample #{self.samples_collected} at ({self.x},{self.y})")
        self.knowledge.update("sample_collected")
        return True

    def force_collect_taumoeba(self):
        self._clear_position()
        actual = self.grid.get_cell(self.x, self.y).cell_type
        self._mark_position()
        if actual == CELL_ADRIAN:
            self.samples_collected += 1
            self.taumoeba_samples  += 1
            self.knowledge.update("sample_collected")
            self._log(f"Taumoeba #{self.taumoeba_samples} at ({self.x},{self.y})")
            return True
        return False

>>>>>>> ea58054867e1113558136a38e37341feaf69fb9b
    def run_experiment(self):
        if self.energy < EXPERIMENT_COST:
            self._log("Not enough energy")
            return False
        if self.samples_collected == 0:
            self._log("No samples")
            return False

        self.energy -= EXPERIMENT_COST
        self.experiments_done += 1
        success_chance = 0.45 + (self.knowledge.knowledge_score() / 250)
        success = random.random() < success_chance

        if success:
            self.knowledge.update("experiment_success")
            self._log(f"Experiment {self.experiments_done} SUCCESS")
        else:
            self.experiments_failed += 1
            self.knowledge.update("experiment_failure")
            self._log(f"Experiment {self.experiments_done} failed")
        return success

    def rest(self):
        self.energy = min(GRACE_MAX_ENERGY, self.energy + REST_GAIN)
        self._log(f"Resting — energy {self.energy}")

    def deploy_beetle(self):
<<<<<<< HEAD
        names = ["John", "Paul", "George", "Ringo"]
        if self.beetles_deployed >= len(names):
            return False
        if self.energy < 15:
            return False
        name = names[self.beetles_deployed]
        self.beetles_deployed += 1
        self.energy -= 15
        self._log(f"Beetle {name} deployed")
        return True

=======
        if self.beetles_deployed >= 4:
            return False
        if self.energy < 15:
            return False

        payload = {
            "knowledge_score":  self.knowledge.knowledge_score(),
            "beliefs":          self.knowledge.summary(),
            "samples":          self.samples_collected,
            "earth_viable":     self.earth_viable,
            "earth_fitness":    round(self.best_earth_strain.fitness, 3) if self.best_earth_strain else 0,
            "erid_viable":      self.erid_viable,
            "best_strain_genes": self.best_earth_strain.summary() if self.best_earth_strain else {},
        }

        beetle = self.swarm.deploy(self.x, self.y, payload)
        if beetle is None:
            return False

        self.beetles_deployed += 1
        self.energy -= 15
        self._log(f"Beetle {beetle.name} deployed from ({self.x},{self.y})")
        return True

    def breed_taumoeba(self, target="earth"):
        if self.taumoeba_samples < 2:
            self._log("Not enough Taumoeba samples to breed")
            return None

        if self.energy < 15:
            self._log("Not enough energy to breed")
            return None

        self.energy -= 15
        self.breeding_attempts += 1

        knowledge_bonus = self.knowledge.knowledge_score() / 100.0
        generations = 10 + int(knowledge_bonus * 20)

        result = run_ga(generations=generations,
                        target=target,
                        knowledge_bonus=knowledge_bonus)

        strain   = result["best_strain"]
        viable   = result["viable"]
        fitness  = result["best_fitness"]

        if target == "earth":
            if self.best_earth_strain is None or fitness > self.best_earth_strain.fitness:
                self.best_earth_strain = strain
            self.earth_viable = viable
        else:
            if self.best_erid_strain is None or fitness > self.best_erid_strain.fitness:
                self.best_erid_strain = strain
            self.erid_viable = viable

        msg = (f"Breeding attempt {self.breeding_attempts} [{target}] "
               f"gen={generations} fitness={fitness:.3f} viable={viable}")
        self._log(msg)
        self.breeding_log.append(msg)

        if viable:
            self.knowledge.update("experiment_success")
        else:
            self.knowledge.update("experiment_failure")

        return result

>>>>>>> ea58054867e1113558136a38e37341feaf69fb9b
    def receive_rocky_data(self):
        self.knowledge.update("rocky_shared_data")
        self._log("Rocky shared data")

    def _check_flashback(self):
        if not self.memory_recovered and self.knowledge.knowledge_score() > 30:
            self.memory_recovered = True
            self.flashback_log.append(
                "FLASHBACK: Eva Stratt — Earth has decades before total dimming"
            )

    def is_alive(self) -> bool:
        return self.health > 0 and self.energy > 0

    def status(self) -> dict:
        return {
            "pos":         (self.x, self.y),
            "health":      self.health,
            "energy":      round(self.energy, 1),
            "samples":     self.samples_collected,
            "experiments": self.experiments_done,
            "failures":    self.experiments_failed,
            "beetles":     self.beetles_deployed,
            "knowledge":   self.knowledge.knowledge_score(),
            "beliefs":     self.knowledge.summary(),
<<<<<<< HEAD
            "on_cell":     self._under_type,
        }

    def decide_action(self):
=======
            "on_cell":          self._under_type,
            "taumoeba_samples":  self.taumoeba_samples,
            "breeding_attempts": self.breeding_attempts,
            "earth_viable":      self.earth_viable,
            "erid_viable":       self.erid_viable,
            "earth_fitness":     round(self.best_earth_strain.fitness, 3) if self.best_earth_strain else 0,
            "erid_fitness":      round(self.best_erid_strain.fitness, 3) if self.best_erid_strain else 0,
            "swarm_transmitted": self.swarm.transmitted_count(),
        }

    def decide_action(self):
        self.swarm.step()
>>>>>>> ea58054867e1113558136a38e37341feaf69fb9b
        self._apply_cell_effects()

        if not self.is_alive():
            return "dead"

        if self.energy < 30:
            self.rest()
            return "rest"

<<<<<<< HEAD
        on_sample = self._under_type in (CELL_ASTROPHAGE, CELL_PETROVA, CELL_ADRIAN)

        if on_sample and self.samples_collected < 8:
            self.collect_sample()
=======
        self._clear_position()
        actual_type = self.grid.get_cell(self.x, self.y).cell_type
        self._mark_position()
        on_sample = actual_type in (CELL_ASTROPHAGE, CELL_PETROVA, CELL_ADRIAN)

        if on_sample and (self.samples_collected < 8 or (actual_type == CELL_ADRIAN and self.taumoeba_samples < 5)):
            if actual_type == CELL_ADRIAN:
                self.force_collect_taumoeba()
            else:
                self.collect_sample()
>>>>>>> ea58054867e1113558136a38e37341feaf69fb9b
            return "collect"

        if self.samples_collected >= 3 and self.energy >= EXPERIMENT_COST:
            if random.random() < 0.35:
                self.run_experiment()
                return "experiment"

<<<<<<< HEAD
        if self.knowledge.knowledge_score() > 50 and self.beetles_deployed < 4:
=======
        if self.taumoeba_samples >= 2 and self.knowledge.knowledge_score() > 25:
            if not self.earth_viable and random.random() < 0.25:
                self.breed_taumoeba(target="earth")
                return "breed_taumoeba"
            if self.earth_viable and not self.erid_viable and random.random() < 0.15:
                self.breed_taumoeba(target="erid")
                return "breed_taumoeba_erid"

        if self.knowledge.knowledge_score() > 30 and self.beetles_deployed < 4:
>>>>>>> ea58054867e1113558136a38e37341feaf69fb9b
            if random.random() < 0.1:
                self.deploy_beetle()
                return "deploy_beetle"

        self._step_toward_target()
        return "move"
