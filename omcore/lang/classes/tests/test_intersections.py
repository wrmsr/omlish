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
