import enum
import typing as ta

from omlish import cached
from omlish import check
from omlish import dataclasses as dc


##


@dc.dataclass(frozen=True)
class Attribute:
    name: str

    entity: ta.Optional['Entity'] = None


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
