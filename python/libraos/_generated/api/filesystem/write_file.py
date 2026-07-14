from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.file_meta import FileMeta
from ...types import UNSET, File, Response, Unset


def _get_kwargs(
    tenant_id: str,
    session_id: str,
    path: str,
    *,
    body: File,
    if_match: str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(if_match, Unset):
        headers["If-Match"] = if_match

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/v1/managed/filesystem/{tenant_id}/{session_id}/files/{path}".format(
            tenant_id=quote(str(tenant_id), safe=""),
            session_id=quote(str(session_id), safe=""),
            path=quote(str(path), safe=""),
        ),
    }

    _kwargs["content"] = body.payload

    headers["Content-Type"] = "application/octet-stream"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | Error | FileMeta | None:
    if response.status_code == 200:
        response_200 = FileMeta.from_dict(response.json())

        return response_200

    if response.status_code == 403:
        response_403 = Error.from_dict(response.json())

        return response_403

    if response.status_code == 412:
        response_412 = cast(Any, None)
        return response_412

    if response.status_code == 507:
        response_507 = cast(Any, None)
        return response_507

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | Error | FileMeta]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    tenant_id: str,
    session_id: str,
    path: str,
    *,
    client: AuthenticatedClient | Client,
    body: File,
    if_match: str | Unset = UNSET,
) -> Response[Any | Error | FileMeta]:
    """Write or overwrite a file

    Args:
        tenant_id (str):
        session_id (str):
        path (str):
        if_match (str | Unset):
        body (File):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error | FileMeta]
    """

    kwargs = _get_kwargs(
        tenant_id=tenant_id,
        session_id=session_id,
        path=path,
        body=body,
        if_match=if_match,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    tenant_id: str,
    session_id: str,
    path: str,
    *,
    client: AuthenticatedClient | Client,
    body: File,
    if_match: str | Unset = UNSET,
) -> Any | Error | FileMeta | None:
    """Write or overwrite a file

    Args:
        tenant_id (str):
        session_id (str):
        path (str):
        if_match (str | Unset):
        body (File):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error | FileMeta
    """

    return sync_detailed(
        tenant_id=tenant_id,
        session_id=session_id,
        path=path,
        client=client,
        body=body,
        if_match=if_match,
    ).parsed


async def asyncio_detailed(
    tenant_id: str,
    session_id: str,
    path: str,
    *,
    client: AuthenticatedClient | Client,
    body: File,
    if_match: str | Unset = UNSET,
) -> Response[Any | Error | FileMeta]:
    """Write or overwrite a file

    Args:
        tenant_id (str):
        session_id (str):
        path (str):
        if_match (str | Unset):
        body (File):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error | FileMeta]
    """

    kwargs = _get_kwargs(
        tenant_id=tenant_id,
        session_id=session_id,
        path=path,
        body=body,
        if_match=if_match,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    tenant_id: str,
    session_id: str,
    path: str,
    *,
    client: AuthenticatedClient | Client,
    body: File,
    if_match: str | Unset = UNSET,
) -> Any | Error | FileMeta | None:
    """Write or overwrite a file

    Args:
        tenant_id (str):
        session_id (str):
        path (str):
        if_match (str | Unset):
        body (File):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error | FileMeta
    """

    return (
        await asyncio_detailed(
            tenant_id=tenant_id,
            session_id=session_id,
            path=path,
            client=client,
            body=body,
            if_match=if_match,
        )
    ).parsed
