import abc
import urllib.error
import urllib.request
import typing as ta

from omlish import dataclasses as dc
from omlish import lang


@dc.dataclass(frozen=True)
class HttpRequest(lang.Final):
    url: str
    method: str = 'GET'

    _: dc.KW_ONLY

    headers: ta.Mapping[str, str] | None = None
    data: bytes | None = None


@dc.dataclass(frozen=True)
class HttpResponse(lang.Final):
    req: HttpRequest

    _: dc.KW_ONLY

    underlying: ta.Any = None


class HttpError(Exception):
    pass


class HttpClient(lang.Abstract):
    def __enter__(self) -> ta.Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @abc.abstractmethod
    def request(self, req: HttpRequest) -> HttpResponse:
        raise NotImplementedError


class UrllibHttpClient(HttpClient):
    def request(self, req: HttpRequest) -> HttpResponse:
        try:
            with urllib.request.urlopen(urllib.request.Request(
                    req.url,
                    method=req.method,
                    headers=req.headers or {},
                    data=req.data,
            )) as resp:
                return HttpResponse(
                    req=req,
                    underlying=resp,
                )
        except urllib.error.URLError as e:
            raise HttpError() from e


def _main() -> None:
    with UrllibHttpClient() as cli:
        resp = cli.request(HttpRequest('https://www.google.com'))
        print(resp)


if __name__ == '__main__':
    _main()
