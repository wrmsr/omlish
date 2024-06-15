import typing as ta


class InfinityType:
    def __repr__(self) -> str:
        return 'Infinity'

    def __hash__(self) -> int:
        return hash(repr(self))

    def __lt__(self, other: ta.Any) -> bool:
        return False

    def __le__(self, other: ta.Any) -> bool:
        return False

    def __eq__(self, other: ta.Any) -> bool:
        return isinstance(other, self.__class__)

    def __gt__(self, other: ta.Any) -> bool:
        return True

    def __ge__(self, other: ta.Any) -> bool:
        return True

    def __neg__(self: ta.Any) -> 'NegativeInfinityType':
        return NegativeInfinity


Infinity = InfinityType()


class NegativeInfinityType:
    def __repr__(self) -> str:
        return '-Infinity'

    def __hash__(self) -> int:
        return hash(repr(self))

    def __lt__(self, other: ta.Any) -> bool:
        return True

    def __le__(self, other: ta.Any) -> bool:
        return True

    def __eq__(self, other: ta.Any) -> bool:
        return isinstance(other, self.__class__)

    def __gt__(self, other: ta.Any) -> bool:
        return False

    def __ge__(self, other: ta.Any) -> bool:
        return False

    def __neg__(self: ta.Any) -> InfinityType:
        return Infinity


NegativeInfinity = NegativeInfinityType()
