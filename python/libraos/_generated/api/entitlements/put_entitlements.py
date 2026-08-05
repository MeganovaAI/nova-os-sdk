from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.entitlements_envelope import EntitlementsEnvelope
from ...models.entitlements_update import EntitlementsUpdate
from ...models.error import Error
from ...types import UNSET, Response


def _get_kwargs(
    *,
    body: EntitlementsUpdate,
    tenant: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["tenant"] = tenant

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/v1/managed/entitlements",
        "params": params,
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
    *,
    client: AuthenticatedClient | Client,
    body: EntitlementsUpdate,
    tenant: str,
) -> Response[EntitlementsEnvelope | Error]:
    """Upsert a tenant's entitlement flags

     The tenant is supplied via the tenant query parameter.

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
        body=body,
        tenant=tenant,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: EntitlementsUpdate,
    tenant: str,
) -> EntitlementsEnvelope | Error | None:
    """Upsert a tenant's entitlement flags

     The tenant is supplied via the tenant query parameter.

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
        client=client,
        body=body,
        tenant=tenant,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: EntitlementsUpdate,
    tenant: str,
) -> Response[EntitlementsEnvelope | Error]:
    """Upsert a tenant's entitlement flags

     The tenant is supplied via the tenant query parameter.

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
        body=body,
        tenant=tenant,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: EntitlementsUpdate,
    tenant: str,
) -> EntitlementsEnvelope | Error | None:
    """Upsert a tenant's entitlement flags

     The tenant is supplied via the tenant query parameter.

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
            client=client,
            body=body,
            tenant=tenant,
        )
    ).parsed
