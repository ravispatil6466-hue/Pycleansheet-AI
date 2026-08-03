import React, { useEffect, useState, useCallback } from 'react'
import { FiTrendingUp, FiTrash2, FiMoreVertical } from 'react-icons/fi'
import { fetchChartData } from '../../api/axiosClient'
import { useDashboard } from '../../context/DashboardContext'
import { getPalette } from '../../utils/chartConfig'

function formatNumber(n) {
  if (n === null || n === undefined || Number.isNaN(n)) return '—'
  if (Math.abs(n) >= 1_000_000) return (n / 1_000_000).toFixed(2) + 'M'
  if (Math.abs(n) >= 1_000) return (n / 1_000).toFixed(2) + 'K'
  return Number.isInteger(n) ? n.toString() : n.toFixed(2)
}

export default function KPICard({ widget }) {
  const { datasetId, globalFilters, removeWidget, setSelectedWidgetId, colorPalette } = useDashboard()
  const [value, setValue] = useState(null)
  const [menuOpen, setMenuOpen] = useState(false)
  const cfg = widget.config || {}
  const palette = getPalette(widget.style?.colorScheme || colorPalette)

  const load = useCallback(async () => {
    if (!datasetId || !cfg.values) return
    const res = await fetchChartData(datasetId, {
      chart_type: 'kpi', values: cfg.values, aggregation: cfg.aggregation || 'sum', filters: globalFilters,
    })
    setValue(res.data.value)
  }, [datasetId, cfg.values, cfg.aggregation, JSON.stringify(globalFilters)])

  useEffect(() => { load() }, [load])

  return (
    <div className="widget-card" onMouseDown={() => setSelectedWidgetId(widget.id)}>
      <div className="widget-header">
        <span className="truncate">{widget.title}</span>
        <div className="relative">
          <button onClick={(e) => { e.stopPropagation(); setMenuOpen((v) => !v) }} className="hover:text-slate-700 dark:hover:text-slate-200">
            <FiMoreVertical size={14} />
          </button>
          {menuOpen && (
            <div className="absolute right-0 top-5 z-20 w-32 panel-card py-1 text-xs" onMouseLeave={() => setMenuOpen(false)}>
              <button onClick={() => removeWidget(widget.id)} className="flex w-full items-center gap-2 px-3 py-1.5 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/30">
                <FiTrash2 size={12} /> Delete
              </button>
            </div>
          )}
        </div>
      </div>
      <div className="flex-1 flex flex-col items-center justify-center gap-1 px-3">
        {!datasetId || !cfg.values ? (
          <span className="text-[11px] text-slate-400 text-center">Set a value field in the formatting pane</span>
        ) : (
          <>
            <div className="flex items-center gap-2" style={{ color: palette[0] }}>
              <FiTrendingUp size={20} />
              <span className="text-3xl font-bold tracking-tight">{formatNumber(value)}</span>
            </div>
            <span className="text-[11px] uppercase tracking-wide text-slate-400">{cfg.aggregation || 'sum'} of {cfg.values}</span>
          </>
        )}
      </div>
    </div>
  )
}
