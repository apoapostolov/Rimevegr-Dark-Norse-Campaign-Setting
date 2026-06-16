# AGENTS.md — Notion export tool rules

## Scope

These rules apply to everything under this folder and to all work on the Norse
Grit Notion export pipeline.

## Instruction Quality Standard

Keep export instructions short and keyed to the live Notion artifacts.

- Name the current manifest or page file when describing a sync step.
- Put page-shape rules here; keep content-specific polish notes in the snapshot
  state files.
- If the pipeline changes, update the exact files that own the export logic and
  the landing page state in the same session.

## Front page rules

- Treat the root Notion front page as a curated landing page, not as a dump of
  raw chapter content.
- Preserve the current snapped front-page title as Rimevegr.
- Keep the opening sequence as hero callout, one summary paragraph, then a
  divider.
- Do not place a TOC block on the front page.
- Keep TOC blocks on chapter documents and oversized chapter index pages only.
- Use chapter titles on the front page instead of numeric prefixes.
- Prefer clear, scannable navigation labels and slightly expanded descriptive
  summaries in the identity columns.

## Manual polish preservation rule

If the user says "snapshot the front page":

1. read the currently active Notion front page
2. compare it with the generated local landing-page layout
3. identify all manual polish changes in wording, structure, ordering, and tone
4. store those differences locally as the new canonical front-page polish state
5. preserve and reapply those manual changes in all future front-page updates

Manual user edits to the front page should be treated as authoritative unless
the user explicitly asks to overwrite them.

## Sync behavior

- Prefer fast page replacement over slow block-by-block clearing when content
  changes materially.
- Create refreshed pages with content in the initial request whenever possible.
- Keep manifest state clean and deterministic so reruns recover from deleted
  Notion pages safely.

## Last reviewed

2026-06-01. Bump on any meaningful change to this file or its siblings.
