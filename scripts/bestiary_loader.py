"""bestiary_loader.py — Load any bestiary YAML entry as a Fighter.

Usage:
    python bestiary_loader.py ANI_WOLF_01
    python bestiary_loader.py UND_DRAUGR_05 --data ../data/bestiary
"""

import json
import pathlib
import sys

import yaml

# ── locate the scripts directory so we can import combat modules ─────────
_HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(_HERE))

from combat_model import Fighter  # noqa: E402

# ── canonical combat skill names (highest rank wins) ─────────────────────
_COMBAT_SKILLS = {"brawl", "swords", "axes", "spears", "bows", "knives", "shields"}

# ── default data directory (relative to the project root) ─────────────────
_DEFAULT_DATA = _HERE.parent / "data" / "bestiary"

# ── bestiary YAML file names ───────────────────────────────────────────────
_BESTIARY_FILES = [
    "animals.yaml",
    "undead.yaml",
    "humans.yaml",
    "supernatural.yaml",
    "named_enemies.yaml",
    "world_bosses.yaml",
]

# ── armor text → (torso_ar, head_ar) numeric mapping ──────────────────────
# Entries with None mean "this key doesn't affect that slot".
# Slots not listed for a given text string remain 0.
_ARMOR_TEXT_MAP: dict[str, dict[str, int]] = {
    # No protection
    "none":                              {"torso": 0, "head": 0},
    "burial shroud":                     {"torso": 0},
    "rags":                              {"torso": 0},
    "distended skin":                    {"torso": 0},
    "incorporating":                     {"torso": 0},
    "incorporeal":                       {"torso": 0},
    "partially incorporeal":             {"torso": 0},
    # Tier 1 — soft leather
    "leather jerkin":                    {"torso": 1},
    "oiled leather":                     {"torso": 2},
    "boiled leather":                    {"torso": 1},
    "studded leather":                   {"torso": 1},
    "hardened leather with bone plates": {"torso": 2},
    # Tier 2 — chain / ring
    "chain mail":                        {"torso": 3},
    "ring mail":                         {"torso": 3},
    "ill-fitting chain mail":            {"torso": 3},
    "looted mail shirt":                 {"torso": 3},
    "old chain mail":                    {"torso": 3},
    "rotted leather over mail fragments": {"torso": 2},
    "fused rusted mail":                 {"torso": 4},
    # Tier 3 — layered / ancient
    "layered mail":                      {"torso": 4},
    "ancient lamellar":                  {"torso": 4},
    # Natural armor
    "thick hide (ar 2)":                 {"torso": 2},
    "dense hide (ar 3)":                 {"torso": 3},
    "stone skin (natural, as plate)":    {"torso": 5, "head": 5},
    "reality-reject skin (acts as mail)": {"torso": 3},
    "bark-plate (natural)":              {"torso": 3},
    # Supernatural — no physical protection (handled by physical_weapons resistance)
    # Head armors
    "leather cap":                       {"head": 1},
    "corroded helmet":                   {"head": 2},
    "steel helm":                        {"head": 3},
    "iron helm":                         {"head": 3},
    "nasal helm":                        {"head": 3},
    "bronze crown-helm":                 {"head": 3},
    "thick skull (ar 2)":                {"head": 2},
    # Shield entries (not armor slots — handled separately)
    "cracked round shield":              {},   # shield_def handled separately
    "round shield":                      {},
}

# ── shield text → (shield_def, shield_skill_bonus) ────────────────────────
_SHIELD_MAP: dict[str, tuple[int, int]] = {
    "cracked round shield": (1, 1),
    "round shield":         (2, 1),
    "large shield":         (3, 1),
    "heater shield":        (2, 1),
    "buckler":              (1, 1),
}

# ── weapon type normalisation ──────────────────────────────────────────────
_WEAPON_TYPE_MAP: dict[str, str] = {
    "natural":        "unarmed",
    "unarmed":        "unarmed",
    "sword":          "sword",
    "one-handed_axe": "hand_axe",
    "two-handed_axe": "great_axe",
    "axe":            "hand_axe",
    "spear":          "spear",
    "knife":          "knife",
    "bow":            "bow",
    "supernatural":   "unarmed",  # Grave-Cold Touch, Spectral Fists, etc.
}


# ── public API ─────────────────────────────────────────────────────────────

def load_all_bestiaries(data_dir: pathlib.Path | str | None = None) -> dict[str, dict]:
    """Load all six bestiary YAML files and return a merged id→entry dict.

    Args:
        data_dir: path to the bestiary directory. Defaults to ``../data/bestiary``
                  relative to this script.

    Returns:
        Dict mapping creature ID strings to their raw YAML entry dicts.
    """
    data_dir = pathlib.Path(data_dir) if data_dir else _DEFAULT_DATA
    all_entries: dict[str, dict] = {}
    for fname in _BESTIARY_FILES:
        fpath = data_dir / fname
        if not fpath.exists():
            continue
        with open(fpath, encoding="utf-8") as fh:
            doc = yaml.safe_load(fh)
        for entry in doc.get("enemies", []):
            eid = entry.get("id")
            if eid:
                all_entries[eid] = entry
    return all_entries


def parse_armor_text(armor_dict: dict) -> dict[str, int]:
    """Convert YAML armor text entries to numeric AR values per location.

    Args:
        armor_dict: the ``gear.armor`` sub-dict from a bestiary entry,
                    e.g. ``{"torso": "Fused Rusted Mail", "head": "None"}``.

    Returns:
        Dict keyed by anatomical location with integer AR values.
        Locations: torso, head, right_arm, left_arm, legs, hands, feet.
    """
    result = {
        "torso": 0, "head": 0,
        "right_arm": 0, "left_arm": 0,
        "legs": 0, "hands": 0, "feet": 0,
    }
    if not armor_dict:
        return result

    for slot, text in armor_dict.items():
        if slot == "shield":
            continue  # shields handled separately
        if not isinstance(text, str):
            continue
        key = text.strip().lower()
        mapping = _ARMOR_TEXT_MAP.get(key)
        if mapping is None:
            # Fallback: try to detect AR value embedded in text, e.g. "(AR 3)"
            import re
            m = re.search(r'\(ar\s*(\d+)\)', key)
            if m:
                ar = int(m.group(1))
                if slot in result:
                    result[slot] = ar
            # Otherwise leave at 0 — unknown text is treated as no protection
        else:
            # Apply all slots from mapping to result
            for mapped_slot, ar_value in mapping.items():
                if mapped_slot in result:
                    result[mapped_slot] = ar_value
    return result


def _pick_shield(armor_dict: dict) -> tuple[int, int]:
    """Return (shield_def, shield_skill) from the armor.shield field if present."""
    if not armor_dict:
        return 0, 0
    shield_text = armor_dict.get("shield", "")
    if not shield_text:
        return 0, 0
    key = shield_text.strip().lower()
    return _SHIELD_MAP.get(key, (1, 1))  # unknown shield text → minimal values


def pick_weapon_skill(skills_list: list[dict]) -> int:
    """Find the highest rank among combat-relevant skills.

    Args:
        skills_list: list of ``{"name": str, "rank": int}`` dicts.

    Returns:
        Highest combat skill rank found, or 1 as fallback.
    """
    best = 1
    for sk in skills_list or []:
        name = sk.get("name", "").lower()
        rank = sk.get("rank", 0)
        if name in _COMBAT_SKILLS and rank > best:
            best = rank
    return best


def _pick_brawl_skill(skills_list: list[dict]) -> int:
    """Return the Brawl rank specifically (used for grapple proficiency)."""
    for sk in skills_list or []:
        if sk.get("name", "").lower() == "brawl":
            return sk.get("rank", 0)
    return 0


def _extract_bloodied_config(entry: dict) -> dict:
    """Extract bloodied/death-quarter phase settings from a bestiary entry."""
    sim_traits = set(entry.get("sim_traits", []) or [])
    phases = entry.get("combat_phases", {}) or {}
    bloodied_rows = phases.get("bloodied", []) or []

    bloodied_traits: list[str] = []
    death_quarter_traits: list[str] = []
    bloodied_mig_bonus = 0
    bloodied_nim_bonus = 0
    bloodied_at = 0.5

    def _add_trait(tr: str):
        if tr not in bloodied_traits:
            bloodied_traits.append(tr)

    # Start from explicit sim_traits (stable IDs)
    if "relentless_advance" in sim_traits:
        _add_trait("relentless_advance")
    if "last_stand" in sim_traits:
        _add_trait("last_stand")
    if "ancient_fury" in sim_traits:
        _add_trait("ancient_fury")
    if "desperate_fury" in sim_traits:
        _add_trait("desperate_fury")
    if "last_stand_25" in sim_traits:
        death_quarter_traits.append("last_stand_25")
    if "blackwine_rage" in sim_traits:
        _add_trait("blackwine_rage")
        bloodied_at = 0.99  # approximates "first wound"
    if "territorial_rage" in sim_traits or "berserk_rage" in sim_traits:
        _add_trait("berserk")
        bloodied_mig_bonus = max(bloodied_mig_bonus, 2)

    # Also parse human-readable combat phase names/descriptions
    joined = " ".join(
        f"{row.get('name', '')} {row.get('description', '')}" for row in bloodied_rows if isinstance(row, dict)
    ).lower()
    if "relentless advance" in joined:
        _add_trait("relentless_advance")
    if "last stand" in joined:
        _add_trait("last_stand")
    if "ancient fury" in joined:
        _add_trait("ancient_fury")
    if "desperate fury" in joined:
        _add_trait("desperate_fury")
    if "blackwine rage" in joined:
        _add_trait("blackwine_rage")
        bloodied_at = min(bloodied_at, 0.99)
    if "territorial rage" in joined or "berserk rage" in joined:
        _add_trait("berserk")
        bloodied_mig_bonus = max(bloodied_mig_bonus, 2)
    if "last stand" in joined and "25" in joined and "last_stand_25" not in death_quarter_traits:
        death_quarter_traits.append("last_stand_25")

    return {
        "bloodied_traits": bloodied_traits,
        "bloodied_mig_bonus": bloodied_mig_bonus,
        "bloodied_nim_bonus": bloodied_nim_bonus,
        "death_quarter_traits": death_quarter_traits,
        "bloodied_at": bloodied_at,
    }


def _extract_death_effects(entry: dict) -> list[str]:
    """Extract on-death effect keys from sim_traits and combat_phases.on_death."""
    effects: list[str] = []

    def _add(effect: str):
        if effect not in effects:
            effects.append(effect)

    # Direct sim_trait mappings
    sim_traits = set(entry.get("sim_traits", []) or [])
    trait_map = {
        "death_rattle": "death_rattle",
        "weapon_throw_on_death": "weapon_throw_on_death",
        "corpse_burst_4_2": "corpse_burst_4_2",
        "nauseating_burst": "nauseating_burst",
    }
    for tr, effect in trait_map.items():
        if tr in sim_traits:
            _add(effect)

    # Structured combat phase parsing
    phases = entry.get("combat_phases", {}) or {}
    rows = phases.get("on_death", []) or []
    text = " ".join(
        f"{row.get('name', '')} {row.get('description', '')}"
        for row in rows
        if isinstance(row, dict)
    ).lower()

    keyword_map = [
        ("death rattle", "death_rattle"),
        ("weapon throw", "weapon_throw_on_death"),
        ("corpse burst", "corpse_burst_4_2"),
        ("nauseating burst", "nauseating_burst"),
        ("death command", "death_command"),
        ("veil snap", "veil_snap_aoe"),
        ("flash freeze", "flash_freeze"),
        ("petrification cascade", "petrification_cascade"),
    ]
    for needle, effect in keyword_map:
        if needle in text:
            _add(effect)

    return effects


def pick_weapon_from_gear(gear: dict) -> tuple[str, int, int, str]:
    """Return (weapon_name, base_damage, speed, weapon_type) from the first weapon entry.

    Prefers the highest-damage non-shield weapon. Falls back to unarmed if empty.

    Args:
        gear: the ``gear`` sub-dict from a bestiary entry.

    Returns:
        A 4-tuple of (name, base_damage, speed, normalised_weapon_type).
    """
    weapons = (gear or {}).get("weapons", []) or []
    best: tuple[str, int, int, str] | None = None
    for w in weapons:
        wtype = w.get("type", "generic")
        if wtype == "shield":
            continue
        name = w.get("name", "Fists")
        dmg = w.get("base_damage", 3)
        spd = w.get("speed", 2)
        normalised = _WEAPON_TYPE_MAP.get(wtype, wtype)
        if best is None or dmg > best[1]:
            best = (name, dmg, spd, normalised)
    if best is None:
        return ("Fists", 3, 2, "unarmed")
    return best


def pick_secondary_weapons_from_gear(gear: dict) -> list[dict]:
    """Return all non-primary, non-shield weapons as secondary_weapons dicts.

    The primary weapon (highest damage, chosen by :func:`pick_weapon_from_gear`)
    is excluded; the rest are returned, sorted damage-descending, as
    ``{"type": str, "base": int, "speed": int}`` suitable for
    ``Fighter.secondary_weapons``.

    Args:
        gear: the ``gear`` sub-dict from a bestiary entry.

    Returns:
        List of secondary weapon dicts (may be empty).
    """
    weapons = (gear or {}).get("weapons", []) or []
    available: list[dict] = []
    for w in weapons:
        wtype = w.get("type", "generic")
        if wtype == "shield":
            continue
        normalised = _WEAPON_TYPE_MAP.get(wtype, wtype)
        available.append({
            "type": normalised,
            "base": w.get("base_damage", 3),
            "speed": w.get("speed", 2),
        })
    available.sort(key=lambda x: x["base"], reverse=True)
    return available[1:]  # index 0 is the primary; the rest are secondaries


def entry_to_fighter(entry: dict) -> Fighter:
    """Convert a raw bestiary entry dict to a Fighter instance.

    All creature stats, gear, resistances, and sim_traits are mapped.

    Args:
        entry: one element from the ``enemies`` list in a bestiary YAML.

    Returns:
        A fully initialised Fighter ready for use in combat_sim.
    """
    stats = entry.get("stats", {})
    gear = entry.get("gear", {})
    skills = entry.get("skills", [])

    name = entry.get("name", entry.get("id", "Unknown"))
    mig = stats.get("MIG", 4)
    nim = stats.get("NIM", 4)
    tou = stats.get("TOU", 4)
    wit = stats.get("WIT", 3)
    wil = stats.get("WIL", 3)

    # Explicit HP from YAML takes priority; the Fighter.__post_init__ will use
    # compute_max_hp only when both max_hp and hp are 0.
    hp_explicit = entry.get("hp", 0)

    weapon_skill = pick_weapon_skill(skills)
    brawl_skill = _pick_brawl_skill(skills)
    w_name, w_base, w_speed, w_type = pick_weapon_from_gear(gear)
    secondary_weapons = pick_secondary_weapons_from_gear(gear)

    armor_dict = gear.get("armor", {})
    armor = parse_armor_text(armor_dict)
    shield_def, shield_skill = _pick_shield(armor_dict)

    resistances = entry.get("resistances", [])
    # Normalise resistance tags: "physical weapons" (with space) → "physical_weapons"
    resistances = [r.replace(" ", "_") for r in resistances]

    weaknesses = entry.get("weaknesses", [])

    sim_traits = entry.get("sim_traits", [])
    is_undead = entry.get("is_undead", False)

    # Berserkers: pain spikes fuel aggression rather than suppressing action.
    if entry.get("subcategory", "") == "berserker":
        if "berserker_pain_fury" not in sim_traits:
            sim_traits.append("berserker_pain_fury")
        if "fear" not in resistances:
            resistances.append("fear")

    bloodied_cfg = _extract_bloodied_config(entry)
    death_effects = _extract_death_effects(entry)

    return Fighter(
        name=name,
        mig=mig,
        nim=nim,
        tou=tou,
        wit=wit,
        wil=wil,
        weapon_skill=weapon_skill,
        weapon_base=w_base,
        weapon_speed=w_speed,
        weapon_type=w_type,
        shield_skill=shield_skill,
        shield_def=shield_def,
        armor=armor,
        max_hp=hp_explicit,
        hp=hp_explicit,
        resistances=resistances,
        weaknesses=weaknesses,
        traits=sim_traits,
        is_undead=is_undead,
        brawl_skill=brawl_skill,
        secondary_weapons=secondary_weapons,
        bloodied_traits=bloodied_cfg["bloodied_traits"],
        bloodied_mig_bonus=bloodied_cfg["bloodied_mig_bonus"],
        bloodied_nim_bonus=bloodied_cfg["bloodied_nim_bonus"],
        death_quarter_traits=bloodied_cfg["death_quarter_traits"],
        bloodied_at=bloodied_cfg["bloodied_at"],
        death_effects=death_effects,
    )


def load_enemy(enemy_id: str, data_dir: pathlib.Path | str | None = None) -> Fighter:
    """Convenience loader: load a single creature by ID.

    Args:
        enemy_id: e.g. ``"ANI_WOLF_01"`` or ``"UND_DRAUGR_05"``.
        data_dir: path to bestiary directory (defaults to ``../data/bestiary``).

    Returns:
        A Fighter instance for the requested creature.

    Raises:
        KeyError: if ``enemy_id`` is not found in any bestiary file.
    """
    catalogue = load_all_bestiaries(data_dir)
    if enemy_id not in catalogue:
        raise KeyError(
            f"Enemy ID {enemy_id!r} not found. "
            f"Available: {sorted(catalogue.keys())}"
        )
    return entry_to_fighter(catalogue[enemy_id])


# ── CLI entry ──────────────────────────────────────────────────────────────

def _cli():
    import argparse

    parser = argparse.ArgumentParser(
        description="Load a bestiary creature as a Fighter and print JSON."
    )
    parser.add_argument("enemy_id", help="Creature ID, e.g. ANI_WOLF_01")
    parser.add_argument(
        "--data",
        default=None,
        help="Path to bestiary directory (default: ../data/bestiary)",
    )
    args = parser.parse_args()

    fighter = load_enemy(args.enemy_id, args.data)
    print(json.dumps(fighter.to_dict(), indent=2))


if __name__ == "__main__":
    _cli()
