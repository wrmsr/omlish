import typing as ta

from .. import lang


Environ = ta.Mapping[str, ta.Any]
StartResponse = ta.Callable[[str, ta.Iterable[tuple[str | bytes, str | bytes]]], ta.Callable[[lang.BytesLike], None]]
App = ta.Callable[[Environ, StartResponse], ta.Iterable[lang.BytesLike]]


# class App(lang.Abstract):
#
#     def __enter__(self: AppT) -> AppT:
#         return self
#
#     def __exit__(self, exc_type, exc_val, exc_tb) -> None:
#         return None
#
#     @abc.abstractmethod
#     def __call__(self, environ: Environ, start_response: StartResponse) -> ta.Iterable[bytes]:
#         raise NotImplementedError


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
