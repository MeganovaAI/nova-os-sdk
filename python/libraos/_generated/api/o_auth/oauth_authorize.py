from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.oauth_authorize_code_challenge_method import OauthAuthorizeCodeChallengeMethod
from ...models.oauth_authorize_response_type import OauthAuthorizeResponseType
from ...models.oauth_error import OauthError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    client_id: str,
    redirect_uri: str | Unset = UNSET,
    response_type: OauthAuthorizeResponseType | Unset = UNSET,
    scope: str | Unset = UNSET,
    state: str | Unset = UNSET,
    code_challenge: str | Unset = UNSET,
    code_challenge_method: OauthAuthorizeCodeChallengeMethod | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["client_id"] = client_id

    params["redirect_uri"] = redirect_uri

    json_response_type: str | Unset = UNSET
    if not isinstance(response_type, Unset):
        json_response_type = response_type.value

    params["response_type"] = json_response_type

    params["scope"] = scope

    params["state"] = state

    params["code_challenge"] = code_challenge

    json_code_challenge_method: str | Unset = UNSET
    if not isinstance(code_challenge_method, Unset):
        json_code_challenge_method = code_challenge_method.value

    params["code_challenge_method"] = json_code_challenge_method

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/oauth/authorize",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | OauthError | str | None:
    if response.status_code == 200:
        response_200 = response.text
        return response_200

    if response.status_code == 302:
        response_302 = cast(Any, None)
        return response_302

    if response.status_code == 400:
        response_400 = OauthError.from_dict(response.json())

        return response_400

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | OauthError | str]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    client_id: str,
    redirect_uri: str | Unset = UNSET,
    response_type: OauthAuthorizeResponseType | Unset = UNSET,
    scope: str | Unset = UNSET,
    state: str | Unset = UNSET,
    code_challenge: str | Unset = UNSET,
    code_challenge_method: OauthAuthorizeCodeChallengeMethod | Unset = UNSET,
) -> Response[Any | OauthError | str]:
    """Authorization endpoint

     OAuth 2.0 / OIDC authorization endpoint. With no valid session cookie it renders the login page
    (HTML); with a valid session it issues a single-use authorization code and 302-redirects to the
    client's registered `redirect_uri` with `code` and `state`. Supports PKCE (S256); some clients
    require it.

    Args:
        client_id (str):
        redirect_uri (str | Unset):
        response_type (OauthAuthorizeResponseType | Unset):
        scope (str | Unset):
        state (str | Unset):
        code_challenge (str | Unset):
        code_challenge_method (OauthAuthorizeCodeChallengeMethod | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | OauthError | str]
    """

    kwargs = _get_kwargs(
        client_id=client_id,
        redirect_uri=redirect_uri,
        response_type=response_type,
        scope=scope,
        state=state,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    client_id: str,
    redirect_uri: str | Unset = UNSET,
    response_type: OauthAuthorizeResponseType | Unset = UNSET,
    scope: str | Unset = UNSET,
    state: str | Unset = UNSET,
    code_challenge: str | Unset = UNSET,
    code_challenge_method: OauthAuthorizeCodeChallengeMethod | Unset = UNSET,
) -> Any | OauthError | str | None:
    """Authorization endpoint

     OAuth 2.0 / OIDC authorization endpoint. With no valid session cookie it renders the login page
    (HTML); with a valid session it issues a single-use authorization code and 302-redirects to the
    client's registered `redirect_uri` with `code` and `state`. Supports PKCE (S256); some clients
    require it.

    Args:
        client_id (str):
        redirect_uri (str | Unset):
        response_type (OauthAuthorizeResponseType | Unset):
        scope (str | Unset):
        state (str | Unset):
        code_challenge (str | Unset):
        code_challenge_method (OauthAuthorizeCodeChallengeMethod | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | OauthError | str
    """

    return sync_detailed(
        client=client,
        client_id=client_id,
        redirect_uri=redirect_uri,
        response_type=response_type,
        scope=scope,
        state=state,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    client_id: str,
    redirect_uri: str | Unset = UNSET,
    response_type: OauthAuthorizeResponseType | Unset = UNSET,
    scope: str | Unset = UNSET,
    state: str | Unset = UNSET,
    code_challenge: str | Unset = UNSET,
    code_challenge_method: OauthAuthorizeCodeChallengeMethod | Unset = UNSET,
) -> Response[Any | OauthError | str]:
    """Authorization endpoint

     OAuth 2.0 / OIDC authorization endpoint. With no valid session cookie it renders the login page
    (HTML); with a valid session it issues a single-use authorization code and 302-redirects to the
    client's registered `redirect_uri` with `code` and `state`. Supports PKCE (S256); some clients
    require it.

    Args:
        client_id (str):
        redirect_uri (str | Unset):
        response_type (OauthAuthorizeResponseType | Unset):
        scope (str | Unset):
        state (str | Unset):
        code_challenge (str | Unset):
        code_challenge_method (OauthAuthorizeCodeChallengeMethod | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | OauthError | str]
    """

    kwargs = _get_kwargs(
        client_id=client_id,
        redirect_uri=redirect_uri,
        response_type=response_type,
        scope=scope,
        state=state,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    client_id: str,
    redirect_uri: str | Unset = UNSET,
    response_type: OauthAuthorizeResponseType | Unset = UNSET,
    scope: str | Unset = UNSET,
    state: str | Unset = UNSET,
    code_challenge: str | Unset = UNSET,
    code_challenge_method: OauthAuthorizeCodeChallengeMethod | Unset = UNSET,
) -> Any | OauthError | str | None:
    """Authorization endpoint

     OAuth 2.0 / OIDC authorization endpoint. With no valid session cookie it renders the login page
    (HTML); with a valid session it issues a single-use authorization code and 302-redirects to the
    client's registered `redirect_uri` with `code` and `state`. Supports PKCE (S256); some clients
    require it.

    Args:
        client_id (str):
        redirect_uri (str | Unset):
        response_type (OauthAuthorizeResponseType | Unset):
        scope (str | Unset):
        state (str | Unset):
        code_challenge (str | Unset):
        code_challenge_method (OauthAuthorizeCodeChallengeMethod | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | OauthError | str
    """

    return (
        await asyncio_detailed(
            client=client,
            client_id=client_id,
            redirect_uri=redirect_uri,
            response_type=response_type,
            scope=scope,
            state=state,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
        )
    ).parsed
