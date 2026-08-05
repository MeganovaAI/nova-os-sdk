from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.scim_error import ScimError
from ...models.scim_list_response import ScimListResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    filter_: str | Unset = UNSET,
    start_index: int | Unset = 1,
    count: int | Unset = 100,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["filter"] = filter_

    params["startIndex"] = start_index

    params["count"] = count

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/scim/v2/Users",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | ScimError | ScimListResponse | None:
    if response.status_code == 200:
        response_200 = ScimListResponse.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = ScimError.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Error | ScimError | ScimListResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    filter_: str | Unset = UNSET,
    start_index: int | Unset = 1,
    count: int | Unset = 100,
) -> Response[Error | ScimError | ScimListResponse]:
    r"""List / query SCIM users

     Lists provisioned users. Supports the `userName eq \"value\"` filter IdPs send for correlation, plus
    `startIndex`/`count` pagination (count capped at 200).

    Args:
        filter_ (str | Unset):
        start_index (int | Unset):  Default: 1.
        count (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | ScimError | ScimListResponse]
    """

    kwargs = _get_kwargs(
        filter_=filter_,
        start_index=start_index,
        count=count,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    filter_: str | Unset = UNSET,
    start_index: int | Unset = 1,
    count: int | Unset = 100,
) -> Error | ScimError | ScimListResponse | None:
    r"""List / query SCIM users

     Lists provisioned users. Supports the `userName eq \"value\"` filter IdPs send for correlation, plus
    `startIndex`/`count` pagination (count capped at 200).

    Args:
        filter_ (str | Unset):
        start_index (int | Unset):  Default: 1.
        count (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | ScimError | ScimListResponse
    """

    return sync_detailed(
        client=client,
        filter_=filter_,
        start_index=start_index,
        count=count,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    filter_: str | Unset = UNSET,
    start_index: int | Unset = 1,
    count: int | Unset = 100,
) -> Response[Error | ScimError | ScimListResponse]:
    r"""List / query SCIM users

     Lists provisioned users. Supports the `userName eq \"value\"` filter IdPs send for correlation, plus
    `startIndex`/`count` pagination (count capped at 200).

    Args:
        filter_ (str | Unset):
        start_index (int | Unset):  Default: 1.
        count (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | ScimError | ScimListResponse]
    """

    kwargs = _get_kwargs(
        filter_=filter_,
        start_index=start_index,
        count=count,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    filter_: str | Unset = UNSET,
    start_index: int | Unset = 1,
    count: int | Unset = 100,
) -> Error | ScimError | ScimListResponse | None:
    r"""List / query SCIM users

     Lists provisioned users. Supports the `userName eq \"value\"` filter IdPs send for correlation, plus
    `startIndex`/`count` pagination (count capped at 200).

    Args:
        filter_ (str | Unset):
        start_index (int | Unset):  Default: 1.
        count (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | ScimError | ScimListResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            filter_=filter_,
            start_index=start_index,
            count=count,
        )
    ).parsed
