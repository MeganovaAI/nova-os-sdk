from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.ocr_document_files_body import OcrDocumentFilesBody
from ...models.ocr_request import OcrRequest
from ...models.ocr_response import OcrResponse
from ...types import UNSET, Response


def _get_kwargs(
    *,
    body: OcrDocumentFilesBody | OcrRequest | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/managed/documents/ocr",
    }

    if isinstance(body, OcrDocumentFilesBody):
        _kwargs["files"] = body.to_multipart()

        headers["Content-Type"] = "multipart/form-data"
    if isinstance(body, OcrRequest):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Error | OcrResponse | None:
    if response.status_code == 200:
        response_200 = OcrResponse.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = Error.from_dict(response.json())

        return response_403

    if response.status_code == 413:
        response_413 = Error.from_dict(response.json())

        return response_413

    if response.status_code == 415:
        response_415 = Error.from_dict(response.json())

        return response_415

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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Error | OcrResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: OcrDocumentFilesBody | OcrRequest | Unset = UNSET,
) -> Response[Error | OcrResponse]:
    """OCR a scanned or image-only PDF into markdown

    Args:
        body (OcrDocumentFilesBody):
        body (OcrRequest): JSON alternative to the multipart upload for OCR.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | OcrResponse]
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
    body: OcrDocumentFilesBody | OcrRequest | Unset = UNSET,
) -> Error | OcrResponse | None:
    """OCR a scanned or image-only PDF into markdown

    Args:
        body (OcrDocumentFilesBody):
        body (OcrRequest): JSON alternative to the multipart upload for OCR.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | OcrResponse
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: OcrDocumentFilesBody | OcrRequest | Unset = UNSET,
) -> Response[Error | OcrResponse]:
    """OCR a scanned or image-only PDF into markdown

    Args:
        body (OcrDocumentFilesBody):
        body (OcrRequest): JSON alternative to the multipart upload for OCR.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | OcrResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: OcrDocumentFilesBody | OcrRequest | Unset = UNSET,
) -> Error | OcrResponse | None:
    """OCR a scanned or image-only PDF into markdown

    Args:
        body (OcrDocumentFilesBody):
        body (OcrRequest): JSON alternative to the multipart upload for OCR.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | OcrResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
