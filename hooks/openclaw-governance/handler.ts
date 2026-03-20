import { postToDiscord } from '../lib/discord.js';
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
  
  // DEBUG: Log the event structure
  console.log('[discord] Bootstrap event:', JSON.stringify({ 
    sessionKey, 
    type: event.type, 
    action: event.action,
    agentId: event.agentId,
    contextAgent: event.context?.agent
  }));

  if (Array.isArray(event.context.bootstrapFiles)) {
    event.context.bootstrapFiles.push({
      path: 'GOVERNANCE_REMINDER.md',
      content: REMINDER,
      virtual: true,
    });
  }

  // Discord notifications for Alex/Scout subagent sessions (fire and forget)
  // Extract agent from sessionKey (e.g., "agent:alex:subagent:...")
  let agent = '';
  if (sessionKey.includes(':alex:')) {
    agent = 'alex';
  } else if (sessionKey.includes(':scout:')) {
    agent = 'scout';
  }
  
  // Also check context.agent as fallback
  if (!agent) {
    agent = event.context?.agent || '';
  }
  
  const taskName = event.context?.task || event.context?.label || 'Unknown Task';
  
  // Extract AEF level from task name
  const levelMatch = taskName.match(/\[L(\d+)\]/i);
  const level = levelMatch ? `L${levelMatch[1]}` : '';
  
  // Format timestamp as HH:MM PT
  const now = new Date();
  const timeStr = now.toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit',
    timeZone: 'America/Los_Angeles'
  }) + ' PT';

  console.log('[discord] Detected agent:', agent, 'task:', taskName);

  if (agent === 'alex') {
    const msg = `🔨 Alex — Starting: ${taskName} | ${level} | ${timeStr}`;
    console.log('[discord] Posting:', msg);
    postToDiscord('openclaw-dev', msg).catch((e) => console.error('[discord] Error:', e));
  } else if (agent === 'scout') {
    const msg = `🔍 Scout — Validating: ${taskName} | ${timeStr}`;
    console.log('[discord] Posting:', msg);
    postToDiscord('openclaw-dev', msg).catch((e) => console.error('[discord] Error:', e));
  }
};

export default handler;
