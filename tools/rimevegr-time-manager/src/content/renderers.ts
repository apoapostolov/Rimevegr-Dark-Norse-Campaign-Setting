export type ChroniclePost = {
  source_type: string;
  category: string;
  title: string;
  summary: string;
  narrative: string[];
  technical: string[];
  tags: string[];
  entities: string[];
  simulated_label: string;
  simulated_year: number;
  simulated_day: number;
  provenance?: string | null;
};

export type ChroniclePresentation = {
  eyebrow: string;
  narrativeHeading: string;
  technicalHeading: string;
  lead: string;
  accent: string;
  flavor: string;
};

function firstMeaningfulLine(lines: string[]): string {
  return lines.map((line) => line.trim()).find(Boolean) ?? "";
}

function joinEntities(entities: string[]): string {
  return entities.filter(Boolean).join(" · ");
}

function makeGenericPresentation(post: ChroniclePost, eyebrow: string): ChroniclePresentation {
  return {
    eyebrow,
    narrativeHeading: "What happened",
    technicalHeading: "Technical layer",
    lead: post.summary,
    accent: post.category,
    flavor: joinEntities(post.entities),
  };
}

function buildWeatherPresentation(post: ChroniclePost): ChroniclePresentation {
  return {
    eyebrow: "Weather Chronicle",
    narrativeHeading: "What the land felt",
    technicalHeading: "Weather mechanics",
    lead: firstMeaningfulLine(post.narrative) || post.summary,
    accent: post.category,
    flavor: joinEntities(post.entities),
  };
}

function buildSettlementPresentation(post: ChroniclePost): ChroniclePresentation {
  return {
    eyebrow: "Settlement Dossier",
    narrativeHeading: "How the place reads",
    technicalHeading: "Settlement ledger",
    lead: firstMeaningfulLine(post.narrative) || post.summary,
    accent: post.category,
    flavor: joinEntities(post.entities),
  };
}

function buildAnimalPresentation(post: ChroniclePost): ChroniclePresentation {
  return {
    eyebrow: "Herd and Kennel Chronicle",
    narrativeHeading: "How the animals moved",
    technicalHeading: "Breeding ledger",
    lead: firstMeaningfulLine(post.narrative) || post.summary,
    accent: post.category,
    flavor: joinEntities(post.entities),
  };
}

function buildTransactionPresentation(post: ChroniclePost): ChroniclePresentation {
  return {
    eyebrow: "World Clock Ledger",
    narrativeHeading: "What the step changed",
    technicalHeading: "Replay journal",
    lead: firstMeaningfulLine(post.narrative) || post.summary,
    accent: post.category,
    flavor: post.simulated_label,
  };
}

function buildEventPresentation(post: ChroniclePost): ChroniclePresentation {
  return {
    eyebrow: `${post.category} Chronicle`,
    narrativeHeading: "How the world remembers it",
    technicalHeading: "Simulation notes",
    lead: firstMeaningfulLine(post.narrative) || post.summary,
    accent: post.category,
    flavor: joinEntities(post.entities),
  };
}

export function buildChroniclePresentation(post: ChroniclePost): ChroniclePresentation {
  switch (post.source_type) {
    case "weather":
      return buildWeatherPresentation(post);
    case "settlement_profile":
      return buildSettlementPresentation(post);
    case "animal_breeding":
      return buildAnimalPresentation(post);
    case "transaction":
      return buildTransactionPresentation(post);
    case "canon_event":
      return buildEventPresentation(post);
    default:
      if (post.category === "Weather") {
        return buildWeatherPresentation(post);
      }
      if (post.category === "Settlements") {
        return buildSettlementPresentation(post);
      }
      if (post.category === "Animals") {
        return buildAnimalPresentation(post);
      }
      if (post.category === "Timekeeping") {
        return buildTransactionPresentation(post);
      }
      return makeGenericPresentation(post, "Simulation Chronicle");
  }
}
