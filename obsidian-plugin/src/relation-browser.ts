import { App, ItemView, WorkspaceLeaf, TFile } from "obsidian";

export const VIEW_TYPE_RELATION_BROWSER = "starter-brain-relations";

export class RelationBrowserView extends ItemView {
  private appRef: App;

  constructor(leaf: WorkspaceLeaf, app: App) {
    super(leaf);
    this.appRef = app;
  }

  getViewType() { return VIEW_TYPE_RELATION_BROWSER; }
  getDisplayText() { return "Relations"; }
  getIcon() { return "git-branch"; }

  async onOpen() {
    this.registerEvent(
      this.appRef.workspace.on("active-leaf-change", () => this.render())
    );
    this.render();
  }

  async render() {
    const container = this.containerEl.children[1];
    container.empty();

    const activeFile = this.appRef.workspace.getActiveFile();
    if (!activeFile || !activeFile.path.startsWith("entities/")) {
      container.createEl("p", { text: "Open an entity file to see its relations." });
      return;
    }

    const cache = this.appRef.metadataCache.getFileCache(activeFile);
    const fm = cache?.frontmatter;
    if (!fm) {
      container.createEl("p", { text: "No frontmatter found." });
      return;
    }

    container.createEl("h3", { text: fm.name || activeFile.basename });
    container.createEl("small", { text: `${fm.type} · ${fm.status || "active"}` });

    const relations = fm.relations || [];
    if (relations.length === 0) {
      container.createEl("p", { text: "No relations." });
      return;
    }

    container.createEl("h4", { text: "Outgoing" });
    const outList = container.createEl("ul");
    for (const rel of relations) {
      const li = outList.createEl("li");
      const badge = li.createEl("span", { text: rel.type, cls: "starter-brain-badge" });
      badge.style.cssText = "font-size:0.8em; opacity:0.7; margin-right:4px;";
      const link = li.createEl("a", { text: rel.target, href: "#" });
      link.addEventListener("click", async (e) => {
        e.preventDefault();
        const targetPath = `entities/${rel.target}.md`;
        const file = this.appRef.vault.getAbstractFileByPath(targetPath);
        if (file instanceof TFile) {
          await this.appRef.workspace.getLeaf(false).openFile(file);
        }
      });
    }

    // Incoming relations
    const entityId = fm.id;
    if (!entityId) return;

    const incoming: { source: string; type: string; name: string }[] = [];
    const allFiles = this.appRef.vault.getFiles().filter((f) => f.path.startsWith("entities/"));

    for (const file of allFiles) {
      if (file.path === activeFile.path) continue;
      const c = this.appRef.metadataCache.getFileCache(file);
      const fileFm = c?.frontmatter;
      if (!fileFm?.relations) continue;
      for (const rel of fileFm.relations) {
        if (rel.target === entityId) {
          incoming.push({ source: fileFm.id, type: rel.type, name: fileFm.name || file.basename });
        }
      }
    }

    if (incoming.length > 0) {
      container.createEl("h4", { text: "Incoming" });
      const inList = container.createEl("ul");
      for (const inc of incoming) {
        const li = inList.createEl("li");
        const badge = li.createEl("span", { text: inc.type, cls: "starter-brain-badge" });
        badge.style.cssText = "font-size:0.8em; opacity:0.7; margin-right:4px;";
        const link = li.createEl("a", { text: `${inc.name} (${inc.source})`, href: "#" });
        link.addEventListener("click", async (e) => {
          e.preventDefault();
          const targetPath = `entities/${inc.source}.md`;
          const file = this.appRef.vault.getAbstractFileByPath(targetPath);
          if (file instanceof TFile) {
            await this.appRef.workspace.getLeaf(false).openFile(file);
          }
        });
      }
    }
  }

  async onClose() {}
}
