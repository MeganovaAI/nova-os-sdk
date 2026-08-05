from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.connector_credentials import ConnectorCredentials
from ...models.error import Error
from ...types import Response


def _get_kwargs(
    kind: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/managed/connectors/{kind}/credentials".format(
            kind=quote(str(kind), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ConnectorCredentials | Error | None:
    if response.status_code == 200:
        response_200 = ConnectorCredentials.from_dict(response.json())

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
) -> Response[ConnectorCredentials | Error]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    kind: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ConnectorCredentials | Error]:
    """Read a connector's decrypted credentials (for connector services)

     Returns decrypted secret values for the connector. Intended for connector services authenticating
    with an admin or service credential; every access is logged with the caller identity.

    Args:
        kind (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ConnectorCredentials | Error]
    """

    kwargs = _get_kwargs(
        kind=kind,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    kind: str,
    *,
    client: AuthenticatedClient | Client,
) -> ConnectorCredentials | Error | None:
    """Read a connector's decrypted credentials (for connector services)

     Returns decrypted secret values for the connector. Intended for connector services authenticating
    with an admin or service credential; every access is logged with the caller identity.

    Args:
        kind (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ConnectorCredentials | Error
    """

    return sync_detailed(
        kind=kind,
        client=client,
    ).parsed


async def asyncio_detailed(
    kind: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ConnectorCredentials | Error]:
    """Read a connector's decrypted credentials (for connector services)

     Returns decrypted secret values for the connector. Intended for connector services authenticating
    with an admin or service credential; every access is logged with the caller identity.

    Args:
        kind (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ConnectorCredentials | Error]
    """

    kwargs = _get_kwargs(
        kind=kind,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    kind: str,
    *,
    client: AuthenticatedClient | Client,
) -> ConnectorCredentials | Error | None:
    """Read a connector's decrypted credentials (for connector services)

     Returns decrypted secret values for the connector. Intended for connector services authenticating
    with an admin or service credential; every access is logged with the caller identity.

    Args:
        kind (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ConnectorCredentials | Error
    """

    return (
        await asyncio_detailed(
            kind=kind,
            client=client,
        )
    ).parsed
