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
    "Plans(tup=(CopyPlan(fields=('lst',)), EqPlan(fields=('lst',)), FrozenPlan(fields=('lst',), allow_dynamic_dunder_at"
    "trs=False), HashPlan(action='add', fields=('lst',), cache=True), InitPlan(fields=(InitPlan.Field(name='lst', annot"
    "ation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field"
    "_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self', std_params=('lst',), "
    "kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields"
    "=(ReprPlan.Field(name='lst', kw_only=False, fn=None),), id=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2finject_2forigins_2fOrigin(
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
        try:
            return self.__dataclass_hash__
        except AttributeError:
            pass
        object.__setattr__(
            self,
            '__dataclass_hash__',
            h := hash((
                self.lst,
            ))
        )
        return h
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        lst: __dataclass__init__fields__0__annotation,
    ) -> __dataclass__None:
        __dataclass__object_setattr(self, 'lst', lst)
    
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
    "Plans(tup=(CopyPlan(fields=('lst',)), EqPlan(fields=('lst',)), FrozenPlan(fields=('lst',), allow_dynamic_dunder_at"
    "trs=False), HashPlan(action='add', fields=('lst',), cache=True), InitPlan(fields=(InitPlan.Field(name='lst', annot"
    "ation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field"
    "_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self', std_params=('lst',), "
    "kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields"
    "=(ReprPlan.Field(name='lst', kw_only=False, fn=None),), id=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2finject_2forigins_2fOrigins(
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
        try:
            return self.__dataclass_hash__
        except AttributeError:
            pass
        object.__setattr__(
            self,
            '__dataclass_hash__',
            h := hash((
                self.lst,
            ))
        )
        return h
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        lst: __dataclass__init__fields__0__annotation,
    ) -> __dataclass__None:
        __dataclass__object_setattr(self, 'lst', lst)
    
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
    "Plans(tup=(CopyPlan(fields=('es', 'cs')), EqPlan(fields=('es', 'cs')), FrozenPlan(fields=('es', 'cs'), allow_dynam"
    "ic_dunder_attrs=False), HashPlan(action='add', fields=('es', 'cs'), cache=False), InitPlan(fields=(InitPlan.Field("
    "name='es', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'), default"
    "_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=No"
    "ne), InitPlan.Field(name='cs', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields."
    "1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate"
    "=None, check_type=None)), self_param='self', std_params=('es', 'cs'), kw_only_params=(), frozen=True, slots=False,"
    " post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='es', kw_only=False, f"
    "n=None), ReprPlan.Field(name='cs', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2finject_2felements_2fElements(
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
            es=self.es,
            cs=self.cs,
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
            self.es == other.es and
            self.cs == other.cs
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'es',
        'cs',
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
        'es',
        'cs',
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
            self.es,
            self.cs,
        ))
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        es: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        cs: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
    ) -> __dataclass__None:
        __dataclass__object_setattr(self, 'es', es)
        __dataclass__object_setattr(self, 'cs', cs)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"es={self.es!r}")
        parts.append(f"cs={self.cs!r}")
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
    "Plans(tup=(CopyPlan(fields=('ty', 'tag')), EqPlan(fields=('ty', 'tag')), FrozenPlan(fields=('ty', 'tag'), allow_dy"
    "namic_dunder_attrs=False), HashPlan(action='add', fields=('ty', 'tag'), cache=True), InitPlan(fields=(InitPlan.Fie"
    "ld(name='ty', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, ov"
    "erride=False, field_type=FieldType.INSTANCE, coerce=OpRef(name='init.fields.0.coerce'), validate=None, check_type="
    "None), InitPlan.Field(name='tag', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fiel"
    "ds.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valid"
    "ate=OpRef(name='init.fields.1.validate'), check_type=None)), self_param='self', std_params=('ty',), kw_only_params"
    "=('tag',), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPl"
    "an.Field(name='ty', kw_only=False, fn=None), ReprPlan.Field(name='tag', kw_only=True, fn=OpRef(name='repr.fns.1.fn"
    "'))), id=False, terse=True, default_fn=None)))"
)
def _process_dataclass__omlish_2finject_2fkeys_2fKey(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__0__coerce,
    __dataclass__init__fields__1__annotation,
    __dataclass__init__fields__1__default,
    __dataclass__init__fields__1__validate,
    __dataclass__repr__fns__1__fn,
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
            tag=self.tag,
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
            self.ty == other.ty and
            self.tag == other.tag
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'ty',
        'tag',
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
        'tag',
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
        try:
            return self.__dataclass_hash__
        except AttributeError:
            pass
        object.__setattr__(
            self,
            '__dataclass_hash__',
            h := hash((
                self.ty,
                self.tag,
            ))
        )
        return h
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        ty: __dataclass__init__fields__0__annotation,
        *,
        tag: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
    ) -> __dataclass__None:
        ty = __dataclass__init__fields__0__coerce(ty)
        if not __dataclass__init__fields__1__validate(tag): 
            raise __dataclass__FieldFnValidationError(
                obj=self,
                fn=__dataclass__init__fields__1__validate,
                field='tag',
                value=tag,
            )
        __dataclass__object_setattr(self, 'ty', ty)
        __dataclass__object_setattr(self, 'tag', tag)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"{self.ty!r}")
        if (s := __dataclass__repr__fns__1__fn(self.tag)) is not None:
            parts.append(f"tag={s}")
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
    "Plans(tup=(CopyPlan(fields=('fn',)), EqPlan(fields=('fn',)), FrozenPlan(fields=('fn',), allow_dynamic_dunder_attrs"
    "=False), HashPlan(action='add', fields=('fn',), cache=True), InitPlan(fields=(InitPlan.Field(name='fn', annotation"
    "=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type"
    "=FieldType.INSTANCE, coerce=None, validate=OpRef(name='init.fields.0.validate'), check_type=None),), self_param='s"
    "elf', std_params=('fn',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validat"
    "e_fns=()), ReprPlan(fields=(ReprPlan.Field(name='fn', kw_only=False, fn=None),), id=False, terse=False, default_fn"
    "=None)))"
)
def _process_dataclass__omlish_2finject_2fproviders_2fAsyncFnProvider(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__0__validate,
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
            fn=self.fn,
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
            self.fn == other.fn
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'fn',
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
        'fn',
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
        try:
            return self.__dataclass_hash__
        except AttributeError:
            pass
        object.__setattr__(
            self,
            '__dataclass_hash__',
            h := hash((
                self.fn,
            ))
        )
        return h
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        fn: __dataclass__init__fields__0__annotation,
    ) -> __dataclass__None:
        if not __dataclass__init__fields__0__validate(fn): 
            raise __dataclass__FieldFnValidationError(
                obj=self,
                fn=__dataclass__init__fields__0__validate,
                field='fn',
                value=fn,
            )
        __dataclass__object_setattr(self, 'fn', fn)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"fn={self.fn!r}")
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
    "Plans(tup=(CopyPlan(fields=('fn',)), EqPlan(fields=('fn',)), FrozenPlan(fields=('fn',), allow_dynamic_dunder_attrs"
    "=False), HashPlan(action='add', fields=('fn',), cache=True), InitPlan(fields=(InitPlan.Field(name='fn', annotation"
    "=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type"
    "=FieldType.INSTANCE, coerce=None, validate=OpRef(name='init.fields.0.validate'), check_type=None),), self_param='s"
    "elf', std_params=('fn',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validat"
    "e_fns=()), ReprPlan(fields=(ReprPlan.Field(name='fn', kw_only=False, fn=None),), id=False, terse=False, default_fn"
    "=None)))"
)
def _process_dataclass__omlish_2finject_2fproviders_2fFnProvider(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__0__validate,
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
            fn=self.fn,
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
            self.fn == other.fn
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'fn',
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
        'fn',
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
        try:
            return self.__dataclass_hash__
        except AttributeError:
            pass
        object.__setattr__(
            self,
            '__dataclass_hash__',
            h := hash((
                self.fn,
            ))
        )
        return h
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        fn: __dataclass__init__fields__0__annotation,
    ) -> __dataclass__None:
        if not __dataclass__init__fields__0__validate(fn): 
            raise __dataclass__FieldFnValidationError(
                obj=self,
                fn=__dataclass__init__fields__0__validate,
                field='fn',
                value=fn,
            )
        __dataclass__object_setattr(self, 'fn', fn)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"fn={self.fn!r}")
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
    "=False), HashPlan(action='add', fields=('ty',), cache=True), InitPlan(fields=(InitPlan.Field(name='ty', annotation"
    "=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type"
    "=FieldType.INSTANCE, coerce=OpRef(name='init.fields.0.coerce'), validate=None, check_type=None),), self_param='sel"
    "f', std_params=('ty',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_"
    "fns=()), ReprPlan(fields=(ReprPlan.Field(name='ty', kw_only=False, fn=None),), id=False, terse=False, default_fn=N"
    "one)))"
)
def _process_dataclass__omlish_2finject_2fproviders_2fCtorProvider(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__0__coerce,
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
        try:
            return self.__dataclass_hash__
        except AttributeError:
            pass
        object.__setattr__(
            self,
            '__dataclass_hash__',
            h := hash((
                self.ty,
            ))
        )
        return h
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        ty: __dataclass__init__fields__0__annotation,
    ) -> __dataclass__None:
        ty = __dataclass__init__fields__0__coerce(ty)
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
    "Plans(tup=(CopyPlan(fields=('v',)), EqPlan(fields=('v',)), FrozenPlan(fields=('v',), allow_dynamic_dunder_attrs=Fa"
    "lse), HashPlan(action='add', fields=('v',), cache=True), InitPlan(fields=(InitPlan.Field(name='v', annotation=OpRe"
    "f(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=Fiel"
    "dType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self', std_params=('v',), kw_only_para"
    "ms=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.F"
    "ield(name='v', kw_only=False, fn=None),), id=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2finject_2fproviders_2fConstProvider(
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
            v=self.v,
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
            self.v == other.v
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'v',
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
        'v',
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
        try:
            return self.__dataclass_hash__
        except AttributeError:
            pass
        object.__setattr__(
            self,
            '__dataclass_hash__',
            h := hash((
                self.v,
            ))
        )
        return h
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        v: __dataclass__init__fields__0__annotation,
    ) -> __dataclass__None:
        __dataclass__object_setattr(self, 'v', v)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"v={self.v!r}")
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
    "Plans(tup=(CopyPlan(fields=('k',)), EqPlan(fields=('k',)), FrozenPlan(fields=('k',), allow_dynamic_dunder_attrs=Fa"
    "lse), HashPlan(action='add', fields=('k',), cache=True), InitPlan(fields=(InitPlan.Field(name='k', annotation=OpRe"
    "f(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=Fiel"
    "dType.INSTANCE, coerce=OpRef(name='init.fields.0.coerce'), validate=None, check_type=None),), self_param='self', s"
    "td_params=('k',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()"
    "), ReprPlan(fields=(ReprPlan.Field(name='k', kw_only=False, fn=None),), id=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2finject_2fproviders_2fLinkProvider(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__0__coerce,
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
            k=self.k,
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
            self.k == other.k
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'k',
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
        'k',
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
        try:
            return self.__dataclass_hash__
        except AttributeError:
            pass
        object.__setattr__(
            self,
            '__dataclass_hash__',
            h := hash((
                self.k,
            ))
        )
        return h
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        k: __dataclass__init__fields__0__annotation,
    ) -> __dataclass__None:
        k = __dataclass__init__fields__0__coerce(k)
        __dataclass__object_setattr(self, 'k', k)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"k={self.k!r}")
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
    "Plans(tup=(CopyPlan(fields=('key', 'provider', 'scope')), EqPlan(fields=('key', 'provider', 'scope')), FrozenPlan("
    "fields=('key', 'provider', 'scope'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('key', 'pro"
    "vider', 'scope'), cache=True), InitPlan(fields=(InitPlan.Field(name='key', annotation=OpRef(name='init.fields.0.an"
    "notation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=O"
    "pRef(name='init.fields.0.coerce'), validate=None, check_type=None), InitPlan.Field(name='provider', annotation=OpR"
    "ef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=Fie"
    "ldType.INSTANCE, coerce=OpRef(name='init.fields.1.coerce'), validate=None, check_type=None), InitPlan.Field(name='"
    "scope', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_fa"
    "ctory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=OpRef(name='init.fields.2.coerce'), v"
    "alidate=None, check_type=None)), self_param='self', std_params=('key', 'provider', 'scope'), kw_only_params=(), fr"
    "ozen=True, slots=False, post_init_params=(), init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='"
    "key', kw_only=False, fn=None), ReprPlan.Field(name='provider', kw_only=False, fn=None), ReprPlan.Field(name='scope"
    "', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2finject_2fbindings_2fBinding(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__0__coerce,
    __dataclass__init__fields__1__annotation,
    __dataclass__init__fields__1__coerce,
    __dataclass__init__fields__2__annotation,
    __dataclass__init__fields__2__coerce,
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
            key=self.key,
            provider=self.provider,
            scope=self.scope,
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
            self.key == other.key and
            self.provider == other.provider and
            self.scope == other.scope
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'key',
        'provider',
        'scope',
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
        'key',
        'provider',
        'scope',
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
        try:
            return self.__dataclass_hash__
        except AttributeError:
            pass
        object.__setattr__(
            self,
            '__dataclass_hash__',
            h := hash((
                self.key,
                self.provider,
                self.scope,
            ))
        )
        return h
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        key: __dataclass__init__fields__0__annotation,
        provider: __dataclass__init__fields__1__annotation,
        scope: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
    ) -> __dataclass__None:
        key = __dataclass__init__fields__0__coerce(key)
        provider = __dataclass__init__fields__1__coerce(provider)
        scope = __dataclass__init__fields__2__coerce(scope)
        __dataclass__object_setattr(self, 'key', key)
        __dataclass__object_setattr(self, 'provider', provider)
        __dataclass__object_setattr(self, 'scope', scope)
        self.__post_init__()
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"key={self.key!r}")
        parts.append(f"provider={self.provider!r}")
        parts.append(f"scope={self.scope!r}")
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
    "Plans(tup=(CopyPlan(fields=('key',)), EqPlan(fields=('key',)), FrozenPlan(fields=('key',), allow_dynamic_dunder_at"
    "trs=False), HashPlan(action='add', fields=('key',), cache=True), InitPlan(fields=(InitPlan.Field(name='key', annot"
    "ation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field"
    "_type=FieldType.INSTANCE, coerce=OpRef(name='init.fields.0.coerce'), validate=None, check_type=None),), self_param"
    "='self', std_params=('key',), kw_only_params=(), frozen=True, slots=False, post_init_params=(), init_fns=(), valid"
    "ate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='key', kw_only=False, fn=None),), id=False, terse=False, default"
    "_fn=None)))"
)
def _process_dataclass__omlish_2finject_2feagers_2fEager(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__0__coerce,
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
            key=self.key,
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
            self.key == other.key
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'key',
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
        'key',
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
        try:
            return self.__dataclass_hash__
        except AttributeError:
            pass
        object.__setattr__(
            self,
            '__dataclass_hash__',
            h := hash((
                self.key,
            ))
        )
        return h
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        key: __dataclass__init__fields__0__annotation,
    ) -> __dataclass__None:
        key = __dataclass__init__fields__0__coerce(key)
        __dataclass__object_setattr(self, 'key', key)
        self.__post_init__()
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"key={self.key!r}")
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
    "Plans(tup=(CopyPlan(fields=('key',)), EqPlan(fields=('key',)), FrozenPlan(fields=('key',), allow_dynamic_dunder_at"
    "trs=False), HashPlan(action='add', fields=('key',), cache=True), InitPlan(fields=(InitPlan.Field(name='key', annot"
    "ation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field"
    "_type=FieldType.INSTANCE, coerce=OpRef(name='init.fields.0.coerce'), validate=None, check_type=None),), self_param"
    "='self', std_params=('key',), kw_only_params=(), frozen=True, slots=False, post_init_params=(), init_fns=(), valid"
    "ate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='key', kw_only=False, fn=None),), id=False, terse=False, default"
    "_fn=None)))"
)
def _process_dataclass__omlish_2finject_2fprivates_2fExpose(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__0__coerce,
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
            key=self.key,
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
            self.key == other.key
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'key',
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
        'key',
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
        try:
            return self.__dataclass_hash__
        except AttributeError:
            pass
        object.__setattr__(
            self,
            '__dataclass_hash__',
            h := hash((
                self.key,
            ))
        )
        return h
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        key: __dataclass__init__fields__0__annotation,
    ) -> __dataclass__None:
        key = __dataclass__init__fields__0__coerce(key)
        __dataclass__object_setattr(self, 'key', key)
        self.__post_init__()
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"key={self.key!r}")
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
    "Plans(tup=(CopyPlan(fields=('elements',)), EqPlan(fields=('elements',)), FrozenPlan(fields=('elements',), allow_dy"
    "namic_dunder_attrs=False), HashPlan(action='add', fields=('elements',), cache=True), InitPlan(fields=(InitPlan.Fie"
    "ld(name='elements', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=Tr"
    "ue, override=False, field_type=FieldType.INSTANCE, coerce=OpRef(name='init.fields.0.coerce'), validate=None, check"
    "_type=None),), self_param='self', std_params=('elements',), kw_only_params=(), frozen=True, slots=False, post_init"
    "_params=(), init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='elements', kw_only=False, fn=None"
    "),), id=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2finject_2fprivates_2fPrivate(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__0__coerce,
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
            elements=self.elements,
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
            self.elements == other.elements
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'elements',
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
        'elements',
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
        try:
            return self.__dataclass_hash__
        except AttributeError:
            pass
        object.__setattr__(
            self,
            '__dataclass_hash__',
            h := hash((
                self.elements,
            ))
        )
        return h
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        elements: __dataclass__init__fields__0__annotation,
    ) -> __dataclass__None:
        elements = __dataclass__init__fields__0__coerce(elements)
        __dataclass__object_setattr(self, 'elements', elements)
        self.__post_init__()
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"elements={self.elements!r}")
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
    "Plans(tup=(CopyPlan(fields=('scope',)), EqPlan(fields=('scope',)), FrozenPlan(fields=('scope',), allow_dynamic_dun"
    "der_attrs=False), HashPlan(action='add', fields=('scope',), cache=True), InitPlan(fields=(InitPlan.Field(name='sco"
    "pe', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=Fa"
    "lse, field_type=FieldType.INSTANCE, coerce=OpRef(name='init.fields.0.coerce'), validate=None, check_type=None),), "
    "self_param='self', std_params=('scope',), kw_only_params=(), frozen=True, slots=False, post_init_params=(), init_f"
    "ns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='scope', kw_only=False, fn=None),), id=False, terse="
    "False, default_fn=None)))"
)
def _process_dataclass__omlish_2finject_2fscopes_2fScopeBinding(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__0__coerce,
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
            scope=self.scope,
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
            self.scope == other.scope
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'scope',
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
        'scope',
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
        try:
            return self.__dataclass_hash__
        except AttributeError:
            pass
        object.__setattr__(
            self,
            '__dataclass_hash__',
            h := hash((
                self.scope,
            ))
        )
        return h
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        scope: __dataclass__init__fields__0__annotation,
    ) -> __dataclass__None:
        scope = __dataclass__init__fields__0__coerce(scope)
        __dataclass__object_setattr(self, 'scope', scope)
        self.__post_init__()
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"scope={self.scope!r}")
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
    "Plans(tup=(CopyPlan(fields=('tag',)), EqPlan(fields=('tag',)), FrozenPlan(fields=('tag',), allow_dynamic_dunder_at"
    "trs=False), HashPlan(action='add', fields=('tag',), cache=True), InitPlan(fields=(InitPlan.Field(name='tag', annot"
    "ation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field"
    "_type=FieldType.INSTANCE, coerce=OpRef(name='init.fields.0.coerce'), validate=None, check_type=None),), self_param"
    "='self', std_params=('tag',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), val"
    "idate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='tag', kw_only=False, fn=None),), id=False, terse=False, defau"
    "lt_fn=None)))"
)
def _process_dataclass__omlish_2finject_2fscopes_2fSeededScope(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__0__coerce,
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
            tag=self.tag,
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
            self.tag == other.tag
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'tag',
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
        'tag',
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
        try:
            return self.__dataclass_hash__
        except AttributeError:
            pass
        object.__setattr__(
            self,
            '__dataclass_hash__',
            h := hash((
                self.tag,
            ))
        )
        return h
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        tag: __dataclass__init__fields__0__annotation,
    ) -> __dataclass__None:
        tag = __dataclass__init__fields__0__coerce(tag)
        __dataclass__object_setattr(self, 'tag', tag)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"tag={self.tag!r}")
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
    "Plans(tup=(CopyPlan(fields=('ss', 'key')), EqPlan(fields=('ss', 'key')), FrozenPlan(fields=('ss', 'key'), allow_dy"
    "namic_dunder_attrs=False), HashPlan(action='add', fields=('ss', 'key'), cache=True), InitPlan(fields=(InitPlan.Fie"
    "ld(name='ss', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, ov"
    "erride=False, field_type=FieldType.INSTANCE, coerce=OpRef(name='init.fields.0.coerce'), validate=None, check_type="
    "None), InitPlan.Field(name='key', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory"
    "=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=OpRef(name='init.fields.1.coerce'), valida"
    "te=None, check_type=None)), self_param='self', std_params=('ss', 'key'), kw_only_params=(), frozen=True, slots=Fal"
    "se, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='ss', kw_only=False"
    ", fn=None), ReprPlan.Field(name='key', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2finject_2fscopes_2fScopeSeededProvider(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__0__coerce,
    __dataclass__init__fields__1__annotation,
    __dataclass__init__fields__1__coerce,
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
            ss=self.ss,
            key=self.key,
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
            self.ss == other.ss and
            self.key == other.key
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'ss',
        'key',
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
        'ss',
        'key',
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
        try:
            return self.__dataclass_hash__
        except AttributeError:
            pass
        object.__setattr__(
            self,
            '__dataclass_hash__',
            h := hash((
                self.ss,
                self.key,
            ))
        )
        return h
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        ss: __dataclass__init__fields__0__annotation,
        key: __dataclass__init__fields__1__annotation,
    ) -> __dataclass__None:
        ss = __dataclass__init__fields__0__coerce(ss)
        key = __dataclass__init__fields__1__coerce(key)
        __dataclass__object_setattr(self, 'ss', ss)
        __dataclass__object_setattr(self, 'key', key)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"ss={self.ss!r}")
        parts.append(f"key={self.key!r}")
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
    "Plans(tup=(CopyPlan(fields=('key', 'source', 'name')), EqPlan(fields=('key', 'source', 'name')), HashPlan(action='"
    "set_none', fields=None, cache=None), InitPlan(fields=(InitPlan.Field(name='key', annotation=OpRef(name='init.field"
    "s.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, co"
    "erce=None, validate=None, check_type=None), InitPlan.Field(name='source', annotation=OpRef(name='init.fields.1.ann"
    "otation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_typ"
    "e=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='name', annotation=OpRef(n"
    "ame='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, ove"
    "rride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_"
    "params=('key', 'source', 'name'), kw_only_params=(), frozen=False, slots=False, post_init_params=None, init_fns=()"
    ", validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='key', kw_only=False, fn=None), ReprPlan.Field(name='sour"
    "ce', kw_only=False, fn=None), ReprPlan.Field(name='name', kw_only=False, fn=None)), id=False, terse=False, default"
    "_fn=None)))"
)
def _process_dataclass__omlish_2finject_2ferrors_2fBaseKeyError(
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
            key=self.key,
            source=self.source,
            name=self.name,
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
            self.key == other.key and
            self.source == other.source and
            self.name == other.name
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    setattr(__dataclass__cls, '__hash__', None)
    
    def __init__(
        self,
        key: __dataclass__init__fields__0__annotation,
        source: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        name: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
    ) -> __dataclass__None:
        self.key = key
        self.source = source
        self.name = name
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"key={self.key!r}")
        parts.append(f"source={self.source!r}")
        parts.append(f"name={self.name!r}")
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
    "Plans(tup=(CopyPlan(fields=('key', 'source', 'name')), EqPlan(fields=('key', 'source', 'name')), HashPlan(action='"
    "set_none', fields=None, cache=None), InitPlan(fields=(InitPlan.Field(name='key', annotation=OpRef(name='init.field"
    "s.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, co"
    "erce=None, validate=None, check_type=None), InitPlan.Field(name='source', annotation=OpRef(name='init.fields.1.ann"
    "otation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_typ"
    "e=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='name', annotation=OpRef(n"
    "ame='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, ove"
    "rride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_"
    "params=('key', 'source', 'name'), kw_only_params=(), frozen=False, slots=False, post_init_params=None, init_fns=()"
    ", validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='key', kw_only=False, fn=None), ReprPlan.Field(name='sour"
    "ce', kw_only=False, fn=None), ReprPlan.Field(name='name', kw_only=False, fn=None)), id=False, terse=False, default"
    "_fn=None)))"
)
def _process_dataclass__omlish_2finject_2ferrors_2fUnboundKeyError(
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
            key=self.key,
            source=self.source,
            name=self.name,
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
            self.key == other.key and
            self.source == other.source and
            self.name == other.name
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    setattr(__dataclass__cls, '__hash__', None)
    
    def __init__(
        self,
        key: __dataclass__init__fields__0__annotation,
        source: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        name: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
    ) -> __dataclass__None:
        self.key = key
        self.source = source
        self.name = name
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"key={self.key!r}")
        parts.append(f"source={self.source!r}")
        parts.append(f"name={self.name!r}")
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
    "Plans(tup=(CopyPlan(fields=('key', 'source', 'name')), EqPlan(fields=('key', 'source', 'name')), HashPlan(action='"
    "set_none', fields=None, cache=None), InitPlan(fields=(InitPlan.Field(name='key', annotation=OpRef(name='init.field"
    "s.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, co"
    "erce=None, validate=None, check_type=None), InitPlan.Field(name='source', annotation=OpRef(name='init.fields.1.ann"
    "otation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_typ"
    "e=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='name', annotation=OpRef(n"
    "ame='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, ove"
    "rride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_"
    "params=('key', 'source', 'name'), kw_only_params=(), frozen=False, slots=False, post_init_params=None, init_fns=()"
    ", validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='key', kw_only=False, fn=None), ReprPlan.Field(name='sour"
    "ce', kw_only=False, fn=None), ReprPlan.Field(name='name', kw_only=False, fn=None)), id=False, terse=False, default"
    "_fn=None)))"
)
def _process_dataclass__omlish_2finject_2ferrors_2fConflictingKeyError(
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
            key=self.key,
            source=self.source,
            name=self.name,
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
            self.key == other.key and
            self.source == other.source and
            self.name == other.name
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    setattr(__dataclass__cls, '__hash__', None)
    
    def __init__(
        self,
        key: __dataclass__init__fields__0__annotation,
        source: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        name: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
    ) -> __dataclass__None:
        self.key = key
        self.source = source
        self.name = name
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"key={self.key!r}")
        parts.append(f"source={self.source!r}")
        parts.append(f"name={self.name!r}")
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
    "Plans(tup=(CopyPlan(fields=('key', 'source', 'name')), EqPlan(fields=('key', 'source', 'name')), HashPlan(action='"
    "set_none', fields=None, cache=None), InitPlan(fields=(InitPlan.Field(name='key', annotation=OpRef(name='init.field"
    "s.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, co"
    "erce=None, validate=None, check_type=None), InitPlan.Field(name='source', annotation=OpRef(name='init.fields.1.ann"
    "otation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_typ"
    "e=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='name', annotation=OpRef(n"
    "ame='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, ove"
    "rride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_"
    "params=('key', 'source', 'name'), kw_only_params=(), frozen=False, slots=False, post_init_params=None, init_fns=()"
    ", validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='key', kw_only=False, fn=None), ReprPlan.Field(name='sour"
    "ce', kw_only=False, fn=None), ReprPlan.Field(name='name', kw_only=False, fn=None)), id=False, terse=False, default"
    "_fn=None)))"
)
def _process_dataclass__omlish_2finject_2ferrors_2fCyclicDependencyError(
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
            key=self.key,
            source=self.source,
            name=self.name,
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
            self.key == other.key and
            self.source == other.source and
            self.name == other.name
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    setattr(__dataclass__cls, '__hash__', None)
    
    def __init__(
        self,
        key: __dataclass__init__fields__0__annotation,
        source: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        name: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
    ) -> __dataclass__None:
        self.key = key
        self.source = source
        self.name = name
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"key={self.key!r}")
        parts.append(f"source={self.source!r}")
        parts.append(f"name={self.name!r}")
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
    "Plans(tup=(CopyPlan(fields=('scope',)), EqPlan(fields=('scope',)), HashPlan(action='set_none', fields=None, cache="
    "None), InitPlan(fields=(InitPlan.Field(name='scope', annotation=OpRef(name='init.fields.0.annotation'), default=No"
    "ne, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, ch"
    "eck_type=None),), self_param='self', std_params=('scope',), kw_only_params=(), frozen=False, slots=False, post_ini"
    "t_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='scope', kw_only=False, fn=None"
    "),), id=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2finject_2ferrors_2fScopeError(
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
            scope=self.scope,
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
            self.scope == other.scope
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    setattr(__dataclass__cls, '__hash__', None)
    
    def __init__(
        self,
        scope: __dataclass__init__fields__0__annotation,
    ) -> __dataclass__None:
        self.scope = scope
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"scope={self.scope!r}")
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
    "Plans(tup=(CopyPlan(fields=('scope',)), EqPlan(fields=('scope',)), HashPlan(action='set_none', fields=None, cache="
    "None), InitPlan(fields=(InitPlan.Field(name='scope', annotation=OpRef(name='init.fields.0.annotation'), default=No"
    "ne, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, ch"
    "eck_type=None),), self_param='self', std_params=('scope',), kw_only_params=(), frozen=False, slots=False, post_ini"
    "t_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='scope', kw_only=False, fn=None"
    "),), id=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2finject_2ferrors_2fScopeAlreadyOpenError(
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
            scope=self.scope,
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
            self.scope == other.scope
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    setattr(__dataclass__cls, '__hash__', None)
    
    def __init__(
        self,
        scope: __dataclass__init__fields__0__annotation,
    ) -> __dataclass__None:
        self.scope = scope
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"scope={self.scope!r}")
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
    "Plans(tup=(CopyPlan(fields=('scope',)), EqPlan(fields=('scope',)), HashPlan(action='set_none', fields=None, cache="
    "None), InitPlan(fields=(InitPlan.Field(name='scope', annotation=OpRef(name='init.fields.0.annotation'), default=No"
    "ne, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, ch"
    "eck_type=None),), self_param='self', std_params=('scope',), kw_only_params=(), frozen=False, slots=False, post_ini"
    "t_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='scope', kw_only=False, fn=None"
    "),), id=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2finject_2ferrors_2fScopeNotOpenError(
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
            scope=self.scope,
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
            self.scope == other.scope
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    setattr(__dataclass__cls, '__hash__', None)
    
    def __init__(
        self,
        scope: __dataclass__init__fields__0__annotation,
    ) -> __dataclass__None:
        self.scope = scope
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"scope={self.scope!r}")
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
    "Plans(tup=(CopyPlan(fields=('listener',)), EqPlan(fields=('listener',)), FrozenPlan(fields=('listener',), allow_dy"
    "namic_dunder_attrs=False), HashPlan(action='add', fields=('listener',), cache=True), InitPlan(fields=(InitPlan.Fie"
    "ld(name='listener', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=Tr"
    "ue, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='sel"
    "f', std_params=('listener',), kw_only_params=(), frozen=True, slots=False, post_init_params=(), init_fns=(), valid"
    "ate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='listener', kw_only=False, fn=None),), id=False, terse=False, de"
    "fault_fn=None)))"
)
def _process_dataclass__omlish_2finject_2flisteners_2fProvisionListenerBinding(
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
            listener=self.listener,
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
            self.listener == other.listener
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'listener',
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
        'listener',
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
        try:
            return self.__dataclass_hash__
        except AttributeError:
            pass
        object.__setattr__(
            self,
            '__dataclass_hash__',
            h := hash((
                self.listener,
            ))
        )
        return h
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        listener: __dataclass__init__fields__0__annotation,
    ) -> __dataclass__None:
        __dataclass__object_setattr(self, 'listener', listener)
        self.__post_init__()
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"listener={self.listener!r}")
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
    "Plans(tup=(CopyPlan(fields=('multi_key', 'dst')), EqPlan(fields=('multi_key', 'dst')), FrozenPlan(fields=('multi_k"
    "ey', 'dst'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('multi_key', 'dst'), cache=True), I"
    "nitPlan(fields=(InitPlan.Field(name='multi_key', annotation=OpRef(name='init.fields.0.annotation'), default=None, "
    "default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=OpRef(name='"
    "init.fields.0.validate'), check_type=None), InitPlan.Field(name='dst', annotation=OpRef(name='init.fields.1.annota"
    "tion'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=OpRef"
    "(name='init.fields.1.coerce'), validate=None, check_type=None)), self_param='self', std_params=('multi_key', 'dst'"
    "), kw_only_params=(), frozen=True, slots=False, post_init_params=(), init_fns=(), validate_fns=()), ReprPlan(field"
    "s=(ReprPlan.Field(name='multi_key', kw_only=False, fn=None), ReprPlan.Field(name='dst', kw_only=False, fn=None)), "
    "id=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2finject_2fmultis_2fSetBinding(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__0__validate,
    __dataclass__init__fields__1__annotation,
    __dataclass__init__fields__1__coerce,
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
            multi_key=self.multi_key,
            dst=self.dst,
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
            self.multi_key == other.multi_key and
            self.dst == other.dst
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'multi_key',
        'dst',
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
        'multi_key',
        'dst',
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
        try:
            return self.__dataclass_hash__
        except AttributeError:
            pass
        object.__setattr__(
            self,
            '__dataclass_hash__',
            h := hash((
                self.multi_key,
                self.dst,
            ))
        )
        return h
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        multi_key: __dataclass__init__fields__0__annotation,
        dst: __dataclass__init__fields__1__annotation,
    ) -> __dataclass__None:
        dst = __dataclass__init__fields__1__coerce(dst)
        if not __dataclass__init__fields__0__validate(multi_key): 
            raise __dataclass__FieldFnValidationError(
                obj=self,
                fn=__dataclass__init__fields__0__validate,
                field='multi_key',
                value=multi_key,
            )
        __dataclass__object_setattr(self, 'multi_key', multi_key)
        __dataclass__object_setattr(self, 'dst', dst)
        self.__post_init__()
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"multi_key={self.multi_key!r}")
        parts.append(f"dst={self.dst!r}")
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
    "Plans(tup=(CopyPlan(fields=('multi_key',)), EqPlan(fields=('multi_key',)), FrozenPlan(fields=('multi_key',), allow"
    "_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('multi_key',), cache=True), InitPlan(fields=(InitPlan"
    ".Field(name='multi_key', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, in"
    "it=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=OpRef(name='init.fields.0.validate')"
    ", check_type=None),), self_param='self', std_params=('multi_key',), kw_only_params=(), frozen=True, slots=False, p"
    "ost_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='multi_key', kw_only=Fal"
    "se, fn=None),), id=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2finject_2fmultis_2fSetProvider(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__0__validate,
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
            multi_key=self.multi_key,
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
            self.multi_key == other.multi_key
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'multi_key',
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
        'multi_key',
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
        try:
            return self.__dataclass_hash__
        except AttributeError:
            pass
        object.__setattr__(
            self,
            '__dataclass_hash__',
            h := hash((
                self.multi_key,
            ))
        )
        return h
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        multi_key: __dataclass__init__fields__0__annotation,
    ) -> __dataclass__None:
        if not __dataclass__init__fields__0__validate(multi_key): 
            raise __dataclass__FieldFnValidationError(
                obj=self,
                fn=__dataclass__init__fields__0__validate,
                field='multi_key',
                value=multi_key,
            )
        __dataclass__object_setattr(self, 'multi_key', multi_key)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"multi_key={self.multi_key!r}")
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
    "Plans(tup=(CopyPlan(fields=('multi_key', 'map_key', 'dst')), EqPlan(fields=('multi_key', 'map_key', 'dst')), Froze"
    "nPlan(fields=('multi_key', 'map_key', 'dst'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('m"
    "ulti_key', 'map_key', 'dst'), cache=True), InitPlan(fields=(InitPlan.Field(name='multi_key', annotation=OpRef(name"
    "='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType."
    "INSTANCE, coerce=None, validate=OpRef(name='init.fields.0.validate'), check_type=None), InitPlan.Field(name='map_k"
    "ey', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=Fa"
    "lse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='dst', annot"
    "ation=OpRef(name='init.fields.2.annotation'), default=None, default_factory=None, init=True, override=False, field"
    "_type=FieldType.INSTANCE, coerce=OpRef(name='init.fields.2.coerce'), validate=None, check_type=None)), self_param="
    "'self', std_params=('multi_key', 'map_key', 'dst'), kw_only_params=(), frozen=True, slots=False, post_init_params="
    "(), init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='multi_key', kw_only=False, fn=None), Repr"
    "Plan.Field(name='map_key', kw_only=False, fn=None), ReprPlan.Field(name='dst', kw_only=False, fn=None)), id=False,"
    " terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2finject_2fmultis_2fMapBinding(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__0__validate,
    __dataclass__init__fields__1__annotation,
    __dataclass__init__fields__2__annotation,
    __dataclass__init__fields__2__coerce,
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
            multi_key=self.multi_key,
            map_key=self.map_key,
            dst=self.dst,
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
            self.multi_key == other.multi_key and
            self.map_key == other.map_key and
            self.dst == other.dst
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'multi_key',
        'map_key',
        'dst',
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
        'multi_key',
        'map_key',
        'dst',
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
        try:
            return self.__dataclass_hash__
        except AttributeError:
            pass
        object.__setattr__(
            self,
            '__dataclass_hash__',
            h := hash((
                self.multi_key,
                self.map_key,
                self.dst,
            ))
        )
        return h
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        multi_key: __dataclass__init__fields__0__annotation,
        map_key: __dataclass__init__fields__1__annotation,
        dst: __dataclass__init__fields__2__annotation,
    ) -> __dataclass__None:
        dst = __dataclass__init__fields__2__coerce(dst)
        if not __dataclass__init__fields__0__validate(multi_key): 
            raise __dataclass__FieldFnValidationError(
                obj=self,
                fn=__dataclass__init__fields__0__validate,
                field='multi_key',
                value=multi_key,
            )
        __dataclass__object_setattr(self, 'multi_key', multi_key)
        __dataclass__object_setattr(self, 'map_key', map_key)
        __dataclass__object_setattr(self, 'dst', dst)
        self.__post_init__()
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"multi_key={self.multi_key!r}")
        parts.append(f"map_key={self.map_key!r}")
        parts.append(f"dst={self.dst!r}")
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
    "Plans(tup=(CopyPlan(fields=('multi_key',)), EqPlan(fields=('multi_key',)), FrozenPlan(fields=('multi_key',), allow"
    "_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('multi_key',), cache=True), InitPlan(fields=(InitPlan"
    ".Field(name='multi_key', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, in"
    "it=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=OpRef(name='init.fields.0.validate')"
    ", check_type=None),), self_param='self', std_params=('multi_key',), kw_only_params=(), frozen=True, slots=False, p"
    "ost_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='multi_key', kw_only=Fal"
    "se, fn=None),), id=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2finject_2fmultis_2fMapProvider(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__0__validate,
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
            multi_key=self.multi_key,
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
            self.multi_key == other.multi_key
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'multi_key',
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
        'multi_key',
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
        try:
            return self.__dataclass_hash__
        except AttributeError:
            pass
        object.__setattr__(
            self,
            '__dataclass_hash__',
            h := hash((
                self.multi_key,
            ))
        )
        return h
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        multi_key: __dataclass__init__fields__0__annotation,
    ) -> __dataclass__None:
        if not __dataclass__init__fields__0__validate(multi_key): 
            raise __dataclass__FieldFnValidationError(
                obj=self,
                fn=__dataclass__init__fields__0__validate,
                field='multi_key',
                value=multi_key,
            )
        __dataclass__object_setattr(self, 'multi_key', multi_key)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"multi_key={self.multi_key!r}")
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
    "Plans(tup=(CopyPlan(fields=('src', 'ovr')), EqPlan(fields=('src', 'ovr')), FrozenPlan(fields=('src', 'ovr'), allow"
    "_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('src', 'ovr'), cache=True), InitPlan(fields=(InitPlan"
    ".Field(name='src', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=Tru"
    "e, override=False, field_type=FieldType.INSTANCE, coerce=OpRef(name='init.fields.0.coerce'), validate=None, check_"
    "type=None), InitPlan.Field(name='ovr', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_fa"
    "ctory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=OpRef(name='init.fields.1.coerce'), v"
    "alidate=None, check_type=None)), self_param='self', std_params=('src', 'ovr'), kw_only_params=(), frozen=True, slo"
    "ts=False, post_init_params=(), init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='src', kw_only="
    "False, fn=None), ReprPlan.Field(name='ovr', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2finject_2foverrides_2fOverrides(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__0__coerce,
    __dataclass__init__fields__1__annotation,
    __dataclass__init__fields__1__coerce,
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
            src=self.src,
            ovr=self.ovr,
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
            self.src == other.src and
            self.ovr == other.ovr
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'src',
        'ovr',
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
        'src',
        'ovr',
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
        try:
            return self.__dataclass_hash__
        except AttributeError:
            pass
        object.__setattr__(
            self,
            '__dataclass_hash__',
            h := hash((
                self.src,
                self.ovr,
            ))
        )
        return h
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        src: __dataclass__init__fields__0__annotation,
        ovr: __dataclass__init__fields__1__annotation,
    ) -> __dataclass__None:
        src = __dataclass__init__fields__0__coerce(src)
        ovr = __dataclass__init__fields__1__coerce(ovr)
        __dataclass__object_setattr(self, 'src', src)
        __dataclass__object_setattr(self, 'ovr', ovr)
        self.__post_init__()
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"src={self.src!r}")
        parts.append(f"ovr={self.ovr!r}")
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
    "Plans(tup=(CopyPlan(fields=('v',)), FrozenPlan(fields=('v',), allow_dynamic_dunder_attrs=False), InitPlan(fields=("
    "InitPlan.Field(name='v', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, in"
    "it=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param"
    "='self', std_params=('v',), kw_only_params=(), frozen=True, slots=False, post_init_params=(), init_fns=(), validat"
    "e_fns=()), ReprPlan(fields=(ReprPlan.Field(name='v', kw_only=False, fn=None),), id=False, terse=False, default_fn="
    "None)))"
)
def _process_dataclass__omlish_2finject_2fhelpers_2fconstfn_2fConstFn(
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
            v=self.v,
        )
    
    __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
    if '__copy__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__copy__', __copy__)
    
    __dataclass___setattr_frozen_fields = {
        'v',
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
        'v',
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
    
    def __init__(
        self,
        v: __dataclass__init__fields__0__annotation,
    ) -> __dataclass__None:
        __dataclass__object_setattr(self, 'v', v)
        self.__post_init__()
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"v={self.v!r}")
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
    "Plans(tup=(CopyPlan(fields=('v', 'tag')), EqPlan(fields=('v', 'tag')), FrozenPlan(fields=('v', 'tag'), allow_dynam"
    "ic_dunder_attrs=False), HashPlan(action='add', fields=('v', 'tag'), cache=True), InitPlan(fields=(InitPlan.Field(n"
    "ame='v', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, overrid"
    "e=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='tag', a"
    "nnotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=Non"
    "e, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=OpRef(name='init.fields.1.valid"
    "ate'), check_type=None)), self_param='self', std_params=('v',), kw_only_params=('tag',), frozen=True, slots=False,"
    " post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='v', kw_only=False, fn"
    "=None), ReprPlan.Field(name='tag', kw_only=True, fn=OpRef(name='repr.fns.1.fn'))), id=False, terse=True, default_f"
    "n=None)))"
)
def _process_dataclass__omlish_2finject_2fhelpers_2fid_2fId(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__1__annotation,
    __dataclass__init__fields__1__default,
    __dataclass__init__fields__1__validate,
    __dataclass__repr__fns__1__fn,
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
            v=self.v,
            tag=self.tag,
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
            self.v == other.v and
            self.tag == other.tag
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'v',
        'tag',
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
        'v',
        'tag',
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
        try:
            return self.__dataclass_hash__
        except AttributeError:
            pass
        object.__setattr__(
            self,
            '__dataclass_hash__',
            h := hash((
                self.v,
                self.tag,
            ))
        )
        return h
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        v: __dataclass__init__fields__0__annotation,
        *,
        tag: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
    ) -> __dataclass__None:
        if not __dataclass__init__fields__1__validate(tag): 
            raise __dataclass__FieldFnValidationError(
                obj=self,
                fn=__dataclass__init__fields__1__validate,
                field='tag',
                value=tag,
            )
        __dataclass__object_setattr(self, 'v', v)
        __dataclass__object_setattr(self, 'tag', tag)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"{self.v!r}")
        if (s := __dataclass__repr__fns__1__fn(self.tag)) is not None:
            parts.append(f"tag={s}")
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
    "Plans(tup=(CopyPlan(fields=('vs',)), FrozenPlan(fields=('vs',), allow_dynamic_dunder_attrs=False), InitPlan(fields"
    "=(InitPlan.Field(name='vs', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None,"
    " init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_pa"
    "ram='self', std_params=('vs',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), v"
    "alidate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='vs', kw_only=False, fn=None),), id=False, terse=False, defa"
    "ult_fn=None)))"
)
def _process_dataclass__omlish_2finject_2fhelpers_2fmultis_2fItemsBinderHelper_2f_00ItemsBox(
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
            vs=self.vs,
        )
    
    __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
    if '__copy__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__copy__', __copy__)
    
    __dataclass___setattr_frozen_fields = {
        'vs',
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
        'vs',
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
    
    def __init__(
        self,
        vs: __dataclass__init__fields__0__annotation,
    ) -> __dataclass__None:
        __dataclass__object_setattr(self, 'vs', vs)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"vs={self.vs!r}")
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
    "Plans(tup=(CopyPlan(fields=()), FrozenPlan(fields=(), allow_dynamic_dunder_attrs=False), InitPlan(fields=(), self_"
    "param='self', std_params=(), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), vali"
    "date_fns=()), ReprPlan(fields=(), id=True, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2finject_2fhelpers_2fmultis_2fItemsBinderHelper_2f_00ItemTag(
    *,
    __dataclass__cls,
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
        return __dataclass__cls()  # noqa
    
    __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
    if '__copy__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__copy__', __copy__)
    
    def __setattr__(self, name, value):
        if (
            type(self) is __dataclass__cls
        ):
            raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
        super(__dataclass__cls, self).__setattr__(name, value)
    
    __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
    if '__setattr__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__setattr__', __setattr__)
    
    def __delattr__(self, name):
        if (
            type(self) is __dataclass__cls
        ):
            raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
        super(__dataclass__cls, self).__delattr__(name)
    
    __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
    if '__delattr__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__delattr__', __delattr__)
    
    def __init__(
        self,
    ) -> __dataclass__None:
        pass
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        return (
            f"{self.__class__.__qualname__}@{hex(id(self))[2:]}("
            f"{', '.join(parts)}"
            f")"
        )
    
    __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
    if '__repr__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__repr__', __repr__)


@_register(
    "Plans(tup=(CopyPlan(fields=()), FrozenPlan(fields=(), allow_dynamic_dunder_attrs=False), InitPlan(fields=(), self_"
    "param='self', std_params=(), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), vali"
    "date_fns=()), ReprPlan(fields=(), id=True, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2finject_2fhelpers_2fwrappers_2fWrapperBinderHelper_2f_00Root(
    *,
    __dataclass__cls,
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
        return __dataclass__cls()  # noqa
    
    __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
    if '__copy__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__copy__', __copy__)
    
    def __setattr__(self, name, value):
        if (
            type(self) is __dataclass__cls
        ):
            raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
        super(__dataclass__cls, self).__setattr__(name, value)
    
    __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
    if '__setattr__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__setattr__', __setattr__)
    
    def __delattr__(self, name):
        if (
            type(self) is __dataclass__cls
        ):
            raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
        super(__dataclass__cls, self).__delattr__(name)
    
    __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
    if '__delattr__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__delattr__', __delattr__)
    
    def __init__(
        self,
    ) -> __dataclass__None:
        pass
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        return (
            f"{self.__class__.__qualname__}@{hex(id(self))[2:]}("
            f"{', '.join(parts)}"
            f")"
        )
    
    __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
    if '__repr__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__repr__', __repr__)


@_register(
    "Plans(tup=(CopyPlan(fields=('root', 'level')), EqPlan(fields=('root', 'level')), FrozenPlan(fields=('root', 'level"
    "'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('root', 'level'), cache=False), InitPlan(fie"
    "lds=(InitPlan.Field(name='root', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory="
    "None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), Init"
    "Plan.Field(name='level', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, in"
    "it=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param="
    "'self', std_params=('root', 'level'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns"
    "=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='root', kw_only=False, fn=None), ReprPlan.Field(name='"
    "level', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2finject_2fhelpers_2fwrappers_2fWrapperBinderHelper_2f_00Level(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__1__annotation,
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
            root=self.root,
            level=self.level,
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
            self.root == other.root and
            self.level == other.level
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'root',
        'level',
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
        'root',
        'level',
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
            self.root,
            self.level,
        ))
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        root: __dataclass__init__fields__0__annotation,
        level: __dataclass__init__fields__1__annotation,
    ) -> __dataclass__None:
        __dataclass__object_setattr(self, 'root', root)
        __dataclass__object_setattr(self, 'level', level)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"root={self.root!r}")
        parts.append(f"level={self.level!r}")
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
    "Plans(tup=(CopyPlan(fields=('impl',)), FrozenPlan(fields=('impl',), allow_dynamic_dunder_attrs=False), InitPlan(fi"
    "elds=(InitPlan.Field(name='impl', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory"
    "=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), s"
    "elf_param='self', std_params=('impl',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_f"
    "ns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='impl', kw_only=False, fn=None),), id=False, terse=F"
    "alse, default_fn=None)))"
)
def _process_dataclass__omlish_2finject_2fimpl_2fproviders_2fInternalProvider(
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
            impl=self.impl,
        )
    
    __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
    if '__copy__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__copy__', __copy__)
    
    __dataclass___setattr_frozen_fields = {
        'impl',
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
        'impl',
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
    
    def __init__(
        self,
        impl: __dataclass__init__fields__0__annotation,
    ) -> __dataclass__None:
        __dataclass__object_setattr(self, 'impl', impl)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"impl={self.impl!r}")
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
    "Plans(tup=(CopyPlan(fields=('p', 'kt')), FrozenPlan(fields=('p', 'kt'), allow_dynamic_dunder_attrs=False), InitPla"
    "n(fields=(InitPlan.Field(name='p', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factor"
    "y=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), In"
    "itPlan.Field(name='kt', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, ini"
    "t=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='"
    "self', std_params=('p', 'kt'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), va"
    "lidate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='p', kw_only=False, fn=None), ReprPlan.Field(name='kt', kw_on"
    "ly=False, fn=None)), id=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2finject_2fimpl_2fproviders_2fAsyncCallableProviderImpl(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__1__annotation,
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
            p=self.p,
            kt=self.kt,
        )
    
    __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
    if '__copy__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__copy__', __copy__)
    
    __dataclass___setattr_frozen_fields = {
        'p',
        'kt',
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
        'p',
        'kt',
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
    
    def __init__(
        self,
        p: __dataclass__init__fields__0__annotation,
        kt: __dataclass__init__fields__1__annotation,
    ) -> __dataclass__None:
        __dataclass__object_setattr(self, 'p', p)
        __dataclass__object_setattr(self, 'kt', kt)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"p={self.p!r}")
        parts.append(f"kt={self.kt!r}")
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
    "Plans(tup=(CopyPlan(fields=('p', 'kt')), FrozenPlan(fields=('p', 'kt'), allow_dynamic_dunder_attrs=False), InitPla"
    "n(fields=(InitPlan.Field(name='p', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factor"
    "y=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), In"
    "itPlan.Field(name='kt', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, ini"
    "t=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='"
    "self', std_params=('p', 'kt'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), va"
    "lidate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='p', kw_only=False, fn=None), ReprPlan.Field(name='kt', kw_on"
    "ly=False, fn=None)), id=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2finject_2fimpl_2fproviders_2fCallableProviderImpl(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__1__annotation,
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
            p=self.p,
            kt=self.kt,
        )
    
    __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
    if '__copy__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__copy__', __copy__)
    
    __dataclass___setattr_frozen_fields = {
        'p',
        'kt',
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
        'p',
        'kt',
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
    
    def __init__(
        self,
        p: __dataclass__init__fields__0__annotation,
        kt: __dataclass__init__fields__1__annotation,
    ) -> __dataclass__None:
        __dataclass__object_setattr(self, 'p', p)
        __dataclass__object_setattr(self, 'kt', kt)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"p={self.p!r}")
        parts.append(f"kt={self.kt!r}")
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
    "Plans(tup=(CopyPlan(fields=('p',)), FrozenPlan(fields=('p',), allow_dynamic_dunder_attrs=False), InitPlan(fields=("
    "InitPlan.Field(name='p', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, in"
    "it=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param"
    "='self', std_params=('p',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), valid"
    "ate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='p', kw_only=False, fn=None),), id=False, terse=False, default_f"
    "n=None)))"
)
def _process_dataclass__omlish_2finject_2fimpl_2fproviders_2fConstProviderImpl(
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
            p=self.p,
        )
    
    __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
    if '__copy__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__copy__', __copy__)
    
    __dataclass___setattr_frozen_fields = {
        'p',
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
        'p',
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
    
    def __init__(
        self,
        p: __dataclass__init__fields__0__annotation,
    ) -> __dataclass__None:
        __dataclass__object_setattr(self, 'p', p)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"p={self.p!r}")
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
    "Plans(tup=(CopyPlan(fields=('p',)), FrozenPlan(fields=('p',), allow_dynamic_dunder_attrs=False), InitPlan(fields=("
    "InitPlan.Field(name='p', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, in"
    "it=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param"
    "='self', std_params=('p',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), valid"
    "ate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='p', kw_only=False, fn=None),), id=False, terse=False, default_f"
    "n=None)))"
)
def _process_dataclass__omlish_2finject_2fimpl_2fproviders_2fLinkProviderImpl(
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
            p=self.p,
        )
    
    __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
    if '__copy__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__copy__', __copy__)
    
    __dataclass___setattr_frozen_fields = {
        'p',
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
        'p',
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
    
    def __init__(
        self,
        p: __dataclass__init__fields__0__annotation,
    ) -> __dataclass__None:
        __dataclass__object_setattr(self, 'p', p)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"p={self.p!r}")
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
    "Plans(tup=(CopyPlan(fields=('key', 'provider', 'scope', 'binding')), FrozenPlan(fields=('key', 'provider', 'scope'"
    ", 'binding'), allow_dynamic_dunder_attrs=False), InitPlan(fields=(InitPlan.Field(name='key', annotation=OpRef(name"
    "='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType."
    "INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='provider', annotation=OpRef(name='ini"
    "t.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTA"
    "NCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='scope', annotation=OpRef(name='init.fields"
    ".2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, fie"
    "ld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='binding', annotatio"
    "n=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init="
    "True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='se"
    "lf', std_params=('key', 'provider', 'scope', 'binding'), kw_only_params=(), frozen=True, slots=False, post_init_pa"
    "rams=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='key', kw_only=False, fn=None), Rep"
    "rPlan.Field(name='provider', kw_only=False, fn=None), ReprPlan.Field(name='scope', kw_only=False, fn=None), ReprPl"
    "an.Field(name='binding', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2finject_2fimpl_2fbindings_2fBindingImpl(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__1__annotation,
    __dataclass__init__fields__2__annotation,
    __dataclass__init__fields__2__default,
    __dataclass__init__fields__3__annotation,
    __dataclass__init__fields__3__default,
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
            key=self.key,
            provider=self.provider,
            scope=self.scope,
            binding=self.binding,
        )
    
    __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
    if '__copy__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__copy__', __copy__)
    
    __dataclass___setattr_frozen_fields = {
        'key',
        'provider',
        'scope',
        'binding',
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
        'key',
        'provider',
        'scope',
        'binding',
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
    
    def __init__(
        self,
        key: __dataclass__init__fields__0__annotation,
        provider: __dataclass__init__fields__1__annotation,
        scope: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        binding: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
    ) -> __dataclass__None:
        __dataclass__object_setattr(self, 'key', key)
        __dataclass__object_setattr(self, 'provider', provider)
        __dataclass__object_setattr(self, 'scope', scope)
        __dataclass__object_setattr(self, 'binding', binding)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"key={self.key!r}")
        parts.append(f"provider={self.provider!r}")
        parts.append(f"scope={self.scope!r}")
        parts.append(f"binding={self.binding!r}")
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
    "Plans(tup=(CopyPlan(fields=('ps',)), FrozenPlan(fields=('ps',), allow_dynamic_dunder_attrs=False), InitPlan(fields"
    "=(InitPlan.Field(name='ps', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None,"
    " init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_pa"
    "ram='self', std_params=('ps',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), v"
    "alidate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='ps', kw_only=False, fn=None),), id=False, terse=False, defa"
    "ult_fn=None)))"
)
def _process_dataclass__omlish_2finject_2fimpl_2fmultis_2fSetProviderImpl(
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
            ps=self.ps,
        )
    
    __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
    if '__copy__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__copy__', __copy__)
    
    __dataclass___setattr_frozen_fields = {
        'ps',
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
        'ps',
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
    
    def __init__(
        self,
        ps: __dataclass__init__fields__0__annotation,
    ) -> __dataclass__None:
        __dataclass__object_setattr(self, 'ps', ps)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"ps={self.ps!r}")
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
    "Plans(tup=(CopyPlan(fields=('es',)), FrozenPlan(fields=('es',), allow_dynamic_dunder_attrs=False), InitPlan(fields"
    "=(InitPlan.Field(name='es', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None,"
    " init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_pa"
    "ram='self', std_params=('es',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), v"
    "alidate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='es', kw_only=False, fn=None),), id=False, terse=False, defa"
    "ult_fn=None)))"
)
def _process_dataclass__omlish_2finject_2fimpl_2fmultis_2fMapProviderImpl(
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
            es=self.es,
        )
    
    __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
    if '__copy__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__copy__', __copy__)
    
    __dataclass___setattr_frozen_fields = {
        'es',
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
        'es',
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
    
    def __init__(
        self,
        es: __dataclass__init__fields__0__annotation,
    ) -> __dataclass__None:
        __dataclass__object_setattr(self, 'es', es)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"es={self.es!r}")
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
    "Plans(tup=(CopyPlan(fields=('p',)), FrozenPlan(fields=('p',), allow_dynamic_dunder_attrs=False), InitPlan(fields=("
    "InitPlan.Field(name='p', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, in"
    "it=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param"
    "='self', std_params=('p',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), valid"
    "ate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='p', kw_only=False, fn=None),), id=False, terse=False, default_f"
    "n=None)))"
)
def _process_dataclass__omlish_2finject_2fimpl_2fscopes_2fScopeSeededProviderImpl(
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
            p=self.p,
        )
    
    __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
    if '__copy__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__copy__', __copy__)
    
    __dataclass___setattr_frozen_fields = {
        'p',
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
        'p',
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
    
    def __init__(
        self,
        p: __dataclass__init__fields__0__annotation,
    ) -> __dataclass__None:
        __dataclass__object_setattr(self, 'p', p)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"p={self.p!r}")
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
    "Plans(tup=(CopyPlan(fields=('seeds', 'prvs')), EqPlan(fields=('seeds', 'prvs')), FrozenPlan(fields=('seeds', 'prvs"
    "'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('seeds', 'prvs'), cache=False), InitPlan(fie"
    "lds=(InitPlan.Field(name='seeds', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory"
    "=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), Ini"
    "tPlan.Field(name='prvs', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=OpRef(na"
    "me='init.fields.1.default_factory'), init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valida"
    "te=None, check_type=None)), self_param='self', std_params=('seeds', 'prvs'), kw_only_params=(), frozen=True, slots"
    "=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='seeds', kw_onl"
    "y=False, fn=None), ReprPlan.Field(name='prvs', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2finject_2fimpl_2fscopes_2fSeededScopeImpl_2fState(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__1__annotation,
    __dataclass__init__fields__1__default_factory,
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
            seeds=self.seeds,
            prvs=self.prvs,
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
            self.seeds == other.seeds and
            self.prvs == other.prvs
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'seeds',
        'prvs',
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
        'seeds',
        'prvs',
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
            self.seeds,
            self.prvs,
        ))
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        seeds: __dataclass__init__fields__0__annotation,
        prvs: __dataclass__init__fields__1__annotation = __dataclass__HAS_DEFAULT_FACTORY,
    ) -> __dataclass__None:
        if prvs is __dataclass__HAS_DEFAULT_FACTORY:
            prvs = __dataclass__init__fields__1__default_factory()
        __dataclass__object_setattr(self, 'seeds', seeds)
        __dataclass__object_setattr(self, 'prvs', prvs)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"seeds={self.seeds!r}")
        parts.append(f"prvs={self.prvs!r}")
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
    "Plans(tup=(CopyPlan(fields=('id',)), EqPlan(fields=('id',)), FrozenPlan(fields=('id',), allow_dynamic_dunder_attrs"
    "=False), HashPlan(action='add', fields=('id',), cache=False), InitPlan(fields=(InitPlan.Field(name='id', annotatio"
    "n=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_typ"
    "e=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self', std_params=('id',), kw_on"
    "ly_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(Rep"
    "rPlan.Field(name='id', kw_only=False, fn=None),), id=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2finject_2fimpl_2fprivates_2fPrivateInjectorId(
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
            id=self.id,
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
            self.id == other.id
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'id',
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
        'id',
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
            self.id,
        ))
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        id: __dataclass__init__fields__0__annotation,
    ) -> __dataclass__None:
        __dataclass__object_setattr(self, 'id', id)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"id={self.id!r}")
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
    "Plans(tup=(CopyPlan(fields=('id', 'ec')), InitPlan(fields=(InitPlan.Field(name='id', annotation=OpRef(name='init.f"
    "ields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE"
    ", coerce=None, validate=None, check_type=None), InitPlan.Field(name='ec', annotation=OpRef(name='init.fields.1.ann"
    "otation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=No"
    "ne, validate=None, check_type=None)), self_param='self', std_params=('id', 'ec'), kw_only_params=(), frozen=False,"
    " slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='id', kw_"
    "only=False, fn=None), ReprPlan.Field(name='ec', kw_only=False, fn=None)), id=False, terse=False, default_fn=None))"
    ")"
)
def _process_dataclass__omlish_2finject_2fimpl_2fprivates_2fPrivateInjectorProviderImpl(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__1__annotation,
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
            id=self.id,
            ec=self.ec,
        )
    
    __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
    if '__copy__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__copy__', __copy__)
    
    def __init__(
        self,
        id: __dataclass__init__fields__0__annotation,
        ec: __dataclass__init__fields__1__annotation,
    ) -> __dataclass__None:
        self.id = id
        self.ec = ec
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"id={self.id!r}")
        parts.append(f"ec={self.ec!r}")
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
    "Plans(tup=(CopyPlan(fields=('pik', 'k')), InitPlan(fields=(InitPlan.Field(name='pik', annotation=OpRef(name='init."
    "fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANC"
    "E, coerce=None, validate=None, check_type=None), InitPlan.Field(name='k', annotation=OpRef(name='init.fields.1.ann"
    "otation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=No"
    "ne, validate=None, check_type=None)), self_param='self', std_params=('pik', 'k'), kw_only_params=(), frozen=False,"
    " slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='pik', kw"
    "_only=False, fn=None), ReprPlan.Field(name='k', kw_only=False, fn=None)), id=False, terse=False, default_fn=None))"
    ")"
)
def _process_dataclass__omlish_2finject_2fimpl_2fprivates_2fExposedPrivateProviderImpl(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__1__annotation,
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
            pik=self.pik,
            k=self.k,
        )
    
    __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
    if '__copy__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__copy__', __copy__)
    
    def __init__(
        self,
        pik: __dataclass__init__fields__0__annotation,
        k: __dataclass__init__fields__1__annotation,
    ) -> __dataclass__None:
        self.pik = pik
        self.k = k
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"pik={self.pik!r}")
        parts.append(f"k={self.k!r}")
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
    "Plans(tup=(CopyPlan(fields=('owner', 'p')), EqPlan(fields=('owner', 'p')), FrozenPlan(fields=('owner', 'p'), allow"
    "_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('owner', 'p'), cache=False), InitPlan(fields=(InitPla"
    "n.Field(name='owner', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init="
    "True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field("
    "name='p', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, overri"
    "de=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_par"
    "ams=('owner', 'p'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns="
    "()), ReprPlan(fields=(ReprPlan.Field(name='owner', kw_only=False, fn=None), ReprPlan.Field(name='p', kw_only=False"
    ", fn=None)), id=False, terse=False, default_fn=None)))"
)
def _process_dataclass__omlish_2finject_2fimpl_2fprivates_2fPrivateInfo(
    *,
    __dataclass__cls,
    __dataclass__init__fields__0__annotation,
    __dataclass__init__fields__1__annotation,
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
            owner=self.owner,
            p=self.p,
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
            self.owner == other.owner and
            self.p == other.p
        )
    
    __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
    if '__eq__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__eq__', __eq__)
    
    __dataclass___setattr_frozen_fields = {
        'owner',
        'p',
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
        'owner',
        'p',
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
            self.owner,
            self.p,
        ))
    
    __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
    setattr(__dataclass__cls, '__hash__', __hash__)
    
    def __init__(
        self,
        owner: __dataclass__init__fields__0__annotation,
        p: __dataclass__init__fields__1__annotation,
    ) -> __dataclass__None:
        __dataclass__object_setattr(self, 'owner', owner)
        __dataclass__object_setattr(self, 'p', p)
    
    __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
    if '__init__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__init__', __init__)
    
    @__dataclass___recursive_repr()
    def __repr__(self):
        parts = []
        parts.append(f"owner={self.owner!r}")
        parts.append(f"p={self.p!r}")
        return (
            f"{self.__class__.__qualname__}("
            f"{', '.join(parts)}"
            f")"
        )
    
    __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
    if '__repr__' in __dataclass__cls.__dict__:
        raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
    setattr(__dataclass__cls, '__repr__', __repr__)
