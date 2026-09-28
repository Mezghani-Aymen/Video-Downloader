import { getApiBaseUrl } from "./config";

export interface RequestOptions extends RequestInit {
  timeoutMs?: number;
}

export class ApiError extends Error {
  status: number;
  data: any;

  constructor(message: string, status: number, data?: any) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

export async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { timeoutMs = 15000, headers, ...customConfig } = options;
  const baseUrl = getApiBaseUrl();
  const url = `${baseUrl}${endpoint.startsWith("/") ? "" : "/"}${endpoint}`;

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  const config: RequestInit = {
    ...customConfig,
    headers: {
      "Content-Type": "application/json",
      ...(headers || {}),
    },
    signal: controller.signal,
  };

  try {
    const response = await fetch(url, config);
    clearTimeout(timer);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }));
      const detail = errorData.detail || `Request failed with status ${response.status}`;
      throw new ApiError(detail, response.status, errorData);
    }

    return (await response.json()) as T;
  } catch (error: any) {
    clearTimeout(timer);
    if (error.name === "AbortError") {
      throw new ApiError("Request timed out.", 408);
    }
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(error.message || "Network connection error.", 0);
  }
}
