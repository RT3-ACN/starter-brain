import { App, Modal, Setting, Notice } from "obsidian";
import { DEFAULT_ENTITY_TYPES, pluralizeType } from "./constants";
import { EntityFrontmatter, buildEntityContent, entityPath } from "./frontmatter";

export class EntityCreatorModal extends Modal {
  private type = "topic";
  private slug = "";
  private name = "";
  private tags = "";
  private author: string;

  constructor(app: App, author: string) {
    super(app);
    this.author = author;
  }

  onOpen() {
    const { contentEl } = this;
    contentEl.createEl("h2", { text: "Create Entity" });

    new Setting(contentEl)
      .setName("Type")
      .addDropdown((dropdown) => {
        for (const t of DEFAULT_ENTITY_TYPES) {
          dropdown.addOption(t, t);
        }
        dropdown.setValue(this.type);
        dropdown.onChange((val) => (this.type = val));
      });

    new Setting(contentEl)
      .setName("Slug")
      .setDesc("URL-safe identifier (e.g. machine-learning)")
      .addText((text) => text.onChange((val) => (this.slug = val)));

    new Setting(contentEl)
      .setName("Name")
      .addText((text) => text.onChange((val) => (this.name = val)));

    new Setting(contentEl)
      .setName("Tags")
      .setDesc("Comma-separated")
      .addText((text) => text.onChange((val) => (this.tags = val)));

    new Setting(contentEl).addButton((btn) =>
      btn.setButtonText("Create").setCta().onClick(() => this.createEntity())
    );
  }

  async createEntity() {
    if (!this.slug || !this.name) {
      new Notice("Slug and name are required.");
      return;
    }

    const today = new Date().toISOString().split("T")[0];
    const tags = this.tags ? this.tags.split(",").map((t) => t.trim()) : [];

    const fm: EntityFrontmatter = {
      type: this.type,
      id: `${pluralizeType(this.type)}/${this.slug}`,
      name: this.name,
      created: today,
      updated: today,
      author: this.author,
      status: "active",
      importance: 5,
      tags,
      relations: [],
    };

    const path = entityPath(this.type, this.slug);
    const body = `## Notes\n\n`;
    const content = buildEntityContent(fm, body);

    const dir = path.substring(0, path.lastIndexOf("/"));
    await this.app.vault.createFolder(dir).catch(() => {});
    await this.app.vault.create(path, content);

    new Notice(`Created ${fm.id}`);
    this.close();
  }

  onClose() {
    this.contentEl.empty();
  }
}
