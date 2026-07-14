from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.conversation_list import ConversationList
from ...models.error import Error
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    agent: str | Unset = UNSET,
    limit: int | Unset = 50,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["agent"] = agent

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/conversations",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ConversationList | Error | None:
    if response.status_code == 200:
        response_200 = ConversationList.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ConversationList | Error]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    agent: str | Unset = UNSET,
    limit: int | Unset = 50,
) -> Response[ConversationList | Error]:
    """List conversations

     List the caller's conversations, newest first.

    Args:
        agent (str | Unset):
        limit (int | Unset):  Default: 50.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ConversationList | Error]
    """

    kwargs = _get_kwargs(
        agent=agent,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    agent: str | Unset = UNSET,
    limit: int | Unset = 50,
) -> ConversationList | Error | None:
    """List conversations

     List the caller's conversations, newest first.

    Args:
        agent (str | Unset):
        limit (int | Unset):  Default: 50.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ConversationList | Error
    """

    return sync_detailed(
        client=client,
        agent=agent,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    agent: str | Unset = UNSET,
    limit: int | Unset = 50,
) -> Response[ConversationList | Error]:
    """List conversations

     List the caller's conversations, newest first.

    Args:
        agent (str | Unset):
        limit (int | Unset):  Default: 50.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ConversationList | Error]
    """

    kwargs = _get_kwargs(
        agent=agent,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    agent: str | Unset = UNSET,
    limit: int | Unset = 50,
) -> ConversationList | Error | None:
    """List conversations

     List the caller's conversations, newest first.

    Args:
        agent (str | Unset):
        limit (int | Unset):  Default: 50.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ConversationList | Error
    """

    return (
        await asyncio_detailed(
            client=client,
            agent=agent,
            limit=limit,
        )
    ).parsed
