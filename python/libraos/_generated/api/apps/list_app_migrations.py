from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_migration_list import AppMigrationList
from ...models.error import Error
from ...types import Response


def _get_kwargs(
    app: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/apps/{app}/migrations".format(
            app=quote(str(app), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> AppMigrationList | Error | None:
    if response.status_code == 200:
        response_200 = AppMigrationList.from_dict(response.json())

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

    if response.status_code == 503:
        response_503 = Error.from_dict(response.json())

        return response_503

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[AppMigrationList | Error]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    app: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[AppMigrationList | Error]:
    """List an app's migration history

     Returns the schema-migration audit rows for the app, ordered by filename. Failed migrations carry
    their `error_message`. Admin-only; 503 when persistent storage is not configured.

    Args:
        app (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AppMigrationList | Error]
    """

    kwargs = _get_kwargs(
        app=app,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    app: str,
    *,
    client: AuthenticatedClient | Client,
) -> AppMigrationList | Error | None:
    """List an app's migration history

     Returns the schema-migration audit rows for the app, ordered by filename. Failed migrations carry
    their `error_message`. Admin-only; 503 when persistent storage is not configured.

    Args:
        app (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AppMigrationList | Error
    """

    return sync_detailed(
        app=app,
        client=client,
    ).parsed


async def asyncio_detailed(
    app: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[AppMigrationList | Error]:
    """List an app's migration history

     Returns the schema-migration audit rows for the app, ordered by filename. Failed migrations carry
    their `error_message`. Admin-only; 503 when persistent storage is not configured.

    Args:
        app (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AppMigrationList | Error]
    """

    kwargs = _get_kwargs(
        app=app,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    app: str,
    *,
    client: AuthenticatedClient | Client,
) -> AppMigrationList | Error | None:
    """List an app's migration history

     Returns the schema-migration audit rows for the app, ordered by filename. Failed migrations carry
    their `error_message`. Admin-only; 503 when persistent storage is not configured.

    Args:
        app (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AppMigrationList | Error
    """

    return (
        await asyncio_detailed(
            app=app,
            client=client,
        )
    ).parsed
