"""Filesystem resource — /v1/managed/filesystem (#178, first slice).

Operates on already-provisioned workspaces. Provisioning happens at
agent-first-turn time today; partner-side provisioning is a follow-up.

Workspaces are scoped to ``(tenant_id, session_id)`` — partners running
multiple sessions per tenant (one per ticket / pipeline run / etc.)
keep that axis. Use the partner's stable internal IDs for both.
"""

from __future__ import annotations

from typing import Any

from nova_os.resources._base import Resource


class Filesystem(Resource):
    _PATH = "/v1/managed/filesystem"

    def _root(self, tenant_id: str, session_id: str) -> str:
        return f"{self._PATH}/{tenant_id}/{session_id}"

    async def list(
        self,
        *,
        tenant_id: str,
        session_id: str,
        mount: str = "/workspace",
        glob: str | None = None,
        recursive: bool = False,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """GET …/files — list files in a workspace mount.

        Returns FileMeta objects (path, size, mtime, content_type, sha256).
        """
        params: dict[str, Any] = {"mount": mount}
        if glob is not None:
            params["glob"] = glob
        if recursive:
            params["recursive"] = "1"
        if limit is not None:
            params["limit"] = limit
        resp = await self._client._request(
            "GET", f"{self._root(tenant_id, session_id)}/files", params=params
        )
        return (resp or {}).get("data", [])

    async def read(
        self,
        *,
        tenant_id: str,
        session_id: str,
        path: str,
    ) -> bytes:
        """GET …/files/{path} — return raw file bytes.

        ``path`` should NOT have a leading ``/``; the workspace mount
        prefix is implicit. Use ``/workspace/PLAN.md`` style internal
        paths in agent code; pass ``workspace/PLAN.md`` here.
        """
        return await self._client._request_bytes(
            "GET", f"{self._root(tenant_id, session_id)}/files/{path.lstrip('/')}"
        )

    async def write(
        self,
        *,
        tenant_id: str,
        session_id: str,
        path: str,
        content: bytes,
        content_type: str | None = None,
        if_match: str | None = None,
    ) -> dict[str, Any]:
        """PUT …/files/{path} — write/overwrite raw bytes.

        Pass ``if_match`` (SHA-256 hex of expected current content) for
        optimistic concurrency. Returns the post-write FileMeta.
        """
        headers: dict[str, str] = {}
        if content_type:
            headers["Content-Type"] = content_type
        if if_match:
            headers["If-Match"] = if_match
        return await self._client._request(
            "PUT",
            f"{self._root(tenant_id, session_id)}/files/{path.lstrip('/')}",
            raw_body=content,
            extra_headers=headers,
        )

    async def delete(
        self,
        *,
        tenant_id: str,
        session_id: str,
        path: str,
    ) -> None:
        """DELETE …/files/{path} — idempotent (always 204)."""
        await self._client._request(
            "DELETE", f"{self._root(tenant_id, session_id)}/files/{path.lstrip('/')}"
        )
