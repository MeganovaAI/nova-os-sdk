from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.message_request import MessageRequest
from ...models.message_response import MessageResponse
from ...types import Response


def _get_kwargs(
    *,
    body: MessageRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/messages",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | MessageResponse | None:
    if response.status_code == 200:
        response_200 = MessageResponse.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())

        return response_404

    if response.status_code == 426:
        response_426 = Error.from_dict(response.json())

        return response_426

    if response.status_code == 429:
        response_429 = Error.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Error | MessageResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: MessageRequest,
) -> Response[Error | MessageResponse]:
    """Send an Anthropic-compatible message

     Route to a Nova OS agent via `metadata.agent_id`; omit for the default agent.

    When `stream:false`, returns a single `MessageResponse`.
    When `stream:true`, returns SSE with one `event:` line + JSON
    payload per event. Event types defined by `StreamEvent`.

    Args:
        body (MessageRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | MessageResponse]
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
    body: MessageRequest,
) -> Error | MessageResponse | None:
    """Send an Anthropic-compatible message

     Route to a Nova OS agent via `metadata.agent_id`; omit for the default agent.

    When `stream:false`, returns a single `MessageResponse`.
    When `stream:true`, returns SSE with one `event:` line + JSON
    payload per event. Event types defined by `StreamEvent`.

    Args:
        body (MessageRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | MessageResponse
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: MessageRequest,
) -> Response[Error | MessageResponse]:
    """Send an Anthropic-compatible message

     Route to a Nova OS agent via `metadata.agent_id`; omit for the default agent.

    When `stream:false`, returns a single `MessageResponse`.
    When `stream:true`, returns SSE with one `event:` line + JSON
    payload per event. Event types defined by `StreamEvent`.

    Args:
        body (MessageRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | MessageResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: MessageRequest,
) -> Error | MessageResponse | None:
    """Send an Anthropic-compatible message

     Route to a Nova OS agent via `metadata.agent_id`; omit for the default agent.

    When `stream:false`, returns a single `MessageResponse`.
    When `stream:true`, returns SSE with one `event:` line + JSON
    payload per event. Event types defined by `StreamEvent`.

    Args:
        body (MessageRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | MessageResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
