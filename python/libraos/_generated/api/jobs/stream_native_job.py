from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...types import UNSET, Response, Unset


def _get_kwargs(
    api_key: str,
    job_id: str,
    *,
    last_event_id: int | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(last_event_id, Unset):
        headers["Last-Event-ID"] = str(last_event_id)

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/agents/v1/{api_key}/jobs/{job_id}/stream".format(
            api_key=quote(str(api_key), safe=""),
            job_id=quote(str(job_id), safe=""),
        ),
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Error | str | None:
    if response.status_code == 200:
        response_200 = response.text
        return response_200

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())

        return response_404

    if response.status_code == 503:
        response_503 = Error.from_dict(response.json())

        return response_503

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Error | str]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    api_key: str,
    job_id: str,
    *,
    client: AuthenticatedClient | Client,
    last_event_id: int | Unset = UNSET,
) -> Response[Error | str]:
    """Stream job events (SSE)

     Server-Sent Events stream. Replays stored events first (honoring `Last-Event-ID`), then delivers
    live events until the job reaches a terminal state. Each frame carries `id` (sequence), `event`
    (type) and a JSON `data` payload; `: nova-heartbeat` comments are sent every 10s.

    Args:
        api_key (str):
        job_id (str):
        last_event_id (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | str]
    """

    kwargs = _get_kwargs(
        api_key=api_key,
        job_id=job_id,
        last_event_id=last_event_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    api_key: str,
    job_id: str,
    *,
    client: AuthenticatedClient | Client,
    last_event_id: int | Unset = UNSET,
) -> Error | str | None:
    """Stream job events (SSE)

     Server-Sent Events stream. Replays stored events first (honoring `Last-Event-ID`), then delivers
    live events until the job reaches a terminal state. Each frame carries `id` (sequence), `event`
    (type) and a JSON `data` payload; `: nova-heartbeat` comments are sent every 10s.

    Args:
        api_key (str):
        job_id (str):
        last_event_id (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | str
    """

    return sync_detailed(
        api_key=api_key,
        job_id=job_id,
        client=client,
        last_event_id=last_event_id,
    ).parsed


async def asyncio_detailed(
    api_key: str,
    job_id: str,
    *,
    client: AuthenticatedClient | Client,
    last_event_id: int | Unset = UNSET,
) -> Response[Error | str]:
    """Stream job events (SSE)

     Server-Sent Events stream. Replays stored events first (honoring `Last-Event-ID`), then delivers
    live events until the job reaches a terminal state. Each frame carries `id` (sequence), `event`
    (type) and a JSON `data` payload; `: nova-heartbeat` comments are sent every 10s.

    Args:
        api_key (str):
        job_id (str):
        last_event_id (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | str]
    """

    kwargs = _get_kwargs(
        api_key=api_key,
        job_id=job_id,
        last_event_id=last_event_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    api_key: str,
    job_id: str,
    *,
    client: AuthenticatedClient | Client,
    last_event_id: int | Unset = UNSET,
) -> Error | str | None:
    """Stream job events (SSE)

     Server-Sent Events stream. Replays stored events first (honoring `Last-Event-ID`), then delivers
    live events until the job reaches a terminal state. Each frame carries `id` (sequence), `event`
    (type) and a JSON `data` payload; `: nova-heartbeat` comments are sent every 10s.

    Args:
        api_key (str):
        job_id (str):
        last_event_id (int | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | str
    """

    return (
        await asyncio_detailed(
            api_key=api_key,
            job_id=job_id,
            client=client,
            last_event_id=last_event_id,
        )
    ).parsed
