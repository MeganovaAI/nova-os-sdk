from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_agent import AppAgent
from ...models.error import Error
from ...types import Response


def _get_kwargs(
    app: str,
    id: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/apps/{app}/agents/{id}".format(
            app=quote(str(app), safe=""),
            id=quote(str(id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> AppAgent | Error | None:
    if response.status_code == 200:
        response_200 = AppAgent.from_dict(response.json())

        return response_200

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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[AppAgent | Error]:
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
) -> Response[AppAgent | Error]:
    """Get one app-scoped agent

     Returns a single agent (id + capabilities) scoped to the app namespace. Admin-only.

    Args:
        app (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AppAgent | Error]
    """

    kwargs = _get_kwargs(
        app=app,
        id=id,
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
) -> AppAgent | Error | None:
    """Get one app-scoped agent

     Returns a single agent (id + capabilities) scoped to the app namespace. Admin-only.

    Args:
        app (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AppAgent | Error
    """

    return sync_detailed(
        app=app,
        id=id,
        client=client,
    ).parsed


async def asyncio_detailed(
    app: str,
    id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[AppAgent | Error]:
    """Get one app-scoped agent

     Returns a single agent (id + capabilities) scoped to the app namespace. Admin-only.

    Args:
        app (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AppAgent | Error]
    """

    kwargs = _get_kwargs(
        app=app,
        id=id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    app: str,
    id: str,
    *,
    client: AuthenticatedClient | Client,
) -> AppAgent | Error | None:
    """Get one app-scoped agent

     Returns a single agent (id + capabilities) scoped to the app namespace. Admin-only.

    Args:
        app (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AppAgent | Error
    """

    return (
        await asyncio_detailed(
            app=app,
            id=id,
            client=client,
        )
    ).parsed
