import collections.abc
import typing as ta

from .. import reflect as rfl


def test_reflect_type():
    assert rfl.reflect(int) == int
    assert rfl.reflect(ta.Union[int, float]) == rfl.Union([int, float])
    assert rfl.reflect(ta.Optional[int]) == rfl.Union([int, type(None)])
    assert rfl.reflect(ta.Sequence[int]) == rfl.Generic(collections.abc.Sequence, [int])
    assert rfl.reflect(ta.Mapping[int, str]) == rfl.Generic(collections.abc.Mapping, [int, str])
    assert rfl.reflect(ta.Mapping[int, ta.Optional[str]]) == rfl.Generic(collections.abc.Mapping, [int, rfl.Union([str, type(None)])])  # noqa
    assert rfl.reflect(ta.Mapping[int, ta.Sequence[ta.Optional[str]]]) == rfl.Generic(collections.abc.Mapping, [int, rfl.Generic(collections.abc.Sequence, [rfl.Union([str, type(None)])])])  # noqa
