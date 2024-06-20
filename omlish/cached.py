from .lang.cached import cached_function
from .lang.cached import _CachedProperty  # noqa


function = cached_function

property = property  # noqa

globals()['property'] = _CachedProperty  # noqa
