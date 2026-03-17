const API_URL = "http://127.0.0.1:8000";

let currentStock = null;
let currentDays = 3;
let chart = null;

let wfFrom = null;
let wfTo = null;

const stocksBox = document.getElementById("stocks");
const canvas = document.getElementById("priceChart");
const periodSelect = document.getElementById("periodSelect");
const wfCalcBtn = document.getElementById("wfCalcBtn");

function setCalcEnabled() {
  if (!wfCalcBtn) return;
  wfCalcBtn.disabled = !(currentStock && wfFrom && wfTo);
}

function formatRub(v) {
  if (v === null || v === undefined || !Number.isFinite(Number(v))) return "—";
  return new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "RUB",
    maximumFractionDigits: 2
  }).format(Number(v));
}

function formatXAxisLabel(iso, days) {
  const s = String(iso);
  if (days === 1) {
    const t = s.includes("T") ? s.split("T")[1] : (s.split(" ")[1] || "");
    return t ? t.slice(0, 5) : "";
  }
  const d = s.slice(0, 10);
  return `${d.slice(8, 10)}.${d.slice(5, 7)}`;
}

function renderExplanations(explanations) {
  if (!explanations) return;
  
  const explanationEl = document.getElementById("aiExplanationText");
  if (explanationEl) {
    explanationEl.textContent = explanations.explanation || "Нет объяснения";
    explanationEl.classList.remove("placeholder");
  }
  
  const tipEl = document.getElementById("aiTipText");
  if (tipEl) {
    tipEl.textContent = explanations.tip || "Нет подсказки";
    tipEl.classList.remove("placeholder");
  }
  
  const termEl = document.getElementById("aiTermText");
  if (termEl) {
    termEl.textContent = explanations.term || "Нет терминов";
    termEl.classList.remove("placeholder");
  }
}

function formatTerms(terms) {
  if (!terms || terms.length === 0) return "—";
  return terms.map(t => `<b>${t.term}</b> — ${t.definition}`).join("<br><br>");
}

function renderWhatIf(data) {
  const openEl = document.getElementById("wfOpen");
  const closeEl = document.getElementById("wfClose");
  const maxEl = document.getElementById("wfMax");
  const minEl = document.getElementById("wfMin");
  const volEl = document.getElementById("wfVol");
  const trdEl = document.getElementById("wfTrd");
  const profitEl = document.getElementById("wfPft");
  const roiEl = document.getElementById("wfRoi");
  const riskEl = document.getElementById("wfRisk");

  const fmt = (v) => (v === null || v === undefined ? "нет данных" : Number(v).toFixed(2));

  if (openEl) openEl.textContent = fmt(data.first_close);
  if (closeEl) closeEl.textContent = fmt(data.last_close);
  if (maxEl) maxEl.textContent = fmt(data.period_high);
  if (minEl) minEl.textContent = fmt(data.period_low);
  if (trdEl) trdEl.textContent = (typeof data.trend === "string" ? data.trend : "нет данных");
  if (riskEl) riskEl.textContent = (typeof data.risk === "string" ? data.risk : "нет данных");

  if (volEl) {
    if (data.volatility == null) {
      volEl.textContent = "нет данных";
      volEl.className = "";
    } else {
      const volPct = Number(data.volatility);
      let label = data.vol_label;
      if (label != null){

        volEl.textContent = volPct.toFixed(3) + " % (" + label + ")";

        volEl.className = "";
        if (label === "низкая") volEl.classList.add("vol-low");
        else if (label === "средняя") volEl.classList.add("vol-mid");
        else volEl.classList.add("vol-high");
      }
    }
  }

  if (profitEl) {
    const p = data.profit;

    if (p === null || p === undefined || !Number.isFinite(Number(p))) {
      profitEl.textContent = "—";
      profitEl.className = "";
    } else {
      const num = Number(p);
      const sign = num > 0 ? "+" : "";
      profitEl.textContent = `${sign}${formatRub(num)}`;

      profitEl.className = "";
      profitEl.classList.add(num > 0 ? "profit-plus" : (num < 0 ? "profit-minus" : "profit-zero"));
    }
  }

  if (roiEl) {
    const p = data.roi;

    if (p === null || p === undefined || !Number.isFinite(Number(p))) {
      roiEl.textContent = "—";
      roiEl.className = "";
    } else {
      const num = Number(p);
      const sign = num > 0 ? "+" : "";
      roiEl.textContent = sign + num.toFixed(2) + " %";

      roiEl.className = "";
      roiEl.classList.add(num > 0 ? "roi-plus" : (num < 0 ? "roi-minus" : "roi-zero"));
    }
  }
}

function renderAI(data) {

  const aiExplanationEl = document.getElementById("aiExplanationText");
  const aiTipEl = document.getElementById("aiTipText");
  const aiTermEl = document.getElementById("aiTermText");

  if (data.ai_text && aiExplanationEl && aiTipEl && aiTermEl) {
    aiExplanationEl.textContent = data.ai_text.explanation ?? "—";
    aiTipEl.textContent = data.ai_text.tip ?? "—";
    aiTermEl.innerHTML = formatTerms(data.ai_text.terms);
    aiExplanationEl.classList.remove("placeholder");
    aiTipEl.classList.remove("placeholder");
    aiTermEl.classList.remove("placeholder");
  } else if (aiExplanationEl && aiTipEl && aiTermEl) {
    aiExplanationEl.textContent = "Нейросеть не использовалась";
    aiTipEl.textContent = "";
    aiTermEl.textContent = "";
  }
}

async function apiGetJson(path) {
  const res = await fetch(`${API_URL}${path}`);
  if (!res.ok) throw new Error(`HTTP ${res.status} ${path}`);
  return res.json();
}

async function apiPostJson(path, body) {
  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status} ${path}`);
  return res.json();
}

function clearSelection() {
  wfFrom = null;
  wfTo = null;
  setCalcEnabled();

  if (chart) {
    chart.$selA = null;
    chart.$selB = null;
    const ds = chart.data.datasets[0];
    ds.pointRadius = 0;
    ds.pointHoverRadius = 3;
    chart.update();
  }
}

function applySelectedPoints() {
  const ds = chart.data.datasets[0];
  const n = chart.data.labels.length;
  const radii = new Array(n).fill(0);

  if (chart.$selA !== null) radii[chart.$selA] = 6;
  if (chart.$selB !== null) radii[chart.$selB] = 6;

  ds.pointRadius = radii;
  ds.pointHoverRadius = radii.map(r => (r > 0 ? 7 : 3));
  ds.pointBackgroundColor = "#000";
  ds.pointBorderColor = "#000";
  ds.pointBorderWidth = 0;

  chart.update();
}

function attachChartClickHandler() {
  if (!canvas) return;

  canvas.onclick = (evt) => {
    if (!chart) return;

    const points = chart.getElementsAtEventForMode(
      evt,
      "nearest",
      { intersect: false },
      true
    );
    if (!points || points.length === 0) return;

    const idx = points[0].index;

    // 1-я точка -> 2-я точка -> сброс -> 1-я...
    if (chart.$selA === null || (chart.$selA !== null && chart.$selB !== null)) {
      chart.$selA = idx;
      chart.$selB = null;
      applySelectedPoints();
      wfFrom = null;
      wfTo = null;
      setCalcEnabled();
      return;
    }

    chart.$selB = idx;
    applySelectedPoints();

    const left = Math.min(chart.$selA, chart.$selB);
    const right = Math.max(chart.$selA, chart.$selB);

    wfFrom = String(chart.data.labels[left]);
    wfTo = String(chart.data.labels[right]);
    setCalcEnabled();
  };
}

function renderStocksList(stocks) {
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

async function loadChart(stock) {
  currentStock = stock;
  clearSelection();
  loadLotSize(stock.ticker);

  const data = await apiGetJson(`/stocks/${encodeURIComponent(stock.ticker)}/history?days=${currentDays}`);

  const labels = data.map(d => d.date);
  const prices = data.map(d => Number(d.close));

  if (chart) chart.destroy();

  if (!canvas) {
    console.error("Не найден canvas #priceChart. Проверь index.html");
    return;
  }

  chart = new Chart(canvas, {
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
            callback: (value) => formatXAxisLabel(labels[value], currentDays)
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

  chart.$selA = null;
  chart.$selB = null;

  attachChartClickHandler();
}

async function init() {
  try {
    const stocks = await apiGetJson("/stocks/");
    renderStocksList(stocks);
  } catch (err) {
    console.error("Ошибка загрузки акций:", err);
  }

  if (periodSelect) {
    periodSelect.addEventListener("change", () => {
      currentDays = Number(periodSelect.value);
      if (currentStock) loadChart(currentStock);
    });
  }

  if (wfCalcBtn) {
    wfCalcBtn.addEventListener("click", async () => {
      if (!currentStock || !wfFrom || !wfTo) return;

      try {
        const data = await apiPostJson("/whatif/analyze", {
          ticker: currentStock.ticker,
          from_: wfFrom,
          to: wfTo,
          interval: 10,
          lots_count: Number(document.getElementById("whatIfLot").value)
        });
        renderWhatIf(data)
        if (data.ai_text.explanation) {
          renderAI(data);
        }
        else {
          document.getElementById("aiHeader").style.display = "none"
          document.getElementById("aiWarning").style.display = "block"
          renderExplanations(data.explanations)
        }
      } catch (e) {
        console.error("Ошибка what-if:", e);
      }
    });
    setCalcEnabled();
  }
}

async function loadLotSize(ticker) {
  try {
    const res = await fetch(`${API_URL}/stocks/${encodeURIComponent(ticker)}/lotsize`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    const el = document.getElementById("lotInfo").textContent = data.lotsize;
    if (el) {
      el.textContent = `Размер лота: ${data.lotsize}`;
    }
  } catch (e) {
    const el = document.getElementById("lotInfo");
    if (el) el.textContent = "нет данных"; 
    console.error("Ошибка загрузки lot size:", e);
  }
}

init();