"""
TODO:
 - check validity
"""
import dataclasses as dc
import enum
import inspect
import typing as ta

from .classes.abstract import Abstract
from .classes.restrict import Final
from .classes.restrict import Sealed
from .maybes import Maybe
from .maybes import empty
from .maybes import just


T = ta.TypeVar('T')


##


@dc.dataclass(frozen=True)
class Param(Sealed, Abstract):
    name: str

    prefix: ta.ClassVar[str] = ''

    @property
    def name_with_prefix(self) -> str:
        return f'{self.name}{self.prefix}'


class VariadicParam(Param, Abstract):
    pass


class ArgsParam(VariadicParam, Final):
    prefix: ta.ClassVar[str] = '*'


class KwargsParam(VariadicParam, Final):
    prefix: ta.ClassVar[str] = '**'


@dc.dataclass(frozen=True)
class ValueParam(Param):
    default: Maybe = empty()
    annotation: Maybe = empty()


class PosOnlyParam(ValueParam, Final):
    pass


class KwOnlyParam(ValueParam, Final):
    pass


class ParamSeparator(enum.Enum):
    POS_ONLY = '/'
    KW_ONLY = '*'


##


def _inspect_empty_to_maybe(o: T) -> Maybe[T]:
    if o is inspect.Parameter.empty:
        return empty()
    else:
        return just(o)


class ParamSpec(ta.Sequence[Param], Final):
    def __init__(self, *ps: Param) -> None:
        super().__init__()

        self._ps = ps
        self._hash: int | None = None
        self._with_seps: tuple[Param | ParamSeparator, ...] | None = None

    #

    @classmethod
    def of_signature(cls, sig: inspect.Signature) -> 'ParamSpec':
        ps: list[Param] = []

        ip: inspect.Parameter
        for ip in sig.parameters.values():
            dfl = _inspect_empty_to_maybe(ip.default)
            ann = _inspect_empty_to_maybe(ip.annotation)

            if ip.kind == inspect.Parameter.POSITIONAL_ONLY:
                ps.append(PosOnlyParam(ip.name, dfl, ann))

            elif ip.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
                ps.append(ValueParam(ip.name, dfl, ann))

            elif ip.kind == inspect.Parameter.VAR_POSITIONAL:
                ps.append(ArgsParam(ip.name))

            elif ip.kind == inspect.Parameter.VAR_KEYWORD:
                ps.append(KwargsParam(ip.name))

            elif ip.kind == inspect.Parameter.KEYWORD_ONLY:
                ps.append(KwOnlyParam(ip.name, dfl, ann))

            else:
                raise ValueError(ip.kind)

        return cls(*ps)

    #

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({", ".join(map(repr, self._ps))})'

    def __hash__(self) -> int:
        if (h := self._hash) is not None:
            return h
        self._hash = h = hash(self._ps)
        return h

    def __eq__(self, other: object) -> bool:
        if type(other) is not ParamSpec:
            raise TypeError(other)
        return self._ps == other._ps  # noqa

    #

    @property
    def with_seps(self) -> ta.Sequence[Param | ParamSeparator]:
        if (ws := self._with_seps) is not None:
            return ws

        l: list[Param | ParamSeparator] = []
        needs_pos_only = False
        seen_kw_only = False
        for p in self._ps:
            if isinstance(p, PosOnlyParam):
                needs_pos_only = True
            elif needs_pos_only:
                l.append(ParamSeparator.POS_ONLY)
                needs_pos_only = False

            if isinstance(p, KwOnlyParam) and not seen_kw_only:
                l.append(ParamSeparator.KW_ONLY)
                seen_kw_only = True
            elif isinstance(p, KwargsParam):
                seen_kw_only = True

            l.append(p)

        self._with_seps = ws = tuple(l)
        return ws

    #

    @ta.overload
    def __getitem__(self, index: int) -> Param: ...

    @ta.overload
    def __getitem__(self, index: slice) -> ta.Sequence[Param]: ...

    def __getitem__(self, index):
        return self._ps[index]

    def __len__(self) -> int:
        return len(self._ps)
