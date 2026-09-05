import { useEffect, useState } from 'react'
import { healthApi } from '../services/api'

const NEO4J_LABELS = {
  connected: { text: 'Live graph', cls: 'text-green-700 bg-green-50 border-green-200' },
  not_configured: { text: 'Mock provider', cls: 'text-amber-700 bg-amber-50 border-amber-200' },
  unavailable: { text: 'Graph unavailable', cls: 'text-red-700 bg-red-50 border-red-200' },
}

export default function HealthBadge() {
  const [neo4j, setNeo4j] = useState(null)

  useEffect(() => {
    let cancelled = false
    healthApi.getHealth()
      .then((h) => { if (!cancelled) setNeo4j(h.services?.neo4j) })
      .catch(() => {})
    return () => { cancelled = true }
  }, [])

  if (!neo4j || !NEO4J_LABELS[neo4j]) return null
  const s = NEO4J_LABELS[neo4j]

  return (
    <span
      className={`mono text-[10px] border rounded px-1.5 py-0.5 ${s.cls}`}
      title="Data source status for graph/entity data, reported by the backend health endpoint"
    >
      {s.text}
    </span>
  )
}
