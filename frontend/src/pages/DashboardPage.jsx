import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { DashboardProvider, useDashboard } from '../context/DashboardContext'
import Ribbon from '../components/Ribbon/Ribbon'
import VisualizationPane from '../components/Panes/VisualizationPane'
import FieldsPane from '../components/Panes/FieldsPane'
import FormattingPane from '../components/Panes/FormattingPane'
import DashboardCanvas from '../components/Dashboard/DashboardCanvas'
import DashboardTabs from '../components/Dashboard/DashboardTabs'
import TemplatesModal from '../components/Dashboard/TemplatesModal'
import AIChatbot from '../components/Chatbot/AIChatbot'
import DataStudioPage from './DataStudioPage'

function DashboardInner() {
  const { id } = useParams()
  const { loadDashboardFromServer } = useDashboard()
  const [chatOpen, setChatOpen] = useState(false)
  const [studioOpen, setStudioOpen] = useState(false)
  const [templatesOpen, setTemplatesOpen] = useState(false)

  useEffect(() => {
    if (id && id !== 'new') {
      loadDashboardFromServer(id).catch(() => {})
    }
  }, [id])

  return (
    <div className="h-screen flex flex-col bg-slate-100 dark:bg-slate-900">
      <Ribbon
        onOpenChat={() => setChatOpen((v) => !v)}
        onOpenDataStudio={() => setStudioOpen(true)}
        onOpenTemplates={() => setTemplatesOpen(true)}
        chatOpen={chatOpen}
      />
      <div className="flex flex-1 min-h-0">
        <VisualizationPane />
        <FieldsPane />
        <div className="flex flex-col flex-1 min-w-0">
          <DashboardCanvas />
          <DashboardTabs />
        </div>
        <FormattingPane />
      </div>

      <TemplatesModal open={templatesOpen} onClose={() => setTemplatesOpen(false)} />
      {studioOpen && <DataStudioPage onClose={() => setStudioOpen(false)} />}
      <AIChatbot open={chatOpen} onClose={() => setChatOpen(false)} />
    </div>
  )
}

export default function DashboardPage() {
  return (
    <DashboardProvider>
      <DashboardInner />
    </DashboardProvider>
  )
}
