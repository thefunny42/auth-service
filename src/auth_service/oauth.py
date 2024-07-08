from typing import Annotated, Literal

import authlib.integrations.starlette_client
from fastapi import Depends

from .settings import Settings, get_settings

OAuthMethod = Literal["google", "github"]


class OAuth(authlib.integrations.starlette_client.OAuth):

    def __init__(self, settings: Annotated[Settings, Depends(get_settings)]):
        super().__init__()
        if settings.google_client_id and settings.google_client_secret:
            self.register(
                name="google",
                server_metadata_url=(
                    "https://accounts.google.com/"
                    ".well-known/openid-configuration"
                ),
                client_id=settings.google_client_id,
                client_secret=settings.google_client_secret,
                client_kwargs={"scope": "openid email profile"},
            )
        if settings.github_client_id and settings.github_client_secret:
            self.register(
                name="github",
                api_base_url="https://api.github.com/",
                access_token_url="https://github.com/login/oauth/access_token",
                authorize_url="https://github.com/login/oauth/authorize",
                userinfo_endpoint="user",
                client_id=settings.github_client_id,
                client_secret=settings.github_client_secret,
                client_kwargs={"scope": "user:email", "allow_signup": False},
            )

    def available(self):
        return list(self._registry.keys())


oauth = OAuth(get_settings())


def get_oauth():  # pragma: no cover
    return oauth
