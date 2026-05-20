# @omlish-lite


##


class FnWriter:
    def __init__(self, fn):
        self._fn = fn

    def write(self, *args, **kwargs):
        return self._fn(*args, **kwargs)
