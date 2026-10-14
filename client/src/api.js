import { API_URL, TOKEN_KEY, USER_KEY } from "./config";

export class ApiError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

function safeStorage(action) {
  try {
    return action();
  } catch {
    return null;
  }
}

export const session = {
  token: () => safeStorage(() => localStorage.getItem(TOKEN_KEY)),
  user: () => safeStorage(() => localStorage.getItem(USER_KEY)),
  save(token, user) {
    safeStorage(() => localStorage.setItem(TOKEN_KEY, token));
    safeStorage(() => localStorage.setItem(USER_KEY, user));
  },
  clear() {
    safeStorage(() => localStorage.removeItem(TOKEN_KEY));
    safeStorage(() => localStorage.removeItem(USER_KEY));
  },
};

function readDetail(data) {
  if (!data || !data.detail) return null;
  if (typeof data.detail === "string") return data.detail;
  if (Array.isArray(data.detail)) return data.detail.map((d) => d.msg).join(", ");
  return null;
}

async function request(path, { method = "GET", body, auth = true } = {}) {
  const headers = { "Content-Type": "application/json" };
  const token = session.token();
  if (auth && token) headers.Authorization = `Bearer ${token}`;

  let response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new ApiError(0, "Cannot reach the server. Check that the API is running.");
  }

  let data = null;
  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    throw new ApiError(response.status, readDetail(data) || `Request failed (${response.status}).`);
  }
  return data;
}

export const api = {
  register: (username, password) =>
    request("/auth/register", { method: "POST", body: { username, password }, auth: false }),
  login: (username, password) =>
    request("/auth/login", { method: "POST", body: { username, password }, auth: false }),
  newGame: () => request("/game/new", { method: "POST" }),
  activeGame: async () => {
    try {
      return await request("/game/active");
    } catch (error) {
      if (error.status === 404) return null;
      throw error;
    }
  },
  play: (gameId, card, chosenColor) =>
    request(`/game/${gameId}/play`, {
      method: "POST",
      body: {
        card: { color: card.color, card_type: card.card_type, value: card.value },
        chosen_color: chosenColor || null,
      },
    }),
  draw: (gameId) => request(`/game/${gameId}/draw`, { method: "POST" }),
};
