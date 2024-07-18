import fastapi
import whtft.app
from starlette.middleware.sessions import SessionMiddleware

from .api import authentication, wellkown, metrics
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

app.mount("/metrics", metrics.metrics.app)


@app.get("/health")
async def get_health(ready: bool = False):
    return {}


app.include_router(authentication.router)
app.include_router(wellkown.router)


def main():  # pragma: no cover
    return whtft.app.main(app, settings)
