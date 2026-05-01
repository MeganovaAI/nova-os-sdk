from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.employee import Employee
from ...models.employee_update import EmployeeUpdate
from ...models.error import Error
from ...types import Response


def _get_kwargs(
    employee_id: str,
    *,
    body: EmployeeUpdate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/v1/managed/employees/{employee_id}".format(
            employee_id=quote(str(employee_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Employee | Error | None:
    if response.status_code == 200:
        response_200 = Employee.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())

        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Employee | Error]:
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
    body: EmployeeUpdate,
) -> Response[Employee | Error]:
    """Update an employee (partial)

    Args:
        employee_id (str):
        body (EmployeeUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Employee | Error]
    """

    kwargs = _get_kwargs(
        employee_id=employee_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    employee_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: EmployeeUpdate,
) -> Employee | Error | None:
    """Update an employee (partial)

    Args:
        employee_id (str):
        body (EmployeeUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Employee | Error
    """

    return sync_detailed(
        employee_id=employee_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    employee_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: EmployeeUpdate,
) -> Response[Employee | Error]:
    """Update an employee (partial)

    Args:
        employee_id (str):
        body (EmployeeUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Employee | Error]
    """

    kwargs = _get_kwargs(
        employee_id=employee_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    employee_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: EmployeeUpdate,
) -> Employee | Error | None:
    """Update an employee (partial)

    Args:
        employee_id (str):
        body (EmployeeUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Employee | Error
    """

    return (
        await asyncio_detailed(
            employee_id=employee_id,
            client=client,
            body=body,
        )
    ).parsed
