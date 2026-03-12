import fs from 'fs'
import path from 'path'
import { v4 as uuidv4 } from 'uuid'

const RUN_HISTORY_PATH = '/Users/raitsai/.openclaw/workspace/data/run_history.json'

export interface RunEntry {
  runId: string
  jobName: string
  agent: string
  startTime: string
  endTime?: string
  status: 'running' | 'success' | 'failed' | 'timeout'
  summary?: string
  artifacts: string[]
}

interface RunHistory {
  runs: RunEntry[]
}

function readRunHistory(): RunHistory {
  if (!fs.existsSync(RUN_HISTORY_PATH)) {
    return { runs: [] }
  }
  const data = fs.readFileSync(RUN_HISTORY_PATH, 'utf8')
  return JSON.parse(data)
}

function writeRunHistory(history: RunHistory): void {
  fs.writeFileSync(RUN_HISTORY_PATH, JSON.stringify(history, null, 2))
}

/**
 * Creates a new run entry with status "running"
 * @param jobName - Name of the job/agent being run
 * @param agent - Agent identifier (e.g., "subagent", "main")
 * @returns The runId of the newly created run
 */
export function createRun(jobName: string, agent: string): string {
  const runId = uuidv4()
  const history = readRunHistory()
  
  const newRun: RunEntry = {
    runId,
    jobName,
    agent,
    startTime: new Date().toISOString(),
    status: 'running',
    artifacts: []
  }
  
  history.runs.unshift(newRun) // Add to beginning (most recent first)
  writeRunHistory(history)
  
  return runId
}

/**
 * Completes a run with the given status and summary
 * @param runId - The runId returned from createRun
 * @param status - "success", "failed", or "timeout"
 * @param summary - Summary text describing the outcome
 */
export function completeRun(runId: string, status: 'success' | 'failed' | 'timeout', summary: string): void {
  const history = readRunHistory()
  
  const runIndex = history.runs.findIndex(r => r.runId === runId)
  if (runIndex === -1) {
    console.error(`Run not found: ${runId}`)
    return
  }
  
  history.runs[runIndex].status = status
  history.runs[runIndex].endTime = new Date().toISOString()
  history.runs[runIndex].summary = summary
  
  writeRunHistory(history)
}

/**
 * Gets all runs from history
 * @param limit - Maximum number of runs to return (default 50)
 * @returns Array of run entries
 */
export function getRuns(limit: number = 50): RunEntry[] {
  const history = readRunHistory()
  return history.runs.slice(0, limit)
}

/**
 * Gets a specific run by ID
 * @param runId - The run ID to find
 * @returns The run entry or undefined if not found
 */
export function getRun(runId: string): RunEntry | undefined {
  const history = readRunHistory()
  return history.runs.find(r => r.runId === runId)
}
