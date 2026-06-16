#!/usr/bin/env python3
"""
Iron Ledger — NPC Generator

Procedural NPC generation with attributes, skills, physical descriptions,
and personality traits. Supports backgrounds and Named Man generation
with triggers and agendas. Rules from 20_SIMULATION_RULES.md §15.

Usage:
    python npc_generator.py generate --background huscarl --rank veteran
    python npc_generator.py named --background wanderer
    python npc_generator.py batch --count 5 --mix
    python npc_generator.py tavern --count 3
"""

import argparse
import json
import random
import sys

sys.path.insert(0, __file__ and __import__('os').path.dirname(__file__) or '.')
from engine import roll_d100, roll_sum

# --- Backgrounds ---
BACKGROUNDS = {
    "farmer": {
        "primary_attr": "tou",
        "secondary_attr": "mig",
        "weak_attr": "wit",
        "skills": {"forage": (1, 2), "shelter": (0, 1)},
        "flavor": "calloused farmer",
    },
    "fisher": {
        "primary_attr": "nim",
        "secondary_attr": "tou",
        "weak_attr": "wil",
        "skills": {"seamanship": (1, 2), "forage": (0, 1)},
        "flavor": "salt-crusted fisherman",
    },
    "thrall": {
        "primary_attr": "tou",
        "secondary_attr": "mig",
        "weak_attr": "wil",
        "skills": {"brawl": (0, 1)},
        "flavor": "scarred former thrall",
    },
    "huscarl": {
        "primary_attr": "mig",
        "secondary_attr": "tou",
        "weak_attr": "wit",
        "skills": {"axes": (1, 3), "shields": (1, 2), "command": (0, 1)},
        "flavor": "tested house-guard",
    },
    "wanderer": {
        "primary_attr": "wit",
        "secondary_attr": "nim",
        "weak_attr": "mig",
        "skills": {"navigate": (1, 2), "track": (0, 1), "forage": (0, 1)},
        "flavor": "long-road wanderer",
    },
    "outlaw": {
        "primary_attr": "nim",
        "secondary_attr": "wit",
        "weak_attr": "wil",
        "skills": {"blades": (1, 2), "deceive": (0, 1)},
        "flavor": "marked outlaw",
    },
    "skald": {
        "primary_attr": "wit",
        "secondary_attr": "wil",
        "weak_attr": "mig",
        "skills": {"sagas": (1, 3), "persuade": (1, 2)},
        "flavor": "silver-tongued skald",
    },
    "hunter": {
        "primary_attr": "nim",
        "secondary_attr": "wit",
        "weak_attr": "wil",
        "skills": {"track": (2, 3), "bows": (1, 2), "forage": (1, 1)},
        "flavor": "patient hunter",
    },
    "smith": {
        "primary_attr": "mig",
        "secondary_attr": "tou",
        "weak_attr": "nim",
        "skills": {"smithing": (2, 3), "leatherwork": (0, 1)},
        "flavor": "soot-blackened smith",
    },
    "healer": {
        "primary_attr": "wit",
        "secondary_attr": "wil",
        "weak_attr": "mig",
        "skills": {"heal": (2, 3), "forage": (1, 2)},
        "flavor": "herb-wise healer",
    },
}

# --- Wyrd Distribution ---
WYRD_TABLE = [
    (90, 1),
    (97, 2),
    (99, 3),
    (100, 4),
]

# --- Physical Descriptions ---
BUILDS = ["gaunt", "lean", "wiry", "stocky", "broad-shouldered", "tall",
           "squat", "thick-limbed", "rangy", "heavy-set"]
HAIR = ["dark", "rust-red", "straw-blond", "grey-streaked", "black",
        "iron-grey", "fox-red", "ash-brown", "white-blond", "bald"]
FACES = ["scarred cheek", "broken nose", "deep-set eyes", "sharp jaw",
         "weather-beaten", "pockmarked", "long scar across brow",
         "a missing ear", "pale eyes", "thick brows", "thin lips",
         "burn scars along the neck", "tattoo across the temple"]
AGES = ["young (16-20)", "prime (21-30)", "seasoned (31-40)",
        "weathered (41-50)", "old (51+)"]

# --- Personality Traits ---
TRAITS = [
    "quiet and watchful", "quick to anger", "dry-humored",
    "pious and superstitious", "greedy but reliable", "loyal to a fault",
    "cowardly under pressure", "cruel when drunk", "oddly cheerful",
    "sullen and withdrawn", "boastful storyteller", "cunning and patient",
    "honest to a fault", "haunted by old deeds", "ambitious and scheming",
    "gentle except in battle", "perpetually cold", "obsessed with omens",
    "fiercely independent", "respects only strength",
]

# --- Named Man Triggers ---
TRIGGERS = [
    "Captain shows weakness in combat",
    "Band retreats from a winnable fight",
    "Personal insult goes unanswered",
    "A blood-kin is harmed by the band",
    "Captain breaks an oath or sworn word",
    "Loot is divided unfairly",
    "Band attacks unarmed folk without cause",
    "Captain consults a seiðr-worker (if male traditionalist)",
    "Band enters a barrow against omens",
    "A Named Man companion is executed or sacrificed",
    "Captain shows mercy to a sworn enemy",
    "The band stays too long in one place (restless)",
]

# --- Named Man Agendas ---
AGENDAS = [
    "Seek vengeance against a specific person or settlement",
    "Accumulate enough silver to buy farmland back home",
    "Find a lost sibling taken by slavers",
    "Earn enough fame to return home with honor",
    "Locate a specific barrow or rune-stone",
    "Kill a particular beast that scarred them",
    "Become captain of their own band",
    "Find a cure for a wasting sickness in their family",
    "Repay a weregild debt to a powerful jarl",
    "Prove themselves worthy of a specific person's hand",
    "Discover the truth about a parent's death",
    "Collect saga-worthy deeds to be remembered after death",
]

# --- Name Lists ---
MALE_NAMES = [
    "Bjorn", "Eirik", "Gunnar", "Halvar", "Ivar", "Kjartan", "Leif",
    "Magnus", "Njall", "Olaf", "Ragnar", "Sigurd", "Thorvald", "Ulf",
    "Vidar", "Yrjar", "Asmund", "Brynjar", "Dagfinn", "Einar",
    "Frode", "Grim", "Harald", "Ingvar", "Jostein", "Ketil",
    "Ljot", "Mord", "Nori", "Orm", "Petur", "Rolf",
    "Snorri", "Torsten", "Ubbe", "Varg", "Yngvar", "Hakon",
    "Thrain", "Skuli", "Egil", "Bard", "Stein", "Rorik",
]

FEMALE_NAMES = [
    "Astrid", "Brynhild", "Dagny", "Eira", "Freydis", "Gudrun",
    "Halla", "Inga", "Jorunn", "Katla", "Ljufa", "Magnhild",
    "Nessa", "Oddny", "Ragnhild", "Sigrid", "Thora", "Ulfhild",
    "Vigdis", "Ylva", "Asa", "Bergliot", "Dalla", "Hervor",
]

BYNAMES = [
    "the Scarred", "the Quiet", "One-Eye", "Blackhand", "the Red",
    "the Lame", "Ironside", "the Young", "the Old", "Crow-feeder",
    "the Bitter", "the Tall", "Half-troll", "the Lean", "Frostbeard",
    "Skullsplitter", "the Grey", "Oxback", "Shieldbreaker", "the Lucky",
    "the Grim", "Stonefist", "the Wanderer", "the Swift", "Boneless",
    "Wolftooth", "Rimewatcher", "Deepcaller", "Shorthair", "Longstride",
]


def _generate_wyrd() -> int:
    roll = roll_d100()
    for threshold, value in WYRD_TABLE:
        if roll <= threshold:
            return value
    return 1


def _random_name(gender: str = "male") -> str:
    names = MALE_NAMES if gender == "male" else FEMALE_NAMES
    name = random.choice(names)
    if random.random() < 0.3:
        name += f" {random.choice(BYNAMES)}"
    return name


def _generate_appearance() -> str:
    build = random.choice(BUILDS)
    hair = random.choice(HAIR)
    face = random.choice(FACES)
    age = random.choice(AGES)
    return f"{age}, {build}, {hair} hair, {face}"


def generate_npc(
    background: str | None = None,
    rank: str = "common",
    gender: str | None = None,
) -> dict:
    """Generate a fully detailed NPC."""
    if background is None:
        background = random.choice(list(BACKGROUNDS.keys()))
    if gender is None:
        gender = "female" if random.random() < 0.15 else "male"

    bg = BACKGROUNDS[background]

    # Base attributes
    attrs = {"mig": 5, "nim": 5, "tou": 5, "wit": 5, "wil": 5}

    # Boost primary +1d4
    attrs[bg["primary_attr"]] += random.randint(1, 4)

    # Boost secondary +1d2
    if "secondary_attr" in bg:
        attrs[bg["secondary_attr"]] += random.randint(0, 2)

    # Reduce weak -1d3
    attrs[bg["weak_attr"]] = max(1, attrs[bg["weak_attr"]] - random.randint(1, 3))

    # Thrall penalty
    if background == "thrall":
        for a in attrs:
            if a != bg["primary_attr"]:
                attrs[a] = max(1, attrs[a] - 1)

    # Veteran/Named Man boosts
    if rank in ("veteran", "named_man"):
        boost = random.choice(["mig", "nim", "tou"])
        attrs[boost] = min(10, attrs[boost] + random.randint(1, 2))

    if rank == "named_man":
        attrs["wil"] = min(10, attrs["wil"] + random.randint(1, 2))

    # Clamp
    for a in attrs:
        attrs[a] = max(1, min(10, attrs[a]))

    # Wyrd
    wyrd = _generate_wyrd()

    # Skills
    skills = {}
    for skill_name, (low, high) in bg["skills"].items():
        val = random.randint(low, high)
        if val > 0:
            skills[skill_name] = val

    if rank in ("veteran", "named_man"):
        combat = random.choice(["axes", "blades", "spears", "shields"])
        skills[combat] = max(skills.get(combat, 0), random.randint(2, 3))

    if rank == "named_man":
        social = random.choice(["command", "intimidate", "persuade"])
        skills[social] = max(skills.get(social, 0), random.randint(1, 2))

    name = _random_name(gender)
    appearance = _generate_appearance()
    trait = random.choice(TRAITS)

    npc = {
        "name": name,
        "gender": gender,
        "background": background,
        "rank": rank,
        "flavor": bg["flavor"],
        "appearance": appearance,
        "personality": trait,
        **attrs,
        "wyr": wyrd,
        "skills": skills,
    }

    # Named Man extras
    if rank == "named_man":
        npc["trigger"] = random.choice(TRIGGERS)
        npc["agenda"] = random.choice(AGENDAS)
        npc["loyalty"] = random.randint(2, 4)

    return npc


def generate_batch(count: int, mixed: bool = False) -> list[dict]:
    """Generate multiple NPCs."""
    npcs = []
    for _ in range(count):
        if mixed:
            bg = random.choice(list(BACKGROUNDS.keys()))
            roll = random.randint(1, 100)
            rank = "named_man" if roll <= 5 else "veteran" if roll <= 25 else "common"
        else:
            bg = None
            rank = "common"
        npcs.append(generate_npc(bg, rank))
    return npcs


def generate_tavern_npcs(count: int = 3) -> list[dict]:
    """Generate colorful tavern NPCs — not necessarily fighters."""
    tavern_bgs = ["farmer", "fisher", "skald", "wanderer", "hunter",
                  "smith", "outlaw", "healer"]
    npcs = []
    for _ in range(count):
        bg = random.choice(tavern_bgs)
        npc = generate_npc(bg, "common")
        # Add a tavern hook
        hooks = [
            "nursing a drink alone, watching the door",
            "telling a loud, probably false tale of adventure",
            "haggling with the innkeeper over a debt",
            "whittling a rune-bone, muttering to themselves",
            "arm-wrestling a much larger opponent",
            "asking strangers about work heading north",
            "brooding over a tattered map",
            "offering to buy drinks for anyone who'll listen",
            "asleep in the corner, clutching a worn satchel",
            "sharpening a knife with slow, deliberate strokes",
        ]
        npc["tavern_hook"] = random.choice(hooks)
        npcs.append(npc)
    return npcs


def main():
    parser = argparse.ArgumentParser(description="Iron Ledger NPC Generator")
    subparsers = parser.add_subparsers(dest="command")

    # --- generate ---
    gen_p = subparsers.add_parser("generate", help="Generate a single NPC")
    gen_p.add_argument("--background", type=str, default=None,
                       choices=list(BACKGROUNDS.keys()))
    gen_p.add_argument("--rank", type=str, default="common",
                       choices=["common", "veteran", "named_man"])
    gen_p.add_argument("--gender", type=str, default=None,
                       choices=["male", "female"])
    gen_p.add_argument("--json", action="store_true")

    # --- named ---
    nam_p = subparsers.add_parser("named", help="Generate a Named Man")
    nam_p.add_argument("--background", type=str, default=None,
                       choices=list(BACKGROUNDS.keys()))
    nam_p.add_argument("--gender", type=str, default=None,
                       choices=["male", "female"])
    nam_p.add_argument("--json", action="store_true")

    # --- batch ---
    bat_p = subparsers.add_parser("batch", help="Generate multiple NPCs")
    bat_p.add_argument("--count", type=int, default=5)
    bat_p.add_argument("--mix", action="store_true", help="Mixed ranks and backgrounds")
    bat_p.add_argument("--json", action="store_true")

    # --- tavern ---
    tav_p = subparsers.add_parser("tavern", help="Generate tavern NPCs")
    tav_p.add_argument("--count", type=int, default=3)
    tav_p.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.command == "generate":
        result = generate_npc(args.background, args.rank, args.gender)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            _print_npc(result)

    elif args.command == "named":
        result = generate_npc(args.background, "named_man", args.gender)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            _print_npc(result)

    elif args.command == "batch":
        results = generate_batch(args.count, args.mix)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            for npc in results:
                _print_npc(npc)
                print()

    elif args.command == "tavern":
        results = generate_tavern_npcs(args.count)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            for npc in results:
                _print_npc(npc)
                if "tavern_hook" in npc:
                    print(f"  Scene: {npc['tavern_hook']}")
                print()

    else:
        parser.print_help()


def _print_npc(npc: dict):
    """Pretty-print an NPC."""
    skills_str = ", ".join(f"{k}:{v}" for k, v in npc.get("skills", {}).items())
    print(f"{npc['name']} [{npc['rank']}] ({npc['background']}) — {npc['flavor']}")
    print(f"  MIG:{npc['mig']} NIM:{npc['nim']} TOU:{npc['tou']} "
          f"WIT:{npc['wit']} WIL:{npc['wil']} WYR:{npc['wyr']}")
    print(f"  Skills: {skills_str}")
    print(f"  Appearance: {npc['appearance']}")
    print(f"  Personality: {npc['personality']}")
    if npc.get("trigger"):
        print(f"  Trigger: {npc['trigger']}")
    if npc.get("agenda"):
        print(f"  Agenda: {npc['agenda']}")
    if npc.get("loyalty") is not None:
        print(f"  Loyalty: {npc['loyalty']}/5")


if __name__ == "__main__":
    main()
