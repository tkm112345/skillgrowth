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
__EXISTING_SKILLS__
"""


CONSULT_SYSTEM_PROMPT = """あなたは経験豊富なキャリアコンサルタントです。
相談者本人が実際にこのアプリに記録してきたキャリアデータ（職歴・学歴・プロジェクト・
スキル・自己PR・ビジョン・キャリア目標）が以下に与えられます。

このデータを踏まえて、一般論ではなく相談者本人の状況に即した具体的なアドバイスを
してください。データからは分からないことを一般論で埋めず、必要なら質問してください。

返答は__LOCALE__で行ってください。
__CUSTOM_INSTRUCTIONS__
--- 相談者のキャリアデータ ---
__CONTEXT__
--- ここまで ---
"""


class LLMRequestError(RuntimeError):
    """Raised when a request to the configured LLM endpoint fails, so
    callers get a clear, catchable error instead of a raw SDK exception."""


def _client(settings: Settings) -> OpenAI:
    return OpenAI(base_url=settings.openai_base_url, api_key=settings.openai_api_key or "not-needed")


def _complete(settings: Settings, **kwargs):
    try:
        return _client(settings).chat.completions.create(**kwargs)
    except Exception as e:
        raise LLMRequestError(str(e)) from e


def test_connection(settings: Settings) -> dict:
    try:
        resp = _client(settings).chat.completions.create(
            model=settings.llm_model,
            messages=[{"role": "user", "content": "Reply with the single word: ok"}],
            max_tokens=5,
        )
        reply = (resp.choices[0].message.content or "").strip()
        return {"ok": True, "message": reply}
    except Exception as e:  # noqa: BLE001 - surface any failure reason to the UI
        return {"ok": False, "message": str(e)}


def _existing_skills_block(existing_skills: list[dict]) -> str:
    if not existing_skills:
        return "(まだ登録されているスキルはありません)"
    return "\n".join(f"- {s['id']}: {s['name']}" for s in existing_skills)


def _strip_code_fence(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:]
    return raw


def _parse_json_array(raw: str) -> list[dict]:
    try:
        data = json.loads(_strip_code_fence(raw))
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def _parse_json_object(raw: str) -> dict:
    try:
        data = json.loads(_strip_code_fence(raw))
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def extract_and_match_text(text: str, existing_skills: list[dict], settings: Settings) -> list[dict]:
    system_prompt = MATCH_PROMPT.replace("__EXISTING_SKILLS__", _existing_skills_block(existing_skills))
    resp = _complete(
        settings,
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

    system_prompt = MATCH_PROMPT.replace("__EXISTING_SKILLS__", _existing_skills_block(existing_skills))
    resp = _complete(
        settings,
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
    resp = _complete(
        settings,
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
    data = _parse_json_object(resp.choices[0].message.content or "{}")
    return {
        "matched": data.get("matched", []),
        "missing": data.get("missing", []),
        "summary": data.get("summary", ""),
    }


def career_consult_reply(messages: list[dict], context: str, locale: str, settings: Settings) -> str:
    locale_name = "日本語" if locale == "ja" else "English"
    custom = settings.consult_custom_instructions.strip()
    custom_block = f"\n追加の指示:\n{custom}\n" if custom else ""
    system_prompt = (
        CONSULT_SYSTEM_PROMPT.replace("__CUSTOM_INSTRUCTIONS__", custom_block)
        .replace("__CONTEXT__", context)
        .replace("__LOCALE__", locale_name)
    )
    resp = _complete(
        settings,
        model=settings.llm_model,
        messages=[{"role": "system", "content": system_prompt}, *messages],
    )
    return resp.choices[0].message.content or ""


def goal_growth_guidance(goals: list[dict], current_skills: list[dict], settings: Settings) -> dict:
    skills_block = "\n".join(f"- {s['name']}（{s['category']}）" for s in current_skills) or "(なし)"
    goals_block = "\n".join(f"- {g['horizon_label']}: {g['description']}" for g in goals)

    resp = _complete(
        settings,
        model=settings.llm_model,
        messages=[
            {
                "role": "system",
                "content": (
                    "あなたはキャリアアドバイザーです。ユーザーの現在のスキル一覧と、"
                    "期間ごとのキャリア目標が与えられます。現在のスキルから見て、"
                    "各目標に近づくために伸ばすべきスキルや取るべき行動を、"
                    "目標ごとに具体的に提案してください。\n\n"
                    "出力は次の形式のJSONオブジェクトのみ。入力された目標と同じ数・同じ順序の"
                    "要素を含めること。\n"
                    '{"by_horizon": [{"horizon": "目標の見出し", "advice": "具体的な提案(2〜4文)"}]}\n\n'
                    f"現在のスキル一覧:\n{skills_block}"
                ),
            },
            {"role": "user", "content": goals_block},
        ],
    )
    data = _parse_json_object(resp.choices[0].message.content or "{}")
    return {"by_horizon": data.get("by_horizon", [])}
