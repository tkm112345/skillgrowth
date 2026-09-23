import uuid
from datetime import date, datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class EvidenceEntry(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    # "certification" | "checkin" | "education" | "employment" | "project" | "learning_activity"
    source_type: str
    raw_input: str
    file_path: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Skill(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str
    category: str = "未分類"
    first_observed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_observed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    include_in_resume: bool = True


class SkillLink(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    evidence_id: str = Field(foreign_key="evidenceentry.id")
    skill_id: str = Field(foreign_key="skill.id")
    mention_text: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ExportSnapshot(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    content: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    edited_at: Optional[datetime] = None


class Settings(SQLModel, table=True):
    id: int = Field(default=1, primary_key=True)
    openai_base_url: str = "https://api.openai.com/v1"
    openai_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    llm_vision_model: str = "gpt-4o-mini"
    skill_extraction_enabled: bool = False


class CareerGoal(SQLModel, table=True):
    horizon: str = Field(primary_key=True)  # "this_year" | "5_years" | "10_years"
    description: str = ""
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CareerVision(SQLModel, table=True):
    id: int = Field(default=1, primary_key=True)  # singleton row, id=1
    content: str = ""
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CareerGoalHistory(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    horizon: str
    description: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ReflectionLog(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    note: str = ""


class Education(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    school: str
    degree: str = ""
    major: str = ""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    achievements: str = ""
    evidence_id: Optional[str] = Field(default=None, foreign_key="evidenceentry.id")


class Employment(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    company: str
    department: str = ""
    role: str = ""
    start_date: Optional[date] = None
    end_date: Optional[date] = None  # null = 現職
    evidence_id: Optional[str] = Field(default=None, foreign_key="evidenceentry.id")


class Project(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    employment_id: Optional[str] = Field(default=None, foreign_key="employment.id")
    title: str
    role: str = ""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: str = ""
    evidence_id: Optional[str] = Field(default=None, foreign_key="evidenceentry.id")


class ExternalLink(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    label: str  # e.g. "GitHub", "X", "note", "Zenn", "Blog" — free text, not a fixed enum
    url: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LearningActivity(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    # "reading" | "talk_given" | "talk_attended" | "certification" | "other"
    activity_type: str
    title: str
    activity_date: Optional[date] = None
    notes: str = ""
    evidence_id: Optional[str] = Field(default=None, foreign_key="evidenceentry.id")


class SelfPR(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_selected: bool = False


class ConsultSession(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ConsultMessage(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    session_id: str = Field(foreign_key="consultsession.id")
    role: str  # "user" | "assistant"
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SampleDataRecord(SQLModel, table=True):
    """Tracks exactly which rows a `load-sample` call created, so
    `reset-sample` can remove precisely those rows (and only those) even if
    load-sample has been run more than once or the user has since added
    their own real data alongside it."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    table_name: str
    record_id: str  # the row's real id, or a CareerGoal horizon
