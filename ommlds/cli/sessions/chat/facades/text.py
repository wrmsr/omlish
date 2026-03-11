import abc
import io
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang


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
class FacadeTextStyle(lang.Final):
    DEFAULT: ta.ClassVar['FacadeTextStyle']

    color: FacadeTextColor | None = None

    bold: bool | None = None
    italic: bool | None = None


FacadeTextStyle.DEFAULT = FacadeTextStyle()


##


@dc.dataclass(frozen=True)
class FacadeText(lang.Abstract, lang.Sealed):
    _BLANK: ta.ClassVar['StrFacadeText']

    @classmethod
    def blank(cls) -> 'StrFacadeText':
        check.is_(cls, FacadeText, 'Method must not be accessed through subclasses.')

        return cls._BLANK

    @classmethod
    def of(cls, obj: CanFacadeText) -> 'FacadeText':
        check.is_(cls, FacadeText, 'Method must not be accessed through subclasses.')

        if isinstance(obj, FacadeText):
            return obj

        elif isinstance(obj, str):
            if not obj:
                return cls._BLANK

            return StrFacadeText(obj)

        elif isinstance(obj, ta.Sequence):
            return ConcatFacadeText(tuple(cls.of(e) for e in obj))

        else:
            raise TypeError(obj)

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
    ) -> 'FacadeText':
        delim = FacadeText.of(self)

        if not delim:
            return FacadeText._BLANK

        return ConcatFacadeText(tuple(lang.interleave(map(FacadeText.of, items), delim)))

    def style(
            self: CanFacadeText,
            *,
            color: FacadeTextColor | None = None,

            bold: bool | None = None,
            italic: bool | None = None,
    ) -> 'FacadeText':
        x = FacadeText.of(self)

        if (
                color is None and
                bold is not None and
                italic is not None
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
class StrFacadeText(FacadeText, lang.Final):
    s: str

    #

    def write_str_to(self, fn: ta.Callable[[str], ta.Any]) -> None:
        fn(self.s)


FacadeText._BLANK = StrFacadeText('')  # noqa


##


@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True)
class ConcatFacadeText(FacadeText, lang.Final):
    l: ta.Sequence[FacadeText]

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

    def write_str_to(self, fn: ta.Callable[[str], ta.Any]) -> None:
        self.c.write_str_to(fn)
