"""
TODO:
 - CancellableFuture
"""
import abc
import typing as ta

import anyio

from ... import lang


T = ta.TypeVar('T')


##


class FutureError(Exception):
    pass


class FutureOutcomeAlreadySetError(FutureError):
    pass


##


class Future(lang.Abstract, ta.Awaitable[lang.Outcome[T]]):
    @abc.abstractmethod
    def __await__(self):
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def outcome(self) -> lang.Maybe[lang.Outcome[T]]:
        raise NotImplementedError

    @abc.abstractmethod
    def set_outcome(self, o: lang.Outcome[T]) -> None:
        raise NotImplementedError

    def set_value(self, v: T) -> None:
        self.set_outcome(lang.value(v))

    def set_error(self, e: BaseException) -> None:
        self.set_outcome(lang.error(e))


##


class _FutureImpl(Future[T]):
    def __init__(self, *, event: anyio.Event | None = None) -> None:
        super().__init__()

        self._outcome: lang.Maybe[lang.Outcome[T]] = lang.empty()

        if event is None:
            event = anyio.Event()
        self._event = event

    def __await__(self):
        if (o := self._outcome).present:
            return o
        yield from self._event.wait().__await__()
        return self._outcome.must()

    @property
    def outcome(self) -> lang.Maybe[lang.Outcome[T]]:
        return self._outcome

    def set_outcome(self, o: lang.Outcome[T]) -> None:
        if self._outcome.present:
            raise FutureOutcomeAlreadySetError
        self._outcome = lang.just(o)
        self._event.set()


##


def _create_future() -> Future[T]:
    return _FutureImpl()


# PEP695 workaround
class create_future(Future[T]):  # noqa
    def __new__(cls) -> Future[T]:  # type: ignore[misc]
        return _create_future()

    def __init__(self) -> None:
        raise TypeError

    def __await__(self):
        raise TypeError

    @property
    def outcome(self) -> lang.Maybe[lang.Outcome[T]]:
        raise TypeError

    def set_outcome(self, o: lang.Outcome[T]) -> None:
        raise TypeError
