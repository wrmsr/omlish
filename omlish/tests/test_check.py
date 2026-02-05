import pytest

from .. import check


def test_check():
    with pytest.raises(ValueError):  # noqa
        check.equal(1, 2)


class A:
    def __init_subclass__(cls, **kwargs):
        check.not_issubclass_except_nameerror(cls, lambda: B)


class B:
    def __init_subclass__(cls, **kwargs):
        check.not_issubclass(cls, A)


def test_check_except_nameerror():
    class GoodA(A):
        pass

    class GoodB(B):
        pass

    with pytest.raises(TypeError):  # noqa
        class BadAB(A, B):
            pass
