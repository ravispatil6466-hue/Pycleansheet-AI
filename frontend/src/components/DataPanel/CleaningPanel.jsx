import React, { useEffect, useState, useCallback } from 'react'
import { FiCheckCircle, FiAlertTriangle, FiRefreshCw } from 'react-icons/fi'
import { useDashboard } from '../../context/DashboardContext'
import * as api from '../../api/axiosClient'

function Section({ title, children }) {
  return (
    <div className="panel-card p-3 space-y-2">
      <h3 className="text-xs font-semibold text-slate-600 dark:text-slate-200">{title}</h3>
      {children}
    </div>
  )
}

function Select({ value, onChange, options, className = '' }) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className={`text-xs rounded-md border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 px-2 py-1.5 text-slate-700 dark:text-slate-200 ${className}`}
    >
      {options.map((o) => <option key={o.value ?? o} value={o.value ?? o}>{o.label ?? o}</option>)}
    </select>
  )
}

export default function CleaningPanel() {
  const { datasetId, datasetMeta, setDatasetMeta } = useDashboard()
  const [report, setReport] = useState(null)
  const [busy, setBusy] = useState(false)
  const [missingStrategy, setMissingStrategy] = useState('mean')
  const [dupKeep, setDupKeep] = useState('first')
  const [outlierCol, setOutlierCol] = useState('')
  const [outlierMethod, setOutlierMethod] = useState('iqr')
  const [outlierAction, setOutlierAction] = useState('remove')
  const [typeCol, setTypeCol] = useState('')
  const [typeTarget, setTypeTarget] = useState('float')
  const [normCols, setNormCols] = useState([])
  const [normMethod, setNormMethod] = useState('standard')

  const columns = datasetMeta ? Object.keys(datasetMeta.columns_meta) : []
  const numericColumns = datasetMeta
    ? Object.entries(datasetMeta.columns_meta).filter(([, m]) => m.kind === 'numeric').map(([k]) => k)
    : []

  const refresh = useCallback(async () => {
    if (!datasetId) return
    const res = await api.qualityReport(datasetId)
    setReport(res.data)
    const ds = await api.getDataset(datasetId)
    setDatasetMeta(ds.data)
  }, [datasetId, setDatasetMeta])

  useEffect(() => { refresh() }, [refresh])

  const run = async (fn) => {
    setBusy(true)
    try { await fn(); await refresh() } finally { setBusy(false) }
  }

  if (!datasetId) return <p className="p-4 text-xs text-slate-400">Upload a dataset first to clean it.</p>

  return (
    <div className="p-4 space-y-4">
      <Section title="Data Quality Overview">
        {report ? (
          <div className="grid grid-cols-2 gap-2 text-xs">
            <Stat label="Rows" value={report.total_rows} />
            <Stat label="Columns" value={report.total_columns} />
            <Stat label="Duplicate rows" value={report.duplicate_rows} warn={report.duplicate_rows > 0} />
            <Stat label="Missing cells" value={report.total_missing_cells} warn={report.total_missing_cells > 0} />
          </div>
        ) : <p className="text-xs text-slate-400">Loading…</p>}
        <button onClick={refresh} className="flex items-center gap-1 text-[11px] text-brand-600 dark:text-brand-300 hover:underline">
          <FiRefreshCw size={11} /> Refresh
        </button>
      </Section>

      <Section title="Handle Missing Values">
        <div className="flex items-center gap-2 flex-wrap">
          <Select value={missingStrategy} onChange={setMissingStrategy} options={['mean', 'median', 'mode', 'ffill', 'bfill', 'drop_rows']} />
          <ActionButton disabled={busy} onClick={() => run(() => api.cleanMissing(datasetId, { strategy: missingStrategy }))}>Apply to all columns</ActionButton>
        </div>
      </Section>

      <Section title="Remove Duplicates">
        <div className="flex items-center gap-2 flex-wrap">
          <Select value={dupKeep} onChange={setDupKeep} options={['first', 'last', 'none']} />
          <ActionButton disabled={busy} onClick={() => run(() => api.cleanDuplicates(datasetId, { keep: dupKeep }))}>Remove duplicates</ActionButton>
        </div>
      </Section>

      <Section title="Outlier Detection">
        <div className="flex items-center gap-2 flex-wrap">
          <Select value={outlierCol} onChange={setOutlierCol} options={[{ value: '', label: 'Select column' }, ...numericColumns]} />
          <Select value={outlierMethod} onChange={setOutlierMethod} options={['iqr', 'zscore']} />
          <Select value={outlierAction} onChange={setOutlierAction} options={['remove', 'cap']} />
          <ActionButton
            disabled={busy || !outlierCol}
            onClick={() => run(() => api.cleanOutliers(datasetId, { columns: [outlierCol], method: outlierMethod, action: outlierAction }))}
          >
            Apply
          </ActionButton>
        </div>
      </Section>

      <Section title="Type Conversion">
        <div className="flex items-center gap-2 flex-wrap">
          <Select value={typeCol} onChange={setTypeCol} options={[{ value: '', label: 'Select column' }, ...columns]} />
          <Select value={typeTarget} onChange={setTypeTarget} options={['int', 'float', 'string', 'datetime', 'category', 'bool']} />
          <ActionButton
            disabled={busy || !typeCol}
            onClick={() => run(() => api.convertType(datasetId, { column: typeCol, target_type: typeTarget }))}
          >
            Convert
          </ActionButton>
        </div>
      </Section>

      <Section title="Normalize / Scale">
        <div className="flex flex-wrap gap-1 mb-1">
          {numericColumns.map((c) => (
            <label key={c} className="flex items-center gap-1 text-[11px] px-1.5 py-0.5 rounded border border-slate-200 dark:border-slate-600">
              <input
                type="checkbox"
                checked={normCols.includes(c)}
                onChange={() => setNormCols((prev) => prev.includes(c) ? prev.filter((x) => x !== c) : [...prev, c])}
                className="accent-brand-500"
              />
              {c}
            </label>
          ))}
        </div>
        <div className="flex items-center gap-2">
          <Select value={normMethod} onChange={setNormMethod} options={['standard', 'minmax', 'robust']} />
          <ActionButton
            disabled={busy || normCols.length === 0}
            onClick={() => run(() => api.normalizeColumns(datasetId, { columns: normCols, method: normMethod }))}
          >
            Normalize
          </ActionButton>
        </div>
      </Section>
    </div>
  )
}

function Stat({ label, value, warn }) {
  return (
    <div className="flex items-center justify-between rounded-md bg-slate-50 dark:bg-slate-700 px-2 py-1.5">
      <span className="text-slate-500 dark:text-slate-400">{label}</span>
      <span className={`font-semibold flex items-center gap-1 ${warn ? 'text-amber-600' : 'text-slate-700 dark:text-slate-200'}`}>
        {warn ? <FiAlertTriangle size={11} /> : <FiCheckCircle size={11} className="text-emerald-500" />}
        {value}
      </span>
    </div>
  )
}

function ActionButton({ children, ...props }) {
  return (
    <button
      {...props}
      className="text-xs font-medium px-3 py-1.5 rounded-md bg-brand-500 text-white hover:bg-brand-600 disabled:opacity-40 disabled:cursor-not-allowed"
    >
      {children}
    </button>
  )
}
