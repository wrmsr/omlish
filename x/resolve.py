import enum
import typing as ta

from omlish import cached
from omlish import dataclasses as dc


##


@dc.dataclass(frozen=True)
class Attribute:
    name: str

    entity: ta.Optional['Entity'] = None


@dc.dataclass(frozen=True)
class Entity:
    name: str
    src_attrs: ta.Sequence[Attribute]

    @cached.property
    @dc.init
    def attrs(self) -> ta.Sequence[Attribute]:
        raise NotImplementedError


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


if __name__ == '__main__':
    _main()
