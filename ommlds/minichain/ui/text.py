import abc
import io
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh


CanUiText: ta.TypeAlias = ta.Union[
    'UiText',
    str,
    ta.Sequence['CanUiText'],
]

UiTextColor: ta.TypeAlias = ta.Literal[
    'red',
    'green',
    'yellow',
    'blue',
]


##


@dc.dataclass(frozen=True, kw_only=True)
@dc.extra_class_params(cache_hash=True, default_repr_fn=lang.opt_repr)
@msh.update_object_options(field_defaults=msh.FieldOptions(omit_if=lang.is_none))
class UiTextStyle(lang.Final):
    DEFAULT: ta.ClassVar[UiTextStyle]

    color: UiTextColor | None = None

    bold: bool | None = None
    italic: bool | None = None


UiTextStyle.DEFAULT = UiTextStyle()


##


@dc.dataclass(frozen=True)
class UiText(lang.Abstract, lang.Sealed):
    _BLANK: ta.ClassVar[StrUiText]

    @classmethod
    def blank(cls) -> StrUiText:
        check.is_(cls, UiText, 'Method must not be accessed through subclasses.')

        return cls._BLANK

    @classmethod
    def of(cls, *objs: CanUiText) -> UiText:
        check.is_(cls, UiText, 'Method must not be accessed through subclasses.')

        if not objs:
            return cls._BLANK

        if len(objs) == 1 and isinstance(o0 := objs[0], UiText):
            return o0

        out: list[UiText] = []
        pending_strs: list[str] = []

        def flush_strs() -> None:
            if pending_strs:
                out.append(StrUiText(''.join(pending_strs)))
                pending_strs.clear()

        def emit_node(t: UiText) -> None:
            if isinstance(t, StrUiText):
                if t.s:
                    pending_strs.append(t.s)

            elif isinstance(t, ConcatUiText):
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
                # For now, preserve StyleUiText exactly as a boundary node.
                out.append(t)

        stack: list[CanUiText] = list(reversed(objs))

        while stack:
            o = stack.pop()

            if isinstance(o, str):
                if o:
                    pending_strs.append(o)

            elif isinstance(o, StrUiText):
                if o.s:
                    pending_strs.append(o.s)

            elif isinstance(o, ConcatUiText):
                stack.extend(reversed(o.l))

            elif isinstance(o, UiText):
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

        return ConcatUiText(tuple(out))

    @classmethod
    def str_of(cls, obj: CanUiText) -> str:
        check.is_(cls, UiText, 'Method must not be accessed through subclasses.')

        if isinstance(obj, str):
            return obj

        else:
            return str(cls.of(obj))

    #

    def join(
            self: CanUiText,
            items: ta.Iterable[CanUiText],
    ) -> UiText:
        delim = UiText.of(self)

        if not delim:
            return UiText.of(*items)

        return UiText.of(*lang.interleave(delim, map(UiText.of, items)))

    def style(
            self: CanUiText,
            *,
            color: UiTextColor | None = None,

            bold: bool | None = None,
            italic: bool | None = None,
    ) -> UiText:
        x = UiText.of(self)

        if not x:
            return UiText._BLANK

        if (
                color is None and
                bold is None and
                italic is None
        ):
            return x

        return StyleUiText(
            x,
            UiTextStyle(
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
class StrUiText(UiText, lang.Final):
    s: str

    def __bool__(self) -> bool:
        return bool(self.s)

    #

    def write_str_to(self, fn: ta.Callable[[str], ta.Any]) -> None:
        fn(self.s)


UiText._BLANK = StrUiText('')  # noqa


##


@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True)
@msh.update_object_options(unwrap_if_single_field=True)
class ConcatUiText(UiText, lang.Final):
    l: ta.Sequence[UiText]

    def __post_init__(self) -> None:
        last_was_str = False
        for c in check.not_empty(self.l):
            check.arg(bool(c))
            check.not_isinstance(c, ConcatUiText)

            is_str = isinstance(c, StrUiText)
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
class StyleUiText(UiText, lang.Final):
    c: UiText
    y: UiTextStyle = UiTextStyle.DEFAULT

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
        msh.polymorphism_from_subclasses(UiText, naming=msh.Naming.SNAKE, strip_suffix=True),
    ))
