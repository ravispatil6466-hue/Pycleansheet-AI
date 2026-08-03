import React, { useEffect, useState, useCallback } from 'react'
import { FiMoreVertical, FiTrash2 } from 'react-icons/fi'
import { fetchChartData } from '../../api/axiosClient'
import { useDashboard } from '../../context/DashboardContext'

export default function TableWidget({ widget }) {
  const { datasetId, globalFilters, removeWidget, setSelectedWidgetId } = useDashboard()
  const [payload, setPayload] = useState(null)
  const [menuOpen, setMenuOpen] = useState(false)
  const cfg = widget.config || {}

  const load = useCallback(async () => {
    if (!datasetId) return
    const res = await fetchChartData(datasetId, {
      chart_type: widget.type, dimensions: cfg.dimensions, y: cfg.y, filters: globalFilters,
    })
    setPayload(res.data)
  }, [datasetId, widget.type, JSON.stringify(cfg), JSON.stringify(globalFilters)])

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
      <div className="flex-1 overflow-auto text-xs">
        {!datasetId && <div className="p-4 text-slate-400">Upload a dataset to see this table</div>}
        {payload && (
          <table className="w-full border-collapse">
            <thead className="sticky top-0 bg-slate-50 dark:bg-slate-800">
              <tr>
                {payload.columns.map((c) => (
                  <th key={c} className="text-left px-2 py-1.5 font-semibold text-slate-500 dark:text-slate-300 border-b border-slate-200 dark:border-slate-700 whitespace-nowrap">{c}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {payload.rows.map((row, i) => (
                <tr key={i} className="hover:bg-slate-50 dark:hover:bg-slate-700/50 odd:bg-slate-50/40 dark:odd:bg-slate-800/40">
                  {payload.columns.map((c) => (
                    <td key={c} className="px-2 py-1 whitespace-nowrap text-slate-600 dark:text-slate-300">{String(row[c] ?? '')}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
