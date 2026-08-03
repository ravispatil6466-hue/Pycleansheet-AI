from fastapi import APIRouter, HTTPException
from app.services import data_service, eda_service

router = APIRouter(prefix="/api/eda", tags=["eda"])


def _load(dataset_id):
    try:
        return data_service.load_dataframe(dataset_id)
    except FileNotFoundError:
        raise HTTPException(404, "Dataset not found")


@router.get("/{dataset_id}/summary")
def summary(dataset_id: str):
    return eda_service.summary_stats(_load(dataset_id))


@router.get("/{dataset_id}/correlation")
def correlation(dataset_id: str, method: str = "pearson"):
    return eda_service.correlation_matrix(_load(dataset_id), method)


@router.get("/{dataset_id}/distribution/{column}")
def dist(dataset_id: str, column: str, bins: int = 20):
    try:
        return eda_service.distribution(_load(dataset_id), column, bins)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/{dataset_id}/report")
def report(dataset_id: str):
    return eda_service.full_eda_report(_load(dataset_id))
