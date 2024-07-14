import fastapi
import prometheus_client
import uvicorn
from starlette.middleware.sessions import SessionMiddleware

from .api import authentication, wellkown
from .settings import get_settings

__version__ = "0.1.0"

settings = get_settings()

app = fastapi.FastAPI()
# Set require https and domain.
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.auth_service_session_secret.get_secret_value(),
    max_age=settings.auth_service_session_ttl,
    path="/authentication",
)

app.mount("/metrics", prometheus_client.make_asgi_app())


@app.get("/health")
async def get_health(ready: bool = False):
    return {}


app.include_router(authentication.router)
app.include_router(wellkown.router)


def main():  # pragma: no cover
    log_config = None
    if settings.auth_service_log_config is not None:
        log_config = str(settings.auth_service_log_config)
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        server_header=False,
        log_config=log_config,
    )
