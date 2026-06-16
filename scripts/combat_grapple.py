"""combat_grapple.py — Iron Ledger grapple resolution: entry A1-A4, positional B1-B12, Glima C1-C4, dirty D1-D8."""
import random

from combat_types import *
from combat_model import Fighter, GrappleState, GrapplePosition
from engine import (
    resolve_check,
    resolve_opposed,
    hit_location,
    calculate_damage,
    wound_severity,
    ResultLevel,
)

# Resolution — Grapple helpers
# ───────────────────────────────────────────────────────────────────────

def _create_grapple(attacker: Fighter, defender: Fighter, position: GrapplePosition):
    """Establish a shared GrappleState between two fighters."""
    gs = GrappleState(
        position=position.value,
        dominant=attacker.name if position.value in (
            "dominant_clinch", "rear_control", "mounted", "side_control"
        ) else "",
        ground=position.value in ("side_control",),
    )
    attacker.grapple_state = gs
    defender.grapple_state = gs
    attacker.add_condition(ConditionType.GRAPPLED, -1)
    defender.add_condition(ConditionType.GRAPPLED, -1)
    if "maul_bite" in attacker.traits:
        attacker.add_condition(ConditionType.MAUL_ACTIVE, -1)


def _clear_grapple(a: Fighter, b: Fighter):
    """Remove grapple state and related conditions from both fighters."""
    a.grapple_state = None
    b.grapple_state = None
    for f in (a, b):
        f.remove_condition(ConditionType.GRAPPLED)
        f.remove_condition(ConditionType.PINNED)
        f.remove_condition(ConditionType.ARM_LOCKED)
        f.remove_condition(ConditionType.CHOKED)
        f.remove_condition(ConditionType.MAUL_ACTIVE)


# ───────────────────────────────────────────────────────────────────────
# Resolution — Grapple entry (A1–A4)
# ───────────────────────────────────────────────────────────────────────

def resolve_grapple_entry(
    attacker: Fighter,
    defender: Fighter,
    maneuver: Maneuver,
    result: dict,
) -> dict:
    """Resolve a grapple entry maneuver (Brókartök, Lausatök, Hryggspenna, Tackle)."""
    wep_mods = GRAPPLE_WEAPON_MODIFIERS.get(attacker.weapon_type, GRAPPLE_WEAPON_MODIFIERS["generic"])
    atk_grapple_mod = wep_mods["attack"]

    trait_bonus = 0
    if maneuver == Maneuver.BROKARTOK and "glima_brokartok" in attacker.traits:
        trait_bonus = 10
    elif maneuver == Maneuver.LAUSATOK and "glima_lausatok" in attacker.traits:
        trait_bonus = 10

    if maneuver == Maneuver.BROKARTOK:
        clothing_mod = 0
        if "no_belt" in defender.traits or "minimal_clothing" in defender.traits:
            clothing_mod = -10
        opposed = resolve_opposed(
            attacker.mig, max(attacker.brawl_skill, 0),
            attacker.condition_attack_mod() + atk_grapple_mod + trait_bonus + clothing_mod,
            defender.mig, max(defender.brawl_skill, 0),
            defender.condition_defense_mod(),
            attacker.name, defender.name,
        )
        if opposed.winner == "attacker":
            _create_grapple(attacker, defender, GrapplePosition.DOMINANT_CLINCH)
            result["condition_applied"] = "dominant_clinch"
            result["hit"] = True
        else:
            _create_grapple(attacker, defender, GrapplePosition.NEUTRAL_CLINCH)
            result["condition_applied"] = "neutral_clinch (countered)"
            result["hit"] = False
        result["winner"] = opposed.winner

    elif maneuver == Maneuver.LAUSATOK:
        opposed = resolve_opposed(
            attacker.nim, max(attacker.brawl_skill, 0),
            attacker.condition_attack_mod() + atk_grapple_mod + trait_bonus,
            defender.nim, max(defender.brawl_skill, 0),
            defender.condition_defense_mod(),
            attacker.name, defender.name,
        )
        if opposed.winner == "attacker":
            _create_grapple(attacker, defender, GrapplePosition.NEUTRAL_CLINCH)
            result["special"] = "throat_seize_unlocked"
            result["condition_applied"] = "neutral_clinch"
            result["hit"] = True
        else:
            _create_grapple(defender, attacker, GrapplePosition.NEUTRAL_CLINCH)
            result["condition_applied"] = "clinch_reversed"
            result["hit"] = False
        result["winner"] = opposed.winner

    elif maneuver == Maneuver.HRYGGSPENNA:
        opposed = resolve_opposed(
            attacker.mig, max(attacker.brawl_skill, 0),
            attacker.condition_attack_mod() + atk_grapple_mod + 10,
            defender.mig, max(defender.brawl_skill, 0),
            defender.condition_defense_mod(),
            attacker.name, defender.name,
        )
        if opposed.winner == "attacker":
            _create_grapple(attacker, defender, GrapplePosition.REAR_CONTROL)
            result["condition_applied"] = "rear_control"
            result["hit"] = True
        else:
            _create_grapple(attacker, defender, GrapplePosition.NEUTRAL_CLINCH)
            result["condition_applied"] = "neutral_clinch (slipped)"
            result["hit"] = False
        result["winner"] = opposed.winner

    elif maneuver == Maneuver.TACKLE:
        tackle_penalty = -20 if attacker.weapon_type not in ("unarmed", "dagger", "seax") else 0
        opposed = resolve_opposed(
            attacker.mig, 0,
            attacker.condition_attack_mod() + tackle_penalty,
            defender.mig, 0,
            defender.condition_defense_mod(),
            attacker.name, defender.name,
        )
        if opposed.winner == "attacker":
            _create_grapple(attacker, defender, GrapplePosition.SIDE_CONTROL)
            attacker.ground = True
            defender.ground = True
            defender.add_condition(ConditionType.PRONE, -1)
            result["condition_applied"] = "side_control (both grounded)"
            result["hit"] = True
        else:
            attacker.add_condition(ConditionType.PRONE, -1)
            attacker.ground = True
            result["condition_applied"] = "attacker_prone (countered)"
            result["hit"] = False
        result["winner"] = opposed.winner

    return result


# ───────────────────────────────────────────────────────────────────────
# Resolution — In-grapple positional moves (B1–B12) + Glíma finishers (C1–C4)
# ───────────────────────────────────────────────────────────────────────

def resolve_ingrapple_move(
    attacker: Fighter,
    defender: Fighter,
    maneuver: Maneuver,
    result: dict,
) -> dict:
    """Resolve an in-grapple positional move or Glíma finisher."""
    gs = attacker.grapple_state
    if gs is None:
        result["action"] = "no_grapple_state"
        result["hit"] = False
        return result

    pos = gs.position
    brawl_a = attacker.brawl_skill
    brawl_d = defender.brawl_skill

    def _opp(a_attr, d_attr, a_extra=0, d_extra=0):
        return resolve_opposed(
            a_attr, brawl_a,
            attacker.condition_attack_mod() + a_extra,
            d_attr, brawl_d,
            defender.condition_defense_mod() + d_extra,
            attacker.name, defender.name,
        )

    if maneuver == Maneuver.CLINCH_IMPROVE:
        opposed = _opp(attacker.nim, defender.nim)
        if opposed.winner == "attacker":
            if pos in (GrapplePosition.CLINCH.value, GrapplePosition.NEUTRAL_CLINCH.value):
                gs.position = GrapplePosition.DOMINANT_CLINCH.value
                gs.dominant = attacker.name
            elif pos == GrapplePosition.GUARD_BOTTOM.value:
                gs.position = GrapplePosition.SIDE_CONTROL.value
                gs.dominant = attacker.name
                attacker.ground = True
            result["condition_applied"] = f"position\u2192{gs.position}"
            result["hit"] = True
        else:
            result["hit"] = False
        result["winner"] = opposed.winner

    elif maneuver == Maneuver.LEG_TRIP:
        if pos != GrapplePosition.DOMINANT_CLINCH.value:
            result["action"] = "requires_dominant_clinch"
            result["hit"] = False
            return result
        opposed = _opp(attacker.mig, defender.mig)
        if opposed.winner == "attacker":
            defender.add_condition(ConditionType.PRONE, -1)
            defender.ground = True
            if attacker.glima_mode or attacker.wants_nonlethal:
                gs.position = GrapplePosition.MOUNTED.value
                gs.dominant = attacker.name
                attacker.ground = True
                result["condition_applied"] = "takedown\u2192mounted"
            else:
                _clear_grapple(attacker, defender)
                result["condition_applied"] = "takedown\u2192standing_free"
            result["hit"] = True
        else:
            gs.position = GrapplePosition.NEUTRAL_CLINCH.value
            gs.dominant = ""
            result["hit"] = False
        result["winner"] = opposed.winner

    elif maneuver == Maneuver.HIP_THROW:
        if pos != GrapplePosition.DOMINANT_CLINCH.value:
            result["action"] = "requires_dominant_clinch"
            result["hit"] = False
            return result
        if attacker.mig < 5:
            result["action"] = "insufficient_mig"
            result["hit"] = False
            return result
        opposed = _opp(attacker.mig, defender.mig)
        if opposed.winner == "attacker":
            land_dmg = random.randint(1, 6)
            if attacker.terrain_context in ("barrow", "stone", "rock"):
                land_dmg = max(land_dmg, random.randint(1, 6) + 2)
            w = defender.apply_wound("torso", land_dmg)
            defender.add_condition(ConditionType.PRONE, -1)
            defender.ground = True
            if opposed.attacker.result == ResultLevel.CRITICAL_SUCCESS:
                defender.add_condition(ConditionType.STAGGERED, 1)
            _clear_grapple(attacker, defender)
            result["hit"] = True
            result["final_damage"] = land_dmg
            result["wound_severity"] = w.severity
            result["condition_applied"] = "prone (hip-thrown)"
        else:
            gs.position = GrapplePosition.NEUTRAL_CLINCH.value
            gs.dominant = ""
            result["hit"] = False
        result["winner"] = opposed.winner

    elif maneuver == Maneuver.GROUND_CONTROL:
        if not (attacker.ground and defender.ground):
            result["action"] = "requires_ground"
            result["hit"] = False
            return result
        avg_a = (attacker.mig + attacker.nim) // 2
        avg_d = (defender.mig + defender.nim) // 2
        opposed = _opp(avg_a, avg_d)
        if opposed.winner == "attacker":
            gs.position = GrapplePosition.MOUNTED.value
            gs.dominant = attacker.name
            defender.add_condition(ConditionType.PRONE, -1)
            result["condition_applied"] = "mounted"
            result["hit"] = True
        else:
            gs.position = GrapplePosition.NEUTRAL_CLINCH.value
            result["hit"] = False
        result["winner"] = opposed.winner

    elif maneuver == Maneuver.THROAT_SEIZE:
        if pos not in (GrapplePosition.DOMINANT_CLINCH.value, GrapplePosition.MOUNTED.value,
                       GrapplePosition.REAR_CONTROL.value):
            result["action"] = "requires_dominant_mounted_or_rear"
            result["hit"] = False
            return result
        if defender.is_undead:
            result["action"] = "undead_no_airway"
            result["hit"] = False
            return result
        opposed = _opp(attacker.mig, defender.mig)
        if opposed.winner == "attacker":
            defender.add_condition(ConditionType.CHOKED, -1)
            gs.throat_seized = True
            gs.throat_seized_by = attacker.name
            result["condition_applied"] = "choked"
            result["hit"] = True
        else:
            result["condition_applied"] = "throat_seize_countered"
            result["hit"] = False
        result["winner"] = opposed.winner

    elif maneuver == Maneuver.ARM_TRAP:
        if pos not in (GrapplePosition.CLINCH.value, GrapplePosition.NEUTRAL_CLINCH.value,
                       GrapplePosition.DOMINANT_CLINCH.value):
            result["action"] = "requires_clinch"
            result["hit"] = False
            return result
        opposed = _opp(attacker.nim, defender.nim)
        if opposed.winner == "attacker":
            defender.add_condition(ConditionType.ARM_LOCKED, -1)
            gs.arm_locked = defender.name
            result["condition_applied"] = "arm_locked"
            result["hit"] = True
        else:
            attacker.add_condition(ConditionType.STAGGERED, 1)
            result["hit"] = False
        result["winner"] = opposed.winner

    elif maneuver == Maneuver.ELBOW_STRIKE:
        pos_bonus = 5 if pos == GrapplePosition.DOMINANT_CLINCH.value else 0
        opposed = _opp(attacker.mig, defender.nim, a_extra=pos_bonus)
        if opposed.winner == "attacker":
            dmg = random.randint(1, 4)
            loc = random.choice(["head", "torso"])
            armor_val = max(0, defender.get_armor_at(loc) - 2)
            actual_dmg = max(1, dmg - armor_val)
            w = defender.apply_wound(loc, actual_dmg)
            result["hit"] = True
            result["location"] = loc
            result["final_damage"] = actual_dmg
            result["wound_severity"] = w.severity
        else:
            result["hit"] = False
        result["winner"] = opposed.winner

    elif maneuver == Maneuver.KNEE_STRIKE:
        if pos not in (GrapplePosition.CLINCH.value, GrapplePosition.NEUTRAL_CLINCH.value,
                       GrapplePosition.DOMINANT_CLINCH.value, GrapplePosition.MOUNTED.value):
            result["action"] = "requires_standing_clinch_or_mounted"
            result["hit"] = False
            return result
        opposed = _opp(attacker.mig, defender.tou)
        if opposed.winner == "attacker":
            dmg = random.randint(3, 6)
            w = defender.apply_wound("torso", dmg)
            defender.add_condition(ConditionType.WINDED, -1)
            result["hit"] = True
            result["location"] = "torso"
            result["final_damage"] = dmg
            result["wound_severity"] = w.severity
            result["condition_applied"] = "winded"
            if opposed.attacker.result == ResultLevel.CRITICAL_SUCCESS:
                gs.position = GrapplePosition.DOMINANT_CLINCH.value
                gs.dominant = attacker.name
        else:
            result["hit"] = False
        result["winner"] = opposed.winner

    elif maneuver == Maneuver.SLAM:
        if pos not in (GrapplePosition.REAR_CONTROL.value, GrapplePosition.MOUNTED.value):
            result["action"] = "requires_rear_or_mounted"
            result["hit"] = False
            return result
        stone_bonus = 4 if attacker.terrain_context in ("barrow", "stone", "rock") else 0
        opposed = _opp(attacker.mig, defender.mig)
        if opposed.winner == "attacker":
            dmg = random.randint(1, 8) + (attacker.mig // 3) + stone_bonus
            w = defender.apply_wound("torso", dmg)
            defender.add_condition(ConditionType.STAGGERED, 1)
            result["hit"] = True
            result["final_damage"] = dmg
            result["wound_severity"] = w.severity
            result["condition_applied"] = "staggered (slammed)"
            if stone_bonus:
                result["terrain_bonus"] = stone_bonus
        else:
            gs.position = GrapplePosition.NEUTRAL_CLINCH.value
            gs.dominant = ""
            result["hit"] = False
        result["winner"] = opposed.winner

    elif maneuver == Maneuver.WEAPON_PRESS:
        if pos != GrapplePosition.DOMINANT_CLINCH.value:
            result["action"] = "requires_dominant_clinch"
            result["hit"] = False
            return result
        if defender.weapon_type in ("unarmed", "shield"):
            result["action"] = "no_edged_weapon"
            result["hit"] = False
            return result
        if defender.has_condition(ConditionType.DISARMED):
            result["action"] = "already_disarmed"
            result["hit"] = False
            return result
        opposed = _opp(attacker.nim, defender.nim)
        if opposed.winner == "attacker":
            self_dmg = max(1, defender.weapon_base // 2)
            w = defender.apply_wound("torso", self_dmg)
            if defender.hp < defender.max_hp * 0.3:
                defender.add_condition(ConditionType.DISARMED, -1)
                result["condition_applied"] = "weapon_pressed + disarmed"
            else:
                result["condition_applied"] = "weapon_pressed (self-damage)"
            result["hit"] = True
            result["final_damage"] = self_dmg
            result["wound_severity"] = w.severity
        else:
            result["hit"] = False
        result["winner"] = opposed.winner

    elif maneuver == Maneuver.BREAK_DISTANCE:
        opposed = _opp(attacker.nim, defender.nim)
        if opposed.winner == "attacker":
            _clear_grapple(attacker, defender)
            attacker.ground = False
            result["condition_applied"] = "grapple_broken (safe exit)"
            result["hit"] = True
        else:
            if pos != GrapplePosition.DOMINANT_CLINCH.value:
                gs.position = GrapplePosition.DOMINANT_CLINCH.value
                gs.dominant = defender.name
            result["hit"] = False
        result["winner"] = opposed.winner

    elif maneuver == Maneuver.PIN_HOLD:
        if pos != GrapplePosition.MOUNTED.value:
            result["action"] = "requires_mounted"
            result["hit"] = False
            return result
        opposed = _opp(attacker.mig, defender.mig, d_extra=-10)
        if opposed.winner == "attacker":
            defender.add_condition(ConditionType.PINNED, -1)
            if "grapple_no_stamina_cost" not in attacker.traits:
                attacker.spend_stamina(1)
            result["condition_applied"] = "pinned"
            result["hit"] = True
        else:
            gs.position = GrapplePosition.NEUTRAL_CLINCH.value
            gs.dominant = ""
            defender.ground = False
            result["hit"] = False
        result["winner"] = opposed.winner

    # ── Glíma Finishers ──

    elif maneuver == Maneuver.GLIMA_LAS:
        if pos != GrapplePosition.DOMINANT_CLINCH.value:
            result["action"] = "requires_dominant_clinch"
            result["hit"] = False
            return result
        opposed = _opp(attacker.nim, defender.nim)
        if opposed.winner == "attacker":
            defender.add_condition(ConditionType.PRONE, -1)
            defender.add_condition(ConditionType.STAGGERED, 1)
            _clear_grapple(attacker, defender)
            result["hit"] = True
            result["condition_applied"] = "prone + staggered (back-heel)"
        else:
            gs.position = GrapplePosition.NEUTRAL_CLINCH.value
            gs.dominant = ""
            result["hit"] = False
        result["winner"] = opposed.winner

    elif maneuver == Maneuver.GLIMA_SNUNINGUR:
        if pos != GrapplePosition.DOMINANT_CLINCH.value:
            result["action"] = "requires_dominant_clinch"
            result["hit"] = False
            return result
        avg_attr = (attacker.mig + attacker.nim) // 2
        avg_def = (defender.mig + defender.nim) // 2
        opposed = _opp(avg_attr, avg_def)
        if opposed.winner == "attacker":
            dmg = random.randint(1, 8)
            w = defender.apply_wound("torso", dmg)
            defender.add_condition(ConditionType.PRONE, -1)
            if attacker.glima_mode or attacker.wants_nonlethal:
                attacker.ground = True
                defender.ground = True
                gs.position = GrapplePosition.SIDE_CONTROL.value
                gs.dominant = attacker.name
                result["condition_applied"] = "rotation\u2192side_control"
            else:
                _clear_grapple(attacker, defender)
                result["condition_applied"] = "rotation\u2192free"
            result["hit"] = True
            result["final_damage"] = dmg
            result["wound_severity"] = w.severity
        else:
            _clear_grapple(attacker, defender)
            result["hit"] = False
        result["winner"] = opposed.winner

    elif maneuver == Maneuver.GLIMA_BEINHNYKKUR:
        if pos != GrapplePosition.SIDE_CONTROL.value:
            result["action"] = "requires_side_control"
            result["hit"] = False
            return result
        opposed = _opp(attacker.nim, defender.nim)
        if opposed.winner == "attacker":
            w = defender.apply_wound("legs", 8)
            result["hit"] = True
            result["final_damage"] = 8
            result["wound_severity"] = w.severity
            result["condition_applied"] = "tendon_torn"
        else:
            gs.position = GrapplePosition.REAR_CONTROL.value
            gs.dominant = defender.name
            result["hit"] = False
        result["winner"] = opposed.winner

    elif maneuver == Maneuver.GLIMA_HNAKKATAK:
        has_grip = (
            "long_hair" in defender.traits or "bearded" in defender.traits
            or getattr(defender, "hair", "short") in ("long", "shoulder")
        )
        if not has_grip:
            result["action"] = "no_hair_grip"
            result["hit"] = False
            return result
        opposed = _opp(attacker.nim, defender.nim)
        if opposed.winner == "attacker":
            defender.add_condition(ConditionType.PRONE, -1)
            defender.add_condition(ConditionType.DAZED, 2)
            _clear_grapple(attacker, defender)
            result["hit"] = True
            result["condition_applied"] = "prone + dazed (nape takedown)"
        else:
            result["hit"] = False
        result["winner"] = opposed.winner

    return result


# ───────────────────────────────────────────────────────────────────────
# Resolution — Dirty tactics (D1–D8)
# ───────────────────────────────────────────────────────────────────────

def resolve_dirty(
    attacker: Fighter,
    defender: Fighter,
    maneuver: Maneuver,
    result: dict,
) -> dict:
    """Resolve a dirty tactic. WIT ≥ 6 defenders may partially negate."""
    wit_mitigated = False
    if defender.wit >= 6 and not defender.has_condition(ConditionType.PINNED):
        wit_check = resolve_check(defender.wit, 0, -5, f"{defender.name} WIT interrupt")
        if wit_check.result in (ResultLevel.SUCCESS, ResultLevel.CRITICAL_SUCCESS):
            wit_mitigated = True
            result["wit_interrupt"] = True

    grappled = attacker.has_condition(ConditionType.GRAPPLED)

    if maneuver == Maneuver.BITE:
        outside_penalty = 0 if grappled else -30
        opposed = resolve_opposed(
            attacker.nim, attacker.brawl_skill,
            attacker.condition_attack_mod() + outside_penalty,
            defender.wit, 0, defender.condition_defense_mod(),
            attacker.name, defender.name,
        )
        result["winner"] = opposed.winner
        if opposed.winner == "attacker":
            crit = opposed.attacker.result == ResultLevel.CRITICAL_SUCCESS
            dmg = random.randint(4, 6) if crit else random.randint(1, 3)
            if wit_mitigated:
                dmg = max(1, dmg // 2)
            w = defender.apply_wound("head", dmg)
            result["hit"] = True
            result["location"] = "head"
            result["final_damage"] = dmg
            result["wound_severity"] = w.severity
            result["wound_subtype"] = "bite"
            wil_check = resolve_check(defender.wil, 0, 0, f"{defender.name} bite WIL")
            if wil_check.result in (ResultLevel.FAILURE, ResultLevel.CRITICAL_FAILURE):
                defender.add_condition(ConditionType.PAIN_SHOCK, 1)
                result["condition_applied"] = "pain_shock"
            if attacker.is_undead:
                result["special"] = "chilling_grip"
        else:
            result["hit"] = False

    elif maneuver == Maneuver.HEADBUTT:
        opposed = resolve_opposed(
            attacker.mig, max(attacker.brawl_skill, 0),
            attacker.condition_attack_mod(),
            defender.nim, 0, defender.condition_defense_mod(),
            attacker.name, defender.name,
        )
        result["winner"] = opposed.winner
        if opposed.winner == "attacker":
            dmg = random.randint(2, 4)
            if wit_mitigated:
                dmg = max(1, dmg // 2)
            attacker.hp = max(0, attacker.hp - 1)
            result["attacker_self_damage"] = 1
            loc = random.choice(["head", "head", "torso"])
            w = defender.apply_wound(loc, dmg)
            result["hit"] = True
            result["location"] = loc
            result["final_damage"] = dmg
            result["wound_severity"] = w.severity
            crit = opposed.attacker.result == ResultLevel.CRITICAL_SUCCESS
            if loc == "head":
                if crit:
                    defender.add_condition(ConditionType.DAZED, 1)
                    result["condition_applied"] = "dazed (nasal)"
                else:
                    defender.add_condition(ConditionType.BLEEDING_NOSE, -1)
                    result["condition_applied"] = "bleeding_nose"
            else:
                defender.add_condition(ConditionType.STAGGERED, 1)
                result["condition_applied"] = "staggered"
        else:
            attacker.hp = max(0, attacker.hp - 1)
            defender.hp = max(0, defender.hp - 1)
            attacker.add_condition(ConditionType.STAGGERED, 1)
            defender.add_condition(ConditionType.STAGGERED, 1)
            result["hit"] = False
            result["mutual_damage"] = {"attacker": 1, "defender": 1}

    elif maneuver == Maneuver.NOSE_BUTT:
        gs = attacker.grapple_state
        pos_ok = (
            defender.has_condition(ConditionType.PINNED)
            or (gs is not None and gs.position == GrapplePosition.DOMINANT_CLINCH.value)
        )
        if not pos_ok:
            result["action"] = "requires_dominant_or_pinned_target"
            result["hit"] = False
            return result
        opposed = resolve_opposed(
            attacker.mig, 0, attacker.condition_attack_mod(),
            defender.nim, 0, defender.condition_defense_mod(),
            attacker.name, defender.name,
        )
        result["winner"] = opposed.winner
        if opposed.winner == "attacker":
            w = defender.apply_wound("head", 3)
            defender.add_condition(ConditionType.BLEEDING_NOSE, -1)
            result["hit"] = True
            result["location"] = "head"
            result["final_damage"] = 3
            result["wound_severity"] = w.severity
            result["condition_applied"] = "bleeding_nose"
        else:
            attacker.hp = max(0, attacker.hp - 1)
            result["hit"] = False
            result["attacker_self_damage"] = 1

    elif maneuver == Maneuver.DIRT_EYES:
        if defender.is_undead:
            result["action"] = "undead_immune_dirt"
            result["hit"] = False
            return result
        opposed = resolve_opposed(
            attacker.nim, attacker.wit,
            attacker.condition_attack_mod(),
            defender.wit, 0, defender.condition_defense_mod(),
            attacker.name, defender.name,
        )
        result["winner"] = opposed.winner
        if opposed.winner == "attacker":
            blind_rounds = 1 if wit_mitigated else random.randint(1, 3)
            defender.add_condition(ConditionType.BLINDED, blind_rounds)
            result["hit"] = True
            result["condition_applied"] = f"blinded ({blind_rounds} rounds)"
            if opposed.attacker.result == ResultLevel.CRITICAL_SUCCESS:
                defender.add_condition(ConditionType.STAGGERED, 1)
                result["condition_applied"] += " + staggered"
        else:
            result["hit"] = False

    elif maneuver == Maneuver.SPIT_EYES:
        if defender.is_undead:
            result["action"] = "undead_immune_spit"
            result["hit"] = False
            return result
        opposed = resolve_opposed(
            attacker.nim, 0, attacker.condition_attack_mod(),
            defender.nim, 0, defender.condition_defense_mod(),
            attacker.name, defender.name,
        )
        result["winner"] = opposed.winner
        if opposed.winner == "attacker":
            defender.add_condition(ConditionType.PAIN_SHOCK, 1)
            result["hit"] = True
            result["condition_applied"] = "spit_distracted (-10 next round)"
            result["special"] = "headbutt_combo_available"
        else:
            result["hit"] = False

    elif maneuver == Maneuver.HAIR_GRIP:
        has_grip = (
            "long_hair" in defender.traits or "bearded" in defender.traits
            or getattr(defender, "hair", "short") in ("long", "shoulder")
        )
        if not has_grip:
            result["action"] = "no_hair_grip"
            result["hit"] = False
            return result
        opposed = resolve_opposed(
            attacker.nim, attacker.brawl_skill,
            attacker.condition_attack_mod(),
            defender.nim, defender.brawl_skill,
            defender.condition_defense_mod(),
            attacker.name, defender.name,
        )
        result["winner"] = opposed.winner
        if opposed.winner == "attacker":
            if attacker.grapple_state:
                attacker.grapple_state.position = GrapplePosition.DOMINANT_CLINCH.value
                attacker.grapple_state.dominant = attacker.name
            result["hit"] = True
            result["condition_applied"] = "hair_gripped (+10 follow-up)"
            result["special"] = "hnakkatak_enabled"
        else:
            attacker.add_condition(ConditionType.ARM_LOCKED, 1)
            result["hit"] = False

    elif maneuver == Maneuver.THUMB_GOUGE:
        if defender.is_undead:
            result["action"] = "undead_immune_gouge"
            result["hit"] = False
            return result
        gs = attacker.grapple_state
        pos_ok = (
            defender.has_condition(ConditionType.PINNED)
            or (gs is not None and gs.position in (
                GrapplePosition.MOUNTED.value, GrapplePosition.SIDE_CONTROL.value,
            ))
        )
        if not pos_ok:
            result["action"] = "requires_mounted_pinned_or_side_control"
            result["hit"] = False
            return result
        opposed = resolve_opposed(
            attacker.nim, 0, attacker.condition_attack_mod(),
            defender.wil, 0, defender.condition_defense_mod(),
            attacker.name, defender.name,
        )
        result["winner"] = opposed.winner
        if opposed.winner == "attacker":
            crit = opposed.attacker.result == ResultLevel.CRITICAL_SUCCESS
            if crit:
                w = defender.apply_wound("head", random.randint(1, 4))
                result["hit"] = True
                result["final_damage"] = w.damage
                result["wound_severity"] = w.severity
                result["condition_applied"] = "eye_damage"
            else:
                result["hit"] = True
                result["condition_applied"] = "thumb_gouge (WIL test)"
        else:
            result["hit"] = False

    elif maneuver == Maneuver.EAR_CUP:
        if defender.is_undead:
            result["action"] = "undead_immune_ear_cup"
            result["hit"] = False
            return result
        opposed = resolve_opposed(
            attacker.mig, max(attacker.brawl_skill, 0),
            attacker.condition_attack_mod(),
            defender.nim, 0, defender.condition_defense_mod(),
            attacker.name, defender.name,
        )
        result["winner"] = opposed.winner
        if opposed.winner == "attacker":
            defender.add_condition(ConditionType.DAZED, 1)
            result["hit"] = True
            result["condition_applied"] = "dazed (ear cup)"
            if opposed.attacker.result == ResultLevel.CRITICAL_SUCCESS:
                tou_check = resolve_check(
                    defender.tou, 0, 0, f"{defender.name} ear_cup TOU"
                )
                if tou_check.result in (ResultLevel.FAILURE, ResultLevel.CRITICAL_FAILURE):
                    defender.add_condition(ConditionType.PRONE, -1)
                    result["condition_applied"] += " + prone"
        else:
            attacker.add_condition(ConditionType.STAGGERED, 1)
            result["hit"] = False

    return result


# ───────────────────────────────────────────────────────────────────────
# Choke round tick and submission / yield
# ───────────────────────────────────────────────────────────────────────

def advance_choke_round(
    gs: "GrappleState",
    defender: Fighter,
    actions: list,
) -> bool:
    """Increment GrappleState.choke_rounds; TOU check for unconsciousness at round 4+.

    Returns True if defender goes unconscious (is captured, not killed).
    Called each end-of-round while defender has ConditionType.CHOKED.
    """
    gs.choke_rounds += 1
    if gs.choke_rounds < 4:
        return False

    tou_chance = min(95, defender.tou * 5 + 50)
    roll = random.randint(1, 100)
    if roll > tou_chance:
        # Unconscious — mark as prone/helpless (not dead)
        defender.add_condition(ConditionType.PRONE, 9999)
        actions.append({
            "type": "choke_unconscious",
            "fighter": defender.name,
            "choke_rounds": gs.choke_rounds,
            "tou_check": tou_chance,
            "roll": roll,
            "result": "unconscious",
        })
        return True

    actions.append({
        "type": "choke_resisted",
        "fighter": defender.name,
        "choke_rounds": gs.choke_rounds,
        "tou_check": tou_chance,
        "roll": roll,
        "result": "still_conscious",
    })
    return False


def check_submission_yield(
    grappler: Fighter,
    subject: Fighter,
    gs: "GrappleState",
    actions: list,
) -> bool:
    """Subject in PIN or throat-seize at ≤25% HP may call yield.

    Grappler rolls WIL*5+50 vs d100:
    - Success → subject is captured (PRONE/permanent); attacker accepts yield.
    - Failure  → grappler's pride forces release; choke_rounds reset.

    Returns True if subject is successfully captured.
    """
    if subject.hp > subject.max_hp * 0.25:
        return False
    if not (subject.has_condition(ConditionType.PINNED)
            or subject.has_condition(ConditionType.CHOKED)):
        return False

    wil_chance = min(95, grappler.wil * 5 + 50)
    roll = random.randint(1, 100)
    if roll <= wil_chance:
        # Grappler accepts — subject captured, not killed
        subject.add_condition(ConditionType.PRONE, 9999)
        actions.append({
            "type": "submission_accepted",
            "grappler": grappler.name,
            "subject": subject.name,
            "wil_check": wil_chance,
            "roll": roll,
            "result": "captured",
        })
        return True
    else:
        # Pride forces release
        subject.remove_condition(ConditionType.PINNED)
        subject.remove_condition(ConditionType.CHOKED)
        gs.choke_rounds = 0
        actions.append({
            "type": "submission_pride_release",
            "grappler": grappler.name,
            "subject": subject.name,
            "wil_check": wil_chance,
            "roll": roll,
            "result": "released_pride",
        })
        return False

