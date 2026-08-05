from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.infra_health import InfraHealth
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    window: str | Unset = "24h",
    limit: int | Unset = 20,
    agent: str | Unset = UNSET,
    model: str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["window"] = window

    params["limit"] = limit

    params["agent"] = agent

    params["model"] = model

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/managed/infra-health",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Error | InfraHealth | None:
    if response.status_code == 200:
        response_200 = InfraHealth.from_dict(response.json())

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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Error | InfraHealth]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    window: str | Unset = "24h",
    limit: int | Unset = 20,
    agent: str | Unset = UNSET,
    model: str | Unset = UNSET,
) -> Response[Error | InfraHealth]:
    """Infrastructure health aggregation

     On-read aggregation of recent call activity into error clusters, tool errors, latency percentiles,
    identity errors, and grounding outcomes, over a rolling window. Admin-only. Requires persistent
    storage.

    Args:
        window (str | Unset):  Default: '24h'.
        limit (int | Unset):  Default: 20.
        agent (str | Unset):
        model (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | InfraHealth]
    """

    kwargs = _get_kwargs(
        window=window,
        limit=limit,
        agent=agent,
        model=model,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    window: str | Unset = "24h",
    limit: int | Unset = 20,
    agent: str | Unset = UNSET,
    model: str | Unset = UNSET,
) -> Error | InfraHealth | None:
    """Infrastructure health aggregation

     On-read aggregation of recent call activity into error clusters, tool errors, latency percentiles,
    identity errors, and grounding outcomes, over a rolling window. Admin-only. Requires persistent
    storage.

    Args:
        window (str | Unset):  Default: '24h'.
        limit (int | Unset):  Default: 20.
        agent (str | Unset):
        model (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | InfraHealth
    """

    return sync_detailed(
        client=client,
        window=window,
        limit=limit,
        agent=agent,
        model=model,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    window: str | Unset = "24h",
    limit: int | Unset = 20,
    agent: str | Unset = UNSET,
    model: str | Unset = UNSET,
) -> Response[Error | InfraHealth]:
    """Infrastructure health aggregation

     On-read aggregation of recent call activity into error clusters, tool errors, latency percentiles,
    identity errors, and grounding outcomes, over a rolling window. Admin-only. Requires persistent
    storage.

    Args:
        window (str | Unset):  Default: '24h'.
        limit (int | Unset):  Default: 20.
        agent (str | Unset):
        model (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | InfraHealth]
    """

    kwargs = _get_kwargs(
        window=window,
        limit=limit,
        agent=agent,
        model=model,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    window: str | Unset = "24h",
    limit: int | Unset = 20,
    agent: str | Unset = UNSET,
    model: str | Unset = UNSET,
) -> Error | InfraHealth | None:
    """Infrastructure health aggregation

     On-read aggregation of recent call activity into error clusters, tool errors, latency percentiles,
    identity errors, and grounding outcomes, over a rolling window. Admin-only. Requires persistent
    storage.

    Args:
        window (str | Unset):  Default: '24h'.
        limit (int | Unset):  Default: 20.
        agent (str | Unset):
        model (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | InfraHealth
    """

    return (
        await asyncio_detailed(
            client=client,
            window=window,
            limit=limit,
            agent=agent,
            model=model,
        )
    ).parsed
