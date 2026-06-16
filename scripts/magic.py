#!/usr/bin/env python3
"""
Iron Ledger — Norse Magic Simulator

Simulates all three magical traditions (galdr, seiðr, wyrd-reading) with
full cost resolution, rank-gated effects, failure consequences, practitioner
degradation tracking, and political magic integration.

All rules from 20_SIMULATION_RULES.md §11, §11.8, §11.9.

Usage:
    python magic.py galdr --wyrd 6 --rune-lore 3 --rank 3
    python magic.py seidr --wyrd 7 --spirit-lore 4 --rank 4 --gender male
    python magic.py wyrd-read --wyrd 5 --skill 2 --rank 2
    python magic.py degrade --tradition galdr --years-active 18 --willpower-spent 140 --toughness 5 --will 4
    python magic.py ward-right --reputation 4 --rune-lore 3 --overjarl-favor 1
    python magic.py testimony --wyrd 7 --spirit-lore 4 --union iron_grip
    python magic.py curse --rune-lore 4 --grievance 3 --defender-rep 3
    python magic.py accuse --testimony-weight 28 --evidence 3 --accused-rep 3 --concealment 2
"""

import argparse
import json
import math
import sys

import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import (
    resolve_galdr,
    resolve_seidr,
    resolve_wyrd_reading,
    galdr_failure_consequence,
    roll_d100,
    roll_sum,
    ResultLevel,
)


# ─── §11.1–11.3: Costs by rank ───────────────────────────────────────────────

GALDR_WILL_COSTS = {
    1: 1,
    2: 1,
    3: 2,
    4: 3,
    5: 5,
}

GALDR_BASE_STAMINA_COSTS = {
    1: 1,
    2: 2,
    3: 4,
    4: 6,
    5: 8,
}

GALDR_HP_COST_PCT = {
    3: 0.10,
    4: 0.22,
    5: 0.33,
}

GALDR_HP_COST_MIN = {
    3: 3,
    4: 6,
    5: 9,
}


def compute_galdr_cost(rank: int, max_hp: int | None = None,
                       max_stamina: int | None = None) -> dict:
    """Return the full cost profile for a galdr working at the given rank."""
    if rank < 1 or rank > 5:
        raise ValueError("Galdr rank must be 1-5.")

    if max_hp is None:
        max_hp = 25
    if max_stamina is None:
        max_stamina = 20

    hp_blood = 0
    if rank >= 3:
        hp_blood = max(
            GALDR_HP_COST_MIN[rank],
            math.ceil(max_hp * GALDR_HP_COST_PCT[rank]),
        )

    return {
        "willpower": GALDR_WILL_COSTS[rank],
        "stamina": GALDR_BASE_STAMINA_COSTS[rank],
        "hp_blood": hp_blood,
        "material_required": rank >= 4,
        "rare_material": rank >= 5,
        "strain_note": (
            "Blood and breath are both spent; higher-rank galdr is visibly draining."
            if rank >= 3 else
            "Minor rune-work is tiring but not yet life-shortening."
        ),
    }


def apply_kvaedi_exertion(rank: int, kvaedi_quality: int,
                          current_stamina: int, current_hp: int,
                          max_stamina: int | None = None,
                          singing: bool = True) -> dict:
    """Apply chant-maintenance fatigue, including HP spillover and divine stroke."""
    if rank < 1 or rank > 5:
        raise ValueError("Galdr rank must be 1-5.")
    if kvaedi_quality < 0 or kvaedi_quality > 4:
        raise ValueError("kvaedi_quality must be 0-4.")

    if max_stamina is None:
        max_stamina = max(current_stamina, 1)

    drain = max(1, rank + max(0, kvaedi_quality - 1))
    stamina_after = current_stamina - drain
    hp_loss_from_overdraw = max(0, -stamina_after)
    hp_after = max(0, current_hp - hp_loss_from_overdraw)
    low_threshold = max(2, math.ceil(max_stamina * 0.25))
    dark_effects_unlocked = stamina_after <= low_threshold or hp_loss_from_overdraw > 0
    divine_stroke = singing and hp_after <= 0

    return {
        "stamina_drain": drain,
        "stamina_after": stamina_after,
        "hp_loss_from_overdraw": hp_loss_from_overdraw,
        "hp_after": hp_after,
        "dark_effects_unlocked": dark_effects_unlocked,
        "divine_stroke": divine_stroke,
        "state": (
            "divine_stroke" if divine_stroke else
            "black_tongue_threshold" if dark_effects_unlocked else
            "controlled"
        ),
    }


def compute_protection_reserve(base_max_hp: int, protection_ranks: list[int]) -> dict:
    """Compute stacked Max HP reserve tax from active permanent protections."""
    clean_ranks = [max(0, int(rank)) for rank in protection_ranks]
    max_hp_tax = sum(clean_ranks)
    effective_max_hp = max(1, base_max_hp - max_hp_tax)

    if max_hp_tax >= max(6, math.ceil(base_max_hp * 0.25)):
        condition = "sickly_and_weak"
    elif max_hp_tax > 0:
        condition = "drawn_and_thinned"
    else:
        condition = "healthy"

    return {
        "base_max_hp": base_max_hp,
        "protection_ranks": clean_ranks,
        "max_hp_tax": max_hp_tax,
        "effective_max_hp": effective_max_hp,
        "condition": condition,
        "destruction_feedback": (
            "If one protection is broken, its tax lifts at once; the carver feels a distant rupture but not which ward failed."
        ),
    }

SEIDR_COSTS = {
    1: {"willpower": 2, "hp": 0, "trance": False, "wits_risk": False},
    2: {"willpower": 2, "hp": 0, "trance": False, "wits_risk": False},
    3: {"willpower": 3, "hp": 0, "trance": True,  "wits_risk": False},
    4: {"willpower": 4, "hp": 1, "trance": True,  "wits_risk": True},
    5: {"willpower": 5, "hp": 2, "trance": True,  "wits_risk": True},
}

WYRD_COSTS = {
    1: {"wits_penalty": 1, "dread": False, "permanent": False},
    2: {"wits_penalty": 1, "dread": False, "permanent": False},
    3: {"wits_penalty": 0, "dread": True,  "permanent": False},
    4: {"wits_penalty": 0, "dread": True,  "permanent": False},
    5: {"wits_penalty": 0, "dread": True,  "permanent": True,
        "wyrd_gain": 1, "will_loss": 1},
}

# ─── §11.1–11.3: Effects by rank ─────────────────────────────────────────────

GALDR_EFFECTS = {
    1: "Read and identify rune-stones. Simple wards (one night).",
    2: "Carve minor runes: mark a trail, strengthen a weapon (+1 dmg, 1 day).",
    3: "Bind runes: ward a camp overnight, compel a bleeding rune-stone to speak.",
    4: "Powerful runes: curse a weapon, seal a barrow entrance, reveal hidden text.",
    5: "Master galdr: call down fog, break an ancient seal, inscribe fate.",
}

SEIDR_EFFECTS = {
    1: "Sense if spirits are nearby. Identify a haunting.",
    2: "Speak with fresh dead (within 3 days). Ask 1 question.",
    3: "Commune with land-spirits. Negotiate passage or shelter.",
    4: "Command lesser dead. Bind a spirit to guard a location.",
    5: "Walk between worlds briefly. Speak with ancient dead.",
}

WYRD_EFFECTS = {
    1: "Sense general fortune (good/bad omen for the day).",
    2: "Cast lots for a specific question (yes/no, cryptic).",
    3: "Read the wyrd of a person (hidden loyalties, sickness).",
    4: "Foresee danger (ambush warning, storm coming, betrayal).",
    5: "See the threads of fate. Reveal hidden events. Always costly.",
}

# ─── §11.8.2: Seiðr testimony admissibility by union ─────────────────────────

SEIDR_ADMISSIBILITY = {
    "iron_grip":             "forbidden",
    "fjord_compact":         "allowed",
    "whispering_circle":     "required",
    "independent":           "varies",
}


# ─── §11.9: Degradation ───────────────────────────────────────────────────────

DEGRADATION_ONSET_YEARS = {
    "galdr":       (15, 20),
    "seidr":       (10, 15),
    "wyrd_reading": (20, 25),
}

DEGRADATION_STAGES = [
    ("none",     "No degradation."),
    ("onset",    "Onset: -5 to all magic rolls. Physical symptoms appear."),
    ("early",    "Early: effective rank -1. Cost per use +1 Willpower."),
    ("mid",      "Mid: effective rank -2. Carving/trance time doubles."),
    ("late",     "Late: effective rank -3. 10% chance of failure per use."),
    ("terminal", "Terminal: cannot perform. Knowledge remains; hands do not."),
]

DEGRADATION_STAGE_NAMES = [s[0] for s in DEGRADATION_STAGES]
DEGRADATION_STAGE_RANK_PENALTY = {
    "none": 0, "onset": 0, "early": 1, "mid": 2, "late": 3, "terminal": 99
}
DEGRADATION_STAGE_ROLL_MOD = {
    "none": 0, "onset": -5, "early": -10, "mid": -20, "late": -30, "terminal": -100
}


def _degradation_stage(years_active: int, willpower_spent: float,
                       toughness: int, will: int) -> dict:
    """
    Compute degradation stage from §11.9.

    degradation_chance = years_active × 3 + willpower_spent × 0.5
                       - (Toughness × 2) - (Will × 2)
    If > 50: onset has begun. Each additional +20 advances one stage.
    """
    score = (years_active * 3
             + willpower_spent * 0.5
             - toughness * 2
             - will * 2)
    if score <= 50:
        stage = "none"
    elif score <= 70:
        stage = "onset"
    elif score <= 90:
        stage = "early"
    elif score <= 110:
        stage = "mid"
    elif score <= 130:
        stage = "late"
    else:
        stage = "terminal"

    desc = dict(DEGRADATION_STAGES)[stage]
    rank_penalty = DEGRADATION_STAGE_RANK_PENALTY[stage]
    roll_mod = DEGRADATION_STAGE_ROLL_MOD[stage]

    return {
        "degradation_score": round(score, 1),
        "stage": stage,
        "description": desc,
        "effective_rank_penalty": rank_penalty,
        "roll_modifier": roll_mod,
    }


# ─── §11.1 Galdr attempt ──────────────────────────────────────────────────────

def attempt_galdr(wyrd: int, rune_lore: int, rank: int,
                  modifiers: int = 0, deg_stage: str = "none",
                  max_hp: int | None = None,
                  max_stamina: int | None = None) -> dict:
    """
    Full galdr attempt including cost, effect, and failure consequence.
    rank = the tier of effect being attempted (1-5).
    """
    if rank < 1 or rank > 5:
        raise ValueError("Galdr rank must be 1-5.")
    effective_rank = max(0, rank - DEGRADATION_STAGE_RANK_PENALTY.get(deg_stage, 0))
    roll_mod = modifiers + DEGRADATION_STAGE_ROLL_MOD.get(deg_stage, 0)

    result = resolve_galdr(wyrd, rune_lore, roll_mod)
    cost = compute_galdr_cost(rank, max_hp=max_hp, max_stamina=max_stamina)
    effect = GALDR_EFFECTS.get(effective_rank, "Rank degraded — cannot achieve intended effect.")

    consequence = None
    if result.result in (ResultLevel.FAILURE, ResultLevel.CRITICAL_FAILURE):
        consequence = galdr_failure_consequence()

    out = {
        "tradition": "galdr",
        "rank_attempted": rank,
        "effective_rank": effective_rank,
        "degradation_stage": deg_stage,
        "check": result.to_dict(),
        "outcome": result.result.value,
        "effect": effect if result.result in (ResultLevel.SUCCESS, ResultLevel.CRITICAL_SUCCESS) else None,
        "cost": {
            "willpower": cost["willpower"] + (1 if deg_stage in ("early", "mid", "late", "terminal") else 0),
            "stamina": cost["stamina"],
            "hp_blood": cost["hp_blood"],
            "material_required": cost["material_required"],
            "rare_material": cost["rare_material"],
            "strain_note": cost["strain_note"],
        },
        "failure_consequence": consequence,
    }
    return out


# ─── §11.2 Seiðr attempt ──────────────────────────────────────────────────────

def attempt_seidr(wyrd: int, spirit_lore: int, rank: int,
                  gender: str = "unknown", modifiers: int = 0,
                  deg_stage: str = "none") -> dict:
    """
    Full seiðr attempt including cost, effect, trance state, and social cost.
    gender used for social cost calculation ("male" practitioners face stigma).
    """
    if rank < 1 or rank > 5:
        raise ValueError("Seiðr rank must be 1-5.")
    effective_rank = max(0, rank - DEGRADATION_STAGE_RANK_PENALTY.get(deg_stage, 0))
    roll_mod = modifiers + DEGRADATION_STAGE_ROLL_MOD.get(deg_stage, 0)

    result = resolve_seidr(wyrd, spirit_lore, roll_mod)
    cost = SEIDR_COSTS[rank]
    effect = SEIDR_EFFECTS.get(effective_rank, "Rank degraded — cannot achieve intended effect.")

    social_cost = None
    if gender.lower() == "male":
        social_cost = "ergi stigma: loses standing if witnessed performing seiðr"

    late_failure_chance = None
    if deg_stage == "late":
        late_roll = roll_d100()
        late_failure_chance = {"roll": late_roll, "failed": late_roll <= 10}

    out = {
        "tradition": "seidr",
        "rank_attempted": rank,
        "effective_rank": effective_rank,
        "degradation_stage": deg_stage,
        "check": result.to_dict(),
        "outcome": result.result.value,
        "effect": effect if result.result in (ResultLevel.SUCCESS, ResultLevel.CRITICAL_SUCCESS) else None,
        "cost": {
            "willpower": cost["willpower"] + (1 if deg_stage in ("early", "mid", "late", "terminal") else 0),
            "hp_blood": cost["hp"],
            "trance_required": cost["trance"],
            "trance_note": "1 hour, practitioner vulnerable" if cost["trance"] else None,
            "wits_reduction_risk": cost["wits_risk"],
        },
        "social_cost": social_cost,
        "late_degradation_extra_fail": late_failure_chance,
    }
    return out


# ─── §11.3 Wyrd-reading attempt ───────────────────────────────────────────────

def attempt_wyrd_reading(wyrd: int, wyrd_reading_skill: int, rank: int,
                         modifiers: int = 0, deg_stage: str = "none") -> dict:
    """Full wyrd-reading attempt including cost and permanent effects at rank 5."""
    if rank < 1 or rank > 5:
        raise ValueError("Wyrd-reading rank must be 1-5.")
    effective_rank = max(0, rank - DEGRADATION_STAGE_RANK_PENALTY.get(deg_stage, 0))
    roll_mod = modifiers + DEGRADATION_STAGE_ROLL_MOD.get(deg_stage, 0)

    result = resolve_wyrd_reading(wyrd, wyrd_reading_skill, roll_mod)
    cost = WYRD_COSTS[rank]
    effect = WYRD_EFFECTS.get(effective_rank, "Rank degraded — cannot achieve intended effect.")

    out = {
        "tradition": "wyrd_reading",
        "rank_attempted": rank,
        "effective_rank": effective_rank,
        "degradation_stage": deg_stage,
        "check": result.to_dict(),
        "outcome": result.result.value,
        "effect": effect if result.result in (ResultLevel.SUCCESS, ResultLevel.CRITICAL_SUCCESS) else None,
        "cost": {
            "temporary_wits_penalty": cost["wits_penalty"],
            "dread_or_obsession": cost["dread"],
            "permanent_effects": (
                {"wyrd_gain": cost["wyrd_gain"], "will_loss": cost["will_loss"]}
                if cost.get("permanent") else None
            ),
        },
        "note": "Future shown is always true but never complete." if result.result in (ResultLevel.SUCCESS, ResultLevel.CRITICAL_SUCCESS) else None,
    }
    return out


# ─── §11.9 Practitioner degradation ──────────────────────────────────────────

def check_degradation(tradition: str, years_active: int, willpower_spent: float,
                      toughness: int, will: int) -> dict:
    """Annual degradation check for a practitioner (§11.9)."""
    if tradition not in DEGRADATION_ONSET_YEARS:
        raise ValueError(f"Unknown tradition: {tradition}. Use galdr, seidr, wyrd_reading.")

    onset_low, onset_high = DEGRADATION_ONSET_YEARS[tradition]
    stage_data = _degradation_stage(years_active, willpower_spent, toughness, will)

    physical_markers = {
        "galdr":        "Hands tremble; fingers stiffen; inscription lines waver. "
                        "Cannot hold a chisel in cold weather.",
        "seidr":        "Trance recovery extends from hours to days. Memory gaps. "
                        "Confusion between spirit-speech and waking speech.",
        "wyrd_reading": "Readings blur — lots say too much or nothing. "
                        "Reader cannot distinguish signal from noise.",
    }

    return {
        "tradition": tradition,
        "years_active": years_active,
        "willpower_spent": willpower_spent,
        "expected_onset_years": f"{onset_low}–{onset_high}",
        **stage_data,
        "physical_marker": physical_markers[tradition] if stage_data["stage"] != "none" else None,
    }


# ─── §11.8.1 Ward-right at the Allthing ──────────────────────────────────────

def calc_ward_right(band_reputation: int, galdr_worker_rune_lore: int,
                    overjarl_favor: int = 0) -> dict:
    """
    Compute ward_influence for a union's Allthing nomination (§11.8.1).

    ward_influence = band_reputation × 2 + galdr_worker_rune_lore × 5 + overjarl_favor
    overjarl_favor = 0-3.
    """
    ward_influence = (band_reputation * 2
                      + galdr_worker_rune_lore * 5
                      + overjarl_favor)
    return {
        "band_reputation": band_reputation,
        "galdr_worker_rune_lore": galdr_worker_rune_lore,
        "overjarl_favor": overjarl_favor,
        "ward_influence": ward_influence,
        "effects": {
            "holding_union_bonus": "+1 to all Allthing action rolls",
            "challenge_dc": ward_influence,
        },
        "note": "Ties broken by highest galdr_worker_rune_lore, then d100 high wins.",
    }


# ─── §11.8.2 Seiðr testimony weight ──────────────────────────────────────────

def calc_testimony_weight(seidr_worker_wyrd: int, spirit_lore: int, union: str = "independent") -> dict:
    """
    testimony_weight = seidr_worker_wyrd × 3 + spirit_lore × 5
    Weight thresholds: ≥31 compelling, 15-30 supporting, 0-14 hearsay.
    """
    admissibility = SEIDR_ADMISSIBILITY.get(union.lower(), "varies")
    weight = seidr_worker_wyrd * 3 + spirit_lore * 5

    if weight >= 31:
        classification = "compelling_evidence"
        effect = "+3 modifier to supported party"
    elif weight >= 15:
        classification = "supporting_evidence"
        effect = "+1 modifier to supported party"
    else:
        classification = "hearsay"
        effect = "ignored — no mechanical effect"

    return {
        "union": union,
        "admissibility": admissibility,
        "seidr_worker_wyrd": seidr_worker_wyrd,
        "spirit_lore": spirit_lore,
        "testimony_weight": weight,
        "classification": classification,
        "effect": effect,
        "note": "Halved if living witness challenge is invoked (costs challenger 1 reputation).",
    }


# ─── §11.8.3 Curse (niding-pole) legitimacy ──────────────────────────────────

def calc_curse_legitimacy(carver_rune_lore: int, grievance_severity: int,
                          defender_reputation: int, blood_galdr: bool = False) -> dict:
    """
    curse_legitimacy = carver_rune_lore × 5 + grievance_severity × 10
                     - defender_reputation × 3

    blood_galdr: if True, automatic niding ruling regardless of score.
    """
    if blood_galdr:
        return {
            "blood_galdr": True,
            "ruling": "automatic_niding",
            "consequence": (
                "Carver declared outlaw. Feud +3 between settlements. "
                "Dark Arts level of carver's union +1."
            ),
        }

    score = carver_rune_lore * 5 + grievance_severity * 10 - defender_reputation * 3

    if score >= 51:
        ruling = "curse_stands"
        consequence = "Target must resolve the grievance or accept the curse's effects."
    elif score >= 25:
        ruling = "compromise"
        consequence = "Both parties lose 1 reputation."
    else:
        ruling = "curse_removed"
        consequence = "Carver branded niding. Carver loses 2 reputation. Feud +1."

    return {
        "carver_rune_lore": carver_rune_lore,
        "grievance_severity": grievance_severity,
        "defender_reputation": defender_reputation,
        "blood_galdr": False,
        "legitimacy_score": score,
        "ruling": ruling,
        "consequence": consequence,
    }


# ─── §11.8.4 Dark arts accusation ────────────────────────────────────────────

def calc_dark_arts_accusation(accuser_testimony_weight: int, evidence_quality: int,
                               accused_reputation: int,
                               accused_dark_arts_concealment: int) -> dict:
    """
    accusation_chance = accuser_testimony_weight + evidence_quality × 5
                      - accused_reputation × 3 - accused_dark_arts_concealment × 10

    evidence_quality = 0-5. dark_arts_concealment = 0-3.
    """
    score = (accuser_testimony_weight
             + evidence_quality * 5
             - accused_reputation * 3
             - accused_dark_arts_concealment * 10)

    if score >= 41:
        outcome = "convicted"
        consequence = "Accused convicted. Consequences per Dark Arts table."
    elif score >= 20:
        outcome = "inconclusive"
        consequence = "Accused gains feud +1 with accuser. No punishment."
    else:
        outcome = "accusation_fails"
        consequence = "Accuser loses 1 reputation for false accusation."

    return {
        "accuser_testimony_weight": accuser_testimony_weight,
        "evidence_quality": evidence_quality,
        "accused_reputation": accused_reputation,
        "accused_dark_arts_concealment": accused_dark_arts_concealment,
        "accusation_score": score,
        "outcome": outcome,
        "consequence": consequence,
        "note": "Iron Grip union cannot bring accusations without a seiðr-worker from another union.",
    }


# ─── §11.9 Practitioner YAML registry ─────────────────────────────────────────

import re as _re
from pathlib import Path as _Path

_PRACTITIONERS_FILE = _Path(__file__).resolve().parent.parent / "data" / "magic" / "practitioners.yaml"

# Stages in advancement order
_STAGES_ORDER = ["pre_onset", "onset", "early", "mid", "late", "terminal"]
_STAGE_RANK_PENALTY = {
    "pre_onset": 0, "onset": 0, "early": -1, "mid": -2, "late": -3, "terminal": None
}
_STAGE_PROGRESSION_MOD = {
    "onset": 0, "early": -10, "mid": -20, "late": -30, "terminal": None
}
_STAGE_NOTES = {
    "pre_onset": "Normal function",
    "onset": "-5 to all magic rolls. Physical symptoms appear",
    "early": "Eff. rank −1. +1 WP cost/use",
    "mid": "Eff. rank −2. Cast/trance time ×2",
    "late": "Eff. rank −3. 10% fail/use",
    "terminal": "Cannot cast. Knowledge intact; hands do not",
}


def _parse_years(v) -> int:
    """Parse years_active: handles int, None, or strings like '~10', '~40'."""
    if v is None:
        return 0
    if isinstance(v, (int, float)):
        return int(v)
    m = _re.search(r'\d+', str(v))
    return int(m.group()) if m else 0


def _prac_stage(p: dict) -> str:
    """Return degradation stage for a practitioner dict."""
    return p.get('stage') or p.get('lifecycle_stage_deg') or "pre_onset"


def _load_practitioners() -> list[dict]:
    try:
        import yaml as _y
        with open(_PRACTITIONERS_FILE, 'r', encoding='utf-8') as f:
            data = _y.safe_load(f)
        return data.get('practitioners', [])
    except (ImportError, FileNotFoundError):
        return []


def _save_practitioners(practitioners: list[dict]) -> None:
    import yaml as _y
    with open(_PRACTITIONERS_FILE, 'r', encoding='utf-8') as f:
        raw = f.read()
    hdr = "\n".join(ln for ln in raw.splitlines() if ln.startswith('#'))
    with open(_PRACTITIONERS_FILE, 'w', encoding='utf-8') as f:
        if hdr:
            f.write(hdr + "\n\n")
        _y.dump({'practitioners': practitioners}, f, allow_unicode=True, sort_keys=False)


def cmd_practitioners() -> list[dict]:
    """Return summary list for all practitioners."""
    rows = []
    for p in _load_practitioners():
        name = p.get('name') or p.get('call_name', '?')
        tradition = p.get('tradition', '?')
        stage = _prac_stage(p)
        base_rank = p.get('rank') or p.get('base_rank') or 0
        if base_rank is None:
            base_rank = 0
        rank_mod = _STAGE_RANK_PENALTY.get(stage, 0) or 0
        eff_rank = max(0, int(base_rank) + int(rank_mod))
        eff_display = (f"{eff_rank} (base)" if rank_mod == 0
                       else f"{eff_rank} ({rank_mod:+d})")
        years = _parse_years(p.get('years_active', 0))
        rows.append({
            "name": name,
            "tradition": tradition,
            "stage": stage,
            "effective_rank": eff_display,
            "years_active": years,
            "notes": _STAGE_NOTES.get(stage, ""),
        })
    return rows


def cmd_degrade_practitioner(name: str) -> dict:
    """Run stochastic annual degradation for one named practitioner."""
    import random as _r
    practitioners = _load_practitioners()
    needle = name.lower()
    idx = next((i for i, p in enumerate(practitioners)
                if (p.get('name') or '').lower() == needle), -1)
    if idx < 0:
        return {"error": f"Practitioner '{name}' not found in practitioners.yaml"}

    p = practitioners[idx]
    tradition = p.get('tradition', 'galdr')
    years_active = _parse_years(p.get('years_active', 0))
    willpower_spent = float(p.get('total_willpower_spent', 0) or 0)
    tou = int(p.get('tou', 3) or 3)
    wil = int(p.get('wil', 3) or 3)
    stage = _prac_stage(p)

    deg_chance = (years_active * 3) + (willpower_spent * 0.5) - (tou * 2) - (wil * 2)
    deg_chance = round(deg_chance, 1)

    roll = None
    advanced = False
    new_stage = stage

    if stage == "pre_onset":
        if deg_chance > 50:
            roll = _r.randint(1, 100)
            if roll <= deg_chance:
                new_stage = "onset"
                advanced = True
    elif stage != "terminal":
        cur_idx = _STAGES_ORDER.index(stage)
        prog_mod = _STAGE_PROGRESSION_MOD.get(stage, 0) or 0
        threshold = min(95, max(5, int(deg_chance + prog_mod)))
        roll = _r.randint(1, 100)
        if roll <= threshold and cur_idx + 1 < len(_STAGES_ORDER):
            new_stage = _STAGES_ORDER[cur_idx + 1]
            advanced = True

    # Update fields in practitioner dict
    rank_mod = _STAGE_RANK_PENALTY.get(new_stage, 0)
    practitioners[idx]['stage'] = new_stage
    practitioners[idx]['effective_rank_mod'] = rank_mod
    # increment years_active
    practitioners[idx]['years_active'] = years_active + 1

    _save_practitioners(practitioners)

    return {
        "practitioner": p.get('name'),
        "tradition": tradition,
        "years_active": years_active,
        "deg_chance": deg_chance,
        "roll": roll,
        "previous_stage": stage,
        "new_stage": new_stage,
        "advanced": advanced,
        "effective_rank_mod": rank_mod,
        "notes": _STAGE_NOTES.get(new_stage, ""),
    }


def cmd_annual_tick() -> list[dict]:
    """Run degradation check for ALL practitioners and return results."""
    practitioners = _load_practitioners()
    results = []
    for p in practitioners:
        name = p.get('name') or p.get('call_name', '?')
        result = cmd_degrade_practitioner(name)
        results.append(result)
    return results


def cmd_practitioner_add(name: str, tradition: str, years_active: int,
                         tou: int = 3, wil: int = 3, base_rank: int = 1) -> dict:
    """Add a new practitioner entry to practitioners.yaml."""
    practitioners = _load_practitioners()
    if any((p.get('name') or '').lower() == name.lower() for p in practitioners):
        return {"error": f"Practitioner '{name}' already exists"}

    new_p = {
        "name": name,
        "tradition": tradition,
        "base_rank": base_rank,
        "rank": base_rank,
        "years_active": years_active,
        "total_willpower_spent": 0,
        "tou": tou,
        "wil": wil,
        "stage": "pre_onset",
        "effective_rank_mod": 0,
        "notes": "Newly registered.",
    }
    practitioners.append(new_p)
    _save_practitioners(practitioners)
    return {"added": name, "tradition": tradition, "years_active": years_active,
            "tou": tou, "wil": wil, "base_rank": base_rank, "stage": "pre_onset"}


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Iron Ledger — Norse Magic Simulator (§11)"
    )
    sub = parser.add_subparsers(dest="cmd")

    # galdr
    p = sub.add_parser("galdr", help="Attempt a galdr (rune scribing) action")
    p.add_argument("--wyrd",       type=int, required=True, help="Wyrd attribute (1-10)")
    p.add_argument("--rune-lore",  type=int, required=True, help="Rune-lore skill rank (0-5)")
    p.add_argument("--rank",       type=int, required=True, help="Effect rank attempted (1-5)")
    p.add_argument("--mods",       type=int, default=0,    help="Situational modifier")
    p.add_argument("--deg-stage",  type=str, default="none",
                   choices=DEGRADATION_STAGE_NAMES, help="Degradation stage of practitioner")
    p.add_argument("--json",       action="store_true")

    # seidr
    p = sub.add_parser("seidr", help="Attempt a seiðr (spirit talking) action")
    p.add_argument("--wyrd",        type=int, required=True)
    p.add_argument("--spirit-lore", type=int, required=True, help="Spirit-lore skill rank (0-5)")
    p.add_argument("--rank",        type=int, required=True, help="Effect rank attempted (1-5)")
    p.add_argument("--gender",      type=str, default="unknown",
                   choices=["male", "female", "unknown"], help="Social context")
    p.add_argument("--mods",        type=int, default=0)
    p.add_argument("--deg-stage",   type=str, default="none", choices=DEGRADATION_STAGE_NAMES)
    p.add_argument("--json",        action="store_true")

    # wyrd-read
    p = sub.add_parser("wyrd-read", help="Attempt a wyrd-reading (fate divination)")
    p.add_argument("--wyrd",  type=int, required=True)
    p.add_argument("--skill", type=int, required=True, help="Wyrd-reading skill rank (0-5)")
    p.add_argument("--rank",  type=int, required=True, help="Effect rank attempted (1-5)")
    p.add_argument("--mods",  type=int, default=0)
    p.add_argument("--deg-stage", type=str, default="none", choices=DEGRADATION_STAGE_NAMES)
    p.add_argument("--json",  action="store_true")

    # degrade (annual check)
    p = sub.add_parser("degrade", help="Annual practitioner degradation check (§11.9)")
    p.add_argument("--tradition",      type=str, default=None,
                   choices=["galdr", "seidr", "wyrd_reading"])
    p.add_argument("--years-active",   type=int, default=None)
    p.add_argument("--willpower-spent", type=float, default=None,
                   help="Total Willpower spent in career")
    p.add_argument("--toughness",      type=int, default=None)
    p.add_argument("--will",           type=int, default=None,
                   help="Will attribute (1-10)")
    p.add_argument("--practitioner",   type=str, default=None,
                   help="Name of practitioner in practitioners.yaml (replaces other flags)")
    p.add_argument("--json",           action="store_true")

    # practitioners list
    sub.add_parser("practitioners", help="Show all practitioners summary table")

    # annual_tick
    sub.add_parser("annual_tick", help="Run annual degradation for ALL practitioners")

    # practitioner_add
    pa = sub.add_parser("practitioner_add", help="Add a new practitioner")
    pa.add_argument("--name",         type=str, required=True)
    pa.add_argument("--tradition",    type=str, required=True,
                    choices=["galdr", "seidr", "wyrd_reading"])
    pa.add_argument("--years-active", type=int, required=True)
    pa.add_argument("--tou",          type=int, default=3)
    pa.add_argument("--wil",          type=int, default=3)
    pa.add_argument("--rank",         type=int, default=1)
    pa.add_argument("--json",         action="store_true")

    # ward-right
    p = sub.add_parser("ward-right", help="Compute Allthing ward-right influence (§11.8.1)")
    p.add_argument("--reputation",    type=int, required=True, help="Band reputation (0-5)")
    p.add_argument("--rune-lore",     type=int, required=True, help="Nominated worker rune-lore rank")
    p.add_argument("--overjarl-favor", type=int, default=0, help="Overjarl favor (0-3)")
    p.add_argument("--json",          action="store_true")

    # testimony
    p = sub.add_parser("testimony", help="Seiðr testimony weight at ting (§11.8.2)")
    p.add_argument("--wyrd",        type=int, required=True, help="Seiðr worker Wyrd attribute")
    p.add_argument("--spirit-lore", type=int, required=True)
    p.add_argument("--union",       type=str, default="independent",
                   choices=list(SEIDR_ADMISSIBILITY.keys()))
    p.add_argument("--json",        action="store_true")

    # curse
    p = sub.add_parser("curse", help="Curse (niding-pole) legitimacy ruling (§11.8.3)")
    p.add_argument("--rune-lore",      type=int, required=True)
    p.add_argument("--grievance",      type=int, required=True, help="Grievance severity (1-5)")
    p.add_argument("--defender-rep",   type=int, required=True, help="Defender reputation (0-5)")
    p.add_argument("--blood-galdr",    action="store_true",
                   help="Used another's blood — automatic niding ruling")
    p.add_argument("--json",           action="store_true")

    # accuse
    p = sub.add_parser("accuse", help="Dark arts accusation resolution (§11.8.4)")
    p.add_argument("--testimony-weight", type=int, required=True)
    p.add_argument("--evidence",         type=int, required=True,
                   help="Evidence quality (0-5)")
    p.add_argument("--accused-rep",      type=int, required=True,
                   help="Accused reputation (0-5)")
    p.add_argument("--concealment",      type=int, required=True,
                   help="Dark arts concealment level (0-3)")
    p.add_argument("--json",             action="store_true")

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        sys.exit(1)

    use_json = getattr(args, "json", False)

    if args.cmd == "galdr":
        result = attempt_galdr(args.wyrd, args.rune_lore, args.rank,
                               args.mods, args.deg_stage)
    elif args.cmd == "seidr":
        result = attempt_seidr(args.wyrd, args.spirit_lore, args.rank,
                                args.gender, args.mods, args.deg_stage)
    elif args.cmd == "wyrd-read":
        result = attempt_wyrd_reading(args.wyrd, args.skill, args.rank,
                                      args.mods, args.deg_stage)
    elif args.cmd == "degrade":
        if args.practitioner:
            result = cmd_degrade_practitioner(args.practitioner)
            if use_json:
                print(json.dumps(result, indent=2))
            elif "error" in result:
                print(result["error"])
            else:
                adv = " ⚠ ADVANCED" if result["advanced"] else ""
                print(f"{result['practitioner']}: {result['previous_stage']} → "
                      f"{result['new_stage']} (deg_chance {result['deg_chance']}, "
                      f"roll {result['roll']}){adv}")
                print(f"  {result['notes']}")
            return
        else:
            # Legacy explicit-stats mode
            missing = [f for f in ("tradition", "years_active", "willpower_spent",
                                   "toughness", "will")
                       if getattr(args, f, None) is None]
            if missing:
                print(f"Error: --practitioner or explicit stats required "
                      f"(missing: {', '.join(missing)})")
                sys.exit(1)
            result = check_degradation(args.tradition, args.years_active,
                                       args.willpower_spent, args.toughness, args.will)
    elif args.cmd == "practitioners":
        rows = cmd_practitioners()
        if not rows:
            print("No practitioners found.")
            sys.exit(0)
        if use_json:
            print(json.dumps(rows, indent=2))
        else:
            header = f"{'Name':<12} {'Tradition':<14} {'Stage':<12} {'Eff.Rank':<10} {'Years':<6} Notes"
            print("\n=== Magic Practitioners ===")
            print(header)
            print("-" * len(header))
            for r in rows:
                print(f"{r['name']:<12} {r['tradition']:<14} {r['stage']:<12} "
                      f"{r['effective_rank']:<10} {r['years_active']:<6} {r['notes']}")
        return
    elif args.cmd == "annual_tick":
        results = cmd_annual_tick()
        if use_json:
            print(json.dumps(results, indent=2))
        else:
            print("=== Annual Degradation Tick ===")
            for r in results:
                if "error" in r:
                    print(f"  {r['error']}")
                    continue
                adv = " ⚠ ADVANCED STAGE" if r["advanced"] else ""
                roll_str = str(r["roll"]) if r["roll"] is not None else "n/a"
                print(f"  {r['practitioner']}: {r['previous_stage']} → {r['new_stage']}"
                      f" (roll {roll_str}/{int(r['deg_chance'])}){adv}")
        return
    elif args.cmd == "practitioner_add":
        result = cmd_practitioner_add(
            args.name, args.tradition, args.years_active,
            tou=args.tou, wil=args.wil, base_rank=args.rank)
        if use_json:
            print(json.dumps(result, indent=2))
        else:
            if "error" in result:
                print(result["error"])
            else:
                print(f"Added {result['added']} ({result['tradition']}, "
                      f"rank {result['base_rank']}, {result['years_active']} yrs)")
        return
    elif args.cmd == "ward-right":
        result = calc_ward_right(args.reputation, args.rune_lore, args.overjarl_favor)
    elif args.cmd == "testimony":
        result = calc_testimony_weight(args.wyrd, args.spirit_lore, args.union)
    elif args.cmd == "curse":
        result = calc_curse_legitimacy(args.rune_lore, args.grievance,
                                        args.defender_rep, args.blood_galdr)
    elif args.cmd == "accuse":
        result = calc_dark_arts_accusation(args.testimony_weight, args.evidence,
                                            args.accused_rep, args.concealment)
    else:
        parser.print_help()
        sys.exit(1)

    if use_json:
        print(json.dumps(result, indent=2))
    else:
        _print_result(args.cmd, result)


def _print_result(cmd: str, r: dict) -> None:
    """Human-readable output."""
    if cmd in ("galdr", "seidr", "wyrd-read"):
        tradition_label = r["tradition"].upper()
        print(f"\n{tradition_label} — rank {r['rank_attempted']} attempt")
        if r.get("degradation_stage") and r["degradation_stage"] != "none":
            print(f"  Degradation: {r['degradation_stage']} "
                  f"(effective rank {r['effective_rank']})")
        chk = r["check"]
        print(f"  Chance: {chk['final_chance']}%  Roll: {chk['roll']}  "
              f"→ {chk['result'].upper()}")
        if r.get("effect"):
            print(f"  Effect: {r['effect']}")
        c = r["cost"]
        # Galdr/seiðr have willpower; wyrd-reading has wits_penalty
        cost_parts = []
        if "willpower" in c:
            cost_parts.append(f"{c['willpower']} WP")
        if c.get("hp_blood"):
            cost_parts.append(f"{c['hp_blood']} HP (blood)")
        if c.get("trance_required"):
            cost_parts.append("trance (1 hr, vulnerable)")
        if c.get("wits_reduction_risk"):
            cost_parts.append("Wits reduction risk")
        if c.get("material_required"):
            cost_parts.append("material component" + (" (rare)" if c.get("rare_material") else ""))
        if c.get("temporary_wits_penalty"):
            cost_parts.append(f"temporary -{c['temporary_wits_penalty']} Wits")
        if c.get("dread_or_obsession"):
            cost_parts.append("dread or obsession")
        if c.get("permanent_effects"):
            pe = c["permanent_effects"]
            cost_parts.append(f"permanent: +{pe['wyrd_gain']} Wyrd / -{pe['will_loss']} Will")
        if not cost_parts:
            cost_parts = ["none"]
        print(f"  Cost: {', '.join(cost_parts)}")
        if r.get("failure_consequence"):
            print(f"  Failure: {r['failure_consequence']}")
        if r.get("social_cost"):
            print(f"  Social: {r['social_cost']}")
        if r.get("note"):
            print(f"  Note: {r['note']}")

    elif cmd == "degrade":
        print(f"\nDEGRADATION — {r['tradition']} ({r['years_active']} years active)")
        print(f"  Degradation score: {r['degradation_score']}")
        print(f"  Stage: {r['stage'].upper()} — {r['description']}")
        if r.get("effective_rank_penalty"):
            print(f"  Effective rank penalty: -{r['effective_rank_penalty']}")
        if r.get("roll_modifier"):
            print(f"  Roll modifier: {r['roll_modifier']:+d}")
        if r.get("physical_marker"):
            print(f"  Physical: {r['physical_marker']}")

    elif cmd == "ward-right":
        print(f"\nWARD-RIGHT influence: {r['ward_influence']}")
        print(f"  Rep×2={r['band_reputation']*2}  "
              f"Rune-lore×5={r['galdr_worker_rune_lore']*5}  "
              f"Overjarl={r['overjarl_favor']}")
        print(f"  Benefit: {r['effects']['holding_union_bonus']}")
        print(f"  Challenge DC: {r['effects']['challenge_dc']}")

    elif cmd == "testimony":
        print(f"\nSEIÐR TESTIMONY — union: {r['union']}")
        print(f"  Admissibility: {r['admissibility'].upper()}")
        print(f"  Weight: {r['testimony_weight']}  ({r['classification'].upper()})")
        print(f"  Effect: {r['effect']}")

    elif cmd == "curse":
        if r.get("blood_galdr"):
            print(f"\nCURSE RULING: AUTOMATIC NIDING (blood-galdr used)")
            print(f"  {r['consequence']}")
        else:
            print(f"\nCURSE LEGITIMACY score: {r['legitimacy_score']}")
            print(f"  Ruling: {r['ruling'].upper().replace('_', ' ')}")
            print(f"  {r['consequence']}")

    elif cmd == "accuse":
        print(f"\nDARK ARTS ACCUSATION score: {r['accusation_score']}")
        print(f"  Outcome: {r['outcome'].upper().replace('_', ' ')}")
        print(f"  {r['consequence']}")
        print(f"  Note: {r['note']}")


if __name__ == "__main__":
    main()
