#!/usr/bin/env python3
"""
Iron Ledger — Core Resolution Engine

Resolves action checks, opposed checks, and provides shared utilities
for all simulation scripts. This is the heart of the Iron Ledger system.

Usage:
    python engine.py check --attr 6 --skill 3 --diff 0
    python engine.py check --attr 6 --skill 3 --diff 0 --mods -10 +5
    python engine.py opposed --a-attr 7 --a-skill 3 --d-attr 5 --d-skill 2
"""

import argparse
import random
import sys
import json
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional


class ResultLevel(Enum):
    CRITICAL_SUCCESS = "critical_success"
    SUCCESS = "success"
    FAILURE = "failure"
    CRITICAL_FAILURE = "critical_failure"


@dataclass
class CheckResult:
    """Result of a single action check."""
    final_chance: int
    roll: int
    result: ResultLevel
    margin: int  # positive = degrees of success, negative = degrees of failure
    details: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        d["result"] = self.result.value
        return d


@dataclass
class OpposedResult:
    """Result of an opposed check between two characters."""
    attacker: CheckResult
    defender: CheckResult
    winner: str  # "attacker", "defender", or "stalemate"
    net_margin: int
    details: str = ""

    def to_dict(self) -> dict:
        return {
            "attacker": self.attacker.to_dict(),
            "defender": self.defender.to_dict(),
            "winner": self.winner,
            "net_margin": self.net_margin,
            "details": self.details,
        }


def compute_success_chance(attribute: int, skill: int, modifiers: int = 0) -> int:
    """
    Compute final success chance as a percentage.

    Formula: (attribute × 5) + (skill × 10) + 15 + modifiers
    Clamped to [5, 95].
    """
    base = (attribute * 5) + (skill * 10) + 15
    final = base + modifiers
    return max(5, min(95, final))


def resolve_check(
    attribute: int,
    skill: int,
    modifiers: int = 0,
    label: str = "",
) -> CheckResult:
    """
    Resolve a single action check.

    Returns a CheckResult with the roll, result level, and margin.
    """
    final_chance = compute_success_chance(attribute, skill, modifiers)
    roll = random.randint(1, 100)

    crit_threshold = max(1, int(final_chance * 0.20))

    if roll <= crit_threshold:
        result = ResultLevel.CRITICAL_SUCCESS
        margin = final_chance - roll
    elif roll <= final_chance:
        result = ResultLevel.SUCCESS
        margin = final_chance - roll
    elif roll > 95:
        result = ResultLevel.CRITICAL_FAILURE
        margin = final_chance - roll
    else:
        result = ResultLevel.FAILURE
        margin = final_chance - roll

    details = (
        f"{label + ': ' if label else ''}"
        f"chance={final_chance}%, roll={roll}, "
        f"result={result.value}, margin={margin:+d}"
    )

    return CheckResult(
        final_chance=final_chance,
        roll=roll,
        result=result,
        margin=margin,
        details=details,
    )


def resolve_opposed(
    a_attr: int,
    a_skill: int,
    a_mods: int,
    d_attr: int,
    d_skill: int,
    d_mods: int,
    a_label: str = "attacker",
    d_label: str = "defender",
) -> OpposedResult:
    """
    Resolve an opposed check between attacker and defender.
    Winner is whoever has the higher positive margin.
    If both fail, stalemate.
    """
    a_result = resolve_check(a_attr, a_skill, a_mods, a_label)
    d_result = resolve_check(d_attr, d_skill, d_mods, d_label)

    a_succeeded = a_result.result in (ResultLevel.SUCCESS, ResultLevel.CRITICAL_SUCCESS)
    d_succeeded = d_result.result in (ResultLevel.SUCCESS, ResultLevel.CRITICAL_FAILURE)

    # Fix: defender success check
    d_succeeded = d_result.result in (ResultLevel.SUCCESS, ResultLevel.CRITICAL_SUCCESS)

    if a_succeeded and not d_succeeded:
        winner = "attacker"
    elif d_succeeded and not a_succeeded:
        winner = "defender"
    elif a_succeeded and d_succeeded:
        # Both succeeded — compare margins
        if a_result.margin >= d_result.margin:
            winner = "attacker"
        else:
            winner = "defender"
    else:
        winner = "stalemate"

    net_margin = a_result.margin - d_result.margin
    details = (
        f"Opposed: {a_label} (margin {a_result.margin:+d}) vs "
        f"{d_label} (margin {d_result.margin:+d}) → {winner}"
    )

    return OpposedResult(
        attacker=a_result,
        defender=d_result,
        winner=winner,
        net_margin=net_margin,
        details=details,
    )


def roll_d100() -> int:
    """Roll a d100 (1-100)."""
    return random.randint(1, 100)


def roll_dice(count: int, sides: int) -> list[int]:
    """Roll multiple dice and return individual results."""
    return [random.randint(1, sides) for _ in range(count)]


def roll_sum(count: int, sides: int) -> int:
    """Roll multiple dice and return the sum."""
    return sum(roll_dice(count, sides))


def hit_location() -> tuple[str, float]:
    """
    Determine hit location and damage multiplier.
    Returns (location_name, damage_multiplier).
    """
    roll = roll_d100()
    if roll <= 10:
        return ("head", 1.5)
    elif roll <= 40:
        return ("torso", 1.0)
    elif roll <= 50:
        return ("right_arm", 0.8)
    elif roll <= 60:
        return ("left_arm", 0.8)
    elif roll <= 80:
        return ("legs", 0.9)
    elif roll <= 90:
        return ("hands", 0.6)
    else:
        return ("feet", 0.6)


def calculate_damage(
    weapon_base: int,
    might: int,
    location_multiplier: float,
    armor_at_location: int,
) -> int:
    """
    Calculate final damage from a hit.

    raw = weapon_base + (might // 3)
    final = max(0, round(raw * location_multiplier) - armor_at_location)
    """
    raw = weapon_base + (might // 3)
    modified = round(raw * location_multiplier)
    return max(0, modified - armor_at_location)


def wound_severity(damage: int) -> str:
    """Determine wound severity from damage dealt."""
    if damage <= 0:
        return "none"
    elif damage <= 3:
        return "scratch"
    elif damage <= 6:
        return "light"
    elif damage <= 10:
        return "serious"
    elif damage <= 15:
        return "critical"
    else:
        return "mortal"


def compute_max_hp(toughness: int, might: int) -> int:
    """Calculate maximum hit points."""
    return (toughness * 3) + might + 10


def compute_carry_limit(might: int) -> float:
    """Calculate carrying capacity in kg."""
    return (might * 5.0) + 10.0


def compute_initiative(nimbleness: int, wits: int, weapon_speed: int) -> int:
    """Calculate combat initiative."""
    return (nimbleness * 3) + (wits * 2) + weapon_speed + random.randint(1, 20)


def compute_max_stamina(toughness: int, will: int) -> int:
    """Calculate maximum stamina. Stamina represents fighting endurance."""
    return (toughness * 2) + will + 10


def compute_stamina_recovery(toughness: int) -> int:
    """Calculate per-round stamina recovery."""
    return 1 + (toughness // 3)


def compute_march_speed(
    base_km: float = 25.0,
    terrain_mult: float = 1.0,
    weather_mult: float = 1.0,
    season_mult: float = 1.0,
    weak_link: bool = False,
) -> float:
    """Calculate daily march speed in km."""
    speed = base_km * terrain_mult * weather_mult * season_mult
    if weak_link:
        speed *= 0.85
    return round(speed, 1)


def compute_foraging(
    terrain_base: int,
    num_foragers: int,
    avg_forage_skill: float,
    season_mult: float = 1.0,
    weather_mult: float = 1.0,
) -> int:
    """
    Calculate foraging output in food units.

    Uses terrain base lookup by forager count, then applies modifiers.
    """
    # Base output scales with forager count (simplified from table)
    if num_foragers <= 0:
        return 0
    elif num_foragers <= 2:
        base = terrain_base
    elif num_foragers <= 5:
        base = int(terrain_base * 2.5)
    elif num_foragers <= 10:
        base = int(terrain_base * 4.5)
    else:
        base = int(terrain_base * 7.5)

    skill_bonus = 1.0 + (avg_forage_skill * 0.08)
    result = base * season_mult * weather_mult * skill_bonus
    return max(0, int(result))


# --- Galdr / Seiðr / Wyrd Resolution ---

def resolve_galdr(wyrd: int, rune_lore: int, modifiers: int = 0) -> CheckResult:
    """Resolve a galdr (rune scribing) attempt."""
    return resolve_check(wyrd, rune_lore, modifiers, "galdr")


def resolve_seidr(wyrd: int, spirit_lore: int, modifiers: int = 0) -> CheckResult:
    """Resolve a seiðr (spirit talking) attempt. Base is +10 not +15."""
    chance = (wyrd * 5) + (spirit_lore * 10) + 10 + modifiers
    chance = max(5, min(95, chance))
    roll = random.randint(1, 100)
    crit_threshold = max(1, int(chance * 0.20))

    if roll <= crit_threshold:
        result = ResultLevel.CRITICAL_SUCCESS
    elif roll <= chance:
        result = ResultLevel.SUCCESS
    elif roll > 95:
        result = ResultLevel.CRITICAL_FAILURE
    else:
        result = ResultLevel.FAILURE

    margin = chance - roll
    details = f"seiðr: chance={chance}%, roll={roll}, result={result.value}, margin={margin:+d}"

    return CheckResult(
        final_chance=chance, roll=roll, result=result, margin=margin, details=details
    )


def resolve_wyrd_reading(wyrd: int, wyrd_reading_skill: int, modifiers: int = 0) -> CheckResult:
    """Resolve a wyrd-reading (fate divination) attempt."""
    return resolve_check(wyrd, wyrd_reading_skill, modifiers, "wyrd-reading")


def galdr_failure_consequence() -> str:
    """Roll on the galdr failure consequence table."""
    roll = roll_d100()
    if roll <= 40:
        return "fizzle: rune fails, willpower cost still paid"
    elif roll <= 70:
        return f"backlash: {roll_sum(1, 6)} damage to carver, rune cracks"
    elif roll <= 90:
        return "inversion: opposite of intended effect manifests"
    else:
        return "attention: something notices — the Hush falls, wyrd check or gain dread"


# --- CLI ---

def main():
    parser = argparse.ArgumentParser(
        description="Iron Ledger Resolution Engine"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # --- check ---
    check_p = subparsers.add_parser("check", help="Resolve a single action check")
    check_p.add_argument("--attr", type=int, required=True, help="Attribute value (1-10)")
    check_p.add_argument("--skill", type=int, default=0, help="Skill rank (0-5)")
    check_p.add_argument("--mods", type=int, nargs="*", default=[], help="Modifiers (e.g. -10 +5)")
    check_p.add_argument("--label", type=str, default="", help="Label for the check")
    check_p.add_argument("--json", action="store_true", help="Output as JSON")

    # --- opposed ---
    opp_p = subparsers.add_parser("opposed", help="Resolve an opposed check")
    opp_p.add_argument("--a-attr", type=int, required=True, help="Attacker attribute")
    opp_p.add_argument("--a-skill", type=int, default=0, help="Attacker skill")
    opp_p.add_argument("--a-mods", type=int, nargs="*", default=[], help="Attacker modifiers")
    opp_p.add_argument("--d-attr", type=int, required=True, help="Defender attribute")
    opp_p.add_argument("--d-skill", type=int, default=0, help="Defender skill")
    opp_p.add_argument("--d-mods", type=int, nargs="*", default=[], help="Defender modifiers")
    opp_p.add_argument("--json", action="store_true", help="Output as JSON")

    # --- damage ---
    dmg_p = subparsers.add_parser("damage", help="Roll hit location and calculate damage")
    dmg_p.add_argument("--weapon", type=int, required=True, help="Weapon base damage")
    dmg_p.add_argument("--might", type=int, required=True, help="Attacker Might")
    dmg_p.add_argument("--armor", type=int, default=0, help="Armor at hit location")
    dmg_p.add_argument("--json", action="store_true", help="Output as JSON")

    # --- magic ---
    mag_p = subparsers.add_parser("magic", help="Resolve a magic check")
    mag_p.add_argument("--type", choices=["galdr", "seidr", "wyrd"], required=True)
    mag_p.add_argument("--wyrd", type=int, required=True, help="Wyrd attribute")
    mag_p.add_argument("--skill", type=int, default=0, help="Relevant lore skill")
    mag_p.add_argument("--mods", type=int, nargs="*", default=[], help="Modifiers")
    mag_p.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if args.command == "check":
        total_mods = sum(args.mods)
        result = resolve_check(args.attr, args.skill, total_mods, args.label)
        if args.json:
            print(json.dumps(result.to_dict(), indent=2))
        else:
            print(result.details)

    elif args.command == "opposed":
        a_mods = sum(args.a_mods)
        d_mods = sum(args.d_mods)
        result = resolve_opposed(
            args.a_attr, args.a_skill, a_mods,
            args.d_attr, args.d_skill, d_mods,
        )
        if args.json:
            print(json.dumps(result.to_dict(), indent=2))
        else:
            print(result.details)
            print(f"  {result.attacker.details}")
            print(f"  {result.defender.details}")

    elif args.command == "damage":
        loc, mult = hit_location()
        dmg = calculate_damage(args.weapon, args.might, mult, args.armor)
        severity = wound_severity(dmg)
        output = {
            "location": loc,
            "multiplier": mult,
            "raw_damage": args.weapon + (args.might // 3),
            "final_damage": dmg,
            "wound_severity": severity,
        }
        if args.json:
            print(json.dumps(output, indent=2))
        else:
            print(
                f"Hit: {loc} (×{mult}) → {dmg} damage → {severity} wound"
            )

    elif args.command == "magic":
        total_mods = sum(args.mods)
        if args.type == "galdr":
            result = resolve_galdr(args.wyrd, args.skill, total_mods)
        elif args.type == "seidr":
            result = resolve_seidr(args.wyrd, args.skill, total_mods)
        else:
            result = resolve_wyrd_reading(args.wyrd, args.skill, total_mods)

        if args.json:
            out = result.to_dict()
            if result.result in (ResultLevel.FAILURE, ResultLevel.CRITICAL_FAILURE):
                if args.type == "galdr":
                    out["failure_consequence"] = galdr_failure_consequence()
            print(json.dumps(out, indent=2))
        else:
            print(result.details)
            if result.result in (ResultLevel.FAILURE, ResultLevel.CRITICAL_FAILURE):
                if args.type == "galdr":
                    print(f"  Consequence: {galdr_failure_consequence()}")

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
