import pytest

from ..intersections import Intersection


class A:
    def a(self):
        pass


class B:
    def b(self):
        pass


class C:
    def c(self):
        pass


class ABIntersection(A, B, Intersection):
    pass


def test_intersections():
    class _AB(A, B):
        pass

    assert isinstance(_AB(), ABIntersection)
    assert issubclass(_AB, ABIntersection)

    class _BA(B, A):
        pass

    assert isinstance(_BA(), ABIntersection)
    assert issubclass(_BA, ABIntersection)

    class _ABC(A, B, C):
        pass

    assert isinstance(_ABC(), ABIntersection)
    assert issubclass(_ABC, ABIntersection)

    class _AC(A, C):
        pass

    assert not isinstance(_AC(), ABIntersection)
    assert not issubclass(_AC, ABIntersection)


def test_nested_intersections():
    class ABCIntersection(ABIntersection, C, Intersection):
        pass

    assert ABCIntersection.__intersection_bases__ == (A, B, C)

    class ABAIntersection(ABIntersection, A, Intersection):
        pass

    assert ABAIntersection.__intersection_bases__ == (A, B)

    class _ABC(A, B, C):
        pass

    assert isinstance(_ABC(), ABCIntersection)
    assert issubclass(_ABC, ABCIntersection)

    class _AB(A, B):
        pass

    assert not isinstance(_AB(), ABCIntersection)
    assert not issubclass(_AB, ABCIntersection)


def test_bare_intersection():
    # Checks against Intersection itself are nominal - 'is this an intersection class' - like ta.Protocol.
    assert issubclass(ABIntersection, Intersection)
    assert not issubclass(A, Intersection)
    assert not issubclass(int, Intersection)

    class Sub(ABIntersection):
        pass

    assert issubclass(Sub, Intersection)

    with pytest.raises(TypeError):
        isinstance(object(), Intersection)
