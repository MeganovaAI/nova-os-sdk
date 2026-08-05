from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    model: str | Unset = UNSET,
    connection: str,
    upgrade: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["Connection"] = connection

    headers["Upgrade"] = upgrade

    params: dict[str, Any] = {}

    params["model"] = model

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/realtime",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | Error | None:
    if response.status_code == 101:
        response_101 = cast(Any, None)
        return response_101

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = Error.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = Error.from_dict(response.json())

        return response_429

    if response.status_code == 502:
        response_502 = Error.from_dict(response.json())

        return response_502

    if response.status_code == 503:
        response_503 = Error.from_dict(response.json())

        return response_503

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
    model: str | Unset = UNSET,
    connection: str,
    upgrade: str,
) -> Response[Any | Error]:
    """Full-duplex speech-to-speech voice session (WebSocket)

     Opens a full-duplex voice WebSocket. The client performs a WebSocket upgrade (responds `101
    Switching Protocols`) on this authenticated endpoint; audio and event frames are then pumped
    bidirectionally between the client and the realtime speech-to-speech model. Standard REST error
    responses are returned only if the upgrade or upstream connection fails before the session starts.

    Args:
        model (str | Unset):  Example: gemini/gemini-3.1-flash-live-preview.
        connection (str):  Example: Upgrade.
        upgrade (str):  Example: websocket.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error]
    """

    kwargs = _get_kwargs(
        model=model,
        connection=connection,
        upgrade=upgrade,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    model: str | Unset = UNSET,
    connection: str,
    upgrade: str,
) -> Any | Error | None:
    """Full-duplex speech-to-speech voice session (WebSocket)

     Opens a full-duplex voice WebSocket. The client performs a WebSocket upgrade (responds `101
    Switching Protocols`) on this authenticated endpoint; audio and event frames are then pumped
    bidirectionally between the client and the realtime speech-to-speech model. Standard REST error
    responses are returned only if the upgrade or upstream connection fails before the session starts.

    Args:
        model (str | Unset):  Example: gemini/gemini-3.1-flash-live-preview.
        connection (str):  Example: Upgrade.
        upgrade (str):  Example: websocket.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error
    """

    return sync_detailed(
        client=client,
        model=model,
        connection=connection,
        upgrade=upgrade,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    model: str | Unset = UNSET,
    connection: str,
    upgrade: str,
) -> Response[Any | Error]:
    """Full-duplex speech-to-speech voice session (WebSocket)

     Opens a full-duplex voice WebSocket. The client performs a WebSocket upgrade (responds `101
    Switching Protocols`) on this authenticated endpoint; audio and event frames are then pumped
    bidirectionally between the client and the realtime speech-to-speech model. Standard REST error
    responses are returned only if the upgrade or upstream connection fails before the session starts.

    Args:
        model (str | Unset):  Example: gemini/gemini-3.1-flash-live-preview.
        connection (str):  Example: Upgrade.
        upgrade (str):  Example: websocket.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error]
    """

    kwargs = _get_kwargs(
        model=model,
        connection=connection,
        upgrade=upgrade,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    model: str | Unset = UNSET,
    connection: str,
    upgrade: str,
) -> Any | Error | None:
    """Full-duplex speech-to-speech voice session (WebSocket)

     Opens a full-duplex voice WebSocket. The client performs a WebSocket upgrade (responds `101
    Switching Protocols`) on this authenticated endpoint; audio and event frames are then pumped
    bidirectionally between the client and the realtime speech-to-speech model. Standard REST error
    responses are returned only if the upgrade or upstream connection fails before the session starts.

    Args:
        model (str | Unset):  Example: gemini/gemini-3.1-flash-live-preview.
        connection (str):  Example: Upgrade.
        upgrade (str):  Example: websocket.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error
    """

    return (
        await asyncio_detailed(
            client=client,
            model=model,
            connection=connection,
            upgrade=upgrade,
        )
    ).parsed
