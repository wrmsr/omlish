import pytest

from ... import check
from ... import dataclasses as dc
from ... import inject as inj
from ..base import AsyncLifecycle
from ..base import Lifecycle
from ..contextmanagers import AsyncLifecycleContextManager
from ..contextmanagers import LifecycleContextManager
from ..injection import bind_async_lifecycle_registrar
from ..injection import bind_lifecycle_registrar
from ..managed import AsyncLifecycleManaged
from ..managed import LifecycleManaged
from ..manager import AsyncLifecycleManager
from ..manager import LifecycleManager
from ..unwrap import unwrap_async_lifecycle
from ..unwrap import unwrap_lifecycle


##


class DumbLifecycle(Lifecycle):
    def lifecycle_construct(self) -> None:
        print(f'{self}.lifecycle_construct')

    def lifecycle_start(self) -> None:
        print(f'{self}.lifecycle_start')

    def lifecycle_stop(self) -> None:
        print(f'{self}.lifecycle_stop')

    def lifecycle_destroy(self) -> None:
        print(f'{self}.lifecycle_destroy')


@dc.dataclass()
class Db(DumbLifecycle):
    pass


@dc.dataclass()
class ServiceA(DumbLifecycle):
    db: Db
    i: int


@dc.dataclass()
class ServiceB(DumbLifecycle):
    db: Db


@dc.dataclass()
class ServiceC(DumbLifecycle):
    a: ServiceA
    b: ServiceB
    db: Db


@dc.dataclass()
class ServiceD(LifecycleManaged):
    c: ServiceC

    def _lifecycle_start(self) -> None:
        print('ServiceD started')


def test_inject():
    with inj.create_managed_injector(
        bind_lifecycle_registrar(),
            inj.bind(LifecycleManager, singleton=True, eager=True),

            inj.bind(Db, singleton=True),
            inj.bind(ServiceA, singleton=True),
            inj.bind(ServiceB, singleton=True),
            inj.bind(ServiceC, singleton=True, eager=True),
            inj.bind(ServiceD, singleton=True, eager=True),

            inj.bind(420),
    ) as i:  # noqa
        print()
        with LifecycleContextManager(check.not_none(unwrap_lifecycle(i[LifecycleManager]))):
            print(i[ServiceC])


##


class DumbAsyncLifecycle(AsyncLifecycle):
    async def lifecycle_construct(self) -> None:
        print(f'{self}.lifecycle_construct')

    async def lifecycle_start(self) -> None:
        print(f'{self}.lifecycle_start')

    async def lifecycle_stop(self) -> None:
        print(f'{self}.lifecycle_stop')

    async def lifecycle_destroy(self) -> None:
        print(f'{self}.lifecycle_destroy')


@dc.dataclass()
class AsyncDb(DumbAsyncLifecycle):
    pass


@dc.dataclass()
class AsyncServiceA(DumbAsyncLifecycle):
    db: AsyncDb
    i: int


@dc.dataclass()
class AsyncServiceB(DumbAsyncLifecycle):
    db: AsyncDb


@dc.dataclass()
class AsyncServiceC(DumbAsyncLifecycle):
    a: AsyncServiceA
    b: AsyncServiceB
    db: AsyncDb


@dc.dataclass()
class AsyncServiceD(AsyncLifecycleManaged):
    c: AsyncServiceC

    async def _lifecycle_start(self) -> None:
        print('ServiceD started')


@pytest.mark.asyncs('asyncio')
async def test_async_inject():
    async with inj.create_async_managed_injector(
            bind_async_lifecycle_registrar(),
            inj.bind(AsyncLifecycleManager, singleton=True, eager=True),

            inj.bind(AsyncDb, singleton=True),
            inj.bind(AsyncServiceA, singleton=True),
            inj.bind(AsyncServiceB, singleton=True),
            inj.bind(AsyncServiceC, singleton=True, eager=True),
            inj.bind(AsyncServiceD, singleton=True, eager=True),

            inj.bind(420),
    ) as i:  # noqa
        print()
        async with AsyncLifecycleContextManager(check.not_none(unwrap_async_lifecycle(await i[AsyncLifecycleManager]))):
            print(await i[AsyncServiceC])
