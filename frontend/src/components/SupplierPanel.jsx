import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer, Tooltip } from 'recharts'
import { X, MapPin, Clock, AlertTriangle, TrendingUp, Newspaper, Cloud, Shield } from 'lucide-react'

const RISK_STYLES = {
  low: 'text-green-700 bg-green-50 border-green-200',
  medium: 'text-amber-700 bg-amber-50 border-amber-200',
  high: 'text-red-700 bg-red-50 border-red-200',
  critical: 'text-red-700 bg-red-50 border-red-200',
}

function RiskBadge({ level }) {
  const cls = RISK_STYLES[level] || RISK_STYLES.medium
  return (
    <span className={`text-xs font-semibold uppercase tracking-wider px-2 py-0.5 rounded border ${cls}`}>
      {level}
    </span>
  )
}

function SentimentDot({ sentiment }) {
  const color = { positive: '#16a34a', neutral: '#94a3b8', negative: '#dc2626' }[sentiment] || '#94a3b8'
  return <span style={{ width: 6, height: 6, borderRadius: '50%', background: color, display: 'inline-block', flexShrink: 0, marginTop: 5 }} />
}

export default function SupplierPanel({ detail, onClose }) {
  if (!detail) return null
  const { supplier, news, weather_alerts, upstream_suppliers, downstream_customers, risk_breakdown } = detail

  const radarData = Object.entries(risk_breakdown).map(([key, value]) => ({
    subject: key.charAt(0).toUpperCase() + key.slice(1),
    value,
    fullMark: 50,
  }))

  return (
    <div className="card h-full flex flex-col overflow-hidden animate-slide-in rounded-none border-0">
      {/* Header */}
      <div className="px-4 py-3 border-b border-slate-200 flex items-start justify-between gap-2 flex-shrink-0">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h2 className="text-sm font-semibold text-slate-900">{supplier.name}</h2>
            <RiskBadge level={supplier.risk_level} />
          </div>
          <div className="flex items-center gap-3 text-xs text-slate-500">
            <span className="flex items-center gap-1"><MapPin size={11} />{supplier.city}, {supplier.country}</span>
            <span className="text-slate-300">·</span>
            <span>Tier {supplier.tier}</span>
            <span className="text-slate-300">·</span>
            <span>{supplier.category}</span>
          </div>
        </div>
        <button
          id="close-supplier-panel"
          onClick={onClose}
          className="text-slate-400 hover:text-slate-700 transition-colors p-1 rounded-lg hover:bg-slate-100 flex-shrink-0"
        >
          <X size={16} />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Key metrics */}
        <div className="grid grid-cols-2 gap-2">
          {[
            { label: 'Risk Score', value: `${supplier.risk_score.toFixed(1)}`, icon: <AlertTriangle size={13} />, color: supplier.risk_score >= 75 ? '#dc2626' : supplier.risk_score >= 60 ? '#dc2626' : supplier.risk_score >= 40 ? '#d97706' : '#16a34a' },
            { label: 'Criticality', value: `${supplier.criticality.toFixed(0)}`, icon: <TrendingUp size={13} />, color: '#2563eb' },
            { label: 'Lead Time', value: `${supplier.lead_time_days}d`, icon: <Clock size={13} />, color: '#64748b' },
            { label: 'Dependency', value: `${supplier.revenue_dependency.toFixed(1)}%`, icon: <Shield size={13} />, color: '#d97706' },
          ].map(m => (
            <div key={m.label} className="bg-slate-50 rounded-lg p-3 border border-slate-200">
              <div className="flex items-center gap-1 text-xs mb-1">
                <span style={{ color: m.color }}>{m.icon}</span>
                <span className="text-slate-500">{m.label}</span>
              </div>
              <div className="text-base font-semibold font-mono" style={{ color: m.color }}>{m.value}</div>
            </div>
          ))}
        </div>

        {/* Risk radar */}
        {radarData.length > 0 && (
          <div>
            <p className="section-title">Risk Breakdown</p>
            <div className="bg-slate-50 rounded-lg p-3 border border-slate-200">
              <ResponsiveContainer width="100%" height={160}>
                <RadarChart data={radarData} margin={{ top: 5, right: 20, bottom: 5, left: 20 }}>
                  <PolarGrid stroke="#e2e8f0" />
                  <PolarAngleAxis dataKey="subject" tick={{ fill: '#64748b', fontSize: 10 }} />
                  <Radar name="Risk" dataKey="value" stroke="#2563eb" fill="#2563eb" fillOpacity={0.15} />
                  <Tooltip
                    contentStyle={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '8px', fontSize: 12 }}
                    labelStyle={{ color: '#475569' }}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* Dependencies */}
        <div className="grid grid-cols-2 gap-2">
          {upstream_suppliers.length > 0 && (
            <div>
              <p className="section-title">Upstream ({upstream_suppliers.length})</p>
              <div className="space-y-1">
                {upstream_suppliers.slice(0, 4).map(id => (
                  <div key={id} className="text-xs text-slate-500 bg-slate-50 rounded px-2 py-1 font-mono border border-slate-200">{id}</div>
                ))}
              </div>
            </div>
          )}
          {downstream_customers.length > 0 && (
            <div>
              <p className="section-title">Downstream ({downstream_customers.length})</p>
              <div className="space-y-1">
                {downstream_customers.slice(0, 4).map(id => (
                  <div key={id} className="text-xs text-slate-500 bg-slate-50 rounded px-2 py-1 font-mono border border-slate-200">{id}</div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Weather alerts */}
        {weather_alerts?.length > 0 && (
          <div>
            <p className="section-title flex items-center gap-1"><Cloud size={11} /> Weather Alerts</p>
            <div className="space-y-2">
              {weather_alerts.map((w, i) => (
                <div key={i} className="bg-amber-50 border border-amber-200 rounded-lg p-3">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-semibold text-amber-700">{w.event_type}</span>
                    <span className="text-xs text-amber-700 bg-amber-100 px-1.5 py-0.5 rounded">{w.severity}</span>
                  </div>
                  <div className="text-xs text-slate-600">{w.location}</div>
                  {w.eta_hours > 0 && (
                    <div className="text-xs text-slate-500 mt-1">ETA: {w.eta_hours}h</div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* News */}
        {news?.length > 0 && (
          <div>
            <p className="section-title flex items-center gap-1"><Newspaper size={11} /> Recent Intelligence</p>
            <div className="space-y-2">
              {news.map((item, i) => (
                <div key={i} className="bg-slate-50 rounded-lg p-3 border border-slate-200">
                  <div className="flex items-start gap-2">
                    <SentimentDot sentiment={item.sentiment} />
                    <div className="flex-1 min-w-0">
                      <p className="text-xs text-slate-800 leading-tight mb-1">{item.title}</p>
                      <div className="flex items-center gap-2 text-xs text-slate-500">
                        <span>{item.source}</span>
                        <span>·</span>
                        <span className="font-mono">{new Date(item.published_at).toLocaleDateString()}</span>
                        <span className="ml-auto text-amber-600 font-mono">{(item.risk_relevance * 100).toFixed(0)}%</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Alternatives count */}
        <div className="bg-slate-50 rounded-lg p-3 border border-slate-200 flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-500 mb-0.5">Available Alternatives</p>
            <p className="text-lg font-semibold text-brand-600">{supplier.alternatives_count}</p>
          </div>
          <div className="text-3xl opacity-30">{supplier.alternatives_count === 0 ? '⚠️' : '✅'}</div>
        </div>
      </div>
    </div>
  )
}