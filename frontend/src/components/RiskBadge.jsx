const STYLES = {
  low: 'risk-badge-low',
  medium: 'risk-badge-medium',
  high: 'risk-badge-high',
  critical: 'risk-badge-critical',
}

export default function RiskBadge({ level }) {
  if (!level) return null
  return (
    <span className={`inline-block uppercase tracking-wider ${STYLES[level] || STYLES.medium}`}>
      {level}
    </span>
  )
}
