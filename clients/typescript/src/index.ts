/**
 * @meganova/nova-os-client — framework-agnostic TypeScript client kit for Nova OS.
 *
 * Three layers, mirroring the Python SDK split (generated types + hand-written
 * ergonomics):
 *  - generated REST types from `openapi/nova-os-partner.v1.yaml` (re-exported as `components`/`paths`);
 *  - an OIDC Auth-Code+PKCE+refresh helper (public-client, transport-agnostic);
 *  - AG-UI streaming event types + a typed SSE parser;
 *  - a thin {@link NovaClient} tying them together (Bearer + refresh-on-401).
 *
 * No React/framework dependencies — runs in browsers, Node 22, and React Native.
 */

// Convenience client + endpoint method types.
export {
  NovaClient,
  type NovaClientOptions,
  type MessageRequest,
  type MessageResponse,
  type JobCreate,
  type Job,
  type Document,
  type Session,
  type SessionCreate,
  type Deployment,
  type Agent,
} from "./client.js";

// Low-level REST factory (for advanced use / custom auth).
export {
  createRestClient,
  throwIfError,
  type RestClient,
  type RestClientOptions,
  type AuthProvider,
} from "./rest.js";

// Auth.
export {
  OidcClient,
  type OidcConfig,
  type PendingLogin,
} from "./auth/oidc.js";
export {
  generatePkcePair,
  generateCodeVerifier,
  deriveCodeChallenge,
  base64UrlEncode,
  randomUrlToken,
  type PkcePair,
  type CryptoProvider,
} from "./auth/pkce.js";
export {
  MemoryTokenStore,
  type TokenStore,
  type TokenSet,
} from "./auth/tokenStore.js";

// Streaming.
export {
  parseSse,
  parseAgUiStream,
  type SseFrame,
} from "./streaming/sse.js";
export type {
  AgUiEvent,
  AgUiEventType,
  RunStarted,
  RunFinished,
  RunError,
  TextMessageStart,
  TextMessageContent,
  TextMessageEnd,
  ReasoningMessageStart,
  ReasoningMessageContent,
  ReasoningMessageEnd,
  ToolCallStart,
  ToolCallArgs,
  ToolCallEnd,
  ToolCallResult,
  StateDelta,
  StateSnapshot,
  CustomEvent,
  RawEvent,
} from "./streaming/events.js";

// Errors.
export {
  NovaApiError,
  asNovaErrorBody,
  type NovaErrorBody,
  type NovaErrorType,
} from "./errors.js";

// Re-export generated OpenAPI types for advanced typing.
export type { components, paths, operations } from "./_generated/schema.js";
