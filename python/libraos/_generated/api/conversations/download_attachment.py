from http import HTTPStatus
from io import BytesIO
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...types import File, Response


def _get_kwargs(
    cid: str,
    aid: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/conversations/{cid}/attachments/{aid}/download".format(
            cid=quote(str(cid), safe=""),
            aid=quote(str(aid), safe=""),
        ),
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | Error | File | None:
    if response.status_code == 200:
        response_200 = File(payload=BytesIO(response.content))

        return response_200

    if response.status_code == 302:
        response_302 = cast(Any, None)
        return response_302

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())

        return response_404

    if response.status_code == 410:
        response_410 = Error.from_dict(response.json())

        return response_410

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | Error | File]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    cid: str,
    aid: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any | Error | File]:
    """Download an attachment

     Stream the attachment bytes. Depending on operator configuration the response is either the bytes
    directly or a 302 redirect to a time-limited download URL.

    Args:
        cid (str):
        aid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error | File]
    """

    kwargs = _get_kwargs(
        cid=cid,
        aid=aid,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    cid: str,
    aid: str,
    *,
    client: AuthenticatedClient | Client,
) -> Any | Error | File | None:
    """Download an attachment

     Stream the attachment bytes. Depending on operator configuration the response is either the bytes
    directly or a 302 redirect to a time-limited download URL.

    Args:
        cid (str):
        aid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error | File
    """

    return sync_detailed(
        cid=cid,
        aid=aid,
        client=client,
    ).parsed


async def asyncio_detailed(
    cid: str,
    aid: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any | Error | File]:
    """Download an attachment

     Stream the attachment bytes. Depending on operator configuration the response is either the bytes
    directly or a 302 redirect to a time-limited download URL.

    Args:
        cid (str):
        aid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error | File]
    """

    kwargs = _get_kwargs(
        cid=cid,
        aid=aid,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    cid: str,
    aid: str,
    *,
    client: AuthenticatedClient | Client,
) -> Any | Error | File | None:
    """Download an attachment

     Stream the attachment bytes. Depending on operator configuration the response is either the bytes
    directly or a 302 redirect to a time-limited download URL.

    Args:
        cid (str):
        aid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error | File
    """

    return (
        await asyncio_detailed(
            cid=cid,
            aid=aid,
            client=client,
        )
    ).parsed
