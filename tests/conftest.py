import fastapi.testclient
import pytest
import pytest_asyncio

from auth_service import main
from auth_service.oauth import OAuth, get_oauth
from auth_service.settings import Settings


@pytest.fixture
def settings():
    return Settings(
        auth_service_session_secret="secret!",
        google_client_id=None,
        google_client_secret=None,
        github_client_id=None,
        github_client_secret=None,
    )


@pytest.fixture
def github_settings():
    return Settings(
        auth_service_session_secret="secret!",
        google_client_id=None,
        google_client_secret=None,
        github_client_id="github_client_id",
        github_client_secret="github_client_secret",
    )


@pytest.fixture
def google_settings():
    return Settings(
        auth_service_session_secret="secret!",
        google_client_id="google_client_id",
        google_client_secret="google_client_secret",
        github_client_id=None,
        github_client_secret=None,
    )


@pytest_asyncio.fixture
async def client(settings):
    oauth = OAuth(settings)
    main.app.dependency_overrides[get_oauth] = lambda: oauth
    with fastapi.testclient.TestClient(
        main.app, follow_redirects=False
    ) as client:
        yield client


@pytest_asyncio.fixture
async def github_client(github_settings):
    oauth = OAuth(github_settings)
    main.app.dependency_overrides[get_oauth] = lambda: oauth
    with fastapi.testclient.TestClient(
        main.app, follow_redirects=False
    ) as client:
        yield client


@pytest_asyncio.fixture
async def google_client(google_settings):
    oauth = OAuth(google_settings)
    main.app.dependency_overrides[get_oauth] = lambda: oauth
    with fastapi.testclient.TestClient(
        main.app, follow_redirects=False
    ) as client:
        yield client
