import { describe, it, expect, vi, beforeEach } from "vitest";

vi.mock("../static/dom.js", () => ({
  registerEmail: { value: "" },
  registerPassword: { value: "" },
  loginEmail: { value: "" },
  loginPassword: { value: "" },
  registerModal: { id: "register-modal" },
  loginModal: { id: "login-modal" },
}));

vi.mock("../static/api.js", () => ({
  apiPostJson: vi.fn(),
}));

vi.mock("../static/utils.js", () => ({
  closeModal: vi.fn(),
  showToast: vi.fn(),
}));

import {
  clearAuthFields,
  registerUser,
  loginUser,
  logoutUser,
} from "../static/auth.js";

import {
  registerEmail,
  registerPassword,
  loginEmail,
  loginPassword,
  registerModal,
  loginModal,
} from "../static/dom.js";

import { apiPostJson } from "../static/api.js";
import { closeModal, showToast } from "../static/utils.js";

describe("auth.js", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    registerEmail.value = "";
    registerPassword.value = "";
    loginEmail.value = "";
    loginPassword.value = "";
  });

  it("clearAuthFields clears register and login fields", () => {
    registerEmail.value = "user@example.com";
    registerPassword.value = "password";
    loginEmail.value = "login@example.com";
    loginPassword.value = "login-password";

    clearAuthFields();

    expect(registerEmail.value).toBe("");
    expect(registerPassword.value).toBe("");
    expect(loginEmail.value).toBe("");
    expect(loginPassword.value).toBe("");
  });

  it("registerUser sends register request and returns true on success", async () => {
    registerEmail.value = " user@example.com ";
    registerPassword.value = " password123 ";

    apiPostJson.mockResolvedValue({ ok: true });

    const result = await registerUser();

    expect(result).toBe(true);
    expect(apiPostJson).toHaveBeenCalledWith("/auth/register", {
      email: "user@example.com",
      password: "password123",
    });
    expect(closeModal).toHaveBeenCalledWith(registerModal);
    expect(registerEmail.value).toBe("");
    expect(registerPassword.value).toBe("");
    expect(showToast).toHaveBeenCalledWith(
      "Регистрация прошла успешно. Войдите в свой аккаунт.",
      "success"
    );
  });

  it("registerUser shows validation error for 422", async () => {
    registerEmail.value = "bad-email";
    registerPassword.value = "password123";

    apiPostJson.mockRejectedValue({
      status: 422,
      data: { detail: "validation error" },
    });

    const result = await registerUser();

    expect(result).toBe(false);
    expect(showToast).toHaveBeenCalledWith("Введите корректный емайл", "error");
    expect(closeModal).not.toHaveBeenCalled();
  });

  it("registerUser shows backend detail if detail is string", async () => {
    registerEmail.value = "user@example.com";
    registerPassword.value = "password123";

    apiPostJson.mockRejectedValue({
      status: 400,
      data: { detail: "Пользователь уже существует" },
    });

    const result = await registerUser();

    expect(result).toBe(false);
    expect(showToast).toHaveBeenCalledWith(
      "Пользователь уже существует",
      "error"
    );
  });

  it("registerUser shows default error if detail is not string", async () => {
    registerEmail.value = "user@example.com";
    registerPassword.value = "password123";

    apiPostJson.mockRejectedValue({
      status: 500,
      data: { detail: [{ msg: "error" }] },
    });

    const result = await registerUser();

    expect(result).toBe(false);
    expect(showToast).toHaveBeenCalledWith("Ошибка регистрации", "error");
  });

  it("loginUser sends login request and returns true on success", async () => {
    loginEmail.value = " user@example.com ";
    loginPassword.value = " password123 ";

    apiPostJson.mockResolvedValue({ ok: true });

    const result = await loginUser();

    expect(result).toBe(true);
    expect(apiPostJson).toHaveBeenCalledWith("/auth/login", {
      email: "user@example.com",
      password: "password123",
    });
    expect(closeModal).toHaveBeenCalledWith(loginModal);
    expect(loginEmail.value).toBe("");
    expect(loginPassword.value).toBe("");
    expect(showToast).toHaveBeenCalledWith("Вы успешно вошли", "success");
  });

  it("loginUser shows validation error for 422", async () => {
    loginEmail.value = "bad-email";
    loginPassword.value = "password123";

    apiPostJson.mockRejectedValue({
      status: 422,
      data: { detail: "validation error" },
    });

    const result = await loginUser();

    expect(result).toBe(false);
    expect(showToast).toHaveBeenCalledWith("Введите корректный емайл", "error");
    expect(closeModal).not.toHaveBeenCalled();
  });

  it("loginUser shows backend detail if detail is string", async () => {
    loginEmail.value = "user@example.com";
    loginPassword.value = "wrong-password";

    apiPostJson.mockRejectedValue({
      status: 401,
      data: { detail: "Invalid email or password" },
    });

    const result = await loginUser();

    expect(result).toBe(false);
    expect(showToast).toHaveBeenCalledWith("Invalid email or password", "error");
  });

  it("loginUser shows default error if detail is not string", async () => {
    loginEmail.value = "user@example.com";
    loginPassword.value = "password123";

    apiPostJson.mockRejectedValue({
      status: 500,
      data: { detail: [{ msg: "error" }] },
    });

    const result = await loginUser();

    expect(result).toBe(false);
    expect(showToast).toHaveBeenCalledWith("Ошибка входа", "error");
  });

  it("logoutUser sends logout request and returns true on success", async () => {
    apiPostJson.mockResolvedValue({ ok: true });

    const result = await logoutUser();

    expect(result).toBe(true);
    expect(apiPostJson).toHaveBeenCalledWith("/auth/logout", {});
    expect(showToast).toHaveBeenCalledWith("Вы вышли из аккаунта", "success");
  });

  it("logoutUser shows error and returns false on failed request", async () => {
    apiPostJson.mockRejectedValue(new Error("Network error"));

    const result = await logoutUser();

    expect(result).toBe(false);
    expect(showToast).toHaveBeenCalledWith("Ошибка выхода", "error");
  });
});