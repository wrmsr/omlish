import abc
import dataclasses as dc
import typing as ta

from omlish import cached

from ..ops import Op
from ..ops import OpRefMap
from ..specs import ClassSpec
from .analysis import ClassAnalysis


PlanT = ta.TypeVar('PlanT')


##


@dc.dataclass(frozen=True)
class Plan(abc.ABC):  # noqa
    pass


##


class PlanContext:
    def __init__(self, cls: type, cs: ClassSpec) -> None:
        super().__init__()

        self._cls = cls
        self._cs = cs

    @property
    def cls(self) -> type:
        return self._cls

    @property
    def cs(self) -> ClassSpec:
        return self._cs

    @cached.property
    def ana(self) -> ClassAnalysis:
        return ClassAnalysis(self._cls, self._cs)


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
