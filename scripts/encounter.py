#!/usr/bin/env python3
"""
Iron Ledger — Random Encounter Generator

Generates random encounters based on terrain, season, time of day, and
band reputation. Encounters range from combat threats to story hooks.

Usage:
    python encounter.py roll --terrain forest --season long_dark --time night
    python encounter.py table --terrain mountain
    python encounter.py batch --terrain moors --count 5 --season long_dark
"""

import argparse
import json
import random
import sys

sys.path.insert(0, __file__ and __import__('os').path.dirname(__file__) or '.')
from engine import roll_d100

# --- Encounter Tables by Terrain ---
ENCOUNTER_TABLES = {
    "coast": [
        (15, "trader_caravan", "combat",
         "A small merchant caravan with 2-4 guards. May trade or be wary.",
         {"fighters": (2, 4), "rank": "common", "loot_silver": (5, 20)}),
        (25, "fishing_boat", "social",
         "Fishermen hauling nets near shore. May share news or ask for help.",
         {"info_chance": 60}),
        (35, "seal_colony", "environment",
         "A rocky beach thick with seals. Good foraging opportunity.",
         {"forage_bonus": 4}),
        (45, "shipwreck", "exploration",
         "Wreckage on the rocks. May contain salvage or trapped sailors.",
         {"loot_silver": (3, 15), "trap_chance": 20}),
        (55, "rival_band", "combat",
         "A rival mercenary band (8-12 fighters) on the same path.",
         {"fighters": (8, 12), "rank": "mixed", "loot_silver": (20, 60)}),
        (70, "pilgrim", "social",
         "A lone pilgrim heading to a holy site. Knowledgeable but frail.",
         {"info_chance": 80}),
        (80, "storm_debris", "environment",
         "Storm-tossed debris blocks the path. Half-day clearance.",
         {"day_penalty": 0.5}),
        (90, "abandoned_camp", "exploration",
         "A recently abandoned campsite. Signs of hasty departure.",
         {"loot_silver": (1, 5), "info_chance": 40}),
        (95, "sea_beast", "combat",
         "Something large moves in the shallows. Sea-troll or giant seal.",
         {"fighters": (1, 1), "rank": "elite", "loot_silver": (10, 30)}),
        (100, "the_hush", "supernatural",
         "The world goes silent. The Hush falls for 1d10 minutes.",
         {"wyrd_check": True, "morale_penalty": -1}),
    ],
    "forest": [
        (12, "wolf_pack", "combat",
         "A pack of 4-8 wolves, hungry and bold.",
         {"fighters": (4, 8), "rank": "beast", "loot_silver": (0, 3)}),
        (24, "outlaw_camp", "combat",
         "Outlaws hiding in the trees. 3-6 desperate men.",
         {"fighters": (3, 6), "rank": "common", "loot_silver": (5, 15)}),
        (36, "herb_clearing", "environment",
         "A clearing rich with medicinal herbs. Skilled foragers benefit.",
         {"forage_bonus": 6, "heal_herbs": True}),
        (48, "hunter", "social",
         "A solitary hunter. Wary but may share information about the trail.",
         {"info_chance": 70}),
        (58, "ancient_tree", "supernatural",
         "A massive, gnarled tree with runes carved into the bark.",
         {"wyrd_check": True, "rune_lore_check": True}),
        (68, "deadfall_trap", "hazard",
         "A concealed pit or deadfall. NIM check or 2d6 damage to point man.",
         {"damage_dice": (2, 6), "check_attr": "nim"}),
        (78, "charcoal_burners", "social",
         "A charcoal-burning camp. Simple folk who know the forest.",
         {"info_chance": 50, "trade_available": True}),
        (88, "boar", "combat",
         "A massive boar, territorial and aggressive.",
         {"fighters": (1, 1), "rank": "beast", "loot_silver": (0, 0),
          "food_units": (5, 10)}),
        (95, "barrow_mound", "exploration",
         "An old barrow mound, partially collapsed. Ancient dead inside?",
         {"loot_silver": (10, 50), "trap_chance": 30, "undead_chance": 40}),
        (100, "veil_thinning", "supernatural",
         "The air shimmers. Voices whisper in a tongue older than men.",
         {"wyrd_check": True, "morale_penalty": -1}),
    ],
    "moors": [
        (15, "fog_shapes", "supernatural",
         "Shapes move in the fog. Could be men, beasts, or neither.",
         {"wyrd_check": True, "combat_chance": 30}),
        (30, "lost_traveler", "social",
         "A disoriented traveler stumbling through the mist.",
         {"info_chance": 30, "recruit_chance": 20}),
        (42, "standing_stones", "supernatural",
         "A ring of ancient standing stones. The air hums faintly.",
         {"wyrd_check": True, "rune_lore_check": True}),
        (54, "bog_body", "environment",
         "A preserved corpse surfaces from the peat. Old offerings nearby.",
         {"loot_silver": (2, 8), "morale_penalty": 0}),
        (66, "raiders", "combat",
         "A raiding party (5-8 warriors) moving fast across the moors.",
         {"fighters": (5, 8), "rank": "common", "loot_silver": (10, 30)}),
        (76, "cairn_marker", "exploration",
         "A trail marker cairn. Someone left a message in rune-stones.",
         {"info_chance": 60, "navigate_bonus": True}),
        (86, "exposure", "hazard",
         "Relentless wind and rain. TOU check or suffer exhaustion.",
         {"check_attr": "tou", "penalty_on_fail": "exhausted"}),
        (93, "shepherd", "social",
         "A moorland shepherd with a flock. Simple but observant.",
         {"info_chance": 50, "food_units": (2, 4)}),
        (97, "banshee_wind", "supernatural",
         "The wind screams like a dying woman. Morale check.",
         {"morale_penalty": -1, "wyrd_check": True}),
        (100, "the_hush", "supernatural",
         "Total silence descends. Something watches from the fog.",
         {"wyrd_check": True, "morale_penalty": -1}),
    ],
    "mountain": [
        (12, "rockslide", "hazard",
         "Loose rocks cascade. NIM check or 2d6 damage, half-day delay.",
         {"damage_dice": (2, 6), "check_attr": "nim", "day_penalty": 0.5}),
        (24, "mountain_goats", "environment",
         "Wild goats on the cliffs. Potential food source.",
         {"food_units": (3, 8), "bows_check": True}),
        (36, "eagle_nest", "environment",
         "A massive eagle circles above. Good vantage point for scouting.",
         {"navigate_bonus": True, "wit_check": True}),
        (48, "abandoned_mine", "exploration",
         "A boarded-up mine entrance. Could contain ore or danger.",
         {"loot_silver": (5, 30), "trap_chance": 25}),
        (58, "mountain_hermit", "social",
         "A reclusive hermit living in a cave. Possibly a rune-carver.",
         {"info_chance": 70, "wyrd_check": True}),
        (68, "ice_bridge", "hazard",
         "A natural ice bridge over a chasm. May hold — or may not.",
         {"check_attr": "nim", "damage_dice": (4, 6)}),
        (78, "giant_tracks", "exploration",
         "Enormous footprints in the snow. Fresh. Something large passed here.",
         {"info_chance": 30, "combat_chance": 15}),
        (88, "cave_camp", "environment",
         "A dry cave suitable for shelter. Cold but defensible.",
         {"shelter": True, "rest_bonus": True}),
        (95, "troll", "combat",
         "A mountain troll emerges from behind rocks. Massive and hungry.",
         {"fighters": (1, 1), "rank": "elite", "loot_silver": (15, 40)}),
        (100, "rune_wall", "supernatural",
         "A cliff face covered in ancient runes. Power radiates from the stone.",
         {"wyrd_check": True, "rune_lore_check": True, "galdr_possible": True}),
    ],
    "river": [
        (15, "thin_ice", "hazard",
         "Ice groans underfoot. NIM check or fall through.",
         {"damage_dice": (1, 6), "check_attr": "nim", "frostbite_risk": True}),
        (30, "ice_fishing", "environment",
         "Good spot for ice fishing. Foraging opportunity.",
         {"forage_bonus": 5}),
        (42, "frozen_corpse", "exploration",
         "A body frozen in the ice. Preserved gear and silver.",
         {"loot_silver": (3, 12)}),
        (54, "trading_post", "social",
         "A small riverbank trading post. Basic goods available.",
         {"trade_available": True, "info_chance": 60}),
        (66, "bandits_on_ice", "combat",
         "Bandits using the frozen river as an ambush corridor.",
         {"fighters": (4, 7), "rank": "common", "loot_silver": (8, 20)}),
        (78, "otter_colony", "environment",
         "A colony of otters near a break in the ice. Peaceful scene.",
         {"morale_bonus": 0}),
        (88, "ice_crack", "hazard",
         "The ice splits with a deafening crack. Reroute needed.",
         {"day_penalty": 0.5}),
        (95, "drowned_dead", "supernatural",
         "Something moves under the ice. Pale faces stare upward.",
         {"wyrd_check": True, "morale_penalty": -1, "combat_chance": 20}),
        (100, "river_spirit", "supernatural",
         "The ice glows faintly. A voice bubbles up from below.",
         {"wyrd_check": True, "seidr_check": True}),
    ],
    "ice": [
        (15, "crevasse", "hazard",
         "Hidden crevasse under snow. WIT+Navigate check.",
         {"damage_dice": (3, 6), "check_attr": "wit"}),
        (28, "blizzard_pocket", "environment",
         "Localized whiteout. No progress for 1d4 hours.",
         {"day_penalty": 0.25}),
        (40, "frozen_beast", "exploration",
         "A frozen beast partially exposed. Ancient, enormous.",
         {"info_chance": 20, "wyrd_check": True}),
        (52, "ice_cave", "exploration",
         "An ice cave reflecting unnatural light. Shelter or trap?",
         {"shelter": True, "trap_chance": 20, "loot_silver": (5, 25)}),
        (64, "polar_bears", "combat",
         "A polar bear defending territory. Enormous and fearless.",
         {"fighters": (1, 2), "rank": "elite", "food_units": (10, 20)}),
        (76, "aurora", "supernatural",
         "The sky erupts in shifting light. A sign from the gods.",
         {"wyrd_check": True, "morale_bonus": 1}),
        (86, "frostbite_exposure", "hazard",
         "Extreme cold bites through armor. Frostbite check for all.",
         {"frostbite_risk": True}),
        (93, "snow_shrine", "supernatural",
         "A shrine of stacked ice, surrounded by offerings. Ancient magic.",
         {"wyrd_check": True, "rune_lore_check": True}),
        (97, "ice_worm", "combat",
         "Something vast moves beneath the ice. The ground shakes.",
         {"fighters": (1, 1), "rank": "legendary", "morale_penalty": -1}),
        (100, "the_hush", "supernatural",
         "Perfect silence. The wind dies. Something vast turns its attention here.",
         {"wyrd_check": True, "morale_penalty": -2}),
    ],
    "barrow": [
        (12, "grave_guardians", "combat",
         "Draugr sentinels animate as you enter. 2-4 undead warriors.",
         {"fighters": (2, 4), "rank": "elite", "loot_silver": (10, 40)}),
        (24, "rune_ward", "supernatural",
         "A galdr ward bars passage. Carved runes flare white-hot.",
         {"galdr_possible": True, "rune_lore_check": True, "damage_dice": (2, 6)}),
        (36, "collapsed_passage", "hazard",
         "The tunnel groans and drops stone. NIM check or 2d6 damage.",
         {"damage_dice": (2, 6), "check_attr": "nim", "day_penalty": 0.5}),
        (48, "burial_offerings", "exploration",
         "An undisturbed burial chamber. Silver arm-rings and a corroded blade.",
         {"loot_silver": (15, 60), "trap_chance": 35}),
        (58, "whispering_dead", "supernatural",
         "The walls speak in Old Tongue. WYR characters hear a name repeated.",
         {"wyrd_check": True, "seidr_check": True, "info_chance": 70}),
        (68, "bone_pit", "hazard",
         "The floor gives way into a pit of ancient remains. TOU check.",
         {"damage_dice": (1, 6), "check_attr": "tou", "morale_penalty": -1}),
        (78, "rune_inscription", "exploration",
         "Faded runes on a lintel. Rune-lore reveals a map or warning.",
         {"rune_lore_check": True, "info_chance": 80, "navigate_bonus": True}),
        (88, "cursed_treasure", "supernatural",
         "Gold gleams in the dark. Taking it triggers a galdr curse.",
         {"loot_silver": (30, 80), "galdr_possible": True, "wyrd_check": True}),
        (95, "draugr_lord", "combat",
         "A draugr chieftain stirs. Massive, armored, impossibly strong.",
         {"fighters": (1, 1), "rank": "legendary", "loot_silver": (40, 100),
          "morale_penalty": -1}),
        (100, "the_binding", "supernatural",
         "The barrow seals. A voice demands a blood-price for passage.",
         {"wyrd_check": True, "seidr_check": True, "galdr_possible": True,
          "morale_penalty": -2}),
    ],
    "fjord": [
        (12, "longship_wreck", "exploration",
         "A half-sunk longship wedged against rocks. Salvageable cargo.",
         {"loot_silver": (8, 35), "trap_chance": 15}),
        (24, "sea_raiders", "combat",
         "A raiding party rowing up the fjord. 6-10 armed men.",
         {"fighters": (6, 10), "rank": "common", "loot_silver": (15, 40)}),
        (36, "cliff_shrine", "supernatural",
         "A salt-crusted shrine cut into the cliff face. Offerings to Rán.",
         {"wyrd_check": True, "morale_bonus": 1}),
        (48, "fisherman_village", "social",
         "A tiny fishing camp clinging to the fjord wall. News and trade.",
         {"trade_available": True, "info_chance": 60, "food_units": (3, 8)}),
        (58, "water_horse", "supernatural",
         "A nykur surfaces — beautiful, impossible. Seiðr practitioners sense danger.",
         {"seidr_check": True, "wyrd_check": True, "combat_chance": 40}),
        (68, "rockfall", "hazard",
         "Cliff face crumbles onto the path. NIM check or 2d6 damage.",
         {"damage_dice": (2, 6), "check_attr": "nim", "day_penalty": 0.5}),
        (78, "smuggler_cave", "exploration",
         "A hidden cave with signs of recent use. Contraband or supplies.",
         {"loot_silver": (5, 25), "info_chance": 40}),
        (88, "tidal_bore", "hazard",
         "The fjord surges without warning. TOU check or swept off feet.",
         {"damage_dice": (1, 6), "check_attr": "tou", "frostbite_risk": True}),
        (95, "sea_troll", "combat",
         "A troll emerges from the deep, barnacled and enormous.",
         {"fighters": (1, 1), "rank": "elite", "loot_silver": (20, 50)}),
        (100, "drowned_chorus", "supernatural",
         "Voices rise from the water. The drowned sing old galdr.",
         {"wyrd_check": True, "seidr_check": True, "galdr_possible": True,
          "morale_penalty": -1}),
    ],
    "ruins": [
        (12, "scavengers", "combat",
         "Desperate outlaws sheltering in the ruins. 3-6 fighters.",
         {"fighters": (3, 6), "rank": "common", "loot_silver": (5, 15)}),
        (24, "rune_pillar", "supernatural",
         "A standing pillar inscribed with layered galdr. Still active.",
         {"galdr_possible": True, "rune_lore_check": True, "wyrd_check": True}),
        (36, "hidden_cellar", "exploration",
         "A trapdoor leads to a root cellar. Preserved supplies inside.",
         {"loot_silver": (2, 10), "food_units": (4, 10)}),
        (48, "seidr_circle", "supernatural",
         "Scorched earth in a perfect ring. Seiðr residue lingers here.",
         {"seidr_check": True, "wyrd_check": True, "info_chance": 50}),
        (58, "wall_collapse", "hazard",
         "A wall buckles. NIM check or 2d6 damage.",
         {"damage_dice": (2, 6), "check_attr": "nim"}),
        (68, "old_forge", "exploration",
         "A ruined smithy. Some tools intact, maybe a masterwork blade.",
         {"loot_silver": (5, 30), "trade_available": True}),
        (78, "ghost_light", "supernatural",
         "Cold flames drift through the ruins at dusk. They lead somewhere.",
         {"wyrd_check": True, "navigate_bonus": True, "info_chance": 60}),
        (88, "feral_dogs", "combat",
         "A pack of wild dogs, territorial over the ruin. 4-8 animals.",
         {"fighters": (4, 8), "rank": "beast", "loot_silver": (0, 0)}),
        (95, "wyrd_well", "supernatural",
         "A well that shows reflections of things that haven't happened yet.",
         {"wyrd_check": True, "seidr_check": True, "info_chance": 90}),
        (100, "bound_spirit", "supernatural",
         "A spirit trapped by ancient galdr screams for release.",
         {"galdr_possible": True, "seidr_check": True, "wyrd_check": True,
          "morale_penalty": -1}),
    ],
    "tundra": [
        (12, "snow_wolves", "combat",
         "White-furred wolves, nearly invisible. 4-6 pack hunters.",
         {"fighters": (4, 6), "rank": "beast", "loot_silver": (0, 2)}),
        (24, "frozen_stream", "environment",
         "A frozen stream with good foraging underneath the ice.",
         {"forage_bonus": 4, "frostbite_risk": True}),
        (36, "nomad_camp", "social",
         "Sami-style nomads with reindeer. Cautious but willing to trade.",
         {"trade_available": True, "info_chance": 50, "food_units": (3, 8)}),
        (48, "seidr_hermit", "supernatural",
         "A völva lives alone on the tundra. She sees the thread of fate.",
         {"seidr_check": True, "wyrd_check": True, "info_chance": 80}),
        (58, "frost_heave", "hazard",
         "The ground buckles from frost. NIM check or twisted ankle.",
         {"check_attr": "nim", "day_penalty": 0.5}),
        (68, "mammoth_bones", "exploration",
         "Enormous bones jut from the permafrost. Rune marks on the skull.",
         {"rune_lore_check": True, "wyrd_check": True, "info_chance": 40}),
        (78, "whiteout", "hazard",
         "Total whiteout. WIT+Navigate check or lose a full day.",
         {"check_attr": "wit", "day_penalty": 1.0}),
        (88, "rune_cairn", "supernatural",
         "A cairn with rune-stones stacked in a galdr sequence. Power remains.",
         {"galdr_possible": True, "rune_lore_check": True, "wyrd_check": True}),
        (95, "frost_giant_sign", "exploration",
         "Tracks the size of boats. Something enormous passed recently.",
         {"morale_penalty": -1, "info_chance": 20, "combat_chance": 10}),
        (100, "aurora_gate", "supernatural",
         "The aurora descends to the ground. A doorway of light opens briefly.",
         {"wyrd_check": True, "seidr_check": True, "galdr_possible": True,
          "morale_bonus": 1}),
    ],
}

# Default table for unmapped terrains
DEFAULT_TABLE = ENCOUNTER_TABLES["forest"]

# --- Time of Day Modifiers ---
TIME_MODIFIERS = {
    "dawn": {"encounter_chance_mod": 0.8, "combat_mod": -10, "supernatural_mod": 0.5},
    "day": {"encounter_chance_mod": 1.0, "combat_mod": 0, "supernatural_mod": 0.3},
    "dusk": {"encounter_chance_mod": 1.2, "combat_mod": 0, "supernatural_mod": 1.0},
    "night": {"encounter_chance_mod": 1.5, "combat_mod": -20, "supernatural_mod": 1.5},
}

# --- Season Modifiers ---
SEASON_MODIFIERS = {
    "long_summer": {"encounter_chance": 0.4, "beast_mod": 1.0, "supernatural_mod": 0.5},
    "long_dark": {"encounter_chance": 0.5, "beast_mod": 1.3, "supernatural_mod": 1.5},
}


def roll_encounter(
    terrain: str,
    season: str = "long_summer",
    time_of_day: str = "day",
    reputation: int = 1,
) -> dict | None:
    """Roll for a random encounter. Returns None if no encounter."""
    season_key = "long_dark" if "dark" in season else "long_summer"
    season_info = SEASON_MODIFIERS.get(season_key, SEASON_MODIFIERS["long_summer"])
    time_info = TIME_MODIFIERS.get(time_of_day, TIME_MODIFIERS["day"])

    # Check if an encounter happens at all
    base_chance = season_info["encounter_chance"]
    modified_chance = base_chance * time_info["encounter_chance_mod"]

    # High reputation = less random bandit attacks, more social encounters
    if reputation >= 3:
        modified_chance *= 0.8

    if random.random() > modified_chance:
        return None

    # Roll on terrain table
    table = ENCOUNTER_TABLES.get(terrain, DEFAULT_TABLE)
    roll = roll_d100()

    for threshold, enc_type, category, description, details in table:
        if roll <= threshold:
            # Adjust supernatural encounters by season
            if category == "supernatural":
                suppress_roll = random.random()
                if suppress_roll > season_info["supernatural_mod"] * time_info["supernatural_mod"]:
                    return None  # Supernatural encounter suppressed

            return {
                "type": enc_type,
                "category": category,
                "description": description,
                "details": details,
                "terrain": terrain,
                "season": season_key,
                "time_of_day": time_of_day,
                "roll": roll,
            }

    return None


def get_encounter_table(terrain: str) -> list[dict]:
    """Get the full encounter table for a terrain."""
    table = ENCOUNTER_TABLES.get(terrain, DEFAULT_TABLE)
    return [
        {
            "threshold": t,
            "type": enc_type,
            "category": cat,
            "description": desc,
            "details": details,
        }
        for t, enc_type, cat, desc, details in table
    ]


def batch_encounters(
    terrain: str,
    count: int,
    season: str = "long_summer",
    time_of_day: str = "day",
) -> list[dict]:
    """Generate multiple encounter checks (simulating multiple days)."""
    encounters = []
    for day in range(1, count + 1):
        enc = roll_encounter(terrain, season, time_of_day)
        if enc:
            enc["day"] = day
            encounters.append(enc)
    return encounters


def main():
    parser = argparse.ArgumentParser(description="Iron Ledger Encounter Generator")
    subparsers = parser.add_subparsers(dest="command")

    # --- roll ---
    roll_p = subparsers.add_parser("roll", help="Roll for a single encounter")
    roll_p.add_argument("--terrain", type=str, default="forest",
                        choices=list(ENCOUNTER_TABLES.keys()))
    roll_p.add_argument("--season", type=str, default="long_summer")
    roll_p.add_argument("--time", type=str, default="day",
                        choices=list(TIME_MODIFIERS.keys()))
    roll_p.add_argument("--reputation", type=int, default=1)
    roll_p.add_argument("--json", action="store_true")

    # --- table ---
    tab_p = subparsers.add_parser("table", help="Show encounter table")
    tab_p.add_argument("--terrain", type=str, required=True,
                       choices=list(ENCOUNTER_TABLES.keys()))
    tab_p.add_argument("--json", action="store_true")

    # --- batch ---
    bat_p = subparsers.add_parser("batch", help="Roll encounters for multiple days")
    bat_p.add_argument("--terrain", type=str, default="forest",
                       choices=list(ENCOUNTER_TABLES.keys()))
    bat_p.add_argument("--count", type=int, default=7, help="Number of days")
    bat_p.add_argument("--season", type=str, default="long_summer")
    bat_p.add_argument("--time", type=str, default="day",
                       choices=list(TIME_MODIFIERS.keys()))
    bat_p.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.command == "roll":
        result = roll_encounter(args.terrain, args.season, args.time, args.reputation)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if result is None:
                print("No encounter.")
            else:
                print(f"[{result['category'].upper()}] {result['type']}")
                print(f"  {result['description']}")
                details = result.get("details", {})
                if details:
                    for k, v in details.items():
                        print(f"  {k}: {v}")

    elif args.command == "table":
        table = get_encounter_table(args.terrain)
        if args.json:
            print(json.dumps(table, indent=2))
        else:
            print(f"Encounter Table — {args.terrain}:")
            for e in table:
                print(f"  [{e['threshold']:3d}] [{e['category']:12s}] "
                      f"{e['type']}: {e['description']}")

    elif args.command == "batch":
        results = batch_encounters(args.terrain, args.count, args.season, args.time)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f"Encounters over {args.count} days in {args.terrain}:")
            if not results:
                print("  No encounters.")
            for enc in results:
                print(f"  Day {enc.get('day', '?')}: [{enc['category']}] {enc['type']}")
                print(f"    {enc['description']}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
