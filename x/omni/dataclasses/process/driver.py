import typing as ta

from .. import construction as csn
from ... import check
from .bootstrap import Fields
from .bootstrap import FixVarAnnotations
from .bootstrap import Params
from .bootstrap import Slots
from .coercion import Coercion
from .defaulting import Defaulting
from .init import StandardInit
from .simple import Doc
from .simple import Eq
from .simple import Frozen
from .simple import Hash
from .simple import Iterable
from .simple import Order
from .simple import Pickle
from .simple import Placeholders
from .simple import PostInitAspect
from .simple import Repr
from .storage import StandardStorage
from .types import Context
from .validation import Validation


TypeT = ta.TypeVar('TypeT', bound=type, covariant=True)


DEFAULT_ASPECTS = {

    Coercion,
    Defaulting,
    Doc,
    Eq,
    Fields,
    FixVarAnnotations,
    Frozen,
    Hash,
    Iterable,
    Order,
    Params,
    Pickle,
    Placeholders,
    PostInitAspect,
    Repr,
    Slots,
    StandardInit,
    StandardStorage,
    Validation,

}


class Driver(ta.Generic[TypeT]):

    def __init__(self, ctx: Context[TypeT]) -> None:
        super().__init__()

        self._ctx = check.isinstance(ctx, Context)

    @property
    def ctx(self) -> Context[TypeT]:
        return self._ctx

    def __call__(self) -> None:
        actions: ta.List[csn.Action] = []
        for aspects in self.ctx.aspect_plan:
            for aspect in aspects:
                aspect.check()
            for aspect in aspects:
                for action in aspect.process():
                    actions.append(action)

        cctx = csn.Context(self.ctx.spec)
        for act in actions:
            csn.apply(act, cctx)
