import type { HookHandler } from "../../src/hooks/hooks.js";
import fs from "fs";
import path from "path";

const LEARNINGS_DIR = path.join(
  process.env.HOME || "",
  ".openclaw/workspace/.learnings"
);
const ERRORS_FILE = path.join(LEARNINGS_DIR, "ERRORS.md");

function appendError(toolName: string, sessionKey: string, errorContent: string) {
  const date = new Date().toISOString().slice(0, 10).replace(/-/g, "");
  const rand = Math.random().toString(36).slice(2, 5).toUpperCase();
  const id = `ERR-${date}-${rand}`;
  const entry = `
## [${id}] ${toolName}
**Logged**: ${new Date().toISOString()}
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
Tool call failed during agent run

### Error
\`\`\`
${errorContent.slice(0, 500)}
\`\`\`

### Context
- Tool: ${toolName}
- Session: ${sessionKey}

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

const handler: HookHandler = async (event) => {
  // ── tool_result_persist: plugin hook for all tool results ──
  const e = event as any;
  if (e.toolName !== undefined && e.message !== undefined) {
    // This is a tool_result_persist event
    const message = e.message;
    const toolName = e.toolName || "unknown";
    const sessionKey = e.sessionKey || "unknown";

    // Detect failure from message content
    const isError =
      message?.isError === true ||
      (Array.isArray(message?.content) &&
        message.content.some(
          (c: any) => c?.type === "tool_result" && c?.is_error === true
        )) ||
      (typeof message?.content === "string" &&
        /error|failed|exception|not found|permission denied/i.test(
          message.content
        ));

    if (isError) {
      const errorContent =
        typeof message?.content === "string"
          ? message.content
          : JSON.stringify(message?.content || message).slice(0, 500);
      appendError(toolName, sessionKey, errorContent);
    }
    return;
  }

  // ── command:new: trigger learning review ──
  if (event.type === "command" && e.action === "new") {
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
