import { saveAs } from 'file-saver'

// Downloads a backend-generated file (csv/xlsx/json/pdf) by hitting the URL directly.
export function downloadFromApi(url, filename) {
  const link = document.createElement('a')
  link.href = url
  link.download = filename || ''
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// Exports a single Plotly widget as PNG or SVG using Plotly's client-side renderer.
export async function exportPlotlyImage(gdEl, format = 'png', filename = 'chart') {
  const Plotly = await import('plotly.js-dist-min')
  const dataUrl = await Plotly.toImage(gdEl, { format, width: 1000, height: 700 })
  const res = await fetch(dataUrl)
  const blob = await res.blob()
  saveAs(blob, `${filename}.${format}`)
}

export function downloadJson(obj, filename = 'export.json') {
  const blob = new Blob([JSON.stringify(obj, null, 2)], { type: 'application/json' })
  saveAs(blob, filename)
}
