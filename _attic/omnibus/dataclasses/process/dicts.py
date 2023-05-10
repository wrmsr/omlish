import dataclasses as dc
import typing as ta

from .. import construction as csn
from ... import properties
from ..internals import FieldType
from ..internals import get_field_type
from ..types import ExtraFieldParams
from .descriptors import AbstractFieldDescriptor
from .storage import Storage
from .types import Aspect
from .types import attach


class DictFieldDescriptor(AbstractFieldDescriptor):

    def __init__(self, key: str, dict_attr: str, **kwargs) -> None:
        super().__init__(**kwargs)

        self._key = key
        self._dict_attr = dict_attr

    def _get(self, instance):
        try:
            return getattr(instance, self._dict_attr)[self._key]
        except KeyError:
            raise AttributeError(self._key)

    def _set(self, instance, value):
        getattr(instance, self._dict_attr)[self._key] = value

    def _del(self, instance):
        del getattr(instance, self._dict_attr)[self._key]


class DictStorage(Storage):

    DEFAULT_DICT_ATTR = '___dict'

    @properties.cached
    def dict_attr(self) -> str:
        return self.DEFAULT_DICT_ATTR

    @property
    def slots(self) -> ta.AbstractSet[str]:
        return {self.dict_attr} if self.dict_attr is not None else set()

    def check(self) -> None:
        if self.dict_attr in self.ctx.spec.fields.by_name:
            raise AttributeError(self.dict_attr)

    def process(self) -> ta.Sequence[csn.Action]:
        # FIXME: should ClassVars should get field_attrs (instead of returning default)?
        for fld in self.ctx.spec.fields.instance:
            default = fld if self.ctx.spec.extra_params.field_attrs else \
                fld.default if fld.default is not dc.MISSING else dc.MISSING
            fefp = fld.metadata.get(ExtraFieldParams, ExtraFieldParams())
            frozen = bool(fefp.frozen if fefp.frozen is not None else self.ctx.spec.params.frozen)
            dsc = DictFieldDescriptor(
                fld.name,
                self.dict_attr,
                default_=default,
                frozen=frozen,
                name=fld.name,
                pre_set=self.build_pre_set(fld),
                post_set=self.build_post_set(fld),
            )
            # FIXME: check not overwriting
            setattr(self.ctx.cls, fld.name, dsc)

        return []

    @attach(Aspect.Function)
    class Building(Storage.Building['DictStorage']):

        def build_raw_set_field(self, fld: dc.Field, value: str) -> str:
            return f'{self.fctx.self_name}.{self.aspect.dict_attr}[{fld.name!r}] = {value}'

    @attach('init')
    class Init(Storage.Init['DictStorage']):

        @properties.cached
        def setattr_name(self) -> str:
            return self.fctx.nsb.put(object.__setattr__, '__setattr__')

        @attach(Aspect.Function.Phase.BOOTSTRAP)
        def build_set_dict_lines(self) -> ta.List[str]:
            return [f'{self.setattr_name}(self, {self.aspect.dict_attr!r}, {{}})']

        @attach(Aspect.Function.Phase.SET_ATTRS)
        def build_set_default_attr_lines(self) -> ta.List[str]:
            ret = []
            for f in self.fctx.ctx.spec.fields.init:
                if get_field_type(f) is not FieldType.INSTANCE:
                    continue
                if f.default is dc.MISSING:
                    continue
                ret.append(self.fctx.get_aspect(self.aspect.Building).build_raw_set_field(f, f.name))
            return ret


ASPECT_REPLACEMENTS = {
    Storage: DictStorage,
}
