import base64
import json
import os

from openai import OpenAI

_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            base_url=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            api_key=os.environ.get("OPENAI_API_KEY", "not-needed"),
        )
    return _client


def _chat_model() -> str:
    return os.environ.get("LLM_MODEL", "gpt-4o-mini")


def _vision_model() -> str:
    return os.environ.get("LLM_VISION_MODEL", _chat_model())


EXTRACT_PROMPT = (
    "以下の文章から、職務経験・スキル・資格として読み取れる項目を"
    "箇条書きの短いフレーズのリストとして抽出してください。"
    '出力はJSON配列のみ（例: ["Pythonでのデータ分析経験", "AWS Solutions Architect Associate"]）。'
    "余計な説明は付けないでください。"
)


def extract_skills_from_text(text: str) -> list[str]:
    resp = get_client().chat.completions.create(
        model=_chat_model(),
        messages=[
            {"role": "system", "content": EXTRACT_PROMPT},
            {"role": "user", "content": text},
        ],
    )
    return _parse_json_array(resp.choices[0].message.content or "[]")


def extract_skills_from_image(image_path: str) -> list[str]:
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    ext = image_path.rsplit(".", 1)[-1].lower()
    mime = "image/png" if ext == "png" else "image/jpeg"
    resp = get_client().chat.completions.create(
        model=_vision_model(),
        messages=[
            {"role": "system", "content": EXTRACT_PROMPT},
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


def _parse_json_array(raw: str) -> list[str]:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:]
    try:
        data = json.loads(raw)
        return [str(item) for item in data] if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def summarize_current_skills(all_mentions: list[str]) -> str:
    if not all_mentions:
        return "まだ証拠が登録されていません。"
    resp = get_client().chat.completions.create(
        model=_chat_model(),
        messages=[
            {
                "role": "system",
                "content": (
                    "以下はある人物のスキル・経験に関する記述の断片です。"
                    "重複や表記ゆれをまとめ、カテゴリ別のMarkdown箇条書きとして"
                    "現在のスキル像を整理してください。"
                ),
            },
            {"role": "user", "content": "\n".join(f"- {m}" for m in all_mentions)},
        ],
    )
    return resp.choices[0].message.content or ""


def generate_resume(evidence_summaries: list[str]) -> str:
    resp = get_client().chat.completions.create(
        model=_chat_model(),
        messages=[
            {
                "role": "system",
                "content": (
                    "以下は蓄積された職務経歴・スキル・資格の断片情報です。"
                    "これらを統合し、職務経歴書として読める形式のMarkdown文書を作成してください。"
                    "職務要約、経験・スキル、資格の各セクションを含めてください。"
                ),
            },
            {"role": "user", "content": "\n".join(f"- {s}" for s in evidence_summaries)},
        ],
    )
    return resp.choices[0].message.content or ""
