'use client'

import { useState, useEffect } from 'react'

interface Commit {
  agent: string
  message: string
  timestamp: string
}

function formatTimestamp(iso: string): string {
  const date = new Date(iso)
  const hours = date.getHours()
  const minutes = date.getMinutes()
  const ampm = hours >= 12 ? 'PM' : 'AM'
  const hour12 = hours % 12 || 12
  const month = date.getMonth() + 1
  const day = date.getDate()
  return `${month}/${day} ${hour12}:${minutes.toString().padStart(2, '0')} ${ampm}`
}

export default function AgentActivityFeed() {
  const [commits, setCommits] = useState<Commit[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchData() {
      try {
        const res = await fetch('/api/agent-activity')
        if (!res.ok) throw new Error('Failed to fetch')
        const json = await res.json()
        setCommits(json.commits || [])
        setError(null)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setLoading(false)
      }
    }
    fetchData()
    const interval = setInterval(fetchData, 10000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div style={{ padding: '1rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
        Loading agent activity...
      </div>
    )
  }

  if (error) {
    return (
      <div style={{ padding: '1rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
        Error: {error}
      </div>
    )
  }

  if (commits.length === 0) {
    return (
      <div style={{ padding: '1rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
        No commits available
      </div>
    )
  }

  return (
    <div style={{
      background: 'var(--card-bg, #1a1a1a)',
      borderRadius: '8px',
      padding: '1rem',
      maxHeight: '300px',
      overflowY: 'auto'
    }}>
      <div style={{
        fontSize: '0.875rem',
        fontWeight: 600,
        marginBottom: '1rem',
        color: 'var(--text-primary, #e5e5e5)'
      }}>
        Agent Activity
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
        {commits.map((commit, idx) => (
          <div
            key={idx}
            style={{
              display: 'flex',
              gap: '0.5rem',
              alignItems: 'flex-start',
              padding: '0.25rem 0.5rem',
              borderRadius: '4px',
              fontSize: '0.8125rem',
              lineHeight: 1.4,
              color: 'var(--text-secondary, #a3a3a3)'
            }}
          >
            <span style={{ color: 'var(--text-primary, #e5e5e5)', flexShrink: 0 }}>●</span>
            <span style={{ color: 'var(--text-primary, #e5e5e5)', fontWeight: 500, flexShrink: 0 }}>
              {commit.agent}
            </span>
            <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {commit.message}
            </span>
            <span style={{ color: 'var(--text-tertiary, #737373)', flexShrink: 0, fontSize: '0.75rem' }}>
              {formatTimestamp(commit.timestamp)}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
