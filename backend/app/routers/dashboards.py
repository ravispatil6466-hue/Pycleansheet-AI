import json
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Dashboard
from app.schemas import DashboardSave

router = APIRouter(prefix="/api/dashboards", tags=["dashboards"])


@router.post("")
def create_dashboard(req: DashboardSave, db: Session = Depends(get_db)):
    d = Dashboard(name=req.name, dataset_id=req.dataset_id, theme=req.theme, pages_json=json.dumps(req.pages))
    db.add(d)
    db.commit()
    db.refresh(d)
    return {"id": d.id, "name": d.name}


@router.get("")
def list_dashboards(db: Session = Depends(get_db)):
    rows = db.query(Dashboard).order_by(Dashboard.updated_at.desc()).all()
    return [{"id": r.id, "name": r.name, "dataset_id": r.dataset_id, "theme": r.theme,
              "updated_at": r.updated_at.isoformat()} for r in rows]


@router.get("/{dashboard_id}")
def get_dashboard(dashboard_id: str, db: Session = Depends(get_db)):
    r = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if not r:
        raise HTTPException(404, "Dashboard not found")
    return {"id": r.id, "name": r.name, "dataset_id": r.dataset_id, "theme": r.theme,
             "pages": json.loads(r.pages_json)}


@router.put("/{dashboard_id}")
def update_dashboard(dashboard_id: str, req: DashboardSave, db: Session = Depends(get_db)):
    r = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if not r:
        raise HTTPException(404, "Dashboard not found")
    r.name = req.name
    r.dataset_id = req.dataset_id
    r.theme = req.theme
    r.pages_json = json.dumps(req.pages)
    db.commit()
    return {"success": True}


@router.delete("/{dashboard_id}")
def delete_dashboard(dashboard_id: str, db: Session = Depends(get_db)):
    r = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if not r:
        raise HTTPException(404, "Dashboard not found")
    db.delete(r)
    db.commit()
    return {"success": True}
