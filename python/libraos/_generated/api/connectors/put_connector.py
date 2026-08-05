from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.connector_upsert import ConnectorUpsert
from ...models.error import Error
from ...models.put_connector_response_200 import PutConnectorResponse200
from ...types import Response


def _get_kwargs(
    kind: str,
    *,
    body: ConnectorUpsert,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/v1/managed/connectors/{kind}".format(
            kind=quote(str(kind), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | PutConnectorResponse200 | None:
    if response.status_code == 200:
        response_200 = PutConnectorResponse200.from_dict(response.json())

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
) -> Response[Error | PutConnectorResponse200]:
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
    body: ConnectorUpsert,
) -> Response[Error | PutConnectorResponse200]:
    """Upsert a connector's settings and merge its secrets

     Creates or updates the connector. Secret merge semantics: a non-empty value overwrites, an empty
    string deletes that key, and absent keys are preserved — so a single credential can be rotated
    without resending the rest.

    Args:
        kind (str):
        body (ConnectorUpsert): Upsert payload for a connector's settings and secrets.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | PutConnectorResponse200]
    """

    kwargs = _get_kwargs(
        kind=kind,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    kind: str,
    *,
    client: AuthenticatedClient | Client,
    body: ConnectorUpsert,
) -> Error | PutConnectorResponse200 | None:
    """Upsert a connector's settings and merge its secrets

     Creates or updates the connector. Secret merge semantics: a non-empty value overwrites, an empty
    string deletes that key, and absent keys are preserved — so a single credential can be rotated
    without resending the rest.

    Args:
        kind (str):
        body (ConnectorUpsert): Upsert payload for a connector's settings and secrets.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | PutConnectorResponse200
    """

    return sync_detailed(
        kind=kind,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    kind: str,
    *,
    client: AuthenticatedClient | Client,
    body: ConnectorUpsert,
) -> Response[Error | PutConnectorResponse200]:
    """Upsert a connector's settings and merge its secrets

     Creates or updates the connector. Secret merge semantics: a non-empty value overwrites, an empty
    string deletes that key, and absent keys are preserved — so a single credential can be rotated
    without resending the rest.

    Args:
        kind (str):
        body (ConnectorUpsert): Upsert payload for a connector's settings and secrets.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | PutConnectorResponse200]
    """

    kwargs = _get_kwargs(
        kind=kind,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    kind: str,
    *,
    client: AuthenticatedClient | Client,
    body: ConnectorUpsert,
) -> Error | PutConnectorResponse200 | None:
    """Upsert a connector's settings and merge its secrets

     Creates or updates the connector. Secret merge semantics: a non-empty value overwrites, an empty
    string deletes that key, and absent keys are preserved — so a single credential can be rotated
    without resending the rest.

    Args:
        kind (str):
        body (ConnectorUpsert): Upsert payload for a connector's settings and secrets.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | PutConnectorResponse200
    """

    return (
        await asyncio_detailed(
            kind=kind,
            client=client,
            body=body,
        )
    ).parsed
