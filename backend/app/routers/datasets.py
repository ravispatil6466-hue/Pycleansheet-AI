import json
import os
import shutil
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Dataset
from app.config import settings
from app.services import data_service

router = APIRouter(prefix="/api/datasets", tags=["datasets"])


@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...), db: Session = Depends(get_db)):
    ext = file.filename.split(".")[-1].lower()
    if ext not in ("csv", "xlsx", "xls", "json", "parquet"):
        raise HTTPException(400, f"Unsupported file type: {ext}")

    dataset_id = data_service.new_id()
    tmp_path = os.path.join(settings.DATA_DIR, f"{dataset_id}_upload.{ext}")
    with open(tmp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        df = data_service.read_upload(tmp_path, ext)
    except Exception as e:
        os.remove(tmp_path)
        raise HTTPException(400, f"Failed to parse file: {e}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    data_service.save_dataframe(dataset_id, df)
    meta = data_service.infer_columns_meta(df)

    record = Dataset(
        id=dataset_id,
        name=file.filename.rsplit(".", 1)[0],
        original_filename=file.filename,
        file_path=data_service._parquet_path(dataset_id),
        file_format=ext,
        rows=len(df),
        cols=len(df.columns),
        columns_meta=json.dumps(meta),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    preview = data_service.df_preview(df, limit=50)
    return {
        "id": record.id,
        "name": record.name,
        "original_filename": record.original_filename,
        "file_format": record.file_format,
        "rows": record.rows,
        "cols": record.cols,
        "columns_meta": meta,
        "preview": preview,
    }


@router.get("")
def list_datasets(db: Session = Depends(get_db)):
    rows = db.query(Dataset).order_by(Dataset.created_at.desc()).all()
    return [{
        "id": r.id, "name": r.name, "original_filename": r.original_filename,
        "file_format": r.file_format, "rows": r.rows, "cols": r.cols,
        "created_at": r.created_at.isoformat(),
    } for r in rows]


@router.get("/{dataset_id}")
def get_dataset(dataset_id: str, db: Session = Depends(get_db)):
    r = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not r:
        raise HTTPException(404, "Dataset not found")
    return {
        "id": r.id, "name": r.name, "original_filename": r.original_filename,
        "file_format": r.file_format, "rows": r.rows, "cols": r.cols,
        "columns_meta": json.loads(r.columns_meta),
    }


@router.get("/{dataset_id}/preview")
def preview_dataset(dataset_id: str, limit: int = Query(100, le=1000), offset: int = 0):
    try:
        df = data_service.load_dataframe(dataset_id)
    except FileNotFoundError:
        raise HTTPException(404, "Dataset not found")
    return data_service.df_preview(df, limit=limit, offset=offset)


@router.delete("/{dataset_id}")
def delete_dataset(dataset_id: str, db: Session = Depends(get_db)):
    r = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not r:
        raise HTTPException(404, "Dataset not found")
    if os.path.exists(r.file_path):
        os.remove(r.file_path)
    db.delete(r)
    db.commit()
    return {"success": True}
