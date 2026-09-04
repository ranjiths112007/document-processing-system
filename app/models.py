from datetime import datetime
from sqlalchemy import Column, DateTime, Float, String, Text
from .db import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    document_type = Column(String, nullable=False)
    status = Column(String, nullable=False, default="UPLOADED")
    raw_text = Column(Text, nullable=True)
    extracted_json = Column(Text, nullable=True)
    validation_json = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
