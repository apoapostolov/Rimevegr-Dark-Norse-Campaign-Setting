# AGENTS.md — `writing/norse_grit/scripts` CLI Operations Guide

This guide is the command contract for every script in this directory.
Use it as the first stop before running simulation tooling.

## Scope

- Folder: `writing/norse_grit/scripts/`
- Goal: safe, reproducible CLI usage during development and testing
- Priority: avoid accidental writes to canonical state files (`data/*.yaml`)

## Catalog discipline

Keep this file as the command contract and refresh protocol.

- If the script catalog becomes stale, regenerate it from `--help` output.
- If the catalog becomes too large for quick scanning, move the long index to a
  sibling reference doc and leave only the safety rules here.
- Name the exact script and subcommand when describing a workflow.

## Mandatory safety rules

- Prefer `--dry-run` for **all mutating commands** during tests and exploration.
- For stateful scripts, use `--json` when possible for deterministic outputs.
- Never assume commands from memory; confirm with `--help` before execution.
- When testing write-path scripts, use temp copies or dry-run mode.

## Always-updated command policy

To keep this file current with latest command lists:

1. Treat script `--help` output as the source of truth.
2. On any CLI change in `scripts/*.py`:
   - update this file in the same change,
   - run markdown lint,
   - run targeted tests for touched scripts.
3. Before using a script, re-check:
   - `python3 <script>.py --help`
   - `python3 <script>.py <subcommand> --help`

### Refresh checklist (required after CLI edits)

- [ ] Re-scan all argparse scripts for subcommands
- [ ] Update the command catalog in this file
- [ ] Validate examples still run
- [ ] Run local `markdownlint-cli2 --fix AGENTS.md`

## Command usage pattern

```bash
python3 <script>.py --help
python3 <script>.py [--dry-run] <subcommand> --help
python3 <script>.py [--dry-run] <subcommand> [args...]
```

## CLI catalog (all argparse scripts in this folder)

Generated from source (`add_parser(...)`) and intended as a fast index.

- `agent_brief.py` — Agent brief generator
  - subcommands: `generate`
- `arc_tracker.py` — Arc tracker
  - subcommands: `status`, `threads`, `volume-map`, `chapter-types`,
    `character-arc`
- `band_manager.py` — Iron Ledger Band Manager
  - subcommands: `create`, `summary`, `add-member`, `remove-member`,
    `roster`, `snapshot`, `oath_break`, `oath_clear`, `named_man_status`,
    `named_man_pardon_check`
- `band_weekly_tick.py` — Iron Ledger — Band Weekly Tick Orchestrator
  - subcommands: `run`, `history`
- `barrow_generator.py` — Iron Ledger Barrow Generator
  - subcommands: `list`, `show`, `generate`, `stats`, `validate`
- `bestiary.py` — Iron Ledger Bestiary Manager
  - subcommands: `list`, `show`, `encounter`, `stats`, `validate`,
    `image-prompts`, `encounter-list`, `encounter-roll`, `encounter-show`,
    `encounter-stats`, `encounter-validate`
- `bestiary_loader.py` — Load a bestiary creature as a Fighter and print JSON.
  - subcommands: _(none; single-command CLI)_
- `calendar_sim.py` — Iron Ledger Calendar Engine
  - subcommands: `show`, `advance`, `season`, `time-cost`, `week-summary`
- `campaign_journal.py` — Campaign journal
  - subcommands: `record`, `timeline`, `npc-log`, `contract-log`, `chapter-log`
- `chapter_scaffolder.py` — Chapter scaffolder
  - subcommands: `scaffold`
- `combat_narrative.py` — Combat narrative translator
  - subcommands: `translate`
- `combat_sim.py` — Iron Ledger Combat Simulator (HEMA)
  - subcommands: `duel`, `skirmish`
  - notable flags:
    - `duel`: `--attacker|--attacker-file`, `--defender|--defender-file`,
      `--max-rounds`, `--json`, `--summary`, `--psych-profile`
    - `skirmish`: `--side-a`, `--side-b`, `--max-rounds`, `--json`,
      `--summary`, `--combat-mode auto|normal|skirmish`, `--psych-profile`
- `contract_manager.py` — Iron Ledger Contract Manager (Extended)
  - subcommands: `list`, `show`, `pool`, `chains`, `stats`, `validate`
- `contracts.py` — Iron Ledger Contract Manager
  - subcommands: `generate`, `detail`, `evaluate`, `feud`, `reputation`
- `encounter.py` — Iron Ledger Encounter Generator
  - subcommands: `roll`, `table`, `batch`
- `engine.py` — Iron Ledger Resolution Engine
  - subcommands: `check`, `opposed`, `damage`, `magic`
- `event_manager.py` — Iron Ledger — Event Manager
  - subcommands: `list`, `show`, `chain`, `timeline`, `decode`, `advance`,
    `stats`, `validate`
- `foraging.py` — Iron Ledger Foraging Engine
  - subcommands: `forage`, `deficit`, `table`
- `hidden_info.py` — Iron Ledger — Hidden Information Encoder/Decoder
  - subcommands: `encode`, `decode`, `decode-file`, `encode-file`, `test`
- `ledger.py` — Iron Ledger Financial Ledger
  - subcommands: `pay`, `mission-pay`, `loot`, `non-payment`, `status`,
    `trade-price`, `upkeep`, `war-event`, `tribute`, `occupation`, `in_kind`,
    `weekly_summary`
- `life_skills.py` — Iron Ledger — Life Skills Classifier (§17)
  - subcommands: `classify`, `check`, `domains`, `baseline`
- `logistics.py` — Iron Ledger Logistics Engine
  - subcommands: `supply`, `march`, `carry`, `band-weight`, `travel`
- `magic.py` — Iron Ledger — Norse Magic Simulator (§11)
  - subcommands: `galdr`, `seidr`, `wyrd-read`, `degrade`, `practitioners`,
    `annual_tick`, `practitioner_add`, `ward-right`, `testimony`, `curse`,
    `accuse`
- `morale.py` — Iron Ledger Morale Engine
  - subcommands: `check`, `resolve`, `loyalty`, `status`, `loyalty_tick`,
    `agenda_advance`, `trigger_check`, `named_man_defect`
- `npc_combat.py` — NPC combat bridge
  - subcommands: `duel`, `skirmish`, `roster`, `statblock`
- `npc_generator.py` — Iron Ledger NPC Generator
  - subcommands: `generate`, `named`, `batch`, `tavern`
- `npc_manager.py` — Iron Ledger — NPC Database Manager
  - subcommands: `list`, `show`, `stats`, `validate`, `relationships`, `web`,
    `image-prompts`
- `recruitment.py` — Iron Ledger Recruitment Engine
  - subcommands: `pool`, `recruit`, `cost`
- `scenario_runner.py` — Scenario runner
  - subcommands: `overland_travel`, `camp_night`, `settlement_visit`,
    `contract_assessment`
- `session_lifecycle.py` — Session lifecycle
  - subcommands: `start`, `end`, `undo`
- `settlement.py` — Iron Ledger Settlement Manager
  - subcommands: `create`, `prices`, `services`, `info`, `event`, `economy`,
    `animal-stock`, `market`
  - notable command shapes:
    - `info --name "<settlement>"`: canonical settlement readout with
      defenses, structures, construction capacity, maintenance burden, and
      damage state from `data/settlements.yaml`
    - `services --size <size>`: template service list plus supporting
      structure/defense fabric for generated settlement classes
    - `services --name "<settlement>"`: canonical service list for a named
      settlement with structure support and defense fabric
    - `create --name <name> --size <size> --terrain <terrain>`: generates a
      synthetic settlement that now includes infrastructure fields, not just
      services and notable buildings
    - `animal-stock --name "<settlement>"`: mount and dog replacement stock
      from recruitment and settlement data
- `spoiler_codec.py` — Iron Ledger — Spoiler Encoder/Decoder (CJK substitution)
  - subcommands: `encode`, `decode`, `decode-file`
- `tactical_report.py` — Tactical report
  - subcommands: `readiness`, `assess`
- `trauma.py` — Hugr Ledger — Psychological Trauma System
  - subcommands: `apply`, `trigger`, `recover`, `worsen`, `improve`,
    `resolve`, `add`, `status`, `roster`, `advance`
- `travel.py` — Iron Ledger Travel Simulator
  - subcommands: `simulate`, `hazard`, `route`, `named-route`, `list-routes`, `encounter`
- `validate_data.py` — Iron Ledger — YAML data validation
  - subcommands: _(none; single-command CLI)_
- `village_politics.py` — Iron Ledger — Village Political Simulation (§18)
  - subcommands: `status`, `union`, `feuds`, `tick`, `allthing`, `raid`,
    `economy`, `demographics`, `war-readiness`, `dark-arts`,
    `union-economy`, `wolfshead`, `contract-market`, `narrative`,
    `spoilers`, `atrocity`, `bounty`, `feud_stage`, `personal_crime`,
    `personal_bounty`, `personal_amnesty`, `personal_pressure`
  - notable command shapes:
    - `--dry-run` must appear before the subcommand:
      `python3 village_politics.py --dry-run tick --week`
    - `status`: now surfaces trade bottlenecks and top outlaw-pressure
      settlements from the active runtime state
    - `union --name "<union>"`: now shows union treasury, weekly tribute,
      levy burden, covert upkeep, smuggling income, support shortfall, and
      per-member weekly flow summaries
    - `union-economy [--name "<union>"]`: focused union treasury-flow view
      for tribute inflow, levy burden, seat upkeep, and member-level dues
    - `economy --settlement "<name>"`: now shows route pressure, shortage
      state, union burdens, covert pressure, outlaw pressure, night-market
      chance, tribute drag, and mercenary-competition pressure
    - `wolfshead [--band-id WOLF_003 | --settlement "Kolvik"]`: inspect
      outlaw-band runtime income, desperation, target settlements, or one
      settlement's outlaw-pressure state
    - `contract-market [--settlement "Kolvik"]`: inspect visible contract
      offers, issuer budget, payout capacity, locked value, pressure tags,
      and active contract reserve state
    - `tick --week|--season`: weekly flow now includes settlement economy,
      union treasury flows, covert upkeep, and wolfshead territorial pressure
- `weather.py` — Iron Ledger Weather Generator
  - subcommands: `generate`, `frostbite`, `modifiers`, `history`, `lookup`,
    `report`, `named-event`, `hazards`
- `world_state.py` — World state reporter
  - subcommands: `report`
- `wounds.py` — Iron Ledger — Wound Management System
  - subcommands: `apply`, `treat`, `heal`, `infect`, `worsen`, `improve`,
    `scar`, `remove`, `amputate`, `status`, `describe`, `roster`

## Non-CLI module scripts in this folder

These `.py` files currently do **not** expose argparse command subcommands
and are used as internal/imported modules:

- `combat_ai.py`
- `combat_grapple.py`
- `combat_model.py`
- `combat_types.py`
- `cross_ref_audit.py`

## Recommended testing mode by script type

- High mutation risk (always start with dry-run):
  - `band_manager.py`, `band_weekly_tick.py`, `village_politics.py`,
    `morale.py`, `wounds.py`, `trauma.py`, `session_lifecycle.py`
- Mostly read/report:
  - `world_state.py`, `tactical_report.py`, `arc_tracker.py`, `agent_brief.py`
- Data generation/lookup:
  - `weather.py`, `travel.py`, `foraging.py`, `logistics.py`, `recruitment.py`,
    `contracts.py`, `contract_manager.py`, `event_manager.py`, `npc_*`,
    `bestiary.py`, `barrow_generator.py`

## Maintenance note for future agents

When unsure, trust runtime help over this file:

- `python3 <script>.py --help`
- `python3 <script>.py <subcommand> --help`

If they disagree with this document, update this file immediately.

## Combat simulator command notes (recent updates)

`combat_sim.py skirmish` now supports explicit mode selection:

- `--combat-mode auto` (default): uses skirmish pipeline only when total
  combatants > 10.
- `--combat-mode normal`: forces legacy/normal targeting behavior.
- `--combat-mode skirmish`: forces perception-limited skirmish behavior.

Recommended validation sequence after `combat_sim.py` CLI changes:

1. `python3 combat_sim.py --help`
2. `python3 combat_sim.py skirmish --help`
3. run targeted combat tests in `tests/test_prompt4_skirmish_mode.py` and
   `tests/test_prompt5_formation_mode.py`

## Last reviewed

2026-06-01. Bump on any meaningful change to this file or its siblings.
