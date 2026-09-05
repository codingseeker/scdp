import { useEffect, useCallback } from 'react'
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import SupplierNode from './SupplierNode'

const nodeTypes = { supplierNode: SupplierNode }

const RISK_COLORS = {
  low: '#16a34a',
  medium: '#d97706',
  high: '#dc2626',
  critical: '#7c3aed',
}

const RELATIONSHIP_COLORS = {
  SUPPLIES: '#475569',
  LOGISTICS: '#0e7490',
  ALTERNATIVE: '#16a34a',
}

function layoutNodes(rawNodes) {
  const byTier = { 1: [], 2: [], 3: [] }
  rawNodes.forEach((n) => {
    const t = n.tier || 1
    if (!byTier[t]) byTier[t] = []
    byTier[t].push(n)
  })

  const positioned = []
  const tierY = { 1: 80, 2: 320, 3: 560 }
  const xSpacing = 220

  Object.entries(byTier).forEach(([tier, nodes]) => {
    const y = tierY[parseInt(tier, 10)]
    const totalWidth = (nodes.length - 1) * xSpacing
    const startX = -totalWidth / 2

    nodes.forEach((n, i) => {
      positioned.push({
        id: n.id,
        type: 'supplierNode',
        position: { x: startX + i * xSpacing, y },
        data: { supplier: n },
        draggable: true,
      })
    })
  })

  return positioned
}

function buildEdges(rawEdges) {
  return rawEdges.map((e) => ({
    id: e.id,
    source: e.source,
    target: e.target,
    labelStyle: { fill: '#64748b', fontSize: 10 },
    labelBgStyle: { fill: '#ffffff', fillOpacity: 0.9 },
    style: {
      stroke: RELATIONSHIP_COLORS[e.relationship] || '#475569',
      strokeWidth: e.relationship === 'ALTERNATIVE' ? 1.5 : 1.5,
      strokeDasharray: e.relationship === 'ALTERNATIVE' ? '4,4' : undefined,
      opacity: 0.7,
    },
    markerEnd: {
      type: MarkerType.ArrowClosed,
      color: RELATIONSHIP_COLORS[e.relationship] || '#475569',
      width: 10,
      height: 10,
    },
  }))
}

export default function NetworkGraph({ graphData, onNodeClick, highlightedIds = [] }) {
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])

  useEffect(() => {
    if (!graphData || !graphData.nodes || graphData.nodes.length === 0) {
      setNodes([])
      setEdges([])
      return
    }
    const positioned = layoutNodes(graphData.nodes)
    const highlighted = new Set(highlightedIds)
    const styledNodes = positioned.map((n) => ({
      ...n,
      style: highlighted.size === 0 || highlighted.has(n.id)
        ? {}
        : { opacity: 0.3, filter: 'grayscale(60%)' },
    }))
    setNodes(styledNodes)
    setEdges(buildEdges(graphData.edges || []))
  }, [graphData, highlightedIds])

  const handleNodeClick = useCallback((_, node) => {
    onNodeClick?.(node.data.supplier)
  }, [onNodeClick])

  const hasData = graphData && graphData.nodes && graphData.nodes.length > 0

  return (
    <div className="w-full h-full overflow-hidden bg-white">
      {!hasData ? (
        <div className="h-full flex items-center justify-center text-sm text-slate-400">
          No relationship data available.
        </div>
      ) : (
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          nodeTypes={nodeTypes}
          onNodeClick={handleNodeClick}
          fitView
          fitViewOptions={{ padding: 0.2 }}
          minZoom={0.3}
          maxZoom={2}
          attributionPosition="bottom-right"
        >
          <Background color="#e2e8f0" gap={24} size={1} />
          <Controls
            style={{
              background: '#ffffff',
              border: '1px solid #e2e8f0',
              borderRadius: '6px',
            }}
            showInteractive={false}
          />
          <MiniMap
            nodeColor={(n) => {
              const supplier = n.data?.supplier
              return supplier ? (RISK_COLORS[supplier.risk_level] || '#475569') : '#475569'
            }}
            style={{
              background: '#ffffff',
              border: '1px solid #e2e8f0',
              borderRadius: '6px',
            }}
            maskColor="rgba(148,163,184,0.2)"
          />
        </ReactFlow>
      )}
    </div>
  )
}
