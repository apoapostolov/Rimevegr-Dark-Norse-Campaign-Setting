# NPC Database Schema

Reference for all NPC YAML files under `data/npcs/`.

---

## File Structure

| File                     | ID Prefix | Count | Category                                                      |
| ------------------------ | --------- | ----- | ------------------------------------------------------------- |
| `settlement_npcs.yaml`   | NPC*SET*  | 50    | Settlement leaders, merchants, smiths, healers, gate-captains |
| `rival_band_npcs.yaml`   | NPC*BND*  | 33    | Mercenary band members (new roster additions)                 |
| `traveling_npcs.yaml`    | NPC*TRV*  | 30    | Wanderers: merchants, skalds, seidr, hermits, wardens         |
| `antagonist_npcs.yaml`   | NPC*ANT*  | 25    | Schemers, criminals, cultists, spies, manipulators            |
| `supernatural_npcs.yaml` | NPC*SUP*  | 19    | Named draugr, barrow spirits, Veil-touched, stone spirits     |

**Total: 157 named NPCs.**

---

## Common Fields (All Types)

| Field           | Type   | Required | Description                                                           |
| --------------- | ------ | -------- | --------------------------------------------------------------------- |
| `id`            | string | yes      | Unique ID: `NPC_{PREFIX}_{NNN}`                                       |
| `name`          | string | yes      | Full Norse name                                                       |
| `call_name`     | string | yes      | Nickname, title, or earned name                                       |
| `description`   | string | yes      | 2-3 sentence physical description                                     |
| `stats`         | object | yes      | MIG, NIM, TOU, WIT, WIL, WYR (1-10)                                   |
| `skills`        | list   | yes      | Each: `{name, rank}`                                                  |
| `personality`   | string | yes      | 2-3 sentences of behavior                                             |
| `agenda`        | string | yes      | Personal goal                                                         |
| `secret`        | string | yes      | Hidden truth (plot hook). `[CJK_PENDING]` prefix for spoiler encoding |
| `relationships` | list   | yes      | Each: `{target, type, note}`                                          |
| `image_prompt`  | string | yes      | Art generation prompt, dark Norse palette                             |

---

## Settlement NPCs (NPC*SET*)

Additional fields:

| Field               | Type   | Description                                                                                        |
| ------------------- | ------ | -------------------------------------------------------------------------------------------------- |
| `role`              | string | `jarl` / `notable` / `smith` / `healer` / `merchant` / `gate_captain` / `scout` / `priest` / `spy` |
| `settlement`        | string | Settlement name from 11_VILLAGES_AND_SETTLEMENTS.md                                                |
| `associated_chains` | list   | Event chain IDs from `data/events/`                                                                |

---

## Rival Band NPCs (NPC*BND*)

Additional fields:

| Field     | Type   | Description                                                             |
| --------- | ------ | ----------------------------------------------------------------------- |
| `role`    | string | `fighter` / `scout` / `healer` / `sergeant` / `champion` / `specialist` |
| `band`    | string | Band name                                                               |
| `gear`    | object | `{weapons: [{name, type, base_damage}], armor: {torso, head, ...}}`     |
| `trigger` | string | The condition that breaks loyalty                                       |
| `loyalty` | int    | 1 (about to leave) through 5 (die for the band)                         |

---

## Traveling NPCs (NPC*TRV*)

Additional fields:

| Field                  | Type   | Description                                                                                      |
| ---------------------- | ------ | ------------------------------------------------------------------------------------------------ |
| `role`                 | string | `merchant` / `skald` / `seidr_practitioner` / `hermit` / `road_warden` / `refugee` / `craftsman` |
| `travel_region`        | string | `coast` / `fjords` / `moors` / `forest` / `mountains` / `all`                                    |
| `services`             | string | What they can offer a mercenary band                                                             |
| `encounter_conditions` | object | `{terrain: [...], season: [...]}`                                                                |
| `associated_chains`    | list   | Event chain IDs                                                                                  |

---

## Antagonist NPCs (NPC*ANT*)

Additional fields:

| Field               | Type   | Description                                                                                   |
| ------------------- | ------ | --------------------------------------------------------------------------------------------- |
| `role`              | string | `sub_jarl` / `cult_leader` / `criminal` / `spy` / `renegade_seidr` / `slaver` / `manipulator` |
| `base`              | string | Settlement or region                                                                          |
| `threat_level`      | string | `low` / `medium` / `high`                                                                     |
| `scheme`            | string | Current active plot (specific and concrete)                                                   |
| `resources`         | string | People, silver, artifacts, territory controlled                                               |
| `vulnerability`     | string | How they can be defeated or exposed                                                           |
| `associated_chains` | list   | Event chain IDs                                                                               |

---

## Supernatural NPCs (NPC*SUP*)

Additional fields:

| Field                  | Type   | Description                                                                          |
| ---------------------- | ------ | ------------------------------------------------------------------------------------ |
| `true_name`            | string | Original name if different                                                           |
| `type`                 | string | `named_draugr` / `barrow_spirit` / `veil_touched` / `stone_spirit` / `ancestor_echo` |
| `bound_location`       | string | Barrow ID or location name                                                           |
| `hp`                   | int    | Hit points (spirits may be 0 = can't be killed by weapons)                           |
| `abilities`            | list   | Special supernatural abilities                                                       |
| `can_communicate`      | bool   | Whether interaction is possible                                                      |
| `communication_method` | string | `speech` / `gesture` / `vision` / `inscription` / `cold_writing`                     |
| `knowledge`            | string | Useful information this entity possesses                                             |
| `danger_level`         | string | `harmless` / `guarded` / `hostile` / `lethal`                                        |
| `interaction_hooks`    | list   | How a band might encounter and interact                                              |
| `associated_barrows`   | list   | BAR\_ IDs                                                                            |
| `associated_chains`    | list   | Event chain IDs                                                                      |

---

## Stats Reference

| Stat       | Abbrev | Governs                                           |
| ---------- | ------ | ------------------------------------------------- |
| Might      | MIG    | Melee damage, carrying, feats of strength         |
| Nimbleness | NIM    | Initiative, dodging, ranged accuracy              |
| Toughness  | TOU    | HP, endurance, resistance to pain                 |
| Wit        | WIT    | Perception, knowledge, crafting                   |
| Will       | WIL    | Morale, leadership, mental resistance             |
| Wyrd       | WYR    | Supernatural sensitivity, seidr, Veil interaction |

Scale: 1-10. Civilians 3-5. Fighters 5-8. Exceptional 8-10. WYR 1 is mundane; 3+ is seidr-sensitive.

---

## Skill List

Axes, Blades, Spears, Brawl, Shields, Bows, Command, Intimidate, Persuade,
Bargain, Deceive, Track, Navigate, Forage, Survival, Shelter, Heal, Rune-lore,
Wyrd-reading, Spirit-lore, Smithing, Sagas, Weather-sense, Stealth.

Rank scale: 1 (trained) through 5 (legendary master). Most NPCs 1-3.

---

## Relationship Types

| Type       | Meaning                              |
| ---------- | ------------------------------------ |
| `ally`     | Active cooperation                   |
| `rival`    | Competition or opposition            |
| `kin`      | Family bond                          |
| `lover`    | Romantic bond                        |
| `debt`     | Owes something (silver, favor, life) |
| `fear`     | Afraid of the target                 |
| `grudge`   | Personal vendetta                    |
| `puppet`   | Controls the target                  |
| `employer` | Pays the target                      |
| `target`   | Intends to act against               |
| `bound_to` | Supernaturally tied to a location    |
| `enemy`    | Active hostility                     |
| `ward`     | Protects something                   |
| `memory`   | Remembers from before death          |

---

## Cross-References

- Settlements: `11_VILLAGES_AND_SETTLEMENTS.md`
- Rival bands: `13_RIVAL_BANDS_AND_FACTIONS.md`
- Named men: `16_NAMED_MEN_AND_ARCHETYPES.md`, `22_MEMBER_STATBLOCKS.md`
- Bestiary: `data/bestiary/*.yaml`
- Barrows: `data/barrows/barrows.yaml`
- Events: `data/events/*.yaml`
- Contracts: `data/contracts/*.yaml`
- Relationship web: `data/npcs/relationship_web.yaml`
