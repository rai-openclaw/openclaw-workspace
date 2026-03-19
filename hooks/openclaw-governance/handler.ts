import type { HookHandler } from "../../src/hooks/hooks.js";
import fs from "fs";
import path from "path";

const WORKSPACE = path.join(process.env.HOME || "", ".openclaw/workspace");
const LEARNINGS_DIR = path.join(WORKSPACE, ".learnings");

const handler: HookHandler = async (event) => {
  const e = event as any;

  // ── agent:bootstrap: inject .learnings/ files into every session ──
  if (event.type === "agent" && e.action === "bootstrap") {
    const files = ["ERRORS.md", "LEARNINGS.md", "FEATURE_REQUESTS.md"];
    for (const file of files) {
      const filePath = path.join(LEARNINGS_DIR, file);
      if (fs.existsSync(filePath)) {
        const content = fs.readFileSync(filePath, "utf8");
        if (content.trim().length > 50) {
          // Only inject if there's actual content beyond the header
          event.context.bootstrapFiles?.push({
            filename: `.learnings/${file}`,
            content,
          });
        }
      }
    }
    return;
  }

  // ── command:new: governance checkpoint before session closes ──
  if (event.type === "command" && e.action === "new") {
    event.messages.push(
      "📚 Governance Checkpoint — Before this session closes:\n" +
        "1. Review ~/.openclaw/workspace/.learnings/ERRORS.md — update Status to resolved for any fixed items\n" +
        "2. Review ~/.openclaw/workspace/.learnings/LEARNINGS.md — promote high-value learnings to SOUL.md, TOOLS.md, AGENTS.md, or RUNTIME.md\n" +
        "3. Write today's memory file to ~/.openclaw/workspace/memory/YYYY-MM-DD.md if not already done\n" +
        "4. Commit both repos atomically before session closes"
    );
    return;
  }
};

export default handler;
