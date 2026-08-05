from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.native_chat_request import NativeChatRequest
from ...models.native_job_accepted import NativeJobAccepted
from ...types import Response


def _get_kwargs(
    api_key: str,
    *,
    body: NativeChatRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/agents/v1/{api_key}/jobs".format(
            api_key=quote(str(api_key), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | NativeJobAccepted | None:
    if response.status_code == 202:
        response_202 = NativeJobAccepted.from_dict(response.json())

        return response_202

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())

        return response_404

    if response.status_code == 429:
        response_429 = Error.from_dict(response.json())

        return response_429

    if response.status_code == 503:
        response_503 = Error.from_dict(response.json())

        return response_503

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Error | NativeJobAccepted]:
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
) -> Response[Error | NativeJobAccepted]:
    """Submit an asynchronous job

     Submit a long-running turn (e.g. deep research, multi-section report) as an asynchronous job.
    Returns 202 immediately; poll or stream for progress and the final result. Requires PostgreSQL
    persistence — returns 503 when async jobs are disabled.

    Args:
        api_key (str):
        body (NativeChatRequest): Native chat request. Supply either `message` (simple form) or
            `messages` (OpenAI array form).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | NativeJobAccepted]
    """

    kwargs = _get_kwargs(
        api_key=api_key,
        body=body,
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
) -> Error | NativeJobAccepted | None:
    """Submit an asynchronous job

     Submit a long-running turn (e.g. deep research, multi-section report) as an asynchronous job.
    Returns 202 immediately; poll or stream for progress and the final result. Requires PostgreSQL
    persistence — returns 503 when async jobs are disabled.

    Args:
        api_key (str):
        body (NativeChatRequest): Native chat request. Supply either `message` (simple form) or
            `messages` (OpenAI array form).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | NativeJobAccepted
    """

    return sync_detailed(
        api_key=api_key,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    api_key: str,
    *,
    client: AuthenticatedClient | Client,
    body: NativeChatRequest,
) -> Response[Error | NativeJobAccepted]:
    """Submit an asynchronous job

     Submit a long-running turn (e.g. deep research, multi-section report) as an asynchronous job.
    Returns 202 immediately; poll or stream for progress and the final result. Requires PostgreSQL
    persistence — returns 503 when async jobs are disabled.

    Args:
        api_key (str):
        body (NativeChatRequest): Native chat request. Supply either `message` (simple form) or
            `messages` (OpenAI array form).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | NativeJobAccepted]
    """

    kwargs = _get_kwargs(
        api_key=api_key,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    api_key: str,
    *,
    client: AuthenticatedClient | Client,
    body: NativeChatRequest,
) -> Error | NativeJobAccepted | None:
    """Submit an asynchronous job

     Submit a long-running turn (e.g. deep research, multi-section report) as an asynchronous job.
    Returns 202 immediately; poll or stream for progress and the final result. Requires PostgreSQL
    persistence — returns 503 when async jobs are disabled.

    Args:
        api_key (str):
        body (NativeChatRequest): Native chat request. Supply either `message` (simple form) or
            `messages` (OpenAI array form).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | NativeJobAccepted
    """

    return (
        await asyncio_detailed(
            api_key=api_key,
            client=client,
            body=body,
        )
    ).parsed
