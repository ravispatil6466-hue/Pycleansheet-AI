import React, { createContext, useContext, useState, useCallback, useMemo } from 'react'
import { v4 as uuidv4 } from 'uuid'
import * as api from '../api/axiosClient'

const DashboardContext = createContext(null)

const defaultPage = () => ({
  id: uuidv4(),
  name: 'Page 1',
  widgets: [],
  layout: [],
})

const CHART_DEFAULT_SIZE = { w: 5, h: 8 }
const KPI_DEFAULT_SIZE = { w: 3, h: 4 }
const TABLE_DEFAULT_SIZE = { w: 8, h: 10 }
const SLICER_DEFAULT_SIZE = { w: 3, h: 5 }

function defaultSizeFor(type) {
  if (type === 'kpi') return KPI_DEFAULT_SIZE
  if (type === 'table' || type === 'matrix') return TABLE_DEFAULT_SIZE
  if (type === 'slicer') return SLICER_DEFAULT_SIZE
  return CHART_DEFAULT_SIZE
}

export function DashboardProvider({ children }) {
  const [dashboardId, setDashboardId] = useState(null)
  const [dashboardName, setDashboardName] = useState('Untitled Dashboard')
  const [colorPalette, setColorPalette] = useState('teal') // teal | sunset | ocean | slate
  const [datasetId, setDatasetId] = useState(null)
  const [datasetMeta, setDatasetMeta] = useState(null)
  const [pages, setPages] = useState([defaultPage()])
  const [activePageId, setActivePageId] = useState(pages[0].id)
  const [selectedWidgetId, setSelectedWidgetId] = useState(null)
  const [globalFilters, setGlobalFilters] = useState([]) // [{column, operator, value}]
  const [saving, setSaving] = useState(false)

  const activePage = useMemo(
    () => pages.find((p) => p.id === activePageId) || pages[0],
    [pages, activePageId]
  )

  const updatePage = useCallback((pageId, patch) => {
    setPages((prev) => prev.map((p) => (p.id === pageId ? { ...p, ...patch } : p)))
  }, [])

  const addPage = useCallback(() => {
    setPages((prev) => {
      const np = { id: uuidv4(), name: `Page ${prev.length + 1}`, widgets: [], layout: [] }
      setActivePageId(np.id)
      return [...prev, np]
    })
  }, [])

  const removePage = useCallback((pageId) => {
    setPages((prev) => {
      const next = prev.filter((p) => p.id !== pageId)
      if (next.length === 0) {
        const np = defaultPage()
        setActivePageId(np.id)
        return [np]
      }
      if (pageId === activePageId) setActivePageId(next[0].id)
      return next
    })
  }, [activePageId])

  const renamePage = useCallback((pageId, name) => {
    updatePage(pageId, { name })
  }, [updatePage])

  const addWidget = useCallback((type, extra = {}) => {
    const id = uuidv4()
    const size = defaultSizeFor(type)
    const widget = {
      id,
      type,
      title: extra.title || defaultTitleFor(type),
      config: extra.config || {},
      style: extra.style || { colorScheme: 'teal', showLegend: true, showDataLabels: false },
    }
    setPages((prev) =>
      prev.map((p) => {
        if (p.id !== activePageId) return p
        const maxY = p.layout.reduce((m, l) => Math.max(m, l.y + l.h), 0)
        const newLayout = { i: id, x: 0, y: maxY, w: size.w, h: size.h, minW: 2, minH: 3 }
        return { ...p, widgets: [...p.widgets, widget], layout: [...p.layout, newLayout] }
      })
    )
    setSelectedWidgetId(id)
    return id
  }, [activePageId])

  const updateWidget = useCallback((widgetId, patch) => {
    setPages((prev) =>
      prev.map((p) => ({
        ...p,
        widgets: p.widgets.map((w) => (w.id === widgetId ? { ...w, ...patch } : w)),
      }))
    )
  }, [])

  const updateWidgetConfig = useCallback((widgetId, configPatch) => {
    setPages((prev) =>
      prev.map((p) => ({
        ...p,
        widgets: p.widgets.map((w) =>
          w.id === widgetId ? { ...w, config: { ...w.config, ...configPatch } } : w
        ),
      }))
    )
  }, [])

  const updateWidgetStyle = useCallback((widgetId, stylePatch) => {
    setPages((prev) =>
      prev.map((p) => ({
        ...p,
        widgets: p.widgets.map((w) =>
          w.id === widgetId ? { ...w, style: { ...w.style, ...stylePatch } } : w
        ),
      }))
    )
  }, [])

  const removeWidget = useCallback((widgetId) => {
    setPages((prev) =>
      prev.map((p) => ({
        ...p,
        widgets: p.widgets.filter((w) => w.id !== widgetId),
        layout: p.layout.filter((l) => l.i !== widgetId),
      }))
    )
    setSelectedWidgetId((cur) => (cur === widgetId ? null : cur))
  }, [])

  const updateLayout = useCallback((pageId, layout) => {
    setPages((prev) => prev.map((p) => (p.id === pageId ? { ...p, layout } : p)))
  }, [])

  const selectedWidget = useMemo(
    () => activePage?.widgets.find((w) => w.id === selectedWidgetId) || null,
    [activePage, selectedWidgetId]
  )

  const loadDataset = useCallback(async (id) => {
    const res = await api.getDataset(id)
    setDatasetId(id)
    setDatasetMeta(res.data)
    setGlobalFilters([])
  }, [])

  const saveDashboardToServer = useCallback(async () => {
    setSaving(true)
    try {
      const payload = {
        name: dashboardName,
        dataset_id: datasetId,
        theme: colorPalette,
        pages: pages,
      }
      if (dashboardId) {
        await api.updateDashboard(dashboardId, payload)
      } else {
        const res = await api.saveDashboard(payload)
        setDashboardId(res.data.id)
      }
    } finally {
      setSaving(false)
    }
  }, [dashboardId, dashboardName, datasetId, colorPalette, pages])

  const loadDashboardFromServer = useCallback(async (id) => {
    const res = await api.getDashboard(id)
    setDashboardId(res.data.id)
    setDashboardName(res.data.name)
    setColorPalette(res.data.theme || 'teal')
    if (res.data.dataset_id) await loadDataset(res.data.dataset_id)
    const loadedPages = res.data.pages && res.data.pages.length ? res.data.pages : [defaultPage()]
    setPages(loadedPages)
    setActivePageId(loadedPages[0].id)
  }, [loadDataset])

  const applyTemplate = useCallback((templatePages) => {
    setPages(templatePages)
    setActivePageId(templatePages[0].id)
  }, [])

  const value = {
    dashboardId, dashboardName, setDashboardName,
    colorPalette, setColorPalette,
    datasetId, datasetMeta, loadDataset, setDatasetId, setDatasetMeta,
    pages, setPages, activePage, activePageId, setActivePageId,
    addPage, removePage, renamePage, updatePage,
    addWidget, updateWidget, updateWidgetConfig, updateWidgetStyle, removeWidget, updateLayout,
    selectedWidgetId, setSelectedWidgetId, selectedWidget,
    globalFilters, setGlobalFilters,
    saving, saveDashboardToServer, loadDashboardFromServer,
    applyTemplate,
  }

  return <DashboardContext.Provider value={value}>{children}</DashboardContext.Provider>
}

function defaultTitleFor(type) {
  const map = {
    bar: 'Bar Chart', column: 'Column Chart', line: 'Line Chart', area: 'Area Chart',
    pie: 'Pie Chart', donut: 'Donut Chart', scatter: 'Scatter Plot', bubble: 'Bubble Chart',
    histogram: 'Histogram', heatmap: 'Heatmap', correlation: 'Correlation Matrix',
    box: 'Box Plot', violin: 'Violin Plot', treemap: 'Treemap', sunburst: 'Sunburst',
    funnel: 'Funnel Chart', waterfall: 'Waterfall Chart', radar: 'Radar Chart',
    polar: 'Polar Chart', parallel: 'Parallel Coordinates', pairplot: 'Pair Plot',
    gauge: 'Gauge', kpi: 'KPI Card', table: 'Table', matrix: 'Matrix', slicer: 'Slicer',
  }
  return map[type] || 'New Visual'
}

export const useDashboard = () => useContext(DashboardContext)
