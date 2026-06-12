/**
 * OIDC Authorization Code + PKCE + refresh helper — public-client shape (no secret).
 *
 * Transport-agnostic core: the kit builds the authorize URL and exchanges the code,
 * but the CALLER owns the redirect (open `ASWebAuthenticationSession`, navigate the
 * browser, etc.) and hands the returned URL back to `handleCallback()`. This keeps
 * the helper consumable in browsers, native iOS, RN, and Node without a framework.
 *
 * Contract: `docs/oidc-client-flow.md` (Auth-Code+PKCE+refresh against the kernel's
 * embedded `/oauth/*` provider). NOT generated from the OpenAPI spec.
 */

import {
  generatePkcePair,
  randomUrlToken,
  type CryptoProvider,
  type PkcePair,
} from "./pkce.js";
import {
  MemoryTokenStore,
  type TokenSet,
  type TokenStore,
} from "./tokenStore.js";

export interface OidcConfig {
  /** OIDC issuer / public base URL (from `Deployment.auth.issuer`). No trailing slash required. */
  issuer: string;
  /** Registered public client id, e.g. "nova-os-ui" or "nova-os-ios". */
  clientId: string;
  /** Registered redirect URI for this client. */
  redirectUri: string;
  /** OAuth scopes; defaults to OIDC standard set. */
  scope?: string;
  /** Token persistence; defaults to in-memory. */
  tokenStore?: TokenStore;
  /** Injected crypto (browser/RN polyfill); defaults to globalThis.crypto. */
  crypto?: CryptoProvider;
  /** Injected fetch; defaults to globalThis.fetch. */
  fetch?: typeof fetch;
  /** Proactive-refresh skew in seconds before expiry. Default 60. */
  refreshSkewSeconds?: number;
}

/** Transient per-login state the caller must round-trip to `handleCallback()`. */
export interface PendingLogin {
  state: string;
  nonce: string;
  pkce: PkcePair;
  /** The full authorize URL to open in the user agent. */
  authorizeUrl: string;
}

interface OidcTokenResponse {
  access_token: string;
  token_type: string;
  expires_in?: number;
  refresh_token?: string;
  id_token?: string;
}

function joinUrl(base: string, path: string): string {
  return base.replace(/\/+$/, "") + path;
}

export class OidcClient {
  private readonly cfg: Required<Omit<OidcConfig, "crypto" | "fetch" | "tokenStore">> &
    Pick<OidcConfig, "crypto">;
  private readonly store: TokenStore;
  private readonly fetchImpl: typeof fetch;

  constructor(config: OidcConfig) {
    this.cfg = {
      issuer: config.issuer,
      clientId: config.clientId,
      redirectUri: config.redirectUri,
      scope: config.scope ?? "openid profile email",
      refreshSkewSeconds: config.refreshSkewSeconds ?? 60,
      crypto: config.crypto,
    };
    this.store = config.tokenStore ?? new MemoryTokenStore();
    const f = config.fetch ?? (globalThis as { fetch?: typeof fetch }).fetch;
    if (!f) throw new Error("No fetch available; pass `fetch` in OidcConfig.");
    this.fetchImpl = f;
  }

  /**
   * Begin an interactive login. Builds the PKCE pair + state/nonce and the
   * authorize URL. The caller opens `result.authorizeUrl` in the user agent and
   * must keep `result` to pass to `handleCallback()`.
   */
  async login(): Promise<PendingLogin> {
    const pkce = await generatePkcePair(this.cfg.crypto);
    const state = randomUrlToken(32, this.cfg.crypto);
    const nonce = randomUrlToken(32, this.cfg.crypto);
    const params = new URLSearchParams({
      response_type: "code",
      client_id: this.cfg.clientId,
      redirect_uri: this.cfg.redirectUri,
      scope: this.cfg.scope,
      state,
      nonce,
      code_challenge: pkce.challenge,
      code_challenge_method: pkce.method,
    });
    const authorizeUrl = joinUrl(this.cfg.issuer, "/oauth/authorize") + "?" + params.toString();
    return { state, nonce, pkce, authorizeUrl };
  }

  /**
   * Complete the flow from the redirect. Pass the full callback URL (or just its
   * query string) and the `PendingLogin` returned by `login()`. Verifies `state`
   * (CSRF), exchanges the code, persists tokens, and returns the token set.
   */
  async handleCallback(callbackUrl: string, pending: PendingLogin): Promise<TokenSet> {
    const query = extractQuery(callbackUrl);
    const returnedState = query.get("state");
    const error = query.get("error");
    if (error) {
      throw new Error(`OIDC authorize error: ${error}${query.get("error_description") ? ` — ${query.get("error_description")}` : ""}`);
    }
    if (!returnedState || returnedState !== pending.state) {
      throw new Error("OIDC state mismatch — aborting (possible CSRF).");
    }
    const code = query.get("code");
    if (!code) throw new Error("OIDC callback missing authorization code.");

    const tokens = await this.exchange(
      new URLSearchParams({
        grant_type: "authorization_code",
        code,
        redirect_uri: this.cfg.redirectUri,
        client_id: this.cfg.clientId,
        code_verifier: pending.pkce.verifier,
      }),
    );
    await this.store.set(tokens);
    return tokens;
  }

  /**
   * Refresh silently using the stored refresh token. Throws if none is present
   * (the kernel refresh-grant gap — caller should fall back to interactive login).
   */
  async refresh(): Promise<TokenSet> {
    const current = await this.store.get();
    if (!current?.refreshToken) {
      throw new Error("No refresh_token available; re-run the interactive login flow.");
    }
    const tokens = await this.exchange(
      new URLSearchParams({
        grant_type: "refresh_token",
        refresh_token: current.refreshToken,
        client_id: this.cfg.clientId,
      }),
    );
    // The refresh response may omit a new refresh_token; keep the old one.
    if (!tokens.refreshToken) tokens.refreshToken = current.refreshToken;
    await this.store.set(tokens);
    return tokens;
  }

  /**
   * Return a valid access token, refreshing proactively when within the skew of
   * expiry. Returns undefined when no token is stored and refresh is impossible.
   */
  async getAccessToken(): Promise<string | undefined> {
    const current = await this.store.get();
    if (!current) return undefined;
    const skewMs = this.cfg.refreshSkewSeconds * 1000;
    const expiringSoon = current.expiresAt !== undefined && Date.now() >= current.expiresAt - skewMs;
    if (expiringSoon && current.refreshToken) {
      try {
        const refreshed = await this.refresh();
        return refreshed.accessToken;
      } catch {
        return current.accessToken; // let the API 401 drive the interactive path
      }
    }
    return current.accessToken;
  }

  /** Clear the token store (logout). */
  async logout(): Promise<void> {
    await this.store.clear();
  }

  /** The token store this client reads/writes — exposed so the REST client can share it. */
  get tokenStore(): TokenStore {
    return this.store;
  }

  private async exchange(body: URLSearchParams): Promise<TokenSet> {
    const res = await this.fetchImpl(joinUrl(this.cfg.issuer, "/oauth/token"), {
      method: "POST",
      headers: { "content-type": "application/x-www-form-urlencoded" },
      body: body.toString(),
    });
    if (!res.ok) {
      let detail = "";
      try {
        const j = (await res.json()) as { error?: string; error_description?: string };
        detail = j.error_description ?? j.error ?? "";
      } catch {
        /* ignore */
      }
      throw new Error(`OIDC token endpoint failed (HTTP ${res.status})${detail ? `: ${detail}` : ""}`);
    }
    const json = (await res.json()) as OidcTokenResponse;
    return {
      accessToken: json.access_token,
      tokenType: json.token_type ?? "Bearer",
      refreshToken: json.refresh_token,
      idToken: json.id_token,
      expiresAt: json.expires_in !== undefined ? Date.now() + json.expires_in * 1000 : undefined,
    };
  }
}

function extractQuery(callbackUrl: string): URLSearchParams {
  // Accept a full URL, a "?a=b" query, or a custom-scheme deep link (novaos://...).
  const q = callbackUrl.indexOf("?");
  if (q !== -1) return new URLSearchParams(callbackUrl.slice(q + 1));
  return new URLSearchParams(callbackUrl);
}
