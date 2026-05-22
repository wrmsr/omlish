# @omlish-generated
# type: ignore
# ruff: noqa
# flake8: noqa
import dataclasses
import reprlib
import types


##


REGISTRY = {}


def _register(**kwargs):
    def inner(fn):
        REGISTRY[kwargs['plan_repr']] = (kwargs, fn)
        return fn
    return inner


##


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('m', 'r')), EqPlan(fields=('m', 'r')), FrozenPlan(fields=('m', 'r'), allow_dynamic"
        "_dunder_attrs=False), HashPlan(action='add', fields=('m', 'r'), cache=False), InitPlan(fields=(InitPlan.Field("
        "name='m', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, ov"
        "erride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name"
        "='r', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, overri"
        "de=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std"
        "_params=('m', 'r'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_"
        "fns=()), ReprPlan(fields=(ReprPlan.Field(name='m', kw_only=False, fn=None), ReprPlan.Field(name='r', kw_only=F"
        "alse, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='08a1aac3841bbd823cbf8591aab4858462242e0f',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('omlish.specs.openapi._marshal', '_ReferenceUnionMarshaler'),
    ),
)
def _process_dataclass__08a1aac3841bbd823cbf8591aab4858462242e0f():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                m=self.m,
                r=self.r,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.m == other.m and
                self.r == other.r
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'm',
            'r',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'm',
            'r',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.m,
                self.r,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            m: __dataclass__init__fields__0__annotation,
            r: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'm', m)
            __dataclass__object_setattr(self, 'r', r)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"m={self.m!r}")
            parts.append(f"r={self.r!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('u', 'r')), EqPlan(fields=('u', 'r')), FrozenPlan(fields=('u', 'r'), allow_dynamic"
        "_dunder_attrs=False), HashPlan(action='add', fields=('u', 'r'), cache=False), InitPlan(fields=(InitPlan.Field("
        "name='u', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, ov"
        "erride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name"
        "='r', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, overri"
        "de=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std"
        "_params=('u', 'r'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_"
        "fns=()), ReprPlan(fields=(ReprPlan.Field(name='u', kw_only=False, fn=None), ReprPlan.Field(name='r', kw_only=F"
        "alse, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='d095992190a4bef8c406f60182977cf8f1f41efa',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('omlish.specs.openapi._marshal', '_ReferenceUnionUnmarshaler'),
    ),
)
def _process_dataclass__d095992190a4bef8c406f60182977cf8f1f41efa():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                u=self.u,
                r=self.r,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.u == other.u and
                self.r == other.r
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'u',
            'r',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'u',
            'r',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.u,
                self.r,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            u: __dataclass__init__fields__0__annotation,
            r: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'u', u)
            __dataclass__object_setattr(self, 'r', r)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"u={self.u!r}")
            parts.append(f"r={self.r!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('m_dct', 'kw_m')), EqPlan(fields=('m_dct', 'kw_m')), FrozenPlan(fields=('m_dct', '"
        "kw_m'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('m_dct', 'kw_m'), cache=False), Init"
        "Plan(fields=(InitPlan.Field(name='m_dct', annotation=OpRef(name='init.fields.0.annotation'), default=None, def"
        "ault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check"
        "_type=None), InitPlan.Field(name='kw_m', annotation=OpRef(name='init.fields.1.annotation'), default=None, defa"
        "ult_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_"
        "type=None)), self_param='self', std_params=('m_dct', 'kw_m'), kw_only_params=(), frozen=True, slots=False, pos"
        "t_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='m_dct', kw_only=False"
        ", fn=None), ReprPlan.Field(name='kw_m', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='719544153ed0b35a74b1651553003d3b354700f1',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('omlish.specs.openapi._marshal', '_SchemaMarshaler'),
    ),
)
def _process_dataclass__719544153ed0b35a74b1651553003d3b354700f1():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                m_dct=self.m_dct,
                kw_m=self.kw_m,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.m_dct == other.m_dct and
                self.kw_m == other.kw_m
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'm_dct',
            'kw_m',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'm_dct',
            'kw_m',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.m_dct,
                self.kw_m,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            m_dct: __dataclass__init__fields__0__annotation,
            kw_m: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'm_dct', m_dct)
            __dataclass__object_setattr(self, 'kw_m', kw_m)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"m_dct={self.m_dct!r}")
            parts.append(f"kw_m={self.kw_m!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('u_dct', 'kw_u')), EqPlan(fields=('u_dct', 'kw_u')), FrozenPlan(fields=('u_dct', '"
        "kw_u'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('u_dct', 'kw_u'), cache=False), Init"
        "Plan(fields=(InitPlan.Field(name='u_dct', annotation=OpRef(name='init.fields.0.annotation'), default=None, def"
        "ault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check"
        "_type=None), InitPlan.Field(name='kw_u', annotation=OpRef(name='init.fields.1.annotation'), default=None, defa"
        "ult_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_"
        "type=None)), self_param='self', std_params=('u_dct', 'kw_u'), kw_only_params=(), frozen=True, slots=False, pos"
        "t_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='u_dct', kw_only=False"
        ", fn=None), ReprPlan.Field(name='kw_u', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='11262894e09b3b420a70ca6beeca90e3128bc4d9',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('omlish.specs.openapi._marshal', '_SchemaUnmarshaler'),
    ),
)
def _process_dataclass__11262894e09b3b420a70ca6beeca90e3128bc4d9():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                u_dct=self.u_dct,
                kw_u=self.kw_u,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.u_dct == other.u_dct and
                self.kw_u == other.kw_u
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'u_dct',
            'kw_u',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'u_dct',
            'kw_u',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.u_dct,
                self.kw_u,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            u_dct: __dataclass__init__fields__0__annotation,
            kw_u: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'u_dct', u_dct)
            __dataclass__object_setattr(self, 'kw_u', kw_u)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"u_dct={self.u_dct!r}")
            parts.append(f"kw_u={self.kw_u!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('schemas', 'responses', 'parameters', 'examples', 'request_bodies', 'headers', 'se"
        "curity_schemes', 'links', 'callbacks', 'path_items')), EqPlan(fields=('schemas', 'responses', 'parameters', 'e"
        "xamples', 'request_bodies', 'headers', 'security_schemes', 'links', 'callbacks', 'path_items')), FrozenPlan(fi"
        "elds=('schemas', 'responses', 'parameters', 'examples', 'request_bodies', 'headers', 'security_schemes', 'link"
        "s', 'callbacks', 'path_items'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('schemas', '"
        "responses', 'parameters', 'examples', 'request_bodies', 'headers', 'security_schemes', 'links', 'callbacks', '"
        "path_items'), cache=False), InitPlan(fields=(InitPlan.Field(name='schemas', annotation=OpRef(name='init.fields"
        ".00.annotation'), default=OpRef(name='init.fields.00.default'), default_factory=None, init=True, override=Fals"
        "e, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='responses"
        "', annotation=OpRef(name='init.fields.01.annotation'), default=OpRef(name='init.fields.01.default'), default_f"
        "actory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type="
        "None), InitPlan.Field(name='parameters', annotation=OpRef(name='init.fields.02.annotation'), default=OpRef(nam"
        "e='init.fields.02.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, c"
        "oerce=None, validate=None, check_type=None), InitPlan.Field(name='examples', annotation=OpRef(name='init.field"
        "s.03.annotation'), default=OpRef(name='init.fields.03.default'), default_factory=None, init=True, override=Fal"
        "se, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='request_"
        "bodies', annotation=OpRef(name='init.fields.04.annotation'), default=OpRef(name='init.fields.04.default'), def"
        "ault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check"
        "_type=None), InitPlan.Field(name='headers', annotation=OpRef(name='init.fields.05.annotation'), default=OpRef("
        "name='init.fields.05.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE"
        ", coerce=None, validate=None, check_type=None), InitPlan.Field(name='security_schemes', annotation=OpRef(name="
        "'init.fields.06.annotation'), default=OpRef(name='init.fields.06.default'), default_factory=None, init=True, o"
        "verride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(nam"
        "e='links', annotation=OpRef(name='init.fields.07.annotation'), default=OpRef(name='init.fields.07.default'), d"
        "efault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, che"
        "ck_type=None), InitPlan.Field(name='callbacks', annotation=OpRef(name='init.fields.08.annotation'), default=Op"
        "Ref(name='init.fields.08.default'), default_factory=None, init=True, override=False, field_type=FieldType.INST"
        "ANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='path_items', annotation=OpRef(name='i"
        "nit.fields.09.annotation'), default=OpRef(name='init.fields.09.default'), default_factory=None, init=True, ove"
        "rride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', "
        "std_params=('schemas', 'responses', 'parameters', 'examples', 'request_bodies', 'headers', 'security_schemes',"
        " 'links', 'callbacks', 'path_items'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init"
        "_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='schemas', kw_only=False, fn=None), ReprPlan.F"
        "ield(name='responses', kw_only=False, fn=None), ReprPlan.Field(name='parameters', kw_only=False, fn=None), Rep"
        "rPlan.Field(name='examples', kw_only=False, fn=None), ReprPlan.Field(name='request_bodies', kw_only=False, fn="
        "None), ReprPlan.Field(name='headers', kw_only=False, fn=None), ReprPlan.Field(name='security_schemes', kw_only"
        "=False, fn=None), ReprPlan.Field(name='links', kw_only=False, fn=None), ReprPlan.Field(name='callbacks', kw_on"
        "ly=False, fn=None), ReprPlan.Field(name='path_items', kw_only=False, fn=None)), id=False, terse=False, default"
        "_fn=OpRef(name='repr.default_fn'))))"
    ),
    plan_repr_sha1='70b15f8a60ca2e32dc7fec02c618641cd0243175',
    op_ref_idents=(
        '__dataclass__init__fields__00__annotation',
        '__dataclass__init__fields__00__default',
        '__dataclass__init__fields__01__annotation',
        '__dataclass__init__fields__01__default',
        '__dataclass__init__fields__02__annotation',
        '__dataclass__init__fields__02__default',
        '__dataclass__init__fields__03__annotation',
        '__dataclass__init__fields__03__default',
        '__dataclass__init__fields__04__annotation',
        '__dataclass__init__fields__04__default',
        '__dataclass__init__fields__05__annotation',
        '__dataclass__init__fields__05__default',
        '__dataclass__init__fields__06__annotation',
        '__dataclass__init__fields__06__default',
        '__dataclass__init__fields__07__annotation',
        '__dataclass__init__fields__07__default',
        '__dataclass__init__fields__08__annotation',
        '__dataclass__init__fields__08__default',
        '__dataclass__init__fields__09__annotation',
        '__dataclass__init__fields__09__default',
        '__dataclass__repr__default_fn',
    ),
    cls_names=(
        ('omlish.specs.openapi.openapi', 'Components'),
    ),
)
def _process_dataclass__70b15f8a60ca2e32dc7fec02c618641cd0243175():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__00__annotation,
        __dataclass__init__fields__00__default,
        __dataclass__init__fields__01__annotation,
        __dataclass__init__fields__01__default,
        __dataclass__init__fields__02__annotation,
        __dataclass__init__fields__02__default,
        __dataclass__init__fields__03__annotation,
        __dataclass__init__fields__03__default,
        __dataclass__init__fields__04__annotation,
        __dataclass__init__fields__04__default,
        __dataclass__init__fields__05__annotation,
        __dataclass__init__fields__05__default,
        __dataclass__init__fields__06__annotation,
        __dataclass__init__fields__06__default,
        __dataclass__init__fields__07__annotation,
        __dataclass__init__fields__07__default,
        __dataclass__init__fields__08__annotation,
        __dataclass__init__fields__08__default,
        __dataclass__init__fields__09__annotation,
        __dataclass__init__fields__09__default,
        __dataclass__repr__default_fn,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                schemas=self.schemas,
                responses=self.responses,
                parameters=self.parameters,
                examples=self.examples,
                request_bodies=self.request_bodies,
                headers=self.headers,
                security_schemes=self.security_schemes,
                links=self.links,
                callbacks=self.callbacks,
                path_items=self.path_items,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.schemas == other.schemas and
                self.responses == other.responses and
                self.parameters == other.parameters and
                self.examples == other.examples and
                self.request_bodies == other.request_bodies and
                self.headers == other.headers and
                self.security_schemes == other.security_schemes and
                self.links == other.links and
                self.callbacks == other.callbacks and
                self.path_items == other.path_items
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'schemas',
            'responses',
            'parameters',
            'examples',
            'request_bodies',
            'headers',
            'security_schemes',
            'links',
            'callbacks',
            'path_items',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'schemas',
            'responses',
            'parameters',
            'examples',
            'request_bodies',
            'headers',
            'security_schemes',
            'links',
            'callbacks',
            'path_items',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.schemas,
                self.responses,
                self.parameters,
                self.examples,
                self.request_bodies,
                self.headers,
                self.security_schemes,
                self.links,
                self.callbacks,
                self.path_items,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            schemas: __dataclass__init__fields__00__annotation = __dataclass__init__fields__00__default,
            responses: __dataclass__init__fields__01__annotation = __dataclass__init__fields__01__default,
            parameters: __dataclass__init__fields__02__annotation = __dataclass__init__fields__02__default,
            examples: __dataclass__init__fields__03__annotation = __dataclass__init__fields__03__default,
            request_bodies: __dataclass__init__fields__04__annotation = __dataclass__init__fields__04__default,
            headers: __dataclass__init__fields__05__annotation = __dataclass__init__fields__05__default,
            security_schemes: __dataclass__init__fields__06__annotation = __dataclass__init__fields__06__default,
            links: __dataclass__init__fields__07__annotation = __dataclass__init__fields__07__default,
            callbacks: __dataclass__init__fields__08__annotation = __dataclass__init__fields__08__default,
            path_items: __dataclass__init__fields__09__annotation = __dataclass__init__fields__09__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'schemas', schemas)
            __dataclass__object_setattr(self, 'responses', responses)
            __dataclass__object_setattr(self, 'parameters', parameters)
            __dataclass__object_setattr(self, 'examples', examples)
            __dataclass__object_setattr(self, 'request_bodies', request_bodies)
            __dataclass__object_setattr(self, 'headers', headers)
            __dataclass__object_setattr(self, 'security_schemes', security_schemes)
            __dataclass__object_setattr(self, 'links', links)
            __dataclass__object_setattr(self, 'callbacks', callbacks)
            __dataclass__object_setattr(self, 'path_items', path_items)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__default_fn(self.schemas)) is not None:
                parts.append(f"schemas={s}")
            if (s := __dataclass__repr__default_fn(self.responses)) is not None:
                parts.append(f"responses={s}")
            if (s := __dataclass__repr__default_fn(self.parameters)) is not None:
                parts.append(f"parameters={s}")
            if (s := __dataclass__repr__default_fn(self.examples)) is not None:
                parts.append(f"examples={s}")
            if (s := __dataclass__repr__default_fn(self.request_bodies)) is not None:
                parts.append(f"request_bodies={s}")
            if (s := __dataclass__repr__default_fn(self.headers)) is not None:
                parts.append(f"headers={s}")
            if (s := __dataclass__repr__default_fn(self.security_schemes)) is not None:
                parts.append(f"security_schemes={s}")
            if (s := __dataclass__repr__default_fn(self.links)) is not None:
                parts.append(f"links={s}")
            if (s := __dataclass__repr__default_fn(self.callbacks)) is not None:
                parts.append(f"callbacks={s}")
            if (s := __dataclass__repr__default_fn(self.path_items)) is not None:
                parts.append(f"path_items={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('name', 'url', 'email')), EqPlan(fields=('name', 'url', 'email')), FrozenPlan(fiel"
        "ds=('name', 'url', 'email'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('name', 'url', "
        "'email'), cache=False), InitPlan(fields=(InitPlan.Field(name='name', annotation=OpRef(name='init.fields.0.anno"
        "tation'), default=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_"
        "type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='url', annotation=O"
        "pRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init"
        "=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.F"
        "ield(name='email', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.defaul"
        "t'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=Non"
        "e, check_type=None)), self_param='self', std_params=('name', 'url', 'email'), kw_only_params=(), frozen=True, "
        "slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='name'"
        ", kw_only=False, fn=None), ReprPlan.Field(name='url', kw_only=False, fn=None), ReprPlan.Field(name='email', kw"
        "_only=False, fn=None)), id=False, terse=False, default_fn=OpRef(name='repr.default_fn'))))"
    ),
    plan_repr_sha1='d4a541cb97da82c217d4aeb1a3c99ba233c59794',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__repr__default_fn',
    ),
    cls_names=(
        ('omlish.specs.openapi.openapi', 'Contact'),
    ),
)
def _process_dataclass__d4a541cb97da82c217d4aeb1a3c99ba233c59794():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
        __dataclass__repr__default_fn,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                name=self.name,
                url=self.url,
                email=self.email,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.name == other.name and
                self.url == other.url and
                self.email == other.email
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'name',
            'url',
            'email',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'name',
            'url',
            'email',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.name,
                self.url,
                self.email,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            name: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            url: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            email: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'url', url)
            __dataclass__object_setattr(self, 'email', email)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__default_fn(self.name)) is not None:
                parts.append(f"name={s}")
            if (s := __dataclass__repr__default_fn(self.url)) is not None:
                parts.append(f"url={s}")
            if (s := __dataclass__repr__default_fn(self.email)) is not None:
                parts.append(f"email={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('property_name', 'mapping')), EqPlan(fields=('property_name', 'mapping')), FrozenP"
        "lan(fields=('property_name', 'mapping'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('pr"
        "operty_name', 'mapping'), cache=False), InitPlan(fields=(InitPlan.Field(name='property_name', annotation=OpRef"
        "(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=F"
        "ieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='mapping', annotation=OpR"
        "ef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=T"
        "rue, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param="
        "'self', std_params=('property_name', 'mapping'), kw_only_params=(), frozen=True, slots=False, post_init_params"
        "=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='property_name', kw_only=False, fn="
        "None), ReprPlan.Field(name='mapping', kw_only=False, fn=None)), id=False, terse=False, default_fn=OpRef(name='"
        "repr.default_fn'))))"
    ),
    plan_repr_sha1='3d1a4171d606ce3a412ee1a299e055a625b5930f',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__repr__default_fn',
    ),
    cls_names=(
        ('omlish.specs.openapi.openapi', 'Discriminator'),
    ),
)
def _process_dataclass__3d1a4171d606ce3a412ee1a299e055a625b5930f():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__repr__default_fn,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                property_name=self.property_name,
                mapping=self.mapping,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.property_name == other.property_name and
                self.mapping == other.mapping
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'property_name',
            'mapping',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'property_name',
            'mapping',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.property_name,
                self.mapping,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            property_name: __dataclass__init__fields__0__annotation,
            mapping: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'property_name', property_name)
            __dataclass__object_setattr(self, 'mapping', mapping)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__default_fn(self.property_name)) is not None:
                parts.append(f"property_name={s}")
            if (s := __dataclass__repr__default_fn(self.mapping)) is not None:
                parts.append(f"mapping={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('content_type', 'headers', 'style', 'explode', 'allow_reserved')), EqPlan(fields=("
        "'content_type', 'headers', 'style', 'explode', 'allow_reserved')), FrozenPlan(fields=('content_type', 'headers"
        "', 'style', 'explode', 'allow_reserved'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('c"
        "ontent_type', 'headers', 'style', 'explode', 'allow_reserved'), cache=False), InitPlan(fields=(InitPlan.Field("
        "name='content_type', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.defa"
        "ult'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=N"
        "one, check_type=None), InitPlan.Field(name='headers', annotation=OpRef(name='init.fields.1.annotation'), defau"
        "lt=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType."
        "INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='style', annotation=OpRef(name='in"
        "it.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, overri"
        "de=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='ex"
        "plode', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), defaul"
        "t_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_ty"
        "pe=None), InitPlan.Field(name='allow_reserved', annotation=OpRef(name='init.fields.4.annotation'), default=OpR"
        "ef(name='init.fields.4.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTAN"
        "CE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=('content_type', 'headers', '"
        "style', 'explode', 'allow_reserved'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init"
        "_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='content_type', kw_only=False, fn=None), ReprP"
        "lan.Field(name='headers', kw_only=False, fn=None), ReprPlan.Field(name='style', kw_only=False, fn=None), ReprP"
        "lan.Field(name='explode', kw_only=False, fn=None), ReprPlan.Field(name='allow_reserved', kw_only=False, fn=Non"
        "e)), id=False, terse=False, default_fn=OpRef(name='repr.default_fn'))))"
    ),
    plan_repr_sha1='188ab7478374634cc437c58cd5e05b336158064f',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__4__default',
        '__dataclass__repr__default_fn',
    ),
    cls_names=(
        ('omlish.specs.openapi.openapi', 'Encoding'),
    ),
)
def _process_dataclass__188ab7478374634cc437c58cd5e05b336158064f():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__3__default,
        __dataclass__init__fields__4__annotation,
        __dataclass__init__fields__4__default,
        __dataclass__repr__default_fn,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                content_type=self.content_type,
                headers=self.headers,
                style=self.style,
                explode=self.explode,
                allow_reserved=self.allow_reserved,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.content_type == other.content_type and
                self.headers == other.headers and
                self.style == other.style and
                self.explode == other.explode and
                self.allow_reserved == other.allow_reserved
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'content_type',
            'headers',
            'style',
            'explode',
            'allow_reserved',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'content_type',
            'headers',
            'style',
            'explode',
            'allow_reserved',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.content_type,
                self.headers,
                self.style,
                self.explode,
                self.allow_reserved,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            content_type: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            headers: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            style: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            explode: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            allow_reserved: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'content_type', content_type)
            __dataclass__object_setattr(self, 'headers', headers)
            __dataclass__object_setattr(self, 'style', style)
            __dataclass__object_setattr(self, 'explode', explode)
            __dataclass__object_setattr(self, 'allow_reserved', allow_reserved)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__default_fn(self.content_type)) is not None:
                parts.append(f"content_type={s}")
            if (s := __dataclass__repr__default_fn(self.headers)) is not None:
                parts.append(f"headers={s}")
            if (s := __dataclass__repr__default_fn(self.style)) is not None:
                parts.append(f"style={s}")
            if (s := __dataclass__repr__default_fn(self.explode)) is not None:
                parts.append(f"explode={s}")
            if (s := __dataclass__repr__default_fn(self.allow_reserved)) is not None:
                parts.append(f"allow_reserved={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('summary', 'description', 'value', 'external_value')), EqPlan(fields=('summary', '"
        "description', 'value', 'external_value')), FrozenPlan(fields=('summary', 'description', 'value', 'external_val"
        "ue'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('summary', 'description', 'value', 'ex"
        "ternal_value'), cache=False), InitPlan(fields=(InitPlan.Field(name='summary', annotation=OpRef(name='init.fiel"
        "ds.0.annotation'), default=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=Fals"
        "e, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='descripti"
        "on', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_f"
        "actory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type="
        "None), InitPlan.Field(name='value', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='ini"
        "t.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=N"
        "one, validate=None, check_type=None), InitPlan.Field(name='external_value', annotation=OpRef(name='init.fields"
        ".3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False,"
        " field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=("
        "'summary', 'description', 'value', 'external_value'), kw_only_params=(), frozen=True, slots=False, post_init_p"
        "arams=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='summary', kw_only=False, fn=N"
        "one), ReprPlan.Field(name='description', kw_only=False, fn=None), ReprPlan.Field(name='value', kw_only=False, "
        "fn=None), ReprPlan.Field(name='external_value', kw_only=False, fn=None)), id=False, terse=False, default_fn=Op"
        "Ref(name='repr.default_fn'))))"
    ),
    plan_repr_sha1='3255469da9b4c7981b4f6c4f6a90ccbf555db3eb',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
        '__dataclass__repr__default_fn',
    ),
    cls_names=(
        ('omlish.specs.openapi.openapi', 'Example'),
    ),
)
def _process_dataclass__3255469da9b4c7981b4f6c4f6a90ccbf555db3eb():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__3__default,
        __dataclass__repr__default_fn,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                summary=self.summary,
                description=self.description,
                value=self.value,
                external_value=self.external_value,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.summary == other.summary and
                self.description == other.description and
                self.value == other.value and
                self.external_value == other.external_value
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'summary',
            'description',
            'value',
            'external_value',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'summary',
            'description',
            'value',
            'external_value',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.summary,
                self.description,
                self.value,
                self.external_value,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            summary: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            description: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            value: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            external_value: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'summary', summary)
            __dataclass__object_setattr(self, 'description', description)
            __dataclass__object_setattr(self, 'value', value)
            __dataclass__object_setattr(self, 'external_value', external_value)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__default_fn(self.summary)) is not None:
                parts.append(f"summary={s}")
            if (s := __dataclass__repr__default_fn(self.description)) is not None:
                parts.append(f"description={s}")
            if (s := __dataclass__repr__default_fn(self.value)) is not None:
                parts.append(f"value={s}")
            if (s := __dataclass__repr__default_fn(self.external_value)) is not None:
                parts.append(f"external_value={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('url', 'description')), EqPlan(fields=('url', 'description')), FrozenPlan(fields=("
        "'url', 'description'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('url', 'description')"
        ", cache=False), InitPlan(fields=(InitPlan.Field(name='url', annotation=OpRef(name='init.fields.0.annotation'),"
        " default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, va"
        "lidate=None, check_type=None), InitPlan.Field(name='description', annotation=OpRef(name='init.fields.1.annotat"
        "ion'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_typ"
        "e=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=('url', 'de"
        "scription'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=())"
        ", ReprPlan(fields=(ReprPlan.Field(name='url', kw_only=False, fn=None), ReprPlan.Field(name='description', kw_o"
        "nly=False, fn=None)), id=False, terse=False, default_fn=OpRef(name='repr.default_fn'))))"
    ),
    plan_repr_sha1='92c624435fbcbab9682c66aa9a03c714fb8df108',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__repr__default_fn',
    ),
    cls_names=(
        ('omlish.specs.openapi.openapi', 'ExternalDocumentation'),
    ),
)
def _process_dataclass__92c624435fbcbab9682c66aa9a03c714fb8df108():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__repr__default_fn,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                url=self.url,
                description=self.description,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.url == other.url and
                self.description == other.description
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'url',
            'description',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'url',
            'description',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.url,
                self.description,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            url: __dataclass__init__fields__0__annotation,
            description: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'url', url)
            __dataclass__object_setattr(self, 'description', description)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__default_fn(self.url)) is not None:
                parts.append(f"url={s}")
            if (s := __dataclass__repr__default_fn(self.description)) is not None:
                parts.append(f"description={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('common',)), EqPlan(fields=('common',)), FrozenPlan(fields=('common',), allow_dyna"
        "mic_dunder_attrs=False), HashPlan(action='add', fields=('common',), cache=False), InitPlan(fields=(InitPlan.Fi"
        "eld(name='common', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init"
        "=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_par"
        "am='self', std_params=('common',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fn"
        "s=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='common', kw_only=False, fn=None),), id=False, te"
        "rse=False, default_fn=OpRef(name='repr.default_fn'))))"
    ),
    plan_repr_sha1='513a3812c33c8abe4d63e23623cf6ca96da920c9',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__repr__default_fn',
    ),
    cls_names=(
        ('omlish.specs.openapi.openapi', 'Header'),
    ),
)
def _process_dataclass__513a3812c33c8abe4d63e23623cf6ca96da920c9():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__repr__default_fn,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                common=self.common,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.common == other.common
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'common',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'common',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.common,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            common: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'common', common)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__default_fn(self.common)) is not None:
                parts.append(f"common={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('title', 'version', 'summary', 'description', 'terms_of_service', 'contact', 'lice"
        "nse')), EqPlan(fields=('title', 'version', 'summary', 'description', 'terms_of_service', 'contact', 'license')"
        "), FrozenPlan(fields=('title', 'version', 'summary', 'description', 'terms_of_service', 'contact', 'license'),"
        " allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('title', 'version', 'summary', 'description"
        "', 'terms_of_service', 'contact', 'license'), cache=False), InitPlan(fields=(InitPlan.Field(name='title', anno"
        "tation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, "
        "field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='version', an"
        "notation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False"
        ", field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='summary', "
        "annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factor"
        "y=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)"
        ", InitPlan.Field(name='description', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='in"
        "it.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce="
        "None, validate=None, check_type=None), InitPlan.Field(name='terms_of_service', annotation=OpRef(name='init.fie"
        "lds.4.annotation'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, override=Fal"
        "se, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='contact'"
        ", annotation=OpRef(name='init.fields.5.annotation'), default=OpRef(name='init.fields.5.default'), default_fact"
        "ory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=Non"
        "e), InitPlan.Field(name='license', annotation=OpRef(name='init.fields.6.annotation'), default=OpRef(name='init"
        ".fields.6.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=No"
        "ne, validate=None, check_type=None)), self_param='self', std_params=('title', 'version', 'summary', 'descripti"
        "on', 'terms_of_service', 'contact', 'license'), kw_only_params=(), frozen=True, slots=False, post_init_params="
        "None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='title', kw_only=False, fn=None), Re"
        "prPlan.Field(name='version', kw_only=False, fn=None), ReprPlan.Field(name='summary', kw_only=False, fn=None), "
        "ReprPlan.Field(name='description', kw_only=False, fn=None), ReprPlan.Field(name='terms_of_service', kw_only=Fa"
        "lse, fn=None), ReprPlan.Field(name='contact', kw_only=False, fn=None), ReprPlan.Field(name='license', kw_only="
        "False, fn=None)), id=False, terse=False, default_fn=OpRef(name='repr.default_fn'))))"
    ),
    plan_repr_sha1='5f1e1eec066ba3cbccd2ca9c47c2b2efe9f82729',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__4__default',
        '__dataclass__init__fields__5__annotation',
        '__dataclass__init__fields__5__default',
        '__dataclass__init__fields__6__annotation',
        '__dataclass__init__fields__6__default',
        '__dataclass__repr__default_fn',
    ),
    cls_names=(
        ('omlish.specs.openapi.openapi', 'Info'),
    ),
)
def _process_dataclass__5f1e1eec066ba3cbccd2ca9c47c2b2efe9f82729():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__3__default,
        __dataclass__init__fields__4__annotation,
        __dataclass__init__fields__4__default,
        __dataclass__init__fields__5__annotation,
        __dataclass__init__fields__5__default,
        __dataclass__init__fields__6__annotation,
        __dataclass__init__fields__6__default,
        __dataclass__repr__default_fn,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                title=self.title,
                version=self.version,
                summary=self.summary,
                description=self.description,
                terms_of_service=self.terms_of_service,
                contact=self.contact,
                license=self.license,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.title == other.title and
                self.version == other.version and
                self.summary == other.summary and
                self.description == other.description and
                self.terms_of_service == other.terms_of_service and
                self.contact == other.contact and
                self.license == other.license
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'title',
            'version',
            'summary',
            'description',
            'terms_of_service',
            'contact',
            'license',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'title',
            'version',
            'summary',
            'description',
            'terms_of_service',
            'contact',
            'license',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.title,
                self.version,
                self.summary,
                self.description,
                self.terms_of_service,
                self.contact,
                self.license,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            title: __dataclass__init__fields__0__annotation,
            version: __dataclass__init__fields__1__annotation,
            summary: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            description: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            terms_of_service: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            contact: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
            license: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'title', title)
            __dataclass__object_setattr(self, 'version', version)
            __dataclass__object_setattr(self, 'summary', summary)
            __dataclass__object_setattr(self, 'description', description)
            __dataclass__object_setattr(self, 'terms_of_service', terms_of_service)
            __dataclass__object_setattr(self, 'contact', contact)
            __dataclass__object_setattr(self, 'license', license)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__default_fn(self.title)) is not None:
                parts.append(f"title={s}")
            if (s := __dataclass__repr__default_fn(self.version)) is not None:
                parts.append(f"version={s}")
            if (s := __dataclass__repr__default_fn(self.summary)) is not None:
                parts.append(f"summary={s}")
            if (s := __dataclass__repr__default_fn(self.description)) is not None:
                parts.append(f"description={s}")
            if (s := __dataclass__repr__default_fn(self.terms_of_service)) is not None:
                parts.append(f"terms_of_service={s}")
            if (s := __dataclass__repr__default_fn(self.contact)) is not None:
                parts.append(f"contact={s}")
            if (s := __dataclass__repr__default_fn(self.license)) is not None:
                parts.append(f"license={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('name', 'identifier', 'url')), EqPlan(fields=('name', 'identifier', 'url')), Froze"
        "nPlan(fields=('name', 'identifier', 'url'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=("
        "'name', 'identifier', 'url'), cache=False), InitPlan(fields=(InitPlan.Field(name='name', annotation=OpRef(name"
        "='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldT"
        "ype.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='identifier', annotation=OpRef"
        "(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=Tru"
        "e, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field"
        "(name='url', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), d"
        "efault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, che"
        "ck_type=None)), self_param='self', std_params=('name', 'identifier', 'url'), kw_only_params=(), frozen=True, s"
        "lots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='name',"
        " kw_only=False, fn=None), ReprPlan.Field(name='identifier', kw_only=False, fn=None), ReprPlan.Field(name='url'"
        ", kw_only=False, fn=None)), id=False, terse=False, default_fn=OpRef(name='repr.default_fn'))))"
    ),
    plan_repr_sha1='87af0c109e49bcc4ab83b6b35870077c91033b7f',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__repr__default_fn',
    ),
    cls_names=(
        ('omlish.specs.openapi.openapi', 'License'),
    ),
)
def _process_dataclass__87af0c109e49bcc4ab83b6b35870077c91033b7f():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
        __dataclass__repr__default_fn,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                name=self.name,
                identifier=self.identifier,
                url=self.url,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.name == other.name and
                self.identifier == other.identifier and
                self.url == other.url
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'name',
            'identifier',
            'url',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'name',
            'identifier',
            'url',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.name,
                self.identifier,
                self.url,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            name: __dataclass__init__fields__0__annotation,
            identifier: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            url: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'identifier', identifier)
            __dataclass__object_setattr(self, 'url', url)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__default_fn(self.name)) is not None:
                parts.append(f"name={s}")
            if (s := __dataclass__repr__default_fn(self.identifier)) is not None:
                parts.append(f"identifier={s}")
            if (s := __dataclass__repr__default_fn(self.url)) is not None:
                parts.append(f"url={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('operation_ref', 'operation_id', 'parameters', 'request_body', 'description', 'ser"
        "ver')), EqPlan(fields=('operation_ref', 'operation_id', 'parameters', 'request_body', 'description', 'server')"
        "), FrozenPlan(fields=('operation_ref', 'operation_id', 'parameters', 'request_body', 'description', 'server'),"
        " allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('operation_ref', 'operation_id', 'parameter"
        "s', 'request_body', 'description', 'server'), cache=False), InitPlan(fields=(InitPlan.Field(name='operation_re"
        "f', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'), default_fa"
        "ctory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=N"
        "one), InitPlan.Field(name='operation_id', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(nam"
        "e='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, co"
        "erce=None, validate=None, check_type=None), InitPlan.Field(name='parameters', annotation=OpRef(name='init.fiel"
        "ds.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=Fals"
        "e, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='request_b"
        "ody', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_"
        "factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type"
        "=None), InitPlan.Field(name='description', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(na"
        "me='init.fields.4.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, c"
        "oerce=None, validate=None, check_type=None), InitPlan.Field(name='server', annotation=OpRef(name='init.fields."
        "5.annotation'), default=OpRef(name='init.fields.5.default'), default_factory=None, init=True, override=False, "
        "field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=('"
        "operation_ref', 'operation_id', 'parameters', 'request_body', 'description', 'server'), kw_only_params=(), fro"
        "zen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(n"
        "ame='operation_ref', kw_only=False, fn=None), ReprPlan.Field(name='operation_id', kw_only=False, fn=None), Rep"
        "rPlan.Field(name='parameters', kw_only=False, fn=None), ReprPlan.Field(name='request_body', kw_only=False, fn="
        "None), ReprPlan.Field(name='description', kw_only=False, fn=None), ReprPlan.Field(name='server', kw_only=False"
        ", fn=None)), id=False, terse=False, default_fn=OpRef(name='repr.default_fn'))))"
    ),
    plan_repr_sha1='68f380551d5fcf6a7b62539649fb8a049f38e6a8',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__4__default',
        '__dataclass__init__fields__5__annotation',
        '__dataclass__init__fields__5__default',
        '__dataclass__repr__default_fn',
    ),
    cls_names=(
        ('omlish.specs.openapi.openapi', 'Link'),
    ),
)
def _process_dataclass__68f380551d5fcf6a7b62539649fb8a049f38e6a8():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__3__default,
        __dataclass__init__fields__4__annotation,
        __dataclass__init__fields__4__default,
        __dataclass__init__fields__5__annotation,
        __dataclass__init__fields__5__default,
        __dataclass__repr__default_fn,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                operation_ref=self.operation_ref,
                operation_id=self.operation_id,
                parameters=self.parameters,
                request_body=self.request_body,
                description=self.description,
                server=self.server,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.operation_ref == other.operation_ref and
                self.operation_id == other.operation_id and
                self.parameters == other.parameters and
                self.request_body == other.request_body and
                self.description == other.description and
                self.server == other.server
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'operation_ref',
            'operation_id',
            'parameters',
            'request_body',
            'description',
            'server',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'operation_ref',
            'operation_id',
            'parameters',
            'request_body',
            'description',
            'server',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.operation_ref,
                self.operation_id,
                self.parameters,
                self.request_body,
                self.description,
                self.server,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            operation_ref: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            operation_id: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            parameters: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            request_body: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            description: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            server: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'operation_ref', operation_ref)
            __dataclass__object_setattr(self, 'operation_id', operation_id)
            __dataclass__object_setattr(self, 'parameters', parameters)
            __dataclass__object_setattr(self, 'request_body', request_body)
            __dataclass__object_setattr(self, 'description', description)
            __dataclass__object_setattr(self, 'server', server)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__default_fn(self.operation_ref)) is not None:
                parts.append(f"operation_ref={s}")
            if (s := __dataclass__repr__default_fn(self.operation_id)) is not None:
                parts.append(f"operation_id={s}")
            if (s := __dataclass__repr__default_fn(self.parameters)) is not None:
                parts.append(f"parameters={s}")
            if (s := __dataclass__repr__default_fn(self.request_body)) is not None:
                parts.append(f"request_body={s}")
            if (s := __dataclass__repr__default_fn(self.description)) is not None:
                parts.append(f"description={s}")
            if (s := __dataclass__repr__default_fn(self.server)) is not None:
                parts.append(f"server={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('schema', 'example', 'examples', 'encoding')), EqPlan(fields=('schema', 'example',"
        " 'examples', 'encoding')), FrozenPlan(fields=('schema', 'example', 'examples', 'encoding'), allow_dynamic_dund"
        "er_attrs=False), HashPlan(action='add', fields=('schema', 'example', 'examples', 'encoding'), cache=False), In"
        "itPlan(fields=(InitPlan.Field(name='schema', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef("
        "name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE,"
        " coerce=None, validate=None, check_type=None), InitPlan.Field(name='example', annotation=OpRef(name='init.fiel"
        "ds.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=Fals"
        "e, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='examples'"
        ", annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_fact"
        "ory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=Non"
        "e), InitPlan.Field(name='encoding', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='ini"
        "t.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=N"
        "one, validate=None, check_type=None)), self_param='self', std_params=('schema', 'example', 'examples', 'encodi"
        "ng'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprP"
        "lan(fields=(ReprPlan.Field(name='schema', kw_only=False, fn=None), ReprPlan.Field(name='example', kw_only=Fals"
        "e, fn=None), ReprPlan.Field(name='examples', kw_only=False, fn=None), ReprPlan.Field(name='encoding', kw_only="
        "False, fn=None)), id=False, terse=False, default_fn=OpRef(name='repr.default_fn'))))"
    ),
    plan_repr_sha1='0c0080dfcfaf4cc95b55cdf6b5b5909bc1125e15',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
        '__dataclass__repr__default_fn',
    ),
    cls_names=(
        ('omlish.specs.openapi.openapi', 'MediaType'),
    ),
)
def _process_dataclass__0c0080dfcfaf4cc95b55cdf6b5b5909bc1125e15():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__3__default,
        __dataclass__repr__default_fn,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                schema=self.schema,
                example=self.example,
                examples=self.examples,
                encoding=self.encoding,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.schema == other.schema and
                self.example == other.example and
                self.examples == other.examples and
                self.encoding == other.encoding
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'schema',
            'example',
            'examples',
            'encoding',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'schema',
            'example',
            'examples',
            'encoding',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.schema,
                self.example,
                self.examples,
                self.encoding,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            schema: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            example: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            examples: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            encoding: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'schema', schema)
            __dataclass__object_setattr(self, 'example', example)
            __dataclass__object_setattr(self, 'examples', examples)
            __dataclass__object_setattr(self, 'encoding', encoding)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__default_fn(self.schema)) is not None:
                parts.append(f"schema={s}")
            if (s := __dataclass__repr__default_fn(self.example)) is not None:
                parts.append(f"example={s}")
            if (s := __dataclass__repr__default_fn(self.examples)) is not None:
                parts.append(f"examples={s}")
            if (s := __dataclass__repr__default_fn(self.encoding)) is not None:
                parts.append(f"encoding={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('authorization_url', 'token_url', 'scopes', 'refresh_ur')), EqPlan(fields=('author"
        "ization_url', 'token_url', 'scopes', 'refresh_ur')), FrozenPlan(fields=('authorization_url', 'token_url', 'sco"
        "pes', 'refresh_ur'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('authorization_url', 't"
        "oken_url', 'scopes', 'refresh_ur'), cache=False), InitPlan(fields=(InitPlan.Field(name='authorization_url', an"
        "notation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False"
        ", field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='token_url'"
        ", annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=F"
        "alse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='scopes"
        "', annotation=OpRef(name='init.fields.2.annotation'), default=None, default_factory=None, init=True, override="
        "False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='refre"
        "sh_ur', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), defaul"
        "t_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_ty"
        "pe=None)), self_param='self', std_params=('authorization_url', 'token_url', 'scopes', 'refresh_ur'), kw_only_p"
        "arams=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(Rep"
        "rPlan.Field(name='authorization_url', kw_only=False, fn=None), ReprPlan.Field(name='token_url', kw_only=False,"
        " fn=None), ReprPlan.Field(name='scopes', kw_only=False, fn=None), ReprPlan.Field(name='refresh_ur', kw_only=Fa"
        "lse, fn=None)), id=False, terse=False, default_fn=OpRef(name='repr.default_fn'))))"
    ),
    plan_repr_sha1='f66d1979aaf6ccb54ddc86ecad04e787f2d5b154',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
        '__dataclass__repr__default_fn',
    ),
    cls_names=(
        ('omlish.specs.openapi.openapi', 'OauthFlow'),
    ),
)
def _process_dataclass__f66d1979aaf6ccb54ddc86ecad04e787f2d5b154():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__3__default,
        __dataclass__repr__default_fn,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                authorization_url=self.authorization_url,
                token_url=self.token_url,
                scopes=self.scopes,
                refresh_ur=self.refresh_ur,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.authorization_url == other.authorization_url and
                self.token_url == other.token_url and
                self.scopes == other.scopes and
                self.refresh_ur == other.refresh_ur
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'authorization_url',
            'token_url',
            'scopes',
            'refresh_ur',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'authorization_url',
            'token_url',
            'scopes',
            'refresh_ur',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.authorization_url,
                self.token_url,
                self.scopes,
                self.refresh_ur,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            authorization_url: __dataclass__init__fields__0__annotation,
            token_url: __dataclass__init__fields__1__annotation,
            scopes: __dataclass__init__fields__2__annotation,
            refresh_ur: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'authorization_url', authorization_url)
            __dataclass__object_setattr(self, 'token_url', token_url)
            __dataclass__object_setattr(self, 'scopes', scopes)
            __dataclass__object_setattr(self, 'refresh_ur', refresh_ur)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__default_fn(self.authorization_url)) is not None:
                parts.append(f"authorization_url={s}")
            if (s := __dataclass__repr__default_fn(self.token_url)) is not None:
                parts.append(f"token_url={s}")
            if (s := __dataclass__repr__default_fn(self.scopes)) is not None:
                parts.append(f"scopes={s}")
            if (s := __dataclass__repr__default_fn(self.refresh_ur)) is not None:
                parts.append(f"refresh_ur={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('implicit', 'password', 'client_credentials', 'authorization_code')), EqPlan(field"
        "s=('implicit', 'password', 'client_credentials', 'authorization_code')), FrozenPlan(fields=('implicit', 'passw"
        "ord', 'client_credentials', 'authorization_code'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', f"
        "ields=('implicit', 'password', 'client_credentials', 'authorization_code'), cache=False), InitPlan(fields=(Ini"
        "tPlan.Field(name='implicit', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.field"
        "s.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, va"
        "lidate=None, check_type=None), InitPlan.Field(name='password', annotation=OpRef(name='init.fields.1.annotation"
        "'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=F"
        "ieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='client_credentials', ann"
        "otation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=N"
        "one, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), I"
        "nitPlan.Field(name='authorization_code', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name"
        "='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coe"
        "rce=None, validate=None, check_type=None)), self_param='self', std_params=('implicit', 'password', 'client_cre"
        "dentials', 'authorization_code'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns"
        "=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='implicit', kw_only=False, fn=None), ReprPlan.Fiel"
        "d(name='password', kw_only=False, fn=None), ReprPlan.Field(name='client_credentials', kw_only=False, fn=None),"
        " ReprPlan.Field(name='authorization_code', kw_only=False, fn=None)), id=False, terse=False, default_fn=OpRef(n"
        "ame='repr.default_fn'))))"
    ),
    plan_repr_sha1='c2628e645062ee631a5099d82bc8fbbcd320b6c0',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
        '__dataclass__repr__default_fn',
    ),
    cls_names=(
        ('omlish.specs.openapi.openapi', 'OauthFlows'),
    ),
)
def _process_dataclass__c2628e645062ee631a5099d82bc8fbbcd320b6c0():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__3__default,
        __dataclass__repr__default_fn,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                implicit=self.implicit,
                password=self.password,
                client_credentials=self.client_credentials,
                authorization_code=self.authorization_code,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.implicit == other.implicit and
                self.password == other.password and
                self.client_credentials == other.client_credentials and
                self.authorization_code == other.authorization_code
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'implicit',
            'password',
            'client_credentials',
            'authorization_code',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'implicit',
            'password',
            'client_credentials',
            'authorization_code',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.implicit,
                self.password,
                self.client_credentials,
                self.authorization_code,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            implicit: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            password: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            client_credentials: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            authorization_code: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'implicit', implicit)
            __dataclass__object_setattr(self, 'password', password)
            __dataclass__object_setattr(self, 'client_credentials', client_credentials)
            __dataclass__object_setattr(self, 'authorization_code', authorization_code)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__default_fn(self.implicit)) is not None:
                parts.append(f"implicit={s}")
            if (s := __dataclass__repr__default_fn(self.password)) is not None:
                parts.append(f"password={s}")
            if (s := __dataclass__repr__default_fn(self.client_credentials)) is not None:
                parts.append(f"client_credentials={s}")
            if (s := __dataclass__repr__default_fn(self.authorization_code)) is not None:
                parts.append(f"authorization_code={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('openapi', 'info', 'json_schema_dialect', 'servers', 'paths', 'webhooks', 'compone"
        "nts', 'security', 'tags', 'external_docs', 'x')), EqPlan(fields=('openapi', 'info', 'json_schema_dialect', 'se"
        "rvers', 'paths', 'webhooks', 'components', 'security', 'tags', 'external_docs', 'x')), FrozenPlan(fields=('ope"
        "napi', 'info', 'json_schema_dialect', 'servers', 'paths', 'webhooks', 'components', 'security', 'tags', 'exter"
        "nal_docs', 'x'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('openapi', 'info', 'json_sc"
        "hema_dialect', 'servers', 'paths', 'webhooks', 'components', 'security', 'tags', 'external_docs', 'x'), cache="
        "False), InitPlan(fields=(InitPlan.Field(name='openapi', annotation=OpRef(name='init.fields.00.annotation'), de"
        "fault=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valid"
        "ate=None, check_type=None), InitPlan.Field(name='info', annotation=OpRef(name='init.fields.01.annotation'), de"
        "fault=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valid"
        "ate=None, check_type=None), InitPlan.Field(name='json_schema_dialect', annotation=OpRef(name='init.fields.02.a"
        "nnotation'), default=OpRef(name='init.fields.02.default'), default_factory=None, init=True, override=False, fi"
        "eld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='servers', anno"
        "tation=OpRef(name='init.fields.03.annotation'), default=OpRef(name='init.fields.03.default'), default_factory="
        "None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), "
        "InitPlan.Field(name='paths', annotation=OpRef(name='init.fields.04.annotation'), default=OpRef(name='init.fiel"
        "ds.04.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, "
        "validate=None, check_type=None), InitPlan.Field(name='webhooks', annotation=OpRef(name='init.fields.05.annotat"
        "ion'), default=OpRef(name='init.fields.05.default'), default_factory=None, init=True, override=False, field_ty"
        "pe=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='components', annotat"
        "ion=OpRef(name='init.fields.06.annotation'), default=OpRef(name='init.fields.06.default'), default_factory=Non"
        "e, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), Ini"
        "tPlan.Field(name='security', annotation=OpRef(name='init.fields.07.annotation'), default=OpRef(name='init.fiel"
        "ds.07.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, "
        "validate=None, check_type=None), InitPlan.Field(name='tags', annotation=OpRef(name='init.fields.08.annotation'"
        "), default=OpRef(name='init.fields.08.default'), default_factory=None, init=True, override=False, field_type=F"
        "ieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='external_docs', annotati"
        "on=OpRef(name='init.fields.09.annotation'), default=OpRef(name='init.fields.09.default'), default_factory=None"
        ", init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), Init"
        "Plan.Field(name='x', annotation=OpRef(name='init.fields.10.annotation'), default=OpRef(name='init.fields.10.de"
        "fault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate"
        "=None, check_type=None)), self_param='self', std_params=('openapi', 'info', 'json_schema_dialect', 'servers', "
        "'paths', 'webhooks', 'components', 'security', 'tags', 'external_docs', 'x'), kw_only_params=(), frozen=True, "
        "slots=False, post_init_params=None, init_fns=(OpRef(name='init.init_fns.0'),), validate_fns=()), ReprPlan(fiel"
        "ds=(ReprPlan.Field(name='openapi', kw_only=False, fn=None), ReprPlan.Field(name='info', kw_only=False, fn=None"
        "), ReprPlan.Field(name='json_schema_dialect', kw_only=False, fn=None), ReprPlan.Field(name='servers', kw_only="
        "False, fn=None), ReprPlan.Field(name='paths', kw_only=False, fn=None), ReprPlan.Field(name='webhooks', kw_only"
        "=False, fn=None), ReprPlan.Field(name='components', kw_only=False, fn=None), ReprPlan.Field(name='security', k"
        "w_only=False, fn=None), ReprPlan.Field(name='tags', kw_only=False, fn=None), ReprPlan.Field(name='external_doc"
        "s', kw_only=False, fn=None), ReprPlan.Field(name='x', kw_only=False, fn=None)), id=False, terse=False, default"
        "_fn=OpRef(name='repr.default_fn'))))"
    ),
    plan_repr_sha1='005124240f699ee17389834eb8ae96f50e1bc933',
    op_ref_idents=(
        '__dataclass__init__fields__00__annotation',
        '__dataclass__init__fields__01__annotation',
        '__dataclass__init__fields__02__annotation',
        '__dataclass__init__fields__02__default',
        '__dataclass__init__fields__03__annotation',
        '__dataclass__init__fields__03__default',
        '__dataclass__init__fields__04__annotation',
        '__dataclass__init__fields__04__default',
        '__dataclass__init__fields__05__annotation',
        '__dataclass__init__fields__05__default',
        '__dataclass__init__fields__06__annotation',
        '__dataclass__init__fields__06__default',
        '__dataclass__init__fields__07__annotation',
        '__dataclass__init__fields__07__default',
        '__dataclass__init__fields__08__annotation',
        '__dataclass__init__fields__08__default',
        '__dataclass__init__fields__09__annotation',
        '__dataclass__init__fields__09__default',
        '__dataclass__init__fields__10__annotation',
        '__dataclass__init__fields__10__default',
        '__dataclass__init__init_fns__0',
        '__dataclass__repr__default_fn',
    ),
    cls_names=(
        ('omlish.specs.openapi.openapi', 'Openapi'),
    ),
)
def _process_dataclass__005124240f699ee17389834eb8ae96f50e1bc933():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__00__annotation,
        __dataclass__init__fields__01__annotation,
        __dataclass__init__fields__02__annotation,
        __dataclass__init__fields__02__default,
        __dataclass__init__fields__03__annotation,
        __dataclass__init__fields__03__default,
        __dataclass__init__fields__04__annotation,
        __dataclass__init__fields__04__default,
        __dataclass__init__fields__05__annotation,
        __dataclass__init__fields__05__default,
        __dataclass__init__fields__06__annotation,
        __dataclass__init__fields__06__default,
        __dataclass__init__fields__07__annotation,
        __dataclass__init__fields__07__default,
        __dataclass__init__fields__08__annotation,
        __dataclass__init__fields__08__default,
        __dataclass__init__fields__09__annotation,
        __dataclass__init__fields__09__default,
        __dataclass__init__fields__10__annotation,
        __dataclass__init__fields__10__default,
        __dataclass__init__init_fns__0,
        __dataclass__repr__default_fn,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                openapi=self.openapi,
                info=self.info,
                json_schema_dialect=self.json_schema_dialect,
                servers=self.servers,
                paths=self.paths,
                webhooks=self.webhooks,
                components=self.components,
                security=self.security,
                tags=self.tags,
                external_docs=self.external_docs,
                x=self.x,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.openapi == other.openapi and
                self.info == other.info and
                self.json_schema_dialect == other.json_schema_dialect and
                self.servers == other.servers and
                self.paths == other.paths and
                self.webhooks == other.webhooks and
                self.components == other.components and
                self.security == other.security and
                self.tags == other.tags and
                self.external_docs == other.external_docs and
                self.x == other.x
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'openapi',
            'info',
            'json_schema_dialect',
            'servers',
            'paths',
            'webhooks',
            'components',
            'security',
            'tags',
            'external_docs',
            'x',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'openapi',
            'info',
            'json_schema_dialect',
            'servers',
            'paths',
            'webhooks',
            'components',
            'security',
            'tags',
            'external_docs',
            'x',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.openapi,
                self.info,
                self.json_schema_dialect,
                self.servers,
                self.paths,
                self.webhooks,
                self.components,
                self.security,
                self.tags,
                self.external_docs,
                self.x,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            openapi: __dataclass__init__fields__00__annotation,
            info: __dataclass__init__fields__01__annotation,
            json_schema_dialect: __dataclass__init__fields__02__annotation = __dataclass__init__fields__02__default,
            servers: __dataclass__init__fields__03__annotation = __dataclass__init__fields__03__default,
            paths: __dataclass__init__fields__04__annotation = __dataclass__init__fields__04__default,
            webhooks: __dataclass__init__fields__05__annotation = __dataclass__init__fields__05__default,
            components: __dataclass__init__fields__06__annotation = __dataclass__init__fields__06__default,
            security: __dataclass__init__fields__07__annotation = __dataclass__init__fields__07__default,
            tags: __dataclass__init__fields__08__annotation = __dataclass__init__fields__08__default,
            external_docs: __dataclass__init__fields__09__annotation = __dataclass__init__fields__09__default,
            x: __dataclass__init__fields__10__annotation = __dataclass__init__fields__10__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'openapi', openapi)
            __dataclass__object_setattr(self, 'info', info)
            __dataclass__object_setattr(self, 'json_schema_dialect', json_schema_dialect)
            __dataclass__object_setattr(self, 'servers', servers)
            __dataclass__object_setattr(self, 'paths', paths)
            __dataclass__object_setattr(self, 'webhooks', webhooks)
            __dataclass__object_setattr(self, 'components', components)
            __dataclass__object_setattr(self, 'security', security)
            __dataclass__object_setattr(self, 'tags', tags)
            __dataclass__object_setattr(self, 'external_docs', external_docs)
            __dataclass__object_setattr(self, 'x', x)
            __dataclass__init__init_fns__0(self)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__default_fn(self.openapi)) is not None:
                parts.append(f"openapi={s}")
            if (s := __dataclass__repr__default_fn(self.info)) is not None:
                parts.append(f"info={s}")
            if (s := __dataclass__repr__default_fn(self.json_schema_dialect)) is not None:
                parts.append(f"json_schema_dialect={s}")
            if (s := __dataclass__repr__default_fn(self.servers)) is not None:
                parts.append(f"servers={s}")
            if (s := __dataclass__repr__default_fn(self.paths)) is not None:
                parts.append(f"paths={s}")
            if (s := __dataclass__repr__default_fn(self.webhooks)) is not None:
                parts.append(f"webhooks={s}")
            if (s := __dataclass__repr__default_fn(self.components)) is not None:
                parts.append(f"components={s}")
            if (s := __dataclass__repr__default_fn(self.security)) is not None:
                parts.append(f"security={s}")
            if (s := __dataclass__repr__default_fn(self.tags)) is not None:
                parts.append(f"tags={s}")
            if (s := __dataclass__repr__default_fn(self.external_docs)) is not None:
                parts.append(f"external_docs={s}")
            if (s := __dataclass__repr__default_fn(self.x)) is not None:
                parts.append(f"x={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('tags', 'summary', 'description', 'external_docs', 'operation_id', 'parameters', '"
        "request_body', 'responses', 'callbacks', 'deprecated', 'security', 'servers', 'x')), EqPlan(fields=('tags', 's"
        "ummary', 'description', 'external_docs', 'operation_id', 'parameters', 'request_body', 'responses', 'callbacks"
        "', 'deprecated', 'security', 'servers', 'x')), FrozenPlan(fields=('tags', 'summary', 'description', 'external_"
        "docs', 'operation_id', 'parameters', 'request_body', 'responses', 'callbacks', 'deprecated', 'security', 'serv"
        "ers', 'x'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('tags', 'summary', 'description'"
        ", 'external_docs', 'operation_id', 'parameters', 'request_body', 'responses', 'callbacks', 'deprecated', 'secu"
        "rity', 'servers', 'x'), cache=False), InitPlan(fields=(InitPlan.Field(name='tags', annotation=OpRef(name='init"
        ".fields.00.annotation'), default=OpRef(name='init.fields.00.default'), default_factory=None, init=True, overri"
        "de=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='su"
        "mmary', annotation=OpRef(name='init.fields.01.annotation'), default=OpRef(name='init.fields.01.default'), defa"
        "ult_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_"
        "type=None), InitPlan.Field(name='description', annotation=OpRef(name='init.fields.02.annotation'), default=OpR"
        "ef(name='init.fields.02.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTA"
        "NCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='external_docs', annotation=OpRef(name="
        "'init.fields.03.annotation'), default=OpRef(name='init.fields.03.default'), default_factory=None, init=True, o"
        "verride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(nam"
        "e='operation_id', annotation=OpRef(name='init.fields.04.annotation'), default=OpRef(name='init.fields.04.defau"
        "lt'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=No"
        "ne, check_type=None), InitPlan.Field(name='parameters', annotation=OpRef(name='init.fields.05.annotation'), de"
        "fault=OpRef(name='init.fields.05.default'), default_factory=None, init=True, override=False, field_type=FieldT"
        "ype.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='request_body', annotation=OpR"
        "ef(name='init.fields.06.annotation'), default=OpRef(name='init.fields.06.default'), default_factory=None, init"
        "=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.F"
        "ield(name='responses', annotation=OpRef(name='init.fields.07.annotation'), default=OpRef(name='init.fields.07."
        "default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valida"
        "te=None, check_type=None), InitPlan.Field(name='callbacks', annotation=OpRef(name='init.fields.08.annotation')"
        ", default=OpRef(name='init.fields.08.default'), default_factory=None, init=True, override=False, field_type=Fi"
        "eldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='deprecated', annotation=O"
        "pRef(name='init.fields.09.annotation'), default=OpRef(name='init.fields.09.default'), default_factory=None, in"
        "it=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan"
        ".Field(name='security', annotation=OpRef(name='init.fields.10.annotation'), default=OpRef(name='init.fields.10"
        ".default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valid"
        "ate=None, check_type=None), InitPlan.Field(name='servers', annotation=OpRef(name='init.fields.11.annotation'),"
        " default=OpRef(name='init.fields.11.default'), default_factory=None, init=True, override=False, field_type=Fie"
        "ldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='x', annotation=OpRef(name="
        "'init.fields.12.annotation'), default=OpRef(name='init.fields.12.default'), default_factory=None, init=True, o"
        "verride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self'"
        ", std_params=('tags', 'summary', 'description', 'external_docs', 'operation_id', 'parameters', 'request_body',"
        " 'responses', 'callbacks', 'deprecated', 'security', 'servers', 'x'), kw_only_params=(), frozen=True, slots=Fa"
        "lse, post_init_params=None, init_fns=(OpRef(name='init.init_fns.0'),), validate_fns=()), ReprPlan(fields=(Repr"
        "Plan.Field(name='tags', kw_only=False, fn=None), ReprPlan.Field(name='summary', kw_only=False, fn=None), ReprP"
        "lan.Field(name='description', kw_only=False, fn=None), ReprPlan.Field(name='external_docs', kw_only=False, fn="
        "None), ReprPlan.Field(name='operation_id', kw_only=False, fn=None), ReprPlan.Field(name='parameters', kw_only="
        "False, fn=None), ReprPlan.Field(name='request_body', kw_only=False, fn=None), ReprPlan.Field(name='responses',"
        " kw_only=False, fn=None), ReprPlan.Field(name='callbacks', kw_only=False, fn=None), ReprPlan.Field(name='depre"
        "cated', kw_only=False, fn=None), ReprPlan.Field(name='security', kw_only=False, fn=None), ReprPlan.Field(name="
        "'servers', kw_only=False, fn=None), ReprPlan.Field(name='x', kw_only=False, fn=None)), id=False, terse=False, "
        "default_fn=OpRef(name='repr.default_fn'))))"
    ),
    plan_repr_sha1='8ee4073aac44214f307f150371e41de5d524aa9d',
    op_ref_idents=(
        '__dataclass__init__fields__00__annotation',
        '__dataclass__init__fields__00__default',
        '__dataclass__init__fields__01__annotation',
        '__dataclass__init__fields__01__default',
        '__dataclass__init__fields__02__annotation',
        '__dataclass__init__fields__02__default',
        '__dataclass__init__fields__03__annotation',
        '__dataclass__init__fields__03__default',
        '__dataclass__init__fields__04__annotation',
        '__dataclass__init__fields__04__default',
        '__dataclass__init__fields__05__annotation',
        '__dataclass__init__fields__05__default',
        '__dataclass__init__fields__06__annotation',
        '__dataclass__init__fields__06__default',
        '__dataclass__init__fields__07__annotation',
        '__dataclass__init__fields__07__default',
        '__dataclass__init__fields__08__annotation',
        '__dataclass__init__fields__08__default',
        '__dataclass__init__fields__09__annotation',
        '__dataclass__init__fields__09__default',
        '__dataclass__init__fields__10__annotation',
        '__dataclass__init__fields__10__default',
        '__dataclass__init__fields__11__annotation',
        '__dataclass__init__fields__11__default',
        '__dataclass__init__fields__12__annotation',
        '__dataclass__init__fields__12__default',
        '__dataclass__init__init_fns__0',
        '__dataclass__repr__default_fn',
    ),
    cls_names=(
        ('omlish.specs.openapi.openapi', 'Operation'),
    ),
)
def _process_dataclass__8ee4073aac44214f307f150371e41de5d524aa9d():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__00__annotation,
        __dataclass__init__fields__00__default,
        __dataclass__init__fields__01__annotation,
        __dataclass__init__fields__01__default,
        __dataclass__init__fields__02__annotation,
        __dataclass__init__fields__02__default,
        __dataclass__init__fields__03__annotation,
        __dataclass__init__fields__03__default,
        __dataclass__init__fields__04__annotation,
        __dataclass__init__fields__04__default,
        __dataclass__init__fields__05__annotation,
        __dataclass__init__fields__05__default,
        __dataclass__init__fields__06__annotation,
        __dataclass__init__fields__06__default,
        __dataclass__init__fields__07__annotation,
        __dataclass__init__fields__07__default,
        __dataclass__init__fields__08__annotation,
        __dataclass__init__fields__08__default,
        __dataclass__init__fields__09__annotation,
        __dataclass__init__fields__09__default,
        __dataclass__init__fields__10__annotation,
        __dataclass__init__fields__10__default,
        __dataclass__init__fields__11__annotation,
        __dataclass__init__fields__11__default,
        __dataclass__init__fields__12__annotation,
        __dataclass__init__fields__12__default,
        __dataclass__init__init_fns__0,
        __dataclass__repr__default_fn,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                tags=self.tags,
                summary=self.summary,
                description=self.description,
                external_docs=self.external_docs,
                operation_id=self.operation_id,
                parameters=self.parameters,
                request_body=self.request_body,
                responses=self.responses,
                callbacks=self.callbacks,
                deprecated=self.deprecated,
                security=self.security,
                servers=self.servers,
                x=self.x,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.tags == other.tags and
                self.summary == other.summary and
                self.description == other.description and
                self.external_docs == other.external_docs and
                self.operation_id == other.operation_id and
                self.parameters == other.parameters and
                self.request_body == other.request_body and
                self.responses == other.responses and
                self.callbacks == other.callbacks and
                self.deprecated == other.deprecated and
                self.security == other.security and
                self.servers == other.servers and
                self.x == other.x
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'tags',
            'summary',
            'description',
            'external_docs',
            'operation_id',
            'parameters',
            'request_body',
            'responses',
            'callbacks',
            'deprecated',
            'security',
            'servers',
            'x',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'tags',
            'summary',
            'description',
            'external_docs',
            'operation_id',
            'parameters',
            'request_body',
            'responses',
            'callbacks',
            'deprecated',
            'security',
            'servers',
            'x',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.tags,
                self.summary,
                self.description,
                self.external_docs,
                self.operation_id,
                self.parameters,
                self.request_body,
                self.responses,
                self.callbacks,
                self.deprecated,
                self.security,
                self.servers,
                self.x,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            tags: __dataclass__init__fields__00__annotation = __dataclass__init__fields__00__default,
            summary: __dataclass__init__fields__01__annotation = __dataclass__init__fields__01__default,
            description: __dataclass__init__fields__02__annotation = __dataclass__init__fields__02__default,
            external_docs: __dataclass__init__fields__03__annotation = __dataclass__init__fields__03__default,
            operation_id: __dataclass__init__fields__04__annotation = __dataclass__init__fields__04__default,
            parameters: __dataclass__init__fields__05__annotation = __dataclass__init__fields__05__default,
            request_body: __dataclass__init__fields__06__annotation = __dataclass__init__fields__06__default,
            responses: __dataclass__init__fields__07__annotation = __dataclass__init__fields__07__default,
            callbacks: __dataclass__init__fields__08__annotation = __dataclass__init__fields__08__default,
            deprecated: __dataclass__init__fields__09__annotation = __dataclass__init__fields__09__default,
            security: __dataclass__init__fields__10__annotation = __dataclass__init__fields__10__default,
            servers: __dataclass__init__fields__11__annotation = __dataclass__init__fields__11__default,
            x: __dataclass__init__fields__12__annotation = __dataclass__init__fields__12__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'tags', tags)
            __dataclass__object_setattr(self, 'summary', summary)
            __dataclass__object_setattr(self, 'description', description)
            __dataclass__object_setattr(self, 'external_docs', external_docs)
            __dataclass__object_setattr(self, 'operation_id', operation_id)
            __dataclass__object_setattr(self, 'parameters', parameters)
            __dataclass__object_setattr(self, 'request_body', request_body)
            __dataclass__object_setattr(self, 'responses', responses)
            __dataclass__object_setattr(self, 'callbacks', callbacks)
            __dataclass__object_setattr(self, 'deprecated', deprecated)
            __dataclass__object_setattr(self, 'security', security)
            __dataclass__object_setattr(self, 'servers', servers)
            __dataclass__object_setattr(self, 'x', x)
            __dataclass__init__init_fns__0(self)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__default_fn(self.tags)) is not None:
                parts.append(f"tags={s}")
            if (s := __dataclass__repr__default_fn(self.summary)) is not None:
                parts.append(f"summary={s}")
            if (s := __dataclass__repr__default_fn(self.description)) is not None:
                parts.append(f"description={s}")
            if (s := __dataclass__repr__default_fn(self.external_docs)) is not None:
                parts.append(f"external_docs={s}")
            if (s := __dataclass__repr__default_fn(self.operation_id)) is not None:
                parts.append(f"operation_id={s}")
            if (s := __dataclass__repr__default_fn(self.parameters)) is not None:
                parts.append(f"parameters={s}")
            if (s := __dataclass__repr__default_fn(self.request_body)) is not None:
                parts.append(f"request_body={s}")
            if (s := __dataclass__repr__default_fn(self.responses)) is not None:
                parts.append(f"responses={s}")
            if (s := __dataclass__repr__default_fn(self.callbacks)) is not None:
                parts.append(f"callbacks={s}")
            if (s := __dataclass__repr__default_fn(self.deprecated)) is not None:
                parts.append(f"deprecated={s}")
            if (s := __dataclass__repr__default_fn(self.security)) is not None:
                parts.append(f"security={s}")
            if (s := __dataclass__repr__default_fn(self.servers)) is not None:
                parts.append(f"servers={s}")
            if (s := __dataclass__repr__default_fn(self.x)) is not None:
                parts.append(f"x={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('name', 'in_', 'common')), EqPlan(fields=('name', 'in_', 'common')), FrozenPlan(fi"
        "elds=('name', 'in_', 'common'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('name', 'in_"
        "', 'common'), cache=False), InitPlan(fields=(InitPlan.Field(name='name', annotation=OpRef(name='init.fields.0."
        "annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, co"
        "erce=None, validate=None, check_type=None), InitPlan.Field(name='in_', annotation=OpRef(name='init.fields.1.an"
        "notation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coer"
        "ce=None, validate=None, check_type=None), InitPlan.Field(name='common', annotation=OpRef(name='init.fields.2.a"
        "nnotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coe"
        "rce=None, validate=None, check_type=None)), self_param='self', std_params=('name', 'in_', 'common'), kw_only_p"
        "arams=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(Rep"
        "rPlan.Field(name='name', kw_only=False, fn=None), ReprPlan.Field(name='in_', kw_only=False, fn=None), ReprPlan"
        ".Field(name='common', kw_only=False, fn=None)), id=False, terse=False, default_fn=OpRef(name='repr.default_fn'"
        "))))"
    ),
    plan_repr_sha1='413190da51b24ddc1aa6c3e244090f3d38971a03',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__repr__default_fn',
    ),
    cls_names=(
        ('omlish.specs.openapi.openapi', 'Parameter'),
    ),
)
def _process_dataclass__413190da51b24ddc1aa6c3e244090f3d38971a03():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__repr__default_fn,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                name=self.name,
                in_=self.in_,
                common=self.common,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.name == other.name and
                self.in_ == other.in_ and
                self.common == other.common
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'name',
            'in_',
            'common',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'name',
            'in_',
            'common',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.name,
                self.in_,
                self.common,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            name: __dataclass__init__fields__0__annotation,
            in_: __dataclass__init__fields__1__annotation,
            common: __dataclass__init__fields__2__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'in_', in_)
            __dataclass__object_setattr(self, 'common', common)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__default_fn(self.name)) is not None:
                parts.append(f"name={s}")
            if (s := __dataclass__repr__default_fn(self.in_)) is not None:
                parts.append(f"in_={s}")
            if (s := __dataclass__repr__default_fn(self.common)) is not None:
                parts.append(f"common={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('description', 'required', 'deprecated', 'allow_empty_value', 'style', 'explode', "
        "'allow_reserved', 'schema', 'example', 'examples', 'content', 'matrix', 'label', 'form', 'simple', 'space_deli"
        "mited', 'pipe_delimited', 'deep_object')), EqPlan(fields=('description', 'required', 'deprecated', 'allow_empt"
        "y_value', 'style', 'explode', 'allow_reserved', 'schema', 'example', 'examples', 'content', 'matrix', 'label',"
        " 'form', 'simple', 'space_delimited', 'pipe_delimited', 'deep_object')), FrozenPlan(fields=('description', 're"
        "quired', 'deprecated', 'allow_empty_value', 'style', 'explode', 'allow_reserved', 'schema', 'example', 'exampl"
        "es', 'content', 'matrix', 'label', 'form', 'simple', 'space_delimited', 'pipe_delimited', 'deep_object'), allo"
        "w_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('description', 'required', 'deprecated', 'allow_"
        "empty_value', 'style', 'explode', 'allow_reserved', 'schema', 'example', 'examples', 'content', 'matrix', 'lab"
        "el', 'form', 'simple', 'space_delimited', 'pipe_delimited', 'deep_object'), cache=False), InitPlan(fields=(Ini"
        "tPlan.Field(name='description', annotation=OpRef(name='init.fields.00.annotation'), default=OpRef(name='init.f"
        "ields.00.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=Non"
        "e, validate=None, check_type=None), InitPlan.Field(name='required', annotation=OpRef(name='init.fields.01.anno"
        "tation'), default=OpRef(name='init.fields.01.default'), default_factory=None, init=True, override=False, field"
        "_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='deprecated', anno"
        "tation=OpRef(name='init.fields.02.annotation'), default=OpRef(name='init.fields.02.default'), default_factory="
        "None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), "
        "InitPlan.Field(name='allow_empty_value', annotation=OpRef(name='init.fields.03.annotation'), default=OpRef(nam"
        "e='init.fields.03.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, c"
        "oerce=None, validate=None, check_type=None), InitPlan.Field(name='style', annotation=OpRef(name='init.fields.0"
        "4.annotation'), default=OpRef(name='init.fields.04.default'), default_factory=None, init=True, override=False,"
        " field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='explode', a"
        "nnotation=OpRef(name='init.fields.05.annotation'), default=OpRef(name='init.fields.05.default'), default_facto"
        "ry=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None"
        "), InitPlan.Field(name='allow_reserved', annotation=OpRef(name='init.fields.06.annotation'), default=OpRef(nam"
        "e='init.fields.06.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, c"
        "oerce=None, validate=None, check_type=None), InitPlan.Field(name='schema', annotation=OpRef(name='init.fields."
        "07.annotation'), default=OpRef(name='init.fields.07.default'), default_factory=None, init=True, override=False"
        ", field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='example', "
        "annotation=OpRef(name='init.fields.08.annotation'), default=OpRef(name='init.fields.08.default'), default_fact"
        "ory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=Non"
        "e), InitPlan.Field(name='examples', annotation=OpRef(name='init.fields.09.annotation'), default=OpRef(name='in"
        "it.fields.09.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce"
        "=None, validate=None, check_type=None), InitPlan.Field(name='content', annotation=OpRef(name='init.fields.10.a"
        "nnotation'), default=OpRef(name='init.fields.10.default'), default_factory=None, init=True, override=False, fi"
        "eld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='matrix', annot"
        "ation=OpRef(name='init.fields.11.annotation'), default=OpRef(name='init.fields.11.default'), default_factory=N"
        "one, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), I"
        "nitPlan.Field(name='label', annotation=OpRef(name='init.fields.12.annotation'), default=OpRef(name='init.field"
        "s.12.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, v"
        "alidate=None, check_type=None), InitPlan.Field(name='form', annotation=OpRef(name='init.fields.13.annotation')"
        ", default=OpRef(name='init.fields.13.default'), default_factory=None, init=True, override=False, field_type=Fi"
        "eldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='simple', annotation=OpRef"
        "(name='init.fields.14.annotation'), default=OpRef(name='init.fields.14.default'), default_factory=None, init=T"
        "rue, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fie"
        "ld(name='space_delimited', annotation=OpRef(name='init.fields.15.annotation'), default=OpRef(name='init.fields"
        ".15.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, va"
        "lidate=None, check_type=None), InitPlan.Field(name='pipe_delimited', annotation=OpRef(name='init.fields.16.ann"
        "otation'), default=OpRef(name='init.fields.16.default'), default_factory=None, init=True, override=False, fiel"
        "d_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='deep_object', an"
        "notation=OpRef(name='init.fields.17.annotation'), default=OpRef(name='init.fields.17.default'), default_factor"
        "y=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)"
        "), self_param='self', std_params=('description', 'required', 'deprecated', 'allow_empty_value', 'style', 'expl"
        "ode', 'allow_reserved', 'schema', 'example', 'examples', 'content', 'matrix', 'label', 'form', 'simple', 'spac"
        "e_delimited', 'pipe_delimited', 'deep_object'), kw_only_params=(), frozen=True, slots=False, post_init_params="
        "None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='description', kw_only=False, fn=Non"
        "e), ReprPlan.Field(name='required', kw_only=False, fn=None), ReprPlan.Field(name='deprecated', kw_only=False, "
        "fn=None), ReprPlan.Field(name='allow_empty_value', kw_only=False, fn=None), ReprPlan.Field(name='style', kw_on"
        "ly=False, fn=None), ReprPlan.Field(name='explode', kw_only=False, fn=None), ReprPlan.Field(name='allow_reserve"
        "d', kw_only=False, fn=None), ReprPlan.Field(name='schema', kw_only=False, fn=None), ReprPlan.Field(name='examp"
        "le', kw_only=False, fn=None), ReprPlan.Field(name='examples', kw_only=False, fn=None), ReprPlan.Field(name='co"
        "ntent', kw_only=False, fn=None), ReprPlan.Field(name='matrix', kw_only=False, fn=None), ReprPlan.Field(name='l"
        "abel', kw_only=False, fn=None), ReprPlan.Field(name='form', kw_only=False, fn=None), ReprPlan.Field(name='simp"
        "le', kw_only=False, fn=None), ReprPlan.Field(name='space_delimited', kw_only=False, fn=None), ReprPlan.Field(n"
        "ame='pipe_delimited', kw_only=False, fn=None), ReprPlan.Field(name='deep_object', kw_only=False, fn=None)), id"
        "=False, terse=False, default_fn=OpRef(name='repr.default_fn'))))"
    ),
    plan_repr_sha1='245ffee6800cd0e12fb4c9b9d49d44fbce1db4b3',
    op_ref_idents=(
        '__dataclass__init__fields__00__annotation',
        '__dataclass__init__fields__00__default',
        '__dataclass__init__fields__01__annotation',
        '__dataclass__init__fields__01__default',
        '__dataclass__init__fields__02__annotation',
        '__dataclass__init__fields__02__default',
        '__dataclass__init__fields__03__annotation',
        '__dataclass__init__fields__03__default',
        '__dataclass__init__fields__04__annotation',
        '__dataclass__init__fields__04__default',
        '__dataclass__init__fields__05__annotation',
        '__dataclass__init__fields__05__default',
        '__dataclass__init__fields__06__annotation',
        '__dataclass__init__fields__06__default',
        '__dataclass__init__fields__07__annotation',
        '__dataclass__init__fields__07__default',
        '__dataclass__init__fields__08__annotation',
        '__dataclass__init__fields__08__default',
        '__dataclass__init__fields__09__annotation',
        '__dataclass__init__fields__09__default',
        '__dataclass__init__fields__10__annotation',
        '__dataclass__init__fields__10__default',
        '__dataclass__init__fields__11__annotation',
        '__dataclass__init__fields__11__default',
        '__dataclass__init__fields__12__annotation',
        '__dataclass__init__fields__12__default',
        '__dataclass__init__fields__13__annotation',
        '__dataclass__init__fields__13__default',
        '__dataclass__init__fields__14__annotation',
        '__dataclass__init__fields__14__default',
        '__dataclass__init__fields__15__annotation',
        '__dataclass__init__fields__15__default',
        '__dataclass__init__fields__16__annotation',
        '__dataclass__init__fields__16__default',
        '__dataclass__init__fields__17__annotation',
        '__dataclass__init__fields__17__default',
        '__dataclass__repr__default_fn',
    ),
    cls_names=(
        ('omlish.specs.openapi.openapi', 'ParameterCommon'),
    ),
)
def _process_dataclass__245ffee6800cd0e12fb4c9b9d49d44fbce1db4b3():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__00__annotation,
        __dataclass__init__fields__00__default,
        __dataclass__init__fields__01__annotation,
        __dataclass__init__fields__01__default,
        __dataclass__init__fields__02__annotation,
        __dataclass__init__fields__02__default,
        __dataclass__init__fields__03__annotation,
        __dataclass__init__fields__03__default,
        __dataclass__init__fields__04__annotation,
        __dataclass__init__fields__04__default,
        __dataclass__init__fields__05__annotation,
        __dataclass__init__fields__05__default,
        __dataclass__init__fields__06__annotation,
        __dataclass__init__fields__06__default,
        __dataclass__init__fields__07__annotation,
        __dataclass__init__fields__07__default,
        __dataclass__init__fields__08__annotation,
        __dataclass__init__fields__08__default,
        __dataclass__init__fields__09__annotation,
        __dataclass__init__fields__09__default,
        __dataclass__init__fields__10__annotation,
        __dataclass__init__fields__10__default,
        __dataclass__init__fields__11__annotation,
        __dataclass__init__fields__11__default,
        __dataclass__init__fields__12__annotation,
        __dataclass__init__fields__12__default,
        __dataclass__init__fields__13__annotation,
        __dataclass__init__fields__13__default,
        __dataclass__init__fields__14__annotation,
        __dataclass__init__fields__14__default,
        __dataclass__init__fields__15__annotation,
        __dataclass__init__fields__15__default,
        __dataclass__init__fields__16__annotation,
        __dataclass__init__fields__16__default,
        __dataclass__init__fields__17__annotation,
        __dataclass__init__fields__17__default,
        __dataclass__repr__default_fn,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                description=self.description,
                required=self.required,
                deprecated=self.deprecated,
                allow_empty_value=self.allow_empty_value,
                style=self.style,
                explode=self.explode,
                allow_reserved=self.allow_reserved,
                schema=self.schema,
                example=self.example,
                examples=self.examples,
                content=self.content,
                matrix=self.matrix,
                label=self.label,
                form=self.form,
                simple=self.simple,
                space_delimited=self.space_delimited,
                pipe_delimited=self.pipe_delimited,
                deep_object=self.deep_object,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.description == other.description and
                self.required == other.required and
                self.deprecated == other.deprecated and
                self.allow_empty_value == other.allow_empty_value and
                self.style == other.style and
                self.explode == other.explode and
                self.allow_reserved == other.allow_reserved and
                self.schema == other.schema and
                self.example == other.example and
                self.examples == other.examples and
                self.content == other.content and
                self.matrix == other.matrix and
                self.label == other.label and
                self.form == other.form and
                self.simple == other.simple and
                self.space_delimited == other.space_delimited and
                self.pipe_delimited == other.pipe_delimited and
                self.deep_object == other.deep_object
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'description',
            'required',
            'deprecated',
            'allow_empty_value',
            'style',
            'explode',
            'allow_reserved',
            'schema',
            'example',
            'examples',
            'content',
            'matrix',
            'label',
            'form',
            'simple',
            'space_delimited',
            'pipe_delimited',
            'deep_object',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'description',
            'required',
            'deprecated',
            'allow_empty_value',
            'style',
            'explode',
            'allow_reserved',
            'schema',
            'example',
            'examples',
            'content',
            'matrix',
            'label',
            'form',
            'simple',
            'space_delimited',
            'pipe_delimited',
            'deep_object',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.description,
                self.required,
                self.deprecated,
                self.allow_empty_value,
                self.style,
                self.explode,
                self.allow_reserved,
                self.schema,
                self.example,
                self.examples,
                self.content,
                self.matrix,
                self.label,
                self.form,
                self.simple,
                self.space_delimited,
                self.pipe_delimited,
                self.deep_object,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            description: __dataclass__init__fields__00__annotation = __dataclass__init__fields__00__default,
            required: __dataclass__init__fields__01__annotation = __dataclass__init__fields__01__default,
            deprecated: __dataclass__init__fields__02__annotation = __dataclass__init__fields__02__default,
            allow_empty_value: __dataclass__init__fields__03__annotation = __dataclass__init__fields__03__default,
            style: __dataclass__init__fields__04__annotation = __dataclass__init__fields__04__default,
            explode: __dataclass__init__fields__05__annotation = __dataclass__init__fields__05__default,
            allow_reserved: __dataclass__init__fields__06__annotation = __dataclass__init__fields__06__default,
            schema: __dataclass__init__fields__07__annotation = __dataclass__init__fields__07__default,
            example: __dataclass__init__fields__08__annotation = __dataclass__init__fields__08__default,
            examples: __dataclass__init__fields__09__annotation = __dataclass__init__fields__09__default,
            content: __dataclass__init__fields__10__annotation = __dataclass__init__fields__10__default,
            matrix: __dataclass__init__fields__11__annotation = __dataclass__init__fields__11__default,
            label: __dataclass__init__fields__12__annotation = __dataclass__init__fields__12__default,
            form: __dataclass__init__fields__13__annotation = __dataclass__init__fields__13__default,
            simple: __dataclass__init__fields__14__annotation = __dataclass__init__fields__14__default,
            space_delimited: __dataclass__init__fields__15__annotation = __dataclass__init__fields__15__default,
            pipe_delimited: __dataclass__init__fields__16__annotation = __dataclass__init__fields__16__default,
            deep_object: __dataclass__init__fields__17__annotation = __dataclass__init__fields__17__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'description', description)
            __dataclass__object_setattr(self, 'required', required)
            __dataclass__object_setattr(self, 'deprecated', deprecated)
            __dataclass__object_setattr(self, 'allow_empty_value', allow_empty_value)
            __dataclass__object_setattr(self, 'style', style)
            __dataclass__object_setattr(self, 'explode', explode)
            __dataclass__object_setattr(self, 'allow_reserved', allow_reserved)
            __dataclass__object_setattr(self, 'schema', schema)
            __dataclass__object_setattr(self, 'example', example)
            __dataclass__object_setattr(self, 'examples', examples)
            __dataclass__object_setattr(self, 'content', content)
            __dataclass__object_setattr(self, 'matrix', matrix)
            __dataclass__object_setattr(self, 'label', label)
            __dataclass__object_setattr(self, 'form', form)
            __dataclass__object_setattr(self, 'simple', simple)
            __dataclass__object_setattr(self, 'space_delimited', space_delimited)
            __dataclass__object_setattr(self, 'pipe_delimited', pipe_delimited)
            __dataclass__object_setattr(self, 'deep_object', deep_object)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__default_fn(self.description)) is not None:
                parts.append(f"description={s}")
            if (s := __dataclass__repr__default_fn(self.required)) is not None:
                parts.append(f"required={s}")
            if (s := __dataclass__repr__default_fn(self.deprecated)) is not None:
                parts.append(f"deprecated={s}")
            if (s := __dataclass__repr__default_fn(self.allow_empty_value)) is not None:
                parts.append(f"allow_empty_value={s}")
            if (s := __dataclass__repr__default_fn(self.style)) is not None:
                parts.append(f"style={s}")
            if (s := __dataclass__repr__default_fn(self.explode)) is not None:
                parts.append(f"explode={s}")
            if (s := __dataclass__repr__default_fn(self.allow_reserved)) is not None:
                parts.append(f"allow_reserved={s}")
            if (s := __dataclass__repr__default_fn(self.schema)) is not None:
                parts.append(f"schema={s}")
            if (s := __dataclass__repr__default_fn(self.example)) is not None:
                parts.append(f"example={s}")
            if (s := __dataclass__repr__default_fn(self.examples)) is not None:
                parts.append(f"examples={s}")
            if (s := __dataclass__repr__default_fn(self.content)) is not None:
                parts.append(f"content={s}")
            if (s := __dataclass__repr__default_fn(self.matrix)) is not None:
                parts.append(f"matrix={s}")
            if (s := __dataclass__repr__default_fn(self.label)) is not None:
                parts.append(f"label={s}")
            if (s := __dataclass__repr__default_fn(self.form)) is not None:
                parts.append(f"form={s}")
            if (s := __dataclass__repr__default_fn(self.simple)) is not None:
                parts.append(f"simple={s}")
            if (s := __dataclass__repr__default_fn(self.space_delimited)) is not None:
                parts.append(f"space_delimited={s}")
            if (s := __dataclass__repr__default_fn(self.pipe_delimited)) is not None:
                parts.append(f"pipe_delimited={s}")
            if (s := __dataclass__repr__default_fn(self.deep_object)) is not None:
                parts.append(f"deep_object={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('ref', 'summary', 'description', 'get', 'put', 'post', 'delete', 'options', 'head'"
        ", 'patch', 'trace', 'servers', 'parameters')), EqPlan(fields=('ref', 'summary', 'description', 'get', 'put', '"
        "post', 'delete', 'options', 'head', 'patch', 'trace', 'servers', 'parameters')), FrozenPlan(fields=('ref', 'su"
        "mmary', 'description', 'get', 'put', 'post', 'delete', 'options', 'head', 'patch', 'trace', 'servers', 'parame"
        "ters'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('ref', 'summary', 'description', 'ge"
        "t', 'put', 'post', 'delete', 'options', 'head', 'patch', 'trace', 'servers', 'parameters'), cache=False), Init"
        "Plan(fields=(InitPlan.Field(name='ref', annotation=OpRef(name='init.fields.00.annotation'), default=OpRef(name"
        "='init.fields.00.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, co"
        "erce=None, validate=None, check_type=None), InitPlan.Field(name='summary', annotation=OpRef(name='init.fields."
        "01.annotation'), default=OpRef(name='init.fields.01.default'), default_factory=None, init=True, override=False"
        ", field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='descriptio"
        "n', annotation=OpRef(name='init.fields.02.annotation'), default=OpRef(name='init.fields.02.default'), default_"
        "factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type"
        "=None), InitPlan.Field(name='get', annotation=OpRef(name='init.fields.03.annotation'), default=OpRef(name='ini"
        "t.fields.03.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce="
        "None, validate=None, check_type=None), InitPlan.Field(name='put', annotation=OpRef(name='init.fields.04.annota"
        "tion'), default=OpRef(name='init.fields.04.default'), default_factory=None, init=True, override=False, field_t"
        "ype=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='post', annotation=O"
        "pRef(name='init.fields.05.annotation'), default=OpRef(name='init.fields.05.default'), default_factory=None, in"
        "it=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan"
        ".Field(name='delete', annotation=OpRef(name='init.fields.06.annotation'), default=OpRef(name='init.fields.06.d"
        "efault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validat"
        "e=None, check_type=None), InitPlan.Field(name='options', annotation=OpRef(name='init.fields.07.annotation'), d"
        "efault=OpRef(name='init.fields.07.default'), default_factory=None, init=True, override=False, field_type=Field"
        "Type.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='head', annotation=OpRef(name"
        "='init.fields.08.annotation'), default=OpRef(name='init.fields.08.default'), default_factory=None, init=True, "
        "override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(na"
        "me='patch', annotation=OpRef(name='init.fields.09.annotation'), default=OpRef(name='init.fields.09.default'), "
        "default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, ch"
        "eck_type=None), InitPlan.Field(name='trace', annotation=OpRef(name='init.fields.10.annotation'), default=OpRef"
        "(name='init.fields.10.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANC"
        "E, coerce=None, validate=None, check_type=None), InitPlan.Field(name='servers', annotation=OpRef(name='init.fi"
        "elds.11.annotation'), default=OpRef(name='init.fields.11.default'), default_factory=None, init=True, override="
        "False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='param"
        "eters', annotation=OpRef(name='init.fields.12.annotation'), default=OpRef(name='init.fields.12.default'), defa"
        "ult_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_"
        "type=None)), self_param='self', std_params=('ref', 'summary', 'description', 'get', 'put', 'post', 'delete', '"
        "options', 'head', 'patch', 'trace', 'servers', 'parameters'), kw_only_params=(), frozen=True, slots=False, pos"
        "t_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='ref', kw_only=False, "
        "fn=None), ReprPlan.Field(name='summary', kw_only=False, fn=None), ReprPlan.Field(name='description', kw_only=F"
        "alse, fn=None), ReprPlan.Field(name='get', kw_only=False, fn=None), ReprPlan.Field(name='put', kw_only=False, "
        "fn=None), ReprPlan.Field(name='post', kw_only=False, fn=None), ReprPlan.Field(name='delete', kw_only=False, fn"
        "=None), ReprPlan.Field(name='options', kw_only=False, fn=None), ReprPlan.Field(name='head', kw_only=False, fn="
        "None), ReprPlan.Field(name='patch', kw_only=False, fn=None), ReprPlan.Field(name='trace', kw_only=False, fn=No"
        "ne), ReprPlan.Field(name='servers', kw_only=False, fn=None), ReprPlan.Field(name='parameters', kw_only=False, "
        "fn=None)), id=False, terse=False, default_fn=OpRef(name='repr.default_fn'))))"
    ),
    plan_repr_sha1='eddcd6e3715fc20c3fab37afd67aa30033d225fb',
    op_ref_idents=(
        '__dataclass__init__fields__00__annotation',
        '__dataclass__init__fields__00__default',
        '__dataclass__init__fields__01__annotation',
        '__dataclass__init__fields__01__default',
        '__dataclass__init__fields__02__annotation',
        '__dataclass__init__fields__02__default',
        '__dataclass__init__fields__03__annotation',
        '__dataclass__init__fields__03__default',
        '__dataclass__init__fields__04__annotation',
        '__dataclass__init__fields__04__default',
        '__dataclass__init__fields__05__annotation',
        '__dataclass__init__fields__05__default',
        '__dataclass__init__fields__06__annotation',
        '__dataclass__init__fields__06__default',
        '__dataclass__init__fields__07__annotation',
        '__dataclass__init__fields__07__default',
        '__dataclass__init__fields__08__annotation',
        '__dataclass__init__fields__08__default',
        '__dataclass__init__fields__09__annotation',
        '__dataclass__init__fields__09__default',
        '__dataclass__init__fields__10__annotation',
        '__dataclass__init__fields__10__default',
        '__dataclass__init__fields__11__annotation',
        '__dataclass__init__fields__11__default',
        '__dataclass__init__fields__12__annotation',
        '__dataclass__init__fields__12__default',
        '__dataclass__repr__default_fn',
    ),
    cls_names=(
        ('omlish.specs.openapi.openapi', 'PathItem'),
    ),
)
def _process_dataclass__eddcd6e3715fc20c3fab37afd67aa30033d225fb():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__00__annotation,
        __dataclass__init__fields__00__default,
        __dataclass__init__fields__01__annotation,
        __dataclass__init__fields__01__default,
        __dataclass__init__fields__02__annotation,
        __dataclass__init__fields__02__default,
        __dataclass__init__fields__03__annotation,
        __dataclass__init__fields__03__default,
        __dataclass__init__fields__04__annotation,
        __dataclass__init__fields__04__default,
        __dataclass__init__fields__05__annotation,
        __dataclass__init__fields__05__default,
        __dataclass__init__fields__06__annotation,
        __dataclass__init__fields__06__default,
        __dataclass__init__fields__07__annotation,
        __dataclass__init__fields__07__default,
        __dataclass__init__fields__08__annotation,
        __dataclass__init__fields__08__default,
        __dataclass__init__fields__09__annotation,
        __dataclass__init__fields__09__default,
        __dataclass__init__fields__10__annotation,
        __dataclass__init__fields__10__default,
        __dataclass__init__fields__11__annotation,
        __dataclass__init__fields__11__default,
        __dataclass__init__fields__12__annotation,
        __dataclass__init__fields__12__default,
        __dataclass__repr__default_fn,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                ref=self.ref,
                summary=self.summary,
                description=self.description,
                get=self.get,
                put=self.put,
                post=self.post,
                delete=self.delete,
                options=self.options,
                head=self.head,
                patch=self.patch,
                trace=self.trace,
                servers=self.servers,
                parameters=self.parameters,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.ref == other.ref and
                self.summary == other.summary and
                self.description == other.description and
                self.get == other.get and
                self.put == other.put and
                self.post == other.post and
                self.delete == other.delete and
                self.options == other.options and
                self.head == other.head and
                self.patch == other.patch and
                self.trace == other.trace and
                self.servers == other.servers and
                self.parameters == other.parameters
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'ref',
            'summary',
            'description',
            'get',
            'put',
            'post',
            'delete',
            'options',
            'head',
            'patch',
            'trace',
            'servers',
            'parameters',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'ref',
            'summary',
            'description',
            'get',
            'put',
            'post',
            'delete',
            'options',
            'head',
            'patch',
            'trace',
            'servers',
            'parameters',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.ref,
                self.summary,
                self.description,
                self.get,
                self.put,
                self.post,
                self.delete,
                self.options,
                self.head,
                self.patch,
                self.trace,
                self.servers,
                self.parameters,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            ref: __dataclass__init__fields__00__annotation = __dataclass__init__fields__00__default,
            summary: __dataclass__init__fields__01__annotation = __dataclass__init__fields__01__default,
            description: __dataclass__init__fields__02__annotation = __dataclass__init__fields__02__default,
            get: __dataclass__init__fields__03__annotation = __dataclass__init__fields__03__default,
            put: __dataclass__init__fields__04__annotation = __dataclass__init__fields__04__default,
            post: __dataclass__init__fields__05__annotation = __dataclass__init__fields__05__default,
            delete: __dataclass__init__fields__06__annotation = __dataclass__init__fields__06__default,
            options: __dataclass__init__fields__07__annotation = __dataclass__init__fields__07__default,
            head: __dataclass__init__fields__08__annotation = __dataclass__init__fields__08__default,
            patch: __dataclass__init__fields__09__annotation = __dataclass__init__fields__09__default,
            trace: __dataclass__init__fields__10__annotation = __dataclass__init__fields__10__default,
            servers: __dataclass__init__fields__11__annotation = __dataclass__init__fields__11__default,
            parameters: __dataclass__init__fields__12__annotation = __dataclass__init__fields__12__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'ref', ref)
            __dataclass__object_setattr(self, 'summary', summary)
            __dataclass__object_setattr(self, 'description', description)
            __dataclass__object_setattr(self, 'get', get)
            __dataclass__object_setattr(self, 'put', put)
            __dataclass__object_setattr(self, 'post', post)
            __dataclass__object_setattr(self, 'delete', delete)
            __dataclass__object_setattr(self, 'options', options)
            __dataclass__object_setattr(self, 'head', head)
            __dataclass__object_setattr(self, 'patch', patch)
            __dataclass__object_setattr(self, 'trace', trace)
            __dataclass__object_setattr(self, 'servers', servers)
            __dataclass__object_setattr(self, 'parameters', parameters)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__default_fn(self.ref)) is not None:
                parts.append(f"ref={s}")
            if (s := __dataclass__repr__default_fn(self.summary)) is not None:
                parts.append(f"summary={s}")
            if (s := __dataclass__repr__default_fn(self.description)) is not None:
                parts.append(f"description={s}")
            if (s := __dataclass__repr__default_fn(self.get)) is not None:
                parts.append(f"get={s}")
            if (s := __dataclass__repr__default_fn(self.put)) is not None:
                parts.append(f"put={s}")
            if (s := __dataclass__repr__default_fn(self.post)) is not None:
                parts.append(f"post={s}")
            if (s := __dataclass__repr__default_fn(self.delete)) is not None:
                parts.append(f"delete={s}")
            if (s := __dataclass__repr__default_fn(self.options)) is not None:
                parts.append(f"options={s}")
            if (s := __dataclass__repr__default_fn(self.head)) is not None:
                parts.append(f"head={s}")
            if (s := __dataclass__repr__default_fn(self.patch)) is not None:
                parts.append(f"patch={s}")
            if (s := __dataclass__repr__default_fn(self.trace)) is not None:
                parts.append(f"trace={s}")
            if (s := __dataclass__repr__default_fn(self.servers)) is not None:
                parts.append(f"servers={s}")
            if (s := __dataclass__repr__default_fn(self.parameters)) is not None:
                parts.append(f"parameters={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('ref', 'summary', 'description')), EqPlan(fields=('ref', 'summary', 'description')"
        "), FrozenPlan(fields=('ref', 'summary', 'description'), allow_dynamic_dunder_attrs=False), HashPlan(action='ad"
        "d', fields=('ref', 'summary', 'description'), cache=False), InitPlan(fields=(InitPlan.Field(name='ref', annota"
        "tion=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, fi"
        "eld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='summary', anno"
        "tation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=No"
        "ne, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), In"
        "itPlan.Field(name='description', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.f"
        "ields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None"
        ", validate=None, check_type=None)), self_param='self', std_params=('ref', 'summary', 'description'), kw_only_p"
        "arams=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(Rep"
        "rPlan.Field(name='ref', kw_only=False, fn=None), ReprPlan.Field(name='summary', kw_only=False, fn=None), ReprP"
        "lan.Field(name='description', kw_only=False, fn=None)), id=False, terse=False, default_fn=OpRef(name='repr.def"
        "ault_fn'))))"
    ),
    plan_repr_sha1='3670b9ebea893cec23429f0248849b2585df602b',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__repr__default_fn',
    ),
    cls_names=(
        ('omlish.specs.openapi.openapi', 'Reference'),
    ),
)
def _process_dataclass__3670b9ebea893cec23429f0248849b2585df602b():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
        __dataclass__repr__default_fn,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                ref=self.ref,
                summary=self.summary,
                description=self.description,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.ref == other.ref and
                self.summary == other.summary and
                self.description == other.description
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'ref',
            'summary',
            'description',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'ref',
            'summary',
            'description',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.ref,
                self.summary,
                self.description,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            ref: __dataclass__init__fields__0__annotation,
            summary: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            description: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'ref', ref)
            __dataclass__object_setattr(self, 'summary', summary)
            __dataclass__object_setattr(self, 'description', description)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__default_fn(self.ref)) is not None:
                parts.append(f"ref={s}")
            if (s := __dataclass__repr__default_fn(self.summary)) is not None:
                parts.append(f"summary={s}")
            if (s := __dataclass__repr__default_fn(self.description)) is not None:
                parts.append(f"description={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('content', 'description', 'required')), EqPlan(fields=('content', 'description', '"
        "required')), FrozenPlan(fields=('content', 'description', 'required'), allow_dynamic_dunder_attrs=False), Hash"
        "Plan(action='add', fields=('content', 'description', 'required'), cache=False), InitPlan(fields=(InitPlan.Fiel"
        "d(name='content', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init="
        "True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fi"
        "eld(name='description', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.d"
        "efault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validat"
        "e=None, check_type=None), InitPlan.Field(name='required', annotation=OpRef(name='init.fields.2.annotation'), d"
        "efault=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldT"
        "ype.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=('content', 'descri"
        "ption', 'required'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate"
        "_fns=()), ReprPlan(fields=(ReprPlan.Field(name='content', kw_only=False, fn=None), ReprPlan.Field(name='descri"
        "ption', kw_only=False, fn=None), ReprPlan.Field(name='required', kw_only=False, fn=None)), id=False, terse=Fal"
        "se, default_fn=OpRef(name='repr.default_fn'))))"
    ),
    plan_repr_sha1='4d7b50c4830d77baf175395781b487267d8cc483',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__repr__default_fn',
    ),
    cls_names=(
        ('omlish.specs.openapi.openapi', 'RequestBody'),
    ),
)
def _process_dataclass__4d7b50c4830d77baf175395781b487267d8cc483():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
        __dataclass__repr__default_fn,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                content=self.content,
                description=self.description,
                required=self.required,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.content == other.content and
                self.description == other.description and
                self.required == other.required
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'content',
            'description',
            'required',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'content',
            'description',
            'required',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.content,
                self.description,
                self.required,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            content: __dataclass__init__fields__0__annotation,
            description: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            required: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'content', content)
            __dataclass__object_setattr(self, 'description', description)
            __dataclass__object_setattr(self, 'required', required)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__default_fn(self.content)) is not None:
                parts.append(f"content={s}")
            if (s := __dataclass__repr__default_fn(self.description)) is not None:
                parts.append(f"description={s}")
            if (s := __dataclass__repr__default_fn(self.required)) is not None:
                parts.append(f"required={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('description', 'headers', 'content', 'links')), EqPlan(fields=('description', 'hea"
        "ders', 'content', 'links')), FrozenPlan(fields=('description', 'headers', 'content', 'links'), allow_dynamic_d"
        "under_attrs=False), HashPlan(action='add', fields=('description', 'headers', 'content', 'links'), cache=False)"
        ", InitPlan(fields=(InitPlan.Field(name='description', annotation=OpRef(name='init.fields.0.annotation'), defau"
        "lt=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate"
        "=None, check_type=None), InitPlan.Field(name='headers', annotation=OpRef(name='init.fields.1.annotation'), def"
        "ault=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldTyp"
        "e.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='content', annotation=OpRef(name"
        "='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, ov"
        "erride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name"
        "='links', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), defa"
        "ult_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_"
        "type=None)), self_param='self', std_params=('description', 'headers', 'content', 'links'), kw_only_params=(), "
        "frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Fiel"
        "d(name='description', kw_only=False, fn=None), ReprPlan.Field(name='headers', kw_only=False, fn=None), ReprPla"
        "n.Field(name='content', kw_only=False, fn=None), ReprPlan.Field(name='links', kw_only=False, fn=None)), id=Fal"
        "se, terse=False, default_fn=OpRef(name='repr.default_fn'))))"
    ),
    plan_repr_sha1='ba1130aff126463fd8f758d0ad559b5d4d40de0c',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
        '__dataclass__repr__default_fn',
    ),
    cls_names=(
        ('omlish.specs.openapi.openapi', 'Response'),
    ),
)
def _process_dataclass__ba1130aff126463fd8f758d0ad559b5d4d40de0c():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__3__default,
        __dataclass__repr__default_fn,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                description=self.description,
                headers=self.headers,
                content=self.content,
                links=self.links,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.description == other.description and
                self.headers == other.headers and
                self.content == other.content and
                self.links == other.links
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'description',
            'headers',
            'content',
            'links',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'description',
            'headers',
            'content',
            'links',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.description,
                self.headers,
                self.content,
                self.links,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            description: __dataclass__init__fields__0__annotation,
            headers: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            content: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            links: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'description', description)
            __dataclass__object_setattr(self, 'headers', headers)
            __dataclass__object_setattr(self, 'content', content)
            __dataclass__object_setattr(self, 'links', links)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__default_fn(self.description)) is not None:
                parts.append(f"description={s}")
            if (s := __dataclass__repr__default_fn(self.headers)) is not None:
                parts.append(f"headers={s}")
            if (s := __dataclass__repr__default_fn(self.content)) is not None:
                parts.append(f"content={s}")
            if (s := __dataclass__repr__default_fn(self.links)) is not None:
                parts.append(f"links={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('discriminator', 'xml', 'external_docs', 'example', 'keywords')), EqPlan(fields=('"
        "discriminator', 'xml', 'external_docs', 'example', 'keywords')), FrozenPlan(fields=('discriminator', 'xml', 'e"
        "xternal_docs', 'example', 'keywords'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('disc"
        "riminator', 'xml', 'external_docs', 'example', 'keywords'), cache=False), InitPlan(fields=(InitPlan.Field(name"
        "='discriminator', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default"
        "'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None"
        ", check_type=None), InitPlan.Field(name='xml', annotation=OpRef(name='init.fields.1.annotation'), default=OpRe"
        "f(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANC"
        "E, coerce=None, validate=None, check_type=None), InitPlan.Field(name='external_docs', annotation=OpRef(name='i"
        "nit.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, overr"
        "ide=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='e"
        "xample', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), defau"
        "lt_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_t"
        "ype=None), InitPlan.Field(name='keywords', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(na"
        "me='init.fields.4.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, c"
        "oerce=None, validate=None, check_type=None)), self_param='self', std_params=('discriminator', 'xml', 'external"
        "_docs', 'example', 'keywords'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=("
        "), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='discriminator', kw_only=False, fn=None), ReprPlan.F"
        "ield(name='xml', kw_only=False, fn=None), ReprPlan.Field(name='external_docs', kw_only=False, fn=None), ReprPl"
        "an.Field(name='example', kw_only=False, fn=None), ReprPlan.Field(name='keywords', kw_only=False, fn=None)), id"
        "=False, terse=False, default_fn=OpRef(name='repr.default_fn'))))"
    ),
    plan_repr_sha1='9dfacb9a92daa4820108c7c6b2beff0e8e7c7896',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__4__default',
        '__dataclass__repr__default_fn',
    ),
    cls_names=(
        ('omlish.specs.openapi.openapi', 'Schema'),
    ),
)
def _process_dataclass__9dfacb9a92daa4820108c7c6b2beff0e8e7c7896():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__3__default,
        __dataclass__init__fields__4__annotation,
        __dataclass__init__fields__4__default,
        __dataclass__repr__default_fn,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                discriminator=self.discriminator,
                xml=self.xml,
                external_docs=self.external_docs,
                example=self.example,
                keywords=self.keywords,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.discriminator == other.discriminator and
                self.xml == other.xml and
                self.external_docs == other.external_docs and
                self.example == other.example and
                self.keywords == other.keywords
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'discriminator',
            'xml',
            'external_docs',
            'example',
            'keywords',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'discriminator',
            'xml',
            'external_docs',
            'example',
            'keywords',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.discriminator,
                self.xml,
                self.external_docs,
                self.example,
                self.keywords,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            discriminator: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            xml: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            external_docs: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            example: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            keywords: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'discriminator', discriminator)
            __dataclass__object_setattr(self, 'xml', xml)
            __dataclass__object_setattr(self, 'external_docs', external_docs)
            __dataclass__object_setattr(self, 'example', example)
            __dataclass__object_setattr(self, 'keywords', keywords)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__default_fn(self.discriminator)) is not None:
                parts.append(f"discriminator={s}")
            if (s := __dataclass__repr__default_fn(self.xml)) is not None:
                parts.append(f"xml={s}")
            if (s := __dataclass__repr__default_fn(self.external_docs)) is not None:
                parts.append(f"external_docs={s}")
            if (s := __dataclass__repr__default_fn(self.example)) is not None:
                parts.append(f"example={s}")
            if (s := __dataclass__repr__default_fn(self.keywords)) is not None:
                parts.append(f"keywords={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('type', 'scheme', 'name', 'in_', 'description', 'bearer_format', 'flows', 'open_id"
        "_connect_url')), EqPlan(fields=('type', 'scheme', 'name', 'in_', 'description', 'bearer_format', 'flows', 'ope"
        "n_id_connect_url')), FrozenPlan(fields=('type', 'scheme', 'name', 'in_', 'description', 'bearer_format', 'flow"
        "s', 'open_id_connect_url'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('type', 'scheme'"
        ", 'name', 'in_', 'description', 'bearer_format', 'flows', 'open_id_connect_url'), cache=False), InitPlan(field"
        "s=(InitPlan.Field(name='type', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factor"
        "y=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)"
        ", InitPlan.Field(name='scheme', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_facto"
        "ry=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None"
        "), InitPlan.Field(name='name', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fie"
        "lds.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, "
        "validate=None, check_type=None), InitPlan.Field(name='in_', annotation=OpRef(name='init.fields.3.annotation'),"
        " default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=Fiel"
        "dType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='description', annotation=Op"
        "Ref(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_factory=None, init="
        "True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fi"
        "eld(name='bearer_format', annotation=OpRef(name='init.fields.5.annotation'), default=OpRef(name='init.fields.5"
        ".default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valid"
        "ate=None, check_type=None), InitPlan.Field(name='flows', annotation=OpRef(name='init.fields.6.annotation'), de"
        "fault=OpRef(name='init.fields.6.default'), default_factory=None, init=True, override=False, field_type=FieldTy"
        "pe.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='open_id_connect_url', annotati"
        "on=OpRef(name='init.fields.7.annotation'), default=OpRef(name='init.fields.7.default'), default_factory=None, "
        "init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_"
        "param='self', std_params=('type', 'scheme', 'name', 'in_', 'description', 'bearer_format', 'flows', 'open_id_c"
        "onnect_url'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()"
        "), ReprPlan(fields=(ReprPlan.Field(name='type', kw_only=False, fn=None), ReprPlan.Field(name='scheme', kw_only"
        "=False, fn=None), ReprPlan.Field(name='name', kw_only=False, fn=None), ReprPlan.Field(name='in_', kw_only=Fals"
        "e, fn=None), ReprPlan.Field(name='description', kw_only=False, fn=None), ReprPlan.Field(name='bearer_format', "
        "kw_only=False, fn=None), ReprPlan.Field(name='flows', kw_only=False, fn=None), ReprPlan.Field(name='open_id_co"
        "nnect_url', kw_only=False, fn=None)), id=False, terse=False, default_fn=OpRef(name='repr.default_fn'))))"
    ),
    plan_repr_sha1='8d8e79ef7f961f4f87613951588263cba38367cd',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__4__default',
        '__dataclass__init__fields__5__annotation',
        '__dataclass__init__fields__5__default',
        '__dataclass__init__fields__6__annotation',
        '__dataclass__init__fields__6__default',
        '__dataclass__init__fields__7__annotation',
        '__dataclass__init__fields__7__default',
        '__dataclass__repr__default_fn',
    ),
    cls_names=(
        ('omlish.specs.openapi.openapi', 'SecurityScheme'),
    ),
)
def _process_dataclass__8d8e79ef7f961f4f87613951588263cba38367cd():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__3__default,
        __dataclass__init__fields__4__annotation,
        __dataclass__init__fields__4__default,
        __dataclass__init__fields__5__annotation,
        __dataclass__init__fields__5__default,
        __dataclass__init__fields__6__annotation,
        __dataclass__init__fields__6__default,
        __dataclass__init__fields__7__annotation,
        __dataclass__init__fields__7__default,
        __dataclass__repr__default_fn,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                type=self.type,
                scheme=self.scheme,
                name=self.name,
                in_=self.in_,
                description=self.description,
                bearer_format=self.bearer_format,
                flows=self.flows,
                open_id_connect_url=self.open_id_connect_url,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.type == other.type and
                self.scheme == other.scheme and
                self.name == other.name and
                self.in_ == other.in_ and
                self.description == other.description and
                self.bearer_format == other.bearer_format and
                self.flows == other.flows and
                self.open_id_connect_url == other.open_id_connect_url
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'type',
            'scheme',
            'name',
            'in_',
            'description',
            'bearer_format',
            'flows',
            'open_id_connect_url',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'type',
            'scheme',
            'name',
            'in_',
            'description',
            'bearer_format',
            'flows',
            'open_id_connect_url',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.type,
                self.scheme,
                self.name,
                self.in_,
                self.description,
                self.bearer_format,
                self.flows,
                self.open_id_connect_url,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            type: __dataclass__init__fields__0__annotation,
            scheme: __dataclass__init__fields__1__annotation,
            name: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            in_: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            description: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            bearer_format: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
            flows: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
            open_id_connect_url: __dataclass__init__fields__7__annotation = __dataclass__init__fields__7__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'type', type)
            __dataclass__object_setattr(self, 'scheme', scheme)
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'in_', in_)
            __dataclass__object_setattr(self, 'description', description)
            __dataclass__object_setattr(self, 'bearer_format', bearer_format)
            __dataclass__object_setattr(self, 'flows', flows)
            __dataclass__object_setattr(self, 'open_id_connect_url', open_id_connect_url)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__default_fn(self.type)) is not None:
                parts.append(f"type={s}")
            if (s := __dataclass__repr__default_fn(self.scheme)) is not None:
                parts.append(f"scheme={s}")
            if (s := __dataclass__repr__default_fn(self.name)) is not None:
                parts.append(f"name={s}")
            if (s := __dataclass__repr__default_fn(self.in_)) is not None:
                parts.append(f"in_={s}")
            if (s := __dataclass__repr__default_fn(self.description)) is not None:
                parts.append(f"description={s}")
            if (s := __dataclass__repr__default_fn(self.bearer_format)) is not None:
                parts.append(f"bearer_format={s}")
            if (s := __dataclass__repr__default_fn(self.flows)) is not None:
                parts.append(f"flows={s}")
            if (s := __dataclass__repr__default_fn(self.open_id_connect_url)) is not None:
                parts.append(f"open_id_connect_url={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('url', 'description', 'variables')), EqPlan(fields=('url', 'description', 'variabl"
        "es')), FrozenPlan(fields=('url', 'description', 'variables'), allow_dynamic_dunder_attrs=False), HashPlan(acti"
        "on='add', fields=('url', 'description', 'variables'), cache=False), InitPlan(fields=(InitPlan.Field(name='url'"
        ", annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=F"
        "alse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='descri"
        "ption', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), defaul"
        "t_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_ty"
        "pe=None), InitPlan.Field(name='variables', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(na"
        "me='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, c"
        "oerce=None, validate=None, check_type=None)), self_param='self', std_params=('url', 'description', 'variables'"
        "), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan"
        "(fields=(ReprPlan.Field(name='url', kw_only=False, fn=None), ReprPlan.Field(name='description', kw_only=False,"
        " fn=None), ReprPlan.Field(name='variables', kw_only=False, fn=None)), id=False, terse=False, default_fn=OpRef("
        "name='repr.default_fn'))))"
    ),
    plan_repr_sha1='0d8ff939993b09e0048474b6080b9fc212767363',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__repr__default_fn',
    ),
    cls_names=(
        ('omlish.specs.openapi.openapi', 'Server'),
    ),
)
def _process_dataclass__0d8ff939993b09e0048474b6080b9fc212767363():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
        __dataclass__repr__default_fn,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                url=self.url,
                description=self.description,
                variables=self.variables,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.url == other.url and
                self.description == other.description and
                self.variables == other.variables
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'url',
            'description',
            'variables',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'url',
            'description',
            'variables',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.url,
                self.description,
                self.variables,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            url: __dataclass__init__fields__0__annotation,
            description: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            variables: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'url', url)
            __dataclass__object_setattr(self, 'description', description)
            __dataclass__object_setattr(self, 'variables', variables)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__default_fn(self.url)) is not None:
                parts.append(f"url={s}")
            if (s := __dataclass__repr__default_fn(self.description)) is not None:
                parts.append(f"description={s}")
            if (s := __dataclass__repr__default_fn(self.variables)) is not None:
                parts.append(f"variables={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('default', 'enum', 'description')), EqPlan(fields=('default', 'enum', 'description"
        "')), FrozenPlan(fields=('default', 'enum', 'description'), allow_dynamic_dunder_attrs=False), HashPlan(action="
        "'add', fields=('default', 'enum', 'description'), cache=False), InitPlan(fields=(InitPlan.Field(name='default'"
        ", annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=F"
        "alse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='enum',"
        " annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_facto"
        "ry=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None"
        "), InitPlan.Field(name='description', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='i"
        "nit.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce"
        "=None, validate=None, check_type=None)), self_param='self', std_params=('default', 'enum', 'description'), kw_"
        "only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(field"
        "s=(ReprPlan.Field(name='default', kw_only=False, fn=None), ReprPlan.Field(name='enum', kw_only=False, fn=None)"
        ", ReprPlan.Field(name='description', kw_only=False, fn=None)), id=False, terse=False, default_fn=OpRef(name='r"
        "epr.default_fn'))))"
    ),
    plan_repr_sha1='ed700960cbf73cb2c74eff6586b4e17b28ce3e64',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__repr__default_fn',
    ),
    cls_names=(
        ('omlish.specs.openapi.openapi', 'ServerVariable'),
    ),
)
def _process_dataclass__ed700960cbf73cb2c74eff6586b4e17b28ce3e64():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
        __dataclass__repr__default_fn,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                default=self.default,
                enum=self.enum,
                description=self.description,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.default == other.default and
                self.enum == other.enum and
                self.description == other.description
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'default',
            'enum',
            'description',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'default',
            'enum',
            'description',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.default,
                self.enum,
                self.description,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            default: __dataclass__init__fields__0__annotation,
            enum: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            description: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'default', default)
            __dataclass__object_setattr(self, 'enum', enum)
            __dataclass__object_setattr(self, 'description', description)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__default_fn(self.default)) is not None:
                parts.append(f"default={s}")
            if (s := __dataclass__repr__default_fn(self.enum)) is not None:
                parts.append(f"enum={s}")
            if (s := __dataclass__repr__default_fn(self.description)) is not None:
                parts.append(f"description={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('name', 'description', 'external_docs')), EqPlan(fields=('name', 'description', 'e"
        "xternal_docs')), FrozenPlan(fields=('name', 'description', 'external_docs'), allow_dynamic_dunder_attrs=False)"
        ", HashPlan(action='add', fields=('name', 'description', 'external_docs'), cache=False), InitPlan(fields=(InitP"
        "lan.Field(name='name', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, "
        "init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPl"
        "an.Field(name='description', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.field"
        "s.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, va"
        "lidate=None, check_type=None), InitPlan.Field(name='external_docs', annotation=OpRef(name='init.fields.2.annot"
        "ation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_t"
        "ype=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=('name', "
        "'description', 'external_docs'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns="
        "(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='name', kw_only=False, fn=None), ReprPlan.Field(nam"
        "e='description', kw_only=False, fn=None), ReprPlan.Field(name='external_docs', kw_only=False, fn=None)), id=Fa"
        "lse, terse=False, default_fn=OpRef(name='repr.default_fn'))))"
    ),
    plan_repr_sha1='403f654c39247dc017aa2d5c3ad151dcdf42f5c9',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__repr__default_fn',
    ),
    cls_names=(
        ('omlish.specs.openapi.openapi', 'Tag'),
    ),
)
def _process_dataclass__403f654c39247dc017aa2d5c3ad151dcdf42f5c9():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
        __dataclass__repr__default_fn,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                name=self.name,
                description=self.description,
                external_docs=self.external_docs,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.name == other.name and
                self.description == other.description and
                self.external_docs == other.external_docs
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'name',
            'description',
            'external_docs',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'name',
            'description',
            'external_docs',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.name,
                self.description,
                self.external_docs,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            name: __dataclass__init__fields__0__annotation,
            description: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            external_docs: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'description', description)
            __dataclass__object_setattr(self, 'external_docs', external_docs)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__default_fn(self.name)) is not None:
                parts.append(f"name={s}")
            if (s := __dataclass__repr__default_fn(self.description)) is not None:
                parts.append(f"description={s}")
            if (s := __dataclass__repr__default_fn(self.external_docs)) is not None:
                parts.append(f"external_docs={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('name', 'namespace', 'prefix', 'attribute', 'wrapped')), EqPlan(fields=('name', 'n"
        "amespace', 'prefix', 'attribute', 'wrapped')), FrozenPlan(fields=('name', 'namespace', 'prefix', 'attribute', "
        "'wrapped'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('name', 'namespace', 'prefix', '"
        "attribute', 'wrapped'), cache=False), InitPlan(fields=(InitPlan.Field(name='name', annotation=OpRef(name='init"
        ".fields.0.annotation'), default=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override"
        "=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='name"
        "space', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), defaul"
        "t_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_ty"
        "pe=None), InitPlan.Field(name='prefix', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name="
        "'init.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coer"
        "ce=None, validate=None, check_type=None), InitPlan.Field(name='attribute', annotation=OpRef(name='init.fields."
        "3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, "
        "field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='wrapped', an"
        "notation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_factory="
        "None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)),"
        " self_param='self', std_params=('name', 'namespace', 'prefix', 'attribute', 'wrapped'), kw_only_params=(), fro"
        "zen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(n"
        "ame='name', kw_only=False, fn=None), ReprPlan.Field(name='namespace', kw_only=False, fn=None), ReprPlan.Field("
        "name='prefix', kw_only=False, fn=None), ReprPlan.Field(name='attribute', kw_only=False, fn=None), ReprPlan.Fie"
        "ld(name='wrapped', kw_only=False, fn=None)), id=False, terse=False, default_fn=OpRef(name='repr.default_fn')))"
        ")"
    ),
    plan_repr_sha1='c7656e6ca8a63c0cf248f48ba702df7d8aac96c5',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__4__default',
        '__dataclass__repr__default_fn',
    ),
    cls_names=(
        ('omlish.specs.openapi.openapi', 'Xml'),
    ),
)
def _process_dataclass__c7656e6ca8a63c0cf248f48ba702df7d8aac96c5():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__3__default,
        __dataclass__init__fields__4__annotation,
        __dataclass__init__fields__4__default,
        __dataclass__repr__default_fn,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                name=self.name,
                namespace=self.namespace,
                prefix=self.prefix,
                attribute=self.attribute,
                wrapped=self.wrapped,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.name == other.name and
                self.namespace == other.namespace and
                self.prefix == other.prefix and
                self.attribute == other.attribute and
                self.wrapped == other.wrapped
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'name',
            'namespace',
            'prefix',
            'attribute',
            'wrapped',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'name',
            'namespace',
            'prefix',
            'attribute',
            'wrapped',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.name,
                self.namespace,
                self.prefix,
                self.attribute,
                self.wrapped,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            name: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            namespace: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            prefix: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            attribute: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            wrapped: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'namespace', namespace)
            __dataclass__object_setattr(self, 'prefix', prefix)
            __dataclass__object_setattr(self, 'attribute', attribute)
            __dataclass__object_setattr(self, 'wrapped', wrapped)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__default_fn(self.name)) is not None:
                parts.append(f"name={s}")
            if (s := __dataclass__repr__default_fn(self.namespace)) is not None:
                parts.append(f"namespace={s}")
            if (s := __dataclass__repr__default_fn(self.prefix)) is not None:
                parts.append(f"prefix={s}")
            if (s := __dataclass__repr__default_fn(self.attribute)) is not None:
                parts.append(f"attribute={s}")
            if (s := __dataclass__repr__default_fn(self.wrapped)) is not None:
                parts.append(f"wrapped={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('schema', 'names')), EqPlan(fields=('schema', 'names')), FrozenPlan(fields=('schem"
        "a', 'names'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('schema', 'names'), cache=Fals"
        "e), InitPlan(fields=(InitPlan.Field(name='schema', annotation=OpRef(name='init.fields.0.annotation'), default="
        "None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=No"
        "ne, check_type=None), InitPlan.Field(name='names', annotation=OpRef(name='init.fields.1.annotation'), default="
        "None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=No"
        "ne, check_type=None)), self_param='self', std_params=('schema', 'names'), kw_only_params=(), frozen=True, slot"
        "s=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='schema', "
        "kw_only=False, fn=None), ReprPlan.Field(name='names', kw_only=False, fn=None)), id=False, terse=False, default"
        "_fn=None)))"
    ),
    plan_repr_sha1='f767b80f010435f6c60531699ee12edc74460b24',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('omlish.specs.openapi.tools.jsonschema', 'OpenapiJsonschema'),
    ),
)
def _process_dataclass__f767b80f010435f6c60531699ee12edc74460b24():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                schema=self.schema,
                names=self.names,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.schema == other.schema and
                self.names == other.names
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'schema',
            'names',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'schema',
            'names',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.schema,
                self.names,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            schema: __dataclass__init__fields__0__annotation,
            names: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'schema', schema)
            __dataclass__object_setattr(self, 'names', names)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"schema={self.schema!r}")
            parts.append(f"names={self.names!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('name', 'schema')), EqPlan(fields=('name', 'schema')), FrozenPlan(fields=('name', "
        "'schema'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('name', 'schema'), cache=False), "
        "InitPlan(fields=(InitPlan.Field(name='name', annotation=OpRef(name='init.fields.0.annotation'), default=None, "
        "default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, ch"
        "eck_type=None), InitPlan.Field(name='schema', annotation=OpRef(name='init.fields.1.annotation'), default=None,"
        " default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, c"
        "heck_type=None)), self_param='self', std_params=('name', 'schema'), kw_only_params=(), frozen=True, slots=Fals"
        "e, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='name', kw_only="
        "False, fn=None), ReprPlan.Field(name='schema', kw_only=False, fn=None)), id=False, terse=False, default_fn=Non"
        "e)))"
    ),
    plan_repr_sha1='28fa5f38326ee968867cdcb54e7cf587c1102899',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('omlish.specs.openapi.tools.jsonschema', '_NamedSchema'),
    ),
)
def _process_dataclass__28fa5f38326ee968867cdcb54e7cf587c1102899():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                name=self.name,
                schema=self.schema,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.name == other.name and
                self.schema == other.schema
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'name',
            'schema',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'name',
            'schema',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.name,
                self.schema,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            name: __dataclass__init__fields__0__annotation,
            schema: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'schema', schema)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"name={self.name!r}")
            parts.append(f"schema={self.schema!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass
