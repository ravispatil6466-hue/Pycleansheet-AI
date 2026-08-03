from fastapi import APIRouter, HTTPException
from app.services import data_service, code_exec_service
from app.schemas import CodeExecRequest

router = APIRouter(prefix="/api/code", tags=["code"])


@router.post("/execute")
def execute(req: CodeExecRequest):
    try:
        df = data_service.load_dataframe(req.dataset_id)
    except FileNotFoundError:
        raise HTTPException(404, "Dataset not found")
    banned = ["import os", "import sys", "subprocess", "__import__", "open(", "eval(", "exec(", "compile("]
    lowered = req.code.lower()
    for b in banned:
        if b in lowered:
            raise HTTPException(400, f"Code contains disallowed pattern: '{b}'")
    result = code_exec_service.run_code(df, req.code)
    return result
