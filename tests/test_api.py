import json
import urllib.parse

import jwcrypto.jwk
import jwcrypto.jwt


def test_user_logged_out_no_methods(client):
    response = client.get("/api/authentication/user")
    assert response.status_code == 200
    assert response.json() == {"available_methods": [], "user": None}


def test_user_logged_out_github(github_client):
    response = github_client.get("/api/authentication/user")
    assert response.status_code == 200
    assert response.json() == {
        "available_methods": ["github"],
        "user": None,
    }


def test_user_logged_out_google(google_client):
    response = google_client.get("/api/authentication/user")
    assert response.status_code == 200
    assert response.json() == {
        "available_methods": ["google"],
        "user": None,
    }


def test_logout(client):
    response = client.get("/api/authentication/logout")
    assert response.status_code == 307
    location = response.headers.get("location")
    assert location == "/"


def test_login_google_not_configured(client):
    response = client.get("/api/authentication/google/login")
    assert response.status_code == 404
    location = response.headers.get("location")
    assert location is None


def test_login_github_not_configured(client):
    response = client.get("/api/authentication/github/login")
    assert response.status_code == 404
    location = response.headers.get("location")
    assert location is None


def test_login_github_configured(github_client):
    response = github_client.get("/api/authentication/github/login")
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
        "http://testserver/api/authentication/github/authorize"
    ]


def test_login_google_configured(google_client):
    response = google_client.get("/api/authentication/google/login")
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
        "http://testserver/api/authentication/google/authorize"
    ]


def test_jwks_json(client):
    response = client.get("/api/authentication/jwks.json")
    assert response.status_code == 200
    key_set = jwcrypto.jwk.JWKSet()
    key_set.import_keyset(response.text)
    assert len(key_set) == 1


def test_authorize_github_not_configured(client):
    response = client.get("/api/authentication/github/authorize")
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

    response = github_client.get("/api/authentication/github/authorize")
    assert response.status_code == 307
    location = response.headers.get("location")
    assert location == "/"

    response = github_client.get("/api/authentication/user")
    assert response.status_code == 200
    assert response.json() == {
        "available_methods": ["github"],
        "user": {
            "email": "me@example.com",
            "method": "github",
            "name": "Me",
            "token": mocker.ANY,
            "roles": ["admin"],
        },
    }

    jwt_raw = response.json().get("user").get("token")
    response = github_client.get("/api/authentication/jwks.json")
    assert response.status_code == 200
    jwk_set = jwcrypto.jwk.JWKSet()
    jwk_set.import_keyset(response.text)

    jwt_token = jwcrypto.jwt.JWT(jwt=jwt_raw, key=jwk_set)
    assert jwt_token.deserializelog == ["Success"]
    assert json.loads(jwt_token.claims).get("roles") == ["admin"]

    response = github_client.get("/api/authentication/logout")
    assert response.status_code == 307
    location = response.headers.get("location")
    assert location == "/"

    response = github_client.get("/api/authentication/user")
    assert response.status_code == 200
    assert response.json() == {
        "available_methods": ["github"],
        "user": None,
    }


def test_authorize_google_not_configured(client):
    response = client.get("/api/authentication/google/authorize")
    assert response.status_code == 404
