"""Surface tests for the 6 new resource modules (#175-#179).

Uses httpx MockTransport so no live server is needed. Each test wires
a stub responder, calls the SDK method, and asserts the right path /
method / payload landed on the wire.
"""

from __future__ import annotations

import json

import httpx
import pytest

from nova_os import Client


def _make_client(handler) -> Client:
    """Construct a Client whose httpx transport routes to `handler`."""
    transport = httpx.MockTransport(handler)
    return Client(
        base_url="https://test.example.com",
        api_key="test-key",
        transport=transport,
    )


# ── Documents (#175) ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_documents_list_yields_paged_data():
    pages = iter([
        {"data": [{"id": "d1"}, {"id": "d2"}], "has_more": True, "next_cursor": "c1"},
        {"data": [{"id": "d3"}], "has_more": False},
    ])

    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "GET"
        assert req.url.path == "/v1/managed/documents"
        return httpx.Response(200, json=next(pages))

    async with _make_client(handler) as c:
        ids = [d["id"] async for d in c.documents.list()]
        assert ids == ["d1", "d2", "d3"]


@pytest.mark.asyncio
async def test_documents_upload_sends_multipart():
    captured = {}

    def handler(req: httpx.Request) -> httpx.Response:
        captured["method"] = req.method
        captured["path"] = req.url.path
        captured["content_type"] = req.headers.get("content-type", "")
        return httpx.Response(201, json={"id": "doc1", "title": "test.txt"})

    async with _make_client(handler) as c:
        result = await c.documents.upload(
            filename="test.txt",
            content=b"hello",
            collection_id="contracts",
        )
    assert captured["method"] == "POST"
    assert captured["path"] == "/v1/managed/documents/upload"
    assert "multipart/form-data" in captured["content_type"]
    assert result["id"] == "doc1"


@pytest.mark.asyncio
async def test_documents_delete_204():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "DELETE"
        assert req.url.path == "/v1/managed/documents/doc-x"
        return httpx.Response(204)

    async with _make_client(handler) as c:
        result = await c.documents.delete("doc-x")
    assert result is None


# ── Knowledge (#176) ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_knowledge_search_returns_data_array():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "POST"
        assert req.url.path == "/v1/managed/knowledge/search"
        body = json.loads(req.content)
        assert body == {"query": "contracts", "top_k": 5, "collection": "shared"}
        return httpx.Response(200, json={"data": [{"content": "hit"}]})

    async with _make_client(handler) as c:
        chunks = await c.knowledge.search(query="contracts", collection="shared")
    assert chunks == [{"content": "hit"}]


@pytest.mark.asyncio
async def test_knowledge_ingest():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "POST"
        assert req.url.path == "/v1/managed/knowledge/ingest"
        return httpx.Response(201, json={"status": "ingested"})

    async with _make_client(handler) as c:
        result = await c.knowledge.ingest(content="hello world")
    assert result["status"] == "ingested"


@pytest.mark.asyncio
async def test_knowledge_collections_returns_list():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.url.path == "/v1/managed/knowledge/collections"
        return httpx.Response(200, json={"data": ["a", "b", "c"]})

    async with _make_client(handler) as c:
        names = await c.knowledge.collections()
    assert names == ["a", "b", "c"]


# ── Hooks (#177) ────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_hooks_create_normalises_body():
    captured = {}

    def handler(req: httpx.Request) -> httpx.Response:
        captured["body"] = json.loads(req.content)
        return httpx.Response(201, json={"id": "h1", "event": "Stop", "target_url": "https://x", "enabled": True, "created_at": "2026-05-05T00:00:00Z"})

    async with _make_client(handler) as c:
        result = await c.hooks.create(
            event="Stop",
            target_url="https://x",
            secret_env="MY_SECRET",
        )
    assert captured["body"]["event"] == "Stop"
    assert captured["body"]["secret_env"] == "MY_SECRET"
    assert captured["body"]["enabled"] is True  # default
    assert result["id"] == "h1"


@pytest.mark.asyncio
async def test_hooks_delete_idempotent():
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(204)

    async with _make_client(handler) as c:
        # Should not raise even for a non-existent hook id.
        await c.hooks.delete("never-existed")


# ── Filesystem (#178) ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_filesystem_list():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "GET"
        assert req.url.path == "/v1/managed/filesystem/tenant-a/sess-1/files"
        return httpx.Response(200, json={"data": [{"path": "/workspace/x.md", "size": 5, "mtime": "2026-05-05T00:00:00Z"}], "has_more": False})

    async with _make_client(handler) as c:
        files = await c.filesystem.list(tenant_id="tenant-a", session_id="sess-1")
    assert len(files) == 1
    assert files[0]["path"] == "/workspace/x.md"


@pytest.mark.asyncio
async def test_filesystem_read_returns_bytes():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "GET"
        assert req.url.path == "/v1/managed/filesystem/t/s/files/workspace/notes.md"
        return httpx.Response(200, content=b"raw bytes here", headers={"Content-Type": "text/markdown"})

    async with _make_client(handler) as c:
        data = await c.filesystem.read(tenant_id="t", session_id="s", path="workspace/notes.md")
    assert data == b"raw bytes here"


@pytest.mark.asyncio
async def test_filesystem_write_sends_raw_body():
    captured = {}

    def handler(req: httpx.Request) -> httpx.Response:
        captured["method"] = req.method
        captured["path"] = req.url.path
        captured["body"] = req.content
        captured["content_type"] = req.headers.get("content-type")
        captured["if_match"] = req.headers.get("if-match")
        return httpx.Response(200, json={"path": "/workspace/x.md", "size": 5, "mtime": "2026-05-05T00:00:00Z"})

    async with _make_client(handler) as c:
        result = await c.filesystem.write(
            tenant_id="t",
            session_id="s",
            path="workspace/x.md",
            content=b"hello",
            content_type="text/plain",
            if_match="abc123",
        )
    assert captured["method"] == "PUT"
    assert captured["path"] == "/v1/managed/filesystem/t/s/files/workspace/x.md"
    assert captured["body"] == b"hello"
    assert captured["content_type"] == "text/plain"
    assert captured["if_match"] == "abc123"
    assert result["size"] == 5


# ── Users (#179) ────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_users_create_sends_role():
    def handler(req: httpx.Request) -> httpx.Response:
        body = json.loads(req.content)
        assert body == {"email": "x@y.com", "role": "manager", "name": "X"}
        return httpx.Response(201, json={"id": "u1", "email": "x@y.com", "role": "manager"})

    async with _make_client(handler) as c:
        result = await c.users.create(email="x@y.com", name="X", role="manager")
    assert result["id"] == "u1"


@pytest.mark.asyncio
async def test_users_list():
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"data": [{"id": "u1"}, {"id": "u2"}]})

    async with _make_client(handler) as c:
        users = await c.users.list()
    assert len(users) == 2


# ── Settings (#179) ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_settings_put_then_get():
    state: dict[str, str] = {}

    def handler(req: httpx.Request) -> httpx.Response:
        if req.method == "PUT":
            body = json.loads(req.content)
            key = req.url.path.rsplit("/", 1)[-1]
            state[key] = body["value"]
            return httpx.Response(200, json={"key": key, "value": body["value"]})
        if req.method == "GET":
            key = req.url.path.rsplit("/", 1)[-1]
            if key not in state:
                return httpx.Response(404, json={"type": "not_found_error", "message": "x"})
            return httpx.Response(200, json={"key": key, "value": state[key]})
        return httpx.Response(405)

    async with _make_client(handler) as c:
        await c.settings.put("answer_model", "anthropic/claude-opus-4-7")
        got = await c.settings.get("answer_model")
    assert got == "anthropic/claude-opus-4-7"


# ── Sessions (#185) ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_sessions_create_minimum():
    captured = {}

    def handler(req: httpx.Request) -> httpx.Response:
        captured["body"] = json.loads(req.content)
        return httpx.Response(201, json={"id": "sess_123", "agent_id": "intake-specialist", "environment_id": "", "created_at": "2026-05-05T00:00:00Z"})

    async with _make_client(handler) as c:
        s = await c.sessions.create(agent_id="intake-specialist")
    assert captured["body"] == {"agent_id": "intake-specialist"}
    assert s["id"] == "sess_123"


@pytest.mark.asyncio
async def test_sessions_create_with_model_override():
    captured = {}

    def handler(req: httpx.Request) -> httpx.Response:
        captured["body"] = json.loads(req.content)
        return httpx.Response(201, json={"id": "sess_456", "agent_id": "x", "model": "anthropic/claude-opus-4-7"})

    async with _make_client(handler) as c:
        await c.sessions.create(
            agent_id="x",
            environment_id="env_test",
            model="anthropic/claude-opus-4-7",
        )
    assert captured["body"]["model"] == "anthropic/claude-opus-4-7"
    assert captured["body"]["environment_id"] == "env_test"


@pytest.mark.asyncio
async def test_sessions_get():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "GET"
        assert req.url.path == "/v1/managed/sessions/sess_lookup"
        return httpx.Response(200, json={"id": "sess_lookup", "agent_id": "x"})

    async with _make_client(handler) as c:
        s = await c.sessions.get("sess_lookup")
    assert s["id"] == "sess_lookup"
