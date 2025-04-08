import typing as ta

from ..headers import CanHttpHeaders
from .base import HttpClient
from .base import HttpRequest
from .base import HttpResponse
from .urllib import UrllibHttpClient


##


def _default_client() -> HttpClient:
    return UrllibHttpClient()


def client() -> HttpClient:
    return _default_client()


def request(
        url: str,
        method: str | None = None,
        *,
        headers: CanHttpHeaders | None = None,
        data: bytes | str | None = None,

        timeout_s: float | None = None,

        check: bool = False,

        client: HttpClient | None = None,  # noqa

        **kwargs: ta.Any,
) -> HttpResponse:
    req = HttpRequest(
        url,
        method=method,

        headers=headers,
        data=data,

        timeout_s=timeout_s,

        **kwargs,
    )

    def do(cli: HttpClient) -> HttpResponse:
        return cli.request(
            req,

            check=check,
        )

    if client is not None:
        return do(client)

    else:
        with _default_client() as cli:
            return do(cli)
