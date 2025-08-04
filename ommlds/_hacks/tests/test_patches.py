import functools

import pytest

from ..patches import patch_method_context


@pytest.mark.parametrize('find_mro', [True, False])
@pytest.mark.parametrize('mode', ['partial', 'inner'])
def test_patches(find_mro, mode):
    class Foo:
        def __init__(self, i):
            self.i = i

        def im(self, x, y):
            return x + y + self.i

        c = 5

        @classmethod
        def cm(cls, x, y):
            return x + y + cls.c

        @staticmethod
        def sm(x, y):
            return x + y

    pmc = functools.partial(
        patch_method_context,
        find_mro=find_mro,
        mode=mode,
    )

    assert Foo(10).im(1, 2) == 13
    with pmc(
            Foo,
            'im',
            lambda self, old, x, y: old(x, y) + 1,
    ):
        assert Foo(10).im(1, 2) == 14
    assert Foo(10).im(1, 2) == 13

    assert Foo.cm(1, 2) == 8
    with pmc(
            Foo,
            'cm',
            classmethod(lambda cls, old, x, y: old(x, y) + 1),
    ):
        assert Foo.cm(1, 2) == 9
    assert Foo.cm(1, 2) == 8

    assert Foo.sm(1, 2) == 3
    with pmc(
            Foo,
            'sm',
            staticmethod(lambda old, x, y: old(x, y) + 1),
    ):
        assert Foo.sm(1, 2) == 4
    assert Foo.sm(1, 2) == 3
