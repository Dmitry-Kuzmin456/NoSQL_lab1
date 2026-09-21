export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

type ApiOptions = RequestInit & { skipAuthRetry?: boolean };

let refreshInFlight: Promise<boolean> | null = null;

async function refreshSession(): Promise<boolean> {
  if (!refreshInFlight) {
    refreshInFlight = (async () => {
      const response = await fetch("/api/auth/refresh", {
        method: "POST",
        credentials: "include",
      });
      return response.ok;
    })().finally(() => {
      refreshInFlight = null;
    });
  }
  return refreshInFlight;
}

export async function api<T>(path: string, init: ApiOptions = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const { skipAuthRetry, ...requestInit } = init;
  const response = await fetch(path, {
    ...requestInit,
    headers,
    credentials: "include",
  });

  if (
    response.status === 401 &&
    !skipAuthRetry &&
    !path.startsWith("/api/auth/")
  ) {
    const refreshed = await refreshSession();
    if (refreshed) {
      return api<T>(path, { ...init, skipAuthRetry: true });
    }
  }

  if (response.status === 204) {
    return undefined as T;
  }

  const payload: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    const detail =
      payload &&
      typeof payload === "object" &&
      "detail" in payload &&
      typeof payload.detail === "string"
        ? payload.detail
        : "Ошибка запроса";
    throw new ApiError(response.status, detail);
  }

  return payload as T;
}
