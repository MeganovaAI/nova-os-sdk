from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_service_key_request import CreateServiceKeyRequest
from ...models.error import Error
from ...models.service_key_secret import ServiceKeySecret
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: CreateServiceKeyRequest | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/service-keys/self",
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | ServiceKeySecret | None:
    if response.status_code == 201:
        response_201 = ServiceKeySecret.from_dict(response.json())

        return response_201

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Error | ServiceKeySecret]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: CreateServiceKeyRequest | Unset = UNSET,
) -> Response[Error | ServiceKeySecret]:
    """Self-serve an inference API key

     Any authenticated user may mint an inference-scoped `nk_` key bound to their own account. The full
    secret is returned once. Available only when Gateway Mode per-key policy is enabled.

    Args:
        body (CreateServiceKeyRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | ServiceKeySecret]
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
    body: CreateServiceKeyRequest | Unset = UNSET,
) -> Error | ServiceKeySecret | None:
    """Self-serve an inference API key

     Any authenticated user may mint an inference-scoped `nk_` key bound to their own account. The full
    secret is returned once. Available only when Gateway Mode per-key policy is enabled.

    Args:
        body (CreateServiceKeyRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | ServiceKeySecret
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: CreateServiceKeyRequest | Unset = UNSET,
) -> Response[Error | ServiceKeySecret]:
    """Self-serve an inference API key

     Any authenticated user may mint an inference-scoped `nk_` key bound to their own account. The full
    secret is returned once. Available only when Gateway Mode per-key policy is enabled.

    Args:
        body (CreateServiceKeyRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | ServiceKeySecret]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: CreateServiceKeyRequest | Unset = UNSET,
) -> Error | ServiceKeySecret | None:
    """Self-serve an inference API key

     Any authenticated user may mint an inference-scoped `nk_` key bound to their own account. The full
    secret is returned once. Available only when Gateway Mode per-key policy is enabled.

    Args:
        body (CreateServiceKeyRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | ServiceKeySecret
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
