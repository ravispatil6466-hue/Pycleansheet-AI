import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { FiPlus, FiLayout, FiClock, FiZap } from 'react-icons/fi'
import { listDashboards } from '../api/axiosClient'
import ThemeToggle from '../components/Common/ThemeToggle'

export default function HomePage() {
  const navigate = useNavigate()
  const [dashboards, setDashboards] = useState([])

  useEffect(() => {
    listDashboards().then((res) => setDashboards(res.data)).catch(() => {})
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-950">
      <header className="flex items-center justify-between px-8 py-5">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-brand-500 to-brand-800 flex items-center justify-center text-white font-bold text-sm">P</div>
          <span className="font-bold text-slate-700 dark:text-slate-100">Pycleansheet AI</span>
        </div>
        <ThemeToggle />
      </header>

      <main className="max-w-5xl mx-auto px-8 pt-10 pb-20">
        <div className="flex items-center gap-2 text-brand-600 dark:text-brand-300 text-xs font-semibold uppercase tracking-wider mb-3">
          <FiZap size={14} /> Intelligent Data Cleaning, Analytics & Dashboard Platform
        </div>
        <h1 className="text-3xl md:text-4xl font-extrabold text-slate-800 dark:text-slate-50 max-w-2xl leading-tight">
          Clean, explore, and visualize your data — no code required (unless you want it).
        </h1>
        <p className="mt-3 text-sm text-slate-500 dark:text-slate-400 max-w-xl">
          Upload a dataset, let AI guide your cleanup, and build a true drag-and-drop dashboard
          with 20+ chart types — all in your browser.
        </p>

        <div className="mt-8 flex gap-3">
          <button
            onClick={() => navigate('/dashboard/new')}
            className="flex items-center gap-2 px-5 py-3 rounded-xl bg-brand-500 text-white text-sm font-semibold hover:bg-brand-600 shadow-lg shadow-brand-500/20"
          >
            <FiPlus /> New Dashboard
          </button>
        </div>

        <div className="mt-14">
          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-1.5">
            <FiClock size={12} /> Recent Dashboards
          </h2>
          {dashboards.length === 0 && (
            <p className="text-sm text-slate-400">No dashboards yet — create your first one above.</p>
          )}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            {dashboards.map((d) => (
              <button
                key={d.id}
                onClick={() => navigate(`/dashboard/${d.id}`)}
                className="text-left panel-card p-4 hover:border-brand-400 hover:shadow-md transition-all"
              >
                <div className="flex items-center gap-2 mb-2 text-brand-500">
                  <FiLayout size={16} />
                  <span className="text-sm font-semibold text-slate-700 dark:text-slate-100 truncate">{d.name}</span>
                </div>
                <p className="text-[11px] text-slate-400">Updated {new Date(d.updated_at).toLocaleString()}</p>
              </button>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}
