"""
TODO:
 - need to re-run checks/validators on all mutations
 - nesting
 - rebuilding from existing
  - stubbing (query comp cache)

Backends:
 - struct
  - w/ bitfield packing
 - arrays
  - numpy
  - mmap
 - configs? reverse (gen cfg cls's w/ getters from dc defs)?
 - 'direct'
"""
import abc
import dataclasses as dc
import typing as ta

from .. import construction as csn
from . import bootstrap
from ... import check
from ... import code
from ... import lang
from ... import properties
from ..internals import FieldType
from ..internals import get_field_type
from ..types import ExtraFieldParams
from ..types import Mangling
from ..types import METADATA_ATTR
from .descriptors import FieldDescriptor
from .types import Aspect
from .types import attach


StorageT = ta.TypeVar('StorageT', bound='Storage', covariant=True)


class Storage(Aspect, lang.Abstract):

    @property
    def deps(self) -> ta.Collection[ta.Type[Aspect]]:
        return [bootstrap.Fields]

    @abc.abstractmethod
    def process(self) -> ta.Sequence[csn.Action]:
        raise NotImplementedError

    @attach(Aspect.Function)
    class Building(Aspect.Function[StorageT], lang.Abstract):

        @abc.abstractmethod
        def build_raw_set_field(self, fld: dc.Field, value: str) -> str:
            raise NotImplementedError

    @attach('init')
    class Init(Aspect.Function[StorageT]):

        @attach(Aspect.Function.Phase.SET_ATTRS)
        def build_set_attr_lines(self) -> ta.List[str]:
            ret = []
            for f in self.fctx.ctx.spec.fields.init:
                if get_field_type(f) is not FieldType.INSTANCE:
                    continue
                if not f.init and f.default_factory is dc.MISSING:
                    continue
                ret.append(self.fctx.get_aspect(self.aspect.Building).build_raw_set_field(f, f.name))
            return ret

    def build_pre_set(self, field: dc.Field) -> ta.Optional[ta.Callable[[object, object], object]]:
        fctx = self.ctx.function(['pre_set'], field=field)
        aspect = fctx.get_aspect(Storage.PreSet)
        return aspect.build(f'_pre_set__{field.name}', optional=True, optional_phases={Aspect.Function.Phase.RETURN})

    @attach('pre_set')
    class PreSet(Aspect.Function['Storage']):

        @properties.cached
        def argspec(self) -> code.ArgSpec:
            ty = self.fctx.nsb.put(self.fctx.field.type)
            return code.ArgSpec(
                [self.fctx.self_name, self.fctx.field.name],
                annotations={'return': ty, self.fctx.field.name: ty},
            )

        @attach(Aspect.Function.Phase.RETURN)
        def build_return_lines(self) -> ta.List[str]:
            return [f'return {self.fctx.field.name}']

    def build_post_set(self, field: dc.Field) -> ta.Optional[ta.Callable[[object, object], None]]:
        fctx = self.ctx.function(['post_set'], field=field)
        aspect = fctx.get_aspect(Storage.PostSet)
        return aspect.build(f'_post_set__{field.name}', optional=True)

    @attach('post_set')
    class PostSet(Aspect.Function['Storage']):

        @properties.cached
        def argspec(self) -> code.ArgSpec:
            ty = self.fctx.nsb.put(self.fctx.field.type)
            return code.ArgSpec(
                [self.fctx.self_name, self.fctx.field.name],
                annotations={'return': None, self.fctx.field.name: ty},
            )


class StandardStorage(Storage):

    @property
    def slots(self) -> ta.AbstractSet[str]:
        return set(self.mangling)

    @properties.cached
    def mangling(self) -> Mangling:
        dct = {}
        names = set(self.ctx.spec.fields.by_name)
        for fld in self.ctx.spec.fields:
            efp = fld.metadata.get(ExtraFieldParams)
            if efp is not None and efp.mangled is not None:
                mang = efp.mangled
            else:
                if self.ctx.spec.extra_params.mangler is not None:
                    fn = self.ctx.spec.extra_params.mangler
                else:
                    fn = lambda n: '_' + n
                mang = fn(fld.name)
            if mang in dct or mang in names:
                raise NameError(dct)
            dct[mang] = fld.name
        return Mangling(dct)

    def process(self) -> ta.Sequence[csn.Action]:
        metadata = self.ctx.cls.__dict__.get(METADATA_ATTR, {})
        if Mangling in metadata:
            raise KeyError(Mangling)
        metadata[Mangling] = self.mangling
        check.state(self.ctx.spec.mangling is self.mangling)
        check.state(self.ctx.spec.unmangling is not None)

        # FIXME: should ClassVars should get field_attrs (instead of returning default)?
        for fld in self.ctx.spec.fields.instance:
            default = fld if self.ctx.spec.extra_params.field_attrs else \
                fld.default if fld.default is not dc.MISSING else dc.MISSING
            fefp = fld.metadata.get(ExtraFieldParams, ExtraFieldParams())
            frozen = bool(fefp.frozen if fefp.frozen is not None else self.ctx.spec.params.frozen)
            dsc = FieldDescriptor(
                self.ctx.spec.unmangling[fld.name],
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
    class Building(Storage.Building['StandardStorage']):

        @properties.cached
        def setattr_name(self) -> str:
            return self.fctx.nsb.put(object.__setattr__, '__setattr__')

        def build_raw_set_field(self, fld: dc.Field, value: str) -> str:
            umd = self.fctx.ctx.spec.unmangling
            name = umd[fld.name] if umd is not None else fld.name
            return f'{self.setattr_name}({self.fctx.self_name}, {name!r}, {value})'
