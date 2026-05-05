"""Users resource — /v1/managed/users (#179)."""

from __future__ import annotations

from typing import Any, Literal

from nova_os.resources._base import Resource


UserRole = Literal["admin", "manager", "developer", "employee"]


class Users(Resource):
    _PATH = "/v1/managed/users"

    async def create(
        self,
        *,
        email: str,
        name: str | None = None,
        role: UserRole = "employee",
    ) -> dict[str, Any]:
        """POST /v1/managed/users — create a user with default password.

        The created user is flagged ``must_change_password=true``.
        Trigger a password reset on first sign-in or hand the user an
        out-of-band reset link.
        """
        body: dict[str, Any] = {"email": email, "role": role}
        if name is not None:
            body["name"] = name
        return await self._client._request("POST", self._PATH, json_body=body)

    async def get(self, user_id: str) -> dict[str, Any]:
        """GET /v1/managed/users/{id}."""
        return await self._client._request("GET", f"{self._PATH}/{user_id}")

    async def delete(self, user_id: str) -> None:
        """DELETE /v1/managed/users/{id}."""
        await self._client._request("DELETE", f"{self._PATH}/{user_id}")

    async def list(self) -> list[dict[str, Any]]:
        """GET /v1/managed/users — return every user."""
        resp = await self._client._request("GET", self._PATH)
        return (resp or {}).get("data", [])
