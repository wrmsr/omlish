class _ProxyFunc:
    _fn = None

    def __call__(self, *args, **kwargs):
        if self._fn is None:
            raise TypeError('recursive proxy not set')
        return self._fn(*args, **kwargs)

    def _set_fn(self, fn):
        if self._fn is not None:
            raise TypeError('recursive proxy already set')
        self._fn = fn

    @classmethod
    def _new(cls):
        return (p := cls()), p._set_fn
