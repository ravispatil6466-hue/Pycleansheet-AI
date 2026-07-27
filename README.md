# 🧠 Pycleansheet AI — Intelligent Data Cleaning, Analytics & Dashboard Platform

A Power BI / Tableau / Looker Studio–inspired analytics platform built entirely in Python + Streamlit.

## Features

- **Upload** — CSV, Excel, JSON, or a bundled sample retail dataset
- **Data Cleaning Studio** — missing values, duplicates, outlier handling (IQR), text cleanup, column rename/dtype conversion, scaling & encoding, full **undo/redo** + cleaning history
- **EDA** — summary statistics, correlation matrix, missing-value & outlier reports, categorical/numerical analysis, AI dataset summary
- **Dashboard Builder** — add / duplicate / delete / reorder / resize / lock charts on a 3-column snap grid, zoom, save/load/import/export layout as JSON (the practical equivalent of Power BI's drag-and-drop, since native Streamlit has no mouse drag API)
- **14 chart types** — bar, line, pie, scatter, histogram, heatmap, box, area, treemap, sunburst, violin, pair plot, distribution, correlation matrix — each with a full **Format Panel** (colors, fonts, borders, opacity, size, legend/grid/tooltip toggles, palettes, themes)
- **Filter Panel** — global search, range sliders, date filters, multi-select slicers, applied live
- **AI Chatbot** — ask about your dataset (summaries, correlations, trends, recommendations). Works out of the box with a built-in analyzer; optionally upgrade with your own Anthropic or OpenAI API key (entered in the sidebar, session-only, never stored)
- **Natural Language Analytics** — type "show sales by city" or "top 5 category" to auto-generate a chart
- **Python Editor** — run Python directly against the working dataframe, `df` updates live
- **Report Generator** — one-click HTML report (dataset summary, cleaning history, EDA highlights, dashboard chart list, AI insights) — no PDF library dependency; open it in a browser and use Print → Save as PDF if you want an actual PDF file
- **Export Center** — cleaned dataset as CSV/Excel/JSON; charts as interactive HTML, PNG, or SVG

## Setup

```bash
cd Pycleansheet_AI
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Then open the URL Streamlit prints (usually `http://localhost:8501`).

### Optional: PNG/SVG chart export
PNG/SVG chart export uses the optional `kaleido` package:
```bash
pip install kaleido
```
Without it, chart export still works via interactive HTML.

### Optional: AI Chatbot with a real LLM
By default the AI Chatbot and AI Summary use a built-in rule-based analyzer — no setup needed. To use Claude or GPT instead, open **⚙️ AI Settings** in the sidebar, choose a provider, and paste your own API key. The key is kept in-session only.

## Project Structure

```
Pycleansheet_AI/
├── app.py                  # Main entry point / navigation
├── requirements.txt
├── src/
│   ├── theme.py             # Glassmorphism CSS, dark/light mode
│   ├── state.py              # Session state, undo/redo
│   ├── components.py         # KPI cards, filter panel, format panel
│   ├── upload.py              # Dataset upload page
│   ├── cleaning.py            # Data Cleaning Studio
│   ├── eda.py                  # Exploratory Data Analysis
│   ├── charts.py                # Chart factory (14 chart types)
│   ├── dashboard.py              # Dashboard Builder
│   ├── chatbot.py                 # AI Chatbot & NL analytics
│   ├── python_editor.py            # Embedded Python code editor
│   ├── reports.py                   # HTML report generator (no PDF library needed)
│   └── export.py                     # Export Center
```

## Notes on scope

This app faithfully implements every functional category requested (cleaning, EDA, 14 chart types, KPI cards, filters, format panel, AI chatbot, NL analytics, Python editor, reports, exports) in a real, running codebase. One honest caveat: true Power BI–style mouse drag-and-drop/resize is not something native Streamlit supports, so the Dashboard Builder implements the equivalent capability (add/duplicate/delete/reorder/resize/lock/save/load) through buttons and controls rather than pretending to fake a drag API that wouldn't actually work in the browser.
