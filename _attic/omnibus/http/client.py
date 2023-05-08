"""
TODO:
 - replace requests/urllib3
 - generic interface
 - models
 - chardet
 - pool
 - session
 - cookie
 - async
 - multipart
 - chunk
 - keepalive

https://docs.python.org/3/library/urllib.request.html
"""
import abc
import http.client
import typing as ta
import urllib.request

from .. import check
from .. import dataclasses as dc
from .. import lang


HttpResponseT = ta.TypeVar('HttpResponseT', bound='HttpResponse')


class HttpRequest(dc.Frozen):
    url: str = dc.field(validate=check.non_empty_str)


class HttpResponse(lang.Abstract, ta.Generic[HttpResponseT]):

    def __enter__(self) -> HttpResponseT:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @abc.abstractmethod
    def read(self, sz: ta.Optional[int] = None) -> bytes:
        raise NotImplementedError


class HttpClient(lang.Abstract):

    @abc.abstractmethod
    def request(self, request: HttpRequest) -> HttpResponse:
        raise NotImplementedError


class UrllibHttpResponse(HttpResponse['UrllibHttpResponse']):

    def __init__(self, obj: http.client.HTTPResponse) -> None:
        super().__init__()
        self._obj = check.isinstance(obj, http.client.HTTPResponse)

    def __enter__(self) -> 'UrllibHttpResponse':
        self._obj.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._obj.__exit__(exc_type, exc_val, exc_tb)

    def read(self, sz: ta.Optional[int] = None) -> bytes:
        return self._obj.read(sz)


class UrllibHttpClient(HttpClient):

    def request(self, request: HttpRequest) -> UrllibHttpResponse:
        obj = urllib.request.urlopen(request.url)
        return UrllibHttpResponse(obj)
