import React, { useEffect, useState, useCallback, useMemo } from 'react'
import { FiMoreVertical, FiTrash2, FiFilter } from 'react-icons/fi'
import { previewDataset } from '../../api/axiosClient'
import { useDashboard } from '../../context/DashboardContext'

export default function SlicerWidget({ widget }) {
  const { datasetId, globalFilters, setGlobalFilters, removeWidget, setSelectedWidgetId } = useDashboard()
  const [options, setOptions] = useState([])
  const [menuOpen, setMenuOpen] = useState(false)
  const column = widget.config?.column

  const load = useCallback(async () => {
    if (!datasetId || !column) return
    const res = await previewDataset(datasetId, 1000, 0)
    const vals = Array.from(new Set(res.data.rows.map((r) => r[column]))).filter((v) => v !== null && v !== undefined)
    setOptions(vals.sort())
  }, [datasetId, column])

  useEffect(() => { load() }, [load])

  const activeFilter = useMemo(
    () => globalFilters.find((f) => f.column === column),
    [globalFilters, column]
  )
  const selected = activeFilter?.value || []

  const toggleValue = (val) => {
    const current = new Set(selected)
    if (current.has(val)) current.delete(val)
    else current.add(val)
    const next = Array.from(current)
    setGlobalFilters((prev) => {
      const others = prev.filter((f) => f.column !== column)
      if (next.length === 0) return others
      return [...others, { column, operator: 'in', value: next }]
    })
  }

  return (
    <div className="widget-card" onMouseDown={() => setSelectedWidgetId(widget.id)}>
      <div className="widget-header">
        <span className="truncate flex items-center gap-1"><FiFilter size={11} /> {widget.title}</span>
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
      <div className="flex-1 overflow-y-auto p-2 text-xs">
        {!column && <div className="text-slate-400 px-2 py-3">Select a field in the formatting pane</div>}
        {column && options.map((opt) => (
          <label key={String(opt)} className="flex items-center gap-2 px-2 py-1 rounded hover:bg-slate-50 dark:hover:bg-slate-700 cursor-pointer">
            <input
              type="checkbox"
              checked={selected.includes(opt)}
              onChange={() => toggleValue(opt)}
              className="accent-brand-500"
            />
            <span className="truncate text-slate-600 dark:text-slate-300">{String(opt)}</span>
          </label>
        ))}
      </div>
    </div>
  )
}
