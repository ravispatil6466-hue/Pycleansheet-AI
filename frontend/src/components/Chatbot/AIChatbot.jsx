import React, { useState, useRef, useEffect } from 'react'
import { FiSend, FiX, FiCpu, FiUser } from 'react-icons/fi'
import { useDashboard } from '../../context/DashboardContext'
import { sendChatMessage } from '../../api/axiosClient'

const SUGGESTIONS = [
  'Give me a summary of this dataset',
  'Which columns have missing values?',
  'Suggest 3 charts I should build',
  'What correlations stand out?',
]

export default function AIChatbot({ open, onClose }) {
  const { datasetId, datasetMeta } = useDashboard()
  const [messages, setMessages] = useState([
    { role: 'assistant', content: "Hi! I'm your Pycleansheet AI assistant. Upload a dataset and ask me anything about cleaning, EDA, or which charts to build." },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const scrollRef = useRef(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, open])

  const send = async (text) => {
    const message = (text ?? input).trim()
    if (!message) return
    setInput('')
    const nextMessages = [...messages, { role: 'user', content: message }]
    setMessages(nextMessages)
    setLoading(true)
    try {
      const res = await sendChatMessage({
        dataset_id: datasetId,
        message,
        history: nextMessages.slice(-10).map((m) => ({ role: m.role, content: m.content })),
      })
      setMessages((prev) => [...prev, { role: 'assistant', content: res.data.reply }])
    } catch (e) {
      setMessages((prev) => [...prev, { role: 'assistant', content: 'Sorry, something went wrong reaching the AI service.' }])
    } finally {
      setLoading(false)
    }
  }

  if (!open) return null

  return (
    <div className="fixed bottom-4 right-4 z-40 w-96 h-[560px] panel-card flex flex-col overflow-hidden shadow-2xl">
      <div className="flex items-center justify-between px-4 py-3 bg-gradient-to-r from-brand-800 to-brand-500 text-white">
        <div className="flex items-center gap-2">
          <FiCpu size={16} />
          <div>
            <p className="text-sm font-semibold leading-none">Pycleansheet AI</p>
            <p className="text-[10px] opacity-80">{datasetMeta ? datasetMeta.name : 'No dataset loaded'}</p>
          </div>
        </div>
        <button onClick={onClose} className="hover:bg-white/10 rounded p-1"><FiX size={16} /></button>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto p-3 space-y-3">
        {messages.map((m, i) => (
          <div key={i} className={`flex gap-2 ${m.role === 'user' ? 'flex-row-reverse' : ''}`}>
            <div className={`h-6 w-6 shrink-0 rounded-full flex items-center justify-center text-white ${m.role === 'user' ? 'bg-slate-400' : 'bg-brand-500'}`}>
              {m.role === 'user' ? <FiUser size={12} /> : <FiCpu size={12} />}
            </div>
            <div className={`max-w-[75%] rounded-xl px-3 py-2 text-xs whitespace-pre-wrap ${
              m.role === 'user'
                ? 'bg-brand-500 text-white rounded-tr-sm'
                : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-200 rounded-tl-sm'
            }`}>
              {m.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex gap-2">
            <div className="h-6 w-6 shrink-0 rounded-full flex items-center justify-center text-white bg-brand-500"><FiCpu size={12} /></div>
            <div className="rounded-xl rounded-tl-sm px-3 py-2 bg-slate-100 dark:bg-slate-700 text-xs text-slate-400">Thinking…</div>
          </div>
        )}
      </div>

      {messages.length < 2 && (
        <div className="px-3 pb-2 flex flex-wrap gap-1.5">
          {SUGGESTIONS.map((s) => (
            <button key={s} onClick={() => send(s)} className="text-[10px] px-2 py-1 rounded-full border border-slate-200 dark:border-slate-600 text-slate-500 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700">
              {s}
            </button>
          ))}
        </div>
      )}

      <div className="flex items-center gap-2 p-3 border-t border-slate-100 dark:border-slate-700">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && send()}
          placeholder="Ask about your data…"
          className="flex-1 text-xs rounded-full border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 px-3 py-2 text-slate-700 dark:text-slate-200 outline-none focus:ring-2 focus:ring-brand-500"
        />
        <button onClick={() => send()} className="h-8 w-8 shrink-0 rounded-full bg-brand-500 text-white flex items-center justify-center hover:bg-brand-600">
          <FiSend size={14} />
        </button>
      </div>
    </div>
  )
}
