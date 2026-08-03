from fastapi import APIRouter, HTTPException
from app.services import data_service, chart_service
from app.schemas import ChartDataRequest

router = APIRouter(prefix="/api/charts", tags=["charts"])


@router.post("/{dataset_id}/data")
def chart_data(dataset_id: str, req: ChartDataRequest):
    try:
        df = data_service.load_dataframe(dataset_id)
    except FileNotFoundError:
        raise HTTPException(404, "Dataset not found")
    return chart_service.build_chart_data(df, req)
