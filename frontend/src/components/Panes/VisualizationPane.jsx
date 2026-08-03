import React from 'react'
import {
  FiBarChart2, FiTrendingUp, FiPieChart, FiCircle, FiGrid, FiActivity,
  FiFilter, FiTable, FiHash, FiLayers, FiTarget, FiGitMerge, FiWind,
} from 'react-icons/fi'
import { CHART_CATALOG } from '../../utils/chartConfig'
import { useDashboard } from '../../context/DashboardContext'

const ICONS = {
  bar: FiBarChart2, column: FiBarChart2, line: FiTrendingUp, area: FiActivity,
  pie: FiPieChart, donut: FiCircle, scatter: FiGrid, bubble: FiCircle,
  histogram: FiBarChart2, heatmap: FiGrid, correlation: FiGrid,
  box: FiLayers, violin: FiLayers, treemap: FiGrid, sunburst: FiTarget,
  funnel: FiWind, waterfall: FiBarChart2, radar: FiTarget, polar: FiTarget,
  parallel: FiGitMerge, pairplot: FiGrid, gauge: FiTarget, kpi: FiHash,
  table: FiTable, matrix: FiTable, slicer: FiFilter,
}

const CATEGORY_ORDER = ['KPI', 'Comparison', 'Trend', 'Proportion', 'Relationship', 'Distribution', 'Flow', 'Multi-dim', 'Table', 'Filter']

export default function VisualizationPane() {
  const { addWidget } = useDashboard()

  const grouped = CATEGORY_ORDER.map((cat) => ({
    cat, items: CHART_CATALOG.filter((c) => c.category === cat),
  })).filter((g) => g.items.length)

  return (
    <aside className="w-56 shrink-0 border-r border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 overflow-y-auto">
      <div className="px-3 py-2.5 border-b border-slate-100 dark:border-slate-700">
        <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Visualizations</h2>
      </div>
      <div className="p-2 space-y-3">
        {grouped.map((g) => (
          <div key={g.cat}>
            <p className="px-1 pb-1 text-[10px] font-semibold uppercase tracking-wide text-slate-400">{g.cat}</p>
            <div className="grid grid-cols-4 gap-1.5">
              {g.items.map((item) => {
                const Icon = ICONS[item.type] || FiGrid
                return (
                  <button
                    key={item.type}
                    title={item.label}
                    draggable
                    onDragStart={(e) => e.dataTransfer.setData('chart-type', item.type)}
                    onClick={() => addWidget(item.type)}
                    className="flex flex-col items-center justify-center gap-1 rounded-lg border border-slate-200 dark:border-slate-700 py-2 hover:border-brand-400 hover:bg-brand-50 dark:hover:bg-slate-700 transition-colors cursor-grab active:cursor-grabbing"
                  >
                    <Icon size={16} className="text-slate-500 dark:text-slate-300" />
                    <span className="text-[9px] leading-none text-slate-500 dark:text-slate-400 text-center">{item.label.split(' ')[0]}</span>
                  </button>
                )
              })}
            </div>
          </div>
        ))}
      </div>
    </aside>
  )
}
