from .. import descriptor as desc_


def test_descriptor_static():
    hits = []

    @desc_.cache()
    def f(x):
        hits.append(x)
        return x + 1

    assert f(0) == 1
    assert hits == [0]
    assert f(0) == 1
    assert hits == [0]
    assert f(1) == 2
    assert hits == [0, 1]


def test_descriptor_instance():
    class C:
        def __init__(self):
            self.hits = []

        @desc_.cache()
        def f(self, x):
            self.hits.append(x)
            return x + 1

    c0 = C()
    c1 = C()

    assert c0.f(0) == 1
    assert c0.hits == [0]
    assert c0.f(0) == 1
    assert c0.hits == [0]
    assert c0.f(1) == 2
    assert c0.hits == [0, 1]
    assert c1.hits == []


def test_func():
    nc = 0

    @desc_.cache()
    def foo(x):
        nonlocal nc
        nc += 1
        return x + 1

    assert nc == 0
    assert foo(0) == 1
    assert nc == 1
    assert foo(0) == 1
    assert nc == 1
    assert foo(1) == 2
    assert nc == 2
    assert foo(0) == 1
    assert nc == 2
