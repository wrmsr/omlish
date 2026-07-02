# ruff: noqa: F821 PLC0132 SLF001
# ruff: noqa: PYI059
import typing as ta

from ..core import types
from ..core.typekeys import TYPE_KEY
from ..typekeys import TypeKeys
from .helpers import make_reflector


def test_newtype_literal_reflection_and_key_are_cache_friendly() -> None:
    reflector = make_reflector()
    type_keys = TypeKeys(lock=reflector._lock)
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore

    typ = reflector.reflect_type(mode)
    key = type_keys.type_key(typ)

    assert reflector.reflect_type(mode) is typ
    assert type_keys.type_key(typ) is key
    assert reflector._type_cache[mode] is typ
    assert type_keys._type_key_cache[(TYPE_KEY, typ)] is key


def test_type_alias_reflection_and_key_are_cache_friendly() -> None:
    reflector = make_reflector()
    type_keys = TypeKeys(lock=reflector._lock)
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    mode_list = ta.TypeAliasType('ModeList', list[mode])  # type: ignore

    typ = reflector.reflect_type(mode_list)
    key = type_keys.type_key(typ)

    assert reflector.reflect_type(mode_list) is typ
    assert type_keys.type_key(typ) is key
    assert reflector._type_cache[mode_list] is typ
    assert type_keys._type_key_cache[(TYPE_KEY, typ)] is key


def test_subscripted_type_alias_reflection_and_key_are_cache_friendly() -> None:
    reflector = make_reflector()
    type_keys = TypeKeys(lock=reflector._lock)
    t_var = ta.TypeVar('T')  # type: ignore
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    alias = ta.TypeAliasType('Alias', dict[str, t_var], type_params=(t_var,))  # type: ignore
    form = alias[mode]

    typ = reflector.reflect_type(form)
    key = type_keys.type_key(typ)

    assert reflector.reflect_type(form) is typ
    assert type_keys.type_key(typ) is key
    assert reflector._type_cache[form] is typ
    assert type_keys._type_key_cache[(TYPE_KEY, typ)] is key


def test_subscripted_variadic_type_alias_reflection_and_key_are_cache_friendly() -> None:
    reflector = make_reflector()
    type_keys = TypeKeys(lock=reflector._lock)
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    alias = ta.TypeAliasType('Alias', tuple[*ts_var], type_params=(ts_var,))  # type: ignore
    form = alias[int, str]

    typ = reflector.reflect_type(form)
    key = type_keys.type_key(typ)

    assert isinstance(typ, types.TypeAliasType)
    assert reflector.reflect_type(form) is typ
    assert type_keys.type_key(typ) is key
    assert reflector._type_cache[form] is typ
    assert type_keys._type_key_cache[(TYPE_KEY, typ)] is key


def test_reflected_string_type_key_common_combinations_are_explicit() -> None:
    reflector = make_reflector()
    type_keys = TypeKeys(lock=reflector._lock)

    assert type_keys.type_key(reflector.reflect_type(list[int])) == "I['builtins.list',I['builtins.int']]"
    assert type_keys.type_key(reflector.reflect_type(dict[str, int])) == (
        "I['builtins.dict',I['builtins.str'],I['builtins.int']]"
    )
    assert type_keys.type_key(reflector.reflect_type(ta.Mapping[str, ta.Sequence[int]])) == (
        "I['collections.abc.Mapping',I['builtins.str'],"
        "I['collections.abc.Sequence',I['builtins.int']]]"
    )
    assert type_keys.type_key(reflector.reflect_type(ta.Literal['x', 'y'])) == (
        "U[L[str:'x',I['builtins.str']],L[str:'y',I['builtins.str']]]"
    )
    assert type_keys.type_key(reflector.reflect_type(ta.Annotated[int, 'cfg'])) == (
        "Ann[I['builtins.int'],$0]",
        ('cfg',),
    )


def test_reflect_type_key_reuses_equivalent_runtime_forms() -> None:
    reflector = make_reflector()
    type_keys = TypeKeys(lock=reflector._lock)

    assert type_keys.type_key(reflector.reflect_type(list[int])) == \
           type_keys.type_key(reflector.reflect_type(list[int]))
    assert type_keys.type_key(reflector.reflect_type(int | str)) == \
           type_keys.type_key(reflector.reflect_type(str | int))


def test_reflect_type_key_keeps_distinct_parameterizations_apart() -> None:
    reflector = make_reflector()
    type_keys = TypeKeys(lock=reflector._lock)

    assert type_keys.type_key(reflector.reflect_type(list[int])) != \
           type_keys.type_key(reflector.reflect_type(list[str]))


def test_reflect_type_key_or_none_suppresses_unsupported_reflected_node() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    reflector = make_reflector()
    type_keys = TypeKeys(lock=reflector._lock)

    assert type_keys.type_key_or_none(reflector.reflect_type(t_var)) is not None
