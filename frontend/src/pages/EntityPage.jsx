import { useState, useEffect, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import { supplierApi, networkApi, healthApi, simulationApi } from '../services/api'
import RiskBadge from '../components/RiskBadge'
import SupplyRelations from '../components/SupplyRelations'
import IntelligenceSection from '../components/IntelligenceSection'
import NetworkGraph from '../components/NetworkGraph'
import SimulationPanel from '../components/SimulationPanel'

const TABS = [
  { id: 'overview', label: 'Overview' },
  { id: 'network', label: 'Network' },
  { id: 'risks', label: 'Risks' },
  { id: 'intelligence', label: 'Intelligence' },
  { id: 'impact', label: 'Impact' },
]

const NEO4J_LABELS = {
  connected: { graph: 'Live graph', intel: 'Live provider' },
  not_configured: { graph: 'Mock provider', intel: 'Mock provider' },
  unavailable: { graph: 'Unavailable', intel: 'Unavailable' },
}

function RiskMeter({ score, level }) {
  const color = score >= 75 ? '#dc2626' : score >= 50 ? '#d97706' : '#16a34a'
  return (
    <div className="mb-2">
      <div className="flex items-end justify-between mb-1.5">
        <div>
          <div className="text-3xl font-semibold mono" style={{ color }}>{score.toFixed(1)}</div>
          <div className="field-label mt-0.5">risk score / 100</div>
        </div>
        <div className="pb-1"><RiskBadge level={level} /></div>
      </div>
      <div className="h-2 bg-slate-100 rounded overflow-hidden">
        <div className="h-full rounded" style={{ width: `${score}%`, background: color }} />
      </div>
    </div>
  )
}

function OverviewTab({ detail, sourceLabel }) {
  const s = detail.supplier
  const upstream = detail.upstream_suppliers || []
  const downstream = detail.downstream_customers || []

  return (
    <div className="space-y-6 max-w-3xl">
      {sourceLabel && (
        <div className="mono text-[10px] text-slate-400">Data source: {sourceLabel}</div>
      )}

      <div className="panel px-5 py-4">
        <RiskMeter score={s.risk_score} level={s.risk_level} />
        <div className="grid grid-cols-2 md:grid-cols-3 gap-x-4 gap-y-3 mt-2">
          <div>
            <div className="field-label">Country</div>
            <div className="field-value">{s.country}</div>
          </div>
          <div>
            <div className="field-label">City</div>
            <div className="field-value">{s.city}</div>
          </div>
          <div>
            <div className="field-label">Category</div>
            <div className="field-value">{s.category}</div>
          </div>
          <div>
            <div className="field-label">Tier</div>
            <div className="field-value mono">T{s.tier}</div>
          </div>
          <div>
            <div className="field-label">Lead Time</div>
            <div className="field-value mono">{s.lead_time_days} days</div>
          </div>
          <div>
            <div className="field-label">Revenue Dependency</div>
            <div className="field-value mono">{s.revenue_dependency}%</div>
          </div>
          <div>
            <div className="field-label">Alternative Suppliers</div>
            <div className="field-value mono">{s.alternatives_count}</div>
          </div>
          <div>
            <div className="field-label">Active Threats</div>
            <div className="field-value mono">{s.active_threats}</div>
          </div>
          <div>
            <div className="field-label">Criticality</div>
            <div className="field-value mono">{s.criticality.toFixed(0)}</div>
          </div>
        </div>
        <div className="mt-3 pt-3 border-t border-slate-100">
          <div className="field-label">Coordinates</div>
          <div className="mono text-xs text-slate-500">{s.lat.toFixed(4)}, {s.lng.toFixed(4)}</div>
        </div>
      </div>

      <div className="panel px-5 py-4">
        <h3 className="panel-title mb-3">Supply Network Position</h3>
        <SupplyRelations upstream={upstream} downstream={downstream} />
      </div>
    </div>
  )
}

function RisksTab({ detail }) {
  const breakdown = detail.risk_breakdown || {}
  const keys = Object.keys(breakdown)

  return (
    <div className="space-y-6 max-w-3xl">
      <div className="panel px-5 py-4">
        <h3 className="panel-title mb-3">Risk Factors</h3>
        {keys.length === 0 ? (
          <div className="text-sm text-slate-400">No risk-factor breakdown is available for this entity.</div>
        ) : (
          <div className="space-y-3">
            {keys.map((k) => (
              <div key={k}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm capitalize text-slate-700">{k}</span>
                  <span className="mono text-sm text-slate-900">{breakdown[k]}</span>
                </div>
                <div className="h-1.5 bg-slate-100 rounded overflow-hidden">
                  <div
                    className="h-full rounded"
                    style={{ width: `${Math.min(breakdown[k], 100)}%`, background: '#dc2626' }}
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function NetworkTab({ supplierId }) {
  const [graphData, setGraphData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    networkApi.getGraph().then((g) => {
      if (cancelled) return
      if (g?.nodes?.length) {
        const ids = new Set()
        g.nodes.forEach((n) => {
          if (n.id === supplierId) ids.add(n.id)
        })
        g.edges?.forEach((e) => {
          if (e.source === supplierId || e.target === supplierId) {
            ids.add(e.source)
            ids.add(e.target)
          }
        })
        const selected = g.nodes.filter((n) => ids.has(n.id))
        const edgeIds = new Set(
          g.edges?.filter((e) => e.source === supplierId || e.target === supplierId).map((e) => e.id)
        )
        const selectedEdges = g.edges?.filter((e) => edgeIds.has(e.id)) || []
        setGraphData({ nodes: selected, edges: selectedEdges })
      } else {
        setGraphData({ nodes: [], edges: [] })
      }
    }).catch(() => setGraphData({ nodes: [], edges: [] })).finally(() => {
      if (!cancelled) setLoading(false)
    })
    return () => { cancelled = true }
  }, [supplierId])

  if (loading) {
    return <div className="text-sm text-slate-400">Loading network…</div>
  }

  return (
    <div className="panel overflow-hidden">
      <div className="panel-header">
        <span className="panel-title">Network — {supplierId}</span>
        <span className="mono text-[10px] text-slate-400">nodes {graphData?.nodes?.length || 0} · edges {graphData?.edges?.length || 0}</span>
      </div>
      <div className="h-[520px]">
        <NetworkGraph graphData={graphData} highlightedIds={[supplierId]} />
      </div>
    </div>
  )
}

function IntelligenceTab({ detail, sourceLabel }) {
  return <IntelligenceSection news={detail.news} weatherAlerts={detail.weather_alerts} sourceLabel={sourceLabel} />
}

function ImpactTab({ supplierId }) {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleRun = useCallback(async (params) => {
    setLoading(true)
    setResult(null)
    try {
      const res = await simulationApi.runScenario({ ...params, affected_nodes: [supplierId] })
      setResult(res)
    } catch (err) {
      console.error('Simulation failed:', err)
      setResult({})
    } finally {
      setLoading(false)
    }
  }, [supplierId])

  return (
    <div className="max-w-3xl space-y-4">
      {supplierId && (
        <div className="mono text-[10px] text-slate-400">
          Impact simulation seed: {supplierId}
        </div>
      )}
      <SimulationPanel onRun={handleRun} result={result} loading={loading} />
      {!result && !loading && (
        <p className="text-xs text-slate-400">
          Run a scenario to see network impact, affected suppliers, and recommended actions based on the backend simulation engine.
        </p>
      )}
    </div>
  )
}

export default function EntityPage() {
  const { id } = useParams()
  const [detail, setDetail] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('overview')
  const [sourceLabel, setSourceLabel] = useState(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setDetail(null)
    setError(null)
    setActiveTab('overview')

    Promise.all([
      supplierApi.getDetail(id),
      healthApi.getHealth().catch(() => null),
    ]).then(([d, h]) => {
      if (cancelled) return
      setDetail(d)
      const neo = h?.services?.neo4j
      if (neo && NEO4J_LABELS[neo]) {
        setSourceLabel(NEO4J_LABELS[neo].intel)
      }
    }).catch((err) => {
      if (cancelled) return
      setError(err?.response?.status === 404 ? 'Entity not found.' : 'Failed to load entity.')
    }).finally(() => {
      if (!cancelled) setLoading(false)
    })

    return () => { cancelled = true }
  }, [id])

  if (loading) {
    return <div className="max-w-5xl mx-auto px-4 py-8 text-sm text-slate-400">Loading entity…</div>
  }

  if (error || !detail) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-8">
        <div className="panel px-4 py-8 text-center text-sm text-slate-500">
          {error || 'Entity not found.'}
        </div>
        <div className="text-center mt-4">
          <Link to="/" className="text-xs text-slate-500 hover:text-slate-700">← Back to search</Link>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-6">
      <div className="mb-2">
        <Link to="/" className="text-xs text-slate-500 hover:text-slate-700">← Search</Link>
      </div>

      <div className="flex items-start justify-between gap-4 mb-4">
        <div>
          <h1 className="text-xl font-semibold text-slate-900">{detail.supplier.name}</h1>
          <div className="flex items-center gap-2 mt-1 text-sm text-slate-500">
            <span className="mono text-xs text-slate-400">{detail.supplier.id}</span>
            <span>·</span>
            <span>{detail.supplier.city}, {detail.supplier.country}</span>
            <span>·</span>
            <span>{detail.supplier.category}</span>
            <span>·</span>
            <span>Tier {detail.supplier.tier}</span>
          </div>
        </div>
      </div>

      <div className="flex gap-1 border-b border-slate-200 mb-5">
        {TABS.map((t) => (
          <button
            key={t.id}
            onClick={() => setActiveTab(t.id)}
            className={`px-3 py-2 text-sm border-b-2 -mb-px transition-colors ${
              activeTab === t.id
                ? 'border-slate-900 text-slate-900 font-medium'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {activeTab === 'overview' && <OverviewTab detail={detail} sourceLabel={sourceLabel} />}
      {activeTab === 'network' && <NetworkTab supplierId={id} />}
      {activeTab === 'risks' && <RisksTab detail={detail} />}
      {activeTab === 'intelligence' && <IntelligenceTab detail={detail} sourceLabel={sourceLabel} />}
      {activeTab === 'impact' && <ImpactTab supplierId={id} />}
    </div>
  )
}
