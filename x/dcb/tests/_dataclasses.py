# type: ignore
# ruff: noqa
# flake8: noqa
# @omlish-generated
import dataclasses
import types


def _transform_dataclass__A(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__check_type,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__coerce,
        __dataclass__init__fields__2__default,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__3__default_factory,
        __dataclass__init__fields__3__validate,
        __dataclass__init__init_fns__0,
        __dataclass__init__validate_fns__0,
        __dataclass__override__fields__1__annotation,
        __dataclass__repr__fns__2__fn,
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__property=property,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
):
    def __copy__(self):
        if self.__class__ is not __dataclass__cls:
            raise TypeError(self)
        return __dataclass__cls(  # noqa
            i=self.i,
            s=self.s,
            d=self.d,
            l=self.l,
        )

    __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
    if '__copy__' in __dataclass__cls.__dict__:
        raise AttributeError('__copy__')
    setattr(__dataclass__cls, '__copy__', __copy__)

    def __eq__(self, other):
        if self is other:
            return True
        if self.__class__ is not other.__class__:
            return NotImplemented
        return (
                self.i == other.i and
                self.s == other.s and
                self.d == other.d and
                self.l == other.l
        )

    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise AttributeError('__eq__')
    setattr(__dataclass__cls, '__eq__', __eq__)

    def __setattr__(self, name, value):
        if type(self) is __dataclass__cls or name in {'i', 's', 'd', 'l'}:
            raise __dataclass__FrozenInstanceError
        super(__dataclass__cls, self).__setattr__(name, value)

    __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
    if '__setattr__' in __dataclass__cls.__dict__:
        raise AttributeError('__setattr__')
    setattr(__dataclass__cls, '__setattr__', __setattr__)

    def __delattr__(self, name):
        if type(self) is __dataclass__cls or name in {'i', 's', 'd', 'l'}:
            raise __dataclass__FrozenInstanceError
        super(__dataclass__cls, self).__delattr__(name)

    __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
    if '__delattr__' in __dataclass__cls.__dict__:
        raise AttributeError('__delattr__')
    setattr(__dataclass__cls, '__delattr__', __delattr__)

    def __hash__(self):
        return hash((
            self.i,
            self.s,
            self.d,
            self.l,
        ))

    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    if '__hash__' in __dataclass__cls.__dict__:
        raise AttributeError('__hash__')
    setattr(__dataclass__cls, '__hash__', __hash__)

    def __init__(
            __dataclass__self,
            i: __dataclass__init__fields__0__annotation,
            s: __dataclass__init__fields__1__annotation,
            d: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            l: __dataclass__init__fields__3__annotation = __dataclass__HAS_DEFAULT_FACTORY,
    ) -> __dataclass__None:
        if l is __dataclass__HAS_DEFAULT_FACTORY:
            l = __dataclass__init__fields__3__default_factory()
        d = __dataclass__init__fields__2__coerce(d)
        if not __dataclass__isinstance(s, __dataclass__init__fields__1__check_type):
            raise __dataclass__FieldTypeValidationError(
                obj=__dataclass__self,
                type=__dataclass__init__fields__1__check_type,
                field='s',
                value=s,
            )
        if not __dataclass__init__fields__3__validate(l):
            raise __dataclass__FieldFnValidationError(
                obj=__dataclass__self,
                fn=__dataclass__init__fields__3__validate,
                field='l',
                value=l,
            )
        if not __dataclass__init__validate_fns__0(
                l,
        ):
            raise __dataclass__FnValidationError(
                obj=__dataclass__self,
                fn=__dataclass__init__validate_fns__0,
            )
        __dataclass__object_setattr(__dataclass__self, 'i', i)
        __dataclass__self_dict = __dataclass__self.__dict__
        __dataclass__self_dict['s'] = s
        __dataclass__object_setattr(__dataclass__self, 'd', d)
        __dataclass__object_setattr(__dataclass__self, 'l', l)
        __dataclass__self.__post_init__()
        __dataclass__init__init_fns__0(__dataclass__self)

    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise AttributeError('__init__')
    setattr(__dataclass__cls, '__init__', __init__)

    def __lt__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        return (
            self.i,
            self.s,
            self.d,
            self.l,
        ) < (
            other.i,
            other.s,
            other.d,
            other.l,
        )

    __lt__.__qualname__ = f"{__dataclass__cls.__qualname__}.__lt__"
    if '__lt__' in __dataclass__cls.__dict__:
        raise AttributeError('__lt__')
    setattr(__dataclass__cls, '__lt__', __lt__)

    def __le__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        return (
            self.i,
            self.s,
            self.d,
            self.l,
        ) <= (
            other.i,
            other.s,
            other.d,
            other.l,
        )

    __le__.__qualname__ = f"{__dataclass__cls.__qualname__}.__le__"
    if '__le__' in __dataclass__cls.__dict__:
        raise AttributeError('__le__')
    setattr(__dataclass__cls, '__le__', __le__)

    def __gt__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        return (
            self.i,
            self.s,
            self.d,
            self.l,
        ) > (
            other.i,
            other.s,
            other.d,
            other.l,
        )

    __gt__.__qualname__ = f"{__dataclass__cls.__qualname__}.__gt__"
    if '__gt__' in __dataclass__cls.__dict__:
        raise AttributeError('__gt__')
    setattr(__dataclass__cls, '__gt__', __gt__)

    def __ge__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        return (
            self.i,
            self.s,
            self.d,
            self.l,
        ) >= (
            other.i,
            other.s,
            other.d,
            other.l,
        )

    __ge__.__qualname__ = f"{__dataclass__cls.__qualname__}.__ge__"
    if '__ge__' in __dataclass__cls.__dict__:
        raise AttributeError('__ge__')
    setattr(__dataclass__cls, '__ge__', __ge__)

    def __dataclass__property__s():
        @__dataclass__property
        def s(__dataclass__self) -> __dataclass__override__fields__1__annotation:
            return __dataclass__self.__dict__['s']

        return s

    setattr(__dataclass__cls, 's', __dataclass__property__s())

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"l={self.l!r}, "
            f"i={self.i!r}, "
            f"{f's={s}' if ((s := __dataclass__repr__fns__2__fn(self.s)) is not None) else ''}, "
            f"d={self.d!r}"
            f")"
        )

    __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
    if '__repr__' in __dataclass__cls.__dict__:
        raise AttributeError('__repr__')
    setattr(__dataclass__cls, '__repr__', __repr__)
