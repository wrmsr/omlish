from .lang.cached import _CachedProperty  # noqa
from .lang.cached import cached_function

function = cached_function

property = property  # noqa

globals()['property'] = _CachedProperty  # noqa
