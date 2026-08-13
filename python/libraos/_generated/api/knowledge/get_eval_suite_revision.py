from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.eval_suite_revision import EvalSuiteRevision
from ...types import Response


def _get_kwargs(
    name: str,
    revision: int,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/managed/evals/suites/{name}/revisions/{revision}".format(
            name=quote(str(name), safe=""),
            revision=quote(str(revision), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | EvalSuiteRevision | None:
    if response.status_code == 200:
        response_200 = EvalSuiteRevision.from_dict(response.json())

        return response_200

    if response.status_code == 403:
        response_403 = Error.from_dict(response.json())

        return response_403

    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())

        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Error | EvalSuiteRevision]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    name: str,
    revision: int,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Error | EvalSuiteRevision]:
    """Get one exact immutable suite revision

    Args:
        name (str):
        revision (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | EvalSuiteRevision]
    """

    kwargs = _get_kwargs(
        name=name,
        revision=revision,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    name: str,
    revision: int,
    *,
    client: AuthenticatedClient | Client,
) -> Error | EvalSuiteRevision | None:
    """Get one exact immutable suite revision

    Args:
        name (str):
        revision (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | EvalSuiteRevision
    """

    return sync_detailed(
        name=name,
        revision=revision,
        client=client,
    ).parsed


async def asyncio_detailed(
    name: str,
    revision: int,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Error | EvalSuiteRevision]:
    """Get one exact immutable suite revision

    Args:
        name (str):
        revision (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | EvalSuiteRevision]
    """

    kwargs = _get_kwargs(
        name=name,
        revision=revision,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    name: str,
    revision: int,
    *,
    client: AuthenticatedClient | Client,
) -> Error | EvalSuiteRevision | None:
    """Get one exact immutable suite revision

    Args:
        name (str):
        revision (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | EvalSuiteRevision
    """

    return (
        await asyncio_detailed(
            name=name,
            revision=revision,
            client=client,
        )
    ).parsed
