"""
This module solely exists for import convenience - tools will tend to resolve the imported 'property' as if it were from
builtins and thus not distinguish it from a normal property.

    from omlish import cached

    class C:
        @cached.property
        def p(self) -> str: ...

"""
from .lang.cached import _CachedProperty  # noqa
from .lang.cached import cached_function as _cached_function

function = _cached_function

property = property  # noqa

globals()['property'] = _CachedProperty  # noqa
