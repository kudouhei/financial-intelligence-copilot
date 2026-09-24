import base64
import binascii
import secrets
from collections.abc import Awaitable, Callable, Iterable

from starlette.responses import PlainTextResponse
from starlette.types import Receive, Scope, Send


class BasicAccessMiddleware:
    """Protect HTTP endpoints with a portable application-level access gate."""

    def __init__(
        self,
        app: Callable[
            [Scope, Receive, Send],
            Awaitable[None],
        ],
        *,
        username: str,
        password: str,
        public_paths: Iterable[str] = ("/health",),
    ) -> None:
        self._app = app
        self._username = username
        self._password = password
        self._public_paths = frozenset(public_paths)

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if (
            scope["type"] != "http"
            or scope.get("path") in self._public_paths
            or self._has_valid_credentials(scope)
        ):
            await self._app(scope, receive, send)
            return

        response = PlainTextResponse(
            "Authentication required.",
            status_code=401,
            headers={
                "WWW-Authenticate": (
                    'Basic realm="Financial Intelligence Copilot", charset="UTF-8"'
                ),
                "Cache-Control": "no-store",
            },
        )
        await response(scope, receive, send)

    def _has_valid_credentials(self, scope: Scope) -> bool:
        headers = dict(scope.get("headers", []))
        authorization = headers.get(b"authorization", b"")
        scheme, separator, encoded_credentials = authorization.partition(b" ")

        if not separator or scheme.lower() != b"basic":
            return False

        try:
            decoded_credentials = base64.b64decode(
                encoded_credentials,
                validate=True,
            ).decode("utf-8")
        except (binascii.Error, UnicodeDecodeError, ValueError):
            return False

        username, separator, password = decoded_credentials.partition(":")

        if not separator:
            return False

        username_matches = secrets.compare_digest(
            username,
            self._username,
        )
        password_matches = secrets.compare_digest(
            password,
            self._password,
        )

        return username_matches and password_matches
