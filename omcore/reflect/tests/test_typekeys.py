# ruff: noqa: F821 PLC0132 SLF001
# ruff: noqa: PYI059
import typing as ta

from ..core.typekeys import type_key
from ..core.typekeys import type_key_or_none
from .helpers import make_mirror


def test_reflected_string_type_key_common_combinations_are_explicit() -> None:
    mirror = make_mirror()

    assert type_key(mirror.reflect_type(list[int])) == "I['builtins.list',I['builtins.int']]"
    assert type_key(mirror.reflect_type(dict[str, int])) == (
        "I['builtins.dict',I['builtins.str'],I['builtins.int']]"
    )
    assert type_key(mirror.reflect_type(ta.Mapping[str, ta.Sequence[int]])) == (
        "I['collections.abc.Mapping',I['builtins.str'],"
        "I['collections.abc.Sequence',I['builtins.int']]]"
    )
    assert type_key(mirror.reflect_type(ta.Literal['x', 'y'])) == (
        "U[L[str:'x',I['builtins.str']],L[str:'y',I['builtins.str']]]"
    )
    assert type_key(mirror.reflect_type(ta.Annotated[int, 'cfg'])) == (
        "Ann[I['builtins.int'],$0]",
        ('cfg',),
    )


def test_reflect_type_key_reuses_equivalent_runtime_forms() -> None:
    mirror = make_mirror()

    assert type_key(mirror.reflect_type(list[int])) == \
           type_key(mirror.reflect_type(list[int]))
    assert type_key(mirror.reflect_type(int | str)) == \
           type_key(mirror.reflect_type(str | int))


def test_reflect_type_key_keeps_distinct_parameterizations_apart() -> None:
    mirror = make_mirror()

    assert type_key(mirror.reflect_type(list[int])) != \
           type_key(mirror.reflect_type(list[str]))


def test_reflect_type_key_or_none_suppresses_unsupported_reflected_node() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    mirror = make_mirror()

    assert type_key_or_none(mirror.reflect_type(t_var)) is not None
