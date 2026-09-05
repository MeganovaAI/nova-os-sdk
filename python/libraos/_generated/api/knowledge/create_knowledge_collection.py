from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_knowledge_collection_body import CreateKnowledgeCollectionBody
from ...models.error import Error
from ...types import Response


def _get_kwargs(
    *,
    body: CreateKnowledgeCollectionBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/knowledge/collections",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | Error | None:
    if response.status_code == 200:
        response_200 = cast(Any, None)
        return response_200

    if response.status_code == 201:
        response_201 = cast(Any, None)
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

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | Error]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: CreateKnowledgeCollectionBody,
) -> Response[Any | Error]:
    """Create a knowledge collection

     Admins may create any collection. A non-admin may create only `access_level: personal`, whose name
    is server-derived from the caller's email so the namespace cannot be squatted. Repeat calls are an
    idempotent 200 ensure.

    Args:
        body (CreateKnowledgeCollectionBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error]
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
    body: CreateKnowledgeCollectionBody,
) -> Any | Error | None:
    """Create a knowledge collection

     Admins may create any collection. A non-admin may create only `access_level: personal`, whose name
    is server-derived from the caller's email so the namespace cannot be squatted. Repeat calls are an
    idempotent 200 ensure.

    Args:
        body (CreateKnowledgeCollectionBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: CreateKnowledgeCollectionBody,
) -> Response[Any | Error]:
    """Create a knowledge collection

     Admins may create any collection. A non-admin may create only `access_level: personal`, whose name
    is server-derived from the caller's email so the namespace cannot be squatted. Repeat calls are an
    idempotent 200 ensure.

    Args:
        body (CreateKnowledgeCollectionBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: CreateKnowledgeCollectionBody,
) -> Any | Error | None:
    """Create a knowledge collection

     Admins may create any collection. A non-admin may create only `access_level: personal`, whose name
    is server-derived from the caller's email so the namespace cannot be squatted. Repeat calls are an
    idempotent 200 ensure.

    Args:
        body (CreateKnowledgeCollectionBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
