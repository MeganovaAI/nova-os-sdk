from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.search_app_knowledge_body import SearchAppKnowledgeBody
from ...types import Response


def _get_kwargs(
    *,
    body: SearchAppKnowledgeBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/knowledge/search",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | Error | None:
    if response.status_code == 200:
        response_200 = cast(Any, None)
        return response_200

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = Error.from_dict(response.json())

        return response_403

    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())

        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | Error]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: SearchAppKnowledgeBody,
) -> Response[Any | Error]:
    r"""Search a knowledge collection

     Hybrid retrieval over one collection. `collection` accepts a collection id OR its exact display
    name; an unresolvable value returns 404 rather than an empty list, because `[]` with HTTP 200 is
    indistinguishable from \"the store is empty\" or \"retrieval is broken\". Omitting `collection`
    defaults to the caller's own and keeps the empty-list behaviour. Set `debug: true` for a per-arm
    breakdown (BM25 ranking, vector ranking, keyword fallback, the full fused ordering before
    truncation, and the resolved rrf_k) — only the surreal backend fuses arms.

    Args:
        body (SearchAppKnowledgeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: SearchAppKnowledgeBody,
) -> Any | Error | None:
    r"""Search a knowledge collection

     Hybrid retrieval over one collection. `collection` accepts a collection id OR its exact display
    name; an unresolvable value returns 404 rather than an empty list, because `[]` with HTTP 200 is
    indistinguishable from \"the store is empty\" or \"retrieval is broken\". Omitting `collection`
    defaults to the caller's own and keeps the empty-list behaviour. Set `debug: true` for a per-arm
    breakdown (BM25 ranking, vector ranking, keyword fallback, the full fused ordering before
    truncation, and the resolved rrf_k) — only the surreal backend fuses arms.

    Args:
        body (SearchAppKnowledgeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: SearchAppKnowledgeBody,
) -> Response[Any | Error]:
    r"""Search a knowledge collection

     Hybrid retrieval over one collection. `collection` accepts a collection id OR its exact display
    name; an unresolvable value returns 404 rather than an empty list, because `[]` with HTTP 200 is
    indistinguishable from \"the store is empty\" or \"retrieval is broken\". Omitting `collection`
    defaults to the caller's own and keeps the empty-list behaviour. Set `debug: true` for a per-arm
    breakdown (BM25 ranking, vector ranking, keyword fallback, the full fused ordering before
    truncation, and the resolved rrf_k) — only the surreal backend fuses arms.

    Args:
        body (SearchAppKnowledgeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: SearchAppKnowledgeBody,
) -> Any | Error | None:
    r"""Search a knowledge collection

     Hybrid retrieval over one collection. `collection` accepts a collection id OR its exact display
    name; an unresolvable value returns 404 rather than an empty list, because `[]` with HTTP 200 is
    indistinguishable from \"the store is empty\" or \"retrieval is broken\". Omitting `collection`
    defaults to the caller's own and keeps the empty-list behaviour. Set `debug: true` for a per-arm
    breakdown (BM25 ranking, vector ranking, keyword fallback, the full fused ordering before
    truncation, and the resolved rrf_k) — only the surreal backend fuses arms.

    Args:
        body (SearchAppKnowledgeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
