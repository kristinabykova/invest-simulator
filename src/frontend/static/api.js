import { API_URL } from "./config.js";

export async function apiGetJson(path) {
  const res = await fetch(`${API_URL}${path}`, {
    credentials: "include"
  });
  if (!res.ok) throw new Error(`HTTP ${res.status} ${path}`);
  return res.json();
}

export async function apiPostJson(path, body) {
  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(body),
  });

  let data = null;
  try {
    data = await res.json();
  } catch {
    data = null;
  }

  if (!res.ok) {
    const error = new Error(`HTTP ${res.status} ${path}`);
    error.status = res.status;
    error.data = data;
    throw error;
  }

  return data;
}