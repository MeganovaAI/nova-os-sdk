/**
 * Tests for PKCE (RFC 7636) helpers — including the insecure-origin (HTTP)
 * crypto fallback where `crypto.subtle` is undefined.
 */
import { describe, it, expect, afterEach } from "vitest";
import { sha256 } from "@noble/hashes/sha2.js";
import {
  deriveCodeChallenge,
  generateCodeVerifier,
  type CryptoProvider,
} from "./pkce";

// ── RFC 7636 §4 S256 test vector ──────────────────────────────────────────────
// https://www.rfc-editor.org/rfc/rfc7636#appendix-B
const RFC_VERIFIER = "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk";
const RFC_CHALLENGE = "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM";

// Minimal CryptoProvider backed by noble sha256 (the "fallback" implementation)
const nobleSha256Subtle: Pick<SubtleCrypto, "digest"> = {
  digest: async (alg: string, data: ArrayBuffer | ArrayBufferView): Promise<ArrayBuffer> => {
    if (alg !== "SHA-256") throw new Error(`Unsupported algorithm: ${alg}`);
    const bytes = data instanceof Uint8Array ? data : new Uint8Array(data as ArrayBuffer);
    return sha256(bytes).buffer as ArrayBuffer;
  },
};

const fallbackProvider: CryptoProvider = {
  // Crypto.getRandomValues excludes null; cast through unknown to match CryptoProvider signature.
  getRandomValues: globalThis.crypto.getRandomValues.bind(
    globalThis.crypto,
  ) as unknown as CryptoProvider["getRandomValues"],
  subtle: nobleSha256Subtle,
};

// ── Save/restore globalThis.crypto ────────────────────────────────────────────
const realCrypto = globalThis.crypto;
afterEach(() => {
  Object.defineProperty(globalThis, "crypto", { value: realCrypto, configurable: true });
});

// ── Helper to install a stubbed globalThis.crypto that has getRandomValues
//    but NO subtle (simulates insecure origin / plain HTTP non-localhost)
function installInsecureOriginCrypto(): void {
  const stub = {
    getRandomValues: realCrypto.getRandomValues.bind(realCrypto),
    // subtle is explicitly absent (undefined)
  };
  Object.defineProperty(globalThis, "crypto", { value: stub, configurable: true });
}

// ─────────────────────────────────────────────────────────────────────────────

describe("RFC 7636 §4 S256 test vector — native Web Crypto", () => {
  it("deriveCodeChallenge produces the RFC-specified challenge using native crypto", async () => {
    const challenge = await deriveCodeChallenge(RFC_VERIFIER);
    expect(challenge).toBe(RFC_CHALLENGE);
  });
});

describe("RFC 7636 §4 S256 test vector — noble/hashes fallback path", () => {
  it("deriveCodeChallenge via explicit fallback CryptoProvider matches RFC vector", async () => {
    const challenge = await deriveCodeChallenge(RFC_VERIFIER, fallbackProvider);
    expect(challenge).toBe(RFC_CHALLENGE);
  });

  it("deriveCodeChallenge via insecure-origin globalThis (no subtle) matches RFC vector", async () => {
    installInsecureOriginCrypto();
    // After the fix, resolveCrypto() should detect getRandomValues-only and
    // synthesise the noble-sha256 subtle — producing the same RFC challenge.
    const challenge = await deriveCodeChallenge(RFC_VERIFIER);
    expect(challenge).toBe(RFC_CHALLENGE);
  });
});

describe("generateCodeVerifier — fallback getRandomValues", () => {
  it("returns a string of the requested length using the fallback provider", () => {
    const verifier = generateCodeVerifier(64, fallbackProvider);
    expect(verifier).toHaveLength(64);
  });

  it("returns a string of the requested length via insecure-origin globalThis", () => {
    installInsecureOriginCrypto();
    const verifier = generateCodeVerifier(64);
    expect(verifier).toHaveLength(64);
  });
});

describe("explicit CryptoProvider wins — no override", () => {
  it("uses the injected provider as-is (does not fall through to globalThis)", async () => {
    let digestCalled = false;
    const spy: CryptoProvider = {
      getRandomValues: realCrypto.getRandomValues.bind(
        realCrypto,
      ) as unknown as CryptoProvider["getRandomValues"],
      subtle: {
        digest: async (alg, data) => {
          digestCalled = true;
          return nobleSha256Subtle.digest(alg as string, data as ArrayBuffer);
        },
      },
    };
    await deriveCodeChallenge(RFC_VERIFIER, spy);
    expect(digestCalled).toBe(true);
  });
});

describe("resolveCrypto — no CSPRNG available → throws", () => {
  it("throws when globalThis.crypto has neither subtle nor getRandomValues", async () => {
    Object.defineProperty(globalThis, "crypto", { value: {}, configurable: true });
    await expect(deriveCodeChallenge(RFC_VERIFIER)).rejects.toThrow(
      /No Web Crypto|CSPRNG/i,
    );
  });
});
