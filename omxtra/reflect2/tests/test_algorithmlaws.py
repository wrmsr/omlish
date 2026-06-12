# ruff: noqa: F821
import collections.abc as cabc
import typing as ta

from ..core.subtypes import is_same_type
from ..core.subtypes import is_structurally_equivalent
from ..ops import reflect_is_assignable
from ..ops import reflect_is_structural_subtype
from ..ops import reflect_join
from ..ops import reflect_meet
from ..ops import reflect_structural_join
from ..ops import reflect_structural_meet
from ..reflect import RuntimeTypeReflector
from ..universe import RuntimeTypeUniverse


##


def assert_reflected_nominal_subtype_lattice_law(
        subtype: object,
        supertype: object,
        reflector: RuntimeTypeReflector,
) -> None:
    subtype_type = reflector.reflect_type(subtype)
    supertype_type = reflector.reflect_type(supertype)

    assert reflect_is_assignable(subtype, supertype, reflector)
    assert is_same_type(reflect_join(subtype, supertype, reflector), supertype_type)
    assert is_same_type(reflect_join(supertype, subtype, reflector), supertype_type)
    assert is_same_type(reflect_meet(subtype, supertype, reflector), subtype_type)
    assert is_same_type(reflect_meet(supertype, subtype, reflector), subtype_type)


def assert_reflected_structural_subtype_lattice_law(
        subtype: object,
        supertype: object,
        reflector: RuntimeTypeReflector,
) -> None:
    subtype_type = reflector.reflect_type(subtype)
    supertype_type = reflector.reflect_type(supertype)

    assert reflect_is_structural_subtype(subtype, supertype, reflector)
    assert is_structurally_equivalent(reflect_structural_join(subtype, supertype, reflector), supertype_type)
    assert is_structurally_equivalent(reflect_structural_join(supertype, subtype, reflector), supertype_type)
    assert is_structurally_equivalent(reflect_structural_meet(subtype, supertype, reflector), subtype_type)
    assert is_structurally_equivalent(reflect_structural_meet(supertype, subtype, reflector), subtype_type)


##


def test_reflected_nominal_subtype_lattice_laws_cover_classes_generics_and_tuples() -> None:
    T_co = ta.TypeVar('T_co', covariant=True)

    class Base:
        pass

    class Child(Base):
        pass

    class Box(ta.Generic[T_co]):
        pass

    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    assert_reflected_nominal_subtype_lattice_law(Child, Base, reflector)
    assert_reflected_nominal_subtype_lattice_law(Box[Child], Box[Base], reflector)
    assert_reflected_nominal_subtype_lattice_law(tuple[int, str], tuple[object, object], reflector)


def test_reflected_nominal_subtype_lattice_laws_cover_callables() -> None:
    class Base:
        pass

    class Child(Base):
        pass

    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    assert_reflected_nominal_subtype_lattice_law(
        cabc.Callable[[Base], Child],
        cabc.Callable[[Child], Base],
        reflector,
    )


def test_reflected_structural_recursive_alias_lattice_laws_cover_unrolling() -> None:
    alias = ta.TypeAliasType('Node', int | list['Node'])  # type: ignore
    unrolled = int | list[alias]  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    assert_reflected_structural_subtype_lattice_law(alias, unrolled, reflector)
    assert_reflected_structural_subtype_lattice_law(unrolled, alias, reflector)


def test_reflected_structural_recursive_alias_lattice_laws_ignore_alias_identity() -> None:
    left = ta.TypeAliasType('Left', int | list['Left'])  # type: ignore
    right = ta.TypeAliasType('Right', int | list['Right'])  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    assert_reflected_structural_subtype_lattice_law(left, right, reflector)
    assert_reflected_structural_subtype_lattice_law(right, left, reflector)
