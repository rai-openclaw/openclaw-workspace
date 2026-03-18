# Calendar Governance

## 1. Purpose

Defines authoritative rules for calendar event management. All calendar operations must comply.

## 2. Source of Truth

Calendar events exist in exactly one source:

| Source | Type | Storage |
|--------|------|---------|
| `scheduler` | Personal + Automation | `~/.openclaw/cron/jobs.json` |
| `internal` | Personal (legacy only) | `data/calendar_events.json` |
| `google` | External | Google Calendar API |
| `outlook` | External | Outlook Calendar API |

No event may exist in multiple sources simultaneously.

## 3. Event Creation Rules

### 3.1 Scheduler Events (Automation)

- MUST be created via `cron.add` CLI
- MAY include `payload.eventType` field (optional — scheduler may not support it)
- MAY use `cron.add --at` for one-time events
- CLI validation of past dates is ENFORCED

### 3.2 Personal Events

- ALL new personal events MUST be created via scheduler (`cron.add`)
- Personal events are identified by:
  - `schedule.kind === 'at'`
  - `payload.kind === 'agentTurn'`
  - `payload.message` exists
- `eventType` field is OPTIONAL and may not be supported by scheduler
- MUST NOT be written to `calendar_events.json`

### 3.3 External Events (Future)

- MUST be fetched via provider API
- MUST NOT be written to local files
- MUST use unified `Event` type schema

## 4. Prohibited Actions

- Manual editing of `jobs.json` for past-date events
- Creating duplicate events across sources
- Writing external calendar data to local storage
- Writing new events to `calendar_events.json`
- Bypassing `cron.add` for scheduler events

## 5. Event Classification

| Type | Description | Source |
|------|-------------|--------|
| `personal` | User personal events | scheduler |
| `automation` | System/agent jobs | scheduler |
| `system` | Infrastructure events | scheduler |

## 6. Legacy Events

- `data/calendar_events.json` is LEGACY storage
- MUST be treated as read-only
- MUST only contain past events
- MUST NOT receive new writes
- SHOULD be deprecated once scheduler supports historical events

## 7. System Boundaries

- Calendar UI reads from aggregator layer only
- Aggregator (`lib/events/index.ts`) is SINGLE entry point
- Aggregator is the ONLY layer allowed to merge multiple sources
- API routes MUST NOT independently read from:
  - `jobs.json`
  - `calendar_events.json`
- API routes MUST use `getAllEvents()`

## 8. Schema Enforcement

All events MUST conform to `Event` interface:

```
- id: source-prefixed (e.g., "scheduler:uuid")
- type: "personal" | "automation" | "system"
- source: "scheduler" | "internal" | "google" | "outlook"
- schedule (scheduler only): { kind, cron?, intervalMs?, at?, tz? }
```

**Personal events are identified by:**
- `schedule.kind === 'at'`
- `payload.kind === 'agentTurn'`
- `payload.message` exists

`eventType` in payload is OPTIONAL. The scheduler may not support this field.

- The agent MUST NOT assume `payload` structure; it must preserve existing fields returned by the scheduler system
- `payload` MUST preserve existing scheduler structure and MAY include `eventType` as an additional field

Example:
```json
{
  "name": "Dinner plan",
  "schedule": { "kind": "at", "at": "2026-03-18T19:00:00Z" },
  "payload": {
    "kind": "agentTurn",
    "message": "Dinner plan at 7pm"
  }
}
```

## 9. Change Classification

Modifications to calendar system are classified:

- **L1**: UI changes, logging, cosmetic
- **L2**: Aggregator logic, schema changes, API modifications
- **L3**: Source-of-truth restructuring, external provider integration

## 10. Intent Mapping

This section defines how user requests are mapped to system actions.

### 10.1 Request Interpretation

Any user request that implies creating a calendar event or reminder MUST be interpreted as a scheduler operation.

Examples:
- "add event"
- "calendar event"
- "reminder"
- "schedule"
- "remind me"
- "put on calendar"
- "set up"
- "create event"

ALL of the above MUST route to: `cron.add`

### 10.2 Agent Constraints

The agent MUST NOT:
- Search for a calendar API endpoint
- Write to `calendar_events.json`
- Claim no system exists

The agent MUST:
- Construct appropriate schedule:
  - One-time → `{ kind: "at" }`
  - Recurring → `{ kind: "cron" }`
- Use `payload.kind === "agentTurn"` and include `payload.message` for personal events
- NOT include `eventType` field (unsupported by scheduler)

### 10.3 Read-Only Boundary

Calendar UI/API is READ-ONLY. Creation is ALWAYS via scheduler tools.

### 10.4 Execution Requirement

The agent MUST execute the `cron.add` command immediately upon intent recognition. No intermediate steps, searches, or API explorations are permitted.

## 11. Tool Binding

### 11.1 Calendar Creation Tool
All calendar event creation MUST use the helper: `createCalendarEvent`
The agent MUST NOT call `cron.add` directly for calendar events.

### 11.2 Required Flow
User request → createCalendarEvent → cron.add

The helper is responsible for:
- Time parsing
- UTC conversion
- Payload construction
- Enforcing correct structure

### 11.3 Prohibited
The agent MUST NOT:
- Call `cron.add` directly for user calendar events
- Construct scheduler payloads manually

### 11.4 Rationale
`createCalendarEvent` is the canonical abstraction layer for calendar creation. This ensures consistency and prevents schema drift.
