"""
TODO:
 - check validity
 - signature vs getfullargspec - diff unwrapping + 'self' handling
"""
import dataclasses as dc
import enum
import inspect
import typing as ta

from ..lite.maybes import Maybe
from .classes.abstract import Abstract
from .classes.restrict import Final
from .classes.restrict import Sealed


T = ta.TypeVar('T')


CanParamSpec: ta.TypeAlias = ta.Union[
    'ParamSpec',
    inspect.Signature,
    ta.Callable,
]


##


@dc.dataclass(frozen=True, unsafe_hash=True)
class Param(Sealed, Abstract):
    name: str

    annotation: Maybe = Maybe.empty()

    prefix: ta.ClassVar[str] = ''

    @property
    def name_with_prefix(self) -> str:
        return f'{self.prefix}{self.name}'


#


@dc.dataclass(frozen=True, unsafe_hash=True)
class VarParam(Param, Abstract):
    pass


@dc.dataclass(frozen=True, unsafe_hash=True)
class ArgsParam(VarParam, Final):
    prefix: ta.ClassVar[str] = '*'


@dc.dataclass(frozen=True, unsafe_hash=True)
class KwargsParam(VarParam, Final):
    prefix: ta.ClassVar[str] = '**'


#


@dc.dataclass(frozen=True, unsafe_hash=True)
class ValParam(Param):
    default: Maybe = Maybe.empty()


@dc.dataclass(frozen=True, unsafe_hash=True)
class PosOnlyParam(ValParam, Final):
    pass


@dc.dataclass(frozen=True, unsafe_hash=True)
class KwOnlyParam(ValParam, Final):
    pass


#


class ParamSeparator(enum.Enum):
    POS_ONLY = '/'
    KW_ONLY = '*'


##


def _inspect_empty_to_maybe(o: T) -> Maybe[T]:
    if o is inspect.Parameter.empty:
        return Maybe.empty()
    else:
        return Maybe.just(o)


class ParamSpec(ta.Sequence[Param], Final):
    def __init__(self, *ps: Param) -> None:
        super().__init__()

        self._ps = ps

        self._hash: int | None = None

        self._has_annotations: bool | None = None
        self._has_defaults: bool | None = None

        self._with_seps: tuple[Param | ParamSeparator, ...] | None = None

    #

    @classmethod
    def of(cls, obj: CanParamSpec) -> 'ParamSpec':
        if isinstance(obj, ParamSpec):
            return obj
        elif isinstance(obj, inspect.Signature):
            return cls.of_signature(obj)
        else:
            return cls.inspect(obj)

    @classmethod
    def of_signature(
            cls,
            sig: inspect.Signature,
            *,
            offset: int = 0,
            strip_annotations: bool = False,
            strip_defaults: bool = False,
    ) -> 'ParamSpec':
        ps: list[Param] = []

        ip: inspect.Parameter
        for i, ip in enumerate(sig.parameters.values()):
            if i < offset:
                continue

            ann = _inspect_empty_to_maybe(ip.annotation) if not strip_annotations else Maybe.empty()
            dfl = _inspect_empty_to_maybe(ip.default) if not strip_defaults else Maybe.empty()

            if ip.kind == inspect.Parameter.POSITIONAL_ONLY:
                ps.append(PosOnlyParam(ip.name, ann, dfl))

            elif ip.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
                ps.append(ValParam(ip.name, ann, dfl))

            elif ip.kind == inspect.Parameter.VAR_POSITIONAL:
                ps.append(ArgsParam(ip.name, ann))

            elif ip.kind == inspect.Parameter.KEYWORD_ONLY:
                ps.append(KwOnlyParam(ip.name, ann, dfl))

            elif ip.kind == inspect.Parameter.VAR_KEYWORD:
                ps.append(KwargsParam(ip.name, ann))

            else:
                raise ValueError(ip.kind)

        return cls(*ps)

    @classmethod
    def inspect(
            cls,
            obj: ta.Any,
            **kwargs: ta.Any,
    ) -> 'ParamSpec':
        return cls.of_signature(
            inspect.signature(obj),
            **kwargs,
        )

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
    def has_annotations(self) -> bool:
        if (ha := self._has_annotations) is not None:
            return ha
        self._has_annotations = ha = any(
            isinstance(p, (VarParam, ValParam)) and p.annotation.present
            for p in self._ps
        )
        return ha

    @property
    def has_defaults(self) -> bool:
        if (hd := self._has_defaults) is not None:
            return hd
        self._has_defaults = hd = any(
            isinstance(p, ValParam) and p.default.present
            for p in self._ps
        )
        return hd

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


##


def param_render(
        p: Param | ParamSeparator,
        *,
        render_annotation: ta.Callable[[ta.Any], str] | None = None,
        render_default: ta.Callable[[ta.Any], str] | None = None,
) -> str:
    if isinstance(p, Param):
        ann_s: str | None = None
        if p.annotation.present:
            if render_annotation is None:
                raise ValueError(f'Param {p.name} has an annotation but no annotation renderer provided')
            ann_s = render_annotation(p.annotation.must())

        dfl_s: str | None = None
        if isinstance(p, ValParam) and p.default.present:
            if render_default is None:
                raise ValueError(f'Param {p.name} has a default but no default renderer provided')
            dfl_s = render_default(p.default.must())

        if ann_s is not None:
            if dfl_s is not None:
                return f'{p.name_with_prefix}: {ann_s} = {dfl_s}'
            else:
                return f'{p.name_with_prefix}: {ann_s}'
        elif dfl_s is not None:
            return f'{p.name_with_prefix}={dfl_s}'
        else:
            return p.name_with_prefix

    elif isinstance(p, ParamSeparator):
        return p.value

    else:
        raise TypeError(p)
