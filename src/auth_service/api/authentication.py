from typing import Annotated

import fastapi
import pydantic
from fastapi import Depends, HTTPException, responses, status

from ..oauth import OAuth, OAuthMethod, get_oauth
from ..settings import Settings, get_settings
from ..token import Token, get_token
from .metrics import metrics

router = fastapi.APIRouter(prefix="/authentication")


@router.get("/{method}/login", name="login")
@metrics.measure()
async def login(
    method: OAuthMethod,
    request: fastapi.Request,
    oauth: Annotated[OAuth, Depends(get_oauth)],
):
    client = oauth.create_client(method)
    if client is None:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    redirect_uri = request.url_for("authorize", method=method)
    return await client.authorize_redirect(request, redirect_uri)


@router.get("/{method}/authorize", name="authorize")
@metrics.measure()
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
    return responses.RedirectResponse("/")


@router.get("/logout", name="logout")
@metrics.measure()
def logout(request: fastapi.Request):
    request.session.clear()
    return responses.RedirectResponse("/")


class CurrentUser(pydantic.BaseModel):
    email: str
    name: str
    roles: list[str]
    method: OAuthMethod


class Link(pydantic.BaseModel):
    url: str
    name: str


class User(pydantic.BaseModel):
    user: CurrentUser | None
    available: list[OAuthMethod]


@router.get("/userinfo", name="userinfo")
@metrics.measure()
def user(
    request: fastapi.Request,
    oauth: Annotated[OAuth, Depends(get_oauth)],
) -> User:
    info = request.session.get("info")
    if info is not None:
        info = CurrentUser(roles=["admin"], **info)
    return User(user=info, available=oauth.available())


class AccessToken(pydantic.BaseModel):
    access_token: str
    token_type: str = pydantic.Field(default="Bearer")
    expire_in: int


@router.get("/token", name="token")
@metrics.measure()
def token(
    request: fastapi.Request,
    token: Annotated[Token, Depends(get_token)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> AccessToken:
    info = request.session.get("info")
    if info is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Insufficient credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return AccessToken(
        access_token=token.create(roles=["admin"]),
        expire_in=settings.auth_service_session_ttl,
    )
