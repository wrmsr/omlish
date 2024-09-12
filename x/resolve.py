import dataclasses as dc
import enum
import typing as ta


##


@dc.dataclass(frozen=True)
class Attribute:
    name: str


@dc.dataclass(frozen=True)
class Entity:
    name: str
    attrs: ta.Sequence[Attribute]


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
