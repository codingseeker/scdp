const SENTIMENT_COLOR = {
  positive: '#16a34a',
  neutral: '#94a3b8',
  negative: '#dc2626',
}

function SentimentIndicator({ sentiment }) {
  const color = SENTIMENT_COLOR[sentiment] || '#94a3b8'
  return (
    <span
      title={`Sentiment: ${sentiment}`}
      style={{ width: 8, height: 8, borderRadius: '50%', background: color, display: 'inline-block', flexShrink: 0 }}
    />
  )
}

export default function IntelligenceSection({ news, weatherAlerts, sourceLabel }) {
  const hasNews = news && news.length > 0
  const hasWeather = weatherAlerts && weatherAlerts.length > 0

  if (!hasNews && !hasWeather) {
    return (
      <div className="panel px-4 py-8 text-center text-sm text-slate-400">
        No intelligence data is currently available for this entity.
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {sourceLabel && (
        <div className="mono text-[10px] text-slate-400">
          Source: {sourceLabel}
        </div>
      )}

      {hasNews && (
        <section>
          <h3 className="panel-title mb-2">Intelligence — {news.length} item{news.length === 1 ? '' : 's'}</h3>
          <div className="space-y-2">
            {news.map((n, i) => (
              <div key={i} className="panel px-4 py-3">
                <div className="flex items-start gap-2">
                  <div className="pt-1"><SentimentIndicator sentiment={n.sentiment} /></div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-slate-800 leading-snug">{n.title}</p>
                    <div className="flex items-center gap-2 mt-1 text-xs text-slate-500">
                      <span>{n.source}</span>
                      <span>·</span>
                      <span className="mono">{formatDate(n.published_at)}</span>
                      <span className="ml-auto mono text-amber-600">
                        relevance {(n.risk_relevance * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {hasWeather && (
        <section>
          <h3 className="panel-title mb-2">Weather Alerts — {weatherAlerts.length}</h3>
          <div className="space-y-2">
            {weatherAlerts.map((w, i) => (
              <div key={i} className="panel px-4 py-3 border-l-2 border-l-amber-400">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-semibold text-slate-800">{w.event_type}</span>
                  <span className="mono text-[11px] text-amber-700 bg-amber-50 border border-amber-200 rounded px-1.5 py-0.5">
                    {w.severity}
                  </span>
                </div>
                <div className="text-xs text-slate-600">{w.location}</div>
                {w.eta_hours > 0 && (
                  <div className="text-xs text-slate-500 mt-1 mono">ETA: {w.eta_hours}h</div>
                )}
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}

function formatDate(iso) {
  if (!iso) return 'unknown'
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso
  return d.toLocaleDateString()
}
