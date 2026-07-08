import typing as ta

from ... import check
from ... import dataclasses as dc
from ... import marshal as msh
from ... import reflect2 as rfl
from .. import jsonschema as jsch
from .openapi import Reference
from .openapi import Schema


##


def _reference_union_arg(rty: rfl.Type) -> rfl.Type | None:
    if (
            isinstance(rty, rfl.UnionType) and
            len(rty.items) == 2 and
            any(rfl.get_runtime_type_or_none(it) is Reference for it in rty.items)
    ):
        return check.single(it for it in rty.items if rfl.get_runtime_type_or_none(it) is not Reference)
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


class _ReferenceUnionMarshalerFactory(msh.MarshalerFactory):
    def make_marshaler(self, ctx: msh.MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Marshaler] | None:
        if (rua := _reference_union_arg(rty)) is None:
            return None
        return lambda: _ReferenceUnionMarshaler(
            ctx.make_marshaler(check.not_none(rua)),
            ctx.make_marshaler(Reference),
        )


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


class _ReferenceUnionUnmarshalerFactory(msh.UnmarshalerFactory):
    def make_unmarshaler(self, ctx: msh.UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Unmarshaler] | None:  # noqa
        if (rua := _reference_union_arg(rty)) is None:
            return None
        return lambda: _ReferenceUnionUnmarshaler(
            ctx.make_unmarshaler(check.not_none(rua)),
            ctx.make_unmarshaler(Reference),
        )


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
        if (skw := sch.keywords) is not None:
            dct.update(check.isinstance(self.kw_m.marshal(ctx, skw), ta.Mapping))
        return dct


class _SchemaMarshalerFactory(msh.MarshalerFactory):
    def make_marshaler(self, ctx: msh.MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Marshaler] | None:
        if rfl.get_runtime_type_or_none(rty) is not Schema:
            return None
        return lambda: _SchemaMarshaler(
            {
                f: (msh.translate_name(f, msh.Naming.LOW_CAMEL), ctx.make_marshaler(a))
                for f, a in dc.reflect(Schema).field_annotations.items()
                if f != 'keywords'
            },
            ctx.make_marshaler(jsch.Keywords),
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


class _SchemaUnmarshalerFactory(msh.UnmarshalerFactory):
    def make_unmarshaler(self, ctx: msh.UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Unmarshaler] | None:  # noqa
        if rfl.get_runtime_type_or_none(rty) is not Schema:
            return None
        return lambda: _SchemaUnmarshaler(
            {
                msh.translate_name(f, msh.Naming.LOW_CAMEL): (f, ctx.make_unmarshaler(a))
                for f, a in dc.reflect(Schema).field_annotations.items()
                if f != 'keywords'
            },
            ctx.make_unmarshaler(jsch.Keywords),
        )


##


@msh.register_global_lazy_init
def _install_standard_marshaling(cfgs: msh.ConfigRegistry) -> None:
    msh.install_standard_factories(
        cfgs,

        _ReferenceUnionMarshalerFactory(),
        _ReferenceUnionUnmarshalerFactory(),

        _SchemaMarshalerFactory(),
        _SchemaUnmarshalerFactory(),
    )
