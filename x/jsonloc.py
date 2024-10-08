import dataclasses as dc
import textwrap
import typing as ta

from omlish import lang


T = ta.TypeVar('T')
V = ta.TypeVar('V')


##


@dc.dataclass(frozen=True)
class TaggedValue(lang.Final, ta.Generic[V, T]):
    v: V
    t: T


##


@dc.dataclass(frozen=True)
class Location(lang.Final):
    l: int
    c: int
    b: int


##


JsonValue: ta.TypeAlias = ta.Union[
    str,
    int,
    float,
    bool,
    None,
    list['JsonValue'],
    dict[str, 'JsonValue'],
]


##


def location_loads(s: str) -> TaggedValue[JsonValue, Location]:
    raise NotImplementedError


def _main() -> None:
    s = textwrap.dedent("""
    {
        "name": "Alice",
        "age": 30,
        "is_student": false,
        "courses": ["Mathematics", "Physics", "Computer Science"],
        "address": {
            "street": "123 Main St",
            "city": "Wonderland",
            "zip_code": "12345"
        },
        "grades": {
            "Mathematics": "A",
            "Physics": "B+",
            "Computer Science": "A-"
        },
        "emergency_contact": null
    }
    """)
    print(loads(s))


if __name__ == '__main__':
    _main()
