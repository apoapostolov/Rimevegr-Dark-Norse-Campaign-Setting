# Rimevegr Hex Map Tool

Interactive hexagonal map of the Rimevegr game world from the Iron Ledger campaign setting.

## Features

- **Hexagonal Grid System**: 6-mile hexes representing the full Rimevegr territory
- **15 Canonical Settlements**: All major settlements positioned on the map with full metadata
- **6 Major Trade Routes**: Járnvegr (Iron Road), Beinvegr (Bone Road), Svartfuruvegr (Black Pine Way), Mosavegr (Moss Way), Hafnarvegr (Harbour Road), and Ísvegr (Ice Road)
- **Terrain Visualization**: 6 terrain types with color coding
  - **Coast (Blue)**: Fjords, coastal settlements, maritime trade
  - **Forest (Dark Green)**: Dense woodlands, wolf territory, mysterious places
  - **Moorland (Tan)**: Open uplands, exposed and wind-scoured
  - **Mountains (Grey)**: High passes, thin air, crevasses
  - **Bog (Cyan)**: Soft ground, marsh hazards, difficult terrain
  - **Ice (Light Blue)**: Far northern regions, extreme cold, Veil-edge phenomena
- **Interactive Settlement Details**: Click any settlement to view full information
- **Zoomable/Pannable Interface**: Drag to pan, scroll to zoom, or use buttons
- **Real-time Coordinates**: Hover to see hex coordinates

## Usage

### Opening the Map

1. Open `index.html` in a web browser
2. The map will load centered on the Rimevegr with all settlements visible

### Viewing Settlements

**Click Method:**

- Click on any settlement marker (orange circle) on the map
- Details panel updates automatically on the right sidebar

**List Method:**

- Click any settlement name in the "Settlements" panel on the right
- Map pans to center the selected settlement
- Selected settlement is highlighted in blue

### Navigation

**Zoom:**

- Scroll mouse wheel to zoom in/out
- Use "Zoom +" and "Zoom -" buttons
- Zoom level displayed in sidebar (50% to 300%)

**Pan:**

- Click and drag anywhere on the map to pan
- Double-click settlements to center and select

**Reset:**

- Click "Reset View" button to return to default centered view

**Coordinates:**

- Hover anywhere to see axial hex coordinates in sidebar
- Use coordinates for custom navigation or campaign notes

## Geographical Layout

### Western Fjord Region (Coast - Blue)

- **Frostfjord Hollow** (q5, r3) - Main jarl seat, Hrothgar
- **Ashen Reach** (q4, r4) - The Pale Widow's influence hub
- **Kolvik** (q6, r5) - Coastal logistics and ship repair
- **Stonebay Hamlet** (q7, r6) - Isolated fishing hamlet

### Central Forest Region (Green)

- **Vargheim** (q5, r6) - Jarl Ulf's wolf doctrine territory
- **Ashmark** (q4, r7) - Forest-border buffer town
- **Feldwick** (q5, r8) - Occupied settlement, example of decay

### Deep Trade Center (Mixed)

- **Deepholm** (q6, r7) - Sigrun's industrial hub, market gravity
- **Skaldhaven** (q7, r8) - Lore-Keeper's archive and saga tradition
- **Raven's Perch** (q7, r7) - Mountain pass guardian, Egil's position

### Moorland Region (Tan)

- **Grimholt** (q8, r6) - Ordovast's militarized stronghold
- **Thornwall** (q6, r9) - Helga's moor defense bastion
- **Moor's End** (q7, r10) - Marginal settlement, attrition

### Marginal Settlements

- **Bleakwater Landing** (q5, r10) - River crossing toll house
- **Icebreak** (q6, r2) - Hermit Ragnhild's Veil-edge outpost

## Trade Routes

Each route connects settlements with specific characteristics:

### Járnvegr (Iron Road) - Red

- **Deepholm ↔ Grimholt**
- Highest traffic, toll-controlled, militarily contested
- Core east-west flow of raw materials and trade

### Beinvegr (Bone Road) - Light Red

- **Frostfjord Hollow → Ashen Reach → Vargheim**
- Exposed ridge route, wind-heavy, politically sensitive
- Critical fjord-to-forest connection

### Svartfuruvegr (Black Pine Way) - Green

- **Vargheim → Ashmark → Feldwick**
- Forest crossing through wolf and outlaw territory
- Hidden and navigationally punishing in fog

### Mosavegr (Moss Way) - Orange

- **Thornwall ↔ Moor's End** and **Grimholt ↔ Thornwall**
- Sinkhole and exposure risk, poor retreat options
- Moorland traverse, dangerous in bad weather

### Hafnarvegr (Harbour Road) - Light Blue

- **Frostfjord Hollow → Kolvik → Stonebay Hamlet**
- Coast-fjord commercial artery
- Storm vulnerability but essential maritime trade

### Ísvegr (Ice Road) - Purple

- **Bleakwater Landing → Icebreak**
- Existential risk corridor, extreme weather
- Veil-edge survival route, rarely attempted

## Hex Scale

- **1 Hex = 6 miles**
- **Band marching speed:** ~15-20 miles/day (2-3 hexes)
- **Expected travel times between major settlements:** 3-7 days
- The distance metric reinforces that travel is about survival, shelter intervals, and forage reliability — not just mileage.

## Settlement Data

Each settlement includes:

- **Name**: Full settlement name
- **Size**: Hamlet, Village, Large Village, Small Town
- **Authority**: Current ruler/leadership
- **Terrain**: Primary terrain type (affects climate, hazards, resources)
- **Economic Spine**: Primary trade goods
- **Strategic Identity**: Military/political role in region
- **Hex Coordinates**: (q, r) in axial system for campaign use

## Coordinate System

Uses **axial (offset) hexagonal coordinates**:

- **q**: Horizontal axis (west-east)
- **r**: Vertical axis (northwest-southeast)

This system is ideal for campaign mapping because:

- Adjacent hexes are easily calculated
- Distance between any two hexes is simple to determine
- Terrain transitions are visually logical
- Perfect for a tabletop campaign grid

## Campaign Use

### For Game Masters

1. Reference settlement locations for contract locations
2. Use trade routes to determine realistic travel paths
3. Check terrain to understand hazard type (forest = wolves/disorientation, moor = exposure, coast = storms)
4. Calculate travel time between settlements (roughly 1-2 days per hex)

### For Writers

1. Place scenes in specific settlements with correct regional context
2. Understand distance relationships for temporal pacing
3. Reference terrain to describe environment authentically
4. Use road network to plan character/band movement sequences

### For Campaign Planning

1. Track band position across the map
2. Mark occupied territory or hostile regions
3. Note seasonal closure of passes (mountains in winter)
4. Calculate logistics: forage availability, supply lines, shelter intervals

## Technical Notes

- **Built with:** HTML5 Canvas, vanilla JavaScript
- **Responsive:** Adapts to window size
- **No dependencies:** Runs entirely in browser
- **Local storage:** No data sent to server
- **Cross-browser:** Works in any modern browser

## Future Enhancements

Possible additions for future versions:

- Save/load campaign marks and notes
- Seasonal route closures with weather overlays
- Barrow locations and network dynamics
- Risk heat maps (wolf territory, outlaw regions)
- Travel time calculator between any two settlements
- Export to PDF for printing
- Custom hex editing for house rules
- Settlement standing/reputation tracker
- Supply chain simulator for logistics planning

## Data Source

All settlement and route information derived from:

- **01_RIMEVEGR_SETTING_BIBLE.md** - Canonical Settlements section
- **Canonical Routes section** - Major strategic Route Network section
- **Geography sections** - Terrain types and regional descriptions

See the setting bible for detailed lore on each settlement and region.

---

**Version:** 1.0 (April 2026)
**Campaign:** Iron Ledger - Mercenaries of the Rimevegr
**Scale:** 6 miles per hex
