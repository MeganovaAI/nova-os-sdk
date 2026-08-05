from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.house_profile import HouseProfile
from ...models.house_profile_update import HouseProfileUpdate
from ...models.put_house_profile_response_409 import PutHouseProfileResponse409
from ...models.put_house_profile_response_413 import PutHouseProfileResponse413
from ...types import UNSET, Response, Unset


def _get_kwargs(
    employee_id: str,
    *,
    body: HouseProfileUpdate,
    if_match: str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(if_match, Unset):
        headers["If-Match"] = if_match

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/v1/managed/employees/{employee_id}/house-profile".format(
            employee_id=quote(str(employee_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | HouseProfile | PutHouseProfileResponse409 | PutHouseProfileResponse413 | None:
    if response.status_code == 200:
        response_200 = HouseProfile.from_dict(response.json())

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

    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())

        return response_404

    if response.status_code == 409:
        response_409 = PutHouseProfileResponse409.from_dict(response.json())

        return response_409

    if response.status_code == 413:
        response_413 = PutHouseProfileResponse413.from_dict(response.json())

        return response_413

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
) -> Response[Error | HouseProfile | PutHouseProfileResponse409 | PutHouseProfileResponse413]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    employee_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: HouseProfileUpdate,
    if_match: str | Unset = UNSET,
) -> Response[Error | HouseProfile | PutHouseProfileResponse409 | PutHouseProfileResponse413]:
    """Replace an employee's house profile

     Replaces the employee's house-profile markdown. Send an empty markdown string to clear it.
    Optionally supply an If-Match header carrying the profile's current updated_at to guard against a
    concurrent overwrite.

    Args:
        employee_id (str):
        if_match (str | Unset):
        body (HouseProfileUpdate): Replacement house-profile content. An empty markdown string
            clears the profile.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | HouseProfile | PutHouseProfileResponse409 | PutHouseProfileResponse413]
    """

    kwargs = _get_kwargs(
        employee_id=employee_id,
        body=body,
        if_match=if_match,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    employee_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: HouseProfileUpdate,
    if_match: str | Unset = UNSET,
) -> Error | HouseProfile | PutHouseProfileResponse409 | PutHouseProfileResponse413 | None:
    """Replace an employee's house profile

     Replaces the employee's house-profile markdown. Send an empty markdown string to clear it.
    Optionally supply an If-Match header carrying the profile's current updated_at to guard against a
    concurrent overwrite.

    Args:
        employee_id (str):
        if_match (str | Unset):
        body (HouseProfileUpdate): Replacement house-profile content. An empty markdown string
            clears the profile.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | HouseProfile | PutHouseProfileResponse409 | PutHouseProfileResponse413
    """

    return sync_detailed(
        employee_id=employee_id,
        client=client,
        body=body,
        if_match=if_match,
    ).parsed


async def asyncio_detailed(
    employee_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: HouseProfileUpdate,
    if_match: str | Unset = UNSET,
) -> Response[Error | HouseProfile | PutHouseProfileResponse409 | PutHouseProfileResponse413]:
    """Replace an employee's house profile

     Replaces the employee's house-profile markdown. Send an empty markdown string to clear it.
    Optionally supply an If-Match header carrying the profile's current updated_at to guard against a
    concurrent overwrite.

    Args:
        employee_id (str):
        if_match (str | Unset):
        body (HouseProfileUpdate): Replacement house-profile content. An empty markdown string
            clears the profile.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | HouseProfile | PutHouseProfileResponse409 | PutHouseProfileResponse413]
    """

    kwargs = _get_kwargs(
        employee_id=employee_id,
        body=body,
        if_match=if_match,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    employee_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: HouseProfileUpdate,
    if_match: str | Unset = UNSET,
) -> Error | HouseProfile | PutHouseProfileResponse409 | PutHouseProfileResponse413 | None:
    """Replace an employee's house profile

     Replaces the employee's house-profile markdown. Send an empty markdown string to clear it.
    Optionally supply an If-Match header carrying the profile's current updated_at to guard against a
    concurrent overwrite.

    Args:
        employee_id (str):
        if_match (str | Unset):
        body (HouseProfileUpdate): Replacement house-profile content. An empty markdown string
            clears the profile.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | HouseProfile | PutHouseProfileResponse409 | PutHouseProfileResponse413
    """

    return (
        await asyncio_detailed(
            employee_id=employee_id,
            client=client,
            body=body,
            if_match=if_match,
        )
    ).parsed
