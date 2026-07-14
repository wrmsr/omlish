# ruff: noqa: UP006 UP007 UP037 UP045
# @om-lite
import abc
import dataclasses as dc
import typing as ta
import urllib.parse

from ...lite.abstract import Abstract
from ...lite.bytes import Bytes
from ...lite.cached import cached_property
from ...lite.dataclasses import install_dataclass_kw_only_init
from ...lite.dataclasses import install_dataclass_repr
from ...lite.typemaps import TypeMap
from ...sockets.addresses import SocketAddress
from ..parsing import ParsedHttpHeaders
from ..statuses import HttpStatus


SimpleHttpHandler = ta.Callable[['SimpleHttpHandlerRequest'], 'SimpleHttpHandlerResponse']  # ta.TypeAlias
SimpleHttpHandlerResponseData = ta.Union[Bytes, 'SimpleHttpHandlerResponseStreamedData']  # ta.TypeAlias  # noqa


##


@install_dataclass_kw_only_init()
@dc.dataclass(frozen=True)
class SimpleHttpHandlerRequest:
    client_address: SocketAddress

    method: str
    path: str
    headers: ParsedHttpHeaders
    data: ta.Optional[Bytes] = None

    #

    context: TypeMap = TypeMap()

    def with_context(self, *items: ta.Any, override: bool = False) -> 'SimpleHttpHandlerRequest':
        return dc.replace(self, context=self.context.update(items, override=override))

    #

    @dc.dataclass(frozen=True)
    class Parsed:
        url: urllib.parse.SplitResult

        @classmethod
        def of(cls, path: str) -> 'SimpleHttpHandlerRequest.Parsed':
            return cls(urllib.parse.urlsplit(path))

        @cached_property
        def qs(self) -> ta.Mapping[str, ta.Sequence[str]]:
            return urllib.parse.parse_qs(
                self.url.query,
                keep_blank_values=True,
            )

    @cached_property
    def parsed(self) -> Parsed:
        return self.Parsed.of(self.path)


@install_dataclass_repr(filter='omit_none')
@install_dataclass_kw_only_init()
@dc.dataclass(frozen=True)
class SimpleHttpHandlerResponse:
    status: ta.Union[HttpStatus, int]
    headers: ta.Optional[ta.Mapping[str, str]] = None
    data: ta.Optional[SimpleHttpHandlerResponseData] = None
    close_connection: ta.Optional[bool] = None

    #

    context: TypeMap = TypeMap()

    def with_context(self, *items: ta.Any, override: bool = False) -> 'SimpleHttpHandlerResponse':
        return dc.replace(self, context=self.context.update(items, override=override))

    #

    def close(self) -> None:
        if isinstance(d := self.data, SimpleHttpHandlerResponseStreamedData):
            d.close()


@dc.dataclass(frozen=True)
class SimpleHttpHandlerResponseStreamedData:
    iter: ta.Iterable[Bytes]
    length: ta.Optional[int] = None

    def close(self) -> None:
        if hasattr(d := self.iter, 'close'):
            d.close()  # noqa


class SimpleHttpHandlerError(Exception):
    pass


class UnsupportedMethodSimpleHttpHandlerError(Exception):
    pass


class SimpleHttpHandler_(Abstract):  # noqa
    @abc.abstractmethod
    def __call__(self, req: SimpleHttpHandlerRequest) -> SimpleHttpHandlerResponse:
        raise NotImplementedError
