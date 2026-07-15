"""LibraAdk — control-plane + data-plane client.

``deploy`` writes the agent to ``/v1/agents``; ``run`` executes it on the
LibraOS managed runtime and streams events. v1 targets the durable jobs surface
(works today); the exact wire shapes are the documented mapping
(docs/design/agent-sdk-rfc.md §5) — confirm against the server before GA.
"""

from __future__ import annotations

import json
import os
from typing import Any, Callable, Iterator, Optional

import httpx

from .agent import Agent

RunEvent = dict[str, Any]


def _env(*keys: str) -> Optional[str]:
    for k in keys:
        v = os.environ.get(k)
        if v:
            return v
    return None


class LibraAdk:
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None) -> None:
        base_url = base_url or _env("LIBRAOS_BASE_URL", "NOVA_OS_BASE_URL")
        api_key = api_key or _env("LIBRAOS_API_KEY", "NOVA_OS_API_KEY")
        if not base_url:
            raise ValueError("LibraAdk: base_url (or $LIBRAOS_BASE_URL) is required")
        if not api_key:
            raise ValueError("LibraAdk: api_key (or $LIBRAOS_API_KEY) is required")
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def _headers(self) -> dict[str, str]:
        return {"authorization": f"Bearer {self.api_key}", "content-type": "application/json"}

    def deploy(self, agent: Agent) -> dict[str, Any]:
        """Create or update the agent (``PUT /v1/agents/:name``, upsert). Idempotent."""
        with httpx.Client() as c:
            r = c.put(
                f"{self.base_url}/v1/agents/{agent.name}",
                headers=self._headers(),
                json=agent.to_managed_agent_body(),
            )
            if r.status_code >= 400:
                raise RuntimeError(f"deploy {agent.name}: {r.status_code} {r.text}")
            data = r.json() if r.content else {}
            out: dict[str, Any] = {"id": data.get("id", agent.name)}
            if "etag" in data:
                out["etag"] = data["etag"]
            return out

    def run(
        self,
        agent_name: str,
        message: str,
        on_event: Optional[Callable[[RunEvent], None]] = None,
    ) -> list[RunEvent]:
        """Run an agent on the LibraOS stack and stream its events.

        Targets the durable jobs surface (``POST /agents/v1/:key/jobs`` +
        ``…/jobs/:id/stream``). Once the P0 seam lands (libraos/libraos#840/#841)
        this can move to the session surface for full Managed-Agents compat.
        """
        events: list[RunEvent] = []
        with httpx.Client(timeout=None) as c:
            r = c.post(
                f"{self.base_url}/agents/v1/{self.api_key}/jobs",
                headers=self._headers(),
                json={"agent": agent_name, "message": message},
            )
            if r.status_code >= 400:
                raise RuntimeError(f"run {agent_name}: submit {r.status_code} {r.text}")
            job_id = r.json().get("job_id")
            if not job_id:
                raise RuntimeError(f"run {agent_name}: server did not return a job_id")
            with c.stream(
                "GET",
                f"{self.base_url}/agents/v1/{self.api_key}/jobs/{job_id}/stream",
                headers={"authorization": f"Bearer {self.api_key}", "accept": "text/event-stream"},
            ) as s:
                for ev in _iter_sse(s):
                    events.append(ev)
                    if on_event:
                        on_event(ev)
        return events


def _iter_sse(resp: "httpx.Response") -> Iterator[RunEvent]:
    buf = ""
    for chunk in resp.iter_text():
        buf += chunk
        while "\n\n" in buf:
            frame, buf = buf.split("\n\n", 1)
            ev = _frame_to_event(frame)
            if ev is not None:
                yield ev


def _frame_to_event(frame: str) -> Optional[RunEvent]:
    etype = "message"
    data: list[str] = []
    for line in frame.split("\n"):
        if line.startswith("event:"):
            etype = line[6:].strip()
        elif line.startswith("data:"):
            data.append(line[5:].strip())
    if not data:
        return None
    raw = "\n".join(data)
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {"type": etype, "data": raw}
    if isinstance(parsed, dict):
        parsed.setdefault("type", etype)
        return parsed
    return {"type": etype, "data": parsed}
