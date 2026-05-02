"""Legaltech — partner-side webhook server hosting the precedent-lookup tool.

Pairs with `contract_clause_extraction.py`. Every time the agent calls the
`lookup_clause_precedent` tool, Nova OS POSTs a signed JSON payload here.
The HMAC-SHA256 signature is verified by `WebhookRouter` before the handler
runs.

In production: replace the in-memory `_PRECEDENT_DB` lookup with a real
query against your clause database (Postgres + pgvector, OpenSearch, or
whatever your legal-tech stack uses). The handler signature is unchanged.

Prerequisites::

    pip install nova-os-sdk fastapi uvicorn
    export NOVA_CB_SECRET=<copy from Nova OS dashboard or generate locally>

Run::

    uvicorn webhook_server:app --port 8080 --reload
"""

from __future__ import annotations

import os

from fastapi import FastAPI

try:
    from nova_os.callbacks import WebhookRouter
except ImportError:
    # Fallback so this file is at least syntax-checkable in environments
    # where the real WebhookRouter isn't installed yet.
    from fastapi import APIRouter

    class WebhookRouter:  # type: ignore[no-redef]
        def __init__(self, secret: str) -> None:
            self.secret = secret

        def tool(self, name: str):  # noqa: ANN202
            def decorator(fn):  # noqa: ANN202
                return fn
            return decorator

        def fastapi_router(self) -> APIRouter:
            return APIRouter()


# Toy in-memory precedent DB. Replace with your real lookup.
# Keys are normalised clause types; values are (canonical_text, similarity_threshold).
_PRECEDENT_DB: dict[str, tuple[str, float]] = {
    "limitation_of_liability": (
        "In no event shall either party be liable for any indirect, incidental, "
        "special, or consequential damages arising out of or related to this Agreement.",
        0.85,
    ),
    "indemnification": (
        "Each party shall indemnify, defend, and hold harmless the other party from "
        "and against any third-party claims arising from the indemnifying party's "
        "breach of this Agreement.",
        0.80,
    ),
    "termination": (
        "Either party may terminate this Agreement for material breach upon thirty "
        "(30) days' written notice if the breach remains uncured.",
        0.75,
    ),
    "confidentiality": (
        "Each party shall protect the other's Confidential Information using at "
        "least the same degree of care it uses to protect its own confidential "
        "information of like kind, but in no event less than reasonable care.",
        0.80,
    ),
}


def _cosine_like_score(a: str, b: str) -> float:
    """Toy similarity: token-overlap Jaccard. Replace with embeddings in prod."""
    sa = set(a.lower().split())
    sb = set(b.lower().split())
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


router = WebhookRouter(secret=os.environ.get("NOVA_CB_SECRET", "changeme"))


@router.tool("lookup_clause_precedent")
async def lookup_clause_precedent(input: dict, ctx: dict) -> dict:
    """Score a clause against the partner's precedent corpus.

    Returns a dict with a similarity score in [0, 1] and the canonical
    precedent text. The agent uses these to decide whether the clause is
    materially out of line with the partner's standard playbook.
    """
    clause_text = input.get("clause_text", "")
    clause_type = input.get("clause_type", "other").lower().replace(" ", "_")

    canonical, threshold = _PRECEDENT_DB.get(clause_type, ("", 0.0))
    score = _cosine_like_score(clause_text, canonical) if canonical else 0.0

    return {
        "score": round(score, 3),
        "canonical_precedent": canonical or None,
        "threshold": threshold,
        "below_threshold": canonical != "" and score < threshold,
        "agent_id": ctx.get("agent_id"),
    }


app = FastAPI(title="Legaltech precedent-lookup webhook")
app.include_router(router.fastapi_router(), prefix="/nova/cb")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
