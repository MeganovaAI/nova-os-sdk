from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.run_skill_tool_body import RunSkillToolBody
from ...models.skill_run_response import SkillRunResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    skill: str,
    tool: str,
    *,
    body: RunSkillToolBody | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/skills/{skill}/{tool}/run".format(
            skill=quote(str(skill), safe=""),
            tool=quote(str(tool), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | SkillRunResponse | None:
    if response.status_code == 200:
        response_200 = SkillRunResponse.from_dict(response.json())

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

    if response.status_code == 500:
        response_500 = Error.from_dict(response.json())

        return response_500

    if response.status_code == 503:
        response_503 = Error.from_dict(response.json())

        return response_503

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Error | SkillRunResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    skill: str,
    tool: str,
    *,
    client: AuthenticatedClient | Client,
    body: RunSkillToolBody | Unset = UNSET,
) -> Response[Error | SkillRunResponse]:
    r"""Run one skill tool directly

     Invokes a single tool belonging to a skill and returns its raw string output, bypassing the agent
    loop. The request body is the tool's own argument JSON (e.g. `{ \"query\": \"...\" }` or `{ \"url\":
    \"...\" }`); an empty body is treated as `{}`.

    Args:
        skill (str):
        tool (str):
        body (RunSkillToolBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | SkillRunResponse]
    """

    kwargs = _get_kwargs(
        skill=skill,
        tool=tool,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    skill: str,
    tool: str,
    *,
    client: AuthenticatedClient | Client,
    body: RunSkillToolBody | Unset = UNSET,
) -> Error | SkillRunResponse | None:
    r"""Run one skill tool directly

     Invokes a single tool belonging to a skill and returns its raw string output, bypassing the agent
    loop. The request body is the tool's own argument JSON (e.g. `{ \"query\": \"...\" }` or `{ \"url\":
    \"...\" }`); an empty body is treated as `{}`.

    Args:
        skill (str):
        tool (str):
        body (RunSkillToolBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | SkillRunResponse
    """

    return sync_detailed(
        skill=skill,
        tool=tool,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    skill: str,
    tool: str,
    *,
    client: AuthenticatedClient | Client,
    body: RunSkillToolBody | Unset = UNSET,
) -> Response[Error | SkillRunResponse]:
    r"""Run one skill tool directly

     Invokes a single tool belonging to a skill and returns its raw string output, bypassing the agent
    loop. The request body is the tool's own argument JSON (e.g. `{ \"query\": \"...\" }` or `{ \"url\":
    \"...\" }`); an empty body is treated as `{}`.

    Args:
        skill (str):
        tool (str):
        body (RunSkillToolBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | SkillRunResponse]
    """

    kwargs = _get_kwargs(
        skill=skill,
        tool=tool,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    skill: str,
    tool: str,
    *,
    client: AuthenticatedClient | Client,
    body: RunSkillToolBody | Unset = UNSET,
) -> Error | SkillRunResponse | None:
    r"""Run one skill tool directly

     Invokes a single tool belonging to a skill and returns its raw string output, bypassing the agent
    loop. The request body is the tool's own argument JSON (e.g. `{ \"query\": \"...\" }` or `{ \"url\":
    \"...\" }`); an empty body is treated as `{}`.

    Args:
        skill (str):
        tool (str):
        body (RunSkillToolBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | SkillRunResponse
    """

    return (
        await asyncio_detailed(
            skill=skill,
            tool=tool,
            client=client,
            body=body,
        )
    ).parsed
