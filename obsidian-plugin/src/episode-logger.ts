import { App, Modal, Setting, Notice } from "obsidian";

export class EpisodeLoggerModal extends Modal {
  private summary = "";
  private episodeType = "reflection";
  private author: string;

  constructor(app: App, author: string) {
    super(app);
    this.author = author;
  }

  onOpen() {
    const { contentEl } = this;
    contentEl.createEl("h2", { text: "Log Episode" });

    new Setting(contentEl)
      .setName("Type")
      .addDropdown((dropdown) => {
        for (const t of ["research", "decision", "discovery", "task", "reflection"]) {
          dropdown.addOption(t, t);
        }
        dropdown.setValue(this.episodeType);
        dropdown.onChange((val) => (this.episodeType = val));
      });

    new Setting(contentEl)
      .setName("Summary")
      .addTextArea((text) => {
        text.inputEl.rows = 4;
        text.inputEl.cols = 50;
        text.onChange((val) => (this.summary = val));
      });

    new Setting(contentEl).addButton((btn) =>
      btn.setButtonText("Log").setCta().onClick(() => this.logEpisode())
    );
  }

  async logEpisode() {
    if (!this.summary) {
      new Notice("Summary is required.");
      return;
    }

    const today = new Date().toISOString().split("T")[0];
    const now = new Date().toTimeString().slice(0, 5);
    const path = `episodes/${today}.md`;

    const entry = `\n## ${this.author} | ${now} | ${this.episodeType} | importance:5\n${this.summary}\n`;

    const existing = this.app.vault.getAbstractFileByPath(path);
    if (existing) {
      await this.app.vault.append(existing as any, entry);
    } else {
      await this.app.vault.createFolder("episodes").catch(() => {});
      await this.app.vault.create(path, `# ${today}\n${entry}`);
    }

    new Notice(`Episode logged to ${path}`);
    this.close();
  }

  onClose() {
    this.contentEl.empty();
  }
}
