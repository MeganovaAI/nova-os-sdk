from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.feature_list import FeatureList
from ...types import Response


def _get_kwargs() -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/managed/features",
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Error | FeatureList | None:
    if response.status_code == 200:
        response_200 = FeatureList.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = Error.from_dict(response.json())

        return response_403

    if response.status_code == 503:
        response_503 = Error.from_dict(response.json())

        return response_503

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Error | FeatureList]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[Error | FeatureList]:
    """Feature-status snapshot

     Returns an in-memory snapshot of each gated feature's resolved state (on / off / degraded), where it
    resolved from, its flag name, and a reason. Admin-only. No secret values are exposed. 503 when
    disabled via the runtime hatch.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | FeatureList]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
) -> Error | FeatureList | None:
    """Feature-status snapshot

     Returns an in-memory snapshot of each gated feature's resolved state (on / off / degraded), where it
    resolved from, its flag name, and a reason. Admin-only. No secret values are exposed. 503 when
    disabled via the runtime hatch.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | FeatureList
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[Error | FeatureList]:
    """Feature-status snapshot

     Returns an in-memory snapshot of each gated feature's resolved state (on / off / degraded), where it
    resolved from, its flag name, and a reason. Admin-only. No secret values are exposed. 503 when
    disabled via the runtime hatch.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | FeatureList]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
) -> Error | FeatureList | None:
    """Feature-status snapshot

     Returns an in-memory snapshot of each gated feature's resolved state (on / off / degraded), where it
    resolved from, its flag name, and a reason. Admin-only. No secret values are exposed. 503 when
    disabled via the runtime hatch.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | FeatureList
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
