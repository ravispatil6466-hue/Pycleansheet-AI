"""
Core dataset storage/cache service.
Datasets are persisted to disk as parquet (fast) under DATA_DIR/<id>.parquet
and metadata is kept in the SQL database. An in-memory LRU-ish cache avoids
re-reading parquet on every request within a process lifetime.
"""
import json
import os
import uuid
from typing import Optional
import pandas as pd
import numpy as np
from app.config import settings

_CACHE: dict[str, pd.DataFrame] = {}
_CACHE_ORDER: list[str] = []
_MAX_CACHE = 20


def _cache_put(dataset_id: str, df: pd.DataFrame):
    _CACHE[dataset_id] = df
    if dataset_id in _CACHE_ORDER:
        _CACHE_ORDER.remove(dataset_id)
    _CACHE_ORDER.append(dataset_id)
    while len(_CACHE_ORDER) > _MAX_CACHE:
        old = _CACHE_ORDER.pop(0)
        _CACHE.pop(old, None)


def _parquet_path(dataset_id: str) -> str:
    return os.path.join(settings.DATA_DIR, f"{dataset_id}.parquet")


def save_dataframe(dataset_id: str, df: pd.DataFrame):
    path = _parquet_path(dataset_id)
    # Parquet requires string column names
    df.columns = [str(c) for c in df.columns]
    df.to_parquet(path, index=False)
    _cache_put(dataset_id, df)


def load_dataframe(dataset_id: str) -> pd.DataFrame:
    if dataset_id in _CACHE:
        return _CACHE[dataset_id]
    path = _parquet_path(dataset_id)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset {dataset_id} not found")
    df = pd.read_parquet(path)
    _cache_put(dataset_id, df)
    return df


def read_upload(file_path: str, file_format: str) -> pd.DataFrame:
    if file_format == "csv":
        return pd.read_csv(file_path)
    if file_format in ("xlsx", "xls"):
        return pd.read_excel(file_path)
    if file_format == "json":
        return pd.read_json(file_path)
    if file_format == "parquet":
        return pd.read_parquet(file_path)
    raise ValueError(f"Unsupported file format: {file_format}")


def infer_columns_meta(df: pd.DataFrame) -> dict:
    meta = {}
    for col in df.columns:
        dtype = str(df[col].dtype)
        if pd.api.types.is_numeric_dtype(df[col]):
            kind = "numeric"
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            kind = "datetime"
        elif pd.api.types.is_bool_dtype(df[col]):
            kind = "boolean"
        else:
            kind = "categorical"
        meta[col] = {
            "dtype": dtype,
            "kind": kind,
            "missing": int(df[col].isna().sum()),
            "unique": int(df[col].nunique(dropna=True)),
        }
    return meta


def df_preview(df: pd.DataFrame, limit: int = 100, offset: int = 0) -> dict:
    total = len(df)
    chunk = df.iloc[offset: offset + limit]
    return {
        "total_rows": total,
        "offset": offset,
        "limit": limit,
        "columns": [str(c) for c in df.columns],
        "rows": json.loads(chunk.to_json(orient="records", date_format="iso")),
    }


def sanitize_json(obj):
    """Recursively convert numpy/pandas types + NaN/Inf into JSON-safe values."""
    if isinstance(obj, dict):
        return {k: sanitize_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [sanitize_json(v) for v in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        v = float(obj)
        if np.isnan(v) or np.isinf(v):
            return None
        return v
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, float):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return obj
    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    return obj


def new_id() -> str:
    return str(uuid.uuid4())
