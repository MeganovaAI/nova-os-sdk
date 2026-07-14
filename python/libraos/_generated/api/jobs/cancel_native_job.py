from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.native_job_cancelled import NativeJobCancelled
from ...types import Response


def _get_kwargs(
    api_key: str,
    job_id: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/agents/v1/{api_key}/jobs/{job_id}".format(
            api_key=quote(str(api_key), safe=""),
            job_id=quote(str(job_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | NativeJobCancelled | None:
    if response.status_code == 200:
        response_200 = NativeJobCancelled.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())

        return response_404

    if response.status_code == 409:
        response_409 = Error.from_dict(response.json())

        return response_409

    if response.status_code == 503:
        response_503 = Error.from_dict(response.json())

        return response_503

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Error | NativeJobCancelled]:
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
) -> Response[Error | NativeJobCancelled]:
    """Cancel a job

     Request graceful cancellation of a non-terminal job.

    Args:
        api_key (str):
        job_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | NativeJobCancelled]
    """

    kwargs = _get_kwargs(
        api_key=api_key,
        job_id=job_id,
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
) -> Error | NativeJobCancelled | None:
    """Cancel a job

     Request graceful cancellation of a non-terminal job.

    Args:
        api_key (str):
        job_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | NativeJobCancelled
    """

    return sync_detailed(
        api_key=api_key,
        job_id=job_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    api_key: str,
    job_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Error | NativeJobCancelled]:
    """Cancel a job

     Request graceful cancellation of a non-terminal job.

    Args:
        api_key (str):
        job_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | NativeJobCancelled]
    """

    kwargs = _get_kwargs(
        api_key=api_key,
        job_id=job_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    api_key: str,
    job_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Error | NativeJobCancelled | None:
    """Cancel a job

     Request graceful cancellation of a non-terminal job.

    Args:
        api_key (str):
        job_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | NativeJobCancelled
    """

    return (
        await asyncio_detailed(
            api_key=api_key,
            job_id=job_id,
            client=client,
        )
    ).parsed
