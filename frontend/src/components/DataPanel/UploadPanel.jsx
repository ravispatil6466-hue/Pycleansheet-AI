import React, { useRef, useState } from 'react'
import { FiUploadCloud, FiFile, FiCheckCircle } from 'react-icons/fi'
import { uploadDataset } from '../../api/axiosClient'
import { useDashboard } from '../../context/DashboardContext'

export default function UploadPanel() {
  const { loadDataset, datasetMeta } = useDashboard()
  const [dragOver, setDragOver] = useState(false)
  const [uploading, setUploading] = useState(false)
  const inputRef = useRef(null)

  const handleFiles = async (files) => {
    const file = files?.[0]
    if (!file) return
    setUploading(true)
    try {
      const res = await uploadDataset(file)
      await loadDataset(res.data.id)
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="p-4">
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => { e.preventDefault(); setDragOver(false); handleFiles(e.dataTransfer.files) }}
        onClick={() => inputRef.current?.click()}
        className={`flex flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed p-8 cursor-pointer transition-colors ${
          dragOver ? 'border-brand-500 bg-brand-50 dark:bg-slate-700' : 'border-slate-300 dark:border-slate-600'
        }`}
      >
        <FiUploadCloud size={28} className="text-brand-500" />
        <p className="text-sm font-medium text-slate-600 dark:text-slate-300">
          {uploading ? 'Uploading…' : 'Drag & drop a file, or click to browse'}
        </p>
        <p className="text-[11px] text-slate-400">Supports CSV, XLSX, XLS, JSON, Parquet</p>
        <input
          ref={inputRef}
          type="file"
          accept=".csv,.xlsx,.xls,.json,.parquet"
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />
      </div>

      {datasetMeta && (
        <div className="mt-4 flex items-center gap-2 rounded-lg bg-brand-50 dark:bg-slate-700 px-3 py-2 text-xs text-brand-700 dark:text-brand-200">
          <FiCheckCircle size={14} />
          <span>
            <strong>{datasetMeta.name}</strong> loaded — {datasetMeta.rows.toLocaleString()} rows × {datasetMeta.cols} columns
          </span>
        </div>
      )}
    </div>
  )
}
