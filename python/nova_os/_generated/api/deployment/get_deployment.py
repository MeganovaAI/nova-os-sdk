from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.deployment import Deployment
from ...models.error import Error
from ...types import Response


def _get_kwargs() -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/managed/deployment",
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Deployment | Error | None:
    if response.status_code == 200:
        response_200 = Deployment.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Deployment | Error]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[Deployment | Error]:
    """Read this instance's capabilities, model tiers, locales, and auth contract

     Minimal capabilities read for boot-time client configuration. Lets a
    web or iOS client discover server version, optional feature labels,
    resolved model tiers, enabled locales, and the OIDC auth contract
    without probing individual endpoints. Per the contract-unification
    design (D1, lean: derive), this is deliberately small and advisory —
    `GET /agents/v1/personas` remains the source of truth for which agents
    exist.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Deployment | Error]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
) -> Deployment | Error | None:
    """Read this instance's capabilities, model tiers, locales, and auth contract

     Minimal capabilities read for boot-time client configuration. Lets a
    web or iOS client discover server version, optional feature labels,
    resolved model tiers, enabled locales, and the OIDC auth contract
    without probing individual endpoints. Per the contract-unification
    design (D1, lean: derive), this is deliberately small and advisory —
    `GET /agents/v1/personas` remains the source of truth for which agents
    exist.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Deployment | Error
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[Deployment | Error]:
    """Read this instance's capabilities, model tiers, locales, and auth contract

     Minimal capabilities read for boot-time client configuration. Lets a
    web or iOS client discover server version, optional feature labels,
    resolved model tiers, enabled locales, and the OIDC auth contract
    without probing individual endpoints. Per the contract-unification
    design (D1, lean: derive), this is deliberately small and advisory —
    `GET /agents/v1/personas` remains the source of truth for which agents
    exist.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Deployment | Error]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
) -> Deployment | Error | None:
    """Read this instance's capabilities, model tiers, locales, and auth contract

     Minimal capabilities read for boot-time client configuration. Lets a
    web or iOS client discover server version, optional feature labels,
    resolved model tiers, enabled locales, and the OIDC auth contract
    without probing individual endpoints. Per the contract-unification
    design (D1, lean: derive), this is deliberately small and advisory —
    `GET /agents/v1/personas` remains the source of truth for which agents
    exist.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Deployment | Error
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
