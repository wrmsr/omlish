# ruff: noqa: F821 PLC0132 SLF001
# ruff: noqa: PYI059
import annotationlib
import collections.abc as cabc
import typing as ta

import pytest

from ..core import symbols
from ..core import types
from ..core.strconv import type_str
from ..core.substitute import substitute_type
from ..core.subtypes import get_mro_instances
from ..core.subtypes import is_alpha_equivalent
from ..core.subtypes import is_equivalent
from ..core.subtypes import is_same_type
from ..core.subtypes import is_subtype
from ..core.typekeys import TYPE_KEY
from ..core.typekeys import tuple_type_key
from ..core.typekeys import type_key
from ..core.typeops import get_proper_type
from ..errors import UnreflectableTypeError
from ..reflector import TypeReflector
from ..reflector import reflect_type
from ..universe import TypeUniverse


def test_new_type_literal_reflection_and_key_are_cache_friendly() -> None:
    reflector = TypeReflector(universe=TypeUniverse())
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore

    typ = reflector.reflect_type(mode)
    key = reflector.type_key(typ)

    assert reflector.reflect_type(mode) is typ
    assert reflector.type_key(typ) is key
    assert reflector._type_cache[mode] is typ
    assert reflector._type_key_cache[(TYPE_KEY, typ)] is key


def test_type_alias_reflection_and_key_are_cache_friendly() -> None:
    reflector = TypeReflector(universe=TypeUniverse())
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    mode_list = ta.TypeAliasType('ModeList', list[mode])  # type: ignore

    typ = reflector.reflect_type(mode_list)
    key = reflector.type_key(typ)

    assert reflector.reflect_type(mode_list) is typ
    assert reflector.type_key(typ) is key
    assert reflector._type_cache[mode_list] is typ
    assert reflector._type_key_cache[(TYPE_KEY, typ)] is key


def test_subscripted_type_alias_reflection_and_key_are_cache_friendly() -> None:
    reflector = TypeReflector(universe=TypeUniverse())
    t_var = ta.TypeVar('T')  # type: ignore
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    alias = ta.TypeAliasType('Alias', dict[str, t_var], type_params=(t_var,))  # type: ignore
    form = alias[mode]

    typ = reflector.reflect_type(form)
    key = reflector.type_key(typ)

    assert reflector.reflect_type(form) is typ
    assert reflector.type_key(typ) is key
    assert reflector._type_cache[form] is typ
    assert reflector._type_key_cache[(TYPE_KEY, typ)] is key


def test_subscripted_variadic_type_alias_reflection_and_key_are_cache_friendly() -> None:
    reflector = TypeReflector(universe=TypeUniverse())
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    alias = ta.TypeAliasType('Alias', tuple[*ts_var], type_params=(ts_var,))  # type: ignore
    form = alias[int, str]

    typ = reflector.reflect_type(form)
    key = reflector.type_key(typ)

    assert isinstance(typ, types.TypeAliasType)
    assert reflector.reflect_type(form) is typ
    assert reflector.type_key(typ) is key
    assert reflector._type_cache[form] is typ
    assert reflector._type_key_cache[(TYPE_KEY, typ)] is key


