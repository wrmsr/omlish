# @omlish-generated
# type: ignore
# ruff: noqa
# flake8: noqa
import dataclasses
import reprlib
import types


#


REGISTRY = {}


def _register(plan_repr):
    def inner(fn):
        REGISTRY[fn.__name__] = (plan_repr, fn)
        return fn
    return inner



@_register(
    "Plans(tup=(CopyPlan(fields=('v_ty', 'l', 'x')), EqPlan(fields=('v_ty', 'l', 'x')), FrozenPlan(fields=('v_ty', 'l',"
    " 'x'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('v_ty', 'l', 'x'), cache=False), InitPlan"
    "(fields=(InitPlan.Field(name='v_ty', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_fact"
    "ory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), "
    "InitPlan.Field(name='l', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, in"
    "it=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fie"
    "ld(name='x', annotation=OpRef(name='init.fields.2.annotation'), default=None, default_factory=None, init=True, ove"
    "rride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_"
    "params=('v_ty', 'l', 'x'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), valida"
    "te_fns=()), ReprPlan(fields=(ReprPlan.Field(name='v_ty', kw_only=False, fn=None), ReprPlan.Field(name='l', kw_only"
    "=False, fn=None), ReprPlan.Field(name='x', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2fmarshal_2fcomposite_2funions_2fliterals_2fLiteralUnionMarshaler(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__1__annotation,
    __dataclass__init__fields__2__annotation,
    __dataclass__isinstance=isinstance,  # noqa
    __dataclass__None=None,  # noqa
    __dataclass__property=property,  # noqa
    __dataclass__TypeError=TypeError,  # noqa
    __dataclass__object_setattr=object.__setattr__,  # noqa
    __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
    __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
    __dataclass__MISSING=dataclasses.MISSING,  # noqa
    __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
    __dataclass__FunctionType=types.FunctionType,  # noqa
    __dataclass__FieldFnValidationError,  # noqa
    __dataclass__FieldTypeValidationError,  # noqa
    __dataclass__FnValidationError,  # noqa
):
    def __copy__(self):
        if self.__class__ is not __dataclass__cls:
            raise TypeError(self)
        return __dataclass__cls(  # noqa
            v_ty=self.v_ty,
            l=self.l,
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
            self.v_ty == other.v_ty and
            self.l == other.l and
            self.x == other.x
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'v_ty',
        'l',
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
        'v_ty',
        'l',
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
            self.v_ty,
            self.l,
            self.x,
        ))
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        v_ty: __dataclass__init__fields__0__annotation,
        l: __dataclass__init__fields__1__annotation,
        x: __dataclass__init__fields__2__annotation,
    ) -> __dataclass__None:
        __dataclass__object_setattr(self, 'v_ty', v_ty)
        __dataclass__object_setattr(self, 'l', l)
        __dataclass__object_setattr(self, 'x', x)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"v_ty={self.v_ty!r}")
        parts.append(f"l={self.l!r}")
        parts.append(f"x={self.x!r}")
        return (
            f"{self.__class__.__qualname__}("
            f"{', '.join(parts)}"
            f")"
        )
    
    __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
    if '__repr__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__repr__', __repr__)


@_register(
    "Plans(tup=(CopyPlan(fields=('v_ty', 'l', 'x')), EqPlan(fields=('v_ty', 'l', 'x')), FrozenPlan(fields=('v_ty', 'l',"
    " 'x'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('v_ty', 'l', 'x'), cache=False), InitPlan"
    "(fields=(InitPlan.Field(name='v_ty', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_fact"
    "ory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), "
    "InitPlan.Field(name='l', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, in"
    "it=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fie"
    "ld(name='x', annotation=OpRef(name='init.fields.2.annotation'), default=None, default_factory=None, init=True, ove"
    "rride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_"
    "params=('v_ty', 'l', 'x'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), valida"
    "te_fns=()), ReprPlan(fields=(ReprPlan.Field(name='v_ty', kw_only=False, fn=None), ReprPlan.Field(name='l', kw_only"
    "=False, fn=None), ReprPlan.Field(name='x', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2fmarshal_2fcomposite_2funions_2fliterals_2fLiteralUnionUnmarshaler(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__1__annotation,
    __dataclass__init__fields__2__annotation,
    __dataclass__isinstance=isinstance,  # noqa
    __dataclass__None=None,  # noqa
    __dataclass__property=property,  # noqa
    __dataclass__TypeError=TypeError,  # noqa
    __dataclass__object_setattr=object.__setattr__,  # noqa
    __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
    __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
    __dataclass__MISSING=dataclasses.MISSING,  # noqa
    __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
    __dataclass__FunctionType=types.FunctionType,  # noqa
    __dataclass__FieldFnValidationError,  # noqa
    __dataclass__FieldTypeValidationError,  # noqa
    __dataclass__FnValidationError,  # noqa
):
    def __copy__(self):
        if self.__class__ is not __dataclass__cls:
            raise TypeError(self)
        return __dataclass__cls(  # noqa
            v_ty=self.v_ty,
            l=self.l,
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
            self.v_ty == other.v_ty and
            self.l == other.l and
            self.x == other.x
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'v_ty',
        'l',
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
        'v_ty',
        'l',
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
            self.v_ty,
            self.l,
            self.x,
        ))
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        v_ty: __dataclass__init__fields__0__annotation,
        l: __dataclass__init__fields__1__annotation,
        x: __dataclass__init__fields__2__annotation,
    ) -> __dataclass__None:
        __dataclass__object_setattr(self, 'v_ty', v_ty)
        __dataclass__object_setattr(self, 'l', l)
        __dataclass__object_setattr(self, 'x', x)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"v_ty={self.v_ty!r}")
        parts.append(f"l={self.l!r}")
        parts.append(f"x={self.x!r}")
        return (
            f"{self.__class__.__qualname__}("
            f"{', '.join(parts)}"
            f")"
        )
    
    __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
    if '__repr__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__repr__', __repr__)


@_register(
    "Plans(tup=(CopyPlan(fields=('tys', 'x')), EqPlan(fields=('tys', 'x')), FrozenPlan(fields=('tys', 'x'), allow_dynam"
    "ic_dunder_attrs=False), HashPlan(action='add', fields=('tys', 'x'), cache=False), InitPlan(fields=(InitPlan.Field("
    "name='tys', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, over"
    "ride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='x', "
    "annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=No"
    "ne, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_"
    "param='self', std_params=('tys', 'x'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fn"
    "s=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='tys', kw_only=False, fn=None), ReprPlan.Field(name='"
    "x', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2fmarshal_2fcomposite_2funions_2fprimitives_2fPrimitiveUnionMarshaler(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__1__annotation,
    __dataclass__init__fields__1__default,
    __dataclass__isinstance=isinstance,  # noqa
    __dataclass__None=None,  # noqa
    __dataclass__property=property,  # noqa
    __dataclass__TypeError=TypeError,  # noqa
    __dataclass__object_setattr=object.__setattr__,  # noqa
    __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
    __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
    __dataclass__MISSING=dataclasses.MISSING,  # noqa
    __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
    __dataclass__FunctionType=types.FunctionType,  # noqa
    __dataclass__FieldFnValidationError,  # noqa
    __dataclass__FieldTypeValidationError,  # noqa
    __dataclass__FnValidationError,  # noqa
):
    def __copy__(self):
        if self.__class__ is not __dataclass__cls:
            raise TypeError(self)
        return __dataclass__cls(  # noqa
            tys=self.tys,
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
            self.tys == other.tys and
            self.x == other.x
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'tys',
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
        'tys',
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
            self.tys,
            self.x,
        ))
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        tys: __dataclass__init__fields__0__annotation,
        x: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
    ) -> __dataclass__None:
        __dataclass__object_setattr(self, 'tys', tys)
        __dataclass__object_setattr(self, 'x', x)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"tys={self.tys!r}")
        parts.append(f"x={self.x!r}")
        return (
            f"{self.__class__.__qualname__}("
            f"{', '.join(parts)}"
            f")"
        )
    
    __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
    if '__repr__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__repr__', __repr__)


@_register(
    "Plans(tup=(CopyPlan(fields=('tys',)), EqPlan(fields=('tys',)), FrozenPlan(fields=('tys',), allow_dynamic_dunder_at"
    "trs=False), HashPlan(action='add', fields=('tys',), cache=False), InitPlan(fields=(InitPlan.Field(name='tys', anno"
    "tation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'), default_factory=None, "
    "init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_par"
    "am='self', std_params=('tys',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), v"
    "alidate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='tys', kw_only=False, fn=None),), id=False, terse=False, def"
    "ault_fn=None)))"
)
def _process_dataclass__omlish_2fmarshal_2fcomposite_2funions_2fprimitives_2fPrimitiveUnionMarshalerFactory(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__0__default,
    __dataclass__isinstance=isinstance,  # noqa
    __dataclass__None=None,  # noqa
    __dataclass__property=property,  # noqa
    __dataclass__TypeError=TypeError,  # noqa
    __dataclass__object_setattr=object.__setattr__,  # noqa
    __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
    __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
    __dataclass__MISSING=dataclasses.MISSING,  # noqa
    __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
    __dataclass__FunctionType=types.FunctionType,  # noqa
    __dataclass__FieldFnValidationError,  # noqa
    __dataclass__FieldTypeValidationError,  # noqa
    __dataclass__FnValidationError,  # noqa
):
    def __copy__(self):
        if self.__class__ is not __dataclass__cls:
            raise TypeError(self)
        return __dataclass__cls(  # noqa
            tys=self.tys,
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
            self.tys == other.tys
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'tys',
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
        'tys',
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
            self.tys,
        ))
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        tys: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
    ) -> __dataclass__None:
        __dataclass__object_setattr(self, 'tys', tys)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"tys={self.tys!r}")
        return (
            f"{self.__class__.__qualname__}("
            f"{', '.join(parts)}"
            f")"
        )
    
    __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
    if '__repr__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__repr__', __repr__)


@_register(
    "Plans(tup=(CopyPlan(fields=('tys', 'x')), EqPlan(fields=('tys', 'x')), FrozenPlan(fields=('tys', 'x'), allow_dynam"
    "ic_dunder_attrs=False), HashPlan(action='add', fields=('tys', 'x'), cache=False), InitPlan(fields=(InitPlan.Field("
    "name='tys', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, over"
    "ride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='x', "
    "annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=No"
    "ne, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_"
    "param='self', std_params=('tys', 'x'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fn"
    "s=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='tys', kw_only=False, fn=None), ReprPlan.Field(name='"
    "x', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2fmarshal_2fcomposite_2funions_2fprimitives_2fPrimitiveUnionUnmarshaler(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__1__annotation,
    __dataclass__init__fields__1__default,
    __dataclass__isinstance=isinstance,  # noqa
    __dataclass__None=None,  # noqa
    __dataclass__property=property,  # noqa
    __dataclass__TypeError=TypeError,  # noqa
    __dataclass__object_setattr=object.__setattr__,  # noqa
    __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
    __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
    __dataclass__MISSING=dataclasses.MISSING,  # noqa
    __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
    __dataclass__FunctionType=types.FunctionType,  # noqa
    __dataclass__FieldFnValidationError,  # noqa
    __dataclass__FieldTypeValidationError,  # noqa
    __dataclass__FnValidationError,  # noqa
):
    def __copy__(self):
        if self.__class__ is not __dataclass__cls:
            raise TypeError(self)
        return __dataclass__cls(  # noqa
            tys=self.tys,
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
            self.tys == other.tys and
            self.x == other.x
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'tys',
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
        'tys',
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
            self.tys,
            self.x,
        ))
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        tys: __dataclass__init__fields__0__annotation,
        x: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
    ) -> __dataclass__None:
        __dataclass__object_setattr(self, 'tys', tys)
        __dataclass__object_setattr(self, 'x', x)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"tys={self.tys!r}")
        parts.append(f"x={self.x!r}")
        return (
            f"{self.__class__.__qualname__}("
            f"{', '.join(parts)}"
            f")"
        )
    
    __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
    if '__repr__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__repr__', __repr__)


@_register(
    "Plans(tup=(CopyPlan(fields=('tys',)), EqPlan(fields=('tys',)), FrozenPlan(fields=('tys',), allow_dynamic_dunder_at"
    "trs=False), HashPlan(action='add', fields=('tys',), cache=False), InitPlan(fields=(InitPlan.Field(name='tys', anno"
    "tation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'), default_factory=None, "
    "init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_par"
    "am='self', std_params=('tys',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), v"
    "alidate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='tys', kw_only=False, fn=None),), id=False, terse=False, def"
    "ault_fn=None)))"
)
def _process_dataclass__omlish_2fmarshal_2fcomposite_2funions_2fprimitives_2fPrimitiveUnionUnmarshalerFactory(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__0__default,
    __dataclass__isinstance=isinstance,  # noqa
    __dataclass__None=None,  # noqa
    __dataclass__property=property,  # noqa
    __dataclass__TypeError=TypeError,  # noqa
    __dataclass__object_setattr=object.__setattr__,  # noqa
    __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
    __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
    __dataclass__MISSING=dataclasses.MISSING,  # noqa
    __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
    __dataclass__FunctionType=types.FunctionType,  # noqa
    __dataclass__FieldFnValidationError,  # noqa
    __dataclass__FieldTypeValidationError,  # noqa
    __dataclass__FnValidationError,  # noqa
):
    def __copy__(self):
        if self.__class__ is not __dataclass__cls:
            raise TypeError(self)
        return __dataclass__cls(  # noqa
            tys=self.tys,
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
            self.tys == other.tys
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'tys',
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
        'tys',
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
            self.tys,
        ))
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        tys: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
    ) -> __dataclass__None:
        __dataclass__object_setattr(self, 'tys', tys)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"tys={self.tys!r}")
        return (
            f"{self.__class__.__qualname__}("
            f"{', '.join(parts)}"
            f")"
        )
    
    __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
    if '__repr__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__repr__', __repr__)


@_register(
    "Plans(tup=(CopyPlan(fields=('omit_if', 'default', 'embed', 'generic_replace', 'no_marshal', 'no_unmarshal')), EqPl"
    "an(fields=('omit_if', 'default', 'embed', 'generic_replace', 'no_marshal', 'no_unmarshal')), FrozenPlan(fields=('o"
    "mit_if', 'default', 'embed', 'generic_replace', 'no_marshal', 'no_unmarshal'), allow_dynamic_dunder_attrs=False), "
    "HashPlan(action='add', fields=('omit_if', 'default', 'embed', 'generic_replace', 'no_marshal', 'no_unmarshal'), ca"
    "che=False), InitPlan(fields=(InitPlan.Field(name='omit_if', annotation=OpRef(name='init.fields.0.annotation'), def"
    "ault=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.IN"
    "STANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='default', annotation=OpRef(name='init.f"
    "ields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False"
    ", field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=OpRef(name='init.fields.1.check_type')), I"
    "nitPlan.Field(name='embed', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.d"
    "efault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=No"
    "ne, check_type=None), InitPlan.Field(name='generic_replace', annotation=OpRef(name='init.fields.3.annotation'), de"
    "fault=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.I"
    "NSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='no_marshal', annotation=OpRef(name='in"
    "it.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, override=F"
    "alse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='no_unmarsh"
    "al', annotation=OpRef(name='init.fields.5.annotation'), default=OpRef(name='init.fields.5.default'), default_facto"
    "ry=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), "
    "self_param='self', std_params=(), kw_only_params=('omit_if', 'default', 'embed', 'generic_replace', 'no_marshal', "
    "'no_unmarshal'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=("
    "ReprPlan.Field(name='omit_if', kw_only=True, fn=None), ReprPlan.Field(name='default', kw_only=True, fn=None), Repr"
    "Plan.Field(name='embed', kw_only=True, fn=None), ReprPlan.Field(name='generic_replace', kw_only=True, fn=None), Re"
    "prPlan.Field(name='no_marshal', kw_only=True, fn=None), ReprPlan.Field(name='no_unmarshal', kw_only=True, fn=None)"
    "), id=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2fmarshal_2fobjects_2fmetadata_2fFieldOptions(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__0__default,
    __dataclass__init__fields__1__annotation,
    __dataclass__init__fields__1__check_type,
    __dataclass__init__fields__1__default,
    __dataclass__init__fields__2__annotation,
    __dataclass__init__fields__2__default,
    __dataclass__init__fields__3__annotation,
    __dataclass__init__fields__3__default,
    __dataclass__init__fields__4__annotation,
    __dataclass__init__fields__4__default,
    __dataclass__init__fields__5__annotation,
    __dataclass__init__fields__5__default,
    __dataclass__isinstance=isinstance,  # noqa
    __dataclass__None=None,  # noqa
    __dataclass__property=property,  # noqa
    __dataclass__TypeError=TypeError,  # noqa
    __dataclass__object_setattr=object.__setattr__,  # noqa
    __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
    __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
    __dataclass__MISSING=dataclasses.MISSING,  # noqa
    __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
    __dataclass__FunctionType=types.FunctionType,  # noqa
    __dataclass__FieldFnValidationError,  # noqa
    __dataclass__FieldTypeValidationError,  # noqa
    __dataclass__FnValidationError,  # noqa
):
    def __copy__(self):
        if self.__class__ is not __dataclass__cls:
            raise TypeError(self)
        return __dataclass__cls(  # noqa
            omit_if=self.omit_if,
            default=self.default,
            embed=self.embed,
            generic_replace=self.generic_replace,
            no_marshal=self.no_marshal,
            no_unmarshal=self.no_unmarshal,
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
            self.omit_if == other.omit_if and
            self.default == other.default and
            self.embed == other.embed and
            self.generic_replace == other.generic_replace and
            self.no_marshal == other.no_marshal and
            self.no_unmarshal == other.no_unmarshal
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'omit_if',
        'default',
        'embed',
        'generic_replace',
        'no_marshal',
        'no_unmarshal',
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
        'omit_if',
        'default',
        'embed',
        'generic_replace',
        'no_marshal',
        'no_unmarshal',
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
            self.omit_if,
            self.default,
            self.embed,
            self.generic_replace,
            self.no_marshal,
            self.no_unmarshal,
        ))
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        *,
        omit_if: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        default: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        embed: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        generic_replace: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        no_marshal: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        no_unmarshal: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
    ) -> __dataclass__None:
        if not __dataclass__isinstance(default, __dataclass__init__fields__1__check_type): 
            raise __dataclass__FieldTypeValidationError(
                obj=self,
                type=__dataclass__init__fields__1__check_type,
                field='default',
                value=default,
            )
        __dataclass__object_setattr(self, 'omit_if', omit_if)
        __dataclass__object_setattr(self, 'default', default)
        __dataclass__object_setattr(self, 'embed', embed)
        __dataclass__object_setattr(self, 'generic_replace', generic_replace)
        __dataclass__object_setattr(self, 'no_marshal', no_marshal)
        __dataclass__object_setattr(self, 'no_unmarshal', no_unmarshal)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"omit_if={self.omit_if!r}")
        parts.append(f"default={self.default!r}")
        parts.append(f"embed={self.embed!r}")
        parts.append(f"generic_replace={self.generic_replace!r}")
        parts.append(f"no_marshal={self.no_marshal!r}")
        parts.append(f"no_unmarshal={self.no_unmarshal!r}")
        return (
            f"{self.__class__.__qualname__}("
            f"{', '.join(parts)}"
            f")"
        )
    
    __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
    if '__repr__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__repr__', __repr__)


@_register(
    "Plans(tup=(CopyPlan(fields=('name', 'alts', 'options', 'marshaler', 'marshaler_factory', 'unmarshaler', 'unmarshal"
    "er_factory')), EqPlan(fields=('name', 'alts', 'options', 'marshaler', 'marshaler_factory', 'unmarshaler', 'unmarsh"
    "aler_factory')), FrozenPlan(fields=('name', 'alts', 'options', 'marshaler', 'marshaler_factory', 'unmarshaler', 'u"
    "nmarshaler_factory'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('name', 'alts', 'options',"
    " 'marshaler', 'marshaler_factory', 'unmarshaler', 'unmarshaler_factory'), cache=False), InitPlan(fields=(InitPlan."
    "Field(name='name', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'),"
    " default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check"
    "_type=None), InitPlan.Field(name='alts', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='in"
    "it.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None"
    ", validate=None, check_type=None), InitPlan.Field(name='options', annotation=OpRef(name='init.fields.2.annotation'"
    "), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldT"
    "ype.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='marshaler', annotation=OpRef(name"
    "='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, overri"
    "de=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=OpRef(name='init.fields.3.check_ty"
    "pe')), InitPlan.Field(name='marshaler_factory', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(n"
    "ame='init.fields.4.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coer"
    "ce=None, validate=None, check_type=None), InitPlan.Field(name='unmarshaler', annotation=OpRef(name='init.fields.5."
    "annotation'), default=OpRef(name='init.fields.5.default'), default_factory=None, init=True, override=False, field_"
    "type=FieldType.INSTANCE, coerce=None, validate=None, check_type=OpRef(name='init.fields.5.check_type')), InitPlan."
    "Field(name='unmarshaler_factory', annotation=OpRef(name='init.fields.6.annotation'), default=OpRef(name='init.fiel"
    "ds.6.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valid"
    "ate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('name', 'alts', 'options', 'marshal"
    "er', 'marshaler_factory', 'unmarshaler', 'unmarshaler_factory'), frozen=True, slots=False, post_init_params=None, "
    "init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='name', kw_only=True, fn=None), ReprPlan.Field"
    "(name='alts', kw_only=True, fn=None), ReprPlan.Field(name='options', kw_only=True, fn=None), ReprPlan.Field(name='"
    "marshaler', kw_only=True, fn=None), ReprPlan.Field(name='marshaler_factory', kw_only=True, fn=None), ReprPlan.Fiel"
    "d(name='unmarshaler', kw_only=True, fn=None), ReprPlan.Field(name='unmarshaler_factory', kw_only=True, fn=None)), "
    "id=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2fmarshal_2fobjects_2fmetadata_2fFieldMetadata(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__0__default,
    __dataclass__init__fields__1__annotation,
    __dataclass__init__fields__1__default,
    __dataclass__init__fields__2__annotation,
    __dataclass__init__fields__2__default,
    __dataclass__init__fields__3__annotation,
    __dataclass__init__fields__3__check_type,
    __dataclass__init__fields__3__default,
    __dataclass__init__fields__4__annotation,
    __dataclass__init__fields__4__default,
    __dataclass__init__fields__5__annotation,
    __dataclass__init__fields__5__check_type,
    __dataclass__init__fields__5__default,
    __dataclass__init__fields__6__annotation,
    __dataclass__init__fields__6__default,
    __dataclass__isinstance=isinstance,  # noqa
    __dataclass__None=None,  # noqa
    __dataclass__property=property,  # noqa
    __dataclass__TypeError=TypeError,  # noqa
    __dataclass__object_setattr=object.__setattr__,  # noqa
    __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
    __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
    __dataclass__MISSING=dataclasses.MISSING,  # noqa
    __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
    __dataclass__FunctionType=types.FunctionType,  # noqa
    __dataclass__FieldFnValidationError,  # noqa
    __dataclass__FieldTypeValidationError,  # noqa
    __dataclass__FnValidationError,  # noqa
):
    def __copy__(self):
        if self.__class__ is not __dataclass__cls:
            raise TypeError(self)
        return __dataclass__cls(  # noqa
            name=self.name,
            alts=self.alts,
            options=self.options,
            marshaler=self.marshaler,
            marshaler_factory=self.marshaler_factory,
            unmarshaler=self.unmarshaler,
            unmarshaler_factory=self.unmarshaler_factory,
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
            self.alts == other.alts and
            self.options == other.options and
            self.marshaler == other.marshaler and
            self.marshaler_factory == other.marshaler_factory and
            self.unmarshaler == other.unmarshaler and
            self.unmarshaler_factory == other.unmarshaler_factory
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'name',
        'alts',
        'options',
        'marshaler',
        'marshaler_factory',
        'unmarshaler',
        'unmarshaler_factory',
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
        'alts',
        'options',
        'marshaler',
        'marshaler_factory',
        'unmarshaler',
        'unmarshaler_factory',
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
            self.alts,
            self.options,
            self.marshaler,
            self.marshaler_factory,
            self.unmarshaler,
            self.unmarshaler_factory,
        ))
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        *,
        name: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        alts: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        options: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        marshaler: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        marshaler_factory: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        unmarshaler: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
        unmarshaler_factory: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
    ) -> __dataclass__None:
        if not __dataclass__isinstance(marshaler, __dataclass__init__fields__3__check_type): 
            raise __dataclass__FieldTypeValidationError(
                obj=self,
                type=__dataclass__init__fields__3__check_type,
                field='marshaler',
                value=marshaler,
            )
        if not __dataclass__isinstance(unmarshaler, __dataclass__init__fields__5__check_type): 
            raise __dataclass__FieldTypeValidationError(
                obj=self,
                type=__dataclass__init__fields__5__check_type,
                field='unmarshaler',
                value=unmarshaler,
            )
        __dataclass__object_setattr(self, 'name', name)
        __dataclass__object_setattr(self, 'alts', alts)
        __dataclass__object_setattr(self, 'options', options)
        __dataclass__object_setattr(self, 'marshaler', marshaler)
        __dataclass__object_setattr(self, 'marshaler_factory', marshaler_factory)
        __dataclass__object_setattr(self, 'unmarshaler', unmarshaler)
        __dataclass__object_setattr(self, 'unmarshaler_factory', unmarshaler_factory)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"name={self.name!r}")
        parts.append(f"alts={self.alts!r}")
        parts.append(f"options={self.options!r}")
        parts.append(f"marshaler={self.marshaler!r}")
        parts.append(f"marshaler_factory={self.marshaler_factory!r}")
        parts.append(f"unmarshaler={self.unmarshaler!r}")
        parts.append(f"unmarshaler_factory={self.unmarshaler_factory!r}")
        return (
            f"{self.__class__.__qualname__}("
            f"{', '.join(parts)}"
            f")"
        )
    
    __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
    if '__repr__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__repr__', __repr__)


@_register(
    "Plans(tup=(CopyPlan(fields=('field_naming', 'unknown_field', 'source_field', 'field_defaults', 'ignore_unknown')),"
    " EqPlan(fields=('field_naming', 'unknown_field', 'source_field', 'field_defaults', 'ignore_unknown')), FrozenPlan("
    "fields=('field_naming', 'unknown_field', 'source_field', 'field_defaults', 'ignore_unknown'), allow_dynamic_dunder"
    "_attrs=False), HashPlan(action='add', fields=('field_naming', 'unknown_field', 'source_field', 'field_defaults', '"
    "ignore_unknown'), cache=False), InitPlan(fields=(InitPlan.Field(name='field_naming', annotation=OpRef(name='init.f"
    "ields.0.annotation'), default=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=False"
    ", field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='unknown_field'"
    ", annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory="
    "None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), Init"
    "Plan.Field(name='source_field', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields"
    ".2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validat"
    "e=None, check_type=None), InitPlan.Field(name='field_defaults', annotation=OpRef(name='init.fields.3.annotation'),"
    " default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldTyp"
    "e.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='ignore_unknown', annotation=OpRef(n"
    "ame='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, ove"
    "rride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_"
    "params=(), kw_only_params=('field_naming', 'unknown_field', 'source_field', 'field_defaults', 'ignore_unknown'), f"
    "rozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(nam"
    "e='field_naming', kw_only=True, fn=None), ReprPlan.Field(name='unknown_field', kw_only=True, fn=None), ReprPlan.Fi"
    "eld(name='source_field', kw_only=True, fn=None), ReprPlan.Field(name='field_defaults', kw_only=True, fn=None), Rep"
    "rPlan.Field(name='ignore_unknown', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2fmarshal_2fobjects_2fmetadata_2fObjectMetadata(
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
    __dataclass__isinstance=isinstance,  # noqa
    __dataclass__None=None,  # noqa
    __dataclass__property=property,  # noqa
    __dataclass__TypeError=TypeError,  # noqa
    __dataclass__object_setattr=object.__setattr__,  # noqa
    __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
    __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
    __dataclass__MISSING=dataclasses.MISSING,  # noqa
    __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
    __dataclass__FunctionType=types.FunctionType,  # noqa
    __dataclass__FieldFnValidationError,  # noqa
    __dataclass__FieldTypeValidationError,  # noqa
    __dataclass__FnValidationError,  # noqa
):
    def __copy__(self):
        if self.__class__ is not __dataclass__cls:
            raise TypeError(self)
        return __dataclass__cls(  # noqa
            field_naming=self.field_naming,
            unknown_field=self.unknown_field,
            source_field=self.source_field,
            field_defaults=self.field_defaults,
            ignore_unknown=self.ignore_unknown,
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
            self.field_naming == other.field_naming and
            self.unknown_field == other.unknown_field and
            self.source_field == other.source_field and
            self.field_defaults == other.field_defaults and
            self.ignore_unknown == other.ignore_unknown
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'field_naming',
        'unknown_field',
        'source_field',
        'field_defaults',
        'ignore_unknown',
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
        'field_naming',
        'unknown_field',
        'source_field',
        'field_defaults',
        'ignore_unknown',
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
            self.field_naming,
            self.unknown_field,
            self.source_field,
            self.field_defaults,
            self.ignore_unknown,
        ))
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        *,
        field_naming: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        unknown_field: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        source_field: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        field_defaults: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ignore_unknown: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
    ) -> __dataclass__None:
        __dataclass__object_setattr(self, 'field_naming', field_naming)
        __dataclass__object_setattr(self, 'unknown_field', unknown_field)
        __dataclass__object_setattr(self, 'source_field', source_field)
        __dataclass__object_setattr(self, 'field_defaults', field_defaults)
        __dataclass__object_setattr(self, 'ignore_unknown', ignore_unknown)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"field_naming={self.field_naming!r}")
        parts.append(f"unknown_field={self.unknown_field!r}")
        parts.append(f"source_field={self.source_field!r}")
        parts.append(f"field_defaults={self.field_defaults!r}")
        parts.append(f"ignore_unknown={self.ignore_unknown!r}")
        return (
            f"{self.__class__.__qualname__}("
            f"{', '.join(parts)}"
            f")"
        )
    
    __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
    if '__repr__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__repr__', __repr__)


@_register(
    "Plans(tup=(CopyPlan(fields=('unknown', 'source')), EqPlan(fields=('unknown', 'source')), FrozenPlan(fields=('unkno"
    "wn', 'source'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('unknown', 'source'), cache=Fals"
    "e), InitPlan(fields=(InitPlan.Field(name='unknown', annotation=OpRef(name='init.fields.0.annotation'), default=OpR"
    "ef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, "
    "coerce=None, validate=None, check_type=None), InitPlan.Field(name='source', annotation=OpRef(name='init.fields.1.a"
    "nnotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_t"
    "ype=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_p"
    "arams=('unknown', 'source'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprP"
    "lan(fields=(ReprPlan.Field(name='unknown', kw_only=True, fn=None), ReprPlan.Field(name='source', kw_only=True, fn="
    "None)), id=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2fmarshal_2fobjects_2fmetadata_2fObjectSpecials(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__0__default,
    __dataclass__init__fields__1__annotation,
    __dataclass__init__fields__1__default,
    __dataclass__isinstance=isinstance,  # noqa
    __dataclass__None=None,  # noqa
    __dataclass__property=property,  # noqa
    __dataclass__TypeError=TypeError,  # noqa
    __dataclass__object_setattr=object.__setattr__,  # noqa
    __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
    __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
    __dataclass__MISSING=dataclasses.MISSING,  # noqa
    __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
    __dataclass__FunctionType=types.FunctionType,  # noqa
    __dataclass__FieldFnValidationError,  # noqa
    __dataclass__FieldTypeValidationError,  # noqa
    __dataclass__FnValidationError,  # noqa
):
    def __copy__(self):
        if self.__class__ is not __dataclass__cls:
            raise TypeError(self)
        return __dataclass__cls(  # noqa
            unknown=self.unknown,
            source=self.source,
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
            self.unknown == other.unknown and
            self.source == other.source
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'unknown',
        'source',
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
        'unknown',
        'source',
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
            self.unknown,
            self.source,
        ))
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        *,
        unknown: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        source: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
    ) -> __dataclass__None:
        __dataclass__object_setattr(self, 'unknown', unknown)
        __dataclass__object_setattr(self, 'source', source)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"unknown={self.unknown!r}")
        parts.append(f"source={self.source!r}")
        return (
            f"{self.__class__.__qualname__}("
            f"{', '.join(parts)}"
            f")"
        )
    
    __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
    if '__repr__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__repr__', __repr__)


@_register(
    "Plans(tup=(CopyPlan(fields=('name', 'type', 'marshal_name', 'unmarshal_names', 'metadata', 'options')), EqPlan(fie"
    "lds=('name', 'type', 'marshal_name', 'unmarshal_names', 'metadata', 'options')), FrozenPlan(fields=('name', 'type'"
    ", 'marshal_name', 'unmarshal_names', 'metadata', 'options'), allow_dynamic_dunder_attrs=False), HashPlan(action='a"
    "dd', fields=('name', 'type', 'marshal_name', 'unmarshal_names', 'metadata', 'options'), cache=False), InitPlan(fie"
    "lds=(InitPlan.Field(name='name', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory="
    "None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), Init"
    "Plan.Field(name='type', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, ini"
    "t=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fiel"
    "d(name='marshal_name', annotation=OpRef(name='init.fields.2.annotation'), default=None, default_factory=None, init"
    "=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field"
    "(name='unmarshal_names', annotation=OpRef(name='init.fields.3.annotation'), default=None, default_factory=None, in"
    "it=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fie"
    "ld(name='metadata', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default')"
    ", default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, chec"
    "k_type=None), InitPlan.Field(name='options', annotation=OpRef(name='init.fields.5.annotation'), default=OpRef(name"
    "='init.fields.5.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce="
    "None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('name', 'type', 'marshal"
    "_name', 'unmarshal_names', 'metadata', 'options'), frozen=True, slots=False, post_init_params=None, init_fns=(), v"
    "alidate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='name', kw_only=True, fn=None), ReprPlan.Field(name='type', "
    "kw_only=True, fn=None), ReprPlan.Field(name='marshal_name', kw_only=True, fn=None), ReprPlan.Field(name='unmarshal"
    "_names', kw_only=True, fn=None), ReprPlan.Field(name='metadata', kw_only=True, fn=None), ReprPlan.Field(name='opti"
    "ons', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2fmarshal_2fobjects_2fmetadata_2fFieldInfo(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__1__annotation,
    __dataclass__init__fields__2__annotation,
    __dataclass__init__fields__3__annotation,
    __dataclass__init__fields__4__annotation,
    __dataclass__init__fields__4__default,
    __dataclass__init__fields__5__annotation,
    __dataclass__init__fields__5__default,
    __dataclass__isinstance=isinstance,  # noqa
    __dataclass__None=None,  # noqa
    __dataclass__property=property,  # noqa
    __dataclass__TypeError=TypeError,  # noqa
    __dataclass__object_setattr=object.__setattr__,  # noqa
    __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
    __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
    __dataclass__MISSING=dataclasses.MISSING,  # noqa
    __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
    __dataclass__FunctionType=types.FunctionType,  # noqa
    __dataclass__FieldFnValidationError,  # noqa
    __dataclass__FieldTypeValidationError,  # noqa
    __dataclass__FnValidationError,  # noqa
):
    def __copy__(self):
        if self.__class__ is not __dataclass__cls:
            raise TypeError(self)
        return __dataclass__cls(  # noqa
            name=self.name,
            type=self.type,
            marshal_name=self.marshal_name,
            unmarshal_names=self.unmarshal_names,
            metadata=self.metadata,
            options=self.options,
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
            self.type == other.type and
            self.marshal_name == other.marshal_name and
            self.unmarshal_names == other.unmarshal_names and
            self.metadata == other.metadata and
            self.options == other.options
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'name',
        'type',
        'marshal_name',
        'unmarshal_names',
        'metadata',
        'options',
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
        'type',
        'marshal_name',
        'unmarshal_names',
        'metadata',
        'options',
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
            self.type,
            self.marshal_name,
            self.unmarshal_names,
            self.metadata,
            self.options,
        ))
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        *,
        name: __dataclass__init__fields__0__annotation,
        type: __dataclass__init__fields__1__annotation,
        marshal_name: __dataclass__init__fields__2__annotation,
        unmarshal_names: __dataclass__init__fields__3__annotation,
        metadata: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        options: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
    ) -> __dataclass__None:
        __dataclass__object_setattr(self, 'name', name)
        __dataclass__object_setattr(self, 'type', type)
        __dataclass__object_setattr(self, 'marshal_name', marshal_name)
        __dataclass__object_setattr(self, 'unmarshal_names', unmarshal_names)
        __dataclass__object_setattr(self, 'metadata', metadata)
        __dataclass__object_setattr(self, 'options', options)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"name={self.name!r}")
        parts.append(f"type={self.type!r}")
        parts.append(f"marshal_name={self.marshal_name!r}")
        parts.append(f"unmarshal_names={self.unmarshal_names!r}")
        parts.append(f"metadata={self.metadata!r}")
        parts.append(f"options={self.options!r}")
        return (
            f"{self.__class__.__qualname__}("
            f"{', '.join(parts)}"
            f")"
        )
    
    __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
    if '__repr__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__repr__', __repr__)


@_register(
    "Plans(tup=(CopyPlan(fields=('lst',)), EqPlan(fields=('lst',)), FrozenPlan(fields=('lst',), allow_dynamic_dunder_at"
    "trs=False), HashPlan(action='add', fields=('lst',), cache=False), InitPlan(fields=(InitPlan.Field(name='lst', anno"
    "tation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, fiel"
    "d_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self', std_params=('lst',),"
    " kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(OpRef(name='init.init_fns.0'), OpRe"
    "f(name='init.init_fns.1'), OpRef(name='init.init_fns.2')), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name="
    "'lst', kw_only=False, fn=None),), id=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2fmarshal_2fobjects_2fmetadata_2fFieldInfos(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__init_fns__0,
    __dataclass__init__init_fns__1,
    __dataclass__init__init_fns__2,
    __dataclass__isinstance=isinstance,  # noqa
    __dataclass__None=None,  # noqa
    __dataclass__property=property,  # noqa
    __dataclass__TypeError=TypeError,  # noqa
    __dataclass__object_setattr=object.__setattr__,  # noqa
    __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
    __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
    __dataclass__MISSING=dataclasses.MISSING,  # noqa
    __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
    __dataclass__FunctionType=types.FunctionType,  # noqa
    __dataclass__FieldFnValidationError,  # noqa
    __dataclass__FieldTypeValidationError,  # noqa
    __dataclass__FnValidationError,  # noqa
):
    def __copy__(self):
        if self.__class__ is not __dataclass__cls:
            raise TypeError(self)
        return __dataclass__cls(  # noqa
            lst=self.lst,
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
            self.lst == other.lst
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'lst',
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
        'lst',
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
            self.lst,
        ))
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        lst: __dataclass__init__fields__0__annotation,
    ) -> __dataclass__None:
        __dataclass__object_setattr(self, 'lst', lst)
        __dataclass__init__init_fns__0(self)
        __dataclass__init__init_fns__1(self)
        __dataclass__init__init_fns__2(self)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"lst={self.lst!r}")
        return (
            f"{self.__class__.__qualname__}("
            f"{', '.join(parts)}"
            f")"
        )
    
    __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
    if '__repr__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__repr__', __repr__)


@_register(
    "Plans(tup=(CopyPlan(fields=('fields', 'specials', 'attr_getter')), EqPlan(fields=('fields', 'specials', 'attr_gett"
    "er')), FrozenPlan(fields=('fields', 'specials', 'attr_getter'), allow_dynamic_dunder_attrs=False), HashPlan(action"
    "='add', fields=('fields', 'specials', 'attr_getter'), cache=False), InitPlan(fields=(InitPlan.Field(name='fields',"
    " annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False,"
    " field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='specials', anno"
    "tation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, "
    "init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.F"
    "ield(name='attr_getter', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.defa"
    "ult'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None,"
    " check_type=None)), self_param='self', std_params=('fields',), kw_only_params=('specials', 'attr_getter'), frozen="
    "True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='fie"
    "lds', kw_only=False, fn=None), ReprPlan.Field(name='specials', kw_only=True, fn=None), ReprPlan.Field(name='attr_g"
    "etter', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2fmarshal_2fobjects_2fmarshal_2fObjectMarshaler(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__1__annotation,
    __dataclass__init__fields__1__default,
    __dataclass__init__fields__2__annotation,
    __dataclass__init__fields__2__default,
    __dataclass__isinstance=isinstance,  # noqa
    __dataclass__None=None,  # noqa
    __dataclass__property=property,  # noqa
    __dataclass__TypeError=TypeError,  # noqa
    __dataclass__object_setattr=object.__setattr__,  # noqa
    __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
    __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
    __dataclass__MISSING=dataclasses.MISSING,  # noqa
    __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
    __dataclass__FunctionType=types.FunctionType,  # noqa
    __dataclass__FieldFnValidationError,  # noqa
    __dataclass__FieldTypeValidationError,  # noqa
    __dataclass__FnValidationError,  # noqa
):
    def __copy__(self):
        if self.__class__ is not __dataclass__cls:
            raise TypeError(self)
        return __dataclass__cls(  # noqa
            fields=self.fields,
            specials=self.specials,
            attr_getter=self.attr_getter,
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
            self.fields == other.fields and
            self.specials == other.specials and
            self.attr_getter == other.attr_getter
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'fields',
        'specials',
        'attr_getter',
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
        'fields',
        'specials',
        'attr_getter',
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
            self.fields,
            self.specials,
            self.attr_getter,
        ))
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        fields: __dataclass__init__fields__0__annotation,
        *,
        specials: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        attr_getter: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
    ) -> __dataclass__None:
        __dataclass__object_setattr(self, 'fields', fields)
        __dataclass__object_setattr(self, 'specials', specials)
        __dataclass__object_setattr(self, 'attr_getter', attr_getter)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"fields={self.fields!r}")
        parts.append(f"specials={self.specials!r}")
        parts.append(f"attr_getter={self.attr_getter!r}")
        return (
            f"{self.__class__.__qualname__}("
            f"{', '.join(parts)}"
            f")"
        )
    
    __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
    if '__repr__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__repr__', __repr__)


@_register(
    "Plans(tup=(CopyPlan(fields=('dct', 'specials')), EqPlan(fields=('dct', 'specials')), FrozenPlan(fields=('dct', 'sp"
    "ecials'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('dct', 'specials'), cache=False), Init"
    "Plan(fields=(InitPlan.Field(name='dct', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_f"
    "actory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None"
    "), InitPlan.Field(name='specials', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fie"
    "lds.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, vali"
    "date=None, check_type=None)), self_param='self', std_params=('dct',), kw_only_params=('specials',), frozen=True, s"
    "lots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='dct', kw_o"
    "nly=False, fn=None), ReprPlan.Field(name='specials', kw_only=True, fn=None)), id=False, terse=False, default_fn=No"
    "ne)))"
)
def _process_dataclass__omlish_2fmarshal_2fobjects_2fmarshal_2fSimpleObjectMarshalerFactory(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__1__annotation,
    __dataclass__init__fields__1__default,
    __dataclass__isinstance=isinstance,  # noqa
    __dataclass__None=None,  # noqa
    __dataclass__property=property,  # noqa
    __dataclass__TypeError=TypeError,  # noqa
    __dataclass__object_setattr=object.__setattr__,  # noqa
    __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
    __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
    __dataclass__MISSING=dataclasses.MISSING,  # noqa
    __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
    __dataclass__FunctionType=types.FunctionType,  # noqa
    __dataclass__FieldFnValidationError,  # noqa
    __dataclass__FieldTypeValidationError,  # noqa
    __dataclass__FnValidationError,  # noqa
):
    def __copy__(self):
        if self.__class__ is not __dataclass__cls:
            raise TypeError(self)
        return __dataclass__cls(  # noqa
            dct=self.dct,
            specials=self.specials,
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
            self.dct == other.dct and
            self.specials == other.specials
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'dct',
        'specials',
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
        'dct',
        'specials',
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
            self.dct,
            self.specials,
        ))
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        dct: __dataclass__init__fields__0__annotation,
        *,
        specials: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
    ) -> __dataclass__None:
        __dataclass__object_setattr(self, 'dct', dct)
        __dataclass__object_setattr(self, 'specials', specials)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"dct={self.dct!r}")
        parts.append(f"specials={self.specials!r}")
        return (
            f"{self.__class__.__qualname__}("
            f"{', '.join(parts)}"
            f")"
        )
    
    __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
    if '__repr__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__repr__', __repr__)


@_register(
    "Plans(tup=(CopyPlan(fields=('factory', 'fields_by_unmarshal_name', 'specials', 'defaults', 'embeds', 'embeds_by_un"
    "marshal_name', 'ignore_unknown')), EqPlan(fields=('factory', 'fields_by_unmarshal_name', 'specials', 'defaults', '"
    "embeds', 'embeds_by_unmarshal_name', 'ignore_unknown')), FrozenPlan(fields=('factory', 'fields_by_unmarshal_name',"
    " 'specials', 'defaults', 'embeds', 'embeds_by_unmarshal_name', 'ignore_unknown'), allow_dynamic_dunder_attrs=False"
    "), HashPlan(action='add', fields=('factory', 'fields_by_unmarshal_name', 'specials', 'defaults', 'embeds', 'embeds"
    "_by_unmarshal_name', 'ignore_unknown'), cache=False), InitPlan(fields=(InitPlan.Field(name='factory', annotation=O"
    "pRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=F"
    "ieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='fields_by_unmarshal_name', a"
    "nnotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, f"
    "ield_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='specials', annota"
    "tion=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, in"
    "it=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fie"
    "ld(name='defaults', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default')"
    ", default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, chec"
    "k_type=None), InitPlan.Field(name='embeds', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name="
    "'init.fields.4.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=N"
    "one, validate=None, check_type=None), InitPlan.Field(name='embeds_by_unmarshal_name', annotation=OpRef(name='init."
    "fields.5.annotation'), default=OpRef(name='init.fields.5.default'), default_factory=None, init=True, override=Fals"
    "e, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='ignore_unknow"
    "n', annotation=OpRef(name='init.fields.6.annotation'), default=OpRef(name='init.fields.6.default'), default_factor"
    "y=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), s"
    "elf_param='self', std_params=('factory', 'fields_by_unmarshal_name'), kw_only_params=('specials', 'defaults', 'emb"
    "eds', 'embeds_by_unmarshal_name', 'ignore_unknown'), frozen=True, slots=False, post_init_params=None, init_fns=(),"
    " validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='factory', kw_only=False, fn=None), ReprPlan.Field(name='f"
    "ields_by_unmarshal_name', kw_only=False, fn=None), ReprPlan.Field(name='specials', kw_only=True, fn=None), ReprPla"
    "n.Field(name='defaults', kw_only=True, fn=None), ReprPlan.Field(name='embeds', kw_only=True, fn=None), ReprPlan.Fi"
    "eld(name='embeds_by_unmarshal_name', kw_only=True, fn=None), ReprPlan.Field(name='ignore_unknown', kw_only=True, f"
    "n=None)), id=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2fmarshal_2fobjects_2funmarshal_2fObjectUnmarshaler(
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
    __dataclass__isinstance=isinstance,  # noqa
    __dataclass__None=None,  # noqa
    __dataclass__property=property,  # noqa
    __dataclass__TypeError=TypeError,  # noqa
    __dataclass__object_setattr=object.__setattr__,  # noqa
    __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
    __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
    __dataclass__MISSING=dataclasses.MISSING,  # noqa
    __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
    __dataclass__FunctionType=types.FunctionType,  # noqa
    __dataclass__FieldFnValidationError,  # noqa
    __dataclass__FieldTypeValidationError,  # noqa
    __dataclass__FnValidationError,  # noqa
):
    def __copy__(self):
        if self.__class__ is not __dataclass__cls:
            raise TypeError(self)
        return __dataclass__cls(  # noqa
            factory=self.factory,
            fields_by_unmarshal_name=self.fields_by_unmarshal_name,
            specials=self.specials,
            defaults=self.defaults,
            embeds=self.embeds,
            embeds_by_unmarshal_name=self.embeds_by_unmarshal_name,
            ignore_unknown=self.ignore_unknown,
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
            self.factory == other.factory and
            self.fields_by_unmarshal_name == other.fields_by_unmarshal_name and
            self.specials == other.specials and
            self.defaults == other.defaults and
            self.embeds == other.embeds and
            self.embeds_by_unmarshal_name == other.embeds_by_unmarshal_name and
            self.ignore_unknown == other.ignore_unknown
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'factory',
        'fields_by_unmarshal_name',
        'specials',
        'defaults',
        'embeds',
        'embeds_by_unmarshal_name',
        'ignore_unknown',
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
        'factory',
        'fields_by_unmarshal_name',
        'specials',
        'defaults',
        'embeds',
        'embeds_by_unmarshal_name',
        'ignore_unknown',
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
            self.factory,
            self.fields_by_unmarshal_name,
            self.specials,
            self.defaults,
            self.embeds,
            self.embeds_by_unmarshal_name,
            self.ignore_unknown,
        ))
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        factory: __dataclass__init__fields__0__annotation,
        fields_by_unmarshal_name: __dataclass__init__fields__1__annotation,
        *,
        specials: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        defaults: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        embeds: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        embeds_by_unmarshal_name: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
        ignore_unknown: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
    ) -> __dataclass__None:
        __dataclass__object_setattr(self, 'factory', factory)
        __dataclass__object_setattr(self, 'fields_by_unmarshal_name', fields_by_unmarshal_name)
        __dataclass__object_setattr(self, 'specials', specials)
        __dataclass__object_setattr(self, 'defaults', defaults)
        __dataclass__object_setattr(self, 'embeds', embeds)
        __dataclass__object_setattr(self, 'embeds_by_unmarshal_name', embeds_by_unmarshal_name)
        __dataclass__object_setattr(self, 'ignore_unknown', ignore_unknown)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"factory={self.factory!r}")
        parts.append(f"fields_by_unmarshal_name={self.fields_by_unmarshal_name!r}")
        parts.append(f"specials={self.specials!r}")
        parts.append(f"defaults={self.defaults!r}")
        parts.append(f"embeds={self.embeds!r}")
        parts.append(f"embeds_by_unmarshal_name={self.embeds_by_unmarshal_name!r}")
        parts.append(f"ignore_unknown={self.ignore_unknown!r}")
        return (
            f"{self.__class__.__qualname__}("
            f"{', '.join(parts)}"
            f")"
        )
    
    __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
    if '__repr__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__repr__', __repr__)


@_register(
    "Plans(tup=(CopyPlan(fields=('dct', 'specials')), EqPlan(fields=('dct', 'specials')), FrozenPlan(fields=('dct', 'sp"
    "ecials'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('dct', 'specials'), cache=False), Init"
    "Plan(fields=(InitPlan.Field(name='dct', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_f"
    "actory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None"
    "), InitPlan.Field(name='specials', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fie"
    "lds.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, vali"
    "date=None, check_type=None)), self_param='self', std_params=('dct',), kw_only_params=('specials',), frozen=True, s"
    "lots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='dct', kw_o"
    "nly=False, fn=None), ReprPlan.Field(name='specials', kw_only=True, fn=None)), id=False, terse=False, default_fn=No"
    "ne)))"
)
def _process_dataclass__omlish_2fmarshal_2fobjects_2funmarshal_2fSimpleObjectUnmarshalerFactory(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__1__annotation,
    __dataclass__init__fields__1__default,
    __dataclass__isinstance=isinstance,  # noqa
    __dataclass__None=None,  # noqa
    __dataclass__property=property,  # noqa
    __dataclass__TypeError=TypeError,  # noqa
    __dataclass__object_setattr=object.__setattr__,  # noqa
    __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
    __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
    __dataclass__MISSING=dataclasses.MISSING,  # noqa
    __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
    __dataclass__FunctionType=types.FunctionType,  # noqa
    __dataclass__FieldFnValidationError,  # noqa
    __dataclass__FieldTypeValidationError,  # noqa
    __dataclass__FnValidationError,  # noqa
):
    def __copy__(self):
        if self.__class__ is not __dataclass__cls:
            raise TypeError(self)
        return __dataclass__cls(  # noqa
            dct=self.dct,
            specials=self.specials,
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
            self.dct == other.dct and
            self.specials == other.specials
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'dct',
        'specials',
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
        'dct',
        'specials',
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
            self.dct,
            self.specials,
        ))
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        dct: __dataclass__init__fields__0__annotation,
        *,
        specials: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
    ) -> __dataclass__None:
        __dataclass__object_setattr(self, 'dct', dct)
        __dataclass__object_setattr(self, 'specials', specials)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"dct={self.dct!r}")
        parts.append(f"specials={self.specials!r}")
        return (
            f"{self.__class__.__qualname__}("
            f"{', '.join(parts)}"
            f")"
        )
    
    __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
    if '__repr__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__repr__', __repr__)


@_register(
    "Plans(tup=(CopyPlan(fields=('m',)), EqPlan(fields=('m',)), FrozenPlan(fields=('m',), allow_dynamic_dunder_attrs=Fa"
    "lse), HashPlan(action='add', fields=('m',), cache=False), InitPlan(fields=(InitPlan.Field(name='m', annotation=OpR"
    "ef(name='init.fields.0.annotation'), default=None, default_factory=OpRef(name='init.fields.0.default_factory'), in"
    "it=True, override=False, field_type=FieldType.INSTANCE, coerce=OpRef(name='init.fields.0.coerce'), validate=None, "
    "check_type=None),), self_param='self', std_params=('m',), kw_only_params=(), frozen=True, slots=False, post_init_p"
    "arams=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='m', kw_only=False, fn=None),), id"
    "=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2fmarshal_2ffactories_2ftypemap_2fTypeMapMarshalerFactory(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__0__coerce,
    __dataclass__init__fields__0__default_factory,
    __dataclass__isinstance=isinstance,  # noqa
    __dataclass__None=None,  # noqa
    __dataclass__property=property,  # noqa
    __dataclass__TypeError=TypeError,  # noqa
    __dataclass__object_setattr=object.__setattr__,  # noqa
    __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
    __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
    __dataclass__MISSING=dataclasses.MISSING,  # noqa
    __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
    __dataclass__FunctionType=types.FunctionType,  # noqa
    __dataclass__FieldFnValidationError,  # noqa
    __dataclass__FieldTypeValidationError,  # noqa
    __dataclass__FnValidationError,  # noqa
):
    def __copy__(self):
        if self.__class__ is not __dataclass__cls:
            raise TypeError(self)
        return __dataclass__cls(  # noqa
            m=self.m,
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
            self.m == other.m
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'm',
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
        ))
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        m: __dataclass__init__fields__0__annotation = __dataclass__HAS_DEFAULT_FACTORY,
    ) -> __dataclass__None:
        if m is __dataclass__HAS_DEFAULT_FACTORY:
            m = __dataclass__init__fields__0__default_factory()
        m = __dataclass__init__fields__0__coerce(m)
        __dataclass__object_setattr(self, 'm', m)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"m={self.m!r}")
        return (
            f"{self.__class__.__qualname__}("
            f"{', '.join(parts)}"
            f")"
        )
    
    __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
    if '__repr__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__repr__', __repr__)


@_register(
    "Plans(tup=(CopyPlan(fields=('u',)), EqPlan(fields=('u',)), FrozenPlan(fields=('u',), allow_dynamic_dunder_attrs=Fa"
    "lse), HashPlan(action='add', fields=('u',), cache=False), InitPlan(fields=(InitPlan.Field(name='u', annotation=OpR"
    "ef(name='init.fields.0.annotation'), default=None, default_factory=OpRef(name='init.fields.0.default_factory'), in"
    "it=True, override=False, field_type=FieldType.INSTANCE, coerce=OpRef(name='init.fields.0.coerce'), validate=None, "
    "check_type=None),), self_param='self', std_params=('u',), kw_only_params=(), frozen=True, slots=False, post_init_p"
    "arams=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='u', kw_only=False, fn=None),), id"
    "=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2fmarshal_2ffactories_2ftypemap_2fTypeMapUnmarshalerFactory(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__0__coerce,
    __dataclass__init__fields__0__default_factory,
    __dataclass__isinstance=isinstance,  # noqa
    __dataclass__None=None,  # noqa
    __dataclass__property=property,  # noqa
    __dataclass__TypeError=TypeError,  # noqa
    __dataclass__object_setattr=object.__setattr__,  # noqa
    __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
    __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
    __dataclass__MISSING=dataclasses.MISSING,  # noqa
    __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
    __dataclass__FunctionType=types.FunctionType,  # noqa
    __dataclass__FieldFnValidationError,  # noqa
    __dataclass__FieldTypeValidationError,  # noqa
    __dataclass__FnValidationError,  # noqa
):
    def __copy__(self):
        if self.__class__ is not __dataclass__cls:
            raise TypeError(self)
        return __dataclass__cls(  # noqa
            u=self.u,
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
            self.u == other.u
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'u',
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
        ))
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        u: __dataclass__init__fields__0__annotation = __dataclass__HAS_DEFAULT_FACTORY,
    ) -> __dataclass__None:
        if u is __dataclass__HAS_DEFAULT_FACTORY:
            u = __dataclass__init__fields__0__default_factory()
        u = __dataclass__init__fields__0__coerce(u)
        __dataclass__object_setattr(self, 'u', u)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"u={self.u!r}")
        return (
            f"{self.__class__.__qualname__}("
            f"{', '.join(parts)}"
            f")"
        )
    
    __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
    if '__repr__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__repr__', __repr__)


@_register(
    "Plans(tup=(CopyPlan(fields=('ty',)), EqPlan(fields=('ty',)), FrozenPlan(fields=('ty',), allow_dynamic_dunder_attrs"
    "=False), HashPlan(action='add', fields=('ty',), cache=False), InitPlan(fields=(InitPlan.Field(name='ty', annotatio"
    "n=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_typ"
    "e=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self', std_params=('ty',), kw_on"
    "ly_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(Rep"
    "rPlan.Field(name='ty', kw_only=False, fn=None),), id=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2fmarshal_2fsingular_2fprimitives_2fPrimitiveMarshalerUnmarshaler(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__isinstance=isinstance,  # noqa
    __dataclass__None=None,  # noqa
    __dataclass__property=property,  # noqa
    __dataclass__TypeError=TypeError,  # noqa
    __dataclass__object_setattr=object.__setattr__,  # noqa
    __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
    __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
    __dataclass__MISSING=dataclasses.MISSING,  # noqa
    __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
    __dataclass__FunctionType=types.FunctionType,  # noqa
    __dataclass__FieldFnValidationError,  # noqa
    __dataclass__FieldTypeValidationError,  # noqa
    __dataclass__FnValidationError,  # noqa
):
    def __copy__(self):
        if self.__class__ is not __dataclass__cls:
            raise TypeError(self)
        return __dataclass__cls(  # noqa
            ty=self.ty,
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
            self.ty == other.ty
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'ty',
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
        'ty',
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
            self.ty,
        ))
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        ty: __dataclass__init__fields__0__annotation,
    ) -> __dataclass__None:
        __dataclass__object_setattr(self, 'ty', ty)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"ty={self.ty!r}")
        return (
            f"{self.__class__.__qualname__}("
            f"{', '.join(parts)}"
            f")"
        )
    
    __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
    if '__repr__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__repr__', __repr__)


@_register(
    "Plans(tup=(CopyPlan(fields=('impls', 'tt', 'allow_partial')), EqPlan(fields=('impls', 'tt', 'allow_partial')), Fro"
    "zenPlan(fields=('impls', 'tt', 'allow_partial'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields="
    "('impls', 'tt', 'allow_partial'), cache=False), InitPlan(fields=(InitPlan.Field(name='impls', annotation=OpRef(nam"
    "e='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType"
    ".INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='tt', annotation=OpRef(name='init.fie"
    "lds.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, "
    "field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='allow_partial', "
    "annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=No"
    "ne, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_"
    "param='self', std_params=('impls', 'tt'), kw_only_params=('allow_partial',), frozen=True, slots=False, post_init_p"
    "arams=None, init_fns=(OpRef(name='init.init_fns.0'),), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='imp"
    "ls', kw_only=False, fn=None), ReprPlan.Field(name='tt', kw_only=False, fn=None), ReprPlan.Field(name='allow_partia"
    "l', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2fmarshal_2fpolymorphism_2funions_2f_00BasePolymorphismUnionFactory(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__1__annotation,
    __dataclass__init__fields__1__default,
    __dataclass__init__fields__2__annotation,
    __dataclass__init__fields__2__default,
    __dataclass__init__init_fns__0,
    __dataclass__isinstance=isinstance,  # noqa
    __dataclass__None=None,  # noqa
    __dataclass__property=property,  # noqa
    __dataclass__TypeError=TypeError,  # noqa
    __dataclass__object_setattr=object.__setattr__,  # noqa
    __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
    __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
    __dataclass__MISSING=dataclasses.MISSING,  # noqa
    __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
    __dataclass__FunctionType=types.FunctionType,  # noqa
    __dataclass__FieldFnValidationError,  # noqa
    __dataclass__FieldTypeValidationError,  # noqa
    __dataclass__FnValidationError,  # noqa
):
    def __copy__(self):
        if self.__class__ is not __dataclass__cls:
            raise TypeError(self)
        return __dataclass__cls(  # noqa
            impls=self.impls,
            tt=self.tt,
            allow_partial=self.allow_partial,
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
            self.impls == other.impls and
            self.tt == other.tt and
            self.allow_partial == other.allow_partial
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'impls',
        'tt',
        'allow_partial',
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
        'impls',
        'tt',
        'allow_partial',
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
            self.impls,
            self.tt,
            self.allow_partial,
        ))
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        impls: __dataclass__init__fields__0__annotation,
        tt: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        *,
        allow_partial: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
    ) -> __dataclass__None:
        __dataclass__object_setattr(self, 'impls', impls)
        __dataclass__object_setattr(self, 'tt', tt)
        __dataclass__object_setattr(self, 'allow_partial', allow_partial)
        __dataclass__init__init_fns__0(self)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"impls={self.impls!r}")
        parts.append(f"tt={self.tt!r}")
        parts.append(f"allow_partial={self.allow_partial!r}")
        return (
            f"{self.__class__.__qualname__}("
            f"{', '.join(parts)}"
            f")"
        )
    
    __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
    if '__repr__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__repr__', __repr__)


@_register(
    "Plans(tup=(CopyPlan(fields=('impls', 'tt', 'allow_partial')), EqPlan(fields=('impls', 'tt', 'allow_partial')), Fro"
    "zenPlan(fields=('impls', 'tt', 'allow_partial'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields="
    "('impls', 'tt', 'allow_partial'), cache=False), InitPlan(fields=(InitPlan.Field(name='impls', annotation=OpRef(nam"
    "e='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType"
    ".INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='tt', annotation=OpRef(name='init.fie"
    "lds.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, "
    "field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='allow_partial', "
    "annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=No"
    "ne, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_"
    "param='self', std_params=('impls', 'tt'), kw_only_params=('allow_partial',), frozen=True, slots=False, post_init_p"
    "arams=None, init_fns=(OpRef(name='init.init_fns.0'),), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='imp"
    "ls', kw_only=False, fn=None), ReprPlan.Field(name='tt', kw_only=False, fn=None), ReprPlan.Field(name='allow_partia"
    "l', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2fmarshal_2fpolymorphism_2funions_2fPolymorphismUnionMarshalerFactory(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__1__annotation,
    __dataclass__init__fields__1__default,
    __dataclass__init__fields__2__annotation,
    __dataclass__init__fields__2__default,
    __dataclass__init__init_fns__0,
    __dataclass__isinstance=isinstance,  # noqa
    __dataclass__None=None,  # noqa
    __dataclass__property=property,  # noqa
    __dataclass__TypeError=TypeError,  # noqa
    __dataclass__object_setattr=object.__setattr__,  # noqa
    __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
    __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
    __dataclass__MISSING=dataclasses.MISSING,  # noqa
    __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
    __dataclass__FunctionType=types.FunctionType,  # noqa
    __dataclass__FieldFnValidationError,  # noqa
    __dataclass__FieldTypeValidationError,  # noqa
    __dataclass__FnValidationError,  # noqa
):
    def __copy__(self):
        if self.__class__ is not __dataclass__cls:
            raise TypeError(self)
        return __dataclass__cls(  # noqa
            impls=self.impls,
            tt=self.tt,
            allow_partial=self.allow_partial,
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
            self.impls == other.impls and
            self.tt == other.tt and
            self.allow_partial == other.allow_partial
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'impls',
        'tt',
        'allow_partial',
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
        'impls',
        'tt',
        'allow_partial',
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
            self.impls,
            self.tt,
            self.allow_partial,
        ))
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        impls: __dataclass__init__fields__0__annotation,
        tt: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        *,
        allow_partial: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
    ) -> __dataclass__None:
        __dataclass__object_setattr(self, 'impls', impls)
        __dataclass__object_setattr(self, 'tt', tt)
        __dataclass__object_setattr(self, 'allow_partial', allow_partial)
        __dataclass__init__init_fns__0(self)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"impls={self.impls!r}")
        parts.append(f"tt={self.tt!r}")
        parts.append(f"allow_partial={self.allow_partial!r}")
        return (
            f"{self.__class__.__qualname__}("
            f"{', '.join(parts)}"
            f")"
        )
    
    __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
    if '__repr__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__repr__', __repr__)


@_register(
    "Plans(tup=(CopyPlan(fields=('impls', 'tt', 'allow_partial')), EqPlan(fields=('impls', 'tt', 'allow_partial')), Fro"
    "zenPlan(fields=('impls', 'tt', 'allow_partial'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields="
    "('impls', 'tt', 'allow_partial'), cache=False), InitPlan(fields=(InitPlan.Field(name='impls', annotation=OpRef(nam"
    "e='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType"
    ".INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='tt', annotation=OpRef(name='init.fie"
    "lds.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, "
    "field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='allow_partial', "
    "annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=No"
    "ne, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_"
    "param='self', std_params=('impls', 'tt'), kw_only_params=('allow_partial',), frozen=True, slots=False, post_init_p"
    "arams=None, init_fns=(OpRef(name='init.init_fns.0'),), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='imp"
    "ls', kw_only=False, fn=None), ReprPlan.Field(name='tt', kw_only=False, fn=None), ReprPlan.Field(name='allow_partia"
    "l', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2fmarshal_2fpolymorphism_2funions_2fPolymorphismUnionUnmarshalerFactory(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__1__annotation,
    __dataclass__init__fields__1__default,
    __dataclass__init__fields__2__annotation,
    __dataclass__init__fields__2__default,
    __dataclass__init__init_fns__0,
    __dataclass__isinstance=isinstance,  # noqa
    __dataclass__None=None,  # noqa
    __dataclass__property=property,  # noqa
    __dataclass__TypeError=TypeError,  # noqa
    __dataclass__object_setattr=object.__setattr__,  # noqa
    __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
    __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
    __dataclass__MISSING=dataclasses.MISSING,  # noqa
    __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
    __dataclass__FunctionType=types.FunctionType,  # noqa
    __dataclass__FieldFnValidationError,  # noqa
    __dataclass__FieldTypeValidationError,  # noqa
    __dataclass__FnValidationError,  # noqa
):
    def __copy__(self):
        if self.__class__ is not __dataclass__cls:
            raise TypeError(self)
        return __dataclass__cls(  # noqa
            impls=self.impls,
            tt=self.tt,
            allow_partial=self.allow_partial,
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
            self.impls == other.impls and
            self.tt == other.tt and
            self.allow_partial == other.allow_partial
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'impls',
        'tt',
        'allow_partial',
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
        'impls',
        'tt',
        'allow_partial',
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
            self.impls,
            self.tt,
            self.allow_partial,
        ))
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        impls: __dataclass__init__fields__0__annotation,
        tt: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        *,
        allow_partial: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
    ) -> __dataclass__None:
        __dataclass__object_setattr(self, 'impls', impls)
        __dataclass__object_setattr(self, 'tt', tt)
        __dataclass__object_setattr(self, 'allow_partial', allow_partial)
        __dataclass__init__init_fns__0(self)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"impls={self.impls!r}")
        parts.append(f"tt={self.tt!r}")
        parts.append(f"allow_partial={self.allow_partial!r}")
        return (
            f"{self.__class__.__qualname__}("
            f"{', '.join(parts)}"
            f")"
        )
    
    __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
    if '__repr__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__repr__', __repr__)


@_register(
    "Plans(tup=(CopyPlan(fields=('ty',)), EqPlan(fields=('ty',)), FrozenPlan(fields=('ty',), allow_dynamic_dunder_attrs"
    "=False), HashPlan(action='add', fields=('ty',), cache=False), InitPlan(fields=(InitPlan.Field(name='ty', annotatio"
    "n=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_typ"
    "e=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self', std_params=('ty',), kw_on"
    "ly_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(Rep"
    "rPlan.Field(name='ty', kw_only=False, fn=None),), id=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2fmarshal_2fsingular_2fbase64_2fBase64MarshalerUnmarshaler(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__isinstance=isinstance,  # noqa
    __dataclass__None=None,  # noqa
    __dataclass__property=property,  # noqa
    __dataclass__TypeError=TypeError,  # noqa
    __dataclass__object_setattr=object.__setattr__,  # noqa
    __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
    __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
    __dataclass__MISSING=dataclasses.MISSING,  # noqa
    __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
    __dataclass__FunctionType=types.FunctionType,  # noqa
    __dataclass__FieldFnValidationError,  # noqa
    __dataclass__FieldTypeValidationError,  # noqa
    __dataclass__FnValidationError,  # noqa
):
    def __copy__(self):
        if self.__class__ is not __dataclass__cls:
            raise TypeError(self)
        return __dataclass__cls(  # noqa
            ty=self.ty,
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
            self.ty == other.ty
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'ty',
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
        'ty',
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
            self.ty,
        ))
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        ty: __dataclass__init__fields__0__annotation,
    ) -> __dataclass__None:
        __dataclass__object_setattr(self, 'ty', ty)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"ty={self.ty!r}")
        return (
            f"{self.__class__.__qualname__}("
            f"{', '.join(parts)}"
            f")"
        )
    
    __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
    if '__repr__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__repr__', __repr__)
