# Tools Directory - Norse Grit Campaign

Campaign tools and utilities for the Iron Ledger mercenary campaign in the Rimevegr.

## Available Tools

### RIMEVEGR_HEX_MAP v1.0

**Interactive hexagonal map of the Rimevegr game world**

- **Main file:** `RIMEVEGR_HEX_MAP/index.html` (open in browser)
- **All 15 canonical settlements** placed on hex grid
- **6 major trade routes** with color coding
- **6 terrain types** with environmental hazards
- **Real-time settlement details** and campaign reference data

#### Quick Start

```bash
cd RIMEVEGR_HEX_MAP/
# Double-click index.html
```

#### Files

- `index.html` - Web interface (open this)
- `map.js` - Hex map engine
- `README.md` - Full documentation
- `QUICKSTART.md` - 60-second guide
- `SETTLEMENTS_DATA.md` - Distance/hazard reference
- `PROJECT_SUMMARY.md` - Complete project overview

#### Features

✅ Zoomable/pannable hex map
✅ Click settlements for full details
✅ Real-time coordinate tracking
✅ Trade route visualization
✅ Responsive dark-theme UI
✅ No dependencies (runs offline)

---

## Using the Hex Map

### For Game Masters

1. **Contract planning** - Check distances, settlement details, terrain hazards
2. **Band tracking** - Note hex positions, calculate travel time
3. **Route planning** - Reference named routes and obstacles
4. **Political mapping** - Understand faction distribution

### For Writers/Narrators

1. **Scene placement** - Verify settlement context and locale details
2. **Travel sequences** - Calculate realistic journey times
3. **Atmosphere** - Reference terrain descriptions and environmental effects
4. **Regional politics** - Understand authority hierarchy

### For Campaign Planning

1. **Scenario design** - Find interesting locations and connections
2. **Multi-session tracking** - Mark band movement and standing
3. **Supply logistics** - Estimate forage availability and shelter
4. **Seasonal effects** - Plan weather impacts and route closures

---

## Data Included

### Settlements (All 15 Canonical)

- Fully mapped on hex grid
- All sizes: Hamlet, Village, Large Village, Small Town
- Authority: Jarls, headmen, independent rulers
- Economy: Primary trade goods
- Strategic role: Military/political significance

### Trade Routes (6 Named Routes)

- **Járnvegr** (Iron Road) - Deepholm-Grimholt corridor
- **Beinvegr** (Bone Road) - Frostfjord-Ashen Reach ridge
- **Svartfuruvegr** (Black Pine Way) - Forest crossing
- **Mosavegr** (Moss Way) - Thornwall-Moor's End axis
- **Hafnarvegr** (Harbour Road) - Coastal artery
- **Ísvegr** (Ice Road) - Northern extreme route

### Terrain Types (6 Classifications)

- **Coast** - Maritime hazards, trade nodes
- **Forest** - Dense woodland, wolf territory
- **Moorland** - Exposed uplands, weather hazards
- **Mountains** - Passes, choke points
- **Bog/Marsh** - Soft ground, navigation traps
- **Ice** - Far north, Veil phenomena

### Reference Data

- Distance tables between settlements
- Terrain hazard descriptions
- Travel time calculations (terrain-adjusted)
- Faction relationships and alliances
- Seasonal effects (Long Summer/Long Dark)
- Authority profiles
- Contract opportunities by settlement

---

## Hex Scale & Distances

**Standard Measurement:**

- 1 hex = 6 miles
- Band marching speed ~15-20 miles/day (2-3 hexes)
- Travel time = hex distance × terrain modifier

**Example Journeys:**

- Deepholm to Grimholt: 2 hexes (12 miles, ~1 day)
- Frostfjord to Deepholm: 3 hexes (18 miles, ~1-2 days)
- Deepholm to Icebreak: 5 hexes (30 miles, ~2-3 days)

**Terrain Modifiers:**

- Forest: +50% time (dense, slow)
- Mountain: +100% time (exhausting)
- Bog: +25% time (difficult ground)
- Ice: +100% time (dangerous conditions)
- Long Dark penalty: +50% all routes (cold, short days)

---

## Coordinate System

All settlements use **axial hex coordinates (q, r)**:

| Settlement                                  | Coordinates | Region        |
| ------------------------------------------- | ----------- | ------------- |
| Frostfjord Hollow                           | q5, r3      | Western Coast |
| Deepholm                                    | q6, r7      | Central Hub   |
| Grimholt                                    | q8, r6      | Eastern Moor  |
| Icebreak                                    | q6, r2      | Northern Edge |
| (See SETTLEMENTS_DATA.md for complete list) |             |               |

**For GMs:** Use coordinates to track band position, calculate distances, reference in campaign notes.

---

## Documentation Structure

1. **PROJECT_SUMMARY.md** - Complete project overview (you are here)
2. **QUICKSTART.md** - 60-second setup and basic usage
3. **README.md** - Full feature documentation
4. **SETTLEMENTS_DATA.md** - Reference tables and calculations

Start with QUICKSTART.md, then read details as needed.

---

## Technical Details

- **Technology:** HTML5 Canvas + vanilla JavaScript
- **Browser:** All modern browsers (Chrome, Firefox, Safari, Edge)
- **Dependencies:** None (runs entirely offline)
- **Performance:** Efficient hex rendering with viewport culling
- **Size:** ~47 KB total (including all documentation)

---

## Future Tools (Planned)

Potential future additions to tools folder:

- Supply chain simulator
- Combat grid overlay
- Faction reputation tracker
- Journey planner with supply calculations
- Barrow atlas and supernatural events
- Random encounter generator
- Settlement generator
- NPC roster manager

---

## How to Use This Tools Folder

### Browse Contents

```bash
ls -la RIMEVEGR_HEX_MAP/
```

### Run the Hex Map

```bash
cd RIMEVEGR_HEX_MAP/
# Open index.html in browser
```

### Read Documentation

1. `QUICKSTART.md` - Quick overview
2. `README.md` - Full features
3. `SETTLEMENTS_DATA.md` - Reference tables
4. `PROJECT_SUMMARY.md` - Project details

### Integrate with Campaign

- Reference settlement coordinates in campaign notes
- Use distances for travel planning
- Check terrain hazards for encounters
- Leverage authority relationships for contracts

---

## Roadmap

**v1.0** (Current)

- ✅ Interactive hex map
- ✅ 15 settlements with full metadata
- ✅ 6 trade routes
- ✅ Terrain visualization
- ✅ Real-time details and reference data

**v1.1** (Planned)

- Custom markers and pins
- Campaign notes overlay
- Settlement standing tracker
- Export/screenshot utilities

**v2.0** (Conception)

- Multiple layers (politics, resources, dangers)
- Barrow locations and network
- Weather/seasonal overlays
- Full integration with 02_MASTER_INDEX

---

## Version History

- **v1.0** (April 14, 2026) - Initial release with 15 settlements, 6 routes, full documentation

---

## Support & Questions

For issues or improvements:

1. Check `QUICKSTART.md` for quick answers
2. Read `README.md` for full feature list
3. Reference `SETTLEMENTS_DATA.md` for campaign math
4. Review `PROJECT_SUMMARY.md` for technical details

---

**Last Updated:** April 14, 2026
**Campaign:** Iron Ledger - Mercenaries of the Rimevegr
**Status:** v1.0 - Complete & Ready for Use
