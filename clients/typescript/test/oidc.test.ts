import { describe, it, expect, afterEach } from "vitest";
import { OidcClient } from "../src/auth/oidc";

describe("OidcClient global fetch binding", () => {
  const realFetch = globalThis.fetch;
  afterEach(() => {
    globalThis.fetch = realFetch;
  });

  it("calls the global fetch with the global receiver (regression: Illegal invocation)", async () => {
    // Browsers throw "TypeError: Failed to execute 'fetch' on 'Window':
    // Illegal invocation" when window.fetch is called with a receiver other
    // than window — which is exactly what `this.fetchImpl(...)` did before the
    // fallback was bound. Emulate that strictness here.
    const strict = function (this: unknown) {
      if (this !== undefined && this !== globalThis) {
        throw new TypeError("Failed to execute 'fetch' on 'Window': Illegal invocation");
      }
      return Promise.resolve(
        new Response(
          JSON.stringify({ access_token: "tok", token_type: "Bearer", expires_in: 3600 }),
          { status: 200, headers: { "content-type": "application/json" } },
        ),
      );
    };
    globalThis.fetch = strict as unknown as typeof fetch;

    const client = new OidcClient({
      issuer: "https://idp.example.com",
      clientId: "app",
      redirectUri: "https://app.example.com/cb",
    });

    const tokens = await (
      client as unknown as { exchange(b: URLSearchParams): Promise<{ accessToken: string }> }
    ).exchange(new URLSearchParams({ grant_type: "authorization_code" }));

    expect(tokens.accessToken).toBe("tok");
  });
});
