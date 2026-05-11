GRID_WIDTH = 20
GRID_HEIGHT = 20

CELL_EMPTY      = 0
CELL_ADRIAN     = 1
CELL_ASTROPHAGE = 2
CELL_HAIL_MARY  = 3
CELL_BLIP_A     = 4
CELL_BEETLE     = 5
CELL_RADIATION  = 6
CELL_DEBRIS     = 7
CELL_PETROVA    = 8
CELL_GRACE      = 9
CELL_ROCKY      = 10

ASTROPHAGE_SPREAD_CHANCE = 0.02
ASTROPHAGE_ENERGY_DRAIN  = 5
PETROVA_ENERGY_DRAIN     = 15
ASTROPHAGE_INTENSITY_MIN = 2
ASTROPHAGE_INTENSITY_MAX = 10

RADIATION_HEALTH_DRAIN = 3

DEFAULT_TURNS    = 200
WRAP_EDGES       = True

GRACE_START_X    = 1
GRACE_START_Y    = 1
GRACE_MAX_HEALTH = 100
GRACE_MAX_ENERGY = 150

ROCKY_START_X    = 18
ROCKY_START_Y    = 1
ROCKY_MAX_HEALTH = 120
ROCKY_MAX_ENERGY = 180

CELL_COLORS = {
    CELL_EMPTY:      "#0a0a1a",
    CELL_ADRIAN:     "#2e7d32",
    CELL_ASTROPHAGE: "#b71c1c",
    CELL_HAIL_MARY:  "#1565c0",
    CELL_BLIP_A:     "#6a1b9a",
    CELL_BEETLE:     "#f9a825",
    CELL_RADIATION:  "#e65100",
    CELL_DEBRIS:     "#4e342e",
    CELL_PETROVA:    "#880e4f",
    CELL_GRACE:      "#00e5ff",
    CELL_ROCKY:      "#00c853",
}

CELL_LABELS = {
    CELL_EMPTY:      " ",
    CELL_ADRIAN:     "A",
    CELL_ASTROPHAGE: "*",
    CELL_HAIL_MARY:  "HM",
    CELL_BLIP_A:     "BA",
    CELL_BEETLE:     "Bt",
    CELL_RADIATION:  "Ra",
    CELL_DEBRIS:     "Db",
    CELL_PETROVA:    "P",
    CELL_GRACE:      "Gr",
    CELL_ROCKY:      "Rk",
}

CELL_NAMES = {
    CELL_EMPTY:      "Empty Space",
    CELL_ADRIAN:     "Planet Adrian",
    CELL_ASTROPHAGE: "Astrophage Cloud",
    CELL_HAIL_MARY:  "Hail Mary Ship",
    CELL_BLIP_A:     "Blip-A Ship",
    CELL_BEETLE:     "Beetle Probe",
    CELL_RADIATION:  "Radiation Zone",
    CELL_DEBRIS:     "Debris Field",
    CELL_PETROVA:    "Petrova Line",
    CELL_GRACE:      "Dr Grace",
    CELL_ROCKY:      "Rocky",
}
