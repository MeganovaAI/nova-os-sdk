from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.action_envelope import ActionEnvelope
from ...models.create_action_request import CreateActionRequest
from ...models.error import Error
from ...types import Response


def _get_kwargs(
    *,
    body: CreateActionRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/managed/actions",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> ActionEnvelope | Error | None:
    if response.status_code == 201:
        response_201 = ActionEnvelope.from_dict(response.json())

        return response_201

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400

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
) -> Response[ActionEnvelope | Error]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: CreateActionRequest,
) -> Response[ActionEnvelope | Error]:
    """Park a connector-sourced action for approval

     Lets an external connector submit a side-effecting action for human approval. Requires an admin-role
    credential. The callback webhook is snapshotted onto the row and fired only when the action is
    approved; `callback.auth.secret_ref` names an environment variable on the server holding the shared
    HMAC secret — the secret itself is never transmitted.

    Args:
        body (CreateActionRequest): Body for a connector parking an action for approval.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ActionEnvelope | Error]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: CreateActionRequest,
) -> ActionEnvelope | Error | None:
    """Park a connector-sourced action for approval

     Lets an external connector submit a side-effecting action for human approval. Requires an admin-role
    credential. The callback webhook is snapshotted onto the row and fired only when the action is
    approved; `callback.auth.secret_ref` names an environment variable on the server holding the shared
    HMAC secret — the secret itself is never transmitted.

    Args:
        body (CreateActionRequest): Body for a connector parking an action for approval.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ActionEnvelope | Error
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: CreateActionRequest,
) -> Response[ActionEnvelope | Error]:
    """Park a connector-sourced action for approval

     Lets an external connector submit a side-effecting action for human approval. Requires an admin-role
    credential. The callback webhook is snapshotted onto the row and fired only when the action is
    approved; `callback.auth.secret_ref` names an environment variable on the server holding the shared
    HMAC secret — the secret itself is never transmitted.

    Args:
        body (CreateActionRequest): Body for a connector parking an action for approval.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ActionEnvelope | Error]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: CreateActionRequest,
) -> ActionEnvelope | Error | None:
    """Park a connector-sourced action for approval

     Lets an external connector submit a side-effecting action for human approval. Requires an admin-role
    credential. The callback webhook is snapshotted onto the row and fired only when the action is
    approved; `callback.auth.secret_ref` names an environment variable on the server holding the shared
    HMAC secret — the secret itself is never transmitted.

    Args:
        body (CreateActionRequest): Body for a connector parking an action for approval.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ActionEnvelope | Error
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
