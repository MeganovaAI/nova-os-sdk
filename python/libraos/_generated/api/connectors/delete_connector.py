from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.delete_connector_response_200 import DeleteConnectorResponse200
from ...models.error import Error
from ...types import Response


def _get_kwargs(
    kind: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/v1/managed/connectors/{kind}".format(
            kind=quote(str(kind), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DeleteConnectorResponse200 | Error | None:
    if response.status_code == 200:
        response_200 = DeleteConnectorResponse200.from_dict(response.json())

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
) -> Response[DeleteConnectorResponse200 | Error]:
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
) -> Response[DeleteConnectorResponse200 | Error]:
    """Remove a connector config

    Args:
        kind (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeleteConnectorResponse200 | Error]
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
) -> DeleteConnectorResponse200 | Error | None:
    """Remove a connector config

    Args:
        kind (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeleteConnectorResponse200 | Error
    """

    return sync_detailed(
        kind=kind,
        client=client,
    ).parsed


async def asyncio_detailed(
    kind: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[DeleteConnectorResponse200 | Error]:
    """Remove a connector config

    Args:
        kind (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeleteConnectorResponse200 | Error]
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
) -> DeleteConnectorResponse200 | Error | None:
    """Remove a connector config

    Args:
        kind (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeleteConnectorResponse200 | Error
    """

    return (
        await asyncio_detailed(
            kind=kind,
            client=client,
        )
    ).parsed
