"""combat_ai.py — Iron Ledger tactical AI: stance/maneuver selection."""
import random

from combat_types import *
from combat_model import Fighter

# Tactical AI
# ───────────────────────────────────────────────────────────────────────

def choose_stance(fighter: Fighter, opponent: Fighter) -> Stance:
    """Select stance based on fighter state and opponent."""
    # Fire aversion: creature stays DEFENSIVE when opponent carries fire
    if "fire_aversion" in fighter.traits and "fire" in getattr(opponent, "weapon_properties", []):
        return Stance.DEFENSIVE
    # Glíma / wrestling mode — commit forward, never retreat
    if fighter.glima_mode:
        if fighter.stamina > fighter.max_stamina * 0.3:
            return Stance.AGGRESSIVE
        return Stance.BALANCED
    # Undead don't self-preserve — they never retreat based on HP or stamina
    if fighter.is_undead:
        if fighter.mig >= 6:
            return Stance.AGGRESSIVE
        return Stance.BALANCED
    # Critically wounded — defensive
    if fighter.hp < fighter.max_hp * 0.3:
        return Stance.DEFENSIVE
    # Low stamina — conserve
    if fighter.stamina < fighter.max_stamina * 0.3:
        return Stance.DEFENSIVE
    # Fresh, strong, might-based — aggressive
    if (fighter.hp > fighter.max_hp * 0.7
            and fighter.stamina > fighter.max_stamina * 0.5
            and fighter.mig >= 6):
        return Stance.AGGRESSIVE
    # Skilled and nimble — low guard sometimes (bait and punish)
    if fighter.weapon_skill >= 3 and fighter.nim >= 6:
        return random.choice([Stance.BALANCED, Stance.LOW_GUARD])
    return Stance.BALANCED


def choose_maneuver(fighter: Fighter, opponent: Fighter) -> Maneuver:
    """Select maneuver based on current state."""
    # ── Batch 8: Lure_song entranced — waste rounds in GUARD ──
    if getattr(fighter, "lure_song_entranced_rounds", 0) > 0:
        return Maneuver.GUARD

    # Fire aversion: never close to melee with fire-weapon opponent
    if "fire_aversion" in fighter.traits and "fire" in getattr(opponent, "weapon_properties", []):
        if fighter.current_distance <= 1:
            return Maneuver.STEP_BACK
        return Maneuver.GUARD

    # tactical_withdrawal_once: disengage on first critical HP moment (once)
    if ("tactical_withdrawal_once" in fighter.traits
            and fighter.hp < fighter.max_hp * 0.60
            and "tactical_withdrawal_once_used" not in getattr(fighter, "used_traits", [])):
        fighter.used_traits.append("tactical_withdrawal_once_used")
        fighter.tactical_withdrawal_active = True
        return Maneuver.GUARD

    # ── Recovery priorities ──
    if fighter.has_condition(ConditionType.PRONE):
        return Maneuver.STAND
    if fighter.has_condition(ConditionType.DISARMED):
        if (
            fighter.can_maneuver(Maneuver.GRAPPLE)
            and not fighter.has_condition(ConditionType.GRAPPLED)
        ):
            return Maneuver.GRAPPLE
        return Maneuver.PICK_UP_WEAPON

    # ── Pinned — almost nothing available ──
    if fighter.has_condition(ConditionType.PINNED):
        pool = [Maneuver.BITE]
        if not opponent.is_undead:
            pool.extend([Maneuver.THUMB_GOUGE, Maneuver.SPIT_EYES])
        return random.choice(pool)

    # ── Active grapple state — use sub-game AI ──
    if fighter.grapple_state is not None:
        return choose_grapple_followup(fighter, opponent)

    # ── Grappled (old-style, no state) — try dirty trick or break free ──
    if fighter.has_condition(ConditionType.GRAPPLED):
        hp_ratio = fighter.hp / max(1, fighter.max_hp)
        if hp_ratio < 0.35 and not opponent.is_undead:
            pool = [Maneuver.HEADBUTT, Maneuver.BITE, Maneuver.SPIT_EYES]
            return random.choice(pool)
        if random.random() < 0.3:
            return Maneuver.HEADBUTT
        return Maneuver.SHOVE

    if fighter.has_condition(ConditionType.BOUND):
        return Maneuver.SHOVE

    # ── Suppression pressure (missile phase) ──
    if fighter.has_condition(ConditionType.SUPPRESSED) and not fighter.has_condition(ConditionType.GRAPPLED):
        # Under arrows and thrown volleys, fighters hesitate, guard, or peel back.
        if random.random() < 0.55:
            return Maneuver.STEP_BACK if fighter.can_maneuver(Maneuver.STEP_BACK) else Maneuver.GUARD

    # ── Exhausted ──
    if fighter.stamina <= 0:
        return Maneuver.GUARD
    base_cost = 2
    extra = STANCE_MODS[fighter.stance]["stamina_extra"]
    if fighter.stamina < base_cost + extra:
        return Maneuver.GUARD

    # ── Desperate dirty tricks (critical HP, unengaged) ──
    hp_ratio = fighter.hp / max(1, fighter.max_hp)
    if hp_ratio < 0.25 and random.random() < 0.35:
        dirty_pool = [Maneuver.HEADBUTT]
        if not opponent.is_undead:
            dirty_pool.extend([Maneuver.SPIT_EYES, Maneuver.DIRT_EYES])
        if "bearded" in opponent.traits or "long_hair" in opponent.traits or opponent.hair in ("shoulder", "long"):
            dirty_pool.append(Maneuver.HAIR_GRIP)
        return random.choice(dirty_pool)

    # ── Glíma mode — prefer wrestling entry over lethal combat ──
    if fighter.glima_mode:
        wep_mods = GRAPPLE_WEAPON_MODIFIERS.get(fighter.weapon_type, GRAPPLE_WEAPON_MODIFIERS["generic"])
        if fighter.stamina > fighter.max_stamina * 0.4:
            pool = [Maneuver.BROKARTOK, Maneuver.BROKARTOK, Maneuver.LAUSATOK, Maneuver.TACKLE]
            return random.choice(pool)
        return Maneuver.GUARD  # low stamina — recover rather than commit to grapple

    # ── Wants nonlethal — initiate grapple when able ──
    if fighter.wants_nonlethal and not fighter.has_condition(ConditionType.GRAPPLED):
        if random.random() < 0.5 and fighter.stamina > fighter.max_stamina * 0.3:
            return random.choice([Maneuver.BROKARTOK, Maneuver.LAUSATOK, Maneuver.GRAPPLE])

    # ── Distance management — correct range before attacking ──
    if not fighter.has_condition(ConditionType.GRAPPLED):
        reach_pen, _, _ = compute_reach_penalty(fighter.weapon_type, fighter.current_distance)
        my_pref = preferred_distance_band(fighter.weapon_type)
        if reach_pen <= -15:
            # Weapon fouled — draw backup before retreating (if one is available)
            if reach_pen <= -30 and fighter.can_maneuver(Maneuver.SWITCH_WEAPON):
                return Maneuver.SWITCH_WEAPON
            # Significant penalty: strongly correct the distance
            if fighter.current_distance > my_pref:
                return Maneuver.STEP_IN
            elif fighter.current_distance < my_pref:
                return Maneuver.STEP_BACK
        elif reach_pen <= -5 and random.random() < 0.70:
            # Moderate penalty: usually correct
            if fighter.current_distance > my_pref:
                return Maneuver.STEP_IN
            elif fighter.current_distance < my_pref:
                return Maneuver.STEP_BACK
        # Long weapon vs short-weapon opponent closing in — try to maintain range
        if (opponent.weapon_reach + 2 <= fighter.weapon_reach
                and fighter.current_distance < my_pref
                and random.random() < 0.55):
            return Maneuver.STEP_BACK

    # ── Terrain/size awareness ──
    if not fighter.has_condition(ConditionType.GRAPPLED):
        _fspace = get_space_class(fighter.terrain_context)
        _fsize  = get_weapon_size(fighter.weapon_type)
        # Switch to shorter weapon when wielding large weapon in tight terrain
        if fighter.can_maneuver(Maneuver.SWITCH_WEAPON):
            if _fspace in ("very_tight", "tight") and _fsize >= 4:
                _secs_small = [s for s in fighter.secondary_weapons
                               if get_weapon_size(s["type"]) <= 2]
                if _secs_small:
                    return Maneuver.SWITCH_WEAPON
        # Polearm/great weapon unusable in very_tight: stall or escape
        if _fspace == "very_tight" and _fsize >= 5:
            if fighter.can_maneuver(Maneuver.STEP_BACK):
                return Maneuver.STEP_BACK
            return Maneuver.GUARD
        # Short weapon in tight/very_tight: space advantage — be more aggressive
        if _fspace in ("tight", "very_tight") and _fsize <= 1:
            if fighter.stamina > fighter.max_stamina * 0.3 and random.random() < 0.25:
                pool = ([Maneuver.CUT, Maneuver.THRUST]
                        if fighter.can_maneuver(Maneuver.THRUST) else [Maneuver.CUT])
                return random.choice(pool)

    # ── Opportunistic: exploit opponent conditions ──
    if opponent.has_condition(ConditionType.PRONE):
        if fighter.can_maneuver(Maneuver.HEAVY_BLOW):
            return Maneuver.HEAVY_BLOW
        return Maneuver.CUT
    if opponent.has_condition(ConditionType.STAGGERED):
        return Maneuver.CUT
    if opponent.has_condition(ConditionType.BOUND):
        if fighter.can_maneuver(Maneuver.DISARM):
            return Maneuver.DISARM
        return Maneuver.CUT

    # ── Stance-influenced selection ──
    if fighter.stance == Stance.AGGRESSIVE:
        pool = [Maneuver.CUT, Maneuver.CUT, Maneuver.HEAVY_BLOW]
        if fighter.can_maneuver(Maneuver.THRUST):
            pool.append(Maneuver.THRUST)
        return random.choice(pool)

    if fighter.stance == Stance.DEFENSIVE:
        pool = [Maneuver.GUARD, Maneuver.CUT]
        if fighter.can_maneuver(Maneuver.THRUST):
            pool.append(Maneuver.THRUST)
        return random.choice(pool)

    if fighter.stance == Stance.LOW_GUARD:
        return Maneuver.CUT

    # ── Balanced — tactical variety ──
    pool = [Maneuver.CUT, Maneuver.CUT]
    if fighter.can_maneuver(Maneuver.THRUST):
        pool.append(Maneuver.THRUST)
    if fighter.stamina > fighter.max_stamina // 2:
        if fighter.can_maneuver(Maneuver.HEAVY_BLOW):
            pool.append(Maneuver.HEAVY_BLOW)
    if fighter.can_maneuver(Maneuver.FEINT) and random.random() < 0.12:
        return Maneuver.FEINT
    if fighter.can_maneuver(Maneuver.SHOVE) and random.random() < 0.08:
        return Maneuver.SHOVE
    if fighter.can_maneuver(Maneuver.BIND) and random.random() < 0.08:
        return Maneuver.BIND
    if fighter.can_maneuver(Maneuver.SHIELD_BASH) and random.random() < 0.10:
        return Maneuver.SHIELD_BASH
    # Anti-armor options
    if opponent.get_armor_at("torso") >= 4:
        if fighter.can_maneuver(Maneuver.HALF_SWORD):
            pool.append(Maneuver.HALF_SWORD)
        if fighter.can_maneuver(Maneuver.MORDSCHLAG):
            pool.append(Maneuver.MORDSCHLAG)

    valid = [m for m in pool if fighter.can_maneuver(m)]
    return random.choice(valid) if valid else Maneuver.CUT


def choose_grapple_followup(fighter: Fighter, opponent: Fighter) -> Maneuver:
    """Select next in-grapple maneuver based on current position."""
    gs = fighter.grapple_state
    if gs is None:
        return Maneuver.SHOVE

    pos = gs.position
    glima = fighter.glima_mode or fighter.wants_nonlethal
    is_specialist = (
        fighter.brawl_skill >= 3
        or "glima_brokartok" in fighter.traits
        or "glima_lausatok" in fighter.traits
    )

    if pos == GrapplePosition.MOUNTED.value:
        if glima:
            pool = [Maneuver.PIN_HOLD, Maneuver.PIN_HOLD, Maneuver.THROAT_SEIZE, Maneuver.KNEE_STRIKE]
        else:
            pool = [Maneuver.PIN_HOLD, Maneuver.KNEE_STRIKE, Maneuver.THROAT_SEIZE, Maneuver.SLAM]
        if not opponent.is_undead:
            pool.extend([Maneuver.THUMB_GOUGE, Maneuver.THUMB_GOUGE])
        return random.choice(pool)

    if pos == GrapplePosition.DOMINANT_CLINCH.value:
        if glima:
            pool = [Maneuver.LEG_TRIP, Maneuver.THROAT_SEIZE, Maneuver.ARM_TRAP]
        else:
            pool = [Maneuver.LEG_TRIP, Maneuver.HIP_THROW, Maneuver.THROAT_SEIZE,
                    Maneuver.ARM_TRAP, Maneuver.WEAPON_PRESS]
        if is_specialist:
            pool.extend([Maneuver.GLIMA_LAS, Maneuver.GLIMA_SNUNINGUR])
            pool.extend([Maneuver.GLIMA_HNAKKATAK]
                        if ("long_hair" in opponent.traits or "bearded" in opponent.traits
                            or opponent.hair in ("shoulder", "long")) else [])
        return random.choice(pool)

    if pos in (GrapplePosition.CLINCH.value, GrapplePosition.NEUTRAL_CLINCH.value):
        pool = [Maneuver.CLINCH_IMPROVE, Maneuver.CLINCH_IMPROVE,
                Maneuver.ELBOW_STRIKE, Maneuver.KNEE_STRIKE]
        if not glima:
            pool.append(Maneuver.BREAK_DISTANCE)
        return random.choice(pool)

    if pos == GrapplePosition.REAR_CONTROL.value:
        if glima:
            pool = [Maneuver.THROAT_SEIZE, Maneuver.THROAT_SEIZE, Maneuver.PIN_HOLD]
        else:
            pool = [Maneuver.SLAM, Maneuver.SLAM, Maneuver.THROAT_SEIZE]
        return random.choice(pool)

    if pos == GrapplePosition.GUARD_BOTTOM.value:
        pool = [Maneuver.BREAK_DISTANCE, Maneuver.GROUND_CONTROL]
        if not opponent.is_undead:
            pool.extend([Maneuver.BITE, Maneuver.HEADBUTT])
        return random.choice(pool)

    if pos == GrapplePosition.SIDE_CONTROL.value:
        pool = [Maneuver.ARM_TRAP, Maneuver.GROUND_CONTROL]
        if is_specialist:
            pool.append(Maneuver.GLIMA_BEINHNYKKUR)
        return random.choice(pool)

    # Default: fight for dominant grip
    return Maneuver.CLINCH_IMPROVE


def can_counter(fighter: Fighter) -> bool:
    """Check if a fighter can execute a Nachreisen (counter-attack)."""
    if fighter.is_down or fighter.stamina < 1:
        return False
    if fighter.has_condition(ConditionType.PRONE):
        return False
    if fighter.has_condition(ConditionType.DISARMED):
        return False
    if fighter.has_condition(ConditionType.DAZED):
        return False
    if fighter.has_condition(ConditionType.TUNNEL_VISION):
        return False
    # Tactical withdrawal in progress — no counters this round
    if getattr(fighter, "tactical_withdrawal_active", False):
        return False
    # Undead without combat memory just shamble — no tactical counters
    if fighter.is_undead and "combat_memory" not in fighter.traits:
        return False
    # Low guard: always counter (it is the entire point)
    if fighter.stance == Stance.LOW_GUARD:
        return True
    # Skilled fighters counter with probability based on skill
    if fighter.weapon_skill >= 3:
        return random.random() < 0.60
    if fighter.weapon_skill >= 2:
        return random.random() < 0.35
    return False


# ───────────────────────────────────────────────────────────────────────
