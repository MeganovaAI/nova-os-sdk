from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.knowledge_signal_mutation import KnowledgeSignalMutation
from ...models.promote_knowledge_signal_body import PromoteKnowledgeSignalBody
from ...types import UNSET, Response, Unset


def _get_kwargs(
    id: str,
    *,
    body: PromoteKnowledgeSignalBody | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/managed/knowledge-signals/{id}/promote".format(
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
) -> Error | KnowledgeSignalMutation | None:
    if response.status_code == 200:
        response_200 = KnowledgeSignalMutation.from_dict(response.json())

        return response_200

    if response.status_code == 202:
        response_202 = KnowledgeSignalMutation.from_dict(response.json())

        return response_202

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
        response_409 = Error.from_dict(response.json())

        return response_409

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
) -> Response[Error | KnowledgeSignalMutation]:
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
    body: PromoteKnowledgeSignalBody | Unset = UNSET,
) -> Response[Error | KnowledgeSignalMutation]:
    """Publish a reviewed knowledge signal

     Admin-only, idempotent publication into the knowledge store. The signal becomes promoted only after
    indexing succeeds and an immutable receipt is committed. Repeating a completed request returns the
    same receipt.

    Args:
        id (str):
        body (PromoteKnowledgeSignalBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | KnowledgeSignalMutation]
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
    body: PromoteKnowledgeSignalBody | Unset = UNSET,
) -> Error | KnowledgeSignalMutation | None:
    """Publish a reviewed knowledge signal

     Admin-only, idempotent publication into the knowledge store. The signal becomes promoted only after
    indexing succeeds and an immutable receipt is committed. Repeating a completed request returns the
    same receipt.

    Args:
        id (str):
        body (PromoteKnowledgeSignalBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | KnowledgeSignalMutation
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
    body: PromoteKnowledgeSignalBody | Unset = UNSET,
) -> Response[Error | KnowledgeSignalMutation]:
    """Publish a reviewed knowledge signal

     Admin-only, idempotent publication into the knowledge store. The signal becomes promoted only after
    indexing succeeds and an immutable receipt is committed. Repeating a completed request returns the
    same receipt.

    Args:
        id (str):
        body (PromoteKnowledgeSignalBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | KnowledgeSignalMutation]
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
    body: PromoteKnowledgeSignalBody | Unset = UNSET,
) -> Error | KnowledgeSignalMutation | None:
    """Publish a reviewed knowledge signal

     Admin-only, idempotent publication into the knowledge store. The signal becomes promoted only after
    indexing succeeds and an immutable receipt is committed. Repeating a completed request returns the
    same receipt.

    Args:
        id (str):
        body (PromoteKnowledgeSignalBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | KnowledgeSignalMutation
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            body=body,
        )
    ).parsed
