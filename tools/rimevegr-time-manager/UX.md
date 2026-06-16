# Rimevegr Time Manager UX

## UX Goal

Give one operator a calm, professional control surface for moving the world
through time without losing trust in the data.

The UX should feel like:

- a timeline console
- a diff-and-approval tool
- a world-state inspector
- a narrative export station

It should not feel like a spreadsheet or a programmer-only debug panel.

Current maturity note:

- the present UI is an early scaffold for live development
- placeholder panels are acceptable while core engine and replay integrity are
  still being built
- the final product target is a world-class operator console with a strong
  medieval mercenary visual language, not a generic dashboard

## Primary Users

- world operator maintaining canonical state
- writing lead reviewing what changed over a period
- systems designer checking simulation consequences

## Primary Screens

### 1. Timeline Workspace

- current world date
- current branch
- forward and backward step controls
- jump-to-date
- bookmarks and named milestones
- last transaction status

### 2. Apply Preview

Shown before commit.

- chosen step
- simulations that will run
- files likely to change
- estimated risk level
- random domains involved
- warning if Voss-band-linked domains are excluded

### 3. World Diff Review

- file list changed
- grouped entity deltas: settlements, unions, traders, contracts, events
- before/after values for critical fields
- semantic summaries like:
  - `Grimholt treasury -4.6 silver`
  - `Ashen Reach confidence shock +0.22`
  - `Thornwall outlaw pressure 1 -> 3`

### 4. Narrative Digest

- operator summary
- writer-facing summary
- chronological bullet timeline
- export buttons for markdown and JSON

### 5. History And Undo

- transaction log
- filters by date, file, settlement, system
- undo and redo controls
- integrity warning if current files do not match expected hashes

### 6. Validation Center

- schema failures
- formatting drift
- missing references
- non-deterministic adapter warnings
- stale snapshot warnings

## Essential UX Behaviors

### Safe apply flow

1. choose time movement
2. preview affected systems
3. inspect expected deltas
4. commit transaction
5. review narrative and validation result

### Safe rewind flow

1. select prior transaction
2. verify current state matches expected hashes
3. preview inverse changes
4. commit undo
5. optionally redo later

### Branching flow

1. choose historical transaction
2. create new branch label
3. fork timeline
4. keep original branch immutable

## UX Rules

- always show whether the view is preview or committed state
- never hide file mutations behind narrative prose
- surface risk and integrity status prominently
- use human-readable labels first and raw ids second
- keep destructive actions two-step, but not bureaucratic

## Visual Direction

- clean operator dashboard
- muted Nordic palette, high readability
- strong typography hierarchy
- side-by-side diff panels where useful
- timeline rail plus detail pane
- final visual tone should feel like a premium command desk for a harsh
  medieval mercenary world: tactile, disciplined, atmospheric, and trustworthy

## Nice-To-Have Later

- heatmap of world stress by settlement
- transaction replay animation
- “why did this change?” provenance panel per field
- writer-mode filtered narrative without technical noise
