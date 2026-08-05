from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.knowledge_signal_list import KnowledgeSignalList
from ...models.list_knowledge_signals_status import ListKnowledgeSignalsStatus
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    status: ListKnowledgeSignalsStatus | Unset = ListKnowledgeSignalsStatus.PENDING,
    limit: int | Unset = 100,
    tenant: str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_status: str | Unset = UNSET
    if not isinstance(status, Unset):
        json_status = status.value

    params["status"] = json_status

    params["limit"] = limit

    params["tenant"] = tenant

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/managed/knowledge-signals",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | KnowledgeSignalList | None:
    if response.status_code == 200:
        response_200 = KnowledgeSignalList.from_dict(response.json())

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
) -> Response[Error | KnowledgeSignalList]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    status: ListKnowledgeSignalsStatus | Unset = ListKnowledgeSignalsStatus.PENDING,
    limit: int | Unset = 100,
    tenant: str | Unset = UNSET,
) -> Response[Error | KnowledgeSignalList]:
    """List queued knowledge signals by status

     Admin-only curator view of captured knowledge signals awaiting review.

    Args:
        status (ListKnowledgeSignalsStatus | Unset):  Default: ListKnowledgeSignalsStatus.PENDING.
        limit (int | Unset):  Default: 100.
        tenant (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | KnowledgeSignalList]
    """

    kwargs = _get_kwargs(
        status=status,
        limit=limit,
        tenant=tenant,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    status: ListKnowledgeSignalsStatus | Unset = ListKnowledgeSignalsStatus.PENDING,
    limit: int | Unset = 100,
    tenant: str | Unset = UNSET,
) -> Error | KnowledgeSignalList | None:
    """List queued knowledge signals by status

     Admin-only curator view of captured knowledge signals awaiting review.

    Args:
        status (ListKnowledgeSignalsStatus | Unset):  Default: ListKnowledgeSignalsStatus.PENDING.
        limit (int | Unset):  Default: 100.
        tenant (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | KnowledgeSignalList
    """

    return sync_detailed(
        client=client,
        status=status,
        limit=limit,
        tenant=tenant,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    status: ListKnowledgeSignalsStatus | Unset = ListKnowledgeSignalsStatus.PENDING,
    limit: int | Unset = 100,
    tenant: str | Unset = UNSET,
) -> Response[Error | KnowledgeSignalList]:
    """List queued knowledge signals by status

     Admin-only curator view of captured knowledge signals awaiting review.

    Args:
        status (ListKnowledgeSignalsStatus | Unset):  Default: ListKnowledgeSignalsStatus.PENDING.
        limit (int | Unset):  Default: 100.
        tenant (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | KnowledgeSignalList]
    """

    kwargs = _get_kwargs(
        status=status,
        limit=limit,
        tenant=tenant,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    status: ListKnowledgeSignalsStatus | Unset = ListKnowledgeSignalsStatus.PENDING,
    limit: int | Unset = 100,
    tenant: str | Unset = UNSET,
) -> Error | KnowledgeSignalList | None:
    """List queued knowledge signals by status

     Admin-only curator view of captured knowledge signals awaiting review.

    Args:
        status (ListKnowledgeSignalsStatus | Unset):  Default: ListKnowledgeSignalsStatus.PENDING.
        limit (int | Unset):  Default: 100.
        tenant (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | KnowledgeSignalList
    """

    return (
        await asyncio_detailed(
            client=client,
            status=status,
            limit=limit,
            tenant=tenant,
        )
    ).parsed
