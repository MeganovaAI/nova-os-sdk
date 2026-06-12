/**
 * Token storage seam. The kit defines the interface; the consumer injects the
 * platform-appropriate implementation (Keychain on iOS, HttpOnly cookie via a
 * BFF on web, expo-secure-store on RN). See `docs/oidc-client-flow.md` §5.
 *
 * Tokens are bearer credentials — store them where the platform protects secrets.
 */

/** The token set issued by `/oauth/token`, plus a computed absolute expiry. */
export interface TokenSet {
  accessToken: string;
  tokenType: string;
  /** Refresh token, when the server issues one (kernel gap — may be absent). */
  refreshToken?: string;
  /** OIDC id_token (JWT), when present. */
  idToken?: string;
  /** Absolute expiry as epoch ms. Derived from `expires_in` at exchange time. */
  expiresAt?: number;
}

/** Swappable token persistence. All methods may be async. */
export interface TokenStore {
  get(): Promise<TokenSet | undefined> | TokenSet | undefined;
  set(tokens: TokenSet): Promise<void> | void;
  clear(): Promise<void> | void;
}

/** In-memory default for tests and Node. Shipping clients inject a hardened store. */
export class MemoryTokenStore implements TokenStore {
  private tokens?: TokenSet;

  get(): TokenSet | undefined {
    return this.tokens;
  }
  set(tokens: TokenSet): void {
    this.tokens = tokens;
  }
  clear(): void {
    this.tokens = undefined;
  }
}
