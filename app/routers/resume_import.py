from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlmodel import Session

from app import llm
from app.db import get_session
from app.models import Settings

router = APIRouter(prefix="/api/resume-import", tags=["resume_import"])

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB, matches evidence/portfolio upload limits


def _document_text(document) -> str:
    # python-docx's `document.paragraphs` only walks body-level paragraphs —
    # it silently skips any paragraph inside a table. A 職務経歴書's
    # period-by-period work history is commonly laid out as a table (seen
    # firsthand on a real resume while building this feature: two tables,
    # 13 and 4 rows, holding almost the entire project history — reading
    # `.paragraphs` alone would have dropped nearly all of it). Walk the
    # body's child elements directly so tables are read in their original
    # position relative to the surrounding paragraphs, not just paragraphs.
    lines = []
    for child in document.element.body.iterchildren():
        if child.tag == qn("w:p"):
            text = Paragraph(child, document).text
            if text.strip():
                lines.append(text)
        elif child.tag == qn("w:tbl"):
            for row in Table(child, document).rows:
                cells = [c.text.strip() for c in row.cells]
                if any(cells):
                    lines.append("\t".join(cells))
    return "\n".join(lines)


@router.post("/extract")
def extract_resume(file: UploadFile = File(...), session: Session = Depends(get_session)) -> dict:
    """Stateless draft extraction: reads the uploaded .docx, asks the LLM
    to structure it, and returns the draft as-is. Nothing is written to
    the DB and the file is never saved to disk — the caller (the
    resume-import UI) is responsible for reviewing the draft and creating
    rows through the existing profile/skills/learning/self-pr endpoints."""
    data = file.file.read()
    if len(data) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail=f"{file.filename}: file exceeds 10MB limit")

    ext = Path(file.filename or "").suffix.lower()
    if ext != ".docx":
        raise HTTPException(status_code=400, detail="Only .docx files are supported")

    file.file.seek(0)
    document = Document(file.file)
    text = _document_text(document)
    if not text.strip():
        raise HTTPException(status_code=400, detail="No text content found in the uploaded file")

    settings = session.get(Settings, 1)
    return llm.extract_resume(text, settings)
