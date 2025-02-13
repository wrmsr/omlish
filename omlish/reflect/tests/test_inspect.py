import typing as ta

import pytest

from ..inspect import get_filtered_type_hints
from . import inttree


def test_filtered():
    def make_int_tree(i: int) -> inttree.IntTree:
        return [i, [i]]

    assert make_int_tree(4) == [4, [4]]

    with pytest.raises(NameError):
        # Tries to lookup 'IntTree' in make_int_tree's namespaces - this module - in which it is not present.
        ta.get_type_hints(make_int_tree)

    assert get_filtered_type_hints(make_int_tree, exclude=['return']) == {'i': int}
