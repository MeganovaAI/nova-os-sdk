"""FastAPI integration for WebhookRouter.

Lazy import — fastapi is NOT a runtime dep of nova-os-sdk. Only loads
when partner code calls `router.fastapi_router()`.

Note: `from __future__ import annotations` is intentionally omitted here.
FastAPI resolves route-handler annotations via `typing.get_type_hints()` at
registration time. When PEP 563 (stringified annotations) is active AND the
annotated type is imported inside the factory function (not at module level),
FastAPI cannot resolve the string back to the class — it raises 422. Keeping
annotations evaluated (no `__future__` import) and importing `Request` at the
top of `build_router` (where it IS in scope for `get_type_hints`) solves this.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nova_os.callbacks import WebhookRouter


def build_router(wr: "WebhookRouter"):  # type: ignore[no-untyped-def]
    from fastapi import APIRouter, HTTPException
    from starlette.requests import Request

    api_router = APIRouter()

    # We must explicitly annotate with the imported class object, not a string.
    # Wrap in a closure that re-binds the annotation so FastAPI's type resolver
    # sees the live class in the function's __globals__ / closure.
    async def _handle(request: Request):  # type: ignore[no-untyped-def]
        body = await request.body()
        headers = dict(request.headers)
        try:
            return await wr.handle(body=body, headers=headers)
        except PermissionError as exc:
            raise HTTPException(status_code=401, detail=str(exc))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    # Force the annotation dict to hold the live class object so FastAPI's
    # get_type_hints() call resolves correctly regardless of PEP-563 mode.
    _handle.__annotations__ = {"request": Request}

    api_router.post("/")(_handle)
    return api_router


__all__ = ["build_router"]
