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
        from nova_os.resources.documents import Documents
        from nova_os.resources.knowledge import Knowledge
        from nova_os.resources.hooks import Hooks
        from nova_os.resources.filesystem import Filesystem
        from nova_os.resources.users import Users
        from nova_os.resources.settings import Settings

        self.agents = Agents(self)
        self.employees = Employees(self)
        self.messages = Messages(self)
        self.jobs = Jobs(self)
        # New resources landed alongside server PRs #189–#193 / OpenAPI alpha.3.
        self.documents = Documents(self)
        self.knowledge = Knowledge(self)
        self.hooks = Hooks(self)
        self.filesystem = Filesystem(self)
        self.users = Users(self)
        self.settings = Settings(self)

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
        files: dict[str, Any] | None = None,
        form: dict[str, Any] | None = None,
        raw_body: bytes | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> Any:
        """Low-level transport. Mutually-exclusive body modes:

        - ``json_body`` — typical JSON request (most resources)
        - ``files`` + optional ``form`` — multipart upload (Documents.upload)
        - ``raw_body`` — application/octet-stream PUT (Filesystem.write)
        """
        merged_headers = dict(headers or {})
        if extra_headers:
            merged_headers.update(extra_headers)
        if idempotency_key is not None:
            merged_headers["Idempotency-Key"] = idempotency_key
        try:
            kwargs: dict[str, Any] = {"params": params, "headers": merged_headers}
            if files is not None:
                kwargs["files"] = files
                if form:
                    kwargs["data"] = form
            elif raw_body is not None:
                kwargs["content"] = raw_body
            elif json_body is not None:
                kwargs["json"] = json_body
            resp = await self._http.request(method, path, **kwargs)
        except httpx.HTTPError:
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

    async def _request_bytes(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> bytes:
        """Like ``_request`` but returns raw response bytes — for
        endpoints that stream files (e.g. Filesystem.read).
        """
        merged_headers = dict(extra_headers or {})
        try:
            resp = await self._http.request(
                method, path, params=params, headers=merged_headers
            )
        except httpx.HTTPError:
            raise

        if 200 <= resp.status_code < 300:
            return resp.content

        body: Any
        try:
            body = resp.json()
        except ValueError:
            body = resp.text
        raise parse_error_response(resp.status_code, body)
