import enum
import operator
import typing as ta

from omlish import cached
from omlish import check
from omlish import collections as col
from omlish import dataclasses as dc


##


@dc.dataclass(frozen=True)
class Attribute:
    name: str

    entity: ta.Optional['Entity'] = None


@dc.dataclass(frozen=True)
class Attributes(ta.Sequence[Attribute]):
    lst: ta.Sequence[Attribute]

    @cached.property
    @dc.init  # FIXME: doesn't cache lol
    def by_name(self) -> ta.Mapping[str, Attribute]:
        return col.make_map_by(operator.attrgetter('name'), self.lst, strict=True)

    def __getitem__(self, item: int) -> Attribute:  # type: ignore
        return self.lst[item]

    def __iter__(self) -> ta.Iterator[Attribute]:
        return iter(self.lst)

    def __len__(self) -> int:
        return len(self.lst)


@dc.dataclass(frozen=True)
class Entity:
    name: str
    src_attrs: ta.Sequence[Attribute] = dc.field(repr=False)

    @cached.property
    @dc.init  # FIXME: doesn't cache lol
    def attrs(self) -> ta.Sequence[Attribute]:
        return [
            dc.replace(a, entity=check.replacing_none(a.entity, self))
            for a in self.src_attrs
        ]


##


@dc.dataclass(frozen=True)
class Derivation:
    pass


##


class Cost(enum.Enum):
    TRIVIAL = enum.auto()
    PURE = enum.auto()
    IO = enum.auto()


##


def _main() -> None:
    user = Entity('user', [Attribute('id'), Attribute('name')])
    business = Entity('business', [Attribute('id'), Attribute('name')])
    review = Entity('review', [Attribute('id'), Attribute('business_id'), Attribute('user_id')])

    print(user.attrs)


if __name__ == '__main__':
    _main()
