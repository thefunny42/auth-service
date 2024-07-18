import pydantic
import whtft.app


class Settings(whtft.app.Settings):

    google_client_id: str | None = pydantic.Field(default=None)
    google_client_secret: pydantic.SecretStr | None = pydantic.Field(
        default=None
    )
    github_client_id: str | None = pydantic.Field(default=None)
    github_client_secret: pydantic.SecretStr | None = pydantic.Field(
        default=None
    )
    auth_service_issuer: str = pydantic.Field(default=...)
    auth_service_audience: str | None = pydantic.Field(default=None)
    auth_service_jwks: str | None = pydantic.Field(default=None)
    auth_service_session_ttl: int = pydantic.Field(default=15 * 60)
    auth_service_session_secret: pydantic.SecretStr = pydantic.Field(
        default=...
    )


settings = Settings()


def get_settings():
    return settings
