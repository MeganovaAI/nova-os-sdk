from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.model_list import ModelList
from ...types import Response


def _get_kwargs() -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/models",
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Error | ModelList | None:
    if response.status_code == 200:
        response_200 = ModelList.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Error | ModelList]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[Error | ModelList]:
    r"""List available models (OpenAI-compatible)

     Lists the models available to the caller in OpenAI's `{object:\"list\", data:[...]}` shape. Each
    entry is an agent id; disabled agents are hidden. When gateway mode is enabled and a passthrough
    allowlist is configured, raw provider models are additionally advertised with `llm:` ids.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | ModelList]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
) -> Error | ModelList | None:
    r"""List available models (OpenAI-compatible)

     Lists the models available to the caller in OpenAI's `{object:\"list\", data:[...]}` shape. Each
    entry is an agent id; disabled agents are hidden. When gateway mode is enabled and a passthrough
    allowlist is configured, raw provider models are additionally advertised with `llm:` ids.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | ModelList
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[Error | ModelList]:
    r"""List available models (OpenAI-compatible)

     Lists the models available to the caller in OpenAI's `{object:\"list\", data:[...]}` shape. Each
    entry is an agent id; disabled agents are hidden. When gateway mode is enabled and a passthrough
    allowlist is configured, raw provider models are additionally advertised with `llm:` ids.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | ModelList]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
) -> Error | ModelList | None:
    r"""List available models (OpenAI-compatible)

     Lists the models available to the caller in OpenAI's `{object:\"list\", data:[...]}` shape. Each
    entry is an agent id; disabled agents are hidden. When gateway mode is enabled and a passthrough
    allowlist is configured, raw provider models are additionally advertised with `llm:` ids.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | ModelList
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
