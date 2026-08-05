from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.extract_document_files_body import ExtractDocumentFilesBody
from ...models.extract_request import ExtractRequest
from ...models.extract_response import ExtractResponse
from ...types import UNSET, Response


def _get_kwargs(
    *,
    body: ExtractDocumentFilesBody | ExtractRequest | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/managed/documents/extract",
    }

    if isinstance(body, ExtractDocumentFilesBody):
        _kwargs["files"] = body.to_multipart()

        headers["Content-Type"] = "multipart/form-data"
    if isinstance(body, ExtractRequest):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | ExtractResponse | None:
    if response.status_code == 200:
        response_200 = ExtractResponse.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

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


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Error | ExtractResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ExtractDocumentFilesBody | ExtractRequest | Unset = UNSET,
) -> Response[Error | ExtractResponse]:
    """Extract text from an office document

     Native text extraction for office and structured documents (DOCX, XLSX, ODT, text-layer PDF, CSV,
    JSON, XML, YAML, HTML, Markdown, EML). A filename with a recognised extension is required to route
    the parser. Scanned or image-only PDFs have no text layer — use /v1/managed/documents/ocr instead.

    Args:
        body (ExtractDocumentFilesBody):
        body (ExtractRequest): JSON alternative to the multipart upload for text extraction.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | ExtractResponse]
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
    body: ExtractDocumentFilesBody | ExtractRequest | Unset = UNSET,
) -> Error | ExtractResponse | None:
    """Extract text from an office document

     Native text extraction for office and structured documents (DOCX, XLSX, ODT, text-layer PDF, CSV,
    JSON, XML, YAML, HTML, Markdown, EML). A filename with a recognised extension is required to route
    the parser. Scanned or image-only PDFs have no text layer — use /v1/managed/documents/ocr instead.

    Args:
        body (ExtractDocumentFilesBody):
        body (ExtractRequest): JSON alternative to the multipart upload for text extraction.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | ExtractResponse
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ExtractDocumentFilesBody | ExtractRequest | Unset = UNSET,
) -> Response[Error | ExtractResponse]:
    """Extract text from an office document

     Native text extraction for office and structured documents (DOCX, XLSX, ODT, text-layer PDF, CSV,
    JSON, XML, YAML, HTML, Markdown, EML). A filename with a recognised extension is required to route
    the parser. Scanned or image-only PDFs have no text layer — use /v1/managed/documents/ocr instead.

    Args:
        body (ExtractDocumentFilesBody):
        body (ExtractRequest): JSON alternative to the multipart upload for text extraction.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | ExtractResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: ExtractDocumentFilesBody | ExtractRequest | Unset = UNSET,
) -> Error | ExtractResponse | None:
    """Extract text from an office document

     Native text extraction for office and structured documents (DOCX, XLSX, ODT, text-layer PDF, CSV,
    JSON, XML, YAML, HTML, Markdown, EML). A filename with a recognised extension is required to route
    the parser. Scanned or image-only PDFs have no text layer — use /v1/managed/documents/ocr instead.

    Args:
        body (ExtractDocumentFilesBody):
        body (ExtractRequest): JSON alternative to the multipart upload for text extraction.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | ExtractResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
