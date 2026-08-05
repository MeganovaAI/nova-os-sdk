import datetime
from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.get_logs_level import GetLogsLevel
from ...models.get_logs_source import GetLogsSource
from ...models.log_list import LogList
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    source: GetLogsSource | Unset = GetLogsSource.SERVER,
    limit: int | Unset = 200,
    since: datetime.datetime | Unset = UNSET,
    level: GetLogsLevel | Unset = UNSET,
    q: str | Unset = UNSET,
    cursor: str | Unset = UNSET,
    request_id: str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_source: str | Unset = UNSET
    if not isinstance(source, Unset):
        json_source = source.value

    params["source"] = json_source

    params["limit"] = limit

    json_since: str | Unset = UNSET
    if not isinstance(since, Unset):
        json_since = since.isoformat()
    params["since"] = json_since

    json_level: str | Unset = UNSET
    if not isinstance(level, Unset):
        json_level = level.value

    params["level"] = json_level

    params["q"] = q

    params["cursor"] = cursor

    params["request_id"] = request_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/managed/logs",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Error | LogList | None:
    if response.status_code == 200:
        response_200 = LogList.from_dict(response.json())

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

    if response.status_code == 503:
        response_503 = Error.from_dict(response.json())

        return response_503

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Error | LogList]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    source: GetLogsSource | Unset = GetLogsSource.SERVER,
    limit: int | Unset = 200,
    since: datetime.datetime | Unset = UNSET,
    level: GetLogsLevel | Unset = UNSET,
    q: str | Unset = UNSET,
    cursor: str | Unset = UNSET,
    request_id: str | Unset = UNSET,
) -> Response[Error | LogList]:
    """Read server or request logs

     Paginated read of server logs (`source=server`, in-memory ring buffer, lost on restart) or request
    logs (`source=requests`, persisted call rows). Admin-only. 503 when disabled via the runtime hatch
    or when `source=requests` and persistent storage is not configured.

    Args:
        source (GetLogsSource | Unset):  Default: GetLogsSource.SERVER.
        limit (int | Unset):  Default: 200.
        since (datetime.datetime | Unset):
        level (GetLogsLevel | Unset):
        q (str | Unset):
        cursor (str | Unset):
        request_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | LogList]
    """

    kwargs = _get_kwargs(
        source=source,
        limit=limit,
        since=since,
        level=level,
        q=q,
        cursor=cursor,
        request_id=request_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    source: GetLogsSource | Unset = GetLogsSource.SERVER,
    limit: int | Unset = 200,
    since: datetime.datetime | Unset = UNSET,
    level: GetLogsLevel | Unset = UNSET,
    q: str | Unset = UNSET,
    cursor: str | Unset = UNSET,
    request_id: str | Unset = UNSET,
) -> Error | LogList | None:
    """Read server or request logs

     Paginated read of server logs (`source=server`, in-memory ring buffer, lost on restart) or request
    logs (`source=requests`, persisted call rows). Admin-only. 503 when disabled via the runtime hatch
    or when `source=requests` and persistent storage is not configured.

    Args:
        source (GetLogsSource | Unset):  Default: GetLogsSource.SERVER.
        limit (int | Unset):  Default: 200.
        since (datetime.datetime | Unset):
        level (GetLogsLevel | Unset):
        q (str | Unset):
        cursor (str | Unset):
        request_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | LogList
    """

    return sync_detailed(
        client=client,
        source=source,
        limit=limit,
        since=since,
        level=level,
        q=q,
        cursor=cursor,
        request_id=request_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    source: GetLogsSource | Unset = GetLogsSource.SERVER,
    limit: int | Unset = 200,
    since: datetime.datetime | Unset = UNSET,
    level: GetLogsLevel | Unset = UNSET,
    q: str | Unset = UNSET,
    cursor: str | Unset = UNSET,
    request_id: str | Unset = UNSET,
) -> Response[Error | LogList]:
    """Read server or request logs

     Paginated read of server logs (`source=server`, in-memory ring buffer, lost on restart) or request
    logs (`source=requests`, persisted call rows). Admin-only. 503 when disabled via the runtime hatch
    or when `source=requests` and persistent storage is not configured.

    Args:
        source (GetLogsSource | Unset):  Default: GetLogsSource.SERVER.
        limit (int | Unset):  Default: 200.
        since (datetime.datetime | Unset):
        level (GetLogsLevel | Unset):
        q (str | Unset):
        cursor (str | Unset):
        request_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | LogList]
    """

    kwargs = _get_kwargs(
        source=source,
        limit=limit,
        since=since,
        level=level,
        q=q,
        cursor=cursor,
        request_id=request_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    source: GetLogsSource | Unset = GetLogsSource.SERVER,
    limit: int | Unset = 200,
    since: datetime.datetime | Unset = UNSET,
    level: GetLogsLevel | Unset = UNSET,
    q: str | Unset = UNSET,
    cursor: str | Unset = UNSET,
    request_id: str | Unset = UNSET,
) -> Error | LogList | None:
    """Read server or request logs

     Paginated read of server logs (`source=server`, in-memory ring buffer, lost on restart) or request
    logs (`source=requests`, persisted call rows). Admin-only. 503 when disabled via the runtime hatch
    or when `source=requests` and persistent storage is not configured.

    Args:
        source (GetLogsSource | Unset):  Default: GetLogsSource.SERVER.
        limit (int | Unset):  Default: 200.
        since (datetime.datetime | Unset):
        level (GetLogsLevel | Unset):
        q (str | Unset):
        cursor (str | Unset):
        request_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | LogList
    """

    return (
        await asyncio_detailed(
            client=client,
            source=source,
            limit=limit,
            since=since,
            level=level,
            q=q,
            cursor=cursor,
            request_id=request_id,
        )
    ).parsed
