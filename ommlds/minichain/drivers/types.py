import abc
import typing as ta
import uuid as uuid_

from omlish import dataclasses as dc
from omlish import lang
from omlish import typedvalues as tv

from ..events.types import Event


##


@dc.dataclass(frozen=True)
class DriverEvent(Event, lang.Abstract):
    pass


##


@dc.dataclass(frozen=True)
class Action(lang.Abstract, lang.PackageSealed):
    _: dc.KW_ONLY

    uuid: uuid_.UUID = dc.field(default_factory=uuid_.uuid4, repr=False)


##


class DriverId(tv.UniqueScalarTypedValue[uuid_.UUID]):
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
