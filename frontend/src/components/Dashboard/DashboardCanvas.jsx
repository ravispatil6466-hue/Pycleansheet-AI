import React, { useCallback } from 'react'
import { WidthProvider, Responsive } from 'react-grid-layout'

const ResponsiveGridLayout = WidthProvider(Responsive)
import { useDashboard } from '../../context/DashboardContext'
import ChartWidget from '../Widgets/ChartWidget'
import KPICard from '../Widgets/KPICard'
import TableWidget from '../Widgets/TableWidget'
import SlicerWidget from '../Widgets/SlicerWidget'

const COLS = 24
const ROW_HEIGHT = 22

export default function DashboardCanvas() {
  const { activePage, updateLayout, addWidget } = useDashboard()
  const layout = activePage?.layout || []
  const widgets = activePage?.widgets || []

  const onLayoutChange = useCallback((newLayout) => {
    if (!activePage) return
    updateLayout(activePage.id, newLayout)
  }, [activePage, updateLayout])

  const onDrop = useCallback((_layout, layoutItem, e) => {
    const type = e.dataTransfer.getData('chart-type')
    if (!type) return
    addWidget(type)
  }, [addWidget])

  const renderWidget = (widget) => {
    if (widget.type === 'kpi') return <KPICard widget={widget} />
    if (widget.type === 'table' || widget.type === 'matrix') return <TableWidget widget={widget} />
    if (widget.type === 'slicer') return <SlicerWidget widget={widget} />
    return <ChartWidget widget={widget} />
  }

  return (
    <div
      className="relative flex-1 overflow-auto bg-slate-100 dark:bg-slate-900 p-3"
      onDragOver={(e) => e.preventDefault()}
    >
      {widgets.length === 0 && (
        <div className="flex h-full items-center justify-center">
          <div className="text-center max-w-sm">
            <p className="text-sm font-medium text-slate-400 dark:text-slate-500">
              Drag a visual from the left panel to start building your dashboard
            </p>
          </div>
        </div>
      )}
      <ResponsiveGridLayout
        className="layout"
        layouts={{ lg: layout }}
        breakpoints={{ lg: 1024, md: 768, sm: 480 }}
        cols={{ lg: COLS, md: COLS, sm: 12 }}
        rowHeight={ROW_HEIGHT}
        onLayoutChange={(l) => onLayoutChange(l)}
        isDroppable
        onDrop={onDrop}
        draggableHandle=".widget-header"
        compactType="vertical"
        preventCollision={false}
        margin={[10, 10]}
      >
        {widgets.map((w) => (
          <div key={w.id}>{renderWidget(w)}</div>
        ))}
      </ResponsiveGridLayout>
    </div>
  )
}
