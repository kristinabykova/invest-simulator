import { state } from "./state.js";
import { canvas } from "./dom.js";
import { setCalcEnabled } from "./whatif.js";

export function clearSelection() {
  state.wfFrom = null;
  state.wfTo = null;
  setCalcEnabled();

  if (state.chart) {
    state.chart.$selA = null;
    state.chart.$selB = null;
    const ds = state.chart.data.datasets[0];
    ds.pointRadius = 0;
    ds.pointHoverRadius = 3;
    state.chart.update();
  }
}

export function applySelectedPoints() {
  const ds = state.chart.data.datasets[0];
  const n = state.chart.data.labels.length;
  const radii = new Array(n).fill(0);

  if (state.chart.$selA !== null) radii[state.chart.$selA] = 6;
  if (state.chart.$selB !== null) radii[state.chart.$selB] = 6;

  ds.pointRadius = radii;
  ds.pointHoverRadius = radii.map(r => (r > 0 ? 7 : 3));
  ds.pointBackgroundColor = "#000";
  ds.pointBorderColor = "#000";
  ds.pointBorderWidth = 0;

  state.chart.update();
}

export function attachChartClickHandler() {
  if (!canvas) return;

  canvas.onclick = (evt) => {
    if (!state.chart) return;

    const points = state.chart.getElementsAtEventForMode(
      evt,
      "nearest",
      { intersect: false },
      true
    );
    if (!points || points.length === 0) return;

    const idx = points[0].index;

    if (state.chart.$selA === null || (state.chart.$selA !== null && state.chart.$selB !== null)) {
      state.chart.$selA = idx;
      state.chart.$selB = null;
      applySelectedPoints();
      state.wfFrom = null;
      state.wfTo = null;
      setCalcEnabled();
      return;
    }

    state.chart.$selB = idx;
    applySelectedPoints();

    const left = Math.min(state.chart.$selA, state.chart.$selB);
    const right = Math.max(state.chart.$selA, state.chart.$selB);

    state.wfFrom = String(state.chart.data.labels[left]);
    state.wfTo = String(state.chart.data.labels[right]);
    setCalcEnabled();
  };
}