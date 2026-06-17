# ruff: noqa: PLC0132 SLF001
import typing as ta

from ...reflect import RuntimeTypeReflector
from ...universe import RuntimeTypeUniverse
from ..ops import reflect_type_key
from ..ops import reflect_type_key_or_none


def test_reflected_string_type_key_common_combinations_are_explicit() -> None:
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    assert reflect_type_key(list[int], reflector) == "I['builtins.list',I['builtins.int']]"
    assert reflect_type_key(dict[str, int], reflector) == (
        "I['builtins.dict',I['builtins.str'],I['builtins.int']]"
    )
    assert reflect_type_key(ta.Mapping[str, ta.Sequence[int]], reflector) == (
        "I['collections.abc.Mapping',I['builtins.str'],"
        "I['collections.abc.Sequence',I['builtins.int']]]"
    )
    assert reflect_type_key(ta.Literal['x', 'y'], reflector) == (
        "U[L[str:'x',I['builtins.str']],L[str:'y',I['builtins.str']]]"
    )
    assert reflect_type_key(ta.Annotated[int, 'cfg'], reflector) == (
        "Ann[I['builtins.int'],$0]",
        ('cfg',),
    )


def test_reflect_type_key_reuses_equivalent_runtime_forms() -> None:
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    assert reflect_type_key(list[int], reflector) == reflect_type_key(list[int], reflector)
    assert reflect_type_key(int | str, reflector) == reflect_type_key(str | int, reflector)


def test_reflect_type_key_keeps_distinct_parameterizations_apart() -> None:
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    assert reflect_type_key(list[int], reflector) != reflect_type_key(list[str], reflector)


def test_reflect_type_key_or_none_suppresses_unsupported_reflected_node() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    assert reflect_type_key_or_none(t_var, reflector) is not None
