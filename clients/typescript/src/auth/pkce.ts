/**
 * PKCE (RFC 7636) S256 helpers — transport-agnostic.
 *
 * Uses Web Crypto (`crypto.subtle` + `crypto.getRandomValues`), which is global
 * in browsers, Node 18+, and React Native (with a polyfill). The crypto provider
 * is injectable so the same core runs everywhere; defaults to `globalThis.crypto`.
 */

export interface CryptoProvider {
  getRandomValues<T extends ArrayBufferView | null>(array: T): T;
  subtle: Pick<SubtleCrypto, "digest">;
}

function resolveCrypto(provided?: CryptoProvider): CryptoProvider {
  const c = provided ?? (globalThis as { crypto?: CryptoProvider }).crypto;
  if (!c || !c.subtle || typeof c.getRandomValues !== "function") {
    throw new Error(
      "No Web Crypto available. Pass a CryptoProvider (e.g. a polyfill) to the PKCE helper.",
    );
  }
  return c;
}

const UNRESERVED = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~";

/** A PKCE verifier/challenge pair for one Auth-Code attempt. */
export interface PkcePair {
  verifier: string;
  challenge: string;
  method: "S256";
}

/** Base64URL-encode (no padding) a byte buffer. */
export function base64UrlEncode(bytes: Uint8Array): string {
  let bin = "";
  for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]!);
  // btoa is global in browsers, Node 18+, and React Native — no Node Buffer dep.
  const enc = (globalThis as { btoa?: (s: string) => string }).btoa;
  if (!enc) {
    throw new Error("No base64 encoder (btoa) available in this runtime.");
  }
  return enc(bin).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

/**
 * Generate a cryptographically random `code_verifier` from the unreserved set,
 * 43–128 chars (RFC 7636 §4.1). Defaults to 64.
 */
export function generateCodeVerifier(length = 64, crypto?: CryptoProvider): string {
  if (length < 43 || length > 128) {
    throw new Error("code_verifier length must be in [43, 128]");
  }
  const c = resolveCrypto(crypto);
  const buf = new Uint8Array(length);
  c.getRandomValues(buf);
  let out = "";
  for (let i = 0; i < length; i++) out += UNRESERVED[buf[i]! % UNRESERVED.length];
  return out;
}

/** Compute the S256 `code_challenge` = BASE64URL(SHA256(verifier)). */
export async function deriveCodeChallenge(
  verifier: string,
  crypto?: CryptoProvider,
): Promise<string> {
  const c = resolveCrypto(crypto);
  const data = new TextEncoder().encode(verifier);
  const digest = await c.subtle.digest("SHA-256", data);
  return base64UrlEncode(new Uint8Array(digest));
}

/** Generate a full verifier + S256 challenge pair. */
export async function generatePkcePair(crypto?: CryptoProvider): Promise<PkcePair> {
  const verifier = generateCodeVerifier(64, crypto);
  const challenge = await deriveCodeChallenge(verifier, crypto);
  return { verifier, challenge, method: "S256" };
}

/** Generate a random URL-safe opaque string (for `state` / `nonce`). */
export function randomUrlToken(bytes = 32, crypto?: CryptoProvider): string {
  const c = resolveCrypto(crypto);
  const buf = new Uint8Array(bytes);
  c.getRandomValues(buf);
  return base64UrlEncode(buf);
}
