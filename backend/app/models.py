import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey
from app.database import Base


def gen_id():
    return str(uuid.uuid4())


class Dataset(Base):
    __tablename__ = "datasets"
    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_format = Column(String, nullable=False)
    rows = Column(Integer, default=0)
    cols = Column(Integer, default=0)
    columns_meta = Column(Text, default="{}")  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Dashboard(Base):
    __tablename__ = "dashboards"
    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, nullable=False)
    dataset_id = Column(String, ForeignKey("datasets.id"), nullable=True)
    theme = Column(String, default="light")
    pages_json = Column(Text, default="[]")  # serialized pages/widgets/layout
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(String, primary_key=True, default=gen_id)
    dataset_id = Column(String, nullable=True)
    role = Column(String, nullable=False)  # user | assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
