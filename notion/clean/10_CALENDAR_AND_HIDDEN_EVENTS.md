# Calendar and Hidden Events

**Project:** Iron Ledger -- Mercenaries of the Rimevegr
**Purpose:** Calendar system and hidden events engine. Hidden data is stored in Chinese via `scripts/hidden_info.py`.

---

## 1. Calendar System

**Year Structure:**

- One year = 360 days (12 months of 30 days each)
- Long Summer: Days 1-60 (Months 1-2)
- The Long Dark: Days 61-360 (Months 3-12)

**Month Names:**

1. Frostwake (summer)
2. Rimeblood (summer)
3. Veilthin
4. Ashfall
5. Ironmoon
6. Wolfmoot
7. Barrowrise
8. Longnight
9. Hearthstar
10. Bloodtide
11. Skaldsong
12. Yuledeep

**Current Date Format:**

```yaml
current_date:
  year: 312
  day_of_year: 87
  season: "The Long Dark"
  month: "Ironmoon"
  day_of_month: 27
```

---

## 2. Hidden Events Engine

Hidden events are pre-seeded and triggered by date, player action, or simulation state. All hidden event text is stored in Chinese encoding.

### Event Structure

```yaml
hidden_event:
  id: "evt_001"
  trigger_type: "date" # date / action / state
  trigger_condition: "day >= 95"
  encoded_text: "Encoded Chinese text here"
  status: "pending" # pending / triggered / resolved
```

### Trigger Types

- **Date:** Fires when the calendar reaches a specific day.
- **Action:** Fires when a band member or NPC takes a specific action.
- **State:** Fires when a simulation value crosses a threshold (e.g., morale drops below 2, food stores hit 0).

### Event Categories

1. **NPC Betrayal** -- Named Men reaching loyalty 1, planning to desert or act against the band.
2. **Rival Band Movement** -- Rival Svarthird approaching, planning ambush, or competing for same contract.
3. **Supernatural** -- Barrow awakening, rune-stone activation, Veil events tied to calendar dates.
4. **Political** -- Jarl's secret plans, settlements forming alliances, bounties posted.
5. **Environmental** -- Severe weather events, blocked passes, flood or avalanche.

### Chinese Encoding Protocol

1. Write event description in English.
2. Run: `python scripts/hidden_info.py encode "<description>"`
3. Store encoded output in `data/hidden/<event_file>.txt`
4. Reference the file path in the event YAML structure.
5. During play, AI decodes as needed.

---

## 3. Pre-Seeded Events

Hidden events are stored encoded in `data/hidden/`. The AI decodes them as needed during play. See:

- `data/hidden/npc_secrets.txt` — 9 NPC secrets and plot seeds
- `data/hidden/calendar_events.txt` — 12 date-triggered events
- `data/hidden/campaign_arcs.txt` — 3 arcs + 4 escalation chains
- `data/hidden/manifest.yaml` — AI-side index (IDs, types, triggers)

To decode any entry: `python scripts/hidden_info.py decode "<encoded>"`

---

## 4. AI Maintenance Rules

- Check hidden events at the start of every in-game day.
- When an event triggers, decode it, apply effects, and re-encode any follow-up events.
- Hidden events manifest through surface effects only (a veteran growing distant, a rival band spotted in the distance, a rune-stone bleeding). The encoded content drives narrative but is never exposed raw.
- Log triggered events for continuity tracking.
