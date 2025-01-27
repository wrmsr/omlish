import abc
import dataclasses as dc
import typing as ta

from ... import check
from ... import lang
from .copy import CopyProcessor
from .fields import FieldsProcessor
from .frozen import FrozenProcessor
from .hashing import HashProcessor
from .init import InitProcessor
from .internals import FIELDS_ATTR
from .internals import PARAMS_ATTR
from .internals import Params
from .order import OrderProcessor
from .overrides import OverridesProcessor
from .params import ParamsExtras
from .processing import Processor
from .reflect import ClassInfo
from .replace import ReplaceProcessor
from .repr import ReprProcessor
from .simple import DocProcessor
from .simple import EqProcessor
from .simple import MatchArgsProcessor
from .slots import add_slots


MISSING = dc.MISSING


class MainProcessor:
    def __init__(self, cls: type) -> None:
        super().__init__()

        self._cls = check.isinstance(cls, type)
        self._info = info = ClassInfo(cls, _constructing=True)

        check.not_in(FIELDS_ATTR, cls.__dict__)
        check.is_(check.isinstance(cls.__dict__[PARAMS_ATTR], Params), info.params)
        check.is_(check.isinstance(check.not_none(info.cls_metadata)[ParamsExtras], ParamsExtras), info.params_extras)  # noqa

    def _check_params(self) -> None:
        if self._info.params.order and not self._info.params.eq:
            raise ValueError('eq must be true if order is true')

    @lang.cached_function
    def _transform_slots(self) -> None:
        if self._info.params.weakref_slot and not self._info.params.slots:
            raise TypeError('weakref_slot is True but slots is False')
        if not self._info.params.slots:
            return
        self._cls = add_slots(self._cls, self._info.params.frozen, self._info.params.weakref_slot)

    PROCESSOR_TYPES: ta.ClassVar[ta.Sequence[type[Processor]]] = [
        FieldsProcessor,
        InitProcessor,
        OverridesProcessor,
        ReprProcessor,
        EqProcessor,
        OrderProcessor,
        FrozenProcessor,
        HashProcessor,
        DocProcessor,
        MatchArgsProcessor,
        ReplaceProcessor,
        CopyProcessor,
    ]

    @lang.cached_function
    def process(self) -> type:
        self._check_params()

        ps = [pcls(self._info) for pcls in self.PROCESSOR_TYPES]

        for p in ps:
            p.check()

        for p in ps:
            p.process()

        self._transform_slots()

        abc.update_abstractmethods(self._cls)  # noqa

        return self._cls


def process_class(cls: type) -> type:
    return MainProcessor(cls).process()
