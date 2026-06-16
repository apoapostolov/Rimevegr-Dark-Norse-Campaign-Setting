# Discussion Logs

Persistent conversation threads between agents. Each file captures
a multi-turn discussion on a specific topic — a scene revision, a
factual dispute, a combat design, a plot decision.

## Naming Convention

```text
YYYY-MM-DD_chNN_topic.md
```

Examples:

- `2026-04-13_ch14_sigrid_negotiation_realism.md`
- `2026-04-14_ch16_barrow_combat_choreography.md`
- `2026-04-15_general_kell_betrayal_arc_direction.md`

Use `general_` prefix for discussions not tied to a specific chapter.

## File Format

```markdown
# Discussion: [Topic]

**Chapter:** [N or "general"]
**Started:** YYYY-MM-DD HH:MM
**Participants:** Agent1, Agent2, Agent3
**Status:** OPEN | RESOLVED | ESCALATED
**Resolution:** [one-line summary, filled when resolved]

---

[AGENT → AGENT] (TYPE) — YYYY-MM-DD HH:MM
Message content.

[AGENT → AGENT] (TYPE) — YYYY-MM-DD HH:MM
Reply content.
```

## Rules

- One topic per file. If a discussion branches, start a new file.
- Never delete logs. Resolved discussions are reference material.
- Agents cite discussion logs when referencing past decisions:
  "See `discussions/2026-04-13_ch14_negotiation_realism.md`"
- Mark ESCALATED when User intervention was required. Record
  the User's decision in the resolution line.
