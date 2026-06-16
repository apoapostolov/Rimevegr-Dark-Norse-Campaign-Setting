# Campaign — DM's Working Directory

This folder is the Dungeon Master's personal campaign workspace for
running tabletop games set in the Iron Ledger Rimevegr setting.

## Folder Structure

```text
campaign/
├── data/               # DM's custom band state (mirrors /data schema)
│   └── band_state.yaml # The DM's player-run band
├── sessions/           # Session logs and notes
├── prep/               # Session prep documents
├── npcs/               # DM-created NPCs (supplements /data/npcs/)
├── maps/               # Battle maps, dungeon maps, region sketches
└── handouts/           # Player-facing handouts and props
```

## Data Convention

- **World data** (geography, settlements, weather, bestiary, factions,
  contracts, barrows, events, hidden content): use the canonical files
  in `/data/` — do not duplicate them here.
- **Band data**: the DM's player-run band lives in `campaign/data/`.
  It follows the same YAML schema as `/data/band_state.yaml` but
  tracks the players' band, not the novel's Voss's Black Axes.
- **Scripts**: use the scripts in `/scripts/` against campaign data
  by passing `--data-dir campaign/data` where supported, or by copying
  the relevant YAML into `campaign/data/` and running locally.

## Session Logs

After each session, create a log in `sessions/`:

```text
sessions/
  session_001.md
  session_002.md
  ...
```

Use the template in
`00_DUNGEON_MASTER_CAMPAIGN_PLANNING.md § Session Log Template`.
