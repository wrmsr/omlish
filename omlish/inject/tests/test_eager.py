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


def test_eager_priorities():
    l: list = []

    def i() -> int:
        l.append(i)
        return 420

    def s() -> str:
        l.append(s)
        return 'four twenty'

    def f() -> float:
        l.append(f)
        return 4.2

    def run(*fps):
        es = inj.as_elements(*[
            inj.bind(fn, eager=p)
            for fn, p in fps
        ])

        for _ in range(2):
            l.clear()
            inj.create_injector(es)
            assert l == [fn for fn, _ in sorted(fps, key=lambda fp: fp[1])]

    run((i, -1), (s, 0), (f, 1))
    run((i, 1), (s, -1), (f, 0))
