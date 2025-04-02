import collections.abc
import typing as ta

from ... import check
from ... import dataclasses as dc
from ... import reflect as rfl
from ..base import SimpleUnmarshalerFactory
from ..base import UnmarshalContext
from ..base import Unmarshaler
from ..values import Value
from .metadata import FieldInfo
from .metadata import FieldInfos
from .metadata import ObjectSpecials


##


@dc.dataclass(frozen=True)
class ObjectUnmarshaler(Unmarshaler):
    factory: ta.Callable
    fields_by_unmarshal_name: ta.Mapping[str, tuple[FieldInfo, Unmarshaler]]

    _: dc.KW_ONLY

    specials: ObjectSpecials = ObjectSpecials()

    defaults: ta.Mapping[str, ta.Any] | None = None

    embeds: ta.Mapping[str, type] | None = None
    embeds_by_unmarshal_name: ta.Mapping[str, tuple[str, str]] | None = None

    ignore_unknown: bool = False

    @classmethod
    def make(
            cls,
            ctx: UnmarshalContext,
            factory: ta.Callable,
            fis: FieldInfos,
            **kwargs: ta.Any,
    ) -> Unmarshaler:
        fields_by_unmarshal_name = {
            n: (fi, ctx.make(fi.type))
            for fi in fis
            for n in fi.unmarshal_names
        }

        defaults = {
            fi.name: fi.options.default.must()
            for fi in fis
            if fi.options.default.present
        }

        return cls(
            factory,
            fields_by_unmarshal_name,
            defaults=defaults,
            **kwargs,
        )

    #

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        ma = check.isinstance(v, collections.abc.Mapping)

        u: ta.Any
        kw: dict[str, ta.Any] = {}
        ukf: dict[str, ta.Any] | None = None

        ekws: dict[str, dict[str, ta.Any]] = {en: {} for en in self.embeds or ()}

        if self.specials.source is not None:
            kw[self.specials.source] = v

        if self.specials.unknown is not None:
            kw[self.specials.unknown] = ukf = {}

        for k, mv in ma.items():
            ks = check.isinstance(k, str)

            try:
                fi, u = self.fields_by_unmarshal_name[ks]

            except KeyError:
                if ukf is not None:
                    ukf[ks] = mv  # FIXME: unmarshal?
                    continue

                if self.ignore_unknown:
                    continue

                raise

            if self.embeds_by_unmarshal_name and (en := self.embeds_by_unmarshal_name.get(ks)):
                tkw, tk = ekws[en[0]], en[1]
            else:
                tkw, tk = kw, fi.name

            if tk in tkw:
                raise KeyError(f'Duplicate keys for field {tk!r}: {ks!r}')

            tkw[tk] = u.unmarshal(ctx, mv)

        for em, ecls in self.embeds.items() if self.embeds else ():
            ekw = ekws[em]
            ev = ecls(**ekw)
            kw[em] = ev

        if self.defaults:
            for dk, dv in self.defaults.items():
                kw.setdefault(dk, dv)

        return self.factory(**kw)


##


@dc.dataclass(frozen=True)
class SimpleObjectUnmarshalerFactory(SimpleUnmarshalerFactory):
    dct: ta.Mapping[type, ta.Sequence[FieldInfo]]

    _: dc.KW_ONLY

    specials: ObjectSpecials = ObjectSpecials()

    def guard(self, ctx: UnmarshalContext, rty: rfl.Type) -> bool:
        return isinstance(rty, type) and rty in self.dct

    def fn(self, ctx: UnmarshalContext, rty: rfl.Type) -> Unmarshaler:
        ty = check.isinstance(rty, type)

        fis = FieldInfos(self.dct[ty])

        return ObjectUnmarshaler.make(
            ctx,
            ty,
            fis,
            specials=self.specials,
        )
