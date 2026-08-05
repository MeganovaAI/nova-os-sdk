from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.mcp_request import McpRequest
from ...models.mcp_response import McpResponse
from ...types import Response


def _get_kwargs(
    *,
    body: McpRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/mcp",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Error | McpResponse | None:
    if response.status_code == 200:
        response_200 = McpResponse.from_dict(response.json())

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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Error | McpResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: McpRequest,
) -> Response[Error | McpResponse]:
    """MCP JSON-RPC endpoint

     Model Context Protocol endpoint speaking JSON-RPC 2.0. Supported methods: `initialize`,
    `tools/list`, `tools/call`, `resources/list`, `resources/read`. Requires an authenticated caller
    with the `mcp:read` scope. Feature-gated: when MCP is disabled the endpoint returns 404. Protocol-
    level failures (unknown method, invalid params, rate limit) are returned as HTTP 200 with a JSON-RPC
    error object. The wildcard form `POST /api/mcp/*` behaves identically.

    Args:
        body (McpRequest): JSON-RPC 2.0 request envelope.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | McpResponse]
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
    body: McpRequest,
) -> Error | McpResponse | None:
    """MCP JSON-RPC endpoint

     Model Context Protocol endpoint speaking JSON-RPC 2.0. Supported methods: `initialize`,
    `tools/list`, `tools/call`, `resources/list`, `resources/read`. Requires an authenticated caller
    with the `mcp:read` scope. Feature-gated: when MCP is disabled the endpoint returns 404. Protocol-
    level failures (unknown method, invalid params, rate limit) are returned as HTTP 200 with a JSON-RPC
    error object. The wildcard form `POST /api/mcp/*` behaves identically.

    Args:
        body (McpRequest): JSON-RPC 2.0 request envelope.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | McpResponse
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: McpRequest,
) -> Response[Error | McpResponse]:
    """MCP JSON-RPC endpoint

     Model Context Protocol endpoint speaking JSON-RPC 2.0. Supported methods: `initialize`,
    `tools/list`, `tools/call`, `resources/list`, `resources/read`. Requires an authenticated caller
    with the `mcp:read` scope. Feature-gated: when MCP is disabled the endpoint returns 404. Protocol-
    level failures (unknown method, invalid params, rate limit) are returned as HTTP 200 with a JSON-RPC
    error object. The wildcard form `POST /api/mcp/*` behaves identically.

    Args:
        body (McpRequest): JSON-RPC 2.0 request envelope.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | McpResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: McpRequest,
) -> Error | McpResponse | None:
    """MCP JSON-RPC endpoint

     Model Context Protocol endpoint speaking JSON-RPC 2.0. Supported methods: `initialize`,
    `tools/list`, `tools/call`, `resources/list`, `resources/read`. Requires an authenticated caller
    with the `mcp:read` scope. Feature-gated: when MCP is disabled the endpoint returns 404. Protocol-
    level failures (unknown method, invalid params, rate limit) are returned as HTTP 200 with a JSON-RPC
    error object. The wildcard form `POST /api/mcp/*` behaves identically.

    Args:
        body (McpRequest): JSON-RPC 2.0 request envelope.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | McpResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
