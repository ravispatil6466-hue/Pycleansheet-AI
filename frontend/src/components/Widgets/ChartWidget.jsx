import React, { useEffect, useRef, useState, useCallback } from 'react'
import Plot from 'react-plotly.js'
import { FiMoreVertical, FiDownload, FiTrash2, FiImage } from 'react-icons/fi'
import { fetchChartData } from '../../api/axiosClient'
import { buildFigure, getPalette } from '../../utils/chartConfig'
import { useDashboard } from '../../context/DashboardContext'
import { useTheme } from '../../context/ThemeContext'
import { exportPlotlyImage } from '../../utils/exportUtils'

export default function ChartWidget({ widget }) {
  const { datasetId, globalFilters, removeWidget, setSelectedWidgetId, colorPalette } = useDashboard()
  const { theme } = useTheme()
  const [payload, setPayload] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)
  const plotRef = useRef(null)

  const cfg = widget.config || {}

  const load = useCallback(async () => {
    if (!datasetId) return
    setLoading(true)
    setError(null)
    try {
      const res = await fetchChartData(datasetId, {
        chart_type: widget.type,
        x: cfg.x, y: cfg.y, color: cfg.color, size: cfg.size,
        aggregation: cfg.aggregation || 'sum',
        filters: globalFilters,
        top_n: cfg.topN,
        values: cfg.values, names: cfg.names,
        theta: cfg.theta, r: cfg.r,
        path: cfg.path, dimensions: cfg.dimensions,
      })
      setPayload(res.data)
    } catch (e) {
      setError(e?.response?.data?.detail || 'Failed to load chart data')
    } finally {
      setLoading(false)
    }
  }, [datasetId, widget.type, JSON.stringify(cfg), JSON.stringify(globalFilters)])

  useEffect(() => { load() }, [load])

  const palette = getPalette(widget.style?.colorScheme || colorPalette)
  const dark = theme === 'dark'

  let figure = { data: [], layout: {} }
  if (payload && !payload.error) {
    figure = buildFigure(widget.type, payload, {
      title: '', dark, palette, showLegend: widget.style?.showLegend !== false,
    })
  }

  return (
    <div className="widget-card" onMouseDown={() => setSelectedWidgetId(widget.id)}>
      <div className="widget-header">
        <span className="truncate">{widget.title}</span>
        <div className="relative flex items-center gap-1">
          <button onClick={(e) => { e.stopPropagation(); setMenuOpen((v) => !v) }} className="hover:text-slate-700 dark:hover:text-slate-200">
            <FiMoreVertical size={14} />
          </button>
          {menuOpen && (
            <div className="absolute right-0 top-5 z-20 w-40 panel-card py-1 text-xs" onMouseLeave={() => setMenuOpen(false)}>
              <button
                onClick={() => exportPlotlyImage(plotRef.current?.el, 'png', widget.title)}
                className="flex w-full items-center gap-2 px-3 py-1.5 hover:bg-slate-50 dark:hover:bg-slate-700"
              >
                <FiImage size={12} /> Export PNG
              </button>
              <button
                onClick={() => exportPlotlyImage(plotRef.current?.el, 'svg', widget.title)}
                className="flex w-full items-center gap-2 px-3 py-1.5 hover:bg-slate-50 dark:hover:bg-slate-700"
              >
                <FiDownload size={12} /> Export SVG
              </button>
              <button
                onClick={() => removeWidget(widget.id)}
                className="flex w-full items-center gap-2 px-3 py-1.5 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/30"
              >
                <FiTrash2 size={12} /> Delete
              </button>
            </div>
          )}
        </div>
      </div>
      <div className="flex-1 min-h-0 relative">
        {loading && <div className="absolute inset-0 flex items-center justify-center text-xs text-slate-400">Loading…</div>}
        {error && <div className="absolute inset-0 flex items-center justify-center text-xs text-red-400 px-4 text-center">{error}</div>}
        {!datasetId && <div className="absolute inset-0 flex items-center justify-center text-xs text-slate-400 px-4 text-center">Upload a dataset to see this visual</div>}
        {payload && !error && datasetId && (
          <Plot
            ref={plotRef}
            data={figure.data}
            layout={figure.layout}
            config={{ displayModeBar: false, responsive: true }}
            style={{ width: '100%', height: '100%' }}
            useResizeHandler
          />
        )}
      </div>
    </div>
  )
}
