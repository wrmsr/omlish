import abc
import dataclasses as dc
import typing as ta

from ..ops import Op
from ..ops import OpRefMap
from ..specs import ClassSpec


PlanT = ta.TypeVar('PlanT')


##


@dc.dataclass(frozen=True)
class Plan(abc.ABC):  # noqa
    pass


##


@dc.dataclass(frozen=True)
class PlanResult(ta.Generic[PlanT]):
    plan: PlanT
    ref_map: OpRefMap | None = None


class Generator(abc.ABC, ta.Generic[PlanT]):
    @abc.abstractmethod
    def plan(self, cls: type, cs: ClassSpec) -> PlanResult[PlanT] | None:
        raise NotImplementedError

    @abc.abstractmethod
    def generate(self, pl: PlanT) -> ta.Iterable[Op]:
        raise NotImplementedError
