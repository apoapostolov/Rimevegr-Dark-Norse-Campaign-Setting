# TODO - Rimevegr Time Manager

## Current Focus

Design and build a production-ready world time manager for the Rimevegr.

Target outcome:

- move the world forward and backward through time safely
- run all time-based simulations except the manually-driven Voss band
- manage selected Black Axes state such as wound recovery, healing, scarring,
  and other passive bodily processes without auto-moving the band on the map
- write canonical YAML changes through reversible transactions
- generate operator diffs and writer-facing narrative summaries
- keep replay, undo, redo, and branching deterministic

## Scope And Boundaries

This tool currently owns:

- world time progression for authored systems outside direct player movement
- settlement, union, route, outlaw, contract, herd, kennel, and other passive
  world-state processes
- selected passive Black Axes state that can advance without choosing travel,
  such as healing, recovery, scar formation, and similar time-driven bodily
  consequences

This tool currently does not own:

- automatic Black Axes location changes
- player-facing tactical choices for the Voss band
- inferred travel paths for the band unless later scope explicitly adds them

**Resume rule:** when returning to this file, start with the first unchecked
prompt in the active queue below.

**Cleanup rule:** when asked to clean this file, remove completed prompt dumps
instead of preserving them. Keep only the current focus, working rules, and
active prompt queue unless the user explicitly asks for archives.

**Removal rule:** if the user says to remove prompts, tasks, or completed
items from this file, delete them outright. Do not archive them elsewhere
unless the user explicitly asks for an archive.

**Protected template rule:** keep the example prompt template and rule scaffold
in this file unless the user explicitly says to remove the template itself.

**Continuation rule:** if the current prompt or session leaves a clear next
prompt that can be handled without major context drift, continue automatically.
If the next prompt is a materially different undertaking, requires rebuilding a
large context window, or introduces a major codebase/topic shift, it is allowed
to ask the user whether to continue before proceeding.

**Prompt autonomy rule:** AI is allowed to expand a prompt with additional
subtasks, create follow-up prompts or sub-prompts, split or combine prompts, and
modify prompt boundaries when discoveries suggest a better implementation path.
If a better approach changes scope or sequencing in a meaningful way, present
the proposal to the user and ask how to handle development before committing to
the new direction.

---

## Active Prompt Queue — Time Manager Epic

### [x] Prompt 1 — product architecture, reversibility model, and safety standard

Define the tool as a real world-state transaction engine rather than a loose
clock UI.

Outputs:

- `DELEVELOPMENT_PLAN.md`
- `STACK.md`
- `UX.md`

### [x] Prompt 2 — authoritative time domains and mutation-risk map

Map which world domains should be time-managed first, which files they own, and
which are high-risk for rollback drift.

Output:

- a first-pass authority and risk matrix embedded in `DELEVELOPMENT_PLAN.md`

### [x] Prompt 3 — scaffold the application shell

Create the initial tool structure and baseline app architecture:

- frontend app shell
- backend service shell
- local state folder conventions
- adapter registry skeleton
- transaction journal skeleton

### [x] Prompt 4 — canonical data loader and validation gateway

Implement the safe loader for all relevant `data/` YAML files:

- round-trip preserving load/write path
- schema and reference validation
- file hash manifest
- dry-run preview output

### [x] Prompt 5 — timeline cursor, snapshots, and reversible transactions

Implement:

- time cursor
- forward step transaction model
- inverse patch generation
- snapshots
- undo and redo

### [x] Prompt 6 — simulation adapter integration layer

Wrap existing time-based systems behind a shared adapter contract:

- economy
- demographics
- politics
- wolfshead
- traders and routes
- construction
- mines
- herd and kennel systems

Completed output:

- shared backend adapter contract and registry in `server/app/adapter_registry.py`
- settlement simulation preview adapter over `village_politics.py`
- seasonal herd and kennel preview adapter over `horse_breeding.py` and
  `dog_breeding.py`
- API preview surface at `/api/adapters/preview`

### [ ] Prompt 7 — deterministic randomness and replay hardening

Add:

- seed strategy
- recorded random draws
- deterministic replay
- branch-safe redo behavior

### [x] Prompt 7A — deterministic seed-journal foundation

Completed output:

- stable master seed and per-adapter sub-seeds in `server/app/deterministic.py`
- seed metadata persisted in `time_engine.py` transaction payloads
- adapter preview path accepts explicit seeds for replay-safe previews
- regression coverage for stable seed generation

### [ ] Prompt 7B — recorded draw capture and replay enforcement

Finish:

- adapter-level random draw journals
- replay validation against recorded draw streams
- redo refusal if branch state and recorded replay assumptions diverge

### [x] Prompt 7B1 — deterministic replay probes and redo guard

Completed output:

- deterministic replay probes persisted in transaction payloads
- replay signatures derived from deterministic adapter preview payloads
- redo blocked when deterministic probe signatures no longer match current
  state

### [ ] Prompt 7B2 — per-draw journals and performance pass

Finish:

- explicit draw journals instead of probe-level signatures where practical
- replay enforcement for stochastic adapters once they expose controlled draws
- performance pass on seasonal replay validation so deterministic checks do not
  stall the operator flow

### [x] Prompt 7B2A — deterministic draw journals and performance pass

Completed output:

- lightweight replay journals for deterministic animal-breeding adapters
- seasonal redo validation no longer depends on expensive full preview execution
- script-module loader updated so sibling Norse Grit script imports resolve
  cleanly inside the tool backend

### [ ] Prompt 7B2B — stochastic settlement-stack draw capture

Finish:

- controlled draw journals for settlement-stack randomness
- replay enforcement for stochastic adapters once draw streams are recorded

### [x] Prompt 7B2B1 — weekly settlement-stack draw journals

Completed output:

- tool-level random journaling around `village_politics.py` weekly replay probes
- seeded settlement-stack replay probes now capture `randint` and `choice`
  calls when they occur
- weekly stochastic settlement replay validated through the tool adapter layer

### [ ] Prompt 7B2B2 — broader settlement-stack draw coverage

Finish:

- confirm seasonal settlement-stack replay coverage under heavier random weeks
- extend draw-journal detail if more random sites are introduced
- decide whether settlement-stack should remain tool-deterministic only or gain
  first-class seeded hooks in the source simulation script

### [x] Prompt 7B2B2 — broader settlement-stack draw coverage

Completed output:

- seasonal settlement-stack replay coverage confirmed through seeded probe runs
- caller-aware draw-journal entries added for settlement-stack replay probes
- current decision: keep settlement-stack tool-deterministic for now rather than
  patching first-class seeded hooks into `village_politics.py` yet

### [x] Prompt 9C — human-readable chronicle UX

Completed output:

- replaced the operator-desk-first homepage with a chronicle/blog layout
- added a left-rail date picker over recorded simulated days
- added category and entity toggles for readable filtering
- merged authored weather/events data with generated transaction chronicle posts
- exposed feed APIs at `/api/feed` and `/api/feed/facets` so the UI can read
  the world as dated posts instead of opaque system panels

### [x] Prompt 10 — grim theme skin and modular narrative renderers

Completed output:

- rebuilt the frontend skin around the logo palette with dark stone, frost,
  bone, moss, and blood accents
- split the feed generation into source-specific modules for weather, canonical
  events, transactions, and settlement dossiers

### [x] Prompt 11 — calendar widget, transport row, and narrative disclosure

Completed output:

- replaced the tag-list calendar with a month-grid calendar widget
- added year, season, and month selectors with directional stepping controls
- redesigned the transport row with centered current date and scaled arrow
  groups for day, week, month, and season movement
- moved secondary tags into the post header tag row
- hid technical content by default and exposed it through a header toggle

### [x] Prompt 12 — hot-reload alignment and content presentation scaffold

Completed output:

- aligned the frontend dev server with the actual browser port so hot reload is
  visible in real time
- added a source-type presentation registry for human-friendly post wrappers
- scaffolded renderer-specific presentation for weather, settlements, animals,
  timekeeping, and canon events
- kept the feed extensible so future content types can plug in their own
  readable presentation without rewriting the main app shell
- added settlement dossier posts so settlements can be browsed as readable
  blog entries, not only as raw event references
- kept the feed registry modular so new script/data types can get their own
  renderers without reopening the whole feed engine

### [ ] Prompt 13 — day brief and chronicle readability pass

Build a first-class daily briefing layer so a selected date reads like a human
blog page instead of a flat feed of cards.

Outputs:

- synthesized day-brief module above the posts
- compact, narrative-first post cards with less repeated metadata
- stronger source-specific wrappers for sparse and settlement-heavy days

Validation:

- frontend build
- visual sanity check on `D1 Y312`
- markdown lint on touched docs

### [ ] Prompt 14 — cadence spans for repeated chronicle posts

Teach the chronicle feed that weekly, monthly, and seasonal simulation results
apply across every day in their span instead of appearing on only one date.

Outputs:

- cadence metadata on feed posts
- day and month filters that respect repeated spans
- visible cadence badges in the post chrome

Validation:

- frontend build
- backend feed checks for day and month overlap
- markdown lint on touched docs

### [ ] Prompt 8 — narrative delta engine and export bundles

Generate:

- operator diff summaries
- writer-facing period summaries
- structured JSON exports
- markdown exports for writing-team handoff

### [x] Prompt 8A — transaction narrative scaffold

Completed output:

- transaction-journal narrative builder in `server/app/narrative_engine.py`
- operator and writer-facing summaries derived from committed transactions
- API surface at `/api/transactions/{transaction_id}/narrative`

### [x] Prompt 8B — export bundle scaffold

Completed output:

- transaction export writer in `server/app/export_engine.py`
- JSON and Markdown export bundle generation under `state/exports/`
- API surface at `/api/transactions/{transaction_id}/export`

### [x] Prompt 8C — recent-period export bundle

Completed output:

- recent-history export builder in `server/app/export_engine.py`
- JSON and Markdown period bundle generation over recent transaction history
- API surface at `/api/exports/period`

### [ ] Prompt 9 — professional operator UX

Build the main UX surfaces:

- timeline controls
- preview and apply flow
- diff review
- transaction history
- validation center

### [x] Prompt 9A — operator workspace shell

Completed output:

- rebuilt `src/App.tsx` into a real operator workspace instead of a placeholder
  hero and card grid
- dry-run timeline planner wired to `/api/time/advance` and
  `/api/adapters/preview`
- validation, export, and recent-transaction surfaces wired to live backend
  APIs
- upgraded visual hierarchy and atmosphere in `src/styles.css`

### [x] Prompt 9B — apply flow and transaction review

Completed output:

- apply-movement flow wired to committed `/api/time/advance` calls
- selected-transaction narrative review wired to
  `/api/transactions/{transaction_id}/narrative`
- selected-transaction export wired to
  `/api/transactions/{transaction_id}/export`
- recent transaction list is now a real selection surface instead of static
  status display

### [ ] Prompt 10 — integrity, corruption, and conflict handling

Add protections for:

- out-of-band file edits
- failed writes
- partial transactions
- snapshot mismatch
- branch divergence

### [ ] Prompt 11 — documentation and runbook completion

Write the operator docs, development docs, and recovery procedures so the tool
is maintainable under heavy use.

### [ ] Prompt 12 — chromatic polish and compact chronicle cards

Refine the dark Norse skin, tighten the transport and calendar presentation,
and keep the post cards compact while preserving readable narrative-first
content.

---

## Working Rules For This Pass

- Treat canonical YAML as sacred state, not disposable cache.
- Never rely on uncontrolled randomness.
- Prefer append-only transactions plus snapshots over ad hoc mutation.
- Every forward move must be replayable.
- Every backward move must be hash-verified before commit.
- All high-risk operations need preview and validation.
- After each markdown pass, lint the touched files.

## Risks And Blockers

- settlement-stack seasonal replay validation works but is still expensive and
  will need a future performance pass if it becomes part of every operator flow

## Protected Template

Use this structure when adding a new prompt sequence or expanding this queue:

```md
## Current Focus

- one-sentence mission
- explicit canonical file or system owner

## Scope And Boundaries

- what this pass owns
- what this pass explicitly does not own

### [ ] Prompt N — <goal>

Short prompt description.

Outputs:

- expected file or system result

Validation:

- tests, lint, preview commands, or manual checks

### [ ] Prompt NA — <sub-goal>

Use sub-prompts when a prompt needs to be split without hiding partial
completion.

Completed output:

- concrete finished deliverable

## Decision Log

- YYYY-MM-DD: important scope or design decision

## Risks And Blockers

- open risk
- explicit blocker if present
```

Template minimums:

- every active TODO should declare current focus, scope boundaries, prompt
  queue, working rules, and a protected template block
- every prompt should state outputs
- risky prompts should also state validation
- partial completion should be represented by sub-prompts instead of vague
  prose updates
- if scope changes during execution, record it in a decision log or directly in
  the prompt text
- completed prompt dumps can be removed during cleanup, but the protected
  template stays unless explicitly removed by the user
