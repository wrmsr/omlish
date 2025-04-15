import abc
import dataclasses as dc
import typing as ta

from ..processing.base import ProcessingContext
from .ops import Op
from .ops import OpRefMap


T = ta.TypeVar('T')
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
    def plan(self, ctx: ProcessingContext) -> PlanResult[PlanT] | None:
        raise NotImplementedError

    @abc.abstractmethod
    def generate(self, pl: PlanT) -> ta.Iterable[Op]:
        raise NotImplementedError
