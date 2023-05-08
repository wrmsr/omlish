import typing as ta

from .. import nodes as no
from ... import check
from ... import collections as col
from .macros import DEFAULT_MACROS
from .macros import DynamicMacro
from .macros import NamedMacro
from .types import Macro


def c(o: ta.Any) -> no.Node:
    return no.Const(o)


class Xlator:

    def __init__(self, macros: ta.Iterable[Macro]) -> None:
        super().__init__()

        self._macros = list(macros)

        dynamic_macros: ta.List[DynamicMacro] = []
        named_macro_lists: ta.Dict[str, ta.List[NamedMacro]] = {}
        default_macro: ta.Optional[DynamicMacro] = None
        for m in self._macros:
            if isinstance(m, DynamicMacro):
                if m.match is True:
                    default_macro = check.replacing_none(default_macro, m)
                else:
                    dynamic_macros.append(m)
            elif isinstance(m, NamedMacro):
                named_macro_lists.setdefault(m.name, []).append(m)
            else:
                raise TypeError(m)

        self._dynamic_macros: ta.Sequence[DynamicMacro] = dynamic_macros

        self._simple_named_macros: ta.Mapping[str, NamedMacro] = {
            n: check.single(ms)
            for n, ms in named_macro_lists.items()
            if len(ms) == 1
        }

        self._arity_overloaded_named_macros: ta.Mapping[str, ta.Mapping[int, NamedMacro]] = {
            n: col.unique_dict((check.isinstance(m.arity, int), m) for m in ms)
            for n, ms in named_macro_lists.items()
            if len(ms) > 1
        }

        self._default_macro = default_macro

    def __call__(self, obj: ta.Any) -> no.Node:
        if isinstance(obj, no.Node):
            return obj

        if isinstance(obj, (int, float)):
            return no.Const(obj)

        if isinstance(obj, str):
            if obj and obj[0] == '~':
                return no.Const(obj[1:])
            else:
                return no.GetVar(no.Ident(obj))

        if isinstance(obj, list):
            args = list(obj)

            dm = None
            for cdm in self._dynamic_macros:
                if cdm.match(args):
                    dm = check.replacing_none(dm, cdm)
            if dm is not None:
                return dm(self, args)

            if args and isinstance(args[0], str) and args[0]:
                try:
                    nm = self._simple_named_macros[args[0]]
                except KeyError:
                    pass
                else:
                    return nm(self, args[1:])

                try:
                    ams = self._arity_overloaded_named_macros[args[0]]
                except KeyError:
                    pass
                else:
                    am = ams[len(args) - 1]
                    return am(self, args[1:])

            if self._default_macro:
                return self._default_macro(self, args)
            else:
                raise ValueError(args)

        raise TypeError(obj)


DEFAULT_XLATOR = Xlator(DEFAULT_MACROS)


def xlat(obj: ta.Any) -> no.Node:
    return DEFAULT_XLATOR(obj)
