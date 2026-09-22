import base64
import json

from openai import OpenAI

from app.models import Settings

MATCH_PROMPT = """あなたはキャリア・スキルの抽出アシスタントです。
入力された文章から、職務経験・スキル・資格として読み取れる項目を抽出してください。

既存のスキル一覧（id: 名前）が与えられます。抽出した項目が既存スキルと
同一とみなせる場合はその skill_id を使い、新規の項目であれば skill_id は null にして
name（正規化した短い名称）と category（技術/資格/マネジメント/ドメイン知識 など緩い分類）を
指定してください。

出力は次の形式のJSON配列のみ。説明文は付けないこと。
[
  {"mention_text": "文中の実際の記述", "skill_id": "既存IDまたはnull", "name": "正規化名（skill_idがnullの場合必須）", "category": "分類"}
]

既存スキル一覧:
{existing_skills}
"""


def _client(settings: Settings) -> OpenAI:
    return OpenAI(base_url=settings.openai_base_url, api_key=settings.openai_api_key or "not-needed")


def _existing_skills_block(existing_skills: list[dict]) -> str:
    if not existing_skills:
        return "(まだ登録されているスキルはありません)"
    return "\n".join(f"- {s['id']}: {s['name']}" for s in existing_skills)


def _parse_json_array(raw: str) -> list[dict]:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:]
    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def extract_and_match_text(text: str, existing_skills: list[dict], settings: Settings) -> list[dict]:
    system_prompt = MATCH_PROMPT.format(existing_skills=_existing_skills_block(existing_skills))
    resp = _client(settings).chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
    )
    return _parse_json_array(resp.choices[0].message.content or "[]")


def extract_and_match_image(image_path: str, existing_skills: list[dict], settings: Settings) -> list[dict]:
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    ext = image_path.rsplit(".", 1)[-1].lower()
    mime = "image/png" if ext == "png" else "image/jpeg"

    system_prompt = MATCH_PROMPT.format(existing_skills=_existing_skills_block(existing_skills))
    resp = _client(settings).chat.completions.create(
        model=settings.llm_vision_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "この資格証・修了証の画像から情報を抽出してください。"},
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                ],
            },
        ],
    )
    return _parse_json_array(resp.choices[0].message.content or "[]")


def gap_check(job_description: str, current_skills: list[dict], settings: Settings) -> dict:
    skills_block = "\n".join(f"- {s['name']}（{s['category']}）" for s in current_skills) or "(なし)"
    resp = _client(settings).chat.completions.create(
        model=settings.llm_model,
        messages=[
            {
                "role": "system",
                "content": (
                    "あなたはキャリアアドバイザーです。ユーザーの現在のスキル一覧と、"
                    "求人票の文章が与えられます。求人票が求めるスキル・要件のうち、"
                    "ユーザーが既に満たしているものと、不足しているものを判定してください。\n\n"
                    "出力は次の形式のJSONオブジェクトのみ。\n"
                    '{"matched": ["求人票が求め、ユーザーも持っている項目"], '
                    '"missing": ["求人票が求めるが、ユーザーには見当たらない項目"], '
                    '"summary": "全体的な適合度についての2〜3文の所感"}\n\n'
                    f"現在のスキル一覧:\n{skills_block}"
                ),
            },
            {"role": "user", "content": job_description},
        ],
    )
    raw = (resp.choices[0].message.content or "{}").strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:]
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {}
    return {
        "matched": data.get("matched", []),
        "missing": data.get("missing", []),
        "summary": data.get("summary", ""),
    }


def generate_resume(skill_summaries: list[str], settings: Settings) -> str:
    resp = _client(settings).chat.completions.create(
        model=settings.llm_model,
        messages=[
            {
                "role": "system",
                "content": (
                    "以下は蓄積されたスキル・経験・資格の一覧です。"
                    "これらを統合し、職務経歴書として読める形式のMarkdown文書を作成してください。"
                    "職務要約、経験・スキル、資格の各セクションを含めてください。"
                ),
            },
            {"role": "user", "content": "\n".join(f"- {s}" for s in skill_summaries)},
        ],
    )
    return resp.choices[0].message.content or ""
