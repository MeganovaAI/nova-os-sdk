from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.add_attachment_body import AddAttachmentBody
from ...models.attachment import Attachment
from ...models.error import Error
from ...types import Response


def _get_kwargs(
    cid: str,
    *,
    body: AddAttachmentBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/conversations/{cid}/attachments".format(
            cid=quote(str(cid), safe=""),
        ),
    }

    _kwargs["files"] = body.to_multipart()

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Attachment | Error | None:
    if response.status_code == 201:
        response_201 = Attachment.from_dict(response.json())

        return response_201

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())

        return response_404

    if response.status_code == 409:
        response_409 = Error.from_dict(response.json())

        return response_409

    if response.status_code == 413:
        response_413 = Error.from_dict(response.json())

        return response_413

    if response.status_code == 415:
        response_415 = Error.from_dict(response.json())

        return response_415

    if response.status_code == 429:
        response_429 = Error.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Attachment | Error]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    cid: str,
    *,
    client: AuthenticatedClient | Client,
    body: AddAttachmentBody,
) -> Response[Attachment | Error]:
    """Attach a file to a conversation

     Upload a file scoped to a single conversation via multipart form. The caller must own the
    conversation; on first upload an unclaimed conversation id is claimed by the caller.

    Args:
        cid (str):
        body (AddAttachmentBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Attachment | Error]
    """

    kwargs = _get_kwargs(
        cid=cid,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    cid: str,
    *,
    client: AuthenticatedClient | Client,
    body: AddAttachmentBody,
) -> Attachment | Error | None:
    """Attach a file to a conversation

     Upload a file scoped to a single conversation via multipart form. The caller must own the
    conversation; on first upload an unclaimed conversation id is claimed by the caller.

    Args:
        cid (str):
        body (AddAttachmentBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Attachment | Error
    """

    return sync_detailed(
        cid=cid,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    cid: str,
    *,
    client: AuthenticatedClient | Client,
    body: AddAttachmentBody,
) -> Response[Attachment | Error]:
    """Attach a file to a conversation

     Upload a file scoped to a single conversation via multipart form. The caller must own the
    conversation; on first upload an unclaimed conversation id is claimed by the caller.

    Args:
        cid (str):
        body (AddAttachmentBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Attachment | Error]
    """

    kwargs = _get_kwargs(
        cid=cid,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    cid: str,
    *,
    client: AuthenticatedClient | Client,
    body: AddAttachmentBody,
) -> Attachment | Error | None:
    """Attach a file to a conversation

     Upload a file scoped to a single conversation via multipart form. The caller must own the
    conversation; on first upload an unclaimed conversation id is claimed by the caller.

    Args:
        cid (str):
        body (AddAttachmentBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Attachment | Error
    """

    return (
        await asyncio_detailed(
            cid=cid,
            client=client,
            body=body,
        )
    ).parsed
