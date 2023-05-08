import dataclasses as dc
import threading
import typing as ta

import pytest

from .. import bind as bind_
from .. import inject as inject_
from .. import scopes as scopes_
from .. import types as types_


def test_base():
    binder = bind_.create_binder()

    class C:
        def __init__(self, x: int) -> None:
            super().__init__()
            self.x = x

    class D(C):
        pass

    # binder.bind_callable(lambda: 420, key=Key(int))
    binder.bind(int, to_instance=420)

    # binder.bind_callable(lambda x: D(x), key=Key(D), kwargs={'x': Key(int)}, in_=EagerSingletonScope)
    binder.bind(D, as_eager_singleton=True)

    # injector.install(lambda x: C(x), kwargs={'x': Key(int)}, key=Key(C))

    class E:
        pass

    class F(E):
        pass

    class G(E):
        pass

    binder.bind(G)
    binder.bind(F, to=G)

    injector = inject_.create_injector(binder, config=inject_.InjectorConfig(enable_jit_bindings=True))

    c = injector.get(types_.Key(C))
    assert isinstance(c, C)
    assert c.x == 420
    assert injector.get(types_.Key(C)) is not c

    d = injector.get(types_.Key(D))
    assert isinstance(d, D)
    assert d.x == 420
    assert injector.get(types_.Key(D)) is d

    f = injector.get(F)
    assert isinstance(f, G)


def test_annotation():
    @bind_.annotate('title', name='name')
    def make_title(name: str) -> str:
        return name + ' title'

    binder = bind_.create_binder()
    binder.bind('some name', annotated_with='name')
    binder.bind_callable(make_title)

    injector = inject_.create_injector(binder)

    name = injector.get(types_.Key(str, 'name'))
    assert name == 'some name'

    title = injector.get(types_.Key(str, 'title'))
    assert title == 'some name title'


def test_provider():
    binder = bind_.create_binder()

    binder.bind(5)
    binder.bind(object, to_provider=int)

    injector = inject_.create_injector(binder)

    assert injector.get(object) == 5


def test_default():
    @bind_.annotate('title', name='name')
    def make_title(name: str = 'default name') -> str:
        return name + ' title'

    binder = bind_.create_binder()
    binder.bind_callable(make_title)

    injector = inject_.create_injector(binder)

    title = injector.get(types_.Key(str, 'title'))
    assert title == 'default name title'


def test_set():
    binder = bind_.create_binder()
    binder.new_set_binder(int).bind(to_instance=4)
    binder.new_set_binder(int).bind(to_instance=5)

    injector = inject_.create_injector(binder)

    s = injector.get(ta.AbstractSet[int])
    assert s == {4, 5}


def test_dict():
    binder = bind_.create_binder()
    binder.new_dict_binder(int, str).bind(4, to_instance='four')
    binder.new_dict_binder(int, str).bind(5, to_instance='five')

    injector = inject_.create_injector(binder)

    s = injector.get(ta.Mapping[int, str])
    assert s == {4: 'four', 5: 'five'}


def test_child():
    binder = bind_.create_binder()
    binder.bind(420)

    injector = inject_.create_injector(binder)
    child_injector = injector.create_child()

    assert injector.get(int) == 420
    assert child_injector.get(int) == 420


def test_child2():
    binder = bind_.create_binder()

    injector = inject_.create_injector(binder, config=types_.InjectorConfig(enable_jit_bindings=True))
    child_injector = injector.create_child()

    assert child_injector.get(int) == 0
    with pytest.raises(types_.InjectionBlacklistedKeyError):
        injector.get(int)


def test_private():
    class A:
        pass

    class B:
        pass

    class C(B):
        def __init__(self, a: A) -> None:
            self.a = a

    class D:
        def __init__(self, b: B) -> None:
            self.b = b

    private_binder = bind_.create_private_binder()
    private_binder.bind(A)
    private_binder.bind(C)  # diff
    private_binder.bind(B, to=C)
    private_binder.expose(B)

    binder = bind_.create_binder()
    binder.bind(D)

    injector = inject_.create_injector(private_binder, binder)
    d = injector.get(D)
    assert isinstance(d, D)
    assert isinstance(d.b, C)
    assert isinstance(d.b.a, A)

    with pytest.raises(types_.InjectionBlacklistedKeyError):
        injector.get(A)

    with pytest.raises(types_.InjectionBlacklistedKeyError):
        injector.get(C)


def test_nested_private():
    binder0 = bind_.create_binder()
    binder0.new_set_binder(int).bind(to_instance=-1)
    binder0.new_set_binder(int).bind(to_instance=0)
    injector0 = inject_.create_injector(binder0)

    binder1 = bind_.create_binder()
    binder1.new_set_binder(int).bind(to_instance=1)
    injector1 = injector0.create_child(binder1)

    binder2 = bind_.create_binder()
    binder2.new_set_binder(int).bind(to_instance=2)
    injector2 = injector0.create_child(binder2)

    print(injector0.get(ta.AbstractSet[int]))
    print(injector0.get(ta.AbstractSet[int]))

    # FIXME: SetProvider.__call__ -> get_bindings parent=True?
    print(injector1.get(ta.AbstractSet[int]))
    print(injector2.get(ta.AbstractSet[int]))


def test_dataclasses():
    @dc.dataclass()
    class C:
        x: int

    binder = bind_.create_binder()
    binder.bind(420)
    binder.bind(C)

    injector = inject_.create_injector(binder)
    c = injector.get(C)
    assert isinstance(c, C)
    assert c.x == 420


def test_scopes0():
    def next_seq() -> int:
        nonlocal seq
        seq += 1
        return seq
    seq = 0

    binder = bind_.create_binder()
    binder.bind_callable(next_seq)

    injector = inject_.create_injector(binder)
    assert injector[int] == 1
    assert injector[int] == 2


def test_scopes1():
    def next_seq() -> int:
        nonlocal seq
        seq += 1
        return seq
    seq = 0

    binder = bind_.create_binder()
    binder.bind_callable(next_seq, in_=scopes_.ThreadScope)

    class Thing:
        pass

    thing = Thing()
    binder.bind(thing)

    injector = inject_.create_injector(binder)
    assert injector[int] == 1
    assert injector[int] == 1
    assert injector[Thing] is thing

    def proc(n):
        assert injector[int] == n
        assert injector[int] == n
        assert injector[Thing] is thing

    for i in range(2, 4):
        t = threading.Thread(target=lambda: proc(i))
        t.start()
        t.join()


def test_scopes2():
    def next_seq() -> int:
        nonlocal seq
        seq += 1
        return seq
    seq = 0

    binder = bind_.create_binder()
    binder.bind_callable(next_seq, in_=scopes_.ThreadScope)

    class StaticThing:

        def __init__(self) -> None:
            super().__init__()

    binder.bind(StaticThing, as_singleton=True)

    @dc.dataclass(frozen=True)
    class Thing:
        i: int
        st: StaticThing

    binder.bind(Thing)

    injector = inject_.create_injector(binder)
    assert injector[int] == 1
    assert injector[int] == 1

    ts = []

    def proc(n):
        assert injector[int] == n
        assert injector[int] == n
        t0 = injector[Thing]
        t1 = injector[Thing]
        ts.append(t0)
        ts.append(t1)
        assert t0.i == n
        assert t1 == t0
        assert t1 is not t0

    for i in range(2, 4):
        t = threading.Thread(target=lambda: proc(i))
        t.start()
        t.join()

    t = injector[Thing]
    ts.append(t)
    assert t.i == 1

    assert len({id(t.st) for t in ts}) == 1


def test_assist():
    def f(x: int, y: int) -> int:
        return x + y

    binder = bind_.create_binder()
    binder.bind(420)
    binder.bind_callable(f, annotated_with='out', assists={'y'})

    injector = inject_.create_injector(binder)

    af = injector[types_.Key(ta.Callable[..., int], 'out')]

    with types_.Injector._CURRENT(injector):  # FIXME
        assert af(y=1) == 421


def test_reject_opaque():
    binder = bind_.create_binder()

    def bad(x: int, y) -> str:
        return x + y

    binder.bind(420)
    with pytest.raises(types_.InjectionOpaqueError):
        binder.bind_callable(bad)


def test_optional():
    def f(x: int = None) -> str:
        return f'f({x})'

    binder = bind_.create_binder()
    binder.bind_callable(f)
    injector = inject_.create_injector(binder)
    assert injector[str] == 'f(None)'

    binder = bind_.create_binder()
    binder.bind(5)
    binder.bind_callable(f)
    injector = inject_.create_injector(binder)
    assert injector[str] == 'f(5)'


@dc.dataclass()
class CycA:
    b: 'CycB'


@dc.dataclass()
class CycB:
    a: CycA


def test_cyclic_exc():
    binder = bind_.create_binder()
    binder.bind_class(CycA, as_singleton=True)
    binder.bind_class(CycB, as_singleton=True)
    injector = inject_.create_injector(binder)
    with pytest.raises(inject_.InjectionRecursionException):
        a = injector[CycA]  # noqa
        b = injector[CycB]  # noqa


def test_cyclic_prox():
    binder = bind_.create_binder()
    binder.bind_class(CycA, as_singleton=True)
    binder.bind_class(CycB, as_singleton=True)
    injector = inject_.create_injector(binder, config=inject_.InjectorConfig(enable_cyclic_proxies=True))
    a = injector[CycA]
    b = injector[CycB]
    a.x = 5
    b.y = 10
    assert a.b is b
    assert b.a is not a
    assert b.a.b is b
    assert a.b.a is not a
    assert a.b.y == 10
    assert b.a.x == 5
