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
from nova_os._retry import RetryConfig, with_retry
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
        from nova_os.resources.sessions import Sessions
        from nova_os.resources.personas import Personas

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
        self.sessions = Sessions(self)
        # alpha.5 — boot-time persona discovery (#187 / nova-os-sdk#14).
        self.personas = Personas(self)

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
        kwargs: dict[str, Any] = {"params": params, "headers": merged_headers}
        if files is not None:
            kwargs["files"] = files
            if form:
                kwargs["data"] = form
        elif raw_body is not None:
            kwargs["content"] = raw_body
        elif json_body is not None:
            kwargs["json"] = json_body

        async def send_once() -> httpx.Response:
            response = await self._http.request(method, path, **kwargs)
            if method.upper() in {"GET", "PUT", "DELETE"} and 500 <= response.status_code < 600:
                response.raise_for_status()
            return response

        try:
            if method.upper() in {"GET", "PUT", "DELETE"}:
                resp = await with_retry(send_once, self._retry_config)
            else:
                resp = await self._http.request(method, path, **kwargs)
        except httpx.HTTPStatusError as exc:
            resp = exc.response
        except httpx.HTTPError:
            raise

        if 200 <= resp.status_code < 300:
            if resp.status_code == 204 or not resp.content:
                return None
            try:
                return resp.json()
            except ValueError:
                return resp.text

        # 304 Not Modified — cache-validation success. No body. Surface
        # as None so callers using If-None-Match can short-circuit:
        #     manifest = await c.personas.list(if_none_match=etag)
        #     if manifest is None: # cached version still current
        if resp.status_code == 304:
            return None

        # Error path — parse to typed exception.
        body: Any
        try:
            body = resp.json()
        except ValueError:
            body = resp.text
        raise parse_error_response(resp.status_code, body)

    # ----- Synthetic-customer simulator surface (Track 1.3 / 1.4 / 1.5) -----

    def simulate(
        self,
        target_agent_id: str,
        archetype: Any,
        *,
        stream: bool = False,
        **kwargs: Any,
    ) -> Any:
        """Run a synthetic-customer simulation. Sync surface.

        See :func:`nova_os.simulator.simulate` for the full signature
        and contract. This shortcut binds ``self`` as the client so
        partners call ``c.simulate(target_id, archetype)`` directly.

        Default (``stream=False``) returns a
        :class:`~nova_os.simulator.SimulationResult`.

        When ``stream=True``, returns a sync
        :class:`~typing.Iterator` of
        :class:`~nova_os.simulator.TurnEvent` — one event per turn
        plus a final ``outcome`` event. The outcome event always
        fires, even on error / timeout / cancellation paths.
        """
        if stream:
            from nova_os.simulator.simulate import simulate_stream

            return simulate_stream(self, target_agent_id, archetype, **kwargs)

        from nova_os.simulator.simulate import simulate as _simulate

        return _simulate(self, target_agent_id, archetype, **kwargs)

    def async_simulate(
        self,
        target_agent_id: str,
        archetype: Any,
        *,
        stream: bool = False,
        **kwargs: Any,
    ) -> Any:
        """Async variant of :meth:`simulate`.

        Default (``stream=False``) returns a coroutine resolving to a
        :class:`~nova_os.simulator.SimulationResult` — ``await`` it.

        When ``stream=True``, returns an
        :class:`~typing.AsyncIterator` of
        :class:`~nova_os.simulator.TurnEvent` — iterate with
        ``async for``. Same outcome-always-emitted contract as the
        sync streaming surface.

        Note: this method is intentionally NOT ``async def`` — the
        ``stream=True`` path needs to hand back the async iterator
        directly without going through one extra ``await`` layer.
        Callers of the non-streaming path do ``await
        c.async_simulate(...)`` exactly as before.
        """
        if stream:
            from nova_os.simulator.simulate import async_simulate_stream

            return async_simulate_stream(
                self, target_agent_id, archetype, **kwargs
            )

        from nova_os.simulator.simulate import async_simulate as _async_simulate

        return _async_simulate(self, target_agent_id, archetype, **kwargs)

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
