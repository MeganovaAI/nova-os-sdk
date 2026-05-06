from http import HTTPStatus
from io import BytesIO
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...types import File, Response


def _get_kwargs(
    tenant_id: str,
    session_id: str,
    path: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/managed/filesystem/{tenant_id}/{session_id}/files/{path}".format(
            tenant_id=quote(str(tenant_id), safe=""),
            session_id=quote(str(session_id), safe=""),
            path=quote(str(path), safe=""),
        ),
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Error | File | None:
    if response.status_code == 200:
        response_200 = File(payload=BytesIO(response.content))

        return response_200

    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())

        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Error | File]:
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
) -> Response[Error | File]:
    """Read a file's raw bytes

    Args:
        tenant_id (str):
        session_id (str):
        path (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | File]
    """

    kwargs = _get_kwargs(
        tenant_id=tenant_id,
        session_id=session_id,
        path=path,
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
) -> Error | File | None:
    """Read a file's raw bytes

    Args:
        tenant_id (str):
        session_id (str):
        path (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | File
    """

    return sync_detailed(
        tenant_id=tenant_id,
        session_id=session_id,
        path=path,
        client=client,
    ).parsed


async def asyncio_detailed(
    tenant_id: str,
    session_id: str,
    path: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Error | File]:
    """Read a file's raw bytes

    Args:
        tenant_id (str):
        session_id (str):
        path (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | File]
    """

    kwargs = _get_kwargs(
        tenant_id=tenant_id,
        session_id=session_id,
        path=path,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    tenant_id: str,
    session_id: str,
    path: str,
    *,
    client: AuthenticatedClient | Client,
) -> Error | File | None:
    """Read a file's raw bytes

    Args:
        tenant_id (str):
        session_id (str):
        path (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | File
    """

    return (
        await asyncio_detailed(
            tenant_id=tenant_id,
            session_id=session_id,
            path=path,
            client=client,
        )
    ).parsed
