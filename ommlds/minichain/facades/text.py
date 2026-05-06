import abc
import io
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh


CanFacadeText: ta.TypeAlias = ta.Union[
    'FacadeText',
    str,
    ta.Sequence['CanFacadeText'],
]

FacadeTextColor: ta.TypeAlias = ta.Literal[
    'red',
    'green',
    'yellow',
    'blue',
]


##


@dc.dataclass(frozen=True, kw_only=True)
@dc.extra_class_params(cache_hash=True, default_repr_fn=lang.opt_repr)
@msh.update_object_options( field_defaults=msh.FieldOptions(omit_if=lang.is_none))
class FacadeTextStyle(lang.Final):
    DEFAULT: ta.ClassVar[FacadeTextStyle]

    color: FacadeTextColor | None = None

    bold: bool | None = None
    italic: bool | None = None


FacadeTextStyle.DEFAULT = FacadeTextStyle()


##


@dc.dataclass(frozen=True)
class FacadeText(lang.Abstract, lang.Sealed):
    _BLANK: ta.ClassVar[StrFacadeText]

    @classmethod
    def blank(cls) -> StrFacadeText:
        check.is_(cls, FacadeText, 'Method must not be accessed through subclasses.')

        return cls._BLANK

    @classmethod
    def of(cls, *objs: CanFacadeText) -> FacadeText:
        check.is_(cls, FacadeText, 'Method must not be accessed through subclasses.')

        if not objs:
            return cls._BLANK

        if len(objs) == 1 and isinstance(o0 := objs[0], FacadeText):
            return o0

        out: list[FacadeText] = []
        pending_strs: list[str] = []

        def flush_strs() -> None:
            if pending_strs:
                out.append(StrFacadeText(''.join(pending_strs)))
                pending_strs.clear()

        def emit_node(t: FacadeText) -> None:
            if isinstance(t, StrFacadeText):
                if t.s:
                    pending_strs.append(t.s)

            elif isinstance(t, ConcatFacadeText):
                # Should normally be handled by stack expansion before this point. Kept here so future
                # node-normalization hooks have one safe sink.
                for c in t.l:
                    emit_node(c)

            else:
                if not t:
                    return

                flush_strs()

                # Future style hook:
                #
                #   - Style(DEFAULT, x) -> x
                #   - Style(Style(x, a), b) -> Style(x, a.merge(b))
                #   - adjacent equal Style nodes maybe merge their children
                #
                # For now, preserve StyleFacadeText exactly as a boundary node.
                out.append(t)

        stack: list[CanFacadeText] = list(reversed(objs))

        while stack:
            o = stack.pop()

            if isinstance(o, str):
                if o:
                    pending_strs.append(o)

            elif isinstance(o, StrFacadeText):
                if o.s:
                    pending_strs.append(o.s)

            elif isinstance(o, ConcatFacadeText):
                stack.extend(reversed(o.l))

            elif isinstance(o, FacadeText):
                emit_node(o)

            elif isinstance(o, ta.Sequence):
                stack.extend(reversed(o))

            else:
                raise TypeError(o)

        flush_strs()

        if not out:
            return cls._BLANK

        if len(out) == 1:
            return out[0]

        return ConcatFacadeText(tuple(out))

    @classmethod
    def str_of(cls, obj: CanFacadeText) -> str:
        check.is_(cls, FacadeText, 'Method must not be accessed through subclasses.')

        if isinstance(obj, str):
            return obj

        else:
            return str(cls.of(obj))

    #

    def join(
            self: CanFacadeText,
            items: ta.Iterable[CanFacadeText],
    ) -> FacadeText:
        delim = FacadeText.of(self)

        if not delim:
            return FacadeText.of(*items)

        return FacadeText.of(*lang.interleave(delim, map(FacadeText.of, items)))

    def style(
            self: CanFacadeText,
            *,
            color: FacadeTextColor | None = None,

            bold: bool | None = None,
            italic: bool | None = None,
    ) -> FacadeText:
        x = FacadeText.of(self)

        if not x:
            return FacadeText._BLANK

        if (
                color is None and
                bold is None and
                italic is None
        ):
            return x

        return StyleFacadeText(
            x,
            FacadeTextStyle(
                color=color,
                bold=bold,
                italic=italic,
            ),
        )

    #

    @abc.abstractmethod
    def write_str_to(self, fn: ta.Callable[[str], ta.Any]) -> None:
        raise NotImplementedError

    @lang.cached_function
    def __str__(self) -> str:
        out = io.StringIO()
        self.write_str_to(out.write)
        return out.getvalue()


##


@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True, terse_repr=True)
@msh.update_object_options(unwrap_if_single_field=True)
class StrFacadeText(FacadeText, lang.Final):
    s: str

    def __bool__(self) -> bool:
        return bool(self.s)

    #

    def write_str_to(self, fn: ta.Callable[[str], ta.Any]) -> None:
        fn(self.s)


FacadeText._BLANK = StrFacadeText('')  # noqa


##


@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True)
@msh.update_object_options(unwrap_if_single_field=True)
class ConcatFacadeText(FacadeText, lang.Final):
    l: ta.Sequence[FacadeText]

    def __post_init__(self) -> None:
        last_was_str = False
        for c in check.not_empty(self.l):
            check.arg(bool(c))
            check.not_isinstance(c, ConcatFacadeText)

            is_str = isinstance(c, StrFacadeText)
            check.arg(not (last_was_str and is_str))
            last_was_str = is_str

    #

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({list(self.l)!r})'

    #

    def write_str_to(self, fn: ta.Callable[[str], ta.Any]) -> None:
        for t in self.l:
            t.write_str_to(fn)


##


@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True, terse_repr=True)
class StyleFacadeText(FacadeText, lang.Final):
    c: FacadeText
    y: FacadeTextStyle = FacadeTextStyle.DEFAULT

    #

    def __post_init__(self) -> None:
        check.state(bool(self.c))

    #

    def write_str_to(self, fn: ta.Callable[[str], ta.Any]) -> None:
        self.c.write_str_to(fn)


##


@msh.register_global_lazy_init
def _install_standard_marshaling(cfgs: msh.ConfigRegistry) -> None:
    msh.install_standard_factories_to(cfgs, *msh.standard_polymorphism_factories(
        msh.polymorphism_from_subclasses(FacadeText, naming=msh.Naming.SNAKE, strip_suffix=True),
    ))
