import abc
import typing as ta

from .. import lang


AppT = ta.TypeVar('AppT', bound='App')
Environ: ta.TypeAlias = dict[str, ta.Any]
StartResponse: ta.TypeAlias = ta.Callable[[str, list[tuple[str, str]]], ta.Callable[[lang.BytesLike], None]]
RawApp: ta.TypeAlias = ta.Callable[[Environ, StartResponse], ta.Iterable[lang.BytesLike]]
AppLike: ta.TypeAlias = ta.Union['App', RawApp]
BadRequestExceptionT = ta.TypeVar('BadRequestExceptionT', bound='BadRequestException')


class BadRequestException(Exception):
    pass


class App(lang.Abstract):

    def __enter__(self: AppT) -> AppT:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        return None

    @abc.abstractmethod
    def __call__(self, environ: Environ, start_response: StartResponse) -> ta.Iterable[bytes]:
        raise NotImplementedError


# class AsyncApp(lang.Abstract):
#
#     async def __aenter__(self: AppT) -> AppT:
#         return self
#
#     async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
#         return None
#
#     @abc.abstractmethod
#     async def __call__(self, scope, receive, send) -> ta.Iterable[bytes]:
#         raise NotImplementedError
