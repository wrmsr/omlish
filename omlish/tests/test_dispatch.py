from .. import dispatch


def test_dispatch():
    @dispatch.function
    def f(x: object):
        return 'object'


