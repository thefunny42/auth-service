from typing import Annotated

import fastapi
import pydantic
from fastapi import Depends, responses, status
from prometheus_client import Counter

from .oauth import OAuth, OAuthMethod, get_oauth
from .token import Token, get_token

router = fastapi.APIRouter(prefix="/api/authentication")


@router.get("/jwks.json")
def jwks(token: Annotated[Token, Depends(get_token)]):
    return responses.ORJSONResponse(
        content=token.jwks(private_keys=False),
        media_type="application/jwk-set+json",
    )


_login = Counter("authservice_login", "Login")


@router.get("/{method}/login", name="login")
async def login(
    method: OAuthMethod,
    request: fastapi.Request,
    oauth: Annotated[OAuth, Depends(get_oauth)],
):
    client = oauth.create_client(method)
    if client is None:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    redirect_uri = request.url_for("authorize", method=method)
    _login.inc()
    return await client.authorize_redirect(request, redirect_uri)


_authorize = Counter("authservice_authorize", "Authorize")


@router.get("/{method}/authorize", name="authorize")
async def authorize(
    method: OAuthMethod,
    request: fastapi.Request,
    oauth: Annotated[OAuth, Depends(get_oauth)],
):
    client = oauth.create_client(method)
    if client is None:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    token = await client.authorize_access_token(request)
    user = token.get("userinfo")
    if not user:
        user = await client.userinfo(token=token)
    user = dict(user)
    request.session["info"] = {
        "email": user.get("email"),
        "name": user.get("name"),
        "method": method,
    }
    request.session["token"] = token
    _authorize.inc()
    return responses.RedirectResponse("/")


_logout = Counter("authservice_logout", "Logout")


@router.get("/logout", name="logout")
def logout(request: fastapi.Request):
    request.session.clear()
    _logout.inc()
    return responses.RedirectResponse("/")


class UserInfo(pydantic.BaseModel):
    email: str
    name: str
    token: str
    roles: list[str]
    method: OAuthMethod


class Link(pydantic.BaseModel):
    url: str
    name: str


class User(pydantic.BaseModel):
    user: UserInfo | None
    available_methods: list[OAuthMethod]


_user = Counter("authservice_user", "User")


@router.get("/user", name="user")
def user(
    request: fastapi.Request,
    oauth: Annotated[OAuth, Depends(get_oauth)],
    token: Annotated[Token, Depends(get_token)],
) -> User:
    info = request.session.get("info")
    if info is not None:
        roles = ["admin"]
        info = UserInfo(token=token.create(roles=roles), roles=roles, **info)
    _user.inc()
    return User(user=info, available_methods=oauth.available())
