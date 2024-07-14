import jwcrypto.jwk


def test_jwks_json(client):
    response = client.get("/.well-known/jwks.json")
    assert response.status_code == 200
    key_set = jwcrypto.jwk.JWKSet()
    key_set.import_keyset(response.text)
    assert len(key_set) == 1


def test_openid_configuration(client):
    response = client.get("/.well-known/openid-configuration")
    assert response.status_code == 200
    assert response.json() == {
        "issuer": "http://example.com",
        "jwks_uri": "http://testserver/authentication/jwks.json",
        "userinfo_endpoint": "http://testserver/authentication/userinfo",
        "token_endpoint": "http://testserver/authentication/token",
        "grant_types_supported": ["authorization_code"],
        "token_endpoint_auth_signing_alg_values_supported": ["HS256"],
    }
