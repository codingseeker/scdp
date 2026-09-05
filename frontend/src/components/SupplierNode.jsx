import { Handle, Position } from '@xyflow/react'

const RISK_COLORS = {
  low: { bg: '#16a34a', text: '#16a34a', border: '#bbf7d0' },
  medium: { bg: '#d97706', text: '#d97706', border: '#fde68a' },
  high: { bg: '#dc2626', text: '#dc2626', border: '#fecaca' },
  critical: { bg: '#7c3aed', text: '#7c3aed', border: '#ddd6fe' },
}

const CATEGORY_ICONS = {
  'Electronics': '⚡',
  'Metal Components': '⚙️',
  'Logistics': '🚢',
  'Chemicals': '🧪',
  'Semiconductors': '💾',
  'Raw Materials': '⛏️',
  'Textiles': '🧵',
  'Assembly': '🔧',
  'default': '📦',
}

export default function SupplierNode({ data, selected }) {
  const { supplier } = data
  const colors = RISK_COLORS[supplier.risk_level] || RISK_COLORS.medium
  const icon = CATEGORY_ICONS[supplier.category] || CATEGORY_ICONS.default

  return (
    <div
      id={`node-${supplier.id}`}
      style={{
        background: selected ? '#eff6ff' : '#ffffff',
        border: selected ? '2px solid #2563eb' : `1.5px solid ${colors.border}`,
        borderRadius: '8px',
        padding: '10px 14px',
        minWidth: '160px',
        transition: 'border-color 0.2s ease, background 0.2s ease',
        cursor: 'pointer',
      }}
    >
      <Handle type="target" position={Position.Top} style={{ background: colors.bg, border: '1px solid #ffffff', width: 8, height: 8 }} />

      {/* Header */}
      <div className="flex items-center gap-2 mb-2">
        <span style={{ fontSize: '16px' }}>{icon}</span>
        <div className="flex-1 min-w-0">
          <div
            style={{
              fontWeight: 500,
              fontSize: '12px',
              color: '#0f172a',
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
            }}
          >
            {supplier.name}
          </div>
          <div style={{ fontSize: '10px', color: '#64748b', marginTop: '1px' }}>
            {supplier.country} · T{supplier.tier}
          </div>
        </div>
      </div>

      {/* Risk meter */}
      <div style={{ marginBottom: '6px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '3px' }}>
          <span style={{ fontSize: '10px', color: '#64748b' }}>Risk Score</span>
          <span style={{ fontSize: '11px', fontWeight: 600, color: colors.text, fontFamily: 'ui-monospace, SFMono-Regular, Menlo, monospace' }}>
            {supplier.risk_score.toFixed(0)}
          </span>
        </div>
        <div style={{ height: '4px', background: '#e2e8f0', borderRadius: '2px', overflow: 'hidden' }}>
          <div
            style={{
              width: `${supplier.risk_score}%`,
              height: '100%',
              background: colors.bg,
              borderRadius: '2px',
              transition: 'width 0.5s ease',
            }}
          />
        </div>
      </div>

      {/* Tags */}
      <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
        <span
          style={{
            fontSize: '9px',
            padding: '2px 6px',
            borderRadius: '4px',
            background: `${colors.bg}15`,
            color: colors.text,
            border: `1px solid ${colors.border}`,
            fontWeight: 600,
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
          }}
        >
          {supplier.risk_level}
        </span>
        {supplier.active_threats > 0 && (
          <span
            style={{
              fontSize: '9px',
              padding: '2px 6px',
              borderRadius: '4px',
              background: 'rgba(220,38,38,0.08)',
              color: '#dc2626',
              border: '1px solid rgba(220,38,38,0.2)',
              fontWeight: 600,
            }}
          >
            ⚠ {supplier.active_threats}
          </span>
        )}
      </div>

      <Handle type="source" position={Position.Bottom} style={{ background: colors.bg, border: '1px solid #ffffff', width: 8, height: 8 }} />
    </div>
  )
}