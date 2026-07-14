from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.entitlements_envelope import EntitlementsEnvelope
from ...models.entitlements_update import EntitlementsUpdate
from ...models.error import Error
from ...types import Response


def _get_kwargs(
    tenant: str,
    *,
    body: EntitlementsUpdate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/v1/managed/entitlements/{tenant}".format(
            tenant=quote(str(tenant), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> EntitlementsEnvelope | Error | None:
    if response.status_code == 200:
        response_200 = EntitlementsEnvelope.from_dict(response.json())

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
) -> Response[EntitlementsEnvelope | Error]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    tenant: str,
    *,
    client: AuthenticatedClient | Client,
    body: EntitlementsUpdate,
) -> Response[EntitlementsEnvelope | Error]:
    """Upsert a tenant's entitlement flags

    Args:
        tenant (str):
        body (EntitlementsUpdate): Upsert payload for a tenant's entitlement flags.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[EntitlementsEnvelope | Error]
    """

    kwargs = _get_kwargs(
        tenant=tenant,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    tenant: str,
    *,
    client: AuthenticatedClient | Client,
    body: EntitlementsUpdate,
) -> EntitlementsEnvelope | Error | None:
    """Upsert a tenant's entitlement flags

    Args:
        tenant (str):
        body (EntitlementsUpdate): Upsert payload for a tenant's entitlement flags.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        EntitlementsEnvelope | Error
    """

    return sync_detailed(
        tenant=tenant,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    tenant: str,
    *,
    client: AuthenticatedClient | Client,
    body: EntitlementsUpdate,
) -> Response[EntitlementsEnvelope | Error]:
    """Upsert a tenant's entitlement flags

    Args:
        tenant (str):
        body (EntitlementsUpdate): Upsert payload for a tenant's entitlement flags.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[EntitlementsEnvelope | Error]
    """

    kwargs = _get_kwargs(
        tenant=tenant,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    tenant: str,
    *,
    client: AuthenticatedClient | Client,
    body: EntitlementsUpdate,
) -> EntitlementsEnvelope | Error | None:
    """Upsert a tenant's entitlement flags

    Args:
        tenant (str):
        body (EntitlementsUpdate): Upsert payload for a tenant's entitlement flags.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        EntitlementsEnvelope | Error
    """

    return (
        await asyncio_detailed(
            tenant=tenant,
            client=client,
            body=body,
        )
    ).parsed
