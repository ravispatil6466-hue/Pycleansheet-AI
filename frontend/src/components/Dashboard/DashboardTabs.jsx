import React, { useState } from 'react'
import { FiPlus, FiX, FiEdit2 } from 'react-icons/fi'
import { useDashboard } from '../../context/DashboardContext'

export default function DashboardTabs() {
  const { pages, activePageId, setActivePageId, addPage, removePage, renamePage } = useDashboard()
  const [editingId, setEditingId] = useState(null)
  const [draft, setDraft] = useState('')

  const startEdit = (p) => { setEditingId(p.id); setDraft(p.name) }
  const commitEdit = () => {
    if (editingId && draft.trim()) renamePage(editingId, draft.trim())
    setEditingId(null)
  }

  return (
    <div className="flex items-center gap-1 border-t border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-2 py-1 overflow-x-auto">
      {pages.map((p) => (
        <div
          key={p.id}
          onClick={() => setActivePageId(p.id)}
          onDoubleClick={() => startEdit(p)}
          className={`group flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium cursor-pointer whitespace-nowrap transition-colors ${
            p.id === activePageId
              ? 'bg-brand-500 text-white shadow-sm'
              : 'text-slate-500 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700'
          }`}
        >
          {editingId === p.id ? (
            <input
              autoFocus
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onBlur={commitEdit}
              onKeyDown={(e) => e.key === 'Enter' && commitEdit()}
              className="bg-transparent border-b border-white/60 outline-none w-20 text-xs"
              onClick={(e) => e.stopPropagation()}
            />
          ) : (
            <span>{p.name}</span>
          )}
          <FiEdit2
            size={10}
            className="opacity-0 group-hover:opacity-70"
            onClick={(e) => { e.stopPropagation(); startEdit(p) }}
          />
          {pages.length > 1 && (
            <FiX
              size={12}
              className="opacity-0 group-hover:opacity-70 hover:!opacity-100"
              onClick={(e) => { e.stopPropagation(); removePage(p.id) }}
            />
          )}
        </div>
      ))}
      <button
        onClick={addPage}
        className="flex items-center gap-1 px-2.5 py-1.5 rounded-md text-xs font-medium text-brand-600 dark:text-brand-300 hover:bg-brand-50 dark:hover:bg-slate-700"
      >
        <FiPlus size={13} /> Page
      </button>
    </div>
  )
}
