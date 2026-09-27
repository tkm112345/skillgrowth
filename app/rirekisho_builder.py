from datetime import date

from sqlmodel import Session, select

from app.models import Education, Employment, PersonalInfo
from app.resume_builder import gather_resume_context


def _age(birthdate: date | None) -> int | None:
    if birthdate is None:
        return None
    today = date.today()
    years = today.year - birthdate.year
    if (today.month, today.day) < (birthdate.month, birthdate.day):
        years -= 1
    return years


def _history_rows(session: Session) -> list[dict]:
    """A single chronological 学歴・職歴 table, alternating 入学/卒業 and
    入社/退社 lines the way a Japanese rirekisho conventionally lists them,
    built from the same Education/Employment rows the resume uses — not
    gather_resume_context's version of them, since that pre-formats dates
    into period strings rather than the separate year/month/label rows a
    rirekisho table needs."""
    rows: list[dict] = []
    for edu in session.exec(select(Education)).all():
        if edu.start_date:
            rows.append({"date": edu.start_date, "label": f"{edu.school} 入学"})
        if edu.end_date:
            rows.append({"date": edu.end_date, "label": f"{edu.school} 卒業"})
    for emp in session.exec(select(Employment)).all():
        if emp.start_date:
            rows.append({"date": emp.start_date, "label": f"{emp.company} 入社"})
        if emp.end_date:
            rows.append({"date": emp.end_date, "label": f"{emp.company} 退社"})
    rows.sort(key=lambda r: r["date"])
    history = [{"year": str(r["date"].year), "month": str(r["date"].month), "label": r["label"]} for r in rows]
    if history:
        history.append({"year": "", "month": "", "label": "現在に至る"})
    return history


def gather_rirekisho_context(session: Session) -> dict:
    """Collect rirekisho data — no LLM call. Reuses gather_resume_context's
    self_pr and certifications rather than re-querying them, so the two
    documents never drift on what those sections contain."""
    resume_ctx = gather_resume_context(session)
    personal = session.get(PersonalInfo, 1) or PersonalInfo()

    return {
        "name": personal.name,
        "name_kana": personal.name_kana,
        "birthdate": personal.birthdate.isoformat() if personal.birthdate else "",
        "age": _age(personal.birthdate),
        "postal_code": personal.postal_code,
        "address": personal.address,
        "address_kana": personal.address_kana,
        "phone": personal.phone,
        "email": personal.email,
        "photo_path": personal.photo_path,
        "history": _history_rows(session),
        "certifications": resume_ctx["certifications"],
        "self_pr": resume_ctx["self_pr"],
    }
