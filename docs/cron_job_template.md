# Cron Job Template

Use this template when creating new cron jobs to ensure consistent delivery configuration.

## Template

```json
{
  "id": "<generate-uuid>",
  "agentId": "jarvis",
  "name": "<Job Name>",
  "enabled": true,
  "schedule": {
    "kind": "cron",
    "expr": "<cron-expression>",
    "tz": "America/Los_Angeles"
  },
  "sessionTarget": "isolated",
  "wakeMode": "now",
  "payload": {
    "kind": "agentTurn",
    "message": "<job-instructions>",
    "timeoutSeconds": <timeout>
  },
  "delivery": {
    "mode": "announce",
    "channel": "telegram",
    "target": "6772014008"
  },
  "state": {}
}
```

## Required Fields

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Generate unique UUID |
| `name` | Yes | Descriptive job name |
| `schedule.expr` | Yes | Cron expression (e.g., "0 9 * * 1-5" = 9am M-F) |
| `payload.message` | Yes | Instructions for the agent |
| `delivery` | **Yes** | Must include channel + target for Telegram |

## Delivery Configuration

**Always use:**
```json
"delivery": {
  "mode": "announce",
  "channel": "telegram", 
  "target": "6772014008"
}
```

**Common mistakes to avoid:**
- ❌ `"delivery": { "mode": "announce" }` — missing channel/target
- ❌ `"delivery": { "mode": "announce", "channel": "last" }` — "last" requires prior session
- ✅ Always specify explicit Telegram target

## Cron Expression Examples

| Expression | Schedule |
|------------|----------|
| `0 6 * * *` | Daily 6:00 AM |
| `0 9 * * 1-5` | Weekdays 9:00 AM |
| `0 18 * * 1-5` | Weekdays 6:00 PM |
| `30 7 * * 2,4` | Tue/Thu 7:30 AM |
| `0 9 * * 0` | Sunday 9:00 AM |

## User ID Reference

- Default Telegram user: `6772014008`
