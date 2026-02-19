import pytest

from .. import check


def test_check():
    with pytest.raises(ValueError):  # noqa
        check.equal(1, 2)


def test_check_not_none():
    assert check.not_none(1) == 1
    with pytest.raises(ValueError) as e:  # noqa
        check.not_none(1 and None)  # noqa
    # print(e.value)


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
