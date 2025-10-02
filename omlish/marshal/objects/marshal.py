import collections.abc
import typing as ta

from ... import check
from ... import dataclasses as dc
from ... import reflect as rfl
from ..base.contexts import MarshalContext
from ..base.contexts import MarshalFactoryContext
from ..base.types import Marshaler
from ..base.types import MarshalerFactory
from ..base.values import Value
from .metadata import FieldInfo
from .metadata import FieldInfos
from .metadata import ObjectSpecials


##


@dc.dataclass(frozen=True)
class ObjectMarshaler(Marshaler):
    fields: ta.Sequence[tuple[FieldInfo, Marshaler]]

    _: dc.KW_ONLY

    specials: ObjectSpecials = ObjectSpecials()

    attr_getter: ta.Callable[[ta.Any, str], ta.Any] | None = None

    @classmethod
    def make(
            cls,
            ctx: MarshalFactoryContext,
            fis: FieldInfos,
            **kwargs: ta.Any,
    ) -> Marshaler:
        fields = [
            (fi, ctx.make_marshaler(fi.type))
            for fi in fis
        ]

        return cls(
            fields,
            **kwargs,
        )

    #

    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        if (attr_getter := self.attr_getter) is None:
            attr_getter = getattr

        ret: dict[str, ta.Any] = {}
        for fi, m in self.fields:
            v = attr_getter(o, fi.name)

            if fi.options.omit_if is not None and fi.options.omit_if(v):
                continue

            if fi.name in self.specials.set:
                continue

            mn = fi.marshal_name
            if mn is None:
                continue

            mv = m.marshal(ctx, v)

            if fi.options.embed:
                for ek, ev in check.isinstance(mv, collections.abc.Mapping).items():
                    ret[mn + check.non_empty_str(ek)] = ev

            else:
                ret[mn] = mv

        if self.specials.unknown is not None:
            if (ukf := attr_getter(o, self.specials.unknown)):
                if (dks := set(ret) & set(ukf)):
                    raise KeyError(f'Unknown field keys duplicate fields: {dks!r}')

            ret.update(ukf)  # FIXME: marshal?

        return ret


##


@dc.dataclass(frozen=True)
class SimpleObjectMarshalerFactory(MarshalerFactory):
    dct: ta.Mapping[type, ta.Sequence[FieldInfo]]

    _: dc.KW_ONLY

    specials: ObjectSpecials = ObjectSpecials()

    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if not (isinstance(rty, type) and rty in self.dct):
            return None

        def inner() -> Marshaler:
            ty = check.isinstance(rty, type)

            fis = FieldInfos(self.dct[ty])

            return ObjectMarshaler.make(
                ctx,
                fis,
                specials=self.specials,
            )

        return inner
