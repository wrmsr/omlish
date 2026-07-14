import typing as ta

import pytest

from ..mro import MroError
from ..mro import try_mro


def test_try_mro_ok_simple() -> None:
    class A:
        pass

    class B:
        pass

    assert try_mro(A, B) == (A, B)


def test_try_mro_conflict_simple() -> None:
    class X:
        pass

    class Y:
        pass

    class A(X, Y):
        pass

    class B(Y, X):
        pass

    with pytest.raises(MroError) as exc_info:
        try_mro(A, B)

    e = exc_info.value

    assert e.bases == (A, B)
    assert e.expanded_bases == (A, B)

    assert any(v == (A, B) for v in e.conflicts.values())
    assert any(v == (B, A) for v in e.conflicts.values())

    s = str(e)
    assert 'Original bases:' in s
    assert 'Expanded bases:' in s
    assert 'Conflicts:' in s
    assert 'Remaining sequences at failure:' in s


def test_try_mro_reports_remaining_sequences_simple() -> None:
    class X:
        pass

    class Y:
        pass

    class A(X, Y):
        pass

    class B(Y, X):
        pass

    with pytest.raises(MroError) as exc_info:
        try_mro(A, B)

    e = exc_info.value

    assert len(e.remaining_sequences) == 2

    seq0, seq1 = e.remaining_sequences

    assert seq0 == (
        (A, X),
        (A, Y),
        (A, object),
    )
    assert seq1 == (
        (B, Y),
        (B, X),
        (B, object),
    )


def test_try_mro_uses_exact_generic_alias_object() -> None:
    T = ta.TypeVar('T')

    class X:
        pass

    class Y:
        pass

    class Left(ta.Generic[T], X, Y):  # noqa
        pass

    class Right(Y, X):
        pass

    alias = Left[int]

    with pytest.raises(MroError) as exc_info:
        try_mro(alias, Right)

    e = exc_info.value
    assert e.bases[0] is alias
    assert e.bases[1] is Right

    assert e.expanded_bases == (Left, Right)

    assert any(v[0] is alias for v in e.conflicts.values()) or any(
        len(v) > 1 and v[1] is alias for v in e.conflicts.values()
    )

    # All entries in sequences attributable to the first expanded base should
    # point back to the exact alias object, not the expanded class Left.
    assert any(
        any(ob is alias for ob, _ in seq)
        for seq in e.remaining_sequences
    )


def test_try_mro_custom_unhashable_mro_entries_object() -> None:
    class X:
        pass

    class Y:
        pass

    class Left(X, Y):
        pass

    class Right(Y, X):
        pass

    class Expand:
        __hash__ = None  # type: ignore[assignment]

        def __init__(self, ty: type) -> None:
            self.ty = ty

        def __mro_entries__(self, bases: tuple[ta.Any, ...]) -> tuple[type, ...]:
            return (self.ty,)

        def __repr__(self) -> str:
            return f'Expand({self.ty.__name__})'

    ex = Expand(Left)

    with pytest.raises(MroError) as exc_info:
        try_mro(ex, Right)

    e = exc_info.value
    assert e.bases[0] is ex
    assert e.bases[1] is Right
    assert e.expanded_bases == (Left, Right)

    assert any(v[0] is ex for v in e.conflicts.values()) or any(
        len(v) > 1 and v[1] is ex for v in e.conflicts.values()
    )

    assert any(
        any(ob is ex for ob, _ in seq)
        for seq in e.remaining_sequences
    )


def test_try_mro_invalid_non_type_without_mro_entries() -> None:
    class NotABase:
        pass

    obj = NotABase()

    with pytest.raises(TypeError):
        try_mro(obj)


def test_try_mro_invalid_mro_entries_return_non_tuple() -> None:
    class Bad:
        def __mro_entries__(self, bases: tuple[ta.Any, ...]) -> ta.Any:
            return object

    with pytest.raises(TypeError, match='returned non-tuple'):
        try_mro(Bad())


def test_try_mro_invalid_mro_entries_return_non_type_entry() -> None:
    class Bad:
        def __mro_entries__(self, bases: tuple[ta.Any, ...]) -> tuple[ta.Any, ...]:
            return (object(),)

    with pytest.raises(TypeError, match='is not a type'):
        try_mro(Bad())


def test_try_mro_remaining_sequences_preserve_exact_original_objects() -> None:
    class X:
        pass

    class Y:
        pass

    class A(X, Y):
        pass

    class B(Y, X):
        pass

    class Expand:
        def __mro_entries__(self, bases: tuple[ta.Any, ...]) -> tuple[type, ...]:
            return (A,)

    ex = Expand()

    with pytest.raises(MroError) as exc_info:
        try_mro(ex, B)

    e = exc_info.value

    assert len(e.remaining_sequences) == 2

    seq0, seq1 = e.remaining_sequences

    assert seq0 == (
        (ex, X),
        (ex, Y),
        (ex, object),
    )
    assert seq1 == (
        (B, Y),
        (B, X),
        (B, object),
    )
