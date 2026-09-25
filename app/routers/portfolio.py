import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlmodel import Session, select

from app.db import PORTFOLIO_DIR, get_session
from app.models import PortfolioFile, PortfolioItem, PortfolioLink, Project

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB per file

# Matches what the page's own subtitle promises ("links, PDFs, spreadsheets,
# photos"). Downloads already force Content-Disposition: attachment (see
# download_portfolio_file below), so this isn't an XSS control — it's here
# so an upload can't silently accept something (an executable, a script)
# that was never part of what this feature is for.
ALLOWED_EXTENSIONS = {".pdf", ".xlsx", ".xls", ".csv", ".ods", ".jpg", ".jpeg", ".png", ".gif", ".webp"}


class PortfolioItemIn(BaseModel):
    title: str | None = None
    description: str | None = None
    project_id: str | None = None


class PortfolioLinkIn(BaseModel):
    label: str
    url: str


class PortfolioItemDetail(BaseModel):
    item: PortfolioItem
    links: list[PortfolioLink]
    files: list[PortfolioFile]


def _validate_project_id(session: Session, project_id: str | None) -> None:
    if project_id is None:
        return
    project = session.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=400, detail="Project not found")
    if project.employment_id is not None:
        raise HTTPException(
            status_code=400,
            detail="Only standalone projects (not tied to an employer) can be linked to a portfolio item",
        )


@router.get("")
def list_portfolio_items(session: Session = Depends(get_session)) -> list[PortfolioItem]:
    return session.exec(select(PortfolioItem).order_by(PortfolioItem.created_at.desc())).all()


@router.get("/{item_id}")
def get_portfolio_item(item_id: str, session: Session = Depends(get_session)) -> PortfolioItemDetail:
    item = session.get(PortfolioItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Portfolio item not found")
    links = session.exec(
        select(PortfolioLink).where(PortfolioLink.portfolio_item_id == item_id).order_by(PortfolioLink.created_at)
    ).all()
    files = session.exec(
        select(PortfolioFile).where(PortfolioFile.portfolio_item_id == item_id).order_by(PortfolioFile.uploaded_at)
    ).all()
    return PortfolioItemDetail(item=item, links=links, files=files)


@router.post("")
def create_portfolio_item(payload: PortfolioItemIn, session: Session = Depends(get_session)) -> PortfolioItem:
    if not (payload.title or "").strip():
        raise HTTPException(status_code=400, detail="Title is required")
    _validate_project_id(session, payload.project_id)

    item = PortfolioItem(
        title=payload.title.strip(),
        description=payload.description or "",
        project_id=payload.project_id,
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.put("/{item_id}")
def update_portfolio_item(
    item_id: str, payload: PortfolioItemIn, session: Session = Depends(get_session)
) -> PortfolioItem:
    item = session.get(PortfolioItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Portfolio item not found")

    if payload.title is not None:
        if not payload.title.strip():
            raise HTTPException(status_code=400, detail="Title is required")
        item.title = payload.title.strip()
    if payload.description is not None:
        item.description = payload.description
    if "project_id" in payload.model_fields_set:
        _validate_project_id(session, payload.project_id)
        item.project_id = payload.project_id

    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.delete("/{item_id}")
def delete_portfolio_item(item_id: str, session: Session = Depends(get_session)):
    item = session.get(PortfolioItem, item_id)
    if item:
        for link in session.exec(select(PortfolioLink).where(PortfolioLink.portfolio_item_id == item_id)).all():
            session.delete(link)
        for f in session.exec(select(PortfolioFile).where(PortfolioFile.portfolio_item_id == item_id)).all():
            Path(f.file_path).unlink(missing_ok=True)
            session.delete(f)
        session.delete(item)
        session.commit()
    return {"ok": True}


@router.post("/{item_id}/links")
def add_portfolio_link(
    item_id: str, payload: PortfolioLinkIn, session: Session = Depends(get_session)
) -> PortfolioLink:
    item = session.get(PortfolioItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Portfolio item not found")
    link = PortfolioLink(portfolio_item_id=item_id, label=payload.label, url=payload.url)
    session.add(link)
    session.commit()
    session.refresh(link)
    return link


@router.delete("/links/{link_id}")
def delete_portfolio_link(link_id: str, session: Session = Depends(get_session)):
    link = session.get(PortfolioLink, link_id)
    if link:
        session.delete(link)
        session.commit()
    return {"ok": True}


@router.post("/{item_id}/files")
def upload_portfolio_files(
    item_id: str,
    files: list[UploadFile] = File(...),
    session: Session = Depends(get_session),
) -> list[PortfolioFile]:
    item = session.get(PortfolioItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Portfolio item not found")

    # Validate every file before writing anything, so a batch is all-or-nothing.
    contents: list[tuple[UploadFile, bytes]] = []
    for f in files:
        suffix = Path(f.filename or "").suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"{f.filename}: unsupported file type")
        data = f.file.read()
        if len(data) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(status_code=400, detail=f"{f.filename}: file exceeds 10MB limit")
        contents.append((f, data))

    created: list[PortfolioFile] = []
    for f, data in contents:
        suffix = Path(f.filename or "").suffix
        dest = PORTFOLIO_DIR / f"{uuid.uuid4()}{suffix}"
        dest.write_bytes(data)
        row = PortfolioFile(
            portfolio_item_id=item_id,
            original_filename=f.filename or dest.name,
            file_path=str(dest),
            content_type=f.content_type or "",
            size_bytes=len(data),
        )
        session.add(row)
        created.append(row)

    session.commit()
    for row in created:
        session.refresh(row)
    return created


@router.get("/files/{file_id}/download")
def download_portfolio_file(file_id: str, session: Session = Depends(get_session)) -> FileResponse:
    row = session.get(PortfolioFile, file_id)
    if row is None or not Path(row.file_path).exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        row.file_path,
        media_type=row.content_type or "application/octet-stream",
        filename=row.original_filename,
    )


@router.delete("/files/{file_id}")
def delete_portfolio_file(file_id: str, session: Session = Depends(get_session)):
    row = session.get(PortfolioFile, file_id)
    if row:
        Path(row.file_path).unlink(missing_ok=True)
        session.delete(row)
        session.commit()
    return {"ok": True}
