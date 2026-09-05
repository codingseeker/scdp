import { useState, useEffect, useCallback, useRef } from 'react'
import { useNavigate, useSearchParams, Link } from 'react-router-dom'
import SearchBar from '../components/SearchBar'
import RiskBadge from '../components/RiskBadge'
import { supplierApi, metricsApi, networkApi } from '../services/api'

function RiskScore({ score, level }) {
  const color = score >= 75 ? '#dc2626' : score >= 50 ? '#d97706' : '#16a34a'
  return (
    <span className="mono text-sm font-semibold" style={{ color }}>
      {score.toFixed(1)}
    </span>
  )
}

export default function SearchPage() {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const urlQuery = searchParams.get('q') || ''
  const [query, setQuery] = useState(urlQuery)
  const [items, setItems] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(urlQuery.length > 0)
  const [error, setError] = useState(null)
  const [overview, setOverview] = useState(null)
  const lastSearchedRef = useRef(null)

  useEffect(() => {
    let cancelled = false
    Promise.all([
      metricsApi.getMetrics().catch(() => null),
      networkApi.getGraph().catch(() => null),
    ]).then(([met, graph]) => {
      if (cancelled) return
      setOverview({ metrics: met, nodeCount: graph?.nodes?.length || 0 })
    })
    return () => { cancelled = true }
  }, [])

  const handleSearch = useCallback(async (q) => {
    lastSearchedRef.current = q
    setQuery(q)
    setSearchParams({ q }, { replace: true })
    setSearched(true)
    setLoading(true)
    setError(null)
    try {
      const res = await supplierApi.list({ search: q, page: 1, page_size: 50, sort_by: 'risk_score', order: 'desc' })
      setItems(res.items || [])
      setTotal(res.total || 0)
    } catch (err) {
      setError('Search request failed.')
      setItems([])
      setTotal(0)
    } finally {
      setLoading(false)
    }
  }, [setSearchParams])

  useEffect(() => {
    if (urlQuery && lastSearchedRef.current !== urlQuery) {
      lastSearchedRef.current = urlQuery
      handleSearch(urlQuery)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [urlQuery])

  const openEntity = (id) => navigate(`/entity/${id}`)

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-lg font-semibold text-slate-900 mb-1">
          Supply Chain Intelligence
        </h1>
        <p className="text-sm text-slate-500">
          Search for a supplier, country, or category to begin an investigation.
        </p>
      </div>

      <div className="mb-6">
        <SearchBar onSearch={handleSearch} initialValue={query} autoFocus size="lg" />
      </div>

      {overview?.metrics && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-8">
          {[
            { label: 'Network Health', value: `${overview.metrics.network_health_score}%` },
            { label: 'Active Threats', value: overview.metrics.active_threats },
            { label: 'High Risk Suppliers', value: overview.metrics.high_risk_suppliers },
            { label: 'Entities', value: overview.nodeCount },
          ].map((m) => (
            <div key={m.label} className="panel px-4 py-3">
              <div className="field-label mb-1">{m.label}</div>
              <div className="text-xl font-semibold text-slate-900 mono">{m.value}</div>
            </div>
          ))}
        </div>
      )}

      {error && (
        <div className="panel px-4 py-3 text-sm text-red-600">
          {error}
        </div>
      )}

      {loading && (
        <div className="text-sm text-slate-400">Searching…</div>
      )}

      {!loading && searched && !error && total === 0 && (
        <div className="panel px-4 py-8 text-center text-sm text-slate-400">
          No matching entities found.
        </div>
      )}

      {!loading && searched && total > 0 && (
        <div>
          <div className="text-sm text-slate-500 mb-2">
            {total} result{total === 1 ? '' : 's'} for “{query}”
          </div>
          <div className="panel overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs text-slate-500 border-b border-slate-200 bg-slate-50">
                  <th className="px-4 py-2 font-medium">Supplier</th>
                  <th className="px-4 py-2 font-medium">Type</th>
                  <th className="px-4 py-2 font-medium">Location</th>
                  <th className="px-4 py-2 font-medium text-right">Risk</th>
                  <th className="px-4 py-2 font-medium text-right">Tier</th>
                </tr>
              </thead>
              <tbody>
                {items.map((s) => (
                  <tr
                    key={s.id}
                    onClick={() => openEntity(s.id)}
                    className="border-b border-slate-100 last:border-0 hover:bg-slate-50 cursor-pointer"
                  >
                    <td className="px-4 py-2.5">
                      <Link to={`/entity/${s.id}`} className="font-medium text-slate-900 hover:text-slate-600">
                        {s.name}
                      </Link>
                      <div className="mono text-[10px] text-slate-400">{s.id}</div>
                    </td>
                    <td className="px-4 py-2.5 text-slate-600">{s.category}</td>
                    <td className="px-4 py-2.5 text-slate-600">{s.city}, {s.country}</td>
                    <td className="px-4 py-2.5 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <RiskScore score={s.risk_score} level={s.risk_level} />
                        <RiskBadge level={s.risk_level} />
                      </div>
                    </td>
                    <td className="px-4 py-2.5 text-right mono text-slate-500">T{s.tier}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
