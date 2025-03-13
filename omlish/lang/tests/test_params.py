import inspect

from ..params import ParamSpec


def test_params() -> None:
    def foo(a, b, *c, **kw):
        pass

    ps = ParamSpec.of_signature(inspect.signature(foo))
    print(ps)
    print(ps.with_seps)
