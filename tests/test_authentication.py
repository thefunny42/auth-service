import json
import urllib.parse

import jwcrypto.jwk
import jwcrypto.jwt


def test_user_logged_out_no_methods(client):
    response = client.get("/authentication/userinfo")
    assert response.status_code == 200
    assert response.json() == {"available": [], "user": None}


def test_user_logged_out_github(github_client):
    response = github_client.get("/authentication/userinfo")
    assert response.status_code == 200
    assert response.json() == {
        "available": ["github"],
        "user": None,
    }


def test_user_logged_out_google(google_client):
    response = google_client.get("/authentication/userinfo")
    assert response.status_code == 200
    assert response.json() == {
        "available": ["google"],
        "user": None,
    }


def test_logout(client):
    response = client.get("/authentication/logout")
    assert response.status_code == 307
    location = response.headers.get("location")
    assert location == "/"


def test_login_google_not_configured(client):
    response = client.get("/authentication/google/login")
    assert response.status_code == 404
    location = response.headers.get("location")
    assert location is None


def test_login_github_not_configured(client):
    response = client.get("/authentication/github/login")
    assert response.status_code == 404
    location = response.headers.get("location")
    assert location is None


def test_login_github_configured(github_client):
    response = github_client.get("/authentication/github/login")
    assert response.status_code == 302
    location = response.headers.get("location")
    assert location is not None
    parts = urllib.parse.urlparse(location)
    assert parts.scheme == "https"
    assert parts.netloc == "github.com"
    assert parts.path == "/login/oauth/authorize"
    query = urllib.parse.parse_qs(parts.query)
    assert query.get("response_type") == ["code"]
    assert query.get("client_id") == ["github_client_id"]
    assert query.get("scope") == ["user:email"]
    assert query.get("redirect_uri") == [
        "http://testserver/authentication/github/authorize"
    ]


def test_login_google_configured(google_client):
    response = google_client.get("/authentication/google/login")
    assert response.status_code == 302
    location = response.headers.get("location")
    assert location is not None
    parts = urllib.parse.urlparse(location)
    assert parts.scheme == "https"
    assert parts.netloc == "accounts.google.com"
    assert parts.path == "/o/oauth2/v2/auth"
    query = urllib.parse.parse_qs(parts.query)
    assert query.get("response_type") == ["code"]
    assert query.get("client_id") == ["google_client_id"]
    assert query.get("scope") == ["openid email profile"]
    assert query.get("redirect_uri") == [
        "http://testserver/authentication/google/authorize"
    ]


def test_authorize_github_not_configured(client):
    response = client.get("/authentication/github/authorize")
    assert response.status_code == 404


def test_authorize_github_flow_mocked(github_client, mocker):
    mocker.patch(
        "authlib.integrations.starlette_client."
        "apps.StarletteOAuth2App.authorize_access_token",
        return_value={"userinfo": None},
    )
    mocker.patch(
        "authlib.integrations.starlette_client."
        "apps.StarletteOAuth2App.userinfo",
        return_value={"name": "Me", "email": "me@example.com"},
    )

    response = github_client.get("/authentication/github/authorize")
    assert response.status_code == 307
    location = response.headers.get("location")
    assert location == "/"

    response = github_client.get("/authentication/userinfo")
    assert response.status_code == 200
    assert response.json() == {
        "available": ["github"],
        "user": {
            "email": "me@example.com",
            "method": "github",
            "name": "Me",
            "roles": ["admin"],
        },
    }

    response = github_client.get("/authentication/token")
    assert response.status_code == 200
    assert response.json() == {
        "access_token": mocker.ANY,
        "token_type": "Bearer",
        "expire_in": 900,
    }

    jwt_raw = response.json().get("access_token")
    response = github_client.get("/.well-known/jwks.json")
    assert response.status_code == 200
    jwk_set = jwcrypto.jwk.JWKSet()
    jwk_set.import_keyset(response.text)

    jwt_token = jwcrypto.jwt.JWT(jwt=jwt_raw, key=jwk_set)
    assert jwt_token.deserializelog == ["Success"]
    assert json.loads(jwt_token.claims).get("roles") == ["admin"]

    response = github_client.get("/authentication/logout")
    assert response.status_code == 307
    location = response.headers.get("location")
    assert location == "/"

    response = github_client.get("/authentication/userinfo")
    assert response.status_code == 200
    assert response.json() == {
        "available": ["github"],
        "user": None,
    }

    response = github_client.get("/authentication/token")
    assert response.status_code == 401


def test_authorize_google_not_configured(client):
    response = client.get("/authentication/google/authorize")
    assert response.status_code == 404
