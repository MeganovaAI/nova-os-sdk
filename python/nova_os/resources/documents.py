"""Documents resource — /v1/managed/documents (#175)."""

from __future__ import annotations

from typing import Any, AsyncIterator, BinaryIO

from nova_os.resources._base import Resource


class Documents(Resource):
    """Upload, list, and delete documents on a Nova OS instance.

    Documents are auto-indexed by Super Nova on upload; partners typically
    upload once and reference resulting `document_id` values from agent
    skills (knowledge_search etc.) thereafter.
    """

    _PATH = "/v1/managed/documents"

    async def upload(
        self,
        *,
        filename: str,
        content: bytes | BinaryIO,
        collection_id: str | None = None,
        content_type: str | None = None,
    ) -> dict[str, Any]:
        """POST /v1/managed/documents/upload — multipart upload.

        ``content`` may be raw bytes or any binary file-like object
        (e.g. ``open(path, 'rb')``). The server returns the created
        Document; ``id`` is the value to reference in agent calls.
        """
        if hasattr(content, "read"):
            data = content.read()  # type: ignore[union-attr]
        else:
            data = content
        files = {"file": (filename, data, content_type or "application/octet-stream")}
        form: dict[str, Any] = {}
        if collection_id is not None:
            form["collection_id"] = collection_id
        return await self._client._request(
            "POST",
            f"{self._PATH}/upload",
            files=files,
            form=form,
        )

    async def delete(self, document_id: str) -> None:
        """DELETE /v1/managed/documents/{document_id}."""
        await self._client._request("DELETE", f"{self._PATH}/{document_id}")

    async def list(
        self,
        *,
        collection_id: str | None = None,
        limit: int | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """GET /v1/managed/documents — async-iterator auto-paginating list.

        Yields one Document per iteration. Pass ``collection_id`` to
        scope to a single collection; omit for the root collection.
        """
        params: dict[str, Any] = {}
        if collection_id is not None:
            params["collection_id"] = collection_id
        if limit is not None:
            params["limit"] = limit

        current_cursor: str | None = None
        while True:
            page_params = dict(params)
            if current_cursor:
                page_params["cursor"] = current_cursor
            page = await self._client._request("GET", self._PATH, params=page_params)
            for item in (page or {}).get("data", []):
                yield item
            if not (page or {}).get("has_more"):
                return
            current_cursor = page.get("next_cursor")
            if not current_cursor:
                return
