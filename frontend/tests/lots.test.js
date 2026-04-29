import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

vi.mock("../static/config.js", () => ({
  API_URL: "http://localhost:8000",
}));

import { loadLotSize } from "../static/lots.js";

describe("lots.js", () => {
  beforeEach(() => {
    global.fetch = vi.fn();
    vi.spyOn(console, "error").mockImplementation(() => {});
    document.body.innerHTML = `<div id="lotInfo"></div>`;
  });

  afterEach(() => {
    vi.restoreAllMocks();
    document.body.innerHTML = "";
  });

  it("loadLotSize loads lot size and writes it to DOM", async () => {
    fetch.mockResolvedValue({
      ok: true,
      status: 200,
      json: vi.fn().mockResolvedValue({ lotsize: 10 }),
    });

    await loadLotSize("SBER");

    expect(fetch).toHaveBeenCalledWith("http://localhost:8000/stocks/SBER/lotsize");
    expect(document.getElementById("lotInfo").textContent).toBe("10");
  });

  it("loadLotSize encodes ticker in URL", async () => {
    fetch.mockResolvedValue({
      ok: true,
      status: 200,
      json: vi.fn().mockResolvedValue({ lotsize: 1 }),
    });

    await loadLotSize("SBER TEST");

    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:8000/stocks/SBER%20TEST/lotsize"
    );
  });

  it("loadLotSize shows fallback text on HTTP error", async () => {
    fetch.mockResolvedValue({
      ok: false,
      status: 404,
      json: vi.fn(),
    });

    await loadLotSize("UNKNOWN");

    expect(document.getElementById("lotInfo").textContent).toBe("нет данных");
    expect(console.error).toHaveBeenCalled();
  });

  it("loadLotSize does not fail if lotInfo element is missing", async () => {
    document.body.innerHTML = "";

    fetch.mockResolvedValue({
      ok: true,
      status: 200,
      json: vi.fn().mockResolvedValue({ lotsize: 10 }),
    });

    await expect(loadLotSize("SBER")).resolves.toBeUndefined();
  });

  it("loadLotSize shows fallback text on JSON parsing error", async () => {
    fetch.mockResolvedValue({
      ok: true,
      status: 200,
      json: vi.fn().mockRejectedValue(new Error("Invalid JSON")),
    });

    await loadLotSize("SBER");

    expect(document.getElementById("lotInfo").textContent).toBe("нет данных");
    expect(console.error).toHaveBeenCalled();
  });
});