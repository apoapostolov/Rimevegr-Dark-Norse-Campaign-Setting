# Rimevegr Time Manager Development Plan

## Purpose

Build a production-grade local world-management suite for the Rimevegr that:

- loads canonical world state from `writing/norse_grit/data/`
- advances or rewinds the world by day, week, month, or season
- runs all relevant time-based simulations except the player-facing Voss band
- records every applied change as deterministic, reversible operations
- replays, reapplies, or undoes changes safely even after repeated forward and
  backward movement
- emits machine-readable change logs and narrative summaries for the writing
  team

The Voss mercenary band is explicitly outside the automatic world clock. The
tool must treat it as a manually-driven actor whose choices can be injected as
external events, contracts, and consequences.

The Black Axes are only partially time-managed at this stage. The tool should
advance passive bodily state that does not require travel decisions, such as:

- wound healing
- infection clearing or worsening when rules support it
- scar formation
- recovery clocks and similar time-driven bodily consequences

The tool should not infer or auto-advance Black Axes location. Their position
remains a manual operator input until a later scope expansion explicitly adds
travel-state management.

## Product Standard

This tool cannot be a loose editor. It will write to canonical YAML. That means
it must behave like a migration engine plus a world-state journal, not like a
toy simulator.

Required qualities:

- deterministic replay
- reversible mutations
- schema validation before and after writes
- snapshotting and rollback
- stable YAML formatting and ordering
- visible audit trail
- safe handling of random generation through seeded journals
- conflict detection if files changed outside the tool

## Core Capability Set

### Time navigation

- advance: `+1 day`, `+1 week`, `+1 month`, `+1 season`, custom range
- rewind: `-1 day`, `-1 week`, `-1 month`, `-1 season`, custom range
- jump to a named date or bookmark
- preview a move before applying it
- branch from a historical point without destroying the current line

### Simulation orchestration

The engine must run only adapters registered for the chosen step size and date.
Likely domains:

- settlement economy
- politics and unions
- wolfshead pressure
- demographics
- herd and kennel systems
- traders and routes
- mine production
- village construction and maintenance
- event calendars
- faction contracts
- Black Axes passive bodily recovery and scar-state progression

### Change management

- create one transaction per time step
- store exact before/after patches
- persist seeds used for random rolls
- allow undo by replaying inverse operations, not by guessing old values
- allow redo by replaying the same transaction with the same recorded random
  outcomes

### Narrative output

- structured delta summary per step
- grouped changes by settlement, faction, and region
- narrative digest generated from deterministic strings and templates
- export bundle for writing-team handoff

## Architecture Direction

Use a split architecture:

- React + TypeScript + Vite frontend for timeline navigation, previews, diff
  review, and operational UX
- Python application service for data mutation, simulation orchestration, YAML
  round-tripping, validation, and adapter execution

Reason:

- the simulation stack already lives in Python
- canonical YAML mutation needs comment-safe, order-safe round-tripping
- deterministic replay and patch generation are safer to build next to the
  existing Python simulation code than to reimplement in TypeScript

This should be treated as a local operator console, not a cloud app.

UI maturity note:

- current implementation is an early operator scaffold
- placeholder surfaces are acceptable during systems integration
- the final target is a world-class, deeply atmospheric control suite for a
  medieval mercenary world, with professional readability, high trust, and
  strong visual identity rather than generic admin tooling

## Source Of Truth Model

### Canonical sources

- `data/*.yaml` remains the source of truth for current world state
- time-manager state lives under its own local folder, not inside the data
  model itself, except for explicit runtime fields we already accept as canon

### Time-manager state

Store under `writing/norse_grit/tools/RIMEVEGR-TIME-MANAGER/state/`:

- `manifest.json` for tool metadata and current branch pointer
- `snapshots/` for compressed state snapshots
- `transactions/` for append-only transaction journals
- `locks/` for write and replay safety
- `exports/` for narrative and diff bundles

## Reversibility Model

The correct model is event-sourced transaction journaling with periodic
snapshots.

Each applied step should produce:

1. requested action
2. resolved date range
3. adapter execution order
4. seed material and random outputs used
5. file-level patch set
6. validation report
7. structured narrative delta

Undo should:

1. verify current files still match the expected post-state hashes
2. apply inverse patches in reverse order
3. restore the previous branch pointer and snapshot references

Redo should:

1. use the recorded transaction
2. reuse recorded random outcomes
3. reapply the exact same patches and validation checks

## Deterministic Randomness Rule

No simulation adapter may call uncontrolled randomness once integrated.

Allowed pattern:

- transaction seed derived from world date + branch id + transaction id
- adapter-specific sub-seeds derived from the transaction seed
- all random draws recorded in the transaction log

This prevents rewind/replay drift.

## Data Integrity Pipeline

Every apply or undo operation must run:

1. preload and schema validation
2. canonical parsing and normalization
3. simulation adapter execution
4. diff generation
5. post-write validation
6. integrity check against expected file hashes
7. snapshot update if the transaction commits

If any stage fails, nothing commits.

## Prompt 2 Deliverable: Authoritative Time Domains And Mutation Matrix

The first production implementation must classify every time-managed domain by
authority, write pattern, and rollback difficulty.

## Prompt 6 Deliverable: Shared Adapter Layer

The tool now needs a real adapter contract rather than a list of intended
domains.

The first integrated adapter tier should be:

- `settlement_stack` for economy, politics, demographics, wolfshead pressure,
  route pressure, contract market pressure, construction pressure, and mine
  production effects already surfaced through `village_politics.py`
- `animal_breeding` for seasonal horse-herd and dog-kennel progression through
  `horse_breeding.py` and `dog_breeding.py`

The next adapter tier should explicitly cover the Black Axes passive injury
state while keeping location manual.

Each adapter must expose:

- supported granularities
- canonical write targets
- preview execution against copied state or temporary files
- compact metrics and affected-entity summaries for the operator UI
- replay probes or draw journals that match the adapter's determinism level

Deterministic adapter rule:

- deterministic adapters should prefer lightweight draw journals or replay
  probes over full simulation reruns during redo validation when that provides
  the same integrity guarantee at much lower cost

### Low-risk deterministic domains

- calendars
- fixed trader schedules
- mine output if formulaic
- village maintenance tick if fully authored

### Medium-risk accumulative domains

- settlement economy
- political treasury and tribute state
- route pressure
- outlaw pressure
- construction progress

### High-risk stochastic or cross-coupled domains

- event generation
- births, deaths, and herd breeding if random
- contract pool mutation
- covert actions and dark-arts consequences
- anything that both mutates state and emits narrative

### Highest-risk write targets

- `data/political_state.yaml`
- `data/settlements.yaml`
- `data/economy/*.yaml`
- `data/contracts/*.yaml`
- any future generated cross-file indexes

These domains need stronger validation, stronger hashes, and transaction-level
diff visibility.

## Delivery Principle

The first usable release should prioritize safety over breadth:

1. read and validate all state
2. advance forward safely
3. capture reversible transactions
4. add rewind only after replay integrity is proven
5. add branching, exports, and richer narrative once the core loop is stable
