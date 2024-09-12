"""
TODO:
 - arrays
  - context 'nesting"
   - but no overriding!!
    - PersistentMap!
  - size is part of the type - (a[20] + b[20]) < (a[50] + b)
   - cache plans.. symbolic math like tg?
 - 'modified' pathfinding - need all targets reached
"""
import abc
import enum
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

    def __str__(self) -> str:
        return f'{lang.snake_case(self.__class__.__name__)}:{self.full_name}'

    @property
    def children(self) -> ta.Iterable['Resolvable']:
        return ()


@dc.dataclass(frozen=True, eq=False)
class Attribute(Resolvable):
    name: str

    entity: ta.Optional['Entity'] = None

    @cached.property
    def full_name(self) -> str:
        return '.'.join([check.not_none(self.entity).name, self.name])


@dc.dataclass(frozen=True)
class Attributes(ta.Sequence[Attribute]):
    lst: ta.Sequence[Attribute]

    @dc.init  # type: ignore
    @cached.property
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


@dc.dataclass(frozen=True, eq=False)
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


class Cost(enum.Enum):
    TRIVIAL = enum.auto()
    PURE = enum.auto()
    IO = enum.auto()


ResolverImpl: ta.TypeAlias = ta.Callable[[ta.Mapping[Resolvable, ta.Any]], ta.Any]


@dc.dataclass(frozen=True)
class Resolver:
    cost: Cost
    inputs: frozenset[Resolvable]
    output: Resolvable
    impl: ResolverImpl


@dc.dataclass(frozen=True)
class Resolvers:
    all: ta.Sequence[Resolver]

    @cached.property
    @dc.init
    def by_output(self) -> ta.Mapping[Resolvable, ta.Sequence[Resolver]]:
        return col.multi_map_by(operator.attrgetter('output'), self.all)

    @cached.property
    @dc.init
    def by_input(self) -> ta.Mapping[Resolvable, ta.Sequence[Resolver]]:
        dct: dict[Resolvable, list[Resolver]] = {}
        for r in self.all:
            for i in r.inputs:
                dct.setdefault(i, []).append(r)
        return dct


##


class _DummyResolvable(Resolvable):
    @property
    def full_name(self) -> str:
        raise TypeError


_DUMMY_RESOLVABLE = _DummyResolvable()


@dc.dataclass(frozen=True, eq=False)
class Derivation(Resolvable):
    name: str
    src_resolver: Resolver = dc.field(repr=False)
    fn: ta.Callable
    params: ta.Sequence[Resolvable]

    @cached.property
    @dc.init
    def resolver(self) -> Resolver:
        return dc.replace(self.src_resolver, output=check.replacing(self.src_resolver.output, _DUMMY_RESOLVABLE, self))

    def __post_init__(self) -> None:
        dc.maybe_post_init(super())
        lang.update_wrapper(self, self.fn, setattr=object.__setattr__)

    @property
    def full_name(self) -> str:
        return self.name

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)


def derivation(
        *params: Resolvable,
        name: str | None = None,
        cost: Cost = Cost.TRIVIAL,
) -> ta.Callable[[ta.Callable], Derivation]:
    def inner(fn):
        def impl(dct: ta.Mapping[Resolvable, ta.Any]) -> ta.Any:
            return fn(*[dct[p] for p in params])

        resolver = Resolver(
            cost=cost,
            inputs=frozenset(params),
            output=_DUMMY_RESOLVABLE,
            impl=impl,
        )

        return Derivation(
            name=name if name is not None else fn.__name__,
            src_resolver=resolver,
            fn=fn,
            params=params,
        )

    return inner  # noqa


##


def make_dataclass_entity(cls: type) -> Entity:
    atts: list[Attribute] = []
    for fld in dc.fields(cls):  # noqa
        atts.append(Attribute(fld.name))

    return Entity(
        lang.snake_case(cls.__name__),
        atts,
    )


def make_entity_attribute_resolvers(ent: Entity) -> ta.Sequence[Resolver]:
    def make_impl(att: Attribute) -> ResolverImpl:
        def impl(dct: ta.Mapping[Resolvable, ta.Any]) -> ta.Any:
            obj = dct[ent]
            return getattr(obj, att.name)
        return impl

    out: list[Resolver] = []
    for att in ent.attrs:
        out.append(Resolver(
            cost=Cost.TRIVIAL,
            inputs=[ent],
            output=att,
            impl=make_impl(att),
        ))

    return out


##


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
    user_id: int
    business_id: int
    text: str


#


USERS = [
    User(
        id=i,
        name=f'user {i}',
        first_name=f'first_name {i}',
        last_name=f'last_name {i}',
    )
    for i in range(3)
]

BUSINESSES = [
    Business(
        id=i,
        name=f'business {i}',
    )
    for i in range(3)
]

REVIEWS = [
    Review(
        id=(i := u * len(USERS) + b),
        user_id=u,
        business_id=b,
        text=f'review {i} user {u} business {b}',
    )
    for u in range(len(USERS))
    for b in range(len(BUSINESSES))
]


#


def make_entity_list_resolver(
        ent: Entity,
        lst: ta.Sequence,
) -> Resolver:
    id_att = ent.attrs['id']

    def impl(dct: ta.Mapping[Resolvable, ta.Any]) -> ta.Any:
        id = dct[id_att]  # noqa
        return lst[id]

    return Resolver(
        cost=Cost.TRIVIAL,
        inputs=[id_att],
        output=ent,
        impl=impl,
    )


#


def _main() -> None:
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
        user_full_name,
    ]

    #

    resolvers = Resolvers([
        *lang.flatten(make_entity_attribute_resolvers(ent) for ent in entities),
        *[d.resolver for d in derivations],

        *[make_entity_list_resolver(c, l) for c, l in [
            (user, USERS),
            (business, BUSINESSES),
            (review, REVIEWS),
        ]],
    ])

    pprint.pprint(resolvers.by_output)
    pprint.pprint(resolvers.by_input)

    #

    resolvables = Resolvables([
        *entities,
        *derivations,
    ])

    pprint.pprint(resolvables.by_full_name)

    #

    ctx: dict[Resolvable, ta.Any] = {
        user.attrs['id']: 1,
    }


if __name__ == '__main__':
    _main()
