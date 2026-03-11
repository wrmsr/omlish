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


@dc.dataclass(frozen=True)
class FacadeText(lang.Abstract, lang.Sealed):
    @classmethod
    def of(cls, obj: CanFacadeText) -> 'FacadeText':
        check.is_(cls, FacadeText, '`FacadeText.of()` must not be accessed through subclasses.')

        if isinstance(obj, FacadeText):
            return obj

        elif isinstance(obj, str):
            return StrFacadeText(obj)

        elif isinstance(obj, ta.Sequence):
            return ConcatFacadeText(tuple(cls.of(e) for e in obj))

        else:
            raise TypeError(obj)

    @classmethod
    def str_of(cls, obj: CanFacadeText) -> str:
        check.is_(cls, FacadeText, '`FacadeText.str_of()` must not be accessed through subclasses.')

        if isinstance(obj, str):
            return obj

        else:
            return str(cls.of(obj))

    #

    def style(
            self,
            *,
            color: FacadeTextColor | None = None,

            bold: bool = False,
            italic: bool = False,
    ) -> 'FacadeText':
        return StyleFacadeText(
            self,

            color=color,

            bold=bold,
            italic=italic,
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


@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True)
class StrFacadeText(FacadeText, lang.Final):
    s: str

    #

    def write_str_to(self, fn: ta.Callable[[str], ta.Any]) -> None:
        fn(self.s)


@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True)
class ConcatFacadeText(FacadeText, lang.Final):
    l: ta.Sequence[FacadeText]

    #

    def write_str_to(self, fn: ta.Callable[[str], ta.Any]) -> None:
        for t in self.l:
            t.write_str_to(fn)


@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True)
class StyleFacadeText(FacadeText, lang.Final):
    t: FacadeText

    _: dc.KW_ONLY

    color: FacadeTextColor | None = None

    bold: bool = False
    italic: bool = False

    #

    def write_str_to(self, fn: ta.Callable[[str], ta.Any]) -> None:
        self.t.write_str_to(fn)
