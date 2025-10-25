import abc
import typing as ta

from ... import lang
from ..headers import CanHttpHeaders
from .asyncs import AsyncHttpClient
from .base import HttpRequest
from .base import HttpResponse
from .sync import HttpClient


with lang.auto_proxy_import(globals()):
    from . import httpx as _httpx
    from . import urllib as _urllib


C = ta.TypeVar('C')
R = ta.TypeVar('R')


##


class _DefaultRequester(lang.Abstract, ta.Generic[C, R]):
    def __call__(
            self,
            url: str,
            method: str | None = None,
            *,
            headers: CanHttpHeaders | None = None,
            data: bytes | str | None = None,

            timeout_s: float | None = None,

            check: bool = False,
            client: C | None = None,  # noqa

            **kwargs: ta.Any,
    ) -> R:
        req = HttpRequest(
            url,
            method=method,

            headers=headers,
            data=data,

            timeout_s=timeout_s,

            **kwargs,
        )

        return self._do(
            req,
            check=check,
            client=client,
        )

    @abc.abstractmethod
    def _do(
            self,
            req: HttpRequest,
            *,
            check: bool = False,
            client: C | None = None,  # noqa
    ) -> R:
        raise NotImplementedError


##


def _default_client() -> HttpClient:
    return _urllib.UrllibHttpClient()


def client() -> HttpClient:
    return _default_client()


#


class _SyncDefaultRequester(_DefaultRequester[HttpClient, HttpResponse]):
    def _do(
            self,
            req: HttpRequest,
            *,
            check: bool = False,
            client: HttpClient | None = None,  # noqa
    ) -> HttpResponse:
        def do(cli: HttpClient) -> HttpResponse:  # noqa
            return cli.request(
                req,

                check=check,
            )

        if client is not None:
            return do(client)

        else:
            with _default_client() as cli:
                return do(cli)


request = _SyncDefaultRequester()


##


def _default_async_client() -> AsyncHttpClient:
    return _httpx.HttpxAsyncHttpClient()


def async_client() -> AsyncHttpClient:
    return _default_async_client()


#


class _AsyncDefaultRequester(_DefaultRequester[AsyncHttpClient, ta.Awaitable[HttpResponse]]):
    async def _do(
            self,
            req: HttpRequest,
            *,
            check: bool = False,
            client: AsyncHttpClient | None = None,  # noqa
    ) -> HttpResponse:
        async def do(cli: AsyncHttpClient) -> HttpResponse:  # noqa
            return await cli.request(
                req,

                check=check,
            )

        if client is not None:
            return await do(client)

        else:
            async with _default_async_client() as cli:
                return await do(cli)


async_request = _AsyncDefaultRequester()
