// Central registry of chart types (icon key, label, category) + Plotly figure builders.

export const PALETTES = {
  teal: ['#1E7A6F', '#3F9D8E', '#E8A33D', '#0F3D5C', '#71BFB2', '#C96A3C', '#4C6B8A', '#9CCFC4'],
  sunset: ['#E8683D', '#F2A65A', '#8E3B46', '#F4D35E', '#EE964B', '#B4436C', '#3C1642', '#F29E4C'],
  ocean: ['#0F3D5C', '#1E7A6F', '#3E92CC', '#71BFB2', '#2A6F97', '#61A5C2', '#89C2D9', '#A9D6E5'],
  slate: ['#334155', '#64748B', '#94A3B8', '#0F172A', '#475569', '#CBD5E1', '#1E293B', '#E2E8F0'],
}

export function getPalette(name) {
  return PALETTES[name] || PALETTES.teal
}

export const CHART_CATALOG = [
  { type: 'bar', label: 'Bar Chart', category: 'Comparison', needs: ['x', 'y'] },
  { type: 'line', label: 'Line Chart', category: 'Trend', needs: ['x', 'y'] },
  { type: 'area', label: 'Area Chart', category: 'Trend', needs: ['x', 'y'] },
  { type: 'pie', label: 'Pie Chart', category: 'Proportion', needs: ['names', 'values'] },
  { type: 'donut', label: 'Donut Chart', category: 'Proportion', needs: ['names', 'values'] },
  { type: 'scatter', label: 'Scatter Plot', category: 'Relationship', needs: ['x', 'y'] },
  { type: 'bubble', label: 'Bubble Chart', category: 'Relationship', needs: ['x', 'y', 'size'] },
  { type: 'histogram', label: 'Histogram', category: 'Distribution', needs: ['x'] },
  { type: 'heatmap', label: 'Heatmap', category: 'Relationship', needs: [] },
  { type: 'box', label: 'Box Plot', category: 'Distribution', needs: ['y'] },
  { type: 'violin', label: 'Violin Plot', category: 'Distribution', needs: ['y'] },
  { type: 'treemap', label: 'Treemap', category: 'Proportion', needs: ['path', 'values'] },
  { type: 'sunburst', label: 'Sunburst', category: 'Proportion', needs: ['path', 'values'] },
  { type: 'funnel', label: 'Funnel Chart', category: 'Flow', needs: ['names', 'values'] },
  { type: 'waterfall', label: 'Waterfall Chart', category: 'Flow', needs: ['x', 'y'] },
  { type: 'radar', label: 'Radar Chart', category: 'Comparison', needs: ['theta', 'r'] },
  { type: 'polar', label: 'Polar Chart', category: 'Comparison', needs: ['theta', 'r'] },
  { type: 'parallel', label: 'Parallel Coordinates', category: 'Multi-dim', needs: ['dimensions'] },
  { type: 'pairplot', label: 'Pair Plot', category: 'Multi-dim', needs: ['dimensions'] },
  { type: 'correlation', label: 'Correlation Matrix', category: 'Relationship', needs: [] },
  { type: 'gauge', label: 'Gauge', category: 'KPI', needs: ['values'] },
  { type: 'kpi', label: 'KPI Card', category: 'KPI', needs: ['values'] },
  { type: 'table', label: 'Table', category: 'Table', needs: [] },
  { type: 'matrix', label: 'Matrix', category: 'Table', needs: [] },
  { type: 'slicer', label: 'Slicer', category: 'Filter', needs: [] },
]

export function chartTypeMeta(type) {
  return CHART_CATALOG.find((c) => c.type === type)
}

const baseLayout = (title, dark) => ({
  title: { text: title, font: { size: 13, family: 'Inter, sans-serif', color: dark ? '#E2E8F0' : '#334155' } },
  margin: { l: 48, r: 20, t: 36, b: 40 },
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor: 'rgba(0,0,0,0)',
  font: { family: 'Inter, sans-serif', color: dark ? '#CBD5E1' : '#475569', size: 11 },
  legend: { orientation: 'h', y: -0.2 },
  xaxis: { gridcolor: dark ? '#334155' : '#EEF2F6' },
  yaxis: { gridcolor: dark ? '#334155' : '#EEF2F6' },
  autosize: true,
})

// Builds { data, layout } for react-plotly given the backend chart payload.
export function buildFigure(type, payload, opts = {}) {
  const { title = '', dark = false, palette = PALETTES.teal, showLegend = true } = opts
  const layout = { ...baseLayout(title, dark), showlegend: showLegend }

  switch (type) {
    case 'bar':
    case 'column': {
      const data = (payload.series || []).map((s, i) => ({
        type: 'bar', name: s.name, x: payload.x, y: s.values,
        marker: { color: palette[i % palette.length] },
      }))
      return { data, layout }
    }
    case 'line': {
      const data = (payload.series || []).map((s, i) => ({
        type: 'scatter', mode: 'lines+markers', name: s.name, x: payload.x, y: s.values,
        line: { color: palette[i % palette.length], width: 2 },
      }))
      return { data, layout }
    }
    case 'area': {
      const data = (payload.series || []).map((s, i) => ({
        type: 'scatter', mode: 'lines', fill: 'tozeroy', name: s.name, x: payload.x, y: s.values,
        line: { color: palette[i % palette.length] },
      }))
      return { data, layout }
    }
    case 'pie': {
      return { data: [{ type: 'pie', labels: payload.labels, values: payload.values, marker: { colors: palette } }], layout }
    }
    case 'donut': {
      return { data: [{ type: 'pie', hole: 0.55, labels: payload.labels, values: payload.values, marker: { colors: palette } }], layout }
    }
    case 'funnel': {
      return { data: [{ type: 'funnel', y: payload.labels, x: payload.values, marker: { color: palette } }], layout }
    }
    case 'scatter': {
      const data = [{
        type: 'scatter', mode: 'markers', x: payload.x, y: payload.y,
        marker: {
          color: payload.color ? payload.color.map((_, i) => palette[i % palette.length]) : palette[0],
          size: 9,
        },
        text: payload.color || undefined,
      }]
      return { data, layout }
    }
    case 'bubble': {
      const sizes = payload.size || payload.y.map(() => 10)
      const maxSize = Math.max(...sizes, 1)
      const data = [{
        type: 'scatter', mode: 'markers', x: payload.x, y: payload.y,
        marker: { size: sizes.map((s) => 8 + (s / maxSize) * 32), color: palette[0], opacity: 0.7 },
      }]
      return { data, layout }
    }
    case 'histogram': {
      return { data: [{ type: 'histogram', x: payload.values, marker: { color: palette[0] } }], layout }
    }
    case 'box': {
      if (payload.grouped) {
        const data = Object.entries(payload.groups).map(([g, vals], i) => ({
          type: 'box', name: g, y: vals, marker: { color: palette[i % palette.length] },
        }))
        return { data, layout }
      }
      const data = Object.entries(payload.series).map(([name, vals], i) => ({
        type: 'box', name, y: vals, marker: { color: palette[i % palette.length] },
      }))
      return { data, layout }
    }
    case 'violin': {
      if (payload.grouped) {
        const data = Object.entries(payload.groups).map(([g, vals], i) => ({
          type: 'violin', name: g, y: vals, box: { visible: true }, meanline: { visible: true },
          marker: { color: palette[i % palette.length] },
        }))
        return { data, layout }
      }
      const data = Object.entries(payload.series).map(([name, vals], i) => ({
        type: 'violin', name, y: vals, box: { visible: true }, meanline: { visible: true },
        marker: { color: palette[i % palette.length] },
      }))
      return { data, layout }
    }
    case 'heatmap':
    case 'correlation': {
      return {
        data: [{
          type: 'heatmap', z: payload.matrix, x: payload.columns, y: payload.columns,
          colorscale: 'RdBu', reversescale: true, zmin: -1, zmax: 1,
        }],
        layout: { ...layout, xaxis: { ...layout.xaxis, tickangle: -35 } },
      }
    }
    case 'treemap': {
      const { labels, parents, values } = flattenPath(payload)
      return { data: [{ type: 'treemap', labels, parents, values, marker: { colors: palette } }], layout }
    }
    case 'sunburst': {
      const { labels, parents, values } = flattenPath(payload)
      return { data: [{ type: 'sunburst', labels, parents, values, marker: { colors: palette } }], layout }
    }
    case 'waterfall': {
      return {
        data: [{
          type: 'waterfall', x: payload.x, y: payload.y,
          decreasing: { marker: { color: '#C96A3C' } },
          increasing: { marker: { color: palette[0] } },
          totals: { marker: { color: palette[3] || '#0F3D5C' } },
        }],
        layout,
      }
    }
    case 'radar':
    case 'polar': {
      return {
        data: [{
          type: 'scatterpolar', r: [...payload.r, payload.r[0]], theta: [...payload.theta, payload.theta[0]],
          fill: 'toself', line: { color: palette[0] },
        }],
        layout: { ...layout, polar: { radialaxis: { visible: true } } },
      }
    }
    case 'parallel': {
      const dims = payload.dimensions.map((d) => ({ label: d, values: payload.data[d] }))
      return { data: [{ type: 'parcoords', line: { color: palette[0] }, dimensions: dims }], layout }
    }
    case 'pairplot': {
      const dims = payload.dimensions
      return {
        data: [{
          type: 'splom', dimensions: dims.map((d) => ({ label: d, values: payload.data[d] })),
          marker: { color: palette[0], size: 4, opacity: 0.6 },
        }],
        layout: { ...layout, height: undefined },
      }
    }
    case 'gauge': {
      return {
        data: [{
          type: 'indicator', mode: 'gauge+number', value: payload.value,
          gauge: {
            axis: { range: [payload.min, payload.max] },
            bar: { color: palette[0] },
            steps: [
              { range: [payload.min, (payload.min + payload.max) / 2], color: dark ? '#1E293B' : '#EEF2F6' },
            ],
          },
        }],
        layout: { ...layout, margin: { l: 20, r: 20, t: 40, b: 10 } },
      }
    }
    default:
      return { data: [], layout }
  }
}

function flattenPath(payload) {
  const { path_columns: pathCols, records, value_column: valueCol } = payload
  const labels = [], parents = [], values = []
  const seen = new Set()
  for (const rec of records) {
    let parentLabel = ''
    for (let i = 0; i < pathCols.length; i++) {
      const col = pathCols[i]
      const label = String(rec[col])
      const fullLabel = i === 0 ? label : `${parentLabel} / ${label}`
      if (!seen.has(fullLabel)) {
        seen.add(fullLabel)
        labels.push(fullLabel)
        parents.push(parentLabel)
        values.push(i === pathCols.length - 1 ? rec[valueCol] : 0)
      }
      parentLabel = fullLabel
    }
  }
  return { labels, parents, values }
}
