import abc
import typing as ta

from .. import lang


AppT = ta.TypeVar('AppT', bound='App')
Environ = ta.Dict[str, ta.Any]
StartResponse = ta.Callable[[str, ta.List[ta.Tuple[str, str]]], ta.Callable[[lang.BytesLike], None]]
RawApp = ta.Callable[[Environ, StartResponse], ta.Iterable[lang.BytesLike]]
AppLike = ta.Union['App', RawApp]
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
