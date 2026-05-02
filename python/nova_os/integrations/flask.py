"""Flask integration for WebhookRouter.

Lazy import — flask is NOT a runtime dep. Bridges the async handler
to Flask's sync request model via asyncio.run() — single-request,
no event-loop concerns since each Flask request runs in its own thread.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nova_os.callbacks import WebhookRouter


def build_blueprint(wr: "WebhookRouter", name: str = "nova_callbacks"):  # type: ignore[no-untyped-def]
    from flask import Blueprint, Response, jsonify, request

    bp = Blueprint(name, __name__)

    @bp.route("/", methods=["POST"], strict_slashes=False)
    def handle():
        body = request.get_data() or b""
        headers = dict(request.headers)
        try:
            result = asyncio.run(wr.handle(body=body, headers=headers))
        except PermissionError as exc:
            return Response(str(exc), status=401)
        except ValueError as exc:
            return Response(str(exc), status=400)
        return jsonify(result)

    return bp


__all__ = ["build_blueprint"]
