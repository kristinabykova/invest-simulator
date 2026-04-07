from src.schemas.whatif import WhatIfRequest
import json
from src.schemas.insights import MetricsIn, InsightsResponse
from openai import AsyncOpenAI
import os

NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
NVIDIA_MODEL = "meta/llama3-70b-instruct"

SYSTEM_PROMPT = """
Ты помощник для обучающего симулятора инвестиций.
Пиши кратко, понятно новичку, без финансовых советов и обещаний прибыли.
Никаких призывов "покупай/продавай" как рекомендаций — только учебные объяснения.
Всегда отвечай СТРОГО JSON-объектом по схеме:
"explanation": "1–3 предложения, почему могла быть такая динамика",
  "tip": "1 предложение — учебная подсказка без советов купить/продать",
  "terms": [
    {"term": "Термин 1", "definition": "1–2 предложения"},
    {"term": "Термин 2", "definition": "1–2 предложения"}
  ],
  "tone": "нейтрально-обучающий"

Требования:
- explanation: 10–350 символов
- tip: 5–180 символов
- terms: 1–2 элемента
- term: до 40 символов
- definition: до 200 символов
"""


def get_openai_client():
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        return None
    return AsyncOpenAI(base_url=NVIDIA_BASE_URL, api_key=api_key)


def build_metrics_for_llm(result: dict, req: WhatIfRequest) -> MetricsIn:

    roi = result["roi"] * 100
    vol = result.get("volatility")

    return MetricsIn(
        ticker=req.ticker,
        first_close=float(result["first_close"]),
        last_close=float(result["last_close"]),
        period_high=float(result["period_high"]),
        period_low=float(result["period_low"]),
        profit=float(result["profit"]),
        roi=float(roi),
        volatility_pct=float(vol) if vol is not None else 0.0,
        volatility_label=result.get("vol_label") or "неизвестно",
        trend=result.get("trend") or "неизвестно",
        risk=result.get("risk") or "неизвестно",
        lots=int(req.lots_count),
    )


def build_user_prompt(m: MetricsIn) -> str:
    return f"""
Данные анализа периода по акции {m.ticker}:

- Цена открытия: {m.first_close}
- Цена закрытия: {m.last_close}
- Максимум: {m.period_high}
- Минимум: {m.period_low}
- Прибыль (для {m.lots} лотов): {m.profit} RUB
- Доходность: {m.roi} %
- Волатильность: {m.volatility_pct} % ({m.volatility_label})
- Тренд: {m.trend}
- Риск: {m.risk}

Сгенерируй:
1) explanation: 1–3 предложения, почему могла быть такая динамика (простыми словами).
2) tip: 1 короткая учебная подсказка (без “делай сделку”).
3) terms: 1–2 термина, релевантные ситуации (не общие “акция/биржа”).
Верни строго JSON.

- Никаких переносов строк внутри строк JSON
- Используй только двойные кавычки
- Не добавляй текст вне JSON
"""


async def generate_insights(metrics: MetricsIn) -> InsightsResponse:
    client = get_openai_client()
    if client is None:
        return InsightsResponse(
            explanation="Генерация нейросетью недоступна.",
            tip="Проверь настройку API-ключа.",
            terms=[],
            tone="нейтрально-обучающий",
        )

    resp = await client.chat.completions.create(
        model=NVIDIA_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(metrics)},
        ],
        temperature=0.4,
        top_p=0.9,
        max_tokens=400,
        extra_body={"chat_template_kwargs": {"thinking": False}},
    )

    content = (resp.choices[0].message.content or "").strip()

    if not content.startswith("{"):
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1 and end > start:
            content = content[start : end + 1]

    data = json.loads(content)

    return InsightsResponse.model_validate(data)


def test():
    return {
        "explanation": "все хорошо",
        "tip": "Обращай внимание на волатильность и ширину торгового диапазона, чтобы оценивать активность рынка.",
        "terms": [
            {
                "term": "Боковой тренд",
                "definition": "Ситуация на рынке, когда цена актива колеблется в горизонтальном диапазоне без явного роста или падения.",
            },
            {
                "term": "Волатильность",
                "definition": "Статистический показатель, который характеризует степень изменчивости цены актива за определенный период.",
            },
        ],
        "tone": "нейтрально-обучающий",
    }
