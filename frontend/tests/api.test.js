import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

vi.mock("../static/config.js", () => ({
  API_URL: "http://localhost:8000",
}));

import { apiGetJson, apiPostJson } from "../static/api.js";

describe("api.js", () => {
  beforeEach(() => {
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("apiGetJson returns JSON data on successful response", async () => {
    const responseData = { message: "ok" };

    fetch.mockResolvedValue({
      ok: true,
      status: 200,
      json: vi.fn().mockResolvedValue(responseData),
    });

    const result = await apiGetJson("/auth/me");

    expect(result).toEqual(responseData);
    expect(fetch).toHaveBeenCalledWith("http://localhost:8000/auth/me", {
      credentials: "include",
    });
  });

  it("apiGetJson throws error on failed response", async () => {
    const errorData = { detail: "Not authenticated" };

    fetch.mockResolvedValue({
      ok: false,
      status: 401,
      json: vi.fn().mockResolvedValue(errorData),
    });

    await expect(apiGetJson("/auth/me")).rejects.toMatchObject({
      message: "HTTP 401 /auth/me",
      status: 401,
      data: errorData,
    });
  });

  it("apiGetJson returns null if response body is not JSON", async () => {
    fetch.mockResolvedValue({
      ok: true,
      status: 204,
      json: vi.fn().mockRejectedValue(new Error("No JSON")),
    });

    const result = await apiGetJson("/empty");

    expect(result).toBeNull();
  });

  it("apiPostJson sends POST request and returns JSON data", async () => {
    const requestBody = {
      email: "user@example.com",
      password: "password123",
    };

    const responseData = {
      access_token: "token",
    };

    fetch.mockResolvedValue({
      ok: true,
      status: 200,
      json: vi.fn().mockResolvedValue(responseData),
    });

    const result = await apiPostJson("/auth/login", requestBody);

    expect(result).toEqual(responseData);
    expect(fetch).toHaveBeenCalledWith("http://localhost:8000/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(requestBody),
    });
  });

  it("apiPostJson uses empty object as default body", async () => {
    fetch.mockResolvedValue({
      ok: true,
      status: 200,
      json: vi.fn().mockResolvedValue({ ok: true }),
    });

    await apiPostJson("/auth/logout");

    expect(fetch).toHaveBeenCalledWith("http://localhost:8000/auth/logout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({}),
    });
  });

  it("apiPostJson throws error on failed response", async () => {
    const errorData = { detail: "Invalid email or password" };

    fetch.mockResolvedValue({
      ok: false,
      status: 401,
      json: vi.fn().mockResolvedValue(errorData),
    });

    await expect(
      apiPostJson("/auth/login", {
        email: "user@example.com",
        password: "wrong",
      })
    ).rejects.toMatchObject({
      message: "HTTP 401 /auth/login",
      status: 401,
      data: errorData,
    });
  });

  it("apiPostJson sets error data to null if error response is not JSON", async () => {
    fetch.mockResolvedValue({
      ok: false,
      status: 500,
      json: vi.fn().mockRejectedValue(new Error("No JSON")),
    });

    await expect(apiPostJson("/broken")).rejects.toMatchObject({
      message: "HTTP 500 /broken",
      status: 500,
      data: null,
    });
  });
});
