import abc
import dataclasses as dc
import typing as ta

from ..specs import ClassSpec
from .ops import Op
from .ops import OpRefMap


T = ta.TypeVar('T')
PlanT = ta.TypeVar('PlanT')


##


@dc.dataclass(frozen=True)
class Plan(abc.ABC):  # noqa
    pass


##


class PlanContext:
    def __init__(
            self,
            cls: type,
            cs: ClassSpec,
            item_factories: ta.Mapping[type, ta.Callable[['PlanContext'], ta.Any]],
    ) -> None:
        super().__init__()

        self._cls = cls
        self._cs = cs
        self._item_factories = item_factories

        self._items: dict = {}

    @property
    def cls(self) -> type:
        return self._cls

    @property
    def cs(self) -> ClassSpec:
        return self._cs

    def __getitem__(self, ty: type[T]) -> T:
        try:
            return self._items[ty]
        except KeyError:
            pass

        fac = self._item_factories[ty]
        ret = fac(self)
        self._items[ty] = ret
        return ret


@dc.dataclass(frozen=True)
class PlanResult(ta.Generic[PlanT]):
    plan: PlanT
    ref_map: OpRefMap | None = None


class Generator(abc.ABC, ta.Generic[PlanT]):
    @abc.abstractmethod
    def plan(self, ctx: PlanContext) -> PlanResult[PlanT] | None:
        raise NotImplementedError

    @abc.abstractmethod
    def generate(self, pl: PlanT) -> ta.Iterable[Op]:
        raise NotImplementedError
