import { useState } from 'react'
import { simulationApi } from '../services/api'

const IMPACT_COLOR = (score) => {
  if (score >= 70) return '#dc2626'
  if (score >= 40) return '#d97706'
  return '#16a34a'
}

export default function SimulationPanel({ onRun, result, loading }) {
  const [description, setDescription] = useState('')
  const [severity, setSeverity] = useState(0.7)

  const handleSubmit = (e) => {
    e.preventDefault()
    if (description.trim()) {
      onRun({ description: description.trim(), severity })
    }
  }

  return (
    <div className="space-y-3">
      <form onSubmit={handleSubmit} className="space-y-3">
        <div>
          <label htmlFor="simulation-input" className="field-label block mb-1">
            Disruption scenario
          </label>
          <input
            id="simulation-input"
            type="text"
            placeholder="Describe a disruption, e.g. port closure or factory outage"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            maxLength={500}
            className="input-field w-full"
          />
        </div>
        <div className="flex items-center gap-3">
          <label htmlFor="severity-slider" className="field-label flex-shrink-0">Severity</label>
          <input
            id="severity-slider"
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={severity}
            onChange={(e) => setSeverity(parseFloat(e.target.value))}
            className="flex-1 accent-slate-900"
          />
          <span className="mono text-xs text-slate-700 w-8">{(severity * 100).toFixed(0)}%</span>
        </div>
        <button
          id="run-simulation"
          type="submit"
          disabled={loading || description.trim().length < 3}
          className="btn-primary w-full"
        >
          {loading ? 'Simulating…' : 'Run Impact Simulation'}
        </button>
      </form>

      {result?.scenario_id && (
        <a
          href={simulationApi.reportUrl(result.scenario_id)}
          download
          className="btn-secondary w-full text-center block"
        >
          Download Report
        </a>
      )}

      {result && result.scenario_id && (
        <div className="panel px-4 py-3 space-y-3">
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="field-label">Network Impact</span>
              <span className="mono text-sm font-semibold" style={{ color: IMPACT_COLOR(result.overall_network_impact) }}>
                {result.overall_network_impact}/100
              </span>
            </div>
            <div className="h-1.5 bg-slate-100 rounded overflow-hidden">
              <div
                className="h-full rounded"
                style={{ width: `${result.overall_network_impact}%`, background: IMPACT_COLOR(result.overall_network_impact) }}
              />
            </div>
          </div>

          {result.executive_summary && (
            <p className="text-xs text-slate-600 leading-relaxed">
              {result.executive_summary}
            </p>
          )}

          <div className="grid grid-cols-2 gap-2 text-center">
            <div className="bg-slate-50 rounded p-2 border border-slate-200">
              <div className="field-label">Affected</div>
              <div className="mono text-sm font-semibold text-slate-900">
                {result.affected_suppliers?.length || 0}
              </div>
            </div>
            <div className="bg-slate-50 rounded p-2 border border-slate-200">
              <div className="field-label">Time to Impact</div>
              <div className="mono text-sm font-semibold text-slate-900">
                {result.time_to_impact_days}d
              </div>
            </div>
          </div>

          {result.mitigation_actions?.length > 0 && (
            <div>
              <div className="field-label mb-1">Recommended Actions</div>
              <ul className="space-y-1">
                {result.mitigation_actions.slice(0, 3).map((action, i) => (
                  <li key={i} className="text-xs text-slate-600 flex items-start gap-1.5">
                    <span className="text-slate-400 mt-0.5">—</span>
                    {action}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {result.ai_enriched && (
            <div className="mono text-[10px] text-slate-400">
              AI-enriched via {result.ai_model_version || 'model'}
              {result.confidence_score != null && ` · confidence ${(result.confidence_score * 100).toFixed(0)}%`}
            </div>
          )}
        </div>
      )}

      {result && !result.scenario_id && (
        <div className="panel px-4 py-3 text-sm text-red-600">
          Simulation failed. Check the backend logs.
        </div>
      )}
    </div>
  )
}
