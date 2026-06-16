# TODO - Iron Ledger: Mercenaries of the Rimevegr

## Current Focus

Core settlement-economy integration work is complete.

The active major undertaking has moved to:

- `writing/norse_grit/tools/RIMEVEGR-TIME-MANAGER/TODO.md`

## Completed Core Outcome

The Norse Grit economy pass now includes:

- settlement production, stocks, shortages, and route pressure
- union tribute, levy, trade-bonus, and seat-support flows
- covert upkeep and confidence pressure
- wolfshead territorial pressure and outlaw economics
- contract-market budgeting, advances, payout reserve, and settlement
  consequences
- CLI inspection for economy, union, wolfshead, and contract-market state
- documentation alignment across `20_SIMULATION_RULES.md` and
  `05_ECONOMY_OF_RIMEVEGR.md`

## Working Rules

**Cleanup rule:** when asked to clean this file, remove completed prompt dumps
instead of preserving them.

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

## Template (Do Not Remove)

Use this structure when a new major undertaking becomes the active queue in this
file:

```md
## Current Focus

- one-sentence mission
- explicit canonical file or system owner

## Scope And Boundaries

- what this pass owns
- what this pass explicitly does not own

## Active Prompt Queue — <Epic Name>

### [ ] Prompt 1 — <goal>

Short prompt description.

Outputs:

- expected file or system result

Validation:

- tests, lint, preview commands, or manual checks

### [ ] Prompt 1A — <sub-goal>

Use sub-prompts when a prompt needs to be split without hiding partial
completion.

Completed output:

- concrete finished deliverable

## Working Rules

- canonical source
- derived outputs
- rollback or safety notes

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
