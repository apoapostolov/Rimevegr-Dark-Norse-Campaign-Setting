# AGENTS.md - Rimevegr Time Manager

## Mission

Maintain the Rimevegr Time Manager as a live, browser-visible chronicle CMS and
world-state control surface.

## Instruction Quality Standard

Keep this file focused on the live tool contract.

- Name the exact dev server command or file path when describing a change.
- Keep canonical state files distinct from reversible runtime output.
- Put UI styling or component details in the owning presentation module.
- If a workflow needs a recovery step, state it explicitly.

## Operational Rules

- Keep the frontend on the real hot-reload dev server.
- Reboot the dev server after every prompt or meaningful UI pass so the browser
  never lingers on stale modules.
- Treat `data/` as canonical state and `state/` as reversible runtime output.
- Keep the current cursor aligned with the canonical tool start date unless the
  user explicitly moves the world.
- Prefer source-specific presentation modules over a single generic renderer.

## Start State

- Canonical tool cursor starts at `D1 Y312`.
- The blog view should default to that day when the tool boots.

## Presentation Goal

- Human-friendly chronicle posts first.
- Technical detail hidden by default and revealed only on request.
- Compact calendar and transport controls.
- Grim Norse steel, frost, ash-blue, moss, and blood palette.

## Last reviewed

2026-06-01. Bump on any meaningful change to this file or its siblings.
