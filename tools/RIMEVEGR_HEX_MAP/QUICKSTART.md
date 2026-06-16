# Rimevegr Hex Map - Quick Start

**TL;DR:** Open `index.html` in your browser. Click settlements. Use mouse to pan/zoom.

---

## 60-Second Setup

1. **Navigate to the folder:**

   ```bash
   cd tools/RIMEVEGR_HEX_MAP/
   ```

2. **Open in browser:**
   - Double-click `index.html`, OR
   - Right-click → "Open with" → Choose your browser

3. **The map appears** with all 15 settlements, 6 trade routes, and terrain colors

---

## Core Controls

| Action                      | Result                          |
| --------------------------- | ------------------------------- |
| **Click a settlement**      | View full details in sidebar    |
| **Scroll mouse wheel**      | Zoom in/out                     |
| **Click & drag**            | Pan around the map              |
| **Settlement list (right)** | Select by name (map pans to it) |
| **Zoom + / Zoom - buttons** | Quick zoom control              |
| **Reset View button**       | Return to default centered view |

---

## What You See

### Left: The Map

- **Orange dots** = Settlements (size = population)
- **Colored hexes** = Terrain (blue=coast, green=forest, tan=moor, grey=mountain, cyan=bog, light blue=ice)
- **Colored lines** = Trade routes (red=contested, green=forest, orange=dangerous, etc.)

### Right: The Sidebar

- **Legend** = Terrain types & colors
- **Settlements list** = All 15 clickable by name
- **Info panel** = Details on selected settlement
- **Coordinates** = Your mouse position in hex coords
- **Zoom level** = Current zoom percentage

---

## Settlement Details

When you select a settlement, you see:

- **Name** & **Size** (Hamlet, Village, Large Village, Small Town)
- **Authority** (who rules it)
- **Terrain** (environmental hazards)
- **Economic** (what it trades)
- **Strategic** (military/political role)
- **Hex coordinates** (for GM reference)

---

## Distance & Travel Time

Use the **Settlements Data** reference (`SETTLEMENTS_DATA.md`) for:

- Distance between any two settlements (in hexes)
- Travel time estimates
- Terrain hazards for each region
- Authority relationships and factions
- Seasonal effects on routes

**Quick math:**

- 1 hex = 6 miles ≈ 1 day travel
- Forest/mountains = add time
- Long Dark season = everything slower

---

## Reading the Map Geographically

### West (Coast)

- **Frostfjord Hollow** (Hrothgar) - Main fjord seat
- **Ashen Reach** (Pale Widow) - Intrigue hub
- **Kolvik** - Ship repair & logistics

### Central (Mixed)

- **Deepholm** (Sigrun) - Market gravity, trade center
- **Vargheim** (Ulf) - Forest authority, wolf doctrine
- **Skaldhaven** - Lore archive

### East (Moor/Mountain)

- **Grimholt** (Ordovast) - Militarized stronghold
- **Raven's Perch** (Egil) - Mountain pass control

### South (Marginal)

- **Thornwall** (Helga) - Moor defense bastion
- **Moor's End** - Attrition settlement
- **Bleakwater Landing** - River toll house

### North (Edge)

- **Icebreak** (Ragnhild) - Veil-edge outpost, supernatural access

---

## Campaign Use Scenarios

### Planning a Contract Route

1. Click start settlement
2. Hover over map to check hexes
3. Reference terrain hazards in sidebar or SETTLEMENTS_DATA
4. Calculate days using hex distance × terrain modifier

### Tracking Band Position

- Note the hex coordinates
- Use sidebar's coordinate display to track movement
- Estimate forage/shelter by terrain type

### Understanding Politics

- Selection shows which jarl/authority controls each settlement
- Read authority relationships in SETTLEMENTS_DATA
- Use to plan faction-based contracts

### Weather & Season Planning

- Reference Long Dark season hazards
- Mountain passes close in winter → check alternate routes
- Forest becomes impassable in deep snow → use Ice Road alternatives

---

## Files in This Folder

- **index.html** — Main map (open this in browser)
- **map.js** — All map logic and settlement data
- **README.md** — Full documentation
- **SETTLEMENTS_DATA.md** — Distance, hazard, and faction reference
- **QUICKSTART.md** — This file

---

## Troubleshooting

### Map doesn't load?

- Check JavaScript console (F12 → Console tab)
- Make sure all three files (index.html, map.js) are in same folder
- Try a different browser

### Settlements don't appear?

- Check that map.js loaded (look for text in sidebar)
- Zoom out if they're off-screen (use "Reset View")

### Performance lag?

- Reduce zoom level
- Close other browser tabs
- Hex rendering is CPU-intensive at high zoom

---

## Tips & Tricks

1. **Find nearest settlement:** Zoom in on area, click settlements to compare distances
2. **Plot a route:** Click each stop to check terrain hazards
3. **Check factions:** Use SETTLEMENTS_DATA to see allied/opposed authorities
4. **Reference GMs:** Share coordinates with grid references ("Band at q7, r8")
5. **Print-friendly:** Zoom out fully, screenshot/print (best in dark theme)

---

## Next Steps

- Read **README.md** for full feature list
- Check **SETTLEMENTS_DATA.md** for distances and hazards
- Modify **map.js** to add custom markers, house rules, or campaign notes
- Integrate coordinates into your campaign notes

---

**Questions?** Refer to the full README.md or check the setting bible for lore context.
