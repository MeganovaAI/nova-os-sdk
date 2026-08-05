from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.file_object import FileObject
from ...models.upload_file_body import UploadFileBody
from ...types import Response


def _get_kwargs(
    *,
    body: UploadFileBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/files",
    }

    _kwargs["files"] = body.to_multipart()

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Error | FileObject | None:
    if response.status_code == 200:
        response_200 = FileObject.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 503:
        response_503 = Error.from_dict(response.json())

        return response_503

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Error | FileObject]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: UploadFileBody,
) -> Response[Error | FileObject]:
    """Upload a file

     Upload a file via multipart form. The file text is extracted and indexed into the caller's knowledge
    collection so subsequent chat turns can retrieve it. OpenAI Files API compatible.

    Args:
        body (UploadFileBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | FileObject]
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
    body: UploadFileBody,
) -> Error | FileObject | None:
    """Upload a file

     Upload a file via multipart form. The file text is extracted and indexed into the caller's knowledge
    collection so subsequent chat turns can retrieve it. OpenAI Files API compatible.

    Args:
        body (UploadFileBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | FileObject
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: UploadFileBody,
) -> Response[Error | FileObject]:
    """Upload a file

     Upload a file via multipart form. The file text is extracted and indexed into the caller's knowledge
    collection so subsequent chat turns can retrieve it. OpenAI Files API compatible.

    Args:
        body (UploadFileBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | FileObject]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: UploadFileBody,
) -> Error | FileObject | None:
    """Upload a file

     Upload a file via multipart form. The file text is extracted and indexed into the caller's knowledge
    collection so subsequent chat turns can retrieve it. OpenAI Files API compatible.

    Args:
        body (UploadFileBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | FileObject
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
