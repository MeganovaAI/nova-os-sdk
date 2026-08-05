from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.action_decision_request import ActionDecisionRequest
from ...models.action_envelope import ActionEnvelope
from ...models.approve_action_response_409 import ApproveActionResponse409
from ...models.error import Error
from ...types import UNSET, Response, Unset


def _get_kwargs(
    id: str,
    *,
    body: ActionDecisionRequest | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/managed/actions/{id}/approve".format(
            id=quote(str(id), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ActionEnvelope | ApproveActionResponse409 | Error | None:
    if response.status_code == 200:
        response_200 = ActionEnvelope.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = Error.from_dict(response.json())

        return response_403

    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())

        return response_404

    if response.status_code == 409:
        response_409 = ApproveActionResponse409.from_dict(response.json())

        return response_409

    if response.status_code == 429:
        response_429 = Error.from_dict(response.json())

        return response_429

    if response.status_code == 502:
        response_502 = Error.from_dict(response.json())

        return response_502

    if response.status_code == 503:
        response_503 = Error.from_dict(response.json())

        return response_503

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ActionEnvelope | ApproveActionResponse409 | Error]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ActionDecisionRequest | Unset = UNSET,
) -> Response[ActionEnvelope | ApproveActionResponse409 | Error]:
    """Approve and execute a pending action

     Atomically transitions the action pending→approved, then fires its webhook once. Admin or an
    approver/lead member of the action's group. The terminal outcome is carried in the returned action's
    `status` / `result` fields (HTTP 200 is returned whether execution succeeded or failed).

    Args:
        id (str):
        body (ActionDecisionRequest | Unset): Optional body carrying an approve/reject reason for
            the audit trail.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ActionEnvelope | ApproveActionResponse409 | Error]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ActionDecisionRequest | Unset = UNSET,
) -> ActionEnvelope | ApproveActionResponse409 | Error | None:
    """Approve and execute a pending action

     Atomically transitions the action pending→approved, then fires its webhook once. Admin or an
    approver/lead member of the action's group. The terminal outcome is carried in the returned action's
    `status` / `result` fields (HTTP 200 is returned whether execution succeeded or failed).

    Args:
        id (str):
        body (ActionDecisionRequest | Unset): Optional body carrying an approve/reject reason for
            the audit trail.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ActionEnvelope | ApproveActionResponse409 | Error
    """

    return sync_detailed(
        id=id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ActionDecisionRequest | Unset = UNSET,
) -> Response[ActionEnvelope | ApproveActionResponse409 | Error]:
    """Approve and execute a pending action

     Atomically transitions the action pending→approved, then fires its webhook once. Admin or an
    approver/lead member of the action's group. The terminal outcome is carried in the returned action's
    `status` / `result` fields (HTTP 200 is returned whether execution succeeded or failed).

    Args:
        id (str):
        body (ActionDecisionRequest | Unset): Optional body carrying an approve/reject reason for
            the audit trail.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ActionEnvelope | ApproveActionResponse409 | Error]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ActionDecisionRequest | Unset = UNSET,
) -> ActionEnvelope | ApproveActionResponse409 | Error | None:
    """Approve and execute a pending action

     Atomically transitions the action pending→approved, then fires its webhook once. Admin or an
    approver/lead member of the action's group. The terminal outcome is carried in the returned action's
    `status` / `result` fields (HTTP 200 is returned whether execution succeeded or failed).

    Args:
        id (str):
        body (ActionDecisionRequest | Unset): Optional body carrying an approve/reject reason for
            the audit trail.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ActionEnvelope | ApproveActionResponse409 | Error
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            body=body,
        )
    ).parsed
