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


def test_mro():
    assert D().f() == 'DBCA'
