"""
FIXME:
 - everything lol
 - can this just do what metadata does
"""
import typing as ta

from omcore import check
from omcore import collections as col
from omcore import dataclasses as dc
from omcore import lang
from omcore import marshal as msh
from omcore import reflect as rfl
from omcore import typedvalues as tv

from ..metadata import CommonMetadata
from ..registries.globals import get_global_registry
from .requests import Request
from .requests import RequestMetadata
from .requests import RequestMetadatas
from .responses import Response
from .responses import ResponseMetadata
from .responses import ResponseMetadatas


##


def _get_rr_cls(rty: rfl.Type) -> type | None:
    if (
            (cls := rfl.get_runtime_type_or_none(rty)) is not None and
            issubclass(cls, (Request, Response))
    ):
        return cls
    return None


class _RrFlds(ta.NamedTuple):
    v: dc.Field
    tv: dc.Field
    md: dc.Field


def _get_rr_flds(rty: rfl.Type) -> _RrFlds:
    flds = col.make_map_by(lambda f: f.name, dc.fields(check.not_none(_get_rr_cls(rty))), strict=True)
    v_fld = flds.pop('v')
    md_fld = flds.pop('_metadata')
    return _RrFlds(
        v=v_fld,
        tv=check.single(flds.values()),
        md=md_fld,
    )


##


@dc.dataclass(frozen=True)
class _RequestResponseMarshaler(msh.Marshaler):
    rty: rfl.Type
    rr_flds: _RrFlds
    v_m: msh.Marshaler | None

    def marshal(self, ctx: msh.MarshalContext, o: ta.Any) -> msh.Value:
        tv_types_set = o._typed_values_info().tv_types_set  # noqa  # FIXME
        tv_ta = tv.TypedValues[ta.Union[*tv_types_set]]  # type: ignore
        tv_m = ctx.marshal_factory_context.make_marshaler(tv_ta)  # FIXME:
        tv_v = check.isinstance(tv_m.marshal(ctx, o._typed_values), ta.Sequence)  # noqa

        if self.v_m is None:
            orty = check.isinstance(ctx.mirror.reflect_type(rfl.get_orig_class(o)), rfl.Instance)
            check.state(orty.type.runtime_object in (Request, Response))
            v_rty, tv_rty = orty.args
            v_v = ctx.marshal_factory_context.make_marshaler(v_rty).marshal(ctx, o.v)  # FIXME
        else:
            v_v = self.v_m.marshal(ctx, o.v)

        md_fmd = self.rr_flds.md.metadata[msh.FieldOptions]
        md_mf = check.isinstance(check.not_none(md_fmd.marshal_via).o, msh.MarshalerFactory)
        md_m = md_mf.make_marshaler(ctx.marshal_factory_context, ctx.mirror.reflect_type(self.rr_flds.md.type))()  # FIXME  # noqa
        md_v = md_m.marshal(ctx, o._metadata)  # noqa

        return {
            'v': v_v,
            **({lang.must_remove_prefix(self.rr_flds.tv.name, '_'): tv_v} if tv_v else {}),
            **({'metadata': md_v} if md_v else {}),
        }


class _RequestResponseMarshalerFactory(msh.MarshalerFactory):
    def make_marshaler(self, ctx: msh.MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Marshaler] | None:
        if _get_rr_cls(rty) is None:
            return None

        def inner() -> msh.Marshaler:
            inst = check.isinstance(rty, rfl.Instance)
            v_rty, tv_rty = inst.args
            v_m: msh.Marshaler | None = None
            if not isinstance(v_rty, (rfl.TypeVarType, rfl.AnyType)):
                v_m = ctx.make_marshaler(v_rty)
            return _RequestResponseMarshaler(
                rty,
                _get_rr_flds(rty),
                v_m,
            )

        return inner


#


@dc.dataclass(frozen=True)
class _RequestResponseUnmarshaler(msh.Unmarshaler):
    rty: rfl.Type
    rr_flds: _RrFlds
    v_u: msh.Unmarshaler
    tv_u: msh.Unmarshaler
    md_u: msh.Unmarshaler

    def unmarshal(self, ctx: msh.UnmarshalContext, v: msh.Value) -> ta.Any:
        dct = dict(check.isinstance(v, ta.Mapping))

        v_v = dct.pop('v')
        v = self.v_u.unmarshal(ctx, v_v)

        if md_v := dct.pop('metadata', None):
            md = self.md_u.unmarshal(ctx, md_v)
        else:
            md = []

        tvs: ta.Any
        if dct:
            tv_vs = dct.pop(lang.must_remove_prefix(self.rr_flds.tv.name, '_'))
            tvs = self.tv_u.unmarshal(ctx, tv_vs)
        else:
            tvs = []

        check.empty(dct)

        cty = check.not_none(_get_rr_cls(self.rty))
        return cty(v, tvs, _metadata=md)


class _RequestResponseUnmarshalerFactory(msh.UnmarshalerFactory):
    def make_unmarshaler(self, ctx: msh.UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Unmarshaler] | None:  # noqa
        if _get_rr_cls(rty) is None:
            return None

        def inner() -> msh.Unmarshaler:
            inst = check.isinstance(rty, rfl.Instance)
            v_rty, tv_rty = inst.args

            rr_flds = _get_rr_flds(rty)

            tv_union = check.isinstance(tv_rty, rfl.UnionType)
            tv_ta = tv.TypedValues[rfl.to_runtime_annotation(tv_union)]  # type: ignore
            tv_u = ctx.make_unmarshaler(tv_ta)

            v_u = ctx.make_unmarshaler(v_rty)

            md_fmd = rr_flds.md.metadata[msh.FieldOptions]
            md_uf = check.isinstance(check.not_none(md_fmd.unmarshal_via).o, msh.UnmarshalerFactory)
            md_u = md_uf.make_unmarshaler(ctx, ctx.mirror.reflect_type(rr_flds.md.type))()  # FIXME

            return _RequestResponseUnmarshaler(
                rty,
                _get_rr_flds(rty),
                v_u,
                tv_u,
                md_u,
            )

        return inner


##


class _MetadataMarshalerUnmarshalerFactory(msh.MarshalerFactory, msh.UnmarshalerFactory, lang.Abstract):
    _md_cls: ta.ClassVar[type]
    _mdu_obj: ta.ClassVar[ta.Any]

    @classmethod
    def _mdu_rty_key(cls) -> ta.Any:
        try:
            return cls.__dict__['_mdu_rty_key_cache']
        except KeyError:
            pass
        key = rfl.reflect_type(cls._mdu_obj).type_key()
        setattr(cls, '_mdu_rty_key_cache', key)
        return key

    def _is_mdu_rty(self, rty: rfl.Type) -> bool:
        return rty.type_key() == self._mdu_rty_key()

    def _matches(self, rty: rfl.Type) -> bool:
        return rfl.get_runtime_type_or_none(rty) is self._md_cls or self._is_mdu_rty(rty)

    def _build_impls(self, rty: rfl.Type) -> list[msh.Impl]:
        impls: list[msh.Impl] = []

        rt = get_global_registry().get_type(self._md_cls)
        for rte in rt.entries.values():
            impls.append(msh.Impl(
                mdi_cls := rte.resolve(),
                msh.translate_name(
                    lang.must_remove_suffix(mdi_cls.__name__, self._md_cls.__name__),
                    msh.Naming.SNAKE,
                ),
            ))

        if self._is_mdu_rty(rty):
            impls.extend(msh.polymorphism_from_subclasses(
                CommonMetadata,
                naming=msh.Naming.SNAKE,
            ).impls)

        return impls

    def make_marshaler(self, ctx: msh.MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Marshaler] | None:
        if not self._matches(rty):
            return None

        return lambda: msh.make_polymorphism_marshaler(
            msh.Impls(self._build_impls(rty)),
            msh.WrapperTypeTagging(),
            ctx,
        )

    def make_unmarshaler(self, ctx: msh.UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Unmarshaler] | None:  # noqa
        if not self._matches(rty):
            return None

        return lambda: msh.make_polymorphism_unmarshaler(
            msh.Impls(self._build_impls(rty)),
            msh.WrapperTypeTagging(),
            ctx,
        )


class _RequestMetadataMarshalerUnmarshalerFactory(_MetadataMarshalerUnmarshalerFactory):
    _md_cls = RequestMetadata
    _mdu_obj = RequestMetadatas


class _ResponseMetadataMarshalerUnmarshalerFactory(_MetadataMarshalerUnmarshalerFactory):
    _md_cls = ResponseMetadata
    _mdu_obj = ResponseMetadatas


##


@msh.register_global_lazy_init
def _install_standard_marshaling(cfgs: msh.ConfigRegistry) -> None:
    msh.install_standard_factories(
        cfgs,

        _RequestResponseMarshalerFactory(),
        _RequestResponseUnmarshalerFactory(),

        _RequestMetadataMarshalerUnmarshalerFactory(),
        _ResponseMetadataMarshalerUnmarshalerFactory(),
    )
