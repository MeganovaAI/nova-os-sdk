"""Personas resource — /agents/v1/personas (#187 server / nova-os-sdk#14).

Boot-time persona discovery — partners cache the manifest by
``manifest_version`` and use ``If-None-Match`` to skip the body when
unchanged. Stops partners from mirroring nova-os YAML in their own
code: every persona's resolved triage mode + emitted route-hint kinds
+ route-template names are exposed in one envelope.

Path note: this resource lives under ``/agents/v1/...``, not the
``/v1/managed/...`` partner prefix used by the wrappers. That's the
existing legacy mount for the personas runtime; partners hit the same
URL the dashboard does.
"""

from __future__ import annotations

from typing import Any

from nova_os.errors import PersonaNotFound, NotFoundError
from nova_os.resources._base import Resource


class Personas(Resource):
    _PATH = "/agents/v1/personas"

    async def list(self, *, if_none_match: str | None = None) -> dict[str, Any] | None:
        """GET /agents/v1/personas — return the persona manifest.

        ``if_none_match`` accepts a previously-cached ``manifest_version``
        (the ``ETag`` value from a prior fetch). When the manifest hasn't
        changed since that version, the server replies 304 and this method
        returns ``None`` — partner can keep its cached copy. On 200,
        returns the manifest dict ``{manifest_version, personas[]}``.
        """
        headers: dict[str, str] = {}
        if if_none_match is not None:
            headers["If-None-Match"] = if_none_match
        return await self._client._request(
            "GET", self._PATH, extra_headers=headers
        )

    async def get(self, persona_id: str) -> dict[str, Any]:
        """GET /agents/v1/personas/{id} — fetch one persona.

        Raises ``PersonaNotFound`` (subclass of ``NotFoundError``) on
        404 with the requested id preserved on ``.persona_id`` so callers
        can re-resolve without parsing the URL.
        """
        try:
            return await self._client._request("GET", f"{self._PATH}/{persona_id}")
        except NotFoundError as exc:
            # The personas endpoint uses a distinct error envelope
            # ({"error": "...", "id": "..."}) that doesn't fit the
            # standard parse_error_response shape — promote to the
            # typed exception here so callers get a stable contract.
            raise PersonaNotFound(persona_id, str(exc) or "persona not found") from exc
