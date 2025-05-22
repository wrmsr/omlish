import typing as ta

import pytest

from ..overrides import RequiresOverride


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
