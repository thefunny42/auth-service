# Auth service

Simple service that allows users to authenticate using OAuth to either Github
or Google. A session cookie is set under the `/authentication` path.
An authenticated user can retrieve a JWT token and validate it against
a local JWKS.

The endpoints are:

1. `/.well-known/jwks.json`: Return the JWKS that can be used to
   validate token obtained with the `/authentication/token` endpoint.

2. `/authentication/{github,google}/login`: Initiate the login process.

3. `/authentication/{github,google}/authorize`: Callback userd during the
   login process.

4. `/authentication/logout`: Logout.

5. `/authentication/token`: Fetch a token:

   ```json
   {
     "access_token": "....",
     "token_type": "Bearer",
     "expire_in": 42
   }
   ```

6. `/authentication/userinfo`: Fetch information about the currently logged
   in user and its token:

   ```json
   {
     "available": ["github"],
     "user": {
       "email": "me@example.com",
       "method": "github",
       "name": "Me",
       "roles": ["admin"]
     }
   }
   ```

## Deployment

You can deploy the service for local testing on either
[minikube](https://minikube.sigs.k8s.io/docs/) or Docker Desktop. This can be
done with the help of an [Helm](https://helm.sh/) chart.

If you use minikube, first start it:

```shell
minikube start --network-plugin=cni
kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.28.0/manifests/calico.yaml
```

Install the chart:

```shell
helm repo add thefunny42 https://thefunny42.github.io/charts
helm install dev thefunny42/authservice
```

You can create a `secrets.yaml` file with your client id and secret for Github
and/or Google:

```yaml
githubClientId: xxxx
githubClientSecret: xxx
googleClientId: xxxx
googleClientSecret: xxx
```

Alternatively you can install it from a clone from this repository:

```shell
helm install dev charts/authservice --values secrets.yaml
```

You can verify that everything is running:

```shell
helm test dev
kubectl get all -l app.kubernetes.io/instance=dev
```

You can forward the port in a terminal to be able to access the application:

```shell
kubectl port-forward service/dev-authservice 8000:8000
```

After you can open http://localhost:8000/authentication/github/login in
your browser to authenticate, and check the result again by opening
http://localhost:8000/authentication/userinfo.

Cleanup with:

```shell
helm uninstall dev
```

If you use minikube:

```shell
minikube stop
```

## Configuration

The following configuration variables are available:

- `GOOGLE_CLIENT_ID`: Client id used to authenticate with Github
- `GOOGLE_CLIENT_SECRET`: Client secret used to authenticae with Github.
- `GITHUB_CLIENT_ID`: Client id used to authenticate with Google.
- `GITHUB_CLIENT_SECRET`: Client secret used to authenticate with Google.
- `AUTH_SERVICE_ISSUER`: Issuer for for JWT token.
- `AUTH_SERVICE_AUDIENCE`: Optional audience for JWT token.
- `AUTH_SERVICE_JWKS`: Optional keys to use to create JWT token.
- `AUTH_SERVICE_LOG_CONFIG`: Custom logging configuration (a default one is provided).
- `AUTH_SERVICE_SESSION_TTL`: TTL for session cookie and JWT token.
- `aUTH_SERVICE_SESSION_SECRET`: Shared secret for session cookie.

## Development

There is a dev container that can be used with vscode.
[Hatch](https://hatch.pypa.io/latest/) is used as a packaging tool, to run
test and code analysis.
