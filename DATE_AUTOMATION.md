# Date Automation Protocol — NO MENTAL MATH

## The Problem
Mental date calculation causes errors:
- "Today is Tuesday, so Thursday is..." → WRONG
- Off-by-one errors
- Wrong dates in API calls
- Wrong actionable days

## The Solution: System Tools Only

### 1. Python Date Calculation (MANDATORY)

Before ANY API call or date claim, run:

```python
from datetime import datetime, timedelta
import calendar

# Set anchor date
today = datetime(2026, 2, 17)  # Update this daily

# Calculate this week
for i in range(5):  # Mon-Fri
    date = today + timedelta(days=i)
    weekday = calendar.day_name[date.weekday()]
    print(f"{weekday}: {date.strftime('%Y-%m-%d')}")

# Output:
# Monday: 2026-02-16
# Tuesday: 2026-02-17  ← TODAY
# Wednesday: 2026-02-18
# Thursday: 2026-02-19
# Friday: 2026-02-20
```

### 2. API Call Template (Copy/Paste)

```python
import json
from datetime import datetime, timedelta

# Calculate dates
today = datetime.now()
thursday = today + timedelta(days=2)  # If today is Tuesday
friday = today + timedelta(days=3)

# Format for API
thursday_str = thursday.strftime('%Y-%m-%d')
friday_str = friday.strftime('%Y-%m-%d')

print(f"Thursday API call: from={thursday_str}&to={thursday_str}")
print(f"Friday API call: from={friday_str}&to={friday_str}")
```

### 3. Date Verification Before Every Report

```python
# At start of research session
import datetime

today = datetime.date.today()
print(f"TODAY: {today} ({today.strftime('%A')})")

for i in range(1, 4):  # Next 3 days
    future = today + datetime.timedelta(days=i)
    print(f"{future.strftime('%A')} {future}: Research for {future.strftime('%A')} AMC / {future + datetime.timedelta(days=1).strftime('%A')} BMO")
```

### 4. Bob's Updated Instructions

**OLD (prone to error):**
> "Research Thursday earnings..."

**NEW (systematic):**
```
Calculate dates using Python:
1. today = datetime.date.today()
2. target_date = today + timedelta(days=OFFSET)
3. Verify weekday matches intent
4. Use target_date in API calls
5. Output: "Researching [DATE] [WEEKDAY]"
```

### 5. Check Before API Calls

**Before every curl command:**
```bash
python3 -c "
from datetime import datetime, timedelta
import sys
today = datetime(2026, 2, 17)
target = today + timedelta(days=int(sys.argv[1]))
print(f'API date: {target.strftime(\"%Y-%m-%d\")} ({target.strftime(\"%A\")})')
" 2
```

### 6. Automation

**Create daily date reference:**
```bash
#!/bin/bash
# update_dates.sh - Run at 6 AM daily

cat > ~/.openclaw/workspace/TODAY.txt << EOT
TODAY: $(date +%Y-%m-%d)
WEEKDAY: $(date +%A)

THIS WEEK:
$(date -d "+0 days" +%A) $(date -d "+0 days" +%Y-%m-%d) - TODAY
$(date -d "+1 days" +%A) $(date -d "+1 days" +%Y-%m-%d) - Tomorrow
$(date -d "+2 days" +%A) $(date -d "+2 days" +%Y-%m-%d) - +2 days
$(date -d "+3 days" +%A) $(date -d "+3 days" +%Y-%m-%d) - +3 days
$(date -d "+4 days" +%A) $(date -d "+4 days" +%Y-%m-%d) - +4 days
EOT
```

## Zero Mental Math Rule

**NEVER:**
- Count days on fingers
- Say "Thursday is Feb 20" without verifying
- Calculate offsets mentally
- Assume dates

**ALWAYS:**
- Use Python datetime
- Print dates with weekday
- Verify before API calls
- Read from system, not memory

## Verification Checklist

Before any earnings research:
- [ ] Ran Python date calculator
- [ ] Verified weekday matches intent
- [ ] API call uses correct date string
- [ ] Output shows date + weekday
- [ ] Cross-check: Does this make sense?

---

**If date error occurs:**
1. Stop immediately
2. Run Python date calc
3. Fix all downstream data
4. Log in optimization journal
5. Re-verify protocol followed
