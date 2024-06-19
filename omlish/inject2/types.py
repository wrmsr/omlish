import abc
import typing as ta

from .. import dataclasses as dc
from .. import lang


T = ta.TypeVar('T')


##


Cls = type | ta.NewType


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class Key(lang.Final, ta.Generic[T]):
    cls: type[T] | ta.NewType
    tag: ta.Any = dc.field(default=None, kw_only=True)
    multi: bool = dc.field(default=False, kw_only=True)


##


class Provider(lang.Abstract):
    @abc.abstractmethod
    def provided_cls(self) -> Cls | None:
        raise NotImplementedError


##


class Element(lang.Abstract):
    pass


@dc.dataclass(frozen=True, eq=False)
class Elements(lang.Final):
    es: ta.Sequence[Element] | None = None
    cs: ta.Sequence['Elements'] | None = None

    def __iter__(self) -> ta.Generator[Element, None, None]:
        if self.es:
            yield from self.es
        if self.cs:
            for c in self.cs:
                yield from c


##


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class Binding(Element, lang.Final):
    key: Key
    provider: Provider


##


class Kwarg(ta.NamedTuple):
    name: str
    key: Key
    has_default: bool


class KwargsTarget(ta.NamedTuple):
    obj: ta.Any
    kwargs: ta.Sequence[Kwarg]


##


class Injector(lang.Abstract):
    @abc.abstractmethod
    def try_provide(self, key: ta.Any) -> lang.Maybe[ta.Any]:
        raise NotImplementedError

    @abc.abstractmethod
    def provide(self, key: ta.Any) -> ta.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def provide_kwargs(self, kt: KwargsTarget) -> ta.Mapping[str, ta.Any]:
        raise NotImplementedError

    @abc.abstractmethod
    def inject(self, obj: ta.Any) -> ta.Any:
        raise NotImplementedError

    def __getitem__(
            self,
            target: ta.Union[Key[T], type[T]],
    ) -> T:
        return self.provide(target)
