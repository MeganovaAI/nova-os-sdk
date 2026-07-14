from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.file_meta_list import FileMetaList
from ...models.list_files_recursive import ListFilesRecursive
from ...types import UNSET, Response, Unset


def _get_kwargs(
    tenant_id: str,
    session_id: str,
    *,
    mount: str | Unset = "/workspace",
    glob: str | Unset = UNSET,
    recursive: ListFilesRecursive | Unset = UNSET,
    limit: int | Unset = 100,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["mount"] = mount

    params["glob"] = glob

    json_recursive: str | Unset = UNSET
    if not isinstance(recursive, Unset):
        json_recursive = recursive.value

    params["recursive"] = json_recursive

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/managed/filesystem/{tenant_id}/{session_id}/files".format(
            tenant_id=quote(str(tenant_id), safe=""),
            session_id=quote(str(session_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Error | FileMetaList | None:
    if response.status_code == 200:
        response_200 = FileMetaList.from_dict(response.json())

        return response_200

    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())

        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Error | FileMetaList]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    tenant_id: str,
    session_id: str,
    *,
    client: AuthenticatedClient | Client,
    mount: str | Unset = "/workspace",
    glob: str | Unset = UNSET,
    recursive: ListFilesRecursive | Unset = UNSET,
    limit: int | Unset = 100,
) -> Response[Error | FileMetaList]:
    """List files in a workspace

    Args:
        tenant_id (str):
        session_id (str):
        mount (str | Unset):  Default: '/workspace'.
        glob (str | Unset):
        recursive (ListFilesRecursive | Unset):
        limit (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | FileMetaList]
    """

    kwargs = _get_kwargs(
        tenant_id=tenant_id,
        session_id=session_id,
        mount=mount,
        glob=glob,
        recursive=recursive,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    tenant_id: str,
    session_id: str,
    *,
    client: AuthenticatedClient | Client,
    mount: str | Unset = "/workspace",
    glob: str | Unset = UNSET,
    recursive: ListFilesRecursive | Unset = UNSET,
    limit: int | Unset = 100,
) -> Error | FileMetaList | None:
    """List files in a workspace

    Args:
        tenant_id (str):
        session_id (str):
        mount (str | Unset):  Default: '/workspace'.
        glob (str | Unset):
        recursive (ListFilesRecursive | Unset):
        limit (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | FileMetaList
    """

    return sync_detailed(
        tenant_id=tenant_id,
        session_id=session_id,
        client=client,
        mount=mount,
        glob=glob,
        recursive=recursive,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    tenant_id: str,
    session_id: str,
    *,
    client: AuthenticatedClient | Client,
    mount: str | Unset = "/workspace",
    glob: str | Unset = UNSET,
    recursive: ListFilesRecursive | Unset = UNSET,
    limit: int | Unset = 100,
) -> Response[Error | FileMetaList]:
    """List files in a workspace

    Args:
        tenant_id (str):
        session_id (str):
        mount (str | Unset):  Default: '/workspace'.
        glob (str | Unset):
        recursive (ListFilesRecursive | Unset):
        limit (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | FileMetaList]
    """

    kwargs = _get_kwargs(
        tenant_id=tenant_id,
        session_id=session_id,
        mount=mount,
        glob=glob,
        recursive=recursive,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    tenant_id: str,
    session_id: str,
    *,
    client: AuthenticatedClient | Client,
    mount: str | Unset = "/workspace",
    glob: str | Unset = UNSET,
    recursive: ListFilesRecursive | Unset = UNSET,
    limit: int | Unset = 100,
) -> Error | FileMetaList | None:
    """List files in a workspace

    Args:
        tenant_id (str):
        session_id (str):
        mount (str | Unset):  Default: '/workspace'.
        glob (str | Unset):
        recursive (ListFilesRecursive | Unset):
        limit (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | FileMetaList
    """

    return (
        await asyncio_detailed(
            tenant_id=tenant_id,
            session_id=session_id,
            client=client,
            mount=mount,
            glob=glob,
            recursive=recursive,
            limit=limit,
        )
    ).parsed
