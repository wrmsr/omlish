from .lang.cached import _CachedProperty  # noqa


property = property  # noqa

globals()['property'] = _CachedProperty  # noqa
