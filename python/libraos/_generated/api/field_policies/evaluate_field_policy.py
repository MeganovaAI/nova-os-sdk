from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.field_evaluate_request import FieldEvaluateRequest
from ...models.field_evaluate_response import FieldEvaluateResponse
from ...types import Response


def _get_kwargs(
    type_: str,
    *,
    body: FieldEvaluateRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/managed/field-policies/{type_}/evaluate".format(
            type_=quote(str(type_), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | FieldEvaluateResponse | None:
    if response.status_code == 200:
        response_200 = FieldEvaluateResponse.from_dict(response.json())

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
) -> Response[Error | FieldEvaluateResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    type_: str,
    *,
    client: AuthenticatedClient | Client,
    body: FieldEvaluateRequest,
) -> Response[Error | FieldEvaluateResponse]:
    r"""Evaluate field access for a caller against a record

     Admin-only canonical reference. Computes the caller's visible/writable fields for the record type
    and returns the enforced view. With `mode` omitted (read) the response strips non-visible fields and
    audits the access; with `mode:\"write\"` it filters to writable fields. A missing policy fails
    closed (nothing visible, nothing writable).

    Args:
        type_ (str):
        body (FieldEvaluateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | FieldEvaluateResponse]
    """

    kwargs = _get_kwargs(
        type_=type_,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    type_: str,
    *,
    client: AuthenticatedClient | Client,
    body: FieldEvaluateRequest,
) -> Error | FieldEvaluateResponse | None:
    r"""Evaluate field access for a caller against a record

     Admin-only canonical reference. Computes the caller's visible/writable fields for the record type
    and returns the enforced view. With `mode` omitted (read) the response strips non-visible fields and
    audits the access; with `mode:\"write\"` it filters to writable fields. A missing policy fails
    closed (nothing visible, nothing writable).

    Args:
        type_ (str):
        body (FieldEvaluateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | FieldEvaluateResponse
    """

    return sync_detailed(
        type_=type_,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    type_: str,
    *,
    client: AuthenticatedClient | Client,
    body: FieldEvaluateRequest,
) -> Response[Error | FieldEvaluateResponse]:
    r"""Evaluate field access for a caller against a record

     Admin-only canonical reference. Computes the caller's visible/writable fields for the record type
    and returns the enforced view. With `mode` omitted (read) the response strips non-visible fields and
    audits the access; with `mode:\"write\"` it filters to writable fields. A missing policy fails
    closed (nothing visible, nothing writable).

    Args:
        type_ (str):
        body (FieldEvaluateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | FieldEvaluateResponse]
    """

    kwargs = _get_kwargs(
        type_=type_,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    type_: str,
    *,
    client: AuthenticatedClient | Client,
    body: FieldEvaluateRequest,
) -> Error | FieldEvaluateResponse | None:
    r"""Evaluate field access for a caller against a record

     Admin-only canonical reference. Computes the caller's visible/writable fields for the record type
    and returns the enforced view. With `mode` omitted (read) the response strips non-visible fields and
    audits the access; with `mode:\"write\"` it filters to writable fields. A missing policy fails
    closed (nothing visible, nothing writable).

    Args:
        type_ (str):
        body (FieldEvaluateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | FieldEvaluateResponse
    """

    return (
        await asyncio_detailed(
            type_=type_,
            client=client,
            body=body,
        )
    ).parsed
