/**
 * PKCE (RFC 7636) S256 helpers — transport-agnostic.
 *
 * Uses Web Crypto (`crypto.subtle` + `crypto.getRandomValues`), which is global
 * in browsers, Node 18+, and React Native (with a polyfill). The crypto provider
 * is injectable so the same core runs everywhere; defaults to `globalThis.crypto`.
 *
 * Insecure-origin (plain HTTP, non-localhost) fallback: browsers expose
 * `crypto.getRandomValues` on all origins but restrict `crypto.subtle` to secure
 * contexts (HTTPS / localhost). When `subtle` is absent but `getRandomValues` IS
 * present, `resolveCrypto` constructs a fallback provider that uses @noble/hashes
 * for the SHA-256 digest so PKCE sign-in works on internal-IP HTTP deployments.
 */

export interface CryptoProvider {
  getRandomValues<T extends ArrayBufferView | null>(array: T): T;
  subtle: Pick<SubtleCrypto, "digest">;
}

/**
 * Build a minimal `subtle` shim backed by @noble/hashes sha256.
 * Only "SHA-256" is supported — the sole algorithm PKCE requires.
 */
async function _nobleDigest(alg: AlgorithmIdentifier, data: BufferSource): Promise<ArrayBuffer> {
  const name = typeof alg === "string" ? alg : alg.name;
  if (name !== "SHA-256") throw new Error(`PKCE fallback only supports SHA-256, got: ${name}`);
  const { sha256 } = await import("@noble/hashes/sha256");
  const bytes = data instanceof Uint8Array ? data : new Uint8Array(data as ArrayBuffer);
  return sha256(bytes).buffer as ArrayBuffer;
}

function resolveCrypto(provided?: CryptoProvider): CryptoProvider {
  // Explicit injection always wins unchanged — no override.
  if (provided !== undefined) return provided;

  const g = (globalThis as { crypto?: Crypto }).crypto;

  // Full Web Crypto available (HTTPS / localhost, Node 18+).
  if (g?.subtle && typeof g.getRandomValues === "function") {
    return g as unknown as CryptoProvider;
  }

  // Insecure-origin (plain HTTP, non-localhost): subtle is undefined but
  // getRandomValues is still present — use @noble/hashes as SHA-256 fallback.
  if (g && typeof g.getRandomValues === "function") {
    // Crypto.getRandomValues excludes null in its signature but CryptoProvider
    // includes it for flexibility; cast through unknown to satisfy both.
    const getRV = g.getRandomValues.bind(g) as unknown as CryptoProvider["getRandomValues"];
    return {
      getRandomValues: getRV,
      subtle: { digest: _nobleDigest },
    };
  }

  // No CSPRNG at all — cannot safely generate a verifier.
  throw new Error(
    "No Web Crypto available. Pass a CryptoProvider (e.g. a polyfill) to the PKCE helper.",
  );
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
