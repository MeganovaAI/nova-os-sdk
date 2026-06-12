/**
 * Typed REST client factory over the generated OpenAPI `paths`.
 *
 * Thin wrapper on `openapi-fetch` (a tiny, framework-agnostic typed fetch — no
 * React/axios). Adds: Bearer auth from a token provider, automatic
 * refresh-on-401 (refresh once, retry once), and raw helpers for the two SSE
 * surfaces (message stream + job stream) that codegen can't model.
 */

import createOpenApiClient from "openapi-fetch";
import type { Client } from "openapi-fetch";
import type { paths } from "./_generated/schema.js";
import { NovaApiError, asNovaErrorBody } from "./errors.js";

/** Supplies the current bearer token and a one-shot refresh on 401. */
export interface AuthProvider {
  /** Returns the access token to attach, or undefined for an unauthenticated call. */
  getAccessToken(): Promise<string | undefined> | string | undefined;
  /** Force a token refresh; return the new token or undefined if refresh failed. */
  refresh?(): Promise<string | undefined>;
}

export interface RestClientOptions {
  /** Base URL of the Nova OS instance, e.g. "https://api.example.com". */
  baseUrl: string;
  /** Token provider; omit for unauthenticated (e.g. health) calls. */
  auth?: AuthProvider;
  /** Injected fetch; defaults to globalThis.fetch. */
  fetch?: typeof fetch;
}

/** A typed `openapi-fetch` client plus the bound options (for SSE helpers). */
export interface RestClient {
  /** The underlying typed openapi-fetch client (GET/POST/PUT/DELETE over `paths`). */
  api: Client<paths>;
  options: RestClientOptions;
}

export function createRestClient(options: RestClientOptions): RestClient {
  const baseFetch = options.fetch ?? (globalThis as { fetch?: typeof fetch }).fetch;
  if (!baseFetch) throw new Error("No fetch available; pass `fetch` in RestClientOptions.");

  // Wrap fetch to inject Bearer + handle a single refresh-retry on 401.
  const authedFetch: typeof fetch = async (input, init) => {
    const withAuth = async (token: string | undefined): Promise<RequestInit> => {
      const headers = new Headers(init?.headers);
      if (token) headers.set("authorization", `Bearer ${token}`);
      return { ...init, headers };
    };

    const token = options.auth ? await options.auth.getAccessToken() : undefined;
    let res = await baseFetch(input, await withAuth(token));

    if (res.status === 401 && options.auth?.refresh) {
      const fresh = await options.auth.refresh();
      if (fresh) {
        res = await baseFetch(input, await withAuth(fresh));
      }
    }
    return res;
  };

  const api = createOpenApiClient<paths>({
    baseUrl: options.baseUrl,
    fetch: authedFetch,
  });

  return { api, options };
}

/**
 * Raise a {@link NovaApiError} from an openapi-fetch `{ error, response }` result.
 * Use after a typed call when you want exceptions instead of the result tuple.
 */
export function throwIfError(result: { error?: unknown; response: Response }): void {
  if (result.error !== undefined || !result.response.ok) {
    throw new NovaApiError(result.response.status, asNovaErrorBody(result.error));
  }
}
