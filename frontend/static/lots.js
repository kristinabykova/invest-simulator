import { API_URL } from "./config.js";

export async function loadLotSize(ticker) {
  try {
    const res = await fetch(`${API_URL}/stocks/${encodeURIComponent(ticker)}/lotsize`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    const el = document.getElementById("lotInfo");
    if (el) {
      el.textContent = `${data.lotsize}`;
    }

  } catch (e) {
    const el = document.getElementById("lotInfo");
    if (el) el.textContent = "нет данных"; 
    console.error("Ошибка загрузки lot size:", e);
  }
}