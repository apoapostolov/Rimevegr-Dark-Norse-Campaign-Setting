import { useEffect, useMemo, useState } from "react";
import { buildChroniclePresentation, buildDayBriefPresentation } from "./content";

type TimelineCursor = {
  year: number;
  day_of_year: number;
  season: string;
  branch: string;
  transaction_index: number;
};

type FeedFacetItem = {
  label: string;
  count: number;
};

type FeedDateFacet = {
  year: number;
  day: number;
  label: string;
  count: number;
};

type FeedFacetsResponse = {
  dates: FeedDateFacet[];
  categories: FeedFacetItem[];
  entities: FeedFacetItem[];
};

type FeedPost = {
  id: string;
  source_type: string;
  simulated_year: number;
  simulated_day: number;
  simulated_label: string;
  cadence?: string;
  span_start_year?: number | null;
  span_start_day?: number | null;
  span_end_year?: number | null;
  span_end_day?: number | null;
  title: string;
  category: string;
  tags: string[];
  entities: string[];
  summary: string;
  narrative: string[];
  technical: string[];
  provenance?: string | null;
};

type FeedResponse = {
  items: FeedPost[];
};

type TimeAdvanceResponse = {
  to_cursor: TimelineCursor;
};

type BrowseDate = {
  year: number;
  month: number;
  day: number;
};

type CalendarSeason = {
  label: string;
  startMonth: number;
};

const API_BASE = "http://127.0.0.1:8000/api";
const MONTH_LABELS = [
  "Frostwake",
  "Rimeblood",
  "Veilthin",
  "Ashfall",
  "Ironmoon",
  "Wolfmoot",
  "Barrowrise",
  "Longnight",
  "Hearthstar",
  "Bloodtide",
  "Skaldsong",
  "Yuledeep",
];
const WEEKDAY_LABELS = [
  "Má",
  "Ty",
  "Óð",
  "Þó",
  "Fr",
  "La",
  "Su",
];
const SEASONS: CalendarSeason[] = [
  { label: "Long Summer", startMonth: 1 },
  { label: "Early Dark", startMonth: 4 },
  { label: "Deep Dark", startMonth: 7 },
  { label: "Late Dark", startMonth: 10 },
];
const TRANSPORT_STEPS = [
  { unit: "season", label: "Season", arrows: "⟪⟪⟪⟪⟪" },
  { unit: "month", label: "Month", arrows: "⟪⟪⟪⟪" },
  { unit: "week", label: "Week", arrows: "⟪⟪⟪" },
  { unit: "day", label: "Day", arrows: "⟪⟪" },
] as const;

function shiftYearMonthMonthDay(date: BrowseDate, deltaMonths: number): BrowseDate {
  const totalMonths = date.year * 12 + (date.month - 1) + deltaMonths;
  const nextYear = Math.floor(totalMonths / 12);
  const nextMonth = ((totalMonths % 12) + 12) % 12 + 1;
  return {
    year: nextYear,
    month: nextMonth,
    day: Math.min(date.day, 30),
  };
}

function shiftBrowseDate(date: BrowseDate, deltaDays: number): BrowseDate {
  const totalDays = (date.year *360) + ((date.month - 1)* 30) + (date.day - 1) + deltaDays;
  const nextYear = Math.floor(totalDays / 360);
  const remainingDays = ((totalDays % 360) + 360) % 360;
  const nextMonth = Math.floor(remainingDays / 30) + 1;
  const nextDay = (remainingDays % 30) + 1;
  return {
    year: nextYear,
    month: nextMonth,
    day: nextDay,
  };
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

function dayOfYearToBrowseDate(year: number, dayOfYear: number): BrowseDate {
  const normalizedDay = clamp(dayOfYear, 1, 360);
  const month = Math.floor((normalizedDay - 1) / 30) + 1;
  const day = ((normalizedDay - 1) % 30) + 1;
  return { year, month, day };
}

function browseDateToDayOfYear(date: BrowseDate): number {
  return ((date.month - 1) * 30) + date.day;
}

function browseDateLabel(date: BrowseDate): string {
  return `${MONTH_LABELS[date.month - 1]} ${date.day}, Y${date.year}`;
}

function seasonForMonth(month: number): CalendarSeason {
  return SEASONS[Math.floor((month - 1) / 3)];
}

function ordinalDay(year: number, day: number): number {
  return (year * 360) + (day - 1);
}

function postSpan(post: FeedPost): {
  startYear: number;
  startDay: number;
  endYear: number;
  endDay: number;
} {
  return {
    startYear: post.span_start_year ?? post.simulated_year,
    startDay: post.span_start_day ?? post.simulated_day,
    endYear: post.span_end_year ?? post.simulated_year,
    endDay: post.span_end_day ?? post.simulated_day,
  };
}

function postAppliesToDate(post: FeedPost, year: number, day: number): boolean {
  const span = postSpan(post);
  const target = ordinalDay(year, day);
  return (
    ordinalDay(span.startYear, span.startDay) <= target &&
    target <= ordinalDay(span.endYear, span.endDay)
  );
}

function postAppliesToMonth(post: FeedPost, year: number, month: number): boolean {
  const span = postSpan(post);
  const monthStart = ordinalDay(year, ((month - 1) * 30) + 1);
  const monthEnd = ordinalDay(year, month * 30);
  return (
    ordinalDay(span.startYear, span.startDay) <= monthEnd &&
    ordinalDay(span.endYear, span.endDay) >= monthStart
  );
}

function cadenceLabel(cadence?: string): string {
  switch (cadence) {
    case "week":
      return "Weekly post";
    case "month":
      return "Monthly post";
    case "season":
      return "Seasonal post";
    case "day":
      return "Daily post";
    default:
      return cadence ? `${cadence} post` : "Simulation post";
  }
}

async function fetchJson<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, init);
  if (!response.ok) {
    const body = await response.text();
    throw new Error(`${response.status} ${response.statusText}${body ?` - ${body}`: ""}`);
  }
  return response.json() as Promise<T>;
}

function formatMetricLines(lines: string[]): string[] {
  return lines.map((line) => line.trim()).filter(Boolean);
}

function App() {
  const [worldCursor, setWorldCursor] = useState<TimelineCursor | null>(null);
  const [browseDate, setBrowseDate] = useState<BrowseDate>({ year: 312, month: 1, day: 1 });
  const [facets, setFacets] = useState<FeedFacetsResponse | null>(null);
  const [yearItems, setYearItems] = useState<FeedPost[]>([]);
  const [loadingFeed, setLoadingFeed] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showTechnical, setShowTechnical] = useState(false);
  const [activeCategories, setActiveCategories] = useState<string[]>([]);
  const [activeEntities, setActiveEntities] = useState<string[]>([]);
  const [advancing, setAdvancing] = useState<string | null>(null);

  const availableYears = useMemo(() => {
    const values = new Map<number, number>();
    for (const item of facets?.dates ?? []) {
      values.set(item.year, (values.get(item.year) ?? 0) + item.count);
    }
    return Array.from(values.entries())
      .sort((left, right) => right[0] - left[0])
      .map(([year, count]) => ({ year, count }));
  }, [facets]);

  const categoryOptions = facets?.categories ?? [];
  const entityOptions = facets?.entities ?? [];

  const filteredYearItems = useMemo(() => {
    const categorySet = new Set(activeCategories.map((item) => item.toLowerCase()));
    const entitySet = new Set(activeEntities.map((item) => item.toLowerCase()));
    return yearItems.filter((post) => {
      const categoryMatch =
        categorySet.size === 0 || categorySet.has(post.category.toLowerCase());
      const entityMatch =
        entitySet.size === 0 ||
        post.entities.some((entity) => entitySet.has(entity.toLowerCase()));
      return categoryMatch && entityMatch;
    });
  }, [activeCategories, activeEntities, yearItems]);

  const selectedDayOfYear = browseDateToDayOfYear(browseDate);
  const browseDayItems = useMemo(
    () => filteredYearItems.filter((post) => postAppliesToDate(post, browseDate.year, selectedDayOfYear)),
    [browseDate.year, filteredYearItems, selectedDayOfYear],
  );

  const monthItems = useMemo(
    () => filteredYearItems.filter((post) => postAppliesToMonth(post, browseDate.year, browseDate.month)),
    [browseDate.month, browseDate.year, filteredYearItems],
  );

  const monthCounts = useMemo(() => {
    const counts = new Map<number, number>();
    for (const post of monthItems) {
      const span = postSpan(post);
      const start = ordinalDay(span.startYear, span.startDay);
      const end = ordinalDay(span.endYear, span.endDay);
      for (let cursor = start; cursor <= end; cursor += 1) {
        const year = Math.floor(cursor / 360);
        if (year !== browseDate.year) {
          continue;
        }
        const day = (cursor % 360) + 1;
        const month = Math.floor((day - 1) / 30) + 1;
        if (month !== browseDate.month) {
          continue;
        }
        counts.set(day, (counts.get(day) ?? 0) + 1);
      }
    }
    return counts;
  }, [browseDate.month, browseDate.year, monthItems]);

  const selectedYearLabel = `Y${browseDate.year}`;
  const selectedSeason = seasonForMonth(browseDate.month);
  const monthName = MONTH_LABELS[browseDate.month - 1];
  const selectedDayItemsCount = browseDayItems.length;

  useEffect(() => {
    let active = true;
    async function loadInitialState() {
      try {
        const [cursor, facetPayload] = await Promise.all([
          fetchJson<TimelineCursor>(`${API_BASE}/time/cursor`),
          fetchJson<FeedFacetsResponse>(`${API_BASE}/feed/facets`),
        ]);
        if (!active) {
          return;
        }
        setWorldCursor(cursor);
        setBrowseDate(dayOfYearToBrowseDate(cursor.year, cursor.day_of_year));
        setFacets(facetPayload);
        if (activeCategories.length === 0) {
          setActiveCategories(facetPayload.categories.map((item) => item.label));
        }
        if (activeEntities.length === 0) {
          setActiveEntities(facetPayload.entities.map((item) => item.label));
        }
      } catch (caught) {
        if (active) {
          setError(caught instanceof Error ? caught.message : String(caught));
        }
      }
    }

    void loadInitialState();
    return () => {
      active = false;
    };
    // Initial bootstrap only.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    let active = true;
    async function loadYearFeed() {
      if (!browseDate.year) {
        return;
      }
      try {
        setLoadingFeed(true);
        const query = new URLSearchParams({
          year: String(browseDate.year),
          limit: "1000",
        });
        const payload = await fetchJson<FeedResponse>(`${API_BASE}/feed?${query.toString()}`);
        if (active) {
          setYearItems(payload.items);
        }
      } catch (caught) {
        if (active) {
          setError(caught instanceof Error ? caught.message : String(caught));
        }
      } finally {
        if (active) {
          setLoadingFeed(false);
        }
      }
    }

    void loadYearFeed();
    return () => {
      active = false;
    };
  }, [browseDate.year]);

  async function refreshSidebarData() {
    const [cursor, facetPayload] = await Promise.all([
      fetchJson<TimelineCursor>(`${API_BASE}/time/cursor`),
      fetchJson<FeedFacetsResponse>(`${API_BASE}/feed/facets`),
    ]);
    setWorldCursor(cursor);
    setFacets(facetPayload);
  }

  async function advanceWorldTime(unit: "day" | "week" | "month" | "season", amount: number) {
    try {
      setAdvancing(`${unit}:${amount}`);
      const payload = await fetchJson<TimeAdvanceResponse>(`${API_BASE}/time/advance`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          unit,
          amount,
          dry_run: false,
        }),
      });
      setWorldCursor(payload.to_cursor);
      setBrowseDate(dayOfYearToBrowseDate(payload.to_cursor.year, payload.to_cursor.day_of_year));
      await refreshSidebarData();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught));
    } finally {
      setAdvancing(null);
    }
  }

  function toggleCategory(label: string) {
    setActiveCategories((current) =>
      current.includes(label)
        ? current.filter((item) => item !== label)
        : [...current, label].sort((left, right) => left.localeCompare(right)),
    );
  }

  function toggleEntity(label: string) {
    setActiveEntities((current) =>
      current.includes(label)
        ? current.filter((item) => item !== label)
        : [...current, label].sort((left, right) => left.localeCompare(right)),
    );
  }

  function cycleYear(delta: number) {
    setBrowseDate((current) => ({ ...current, year: current.year + delta }));
  }

  function cycleSeason(delta: number) {
    setBrowseDate((current) => shiftYearMonthMonthDay(current, delta * 3));
  }

  function cycleMonth(delta: number) {
    setBrowseDate((current) => shiftYearMonthMonthDay(current, delta));
  }

  const selectedYearFeed = useMemo(() => {
    return browseDayItems.slice().sort(
      (left, right) =>
        right.simulated_day - left.simulated_day ||
        right.simulated_year - left.simulated_year ||
        left.id.localeCompare(right.id),
    );
  }, [browseDayItems]);

  const visibleCount = browseDayItems.length;
  const dayBrief = buildDayBriefPresentation(browseDayItems, browseDateLabel(browseDate));

  return (
    <div className="chronicle-app">
      <header className="top-header">
        <div>
          <p className="kicker">Rimevegr Time Manager</p>
          <h1>Chronicle CMS</h1>
          <p className="header-copy">
            Simulation output becomes readable posts. The calendar picks the day, the
            transport bar moves the world, and the feed stays human first.
          </p>
        </div>
        <div className="header-state">
          <div>
            <span>World cursor</span>
            <strong>
              {worldCursor ? `D${worldCursor.day_of_year} Y${worldCursor.year}` : "Loading"}
            </strong>
          </div>
          <div>
            <span>Viewing</span>
            <strong>{browseDateLabel(browseDate)}</strong>
          </div>
          <div>
            <span>Visible posts</span>
            <strong>{visibleCount}</strong>
          </div>
          <div>
            <span>Technical layer</span>
            <strong>{showTechnical ? "Shown" : "Hidden"}</strong>
          </div>
        </div>
      </header>

      <section className="transport-bar" aria-label="World time transport">
        <div className="transport-side transport-side--left">
          {TRANSPORT_STEPS.map((step) => (
            <button
              key={`back-${step.unit}`}
              type="button"
              className="transport-button transport-button--back"
              disabled={advancing !== null}
              onClick={() => void advanceWorldTime(step.unit, -1)}
              aria-label={`Move back one ${step.unit}`}
            >
              <span className="transport-arrows">{step.arrows}</span>
              <span className="transport-label">{step.label}</span>
            </button>
          ))}
        </div>

        <button
          type="button"
          className="transport-center"
          onClick={() => {
            if (worldCursor) {
              setBrowseDate(dayOfYearToBrowseDate(worldCursor.year, worldCursor.day_of_year));
            }
          }}
        >
          <span className="transport-center__eyebrow">Current date</span>
          <span className="transport-center__date">
            {worldCursor ? `D${worldCursor.day_of_year} Y${worldCursor.year}` : "Loading"}
          </span>
          <span className="transport-center__season">
            {worldCursor ? worldCursor.season : "Holding the line"}
          </span>
        </button>

        <div className="transport-side transport-side--right">
          {TRANSPORT_STEPS.slice().reverse().map((step) => (
            <button
              key={`forward-${step.unit}`}
              type="button"
              className="transport-button transport-button--forward"
              disabled={advancing !== null}
              onClick={() => void advanceWorldTime(step.unit, 1)}
              aria-label={`Move forward one ${step.unit}`}
            >
              <span className="transport-label">{step.label}</span>
              <span className="transport-arrows">
                {step.arrows.replaceAll("⟪", "⟫")}
              </span>
            </button>
          ))}
        </div>
      </section>

      <main className="main-layout">
        <aside className="sidebar">
          <section className="sidebar-card calendar-shell">
            <div className="section-heading">
              <h2>Calendar</h2>
              <p>Choose the day the chronicle should show.</p>
            </div>

            <div className="calendar-controls">
              <div className="calendar-control-strip">
                <select
                  className="calendar-select calendar-select--year"
                  aria-label="Year"
                  value={browseDate.year}
                  onChange={(event) =>
                    setBrowseDate((current) => ({
                      ...current,
                      year: Number(event.target.value),
                    }))
                  }
                >
                  {availableYears.map((option) => (
                    <option key={option.year} value={option.year}>
                      Y{option.year}
                    </option>
                  ))}
                  {!availableYears.some((item) => item.year === browseDate.year) ? (
                    <option value={browseDate.year}>Y{browseDate.year}</option>
                  ) : null}
                </select>
                <select
                  className="calendar-select calendar-select--season"
                  aria-label="Season"
                  value={seasonForMonth(browseDate.month).label}
                  onChange={(event) => {
                    const season = SEASONS.find((item) => item.label === event.target.value);
                    if (season) {
                      setBrowseDate((current) => ({
                        ...current,
                        month: season.startMonth,
                        day: clamp(current.day, 1, 30),
                      }));
                    }
                  }}
                >
                  {SEASONS.map((season) => (
                    <option key={season.label} value={season.label}>
                      {season.label}
                    </option>
                  ))}
                </select>
                <select
                  className="calendar-select calendar-select--month"
                  aria-label="Month"
                  value={browseDate.month}
                  onChange={(event) =>
                    setBrowseDate((current) => ({
                      ...current,
                      month: Number(event.target.value),
                      day: clamp(current.day, 1, 30),
                    }))
                  }
                >
                  {MONTH_LABELS.map((label, index) => (
                    <option key={label} value={index + 1}>
                    {label}
                  </option>
                ))}
                </select>
              </div>
            </div>

            <div className="calendar-weekdays" aria-hidden="true">
              {WEEKDAY_LABELS.map((label) => (
                <span key={label}>{label}</span>
              ))}
            </div>

            <div className="calendar-grid" role="grid" aria-label="Month calendar">
              {Array.from({ length: 35 }, (_, index) => {
                const dayNumber = index + 1;
                if (dayNumber > 30) {
                  return <div key={`blank-${index}`} className="calendar-day calendar-day--blank" />;
                }
                const count = monthCounts.get(dayNumber) ?? 0;
                const selected = browseDate.day === dayNumber;
                const worldDate = worldCursor
                  ? dayOfYearToBrowseDate(worldCursor.year, worldCursor.day_of_year)
                  : null;
                const worldSelected =
                  worldDate !== null &&
                  worldCursor?.year === browseDate.year &&
                  worldDate.month === browseDate.month &&
                  worldDate.day === dayNumber;
                return (
                  <button
                    key={`day-${dayNumber}`}
                    type="button"
                    className={[
                      "calendar-day",
                      count > 0 ? "calendar-day--live" : "calendar-day--muted",
                      selected ? "calendar-day--selected" : "",
                      worldSelected ? "calendar-day--world" : "",
                    ]
                      .filter(Boolean)
                      .join(" ")}
                    onClick={() =>
                      setBrowseDate((current) => ({
                        ...current,
                        day: dayNumber,
                      }))
                    }
                  >
                    <span>{dayNumber}</span>
                    <small>{count > 0 ? `${count}` : "—"}</small>
                  </button>
                );
              })}
            </div>
          </section>

          <section className="sidebar-card">
            <div className="section-heading">
              <h2>Simulation tags</h2>
              <p>Primary filters from the simulated content type.</p>
            </div>
            <div className="filter-actions">
              <button type="button" onClick={() => setActiveCategories(categoryOptions.map((item) => item.label))}>
                All
              </button>
              <button type="button" onClick={() => setActiveCategories([])}>
                None
              </button>
            </div>
            <div className="filter-list">
              {categoryOptions.map((item) => (
                <button
                  key={item.label}
                  type="button"
                  className={`filter-chip ${activeCategories.includes(item.label) ? "active" : ""}`}
                  onClick={() => toggleCategory(item.label)}
                >
                  <strong>{item.label}</strong>
                  <span>{item.count}</span>
                </button>
              ))}
            </div>
          </section>

          <section className="sidebar-card">
            <div className="section-heading">
              <h2>Settlements and bands</h2>
              <p>Secondary tags that narrow the chronicle to a place or mercenary band.</p>
            </div>
            <div className="filter-actions">
              <button type="button" onClick={() => setActiveEntities(entityOptions.map((item) => item.label))}>
                All
              </button>
              <button type="button" onClick={() => setActiveEntities([])}>
                None
              </button>
            </div>
            <div className="filter-list">
              {entityOptions.map((item) => (
                <button
                  key={item.label}
                  type="button"
                  className={`filter-chip ${activeEntities.includes(item.label) ? "active" : ""}`}
                  onClick={() => toggleEntity(item.label)}
                >
                  <strong>{item.label}</strong>
                  <span>{item.count}</span>
                </button>
              ))}
            </div>
          </section>
        </aside>

        <section className="content-pane">
          <div className="content-header">
            <div>
              <h2>{browseDateLabel(browseDate)}</h2>
                <p className="content-state">
                  {loadingFeed
                    ? "Loading chronicle entries..."
                  : `${selectedDayItemsCount} ${selectedDayItemsCount === 1 ? "entry" : "entries"} for this date`}
                </p>
            </div>
            <div className="content-actions">
              <button type="button" onClick={() => setShowTechnical((current) => !current)}>
                {showTechnical ? "Hide technical" : "Show technical"}
              </button>
            </div>
          </div>

          {error ? <div className="error-banner">{error}</div> : null}

          <div className="day-brief-card">
            <div className="post-topline">
              <span className="post-eyebrow">{dayBrief.eyebrow}</span>
              <span className="post-date">{browseDateLabel(browseDate)}</span>
            </div>
            <div className="post-title-row">
              <h3>{dayBrief.title}</h3>
            </div>
            <p className="post-lead">{dayBrief.lead}</p>
            {dayBrief.flavor ? <p className="post-flavor">{dayBrief.flavor}</p> : null}
            <div className="post-body">
              <ul className="day-brief-points">
                {dayBrief.points.map((line) => (
                  <li key={`${browseDate.year}-${browseDate.month}-${browseDate.day}-${line}`}>{line}</li>
                ))}
              </ul>
            </div>
          </div>

          <div className="post-list">
            {selectedYearFeed.length > 0 ? (
              selectedYearFeed.map((post) => {
                const presentation = buildChroniclePresentation(post);
                const narrative = post.narrative.filter((line, index) => {
                  const normalized = line.trim();
                  if (!normalized) {
                    return false;
                  }
                  if (index === 0 && normalized === post.summary.trim()) {
                    return false;
                  }
                  return true;
                });
                const technical = formatMetricLines(post.technical);
                return (
                  <article key={post.id} className="post-card">
                    <div className="post-topline">
                      <span className="post-eyebrow">{presentation.eyebrow}</span>
                      <div className="post-topline-meta">
                        {post.cadence && post.cadence !== "day" ? (
                          <span className="post-cadence">{cadenceLabel(post.cadence)}</span>
                        ) : null}
                        <span className="post-date">{post.simulated_label}</span>
                      </div>
                    </div>
                    <div className="post-title-row">
                      <h3>{post.title}</h3>
                      <div className="post-tag-row">
                        <span className="post-category">{post.category}</span>
                        {post.entities.map((entity) => (
                          <span key={`${post.id}-${entity}`} className="entity-tag">
                            {entity}
                          </span>
                        ))}
                      </div>
                    </div>
                    <p className="post-lead">{presentation.lead}</p>
                    {presentation.flavor ? <p className="post-flavor">{presentation.flavor}</p> : null}
                    <div className="post-body">
                      <strong className="post-section-title">{presentation.narrativeHeading}</strong>
                      {narrative.map((line) => (
                        <p key={`${post.id}-${line}`}>{line}</p>
                      ))}
                    </div>
                    {showTechnical && technical.length > 0 ? (
                      <div className="post-technical">
                        <strong className="post-section-title">{presentation.technicalHeading}</strong>
                        {technical.map((line) => (
                          <p key={`${post.id}-${line}`}>{line}</p>
                        ))}
                        {post.provenance ? <p>Provenance: {post.provenance}</p> : null}
                      </div>
                    ) : null}
                  </article>
                );
              })
            ) : (
              <div className="empty-state">
                <h3>No chronicle entries for this day</h3>
                <p>
                  The month has entries, but this date does not. Pick a lit day in the
                  calendar grid to read the posts that were generated there.
                </p>
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
