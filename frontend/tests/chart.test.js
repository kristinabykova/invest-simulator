import { describe, it, expect, vi, beforeEach } from "vitest";

vi.mock("../static/state.js", () => ({
  state: {
    chart: null,
    wfFrom: null,
    wfTo: null,
  },
}));

vi.mock("../static/dom.js", () => ({
  canvas: {
    onclick: null,
  },
}));

vi.mock("../static/whatif.js", () => ({
  setCalcEnabled: vi.fn(),
}));

import {
  clearSelection,
  applySelectedPoints,
  attachChartClickHandler,
} from "../static/chart.js";

import { state } from "../static/state.js";
import { canvas } from "../static/dom.js";
import { setCalcEnabled } from "../static/whatif.js";

function createFakeChart() {
  return {
    $selA: null,
    $selB: null,
    data: {
      labels: ["2024-01-01", "2024-01-02", "2024-01-03"],
      datasets: [
        {
          pointRadius: null,
          pointHoverRadius: null,
          pointBackgroundColor: null,
          pointBorderColor: null,
          pointBorderWidth: null,
        },
      ],
    },
    update: vi.fn(),
    getElementsAtEventForMode: vi.fn(),
  };
}

describe("chart.js", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    state.chart = null;
    state.wfFrom = "2024-01-01";
    state.wfTo = "2024-01-03";
    canvas.onclick = null;
  });

  it("clearSelection clears selected dates and disables calculation", () => {
    clearSelection();

    expect(state.wfFrom).toBeNull();
    expect(state.wfTo).toBeNull();
    expect(setCalcEnabled).toHaveBeenCalledOnce();
  });

  it("clearSelection clears chart selected points if chart exists", () => {
    state.chart = createFakeChart();
    state.chart.$selA = 0;
    state.chart.$selB = 2;

    clearSelection();

    const ds = state.chart.data.datasets[0];

    expect(state.chart.$selA).toBeNull();
    expect(state.chart.$selB).toBeNull();
    expect(ds.pointRadius).toBe(0);
    expect(ds.pointHoverRadius).toBe(3);
    expect(state.chart.update).toHaveBeenCalledOnce();
  });

  it("applySelectedPoints highlights selected points", () => {
    state.chart = createFakeChart();
    state.chart.$selA = 0;
    state.chart.$selB = 2;

    applySelectedPoints();

    const ds = state.chart.data.datasets[0];

    expect(ds.pointRadius).toEqual([6, 0, 6]);
    expect(ds.pointHoverRadius).toEqual([7, 3, 7]);
    expect(ds.pointBackgroundColor).toBe("#000");
    expect(ds.pointBorderColor).toBe("#000");
    expect(ds.pointBorderWidth).toBe(0);
    expect(state.chart.update).toHaveBeenCalledOnce();
  });

  it("applySelectedPoints handles only one selected point", () => {
    state.chart = createFakeChart();
    state.chart.$selA = 1;
    state.chart.$selB = null;

    applySelectedPoints();

    const ds = state.chart.data.datasets[0];

    expect(ds.pointRadius).toEqual([0, 6, 0]);
    expect(ds.pointHoverRadius).toEqual([3, 7, 3]);
    expect(state.chart.update).toHaveBeenCalledOnce();
  });

  it("attachChartClickHandler does nothing if chart does not exist", () => {
    attachChartClickHandler();

    expect(typeof canvas.onclick).toBe("function");

    canvas.onclick({ type: "click" });

    expect(setCalcEnabled).not.toHaveBeenCalled();
  });

  it("attachChartClickHandler does nothing if no point is clicked", () => {
    state.chart = createFakeChart();
    state.chart.getElementsAtEventForMode.mockReturnValue([]);

    attachChartClickHandler();
    canvas.onclick({ type: "click" });

    expect(state.chart.$selA).toBeNull();
    expect(state.chart.$selB).toBeNull();
  });

  it("first click selects first point and clears period", () => {
    state.chart = createFakeChart();
    state.chart.getElementsAtEventForMode.mockReturnValue([{ index: 1 }]);

    attachChartClickHandler();
    canvas.onclick({ type: "click" });

    expect(state.chart.$selA).toBe(1);
    expect(state.chart.$selB).toBeNull();
    expect(state.wfFrom).toBeNull();
    expect(state.wfTo).toBeNull();
    expect(setCalcEnabled).toHaveBeenCalledOnce();
    expect(state.chart.update).toHaveBeenCalledOnce();
  });

  it("second click selects period from left to right", () => {
    state.chart = createFakeChart();
    state.chart.$selA = 2;
    state.chart.$selB = null;
    state.chart.getElementsAtEventForMode.mockReturnValue([{ index: 0 }]);

    attachChartClickHandler();
    canvas.onclick({ type: "click" });

    expect(state.chart.$selA).toBe(2);
    expect(state.chart.$selB).toBe(0);
    expect(state.wfFrom).toBe("2024-01-01");
    expect(state.wfTo).toBe("2024-01-03");
    expect(setCalcEnabled).toHaveBeenCalledOnce();
    expect(state.chart.update).toHaveBeenCalledOnce();
  });

  it("click after two selected points starts new selection", () => {
    state.chart = createFakeChart();
    state.chart.$selA = 0;
    state.chart.$selB = 2;
    state.chart.getElementsAtEventForMode.mockReturnValue([{ index: 1 }]);

    attachChartClickHandler();
    canvas.onclick({ type: "click" });

    expect(state.chart.$selA).toBe(1);
    expect(state.chart.$selB).toBeNull();
    expect(state.wfFrom).toBeNull();
    expect(state.wfTo).toBeNull();
    expect(setCalcEnabled).toHaveBeenCalledOnce();
  });
});