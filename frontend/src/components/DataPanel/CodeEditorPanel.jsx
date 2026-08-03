import React, { useState } from 'react'
import { FiPlay, FiTerminal } from 'react-icons/fi'
import { useDashboard } from '../../context/DashboardContext'
import { executeCode } from '../../api/axiosClient'

const DEFAULT_CODE = `# 'df' is your dataset as a pandas DataFrame.
# Assign a DataFrame to 'result' to preview it below.
result = df.describe()
print("Shape:", df.shape)
`

export default function CodeEditorPanel() {
  const { datasetId } = useDashboard()
  const [code, setCode] = useState(DEFAULT_CODE)
  const [output, setOutput] = useState(null)
  const [running, setRunning] = useState(false)

  const run = async () => {
    if (!datasetId) return
    setRunning(true)
    setOutput(null)
    try {
      const res = await executeCode({ dataset_id: datasetId, code })
      setOutput(res.data)
    } catch (e) {
      setOutput({ error: e?.response?.data?.detail || 'Execution failed' })
    } finally {
      setRunning(false)
    }
  }

  if (!datasetId) return <p className="p-4 text-xs text-slate-400">Upload a dataset first to run Python code against it.</p>

  return (
    <div className="p-4 space-y-3 flex flex-col h-full">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-semibold text-slate-600 dark:text-slate-200 flex items-center gap-1.5">
          <FiTerminal size={13} /> Python Sandbox
        </h3>
        <button
          onClick={run}
          disabled={running}
          className="flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-md bg-brand-500 text-white hover:bg-brand-600 disabled:opacity-40"
        >
          <FiPlay size={12} /> {running ? 'Running…' : 'Run Code'}
        </button>
      </div>

      <textarea
        value={code}
        onChange={(e) => setCode(e.target.value)}
        spellCheck={false}
        className="w-full h-52 font-mono text-xs rounded-lg border border-slate-200 dark:border-slate-600 bg-slate-900 text-emerald-300 p-3 resize-y focus:outline-none focus:ring-2 focus:ring-brand-500"
      />
      <p className="text-[10px] text-slate-400">
        Sandboxed execution: pandas (pd), numpy (np), and selected scikit-learn modules are available.
        File I/O, imports, and shell access are disabled.
      </p>

      {output && (
        <div className="panel-card p-3 space-y-2 overflow-auto">
          {output.error && <pre className="text-[11px] text-red-500 whitespace-pre-wrap">{output.error}</pre>}
          {output.stdout && (
            <div>
              <p className="text-[10px] font-semibold uppercase text-slate-400 mb-1">stdout</p>
              <pre className="text-[11px] text-slate-600 dark:text-slate-300 whitespace-pre-wrap">{output.stdout}</pre>
            </div>
          )}
          {output.result_preview && Array.isArray(output.result_preview) && (
            <div>
              <p className="text-[10px] font-semibold uppercase text-slate-400 mb-1">
                result {output.result_shape ? `(${output.result_shape[0]} × ${output.result_shape[1]})` : ''}
              </p>
              <div className="overflow-auto max-h-64">
                <table className="text-[11px] w-full">
                  <thead>
                    <tr className="text-slate-400">
                      {output.result_columns?.map((c) => <th key={c} className="text-left px-2 py-1">{c}</th>)}
                    </tr>
                  </thead>
                  <tbody>
                    {output.result_preview.slice(0, 50).map((row, i) => (
                      <tr key={i} className="border-t border-slate-100 dark:border-slate-700">
                        {output.result_columns?.map((c) => <td key={c} className="px-2 py-1 text-slate-600 dark:text-slate-300">{String(row[c] ?? '')}</td>)}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
          {output.result_preview && !Array.isArray(output.result_preview) && (
            <pre className="text-[11px] text-slate-600 dark:text-slate-300 whitespace-pre-wrap">{output.result_preview}</pre>
          )}
        </div>
      )}
    </div>
  )
}
