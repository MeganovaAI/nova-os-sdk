from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.native_chat_request import NativeChatRequest
from ...models.native_chat_result import NativeChatResult
from ...types import UNSET, Response, Unset


def _get_kwargs(
    api_key: str,
    *,
    body: NativeChatRequest,
    fast: bool | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["fast"] = fast

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/agents/v1/{api_key}/chat".format(
            api_key=quote(str(api_key), safe=""),
        ),
        "params": params,
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

    if response.status_code == 429:
        response_429 = Error.from_dict(response.json())

        return response_429

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
    api_key: str,
    *,
    client: AuthenticatedClient | Client,
    body: NativeChatRequest,
    fast: bool | Unset = UNSET,
) -> Response[Error | NativeChatResult]:
    """Send a chat turn to an agent (native)

     Native chat endpoint. Accepts either the simple `{message}` shape or the OpenAI-style `messages[]`
    array, plus Nova extensions (`fast`, `stream`, `brain`, `metadata`). The synchronous response
    carries the assistant `response`, an aggregated per-turn `usage` block (with a `by_stage[]` split),
    a `grounding` outcome, and the resolved `conversation_id`.

    Args:
        api_key (str):
        fast (bool | Unset):
        body (NativeChatRequest): Native chat request. Supply either `message` (simple form) or
            `messages` (OpenAI array form).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | NativeChatResult]
    """

    kwargs = _get_kwargs(
        api_key=api_key,
        body=body,
        fast=fast,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    api_key: str,
    *,
    client: AuthenticatedClient | Client,
    body: NativeChatRequest,
    fast: bool | Unset = UNSET,
) -> Error | NativeChatResult | None:
    """Send a chat turn to an agent (native)

     Native chat endpoint. Accepts either the simple `{message}` shape or the OpenAI-style `messages[]`
    array, plus Nova extensions (`fast`, `stream`, `brain`, `metadata`). The synchronous response
    carries the assistant `response`, an aggregated per-turn `usage` block (with a `by_stage[]` split),
    a `grounding` outcome, and the resolved `conversation_id`.

    Args:
        api_key (str):
        fast (bool | Unset):
        body (NativeChatRequest): Native chat request. Supply either `message` (simple form) or
            `messages` (OpenAI array form).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | NativeChatResult
    """

    return sync_detailed(
        api_key=api_key,
        client=client,
        body=body,
        fast=fast,
    ).parsed


async def asyncio_detailed(
    api_key: str,
    *,
    client: AuthenticatedClient | Client,
    body: NativeChatRequest,
    fast: bool | Unset = UNSET,
) -> Response[Error | NativeChatResult]:
    """Send a chat turn to an agent (native)

     Native chat endpoint. Accepts either the simple `{message}` shape or the OpenAI-style `messages[]`
    array, plus Nova extensions (`fast`, `stream`, `brain`, `metadata`). The synchronous response
    carries the assistant `response`, an aggregated per-turn `usage` block (with a `by_stage[]` split),
    a `grounding` outcome, and the resolved `conversation_id`.

    Args:
        api_key (str):
        fast (bool | Unset):
        body (NativeChatRequest): Native chat request. Supply either `message` (simple form) or
            `messages` (OpenAI array form).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | NativeChatResult]
    """

    kwargs = _get_kwargs(
        api_key=api_key,
        body=body,
        fast=fast,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    api_key: str,
    *,
    client: AuthenticatedClient | Client,
    body: NativeChatRequest,
    fast: bool | Unset = UNSET,
) -> Error | NativeChatResult | None:
    """Send a chat turn to an agent (native)

     Native chat endpoint. Accepts either the simple `{message}` shape or the OpenAI-style `messages[]`
    array, plus Nova extensions (`fast`, `stream`, `brain`, `metadata`). The synchronous response
    carries the assistant `response`, an aggregated per-turn `usage` block (with a `by_stage[]` split),
    a `grounding` outcome, and the resolved `conversation_id`.

    Args:
        api_key (str):
        fast (bool | Unset):
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
            api_key=api_key,
            client=client,
            body=body,
            fast=fast,
        )
    ).parsed
