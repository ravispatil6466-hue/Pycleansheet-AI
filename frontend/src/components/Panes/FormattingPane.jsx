import React from 'react'
import { useDashboard } from '../../context/DashboardContext'
import { PALETTES } from '../../utils/chartConfig'

const AGGS = ['sum', 'avg', 'count', 'min', 'max', 'median']

function FieldSelect({ label, value, onChange, columns, allowEmpty = true }) {
  return (
    <div>
      <label className="block text-[10px] font-semibold uppercase tracking-wide text-slate-400 mb-1">{label}</label>
      <select
        value={value || ''}
        onChange={(e) => onChange(e.target.value || null)}
        className="w-full text-xs rounded-md border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 px-2 py-1.5 text-slate-700 dark:text-slate-200"
      >
        {allowEmpty && <option value="">— none —</option>}
        {columns.map((c) => <option key={c} value={c}>{c}</option>)}
      </select>
    </div>
  )
}

function MultiFieldSelect({ label, values, onChange, columns }) {
  const toggle = (col) => {
    const set = new Set(values || [])
    if (set.has(col)) set.delete(col); else set.add(col)
    onChange(Array.from(set))
  }
  return (
    <div>
      <label className="block text-[10px] font-semibold uppercase tracking-wide text-slate-400 mb-1">{label}</label>
      <div className="max-h-32 overflow-y-auto rounded-md border border-slate-200 dark:border-slate-600 p-1.5 space-y-0.5">
        {columns.map((c) => (
          <label key={c} className="flex items-center gap-1.5 text-xs text-slate-600 dark:text-slate-300 px-1 py-0.5 rounded hover:bg-slate-50 dark:hover:bg-slate-700">
            <input type="checkbox" checked={(values || []).includes(c)} onChange={() => toggle(c)} className="accent-brand-500" />
            {c}
          </label>
        ))}
      </div>
    </div>
  )
}

export default function FormattingPane() {
  const { selectedWidget, updateWidget, updateWidgetConfig, updateWidgetStyle, datasetMeta } = useDashboard()
  const columns = datasetMeta ? Object.keys(datasetMeta.columns_meta) : []
  const numericColumns = datasetMeta
    ? Object.entries(datasetMeta.columns_meta).filter(([, m]) => m.kind === 'numeric').map(([k]) => k)
    : []

  if (!selectedWidget) {
    return (
      <aside className="w-64 shrink-0 border-l border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-4">
        <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-2">Format</h2>
        <p className="text-[11px] text-slate-400">Select a visual on the canvas to configure its fields and style.</p>
      </aside>
    )
  }

  const { type, config, style, title } = selectedWidget
  const set = (patch) => updateWidgetConfig(selectedWidget.id, patch)
  const setStyle = (patch) => updateWidgetStyle(selectedWidget.id, patch)

  const needsXY = ['bar', 'column', 'line', 'area', 'waterfall'].includes(type)
  const needsScatter = ['scatter', 'bubble'].includes(type)
  const needsHist = type === 'histogram'
  const needsPie = ['pie', 'donut', 'funnel'].includes(type)
  const needsBoxViolin = ['box', 'violin'].includes(type)
  const needsPath = ['treemap', 'sunburst'].includes(type)
  const needsPolar = ['radar', 'polar'].includes(type)
  const needsMulti = ['parallel', 'pairplot'].includes(type)
  const needsGaugeKpi = ['gauge', 'kpi'].includes(type)
  const needsTable = ['table', 'matrix'].includes(type)
  const needsSlicer = type === 'slicer'

  return (
    <aside className="w-64 shrink-0 border-l border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 overflow-y-auto">
      <div className="px-3 py-2.5 border-b border-slate-100 dark:border-slate-700">
        <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Format Visual</h2>
      </div>
      <div className="p-3 space-y-4">
        <div>
          <label className="block text-[10px] font-semibold uppercase tracking-wide text-slate-400 mb-1">Title</label>
          <input
            value={title}
            onChange={(e) => updateWidget(selectedWidget.id, { title: e.target.value })}
            className="w-full text-xs rounded-md border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 px-2 py-1.5 text-slate-700 dark:text-slate-200"
          />
        </div>

        {needsXY && (
          <>
            <FieldSelect label="Axis (X)" value={config.x} onChange={(v) => set({ x: v })} columns={columns} allowEmpty={false} />
            <MultiFieldSelect label="Values (Y)" values={config.y} onChange={(v) => set({ y: v })} columns={numericColumns} />
          </>
        )}

        {needsScatter && (
          <>
            <FieldSelect label="X Axis" value={config.x} onChange={(v) => set({ x: v })} columns={numericColumns} allowEmpty={false} />
            <FieldSelect label="Y Axis" value={config.y?.[0]} onChange={(v) => set({ y: v ? [v] : [] })} columns={numericColumns} allowEmpty={false} />
            <FieldSelect label="Color / Group" value={config.color} onChange={(v) => set({ color: v })} columns={columns} />
            {type === 'bubble' && <FieldSelect label="Size" value={config.size} onChange={(v) => set({ size: v })} columns={numericColumns} />}
          </>
        )}

        {needsHist && (
          <FieldSelect label="Column" value={config.x} onChange={(v) => set({ x: v })} columns={numericColumns} allowEmpty={false} />
        )}

        {needsPie && (
          <>
            <FieldSelect label="Names / Category" value={config.names} onChange={(v) => set({ names: v })} columns={columns} allowEmpty={false} />
            <FieldSelect label="Values" value={config.values} onChange={(v) => set({ values: v })} columns={numericColumns} allowEmpty={false} />
          </>
        )}

        {needsBoxViolin && (
          <>
            <FieldSelect label="Value column" value={config.y?.[0]} onChange={(v) => set({ y: v ? [v] : [] })} columns={numericColumns} allowEmpty={false} />
            <FieldSelect label="Group by (optional)" value={config.color} onChange={(v) => set({ color: v })} columns={columns} />
          </>
        )}

        {needsPath && (
          <>
            <MultiFieldSelect label="Hierarchy path" values={config.path} onChange={(v) => set({ path: v })} columns={columns} />
            <FieldSelect label="Values" value={config.values} onChange={(v) => set({ values: v })} columns={numericColumns} allowEmpty={false} />
          </>
        )}

        {needsPolar && (
          <>
            <FieldSelect label="Category (theta)" value={config.theta} onChange={(v) => set({ theta: v })} columns={columns} allowEmpty={false} />
            <FieldSelect label="Value (r)" value={config.r} onChange={(v) => set({ r: v })} columns={numericColumns} allowEmpty={false} />
          </>
        )}

        {needsMulti && (
          <MultiFieldSelect label="Dimensions" values={config.dimensions} onChange={(v) => set({ dimensions: v })} columns={numericColumns} />
        )}

        {needsGaugeKpi && (
          <FieldSelect label="Value field" value={config.values} onChange={(v) => set({ values: v })} columns={numericColumns} allowEmpty={false} />
        )}

        {needsTable && (
          <MultiFieldSelect label="Columns to show" values={[...(config.dimensions || []), ...(config.y || [])]} onChange={(v) => set({ dimensions: v, y: [] })} columns={columns} />
        )}

        {needsSlicer && (
          <FieldSelect label="Filter column" value={config.column} onChange={(v) => set({ column: v })} columns={columns} allowEmpty={false} />
        )}

        {!needsSlicer && !needsTable && (
          <div>
            <label className="block text-[10px] font-semibold uppercase tracking-wide text-slate-400 mb-1">Aggregation</label>
            <select
              value={config.aggregation || 'sum'}
              onChange={(e) => set({ aggregation: e.target.value })}
              className="w-full text-xs rounded-md border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 px-2 py-1.5 text-slate-700 dark:text-slate-200"
            >
              {AGGS.map((a) => <option key={a} value={a}>{a}</option>)}
            </select>
          </div>
        )}

        {!needsSlicer && !needsTable && !needsGaugeKpi && (
          <div>
            <label className="block text-[10px] font-semibold uppercase tracking-wide text-slate-400 mb-2">Color palette</label>
            <div className="flex gap-2">
              {Object.entries(PALETTES).map(([name, colors]) => (
                <button
                  key={name}
                  title={name}
                  onClick={() => setStyle({ colorScheme: name })}
                  className={`h-6 w-6 rounded-full ring-2 transition-all ${style?.colorScheme === name ? 'ring-brand-500' : 'ring-transparent'}`}
                  style={{ background: `linear-gradient(135deg, ${colors[0]}, ${colors[1]}, ${colors[2]})` }}
                />
              ))}
            </div>
          </div>
        )}

        {!needsSlicer && !needsTable && !needsGaugeKpi && (
          <label className="flex items-center gap-2 text-xs text-slate-600 dark:text-slate-300">
            <input
              type="checkbox"
              checked={style?.showLegend !== false}
              onChange={(e) => setStyle({ showLegend: e.target.checked })}
              className="accent-brand-500"
            />
            Show legend
          </label>
        )}
      </div>
    </aside>
  )
}
