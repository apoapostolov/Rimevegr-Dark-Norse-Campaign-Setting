# Mailbox — Timestamped Agent Messages

Long-form messages between agents that do not fit the rapid
back-and-forth of discussion threads. Used for:

- Fan reactions and chapter reviews (essays, not one-liners)
- Strategist assessments of multi-chapter arcs
- Historian research proposals with full evidence
- Author reflections on direction and craft decisions
- Editor comprehensive quality reports
- Choreographer fight design proposals with full geometry

## Structure

Each agent has a subfolder. Messages are filed by **recipient**
so each agent finds incoming messages in their own folder.

```text
mailbox/
├── author/
│   ├── 2026-04-13_1445_from_editor_ch14_quality_report.md
│   └── 2026-04-13_1500_from_fan_ch14_reaction.md
├── editor/
│   └── 2026-04-13_1430_from_author_ch14_revision_notes.md
├── historian/
├── strategist/
├── computer/
├── simulator/
├── fan/
└── choreographer/
```

## Naming Convention

```text
YYYY-MM-DD_HHMM_from_SENDER_topic.md
```

Use `from_all` for broadcast messages received by everyone.
Use `from_user` for messages from the User.

Broadcast messages: the sender creates one copy in each
recipient's folder (or a single copy in a `_broadcast/`
subfolder if created).

## Message Format

```markdown
# [SENDER → RECIPIENT] — YYYY-MM-DD HH:MM

**Subject:** [topic]
**Chapter:** [N or "general"]
**Priority:** NORMAL | URGENT | FYI

---

[Long-form message content. No length limit. This is where
agents write extended thoughts, detailed analyses, and
substantive feedback that would be too long for a discussion
thread message.]
```

## Rules

- Messages are immutable once sent. Corrections go in a new
  message referencing the original.
- URGENT messages should be read before the next draft cycle.
- FYI messages are reference material — no response required.
- Agents check their own subfolder at the start of each chapter
  cycle to see if anything was left for them.
