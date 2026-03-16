export const DEFAULT_ENTITY_TYPES = [
  "topic", "insight", "research", "decision",
  "pattern", "person", "project", "hypothesis",
];

export const RELATION_TYPES = [
  "REFERENCES", "INFORMS", "DERIVED_FROM", "SUPERSEDED_BY",
  "CONTRADICTS", "DEPENDS_ON", "PART_OF", "USES_TOPIC", "CREATED_BY",
];

export function pluralizeType(type: string): string {
  if (type.endsWith("s")) return type;
  if (type === "person") return "people";
  if (type === "hypothesis") return "hypotheses";
  if (type === "research") return "research";
  return type + "s";
}

export function singularizeType(plural: string): string {
  if (plural === "people") return "person";
  if (plural === "hypotheses") return "hypothesis";
  if (plural === "research") return "research";
  if (plural.endsWith("s") && plural !== "hypothesis") return plural.slice(0, -1);
  return plural;
}
