"""Knowledge resource — /v1/managed/knowledge (#176)."""

from __future__ import annotations

from typing import Any

from nova_os.resources._base import Resource


class Knowledge(Resource):
    """Hybrid search + ingest for Nova OS knowledge collections.

    Collections are scoped via the partner's API-key auth; partners
    cannot read other tenants' collections regardless of name. ``search``
    defaults to the caller's own collection when ``collection`` is unset.
    """

    _PATH = "/v1/managed/knowledge"

    async def search(
        self,
        *,
        query: str,
        collection: str | None = None,
        top_k: int = 5,
        threshold: float = 0.0,
    ) -> list[dict[str, Any]]:
        """POST /v1/managed/knowledge/search — hybrid search.

        Returns the ranked passages list. Each passage has at minimum
        ``content`` and ``score``; extra fields (``document_id``,
        ``collection``, ``metadata``) populate when known.
        """
        body: dict[str, Any] = {"query": query, "top_k": top_k}
        if collection is not None:
            body["collection"] = collection
        if threshold:
            body["threshold"] = threshold
        resp = await self._client._request(
            "POST", f"{self._PATH}/search", json_body=body
        )
        return (resp or {}).get("data", [])

    async def ingest(
        self,
        *,
        content: str,
        title: str | None = None,
        collection: str = "default",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """POST /v1/managed/knowledge/ingest — index a single document."""
        body: dict[str, Any] = {"content": content, "collection": collection}
        if title is not None:
            body["title"] = title
        if metadata is not None:
            body["metadata"] = metadata
        return await self._client._request(
            "POST", f"{self._PATH}/ingest", json_body=body
        )

    async def collections(self) -> list[str]:
        """GET /v1/managed/knowledge/collections — list every collection name."""
        resp = await self._client._request("GET", f"{self._PATH}/collections")
        return (resp or {}).get("data", [])
