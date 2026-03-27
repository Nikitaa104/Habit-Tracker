import axios from "axios";

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || "/api",
  headers: { "Content-Type": "application/json" },
});

// Normalise errors so callers always get { message, errors? }
api.interceptors.response.use(
  (res) => res,
  (err) => {
    const data = err.response?.data || {};
    const message = data.error || "An unexpected error occurred.";
    const errors = data.errors || null;
    return Promise.reject({ message, errors, status: err.response?.status });
  }
);

// ── Habits ────────────────────────────────────────────────────────

export const listHabits = (includeArchived = false) =>
  api.get(`/habits${includeArchived ? "?archived=true" : ""}`).then((r) => r.data);

export const getHabit = (id) => api.get(`/habits/${id}`).then((r) => r.data);

export const createHabit = (payload) =>
  api.post("/habits", payload).then((r) => r.data);

export const updateHabit = (id, payload) =>
  api.patch(`/habits/${id}`, payload).then((r) => r.data);

export const deleteHabit = (id) => api.delete(`/habits/${id}`);

// ── Completions ───────────────────────────────────────────────────

export const logCompletion = (habitId, payload = {}) =>
  api.post(`/habits/${habitId}/completions`, payload).then((r) => r.data);

export const undoCompletion = (habitId, dateStr) =>
  api.delete(`/habits/${habitId}/completions/${dateStr}`);

export const listCompletions = (habitId) =>
  api.get(`/habits/${habitId}/completions`).then((r) => r.data);
