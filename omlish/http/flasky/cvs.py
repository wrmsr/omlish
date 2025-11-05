import contextlib
import contextvars
import typing as ta

from ... import dataclasses as dc
from ... import lang


if ta.TYPE_CHECKING:
    from .app import AppRunner
    from .requests import Request


T = ta.TypeVar('T')


##


@dc.dataclass()
class CvLookupError(LookupError):
    cv: 'Cv'


@ta.final
class Cv(ta.Generic[T]):
    def __init__(self, name: str) -> None:
        self._name = name
        self._var: contextvars.ContextVar[T] = contextvars.ContextVar(name)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._name!r})'

    def get(self) -> T:
        try:
            return self._var.get()
        except LookupError:
            raise CvLookupError(self) from None

    @contextlib.contextmanager
    def set(self, new: T) -> ta.Iterator[None]:
        tok = self._var.set(new)
        try:
            yield
        finally:
            self._var.reset(tok)


##


def _cv(name: str) -> Cv:
    return Cv(f'{__name__}.Cvs.{name}')


class Cvs(lang.Namespace, lang.Final):
    APP_RUNNER: Cv['AppRunner'] = _cv('APP_RUNNER')

    REQUEST: Cv['Request'] = _cv('REQUEST')
