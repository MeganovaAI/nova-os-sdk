import { describe, it, expect, afterEach } from "vitest";
import { NovaClient } from "../client";
import { OidcClient } from "./oidc";

/**
 * Regression for the "Illegal invocation" bug: when the kit resolves the global
 * `fetch` it must bind it to `globalThis`. A bare `window.fetch` reference called
 * detached (`const f = globalThis.fetch; f(...)`) runs with `this === undefined`,
 * and browsers throw `TypeError: Failed to execute 'fetch' on 'Window': Illegal
 * invocation`. Node's fetch doesn't enforce this, so we install a strict stand-in
 * that mimics the browser: it rejects unless invoked with `this === globalThis`.
 */
const realFetch = globalThis.fetch;
afterEach(() => {
  globalThis.fetch = realFetch;
});

function installStrictFetch(response: Response): void {
  const strict = function (this: unknown): Promise<Response> {
    if (this !== globalThis) {
      return Promise.reject(
        new TypeError("Failed to execute 'fetch' on 'Window': Illegal invocation"),
      );
    }
    return Promise.resolve(response);
  };
  globalThis.fetch = strict as unknown as typeof fetch;
}

const auth = { getAccessToken: async () => "tok" };

describe("global fetch is bound to globalThis", () => {
  it("NovaClient routes through fetch with the window receiver (rawFetch)", async () => {
    installStrictFetch(
      new Response(JSON.stringify({ text: "ok" }), {
        status: 200,
        headers: { "content-type": "application/json" },
      }),
    );
    const client = new NovaClient({ baseUrl: "http://x", auth });
    await expect(
      client.transcribeAudio(new Blob(["a"], { type: "audio/webm" })),
    ).resolves.toEqual({ text: "ok" });
  });

  it("OidcClient token exchange calls fetch with the window receiver", async () => {
    installStrictFetch(
      new Response(JSON.stringify({ access_token: "a", token_type: "Bearer", expires_in: 3600 }), {
        status: 200,
        headers: { "content-type": "application/json" },
      }),
    );
    const oidc = new OidcClient({ issuer: "http://x", clientId: "c", redirectUri: "http://x" });
    const exchange = (oidc as unknown as { exchange: (b: URLSearchParams) => Promise<unknown> })
      .exchange;
    await expect(
      exchange.call(oidc, new URLSearchParams({ grant_type: "authorization_code" })),
    ).resolves.toBeTruthy();
  });
});
