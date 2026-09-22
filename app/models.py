import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class EvidenceEntry(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    source_type: str  # "resume" | "certification" | "checkin"
    raw_input: str
    file_path: Optional[str] = None
    llm_extracted: Optional[str] = None  # JSON-encoded list[str] of skill/experience mentions
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ExportSnapshot(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    content: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
