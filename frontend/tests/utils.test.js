import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

vi.mock("../static/dom.js", () => ({
  toastEl: document.createElement("div"),
}));

import {
  showToast,
  openModal,
  closeModal,
  formatRub,
  formatXAxisLabel,
} from "../static/utils.js";

import { toastEl } from "../static/dom.js";

describe("utils.js", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    toastEl.textContent = "";
    toastEl.className = "";
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.clearAllMocks();
  });

  it("showToast displays message and type", () => {
    showToast("Успешно", "success");

    expect(toastEl.textContent).toBe("Успешно");
    expect(toastEl.className).toBe("toast show success");
  });

  it("showToast hides toast after timeout", () => {
    showToast("Ошибка", "error");

    vi.advanceTimersByTime(2500);

    expect(toastEl.className).toBe("toast");
  });

  it("openModal removes hidden class", () => {
    const modal = document.createElement("div");
    modal.classList.add("hidden");

    openModal(modal);

    expect(modal.classList.contains("hidden")).toBe(false);
  });

  it("closeModal adds hidden class", () => {
    const modal = document.createElement("div");

    closeModal(modal);

    expect(modal.classList.contains("hidden")).toBe(true);
  });

  it("openModal and closeModal do nothing if modal is null", () => {
    expect(() => openModal(null)).not.toThrow();
    expect(() => closeModal(null)).not.toThrow();
  });

  it("formatRub formats number as RUB currency", () => {
    const result = formatRub(1500.5);

    expect(result).toContain("1");
    expect(result).toContain("500");
    expect(result).toContain("50");
    expect(result).toContain("₽");
  });

  it("formatRub returns dash for invalid values", () => {
    expect(formatRub(null)).toBe("—");
    expect(formatRub(undefined)).toBe("—");
    expect(formatRub("abc")).toBe("—");
  });

  it("formatXAxisLabel returns time for one-day period with T separator", () => {
    expect(formatXAxisLabel("2024-01-01T15:30:00", 1)).toBe("15:30");
  });

  it("formatXAxisLabel returns time for one-day period with space separator", () => {
    expect(formatXAxisLabel("2024-01-01 09:45:00", 1)).toBe("09:45");
  });

  it("formatXAxisLabel returns day and month for multi-day period", () => {
    expect(formatXAxisLabel("2024-01-15T10:00:00", 30)).toBe("15.01");
  });
});