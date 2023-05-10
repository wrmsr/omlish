"""
TODO:
 - def __dataclass_replace__(self, ...
"""
import dataclasses as dc
import typing as ta

from .. import construction as csn
from ... import check
from ... import collections as ocol
from ... import properties
from ..internals import FieldType
from ..internals import get_field_type
from .storage import Storage
from .types import Aspect
from .types import attach


class PersistentDescriptor:

    def __init__(
            self,
            field: dc.Field,
            seq_attr: str,
            idx: int,
            *,
            field_attrs: bool = False,
    ) -> None:
        super().__init__()

        self._field = field
        self._seq_attr = seq_attr
        self._idx = idx
        self._field_attrs = field_attrs

    def __get__(self, instance, owner=None):
        if instance is not None:
            seq = getattr(instance, self._seq_attr)
            try:
                return seq[self._idx]
            except IndexError:
                raise AttributeError(self._field.name)
        elif self._field_attrs is not None:
            return self._field
        else:
            return self


class PersistentStorage(Storage):

    @property
    def seq_ctor(self) -> ta.Callable:
        return ocol.PyrsistentSequence

    @properties.cached
    def seq_attr(self) -> str:
        return '__%s_%x_seq' % (self.ctx.cls.__name__, id(self.ctx.cls))

    def check(self) -> None:
        check.state(check.not_none(self.ctx.spec.params).frozen)

    def process(self) -> ta.Sequence[csn.Action]:
        for idx, fld in enumerate(self.ctx.spec.fields.instance):
            dsc = PersistentDescriptor(
                fld,
                self.seq_attr,
                idx,
                field_attrs=self.ctx.spec.extra_params.field_attrs,
            )
            self.ctx.set_new_attribute(fld.name, dsc)

        return []

    @attach('init')
    class Init(Storage.Function['PersistentStorage']):

        @attach(Aspect.Function.Phase.SET_ATTRS)
        def build_set_attr_lines(self) -> ta.List[str]:
            args = []
            for f in self.fctx.ctx.spec.fields.init:
                if get_field_type(f) is FieldType.INIT:
                    continue
                if not f.init and f.default_factory is dc.MISSING:
                    continue
                args.append(f.name)
            seq_new = self.fctx.nsb.put(self.aspect.seq_ctor, '_seq_new')
            return [
                self.fctx.get_aspect(Storage.Function).build_setattr(
                    self.aspect.seq_attr, f'{seq_new}(({", ".join(args)}),)')
            ]
