def test_super():
    class A:
        def f(self):
            return 'A'

    class B(A):
        def f(self):
            return 'B' + super().f()

    class C(A):
        def f(self):
            return 'C' + super().f()

    class D(B, C):
        def f(self):
            return 'D' + super().f()

    assert D().f() == 'DBCA'


def test_descriptor():
    class Desc:
        def __get__(self, instance, owner=None):
            return self

    class A:
        d = Desc()

    class B(A):
        pass

    class C(A):
        pass

    class D(B, C):
        def f(self):
            sup = super()
            sup.d  # type: ignore  # noqa

    D().f()
