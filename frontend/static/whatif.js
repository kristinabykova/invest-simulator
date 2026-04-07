import { state } from "./state.js";
import { wfCalcBtn } from "./dom.js";
import { formatRub } from "./utils.js";

export function setCalcEnabled() {
  if (!wfCalcBtn) return;
  wfCalcBtn.disabled = !(state.currentStock && state.wfFrom && state.wfTo);
}

export function renderExplanations(explanations) {
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

export function formatTerms(terms) {
  if (!terms || terms.length === 0) return "—";
  return terms.map(t => `<b>${t.term}</b> — ${t.definition}`).join("<br><br>");
}

export function renderWhatIf(data) {
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

export function renderAI(data) {
  const aiExplanationEl = document.getElementById("aiExplanationText");
  const aiTipEl = document.getElementById("aiTipText");
  const aiTermEl = document.getElementById("aiTermText");

  if (data && aiExplanationEl && aiTipEl && aiTermEl) {
    aiExplanationEl.textContent = data.explanation ?? "—";
    aiTipEl.textContent = data.tip ?? "—";
    aiTermEl.innerHTML = formatTerms(data.terms);
    aiExplanationEl.classList.remove("placeholder");
    aiTipEl.classList.remove("placeholder");
    aiTermEl.classList.remove("placeholder");
  } else if (aiExplanationEl && aiTipEl && aiTermEl) {
    aiExplanationEl.textContent = "Нейросеть не использовалась";
    aiTipEl.textContent = "";
    aiTermEl.textContent = "";
  }
}