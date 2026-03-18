'use client'
import { useState, useEffect } from 'react'

interface AgentData {
  status: string
  sessionTokens: number
  sessionStartTime: string
  gitStatus: string[]
}

interface Commit {
  message: string
  timestamp: string
}

interface ActivityData {
  agents: Record<string, AgentData>
  recentCommits: Commit[]
}

export default function AgentActivityFeed() {
  const [data, setData] = useState<ActivityData | null>(null)
  
  useEffect(() => {
    async function fetchData() {
      try {
        const res = await fetch('/api/agent-activity')
        const json = await res.json()
        setData(json)
      } catch (e) {
        console.error('Failed to fetch activity:', e)
      }
    }
    fetchData()
    const interval = setInterval(fetchData, 10000)
    return () => clearInterval(interval)
  }, [])
  
  if (!data) return <div style={{ padding: '1rem' }}>Loading...</div>
  
  // Safe data access with optional chaining and defaults
  const agents = data?.agents ?? {}
  const commits = data?.recentCommits ?? []
  
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {Object.entries(agents).map(([agent, info]: [string, AgentData]) => (
        <div key={agent} style={{ padding: '0.75rem', background: 'var(--bg-secondary)', borderRadius: '4px' }}>
          <div style={{ fontWeight: 600, textTransform: 'uppercase', marginBottom: '0.5rem' }}>
            {agent} — {info?.status ?? 'UNKNOWN'}
          </div>
          {info?.status === 'ACTIVE' && (info?.gitStatus?.length ?? 0) > 0 && (
            <div style={{ color: 'var(--accent)', fontSize: '0.8rem' }}>
              BUILDING NOW: {(info?.gitStatus ?? []).join(', ')}
            </div>
          )}
          {info?.sessionStartTime && (
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
              Started: {info.sessionStartTime}
            </div>
          )}
        </div>
      ))}
      {(commits?.length ?? 0) > 0 && (
        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
          <div style={{ fontWeight: 600, marginBottom: '0.25rem' }}>Recent Commits:</div>
          {commits.slice(0, 3).map((c: Commit, i: number) => (
            <div key={i} style={{ marginBottom: '0.25rem' }}>{c?.timestamp ?? ''} — {c?.message ?? ''}</div>
          ))}
        </div>
      )}
    </div>
  )
}
