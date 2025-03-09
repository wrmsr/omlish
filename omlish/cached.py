"""
This module solely exists for import convenience - tools will tend to resolve the imported 'property' as if it were from
builtins and thus not distinguish it from a normal property.

    from omlish import cached

    class C:
        @cached.property
        def p(self) -> str: ...

"""
from .lang.cached.function import cached_function as _cached_function
from .lang.cached.property import cached_property as _cached_property


function = _cached_function

property = property  # noqa

globals()['property'] = _cached_property  # noqa
