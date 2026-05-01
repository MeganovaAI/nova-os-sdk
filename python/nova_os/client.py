"""Public Client class — partner-facing entry point.

Wraps an httpx.AsyncClient with bearer-token auth, structured error
parsing, and the resource dispatchers. Long-lived singleton is the
documented default (matches Anthropic/OpenAI/Stripe SDK convention);
context-manager usage is also supported for scripts/tests.
"""

from __future__ import annotations

from typing import Any, Optional

import httpx

from nova_os.errors import parse_error_response
from nova_os._retry import RetryConfig
from nova_os._version import __version__, OPENAPI_VERSION


_DEFAULT_TIMEOUT_SEC = 30.0


class Client:
    """Public Nova OS SDK client.

    Args:
        base_url: Nova OS server URL (e.g. https://nova.partner.com).
        api_key: HS256 JWT bearer (partner-self-hosted) or msk_live_... (cloud).
        timeout: Per-request timeout in seconds. Default 30.
        transport: Optional httpx.AsyncBaseTransport — useful for tests.
        retry_config: RetryConfig for idempotent-verb auto-retry.
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        *,
        timeout: float = _DEFAULT_TIMEOUT_SEC,
        transport: httpx.AsyncBaseTransport | None = None,
        retry_config: RetryConfig | None = None,
    ) -> None:
        if not base_url:
            raise ValueError("base_url is required")
        if not api_key:
            raise ValueError("api_key is required")
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout = timeout
        self._retry_config = retry_config or RetryConfig()
        self._http = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=timeout,
            transport=transport,
            headers={
                "Authorization": f"Bearer {api_key}",
                "X-Nova-SDK-Version": __version__,
                "X-Nova-OpenAPI-Hash": OPENAPI_VERSION,
                "Accept": "application/json",
            },
        )
        self._closed = False

        # Lazy-import resources to avoid circular import at module load.
        from nova_os.resources.agents import Agents
        from nova_os.resources.employees import Employees
        from nova_os.resources.messages import Messages
        from nova_os.resources.jobs import Jobs

        self.agents = Agents(self)
        self.employees = Employees(self)
        self.messages = Messages(self)
        self.jobs = Jobs(self)

        # .sync proxy — wired in Task 9
        from nova_os._sync import _SyncProxy
        self.sync = _SyncProxy(self)

    async def __aenter__(self) -> "Client":
        return self

    async def __aexit__(self, *exc_info: Any) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if self._closed:
            return
        self._closed = True
        await self._http.aclose()

    # Internal: low-level request helper — resources delegate here.
    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: Any | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> Any:
        merged_headers = dict(headers or {})
        if idempotency_key is not None:
            merged_headers["Idempotency-Key"] = idempotency_key
        try:
            resp = await self._http.request(
                method,
                path,
                params=params,
                json=json_body,
                headers=merged_headers,
            )
        except httpx.HTTPError as exc:
            # Network-level — let caller decide via with_retry whether to retry.
            raise

        if 200 <= resp.status_code < 300:
            if resp.status_code == 204 or not resp.content:
                return None
            try:
                return resp.json()
            except ValueError:
                return resp.text

        # Error path — parse to typed exception.
        body: Any
        try:
            body = resp.json()
        except ValueError:
            body = resp.text
        raise parse_error_response(resp.status_code, body)
