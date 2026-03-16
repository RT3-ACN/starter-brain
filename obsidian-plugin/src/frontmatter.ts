import { stringifyYaml } from "obsidian";
import { pluralizeType } from "./constants";

export interface Relation {
  type: string;
  target: string;
}

export interface EntityFrontmatter {
  type: string;
  id: string;
  name: string;
  created: string;
  updated: string;
  author: string;
  status: string;
  confidence?: number | null;
  importance?: number;
  tags?: string[];
  relations?: Relation[];
}

export function buildEntityContent(fm: EntityFrontmatter, body: string): string {
  const yamlStr = stringifyYaml(fm);
  let content = `---\n${yamlStr}---\n\n${body}`;
  if (fm.relations && fm.relations.length > 0) {
    content += "\n## Related\n";
    for (const rel of fm.relations) {
      const slug = rel.target.split("/").pop() || rel.target;
      content += `- ${rel.type}: [[${rel.target}|${slug}]]\n`;
    }
  }
  return content;
}

export function entityPath(type: string, slug: string): string {
  return `entities/${pluralizeType(type)}/${slug}.md`;
}
