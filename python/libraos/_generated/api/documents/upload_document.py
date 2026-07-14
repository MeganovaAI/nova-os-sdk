from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.document import Document
from ...models.error import Error
from ...models.upload_document_body import UploadDocumentBody
from ...types import Response


def _get_kwargs(
    *,
    body: UploadDocumentBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/managed/documents/upload",
    }

    _kwargs["files"] = body.to_multipart()

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Document | Error | None:
    if response.status_code == 201:
        response_201 = Document.from_dict(response.json())

        return response_201

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Document | Error]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: UploadDocumentBody,
) -> Response[Document | Error]:
    """Upload a document

    Args:
        body (UploadDocumentBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Document | Error]
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
    body: UploadDocumentBody,
) -> Document | Error | None:
    """Upload a document

    Args:
        body (UploadDocumentBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Document | Error
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: UploadDocumentBody,
) -> Response[Document | Error]:
    """Upload a document

    Args:
        body (UploadDocumentBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Document | Error]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: UploadDocumentBody,
) -> Document | Error | None:
    """Upload a document

    Args:
        body (UploadDocumentBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Document | Error
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
