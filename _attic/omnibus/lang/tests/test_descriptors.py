import pytest

from .. import descriptors as d_


def test_noinstance():
    class C:

        @d_.nosubclass  # noqa
        @classmethod
        def a(cls):
            return cls

        @d_.noinstance  # noqa
        @classmethod
        def b(cls):  # noqa
            pass

        # Not supported:
        # @classmethod
        # @fns.classmethodonly
        # def c(cls):
        #     pass

        @d_.noinstance
        def f(self):
            pass

        @d_.staticfunction  # noqa
        @staticmethod
        def g():
            pass
        assert g() is None

        @d_.noinstance  # noqa
        @d_.nosubclass  # noqa
        @d_.staticfunction  # noqa
        @staticmethod
        def h():  # noqa
            pass
        assert h() is None

    class D(C):
        pass

    assert C().a() is C
    with pytest.raises(TypeError):
        D().a()

    with pytest.raises(TypeError):
        C().b()

    # with pytest.raises(TypeError):
    #     C().c()
    assert C.f(C()) is None

    with pytest.raises(TypeError):
        C().f()

    assert C.g() is None
    assert C().g() is None

    assert C.h() is None
    with pytest.raises(TypeError):
        C().h()
