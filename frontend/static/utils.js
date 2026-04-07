import { toastEl } from "./dom.js";

export function showToast(message, type = "success") {
  if (!toastEl) return;

  toastEl.textContent = message;
  toastEl.className = `toast show ${type}`;

  setTimeout(() => {
    toastEl.className = "toast";
  }, 2500);
}

export function openModal(modal) {
  if (modal) modal.classList.remove("hidden");
}

export function closeModal(modal) {
  if (modal) modal.classList.add("hidden");
}

export function formatRub(v) {
  if (v === null || v === undefined || !Number.isFinite(Number(v))) return "—";
  return new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "RUB",
    maximumFractionDigits: 2
  }).format(Number(v));
}

export function formatXAxisLabel(iso, days) {
  const s = String(iso);
  if (days === 1) {
    const t = s.includes("T") ? s.split("T")[1] : (s.split(" ")[1] || "");
    return t ? t.slice(0, 5) : "";
  }
  const d = s.slice(0, 10);
  return `${d.slice(8, 10)}.${d.slice(5, 7)}`;
}