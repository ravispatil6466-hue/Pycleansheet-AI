import React, { useEffect, useState, useCallback } from 'react'
import Plot from 'react-plotly.js'
import { useDashboard } from '../../context/DashboardContext'
import * as api from '../../api/axiosClient'
import { PALETTES } from '../../utils/chartConfig'
import { useTheme } from '../../context/ThemeContext'

export default function EDAPanel() {
  const { datasetId, datasetMeta } = useDashboard()
  const { theme } = useTheme()
  const dark = theme === 'dark'
  const [summary, setSummary] = useState(null)
  const [correlation, setCorrelation] = useState(null)
  const [distCol, setDistCol] = useState('')
  const [distribution, setDistribution] = useState(null)

  const numericColumns = datasetMeta
    ? Object.entries(datasetMeta.columns_meta).filter(([, m]) => m.kind === 'numeric').map(([k]) => k)
    : []

  const load = useCallback(async () => {
    if (!datasetId) return
    const [s, c] = await Promise.all([api.edaSummary(datasetId), api.edaCorrelation(datasetId)])
    setSummary(s.data)
    setCorrelation(c.data)
    if (numericColumns.length && !distCol) setDistCol(numericColumns[0])
  }, [datasetId])

  useEffect(() => { load() }, [load])

  useEffect(() => {
    if (!datasetId || !distCol) return
    api.edaDistribution(datasetId, distCol).then((res) => setDistribution(res.data))
  }, [datasetId, distCol])

  if (!datasetId) return <p className="p-4 text-xs text-slate-400">Upload a dataset first to explore it.</p>

  const axisStyle = { gridcolor: dark ? '#334155' : '#EEF2F6' }
  const fontStyle = { family: 'Inter, sans-serif', color: dark ? '#CBD5E1' : '#475569', size: 11 }

  return (
    <div className="p-4 space-y-4">
      {summary && (
        <div className="panel-card p-3">
          <h3 className="text-xs font-semibold text-slate-600 dark:text-slate-200 mb-2">Dataset Overview</h3>
          <div className="grid grid-cols-3 gap-2 text-xs">
            <MiniStat label="Rows" value={summary.shape.rows} />
            <MiniStat label="Columns" value={summary.shape.columns} />
            <MiniStat label="Missing values" value={summary.missing_total} />
          </div>
        </div>
      )}

      {summary?.numeric_summary && Object.keys(summary.numeric_summary).length > 0 && (
        <div className="panel-card p-3 overflow-x-auto">
          <h3 className="text-xs font-semibold text-slate-600 dark:text-slate-200 mb-2">Numeric Summary</h3>
          <table className="text-[11px] w-full">
            <thead>
              <tr className="text-slate-400">
                <th className="text-left pr-3 py-1">Column</th>
                {['mean', 'std', 'min', '25%', '50%', '75%', 'max'].map((k) => (
                  <th key={k} className="text-right px-2 py-1">{k}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {Object.entries(summary.numeric_summary).map(([col, stats]) => (
                <tr key={col} className="border-t border-slate-100 dark:border-slate-700">
                  <td className="pr-3 py-1 font-medium text-slate-600 dark:text-slate-300">{col}</td>
                  {['mean', 'std', 'min', '25%', '50%', '75%', 'max'].map((k) => (
                    <td key={k} className="text-right px-2 py-1 text-slate-500 dark:text-slate-400">
                      {stats[k] !== null && stats[k] !== undefined ? Number(stats[k]).toFixed(2) : '—'}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {correlation?.columns?.length > 1 && (
        <div className="panel-card p-3">
          <h3 className="text-xs font-semibold text-slate-600 dark:text-slate-200 mb-2">Correlation Matrix</h3>
          <Plot
            data={[{
              type: 'heatmap', z: correlation.matrix, x: correlation.columns, y: correlation.columns,
              colorscale: 'RdBu', reversescale: true, zmin: -1, zmax: 1,
            }]}
            layout={{
              margin: { l: 60, r: 20, t: 10, b: 60 }, paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
              font: fontStyle, xaxis: { ...axisStyle, tickangle: -35 }, yaxis: axisStyle, height: 360,
            }}
            config={{ displayModeBar: false, responsive: true }}
            style={{ width: '100%' }}
          />
        </div>
      )}

      {numericColumns.length > 0 && (
        <div className="panel-card p-3">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-xs font-semibold text-slate-600 dark:text-slate-200">Distribution</h3>
            <select
              value={distCol}
              onChange={(e) => setDistCol(e.target.value)}
              className="text-xs rounded-md border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 px-2 py-1 text-slate-700 dark:text-slate-200"
            >
              {numericColumns.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          {distribution && distribution.type === 'numeric' && (
            <Plot
              data={[{
                type: 'bar',
                x: distribution.bin_edges.slice(0, -1).map((e, i) => ((e + distribution.bin_edges[i + 1]) / 2).toFixed(1)),
                y: distribution.counts,
                marker: { color: PALETTES.teal[0] },
              }]}
              layout={{
                margin: { l: 40, r: 20, t: 10, b: 40 }, paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
                font: fontStyle, xaxis: axisStyle, yaxis: axisStyle, height: 280,
              }}
              config={{ displayModeBar: false, responsive: true }}
              style={{ width: '100%' }}
            />
          )}
        </div>
      )}
    </div>
  )
}

function MiniStat({ label, value }) {
  return (
    <div className="rounded-md bg-slate-50 dark:bg-slate-700 px-2 py-2 text-center">
      <div className="text-base font-bold text-brand-600 dark:text-brand-300">{value?.toLocaleString?.() ?? value}</div>
      <div className="text-[10px] text-slate-400">{label}</div>
    </div>
  )
}
