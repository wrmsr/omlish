# ruff: noqa: F821 PLC0132 SLF001
import typing as ta

import pytest

from .._mirror import MirrorImpl
from ..core import types
from ..core.strconv import type_str
from ..core.subtypes import is_same_type
from ..core.subtypes import is_subtype
from ..core.typeops import get_proper_type
from ..errors import FrozenMirrorReflectionError
from ..errors import ReflectionValueError


def make_root_mirror() -> MirrorImpl:
    mirror = MirrorImpl()
    mirror._internal.freeze()
    return mirror


def test_parent_must_be_frozen() -> None:
    unfrozen = MirrorImpl()

    with pytest.raises(ReflectionValueError):
        MirrorImpl(_parent_state=unfrozen._internal._state)


def test_freeze_is_idempotent() -> None:
    mirror = MirrorImpl()
    assert not mirror._internal._state.is_frozen

    mirror._internal.freeze()
    assert mirror._internal._state.is_frozen


def test_frozen_mirror_reflects_known_compositions_statelessly() -> None:
    root = make_root_mirror()

    typ = root.reflect_type(int)
    assert isinstance(typ, types.Instance)
    assert typ.type.fullname == 'builtins.int'

    composed = root.reflect_type(dict[str, list[int] | None])
    assert type_str(composed) == 'builtins.dict[builtins.str, Union[builtins.list[builtins.int], None]]'

    # The composition was not memoized - the frozen mirror accreted no state.
    assert root.reflect_type(dict[str, list[int] | None]) is not composed
    assert is_same_type(root.reflect_type(dict[str, list[int] | None]), composed)


def test_frozen_mirror_rejects_new_types() -> None:
    root = make_root_mirror()

    class Local:
        pass

    with pytest.raises(FrozenMirrorReflectionError):
        root.reflect_type(Local)

    with pytest.raises(FrozenMirrorReflectionError):
        root.get_type_info(Local)


def test_child_shares_parent_known_infos() -> None:
    root = make_root_mirror()
    child = MirrorImpl(_parent_state=root._internal._state)

    assert child.get_type_info(int) is root.get_type_info(int)

    typ = child.reflect_type(list[int])
    assert isinstance(typ, types.Instance)
    assert typ.type is root.get_type_info(list)


def test_siblings_sharing_a_root_mingle_known_types() -> None:
    root = make_root_mirror()
    left = MirrorImpl(_parent_state=root._internal._state)
    right = MirrorImpl(_parent_state=root._internal._state)

    assert is_same_type(left.reflect_type(list[int]), right.reflect_type(list[int]))
    assert is_subtype(
        left.reflect_type(list[int]),
        right.reflect_type(ta.Sequence[int]),  # noqa
    )


def test_parentless_mirrors_do_not_mingle_known_types() -> None:
    left = MirrorImpl()
    right = MirrorImpl()

    assert not is_same_type(left.reflect_type(list[int]), right.reflect_type(list[int]))


def test_child_state_stays_out_of_parent() -> None:
    root = make_root_mirror()
    child = MirrorImpl(_parent_state=root._internal._state)

    parent_infos = dict(root._internal._state._MirrorState__infos_by_fullname)  # type: ignore[attr-defined]
    parent_cache = dict(root._internal._state._MirrorState__type_cache)  # type: ignore[attr-defined]

    class Local:
        pass

    typ = child.reflect_type(Local)
    assert isinstance(typ, types.Instance)

    assert root._internal._state._MirrorState__infos_by_fullname == parent_infos  # type: ignore[attr-defined]
    assert root._internal._state._MirrorState__type_cache == parent_cache  # type: ignore[attr-defined]
    assert typ.type is child._internal._state.get_info(typ.type.fullname)


def test_sibling_dynamic_types_stay_distinct() -> None:
    root = make_root_mirror()
    left = MirrorImpl(_parent_state=root._internal._state)
    right = MirrorImpl(_parent_state=root._internal._state)

    class Local:
        pass

    left_typ = left.reflect_type(Local)
    right_typ = right.reflect_type(Local)

    assert isinstance(left_typ, types.Instance)
    assert isinstance(right_typ, types.Instance)
    assert left_typ.type is not right_typ.type
    assert not is_same_type(left_typ, right_typ)


def test_child_of_frozen_child_layers() -> None:
    root = make_root_mirror()

    middle = MirrorImpl(_parent_state=root._internal._state)

    class AppThing:
        pass

    middle_typ = middle.reflect_type(AppThing)
    assert isinstance(middle_typ, types.Instance)
    middle._internal.freeze()

    tip = MirrorImpl(_parent_state=middle._internal._state)

    assert tip.get_type_info(AppThing) is middle_typ.type
    assert tip.get_type_info(int) is root.get_type_info(int)

    class TipThing(AppThing):
        pass

    tip_typ = tip.reflect_type(TipThing)
    assert isinstance(tip_typ, types.Instance)
    assert tip_typ.type.mro[1] is middle_typ.type


def test_freeze_prepares_held_infos() -> None:
    mirror = MirrorImpl()

    t_var = ta.TypeVar('T')  # type: ignore

    class Box(ta.Generic[t_var]):  # type: ignore
        pass

    # get_type_info alone leaves the info unprepared (no type vars reflected yet).
    info = mirror.get_type_info(Box)
    assert info.type_vars == ()

    mirror._internal.freeze()

    assert [type_var.name for type_var in info.type_vars] == ['T']  # type: ignore[var-annotated]
    assert mirror._internal._state.is_info_prepared(Box)

    # A child can subscript it without preparing (mutating) the frozen parent's info.
    child = MirrorImpl(_parent_state=mirror._internal._state)
    typ = child.reflect_type(Box[int])  # type: ignore
    assert isinstance(typ, types.Instance)
    assert typ.type is info


def test_freeze_heals_unresolved_aliases() -> None:
    calls: list[str] = []

    def resolver(frr):
        calls.append(frr.name)
        if len(calls) == 1:
            raise RuntimeError('transient resolution failure')
        return int

    mirror = MirrorImpl(forward_ref_resolver=resolver)
    alias = ta.TypeAliasType('Alias', 'User')  # type: ignore

    with pytest.raises(RuntimeError):
        mirror.reflect_type(alias)

    mirror._internal.freeze()

    assert calls == ['User', 'User']

    typ = mirror.reflect_type(alias)
    assert isinstance(typ, types.TypeAliasType)
    assert type_str(get_proper_type(typ)) == 'builtins.int'


def test_compact() -> None:
    root_mirror = make_root_mirror()
    root_mirror.reflect_type(int)

    class A:
        pass

    a_mirror = MirrorImpl(_parent_state=root_mirror._internal._state)
    a_mirror.reflect_type(int)
    a_mirror.reflect_type(A)

    a_mirror._internal.freeze()

    class B:
        pass

    b_mirror = MirrorImpl(_parent_state=a_mirror._internal._state)
    b_mirror.reflect_type(int)
    b_mirror.reflect_type(A)
    b_mirror.reflect_type(B)

    b_mirror._internal._state.compact()
    b_mirror._internal.freeze()
    b_mirror.reflect_type(int)
    b_mirror.reflect_type(A)
    b_mirror.reflect_type(B)

    class C:
        pass

    with pytest.raises(FrozenMirrorReflectionError):
        b_mirror.reflect_type(C)
