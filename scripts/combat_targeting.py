"""combat_targeting.py — Smart skirmish target selection and commander orders.

Replaces random.choice() in run_skirmish() with score-based selection that
accounts for:
  - Target stickiness (memory across rounds)
  - Commander-issued focus orders
  - Wounded / low-HP finishing preference
  - Role-based threat prioritisation (casters, archers, commanders)
  - Anti-overassignment (avoid stacking too many attackers on one enemy)
  - Fighter discipline affecting priority adherence and order obedience

Public API
----------
choose_skirmish_target(attacker, candidates, ally_assignments, active_orders,
                       round_num) -> Fighter
commander_issue_orders(side, enemy_side, round_num) -> dict[str, str]
infer_combat_role(fighter) -> str
infer_discipline(fighter) -> int
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from combat_types import ConditionType

if TYPE_CHECKING:
    from combat_model import Fighter

# ───────────────────────────────────────────────────────────────────────
# Role classification sets
# ───────────────────────────────────────────────────────────────────────

_CASTER_TRAITS: frozenset[str] = frozenset({
    "galdr", "galdr_worker", "seidr", "seidr_worker",
    "magic_aura", "curse_on_hit", "death_command",
    "lure_song", "frostbitten", "reality_warping",
    "warp_strike", "ley_anchor", "curse_hex",
    "prepared_ground",
})

_RANGED_WEAPONS: frozenset[str] = frozenset({
    "bow", "shortbow", "longbow", "crossbow",
    "javelin", "throwing_axe", "sling",
})

_COMMANDER_TRAITS: frozenset[str] = frozenset({
    "rally_allies", "veteran_eye", "pack_leader",
    "shield_wall_anchor", "death_command",
})

_BRUTE_WEAPONS: frozenset[str] = frozenset({
    "great_axe", "maul", "two_handed_axe", "two_handed_sword",
    "warhammer", "flail",
})

_SKIRMISHER_WEAPONS: frozenset[str] = frozenset({
    "hand_axe", "knife", "seax", "short_sword", "dagger",
    "buckler_and_knife",
})

# Maximum allies the commander directs onto a single focus target per round
_MAX_FOCUS_STACK = 3

# Obedience probability by discipline tier (0-3)
_OBEDIENCE_PROB: dict[int, float] = {0: 0.15, 1: 0.45, 2: 0.70, 3: 1.00}

# Noise injected per discipline tier (lower discipline = wilder target choice)
_NOISE_BY_DISC: dict[int, float] = {0: 8.0, 1: 5.0, 2: 2.5, 3: 0.5}

# Threat weight per role (how urgently we want to eliminate this role)
_ROLE_THREAT: dict[str, float] = {
    "caster":    12.0,
    "archer":     8.0,
    "commander":  6.0,
    "support":    5.0,
    "brute":      4.0,
    "skirmisher": 3.0,
    "line":       2.0,
}


# ───────────────────────────────────────────────────────────────────────
# Role and discipline inference
# ───────────────────────────────────────────────────────────────────────

def infer_combat_role(fighter: "Fighter") -> str:
    """Derive a combat role string from Fighter metadata.

    Returns one of: line | skirmisher | archer | caster | commander | brute | support.
    An explicit non-empty combat_role field always wins.
    Falls back to 'line' if no better fit is found.
    """
    explicit = getattr(fighter, "combat_role", "")
    if explicit:
        return explicit

    traits = set(getattr(fighter, "traits", []))
    wt = getattr(fighter, "weapon_type", "generic")

    # Caster check first (trait-driven, weapon-agnostic)
    if traits & _CASTER_TRAITS:
        return "caster"

    # Commander check
    if traits & _COMMANDER_TRAITS:
        return "commander"

    # Ranged
    if wt in _RANGED_WEAPONS:
        return "archer"

    # Brute — slow and heavy two-handed brawler
    if wt in _BRUTE_WEAPONS:
        return "brute"

    # Skirmisher — light / fast weapons
    if wt in _SKIRMISHER_WEAPONS:
        return "skirmisher"

    # Default: line fighter
    return "line"


def infer_discipline(fighter: "Fighter") -> int:
    """Derive a 0–3 discipline score for obedience and priority adherence.

    3 = veteran captain who always follows tactical priorities.
    0 = berserker, beast, or poorly-controlled creature.
    An explicit non-negative discipline field always wins.
    """
    explicit = getattr(fighter, "discipline", -1)
    if explicit >= 0:
        return int(explicit)

    traits = set(getattr(fighter, "traits", []))

    # Discipline-breaking states
    if any(t in traits for t in ("frenzy", "berserker_rage", "territorial_rage")):
        return 0
    if getattr(fighter, "is_undead", False) and "combat_memory" not in traits:
        return 0

    d = 0
    if getattr(fighter, "weapon_skill", 1) >= 3:
        d += 1
    if getattr(fighter, "wil", 5) >= 6:
        d += 1
    if getattr(fighter, "wit", 5) >= 6:
        d += 1
    if any(t in traits for t in ("veteran_eye", "pack_leader", "rally_allies")):
        d += 1

    return min(d, 3)


# ───────────────────────────────────────────────────────────────────────
# Target scoring
# ───────────────────────────────────────────────────────────────────────

def score_target(
    attacker: "Fighter",
    candidate: "Fighter",
    ally_assignments: dict[str, int],
    active_orders: dict[str, str],
    round_num: int,
) -> float:
    """Score candidate as a potential target for attacker. Higher = more preferred.

    Pure function — no side effects, no randomness. Discipline-scaled noise is
    added separately in choose_skirmish_target().
    """
    score: float = 0.0

    # ── Commander order — highest weight ──
    if active_orders.get(attacker.name) == candidate.name:
        score += 20.0

    # ── Target stickiness (commitment across rounds) ──
    if getattr(attacker, "current_target_name", "") == candidate.name:
        # Gain increases with turns on target, capped at 8 points
        turns = getattr(attacker, "turns_on_target", 0)
        score += min(turns * 1.5, 8.0)

    # ── HP / wounded finishing ──
    max_hp = max(1, candidate.max_hp)
    hp_ratio = candidate.hp / max_hp
    if hp_ratio <= 0.25:
        score += 15.0   # death-quarter: finish it now
    elif hp_ratio <= 0.50:
        score += 8.0    # bloodied / half HP
    elif hp_ratio <= 0.75:
        score += 2.0    # moderate damage

    # ── Bloodied status extra signal ──
    if getattr(candidate, "bloodied_triggered", False):
        score += 3.0

    # ── Role-based threat ──
    role = infer_combat_role(candidate)
    score += _ROLE_THREAT.get(role, 2.0)

    # ── Anti-overassignment ──
    assigned = ally_assignments.get(candidate.name, 0)
    if assigned >= 4:
        score -= 15.0   # severe overassignment — redistribute
    elif assigned >= 3:
        score -= 8.0
    elif assigned >= 2:
        score -= 2.0    # two on one is acceptable

    # ── Death-effect targets ──
    # Minor nudge to burst down dangerous AOE/aura death effects early
    if getattr(candidate, "death_effects", []):
        score += 2.0

    return score


# ───────────────────────────────────────────────────────────────────────
# Target selection
# ───────────────────────────────────────────────────────────────────────

def choose_skirmish_target(
    attacker: "Fighter",
    candidates: list["Fighter"],
    ally_assignments: dict[str, int],
    active_orders: dict[str, str],
    round_num: int,
) -> "Fighter":
    """Choose the best target for attacker from non-down candidates.

    Falls back to random.choice() for impulsive fighters (beasts, frenzied,
    undead without combat_memory) so their chaotic behaviour is preserved.
    """
    if not candidates:
        raise ValueError("choose_skirmish_target: candidates list is empty")
    if len(candidates) == 1:
        return candidates[0]

    traits = set(getattr(attacker, "traits", []))
    is_impulsive = (
        any(t in traits for t in ("frenzy", "berserker_rage", "territorial_rage", "bestial"))
        or (
            getattr(attacker, "is_undead", False)
            and "combat_memory" not in traits
        )
    )

    if is_impulsive:
        # Purely random — no tactical awareness
        return random.choice(candidates)

    discipline = infer_discipline(attacker)
    noise_scale = _NOISE_BY_DISC.get(discipline, 5.0)

    scored: list[tuple["Fighter", float]] = []
    for c in candidates:
        base = score_target(attacker, c, ally_assignments, active_orders, round_num)
        noise = random.uniform(0.0, noise_scale)
        scored.append((c, base + noise))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[0][0]


# ───────────────────────────────────────────────────────────────────────
# Commander order generation
# ───────────────────────────────────────────────────────────────────────

def commander_issue_orders(
    side: list["Fighter"],
    enemy_side: list["Fighter"],
    round_num: int,
) -> dict[str, str]:
    """Return a mapping {fighter_name -> target_name} for eligible allies.

    Only command-capable fighters can issue orders. The focus target is the
    highest-priority threat on the enemy side. Obedience is probabilistic —
    low-discipline fighters may ignore orders. Returns {} if no commander is
    active or no enemies remain.
    """
    active_side = [f for f in side if not f.is_down]
    enemies = [e for e in enemy_side if not e.is_down]
    if not active_side or not enemies:
        return {}

    # Find eligible commanders
    commanders = [
        f for f in active_side
        if (
            infer_combat_role(f) == "commander"
            or any(t in getattr(f, "traits", []) for t in _COMMANDER_TRAITS)
        )
    ]
    if not commanders:
        return {}

    # Use the highest-discipline commander
    commanders.sort(key=lambda f: infer_discipline(f), reverse=True)
    commander = commanders[0]

    focus = _pick_focus_target(enemies, commander)
    if focus is None:
        return {}

    orders: dict[str, str] = {}
    assigned_count = 0

    # Assign orders to allies (excluding commander), most-disciplined first
    allies = sorted(
        [f for f in active_side if f is not commander],
        key=lambda f: infer_discipline(f),
        reverse=True,
    )

    for ally in allies:
        if assigned_count >= _MAX_FOCUS_STACK:
            break
        disc = infer_discipline(ally)
        threshold = _OBEDIENCE_PROB.get(disc, 0.45)
        if random.random() < threshold:
            orders[ally.name] = focus.name
            assigned_count += 1

    return orders


def _pick_focus_target(
    enemies: list["Fighter"],
    commander: "Fighter",
) -> "Fighter | None":
    """Select the highest-priority enemy for the commander to call out."""
    if not enemies:
        return None

    # Priority: eliminate backline threats first
    for priority_role in ("caster", "archer", "commander"):
        for e in enemies:
            if infer_combat_role(e) == priority_role:
                return e

    # Finish most wounded
    bloodied = [e for e in enemies if getattr(e, "bloodied_triggered", False)]
    if bloodied:
        return min(bloodied, key=lambda e: e.hp)

    # Fallback: highest raw threat (weapon_base + mig)
    return max(
        enemies,
        key=lambda e: getattr(e, "weapon_base", 6) + getattr(e, "mig", 5),
    )


# ───────────────────────────────────────────────────────────────────────
# Prompt 4 — skirmish chaos targeting (perception economy + command friction)
# ───────────────────────────────────────────────────────────────────────

def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def compute_attention_budget(
    fighter: "Fighter",
    local_noise: int,
    incoming_threats: list[str],
) -> int:
    """Compute per-round attention budget (1..5) for skirmish perception.

    Budget is consumed by tracking current opponent, scanning, and command parsing.
    Under overload, budget shrinks and awareness quality collapses.
    """
    discipline = infer_discipline(fighter)
    base = int(getattr(fighter, "attention_budget_base", 2))
    awareness = int(getattr(fighter, "awareness", 2))
    noise_tol = int(getattr(fighter, "combat_noise_tolerance", 2))

    budget = base
    budget += awareness // 2
    budget += discipline // 2
    budget += 1 if getattr(fighter, "wit", 5) >= 7 else 0

    # Stress / injury / chaos penalties
    budget -= int(getattr(fighter, "stress_load", 0)) // 30
    budget -= int(getattr(fighter, "wound_penalty", 0)) // 20
    budget -= max(0, local_noise - noise_tol) // 2
    budget -= max(0, len(incoming_threats) - 1)

    if getattr(fighter, "has_condition", None):
        if fighter.has_condition(ConditionType.DAZED):
            budget -= 1
        if fighter.has_condition(ConditionType.TUNNEL_VISION):
            budget -= 1
        if fighter.has_condition(ConditionType.FLEEING):
            budget -= 1

    return int(_clamp(budget, 1, 5))


def resolve_order_state(
    fighter: "Fighter",
    has_order: bool,
    local_noise: int,
) -> str:
    """Resolve command reception quality in skirmish chaos."""
    if not has_order:
        return "none"

    discipline = infer_discipline(fighter)
    base = float(getattr(fighter, "order_reliability", 0.65))
    clarity = base + 0.10 * discipline - 0.04 * local_noise
    clarity -= int(getattr(fighter, "stress_load", 0)) / 200.0
    clarity = float(_clamp(clarity, 0.05, 0.95))

    r = random.random()
    if r <= clarity:
        return "received_clear"
    if r <= min(1.0, clarity + 0.20):
        return "received_partial"
    if r <= min(1.0, clarity + 0.40):
        return "heard_but_ignored"
    return "not_received"


def build_perception_snapshot(
    fighter: "Fighter",
    candidates: list["Fighter"],
    incoming_threats: list[str],
    local_noise: int,
    round_num: int,
) -> dict:
    """Build focused/noticed/glimpsed target tiers for this round."""
    budget = compute_attention_budget(fighter, local_noise, incoming_threats)
    remaining = list(candidates)
    focused: list[str] = []
    noticed: list[str] = []
    glimpsed: list[str] = []

    # 1) Maintain current target track when possible.
    cur = getattr(fighter, "current_target_name", "")
    if cur and any(c.name == cur for c in remaining):
        focused.append(cur)
        remaining = [c for c in remaining if c.name != cur]

    # 2) Immediate contact threats (who attacked me recently).
    for name in incoming_threats:
        if len(focused) >= 1:
            break
        if any(c.name == name for c in remaining):
            focused.append(name)
            remaining = [c for c in remaining if c.name != name]

    # 3) Fill noticed list by highest local threat, constrained by budget.
    notice_slots = max(0, budget - len(focused))
    ranked = sorted(
        remaining,
        key=lambda c: score_target(fighter, c, {}, {}, round_num),
        reverse=True,
    )
    for c in ranked[:notice_slots]:
        noticed.append(c.name)

    # 4) A few low-confidence glimpses under overload.
    left = [c for c in remaining if c.name not in noticed]
    glimpse_slots = 1 if budget <= 2 else 2
    for c in left[:glimpse_slots]:
        glimpsed.append(c.name)

    unseen_count = max(0, len(candidates) - len(focused) - len(noticed) - len(glimpsed))

    # Write transient per-round state back to fighter.
    fighter.focused_target = focused[0] if focused else ""
    fighter.noticed_targets = noticed
    fighter.glimpsed_targets = glimpsed
    fighter.unseen_threat_count = unseen_count
    fighter.orientation_commitment = int(_clamp(
        35 + getattr(fighter, "turns_on_target", 0) * 12,
        20,
        95,
    ))
    if unseen_count > 0 and budget <= 2:
        fighter.last_rear_alert_round = round_num

    return {
        "budget": budget,
        "focused": list(focused),
        "noticed": list(noticed),
        "glimpsed": list(glimpsed),
        "unseen_count": unseen_count,
    }


def choose_skirmish_target_perception(
    attacker: "Fighter",
    candidates: list["Fighter"],
    ally_assignments: dict[str, int],
    active_orders: dict[str, str],
    round_num: int,
    incoming_threats: list[str] | None = None,
    local_noise: int = 0,
) -> tuple["Fighter", dict]:
    """Skirmish-mode target choice constrained by perception tiers.

    Returns (target, metadata) where metadata includes awareness and order-state
    fields for logs and narrative.
    """
    if not candidates:
        raise ValueError("choose_skirmish_target_perception: candidates list is empty")
    if len(candidates) == 1:
        return candidates[0], {
            "budget": 1,
            "focused": [candidates[0].name],
            "noticed": [],
            "glimpsed": [],
            "unseen_count": 0,
            "order_state": "none",
        }

    incoming = incoming_threats or []
    snap = build_perception_snapshot(attacker, candidates, incoming, local_noise, round_num)

    has_order = attacker.name in active_orders
    order_state = resolve_order_state(attacker, has_order, local_noise)
    attacker.order_state = order_state

    candidate_map = {c.name: c for c in candidates}
    perceived_names = snap["focused"] + snap["noticed"]
    if not perceived_names:
        perceived_names = list(snap["glimpsed"])
    if not perceived_names:
        perceived_names = [random.choice(candidates).name]

    # Command friction filter
    effective_order_target = None
    if has_order and order_state == "received_clear":
        ordered = active_orders[attacker.name]
        if ordered in perceived_names:
            effective_order_target = ordered
    elif has_order and order_state == "received_partial":
        ordered = active_orders[attacker.name]
        ordered_f = candidate_map.get(ordered)
        if ordered_f is not None:
            role = infer_combat_role(ordered_f)
            same_role = [n for n in perceived_names if infer_combat_role(candidate_map[n]) == role]
            if same_role:
                effective_order_target = random.choice(same_role)

    effective_orders = {attacker.name: effective_order_target} if effective_order_target else {}

    discipline = infer_discipline(attacker)
    noise_scale = _NOISE_BY_DISC.get(discipline, 5.0) + max(0.0, local_noise * 0.25)

    # Tunnel-lock under overload: often keep existing target if still perceived.
    cur = getattr(attacker, "current_target_name", "")
    if (snap["budget"] <= 1 and cur in perceived_names and random.random() < 0.70):
        return candidate_map[cur], {**snap, "order_state": order_state, "perceived": perceived_names}

    scored: list[tuple["Fighter", float]] = []
    for name in perceived_names:
        c = candidate_map[name]
        score = score_target(attacker, c, ally_assignments, effective_orders, round_num)
        if name in incoming:
            score += 6.0   # immediate threat in your face
        if name in snap["glimpsed"]:
            score -= 2.0   # low-confidence awareness
        score += random.uniform(0.0, noise_scale)
        scored.append((c, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    chosen = scored[0][0]
    return chosen, {**snap, "order_state": order_state, "perceived": perceived_names}


def compute_directional_engagement(
    attacker: "Fighter",
    defender: "Fighter",
    attackers_on_defender: int,
) -> dict:
    """Compute front/flank/rear modifiers in skirmish mode.

    Returns dict with:
      vector: front|flank|rear
      attack_mod: int
      defense_mod: int  (applied to defender roll; negative means weaker defense)
      surprise: bool
      severity_shift: int
    """
    focused = getattr(defender, "focused_target", "")
    noticed = set(getattr(defender, "noticed_targets", []) or [])

    if focused == attacker.name:
        return {
            "vector": "front",
            "attack_mod": 0,
            "defense_mod": 0,
            "surprise": False,
            "severity_shift": 0,
        }

    unseen = attacker.name not in noticed and focused != attacker.name

    if unseen and attackers_on_defender >= 2:
        return {
            "vector": "rear",
            "attack_mod": 20,
            "defense_mod": -25,
            "surprise": True,
            "severity_shift": 1,
        }
    if unseen:
        return {
            "vector": "flank",
            "attack_mod": 10,
            "defense_mod": -15,
            "surprise": True,
            "severity_shift": 0,
        }
    if attackers_on_defender >= 3:
        return {
            "vector": "flank",
            "attack_mod": 6,
            "defense_mod": -8,
            "surprise": False,
            "severity_shift": 0,
        }

    return {
        "vector": "front",
        "attack_mod": 0,
        "defense_mod": 0,
        "surprise": False,
        "severity_shift": 0,
    }
