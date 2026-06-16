# Notion export and sync pipeline

This folder holds the dedicated publishing pipeline that prepares the numbered
Norse Grit core chapters for repeatable upload into a personal Notion space.

## Scope

Canonical source set for this pipeline:

- include the numbered core chapter family from 01 through 24
- ignore the already-merged 07B file
- ignore 08A through 08H during normal export because 08 is the merged core
  chapter for that material
- keep an audit function in the tool so these assumptions can be verified on
  demand instead of being hardcoded blindly

## Verified Notion API constraints

These values are taken from the current Notion developer documentation as of
2026-04-17.

| Constraint                          |                Official limit |          Project house limit |
| ----------------------------------- | ----------------------------: | ---------------------------: |
| Average request rate                |         3 requests per second | 2 requests per second target |
| Children appended per request       |                    100 blocks |                    90 blocks |
| Nesting depth in one append request |                      2 levels |                     2 levels |
| Total block elements per payload    |                          1000 |                          900 |
| Total request payload size          |                        500 KB |                       450 KB |
| Rich text content per object        |                    2000 chars |                   1800 chars |
| Source chapter soft size target     | not published as one page cap |                        90 KB |

## Design decision

Notion does not publish one simple "max page text size" number for a whole
page. The real API guardrails are request payload size, block counts, and rich
text limits. For this project, the pipeline will therefore split chapters using
three safety checks:

1. clean UTF-8 source text size over 90 KB
2. estimated Notion block count over the project safety budget
3. any single paragraph or list item that would overflow the rich text limit

## Landing page quality standard

The Notion root page should be curated as a proper entry experience, not merely
an upload dump. Use:

- one strong vignette to open the world
- one short world summary in plain language
- one two-column identity frame for what the setting is and is not
- one three-column entry hub for document families and reader goals
- consistent emoji per chapter page for rapid scanning

The concrete draft for this lives in [ENTRY_PAGE_BLUEPRINT.md](ENTRY_PAGE_BLUEPRINT.md).

## Planned CLI

Primary entry point:

- run the pipeline from this folder with Python on [notion_export.py](notion_export.py)

Planned commands:

- `plan` shows the chosen limits, source rules, and directories
- `raw-copy` copies the canonical chapters into raw output
- `raw-copy --dry-run` previews the chapter set and audit results without writing
  files
- `normalize` generates Notion-ready clean Markdown
- `normalize --dry-run` previews the clean-output size changes without writing
  files
- `split` creates stable page and subpage chunks
- `upload` creates or updates Notion pages using saved manifest state
- `upload --patient --max-wait-minutes 180` keeps retrying patiently through temporary Cloudflare or rate-limit blocks
- `sync` runs the full pipeline in order
- `sync --patient --max-wait-minutes 180` does the same for the full end-to-end pipeline

## Project layout

- [notion_export.py](notion_export.py) — CLI entry point and orchestration
- [models.py](models.py) — limits, manifest records, and discovery rules
- [format_normalizer.py](format_normalizer.py) — paragraph unwrapping and safe
  Markdown normalization
- [raw](raw) — copied source chapters
- [clean](clean) — normalized and split output ready for upload
- [state](state) — manifest, upload IDs, and run metadata

## Raw discovery behavior

The exporter currently treats the exact `01` through `24` files as the core
publishable chapter set.

It also audits lettered chapter variants into two groups:

- ignored merged files, currently `07B` and `08A` through `08H`
- notable supplemental variants, currently the `23A` through `23E` arc files

The latest machine-readable discovery result is written to
[state/raw_copy_report.json](state/raw_copy_report.json).

## Normalization behavior

The normalizer unwraps hard-wrapped prose into single-line paragraphs while
preserving the structure that should remain line-sensitive:

- headings
- bullet and numbered lists
- tables
- fenced code blocks
- blockquotes

The latest machine-readable normalization result is written to
[state/normalize_report.json](state/normalize_report.json).

## Upload flow

1. Discover the valid chapter set.
2. Copy the source files into the raw folder.
3. Normalize hard-wrapped Markdown without damaging structure.
4. Estimate Notion size and split at H2 boundaries where possible.
5. Create placeholder or real pages in Notion to reserve page IDs.
6. Rewrite internal chapter references to those page IDs.
7. Upload or update page content in stable batches.
8. If Notion or Cloudflare temporarily blocks requests, patient mode can wait and retry for a long window instead of failing fast.
9. Save manifest state so reruns update pages in place.

## Manifest model

The persisted state file will track:

- project root page ID
- chapter key and source filename
- chapter title and merged or ignored status
- source hash and clean hash
- root page ID for the chapter
- subpage keys such as 05A or 05B
- per-subpage Notion page IDs and upload timestamps
- last successful API version and pipeline version
