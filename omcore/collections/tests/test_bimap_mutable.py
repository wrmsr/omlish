# ruff: noqa: PT011
import pytest

from ..bimap import MutableBiMap
from ..bimap import make_mutable_bi_map


# init


def test_init_from_mapping():
    bm = make_mutable_bi_map({'a': 1, 'b': 2})
    assert bm['a'] == 1
    assert bm['b'] == 2
    assert len(bm) == 2
    assert set(bm) == {'a', 'b'}


def test_init_from_iterable_of_pairs():
    bm = make_mutable_bi_map([('a', 1), ('b', 2)])
    assert bm['a'] == 1
    assert bm['b'] == 2
    assert len(bm) == 2


def test_init_empty():
    bm: MutableBiMap = make_mutable_bi_map({})
    assert len(bm) == 0
    assert list(bm) == []
    assert len(bm.inverse) == 0


def test_init_value_collision_raises():
    with pytest.raises(ValueError):
        make_mutable_bi_map({'a': 1, 'b': 1})


def test_init_duplicate_key_same_value_in_pairs_is_noop():
    # Re-setting a key to its current value is permitted, so this is fine.
    bm = make_mutable_bi_map([('a', 1), ('a', 1)])
    assert dict(bm.items()) == {'a': 1}


# basic mapping behavior


def test_getitem_missing_raises_keyerror():
    bm = make_mutable_bi_map({'a': 1})
    with pytest.raises(KeyError):
        bm['zzz']


def test_contains_and_get():
    bm = make_mutable_bi_map({'a': 1})
    assert 'a' in bm
    assert 'b' not in bm
    assert bm.get('b') is None
    assert bm.get('b', 'dflt') == 'dflt'


# inverse view


def test_inverse_lookup():
    bm = make_mutable_bi_map({'a': 1, 'b': 2})
    inv = bm.inverse
    assert inv[1] == 'a'
    assert inv[2] == 'b'
    assert len(inv) == 2
    assert set(inv) == {1, 2}


def test_inverse_of_inverse_is_forward():
    bm = make_mutable_bi_map({'a': 1})
    assert bm.inverse.inverse is bm


def test_inverse_is_live_view():
    bm = make_mutable_bi_map({'a': 1})
    inv = bm.inverse
    bm['b'] = 2
    assert inv[2] == 'b'
    del bm['a']
    assert 1 not in inv


# forward __setitem__


def test_set_new_pair_updates_both_sides():
    bm = make_mutable_bi_map({'a': 1})
    bm['b'] = 2
    assert bm['b'] == 2
    assert bm.inverse[2] == 'b'
    assert len(bm) == 2
    assert len(bm.inverse) == 2


def test_set_same_key_same_value_is_noop():
    bm = make_mutable_bi_map({'a': 1, 'b': 2})
    bm['a'] = 1
    assert dict(bm.items()) == {'a': 1, 'b': 2}
    assert dict(bm.inverse.items()) == {1: 'a', 2: 'b'}


def test_set_existing_key_new_value_replaces_and_drops_stale_inverse():
    bm = make_mutable_bi_map({'a': 1, 'b': 2})
    bm['a'] = 3
    assert bm['a'] == 3
    assert bm.inverse[3] == 'a'
    assert 1 not in bm.inverse  # old inverse entry must be gone
    assert len(bm) == len(bm.inverse) == 2


def test_set_value_owned_by_other_key_raises_valueerror():
    bm = make_mutable_bi_map({'a': 1, 'b': 2})
    with pytest.raises(ValueError) as ei:
        bm['a'] = 2
    assert ei.value.args == (2,)


def test_set_new_key_to_existing_value_raises_valueerror():
    bm = make_mutable_bi_map({'a': 1})
    with pytest.raises(ValueError):
        bm['c'] = 1


def test_failed_set_leaves_state_unchanged():
    bm = make_mutable_bi_map({'a': 1, 'b': 2})
    with pytest.raises(ValueError):
        bm['a'] = 2
    # Neither side may be mutated by a rejected set.
    assert dict(bm.items()) == {'a': 1, 'b': 2}
    assert dict(bm.inverse.items()) == {1: 'a', 2: 'b'}


def test_explicit_delete_then_reassign_value():
    # The intended workflow: delete the owning pair, then the value is free.
    bm = make_mutable_bi_map({'a': 1, 'b': 2})
    with pytest.raises(ValueError):
        bm['a'] = 2
    del bm['b']
    bm['a'] = 2
    assert dict(bm.items()) == {'a': 2}
    assert dict(bm.inverse.items()) == {2: 'a'}


# forward __delitem__


def test_delete_removes_both_sides():
    bm = make_mutable_bi_map({'a': 1, 'b': 2})
    del bm['a']
    assert 'a' not in bm
    assert 1 not in bm.inverse
    assert len(bm) == len(bm.inverse) == 1


def test_delete_missing_key_raises_keyerror():
    bm = make_mutable_bi_map({'a': 1})
    with pytest.raises(KeyError):
        del bm['zzz']
    assert dict(bm.items()) == {'a': 1}


# inverse __setitem__


def test_inverse_set_new_pair_updates_both_sides():
    bm = make_mutable_bi_map({'a': 1})
    inv = bm.inverse
    inv[2] = 'b'
    assert bm['b'] == 2
    assert inv[2] == 'b'
    assert len(bm) == len(inv) == 2


def test_inverse_reassign_own_key_replaces():
    # inv's keys are values of the forward map; reassigning one is normal MutableMapping replacement, and the old
    # forward key must be dropped.
    bm = make_mutable_bi_map({'a': 1, 'b': 2})
    inv = bm.inverse
    inv[1] = 'c'
    assert inv[1] == 'c'
    assert bm['c'] == 1
    assert 'a' not in bm  # 1's old owner is gone
    assert len(bm) == len(inv) == 2


def test_inverse_set_colliding_forward_key_raises_valueerror():
    # 'a' already exists as a forward key mapped to a different value.
    bm = make_mutable_bi_map({'a': 1, 'b': 2})
    inv = bm.inverse
    with pytest.raises(ValueError):
        inv[3] = 'a'


def test_inverse_set_same_pair_is_noop():
    bm = make_mutable_bi_map({'a': 1, 'b': 2})
    inv = bm.inverse
    inv[1] = 'a'
    assert dict(bm.items()) == {'a': 1, 'b': 2}
    assert dict(inv.items()) == {1: 'a', 2: 'b'}


def test_inverse_failed_set_leaves_state_unchanged():
    bm = make_mutable_bi_map({'a': 1, 'b': 2})
    inv = bm.inverse
    with pytest.raises(ValueError):
        inv[3] = 'a'
    assert dict(bm.items()) == {'a': 1, 'b': 2}
    assert dict(inv.items()) == {1: 'a', 2: 'b'}


# inverse __delitem__


def test_inverse_delete_removes_both_sides():
    bm = make_mutable_bi_map({'a': 1, 'b': 2})
    inv = bm.inverse
    del inv[1]
    assert 1 not in inv
    assert 'a' not in bm
    assert len(bm) == len(inv) == 1


def test_inverse_delete_missing_key_raises_keyerror():
    bm = make_mutable_bi_map({'a': 1})
    with pytest.raises(KeyError):
        del bm.inverse[99]


# MutableMapping mixin methods (exercise the fixed primitives indirectly)


def test_pop():
    bm = make_mutable_bi_map({'a': 1, 'b': 2})
    assert bm.pop('a') == 1
    assert 1 not in bm.inverse
    assert bm.pop('zzz', 'dflt') == 'dflt'


def test_clear():
    bm = make_mutable_bi_map({'a': 1, 'b': 2})
    bm.clear()
    assert len(bm) == 0
    assert len(bm.inverse) == 0


def test_setdefault():
    bm = make_mutable_bi_map({'a': 1})
    assert bm.setdefault('a', 99) == 1
    assert bm.setdefault('b', 2) == 2
    assert bm.inverse[2] == 'b'


def test_setdefault_colliding_value_raises():
    bm = make_mutable_bi_map({'a': 1})
    with pytest.raises(ValueError):
        bm.setdefault('b', 1)


def test_update_with_disjoint_values():
    bm = make_mutable_bi_map({'a': 1})
    bm.update({'b': 2, 'c': 3})
    assert dict(bm.items()) == {'a': 1, 'b': 2, 'c': 3}
    assert dict(bm.inverse.items()) == {1: 'a', 2: 'b', 3: 'c'}


def test_update_with_colliding_value_raises():
    bm = make_mutable_bi_map({'a': 1, 'b': 2})
    with pytest.raises(ValueError):
        bm.update({'c': 2})


# invariants


def test_sides_always_consistent_after_mixed_operations():
    bm = make_mutable_bi_map({'a': 1, 'b': 2, 'c': 3})
    inv = bm.inverse

    bm['a'] = 4
    del bm['b']
    inv[3] = 'z'
    inv[5] = 'w'
    with pytest.raises(ValueError):
        bm['w'] = 4
    with pytest.raises(ValueError):
        inv[9] = 'z'

    fwd_items = dict(bm.items())
    inv_items = dict(inv.items())
    assert fwd_items == {'a': 4, 'z': 3, 'w': 5}
    assert inv_items == {v: k for k, v in fwd_items.items()}
    assert len(bm) == len(inv)


# atomic update: all-or-nothing


def test_update_failure_applies_nothing_even_if_earlier_pairs_were_valid():
    bm = make_mutable_bi_map({'a': 1, 'b': 2})
    # ('x', 9) is perfectly valid on its own; ('c', 2) collides with untouched 'b'.
    with pytest.raises(ValueError) as ei:
        bm.update([('x', 9), ('c', 2)])
    assert ei.value.args == (2,)
    assert dict(bm.items()) == {'a': 1, 'b': 2}
    assert dict(bm.inverse.items()) == {1: 'a', 2: 'b'}
    assert 'x' not in bm  # the valid pair must not have landed


def test_update_failure_touches_neither_side():
    bm = make_mutable_bi_map({'a': 1, 'b': 2, 'c': 3})
    with pytest.raises(ValueError):
        bm.update({'a': 10, 'z': 3})  # 3 owned by untouched 'c'
    assert dict(bm.items()) == {'a': 1, 'b': 2, 'c': 3}
    assert dict(bm.inverse.items()) == {1: 'a', 2: 'b', 3: 'c'}


# atomic update: swaps and rotations


def test_update_value_swap_succeeds():
    bm = make_mutable_bi_map({'a': 1, 'b': 2})
    bm.update({'a': 2, 'b': 1})
    assert dict(bm.items()) == {'a': 2, 'b': 1}
    assert dict(bm.inverse.items()) == {2: 'a', 1: 'b'}


def test_update_value_rotation_succeeds():
    bm = make_mutable_bi_map({'a': 1, 'b': 2, 'c': 3})
    bm.update({'a': 2, 'b': 3, 'c': 1})
    assert dict(bm.items()) == {'a': 2, 'b': 3, 'c': 1}
    assert dict(bm.inverse.items()) == {2: 'a', 3: 'b', 1: 'c'}


def test_update_value_freed_within_batch_is_reusable():
    # 'a' releases 1 in the same batch that 'c' claims it.
    bm = make_mutable_bi_map({'a': 1, 'b': 2})
    bm.update({'a': 5, 'c': 1})
    assert dict(bm.items()) == {'a': 5, 'b': 2, 'c': 1}
    assert dict(bm.inverse.items()) == {5: 'a', 2: 'b', 1: 'c'}


# atomic update: intra-batch collisions


def test_update_duplicate_values_within_batch_raise():
    bm = make_mutable_bi_map({'a': 1})
    with pytest.raises(ValueError) as ei:
        bm.update({'x': 9, 'y': 9})
    assert ei.value.args == (9,)
    assert dict(bm.items()) == {'a': 1}


def test_update_iterable_duplicate_keys_last_wins():
    # dict.update semantics: same key repeated in a pair iterable collapses,
    # so this is x -> 2, not a 1-vs-2 collision.
    bm: MutableBiMap = make_mutable_bi_map({})
    bm.update([('x', 1), ('x', 2)])
    assert dict(bm.items()) == {'x': 2}
    assert dict(bm.inverse.items()) == {2: 'x'}


# atomic update: signature and trivia


def test_update_with_kwargs():
    bm = make_mutable_bi_map({'a': 1})
    bm.update(b=2, c=3)
    assert dict(bm.items()) == {'a': 1, 'b': 2, 'c': 3}
    assert dict(bm.inverse.items()) == {1: 'a', 2: 'b', 3: 'c'}


def test_update_positional_and_kwargs_kwargs_win():
    bm: MutableBiMap = make_mutable_bi_map({})
    bm.update({'a': 1}, a=2)
    assert dict(bm.items()) == {'a': 2}
    assert dict(bm.inverse.items()) == {2: 'a'}


def test_update_empty_is_noop():
    bm = make_mutable_bi_map({'a': 1})
    bm.update({})
    bm.update([])
    bm.update()
    assert dict(bm.items()) == {'a': 1}
    assert dict(bm.inverse.items()) == {1: 'a'}


def test_update_resetting_key_to_current_value_is_noop_within_batch():
    bm = make_mutable_bi_map({'a': 1, 'b': 2})
    bm.update({'a': 1, 'c': 3})
    assert dict(bm.items()) == {'a': 1, 'b': 2, 'c': 3}
    assert dict(bm.inverse.items()) == {1: 'a', 2: 'b', 3: 'c'}


# atomic update on the inverse view (inherited from the base class)


def test_inverse_update_swap_succeeds():
    bm = make_mutable_bi_map({'a': 1, 'b': 2})
    inv = bm.inverse
    inv.update({1: 'b', 2: 'a'})
    assert dict(inv.items()) == {1: 'b', 2: 'a'}
    assert dict(bm.items()) == {'b': 1, 'a': 2}


def test_inverse_update_collision_raises_and_applies_nothing():
    bm = make_mutable_bi_map({'a': 1, 'b': 2})
    inv = bm.inverse
    # 'b' is owned by untouched inverse key 2 -> collision on the inverse's
    # value side (a forward key).
    with pytest.raises(ValueError) as ei:
        inv.update({3: 'c', 1: 'b'})
    assert ei.value.args == ('b',)
    assert dict(bm.items()) == {'a': 1, 'b': 2}
    assert dict(inv.items()) == {1: 'a', 2: 'b'}


def test_inverse_update_keeps_views_mirrored():
    bm = make_mutable_bi_map({'a': 1, 'b': 2, 'c': 3})
    inv = bm.inverse
    inv.update({1: 'x', 4: 'd'})
    fwd_items = dict(bm.items())
    assert fwd_items == {'x': 1, 'b': 2, 'c': 3, 'd': 4}
    assert dict(inv.items()) == {v: k for k, v in fwd_items.items()}
    assert len(bm) == len(inv)
