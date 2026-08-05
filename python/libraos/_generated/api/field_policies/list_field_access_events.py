import datetime
from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.field_access_event_list import FieldAccessEventList
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    record_type: str | Unset = UNSET,
    record_id: str | Unset = UNSET,
    since: datetime.datetime | Unset = UNSET,
    limit: int | Unset = 200,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["record_type"] = record_type

    params["record_id"] = record_id

    json_since: str | Unset = UNSET
    if not isinstance(since, Unset):
        json_since = since.isoformat()
    params["since"] = json_since

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/managed/field-access-events",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | FieldAccessEventList | None:
    if response.status_code == 200:
        response_200 = FieldAccessEventList.from_dict(response.json())

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
) -> Response[Error | FieldAccessEventList]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    record_type: str | Unset = UNSET,
    record_id: str | Unset = UNSET,
    since: datetime.datetime | Unset = UNSET,
    limit: int | Unset = 200,
) -> Response[Error | FieldAccessEventList]:
    """Query the field-access audit log

     Admin-only. Append-only record of sensitive-field access, scoped to the request tenant.

    Args:
        record_type (str | Unset):
        record_id (str | Unset):
        since (datetime.datetime | Unset):
        limit (int | Unset):  Default: 200.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | FieldAccessEventList]
    """

    kwargs = _get_kwargs(
        record_type=record_type,
        record_id=record_id,
        since=since,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    record_type: str | Unset = UNSET,
    record_id: str | Unset = UNSET,
    since: datetime.datetime | Unset = UNSET,
    limit: int | Unset = 200,
) -> Error | FieldAccessEventList | None:
    """Query the field-access audit log

     Admin-only. Append-only record of sensitive-field access, scoped to the request tenant.

    Args:
        record_type (str | Unset):
        record_id (str | Unset):
        since (datetime.datetime | Unset):
        limit (int | Unset):  Default: 200.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | FieldAccessEventList
    """

    return sync_detailed(
        client=client,
        record_type=record_type,
        record_id=record_id,
        since=since,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    record_type: str | Unset = UNSET,
    record_id: str | Unset = UNSET,
    since: datetime.datetime | Unset = UNSET,
    limit: int | Unset = 200,
) -> Response[Error | FieldAccessEventList]:
    """Query the field-access audit log

     Admin-only. Append-only record of sensitive-field access, scoped to the request tenant.

    Args:
        record_type (str | Unset):
        record_id (str | Unset):
        since (datetime.datetime | Unset):
        limit (int | Unset):  Default: 200.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | FieldAccessEventList]
    """

    kwargs = _get_kwargs(
        record_type=record_type,
        record_id=record_id,
        since=since,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    record_type: str | Unset = UNSET,
    record_id: str | Unset = UNSET,
    since: datetime.datetime | Unset = UNSET,
    limit: int | Unset = 200,
) -> Error | FieldAccessEventList | None:
    """Query the field-access audit log

     Admin-only. Append-only record of sensitive-field access, scoped to the request tenant.

    Args:
        record_type (str | Unset):
        record_id (str | Unset):
        since (datetime.datetime | Unset):
        limit (int | Unset):  Default: 200.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | FieldAccessEventList
    """

    return (
        await asyncio_detailed(
            client=client,
            record_type=record_type,
            record_id=record_id,
            since=since,
            limit=limit,
        )
    ).parsed
