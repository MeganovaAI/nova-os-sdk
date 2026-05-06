from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.stream_event_custom_tool_use import StreamEventCustomToolUse
from ...models.stream_event_done import StreamEventDone
from ...models.stream_event_error import StreamEventError
from ...models.stream_event_route_hint import StreamEventRouteHint
from ...models.stream_event_text_delta import StreamEventTextDelta
from ...models.stream_event_thinking import StreamEventThinking
from ...models.stream_event_tool_result import StreamEventToolResult
from ...models.stream_event_tool_use import StreamEventToolUse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    job_id: str,
    *,
    last_event_id: str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(last_event_id, Unset):
        headers["Last-Event-ID"] = last_event_id

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/managed/agents/jobs/{job_id}/stream".format(
            job_id=quote(str(job_id), safe=""),
        ),
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    Error
    | StreamEventCustomToolUse
    | StreamEventDone
    | StreamEventError
    | StreamEventRouteHint
    | StreamEventTextDelta
    | StreamEventThinking
    | StreamEventToolResult
    | StreamEventToolUse
    | None
):
    if response.status_code == 200:

        def _parse_response_200(
            data: object,
        ) -> (
            StreamEventCustomToolUse
            | StreamEventDone
            | StreamEventError
            | StreamEventRouteHint
            | StreamEventTextDelta
            | StreamEventThinking
            | StreamEventToolResult
            | StreamEventToolUse
        ):
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_stream_event_type_0 = StreamEventTextDelta.from_dict(data)

                return componentsschemas_stream_event_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_stream_event_type_1 = StreamEventToolUse.from_dict(data)

                return componentsschemas_stream_event_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_stream_event_type_2 = StreamEventToolResult.from_dict(data)

                return componentsschemas_stream_event_type_2
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_stream_event_type_3 = StreamEventCustomToolUse.from_dict(data)

                return componentsschemas_stream_event_type_3
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_stream_event_type_4 = StreamEventThinking.from_dict(data)

                return componentsschemas_stream_event_type_4
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_stream_event_type_5 = StreamEventError.from_dict(data)

                return componentsschemas_stream_event_type_5
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_stream_event_type_6 = StreamEventDone.from_dict(data)

                return componentsschemas_stream_event_type_6
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_stream_event_type_7 = StreamEventRouteHint.from_dict(data)

            return componentsschemas_stream_event_type_7

        response_200 = _parse_response_200(response.text)

        return response_200

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
) -> Response[
    Error
    | StreamEventCustomToolUse
    | StreamEventDone
    | StreamEventError
    | StreamEventRouteHint
    | StreamEventTextDelta
    | StreamEventThinking
    | StreamEventToolResult
    | StreamEventToolUse
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    job_id: str,
    *,
    client: AuthenticatedClient | Client,
    last_event_id: str | Unset = UNSET,
) -> Response[
    Error
    | StreamEventCustomToolUse
    | StreamEventDone
    | StreamEventError
    | StreamEventRouteHint
    | StreamEventTextDelta
    | StreamEventThinking
    | StreamEventToolResult
    | StreamEventToolUse
]:
    """SSE stream for an async job (with replay)

    Args:
        job_id (str):
        last_event_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | StreamEventCustomToolUse | StreamEventDone | StreamEventError | StreamEventRouteHint | StreamEventTextDelta | StreamEventThinking | StreamEventToolResult | StreamEventToolUse]
    """

    kwargs = _get_kwargs(
        job_id=job_id,
        last_event_id=last_event_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    job_id: str,
    *,
    client: AuthenticatedClient | Client,
    last_event_id: str | Unset = UNSET,
) -> (
    Error
    | StreamEventCustomToolUse
    | StreamEventDone
    | StreamEventError
    | StreamEventRouteHint
    | StreamEventTextDelta
    | StreamEventThinking
    | StreamEventToolResult
    | StreamEventToolUse
    | None
):
    """SSE stream for an async job (with replay)

    Args:
        job_id (str):
        last_event_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | StreamEventCustomToolUse | StreamEventDone | StreamEventError | StreamEventRouteHint | StreamEventTextDelta | StreamEventThinking | StreamEventToolResult | StreamEventToolUse
    """

    return sync_detailed(
        job_id=job_id,
        client=client,
        last_event_id=last_event_id,
    ).parsed


async def asyncio_detailed(
    job_id: str,
    *,
    client: AuthenticatedClient | Client,
    last_event_id: str | Unset = UNSET,
) -> Response[
    Error
    | StreamEventCustomToolUse
    | StreamEventDone
    | StreamEventError
    | StreamEventRouteHint
    | StreamEventTextDelta
    | StreamEventThinking
    | StreamEventToolResult
    | StreamEventToolUse
]:
    """SSE stream for an async job (with replay)

    Args:
        job_id (str):
        last_event_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | StreamEventCustomToolUse | StreamEventDone | StreamEventError | StreamEventRouteHint | StreamEventTextDelta | StreamEventThinking | StreamEventToolResult | StreamEventToolUse]
    """

    kwargs = _get_kwargs(
        job_id=job_id,
        last_event_id=last_event_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    job_id: str,
    *,
    client: AuthenticatedClient | Client,
    last_event_id: str | Unset = UNSET,
) -> (
    Error
    | StreamEventCustomToolUse
    | StreamEventDone
    | StreamEventError
    | StreamEventRouteHint
    | StreamEventTextDelta
    | StreamEventThinking
    | StreamEventToolResult
    | StreamEventToolUse
    | None
):
    """SSE stream for an async job (with replay)

    Args:
        job_id (str):
        last_event_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | StreamEventCustomToolUse | StreamEventDone | StreamEventError | StreamEventRouteHint | StreamEventTextDelta | StreamEventThinking | StreamEventToolResult | StreamEventToolUse
    """

    return (
        await asyncio_detailed(
            job_id=job_id,
            client=client,
            last_event_id=last_event_id,
        )
    ).parsed
