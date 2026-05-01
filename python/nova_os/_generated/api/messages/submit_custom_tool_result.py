from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.custom_tool_result_request import CustomToolResultRequest
from ...models.error import Error
from ...types import Response


def _get_kwargs(
    message_id: str,
    *,
    body: CustomToolResultRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/managed/agents/messages/{message_id}/custom_tool_results".format(
            message_id=quote(str(message_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | Error | None:
    if response.status_code == 202:
        response_202 = cast(Any, None)
        return response_202

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
) -> Response[Any | Error]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    message_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: CustomToolResultRequest,
) -> Response[Any | Error]:
    """Submit a custom_tool_use result (Mode A inline)

     Used when partner consumes the SSE stream directly. POST the result
    for an emitted `custom_tool_use` event; Nova OS resumes the agent
    loop and continues streaming on the original request connection.

    Args:
        message_id (str):
        body (CustomToolResultRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error]
    """

    kwargs = _get_kwargs(
        message_id=message_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    message_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: CustomToolResultRequest,
) -> Any | Error | None:
    """Submit a custom_tool_use result (Mode A inline)

     Used when partner consumes the SSE stream directly. POST the result
    for an emitted `custom_tool_use` event; Nova OS resumes the agent
    loop and continues streaming on the original request connection.

    Args:
        message_id (str):
        body (CustomToolResultRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error
    """

    return sync_detailed(
        message_id=message_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    message_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: CustomToolResultRequest,
) -> Response[Any | Error]:
    """Submit a custom_tool_use result (Mode A inline)

     Used when partner consumes the SSE stream directly. POST the result
    for an emitted `custom_tool_use` event; Nova OS resumes the agent
    loop and continues streaming on the original request connection.

    Args:
        message_id (str):
        body (CustomToolResultRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error]
    """

    kwargs = _get_kwargs(
        message_id=message_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    message_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: CustomToolResultRequest,
) -> Any | Error | None:
    """Submit a custom_tool_use result (Mode A inline)

     Used when partner consumes the SSE stream directly. POST the result
    for an emitted `custom_tool_use` event; Nova OS resumes the agent
    loop and continues streaming on the original request connection.

    Args:
        message_id (str):
        body (CustomToolResultRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error
    """

    return (
        await asyncio_detailed(
            message_id=message_id,
            client=client,
            body=body,
        )
    ).parsed
