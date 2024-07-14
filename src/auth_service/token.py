import argparse
import json
import time
import uuid

import jwcrypto.jwk
import jwcrypto.jwt

from .settings import Settings, get_settings


class Token:
    algorithm = "ES256"

    def __init__(self, settings: Settings):
        self.__issuer = settings.auth_service_issuer
        self.__audience = settings.auth_service_audience
        self.__ttl = settings.auth_service_session_ttl
        if settings.auth_service_jwks:
            self.load(settings.auth_service_jwks)
        else:
            self.reset()

    def load(self, source: str):
        new_set = jwcrypto.jwk.JWKSet()
        new_set.import_keyset(source)
        new_kids = [key.get("kid") for key in new_set["keys"]]
        if len(new_kids) != 1 or new_kids[0] is None:
            # jwcrypto does not raise instances of classes!
            raise jwcrypto.jwk.InvalidJWKValue
        self.__set = new_set
        self.__kid = new_kids[0]

    def reset(self):
        self.__kid = uuid.uuid4().hex
        self.__set = jwcrypto.jwk.JWKSet()
        self.__set.add(
            jwcrypto.jwk.JWK.generate(
                kty="EC", crv="P-256", kid=self.__kid, use="sig"
            )
        )

    def jwks(self, private_keys: bool = False):
        return self.__set.export(as_dict=True, private_keys=private_keys)

    def create(
        self,
        sub: str | None = None,
        aud: str | None = None,
        roles: list[str] = [],
    ):
        now = int(time.time())
        token = jwcrypto.jwt.JWT(
            header={"alg": self.algorithm, "kid": self.__kid},
            claims={
                "iss": self.__issuer or "",
                "sub": sub or "",
                "aud": aud or self.__audience or "",
                "roles": list(roles),
                "iat": now,
                "nbf": now - 60,
                "exp": now + self.__ttl,
            },
        )
        token.make_signed_token(self.__set.get_key(self.__kid))
        return token.serialize()


token = Token(get_settings())


def get_token():
    return token


def main():  # pragma: no cover
    parser = argparse.ArgumentParser(
        "auth-service-token", description="Generate jwks private keys"
    )
    parser.add_argument(
        "--output", action="store", nargs="?", type=argparse.FileType("w")
    )
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()
    if args.reset:
        token.reset()
    jwks = json.dumps(token.jwks(private_keys=True))
    if args.output is not None:
        args.output.write(jwks)
    else:
        print(jwks)
