import { describe, it, expect } from "vitest";
import {
  generateCodeVerifier,
  deriveCodeChallenge,
  generatePkcePair,
  base64UrlEncode,
} from "../src/auth/pkce.js";

describe("pkce", () => {
  it("generates a verifier in the legal length + charset", () => {
    const v = generateCodeVerifier(64);
    expect(v).toHaveLength(64);
    expect(v).toMatch(/^[A-Za-z0-9\-._~]+$/);
  });

  it("rejects out-of-range verifier lengths", () => {
    expect(() => generateCodeVerifier(10)).toThrow();
    expect(() => generateCodeVerifier(200)).toThrow();
  });

  it("derives a deterministic S256 challenge (RFC 7636 test vector)", async () => {
    // RFC 7636 Appendix B verifier → challenge.
    const verifier = "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk";
    const challenge = await deriveCodeChallenge(verifier);
    expect(challenge).toBe("E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM");
  });

  it("base64url has no padding or url-unsafe chars", () => {
    const enc = base64UrlEncode(new Uint8Array([251, 255, 191]));
    expect(enc).not.toMatch(/[+/=]/);
  });

  it("generatePkcePair returns a matching verifier/challenge", async () => {
    const pair = await generatePkcePair();
    expect(pair.method).toBe("S256");
    expect(await deriveCodeChallenge(pair.verifier)).toBe(pair.challenge);
  });
});
