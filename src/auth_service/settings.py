import pydantic
import pydantic_settings


class Settings(pydantic_settings.BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", secrets_dir="/run/secrets"
    )

    google_client_id: str | None = pydantic.Field(default=None)
    google_client_secret: str | None = pydantic.Field(default=None)
    github_client_id: str | None = pydantic.Field(default=None)
    github_client_secret: str | None = pydantic.Field(default=None)
    auth_service_issuer: str | None = pydantic.Field(default=None)
    auth_service_jwks: str | None = pydantic.Field(default=None)
    auth_service_log_config: str | None = pydantic.Field(default=None)
    auth_service_session_ttl: int = pydantic.Field(default=15 * 60)
    auth_service_session_secret: str = pydantic.Field(default=...)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[pydantic_settings.BaseSettings],
        init_settings: pydantic_settings.PydanticBaseSettingsSource,
        env_settings: pydantic_settings.PydanticBaseSettingsSource,
        dotenv_settings: pydantic_settings.PydanticBaseSettingsSource,
        file_secret_settings: pydantic_settings.PydanticBaseSettingsSource,
    ) -> tuple[pydantic_settings.PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            file_secret_settings,
            env_settings,
            dotenv_settings,
        )


settings = Settings()


def get_settings():
    return settings
