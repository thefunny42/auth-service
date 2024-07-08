# Auth service

Simple service that allows users to authenticate using OAuth to either Github
or Google. A session cookie is set under the ``/api/authentication`` path.
An authenticated user gets a JWT token that can be validated against
a local JWKS.

The endpoints are:

1. ``/api/authentication/jwks.json``: Return the JWKS that can be used to
   validate token obtained with the ``/api/authentication/user`` endpoint.

2. ``/api/authentication/{github,google}/login``: Initiate the login process.

3. ``/api/authentication/{github,google}/authorize``: Callback userd during the
   login process.

4. ``/api/authentication/logout``: Logout.

5. ``/api/authentication/user``: Fetch information about the currently logged
   in user and its token:

   ```json
   {
        "available_methods": ["github"],
        "user": {
            "email": "me@example.com",
            "method": "github",
            "name": "Me",
            "token": "xxxx",
            "roles": ["admin"],
        },
    }
    ```
