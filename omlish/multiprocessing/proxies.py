import dataclasses as dc
import typing as ta

from .. import lang


T = ta.TypeVar('T')


@ta.runtime_checkable
class ValueProxy(ta.Protocol[T]):
    # value = property(get, set)

    def get(self) -> T:
        ...

    def set(self, value: T) -> None:
        ...


@dc.dataclass()
@lang.protocol_check(ValueProxy)
class DummyValueProxy(ValueProxy[T]):
    value: T

    def get(self) -> T:
        return self.value

    def set(self, value: T) -> None:
        self.value = value
