from ... import dataclasses as dc
from ... import inject as inj
from ..base import Lifecycle
from ..contextmanagers import LifecycleContextManager
from ..injection import bind_lifecycle_registrar
from ..managed import LifecycleManaged
from ..manager import LifecycleManager


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
        with LifecycleContextManager(i[LifecycleManager].lifecycle):
            print(i[ServiceC])
