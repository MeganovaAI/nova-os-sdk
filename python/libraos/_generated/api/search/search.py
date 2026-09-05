from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.web_search_request import WebSearchRequest
from ...models.web_search_response import WebSearchResponse
from ...types import Response


def _get_kwargs(
    *,
    body: WebSearchRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/search",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | WebSearchResponse | None:
    if response.status_code == 200:
        response_200 = WebSearchResponse.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 503:
        response_503 = Error.from_dict(response.json())

        return response_503

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Error | WebSearchResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: WebSearchRequest,
) -> Response[Error | WebSearchResponse]:
    """Governed web search

     The search subsystem as a first-class primitive: the sibling of `/v1/chat/completions`. The governed
    engine (source buckets -> adapters -> publisher-policy gate -> hydration) is otherwise reachable
    only inside a persona turn via the web skill; this is the call any app, agent or MCP client makes
    directly.

    Semantics are the skill layer's, re-exposed. The bucket cascade runs first and per-source refusals
    are NAMED in-band rather than dropped, so a source the deployment is not permitted to read is
    visible as a refusal instead of silently missing from the results. The publisher-policy gate runs
    per source with the caller-declared `kind`: `batch` honours robots everywhere, including sources
    where an interactive, user-initiated turn is exempt.

    Results are grouped by source (bucket order, then general) and are NOT re-ranked across sources in
    v1. Content carries `representation` and `status` so a provider's generated summary is never
    mistaken for text read from the page, and a hit that was found but never opened is not reported as
    read.

    Args:
        body (WebSearchRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | WebSearchResponse]
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
    body: WebSearchRequest,
) -> Error | WebSearchResponse | None:
    """Governed web search

     The search subsystem as a first-class primitive: the sibling of `/v1/chat/completions`. The governed
    engine (source buckets -> adapters -> publisher-policy gate -> hydration) is otherwise reachable
    only inside a persona turn via the web skill; this is the call any app, agent or MCP client makes
    directly.

    Semantics are the skill layer's, re-exposed. The bucket cascade runs first and per-source refusals
    are NAMED in-band rather than dropped, so a source the deployment is not permitted to read is
    visible as a refusal instead of silently missing from the results. The publisher-policy gate runs
    per source with the caller-declared `kind`: `batch` honours robots everywhere, including sources
    where an interactive, user-initiated turn is exempt.

    Results are grouped by source (bucket order, then general) and are NOT re-ranked across sources in
    v1. Content carries `representation` and `status` so a provider's generated summary is never
    mistaken for text read from the page, and a hit that was found but never opened is not reported as
    read.

    Args:
        body (WebSearchRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | WebSearchResponse
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: WebSearchRequest,
) -> Response[Error | WebSearchResponse]:
    """Governed web search

     The search subsystem as a first-class primitive: the sibling of `/v1/chat/completions`. The governed
    engine (source buckets -> adapters -> publisher-policy gate -> hydration) is otherwise reachable
    only inside a persona turn via the web skill; this is the call any app, agent or MCP client makes
    directly.

    Semantics are the skill layer's, re-exposed. The bucket cascade runs first and per-source refusals
    are NAMED in-band rather than dropped, so a source the deployment is not permitted to read is
    visible as a refusal instead of silently missing from the results. The publisher-policy gate runs
    per source with the caller-declared `kind`: `batch` honours robots everywhere, including sources
    where an interactive, user-initiated turn is exempt.

    Results are grouped by source (bucket order, then general) and are NOT re-ranked across sources in
    v1. Content carries `representation` and `status` so a provider's generated summary is never
    mistaken for text read from the page, and a hit that was found but never opened is not reported as
    read.

    Args:
        body (WebSearchRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | WebSearchResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: WebSearchRequest,
) -> Error | WebSearchResponse | None:
    """Governed web search

     The search subsystem as a first-class primitive: the sibling of `/v1/chat/completions`. The governed
    engine (source buckets -> adapters -> publisher-policy gate -> hydration) is otherwise reachable
    only inside a persona turn via the web skill; this is the call any app, agent or MCP client makes
    directly.

    Semantics are the skill layer's, re-exposed. The bucket cascade runs first and per-source refusals
    are NAMED in-band rather than dropped, so a source the deployment is not permitted to read is
    visible as a refusal instead of silently missing from the results. The publisher-policy gate runs
    per source with the caller-declared `kind`: `batch` honours robots everywhere, including sources
    where an interactive, user-initiated turn is exempt.

    Results are grouped by source (bucket order, then general) and are NOT re-ranked across sources in
    v1. Content carries `representation` and `status` so a provider's generated summary is never
    mistaken for text read from the page, and a hit that was found but never opened is not reported as
    read.

    Args:
        body (WebSearchRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | WebSearchResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
