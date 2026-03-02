# HEARTBEAT.md - Raibot Periodic Tasks

## Passive Tasks (When Mentioned)

- Log all messages from the triggering channel to `memory/messages/`
- Store any attached images with OCR results

## Periodic Checks (If Activated as all_messages)

- [ ] Monitor configured channels for new messages
- [ ] Run OCR on new images within 1 hour of posting
- [ ] Index new messages to search database

## Manual Triggers

When asked:
- Search past messages: check `memory/messages/`
- Answer questions: use stored data + web search
- Process OCR: use gemini_ocr.py tool (Gemini 2.0 Flash)

## OCR Tool

**Location:** `tools/gemini_ocr.py`

**Usage:**
```bash
python3 tools/gemini_ocr.py <image_path> [prompt]
```

**Example:**
```bash
python3 tools/gemini_ocr.py image.png "What text do you see?"
```

## Current Status

- **Activation:** mention-only (needs change to all_messages)
- **OCR:** Gemini 2.0 Flash via direct API (working ✅)
- **Storage:** JSON files by day (`memory/messages/YYYY-MM-DD.json`)
