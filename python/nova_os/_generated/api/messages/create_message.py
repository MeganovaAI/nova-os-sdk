from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.message_request import MessageRequest
from ...models.message_response import MessageResponse
from ...types import Response


def _get_kwargs(
    agent_id: str,
    *,
    body: MessageRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/managed/agents/{agent_id}/messages".format(
            agent_id=quote(str(agent_id), safe=""),
        ),
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
    agent_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: MessageRequest,
) -> Response[Error | MessageResponse]:
    """Send a message to an agent

     When `stream:false`, returns a single `MessageResponse`.
    When `stream:true`, returns SSE with one `event:` line + JSON
    payload per event. Event types defined by `StreamEvent`.

    Args:
        agent_id (str):
        body (MessageRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | MessageResponse]
    """

    kwargs = _get_kwargs(
        agent_id=agent_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    agent_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: MessageRequest,
) -> Error | MessageResponse | None:
    """Send a message to an agent

     When `stream:false`, returns a single `MessageResponse`.
    When `stream:true`, returns SSE with one `event:` line + JSON
    payload per event. Event types defined by `StreamEvent`.

    Args:
        agent_id (str):
        body (MessageRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | MessageResponse
    """

    return sync_detailed(
        agent_id=agent_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    agent_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: MessageRequest,
) -> Response[Error | MessageResponse]:
    """Send a message to an agent

     When `stream:false`, returns a single `MessageResponse`.
    When `stream:true`, returns SSE with one `event:` line + JSON
    payload per event. Event types defined by `StreamEvent`.

    Args:
        agent_id (str):
        body (MessageRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | MessageResponse]
    """

    kwargs = _get_kwargs(
        agent_id=agent_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    agent_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: MessageRequest,
) -> Error | MessageResponse | None:
    """Send a message to an agent

     When `stream:false`, returns a single `MessageResponse`.
    When `stream:true`, returns SSE with one `event:` line + JSON
    payload per event. Event types defined by `StreamEvent`.

    Args:
        agent_id (str):
        body (MessageRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | MessageResponse
    """

    return (
        await asyncio_detailed(
            agent_id=agent_id,
            client=client,
            body=body,
        )
    ).parsed
