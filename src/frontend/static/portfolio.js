import { apiGetJson, apiPostJson } from "./api.js";
import { state } from "./state.js";
import {
  portfolioTickerSelect,
  portfolioValue,
  buyBtn,
  sellBtn,
  tradeSum,
  registerOpenBtn,
  loginOpenBtn,
  logoutBtn,
} from "./dom.js";
import { showToast } from "./utils.js";
import { selectStockByTicker } from "./stocks.js";

let portfolioTickerOrder = [];

function formatPortfolioValue(value) {
  const num = Number(value);
  if (!Number.isFinite(num)) return "—";
  return num.toLocaleString("ru-RU", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

function setGuestUI() {
  state.isAuthenticated = false;
  portfolioTickerOrder = [];

  if (portfolioTickerSelect) {
    portfolioTickerSelect.innerHTML = `<option value="">—</option>`;
    portfolioTickerSelect.disabled = true;
    portfolioTickerSelect.title = "Войдите в аккаунт";
  }

  if (portfolioValue) {
    portfolioValue.textContent = "—";
    portfolioValue.classList.add("portfolioValueDisabled");
    portfolioValue.title = "Войдите в аккаунт";
  }

  if (buyBtn) {
    buyBtn.disabled = true;
    buyBtn.title = "Войдите в аккаунт";
  }

  if (sellBtn) {
    sellBtn.disabled = true;
    sellBtn.title = "Войдите в аккаунт";
  }

  if (registerOpenBtn) registerOpenBtn.classList.remove("hidden");
  if (loginOpenBtn) loginOpenBtn.classList.remove("hidden");
  if (logoutBtn) logoutBtn.classList.add("hidden");
}

function setAuthUI(data) {
  state.isAuthenticated = true;

  if (portfolioTickerSelect) {
    const positions = Array.isArray(data.positions) ? data.positions : [];
    const selectedTicker = portfolioTickerSelect.value;

    const qtyMap = new Map(
      positions.map((p) => [p.ticker, p.qty])
    );

    if (portfolioTickerOrder.length === 0) {
      portfolioTickerOrder = positions.map((p) => p.ticker);
    } else {
      for (const p of positions) {
        if (!portfolioTickerOrder.includes(p.ticker)) {
          portfolioTickerOrder.push(p.ticker);
        }
      }
    }

    portfolioTickerSelect.innerHTML = "";

    const visibleTickers = portfolioTickerOrder.filter((ticker) =>
      qtyMap.has(ticker)
    );

    if (visibleTickers.length === 0) {
      portfolioTickerSelect.innerHTML = `<option value="">Нет акций</option>`;
    } else {
      visibleTickers.forEach((ticker) => {
        const option = document.createElement("option");
        option.value = ticker;
        option.textContent = `${ticker} (${qtyMap.get(ticker)})`;
        portfolioTickerSelect.appendChild(option);
      });

      const hasSelectedTicker = visibleTickers.includes(selectedTicker);
      portfolioTickerSelect.value = hasSelectedTicker
        ? selectedTicker
        : visibleTickers[0];
    }

    portfolioTickerSelect.disabled = false;
    portfolioTickerSelect.title = "";
  }

  if (portfolioValue) {
    portfolioValue.textContent = formatPortfolioValue(data.cash_balance);
    portfolioValue.classList.remove("portfolioValueDisabled");
    portfolioValue.title = "";
  }

  if (buyBtn) {
    buyBtn.disabled = false;
    buyBtn.title = "";
  }

  if (sellBtn) {
    sellBtn.disabled = false;
    sellBtn.title = "";
  }

  if (registerOpenBtn) registerOpenBtn.classList.add("hidden");
  if (loginOpenBtn) loginOpenBtn.classList.add("hidden");
  if (logoutBtn) logoutBtn.classList.remove("hidden");
}

export async function refreshPortfolioUI() {
  try {
    const data = await apiGetJson("/portfolio/tickers");
    setAuthUI(data);
  } catch (e) {
    setGuestUI();
  }
}

function getQtyFromInput() {
  const qty = Number(tradeSum?.value);
  if (!Number.isInteger(qty) || qty <= 0) {
    showToast("Введите корректное количество лотов", "error");
    return null;
  }
  return qty;
}

export async function buySelectedStock() {
  if (!state.isAuthenticated) {
    showToast("Войдите в аккаунт", "error");
    return;
  }

  if (!state.currentStock?.ticker) {
    showToast("Выберите акцию слева", "error");
    return;
  }

  const qty = getQtyFromInput();
  if (qty === null) return;

  try {
    const data = await apiPostJson("/portfolio/buy", {
      ticker: state.currentStock.ticker,
      qty,
    });

    showToast(data.msg || "Покупка выполнена", "success");
    await refreshPortfolioUI();
  } catch (e) {
    const detail = e.data?.detail;
    showToast(typeof detail === "string" ? detail : "Ошибка покупки", "error");
  }
}

export async function sellSelectedStock() {
  if (!state.isAuthenticated) {
    showToast("Войдите в аккаунт", "error");
    return;
  }

  const ticker = portfolioTickerSelect?.value;
  if (!ticker) {
    showToast("Выберите акцию из списка портфеля", "error");
    return;
  }

  const qty = getQtyFromInput();
  if (qty === null) return;

  try {
    const data = await apiPostJson("/portfolio/sell", {
      ticker,
      qty,
    });

    showToast(data.msg || "Продажа выполнена", "success");
    await refreshPortfolioUI();
  } catch (e) {
    const detail = e.data?.detail;
    showToast(typeof detail === "string" ? detail : "Ошибка продажи", "error");
  }
}

export function bindPortfolioSelectSync() {
  if (!portfolioTickerSelect) return;

  portfolioTickerSelect.addEventListener("change", () => {
    const ticker = portfolioTickerSelect.value;
    if (!ticker) return;

    selectStockByTicker(ticker);
  });
}