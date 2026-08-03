import React from 'react'
import { v4 as uuidv4 } from 'uuid'
import Modal from '../Common/Modal'
import { useDashboard } from '../../context/DashboardContext'

function makePage(name, widgetTypes) {
  const widgets = widgetTypes.map((type, i) => ({
    id: uuidv4(), type, title: type.toUpperCase(), config: {}, style: { colorScheme: 'teal', showLegend: true },
  }))
  const layoutPresets = {
    4: [
      { w: 6, h: 4 }, { w: 6, h: 4 }, { w: 6, h: 4 }, { w: 6, h: 4 },
    ],
    5: [
      { w: 4, h: 4 }, { w: 4, h: 4 }, { w: 4, h: 4 }, { w: 12, h: 8 }, { w: 12, h: 8 },
    ],
  }
  const preset = layoutPresets[widgets.length] || widgets.map(() => ({ w: 8, h: 8 }))
  let cursorX = 0, cursorY = 0, rowH = 0
  const layout = widgets.map((w, i) => {
    const { w: pw, h: ph } = preset[i]
    if (cursorX + pw > 24) { cursorX = 0; cursorY += rowH; rowH = 0 }
    const item = { i: w.id, x: cursorX, y: cursorY, w: pw, h: ph, minW: 2, minH: 3 }
    cursorX += pw
    rowH = Math.max(rowH, ph)
    return item
  })
  return { id: uuidv4(), name, widgets, layout }
}

const TEMPLATES = [
  {
    id: 'exec-summary',
    name: 'Executive Summary',
    description: '3 KPI cards + a trend line + category breakdown table',
    build: () => [makePage('Overview', ['kpi', 'kpi', 'kpi', 'line', 'table'])],
  },
  {
    id: 'sales-analytics',
    name: 'Sales Analytics',
    description: 'Bar, pie, line, and scatter for a classic BI overview',
    build: () => [makePage('Sales', ['bar', 'pie', 'line', 'scatter'])],
  },
  {
    id: 'data-quality',
    name: 'Data Quality Dashboard',
    description: 'Heatmap correlation, histogram, box plot, and table',
    build: () => [makePage('Quality', ['heatmap', 'histogram', 'box', 'table'])],
  },
  {
    id: 'blank',
    name: 'Blank Canvas',
    description: 'Start from scratch',
    build: () => [makePage('Page 1', [])],
  },
]

export default function TemplatesModal({ open, onClose }) {
  const { applyTemplate } = useDashboard()

  const apply = (tpl) => {
    applyTemplate(tpl.build())
    onClose()
  }

  return (
    <Modal open={open} onClose={onClose} title="Dashboard Templates" width="max-w-2xl">
      <div className="grid grid-cols-2 gap-3">
        {TEMPLATES.map((t) => (
          <button
            key={t.id}
            onClick={() => apply(t)}
            className="text-left rounded-xl border border-slate-200 dark:border-slate-600 p-4 hover:border-brand-400 hover:bg-brand-50 dark:hover:bg-slate-700 transition-colors"
          >
            <p className="text-sm font-semibold text-slate-700 dark:text-slate-100">{t.name}</p>
            <p className="text-[11px] text-slate-400 mt-1">{t.description}</p>
          </button>
        ))}
      </div>
    </Modal>
  )
}
