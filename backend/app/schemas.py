from pydantic import BaseModel
from typing import Any, Optional, List, Dict


class DatasetOut(BaseModel):
    id: str
    name: str
    original_filename: str
    file_format: str
    rows: int
    cols: int
    columns_meta: Dict[str, Any]

    class Config:
        from_attributes = True


class MissingValueRequest(BaseModel):
    columns: Optional[List[str]] = None
    strategy: str = "mean"  # mean | median | mode | constant | drop_rows | ffill | bfill
    constant_value: Optional[Any] = None


class DuplicateRequest(BaseModel):
    subset: Optional[List[str]] = None
    keep: str = "first"  # first | last | none


class OutlierRequest(BaseModel):
    columns: List[str]
    method: str = "iqr"  # iqr | zscore
    action: str = "remove"  # remove | cap
    threshold: float = 1.5


class TypeConversionRequest(BaseModel):
    column: str
    target_type: str  # int | float | string | datetime | category | bool


class RenameRequest(BaseModel):
    mapping: Dict[str, str]


class NormalizeRequest(BaseModel):
    columns: List[str]
    method: str = "standard"  # standard | minmax | robust


class EncodeRequest(BaseModel):
    columns: List[str]
    method: str = "onehot"  # onehot | label


class ChartDataRequest(BaseModel):
    chart_type: str
    x: Optional[str] = None
    y: Optional[List[str]] = None
    color: Optional[str] = None
    size: Optional[str] = None
    aggregation: Optional[str] = "sum"  # sum | avg | count | min | max | median
    filters: Optional[List[Dict[str, Any]]] = None
    top_n: Optional[int] = None
    values: Optional[str] = None
    names: Optional[str] = None
    theta: Optional[str] = None
    r: Optional[str] = None
    path: Optional[List[str]] = None
    dimensions: Optional[List[str]] = None


class CodeExecRequest(BaseModel):
    dataset_id: str
    code: str


class ChatRequest(BaseModel):
    dataset_id: Optional[str] = None
    message: str
    history: Optional[List[Dict[str, str]]] = None


class DashboardSave(BaseModel):
    name: str
    dataset_id: Optional[str] = None
    theme: str = "light"
    pages: List[Dict[str, Any]]


class DashboardOut(BaseModel):
    id: str
    name: str
    dataset_id: Optional[str]
    theme: str
    pages: List[Dict[str, Any]]

    class Config:
        from_attributes = True
