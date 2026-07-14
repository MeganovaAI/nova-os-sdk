from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.field_policy import FieldPolicy
from ...types import Response


def _get_kwargs(
    type_: str,
    *,
    body: FieldPolicy,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/v1/managed/field-policies/{type_}".format(
            type_=quote(str(type_), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Error | FieldPolicy | None:
    if response.status_code == 200:
        response_200 = FieldPolicy.from_dict(response.json())

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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Error | FieldPolicy]:
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
    body: FieldPolicy,
) -> Response[Error | FieldPolicy]:
    """Create or replace the field policy for a record type

     Admin-only. Upserts the policy for `(tenant, type)`.

    Args:
        type_ (str):
        body (FieldPolicy): Declarative per-(tenant, record type) field-access policy.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | FieldPolicy]
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
    body: FieldPolicy,
) -> Error | FieldPolicy | None:
    """Create or replace the field policy for a record type

     Admin-only. Upserts the policy for `(tenant, type)`.

    Args:
        type_ (str):
        body (FieldPolicy): Declarative per-(tenant, record type) field-access policy.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | FieldPolicy
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
    body: FieldPolicy,
) -> Response[Error | FieldPolicy]:
    """Create or replace the field policy for a record type

     Admin-only. Upserts the policy for `(tenant, type)`.

    Args:
        type_ (str):
        body (FieldPolicy): Declarative per-(tenant, record type) field-access policy.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | FieldPolicy]
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
    body: FieldPolicy,
) -> Error | FieldPolicy | None:
    """Create or replace the field policy for a record type

     Admin-only. Upserts the policy for `(tenant, type)`.

    Args:
        type_ (str):
        body (FieldPolicy): Declarative per-(tenant, record type) field-access policy.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | FieldPolicy
    """

    return (
        await asyncio_detailed(
            type_=type_,
            client=client,
            body=body,
        )
    ).parsed
