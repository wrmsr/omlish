from ... import inject as inj
from ... import lang


def test_provision_listener():
    ks = []

    def pl(injector, key, binding, fn):
        ks.append(key)
        v = fn()
        if isinstance(v, int):
            return v + 1
        if isinstance(v, str):
            return v + '!'
        return v

    i = inj.create_injector(
        inj.bind(420),
        inj.bind(lang.typed_lambda(str, i=int)(lambda i: str(i))),
        inj.bind_provision_listener(pl),
    )

    assert i.provide(int) == 421
    assert i.provide(str) == '421!'
    assert ks == list(map(inj.as_key, [int, str, int]))
