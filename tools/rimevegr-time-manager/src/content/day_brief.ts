export type DayBriefPresentation = {
  eyebrow: string;
  title: string;
  lead: string;
  flavor: string;
  points: string[];
};

export type DayBriefSource = {
  id: string;
  title: string;
  category: string;
  entities: string[];
};

function joinNames(values: string[]): string {
  return values.filter(Boolean).join(" · ");
}

function uniqueLabels(values: string[]): string[] {
  return Array.from(new Set(values.filter(Boolean)));
}

export function buildDayBriefPresentation(posts: DayBriefSource[], dayLabel: string): DayBriefPresentation {
  const categories = uniqueLabels(posts.map((post) => post.category));
  const entities = uniqueLabels(posts.flatMap((post) => post.entities));
  const firstPost = posts[0];
  const lastPost = posts[posts.length - 1];

  const lead =
    posts.length === 0
      ? `No chronicle entries were recorded for ${dayLabel}.`
      : `${posts.length} post${posts.length === 1 ? "" : "s"} were recorded for ${dayLabel}.`;

  const points: string[] = [];
  if (categories.length > 0) {
    points.push(`Threads in view: ${joinNames(categories)}.`);
  }
  if (entities.length > 0) {
    points.push(`Places and bands in view: ${joinNames(entities.slice(0, 6))}.`);
  }
  if (firstPost && lastPost && firstPost.id !== lastPost.id) {
    points.push(`The feed spans from ${lastPost.title} to ${firstPost.title}.`);
  } else if (firstPost) {
    points.push(`The day is anchored by ${firstPost.title}.`);
  }
  if (posts.length > 0) {
    points.push("Open the posts below for the narrative layer; technical detail stays hidden unless requested.");
  }

  return {
    eyebrow: "Day Brief",
    title: dayLabel,
    lead,
    flavor: categories.length > 0 ? `Primary threads: ${joinNames(categories)}.` : "No active threads were filtered in.",
    points,
  };
}
