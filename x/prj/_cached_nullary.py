import functools


class cached_nullary:
    def __init__(self, fn):
        self._fn = fn
        self._value = self._missing = object()
        functools.update_wrapper(self, fn)
    def __call__(self, *args, **kwargs):  # noqa
        if self._value is self._missing:
            self._value = self._fn()
        return self._value
    def __get__(self, instance, owner):  # noqa
        bound = instance.__dict__[self._fn.__name__] = self.__class__(self._fn.__get__(instance, owner))
        return bound


def _main():
    @cached_nullary
    def f():
        nonlocal c
        c += 1
        return 'foo'

    c = 0
    for _ in range(2):
        assert f() == 'foo'
        assert c == 1

    class O:
        @cached_nullary
        def f(self):
            nonlocal c
            c += 1
            return 'foo'

    for _ in range(2):
        c = 0
        o = O()
        for _ in range(2):
            assert o.f() == 'foo'
            assert c == 1


if __name__ == '__main__':
    _main()
