from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from app.services import data_service, export_service, cleaning_service, eda_service

router = APIRouter(prefix="/api/export", tags=["export"])


def _load(dataset_id):
    try:
        return data_service.load_dataframe(dataset_id)
    except FileNotFoundError:
        raise HTTPException(404, "Dataset not found")


@router.get("/{dataset_id}/csv")
def export_csv(dataset_id: str):
    df = _load(dataset_id)
    data = export_service.to_csv_bytes(df)
    return Response(content=data, media_type="text/csv",
                     headers={"Content-Disposition": f"attachment; filename={dataset_id}.csv"})


@router.get("/{dataset_id}/excel")
def export_excel(dataset_id: str):
    df = _load(dataset_id)
    data = export_service.to_excel_bytes(df)
    return Response(content=data, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                     headers={"Content-Disposition": f"attachment; filename={dataset_id}.xlsx"})


@router.get("/{dataset_id}/json")
def export_json(dataset_id: str):
    df = _load(dataset_id)
    data = export_service.to_json_bytes(df)
    return Response(content=data, media_type="application/json",
                     headers={"Content-Disposition": f"attachment; filename={dataset_id}.json"})


@router.get("/{dataset_id}/pdf-report")
def export_pdf(dataset_id: str):
    df = _load(dataset_id)
    quality = cleaning_service.quality_report(df)
    summary = eda_service.summary_stats(df)
    pdf_bytes = export_service.build_pdf_report("Pycleansheet AI - Data Report", quality, summary)
    return Response(content=pdf_bytes, media_type="application/pdf",
                     headers={"Content-Disposition": f"attachment; filename={dataset_id}_report.pdf"})
