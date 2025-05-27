import collections.abc
import inspect
import types
import typing as ta

from omdev.py import docstrings
from omlish import check
from omlish import collections as col
from omlish import reflect as rfl

from .types import OBJECT_PRIMITIVE_TYPE
from .types import PRIMITIVE_TYPE_MAP
from .types import Enum
from .types import Function
from .types import Mapping
from .types import Nullable
from .types import Param
from .types import Sequence
from .types import Tuple
from .types import Type
from .types import Union


##


class Reflector:
    def make_union_type(self, *args: rfl.Type) -> Type:
        check.unique(args)

        if types.NoneType in args:
            is_nullable = True
            args = tuple(a for a in args if a is not types.NoneType)
        else:
            is_nullable = False

        ret: Type
        if not args:
            raise RuntimeError

        elif len(args) == 1:
            ret = self.make_type(check.single(args))

        else:
            ret = Union(tuple(
                self.make_type(a_rty)
                for a_rty in args
            ))

        if is_nullable:
            ret = Nullable(ret)

        return ret

    SEQUENCE_TYPES: ta.Container[type] = frozenset([
        collections.abc.Sequence,
        list,
    ])

    MAPPING_TYPES: ta.Container[type] = frozenset([
        collections.abc.Mapping,
        dict,
    ])

    def make_type(self, rty: rfl.Type) -> Type:
        if isinstance(rty, type):
            return PRIMITIVE_TYPE_MAP.get(rty, OBJECT_PRIMITIVE_TYPE)

        if isinstance(rty, rfl.Union):
            return self.make_union_type(*rty.args)

        if isinstance(rty, rfl.Generic):
            g_cls = rty.cls

            if g_cls in self.SEQUENCE_TYPES:
                a_rty = check.single(rty.args)
                return Sequence(self.make_type(a_rty))

            if g_cls in self.MAPPING_TYPES:
                k_rty, v_rty = rty.args
                return Mapping(
                    self.make_type(k_rty),
                    self.make_type(v_rty),
                )

            if g_cls is tuple:
                return Tuple(tuple(
                    self.make_type(a_rty)
                    for a_rty in rty.args
                ))

        if isinstance(rty, rfl.Literal):
            return Enum(
                self.make_union_type(*col.unique(
                    rfl.type_(type(a))
                    for a in rty.args
                )),
                rty.args,
            )

        raise TypeError(rty)

    def make_function(self, fn: ta.Callable) -> Function:
        ds: docstrings.Docstring | None = None
        if (doc := inspect.getdoc(fn)) is not None:
            ds = docstrings.parse(doc)

        ds_p_dct = {
            ds_p.arg_name: ds_p
            for ds_p in (ds.params if ds is not None else [])
        }

        th = ta.get_type_hints(fn)
        sig = inspect.signature(fn)

        params: dict[str, Param] = {}
        for sig_p in sig.parameters.values():
            ds_p = ds_p_dct.get(sig_p.name)

            params[sig_p.name] = Param(
                sig_p.name,

                description=ds_p.description if ds_p is not None else None,

                type=self.make_type(rfl.type_(th[sig_p.name])) if sig_p.name in th else None,

                required=sig_p.default is inspect.Parameter.empty,
            )

        return Function(
            fn.__name__,

            description=ds.description if ds is not None else None,

            params=tuple(params.values()) if params else None,

            returns_description=ds.returns.description if ds is not None and ds.returns is not None else None,
            returns_type=self.make_type(rfl.type_(th['return'])) if 'return' in th else None,
        )
