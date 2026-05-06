import pytest

from src.services import explanation


def test_normalize_risk_allowed():
    assert explanation.normalize_risk("низкий риск") == "низкий риск"
    assert explanation.normalize_risk("умеренный риск") == "умеренный риск"
    assert explanation.normalize_risk("высокий риск") == "высокий риск"


def test_normalize_risk_unknown_returns_moderate():
    assert explanation.normalize_risk(None) == "умеренный риск"
    assert explanation.normalize_risk("неизвестный риск") == "умеренный риск"


@pytest.mark.parametrize(
    "roi, risk, expected",
    [
        (10, "низкий риск", "высокий доход и низкий риск"),
        (5, "высокий риск", "высокий доход и высокий риск"),
        (2, "умеренный риск", "низкий доход и умеренный риск"),
        (0, "низкий риск", "низкий доход и низкий риск"),
        (-1, "высокий риск", "убыток и высокий риск"),
        (3, None, "низкий доход и умеренный риск"),
    ],
)
def test_get_roi_risk_label(roi, risk, expected):
    assert explanation.get_roi_risk_label(roi, risk) == expected


@pytest.mark.parametrize(
    "volatility, expected",
    [
        (None, None),
        (1.5, "высокая волатильность"),
        (2.0, "высокая волатильность"),
        (0.5, "низкая волатильность"),
        (0.3, "низкая волатильность"),
        (1.0, None),
    ],
)
def test_get_volatility_label(volatility, expected):
    assert explanation.get_volatility_label(volatility) == expected


def test_get_main_tip_priority_roi_risk_first():
    tip = explanation.get_main_tip(
        roi_risk_label="убыток и высокий риск",
        volatility_label="высокая волатильность",
        trend="восходящий тренд",
    )

    assert tip == explanation.TIPS["убыток и высокий риск"]


def test_get_main_tip_uses_volatility_if_no_roi_risk():
    tip = explanation.get_main_tip(
        roi_risk_label=None,
        volatility_label="высокая волатильность",
        trend="восходящий тренд",
    )

    assert tip == explanation.TIPS["высокая волатильность"]


def test_get_main_tip_uses_trend_if_no_other_labels():
    tip = explanation.get_main_tip(
        roi_risk_label=None,
        volatility_label=None,
        trend="восходящий тренд",
    )

    assert tip == explanation.TIPS["восходящий тренд"]


def test_get_main_tip_fallback():
    tip = explanation.get_main_tip(
        roi_risk_label=None,
        volatility_label=None,
        trend=None,
    )

    assert "Недостаточно данных" in tip


def test_build_terms_returns_unique_terms():
    terms = explanation.build_terms(
        trend="восходящий тренд",
        volatility_label="высокая волатильность",
        roi=10,
        risk="низкий риск",
    )

    term_names = [item["term"] for item in terms]

    assert term_names == [
        "Восходящий тренд",
        "Волатильность",
        "Доходность",
        "Риск",
    ]


def test_build_terms_without_optional_values():
    terms = explanation.build_terms(
        trend=None,
        volatility_label=None,
        roi=None,
        risk=None,
    )

    assert terms == []


def test_all_explanations_full_result():
    result = {
        "trend": "восходящий тренд",
        "volatility": 2.0,
        "roi": 12,
        "risk": "высокий риск",
    }

    data = explanation.all_explanations(result)

    assert "Что произошло с ценой:" in data["explanation"]
    assert "Оценка входа:" in data["explanation"]
    assert "Дополнительно:" in data["explanation"]

    assert data["tip"] == explanation.TIPS["высокий доход и высокий риск"]

    term_names = [item["term"] for item in data["term"]]

    assert "Восходящий тренд" in term_names
    assert "Волатильность" in term_names
    assert "Доходность" in term_names
    assert "Риск" in term_names


def test_all_explanations_without_high_volatility():
    result = {
        "trend": "боковой тренд",
        "volatility": 1.0,
        "roi": 2,
        "risk": "умеренный риск",
    }

    data = explanation.all_explanations(result)

    assert "Что произошло с ценой:" in data["explanation"]
    assert "Оценка входа:" in data["explanation"]
    assert "Дополнительно:" not in data["explanation"]

    assert data["tip"] == explanation.TIPS["низкий доход и умеренный риск"]

    term_names = [item["term"] for item in data["term"]]

    assert "Боковой тренд" in term_names
    assert "Волатильность" not in term_names
    assert "Доходность" in term_names
    assert "Риск" in term_names


def test_all_explanations_only_trend():
    result = {
        "trend": "нисходящий тренд",
        "volatility": None,
        "roi": None,
        "risk": None,
    }

    data = explanation.all_explanations(result)

    assert "Что произошло с ценой:" in data["explanation"]
    assert "Оценка входа:" not in data["explanation"]
    assert "Дополнительно:" not in data["explanation"]

    assert data["tip"] == explanation.TIPS["нисходящий тренд"]

    term_names = [item["term"] for item in data["term"]]

    assert term_names == ["Нисходящий тренд"]


def test_all_explanations_only_high_volatility():
    result = {
        "trend": None,
        "volatility": 2.0,
        "roi": None,
        "risk": None,
    }

    data = explanation.all_explanations(result)

    assert "Дополнительно:" in data["explanation"]
    assert data["tip"] == explanation.TIPS["высокая волатильность"]

    term_names = [item["term"] for item in data["term"]]

    assert term_names == ["Волатильность"]


def test_all_explanations_fallback_when_no_data():
    result = {}

    data = explanation.all_explanations(result)

    assert data["explanation"] == "Недостаточно данных для объяснения результата."
    assert "Недостаточно данных" in data["tip"]
    assert data["term"] == []


def test_all_explanations_unknown_values():
    result = {
        "trend": "неизвестный тренд",
        "volatility": 1.0,
        "roi": None,
        "risk": "неизвестный риск",
    }

    data = explanation.all_explanations(result)

    assert data["explanation"] == "Недостаточно данных для объяснения результата."
    assert "Недостаточно данных" in data["tip"]

    term_names = [item["term"] for item in data["term"]]
    assert term_names == ["Риск"]
