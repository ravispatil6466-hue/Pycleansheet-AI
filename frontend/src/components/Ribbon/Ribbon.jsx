import React, { useRef, useState } from 'react'
import {
  FiUploadCloud, FiSave, FiDownload, FiPlus, FiMessageSquare, FiLayout,
  FiFileText, FiDatabase, FiEye, FiHome, FiChevronDown, FiCode,
} from 'react-icons/fi'
import { useDashboard } from '../../context/DashboardContext'
import { uploadDataset, exportUrl } from '../../api/axiosClient'
import { downloadFromApi } from '../../utils/exportUtils'
import ThemeToggle from '../Common/ThemeToggle'
import { PALETTES } from '../../utils/chartConfig'

const TABS = [
  { id: 'home', label: 'Home', icon: FiHome },
  { id: 'insert', label: 'Insert', icon: FiPlus },
  { id: 'data', label: 'Data', icon: FiDatabase },
  { id: 'view', label: 'View', icon: FiEye },
]

export default function Ribbon({ onOpenChat, onOpenDataStudio, onOpenTemplates, chatOpen }) {
  const [activeTab, setActiveTab] = useState('home')
  const [exportMenuOpen, setExportMenuOpen] = useState(false)
  const fileInputRef = useRef(null)
  const {
    dashboardName, setDashboardName, addWidget, addPage, saveDashboardToServer, saving,
    datasetId, loadDataset, colorPalette, setColorPalette,
  } = useDashboard()

  const handleFile = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    const res = await uploadDataset(file)
    await loadDataset(res.data.id)
    e.target.value = ''
  }

  return (
    <div className="border-b border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 shrink-0">
      <div className="flex items-center justify-between px-3 pt-1.5">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 pr-3 border-r border-slate-200 dark:border-slate-700">
            <div className="h-6 w-6 rounded bg-gradient-to-br from-brand-500 to-brand-800 flex items-center justify-center text-white text-[11px] font-bold">P</div>
            <input
              value={dashboardName}
              onChange={(e) => setDashboardName(e.target.value)}
              className="text-sm font-semibold bg-transparent outline-none text-slate-700 dark:text-slate-100 w-40"
            />
          </div>
          <div className="flex items-center gap-1">
            {TABS.map((t) => (
              <button
                key={t.id}
                onClick={() => setActiveTab(t.id)}
                className={`px-3 py-1.5 text-xs font-medium rounded-t-md transition-colors ${
                  activeTab === t.id
                    ? 'text-brand-700 dark:text-brand-300 border-b-2 border-brand-500'
                    : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200'
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>
        </div>
        <div className="flex items-center gap-2 pb-1.5">
          <ThemeToggle />
        </div>
      </div>

      <div className="flex items-center gap-1 px-3 py-2 flex-wrap">
        {activeTab === 'home' && (
          <>
            <RibbonButton icon={FiUploadCloud} label="Get Data" onClick={() => fileInputRef.current?.click()} />
            <input ref={fileInputRef} type="file" accept=".csv,.xlsx,.xls,.json,.parquet" className="hidden" onChange={handleFile} />
            <RibbonButton icon={FiSave} label={saving ? 'Saving…' : 'Save'} onClick={saveDashboardToServer} />
            <Divider />
            <RibbonButton icon={FiPlus} label="New Page" onClick={addPage} />
            <RibbonButton icon={FiLayout} label="Templates" onClick={onOpenTemplates} />
            <Divider />
            <RibbonButton icon={FiCode} label="Data Studio" onClick={onOpenDataStudio} />
            <RibbonButton icon={FiMessageSquare} label="AI Chat" onClick={onOpenChat} active={chatOpen} />
            <Divider />
            <div className="relative">
              <RibbonButton icon={FiDownload} label="Export" onClick={() => setExportMenuOpen((v) => !v)} />
              {exportMenuOpen && (
                <div className="absolute left-0 top-full mt-1 z-30 w-44 panel-card py-1 text-xs" onMouseLeave={() => setExportMenuOpen(false)}>
                  {[
                    ['csv', 'Export as CSV'],
                    ['excel', 'Export as Excel'],
                    ['json', 'Export as JSON'],
                    ['pdf-report', 'Export PDF Report'],
                  ].map(([fmt, label]) => (
                    <button
                      key={fmt}
                      disabled={!datasetId}
                      onClick={() => datasetId && downloadFromApi(exportUrl(datasetId, fmt), `${dashboardName}.${fmt === 'pdf-report' ? 'pdf' : fmt === 'excel' ? 'xlsx' : fmt}`)}
                      className="flex w-full items-center gap-2 px-3 py-1.5 hover:bg-slate-50 dark:hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-slate-600 dark:text-slate-300"
                    >
                      <FiFileText size={12} /> {label}
                    </button>
                  ))}
                  <p className="px-3 pt-1 pb-0.5 text-[10px] text-slate-400">Chart PNG/SVG export is available from each visual's menu.</p>
                </div>
              )}
            </div>
          </>
        )}

        {activeTab === 'insert' && (
          <p className="text-xs text-slate-400 px-1">Use the Visualizations panel on the left to insert charts, KPI cards, tables, and slicers.</p>
        )}

        {activeTab === 'data' && (
          <>
            <RibbonButton icon={FiUploadCloud} label="Upload Dataset" onClick={() => fileInputRef.current?.click()} />
            <RibbonButton icon={FiCode} label="Clean & Explore" onClick={onOpenDataStudio} />
          </>
        )}

        {activeTab === 'view' && (
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-semibold uppercase tracking-wide text-slate-400 mr-1">Theme</span>
            {Object.entries(PALETTES).map(([name, colors]) => (
              <button
                key={name}
                title={name}
                onClick={() => setColorPalette(name)}
                className={`h-6 w-6 rounded-full ring-2 transition-all ${colorPalette === name ? 'ring-brand-500' : 'ring-transparent'}`}
                style={{ background: `linear-gradient(135deg, ${colors[0]}, ${colors[1]}, ${colors[2]})` }}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function RibbonButton({ icon: Icon, label, onClick, active }) {
  return (
    <button onClick={onClick} className={`ribbon-btn ${active ? 'active' : ''}`}>
      <Icon size={16} />
      <span>{label}</span>
    </button>
  )
}

function Divider() {
  return <div className="w-px h-8 bg-slate-200 dark:bg-slate-700 mx-1" />
}
