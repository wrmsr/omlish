from ... import inject as inj
from ... import lang


def test_override():
    es = inj.as_elements(
        inj.override(
            inj.bind(421),
            inj.bind(420),
        ),
        inj.bind(5.2),
        inj.bind(lang.typed_lambda(str, i=int, f=float)(lambda i, f: f'{i}, {f}')),
    )

    i = inj.create_injector(es)
    assert i.provide(int) == 421
    assert i.provide(str) == '421, 5.2'
