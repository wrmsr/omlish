import abc
import typing as ta
import uuid

from omlish import dataclasses as dc
from omlish import lang
from omlish import typedvalues as tv


##


@dc.dataclass(frozen=True)
class Event(lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class Action(lang.Abstract, lang.PackageSealed):
    pass


##


class DriverId(tv.UniqueScalarTypedValue[uuid.UUID]):
    pass


class DriverGetter(lang.Func0[ta.Awaitable['Driver']]):
    pass


class Driver(lang.Abstract):
    async def start(self) -> None:
        pass

    async def stop(self) -> None:
        pass

    @abc.abstractmethod
    def do_action(self, action: Action) -> ta.Awaitable[None]:
        raise NotImplementedError
