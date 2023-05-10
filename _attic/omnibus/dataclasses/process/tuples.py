import dataclasses as dc
import typing as ta

from .. import construction as csn
from ... import check
from ... import code
from ... import properties
from ..internals import FieldType
from ..internals import get_field_type
from ..types import ExtraFieldParams
from .descriptors import AbstractFieldDescriptor
from .init import append_argspec_args
from .init import Init
from .storage import Storage
from .types import Aspect
from .types import attach


class TupleFieldDescriptor(AbstractFieldDescriptor):

    def __init__(self, idx: ta.Optional[int], **kwargs) -> None:
        super().__init__(**kwargs)

        self._idx = idx

    def _get(self, instance):
        return instance[self._idx]

    def _set(self, instance, value):
        raise TypeError

    def _del(self, instance):
        raise TypeError


class TupleStorage(Storage):

    def check(self) -> None:
        if not self.ctx.inspecting:
            check.state(issubclass(self.ctx.cls, tuple))
        check.state(self.ctx.spec.params.frozen)
        check.state(not self.ctx.spec.extra_params.allow_setattr)

    @properties.cached
    def idxs_by_field_name(self) -> ta.Mapping[str, int]:
        dct = {}
        for f in self.ctx.spec.fields.init:
            if get_field_type(f) is FieldType.INIT:
                continue
            dct[f.name] = len(dct)
        return dct

    def process(self) -> ta.Sequence[csn.Action]:
        # FIXME: should ClassVars should get field_attrs (instead of returning default)?
        for fld in self.ctx.spec.fields.instance:
            default = fld if self.ctx.spec.extra_params.field_attrs else \
                fld.default if fld.default is not dc.MISSING else dc.MISSING
            fefp = fld.metadata.get(ExtraFieldParams, ExtraFieldParams())
            frozen = bool(fefp.frozen if fefp.frozen is not None else self.ctx.spec.params.frozen)
            dsc = TupleFieldDescriptor(
                self.idxs_by_field_name.get(fld.name),
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
    class Building(Storage.Building['TupleStorage']):

        def build_raw_set_field(self, fld: dc.Field, value: str) -> str:
            raise TypeError

    @attach('init')
    class Init(Storage.Function['TupleStorage']):

        @properties.cached
        def cls_name(self) -> str:
            return self.fctx.nsb.put(None, '_cls')

        @attach(Aspect.Function.Phase.SET_ATTRS)
        def build_set_attr_lines(self) -> ta.List[str]:
            tuple_new = self.fctx.nsb.put(tuple.__new__, '_tuple_new')
            args = (', '.join(self.aspect.idxs_by_field_name) + ',') if self.aspect.idxs_by_field_name else ''
            return [f'{self.fctx.self_name} = {tuple_new}({self.cls_name}, ({args}))']  # noqa


class TupleInit(Init):

    def process(self) -> ta.Sequence[csn.Action]:
        if not self.ctx.spec.params.init:
            return []

        fctx = self.ctx.function(['init'])
        init = fctx.get_aspect(TupleInit.Init)
        fn = init.build('__new__')
        self.ctx.set_new_attribute('__new__', fn)
        return []

    @attach('init')
    class Init(Aspect.Function['TupleInit']):

        @properties.cached
        def argspec(self) -> code.ArgSpec:
            argspec = code.ArgSpec(
                [self.fctx.get_aspect(TupleStorage.Init).cls_name],
                annotations={'return': self.fctx.nsb.put(self.fctx.ctx.cls)},
            )
            return append_argspec_args(
                argspec,
                self.fctx.ctx.spec.fields.init,
                kwonly=self.fctx.ctx.spec.extra_params.kwonly,
            )

        @attach(Aspect.Function.Phase.RETURN)
        def build_return_lines(self) -> ta.List[str]:
            return [f'return {self.fctx.self_name}']


ASPECT_REPLACEMENTS = {
    Init: TupleInit,
    Storage: TupleStorage,
}
