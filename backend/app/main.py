from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings, cors_origins_list
from app.database import Base, engine
from app.routers import datasets, cleaning, eda, charts, code_exec, ai_chat, export, dashboards

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Pycleansheet AI",
    description="Intelligent Data Cleaning, Analytics & Dashboard Platform API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(datasets.router)
app.include_router(cleaning.router)
app.include_router(eda.router)
app.include_router(charts.router)
app.include_router(code_exec.router)
app.include_router(ai_chat.router)
app.include_router(export.router)
app.include_router(dashboards.router)


@app.get("/")
def root():
    return {"name": "Pycleansheet AI API", "status": "ok", "version": "1.0.0"}


@app.get("/api/health")
def health():
    return {"status": "healthy"}
