import base64
import os
import secrets

from fastapi import FastAPI, Request
from fastapi.responses import Response

ENV_USER = "SKILLGROWTH_BASIC_AUTH_USER"
ENV_PASS = "SKILLGROWTH_BASIC_AUTH_PASS"


def _unauthorized() -> Response:
    return Response(status_code=401, headers={"WWW-Authenticate": 'Basic realm="skillgrowth"'})


def _credentials_valid(header: str | None, user: str, password: str) -> bool:
    if not header or not header.startswith("Basic "):
        return False
    try:
        decoded = base64.b64decode(header.removeprefix("Basic ")).decode("utf-8")
        given_user, given_password = decoded.split(":", 1)
    except (ValueError, UnicodeDecodeError):
        return False
    # secrets.compare_digest, not ==, so a wrong guess can't be timed to
    # learn how many leading characters it got right.
    return secrets.compare_digest(given_user, user) and secrets.compare_digest(given_password, password)


def setup_basic_auth(app: FastAPI) -> None:
    user = os.environ.get(ENV_USER)
    password = os.environ.get(ENV_PASS)
    if not user or not password:
        return  # gate disabled by default — unset means fully unauthenticated, unchanged

    @app.middleware("http")
    async def basic_auth_gate(request: Request, call_next):
        # Exempt: the Dockerfile's HEALTHCHECK has no way to know user-chosen
        # credentials, so gating it too would make the container report
        # unhealthy the moment this env-var gate is turned on.
        if request.url.path == "/api/health":
            return await call_next(request)
        if _credentials_valid(request.headers.get("Authorization"), user, password):
            return await call_next(request)
        return _unauthorized()
