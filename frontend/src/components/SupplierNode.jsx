import { Handle, Position } from '@xyflow/react'

const RISK_BORDER = {
  low: '#16a34a',
  medium: '#d97706',
  high: '#dc2626',
  critical: '#7c3aed',
}

const RISK_TEXT = {
  low: '#16a34a',
  medium: '#d97706',
  high: '#dc2626',
  critical: '#7c3aed',
}

export default function SupplierNode({ data, selected }) {
  const { supplier } = data
  const border = RISK_BORDER[supplier.risk_level] || '#d97706'
  const text = RISK_TEXT[supplier.risk_level] || '#d97706'

  return (
    <div
      id={`node-${supplier.id}`}
      style={{
        background: selected ? '#f1f5f9' : '#ffffff',
        border: selected ? '2px solid #334155' : `1px solid ${border}`,
        borderRadius: '6px',
        padding: '10px 14px',
        minWidth: '160px',
        cursor: 'pointer',
      }}
    >
      <Handle type="target" position={Position.Top} style={{ background: border, width: 8, height: 8 }} />

      <div className="mb-2">
        <div
          style={{
            fontWeight: 600,
            fontSize: '12px',
            color: '#1e293b',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
          }}
        >
          {supplier.name}
        </div>
        <div className="mono" style={{ fontSize: '10px', color: '#64748b', marginTop: '2px' }}>
          {supplier.id} · {supplier.country}
        </div>
      </div>

      <div className="mb-2">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '3px' }}>
          <span style={{ fontSize: '10px', color: '#64748b' }}>Risk</span>
          <span className="mono" style={{ fontSize: '11px', fontWeight: 600, color: text }}>
            {supplier.risk_score.toFixed(0)}/100
          </span>
        </div>
        <div style={{ height: '3px', background: '#e2e8f0', borderRadius: '2px', overflow: 'hidden' }}>
          <div
            style={{
              width: `${supplier.risk_score}%`,
              height: '100%',
              background: border,
              borderRadius: '2px',
            }}
          />
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '4px', flexWrap: 'wrap' }}>
        <span
          className="mono"
          style={{
            fontSize: '9px',
            padding: '1px 5px',
            borderRadius: '3px',
            background: `${border}15`,
            color: text,
            border: `1px solid ${border}40`,
            fontWeight: 600,
            textTransform: 'uppercase',
          }}
        >
          T{supplier.tier}
        </span>
        <span style={{ fontSize: '9px', color: '#94a3b8', maxWidth: '90px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {supplier.category}
        </span>
      </div>

      <Handle type="source" position={Position.Bottom} style={{ background: border, width: 8, height: 8 }} />
    </div>
  )
}
