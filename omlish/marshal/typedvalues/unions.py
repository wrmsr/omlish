import typing as ta

from ... import check
from ... import reflect as rfl
from ... import typedvalues as tv
from ..api.contexts import BaseContext
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalFactoryContext
from ..api.naming import Naming
from ..api.naming import translate_name
from ..api.types import Marshaler
from ..api.types import Unmarshaler
from ..factories.method import MarshalerFactoryMethodClass
from ..factories.method import UnmarshalerFactoryMethodClass
from ..polymorphism.api import Impl
from ..polymorphism.api import Impls
from ..polymorphism.api import WrapperTypeTagging
from ..polymorphism.marshal import PolymorphismMarshaler
from ..polymorphism.marshal import make_polymorphism_marshaler
from ..polymorphism.unmarshal import PolymorphismUnmarshaler
from ..polymorphism.unmarshal import make_polymorphism_unmarshaler


##


def _is_typed_values_union(rty: rfl.Type) -> bool:
    return (
        isinstance(rty, rfl.Union) and
        all(
            (isinstance(a, type) and issubclass(a, tv.TypedValue)) or
            (isinstance(a, rfl.Generic) and issubclass(a.cls, tv.TypedValue))
            for a in rty.args
        )
    )


def _build_typed_value_union_poly(ctx: BaseContext, rty: rfl.Type) -> Impls:
    def gus(sty: type) -> list[type]:
        if isinstance(ctx, MarshalFactoryContext):
            m = ctx.make_marshaler(sty)  # noqa
            impls = check.isinstance(m, PolymorphismMarshaler).get_impls()
        elif isinstance(ctx, UnmarshalFactoryContext):
            u = ctx.make_unmarshaler(sty)  # noqa
            impls = check.isinstance(u, PolymorphismUnmarshaler).get_impls()
        else:
            raise TypeError(ctx)

        impls = check.not_none(impls)

        return [i.ty for i in impls]

    tv_cls_set = tv.reflect_typed_values_impls(
        rty,
        find_abstract_subclasses=True,
        get_unsealed_subclasses=gus,
    )

    return Impls([
        Impl(
            tv_cls,
            translate_name(tv_cls.__name__, Naming.SNAKE),
        )
        for tv_cls in tv_cls_set
    ])


class TypedValueUnionMarshalerFactory(MarshalerFactoryMethodClass):
    @MarshalerFactoryMethodClass.make_marshaler.register
    def _make_union(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if not _is_typed_values_union(rty):
            return None

        return lambda: make_polymorphism_marshaler(
            _build_typed_value_union_poly(ctx, rty),
            WrapperTypeTagging(),
            ctx,
        )


class TypedValueUnionUnmarshalerFactory(UnmarshalerFactoryMethodClass):
    @UnmarshalerFactoryMethodClass.make_unmarshaler.register
    def _make_union(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if not _is_typed_values_union(rty):
            return None

        return lambda: make_polymorphism_unmarshaler(
            _build_typed_value_union_poly(ctx, rty),
            WrapperTypeTagging(),
            ctx,
        )
