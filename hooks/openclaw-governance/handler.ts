import type { HookHandler } from "../../src/hooks/hooks.js";
import fs from "fs";
import path from "path";

const DEBUG_FILE = path.join(
  process.env.HOME || "",
  ".openclaw/workspace/.learnings/debug.log"
);

const handler: HookHandler = async (event) => {
  // Log every single event to debug file
  const entry = `[${new Date().toISOString()}] event received:\n${JSON.stringify(event, null, 2)}\n---\n`;
  try {
    fs.appendFileSync(DEBUG_FILE, entry, "utf8");
  } catch (e) {
    console.error("[openclaw-governance] debug write failed:", e);
  }
};

export default handler;
