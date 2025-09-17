import typing as ta


T = ta.TypeVar('T')


##


@ta.final
class _ClassOrInstanceMethod:
    def __init__(self, func):
        self.__func__ = func

    def __get__(self, instance, owner=None):
        return self.__func__.__get__(instance if instance is not None else owner)


class BindableClass(ta.Generic[T]):
    # FIXME: apparently can't have TypeVars in ClassVars, but could stick in a @classmethod (which gets transformed)...
    _bound: ta.ClassVar[type[T] | None] = None

    def __init__(self, *, _bound):
        super().__init__()

        setattr(self, '_bound', _bound)

    def __class_getitem__(cls, *args, **kwargs):
        # FIXME: this could handle __mro_items__ to be subclassable, but it's not currently really intended to be
        #   subclassed
        if cls is BindableClass:
            return super().__class_getitem__(*args, **kwargs)  # type: ignore[misc]

        [bind_cls] = args
        return cls(_bound=bind_cls)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        for k, v in cls.__dict__.items():
            if isinstance(v, classmethod):
                setattr(cls, k, _ClassOrInstanceMethod(v.__func__))
