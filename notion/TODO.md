# TODO - Notion Export and Sync Pipeline for Iron Ledger

## Current Focus

Build a repeatable publishing tool that converts the core Norse Grit chapter
files for safe import and update in Notion.

Target outcome:

- copy the canonical `01_` through `24_` chapter files into `notion/raw/`
- normalize wrapped Markdown prose into proper Notion-ready paragraphs
- preserve headings, lists, tables, code fences, and other structural blocks
- estimate Notion limits conservatively and split oversized chapters into
  stable subpages such as `05A`, `05B`, and `05C`
- add a table of contents marker at the top of each clean page body
- convert cross-chapter references into Notion page links during upload
- store page IDs and content hashes so reruns update existing pages instead of
  creating duplicates

## Project Configuration

- Parent Notion destination: create a new root page
- Internal cross-links: target specific subpages when possible
- Oversized chapter layout: parent chapter page acts as an index and also
  includes the first content chunk where this stays readable
- Chapter selection rules: ignore 07B and ignore 08A through 08H during the
  normal export path because 08 is the merged core file for that material
- Add a duplicate-audit check so the tool can confirm those merge assumptions
  instead of trusting them silently
- Notion API key for this project:
  `NOTION_API_KEY=ntn_h39319427987sUHCsEQrs8cjAxo1v9dWPcHEhUtDtgN2wX`

**Resume rule:** when returning to this file, start with the first unchecked
prompt in the active queue below.

**Cleanup rule:** when asked to clean this file, remove completed prompt dumps
instead of preserving them. Keep only the current focus, working rules, and
active prompt queue unless the user explicitly asks for archives.

**Removal rule:** if the user says to remove prompts, tasks, or completed items
from this file, delete them outright. Do not archive them elsewhere unless the
user explicitly asks for an archive.

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

## Active Prompt Queue — Notion Export and Sync Pipeline

### [x] Prompt 1 — limits and architecture pass

Research the relevant Notion API constraints and define the project layout,
state model, and upload flow.

Completed output:

- verified Notion request and block limits recorded in `notion/README.md`
- chosen Python module layout and CLI entry point scaffolded in
  `notion/notion_export.py`
- manifest schema scaffolded in `notion/models.py` and
  `notion/state/manifest_template.json`

### [ ] Prompt 1A — Notion landing page composition pass

Design a high-quality root entry page for the Notion project so the uploaded
material opens with atmosphere, clarity, and strong navigation.

Output:

- a world-opening vignette chosen from the existing material
- a short summary of the setting
- a two-column section for what the setting is and is not
- a three-column navigation hub for the document families
- an emoji scheme for the page tree and chapter pages
- a root-page blueprint in `notion/ENTRY_PAGE_BLUEPRINT.md`

### [x] Prompt 2 — raw copy and discovery pass

Implement the source discovery logic for the canonical numbered chapter files,
copy them into `notion/raw/`, and ignore non-core support files.

Completed output:

- stable file ordering from `01_` through `24_` verified by tests
- reproducible raw export step implemented in the raw-copy command
- dry-run output and audit report now show the core set, ignored merged files,
  and supplemental chapter variants

### [x] Prompt 3 — Markdown normalization pass

Implement `format_normalizer.py` to unwrap hard-wrapped prose while preserving
all meaningful Markdown structure.

Completed output:

- one-line paragraphs for prose blocks now generated in `notion/clean/`
- preserved bullet and numbered list semantics verified by tests
- preserved tables, headings, code fences, and blockquotes verified by tests
- regression coverage added for wrapped paragraphs, wrapped bullets, and fenced
  content

### [ ] Prompt 4 — size estimation and split pass

Implement a Notion-aware estimator and chapter splitter that prefers `##`
headings for boundaries and falls back gracefully when a section is too large.

Output:

- conservative size budgeting for text and block counts
- stable subpage naming such as `05A`, `05B`, and `05C`
- parent chapter index page for oversized chapters
- deterministic split behavior across reruns

### [ ] Prompt 5 — TOC and internal linking pass

Insert a table of contents block marker at the top of each page and resolve
cross-references into real Notion links after page IDs are known.

Output:

- TOC marker on every clean page or subpage
- link-rewrite strategy that survives repeated uploads
- fallback handling when a referenced chapter has no uploaded target yet

### [ ] Prompt 6 — upload and update sync pass

Build the Notion upload client so the tool can create pages on first run and
update them in place on later runs.

Output:

- parent project page support
- page create versus update logic
- manifest persistence in `notion/state/`
- safe retry and partial-failure recovery behavior

### [ ] Prompt 7 — validation and docs pass

Test the pipeline end to end on a subset of chapters, document usage, and make
sure reruns are idempotent.

Output:

- sample run against a few large and small chapters
- clear README or usage notes for future reruns
- regression tests for normalization, chunking, and sync behavior

---

## Working Rules for This Pass

- Treat the numbered Norse Grit files as the canonical source material.
- Treat everything under `notion/raw/`, `notion/clean/`, and `notion/state/`
  as derived artifacts unless explicitly documented otherwise.
- Prefer deterministic behavior so rerunning the tool produces stable page and
  subpage identities.
- Use conservative Notion limits with safety margin instead of aiming at the
  absolute maximum.
- Prefer splitting on `##` headings; only split deeper when a single section is
  still too large.
- Do not damage tables, lists, or code fences during paragraph unwrapping.
- Keep the parent page primarily as an index and navigation surface for
  oversized chapters unless a mixed index-plus-content layout proves cleaner.
- Add tests before or alongside each risky transformation step.

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

Output:

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
