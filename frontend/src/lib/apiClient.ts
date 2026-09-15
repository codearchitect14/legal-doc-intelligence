import type { components } from "./api-types";

// Every page calls through this module rather than using raw fetch, so auth
// headers, token refresh, and error handling stay in exactly one place
// (docs/PROJECT_PLAN_v2.md Section 14 Phase 6: a typed client generated from
// the OpenAPI schema, so frontend and backend never drift out of sync).

export type Schemas = components["schemas"];

const REFRESH_TOKEN_KEY = "ldi_refresh_token";
let accessToken: string | null = null;

export function setRefreshToken(token: string | null): void {
  if (token) {
    localStorage.setItem(REFRESH_TOKEN_KEY, token);
  } else {
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  }
}

export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function setAccessToken(token: string | null): void {
  accessToken = token;
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return null;

  const response = await fetch("/api/auth/refresh", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
    cache: "no-store",
  });
  if (!response.ok) {
    setRefreshToken(null);
    setAccessToken(null);
    return null;
  }
  const data = (await response.json()) as Schemas["AccessToken"];
  setAccessToken(data.access_token);
  return data.access_token;
}

interface RequestOptions {
  method?: string;
  body?: unknown;
  isForm?: boolean;
  signal?: AbortSignal;
}

async function request<T>(path: string, options: RequestOptions = {}, isRetry = false): Promise<T> {
  const headers: Record<string, string> = {};
  if (accessToken) headers.Authorization = `Bearer ${accessToken}`;
  if (!options.isForm && options.body !== undefined) headers["Content-Type"] = "application/json";

  const response = await fetch(`/api${path}`, {
    method: options.method ?? "GET",
    headers,
    body: options.isForm
      ? (options.body as FormData)
      : options.body !== undefined
        ? JSON.stringify(options.body)
        : undefined,
    signal: options.signal,
    // Every response here reflects live, frequently-changing case state
    // (e.g. GET /totals legitimately flips from 404 to 200 the moment
    // /analyze runs). Without this, the browser's HTTP cache can serve an
    // earlier response for an identical GET instead of hitting the network,
    // showing stale results after an action that just changed them.
    cache: "no-store",
  });

  if (response.status === 401 && !isRetry) {
    const newToken = await refreshAccessToken();
    if (newToken) {
      return request<T>(path, options, true);
    }
  }

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const errorBody = await response.json();
      detail = errorBody.detail ? JSON.stringify(errorBody.detail) : detail;
    } catch {
      // response body wasn't JSON; keep the status text
    }
    throw new ApiError(response.status, detail);
  }

  if (response.status === 204) return undefined as T;

  const contentType = response.headers.get("content-type") ?? "";
  if (contentType.includes("application/json")) {
    return (await response.json()) as T;
  }
  return (await response.blob()) as T;
}

export const authApi = {
  registerFirm: (payload: Schemas["FirmRegisterRequest"]) =>
    request<Schemas["UserOut"]>("/auth/register-firm", { method: "POST", body: payload }),

  login: async (email: string, password: string) => {
    const form = new URLSearchParams();
    form.set("username", email);
    form.set("password", password);
    let response: Response;
    try {
      response = await fetch("/api/auth/login", { method: "POST", body: form, cache: "no-store" });
    } catch {
      throw new ApiError(0, "Could not reach the server. Is the backend running?");
    }
    if (!response.ok) {
      // A wrong password/email is the only case that should say so; any
      // other failure (backend down, proxy error, validation error) must
      // surface its real cause instead of being mislabeled as bad
      // credentials, which was hiding genuine outages during local testing.
      if (response.status === 401) {
        throw new ApiError(response.status, "Incorrect email or password");
      }
      let detail = response.statusText || "Login failed";
      try {
        const errorBody = await response.json();
        detail = errorBody.detail ? JSON.stringify(errorBody.detail) : detail;
      } catch {
        // response body wasn't JSON; keep the status text
      }
      throw new ApiError(response.status, detail);
    }
    const data = (await response.json()) as Schemas["TokenPair"];
    setAccessToken(data.access_token);
    setRefreshToken(data.refresh_token);
    return data;
  },

  me: () => request<Schemas["UserOut"]>("/auth/me"),

  logout: () => {
    setAccessToken(null);
    setRefreshToken(null);
  },

  restoreSession: async () => {
    const token = await refreshAccessToken();
    return token !== null;
  },
};

export const casesApi = {
  list: () => request<Schemas["CaseOut"][]>("/cases"),
  get: (caseId: string) => request<Schemas["CaseOut"]>(`/cases/${caseId}`),
  create: (payload: Schemas["CaseCreateRequest"]) =>
    request<Schemas["CaseOut"]>("/cases", { method: "POST", body: payload }),
};

export const documentsApi = {
  list: (caseId: string) => request<Schemas["DocumentOut"][]>(`/cases/${caseId}/documents`),
  get: (caseId: string, documentId: string) =>
    request<Schemas["DocumentOut"]>(`/cases/${caseId}/documents/${documentId}`),
  fields: (caseId: string, documentId: string) =>
    request<Schemas["ExtractedFieldOut"][]>(`/cases/${caseId}/documents/${documentId}/fields`),
  // Bearer auth means a plain <a>/<img> URL can't carry the token, so the
  // file is fetched as a blob and handed back as an object URL instead.
  // The blob's own content-type (set by the backend from the stored
  // filename) tells the viewer whether to render an image, a PDF, or fall
  // back to a plain download link - DocumentOut doesn't expose a filename.
  fetchFile: async (caseId: string, documentId: string) => {
    const blob = await request<Blob>(`/cases/${caseId}/documents/${documentId}/file`);
    return { url: URL.createObjectURL(blob), contentType: blob.type };
  },
  upload: (caseId: string, files: FileList) => {
    const form = new FormData();
    Array.from(files).forEach((file) => form.append("files", file));
    return request<Schemas["DocumentOut"][]>(`/cases/${caseId}/documents`, {
      method: "POST",
      body: form,
      isForm: true,
    });
  },
};

export const analysisApi = {
  analyze: (caseId: string) =>
    request<Schemas["AnalysisResult"]>(`/cases/${caseId}/analyze`, { method: "POST" }),
  chronology: (caseId: string) =>
    request<Schemas["TimelineEventOut"][]>(`/cases/${caseId}/chronology`),
  totals: (caseId: string) => request<Schemas["CaseTotalsOut"]>(`/cases/${caseId}/totals`),
  inconsistencies: (caseId: string) =>
    request<Schemas["InconsistencyFlagOut"][]>(`/cases/${caseId}/inconsistencies`),
};

export const draftApi = {
  list: (caseId: string) => request<Schemas["DraftOutputOut"][]>(`/cases/${caseId}/drafts`),
  create: (caseId: string, outputType: string) =>
    request<Schemas["DraftOutputOut"]>(`/cases/${caseId}/draft`, {
      method: "POST",
      body: { output_type: outputType },
    }),
  update: (caseId: string, draftId: string, content: string) =>
    request<Schemas["DraftOutputOut"]>(`/cases/${caseId}/drafts/${draftId}`, {
      method: "PATCH",
      body: { content },
    }),
  fetchExportUrl: async (caseId: string, draftId: string) => {
    const blob = await request<Blob>(`/cases/${caseId}/drafts/${draftId}/export`);
    return URL.createObjectURL(blob);
  },
};
