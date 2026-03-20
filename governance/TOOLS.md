# TOOLS.md

## MiniMax

### MiniMax Concurrency Limit
MiniMax API rate limits when too many concurrent sessions hit simultaneously. 35+ active sessions confirmed to trigger rate limiting. Mitigation: spawn subagents sequentially, not in parallel.
