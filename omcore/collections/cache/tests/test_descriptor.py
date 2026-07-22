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
        def __init__(self) -> None:
            self.hits: list = []

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


def test_descriptor_instance_honors_kwargs():
    calls = []

    class C:
        @desc_.cache(scope='instance', max_size=1)
        def f(self, x):
            calls.append(x)
            return x + 1

    c = C()

    assert c.f(1) == 2
    assert c.f(2) == 3
    assert c.f(1) == 2

    # With max_size=1, f(2) evicted f(1)'s entry, so the second f(1) recomputes.
    assert calls == [1, 2, 1]


def test_descriptor_class_scope():
    class C:
        def __init__(self) -> None:
            self.calls: list = []

        @desc_.cache(scope='class')
        def f(self, x):
            self.calls.append(x)
            return (id(self), x + 1)

    c0 = C()
    c1 = C()

    assert c0.f(1) == (id(c0), 2)
    assert c1.f(1) == (id(c1), 2)

    assert c0.f(1) == (id(c0), 2)
    assert c1.f(1) == (id(c1), 2)

    assert c0.calls == [1]
    assert c1.calls == [1]


def test_descriptor_static_on_method_shares_across_instances():
    calls = []

    class C:
        @desc_.cache(scope='static')
        def f(self, x):
            calls.append(x)
            return x + 1

    c0 = C()
    c1 = C()

    assert c0.f(1) == 2
    assert c1.f(1) == 2
    assert calls == [1]

    # The built wrapper is cached on the instance rather than rebuilt per attribute fetch.
    assert c0.f is c0.f


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
