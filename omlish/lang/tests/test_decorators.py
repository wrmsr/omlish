import functools


##


class decorator:  # noqa
    def __init__(self, fn):
        super().__init__()
        self._fn = fn

    def __call__(self, *args, **kwargs):
        return self._fn(*args, **kwargs)


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
        def c(cls, x):
            return cls.z + x + 1

        @my_decorator
        @staticmethod
        def s(x):
            return x + 1

    assert Foo(4).m(2) == 7
    assert Foo.c(2) == 8
    assert Foo.c(1) == 2


# def test_double_decorator():
#     @decorator
#     def my_decorator(y):
#         def outer(fn):
#             @functools.wraps(fn)
#             def inner(x):
#                 return fn(x + y)
#             return inner
#         return outer
