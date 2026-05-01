from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...types import UNSET, Response, Unset


def _get_kwargs(
    employee_id: str,
    *,
    include_knowledge: bool | Unset = True,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["include_knowledge"] = include_knowledge

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/managed/employees/{employee_id}/bundle/export".format(
            employee_id=quote(str(employee_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Error | None:
    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())

        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Error]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    employee_id: str,
    *,
    client: AuthenticatedClient | Client,
    include_knowledge: bool | Unset = True,
) -> Response[Error]:
    """Download a portable .nova-bundle.zip

    Args:
        employee_id (str):
        include_knowledge (bool | Unset):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error]
    """

    kwargs = _get_kwargs(
        employee_id=employee_id,
        include_knowledge=include_knowledge,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    employee_id: str,
    *,
    client: AuthenticatedClient | Client,
    include_knowledge: bool | Unset = True,
) -> Error | None:
    """Download a portable .nova-bundle.zip

    Args:
        employee_id (str):
        include_knowledge (bool | Unset):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error
    """

    return sync_detailed(
        employee_id=employee_id,
        client=client,
        include_knowledge=include_knowledge,
    ).parsed


async def asyncio_detailed(
    employee_id: str,
    *,
    client: AuthenticatedClient | Client,
    include_knowledge: bool | Unset = True,
) -> Response[Error]:
    """Download a portable .nova-bundle.zip

    Args:
        employee_id (str):
        include_knowledge (bool | Unset):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error]
    """

    kwargs = _get_kwargs(
        employee_id=employee_id,
        include_knowledge=include_knowledge,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    employee_id: str,
    *,
    client: AuthenticatedClient | Client,
    include_knowledge: bool | Unset = True,
) -> Error | None:
    """Download a portable .nova-bundle.zip

    Args:
        employee_id (str):
        include_knowledge (bool | Unset):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error
    """

    return (
        await asyncio_detailed(
            employee_id=employee_id,
            client=client,
            include_knowledge=include_knowledge,
        )
    ).parsed
