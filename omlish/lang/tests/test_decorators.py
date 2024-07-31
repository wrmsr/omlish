import functools


##


class decorator:  # noqa
    def __init__(self, wrapper):
        self._wrapper = wrapper
        functools.update_wrapper(self, wrapper)

    def __call__(self, fn, *args, **kwargs):
        return self._Descriptor(self._wrapper, fn, args, kwargs)

    class _Descriptor:
        def __init__(self, wrapper, fn, args, kwargs):
            self._wrapper, self._fn, self._args, self._kwargs = wrapper, fn, args, kwargs
            self._wrapped = wrapper(fn, *args, **kwargs)
            functools.update_wrapper(self, self._wrapped)

        def __call__(self, *args, **kwargs):
            return self._wrapped(*args, **kwargs)

        def __get__(self, instance, owner):
            return self.__class__(self._wrapper, self._fn.__get__(instance, owner), self._args, self._kwargs)


def test_single_decorator():
    @decorator
    def my_decorator(fn):
        @functools.wraps(fn)
        def inner(x):
            return fn(x + 1)
        return inner

    @my_decorator
    def f(x):
        return x + 1

    assert f(3) == 5

    class Foo:
        def __init__(self, z):
            super().__init__()
            self.z = z

        z = 5

        @my_decorator
        def m(self, x):
            return self.z + x + 1

        @my_decorator
        @classmethod
        def c1(cls, x):
            return cls.z + x + 1

        @my_decorator
        @staticmethod
        def s1(x):
            return x + 1

        @classmethod
        @my_decorator
        def c2(cls, x):
            return cls.z + x + 1

        @staticmethod
        @my_decorator
        def s2(x):
            return x + 1

    assert Foo(4).m(2) == 8
    # assert Foo.m(Foo(4), 2) == 8  # FIXME
    assert Foo.c1(2) == 9
    assert Foo.s1(1) == 3
    assert Foo.c2(2) == 9
    assert Foo.s2(1) == 3


def test_double_decorator():
    def my_decorator(y):
        @decorator
        def outer(fn):
            @functools.wraps(fn)
            def inner(x):
                return fn(x + y)
            return inner
        return outer

    @my_decorator(2)
    def f(x):
        return x + 1

    assert f(3) == 6

    class Foo:
        def __init__(self, z):
            super().__init__()
            self.z = z

        z = 5

        @my_decorator(2)
        def m(self, x):
            return self.z + x + 1

        @my_decorator(2)
        @classmethod
        def c1(cls, x):
            return cls.z + x + 1

        @my_decorator(2)
        @staticmethod
        def s1(x):
            return x + 1

        @classmethod
        @my_decorator(2)
        def c2(cls, x):
            return cls.z + x + 1

        @staticmethod
        @my_decorator(2)
        def s2(x):
            return x + 1

    assert Foo(4).m(2) == 9
    # assert Foo.m(Foo(4), 2) == 9  # FIXME
    assert Foo.c1(2) == 10
    assert Foo.s1(1) == 4
    assert Foo.c2(2) == 10
    assert Foo.s2(1) == 4


##


def decorator2(wrapper):
    def outer(fn):
        def inner(*args, **kwargs):
            return wrapper(fn, *args, **kwargs)
        return inner
    return outer


def test_decorator2():
    @decorator2
    def my_decorator(fn, x):
        return fn(x) + 1

    @my_decorator
    def f(x):
        return x + 1

    assert f(3) == 5

    class Foo:
        def __init__(self, z):
            super().__init__()
            self.z = z

        z = 5

        @my_decorator
        def m(self, x):
            return self.z + x + 1

        @my_decorator
        @classmethod
        def c1(cls, x):
            return cls.z + x + 1

        @my_decorator
        @staticmethod
        def s1(x):
            return x + 1

        @classmethod
        @my_decorator
        def c2(cls, x):
            return cls.z + x + 1

        @staticmethod
        @my_decorator
        def s2(x):
            return x + 1

    assert Foo(4).m(2) == 8
    # assert Foo.m(Foo(4), 2) == 8  # FIXME
    assert Foo.c1(2) == 9
    assert Foo.s1(1) == 3
    assert Foo.c2(2) == 9
    assert Foo.s2(1) == 3
