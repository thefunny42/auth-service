import json

import jwcrypto.jwk
import jwcrypto.jwt
import pytest

from auth_service.settings import Settings
from auth_service.token import Token


def test_import_token_without_kid():
    faulty_set = jwcrypto.jwk.JWKSet()
    faulty_set.add(jwcrypto.jwk.JWK.generate(kty="EC", crv="P-256", use="sig"))
    jwk_faulty_set_export = faulty_set.export()
    assert isinstance(jwk_faulty_set_export, str)

    faulty_settings = Settings(
        auth_service_session_secret="secret!",
        auth_service_jwks=jwk_faulty_set_export,
        google_client_id=None,
        google_client_secret=None,
        github_client_id=None,
        github_client_secret=None,
    )

    with pytest.raises(jwcrypto.jwk.InvalidJWKValue):
        Token(faulty_settings)


def test_import_export_token(settings):
    token = Token(settings)
    jwt_raw = token.create(roles=["me"])
    jwk_set_export = json.dumps(token.jwks(private_keys=True))

    jwk_set = jwcrypto.jwk.JWKSet()
    jwk_set.import_keyset(jwk_set_export)

    jwt_token = jwcrypto.jwt.JWT(jwt=jwt_raw, key=jwk_set)
    assert jwt_token.deserializelog == ["Success"]
    assert json.loads(jwt_token.claims).get("roles") == ["me"]

    token.reset()
    jwt_raw_2 = token.create(roles=["me"])
    jwk_set_export_2 = json.dumps(token.jwks(private_keys=True))

    jwk_set_2 = jwcrypto.jwk.JWKSet()
    jwk_set_2.import_keyset(jwk_set_export_2)

    jwt_token_2 = jwcrypto.jwt.JWT(jwt=jwt_raw_2, key=jwk_set_2)
    assert jwt_token_2.deserializelog == ["Success"]
    assert json.loads(jwt_token_2.claims).get("roles") == ["me"]

    with pytest.raises(jwcrypto.jwt.JWTMissingKey):
        jwcrypto.jwt.JWT(jwt=jwt_raw_2, key=jwk_set)

    with pytest.raises(jwcrypto.jwt.JWTMissingKey):
        jwcrypto.jwt.JWT(jwt=jwt_raw, key=jwk_set_2)

    token.load(jwk_set_export)
    jwk_set_export_3 = json.dumps(token.jwks(private_keys=True))

    jwk_set_3 = jwcrypto.jwk.JWKSet()
    jwk_set_3.import_keyset(jwk_set_export_3)

    jwt_token_3a = jwcrypto.jwt.JWT(jwt=jwt_raw, key=jwk_set_3)
    assert jwt_token_3a.deserializelog == ["Success"]
    assert json.loads(jwt_token_3a.claims).get("roles") == ["me"]

    jwt_raw_3 = token.create(roles=["you"])

    jwt_token_3b = jwcrypto.jwt.JWT(jwt=jwt_raw_3, key=jwk_set)
    assert jwt_token_3b.deserializelog == ["Success"]
    assert json.loads(jwt_token_3b.claims).get("roles") == ["you"]

    with pytest.raises(jwcrypto.jwt.JWTMissingKey):
        jwcrypto.jwt.JWT(jwt=jwt_raw_2, key=jwk_set_3)
