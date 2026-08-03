import React, { useState } from 'react'
import { FiUploadCloud, FiTool, FiBarChart2, FiCode, FiX } from 'react-icons/fi'
import UploadPanel from '../components/DataPanel/UploadPanel'
import CleaningPanel from '../components/DataPanel/CleaningPanel'
import EDAPanel from '../components/DataPanel/EDAPanel'
import CodeEditorPanel from '../components/DataPanel/CodeEditorPanel'

const TABS = [
  { id: 'upload', label: 'Upload', icon: FiUploadCloud, Comp: UploadPanel },
  { id: 'clean', label: 'Clean & Preprocess', icon: FiTool, Comp: CleaningPanel },
  { id: 'eda', label: 'EDA', icon: FiBarChart2, Comp: EDAPanel },
  { id: 'code', label: 'Python Sandbox', icon: FiCode, Comp: CodeEditorPanel },
]

export default function DataStudioPage({ onClose }) {
  const [active, setActive] = useState('upload')
  const Active = TABS.find((t) => t.id === active)?.Comp || UploadPanel

  return (
    <div className="fixed inset-0 z-40 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="w-full max-w-5xl h-[85vh] panel-card flex overflow-hidden">
        <aside className="w-52 shrink-0 border-r border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 p-3">
          <div className="flex items-center justify-between mb-4">
            <p className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Data Studio</p>
            <button onClick={onClose} className="text-slate-400 hover:text-slate-700 dark:hover:text-slate-200"><FiX size={16} /></button>
          </div>
          <nav className="space-y-1">
            {TABS.map((t) => (
              <button
                key={t.id}
                onClick={() => setActive(t.id)}
                className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                  active === t.id
                    ? 'bg-brand-500 text-white'
                    : 'text-slate-500 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700'
                }`}
              >
                <t.icon size={14} /> {t.label}
              </button>
            ))}
          </nav>
        </aside>
        <div className="flex-1 overflow-y-auto">
          <Active />
        </div>
      </div>
    </div>
  )
}
