import abc
import typing as ta
import weakref

from omlish import check
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import defs
from omlish import lang


class Resolvable(abc.ABC):
    pass


@dc.dataclass(frozen=True)
class Field(Resolvable):
    name: str = dc.xfield(coerce=check.non_empty_str)
    type: type
    metadata: ta.Mapping[ta.Any, ta.Any] = dc.field(default_factory=dict)
    entity: ta.Optional['Entity'] = None


class Entity(Resolvable):
    def __init__(
            self,
            name: str,
            fields: ta.Iterable[Field],
            metadata: ta.Mapping[ta.Any, ta.Any] | None = None,
    ) -> None:
        super().__init__()
        self._name = name
        self._fields: dict[str, Field] = {}
        for f in fields:
            check.none(f.entity)
            check.not_in(f.name, self._fields)
            self._fields[f.name] = dc.replace(f, entity=self)
        self._metadata = metadata

    defs.repr('name')

    @property
    def name(self) -> str:
        return self._name

    @property
    def fields(self) -> ta.Mapping[str, Field]:
        return self._fields

    @property
    def metadata(self) -> ta.Mapping[ta.Any, ta.Any]:
        return self._metadata


class FailedResolutionError(Exception):
    pass


class AmbiguousResolutionError(Exception):
    pass


class Resolver(abc.ABC):
    @abc.abstractmethod
    def resolve(
            self,
            ty: type[Resolvable] | tuple[type[Resolvable, ...]],
            obj: ta.Any,
            ns: ta.Mapping[str, ta.Any] | None = None,
    ) -> ta.Optional[ta.Any]:
        raise NotImplementedError


class Config(Resolver):
    def __init__(self, parent: ta.Optional['Config']) -> None:
        super().__init__()
        self._parent = parent
        self._children: weakref.WeakSet['Config'] = weakref.WeakSet()
        if parent is not None:
            parent._children.add(self)

        self._resolvers = []
        self._providers_by_key_by_type = col.IdentityKeyDict()
        self._generators = []
        self._version = 0
        self._generated_for = col.IdentitySet()
        self._all_providers = None

    @property
    def lineage(self) -> ta.Iterator['Config']:
        yield self
        if self._parent is not None:
            yield from self._parent.lineage

    @property
    def children(self) -> ta.AbstractSet['Config']:
        return self._children

    def invalidate(self) -> None:
        self._version += 1
        self._generated_for = col.IdentitySet()
        self._all_providers = None
        for c in self.children:
          c.invalidate()

    def resolve(
            self,
            ty: type[Resolvable] | tuple[type[Resolvable, ...]],
            obj: ta.Any,
            ns: ta.Mapping[str, ta.Any] | None = None,
    ) -> ta.Optional[ta.Any]:
        if isinstance(ty, tuple):
            ra = []
            for t in ty:
                try:
                    r = self.resolve(t, obj, ns)
                except FailedResolutionError:
                    pass
                else:
                    if r is not None:
                        ra.append(r)

            if len(ra) > 1:
                raise AmbiguousResolutionError
            elif ra:
                return ra[0]
            else:
                raise FailedResolutionError

        elif ty not in (Field, Entity):
            raise TypeError(ty)

        elif isinstance(obj, ty):
            return obj

        elif isinstance(obj, str):
            if not ns:
                raise FailedResolutionError
            try:
                return ns[obj]
            except KeyError:
                raise FailedResolutionError



ROOT_CONFIG = Config(None)


class Provider(abc.ABC):
    pass


MAX_DEPTH = 50


class Context:
    def __init__(
            self,
            origin: ta.Union['Context', Config, None],
            seed: ta.Mapping[Resolvable, ta.Any] | None = None,
    ) -> None:
        super().__init__()

        if isinstance(origin, Context):
            parent = origin
            config = origin.config
        elif isinstance(origin, Config):
            parent = None
            config = origin
        elif origin is None:
            parent = None
            config = ROOT_CONFIG
        else:
            raise TypeError

        self._parent = parent
        self._config = config

        self._children: list['Context'] = []
        self._bindings = col.IdentityKeyDict()
        self._metadata: dict = {}
        self._children_with_metadata = {}

        if parent is not None:
            parent._children.append(self)

        if seed is not None:
            for k, v in seed.items():
                self.bind(k, v)

    @property
    def parent(self) -> ta.Optional['Context']:
        return self._parent

    @property
    def config(self) -> Config:
        return self._config

    @property
    def children(self) -> ta.Sequence['Context']:
        return self._children

    @property
    def metadata(self) -> ta.Mapping[ta.Any, ta.Any]:
        return self._metadata

    @property
    def lineage(self) -> ta.Iterator['Context']:
        yield self
        if self._parent is not None:
            yield from self._parent.lineage

    def provide(self, key: Resolvable, max_depth: int = MAX_DEPTH) -> ta.Any:
        if max_depth < 1:
            raise RuntimeError('Recursion depth exceeded')