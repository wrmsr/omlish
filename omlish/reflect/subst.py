import dataclasses as dc
import types
import typing as ta

from .. import c3
from .. import lang
from .ops import get_concrete_type
from .ops import to_annotation
from .types import Any
from .types import Generic
from .types import Literal
from .types import NewType
from .types import Type
from .types import Union
from .types import get_params
from .types import type_


if ta.TYPE_CHECKING:
    from ..collections import cache
else:
    cache = lang.proxy_import('.collections.cache', __package__)


def get_type_var_replacements(ty: Type) -> ta.Mapping[ta.TypeVar, Type]:
    if isinstance(ty, Generic):
        return dict(zip(ty.params, ty.args))

    return {}


def replace_type_vars(
        ty: Type,
        rpl: ta.Mapping[ta.TypeVar, Type],
        *,
        update_aliases: bool = False,
) -> Type:
    def rec(cur):
        if isinstance(cur, (type, NewType, Any, Literal)):
            return cur

        if isinstance(cur, Generic):
            args = tuple(rec(a) for a in cur.args)
            if update_aliases:
                obj = cur.obj
                if (ops := get_params(obj)):
                    nargs = [to_annotation(rpl[p]) for p in ops]
                    if ta.get_origin(obj) is ta.Generic:
                        # FIXME: None? filter_typing_generic in get_generic_bases?
                        pass
                    else:
                        obj = cur.obj[*nargs]
            else:
                obj = None
            return dc.replace(cur, args=args, obj=obj)

        if isinstance(cur, Union):
            return Union(frozenset(rec(e) for e in cur.args))

        if isinstance(cur, ta.TypeVar):
            return rpl[cur]

        raise TypeError(cur)

    return rec(ty)


class GenericSubstitution:
    def __init__(
            self,
            *,
            update_aliases: bool = False,
            cache_size: int = 0,  # FIXME: ta.Generic isn't weakrefable..
    ) -> None:
        super().__init__()

        self._update_aliases = update_aliases

        if cache_size > 0:
            self.get_generic_bases = cache.cache(weak_keys=True, max_size=cache_size)(self.get_generic_bases)  # type: ignore  # noqa
            self.generic_mro = cache.cache(weak_keys=True, max_size=cache_size)(self.generic_mro)  # type: ignore

    def get_generic_bases(self, ty: Type) -> tuple[Type, ...]:
        if (cty := get_concrete_type(ty)) is not None:
            rpl = get_type_var_replacements(ty)
            ret: list[Type] = []
            for b in types.get_original_bases(cty):
                bty = type_(b)
                if isinstance(bty, Generic) and isinstance(b, type):
                    # FIXME: throws away relative types, but can't use original vars as they're class-contextual
                    bty = type_(b[*((ta.Any,) * len(bty.params))])  # type: ignore
                rty = replace_type_vars(bty, rpl, update_aliases=self._update_aliases)
                ret.append(rty)
            return tuple(ret)
        return ()

    def generic_mro(self, obj: ta.Any) -> list[Type]:
        mro = c3.mro(
            type_(obj),
            get_bases=lambda t: self.get_generic_bases(t),
            is_subclass=lambda l, r: issubclass(get_concrete_type(l), get_concrete_type(r)),  # type: ignore
        )
        return [ty for ty in mro if get_concrete_type(ty) is not ta.Generic]


DEFAULT_GENERIC_SUBSTITUTION = GenericSubstitution()

get_generic_bases = DEFAULT_GENERIC_SUBSTITUTION.get_generic_bases
generic_mro = DEFAULT_GENERIC_SUBSTITUTION.generic_mro

ALIAS_UPDATING_GENERIC_SUBSTITUTION = GenericSubstitution(update_aliases=True)
