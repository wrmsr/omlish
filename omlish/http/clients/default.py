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
        request = HttpRequest(  # noqa
            url,
            method=method,

            headers=headers,
            data=data,

            timeout_s=timeout_s,

            **kwargs,
        )

        return self._do(
            request,
            check=check,
            client=client,
        )

    @abc.abstractmethod
    def _do(
            self,
            request: HttpRequest,  # noqa
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


class _BaseSyncDefaultRequester(_DefaultRequester[HttpClient, R], ta.Generic[R]):
    def _do(
            self,
            request: HttpRequest,  # noqa
            *,
            check: bool = False,
            client: HttpClient | None = None,  # noqa
    ) -> R:
        if client is not None:
            return self._do_(
                client,
                request,
                check=check,
            )

        else:
            with _default_client() as client:  # noqa
                return self._do_(
                    client,
                    request,
                    check=check,
                )

    @abc.abstractmethod
    def _do_(
            self,
            client: HttpClient,  # noqa
            request: HttpRequest,  # noqa
            *,
            check: bool = False,  # noqa
    ) -> R:
        raise NotImplementedError


class _SyncDefaultRequester(_BaseSyncDefaultRequester[HttpResponse]):
    def _do_(
            self,
            client: HttpClient,  # noqa
            request: HttpRequest,  # noqa
            *,
            check: bool = False,  # noqa
    ) -> HttpResponse:
        return client.request(
            request,
            check=check,
        )


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
            request: HttpRequest,  # noqa
            *,
            check: bool = False,
            client: AsyncHttpClient | None = None,  # noqa
    ) -> HttpResponse:
        async def do(client: AsyncHttpClient) -> HttpResponse:  # noqa
            return await client.request(
                request,
                check=check,
            )

        if client is not None:
            return await do(client)

        else:
            async with _default_async_client() as cli:
                return await do(cli)


async_request = _AsyncDefaultRequester()
