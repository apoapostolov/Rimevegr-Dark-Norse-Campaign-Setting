"""combat_types.py — Iron Ledger combat: enums, constants, weapon/terrain tables."""
from enum import Enum

# Enums
# ───────────────────────────────────────────────────────────────────────

LOCATIONS = ["head", "torso", "right_arm", "left_arm", "legs", "hands", "feet"]


class Stance(Enum):
    """Fighting stances drawn from the Liechtenauer tradition."""
    AGGRESSIVE = "aggressive"   # Vom Tag / Zorn — commit forward
    BALANCED = "balanced"       # Pflug — measured, default
    DEFENSIVE = "defensive"     # Ochs — conserve, parry focus
    LOW_GUARD = "low_guard"     # Alber — bait and counter


class Maneuver(Enum):
    """Available combat maneuvers."""
    # ── Attack ──
    CUT = "cut"                     # Standard cut (Hau)
    THRUST = "thrust"               # Stich — piercing
    HEAVY_BLOW = "heavy_blow"       # Oberhau — powerful overhead
    HALF_SWORD = "half_sword"       # Halbschwert — anti-armor
    MORDSCHLAG = "mordschlag"       # Pommel strike — anti-armor
    # ── Control ──
    BIND = "bind"                   # Winden — weapon control
    SHOVE = "shove"                 # Ringen — knockdown / break grapple
    GRAPPLE = "grapple"             # Ringen am Schwert — wrestling
    SHIELD_BASH = "shield_bash"     # Shield strike — stagger
    DISARM = "disarm"               # Entwinden — strip weapon
    # ── Setup ──
    FEINT = "feint"                 # Fehlen / Zucken — deception
    # ── Distance Management ──
    STEP_IN   = "step_in"           # Close distance one band (action or free reaction to miss)
    STEP_BACK = "step_back"         # Open distance one band
    # ── Defensive ──
    GUARD = "guard"                 # Hold position, recover
    # ── Recovery ──
    STAND = "stand"                 # Rise from prone
    PICK_UP_WEAPON = "pick_up_weapon"  # Retrieve dropped weapon
    SWITCH_WEAPON  = "switch_weapon"   # Draw backup weapon from belt
    # ── Grapple Entry (require melee range) ──
    BROKARTOK = "brokartok"         # Belt-and-thigh grip, leg-trip family
    LAUSATOK = "lausatok"           # Collar/throat tie-up, free-style
    HRYGGSPENNA = "hryggspenna"     # Back-wrap from behind
    TACKLE = "tackle"               # Raw charge, both fall
    # ── In-Grapple Positional (require active GRAPPLED) ──
    CLINCH_IMPROVE = "clinch_improve"   # Fight for dominant grip
    LEG_TRIP = "leg_trip"               # Throw from dominant clinch
    HIP_THROW = "hip_throw"             # Mjaðartak — lift and slam
    GROUND_CONTROL = "ground_control"   # Scramble for mount
    THROAT_SEIZE = "throat_seize"       # Choke hold
    ARM_TRAP = "arm_trap"               # Lock weapon arm to body
    ELBOW_STRIKE = "elbow_strike"       # Short-range from clinch
    KNEE_STRIKE = "knee_strike"         # Midsection knee
    SLAM = "slam"                       # Drive into ground or wall
    WEAPON_PRESS = "weapon_press"       # Push opponent's weapon into them
    BREAK_DISTANCE = "break_distance"   # Exit grapple safely
    PIN_HOLD = "pin_hold"               # Full body pin
    # ── Glíma Specialist Finishers (Brawl ≥ 3 or glíma trait) ──
    GLIMA_LAS = "glima_las"                   # Back-heel trip takedown
    GLIMA_SNUNINGUR = "glima_snuningur"       # Hip rotation throw
    GLIMA_BEINHNYKKUR = "glima_beinhnykkur"   # Leg joint submission
    GLIMA_HNAKKATAK = "glima_hnakkatak"       # Nape/hair takedown
    # ── Dirty Tactics (melee range, any weapon) ──
    BITE = "bite"               # Flesh tear — face, hand, throat
    HEADBUTT = "headbutt"       # Close-range head strike
    NOSE_BUTT = "nose_butt"     # Deliberate nasal crush
    DIRT_EYES = "dirt_eyes"     # Environment debris blinding
    SPIT_EYES = "spit_eyes"     # Distraction spit
    HAIR_GRIP = "hair_grip"     # Beard or hair control
    THUMB_GOUGE = "thumb_gouge" # Eye socket or pressure point
    EAR_CUP = "ear_cup"         # Open-palm concussion strike


class ConditionType(Enum):
    """Status conditions that affect combat rolls and available actions."""
    PRONE = "prone"             # Knocked down
    STAGGERED = "staggered"     # Stunned briefly (1 round)
    WINDED = "winded"           # Exhausted (auto from low stamina)
    DAZED = "dazed"             # Head trauma (2 rounds)
    DISARMED = "disarmed"       # No weapon
    GRAPPLED = "grappled"       # Locked in close combat
    BOUND = "bound"             # Weapon controlled (1 round)
    # ── Grapple / close quarters ──
    CHOKED = "choked"               # Airway seized — 4 HP/round; no speech
    ARM_LOCKED = "arm_locked"       # Weapon arm pinned — cannot attack with it
    PINNED = "pinned"               # Body pin on ground — cannot act
    # ── Sensory / pain ──
    BLINDED = "blinded"             # Cannot see — -30 attack and defense
    BLEEDING_NOSE = "bleeding_nose" # -5 perception; blood in eyes
    PAIN_SHOCK = "pain_shock"       # -10 all actions, 1 round
    TUNNEL_VISION = "tunnel_vision" # Peripheral awareness collapse under pain spike
    # ── Awareness ──
    UNAWARE = "unaware"             # Caught off-guard — no reaction, -50 defense this round
    # ── Morale ──
    FLEEING = "fleeing"             # Panicked — fighter retreats, cannot attack
    HAMSTRUNG = "hamstrung"         # Leg tendon injury — stamina recovery halved
    MAUL_ACTIVE = "maul_active"     # Predator keeps bite pressure during grapple
    FROSTBITTEN = "frostbitten"     # Frost DOT: cold damage each round for d4 rounds
    SUPPRESSED = "suppressed"       # Under missile pressure — reduced action quality


class AmbientCondition(Enum):
    """Environmental factors that limit a fighter's perceptual awareness."""
    DARKNESS = "darkness"   # Cannot see at all — attacker penalty -20, no distance gauge
    NOISE    = "noise"      # Loud ambient sound — rear/flank approach undetectable
    OBSCURED = "obscured"   # Fog, smoke, heavy rain — -10 to both sides


class GrapplePosition(Enum):
    """Positional states within an active grapple."""
    CLINCH = "clinch"                     # Default entry — neither dominant
    NEUTRAL_CLINCH = "neutral_clinch"     # Deadlocked, both straining
    DOMINANT_CLINCH = "dominant_clinch"   # One fighter controls the grip
    TRIP_SETUP = "trip_setup"             # Glíma — one round from throw
    REAR_CONTROL = "rear_control"         # Behind opponent — best control
    MOUNTED = "mounted"                   # On top of grounded opponent
    GUARD_BOTTOM = "guard_bottom"         # Bottom — legs wrap attacker
    SIDE_CONTROL = "side_control"         # Top, across chest, no leg control


# ───────────────────────────────────────────────────────────────────────
# Constants
# ───────────────────────────────────────────────────────────────────────

STANCE_MODS = {
    Stance.AGGRESSIVE: {"attack": 10, "defense": -10, "damage": 1, "stamina_extra": 1, "init": 3},
    Stance.BALANCED:   {"attack": 0,  "defense": 0,   "damage": 0, "stamina_extra": 0, "init": 0},
    Stance.DEFENSIVE:  {"attack": -10,"defense": 10,  "damage": 0, "stamina_extra": 0, "init": -3},
    Stance.LOW_GUARD:  {"attack": -5, "defense": -5,  "damage": 0, "stamina_extra": 0, "init": -5},
}

MANEUVER_STAMINA = {
    Maneuver.CUT: 2,
    Maneuver.THRUST: 2,
    Maneuver.HEAVY_BLOW: 3,
    Maneuver.HALF_SWORD: 2,
    Maneuver.MORDSCHLAG: 3,
    Maneuver.BIND: 2,
    Maneuver.SHOVE: 2,
    Maneuver.GRAPPLE: 3,
    Maneuver.SHIELD_BASH: 2,
    Maneuver.DISARM: 2,
    Maneuver.FEINT: 2,
    Maneuver.STEP_IN: 1,
    Maneuver.STEP_BACK: 1,
    Maneuver.GUARD: 0,
    Maneuver.STAND: 2,
    Maneuver.PICK_UP_WEAPON: 1,
    Maneuver.SWITCH_WEAPON:  1,
    # ── Grapple entry ──
    Maneuver.BROKARTOK: 3,
    Maneuver.LAUSATOK: 2,
    Maneuver.HRYGGSPENNA: 3,
    Maneuver.TACKLE: 3,
    # ── In-grapple positional ──
    Maneuver.CLINCH_IMPROVE: 2,
    Maneuver.LEG_TRIP: 3,
    Maneuver.HIP_THROW: 4,
    Maneuver.GROUND_CONTROL: 3,
    Maneuver.THROAT_SEIZE: 2,
    Maneuver.ARM_TRAP: 2,
    Maneuver.ELBOW_STRIKE: 2,
    Maneuver.KNEE_STRIKE: 2,
    Maneuver.SLAM: 4,
    Maneuver.WEAPON_PRESS: 3,
    Maneuver.BREAK_DISTANCE: 2,
    Maneuver.PIN_HOLD: 3,
    # ── Glíma finishers ──
    Maneuver.GLIMA_LAS: 3,
    Maneuver.GLIMA_SNUNINGUR: 4,
    Maneuver.GLIMA_BEINHNYKKUR: 3,
    Maneuver.GLIMA_HNAKKATAK: 2,
    # ── Dirty tactics ──
    Maneuver.BITE: 1,
    Maneuver.HEADBUTT: 1,
    Maneuver.NOSE_BUTT: 1,
    Maneuver.DIRT_EYES: 1,
    Maneuver.SPIT_EYES: 0,
    Maneuver.HAIR_GRIP: 1,
    Maneuver.THUMB_GOUGE: 1,
    Maneuver.EAR_CUP: 2,
}

# Maneuvers available per weapon type (controls AI selection)
WEAPON_MANEUVERS = {
    "sword":       {"cut", "thrust", "heavy_blow", "feint", "bind", "half_sword", "mordschlag", "disarm", "step_in", "step_back"},
    "great_sword": {"cut", "thrust", "heavy_blow", "feint", "bind", "half_sword", "mordschlag", "disarm", "step_in", "step_back"},
    "hand_axe":    {"cut", "heavy_blow", "feint", "bind", "shove", "step_in", "step_back"},
    "long_axe":    {"cut", "heavy_blow", "feint", "bind", "shove", "step_in", "step_back"},
    "spear":       {"cut", "thrust", "feint", "bind", "shove", "step_in", "step_back"},
    "dagger":      {"cut", "thrust", "feint", "grapple", "step_in", "step_back"},
    "seax":        {"cut", "thrust", "feint", "step_in", "step_back"},
    "mace":        {"cut", "heavy_blow", "bind", "shove", "step_in", "step_back"},
    "unarmed": {
        "shove", "grapple",
        "brokartok", "lausatok", "hryggspenna", "tackle",
        "clinch_improve", "leg_trip", "hip_throw", "ground_control",
        "throat_seize", "arm_trap", "elbow_strike", "knee_strike",
        "slam", "weapon_press", "break_distance", "pin_hold",
        "glima_las", "glima_snuningur", "glima_beinhnykkur", "glima_hnakkatak",
        "bite", "headbutt", "nose_butt", "dirt_eyes", "spit_eyes",
        "hair_grip", "thumb_gouge", "ear_cup",
        "step_in", "step_back",
    },
    "generic":     {"cut", "thrust", "heavy_blow", "feint", "bind", "shove", "step_in", "step_back"},
}

CONDITION_EFFECTS = {
    ConditionType.PRONE:     {"attack": -10, "defense": -20},
    ConditionType.STAGGERED: {"attack": -10, "defense": -10},
    ConditionType.WINDED:    {"attack": -5,  "defense": -5},
    ConditionType.DAZED:     {"attack": -15, "defense": -15},
    ConditionType.DISARMED:  {"attack": -50, "defense": 0},
    ConditionType.GRAPPLED:  {"attack": -20, "defense": -10},
    ConditionType.BOUND:         {"attack": -20, "defense": -10},
    # ── Grapple / close quarters ──
    ConditionType.CHOKED:        {"attack": -20, "defense": -10},
    ConditionType.ARM_LOCKED:    {"attack": -40, "defense": 0},
    ConditionType.PINNED:        {"attack": -50, "defense": -30},
    # ── Sensory / pain ──
    ConditionType.BLINDED:       {"attack": -30, "defense": -30},
    ConditionType.BLEEDING_NOSE: {"attack": -5,  "defense": 0},
    ConditionType.PAIN_SHOCK:    {"attack": -10, "defense": -10},
    ConditionType.TUNNEL_VISION: {"attack": -5,  "defense": -15},
    ConditionType.UNAWARE:       {"attack":   0, "defense": -50},
    ConditionType.HAMSTRUNG:     {"attack":   0, "defense": 0},
    ConditionType.MAUL_ACTIVE:   {"attack":   0, "defense": 0},
    ConditionType.FLEEING:       {"attack": -30, "defense": -20},
    ConditionType.FROSTBITTEN:   {"attack":  -5, "defense":  -5},
    ConditionType.SUPPRESSED:    {"attack": -10, "defense":  -5},
}

MISSILE_WEAPONS: frozenset[str] = frozenset({
    "bow", "shortbow", "longbow", "crossbow",
    "javelin", "throwing_axe", "sling",
})

ATTACK_MANEUVERS = {
    Maneuver.CUT, Maneuver.THRUST, Maneuver.HEAVY_BLOW,
    Maneuver.HALF_SWORD, Maneuver.MORDSCHLAG,
}

CONTROL_MANEUVERS = {
    Maneuver.BIND, Maneuver.SHOVE, Maneuver.GRAPPLE,
    Maneuver.SHIELD_BASH, Maneuver.DISARM,
}

STANCE_DESC = {
    Stance.AGGRESSIVE: "presses forward",
    Stance.BALANCED:   "maintains guard",
    Stance.DEFENSIVE:  "steps back, measures",
    Stance.LOW_GUARD:  "drops guard low, waits",
}

MANEUVER_HIT_DESC = {
    "cut":            "cuts at",
    "thrust":         "thrusts at",
    "heavy_blow":     "brings a heavy blow upon",
    "half_sword":     "half-swords into",
    "mordschlag":     "reverses grip, strikes",
    "bind":           "binds",
    "shove":          "shoves",
    "grapple":        "seizes",
    "shield_bash":    "bashes",
    "disarm":         "strips the weapon from",
    "feint":          "feints at",
    "step_in":        "steps into range at",
    "step_back":      "steps back from",
    "guard":          "holds guard",
    "counter":        "counters",
    "stand":          "rises",
    "pick_up_weapon": "retrieves weapon",
    # ── Grapple entry ──
    "brokartok":     "seizes for a belt-throw at",
    "lausatok":      "collar-ties",
    "hryggspenna":   "back-wraps",
    "tackle":        "charges and tackles",
    # ── In-grapple ──
    "clinch_improve":  "fights for dominant grip on",
    "leg_trip":        "trips",
    "hip_throw":       "hip-throws",
    "ground_control":  "scrambles for mount on",
    "throat_seize":    "seizes the throat of",
    "arm_trap":        "locks the arm of",
    "elbow_strike":    "drives an elbow into",
    "knee_strike":     "drives a knee into",
    "slam":            "slams",
    "weapon_press":    "presses the weapon of",
    "break_distance":  "breaks free from",
    "pin_hold":        "pins",
    # ── Glíma finishers ──
    "glima_las":         "back-heels",
    "glima_snuningur":   "rotation-throws",
    "glima_beinhnykkur": "leg-snaps",
    "glima_hnakkatak":   "nape-slams",
    # ── Dirty tactics ──
    "bite":        "bites",
    "headbutt":    "headbutts",
    "nose_butt":   "nose-butts",
    "dirt_eyes":   "throws grit at the eyes of",
    "spit_eyes":   "spits at",
    "hair_grip":   "grips the hair of",
    "thumb_gouge": "thumb-gouges",
    "ear_cup":     "ear-cups",
}


# Grapple weapon modifiers: in-grapple attack bonus and AI grapple willingness
GRAPPLE_WEAPON_MODIFIERS: dict[str, dict] = {
    "unarmed":    {"attack": 0,   "willingness": 20},
    "dagger":     {"attack": 10,  "willingness": 15},
    "seax":       {"attack": 10,  "willingness": 15},
    "hand_axe":   {"attack": -5,  "willingness": 0},
    "mace":       {"attack": -5,  "willingness": 0},
    "sword":      {"attack": -15, "willingness": -10},
    "spear":      {"attack": -30, "willingness": -20},
    "long_axe":   {"attack": -40, "willingness": -30},
    "great_sword":{"attack": -40, "willingness": -30},
    "generic":    {"attack": -10, "willingness": -5},
    "shield":     {"attack": -10, "willingness": -5},
    "improvised": {"attack": -5,  "willingness": 0},
}

# Maneuver category sets used by can_maneuver() and resolve_fighter_action()
GRAPPLE_ENTRY_MANEUVERS: frozenset = frozenset({
    Maneuver.BROKARTOK, Maneuver.LAUSATOK, Maneuver.HRYGGSPENNA, Maneuver.TACKLE,
})
IN_GRAPPLE_MANEUVERS: frozenset = frozenset({
    Maneuver.CLINCH_IMPROVE, Maneuver.LEG_TRIP, Maneuver.HIP_THROW,
    Maneuver.GROUND_CONTROL, Maneuver.THROAT_SEIZE, Maneuver.ARM_TRAP,
    Maneuver.ELBOW_STRIKE, Maneuver.KNEE_STRIKE, Maneuver.SLAM,
    Maneuver.WEAPON_PRESS, Maneuver.BREAK_DISTANCE, Maneuver.PIN_HOLD,
})
GLIMA_FINISHER_MANEUVERS: frozenset = frozenset({
    Maneuver.GLIMA_LAS, Maneuver.GLIMA_SNUNINGUR,
    Maneuver.GLIMA_BEINHNYKKUR, Maneuver.GLIMA_HNAKKATAK,
})
DIRTY_MANEUVERS: frozenset = frozenset({
    Maneuver.BITE, Maneuver.HEADBUTT, Maneuver.NOSE_BUTT, Maneuver.DIRT_EYES,
    Maneuver.SPIT_EYES, Maneuver.HAIR_GRIP, Maneuver.THUMB_GOUGE, Maneuver.EAR_CUP,
})

# ───────────────────────────────────────────────────────────────────────
# Weapon Reach & Distance System
# ───────────────────────────────────────────────────────────────────────

# Discrete combat distance bands (0 = body contact, 3 = polearm range)
DIST_GRAPPLE = 0   # 0–40 cm  — grapple / unarmed territory
DIST_CLOSE   = 1   # 40–90 cm — dagger, axe, short blade
DIST_MELEE   = 2   # 90–150 cm — sword range (default starting distance)
DIST_LONG    = 3   # 150–250 cm — spear / polearm territory

# Per-weapon reach data (reach: 0–5 tier, min/max band: optimal range, foul_band: ≤ this → haft only)
WEAPON_REACH_TABLE: dict[str, dict] = {
    "unarmed":    {"reach": 0, "min_band": 0, "max_band": 0, "foul_band": -1},
    "dagger":     {"reach": 1, "min_band": 0, "max_band": 1, "foul_band": -1},
    "seax":       {"reach": 1, "min_band": 0, "max_band": 1, "foul_band": -1},
    "hand_axe":   {"reach": 2, "min_band": 0, "max_band": 2, "foul_band": -1},
    "mace":       {"reach": 2, "min_band": 0, "max_band": 2, "foul_band": -1},
    "sword":      {"reach": 3, "min_band": 1, "max_band": 2, "foul_band": -1},
    "great_sword":{"reach": 4, "min_band": 2, "max_band": 3, "foul_band": 0},
    "long_axe":   {"reach": 4, "min_band": 2, "max_band": 3, "foul_band": 0},
    "spear":      {"reach": 5, "min_band": 2, "max_band": 3, "foul_band": 1},
    "generic":    {"reach": 3, "min_band": 1, "max_band": 2, "foul_band": -1},
    "improvised": {"reach": 2, "min_band": 0, "max_band": 2, "foul_band": -1},
    "shield":     {"reach": 2, "min_band": 0, "max_band": 2, "foul_band": -1},
}


def get_weapon_reach(weapon_type: str) -> int:
    """Return the reach tier (0–5) for a weapon type."""
    return WEAPON_REACH_TABLE.get(weapon_type, WEAPON_REACH_TABLE["generic"])["reach"]


def compute_reach_penalty(weapon_type: str, distance_band: int) -> tuple:
    """Return (attack_mod, is_fouled, base_override | None).

    attack_mod < 0 when outside effective range.
    is_fouled True when weapon is inside its own guard — haft-only.
    base_override replaces weapon_base when fouled.
    """
    data = WEAPON_REACH_TABLE.get(weapon_type, WEAPON_REACH_TABLE["generic"])
    if data["foul_band"] >= 0 and distance_band <= data["foul_band"]:
        return (-30, True, 3)                       # fouled — haft-only strike
    if distance_band < data["min_band"]:
        excess = data["min_band"] - distance_band
        return (-(15 * excess), False, None)        # too close for this weapon
    if distance_band > data["max_band"]:
        excess = distance_band - data["max_band"]
        return (-(20 * excess), False, None)        # out of reach
    return (0, False, None)                         # in optimal band


def preferred_distance_band(weapon_type: str) -> int:
    """Return the AI-preferred distance band for this weapon type."""
    data = WEAPON_REACH_TABLE.get(weapon_type, WEAPON_REACH_TABLE["generic"])
    foul = data["foul_band"]
    min_b = max(data["min_band"], foul + 1)         # stay above foul threshold
    max_b = data["max_band"]
    # Prefer upper end of optimal range (stay at distance if possible)
    return max(min_b, (min_b + max_b + 1) // 2)


# ── Weapon Size Tiers (0 = unarmed/no footprint, 5 = polearm) ──
WEAPON_SIZE_TABLE: dict[str, int] = {
    "unarmed":     0,  # fists — minimal footprint
    "dagger":      1,  # easily concealed; thrives in close quarters
    "seax":        1,
    "hand_axe":    2,
    "mace":        2,
    "sword":       3,  # one-handed arming sword / messer
    "generic":     3,
    "improvised":  2,
    "shield":      2,  # weapon hand only; shield column handled elsewhere
    "great_sword": 4,  # two-handed longsword / zweihänder
    "long_axe":    4,
    "spear":       5,  # polearm — worst-case in restricted space
}

# Maps terrain_context string → abstract space tier
TERRAIN_SPACE_CLASS: dict[str, str] = {
    "open":         "free",       # open field, shore, cleared courtyard
    "stone":        "free",       # stone hall or castle yard with full headroom
    "winter":       "free",       # snow field (footwork affected, not swing arc)
    "sand":         "free",       # beach combat (footwork affected, not swing arc)
    "ship":         "moderate",   # ship deck — room but uneven underfoot
    "interior":     "moderate",   # longhouse, tavern, average indoor room
    "forest":       "moderate",   # sparse trees — trunks obstruct lateral angles
    "narrow":       "tight",      # corridor, alley, doorway, ravine bottleneck
    "forest_dense": "tight",      # dense woodland — limbs and trunks everywhere
    "crowd":        "packed",     # surrounded by combatants; friendly-fire risk
    "barrow":       "very_tight", # burial mound tunnel or cave crawlway
    "low_ceiling":  "very_tight", # cellar, mine drift, collapsed structure
}

# Attack roll modifier by (space_class, weapon_size)
# Positive = short weapons gain advantage; negative = large weapons are hampered
TERRAIN_SIZE_ATTACK_MODS: dict[str, dict[int, int]] = {
    #              sz0   sz1   sz2   sz3    sz4    sz5
    "free":       {0:  0, 1:  0, 2:  0, 3:  0, 4:   0, 5:   0},
    "moderate":   {0:  0, 1:  0, 2:  0, 3: -5, 4: -15, 5: -25},
    "tight":      {0:  5, 1:  5, 2:  0, 3:-10, 4: -25, 5: -40},
    "very_tight": {0: 10, 1: 15, 2:  5, 3:-20, 4: -40, 5: -60},
    "packed":     {0:  0, 1:  5, 2:  0, 3:-10, 4: -20, 5: -30},
}

# Extra stamina cost per offensive/control action for large weapons in restricted spaces
TERRAIN_SIZE_STAMINA_EXTRA: dict[str, dict[int, int]] = {
    #              sz0  sz1  sz2  sz3  sz4  sz5
    "free":       {0:0, 1:0, 2:0, 3:0, 4:0, 5:0},
    "moderate":   {0:0, 1:0, 2:0, 3:0, 4:1, 5:1},
    "tight":      {0:0, 1:0, 2:0, 3:1, 4:2, 5:3},
    "very_tight": {0:0, 1:0, 2:1, 3:2, 4:3, 5:4},
    "packed":     {0:0, 1:0, 2:0, 3:1, 4:2, 5:2},
}


def get_weapon_size(weapon_type: str) -> int:
    """Return physical size tier (0–5) for a weapon type."""
    return WEAPON_SIZE_TABLE.get(weapon_type, WEAPON_SIZE_TABLE.get("generic", 3))


def get_space_class(terrain_context: str) -> str:
    """Return the abstract space tier for a terrain context string."""
    return TERRAIN_SPACE_CLASS.get(terrain_context, "free")


def compute_terrain_penalty(weapon_type: str, terrain_context: str) -> int:
    """Attack modifier for this weapon type in this terrain space (negative = penalty)."""
    size = get_weapon_size(weapon_type)
    space = get_space_class(terrain_context)
    return TERRAIN_SIZE_ATTACK_MODS[space][size]


def terrain_stamina_extra(weapon_type: str, terrain_context: str) -> int:
    """Extra stamina cost for offensive/control actions with large weapons in tight spaces."""
    size = get_weapon_size(weapon_type)
    space = get_space_class(terrain_context)
    return TERRAIN_SIZE_STAMINA_EXTRA[space][size]


