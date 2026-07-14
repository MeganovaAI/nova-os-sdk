from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.native_chat_request import NativeChatRequest
from ...models.native_chat_result import NativeChatResult
from ...types import Response


def _get_kwargs(
    app: str,
    id: str,
    *,
    body: NativeChatRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/apps/{app}/agents/{id}/chat".format(
            app=quote(str(app), safe=""),
            id=quote(str(id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | NativeChatResult | None:
    if response.status_code == 200:
        response_200 = NativeChatResult.from_dict(response.json())

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


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Error | NativeChatResult]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    app: str,
    id: str,
    *,
    client: AuthenticatedClient | Client,
    body: NativeChatRequest,
) -> Response[Error | NativeChatResult]:
    """Chat with an app-scoped agent

     Sends a chat turn to an agent resolved within the given app namespace. Accepts the standard chat
    request body (simple `message` or OpenAI-style `messages`); set `stream: true` for Server-Sent
    Events.

    Args:
        app (str):
        id (str):
        body (NativeChatRequest): Native chat request. Supply either `message` (simple form) or
            `messages` (OpenAI array form).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | NativeChatResult]
    """

    kwargs = _get_kwargs(
        app=app,
        id=id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    app: str,
    id: str,
    *,
    client: AuthenticatedClient | Client,
    body: NativeChatRequest,
) -> Error | NativeChatResult | None:
    """Chat with an app-scoped agent

     Sends a chat turn to an agent resolved within the given app namespace. Accepts the standard chat
    request body (simple `message` or OpenAI-style `messages`); set `stream: true` for Server-Sent
    Events.

    Args:
        app (str):
        id (str):
        body (NativeChatRequest): Native chat request. Supply either `message` (simple form) or
            `messages` (OpenAI array form).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | NativeChatResult
    """

    return sync_detailed(
        app=app,
        id=id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    app: str,
    id: str,
    *,
    client: AuthenticatedClient | Client,
    body: NativeChatRequest,
) -> Response[Error | NativeChatResult]:
    """Chat with an app-scoped agent

     Sends a chat turn to an agent resolved within the given app namespace. Accepts the standard chat
    request body (simple `message` or OpenAI-style `messages`); set `stream: true` for Server-Sent
    Events.

    Args:
        app (str):
        id (str):
        body (NativeChatRequest): Native chat request. Supply either `message` (simple form) or
            `messages` (OpenAI array form).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | NativeChatResult]
    """

    kwargs = _get_kwargs(
        app=app,
        id=id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    app: str,
    id: str,
    *,
    client: AuthenticatedClient | Client,
    body: NativeChatRequest,
) -> Error | NativeChatResult | None:
    """Chat with an app-scoped agent

     Sends a chat turn to an agent resolved within the given app namespace. Accepts the standard chat
    request body (simple `message` or OpenAI-style `messages`); set `stream: true` for Server-Sent
    Events.

    Args:
        app (str):
        id (str):
        body (NativeChatRequest): Native chat request. Supply either `message` (simple form) or
            `messages` (OpenAI array form).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | NativeChatResult
    """

    return (
        await asyncio_detailed(
            app=app,
            id=id,
            client=client,
            body=body,
        )
    ).parsed
