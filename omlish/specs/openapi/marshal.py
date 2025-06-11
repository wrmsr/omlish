import typing as ta

from ... import check
from ... import dataclasses as dc
from ... import lang
from ... import marshal as msh
from ... import reflect as rfl
from ...funcs import match as mfs
from .. import jsonschema as jsch
from .openapi import Reference
from .openapi import Schema


##


def _reference_union_arg(rty: rfl.Type) -> rfl.Type | None:
    if isinstance(rty, rfl.Union) and len(rty.args) == 2 and Reference in rty.args:
        return check.single(a for a in rty.args if a is not Reference)
    else:
        return None


#


@dc.dataclass(frozen=True)
class _ReferenceUnionMarshaler(msh.Marshaler):
    m: msh.Marshaler
    r: msh.Marshaler

    def marshal(self, ctx: msh.MarshalContext, o: ta.Any) -> msh.Value:
        if isinstance(o, Reference):
            return self.r.marshal(ctx, o)
        else:
            return self.m.marshal(ctx, o)


class _ReferenceUnionMarshalerFactory(msh.MarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: _reference_union_arg(rty) is not None)
    def _build(self, ctx: msh.MarshalContext, rty: rfl.Type) -> msh.Marshaler:
        return _ReferenceUnionMarshaler(ctx.make(check.not_none(_reference_union_arg(rty))), ctx.make(Reference))


#


@dc.dataclass(frozen=True)
class _ReferenceUnionUnmarshaler(msh.Unmarshaler):
    u: msh.Unmarshaler
    r: msh.Unmarshaler

    def unmarshal(self, ctx: msh.UnmarshalContext, v: msh.Value) -> ta.Any:
        if not isinstance(v, ta.Mapping):
            raise TypeError(v)
        elif '$ref' in v:
            return self.r.unmarshal(ctx, v)
        else:
            return self.u.unmarshal(ctx, v)  # noqa


class _ReferenceUnionUnmarshalerFactory(msh.UnmarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: _reference_union_arg(rty) is not None)
    def _build(self, ctx: msh.UnmarshalContext, rty: rfl.Type) -> msh.Unmarshaler:
        return _ReferenceUnionUnmarshaler(ctx.make(check.not_none(_reference_union_arg(rty))), ctx.make(Reference))


##


@dc.dataclass(frozen=True)
class _SchemaMarshaler(msh.Marshaler):
    m_dct: ta.Mapping[str, tuple[str, msh.Marshaler]]
    kw_m: msh.Marshaler

    def marshal(self, ctx: msh.MarshalContext, o: ta.Any) -> msh.Value:
        sch: Schema = check.isinstance(o, Schema)
        dct = {}
        for f, (k, fm) in self.m_dct.items():
            fv = getattr(sch, f)
            if fv is None:
                continue
            dct[k] = fm.marshal(ctx, fv)
        if sch.keywords is not None:
            dct.update(keywords=self.kw_m.marshal(ctx, sch.keywords))
        return dct


class _SchemaMarshalerFactory(msh.MarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: rty is Schema)
    def _build(self, ctx: msh.MarshalContext, rty: rfl.Type) -> msh.Marshaler:
        return _SchemaMarshaler(
            {
                f: (msh.translate_name(f, msh.Naming.LOW_CAMEL), ctx.make(rfl.type_(a)))
                for f, a in dc.reflect(Schema).field_annotations.items()
                if f != 'keywords'
            },
            ctx.make(jsch.Keywords),
        )


#


@dc.dataclass(frozen=True)
class _SchemaUnmarshaler(msh.Unmarshaler):
    u_dct: ta.Mapping[str, tuple[str, msh.Unmarshaler]]
    kw_u: msh.Unmarshaler

    def unmarshal(self, ctx: msh.UnmarshalContext, v: msh.Value) -> ta.Any:
        dct = dict(check.isinstance(v, ta.Mapping))
        kw = {}
        for k, (f, fu) in self.u_dct.items():
            try:
                kv = dct.pop(k)
            except KeyError:
                continue
            kw[f] = fu.unmarshal(ctx, kv)
        if dct:
            kw.update(keywords=self.kw_u.unmarshal(ctx, dct))
        return Schema(**kw)


class _SchemaUnmarshalerFactory(msh.UnmarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: rty is Schema)
    def _build(self, ctx: msh.UnmarshalContext, rty: rfl.Type) -> msh.Unmarshaler:
        return _SchemaUnmarshaler(
            {
                msh.translate_name(f, msh.Naming.LOW_CAMEL): (f, ctx.make(rfl.type_(a)))
                for f, a in dc.reflect(Schema).field_annotations.items()
                if f != 'keywords'
            },
            ctx.make(jsch.Keywords),
        )


##


@lang.static_init
def _install_standard_marshalling() -> None:
    msh.install_standard_factories(
        _ReferenceUnionMarshalerFactory(),
        _ReferenceUnionUnmarshalerFactory(),

        _SchemaMarshalerFactory(),
        _SchemaUnmarshalerFactory(),
    )
