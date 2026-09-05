import { useState, useEffect, useCallback } from 'react'
import {
  Activity,
  AlertTriangle,
  Download,
  Shield,
  TrendingUp,
  Zap,
  RefreshCw,
  Play,
  BarChart3,
  Globe,
} from 'lucide-react'
import NetworkGraph from './components/NetworkGraph'
import SupplierPanel from './components/SupplierPanel'
import { networkApi, supplierApi, metricsApi, simulationApi, threatsApi } from './services/api'

function MetricCard({ icon, label, value, color, subtitle }) {
  return (
    <div className="metric-card">
      <div className="flex items-center gap-2">
        <div style={{ color }}>{icon}</div>
        <span className="text-xs text-slate-500 uppercase tracking-wider">{label}</span>
      </div>
      <div className="text-2xl font-semibold mt-1" style={{ color }}>
        {value}
      </div>
      {subtitle && <div className="text-xs text-slate-500 mt-0.5">{subtitle}</div>}
    </div>
  )
}

function ThreatTicker({ threats }) {
  if (!threats || threats.length === 0) return null
  const doubled = [...threats, ...threats]

  return (
    <div className="w-full overflow-hidden card py-2 px-3">
      <div className="flex gap-8 ticker-track" style={{ width: 'max-content' }}>
        {doubled.map((t, i) => (
          <div key={i} className="flex items-center gap-2 whitespace-nowrap">
            <span
              className="w-2 h-2 rounded-full flex-shrink-0"
              style={{
                background:
                  t.severity === 'CRITICAL' ? '#dc2626' :
                  t.severity === 'HIGH' ? '#dc2626' : '#d97706',
              }}
            />
            <span className="text-xs text-slate-700">{t.title?.slice(0, 80)}</span>
            <span className="text-xs text-slate-500">{t.supplier_name}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function SimulationPanel({ onRun, result, loading }) {
  const [description, setDescription] = useState('')
  const [severity, setSeverity] = useState(0.7)

  const handleSubmit = (e) => {
    e.preventDefault()
    if (description.trim()) {
      onRun({ description: description.trim(), severity })
    }
  }

  return (
    <div className="card p-4 space-y-3">
      <h3 className="section-title flex items-center gap-1 mb-0">
        <Zap size={12} /> Disruption Simulator
      </h3>
      <form onSubmit={handleSubmit} className="space-y-3">
        <input
          id="simulation-input"
          type="text"
          placeholder="e.g. Port closure in Suez Canal for 5 days"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          maxLength={500}
          className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:border-brand-500"
        />
        <div className="flex items-center gap-3">
          <label className="text-xs text-slate-500 flex-shrink-0">Severity</label>
          <input
            id="severity-slider"
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={severity}
            onChange={(e) => setSeverity(parseFloat(e.target.value))}
            className="flex-1 accent-brand-500"
          />
          <span className="text-xs font-mono text-slate-700 w-8">{(severity * 100).toFixed(0)}%</span>
        </div>
        <button
          id="run-simulation"
          type="submit"
          disabled={loading || !description.trim()}
          className="btn-primary w-full text-sm flex items-center justify-center gap-2"
        >
          {loading ? <RefreshCw size={14} className="animate-spin" /> : <Play size={14} />}
          {loading ? 'Simulating...' : 'Run Simulation'}
        </button>
      </form>

      {result && result.scenario_id && (
        <a
          href={simulationApi.reportUrl(result.scenario_id)}
          download
          className="btn-secondary w-full text-sm flex items-center justify-center gap-2"
        >
          <Download size={14} />
          Download Report
        </a>
      )}

      {result && (
        <div className="mt-3 space-y-2 animate-slide-in">
          <div className="bg-slate-50 rounded-lg p-3 border border-slate-200">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-slate-500">Network Impact</span>
              <span className="text-sm font-semibold" style={{
                color: result.overall_network_impact >= 70 ? '#dc2626' :
                       result.overall_network_impact >= 40 ? '#d97706' : '#16a34a'
              }}>
                {result.overall_network_impact}/100
              </span>
            </div>
            <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-1000"
                style={{
                  width: `${result.overall_network_impact}%`,
                  background: result.overall_network_impact >= 70 ? '#dc2626' :
                              result.overall_network_impact >= 40 ? '#d97706' : '#16a34a',
                }}
              />
            </div>
          </div>

          <div className="text-xs text-slate-700 bg-slate-50 rounded-lg p-3 border border-slate-200 leading-relaxed">
            {result.executive_summary}
          </div>

          <div className="grid grid-cols-2 gap-2 text-center">
            <div className="bg-slate-50 rounded p-2 border border-slate-200">
              <div className="text-xs text-slate-500">Affected</div>
              <div className="text-sm font-semibold text-red-600">{result.affected_suppliers?.length || 0}</div>
            </div>
            <div className="bg-slate-50 rounded p-2 border border-slate-200">
              <div className="text-xs text-slate-500">Time to Impact</div>
              <div className="text-sm font-semibold text-amber-600">{result.time_to_impact_days}d</div>
            </div>
          </div>

          {result.mitigation_actions?.length > 0 && (
            <div>
              <p className="text-xs text-slate-500 mb-1">Recommended Actions:</p>
              <ul className="space-y-1">
                {result.mitigation_actions.slice(0, 3).map((action, i) => (
                  <li key={i} className="text-xs text-slate-700 flex items-start gap-1.5">
                    <span className="text-brand-500 mt-0.5">→</span>
                    {action}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default function App() {
  const [graphData, setGraphData] = useState(null)
  const [metrics, setMetrics] = useState(null)
  const [threats, setThreats] = useState([])
  const [selectedSupplier, setSelectedSupplier] = useState(null)
  const [supplierDetail, setSupplierDetail] = useState(null)
  const [simulationResult, setSimulationResult] = useState(null)
  const [simulating, setSimulating] = useState(false)
  const [highlightedIds, setHighlightedIds] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const [graph, met, thr] = await Promise.all([
          networkApi.getGraph(),
          metricsApi.getMetrics(),
          threatsApi.getThreats(),
        ])
        setGraphData(graph)
        setMetrics(met)
        setThreats(thr.threats || [])
      } catch (err) {
        console.error('Failed to load data:', err)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const handleNodeClick = useCallback(async (supplier) => {
    setSelectedSupplier(supplier)
    try {
      const detail = await supplierApi.getDetail(supplier.id)
      setSupplierDetail(detail)
    } catch (err) {
      console.error('Failed to load supplier detail:', err)
    }
  }, [])

  const handleClosePanel = useCallback(() => {
    setSelectedSupplier(null)
    setSupplierDetail(null)
  }, [])

  const handleSimulation = useCallback(async (params) => {
    setSimulating(true)
    setSimulationResult(null)
    try {
      const result = await simulationApi.runScenario(params)
      setSimulationResult(result)
      if (result.affected_suppliers) {
        setHighlightedIds(result.affected_suppliers.map(a => a.supplier_id))
      }
    } catch (err) {
      console.error('Simulation failed:', err)
      setSimulationResult({ error: 'Simulation failed. Check console for details.' })
    } finally {
      setSimulating(false)
    }
  }, [])

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center bg-white">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-2 border-brand-500 border-t-transparent mx-auto mb-4" />
          <p className="text-slate-500 text-sm">Loading supply chain risk intelligence...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen flex flex-col bg-white">
      {/* Header */}
      <header className="flex items-center justify-between px-5 py-3 border-b border-slate-200 flex-shrink-0 bg-slate-50">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-brand-500 flex items-center justify-center">
            <Shield size={16} className="text-white" />
          </div>
          <div>
            <h1 className="text-sm font-semibold text-slate-900">Supply Chain Disruption Predictor</h1>
            <p className="text-xs text-slate-500">Supply Chain Risk Intelligence</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {metrics && (
            <div className="hidden md:flex items-center gap-4 text-xs">
              <span className="flex items-center gap-1 text-slate-500">
                <Globe size={11} />
                {graphData?.nodes?.length || 0} suppliers
              </span>
              <span className="flex items-center gap-1 text-amber-600">
                <AlertTriangle size={11} />
                {metrics.active_threats} threats
              </span>
            </div>
          )}
          <span
            className="h-2 w-2 rounded-full"
            style={{
              background: metrics?.trend === 'improving' ? '#16a34a' :
                          metrics?.trend === 'degrading' ? '#dc2626' : '#d97706',
            }}
            title={`Trend: ${metrics?.trend || 'unknown'}`}
          />
        </div>
      </header>

      {/* Threat Ticker */}
      <ThreatTicker threats={threats} />

      {/* Main Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel — Metrics & Simulation */}
        <div className="w-72 flex-shrink-0 border-r border-slate-200 overflow-y-auto p-3 space-y-3 bg-slate-50">
          {metrics && (
            <>
              <MetricCard
                icon={<Activity size={14} />}
                label="Network Health"
                value={`${metrics.network_health_score}%`}
                color={metrics.network_health_score >= 65 ? '#16a34a' : metrics.network_health_score >= 40 ? '#d97706' : '#dc2626'}
                subtitle={`Trend: ${metrics.trend}`}
              />
              <MetricCard
                icon={<AlertTriangle size={14} />}
                label="High Risk"
                value={metrics.high_risk_suppliers}
                color="#dc2626"
                subtitle={`${metrics.critical_suppliers} critical`}
              />
              <MetricCard
                icon={<BarChart3 size={14} />}
                label="Avg Risk Score"
                value={metrics.average_risk_score}
                color="#d97706"
                subtitle={`30d disruption: ${(metrics.disruption_probability_30d * 100).toFixed(0)}%`}
              />
              <MetricCard
                icon={<TrendingUp size={14} />}
                label="Disruption Prob"
                value={`${(metrics.disruption_probability_30d * 100).toFixed(0)}%`}
                color="#2563eb"
                subtitle="Next 30 days"
              />
            </>
          )}

          <SimulationPanel
            onRun={handleSimulation}
            result={simulationResult}
            loading={simulating}
          />
        </div>

        {/* Center — Network Graph */}
        <div className="flex-1 relative">
          <NetworkGraph
            graphData={graphData}
            onNodeClick={handleNodeClick}
            highlightedIds={highlightedIds}
          />
          {highlightedIds.length > 0 && (
            <button
              id="clear-highlights"
              onClick={() => setHighlightedIds([])}
              className="absolute top-3 right-3 btn-secondary text-xs"
            >
              Clear Highlights
            </button>
          )}
        </div>

        {/* Right Panel — Supplier Detail */}
        {supplierDetail && (
          <div className="w-80 flex-shrink-0 border-l border-slate-200 bg-slate-50">
            <SupplierPanel detail={supplierDetail} onClose={handleClosePanel} />
          </div>
        )}
      </div>
    </div>
  )
}