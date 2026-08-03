from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ChatMessage
from app.services import data_service, ai_service
from app.schemas import ChatRequest

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/chat")
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    df = None
    if req.dataset_id:
        try:
            df = data_service.load_dataframe(req.dataset_id)
        except FileNotFoundError:
            df = None
    reply = ai_service.chat_completion(req.message, df, req.history)

    db.add(ChatMessage(dataset_id=req.dataset_id, role="user", content=req.message))
    db.add(ChatMessage(dataset_id=req.dataset_id, role="assistant", content=reply))
    db.commit()

    return {"reply": reply}


@router.get("/chat/{dataset_id}/history")
def history(dataset_id: str, db: Session = Depends(get_db)):
    rows = db.query(ChatMessage).filter(ChatMessage.dataset_id == dataset_id).order_by(ChatMessage.created_at).all()
    return [{"role": r.role, "content": r.content} for r in rows]
