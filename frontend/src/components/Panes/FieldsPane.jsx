import React from 'react'
import { FiHash, FiType, FiCalendar, FiToggleLeft, FiFilter } from 'react-icons/fi'
import { useDashboard } from '../../context/DashboardContext'

const KIND_ICON = { numeric: FiHash, categorical: FiType, datetime: FiCalendar, boolean: FiToggleLeft }

export default function FieldsPane() {
  const { datasetMeta, addWidget, updateWidgetConfig } = useDashboard()
  const cols = datasetMeta?.columns_meta || {}

  const addSlicerFor = (col) => {
    const id = addWidget('slicer', { title: `Filter: ${col}` })
    updateWidgetConfig(id, { column: col })
  }

  return (
    <aside className="w-56 shrink-0 border-r border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 overflow-y-auto">
      <div className="px-3 py-2.5 border-b border-slate-100 dark:border-slate-700">
        <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Fields</h2>
      </div>
      {!datasetMeta && (
        <p className="p-3 text-[11px] text-slate-400">Upload a dataset to see its fields here.</p>
      )}
      <ul className="p-1.5">
        {Object.entries(cols).map(([name, meta]) => {
          const Icon = KIND_ICON[meta.kind] || FiType
          return (
            <li key={name} className="group flex items-center justify-between gap-1 px-2 py-1.5 rounded-md hover:bg-slate-50 dark:hover:bg-slate-700 text-xs text-slate-600 dark:text-slate-300">
              <span className="flex items-center gap-2 truncate">
                <Icon size={12} className="text-brand-500 shrink-0" />
                <span className="truncate" title={name}>{name}</span>
              </span>
              <button
                title="Add as slicer"
                onClick={() => addSlicerFor(name)}
                className="opacity-0 group-hover:opacity-100 text-slate-400 hover:text-brand-500"
              >
                <FiFilter size={12} />
              </button>
            </li>
          )
        })}
      </ul>
    </aside>
  )
}
