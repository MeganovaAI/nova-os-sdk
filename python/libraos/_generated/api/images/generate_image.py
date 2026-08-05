from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.image_generation_request import ImageGenerationRequest
from ...models.image_response import ImageResponse
from ...types import Response


def _get_kwargs(
    *,
    body: ImageGenerationRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/images/generations",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Error | ImageResponse | None:
    if response.status_code == 200:
        response_200 = ImageResponse.from_dict(response.json())

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

    if response.status_code == 413:
        response_413 = Error.from_dict(response.json())

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
) -> Response[Error | ImageResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ImageGenerationRequest,
) -> Response[Error | ImageResponse]:
    """Generate images from a text prompt

     OpenAI-compatible image generation. The request body is forwarded to the configured image model and
    the response is returned unchanged, so the client owns all parameters. `model` must be provider-
    prefixed (e.g. `Alibaba/z-image-turbo`). Not admin-only.

    Args:
        body (ImageGenerationRequest): Forwarded verbatim to the image model; additional provider-
            specific fields are accepted and passed through.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | ImageResponse]
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
    body: ImageGenerationRequest,
) -> Error | ImageResponse | None:
    """Generate images from a text prompt

     OpenAI-compatible image generation. The request body is forwarded to the configured image model and
    the response is returned unchanged, so the client owns all parameters. `model` must be provider-
    prefixed (e.g. `Alibaba/z-image-turbo`). Not admin-only.

    Args:
        body (ImageGenerationRequest): Forwarded verbatim to the image model; additional provider-
            specific fields are accepted and passed through.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | ImageResponse
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ImageGenerationRequest,
) -> Response[Error | ImageResponse]:
    """Generate images from a text prompt

     OpenAI-compatible image generation. The request body is forwarded to the configured image model and
    the response is returned unchanged, so the client owns all parameters. `model` must be provider-
    prefixed (e.g. `Alibaba/z-image-turbo`). Not admin-only.

    Args:
        body (ImageGenerationRequest): Forwarded verbatim to the image model; additional provider-
            specific fields are accepted and passed through.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | ImageResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: ImageGenerationRequest,
) -> Error | ImageResponse | None:
    """Generate images from a text prompt

     OpenAI-compatible image generation. The request body is forwarded to the configured image model and
    the response is returned unchanged, so the client owns all parameters. `model` must be provider-
    prefixed (e.g. `Alibaba/z-image-turbo`). Not admin-only.

    Args:
        body (ImageGenerationRequest): Forwarded verbatim to the image model; additional provider-
            specific fields are accepted and passed through.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | ImageResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
