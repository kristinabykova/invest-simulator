import { state } from "./state.js";
import { stocksBox, canvas } from "./dom.js";
import { apiGetJson } from "./api.js";
import { clearSelection, attachChartClickHandler } from "./chart.js";
import { formatXAxisLabel } from "./utils.js";
import { loadLotSize } from "./lots.js";

export function renderStocksList(stocks) {
  if (!stocksBox) {
    console.error("Не найден контейнер #stocks. Проверь index.html");
    return;
  }

  stocksBox.innerHTML = "";

  stocks.forEach((stock, idx) => {
    const row = document.createElement("div");
    row.className = "stockItem";
    row.dataset.ticker = stock.ticker;

    const name = document.createElement("div");
    name.className = "stockName";
    name.innerText = stock.name;

    const ticker = document.createElement("div");
    ticker.className = "stockTicker";
    ticker.innerText = stock.ticker;

    row.appendChild(name);
    row.appendChild(ticker);

    row.onclick = () => {
      document.querySelectorAll(".stockItem").forEach(el => el.classList.remove("active"));
      row.classList.add("active");
      loadChart(stock);
    };

    stocksBox.appendChild(row);

    if (idx === 0) {
      row.classList.add("active");
      loadChart(stock);
    }
  });
}

export async function loadChart(stock) {
  state.currentStock = stock;
  clearSelection();
  loadLotSize(stock.ticker);

  await refreshCurrentPrices(stock.ticker);

  const data = await apiGetJson(`/stocks/${encodeURIComponent(stock.ticker)}/history?days=${state.currentDays}`);

  const labels = data.map(d => d.date);
  const prices = data.map(d => Number(d.close));

  if (state.chart) state.chart.destroy();

  if (!canvas) {
    console.error("Не найден canvas #priceChart. Проверь index.html");
    return;
  }

  state.chart = new Chart(canvas, {
    type: "line",
    data: {
      labels,
      datasets: [{
        label: stock.ticker,
        data: prices,
        borderWidth: 1,
        borderColor: "#111",
        backgroundColor: "transparent",
        pointRadius: 0,
        pointHoverRadius: 3,
        tension: 0.25
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: { enabled: true }
      },
      scales: {
        x: {
          ticks: {
            autoSkip: true,
            maxTicksLimit: 6,
            maxRotation: 0,
            callback: (value) => formatXAxisLabel(labels[value], state.currentDays)
          },
          grid: { drawBorder: false }
        },
        y: {
          position: "right",
          ticks: {
            padding: 8,
            callback: (value) => Number(value).toFixed(1),
          },
          grid: { drawBorder: false }
        }
      }
    }
  });

  state.chart.$selA = null;
  state.chart.$selB = null;

  attachChartClickHandler();
}

export async function refreshCurrentPrices(ticker) {
  const buyPriceEl = document.getElementById("buyPrice");
  const sellPriceEl = document.getElementById("sellPrice");

  if (!buyPriceEl || !sellPriceEl) return;

  if (!ticker) {
    buyPriceEl.textContent = "Покупка: — ₽";
    sellPriceEl.textContent = "Продажа: — ₽";
    return;
  }

  try {
    const data = await apiGetJson(`/stocks/${ticker}/current`);

    const offer = Number(data.offer);
    const bid = Number(data.bid);

    buyPriceEl.textContent = `Покупка: ${Number.isFinite(offer) ? offer.toFixed(2) : "—"} ₽`;
    sellPriceEl.textContent = `Продажа: ${Number.isFinite(bid) ? bid.toFixed(2) : "—"} ₽`;
  } catch (e) {
    buyPriceEl.textContent = "Покупка: — ₽";
    sellPriceEl.textContent = "Продажа: — ₽";
  }
}

