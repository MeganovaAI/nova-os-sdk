from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.count_tokens_request import CountTokensRequest
from ...models.count_tokens_result import CountTokensResult
from ...models.error import Error
from ...types import Response


def _get_kwargs(
    *,
    body: CountTokensRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/messages/count_tokens",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CountTokensResult | Error | None:
    if response.status_code == 200:
        response_200 = CountTokensResult.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[CountTokensResult | Error]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: CountTokensRequest,
) -> Response[CountTokensResult | Error]:
    """Count input tokens (Anthropic-compatible)

     Anthropic-compatible pre-flight token count. Accepts the Messages request shape and returns an
    estimated `input_tokens` for the supplied system + messages. Citation/document consistency
    validators run here too, so misconfigurations surface as 400 before the chat path.

    Args:
        body (CountTokensRequest): Anthropic-compatible Messages request used for token counting.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CountTokensResult | Error]
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
    body: CountTokensRequest,
) -> CountTokensResult | Error | None:
    """Count input tokens (Anthropic-compatible)

     Anthropic-compatible pre-flight token count. Accepts the Messages request shape and returns an
    estimated `input_tokens` for the supplied system + messages. Citation/document consistency
    validators run here too, so misconfigurations surface as 400 before the chat path.

    Args:
        body (CountTokensRequest): Anthropic-compatible Messages request used for token counting.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CountTokensResult | Error
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: CountTokensRequest,
) -> Response[CountTokensResult | Error]:
    """Count input tokens (Anthropic-compatible)

     Anthropic-compatible pre-flight token count. Accepts the Messages request shape and returns an
    estimated `input_tokens` for the supplied system + messages. Citation/document consistency
    validators run here too, so misconfigurations surface as 400 before the chat path.

    Args:
        body (CountTokensRequest): Anthropic-compatible Messages request used for token counting.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CountTokensResult | Error]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: CountTokensRequest,
) -> CountTokensResult | Error | None:
    """Count input tokens (Anthropic-compatible)

     Anthropic-compatible pre-flight token count. Accepts the Messages request shape and returns an
    estimated `input_tokens` for the supplied system + messages. Citation/document consistency
    validators run here too, so misconfigurations surface as 400 before the chat path.

    Args:
        body (CountTokensRequest): Anthropic-compatible Messages request used for token counting.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CountTokensResult | Error
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
