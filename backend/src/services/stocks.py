STOCKS = [
    {"ticker": "SBER", "name": "Сбербанк"},
    {"ticker": "GAZP", "name": "Газпром"},
    {"ticker": "LKOH", "name": "Лукойл"},
    {"ticker": "ROSN", "name": "Роснефть"},
    {"ticker": "NVTK", "name": "Новатэк"},
    {"ticker": "GMKN", "name": "Норникель"},
    {"ticker": "MTSS", "name": "МТС"},
    {"ticker": "ALRS", "name": "Алроса"},
    {"ticker": "MAGN", "name": "ММК"},
    {"ticker": "NLMK", "name": "НЛМК"},
    {"ticker": "TATN", "name": "Татнефть"},
    {"ticker": "VTBR", "name": "ВТБ"},
    {"ticker": "AFLT", "name": "Аэрофлот"},
    {"ticker": "VKCO", "name": "ВК"},
    {"ticker": "OZON", "name": "Ozon Holdings"},
]

_SUPPORTED_TICKERS = frozenset(s["ticker"] for s in STOCKS)


def is_supported_ticker(ticker: str):
    return ticker.upper().strip() in _SUPPORTED_TICKERS


def list_of_stocks():
    return STOCKS
