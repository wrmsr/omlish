import typing as ta

import pytest

from .. import check


def test_check():
    with pytest.raises(ValueError):  # noqa
        check.equal(1, 2)


def test_cext():
    assert check.check._unpack_isinstance_spec(int) == int  # noqa
    assert check.check._unpack_isinstance_spec((int, str)) == (int, str)  # noqa
    assert check.check._unpack_isinstance_spec((int, str, None)) == (int, str, type(None))  # noqa
    assert check.check._unpack_isinstance_spec((int, str, None, ta.Any)) == object  # noqa

    assert check.not_none(1) == 1
    with pytest.raises(ValueError) as e:  # noqa
        check.not_none(1 and None)  # noqa
    check.state(True)
    check.arg(True)

    check.equal(420, 420)
    check.not_equal(420, 421)

    check.isinstance(420, int)
    check.not_isinstance(420, str)
    check.isinstance(420, (int, str))
    with pytest.raises(TypeError) as e:  # noqa
        check.isinstance(420, str)  # noqa
    check.isinstance(420, ta.Any)  # noqa
    check.isinstance(None, None)  # noqa
    check.isinstance(None, (int, None))  # noqa
    check.isinstance(420, (int, None))  # noqa
    with pytest.raises(TypeError) as e:  # noqa
        check.isinstance(420, (str, None))  # noqa

    check.issubclass(bool, int)
    check.not_issubclass(bool, str)
    with pytest.raises(TypeError) as e:  # noqa
        check.issubclass(bool, str)


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
