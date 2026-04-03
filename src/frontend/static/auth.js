import {
  registerEmail,
  registerPassword,
  loginEmail,
  loginPassword,
  registerModal,
  loginModal,
} from "./dom.js";
import { apiPostJson } from "./api.js";
import { closeModal, showToast } from "./utils.js";

export function clearAuthFields() {
  if (registerEmail) registerEmail.value = "";
  if (registerPassword) registerPassword.value = "";
  if (loginEmail) loginEmail.value = "";
  if (loginPassword) loginPassword.value = "";
}

export async function registerUser() {
  const email = registerEmail.value.trim();
  const password = registerPassword.value.trim();

  try {
    await apiPostJson("/auth/register", { email, password });
    closeModal(registerModal);
    clearAuthFields();
    showToast("Регистрация прошла успешно. Войдите в свой аккаунт.", "success");
    return true;
  } catch (e) {
    if (e.status === 422) {
      showToast("Введите корректный емайл", "error");
      return false;
    }

    const detail = e.data?.detail;

    if (typeof detail === "string") {
      showToast(detail, "error");
    } else {
      showToast("Ошибка регистрации", "error");
    }

    return false;
  }
}

export async function loginUser() {
  const email = loginEmail.value.trim();
  const password = loginPassword.value.trim();

  try {
    await apiPostJson("/auth/login", { email, password });
    closeModal(loginModal);
    clearAuthFields();
    showToast("Вы успешно вошли", "success");
    return true;
  } catch (e) {
    if (e.status === 422) {
      showToast("Введите корректный емайл", "error");
      return false;
    }

    const detail = e.data?.detail;

    if (typeof detail === "string") {
      showToast(detail, "error");
    } else {
      showToast("Ошибка входа", "error");
    }

    return false;
  }
}

export async function logoutUser() {
  try {
    await apiPostJson("/auth/logout", {});
    showToast("Вы вышли из аккаунта", "success");
    return true;
  } catch (e) {
    showToast("Ошибка выхода", "error");
    return false;
  }
}