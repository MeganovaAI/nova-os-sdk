from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.promotion_candidates import PromotionCandidates
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    tenant: str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["tenant"] = tenant

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/managed/knowledge-signals/candidates",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | PromotionCandidates | None:
    if response.status_code == 200:
        response_200 = PromotionCandidates.from_dict(response.json())

        return response_200

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
) -> Response[Error | PromotionCandidates]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    tenant: str | Unset = UNSET,
) -> Response[Error | PromotionCandidates]:
    """List knowledge signals eligible for promotion

     Admin-only. Returns the fact keys that have cleared the promotion quorum and are candidates for
    promotion into the knowledge store. Promotion itself is a separate step.

    Args:
        tenant (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | PromotionCandidates]
    """

    kwargs = _get_kwargs(
        tenant=tenant,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    tenant: str | Unset = UNSET,
) -> Error | PromotionCandidates | None:
    """List knowledge signals eligible for promotion

     Admin-only. Returns the fact keys that have cleared the promotion quorum and are candidates for
    promotion into the knowledge store. Promotion itself is a separate step.

    Args:
        tenant (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | PromotionCandidates
    """

    return sync_detailed(
        client=client,
        tenant=tenant,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    tenant: str | Unset = UNSET,
) -> Response[Error | PromotionCandidates]:
    """List knowledge signals eligible for promotion

     Admin-only. Returns the fact keys that have cleared the promotion quorum and are candidates for
    promotion into the knowledge store. Promotion itself is a separate step.

    Args:
        tenant (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | PromotionCandidates]
    """

    kwargs = _get_kwargs(
        tenant=tenant,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    tenant: str | Unset = UNSET,
) -> Error | PromotionCandidates | None:
    """List knowledge signals eligible for promotion

     Admin-only. Returns the fact keys that have cleared the promotion quorum and are candidates for
    promotion into the knowledge store. Promotion itself is a separate step.

    Args:
        tenant (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | PromotionCandidates
    """

    return (
        await asyncio_detailed(
            client=client,
            tenant=tenant,
        )
    ).parsed
