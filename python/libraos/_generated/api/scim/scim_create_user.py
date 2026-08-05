from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.scim_error import ScimError
from ...models.scim_user import ScimUser
from ...types import Response


def _get_kwargs(
    *,
    body: ScimUser,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/scim/v2/Users",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/scim+json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | ScimError | ScimUser | None:
    if response.status_code == 201:
        response_201 = ScimUser.from_dict(response.json())

        return response_201

    if response.status_code == 400:
        response_400 = ScimError.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 409:
        response_409 = ScimError.from_dict(response.json())

        return response_409

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Error | ScimError | ScimUser]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: ScimUser,
) -> Response[Error | ScimError | ScimUser]:
    """Provision a SCIM user

     Creates a user from the IdP-supplied resource; `userName` (email) is unique.

    Args:
        body (ScimUser): SCIM 2.0 core User resource (RFC 7643), restricted to the supported
            attributes.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | ScimError | ScimUser]
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
    client: AuthenticatedClient,
    body: ScimUser,
) -> Error | ScimError | ScimUser | None:
    """Provision a SCIM user

     Creates a user from the IdP-supplied resource; `userName` (email) is unique.

    Args:
        body (ScimUser): SCIM 2.0 core User resource (RFC 7643), restricted to the supported
            attributes.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | ScimError | ScimUser
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: ScimUser,
) -> Response[Error | ScimError | ScimUser]:
    """Provision a SCIM user

     Creates a user from the IdP-supplied resource; `userName` (email) is unique.

    Args:
        body (ScimUser): SCIM 2.0 core User resource (RFC 7643), restricted to the supported
            attributes.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | ScimError | ScimUser]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: ScimUser,
) -> Error | ScimError | ScimUser | None:
    """Provision a SCIM user

     Creates a user from the IdP-supplied resource; `userName` (email) is unique.

    Args:
        body (ScimUser): SCIM 2.0 core User resource (RFC 7643), restricted to the supported
            attributes.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | ScimError | ScimUser
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
