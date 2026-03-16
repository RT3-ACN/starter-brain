import { Plugin, Notice, parseYaml } from "obsidian";
import { EntityCreatorModal } from "./src/entity-creator";
import { EpisodeLoggerModal } from "./src/episode-logger";
import { RelationBrowserView, VIEW_TYPE_RELATION_BROWSER } from "./src/relation-browser";

export default class StarterBrainPlugin extends Plugin {
  private author = "user";

  async onload() {
    const brainrc = this.app.vault.getAbstractFileByPath(".brainrc");
    if (brainrc) {
      const content = await this.app.vault.cachedRead(brainrc as any);
      try {
        const parsed = parseYaml(content);
        if (parsed?.author) this.author = parsed.author;
      } catch {}
    }

    this.addCommand({
      id: "create-entity",
      name: "Create Entity",
      callback: () => new EntityCreatorModal(this.app, this.author).open(),
    });

    this.addCommand({
      id: "log-episode",
      name: "Log Episode",
      callback: () => new EpisodeLoggerModal(this.app, this.author).open(),
    });

    this.registerView(
      VIEW_TYPE_RELATION_BROWSER,
      (leaf) => new RelationBrowserView(leaf, this.app),
    );

    this.addCommand({
      id: "open-relation-browser",
      name: "Open Relation Browser",
      callback: () => this.activateRelationBrowser(),
    });

    this.app.workspace.onLayoutReady(() => this.runHealthCheck());
  }

  async activateRelationBrowser() {
    const { workspace } = this.app;
    let leaf = workspace.getLeavesOfType(VIEW_TYPE_RELATION_BROWSER)[0];
    if (!leaf) {
      const rightLeaf = workspace.getRightLeaf(false);
      if (rightLeaf) {
        await rightLeaf.setViewState({ type: VIEW_TYPE_RELATION_BROWSER });
        leaf = rightLeaf;
      }
    }
    if (leaf) workspace.revealLeaf(leaf);
  }

  async runHealthCheck() {
    const files = this.app.vault.getFiles().filter((f) => f.path.startsWith("entities/"));
    let brokenCount = 0;
    for (const file of files) {
      const cache = this.app.metadataCache.getFileCache(file);
      const fm = cache?.frontmatter;
      if (!fm?.relations) continue;
      for (const rel of fm.relations) {
        const targetPath = `entities/${rel.target}.md`;
        if (!this.app.vault.getAbstractFileByPath(targetPath)) {
          brokenCount++;
        }
      }
    }
    if (brokenCount > 0) {
      new Notice(`Starter Brain: ${brokenCount} broken relation(s) found. Run brain health for details.`);
    }
  }

  onunload() {}
}
