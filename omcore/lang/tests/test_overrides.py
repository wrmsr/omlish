import functools
import typing as ta

import pytest

from ..overrides import RequiresOverride
from ..overrides import RequiresOverrideError


def test_requires_override():
    class A(RequiresOverride):
        def foo(self):
            pass

        def bar(self):
            pass

    with pytest.raises(RequiresOverrideError) as roe:  # noqa
        class B(A):  # noqa
            def bar(self):
                pass

    class C(A):  # noqa
        @ta.override
        def bar(self):
            pass

    class D:
        def bar(self):
            pass

    with pytest.raises(RequiresOverrideError) as roe:  # noqa
        class E(D, A):  # noqa
            pass

    class F(A, D):  # noqa
        pass


def test_requires_override_annotated_classes():
    # Annotation machinery entries (PEP 649 __annotate_func__ / __annotations_cache__) must be exempt.
    class A(RequiresOverride):
        x: int = 1

    A.__annotations__  # materialize any lazy annotation cache on the base  # noqa

    class B(A):
        y: str = 'hi'

    assert B().y == 'hi'


def test_requires_override_non_plain_functions():
    class A(RequiresOverride):
        @classmethod
        def cm(cls):
            pass

        @staticmethod
        def sm():
            pass

        @property
        def p(self):
            return 1

    class B(A):
        @classmethod
        @ta.override
        def cm(cls):
            pass

        @staticmethod
        @ta.override
        def sm():
            pass

        @property
        @ta.override
        def p(self):
            return 2

    assert B().p == 2

    with pytest.raises(RequiresOverrideError):
        class C(A):  # noqa
            @classmethod
            def cm(cls):
                pass


def test_requires_override_wrapped_functions():
    def deco(fn):
        @functools.wraps(fn)
        def inner(*args, **kwargs):
            return fn(*args, **kwargs)
        return inner

    class A(RequiresOverride):
        def m(self):
            pass

    # The @ta.override flag must be honored wherever it lands in the wrapper chain - on the outermost wrapper when
    # applied atop a decorator, or on the innermost function when applied beneath one.
    class B(A):
        @ta.override
        @deco
        def m(self):
            pass

    class C(A):
        @deco
        @ta.override
        def m(self):
            pass

    with pytest.raises(RequiresOverrideError):
        class D(A):  # noqa
            @deco
            def m(self):
                pass
