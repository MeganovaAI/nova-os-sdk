from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.manifest import Manifest
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    if_none_match: str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(if_none_match, Unset):
        headers["If-None-Match"] = if_none_match

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/agents/v1/personas",
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | Manifest | None:
    if response.status_code == 200:
        response_200 = Manifest.from_dict(response.json())

        return response_200

    if response.status_code == 304:
        response_304 = cast(Any, None)
        return response_304

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | Manifest]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    if_none_match: str | Unset = UNSET,
) -> Response[Any | Manifest]:
    """Boot-time persona manifest with ETag round-trip

     Returns the manifest envelope (`manifest_version` sha256 + every
    registered persona). Partners cache by `manifest_version` and
    send `If-None-Match` on subsequent fetches; the server replies
    304 with no body when the manifest hasn't changed.

    Args:
        if_none_match (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Manifest]
    """

    kwargs = _get_kwargs(
        if_none_match=if_none_match,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    if_none_match: str | Unset = UNSET,
) -> Any | Manifest | None:
    """Boot-time persona manifest with ETag round-trip

     Returns the manifest envelope (`manifest_version` sha256 + every
    registered persona). Partners cache by `manifest_version` and
    send `If-None-Match` on subsequent fetches; the server replies
    304 with no body when the manifest hasn't changed.

    Args:
        if_none_match (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Manifest
    """

    return sync_detailed(
        client=client,
        if_none_match=if_none_match,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    if_none_match: str | Unset = UNSET,
) -> Response[Any | Manifest]:
    """Boot-time persona manifest with ETag round-trip

     Returns the manifest envelope (`manifest_version` sha256 + every
    registered persona). Partners cache by `manifest_version` and
    send `If-None-Match` on subsequent fetches; the server replies
    304 with no body when the manifest hasn't changed.

    Args:
        if_none_match (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Manifest]
    """

    kwargs = _get_kwargs(
        if_none_match=if_none_match,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    if_none_match: str | Unset = UNSET,
) -> Any | Manifest | None:
    """Boot-time persona manifest with ETag round-trip

     Returns the manifest envelope (`manifest_version` sha256 + every
    registered persona). Partners cache by `manifest_version` and
    send `If-None-Match` on subsequent fetches; the server replies
    304 with no body when the manifest hasn't changed.

    Args:
        if_none_match (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Manifest
    """

    return (
        await asyncio_detailed(
            client=client,
            if_none_match=if_none_match,
        )
    ).parsed
