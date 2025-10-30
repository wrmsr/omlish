import abc
import contextlib
import typing as ta

from ... import lang
from ..headers import CanHttpHeaders
from .asyncs import AsyncHttpClient
from .base import HttpClientContext
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

            context: HttpClientContext | None = None,
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
            context=context,
            check=check,
            client=client,
        )

    @abc.abstractmethod
    def _do(
            self,
            request: HttpRequest,  # noqa
            *,
            context: HttpClientContext | None = None,
            check: bool = False,
            client: C | None = None,  # noqa
    ) -> R:
        raise NotImplementedError


##


def _default_client() -> HttpClient:
    return _urllib.UrllibHttpClient()


def client() -> HttpClient:
    return _default_client()


@contextlib.contextmanager
def manage_client(client: HttpClient | None = None) -> ta.Generator[HttpClient]:  # noqa
    if client is not None:
        yield client

    else:
        with _default_client() as client:  # noqa
            yield client


#


class _BaseSyncDefaultRequester(_DefaultRequester[HttpClient, R], lang.Abstract, ta.Generic[R]):
    def _do(
            self,
            request: HttpRequest,  # noqa
            *,
            context: HttpClientContext | None = None,
            check: bool = False,
            client: HttpClient | None = None,  # noqa
    ) -> R:
        if context is None:
            context = HttpClientContext()

        if client is not None:
            return self._do_(
                client,
                context,
                request,
                check=check,
            )

        else:
            with _default_client() as client:  # noqa
                return self._do_(
                    client,
                    context,
                    request,
                    check=check,
                )

    @abc.abstractmethod
    def _do_(
            self,
            client: HttpClient,  # noqa
            context: HttpClientContext,
            request: HttpRequest,  # noqa
            *,
            check: bool = False,  # noqa
    ) -> R:
        raise NotImplementedError


class _SyncDefaultRequester(_BaseSyncDefaultRequester[HttpResponse]):
    def _do_(
            self,
            client: HttpClient,  # noqa
            context: HttpClientContext,
            request: HttpRequest,  # noqa
            *,
            check: bool = False,  # noqa
    ) -> HttpResponse:
        return client.request(
            request,
            context=context,
            check=check,
        )


request = _SyncDefaultRequester()


##


def _default_async_client() -> AsyncHttpClient:
    return _httpx.HttpxAsyncHttpClient()


def async_client() -> AsyncHttpClient:
    return _default_async_client()


@contextlib.asynccontextmanager
async def manage_async_client(client: AsyncHttpClient | None = None) -> ta.AsyncGenerator[AsyncHttpClient]:  # noqa
    if client is not None:
        yield client

    else:
        async with _default_async_client() as client:  # noqa
            yield client


#


class _BaseAsyncDefaultRequester(_DefaultRequester[AsyncHttpClient, ta.Awaitable[R]], lang.Abstract, ta.Generic[R]):
    async def _do(
            self,
            request: HttpRequest,  # noqa
            *,
            context: HttpClientContext | None = None,
            check: bool = False,
            client: AsyncHttpClient | None = None,  # noqa
    ) -> R:
        if context is None:
            context = HttpClientContext()

        if client is not None:
            return await self._do_(
                client,
                context,
                request,
                check=check,
            )

        else:
            async with _default_async_client() as client:  # noqa
                return await self._do_(
                    client,
                    context,
                    request,
                    check=check,
                )

    @abc.abstractmethod
    def _do_(
            self,
            client: AsyncHttpClient,  # noqa
            context: HttpClientContext,
            request: HttpRequest,  # noqa
            *,
            check: bool = False,  # noqa
    ) -> ta.Awaitable[R]:
        raise NotImplementedError


class _AsyncDefaultRequester(_BaseAsyncDefaultRequester[HttpResponse]):
    async def _do_(
            self,
            client: AsyncHttpClient,  # noqa
            context: HttpClientContext,
            request: HttpRequest,  # noqa
            *,
            check: bool = False,
    ) -> HttpResponse:  # noqa
        return await client.request(
            request,
            context=context,
            check=check,
        )


async_request = _AsyncDefaultRequester()
