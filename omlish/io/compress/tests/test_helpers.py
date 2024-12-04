from .helpers import buffer_generator_writer


def test_bgw():
    def f():
        for _ in range(3):
            s = yield
            yield s + '?'
            yield s + '!'

    g = f()
    for s in 'abc':
        next(g)
        print(g.send(s))
        print(next(g))
