# OIDC client flow — Auth-Code + PKCE + refresh

**Status:** contract reference for client kits (web + iOS). **Owner:** libraos-sdk.

Interactive login for LibraOS clients is **OpenID Connect Authorization Code + PKCE**
against the kernel's embedded OIDC provider (`/oauth/*`). This contract is **not** part of
the OpenAPI partner spec — that spec's `bearerAuth` assumes a partner-minted JWT. Interactive
end-user login is a separate auth contract, documented here, and consumed by the hand-written
OIDC helper in each client kit (it is **not** generated from the OpenAPI spec).

Once a client holds an access token from this flow, it sets it as the `Bearer` token on every
REST call described by `openapi/nova-os-partner.v1.yaml`.

---

## 1. Endpoints

The LibraOS server exposes a minimal OIDC provider. Base URL is the instance's public URL
(`NOVA_OS_PUBLIC_URL`, falling back to `http://<host>:<port>`); the `Deployment.auth.issuer`
field (`GET /v1/managed/deployment`) advertises it and whether OIDC is enabled.

| Endpoint | Method | Purpose |
|---|---|---|
| `/oauth/authorize` | GET | Embedded login screen (no third-party redirects). Renders the login form; on success issues a one-time authorization `code` to the registered `redirect_uri`. |
| `/oauth/login` | POST | Form post from the login screen: bcrypt-verifies credentials, sets the short-lived `nova_oidc_session` cookie (HttpOnly + Secure + SameSite=Lax, ~10 min). |
| `/oauth/token` | POST | Exchanges a one-time `code` (5 min TTL, single-use) for an `id_token` + `access_token`. PKCE `code_verifier` required when the auth request used `code_challenge`. Also serves the `refresh_token` grant. |
| `/oauth/userinfo` | GET | Returns `sub` / `email` / `name` / `role` for the bearer token. |

The issued JWT is HS256 and carries `sub`, `email`, `role`, `name`.

> **Sign in with X (upstream IdP brokering):** when the operator configures upstream providers,
> the `/oauth/authorize` login screen also renders "Sign in with X" buttons (Google/Okta/Azure/
> Authentik via OIDC discovery, GitHub via OAuth2). This is transparent to the client — the
> client still does the same Auth-Code+PKCE dance against LibraOS; the upstream round-trip happens
> server-side behind the LibraOS login screen.

---

## 2. Registered clients

Clients are pre-registered server-side (no dynamic registration). The two first-party clients
the kits target:

| `client_id` | `redirect_uri` | PKCE | Notes |
|---|---|---|---|
| `nova-os-ios` | `novaos://oauth/callback` | **required** (S256) | Native iOS deep-link. Opened via `ASWebAuthenticationSession`; the callback custom scheme returns control to the app. |
| `nova-os-ui` | `<web-origin>/oauth/callback` | **required** (S256) | First-party web client (employee-ui / school-ui). Exact origin is operator-configured. |

Public clients (browser SPA, mobile app) have **no client secret** — PKCE is the proof-of-possession
that replaces it. Additional clients are operator-configured (`NOVA_OS_OIDC_CLIENTS` env or
`oidc_clients:` YAML); `app_id` collisions with the built-ins are rejected in favor of the built-ins.

---

## 3. Auth-Code + PKCE sequence

```
Client                         LibraOS /oauth                       Token store
  │                                  │                                   │
  │ 1. generate code_verifier (43–128 char, [A-Za-z0-9-._~])            │
  │    code_challenge = BASE64URL(SHA256(code_verifier))               │
  │    state = random; nonce = random                                  │
  │                                  │                                   │
  │ 2. open authorize URL ──────────▶│                                   │
  │    GET /oauth/authorize?                                            │
  │      response_type=code                                            │
  │      &client_id=nova-os-ios                                        │
  │      &redirect_uri=novaos://oauth/callback                         │
  │      &scope=openid%20profile%20email                               │
  │      &state=<state>&nonce=<nonce>                                  │
  │      &code_challenge=<challenge>&code_challenge_method=S256        │
  │                                  │                                   │
  │              (user authenticates: POST /oauth/login → session)     │
  │                                  │                                   │
  │ 3. ◀──── redirect to redirect_uri?code=<code>&state=<state>        │
  │    verify returned state == sent state (CSRF)                      │
  │                                  │                                   │
  │ 4. POST /oauth/token ───────────▶│                                   │
  │    grant_type=authorization_code                                  │
  │    &code=<code>                                                    │
  │    &redirect_uri=novaos://oauth/callback                          │
  │    &client_id=nova-os-ios                                          │
  │    &code_verifier=<verifier>                                       │
  │                                  │                                   │
  │ 5. ◀──── { id_token, access_token, token_type:"Bearer",           │
  │            expires_in, refresh_token? }                            │
  │                                  │                                   │
  │ 6. persist tokens ──────────────────────────────────────────────▶ │
  │ 7. call REST API with Authorization: Bearer <access_token>        │
```

The authorization `code` is single-use and expires in 5 minutes. Reusing it fails.

### PKCE (S256)

- `code_verifier`: cryptographically-random string, 43–128 chars from the unreserved set
  `[A-Za-z0-9-._~]`.
- `code_challenge` = `BASE64URL-NO-PAD( SHA256( ASCII(code_verifier) ) )`.
- `code_challenge_method` = `S256` (plain is not used by the kits).

In browsers and React Native this is computed with Web Crypto (`crypto.subtle.digest`); the
client kit's PKCE helper takes an injectable crypto provider so the same core runs in Node 22,
browsers, and RN (with a polyfilled `crypto`).

---

## 4. Refresh grant

> **Kernel status:** the `refresh_token` grant on `/oauth/token` is the one known kernel gap in
> the contract-unification plan (reference: `nova-os-school` branch `feat/i5-oidc-refresh`). Clients
> keep the `refresh()` seam regardless; when the access token is short-lived and no refresh token
> is issued yet, the client re-runs the interactive Auth-Code flow on expiry.

When a `refresh_token` is present, the client refreshes silently:

```
POST /oauth/token
  grant_type=refresh_token
  &refresh_token=<refresh_token>
  &client_id=nova-os-ios

→ { access_token, token_type:"Bearer", expires_in, refresh_token? }
```

Refresh strategy in the kit:

- Refresh **proactively** when the access token is within a small skew (e.g. 60 s) of expiry, OR
  **reactively** on a `401 authentication_error` from a REST call — refresh once, retry the call once.
- If refresh fails (`invalid_grant`), clear the token store and fall back to the interactive
  Auth-Code flow.
- Never retry a refresh more than once per failure — a refresh loop is a bug, not a backoff.

---

## 5. Token storage guidance

The kit defines a swappable `TokenStore` interface (`get` / `set` / `clear`); the consumer injects
the platform-appropriate implementation. **Tokens are bearer credentials — store them where the
platform protects secrets, not in plaintext app state.**

| Platform | Recommended store | Avoid |
|---|---|---|
| iOS (`nova-os-ios`) | Keychain (`kSecAttrAccessibleAfterFirstUnlock`) | `UserDefaults`, plist |
| Web SPA (`nova-os-ui`) | In-memory + refresh-token in an HttpOnly cookie when a BFF is present; else `sessionStorage` over `localStorage` | `localStorage` for long-lived refresh tokens (XSS-exfiltratable) |
| Node / server-side | Process memory or the host secret manager | env files committed to VCS |
| React Native | `expo-secure-store` / Keychain-backed module | `AsyncStorage` plaintext |

The kit ships a `MemoryTokenStore` default for tests and Node; every shipping client injects a
hardened store.

### Logout

Clear the token store and drop the `nova_oidc_session` cookie (web). The kernel issues stateless
JWTs, so client-side clearing is the logout primitive; short token lifetimes bound the blast radius.

---

## 6. Error handling

| Condition | Response | Client action |
|---|---|---|
| `state` mismatch on callback | — (client-side check) | Abort the flow; do not exchange the code (CSRF). |
| `code` expired / reused | `400 invalid_grant` | Restart the Auth-Code flow. |
| Missing/invalid `code_verifier` | `400 invalid_grant` | Bug in the client PKCE pairing; regenerate verifier+challenge per attempt. |
| Refresh token revoked/expired | `400 invalid_grant` | Clear store, restart interactive flow. |
| REST call after token expiry | `401 authentication_error` | Refresh once, retry once; else interactive flow. |

---

## 7. References

- LibraOS OIDC provider — `/oauth/{authorize,login,token,userinfo}`; HS256 id_token; PKCE S256.
- `openapi/nova-os-partner.v1.yaml` — `Deployment.auth` advertises `oidc_enabled` + `issuer`.
- Contract-unification design — `docs/superpowers/specs/2026-06-12-contract-unification-design.md`
  (§2 "the contract is three specs", §5 libraos-sdk owns this doc, §6 refresh grant is the kernel gap).
- RFC 7636 (PKCE), RFC 6749 §4.1 (Authorization Code), RFC 6749 §6 (Refresh grant).
