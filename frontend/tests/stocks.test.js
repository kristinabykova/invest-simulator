import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

vi.mock("../static/state.js", () => ({
  state: {
    currentStock: null,
    currentDays: 30,
    chart: null,
  },
}));

vi.mock("../static/dom.js", () => ({
  stocksBox: document.createElement("div"),
  canvas: document.createElement("canvas"),
  portfolioTickerSelect: document.createElement("select"),
}));

vi.mock("../static/api.js", () => ({
  apiGetJson: vi.fn(),
}));

vi.mock("../static/chart.js", () => ({
  clearSelection: vi.fn(),
  attachChartClickHandler: vi.fn(),
}));

vi.mock("../static/utils.js", () => ({
  formatXAxisLabel: vi.fn((date) => `formatted-${date}`),
}));

vi.mock("../static/lots.js", () => ({
  loadLotSize: vi.fn(),
}));

import {
  renderStocksList,
  selectStockByTicker,
  loadChart,
  refreshCurrentPrices,
} from "../static/stocks.js";

import { state } from "../static/state.js";
import {
  stocksBox,
  canvas,
  portfolioTickerSelect,
} from "../static/dom.js";
import { apiGetJson } from "../static/api.js";
import {
  clearSelection,
  attachChartClickHandler,
} from "../static/chart.js";
import { loadLotSize } from "../static/lots.js";

function mockApiResponses() {
  apiGetJson.mockImplementation((url) => {
    if (url.includes("/current")) {
      return Promise.resolve({
        offer: 150.25,
        bid: 149.75,
      });
    }

    if (url.includes("/history")) {
      return Promise.resolve([
        { date: "2024-01-01", close: 100 },
        { date: "2024-01-02", close: 110 },
      ]);
    }

    return Promise.resolve({});
  });
}

describe("stocks.js", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    document.body.innerHTML = `
      <div id="buyPrice"></div>
      <div id="sellPrice"></div>
    `;

    stocksBox.innerHTML = "";

    document.body.appendChild(stocksBox);

    portfolioTickerSelect.innerHTML = `
      <option value="SBER">SBER</option>
      <option value="GAZP">GAZP</option>
    `;
    portfolioTickerSelect.value = "SBER";

    state.currentStock = null;
    state.currentDays = 30;
    state.chart = null;

    global.Chart = vi.fn(function (canvasArg, config) {
  this.canvasArg = canvasArg;
  this.config = config;
  this.data = config.data;
  this.options = config.options;
  this.destroy = vi.fn();
  this.update = vi.fn();
  this.$selA = "old";
  this.$selB = "old";
});

    mockApiResponses();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    delete global.Chart;
  });

  it("renderStocksList renders stocks and selects first stock by default", async () => {
    const stocks = [
      { ticker: "SBER", name: "Сбербанк" },
      { ticker: "GAZP", name: "Газпром" },
    ];

    renderStocksList(stocks);

    const rows = stocksBox.querySelectorAll(".stockItem");

    expect(rows.length).toBe(2);
    expect(rows[0].dataset.ticker).toBe("SBER");
    expect(rows[0].classList.contains("active")).toBe(true);
    expect(rows[1].classList.contains("active")).toBe(false);

    await vi.waitFor(() => {
      expect(global.Chart).toHaveBeenCalled();
    });

    expect(state.currentStock).toEqual({
      ticker: "SBER",
      name: "Сбербанк",
    });
  });

  it("click on stock row makes it active and loads chart", async () => {
    const stocks = [
      { ticker: "SBER", name: "Сбербанк" },
      { ticker: "GAZP", name: "Газпром" },
    ];

    renderStocksList(stocks);

    await vi.waitFor(() => {
      expect(global.Chart).toHaveBeenCalled();
    });

    vi.clearAllMocks();
    mockApiResponses();

    const rows = stocksBox.querySelectorAll(".stockItem");

    rows[1].click();

    expect(rows[0].classList.contains("active")).toBe(false);
    expect(rows[1].classList.contains("active")).toBe(true);

    await vi.waitFor(() => {
      expect(state.currentStock).toEqual({
        ticker: "GAZP",
        name: "Газпром",
      });
    });
  });

  it("selectStockByTicker selects row and loads chart", async () => {
    const stocks = [
      { ticker: "SBER", name: "Сбербанк" },
      { ticker: "GAZP", name: "Газпром" },
    ];

    renderStocksList(stocks);

    await vi.waitFor(() => {
      expect(global.Chart).toHaveBeenCalled();
    });

    vi.clearAllMocks();
    mockApiResponses();

    selectStockByTicker("GAZP");

    const sberRow = stocksBox.querySelector('[data-ticker="SBER"]');
    const gazpRow = stocksBox.querySelector('[data-ticker="GAZP"]');

    expect(sberRow.classList.contains("active")).toBe(false);
    expect(gazpRow.classList.contains("active")).toBe(true);

    await vi.waitFor(() => {
      expect(state.currentStock.ticker).toBe("GAZP");
    });
  });

  it("selectStockByTicker does nothing if ticker is empty or missing", () => {
    selectStockByTicker("");

    expect(state.currentStock).toBeNull();

    selectStockByTicker("UNKNOWN");

    expect(state.currentStock).toBeNull();
  });

  it("loadChart loads current prices, history and creates chart", async () => {
    await loadChart({
      ticker: "SBER",
      name: "Сбербанк",
    });

    expect(state.currentStock).toEqual({
      ticker: "SBER",
      name: "Сбербанк",
    });

    expect(clearSelection).toHaveBeenCalledOnce();
    expect(loadLotSize).toHaveBeenCalledWith("SBER");

    expect(apiGetJson).toHaveBeenCalledWith("/stocks/SBER/current");
    expect(apiGetJson).toHaveBeenCalledWith("/stocks/SBER/history?days=30");

    expect(portfolioTickerSelect.value).toBe("SBER");

    expect(global.Chart).toHaveBeenCalledWith(
      canvas,
      expect.objectContaining({
        type: "line",
      })
    );

    expect(state.chart.data.labels).toEqual(["2024-01-01", "2024-01-02"]);
    expect(state.chart.data.datasets[0].data).toEqual([100, 110]);
    expect(state.chart.data.datasets[0].label).toBe("SBER");

    expect(state.chart.$selA).toBeNull();
    expect(state.chart.$selB).toBeNull();

    expect(attachChartClickHandler).toHaveBeenCalledOnce();
  });

  it("loadChart destroys previous chart before creating a new one", async () => {
    const destroy = vi.fn();

    state.chart = {
      destroy,
    };

    await loadChart({
      ticker: "SBER",
      name: "Сбербанк",
    });

    expect(destroy).toHaveBeenCalledOnce();
    expect(global.Chart).toHaveBeenCalled();
  });

  it("loadChart encodes ticker in history URL", async () => {
    await loadChart({
      ticker: "SBER TEST",
      name: "Test",
    });

    expect(apiGetJson).toHaveBeenCalledWith(
      "/stocks/SBER%20TEST/history?days=30"
    );
  });

  it("refreshCurrentPrices writes buy and sell prices to DOM", async () => {
    apiGetJson.mockResolvedValue({
      offer: 150.25,
      bid: 149.75,
    });

    await refreshCurrentPrices("SBER");

    expect(apiGetJson).toHaveBeenCalledWith("/stocks/SBER/current");
    expect(document.getElementById("buyPrice").textContent).toBe(
      "Покупка: 150.25 ₽"
    );
    expect(document.getElementById("sellPrice").textContent).toBe(
      "Продажа: 149.75 ₽"
    );
  });

  it("refreshCurrentPrices shows fallback if ticker is empty", async () => {
    await refreshCurrentPrices("");

    expect(document.getElementById("buyPrice").textContent).toBe("Покупка: — ₽");
    expect(document.getElementById("sellPrice").textContent).toBe(
      "Продажа: — ₽"
    );
    expect(apiGetJson).not.toHaveBeenCalled();
  });

  it("refreshCurrentPrices shows fallback for invalid prices", async () => {
    apiGetJson.mockResolvedValue({
      offer: "abc",
      bid: undefined,
    });

    await refreshCurrentPrices("SBER");

    expect(document.getElementById("buyPrice").textContent).toBe("Покупка: — ₽");
    expect(document.getElementById("sellPrice").textContent).toBe(
      "Продажа: — ₽"
    );
  });

  it("refreshCurrentPrices shows fallback on request error", async () => {
    apiGetJson.mockRejectedValue(new Error("Network error"));

    await refreshCurrentPrices("SBER");

    expect(document.getElementById("buyPrice").textContent).toBe("Покупка: — ₽");
    expect(document.getElementById("sellPrice").textContent).toBe(
      "Продажа: — ₽"
    );
  });

  it("refreshCurrentPrices does nothing if price elements are missing", async () => {
    document.body.innerHTML = "";

    await expect(refreshCurrentPrices("SBER")).resolves.toBeUndefined();

    expect(apiGetJson).not.toHaveBeenCalled();
  });
});