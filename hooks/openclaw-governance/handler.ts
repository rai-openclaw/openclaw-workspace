import type { HookHandler } from "../../src/hooks/hooks.js";
import fs from "fs";
import path from "path";

const LEARNINGS_DIR = path.join(
  process.env.HOME || "",
  ".openclaw/workspace/.learnings"
);
const ERRORS_FILE = path.join(LEARNINGS_DIR, "ERRORS.md");

const handler: HookHandler = async (event) => {
  // ── tool_result_persist: auto-log failures ──
  if (event.type === "tool_result_persist") {
    const result = (event as any).toolResult;
    const isError =
      result?.isError === true ||
      result?.error !== undefined ||
      (typeof result?.content === "string" && result.content.toLowerCase().includes("error"));

    if (isError) {
      const date = new Date().toISOString().slice(0, 10).replace(/-/g, "");
      const rand = Math.random().toString(36).slice(2, 5).toUpperCase();
      const id = `ERR-${date}-${rand}`;
      const toolName = (event as any).toolName || "unknown";
      const errorContent = typeof result?.content === "string"
        ? result.content.slice(0, 500)
        : JSON.stringify(result).slice(0, 500);

      const entry = `
## [${id}] ${toolName}
Logged: ${new Date().toISOString()}
Priority: high
Status: pending
Area: infra

### Summary
Tool call failed during agent run

### Error
\`\`\`
${errorContent}
\`\`\`

### Context
- Tool: ${toolName}
- Session: ${event.sessionKey}

### Suggested Fix
Review error above and determine root cause

---
`;

      try {
        fs.appendFileSync(ERRORS_FILE, entry, "utf8");
      } catch (e) {
        console.error("[openclaw-governance] Failed to write error log:", e);
      }
    }
    return;
  }

  // ── command:new: trigger learning review ──
  if (event.type === "command" && (event as any).action === "new") {
    event.messages.push(
      "📚 Governance Checkpoint — Before this session closes:\n" +
        "1. Review ~/.openclaw/workspace/.learnings/ERRORS.md for any pending items — update Status to resolved if fixed\n" +
        "2. Review ~/.openclaw/workspace/.learnings/LEARNINGS.md — promote any high-value learnings to SOUL.md, TOOLS.md, AGENTS.md, or RUNTIME.md\n" +
        "3. Write today's memory file to ~/.openclaw/workspace/memory/YYYY-MM-DD.md if not already done\n" +
        "4. Commit both repos atomically before session closes"
    );
    return;
  }
};

export default handler;
