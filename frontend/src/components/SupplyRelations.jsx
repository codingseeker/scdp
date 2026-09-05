import { Link } from 'react-router-dom'

const DEP_COLORS = {
  upstream: {
    title: 'Upstream Supplies',
    empty: 'No upstream suppliers reported.',
    tone: 'text-slate-700',
  },
  downstream: {
    title: 'Downstream Customers',
    empty: 'No downstream customers reported.',
    tone: 'text-slate-700',
  },
}

export default function SupplyRelations({ upstream, downstream }) {
  const hasUpstream = upstream && upstream.length > 0
  const hasDownstream = downstream && downstream.length > 0

  if (!hasUpstream && !hasDownstream) {
    return null
  }

  const rows = []
  if (hasUpstream) {
    rows.push({
      label: DEP_COLORS.upstream.title,
      ids: upstream,
      empty: DEP_COLORS.upstream.empty,
    })
  }
  if (hasDownstream) {
    rows.push({
      label: DEP_COLORS.downstream.title,
      ids: downstream,
      empty: DEP_COLORS.downstream.empty,
    })
  }

  return (
    <div className="space-y-3">
      {rows.map((r) => (
        <div key={r.label}>
          <div className="field-label mb-1.5">{r.label} ({r.ids.length})</div>
          <div className="flex flex-wrap gap-1.5">
            {r.ids.map((id) => (
              <Link
                key={id}
                to={`/entity/${id}`}
                className="mono text-[11px] text-slate-600 bg-slate-50 border border-slate-200 rounded px-2 py-0.5 hover:bg-slate-100 hover:border-slate-300 hover:text-slate-900 transition-colors"
              >
                {id}
              </Link>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
