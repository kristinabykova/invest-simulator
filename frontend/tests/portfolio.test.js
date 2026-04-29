import { describe, it, expect, vi, beforeEach } from "vitest";

vi.mock("../static/state.js", () => ({
  state: {
    isAuthenticated: false,
    currentStock: null,
  },
}));

vi.mock("../static/dom.js", () => ({
  portfolioTickerSelect: document.createElement("select"),
  portfolioValue: document.createElement("div"),
  buyBtn: document.createElement("button"),
  sellBtn: document.createElement("button"),
  tradeSum: document.createElement("input"),
  registerOpenBtn: document.createElement("button"),
  loginOpenBtn: document.createElement("button"),
  logoutBtn: document.createElement("button"),
}));

vi.mock("../static/api.js", () => ({
  apiGetJson: vi.fn(),
  apiPostJson: vi.fn(),
}));

vi.mock("../static/utils.js", () => ({
  showToast: vi.fn(),
}));

vi.mock("../static/stocks.js", () => ({
  selectStockByTicker: vi.fn(),
}));

import {
  refreshPortfolioUI,
  buySelectedStock,
  sellSelectedStock,
  bindPortfolioSelectSync,
} from "../static/portfolio.js";

import { state } from "../static/state.js";
import {
  portfolioTickerSelect,
  portfolioValue,
  buyBtn,
  sellBtn,
  tradeSum,
  registerOpenBtn,
  loginOpenBtn,
  logoutBtn,
} from "../static/dom.js";

import { apiGetJson, apiPostJson } from "../static/api.js";
import { showToast } from "../static/utils.js";
import { selectStockByTicker } from "../static/stocks.js";

describe("portfolio.js", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    state.isAuthenticated = false;
    state.currentStock = null;

    portfolioTickerSelect.innerHTML = "";
    portfolioTickerSelect.disabled = false;
    portfolioTickerSelect.title = "";
    portfolioTickerSelect.value = "";

    portfolioValue.textContent = "";
    portfolioValue.className = "";
    portfolioValue.title = "";

    buyBtn.disabled = false;
    buyBtn.title = "";

    sellBtn.disabled = false;
    sellBtn.title = "";

    tradeSum.value = "";

    registerOpenBtn.className = "";
    loginOpenBtn.className = "";
    logoutBtn.className = "";
  });

  it("refreshPortfolioUI sets authenticated UI on successful request", async () => {
    apiGetJson.mockResolvedValue({
      cash_balance: 100000,
      positions: [
        { ticker: "SBER", qty: 2, price: 150.25 },
        { ticker: "GAZP", qty: 3, price: 180 },
      ],
    });

    await refreshPortfolioUI();

    expect(apiGetJson).toHaveBeenCalledWith("/portfolio/tickers");
    expect(state.isAuthenticated).toBe(true);

    expect(portfolioTickerSelect.disabled).toBe(false);
    expect(portfolioTickerSelect.options.length).toBe(2);
    expect(portfolioTickerSelect.options[0].value).toBe("SBER");
    expect(portfolioTickerSelect.options[0].textContent).toBe("SBER (2) 150,25 ₽");

    expect(portfolioValue.textContent).toBe(
  (100000).toLocaleString("ru-RU", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
);
    expect(portfolioValue.classList.contains("portfolioValueDisabled")).toBe(false);

    expect(buyBtn.disabled).toBe(false);
    expect(sellBtn.disabled).toBe(false);

    expect(registerOpenBtn.classList.contains("hidden")).toBe(true);
    expect(loginOpenBtn.classList.contains("hidden")).toBe(true);
    expect(logoutBtn.classList.contains("hidden")).toBe(false);
  });

  it("refreshPortfolioUI shows empty portfolio option if user has no positions", async () => {
    apiGetJson.mockResolvedValue({
      cash_balance: 5000,
      positions: [],
    });

    await refreshPortfolioUI();

    expect(state.isAuthenticated).toBe(true);
    expect(portfolioTickerSelect.innerHTML).toContain("Нет акций");
    expect(portfolioValue.textContent).toBe(
  (5000).toLocaleString("ru-RU", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
);
  });

  it("refreshPortfolioUI sets guest UI on failed request", async () => {
    apiGetJson.mockRejectedValue(new Error("Unauthorized"));

    await refreshPortfolioUI();

    expect(state.isAuthenticated).toBe(false);

    expect(portfolioTickerSelect.disabled).toBe(true);
    expect(portfolioTickerSelect.title).toBe("Войдите в аккаунт");
    expect(portfolioTickerSelect.innerHTML).toContain("—");

    expect(portfolioValue.textContent).toBe("—");
    expect(portfolioValue.classList.contains("portfolioValueDisabled")).toBe(true);

    expect(buyBtn.disabled).toBe(true);
    expect(sellBtn.disabled).toBe(true);

    expect(registerOpenBtn.classList.contains("hidden")).toBe(false);
    expect(loginOpenBtn.classList.contains("hidden")).toBe(false);
    expect(logoutBtn.classList.contains("hidden")).toBe(true);
  });

  it("buySelectedStock shows error if user is not authenticated", async () => {
    state.isAuthenticated = false;

    await buySelectedStock();

    expect(showToast).toHaveBeenCalledWith("Войдите в аккаунт", "error");
    expect(apiPostJson).not.toHaveBeenCalled();
  });

  it("buySelectedStock shows error if current stock is not selected", async () => {
    state.isAuthenticated = true;
    state.currentStock = null;

    await buySelectedStock();

    expect(showToast).toHaveBeenCalledWith("Выберите акцию слева", "error");
    expect(apiPostJson).not.toHaveBeenCalled();
  });

  it("buySelectedStock shows error if quantity is invalid", async () => {
    state.isAuthenticated = true;
    state.currentStock = { ticker: "SBER" };
    tradeSum.value = "0";

    await buySelectedStock();

    expect(showToast).toHaveBeenCalledWith(
      "Введите корректное количество лотов",
      "error"
    );
    expect(apiPostJson).not.toHaveBeenCalled();
  });

  it("buySelectedStock sends buy request and refreshes portfolio on success", async () => {
    state.isAuthenticated = true;
    state.currentStock = { ticker: "SBER" };
    tradeSum.value = "2";

    apiPostJson.mockResolvedValue({ msg: "Покупка выполнена" });
    apiGetJson.mockResolvedValue({
      cash_balance: 1000,
      positions: [{ ticker: "SBER", qty: 2, price: 150 }],
    });

    await buySelectedStock();

    expect(apiPostJson).toHaveBeenCalledWith("/portfolio/buy", {
      ticker: "SBER",
      qty: 2,
    });
    expect(showToast).toHaveBeenCalledWith("Покупка выполнена", "success");
    expect(apiGetJson).toHaveBeenCalledWith("/portfolio/tickers");
  });

  it("buySelectedStock shows backend error detail", async () => {
    state.isAuthenticated = true;
    state.currentStock = { ticker: "SBER" };
    tradeSum.value = "2";

    apiPostJson.mockRejectedValue({
      data: { detail: "Недостаточно средств" },
    });

    await buySelectedStock();

    expect(showToast).toHaveBeenCalledWith("Недостаточно средств", "error");
  });

  it("buySelectedStock shows default error if backend detail is not string", async () => {
    state.isAuthenticated = true;
    state.currentStock = { ticker: "SBER" };
    tradeSum.value = "2";

    apiPostJson.mockRejectedValue({
      data: { detail: [{ msg: "error" }] },
    });

    await buySelectedStock();

    expect(showToast).toHaveBeenCalledWith("Ошибка покупки", "error");
  });

  it("sellSelectedStock shows error if user is not authenticated", async () => {
    state.isAuthenticated = false;

    await sellSelectedStock();

    expect(showToast).toHaveBeenCalledWith("Войдите в аккаунт", "error");
    expect(apiPostJson).not.toHaveBeenCalled();
  });

  it("sellSelectedStock shows error if ticker is not selected", async () => {
    state.isAuthenticated = true;
    portfolioTickerSelect.innerHTML = `<option value="">Нет акций</option>`;
    portfolioTickerSelect.value = "";

    await sellSelectedStock();

    expect(showToast).toHaveBeenCalledWith(
      "Выберите акцию из списка портфеля",
      "error"
    );
    expect(apiPostJson).not.toHaveBeenCalled();
  });

  it("sellSelectedStock shows error if quantity is invalid", async () => {
    state.isAuthenticated = true;
    portfolioTickerSelect.innerHTML = `<option value="SBER">SBER</option>`;
    portfolioTickerSelect.value = "SBER";
    tradeSum.value = "-1";

    await sellSelectedStock();

    expect(showToast).toHaveBeenCalledWith(
      "Введите корректное количество лотов",
      "error"
    );
    expect(apiPostJson).not.toHaveBeenCalled();
  });

  it("sellSelectedStock sends sell request and refreshes portfolio on success", async () => {
    state.isAuthenticated = true;
    portfolioTickerSelect.innerHTML = `<option value="SBER">SBER</option>`;
    portfolioTickerSelect.value = "SBER";
    tradeSum.value = "2";

    apiPostJson.mockResolvedValue({ msg: "Продажа выполнена" });
    apiGetJson.mockResolvedValue({
      cash_balance: 1000,
      positions: [],
    });

    await sellSelectedStock();

    expect(apiPostJson).toHaveBeenCalledWith("/portfolio/sell", {
      ticker: "SBER",
      qty: 2,
    });
    expect(showToast).toHaveBeenCalledWith("Продажа выполнена", "success");
    expect(apiGetJson).toHaveBeenCalledWith("/portfolio/tickers");
  });

  it("sellSelectedStock shows backend error detail", async () => {
    state.isAuthenticated = true;
    portfolioTickerSelect.innerHTML = `<option value="SBER">SBER</option>`;
    portfolioTickerSelect.value = "SBER";
    tradeSum.value = "2";

    apiPostJson.mockRejectedValue({
      data: { detail: "Недостаточно акций для продажи" },
    });

    await sellSelectedStock();

    expect(showToast).toHaveBeenCalledWith(
      "Недостаточно акций для продажи",
      "error"
    );
  });

  it("sellSelectedStock shows default error if backend detail is not string", async () => {
    state.isAuthenticated = true;
    portfolioTickerSelect.innerHTML = `<option value="SBER">SBER</option>`;
    portfolioTickerSelect.value = "SBER";
    tradeSum.value = "2";

    apiPostJson.mockRejectedValue({
      data: { detail: [{ msg: "error" }] },
    });

    await sellSelectedStock();

    expect(showToast).toHaveBeenCalledWith("Ошибка продажи", "error");
  });

  it("bindPortfolioSelectSync calls selectStockByTicker on select change", () => {
    portfolioTickerSelect.innerHTML = `<option value="SBER">SBER</option>`;
    portfolioTickerSelect.value = "SBER";

    bindPortfolioSelectSync();

    portfolioTickerSelect.dispatchEvent(new Event("change"));

    expect(selectStockByTicker).toHaveBeenCalledWith("SBER");
  });

  it("bindPortfolioSelectSync does nothing if selected ticker is empty", () => {
    portfolioTickerSelect.innerHTML = `<option value="">—</option>`;
    portfolioTickerSelect.value = "";

    bindPortfolioSelectSync();

    portfolioTickerSelect.dispatchEvent(new Event("change"));

    expect(selectStockByTicker).not.toHaveBeenCalled();
  });
});