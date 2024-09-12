"""
FIXME:
 - @cached.property @dc.init doesn't cache lol, need idiom + dont break pycharm
"""
import abc
import enum
import functools
import operator
import pprint
import typing as ta

from omlish import cached
from omlish import check
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang


##


class Resolvable(abc.ABC):
    @property
    @abc.abstractmethod
    def full_name(self) -> str:
        raise NotImplementedError

    @property
    def children(self) -> ta.Iterable['Resolvable']:
        return ()


@dc.dataclass(frozen=True)
class Attribute(Resolvable):
    name: str

    entity: ta.Optional['Entity'] = None

    @cached.property
    def full_name(self) -> str:
        return '.'.join([check.not_none(self.entity).name, self.name])


@dc.dataclass(frozen=True)
class Attributes(ta.Sequence[Attribute]):
    lst: ta.Sequence[Attribute]

    @cached.property
    @dc.init
    def by_name(self) -> ta.Mapping[str, Attribute]:
        return col.make_map_by(operator.attrgetter('name'), self.lst, strict=True)

    def __getitem__(self, item: int | str) -> Attribute:  # type: ignore
        if isinstance(item, int):
            return self.lst[item]
        elif isinstance(item, str):
            return self.by_name[item]
        else:
            raise TypeError(item)

    def __iter__(self) -> ta.Iterator[Attribute]:
        return iter(self.lst)

    def __len__(self) -> int:
        return len(self.lst)


@dc.dataclass(frozen=True)
class Entity(Resolvable):
    name: str
    src_attrs: ta.Sequence[Attribute] = dc.field(repr=False)

    @property
    def full_name(self) -> str:
        return self.name

    @cached.property
    @dc.init
    def attrs(self) -> Attributes:
        return Attributes([
            dc.replace(a, entity=check.replacing_none(a.entity, self))
            for a in self.src_attrs
        ])

    @property
    def children(self) -> ta.Iterable[Resolvable]:
        return self.attrs


##


@dc.dataclass(frozen=True)
class Resolvables:
    roots: ta.Sequence[Resolvable]

    @cached.property
    @dc.init
    def all(self) -> ta.Sequence[Resolvable]:
        out: list[Resolvable] = []
        stk: list[Resolvable] = list(reversed(self.roots))
        while stk:
            cur = stk.pop()
            out.append(cur)
            stk.extend(reversed(list(cur.children)))
        return out

    @cached.property
    @dc.init
    def by_full_name(self) -> ta.Mapping[str, Resolvable]:
        return col.make_map_by(operator.attrgetter('full_name'), self.all)


##


@dc.dataclass(frozen=True)
class Derivation(Resolvable):
    name: str
    inputs: ta.Sequence[Resolvable]
    fn: ta.Callable

    def __post_init__(self) -> None:
        dc.maybe_post_init(super())
        lang.update_wrapper(self, self.fn, setattr=object.__setattr__)

    @property
    def full_name(self) -> str:
        return self.name

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)


def derivation(*inputs: Resolvable, **kwargs: ta.Any) -> ta.Callable[[ta.Callable], Derivation]:
    def inner(fn):
        if 'name' in kwargs:
            name = kwargs.pop('name')
        else:
            name = fn.__name__
        return Derivation(
            name=name,
            inputs=inputs,
            fn=fn,
            **kwargs,
        )
    return inner


##


def make_dataclass_entity(cls: type) -> Entity:
    atts: list[Attribute] = []
    for fld in dc.fields(cls):  # noqa
        atts.append(Attribute(fld.name))
    return Entity(
        lang.snake_case(cls.__name__),
        atts,
    )


def make_entity_attribute_derivations(ent: Entity) -> ta.Sequence[Derivation]:
    out: list[Derivation] = []
    for att in ent.attrs:
        out.append(Derivation(
            name='_'.join([ent.name, att.name]),
            inputs=[ent],
            fn=operator.attrgetter(att.name),
        ))
    return out


##


class Cost(enum.Enum):
    TRIVIAL = enum.auto()
    PURE = enum.auto()
    IO = enum.auto()


##


def _main() -> None:
    @dc.dataclass(frozen=True)
    class User:
        id: int
        name: str
        first_name: str
        last_name: str

    @dc.dataclass(frozen=True)
    class Business:
        id: int
        name: str

    @dc.dataclass(frozen=True)
    class Review:
        id: int
        business_id: int
        user_id: int
        text: str

    #

    user = make_dataclass_entity(User)
    business = make_dataclass_entity(Business)
    review = make_dataclass_entity(Review)

    entities = [
        user,
        business,
        review,
    ]

    #

    @derivation(user.attrs['first_name'], user.attrs['last_name'])
    def user_full_name(first_name: str, last_name: str) -> str:
        return ' '.join([first_name, last_name])

    derivations = [
        *lang.flatten(make_entity_attribute_derivations(ent) for ent in entities),
        user_full_name,
    ]

    #

    resolvables = Resolvables([
        *entities,
        *derivations,
    ])

    pprint.pprint(resolvables.by_full_name)


if __name__ == '__main__':
    _main()
