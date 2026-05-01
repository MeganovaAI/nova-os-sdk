"""Mode B custom tool — webhook (FastAPI) pattern.

In Mode B, Nova OS POSTs a signed JSON payload to the partner's webhook
endpoint whenever the agent calls a custom tool. The partner executes the
tool and returns the result in the HTTP response.

HMAC-SHA256 signature verification is handled by ``WebhookRouter``, which
also provides idempotency dedup (skips duplicate deliveries by event ID).

Setup:
  1. Run this server: ``uvicorn 05_custom_tool_webhook:app --port 8080``
  2. Register the agent + tool with Nova OS:
       ``NOVA_CB_URL=https://partner.example.com/nova/cb python 02_create_employee_and_agent.py``
  3. Nova OS will POST to ``/nova/cb/tools/fetch_invoice`` on each tool call.

Prerequisites::

    pip install nova-os-sdk fastapi uvicorn
    export NOVA_CB_SECRET=<your-webhook-secret-from-nova-os-dashboard>

Run::

    uvicorn 05_custom_tool_webhook:app --port 8080 --reload
"""

from __future__ import annotations

import os

from fastapi import FastAPI

# WebhookRouter handles HMAC-SHA256 verification + idempotency dedup.
# It is available via: from nova_os.callbacks import WebhookRouter
# (ships in the next SDK release; import shown here for documentation).
try:
    from nova_os.callbacks import WebhookRouter  # type: ignore[import]
except ImportError:
    # Graceful fallback: stub router for syntax-check / documentation purposes.
    class WebhookRouter:  # type: ignore[no-redef]
        """Stub — install nova-os-sdk>=1.0.0 for the real implementation."""

        def __init__(self, secret: str) -> None:
            self.secret = secret

        def tool(self, name: str):  # noqa: ANN202
            def decorator(fn):  # noqa: ANN202
                return fn
            return decorator

        def fastapi_router(self):  # noqa: ANN202
            from fastapi import APIRouter
            return APIRouter()


router = WebhookRouter(secret=os.environ.get("NOVA_CB_SECRET", "changeme"))


@router.tool("fetch_invoice")
async def fetch_invoice(input: dict, ctx: dict) -> str:
    """Return invoice details for the given invoice_id.

    ``input`` is the tool call's JSON input from the agent.
    ``ctx``   carries Nova OS metadata (agent_id, job_id, etc.).
    """
    invoice_id = input.get("invoice_id", "UNKNOWN")
    agent_id = ctx.get("agent_id", "?")
    # In production: query your DB / ERP here.
    result = f"Invoice {invoice_id}: status=paid, amount=$1,250.00"
    print(f"[fetch_invoice] agent={agent_id} invoice={invoice_id} → {result}")
    return result


@router.tool("check_eligibility")
async def check_eligibility(input: dict, ctx: dict) -> dict:
    """Check whether a client is eligible for a service.

    Returning a dict is fine — Nova OS serialises it to JSON automatically.
    """
    client_id = input.get("client_id", "UNKNOWN")
    return {"eligible": True, "reason": "All criteria met", "client_id": client_id}


# Mount on a FastAPI app — production deployments typically nest this under
# the main application router.
app = FastAPI(title="Partner Webhook Server")
app.include_router(router.fastapi_router(), prefix="/nova/cb")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
