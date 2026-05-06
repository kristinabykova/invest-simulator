import { describe, it, expect, vi, beforeEach } from "vitest";

vi.mock("../static/state.js", () => ({
  state: {
    currentStock: null,
    wfFrom: null,
    wfTo: null,
  },
}));

vi.mock("../static/dom.js", () => ({
  wfCalcBtn: document.createElement("button"),
}));

vi.mock("../static/utils.js", () => ({
  formatRub: vi.fn((value) => `${Number(value).toFixed(2)} ₽`),
}));

import {
  setCalcEnabled,
  renderExplanations,
  formatTerms,
  renderWhatIf,
  renderAI,
} from "../static/whatif.js";

import { state } from "../static/state.js";
import { wfCalcBtn } from "../static/dom.js";

describe("whatif.js", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    state.currentStock = null;
    state.wfFrom = null;
    state.wfTo = null;
    wfCalcBtn.disabled = false;

    document.body.innerHTML = `
      <div id="aiExplanationText" class="placeholder"></div>
      <div id="aiTipText" class="placeholder"></div>
      <div id="aiTermText" class="placeholder"></div>

      <div id="wfOpen"></div>
      <div id="wfClose"></div>
      <div id="wfMax"></div>
      <div id="wfMin"></div>
      <div id="wfVol"></div>
      <div id="wfTrd"></div>
      <div id="wfPft"></div>
      <div id="wfRoi"></div>
      <div id="wfRisk"></div>
    `;
  });

  it("setCalcEnabled disables button if data is missing", () => {
    state.currentStock = { ticker: "SBER" };
    state.wfFrom = "2024-01-01";
    state.wfTo = null;

    setCalcEnabled();

    expect(wfCalcBtn.disabled).toBe(true);
  });

  it("setCalcEnabled enables button if stock and dates are selected", () => {
    state.currentStock = { ticker: "SBER" };
    state.wfFrom = "2024-01-01";
    state.wfTo = "2024-01-31";

    setCalcEnabled();

    expect(wfCalcBtn.disabled).toBe(false);
  });

  it("renderExplanations fills explanation blocks", () => {
  document.body.innerHTML = `
    <div id="aiExplanationText" class="placeholder"></div>
    <div id="aiTipText" class="placeholder"></div>
    <div id="aiTermText" class="placeholder"></div>
  `;

  renderExplanations({
    explanation: "Объяснение",
    tip: "Совет",
    terms: [
      {
        term: "Термин",
        definition: "Определение",
      },
    ],
  });

  expect(document.getElementById("aiExplanationText").textContent).toBe("Объяснение");
  expect(document.getElementById("aiTipText").textContent).toBe("Совет");
  expect(document.getElementById("aiTermText").textContent).toBe("Термин — Определение");

  expect(document.getElementById("aiExplanationText").classList.contains("placeholder")).toBe(false);
  expect(document.getElementById("aiTipText").classList.contains("placeholder")).toBe(false);
  expect(document.getElementById("aiTermText").classList.contains("placeholder")).toBe(false);
});

  it("renderExplanations uses fallback text", () => {
    renderExplanations({});

    expect(document.getElementById("aiExplanationText").textContent).toBe("Нет объяснения");
    expect(document.getElementById("aiTipText").textContent).toBe("Нет подсказки");
    expect(document.getElementById("aiTermText").textContent).toBe("—");
  });

  it("renderExplanations does nothing if explanations are missing", () => {
    renderExplanations(null);

    expect(document.getElementById("aiExplanationText").textContent).toBe("");
  });

  it("formatTerms returns dash for empty terms", () => {
    expect(formatTerms(null)).toBe("—");
    expect(formatTerms([])).toBe("—");
  });

  it("formatTerms formats terms as HTML", () => {
    const result = formatTerms([
      { term: "ROI", definition: "Доходность" },
      { term: "Риск", definition: "Вероятность потерь" },
    ]);

    expect(result).toBe(
      "<b>ROI</b> — Доходность<br><br><b>Риск</b> — Вероятность потерь"
    );
  });

  it("renderWhatIf renders numeric metrics", () => {
    renderWhatIf({
      first_close: 100,
      last_close: 120,
      period_high: 130,
      period_low: 90,
      volatility: 1.23456,
      vol_label: "средняя",
      trend: "восходящий тренд",
      profit: 500,
      roi: 20,
      risk: "умеренный риск",
    });

    expect(document.getElementById("wfOpen").textContent).toBe("100.00");
    expect(document.getElementById("wfClose").textContent).toBe("120.00");
    expect(document.getElementById("wfMax").textContent).toBe("130.00");
    expect(document.getElementById("wfMin").textContent).toBe("90.00");
    expect(document.getElementById("wfTrd").textContent).toBe("восходящий тренд");
    expect(document.getElementById("wfRisk").textContent).toBe("умеренный риск");

    expect(document.getElementById("wfVol").textContent).toBe("1.235 % (средняя)");
    expect(document.getElementById("wfVol").classList.contains("vol-mid")).toBe(true);

    expect(document.getElementById("wfPft").textContent).toBe("+500.00 ₽");
    expect(document.getElementById("wfPft").classList.contains("profit-plus")).toBe(true);

    expect(document.getElementById("wfRoi").textContent).toBe("+20.00 %");
    expect(document.getElementById("wfRoi").classList.contains("roi-plus")).toBe(true);
  });

  it("renderWhatIf renders fallback values for missing data", () => {
    renderWhatIf({
      first_close: null,
      last_close: undefined,
      period_high: null,
      period_low: undefined,
      volatility: null,
      trend: null,
      profit: null,
      roi: undefined,
      risk: null,
    });

    expect(document.getElementById("wfOpen").textContent).toBe("нет данных");
    expect(document.getElementById("wfClose").textContent).toBe("нет данных");
    expect(document.getElementById("wfMax").textContent).toBe("нет данных");
    expect(document.getElementById("wfMin").textContent).toBe("нет данных");
    expect(document.getElementById("wfTrd").textContent).toBe("нет данных");
    expect(document.getElementById("wfRisk").textContent).toBe("нет данных");
    expect(document.getElementById("wfVol").textContent).toBe("нет данных");
    expect(document.getElementById("wfPft").textContent).toBe("—");
    expect(document.getElementById("wfRoi").textContent).toBe("—");
  });

  it("renderWhatIf applies negative and zero classes", () => {
    renderWhatIf({
      first_close: 100,
      last_close: 100,
      period_high: 100,
      period_low: 100,
      volatility: 2,
      vol_label: "высокая",
      trend: "боковой тренд",
      profit: -50,
      roi: 0,
      risk: "высокий риск",
    });

    expect(document.getElementById("wfVol").classList.contains("vol-high")).toBe(true);
    expect(document.getElementById("wfPft").classList.contains("profit-minus")).toBe(true);
    expect(document.getElementById("wfRoi").classList.contains("roi-zero")).toBe(true);
  });

  it("renderWhatIf applies low volatility class", () => {
    renderWhatIf({
      first_close: 100,
      last_close: 100,
      period_high: 100,
      period_low: 100,
      volatility: 0.1,
      vol_label: "низкая",
      trend: "боковой тренд",
      profit: 0,
      roi: -5,
      risk: "низкий риск",
    });

    expect(document.getElementById("wfVol").classList.contains("vol-low")).toBe(true);
    expect(document.getElementById("wfPft").classList.contains("profit-zero")).toBe(true);
    expect(document.getElementById("wfRoi").classList.contains("roi-minus")).toBe(true);
  });

  it("renderAI renders AI data", () => {
    renderAI({
      explanation: "AI объяснение",
      tip: "AI совет",
      terms: [{ term: "ROI", definition: "Доходность" }],
    });

    expect(document.getElementById("aiExplanationText").textContent).toBe("AI объяснение");
    expect(document.getElementById("aiTipText").textContent).toBe("AI совет");
    expect(document.getElementById("aiTermText").innerHTML).toBe(
      "<b>ROI</b> — Доходность"
    );
    expect(document.getElementById("aiExplanationText").classList.contains("placeholder")).toBe(false);
  });

  it("renderAI uses fallback when AI data is missing", () => {
    renderAI(null);

    expect(document.getElementById("aiExplanationText").textContent).toBe(
      "Нейросеть не использовалась"
    );
    expect(document.getElementById("aiTipText").textContent).toBe("");
    expect(document.getElementById("aiTermText").textContent).toBe("");
  });

  it("renderAI uses dashes for missing fields", () => {
    renderAI({});

    expect(document.getElementById("aiExplanationText").textContent).toBe("—");
    expect(document.getElementById("aiTipText").textContent).toBe("—");
    expect(document.getElementById("aiTermText").innerHTML).toBe("—");
  });
});