from src.services import stocks


def test_is_supported_ticker_returns_true_for_existing_ticker():
    assert stocks.is_supported_ticker("SBER") is True


def test_is_supported_ticker_is_case_insensitive():
    assert stocks.is_supported_ticker("sber") is True


def test_is_supported_ticker_strips_spaces():
    assert stocks.is_supported_ticker("  SBER  ") is True


def test_is_supported_ticker_returns_false_for_unknown_ticker():
    assert stocks.is_supported_ticker("UNKNOWN") is False


def test_list_of_stocks_returns_stocks_list():
    result = stocks.list_of_stocks()

    assert result == stocks.STOCKS
    assert isinstance(result, list)
    assert len(result) > 0


def test_all_stocks_have_ticker_and_name():
    for stock in stocks.list_of_stocks():
        assert "ticker" in stock
        assert "name" in stock
        assert stock["ticker"]
        assert stock["name"]
