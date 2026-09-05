import { useCallback, useEffect, useState } from 'react'
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
  SUPPLIES: '#2563eb',
  LOGISTICS: '#0e7490',
  ALTERNATIVE: '#16a34a',
}

// Layout: arrange by tier
function layoutNodes(rawNodes) {
  const byTier = { 1: [], 2: [], 3: [] }
  rawNodes.forEach(n => {
    const t = n.tier || 1
    if (!byTier[t]) byTier[t] = []
    byTier[t].push(n)
  })

  const positioned = []
  const tierY = { 1: 80, 2: 320, 3: 560 }
  const xSpacing = 220

  Object.entries(byTier).forEach(([tier, nodes]) => {
    const y = tierY[parseInt(tier)]
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
  return rawEdges.map(e => ({
    id: e.id,
    source: e.source,
    target: e.target,
    label: e.relationship === 'ALTERNATIVE' ? 'ALT' : undefined,
    labelStyle: { fill: '#64748b', fontSize: 10 },
    labelBgStyle: { fill: '#ffffff', fillOpacity: 0.9 },
    animated: e.relationship === 'LOGISTICS',
    style: {
      stroke: RELATIONSHIP_COLORS[e.relationship] || '#2563eb',
      strokeWidth: e.relationship === 'ALTERNATIVE' ? 1.5 : 2,
      strokeDasharray: e.relationship === 'ALTERNATIVE' ? '5,4' : undefined,
      opacity: 0.7,
    },
    markerEnd: {
      type: MarkerType.ArrowClosed,
      color: RELATIONSHIP_COLORS[e.relationship] || '#2563eb',
      width: 12,
      height: 12,
    },
  }))
}

export default function NetworkGraph({ graphData, onNodeClick, highlightedIds = [] }) {
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])

  useEffect(() => {
    if (!graphData) return
    const positioned = layoutNodes(graphData.nodes)
    // Apply highlight
    const highlighted = new Set(highlightedIds)
    const styledNodes = positioned.map(n => ({
      ...n,
      style: highlighted.size === 0 || highlighted.has(n.id)
        ? {}
        : { opacity: 0.35, filter: 'grayscale(60%)' },
    }))
    setNodes(styledNodes)
    setEdges(buildEdges(graphData.edges))
  }, [graphData, highlightedIds])

  const handleNodeClick = useCallback((_, node) => {
    onNodeClick?.(node.data.supplier)
  }, [onNodeClick])

  return (
    <div className="w-full h-full overflow-hidden bg-white">
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
            borderRadius: '8px',
          }}
          showInteractive={false}
        />
        <MiniMap
          nodeColor={(n) => {
            const supplier = n.data?.supplier
            return supplier ? (RISK_COLORS[supplier.risk_level] || '#2563eb') : '#2563eb'
          }}
          style={{
            background: '#ffffff',
            border: '1px solid #e2e8f0',
            borderRadius: '8px',
          }}
          maskColor="rgba(148,163,184,0.2)"
        />
      </ReactFlow>
    </div>
  )
}