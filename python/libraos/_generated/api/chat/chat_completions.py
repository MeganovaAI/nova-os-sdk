from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.chat_completion_request import ChatCompletionRequest
from ...models.chat_completion_response import ChatCompletionResponse
from ...models.error import Error
from ...types import Response


def _get_kwargs(
    *,
    body: ChatCompletionRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/chat/completions",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ChatCompletionResponse | Error | None:
    if response.status_code == 200:
        response_200 = ChatCompletionResponse.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 429:
        response_429 = Error.from_dict(response.json())

        return response_429

    if response.status_code == 502:
        response_502 = Error.from_dict(response.json())

        return response_502

    if response.status_code == 503:
        response_503 = Error.from_dict(response.json())

        return response_503

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ChatCompletionResponse | Error]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ChatCompletionRequest,
) -> Response[ChatCompletionResponse | Error]:
    """Chat completions (OpenAI-compatible)

     OpenAI-compatible chat completions. Accepts the standard `model`, `messages`, `stream`, and
    `max_tokens` / `max_completion_tokens` fields. The response reports the provider's real
    `finish_reason` and a per-response `usage`. Report-style requests are auto-detected and streamed
    with periodic heartbeat comments. When gateway mode is enabled, a `model` of the form
    `llm:<provider>/<model>` bypasses the agent pipeline and forwards the call straight to the
    underlying provider (raw passthrough).

    Args:
        body (ChatCompletionRequest): OpenAI-compatible chat completion request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ChatCompletionResponse | Error]
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
    body: ChatCompletionRequest,
) -> ChatCompletionResponse | Error | None:
    """Chat completions (OpenAI-compatible)

     OpenAI-compatible chat completions. Accepts the standard `model`, `messages`, `stream`, and
    `max_tokens` / `max_completion_tokens` fields. The response reports the provider's real
    `finish_reason` and a per-response `usage`. Report-style requests are auto-detected and streamed
    with periodic heartbeat comments. When gateway mode is enabled, a `model` of the form
    `llm:<provider>/<model>` bypasses the agent pipeline and forwards the call straight to the
    underlying provider (raw passthrough).

    Args:
        body (ChatCompletionRequest): OpenAI-compatible chat completion request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ChatCompletionResponse | Error
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ChatCompletionRequest,
) -> Response[ChatCompletionResponse | Error]:
    """Chat completions (OpenAI-compatible)

     OpenAI-compatible chat completions. Accepts the standard `model`, `messages`, `stream`, and
    `max_tokens` / `max_completion_tokens` fields. The response reports the provider's real
    `finish_reason` and a per-response `usage`. Report-style requests are auto-detected and streamed
    with periodic heartbeat comments. When gateway mode is enabled, a `model` of the form
    `llm:<provider>/<model>` bypasses the agent pipeline and forwards the call straight to the
    underlying provider (raw passthrough).

    Args:
        body (ChatCompletionRequest): OpenAI-compatible chat completion request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ChatCompletionResponse | Error]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: ChatCompletionRequest,
) -> ChatCompletionResponse | Error | None:
    """Chat completions (OpenAI-compatible)

     OpenAI-compatible chat completions. Accepts the standard `model`, `messages`, `stream`, and
    `max_tokens` / `max_completion_tokens` fields. The response reports the provider's real
    `finish_reason` and a per-response `usage`. Report-style requests are auto-detected and streamed
    with periodic heartbeat comments. When gateway mode is enabled, a `model` of the form
    `llm:<provider>/<model>` bypasses the agent pipeline and forwards the call straight to the
    underlying provider (raw passthrough).

    Args:
        body (ChatCompletionRequest): OpenAI-compatible chat completion request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ChatCompletionResponse | Error
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
