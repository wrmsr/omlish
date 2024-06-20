import abc
import dataclasses as dc
import typing as ta

from ... import check
from ... import lang
from .fields import preprocess_field
from .frozen import FrozenProcessor
from .hashing import HashProcessor
from .init import InitProcessor
from .internals import FIELDS_ATTR
from .internals import PARAMS_ATTR
from .internals import Params
from .internals import is_kw_only
from .order import OrderProcessor
from .params import ParamsExtras
from .processing import Processor
from .reflect import ClassInfo
from .repr import ReprProcessor
from .simple import DocProcessor
from .simple import EqProcessor
from .simple import MatchArgsProcessor
from .simple import OverridesProcessor
from .simple import ReplaceProcessor
from .slots import add_slots

if ta.TYPE_CHECKING:
    from . import metaclass
else:
    metaclass = lang.proxy_import('.metaclass', __package__)


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

    def _check_frozen_bases(self) -> None:
        mc_base = getattr(metaclass, 'Data', None)
        all_frozen_bases = None
        any_frozen_base = False
        has_dataclass_bases = False
        for b in self._cls.__mro__[-1:0:-1]:
            if b is mc_base:
                continue
            base_fields = getattr(b, FIELDS_ATTR, None)
            if base_fields is not None:
                has_dataclass_bases = True
                if all_frozen_bases is None:
                    all_frozen_bases = True
                current_frozen = getattr(b, PARAMS_ATTR).frozen
                all_frozen_bases = all_frozen_bases and current_frozen
                any_frozen_base = any_frozen_base or current_frozen

        if has_dataclass_bases:
            if any_frozen_base and not self._info.params.frozen:
                raise TypeError('cannot inherit non-frozen dataclass from a frozen one')

            if all_frozen_bases is False and self._info.params.frozen:
                raise TypeError('cannot inherit frozen dataclass from a non-frozen one')

    @lang.cached_function
    def _process_fields(self) -> None:
        fields: dict[str, dc.Field] = {}

        for b in self._cls.__mro__[-1:0:-1]:
            base_fields = getattr(b, FIELDS_ATTR, None)
            if base_fields is not None:
                for f in base_fields.values():
                    fields[f.name] = f

        cls_fields: list[dc.Field] = []

        kw_only = self._info.params12.kw_only
        kw_only_seen = False
        for name, ann in self._info.cls_annotations.items():
            if is_kw_only(self._cls, ann):
                if kw_only_seen:
                    raise TypeError(f'{name!r} is KW_ONLY, but KW_ONLY has already been specified')
                kw_only_seen = True
                kw_only = True
            else:
                cls_fields.append(preprocess_field(self._cls, name, ann, kw_only))

        for f in cls_fields:
            fields[f.name] = f
            if isinstance(getattr(self._cls, f.name, None), dc.Field):
                if f.default is MISSING:
                    delattr(self._cls, f.name)
                else:
                    setattr(self._cls, f.name, f.default)

        for name, value in self._cls.__dict__.items():
            if isinstance(value, dc.Field) and name not in self._info.cls_annotations:
                raise TypeError(f'{name!r} is a field but has no type annotation')

        setattr(self._cls, FIELDS_ATTR, fields)

    @lang.cached_function
    def _transform_slots(self) -> None:
        if self._info.params12.weakref_slot and not self._info.params12.slots:
            raise TypeError('weakref_slot is True but slots is False')
        if not self._info.params12.slots:
            return
        self._cls = add_slots(self._cls, self._info.params.frozen, self._info.params12.weakref_slot)

    @lang.cached_function
    def process(self) -> type:
        self._check_params()
        self._check_frozen_bases()

        self._process_fields()

        pcls: type[Processor]
        for pcls in [
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
        ]:
            pcls(self._info).process()

        self._transform_slots()

        abc.update_abstractmethods(self._cls)  # noqa

        return self._cls


def process_class(cls: type) -> type:
    return MainProcessor(cls).process()
