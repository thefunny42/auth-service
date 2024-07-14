from typing import Annotated

import fastapi
import pydantic
import pydantic_core
from fastapi import Depends, responses

from ..settings import Settings, get_settings
from ..token import Token, get_token

router = fastapi.APIRouter(prefix="/.well-known")


class Configuration(pydantic.BaseModel):
    # This is only some keys to get the token validated
    issuer: str
    jwks_uri: pydantic.HttpUrl
    userinfo_endpoint: pydantic.HttpUrl
    token_endpoint: pydantic.HttpUrl
    grant_types_supported: list[str]
    token_endpoint_auth_signing_alg_values_supported: list[str]


def global_url(request: fastapi.Request, name: str):
    app: fastapi.FastAPI = request.app
    return pydantic_core.Url(
        str(app.url_path_for(name).make_absolute_url(request.base_url))
    )


@router.get("/openid-configuration")
def configuration(
    settings: Annotated[Settings, Depends(get_settings)],
    request: fastapi.Request,
):
    return Configuration(
        issuer=settings.auth_service_issuer,
        userinfo_endpoint=global_url(request, "userinfo"),
        token_endpoint=global_url(request, "token"),
        jwks_uri=global_url(request, "jwks"),
        grant_types_supported=["authorization_code"],
        token_endpoint_auth_signing_alg_values_supported=["HS256"],
    )


@router.get("/jwks.json", name="jwks")
def jwks(token: Annotated[Token, Depends(get_token)]):
    return responses.ORJSONResponse(
        content=token.jwks(private_keys=False),
        media_type="application/jwk-set+json",
    )
