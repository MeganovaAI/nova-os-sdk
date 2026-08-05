from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.action_list import ActionList
from ...models.error import Error
from ...models.list_actions_status import ListActionsStatus
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    status: ListActionsStatus | Unset = UNSET,
    source: str | Unset = UNSET,
    external_ref: str | Unset = UNSET,
    limit: int | Unset = 50,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_status: str | Unset = UNSET
    if not isinstance(status, Unset):
        json_status = status.value

    params["status"] = json_status

    params["source"] = source

    params["external_ref"] = external_ref

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/managed/actions",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> ActionList | Error | None:
    if response.status_code == 200:
        response_200 = ActionList.from_dict(response.json())

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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[ActionList | Error]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    status: ListActionsStatus | Unset = UNSET,
    source: str | Unset = UNSET,
    external_ref: str | Unset = UNSET,
    limit: int | Unset = 50,
) -> Response[ActionList | Error]:
    """List pending actions in the approval queue

     Admins see every action; a group member sees only actions carrying a group_id for a group they
    belong to. Requires the pending-actions feature to be enabled.

    Args:
        status (ListActionsStatus | Unset):
        source (str | Unset):
        external_ref (str | Unset):
        limit (int | Unset):  Default: 50.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ActionList | Error]
    """

    kwargs = _get_kwargs(
        status=status,
        source=source,
        external_ref=external_ref,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    status: ListActionsStatus | Unset = UNSET,
    source: str | Unset = UNSET,
    external_ref: str | Unset = UNSET,
    limit: int | Unset = 50,
) -> ActionList | Error | None:
    """List pending actions in the approval queue

     Admins see every action; a group member sees only actions carrying a group_id for a group they
    belong to. Requires the pending-actions feature to be enabled.

    Args:
        status (ListActionsStatus | Unset):
        source (str | Unset):
        external_ref (str | Unset):
        limit (int | Unset):  Default: 50.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ActionList | Error
    """

    return sync_detailed(
        client=client,
        status=status,
        source=source,
        external_ref=external_ref,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    status: ListActionsStatus | Unset = UNSET,
    source: str | Unset = UNSET,
    external_ref: str | Unset = UNSET,
    limit: int | Unset = 50,
) -> Response[ActionList | Error]:
    """List pending actions in the approval queue

     Admins see every action; a group member sees only actions carrying a group_id for a group they
    belong to. Requires the pending-actions feature to be enabled.

    Args:
        status (ListActionsStatus | Unset):
        source (str | Unset):
        external_ref (str | Unset):
        limit (int | Unset):  Default: 50.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ActionList | Error]
    """

    kwargs = _get_kwargs(
        status=status,
        source=source,
        external_ref=external_ref,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    status: ListActionsStatus | Unset = UNSET,
    source: str | Unset = UNSET,
    external_ref: str | Unset = UNSET,
    limit: int | Unset = 50,
) -> ActionList | Error | None:
    """List pending actions in the approval queue

     Admins see every action; a group member sees only actions carrying a group_id for a group they
    belong to. Requires the pending-actions feature to be enabled.

    Args:
        status (ListActionsStatus | Unset):
        source (str | Unset):
        external_ref (str | Unset):
        limit (int | Unset):  Default: 50.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ActionList | Error
    """

    return (
        await asyncio_detailed(
            client=client,
            status=status,
            source=source,
            external_ref=external_ref,
            limit=limit,
        )
    ).parsed
