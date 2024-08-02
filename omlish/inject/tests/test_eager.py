from ... import inject as inj


def test_eager():
    c = 0

    def f() -> int:
        nonlocal c
        c += 1
        return 420

    es = inj.as_elements(
        inj.bind(f, eager=True),
    )

    for _ in range(2):
        c = 0
        i = inj.create_injector(es)
        assert c == 1
        assert i.provide(int) == 420
        assert c == 2
