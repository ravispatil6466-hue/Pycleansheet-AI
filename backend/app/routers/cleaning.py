import json
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Dataset
from app.services import data_service, cleaning_service
from app.schemas import (MissingValueRequest, DuplicateRequest, OutlierRequest,
                          TypeConversionRequest, RenameRequest, NormalizeRequest, EncodeRequest)

router = APIRouter(prefix="/api/cleaning", tags=["cleaning"])


def _load(dataset_id):
    try:
        return data_service.load_dataframe(dataset_id)
    except FileNotFoundError:
        raise HTTPException(404, "Dataset not found")


def _persist(dataset_id, df, db: Session):
    data_service.save_dataframe(dataset_id, df)
    record = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if record:
        record.rows = len(df)
        record.cols = len(df.columns)
        record.columns_meta = json.dumps(data_service.infer_columns_meta(df))
        db.commit()
    return data_service.df_preview(df, limit=50)


@router.get("/{dataset_id}/quality-report")
def quality_report(dataset_id: str):
    df = _load(dataset_id)
    return cleaning_service.quality_report(df)


@router.post("/{dataset_id}/missing")
def clean_missing(dataset_id: str, req: MissingValueRequest, db: Session = Depends(get_db)):
    df = _load(dataset_id)
    df = cleaning_service.handle_missing(df, req.columns, req.strategy, req.constant_value)
    return _persist(dataset_id, df, db)


@router.post("/{dataset_id}/duplicates")
def clean_duplicates(dataset_id: str, req: DuplicateRequest, db: Session = Depends(get_db)):
    df = _load(dataset_id)
    df = cleaning_service.remove_duplicates(df, req.subset, req.keep)
    return _persist(dataset_id, df, db)


@router.post("/{dataset_id}/outliers")
def clean_outliers(dataset_id: str, req: OutlierRequest, db: Session = Depends(get_db)):
    df = _load(dataset_id)
    df = cleaning_service.handle_outliers(df, req.columns, req.method, req.action, req.threshold)
    return _persist(dataset_id, df, db)


@router.post("/{dataset_id}/type-conversion")
def clean_type(dataset_id: str, req: TypeConversionRequest, db: Session = Depends(get_db)):
    df = _load(dataset_id)
    try:
        df = cleaning_service.convert_type(df, req.column, req.target_type)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return _persist(dataset_id, df, db)


@router.post("/{dataset_id}/rename")
def clean_rename(dataset_id: str, req: RenameRequest, db: Session = Depends(get_db)):
    df = _load(dataset_id)
    df = cleaning_service.rename_columns(df, req.mapping)
    return _persist(dataset_id, df, db)


@router.post("/{dataset_id}/normalize")
def clean_normalize(dataset_id: str, req: NormalizeRequest, db: Session = Depends(get_db)):
    df = _load(dataset_id)
    df = cleaning_service.normalize_columns(df, req.columns, req.method)
    return _persist(dataset_id, df, db)


@router.post("/{dataset_id}/encode")
def clean_encode(dataset_id: str, req: EncodeRequest, db: Session = Depends(get_db)):
    df = _load(dataset_id)
    df = cleaning_service.encode_columns(df, req.columns, req.method)
    return _persist(dataset_id, df, db)
