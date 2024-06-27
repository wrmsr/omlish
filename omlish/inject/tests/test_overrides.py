from ... import inject as inj
from ... import lang


def test_override():
    es = inj.as_elements(
        inj.override(
            inj.as_binding(421),
            inj.as_binding(420),
        ),
        inj.as_binding(5.2),
        inj.as_binding(lang.typed_lambda(str, i=int, f=float)(lambda i, f: f'{i}, {f}')),
    )

    i = inj.create_injector(es)
    assert i.provide(int) == 421
    assert i.provide(str) == '421, 5.2'
