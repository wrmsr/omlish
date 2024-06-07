_IGNORE = object()

_property = property


class Property:
    def __init__(self, fn, *, name=None, ignore_if=lambda _: False, clear_on_init=False):
        super().__init__()
        if isinstance(fn, _property):
            fn = fn.fget
        self._fn = fn
        self._ignore_if = ignore_if
        self._name = name
        self._clear_on_init = clear_on_init

    def __set_name__(self, owner, name):
        if self._name is None:
            self._name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        if self._name is None:
            raise TypeError(self)
        try:
            return instance.__dict__[self._name]
        except KeyError:
            pass
        value = self._fn.__get__(instance, owner)()
        if value is _IGNORE:
            return None
        instance.__dict__[self._name] = value
        return value

    def __set__(self, instance, value):
        if self._ignore_if(value):
            return
        if instance.__dict__[self._name] == value:
            return
        raise TypeError(self._name)


# Last
property = property  # noqa

globals()['property'] = Property  # noqa
