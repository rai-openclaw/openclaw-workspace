import type { HookHandler } from 'openclaw/hooks';

const REMINDER = `## Governance & Learning Reminder

At session start, you must:
1. Confirm governance loaded from ~/.openclaw/workspace/governance/RUNTIME.md
2. Check ~/.openclaw/workspace/.learnings/ERRORS.md for any high-priority pending items
3. Check ~/.openclaw/workspace/.learnings/LEARNINGS.md for any promoted learnings

Log during session when:
- A tool or command fails → ~/.openclaw/workspace/.learnings/ERRORS.md
- User corrects you → ~/.openclaw/workspace/.learnings/LEARNINGS.md
- User requests missing capability → ~/.openclaw/workspace/.learnings/FEATURE_REQUESTS.md
- You find a better approach → ~/.openclaw/workspace/.learnings/LEARNINGS.md

Before session closes (/new or /reset):
- Review .learnings/ and promote high-value items to SOUL.md, TOOLS.md, AGENTS.md, or RUNTIME.md
- Write today's memory file
- Commit both repos atomically`;

const handler: HookHandler = async (event) => {
  if (!event || typeof event !== 'object') return;
  if (event.type !== 'agent' || event.action !== 'bootstrap') return;
  if (!event.context || typeof event.context !== 'object') return;

  const sessionKey = event.sessionKey || '';
  if (sessionKey.includes(':subagent:')) return;

  if (Array.isArray(event.context.bootstrapFiles)) {
    event.context.bootstrapFiles.push({
      path: 'GOVERNANCE_REMINDER.md',
      content: REMINDER,
      virtual: true,
    });
  }
};

export default handler;
