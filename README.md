<<<<<<< HEAD
# Pycleansheet AI

**Intelligent Data Cleaning, Analytics & Dashboard Platform** — a Power BI–style, full-stack
web app for uploading, cleaning, exploring, and visualizing tabular data with a true
drag‑and‑drop dashboard builder and an AI chatbot.

No Streamlit. Real React frontend, real FastAPI backend.

---

## ✨ Features

- **True drag‑and‑drop dashboard builder** (React Grid Layout) — free movement, resize,
  snap‑to‑grid, multi‑page dashboards
- **Power BI–style UI** — ribbon toolbar, left visualization pane, fields pane, right
  formatting pane, bottom page tabs
- **20+ chart types** via Plotly.js: Bar, Line, Area, Pie, Donut, Scatter, Bubble,
  Histogram, Heatmap, Box, Violin, Treemap, Sunburst, Funnel, Waterfall, Radar, Polar,
  Parallel Coordinates, Pair Plot, Correlation Matrix, Gauge, KPI Cards, Table, Matrix
- **KPI cards & slicers** with global cross-filtering
- **Dashboard templates** and light/dark themes with multiple color palettes
- **Data cleaning & preprocessing**: missing values, duplicates, outliers (IQR/Z‑score),
  type conversion, renaming, normalization (StandardScaler/MinMax/Robust), encoding
  (one‑hot/label)
- **EDA**: summary statistics, correlation matrix, distributions
- **Python code execution sandbox** — run pandas/numpy/scikit-learn code directly against
  the uploaded dataset from the browser
- **AI chatbot** (OpenAI or Gemini, pluggable) for dataset Q&A, cleaning suggestions, and
  chart recommendations — falls back to a rule‑based assistant if no API key is set
- **Exports**: CSV, Excel, JSON, PDF report (server-side), PNG/SVG (client-side per chart)

---

## 🏗️ Tech Stack

**Frontend:** React 18, Vite, Tailwind CSS, React Grid Layout, Plotly.js
(`react-plotly.js`), Axios, React Router

**Backend:** FastAPI, Pandas, NumPy, Scikit-learn, SQLAlchemy (SQLite), ReportLab,
OpenAI / Google Generative AI SDKs

---

## 📁 Project Structure

```
pycleansheet-ai/
├── backend/
│   ├── app/
│   │   ├── main.py                # FastAPI app entrypoint
│   │   ├── config.py               # Settings (env vars)
│   │   ├── database.py             # SQLAlchemy engine/session
│   │   ├── models.py               # Dataset / Dashboard / ChatMessage tables
│   │   ├── schemas.py              # Pydantic request/response models
│   │   ├── routers/                # REST API endpoints
│   │   │   ├── datasets.py
│   │   │   ├── cleaning.py
│   │   │   ├── eda.py
│   │   │   ├── charts.py
│   │   │   ├── code_exec.py
│   │   │   ├── ai_chat.py
│   │   │   ├── export.py
│   │   │   └── dashboards.py
│   │   └── services/                # Business logic
│   │       ├── data_service.py
│   │       ├── cleaning_service.py
│   │       ├── eda_service.py
│   │       ├── chart_service.py
│   │       ├── ai_service.py
│   │       ├── export_service.py
│   │       └── code_exec_service.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── api/axiosClient.js       # All API calls
│   │   ├── context/                 # Theme + Dashboard state
│   │   ├── components/
│   │   │   ├── Ribbon/              # Top toolbar
│   │   │   ├── Panes/               # Visualization / Fields / Formatting panes
│   │   │   ├── Dashboard/           # Canvas, page tabs, templates
│   │   │   ├── Widgets/             # Chart / KPI / Table / Slicer widgets
│   │   │   ├── Chatbot/             # AI chat panel
│   │   │   ├── DataPanel/           # Upload / Clean / EDA / Code Studio
│   │   │   └── Common/              # Modal, ThemeToggle
│   │   ├── pages/                   # HomePage, DashboardPage, DataStudioPage
│   │   └── utils/                   # Chart config + export helpers
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
└── README.md
```

---

## 🚀 Getting Started (local development)

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # add your OPENAI_API_KEY / GEMINI_API_KEY (optional)
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000` (docs at `/docs`).

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:5173`. The Vite dev server proxies `/api`
requests to `http://localhost:8000` (see `vite.config.js`).

---

## 🐳 Getting Started (Docker)

```bash
cp backend/.env.example backend/.env   # add your API keys (optional)
docker compose up --build
```

- Frontend: http://localhost
- Backend API: http://localhost:8000/docs

---

## 🤖 AI Chatbot Configuration

Set **one** of the following in `backend/.env`:

```
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

or

```
AI_PROVIDER=gemini
GEMINI_API_KEY=...
```

If no key is configured, the chatbot automatically falls back to a rule‑based assistant
that can still answer basic questions about missing values, correlations, and dataset
shape, so the app is fully functional without any external API key.

---

## 🔒 Security Notes

- The Python code execution endpoint (`/api/code/execute`) runs user code in a separate
  process with a restricted builtins list and a wall-clock timeout, exposing only
  `pandas`, `numpy`, and a few `scikit-learn` modules plus the loaded `df`. It also
  blocks obvious dangerous patterns (`import os`, `subprocess`, `eval`, etc.) at the API
  layer. For a public multi-tenant deployment, run this in a fully isolated
  container/VM sandbox instead of in-process `exec()`.
- CORS origins are restricted via `CORS_ORIGINS` in `backend/.env`.

---

## 📊 REST API Overview

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/datasets/upload` | Upload CSV/XLSX/JSON/Parquet |
| GET | `/api/datasets/{id}/preview` | Paginated data preview |
| GET | `/api/cleaning/{id}/quality-report` | Missing values, duplicates, dtypes |
| POST | `/api/cleaning/{id}/missing` | Handle missing values |
| POST | `/api/cleaning/{id}/duplicates` | Remove duplicates |
| POST | `/api/cleaning/{id}/outliers` | Detect/handle outliers |
| POST | `/api/cleaning/{id}/type-conversion` | Convert column dtype |
| POST | `/api/cleaning/{id}/normalize` | Scale numeric columns |
| POST | `/api/cleaning/{id}/encode` | One-hot / label encode |
| GET | `/api/eda/{id}/summary` | Descriptive statistics |
| GET | `/api/eda/{id}/correlation` | Correlation matrix |
| GET | `/api/eda/{id}/distribution/{col}` | Histogram / value counts |
| POST | `/api/charts/{id}/data` | Chart-ready aggregated data for any chart type |
| POST | `/api/code/execute` | Run sandboxed Python against the dataset |
| POST | `/api/ai/chat` | AI chatbot completion |
| GET | `/api/export/{id}/csv` \| `excel` \| `json` \| `pdf-report` | File exports |
| CRUD | `/api/dashboards` | Save/load dashboard layouts |

Full interactive documentation is auto-generated by FastAPI at `/docs`.

---

## 📦 Packaging

This repository is ready to be zipped and shared as-is. See `pycleansheet-ai.zip` in the
project root (if generated) for a ready-to-distribute archive.

---

## 📝 License

MIT — build on top of this freely.
=======
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
>>>>>>> a3072ea40416663e2905c19980ef3ca92b26e8c1
