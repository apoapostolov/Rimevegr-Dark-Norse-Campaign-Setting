// Rimevegr Hex Map - JavaScript Implementation
// Hexagonal grid system with 6-mile hexes

class HexMap {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext("2d");

    // Size canvas to fill parent container
    this.resizeCanvas();

    // Hex configuration
    this.hexRadius = 30; // pixels per hex
    this.hexWidth = this.hexRadius * 2;
    this.hexHeight = (Math.sqrt(3) / 2) * this.hexWidth;

    // Camera/view settings
    this.offsetX = 0;
    this.offsetY = 0;
    this.zoom = 1;
    this.minZoom = 0.5;
    this.maxZoom = 3;

    // Selected settlement
    this.selectedSettlement = null;

    // Layer visibility controls
    this.layers = {
      terrain: true,
      roads: true,
      settlements: true,
      passes: true,
      locations: true,
      barrows: false, // Hidden by default - spoiler content
    };
    this.barrowsSpoilerAcknowledged = false;
    this.hoveredLocation = null; // For tooltip support

    // Terrain definitions
    this.terrainTypes = {
      coast: { color: "#1a4d7a", label: "Coast (Fjords)" },
      forest: { color: "#2d5a3d", label: "Forest (Dense)" },
      moor: { color: "#6b7550", label: "Moorland" },
      mountain: { color: "#5a5a6b", label: "Mountains" },
      bog: { color: "#4a6b7a", label: "Bog/Marsh" },
      ice: { color: "#a0a8c0", label: "Ice/Snow" },
    };

    // Cache for elevation map (noise-based terrain generation)
    this.elevationCache = new Map();
    this.terrainCache = new Map();

    // Settlement data - positioned on expanded hex grid (15x14) with realistic geography
    // Terrain distribution: Coast (W), Forest (C), Moors (E/S), Mountains (E), Ice (N)
    this.settlements = [
      // ============ INNER FJORDS (Western Coast) ============
      {
        name: "Frostfjord Hollow",
        size: "Village",
        authority: "Jarl Hrothgar",
        terrain: "coast",
        q: 1,
        r: 3,
        economic: "Dried cod, fjord trade",
        strategic: "Fjord seat under pressure",
      },
      {
        name: "Stonebay Hamlet",
        size: "Hamlet",
        authority: "Local elders",
        terrain: "coast",
        q: 2,
        r: 6,
        economic: "Fishing",
        strategic: "Isolated, low-defense coast hold",
      },
      {
        name: "Kolvik",
        size: "Village",
        authority: "Harbour-Master Inga",
        terrain: "coast",
        q: 1,
        r: 8,
        economic: "Ship repair, fish",
        strategic: "Coastal logistics node",
      },
      {
        name: "Ashen Reach",
        size: "Large Village",
        authority: "The Pale Widow",
        terrain: "coast",
        q: 3,
        r: 10,
        economic: "Pine tar, ironwork",
        strategic: "Intrigue-heavy regional hinge",
      },

      // ============ BLACK PINE WILDS (Central Forest) ============
      {
        name: "Vargheim",
        size: "Large Village",
        authority: "Jarl Ulf Vargson",
        terrain: "forest",
        q: 6,
        r: 4,
        economic: "Charcoal, kennels",
        strategic: "Forest authority with wolf doctrine",
      },
      {
        name: "Ashmark",
        size: "Village",
        authority: "Reeve Torsten",
        terrain: "forest",
        q: 7,
        r: 8,
        economic: "Pine tar, herbs",
        strategic: "Forest-border buffer",
      },
      {
        name: "Feldwick",
        size: "Village",
        authority: "Occupied (Three Wolves)",
        terrain: "forest",
        q: 8,
        r: 10,
        economic: "Sheep, root stores",
        strategic: "Example of occupation decay",
      },
      {
        name: "Skaldhaven",
        size: "Village",
        authority: "Lore-Keeper Audun",
        terrain: "forest",
        q: 9,
        r: 6,
        economic: "Relic and knowledge trade",
        strategic: "Archive culture and saga memory",
      },

      // ============ CENTRAL BOG/MARKET HUB ============
      {
        name: "Deepholm",
        size: "Small Town",
        authority: "Jarl Sigrun",
        terrain: "bog",
        q: 6,
        r: 7,
        economic: "Metals, arms, market",
        strategic: "Industrial and political gravity well",
      },

      // ============ BLEAKWATER REGION (Bog/River margin) ============
      {
        name: "Bleakwater Landing",
        size: "Hamlet",
        authority: "Ferryman Olaf",
        terrain: "bog",
        q: 3,
        r: 12,
        economic: "Crossing tolls, fish",
        strategic: "River bottleneck in a dying margin",
      },

      // ============ HIGH RIME-MOORS (Southern/Eastern Moors) ============
      {
        name: "Thornwall",
        size: "Large Village",
        authority: "Jarl Helga Thornwall",
        terrain: "moor",
        q: 7,
        r: 11,
        economic: "Wool, mutton, sheep trade",
        strategic: "Moor bulwark and levy source",
      },
      {
        name: "Moor's End",
        size: "Hamlet",
        authority: "Elder Brosa",
        terrain: "moor",
        q: 8,
        r: 13,
        economic: "Sheep, peat",
        strategic: "Marginal settlement under attrition",
      },

      // ============ EASTERN MOORS / MOUNTAIN BORDER ============
      {
        name: "Grimholt",
        size: "Large Village",
        authority: "Warchief Ordovast",
        terrain: "moor",
        q: 11,
        r: 7,
        economic: "Iron extraction",
        strategic: "Militarized moor stronghold",
      },

      // ============ MOUNTAIN REGION (Eastern Heights) ============
      {
        name: "Raven's Perch",
        size: "Village",
        authority: "Thane Egil Raven-Eye",
        terrain: "mountain",
        q: 12,
        r: 5,
        economic: "Mountain hides, ore",
        strategic: "Pass control and high watch position",
      },

      // ============ NORTHERN ICE-REACH ============
      {
        name: "Icebreak",
        size: "Hamlet",
        authority: "Hermit Ragnhild",
        terrain: "ice",
        q: 6,
        r: 1,
        economic: "Subsistence outpost",
        strategic: "Veil-edge survival and seidr access",
      },

      // ============ MOUNTAIN PASSES (Strategic landmarks) ============
      {
        name: "Járnskarð",
        size: "Pass",
        authority: "Contested",
        terrain: "mountain",
        q: 11,
        r: 6,
        economic: "N/A",
        strategic: "Primary mountain crossing; controls east-west flow",
        isPass: true,
      },
      {
        name: "Hrafnaskarð",
        size: "Pass",
        authority: "Contested",
        terrain: "mountain",
        q: 12,
        r: 6,
        economic: "N/A",
        strategic: "Access spine to Raven's Perch; highland surveillance",
        isPass: true,
      },
      {
        name: "Kveldsskarð",
        size: "Pass",
        authority: "Perilous",
        terrain: "mountain",
        q: 13,
        r: 8,
        economic: "N/A",
        strategic: "Hard-winter fallback pass; less stable, more lethal",
        isPass: true,
      },
    ];

    // Road network based on canonical routes.yaml corridors between nearby settlements.
    this.roads = [
      {
        from: "Frostfjord Hollow",
        to: "Ashen Reach",
        name: "Beinvegr",
        color: "#ff9999",
      },
      {
        from: "Frostfjord Hollow",
        to: "Skaldhaven",
        name: "Fjörðskuggaleið",
        color: "#7db7d9",
      },
      {
        from: "Frostfjord Hollow",
        to: "Kolvik",
        name: "Hafnleið",
        color: "#69b3d7",
      },
      {
        from: "Ashen Reach",
        to: "Thornwall",
        name: "Ekkjubraut",
        color: "#ffaa00",
      },
      {
        from: "Ashen Reach",
        to: "Ashmark",
        name: "Askstígr",
        color: "#6bc56b",
      },
      {
        from: "Ashen Reach",
        to: "Feldwick",
        name: "Austrvegr",
        color: "#8acb7f",
      },
      {
        from: "Ashen Reach",
        to: "Vargheim",
        name: "Úlfaleið",
        color: "#5ca85c",
      },
      {
        from: "Thornwall",
        to: "Moor's End",
        name: "Mosavegr",
        color: "#cfa558",
      },
      {
        from: "Thornwall",
        to: "Grimholt",
        name: "Hrímheiðarvegr",
        color: "#d28f4a",
      },
      {
        from: "Thornwall",
        to: "Feldwick",
        name: "Ullarbraut",
        color: "#bba26e",
      },
      { from: "Grimholt", to: "Deepholm", name: "Járnvegr", color: "#ff6b6b" },
      { from: "Grimholt", to: "Ashmark", name: "Markaleið", color: "#c88266" },
      { from: "Grimholt", to: "Vargheim", name: "Viðarvegr", color: "#8d7a5b" },
      {
        from: "Grimholt",
        to: "Raven's Perch",
        name: "Hrafnaniðrstígr",
        color: "#9ba3bb",
      },
      { from: "Deepholm", to: "Ashmark", name: "Námuvegr", color: "#d38f54" },
      {
        from: "Deepholm",
        to: "Vargheim",
        name: "Leynibraut",
        color: "#8f9a6b",
      },
      {
        from: "Deepholm",
        to: "Raven's Perch",
        name: "Himinstígr",
        color: "#a8a8d8",
      },
      {
        from: "Kolvik",
        to: "Stonebay Hamlet",
        name: "Hamargata",
        color: "#4ea8d6",
      },
      {
        from: "Kolvik",
        to: "Skaldhaven",
        name: "Hafnarvegr",
        color: "#5ab0d6",
      },
      { from: "Kolvik", to: "Feldwick", name: "Fjǫrustígr", color: "#7fbf8f" },
      {
        from: "Kolvik",
        to: "Bleakwater Landing",
        name: "Suðrstrandleið",
        color: "#8ecae6",
      },
      {
        from: "Stonebay Hamlet",
        to: "Skaldhaven",
        name: "Brimstígr",
        color: "#84b9d8",
      },
      {
        from: "Stonebay Hamlet",
        to: "Bleakwater Landing",
        name: "Norðurstrandarvegr",
        color: "#9fcfe6",
      },
      {
        from: "Vargheim",
        to: "Feldwick",
        name: "Svartfuruvegr",
        color: "#5fbf5f",
      },
      { from: "Vargheim", to: "Ashmark", name: "Úlfavegr", color: "#58b458" },
      {
        from: "Vargheim",
        to: "Raven's Perch",
        name: "Veiðistígr",
        color: "#7f9aa8",
      },
      {
        from: "Moor's End",
        to: "Feldwick",
        name: "Lambastígr",
        color: "#b8a96a",
      },
      {
        from: "Moor's End",
        to: "Ashmark",
        name: "Heiðimarkaleið",
        color: "#b99a66",
      },
      {
        from: "Bleakwater Landing",
        to: "Icebreak",
        name: "Ísvegr",
        color: "#b7c8ff",
      },
      {
        from: "Raven's Perch",
        to: "Skaldhaven",
        name: "Hrafnstígr",
        color: "#9aa8c4",
      },
      {
        from: "Ashmark",
        to: "Skaldhaven",
        name: "Griptvegr",
        color: "#9ab67c",
      },
    ];

    // Barrow locations with spoiler summaries (hidden by default)
    this.barrows = [
      // Frostfjord Region
      {
        name: "Whispering Barrow",
        code: "BAR_001",
        q: 2,
        r: 2,
        summary:
          "Stone lintel with humming runes marks the restless resting place of the spring-risen dead.",
      },
      {
        name: "Draugr-Jarl's Crypt",
        code: "BAR_002",
        q: 1,
        r: 3,
        summary:
          "Ancient binding beneath Hrothgar's hall weakens; the Draugr-Jarl's cold kills within five metres.",
      },
      {
        name: "Skaldhaven Cairn",
        code: "BAR_003",
        q: 8,
        r: 7,
        summary:
          "Broken fishermen's cairn on dangerous cliff ledge hosts three restless dead with accessible relic trade.",
      },
      {
        name: "Bone Road Mound",
        code: "BAR_004",
        q: 5,
        r: 5,
        summary:
          "Unbroken grass-covered mound whispers of voices beneath; never opened, positioned to be found or avoided.",
      },
      // Grimholt Region
      {
        name: "Iron Barrow",
        code: "BAR_005",
        q: 10,
        r: 8,
        summary:
          "Opened autumn-last, holds fourteen draugr in disciplined military formation; Hollow Hall camps at entrance.",
      },
      {
        name: "Ordovast's Shame",
        code: "BAR_006",
        q: 11,
        r: 8,
        summary:
          "Deliberately collapsed by Warchief order; rubble shifts at night—sealed or still spreading unknown.",
      },
      {
        name: "Bleakwater Hollow",
        code: "BAR_007",
        q: 4,
        r: 11,
        summary:
          "Exposed by flood, waterlogged dead move slowly but relentlessly through re-flooding chambers each season.",
      },
      {
        name: "The War-Grave",
        code: "BAR_008",
        q: 12,
        r: 9,
        summary:
          "Unsealed mass burial of hundreds without saga record; weapon points pierce turf as if pressing upward.",
      },
      // Deepholm Region
      {
        name: "Archive Barrow",
        code: "BAR_009",
        q: 7,
        r: 8,
        summary:
          "Mountain cavern holds rune-inscribed archive of older knowledge, guarded by haugbui beyond first hall.",
      },
      {
        name: "The Hollow Vein",
        code: "BAR_010",
        q: 7,
        r: 10,
        summary:
          "Miners broke through to burial chamber; dead miners now walk with barrow occupants in narrow, toxic shafts.",
      },
      {
        name: "Thornwall Passage",
        code: "BAR_011",
        q: 8,
        r: 11,
        summary:
          "Sealed tunnel in ancient unreadable rune dialect, actively warded; connected to Dalla's unwanted visions.",
      },
      // Coastal Region
      {
        name: "Kolvik Barrow",
        code: "BAR_012",
        q: 2,
        r: 6,
        summary:
          "Minor barrow activated spring-last; first sign in the waking-barrows chain marked by dead cattle.",
      },
      {
        name: "Stonebay Wreck-Grave",
        code: "BAR_013",
        q: 2,
        r: 5,
        summary:
          "Ship-burial in sea cliffs with drowned captain preserved in salt; tide-access four-hour window.",
      },
      {
        name: "Salt Cairn",
        code: "BAR_014",
        q: 3,
        r: 7,
        summary:
          "Cave-sealed with regenerating salt crystals; pre-settlement masonry of unknown construction.",
      },
      // Moor Region
      {
        name: "Standing Stone Barrow",
        code: "BAR_015",
        q: 7,
        r: 11,
        summary:
          "Humming standing stones create unpredictable Veil activity; haugbui guards chamber on featureless moor.",
      },
      {
        name: "Feldwick Peat Grave",
        code: "BAR_016",
        q: 8,
        r: 11,
        summary:
          "Peat-acid preserved leather-jointed dead; bog ground swallows armoured fighters while bog-preserved corpses move undamaged.",
      },
      {
        name: "Ghost Moor Cairns",
        code: "BAR_017",
        q: 6,
        r: 9,
        summary:
          "Seven sealed cairns in unknown pattern; compasses spin and stars look wrong in Veil-field between them.",
      },
      {
        name: "Helga's Watch",
        code: "BAR_018",
        q: 7,
        r: 11,
        summary:
          "Thornwall's buried shield-maiden disturbed from below; five draugr circle moonlit hilltop.",
      },
      // Forest Region
      {
        name: "Ashmark Root-Grave",
        code: "BAR_019",
        q: 7,
        r: 9,
        summary:
          "Barrow overgrown by forest roots in dead-earth oval; bone swarms nest in root-tangles.",
      },
      {
        name: "Vargheim Pit",
        code: "BAR_020",
        q: 6,
        r: 4,
        summary:
          "Sinkhole burial accessible only in dry summers before autumn rain refills the chamber.",
      },
      {
        name: "The Widow's Barrow",
        code: "BAR_021",
        q: 4,
        r: 9,
        summary:
          "Woman's carved face screaming at entrance; sealed, warded, forbidden; Pale Widow knows contents.",
      },
      // Mountain Region
      {
        name: "Raven's Perch Barrow",
        code: "BAR_022",
        q: 12,
        r: 5,
        summary:
          "Largest active barrow holds Barrow-King seated on throne with burning eyes; map stone reveals connected barrows.",
      },
      {
        name: "Spine Ridge Ossuary",
        code: "BAR_023",
        q: 13,
        r: 7,
        summary:
          "Bone alcoves in cliff face for dishonoured oath-breakers; haugbui guards deepest chambers high above treeline.",
      },
      {
        name: "High Pass Tomb",
        code: "BAR_024",
        q: 13,
        r: 9,
        summary:
          "Stone slab blocks cave mouth with fresh scratch marks from inside—claws trying escape from sealed tomb.",
      },
      // Ice Region
      {
        name: "Icebreak Complex",
        code: "BAR_025",
        q: 6,
        r: 1,
        summary:
          "Network of ice-linked chambers with blue-glowing rune-stones; Veil permanence thinning.",
      },
      {
        name: "The First Barrow",
        code: "BAR_026",
        q: 5,
        r: 0,
        summary:
          "Hill that breathes and shifts corridors; collects dead like immune system; source of Rimevegr death-energy network.",
      },
    ];

    // Geography atlas points of interest (full data/geography/atlas.yaml coverage)
    this.locations = this.buildAtlasLocations();
    this.settlementFlavor = this.buildSettlementFlavorMap();

    // Per-hex marker occupancy for overlap-aware rendering/hover
    this.hexObjectCounts = new Map();
    this.hexMarkerOffsets = new Map();
    this.buildHexObjectCounts();

    // Initialize
    this.setupEventListeners();
    this.populateSettlementsList();
    this.centerView();
    this.render();

    // Handle window resize
    window.addEventListener("resize", () => this.handleResize());
  }

  resizeCanvas() {
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.canvas.width = rect.width;
    this.canvas.height = rect.height;
  }

  handleResize() {
    this.resizeCanvas();
    this.render();
  }

  setupEventListeners() {
    // Canvas interaction
    this.canvas.addEventListener("click", (e) => this.handleCanvasClick(e));
    this.canvas.addEventListener("mousemove", (e) => this.handleMouseMove(e));
    this.canvas.addEventListener("wheel", (e) => this.handleZoom(e));

    // Drag to pan
    let isDragging = false;
    let dragStartX = 0;
    let dragStartY = 0;

    this.canvas.addEventListener("mousedown", (e) => {
      isDragging = true;
      dragStartX = e.clientX;
      dragStartY = e.clientY;
    });

    this.canvas.addEventListener("mousemove", (e) => {
      if (isDragging) {
        const dx = e.clientX - dragStartX;
        const dy = e.clientY - dragStartY;
        this.offsetX += dx;
        this.offsetY += dy;
        dragStartX = e.clientX;
        dragStartY = e.clientY;
        this.render();
      }
    });

    this.canvas.addEventListener("mouseup", () => {
      isDragging = false;
    });

    this.canvas.addEventListener("mouseleave", () => {
      isDragging = false;
    });
  }

  populateSettlementsList() {
    const list = document.getElementById("settlementsList");
    list.innerHTML = "";

    this.settlements.forEach((settlement) => {
      const item = document.createElement("div");
      item.className = "settlement-item";
      item.textContent = settlement.name;
      item.onclick = () => this.selectSettlement(settlement);
      list.appendChild(item);
    });
  }

  selectSettlement(settlement) {
    this.selectedSettlement = settlement;
    this.updateInfoPanel(settlement);

    // Update UI
    document.querySelectorAll(".settlement-item").forEach((item) => {
      item.classList.remove("selected");
      if (item.textContent === settlement.name) {
        item.classList.add("selected");
      }
    });

    // Pan to settlement
    const screenX = this.canvas.width / 2;
    const screenY = this.canvas.height / 2;
    const hexPos = this.axialToPixel(settlement.q, settlement.r);
    this.offsetX = screenX - hexPos.x * this.zoom;
    this.offsetY = screenY - hexPos.y * this.zoom;

    this.render();
  }

  updateInfoPanel(settlement) {
    const panel = document.getElementById("infoPanel");
    const terrain = this.terrainTypes[settlement.terrain];

    panel.innerHTML = `
            <h4>${settlement.name}</h4>
            <p><span class="size">Size:</span> ${settlement.size}</p>
            <p><span class="authority">Authority:</span> ${settlement.authority}</p>
            <p><span class="terrain">Terrain:</span> ${terrain.label}</p>
            <p><strong>Economic:</strong> ${settlement.economic}</p>
            <p><strong>Strategic:</strong> ${settlement.strategic}</p>
            <p style="margin-top: 10px; color: #666; font-size: 11px;">Hex coordinates: (${settlement.q}, ${settlement.r})</p>
        `;
  }

  handleCanvasClick(e) {
    const rect = this.canvas.getBoundingClientRect();
    const mouseX = (e.clientX - rect.left - this.offsetX) / this.zoom;
    const mouseY = (e.clientY - rect.top - this.offsetY) / this.zoom;

    // Check if clicked on a settlement
    for (let settlement of this.settlements) {
      const hexPos = this.getMarkerPosition(
        settlement.q,
        settlement.r,
        "settlement",
        settlement.name,
      );
      const distance = Math.hypot(mouseX - hexPos.x, mouseY - hexPos.y);
      if (distance < 15) {
        this.selectSettlement(settlement);
        return;
      }
    }
  }

  handleMouseMove(e) {
    const rect = this.canvas.getBoundingClientRect();
    const mouseX = (e.clientX - rect.left - this.offsetX) / this.zoom;
    const mouseY = (e.clientY - rect.top - this.offsetY) / this.zoom;

    // Update coordinates display
    const hex = this.pixelToAxial(mouseX, mouseY);
    document.getElementById("coords").textContent =
      `(${Math.round(hex.q)}, ${Math.round(hex.r)})`;

    // Check hover on settlements first (highest priority)
    const tooltip = document.getElementById("locationTooltip");
    let hovering = false;
    let foundSettlement = false;

    for (let settlement of this.settlements) {
      const hexPos = this.getMarkerPosition(
        settlement.q,
        settlement.r,
        "settlement",
        settlement.name,
      );
      const distance = Math.hypot(mouseX - hexPos.x, mouseY - hexPos.y);
      if (distance < 15) {
        const terrainLabel =
          this.terrainTypes[settlement.terrain]?.label || settlement.terrain;
        const shortDescription = this.getSettlementFlavor(settlement.name);
        this.canvas.style.cursor = "pointer";
        this.showTooltip(
          e.clientX - rect.left,
          e.clientY - rect.top,
          settlement.name,
          `${settlement.size} • ${terrainLabel} — ${shortDescription}`,
          "settlement",
        );
        hovering = true;
        foundSettlement = true;
        break;
      }
    }

    // Check hover on barrows (only if no settlement hovered)
    if (!foundSettlement && this.layers.barrows) {
      for (let barrow of this.barrows) {
        const hexPos = this.getMarkerPosition(
          barrow.q,
          barrow.r,
          "barrow",
          barrow.code,
        );
        const distance = Math.hypot(mouseX - hexPos.x, mouseY - hexPos.y);
        if (distance < 12) {
          this.canvas.style.cursor = "pointer";
          this.showTooltip(
            e.clientX - rect.left,
            e.clientY - rect.top,
            barrow.name,
            barrow.summary,
            "barrow",
          );
          hovering = true;
          foundSettlement = true;
          break;
        }
      }
    }

    // Check hover on locations (only if no settlement/barrow hovered)
    if (!foundSettlement && this.layers.locations) {
      for (let location of this.locations) {
        const hexPos = this.getMarkerPosition(
          location.q,
          location.r,
          "location",
          location.id || location.name,
        );
        const distance = Math.hypot(mouseX - hexPos.x, mouseY - hexPos.y);
        if (distance < 12) {
          this.canvas.style.cursor = "pointer";
          this.showTooltip(
            e.clientX - rect.left,
            e.clientY - rect.top,
            location.name,
            location.summary,
            "location",
          );
          hovering = true;
          foundSettlement = true;
          break;
        }
      }
    }

    // Hide tooltip if nothing hovered
    if (!foundSettlement) {
      tooltip.style.display = "none";
    }

    // Set grab cursor if nothing hovering
    if (!hovering) {
      this.canvas.style.cursor = "grab";
    }
  }

  buildHexObjectCounts() {
    this.hexObjectCounts.clear();
    this.hexMarkerOffsets.clear();

    const add = (q, r, type) => {
      const key = `${q},${r}`;
      if (!this.hexObjectCounts.has(key)) {
        this.hexObjectCounts.set(key, {
          total: 0,
          settlement: 0,
          barrow: 0,
          location: 0,
        });
      }

      const entry = this.hexObjectCounts.get(key);
      entry.total += 1;
      entry[type] += 1;
    };

    const markersByHex = new Map();
    const addMarker = (q, r, markerKey, markerType, sortName) => {
      const key = `${q},${r}`;
      if (!markersByHex.has(key)) {
        markersByHex.set(key, []);
      }
      markersByHex.get(key).push({ markerKey, markerType, sortName });
    };

    this.settlements.forEach((settlement) => {
      add(settlement.q, settlement.r, "settlement");
      addMarker(
        settlement.q,
        settlement.r,
        `settlement:${settlement.name}`,
        "settlement",
        settlement.name,
      );
    });
    this.barrows.forEach((barrow) => {
      add(barrow.q, barrow.r, "barrow");
      addMarker(
        barrow.q,
        barrow.r,
        `barrow:${barrow.code}`,
        "barrow",
        barrow.code,
      );
    });
    this.locations.forEach((location) => {
      add(location.q, location.r, "location");
      addMarker(
        location.q,
        location.r,
        `location:${location.id || location.name}`,
        "location",
        location.name,
      );
    });

    const slotOffsets = [
      { x: -10, y: -10 },
      { x: 10, y: -10 },
      { x: 10, y: 10 },
      { x: -10, y: 10 },
      { x: 0, y: -14 },
      { x: 14, y: 0 },
      { x: 0, y: 14 },
      { x: -14, y: 0 },
    ];
    const priority = { settlement: 0, barrow: 1, location: 2 };

    for (const [hexKey, markers] of markersByHex.entries()) {
      if (markers.length <= 1) continue;

      markers.sort((a, b) => {
        const typeOrder =
          (priority[a.markerType] ?? 9) - (priority[b.markerType] ?? 9);
        if (typeOrder !== 0) return typeOrder;
        return a.sortName.localeCompare(b.sortName);
      });

      const perHexOffsets = new Map();
      markers.forEach((marker, index) => {
        perHexOffsets.set(
          marker.markerKey,
          slotOffsets[index] || { x: 0, y: 0 },
        );
      });
      this.hexMarkerOffsets.set(hexKey, perHexOffsets);
    }
  }

  getMarkerOffset(q, r, markerType, markerId = null) {
    const key = `${q},${r}`;
    const counts = this.hexObjectCounts.get(key);

    if (markerId !== null && markerId !== undefined) {
      const markerKey = `${markerType}:${markerId}`;
      const perHexOffsets = this.hexMarkerOffsets.get(key);
      if (perHexOffsets && perHexOffsets.has(markerKey)) {
        return perHexOffsets.get(markerKey);
      }
    }

    // Keep centered when there is only one marker in the hex.
    if (!counts || counts.total < 2) {
      return { x: 0, y: 0 };
    }

    // Slight type-based offsets to separate stacked markers in one hex.
    if (markerType === "settlement") {
      return { x: -8, y: -8 };
    }
    if (markerType === "barrow") {
      return { x: 8, y: -8 };
    }
    if (markerType === "location") {
      return { x: 8, y: 8 };
    }

    return { x: 0, y: 0 };
  }

  getMarkerPosition(q, r, markerType, markerId = null) {
    const base = this.axialToPixel(q, r);
    const offset = this.getMarkerOffset(q, r, markerType, markerId);
    return {
      x: base.x + offset.x,
      y: base.y + offset.y,
    };
  }

  normalizeName(value) {
    return (value || "")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "")
      .trim();
  }

  hashString(value) {
    let hash = 2166136261;
    for (let i = 0; i < value.length; i++) {
      hash ^= value.charCodeAt(i);
      hash +=
        (hash << 1) + (hash << 4) + (hash << 7) + (hash << 8) + (hash << 24);
    }
    return (hash >>> 0) / 4294967295;
  }

  classifyLocationType(rawType) {
    const type = (rawType || "").toLowerCase();

    if (["pass", "bridge", "ford", "causeway", "crossroads"].includes(type)) {
      return "pass";
    }

    if (
      [
        "standing_stone",
        "waymarker",
        "watchtower",
        "ridge",
        "headland",
        "hill",
        "island",
        "cliff",
        "precipice",
        "aurora_field",
      ].includes(type)
    ) {
      return "landmark";
    }

    if (
      ["ruin", "abandoned_farm", "shelter", "ice_camp", "mine"].includes(type)
    ) {
      return "facility";
    }

    if (
      [
        "bog",
        "battlefield",
        "execution_ground",
        "crevasse",
        "veil_zone",
        "quaking_ground",
        "avalanche_zone",
        "slag_heap",
        "fjord_arm",
      ].includes(type)
    ) {
      return "hazard";
    }

    return "location";
  }

  inferLocationSubtype(name) {
    const value = (name || "").toLowerCase();

    if (value.includes("pass") || value.includes("skarð")) return "pass";
    if (value.includes("ford") || value.includes("vað")) return "ford";
    if (value.includes("bridge") || value.includes("brú")) return "bridge";
    if (value.includes("crossroads") || value.includes("vegamót"))
      return "crossroads";
    if (
      value.includes("watch") ||
      value.includes("tower") ||
      value.includes("vörð")
    )
      return "watchtower";
    if (
      value.includes("stone") ||
      value.includes("steinn") ||
      value.includes("marker")
    )
      return "standing_stone";
    if (
      value.includes("bog") ||
      value.includes("mýr") ||
      value.includes("pool")
    )
      return "bog";
    if (
      value.includes("cave") ||
      value.includes("hellir") ||
      value.includes("grotto")
    )
      return "cave";
    if (
      value.includes("ruin") ||
      value.includes("croft") ||
      value.includes("stead")
    )
      return "ruin";
    if (value.includes("waterfall") || value.includes("foss"))
      return "waterfall";
    if (value.includes("ridge") || value.includes("hryggr")) return "ridge";
    if (value.includes("cliff") || value.includes("hamr")) return "cliff";
    if (value.includes("shrine") || value.includes("altar")) return "shrine";
    if (value.includes("field") || value.includes("battle"))
      return "battlefield";
    return "landmark";
  }

  pickOpenHex(q, r, occupancy, seed) {
    const candidates = [
      [0, 0],
      [1, 0],
      [-1, 0],
      [0, 1],
      [0, -1],
      [1, -1],
      [-1, 1],
      [2, 0],
      [-2, 0],
      [0, 2],
      [0, -2],
      [2, -1],
      [-2, 1],
      [1, 1],
      [-1, -1],
      [2, -2],
      [-2, 2],
    ];

    const start = Math.floor(this.hashString(seed) * candidates.length);
    for (let i = 0; i < candidates.length; i++) {
      const [dq, dr] = candidates[(start + i) % candidates.length];
      const cq = Math.max(0, Math.min(14, q + dq));
      const cr = Math.max(0, Math.min(13, r + dr));
      const key = `${cq},${cr}`;
      if (!occupancy.has(key)) {
        occupancy.add(key);
        return { q: cq, r: cr };
      }
    }

    const fallbackKey = `${q},${r}`;
    occupancy.add(fallbackKey);
    return { q, r };
  }

  buildAtlasLocations() {
    const atlasSummary = `GEO_COAST_001|Kolvik Breakwater|coastal|Kolvik|0
GEO_COAST_002|The Tide-Teeth|coastal|Kolvik|1
GEO_COAST_003|Vigdis-Steinn|coastal|Stonebay|0
GEO_COAST_004|Drengr's Needle|coastal|Kolvik|2
GEO_COAST_005|Skerjaholm|coastal|Kolvik|3
GEO_COAST_006|Gannet Sker|coastal|Stonebay|1
GEO_COAST_007|Járnnes|coastal|Kolvik|2
GEO_COAST_008|Hvalbein Cliff|coastal|Stonebay|0
GEO_COAST_009|The Maw|coastal|Stonebay|1
GEO_COAST_010|The Keel of Ulfvár|coastal|Kolvik|3
GEO_COAST_011|Eldvörðr Tower|coastal|Stonebay|2
GEO_COAST_012|Kolvik Light|coastal|Kolvik|1
GEO_COAST_013|Drekavágr|coastal|Skaldhaven|1
GEO_COAST_014|Beinastrand|coastal|Stonebay|1
GEO_COAST_015|Þrívegr Cairn|coastal|Stonebay|1
GEO_COAST_016|Selþing|coastal|Kolvik|2
GEO_COAST_017|Ørnahamr|coastal|Stonebay|3
GEO_COAST_018|Netbýli|coastal|Kolvik|1
GEO_COAST_019|Sjávarpottr|coastal|Stonebay|1
GEO_DEEP_001|The Hoard-Pillar|deepholm|Deepholm|0
GEO_DEEP_002|Sif's Finger|deepholm|Deepholm|1
GEO_DEEP_003|The Drowning Drift|deepholm|Deepholm|2
GEO_DEEP_004|Brokk's Grotto|deepholm|Deepholm|1
GEO_DEEP_005|The Long Seam|deepholm|Deepholm|1
GEO_DEEP_006|The Slag Meres|deepholm|Ashmark|1
GEO_DEEP_007|Kolgruva|deepholm|Ashmark|2
GEO_DEEP_008|Gapjaw Bridge|deepholm|Deepholm|1
GEO_DEEP_009|Járnkelda Hall|deepholm|Deepholm|3
GEO_DEEP_010|The Midkaup|deepholm|Deepholm|0
GEO_DEEP_011|The Forge-Altar|deepholm|Deepholm|2
GEO_DEEP_012|Ashmark Hollow|deepholm|Ashmark|0
GEO_DEEP_013|The Scar|deepholm|Deepholm|2
GEO_DEEP_014|Munnr Gate|deepholm|Deepholm|0
GEO_DEEP_015|Svartfoss|deepholm|Deepholm|3
GEO_DEEP_016|Silfurkelda|deepholm|Deepholm|1
GEO_DEEP_017|Ginnungagat|deepholm|Ashmark|2
GEO_DEEP_018|Grjótstalli|deepholm|Deepholm|3
GEO_DEEP_019|Kolbýli|deepholm|Ashmark|2
GEO_FOREST_001|The Kviststeinar|forest|Vargheim|1
GEO_FOREST_002|Rotviðr Marker|forest|Vargheim|3
GEO_FOREST_003|Úlfhella Staves|forest|Vargheim|2
GEO_FOREST_004|Heilagrlundr|forest|Vargheim|4
GEO_FOREST_005|The Stillvǫllr|forest|Feldwick|3
GEO_FOREST_006|Kolbrannssléttan|forest|Feldwick|1
GEO_FOREST_007|Gamlafelling|forest|Vargheim|5
GEO_FOREST_008|Svartkelda|forest|Vargheim|2
GEO_FOREST_009|Fornhǫll|forest|Feldwick|4
GEO_FOREST_010|Úlfagrǫf|forest|Vargheim|3
GEO_FOREST_011|Furubrú|forest|Feldwick|2
GEO_FOREST_012|Blóðnálar|forest|Vargheim|4
GEO_FOREST_013|Vegamót|forest|Feldwick|2
GEO_FOREST_014|Djúpgil|forest|Vargheim|5
GEO_FOREST_015|Aldreik|forest|Feldwick|5
GEO_FOREST_016|Hulðufoss|forest|Vargheim|3
GEO_FOREST_017|Svartvatn|forest|Feldwick|4
GEO_FOREST_018|Naglastalli|forest|Vargheim|2
GEO_FOREST_019|Merkitrjám|forest|Feldwick|1
GEO_FROST_001|Hrothgar's Mark|frostfjord|Frostfjord Hollow|1
GEO_FROST_002|Seidr-Nail|frostfjord|Skaldhaven|2
GEO_FROST_003|Tide-Watcher's Finger|frostfjord|Ashen Reach|3
GEO_FROST_004|Kveldsarm|frostfjord|Frostfjord Hollow|2
GEO_FROST_005|Daudagrof|frostfjord|Skaldhaven|4
GEO_FROST_006|Beinbrú|frostfjord|Frostfjord Hollow|3
GEO_FROST_007|Ormahellir|frostfjord|Frostfjord Hollow|5
GEO_FROST_008|Kolgrafhellir|frostfjord|Skaldhaven|3
GEO_FROST_009|Ketilstead|frostfjord|Frostfjord Hollow|6
GEO_FROST_010|Bleikrvollr|frostfjord|Ashen Reach|2
GEO_FROST_011|Blóðlundr|frostfjord|Skaldhaven|1
GEO_FROST_012|Grátindur|frostfjord|Frostfjord Hollow|2
GEO_FROST_013|Svarthofði|frostfjord|Ashen Reach|1
GEO_FROST_014|Varðaturn|frostfjord|Frostfjord Hollow|4
GEO_FROST_015|Þríræði|frostfjord|Frostfjord Hollow|3
GEO_FROST_016|Geirrhús|frostfjord|Frostfjord Hollow|2
GEO_FROST_017|Brúðarfoss|frostfjord|Ashen Reach|3
GEO_FROST_018|Heitkeldur|frostfjord|Skaldhaven|4
GEO_FROST_019|Kaupvörðr|frostfjord|Frostfjord Hollow|1
GEO_GRIM_001|Ordovast's Nail|grimholt|Grimholt|1
GEO_GRIM_002|The Herd-Stones|grimholt|Grimholt|3
GEO_GRIM_003|Skamstein|grimholt|Grimholt|2
GEO_GRIM_004|Járnmunn|grimholt|Grimholt|1
GEO_GRIM_005|Slagfell|grimholt|Grimholt|1
GEO_GRIM_006|Járnhryggr|grimholt|Grimholt|2
GEO_GRIM_007|Varðhaugr|grimholt|Grimholt|4
GEO_GRIM_008|Rauðvatn Ford|grimholt|Grimholt|3
GEO_GRIM_009|Brunnastaðr|grimholt|Grimholt|5
GEO_GRIM_010|Dómvǫllr|grimholt|Grimholt|1
GEO_GRIM_011|Sveigdir's Folly|grimholt|Grimholt|4
GEO_GRIM_012|Flóttamannahellir|grimholt|Grimholt|5
GEO_GRIM_013|Kolgrímr's Notch|grimholt|Grimholt|6
GEO_GRIM_014|Þrívegr|grimholt|Grimholt|2
GEO_GRIM_015|Hrímvarða|grimholt|Grimholt|3
GEO_GRIM_016|Bóndasól|grimholt|Grimholt|2
GEO_GRIM_017|Rauðvað|grimholt|Grimholt|3
GEO_GRIM_018|Varghaugr|grimholt|Grimholt|4
GEO_GRIM_019|Blóðstalli|grimholt|Grimholt|5
GEO_ICE_001|Svartvatnssteinn|ice|Bleakwater|2
GEO_ICE_002|Kaldrvatn|ice|Bleakwater|3
GEO_ICE_003|Ísbuð|ice|Icebreak|1
GEO_ICE_004|Svellsteininn|ice|Icebreak|3
GEO_ICE_005|Helbrannr|ice|Icebreak|4
GEO_ICE_006|Jǫkullhellir|ice|Icebreak|5
GEO_ICE_007|Ísbrú|ice|Icebreak|5
GEO_ICE_008|Forngarðr|ice|Icebreak|7
GEO_ICE_009|Jǫkullsundr|ice|Icebreak|8
GEO_ICE_010|Helvörðr|ice|Icebreak|9
GEO_ICE_011|Norðrljósafjall|ice|Icebreak|10
GEO_ICE_012|Helgrind|ice|Icebreak|12
GEO_ICE_013|Hélafoss|ice|Icebreak|4
GEO_ICE_014|Frystholm|ice|Bleakwater|3
GEO_ICE_015|Fonnbýli|ice|Icebreak|5
GEO_ICE_016|Dauðaaltari|ice|Bleakwater|6
GEO_MOOR_001|The Niðsteinar Circle|moor|Thornwall|2
GEO_MOOR_002|Heiðr-Steinn|moor|Thornwall|1
GEO_MOOR_003|The Drowned Pillars|moor|Moor's End|1
GEO_MOOR_004|Mýrr-Vatn|moor|Thornwall|3
GEO_MOOR_005|The Quaking Field|moor|Moor's End|2
GEO_MOOR_006|Thornwall Peat-Hags|moor|Thornwall|1
GEO_MOOR_007|Mosi-Vegr Crossroads|moor|Thornwall|2
GEO_MOOR_008|The Niðing Pool|moor|Thornwall|2
GEO_MOOR_009|Ketill's Croft|moor|Moor's End|1
GEO_MOOR_010|The Watcher's Mound|moor|Thornwall|3
GEO_MOOR_011|The Mosi-Brú|moor|Thornwall|2
GEO_MOOR_012|Fenwalker's Bothy|moor|Thornwall|3
GEO_MOOR_013|The Thornwall Marches|moor|Thornwall|0
GEO_MOOR_014|Fen-Greyja's Beck|moor|Moor's End|1
GEO_MOOR_015|Ash-Heiðr Ridge|moor|Ashen Reach|1
GEO_MOOR_016|Hǫfuðkollr|moor|Thornwall|3
GEO_MOOR_017|Krókamýrr|moor|Moor's End|2
GEO_MOOR_018|Svínvað|moor|Thornwall|4
GEO_MOOR_019|Stafrvörðr|moor|Moor's End|1
GEO_MTN_001|Tindrsteininn|mountain|Raven's Perch|3
GEO_MTN_002|Skarðvarðar|mountain|Raven's Perch|5
GEO_MTN_003|Eggjasteininn|mountain|Raven's Perch|2
GEO_MTN_004|Járnskarð|mountain|Raven's Perch|5
GEO_MTN_005|Kveldsskarð|mountain|Raven's Perch|7
GEO_MTN_006|Hrafnaskarð|mountain|Raven's Perch|1
GEO_MTN_007|Jǫkulkjaftr|mountain|Raven's Perch|6
GEO_MTN_008|Hamraból|mountain|Raven's Perch|4
GEO_MTN_009|Vindbrú|mountain|Raven's Perch|3
GEO_MTN_010|Niðahamr|mountain|Raven's Perch|2
GEO_MTN_011|Hornvörðr|mountain|Raven's Perch|4
GEO_MTN_012|Ísgilsfoss|mountain|Raven's Perch|3
GEO_MTN_013|Blóðegg|mountain|Raven's Perch|5
GEO_MTN_014|Skjóldalr Hut|mountain|Raven's Perch|6
GEO_MTN_015|Urðarbrekkur|mountain|Raven's Perch|4
GEO_MTN_016|Reykjalaug|mountain|Raven's Perch|5
GEO_MTN_017|Skeljabrún|mountain|Raven's Perch|3
GEO_MTN_018|Öxlahæð|mountain|Raven's Perch|2
GEO_MTN_019|Steinvað|mountain|Raven's Perch|4`;

    const settlementAliases = {
      stonebay: "Stonebay Hamlet",
      bleakwater: "Bleakwater Landing",
    };

    const anchorLookup = new Map();
    this.settlements.forEach((s) => {
      anchorLookup.set(this.normalizeName(s.name), s);
    });

    const regionVectors = {
      coastal: { q: -1.2, r: 0.35 },
      frostfjord: { q: -0.8, r: -0.6 },
      forest: { q: 0.35, r: 0.15 },
      deepholm: { q: 0.8, r: 0.3 },
      grimholt: { q: 1.05, r: 0.15 },
      moor: { q: 0.35, r: 1.05 },
      mountain: { q: 1.0, r: -0.7 },
      ice: { q: -0.05, r: -1.25 },
    };

    const occupancy = new Set(this.settlements.map((s) => `${s.q},${s.r}`));

    return atlasSummary
      .trim()
      .split("\n")
      .map((line, index) => {
        const [id, name, region, nearestRaw, distanceRaw] = line.split("|");
        if (!id || !name || !region || !nearestRaw) {
          return null;
        }

        const nearestNormalized = this.normalizeName(nearestRaw);
        const aliasName = settlementAliases[nearestNormalized];
        const anchor =
          (aliasName && anchorLookup.get(this.normalizeName(aliasName))) ||
          anchorLookup.get(nearestNormalized);

        if (!anchor) {
          return null;
        }

        const distanceHours = Math.max(0, Number(distanceRaw) || 0);
        const baseVector = regionVectors[region] || { q: 0.5, r: 0.2 };
        const baseAngle = Math.atan2(baseVector.r, baseVector.q);
        const spread = (this.hashString(id) - 0.5) * (Math.PI * 1.15);
        const angle = baseAngle + spread;

        const radius = Math.min(
          5.6,
          Math.max(0.35, distanceHours * 0.72 + 0.15),
        );
        const seededNudge = (this.hashString(`${id}:${index}`) - 0.5) * 0.45;

        const roughQ = Math.round(
          anchor.q + Math.cos(angle) * (radius + seededNudge),
        );
        const roughR = Math.round(
          anchor.r + Math.sin(angle) * (radius - seededNudge),
        );

        const clampedQ = Math.max(0, Math.min(14, roughQ));
        const clampedR = Math.max(0, Math.min(13, roughR));
        const placed = this.pickOpenHex(clampedQ, clampedR, occupancy, id);

        const rawType = this.inferLocationSubtype(name);
        const visualType = this.classifyLocationType(rawType);

        return {
          id,
          name,
          q: placed.q,
          r: placed.r,
          region,
          rawType,
          nearestSettlement: anchor.name,
          distanceHours,
          type: visualType,
          summary: `${region} • ${rawType.replace(/_/g, " ")} • near ${nearestRaw} (${distanceHours}h)`,
        };
      })
      .filter(Boolean);
  }

  buildSettlementFlavorMap() {
    const grouped = new Map();

    this.locations.forEach((location) => {
      const key = location.nearestSettlement;
      if (!grouped.has(key)) {
        grouped.set(key, []);
      }
      grouped.get(key).push(location);
    });

    const hazardTypes = new Set([
      "hazard",
      "bog",
      "battlefield",
      "execution_ground",
      "crevasse",
      "veil_zone",
      "avalanche_zone",
    ]);

    const flavor = new Map();

    this.settlements.forEach((settlement) => {
      const nearby = (grouped.get(settlement.name) || [])
        .slice()
        .sort((a, b) => a.distanceHours - b.distanceHours);

      if (!nearby.length) {
        flavor.set(
          settlement.name,
          `${settlement.strategic}. ${settlement.economic} keep the settlement alive through hard seasons.`,
        );
        return;
      }

      const notable = nearby.slice(0, 3).map((location) => location.name);
      const joined =
        notable.length === 1
          ? notable[0]
          : notable.length === 2
            ? `${notable[0]} and ${notable[1]}`
            : `${notable[0]}, ${notable[1]}, and ${notable[2]}`;

      const dangerousCount = nearby.filter(
        (location) =>
          location.type === "hazard" || hazardTypes.has(location.rawType),
      ).length;

      const secondSentence =
        dangerousCount >= Math.ceil(nearby.length / 3)
          ? "The surrounding routes are rich in old scars and dangerous ground, so even short journeys demand caution."
          : "These nearby sites feed trade, gossip, and old superstition, giving the settlement a constant pulse of travelers and stories.";

      flavor.set(
        settlement.name,
        `${settlement.name} sits within reach of ${joined}. ${secondSentence}`,
      );
    });

    return flavor;
  }

  getSettlementFlavor(settlementName) {
    return (
      this.settlementFlavor.get(settlementName) ||
      "The nearby wilds shape daily life here, and every road carries old history."
    );
  }

  showTooltip(screenX, screenY, title, content, type) {
    const tooltip = document.getElementById("locationTooltip");
    const mapArea = document.querySelector(".map-area");
    const rect = mapArea.getBoundingClientRect();

    let tooltipClass = "location-tooltip";
    if (type === "barrow") {
      tooltipClass += " barrow";
    } else if (type === "settlement") {
      tooltipClass += " settlement";
    }
    tooltip.className = tooltipClass;
    tooltip.querySelector(".title").textContent = title;
    tooltip.querySelector(".content").textContent = content;

    // Position tooltip near mouse, but keep it in bounds
    let top = screenY - 20;
    let left = screenX + 15;

    const tooltipWidth = 250;
    const tooltipHeight = 120;

    // Keep tooltip within map area
    if (left + tooltipWidth > rect.width) {
      left = screenX - tooltipWidth - 15;
    }
    if (top + tooltipHeight > rect.height) {
      top = screenY - tooltipHeight - 10;
    }

    tooltip.style.left = `${Math.max(5, left)}px`;
    tooltip.style.top = `${Math.max(5, top)}px`;
    tooltip.style.display = "block";
  }

  handleZoom(e) {
    e.preventDefault();
    const zoomFactor = e.deltaY > 0 ? 0.9 : 1.1;
    const newZoom = Math.max(
      this.minZoom,
      Math.min(this.maxZoom, this.zoom * zoomFactor),
    );

    // Zoom towards mouse position
    const rect = this.canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    this.offsetX = mouseX - (mouseX - this.offsetX) * (newZoom / this.zoom);
    this.offsetY = mouseY - (mouseY - this.offsetY) * (newZoom / this.zoom);
    this.zoom = newZoom;

    document.getElementById("zoomLevel").textContent =
      `${Math.round(this.zoom * 100)}%`;
    this.render();
  }

  handleResize() {
    this.canvas.width = this.canvas.offsetWidth || 1200;
    this.canvas.height = this.canvas.offsetHeight || 800;
    this.render();
  }

  // Hex coordinate conversion utilities
  axialToPixel(q, r) {
    const x = this.hexRadius * ((3 / 2) * q);
    const y = this.hexRadius * ((Math.sqrt(3) / 2) * q + Math.sqrt(3) * r);
    return { x, y };
  }

  pixelToAxial(x, y) {
    const q = ((2 / 3) * x) / this.hexRadius;
    const r = ((-1 / 3) * x + (Math.sqrt(3) / 3) * y) / this.hexRadius;
    return { q, r };
  }

  // Cube coordinate conversion for hex neighbors
  axialToCube(q, r) {
    return { x: q, y: -q - r, z: r };
  }

  centerView() {
    // Find center of all settlements
    const avgQ =
      this.settlements.reduce((sum, s) => sum + s.q, 0) /
      this.settlements.length;
    const avgR =
      this.settlements.reduce((sum, s) => sum + s.r, 0) /
      this.settlements.length;

    const centerPos = this.axialToPixel(avgQ, avgR);
    this.offsetX = this.canvas.width / 2 - centerPos.x * this.zoom;
    this.offsetY = this.canvas.height / 2 - centerPos.y * this.zoom;
  }

  render() {
    this.ctx.fillStyle = "linear-gradient(135deg, #1a2a3a 0%, #0a1a2a 100%)";
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

    this.ctx.save();
    this.ctx.translate(this.offsetX, this.offsetY);
    this.ctx.scale(this.zoom, this.zoom);

    // Draw hexagon grid
    this.drawHexGrid();

    // Draw roads (with curve support)
    this.drawRoads();

    // Draw interesting locations
    if (this.layers.locations) {
      this.drawLocations();
    }

    // Draw barrows (spoiler-protected layer)
    if (this.layers.barrows) {
      this.drawBarrows();
    }

    // Draw settlements (on top of other layers)
    this.drawSettlements();

    this.ctx.restore();
  }

  drawHexGrid() {
    // Calculate visible hex range (with extended padding to fill corners)
    // Q direction extends further due to hexagon width (1.5 * hexRadius spacing)
    // Use generous padding to ensure corner coverage at all zoom levels
    const minQ =
      Math.floor(-this.offsetX / this.zoom / (this.hexRadius * 1.5)) - 20;
    const maxQ =
      Math.ceil(
        (-this.offsetX / this.zoom + this.canvas.width / this.zoom) /
          (this.hexRadius * 1.5),
      ) + 20;
    const minR = Math.floor(-this.offsetY / this.zoom / this.hexHeight) - 12;
    const maxR =
      Math.ceil(
        (-this.offsetY / this.zoom + this.canvas.height / this.zoom) /
          this.hexHeight,
      ) + 12;

    for (let q = minQ; q < maxQ; q++) {
      for (let r = minR; r < maxR; r++) {
        const terrain = this.getTerrainType(q, r);
        this.drawHex(q, r, terrain);
      }
    }
  }

  // Simplex-like 2D noise function (deterministic, seeded)
  noise2D(x, y, seed = 0) {
    // Improved Perlin-like noise using multiple octaves for natural clustering
    // Uses floor values to create smooth gradients between hex values
    const n =
      Math.sin(x * 12.9898 + y * 78.233 + seed * 43758.5453) * 43758.5453;
    return n - Math.floor(n);
  }

  // Multi-octave noise for more realistic terrain variation
  perlin2D(x, y, octaves = 4, seed = 0) {
    let value = 0;
    let amplitude = 1;
    let frequency = 1;
    let maxValue = 0;

    for (let i = 0; i < octaves; i++) {
      value += this.noise2D(x * frequency, y * frequency, seed + i) * amplitude;
      maxValue += amplitude;
      amplitude *= 0.5;
      frequency *= 2;
    }

    return value / maxValue;
  }

  // Calculate elevation-like value for a hex based on noise
  getHexElevation(q, r) {
    const key = `${q},${r}`;
    if (this.elevationCache.has(key)) {
      return this.elevationCache.get(key);
    }

    // Multiple noise layers create varied terrain
    const baseNoise = this.perlin2D(q * 0.5, r * 0.5, 3, 12345);
    const detailNoise = this.perlin2D(q * 1.5, r * 1.5, 2, 54321);
    const ridgeNoise = this.perlin2D(q * 0.3, r * 0.3, 2, 99999);

    // Combine layers: base terrain shape + detail variation + ridge accentuation
    let elevation =
      baseNoise * 0.6 + detailNoise * 0.3 + Math.abs(ridgeNoise - 0.5) * 0.1;

    // Add latitude gradient: higher terrain in north (r < center), lower in south
    // This creates a realistic north-to-south elevation trend
    const latitudeInfluence = (7 - r) / 14; // 7 is approx center (0-14 range)
    elevation += latitudeInfluence * 0.15;

    // Add longitude gradient: coastal zones are lower, interior can be higher
    const distanceFromWest = Math.min(q / 3, 1); // Normalize 0-1
    const distanceFromEast = Math.min((15 - q) / 3, 1);
    const coastalZone = Math.min(distanceFromWest, distanceFromEast);
    elevation -= (1 - coastalZone) * 0.2; // Coastal areas more depressed

    elevation = Math.max(0, Math.min(1, elevation)); // Clamp to 0-1

    this.elevationCache.set(key, elevation);
    return elevation;
  }

  // Determine terrain type for a hex based on elevation and position
  getTerrainType(q, r) {
    const key = `${q},${r}`;
    if (this.terrainCache.has(key)) {
      return this.terrainCache.get(key);
    }

    let terrain = "moor"; // default

    // NORTHERN ICE-REACH: Frozen far north (r <= 1)
    if (r <= 1) {
      terrain = "ice";
    }
    // WESTERN FJORD COAST: q <= 3 (west edge has coast/fjords)
    else if (q <= 3) {
      const elevation = this.getHexElevation(q, r);
      if (elevation < 0.3) {
        terrain = "coast";
      } else if (elevation < 0.5) {
        terrain = "moor"; // Coastal hills
      } else {
        terrain = "mountain"; // Fjord walls
      }
    }
    // EASTERN MOUNTAINS: High elevation on east side (q >= 11)
    else if (q >= 11) {
      const elevation = this.getHexElevation(q, r);
      if (elevation > 0.65) {
        terrain = "mountain";
      } else if (elevation > 0.5) {
        terrain = "moor"; // Mountain foothills
      } else {
        terrain = "forest";
      }
    }
    // INTERIOR FOREST & BOG: Central regions (q between 4-10)
    else {
      const elevation = this.getHexElevation(q, r);

      // High elevation = mountains or exposed moorland
      if (elevation > 0.7) {
        terrain = "mountain";
      }
      // Mid-high elevation = moorland/exposed areas
      else if (elevation > 0.55) {
        terrain = "moor";
      }
      // Mid elevation = forest (protected valleys)
      else if (elevation > 0.35) {
        // Check for bog tendency: southern regions + lower elevation
        if (r > 9 && elevation < 0.45) {
          terrain = "bog";
        } else {
          terrain = "forest";
        }
      }
      // Low elevation = bog/marsh (naturally wet areas)
      else {
        terrain = "bog";
      }
    }

    this.terrainCache.set(key, terrain);
    return terrain;
  }

  drawHex(q, r, terrain) {
    const pos = this.axialToPixel(q, r);
    const x = pos.x;
    const y = pos.y;

    // Hex vertices
    const hexPoints = [];
    for (let i = 0; i < 6; i++) {
      const angle = (i * Math.PI) / 3;
      hexPoints.push({
        x: x + this.hexRadius * Math.cos(angle),
        y: y + this.hexRadius * Math.sin(angle),
      });
    }

    // Draw hex
    this.ctx.fillStyle = this.terrainTypes[terrain].color;
    this.ctx.beginPath();
    this.ctx.moveTo(hexPoints[0].x, hexPoints[0].y);
    for (let i = 1; i < 6; i++) {
      this.ctx.lineTo(hexPoints[i].x, hexPoints[i].y);
    }
    this.ctx.closePath();
    this.ctx.fill();

    // Hex border
    this.ctx.strokeStyle = "#444";
    this.ctx.lineWidth = 1;
    this.ctx.stroke();
  }

  getHexNeighbors(q, r) {
    const directions = [
      [1, 0],
      [1, -1],
      [0, -1],
      [-1, 0],
      [-1, 1],
      [0, 1],
    ];

    return directions
      .map(([dq, dr]) => [q + dq, r + dr])
      .filter(([nq, nr]) => nq >= 0 && nq <= 14 && nr >= 0 && nr <= 13);
  }

  axialDistance(q1, r1, q2, r2) {
    return (
      (Math.abs(q1 - q2) + Math.abs(r1 - r2) + Math.abs(q1 + r1 - (q2 + r2))) /
      2
    );
  }

  getTerrainTravelCost(q, r) {
    const terrain = this.getTerrainType(q, r);
    const costByTerrain = {
      forest: 1.0,
      coast: 1.2,
      moor: 1.35,
      bog: 2.1,
      mountain: 3.2,
      ice: 4.0,
    };
    return costByTerrain[terrain] || 1.6;
  }

  // Terrain-aware A* pathfinding for realistic overland roads.
  findPath(startQ, startR, endQ, endR) {
    const startKey = `${startQ},${startR}`;
    const goalKey = `${endQ},${endR}`;

    const open = new Set([startKey]);
    const cameFrom = new Map();
    const gScore = new Map([[startKey, 0]]);
    const fScore = new Map([
      [startKey, this.axialDistance(startQ, startR, endQ, endR)],
    ]);

    const nodeFromKey = (key) => {
      const [q, r] = key.split(",").map(Number);
      return { q, r };
    };

    while (open.size > 0) {
      let currentKey = null;
      let bestF = Infinity;
      for (const key of open) {
        const f = fScore.get(key) ?? Infinity;
        if (f < bestF) {
          bestF = f;
          currentKey = key;
        }
      }

      if (currentKey === goalKey) {
        const path = [];
        let cursor = currentKey;
        while (cursor) {
          const { q, r } = nodeFromKey(cursor);
          path.push([q, r]);
          cursor = cameFrom.get(cursor);
        }
        return path.reverse();
      }

      open.delete(currentKey);
      const { q: cq, r: cr } = nodeFromKey(currentKey);

      for (const [nq, nr] of this.getHexNeighbors(cq, cr)) {
        const neighborKey = `${nq},${nr}`;
        const tentativeG =
          (gScore.get(currentKey) ?? Infinity) +
          this.getTerrainTravelCost(nq, nr);

        if (tentativeG < (gScore.get(neighborKey) ?? Infinity)) {
          cameFrom.set(neighborKey, currentKey);
          gScore.set(neighborKey, tentativeG);
          fScore.set(
            neighborKey,
            tentativeG + this.axialDistance(nq, nr, endQ, endR),
          );
          open.add(neighborKey);
        }
      }
    }

    // Fallback if A* fails for any reason.
    return [
      [startQ, startR],
      [endQ, endR],
    ];
  }

  // Draw terrain-routed polyline between settlement hexes.
  drawRoadPath(hexPath, color) {
    if (hexPath.length < 2) return;

    const points = hexPath.map(([q, r]) => this.axialToPixel(q, r));

    this.ctx.strokeStyle = color;
    this.ctx.globalAlpha = 0.6;
    this.ctx.lineWidth = 2.5;
    this.ctx.lineCap = "round";
    this.ctx.lineJoin = "round";

    this.ctx.beginPath();
    this.ctx.moveTo(points[0].x, points[0].y);
    for (let i = 1; i < points.length; i++) {
      this.ctx.lineTo(points[i].x, points[i].y);
    }
    this.ctx.stroke();

    this.ctx.globalAlpha = 1;
    this.ctx.lineWidth = 1;
  }

  drawRoads() {
    for (let road of this.roads) {
      const fromSettlement = this.settlements.find((s) => s.name === road.from);
      const toSettlement = this.settlements.find((s) => s.name === road.to);

      if (fromSettlement && toSettlement) {
        // Find terrain-aware path
        const hexPath = this.findPath(
          fromSettlement.q,
          fromSettlement.r,
          toSettlement.q,
          toSettlement.r,
        );

        // Draw terrain-routed road
        this.drawRoadPath(hexPath, road.color);
      }
    }
  }

  drawSettlements() {
    for (let settlement of this.settlements) {
      const pos = this.getMarkerPosition(
        settlement.q,
        settlement.r,
        "settlement",
        settlement.name,
      );

      // Handle mountain passes separately (as triangle markers)
      if (settlement.isPass) {
        // Pass marker: triangle
        const triangleSize = 10;
        this.ctx.fillStyle = "#ff00ff"; // Magenta for passes
        this.ctx.beginPath();
        this.ctx.moveTo(pos.x, pos.y - triangleSize);
        this.ctx.lineTo(pos.x + triangleSize, pos.y + triangleSize);
        this.ctx.lineTo(pos.x - triangleSize, pos.y + triangleSize);
        this.ctx.closePath();
        this.ctx.fill();

        // Border
        this.ctx.strokeStyle = "#333";
        this.ctx.lineWidth = 2;
        this.ctx.stroke();

        // Name label at higher zoom
        if (this.zoom >= 0.8) {
          this.ctx.fillStyle = "#000";
          this.ctx.font = "bold 9px Arial";
          this.ctx.textAlign = "center";
          this.ctx.textBaseline = "top";
          this.ctx.fillText(settlement.name, pos.x, pos.y + 15);
        }
        continue;
      }

      // Regular settlements: circles
      let radius = 10;
      if (settlement.size === "Small Town") radius = 14;
      else if (settlement.size === "Large Village") radius = 12;
      else if (settlement.size === "Hamlet") radius = 7;

      // Outer ring (selection indicator)
      if (
        this.selectedSettlement &&
        this.selectedSettlement.name === settlement.name
      ) {
        this.ctx.fillStyle = "#00ff00";
        this.ctx.beginPath();
        this.ctx.arc(pos.x, pos.y, radius + 8, 0, Math.PI * 2);
        this.ctx.fill();
      }

      // Settlement circle
      this.ctx.fillStyle = "#ffaa00";
      this.ctx.beginPath();
      this.ctx.arc(pos.x, pos.y, radius, 0, Math.PI * 2);
      this.ctx.fill();

      // Border
      this.ctx.strokeStyle = "#333";
      this.ctx.lineWidth = 2;
      this.ctx.stroke();

      // Name label (only at certain zoom levels)
      if (this.zoom >= 0.8) {
        this.ctx.fillStyle = "#000";
        this.ctx.font = "bold 10px Arial";
        this.ctx.textAlign = "center";
        this.ctx.textBaseline = "middle";
        this.ctx.fillText(settlement.name.split(" ")[0], pos.x, pos.y);
      }
    }
  }

  drawBarrows() {
    // Draw barrow markers (spoiler layer - hidden by default)
    for (let barrow of this.barrows) {
      const pos = this.getMarkerPosition(
        barrow.q,
        barrow.r,
        "barrow",
        barrow.code,
      );
      const radius = 7;

      // Barrow marker: red/dark circle with X
      this.ctx.fillStyle = "#8b0000"; // Dark red
      this.ctx.beginPath();
      this.ctx.arc(pos.x, pos.y, radius, 0, Math.PI * 2);
      this.ctx.fill();

      // X symbol for barrow (crossbones)
      this.ctx.strokeStyle = "#cccccc";
      this.ctx.lineWidth = 2;
      this.ctx.beginPath();
      this.ctx.moveTo(pos.x - 5, pos.y - 5);
      this.ctx.lineTo(pos.x + 5, pos.y + 5);
      this.ctx.moveTo(pos.x + 5, pos.y - 5);
      this.ctx.lineTo(pos.x - 5, pos.y + 5);
      this.ctx.stroke();

      // Border
      this.ctx.strokeStyle = "#333";
      this.ctx.lineWidth = 1;
      this.ctx.stroke();

      // Name label at higher zoom
      if (this.zoom >= 1.2) {
        this.ctx.fillStyle = "#ccc";
        this.ctx.font = "bold 8px Arial";
        this.ctx.textAlign = "center";
        this.ctx.textBaseline = "top";
        this.ctx.fillText(barrow.code, pos.x, pos.y + 10);
      }
    }
  }

  drawLocations() {
    // Draw interesting locations (landmarks, ruins, notable sites)
    for (let location of this.locations) {
      const pos = this.getMarkerPosition(
        location.q,
        location.r,
        "location",
        location.id || location.name,
      );

      // Render by location type
      if (location.type === "pass") {
        // Pass marker: triangle (same as mountain passes)
        const triangleSize = 8;
        this.ctx.fillStyle = "#ffaa00"; // Orange for location passes
        this.ctx.beginPath();
        this.ctx.moveTo(pos.x, pos.y - triangleSize);
        this.ctx.lineTo(pos.x + triangleSize, pos.y + triangleSize);
        this.ctx.lineTo(pos.x - triangleSize, pos.y + triangleSize);
        this.ctx.closePath();
        this.ctx.fill();
        this.ctx.strokeStyle = "#333";
        this.ctx.lineWidth = 1;
        this.ctx.stroke();
      } else if (location.type === "landmark") {
        // Landmark: star
        this.ctx.fillStyle = "#ffff00"; // Yellow
        this.drawStar(pos.x, pos.y, 6, 5, 3);
        this.ctx.fillStyle = "#ffff00";
        this.ctx.fill();
      } else if (location.type === "facility") {
        // Facility: square
        this.ctx.fillStyle = "#aabbff"; // Light blue
        this.ctx.fillRect(pos.x - 5, pos.y - 5, 10, 10);
        this.ctx.strokeStyle = "#333";
        this.ctx.lineWidth = 1;
        this.ctx.stroke();
      } else if (location.type === "hazard") {
        // Hazard: skull/warning
        this.ctx.fillStyle = "#ff3333"; // Red
        this.ctx.beginPath();
        this.ctx.arc(pos.x, pos.y, 5, 0, Math.PI * 2);
        this.ctx.fill();
        this.ctx.strokeStyle = "#000";
        this.ctx.lineWidth = 1;
        this.ctx.stroke();
      } else {
        // Default: circle
        this.ctx.fillStyle = "#aaa";
        this.ctx.beginPath();
        this.ctx.arc(pos.x, pos.y, 4, 0, Math.PI * 2);
        this.ctx.fill();
      }

      // Name label at higher zoom
      if (this.zoom >= 1.0) {
        this.ctx.fillStyle = "#bbb";
        this.ctx.font = "8px Arial";
        this.ctx.textAlign = "center";
        this.ctx.textBaseline = "top";
        this.ctx.fillText(location.name, pos.x, pos.y + 8);
      }
    }
  }

  drawStar(cx, cy, spikes, outerRadius, innerRadius) {
    // Helper to draw star shape
    let rot = (Math.PI / 2) * 3;
    let step = Math.PI / spikes;

    this.ctx.beginPath();
    this.ctx.moveTo(cx, cy - outerRadius);
    for (let i = 0; i < spikes; i++) {
      this.ctx.lineTo(
        cx + Math.cos(rot) * outerRadius,
        cy + Math.sin(rot) * outerRadius,
      );
      rot += step;
      this.ctx.lineTo(
        cx + Math.cos(rot) * innerRadius,
        cy + Math.sin(rot) * innerRadius,
      );
      rot += step;
    }
    this.ctx.lineTo(cx, cy - outerRadius);
    this.ctx.closePath();
  }

  toggleBarrowLayer() {
    // Show spoiler warning if trying to enable barrows for first time
    if (!this.layers.barrows && !this.barrowsSpoilerAcknowledged) {
      this.showSpoilerWarning();
    } else {
      this.layers.barrows = !this.layers.barrows;
      this.render();
      this.updateLayerUI();
    }
  }

  showSpoilerWarning() {
    const modal = document.getElementById("spoilerModal");
    if (modal) {
      modal.style.display = "flex";
    }
  }

  acceptSpoilers() {
    this.barrowsSpoilerAcknowledged = true;
    this.layers.barrows = true;
    this.render();
    this.updateLayerUI();
    const modal = document.getElementById("spoilerModal");
    if (modal) {
      modal.style.display = "none";
    }
  }

  rejectSpoilers() {
    this.layers.barrows = false;
    this.updateLayerUI();
    const modal = document.getElementById("spoilerModal");
    if (modal) {
      modal.style.display = "none";
    }
  }

  updateLayerUI() {
    // Update checkbox states in sidebar
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach((checkbox) => {
      const layer = checkbox.id.replace("show", "").toLowerCase();
      if (this.layers.hasOwnProperty(layer)) {
        checkbox.checked = this.layers[layer];
      }
    });
  }
}

// Global state
let hexMap;

function initMap() {
  hexMap = new HexMap("mapCanvas");
}

function zoomIn() {
  hexMap.zoom = Math.min(hexMap.maxZoom, hexMap.zoom * 1.2);
  document.getElementById("zoomLevel").textContent =
    `${Math.round(hexMap.zoom * 100)}%`;
  hexMap.render();
}

function zoomOut() {
  hexMap.zoom = Math.max(hexMap.minZoom, hexMap.zoom / 1.2);
  document.getElementById("zoomLevel").textContent =
    `${Math.round(hexMap.zoom * 100)}%`;
  hexMap.render();
}

function resetView() {
  hexMap.zoom = 1;
  hexMap.centerView();
  document.getElementById("zoomLevel").textContent = "100%";
  hexMap.selectedSettlement = null;
  document
    .querySelectorAll(".settlement-item")
    .forEach((item) => item.classList.remove("selected"));
  hexMap.render();
}

// Initialize on page load
window.addEventListener("DOMContentLoaded", () => {
  initMap();
});
