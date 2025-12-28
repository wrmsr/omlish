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
        "Plans(tup=(CopyPlan(fields=('name', 'root')), EqPlan(fields=('name', 'root')), FrozenPlan(fields=('name', 'roo"
        "t'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('name', 'root'), cache=False), InitPlan"
        "(fields=(InitPlan.Field(name='name', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_"
        "factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type"
        "=None), InitPlan.Field(name='root', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_f"
        "actory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type="
        "None)), self_param='self', std_params=('name', 'root'), kw_only_params=(), frozen=True, slots=False, post_init"
        "_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='name', kw_only=False, fn=No"
        "ne), ReprPlan.Field(name='root', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='2c0fde04446fe22ec745d89192a13d59b4b1d280',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('ommlds.minichain._marshal', 'JsonSchema'),
    ),
)
def _process_dataclass__2c0fde04446fe22ec745d89192a13d59b4b1d280():
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
                root=self.root,
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
                self.root == other.root
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'name',
            'root',
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
            'root',
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
                self.root,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            name: __dataclass__init__fields__0__annotation,
            root: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'root', root)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"name={self.name!r}")
            parts.append(f"root={self.root!r}")
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
        "Plans(tup=(CopyPlan(fields=('tvs_rty',)), EqPlan(fields=('tvs_rty',)), HashPlan(action='set_none', fields=None"
        ", cache=None), InitPlan(fields=(InitPlan.Field(name='tvs_rty', annotation=OpRef(name='init.fields.0.annotation"
        "'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None,"
        " validate=None, check_type=None),), self_param='self', std_params=('tvs_rty',), kw_only_params=(), frozen=Fals"
        "e, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='tv"
        "s_rty', kw_only=False, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='5ff91637e71f103a7df9eb0cda9a79d689462daa',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain._marshal', '_TypedValuesFieldMarshalerFactory'),
        ('ommlds.minichain._marshal', '_TypedValuesFieldUnmarshalerFactory'),
    ),
)
def _process_dataclass__5ff91637e71f103a7df9eb0cda9a79d689462daa():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                tvs_rty=self.tvs_rty,
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
                self.tvs_rty == other.tvs_rty
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        setattr(__dataclass__cls, '__hash__', None)

        def __init__(
            self,
            tvs_rty: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            self.tvs_rty = tvs_rty

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"tvs_rty={self.tvs_rty!r}")
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
        "Plans(tup=(CopyPlan(fields=('service_cls', 'name', 'factory_fn')), FrozenPlan(fields=('service_cls', 'name', '"
        "factory_fn'), allow_dynamic_dunder_attrs=False), InitPlan(fields=(InitPlan.Field(name='service_cls', annotatio"
        "n=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field"
        "_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='name', annotation"
        "=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_"
        "type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='factory_fn', annot"
        "ation=OpRef(name='init.fields.2.annotation'), default=None, default_factory=None, init=True, override=False, f"
        "ield_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=('s"
        "ervice_cls', 'name', 'factory_fn'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_f"
        "ns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='service_cls', kw_only=False, fn=None), ReprPlan"
        ".Field(name='name', kw_only=False, fn=None), ReprPlan.Field(name='factory_fn', kw_only=False, fn=None)), id=Fa"
        "lse, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='65dff4bc90ea364cde2f95f6d5d9a2c70fb63c18',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.backends.catalogs.simple', 'SimpleBackendCatalogEntry'),
    ),
)
def _process_dataclass__65dff4bc90ea364cde2f95f6d5d9a2c70fb63c18():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
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
                service_cls=self.service_cls,
                name=self.name,
                factory_fn=self.factory_fn,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        __dataclass___setattr_frozen_fields = {
            'service_cls',
            'name',
            'factory_fn',
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
            'service_cls',
            'name',
            'factory_fn',
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
            service_cls: __dataclass__init__fields__0__annotation,
            name: __dataclass__init__fields__1__annotation,
            factory_fn: __dataclass__init__fields__2__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'service_cls', service_cls)
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'factory_fn', factory_fn)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"service_cls={self.service_cls!r}")
            parts.append(f"name={self.name!r}")
            parts.append(f"factory_fn={self.factory_fn!r}")
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
        "Plans(tup=(CopyPlan(fields=('ra', 'lst')), EqPlan(fields=('ra', 'lst')), HashPlan(action='set_none', fields=No"
        "ne, cache=None), InitPlan(fields=(InitPlan.Field(name='ra', annotation=OpRef(name='init.fields.0.annotation'),"
        " default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, va"
        "lidate=None, check_type=None), InitPlan.Field(name='lst', annotation=OpRef(name='init.fields.1.annotation'), d"
        "efault=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, vali"
        "date=None, check_type=None)), self_param='self', std_params=('ra', 'lst'), kw_only_params=(), frozen=False, sl"
        "ots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='ra', kw"
        "_only=False, fn=None), ReprPlan.Field(name='lst', kw_only=False, fn=None)), id=False, terse=False, default_fn="
        "None)))"
    ),
    plan_repr_sha1='65a4fe67fac0748cfb55c6f5820bf0837c939b9d',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.backends.catalogs.strings', 'AmbiguousBackendStringResolutionError'),
    ),
)
def _process_dataclass__65a4fe67fac0748cfb55c6f5820bf0837c939b9d():
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
                ra=self.ra,
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
                self.ra == other.ra and
                self.lst == other.lst
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        setattr(__dataclass__cls, '__hash__', None)

        def __init__(
            self,
            ra: __dataclass__init__fields__0__annotation,
            lst: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            self.ra = ra
            self.lst = lst

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"ra={self.ra!r}")
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

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('v',)), EqPlan(fields=('v',)), FrozenPlan(fields=('v',), allow_dynamic_dunder_attr"
        "s=False), HashPlan(action='add', fields=('v',), cache=False), InitPlan(fields=(InitPlan.Field(name='v', annota"
        "tion=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, fi"
        "eld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self', std_params=('v"
        "',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPl"
        "an(fields=(ReprPlan.Field(name='v', kw_only=False, fn=None),), id=False, terse=True, default_fn=None)))"
    ),
    plan_repr_sha1='3576262424b3ef8ff20966fa3744e5dba9a2ae7d',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.backends.catalogs.strings', 'ModelName'),
        ('ommlds.minichain.backends.catalogs.strings', 'ModelPath'),
        ('ommlds.minichain.backends.impls.sentencepiece.tokens', 'TokenStr'),
        ('ommlds.minichain.backends.impls.transformers.transformers', 'TransformersPipelineKwargs'),
        ('ommlds.minichain.chat.templating', 'MessageTemplate'),
        ('ommlds.minichain.chat.transforms.metadata', 'TransformedMessageOrigin'),
        ('ommlds.minichain.completion', 'FinishReasonOutput'),
        ('ommlds.minichain.completion', 'MaxCompletionTokens'),
        ('ommlds.minichain.completion', 'MaxTokens'),
        ('ommlds.minichain.completion', 'Temperature'),
        ('ommlds.minichain.completion', 'TokenUsageOutput'),
        ('ommlds.minichain.completion', 'TopK'),
        ('ommlds.minichain.metadata', 'CreatedAt'),
        ('ommlds.minichain.metadata', 'Uuid'),
        ('ommlds.minichain.resources', 'UseResources'),
        ('ommlds.minichain.standard', 'ApiUrl'),
        ('ommlds.minichain.standard', 'Device'),
    ),
)
def _process_dataclass__3576262424b3ef8ff20966fa3744e5dba9a2ae7d():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
            return hash((
                self.v,
            ))

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
            parts.append(f"{self.v!r}")
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
        "Plans(tup=(CopyPlan(fields=('default', 'aliases')), EqPlan(fields=('default', 'aliases')), FrozenPlan(fields=("
        "'default', 'aliases'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('default', 'aliases')"
        ", cache=False), InitPlan(fields=(InitPlan.Field(name='default', annotation=OpRef(name='init.fields.0.annotatio"
        "n'), default=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type="
        "FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='aliases', annotation=Op"
        "Ref(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init="
        "True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param"
        "='self', std_params=(), kw_only_params=('default', 'aliases'), frozen=True, slots=False, post_init_params=None"
        ", init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='default', kw_only=True, fn=None), ReprP"
        "lan.Field(name='aliases', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='ac01c4fef98980477efa107b7b5909a6386bef53',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.minichain.backends.catalogs.strings', 'ModelNameCollection'),
    ),
)
def _process_dataclass__ac01c4fef98980477efa107b7b5909a6386bef53():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
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
                aliases=self.aliases,
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
                self.aliases == other.aliases
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'default',
            'aliases',
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
            'aliases',
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
                self.aliases,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            default: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            aliases: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'default', default)
            __dataclass__object_setattr(self, 'aliases', aliases)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"default={self.default!r}")
            parts.append(f"aliases={self.aliases!r}")
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
        "Plans(tup=(CopyPlan(fields=('namespace', 'repo', 'tag', 'path')), EqPlan(fields=('namespace', 'repo', 'tag', '"
        "path')), FrozenPlan(fields=('namespace', 'repo', 'tag', 'path'), allow_dynamic_dunder_attrs=False), HashPlan(a"
        "ction='add', fields=('namespace', 'repo', 'tag', 'path'), cache=False), InitPlan(fields=(InitPlan.Field(name='"
        "namespace', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, "
        "override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(na"
        "me='repo', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, o"
        "verride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(nam"
        "e='tag', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), defau"
        "lt_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_t"
        "ype=None), InitPlan.Field(name='path', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='"
        "init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerc"
        "e=None, validate=None, check_type=None)), self_param='self', std_params=('namespace', 'repo'), kw_only_params="
        "('tag', 'path'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fiel"
        "ds=(ReprPlan.Field(name='namespace', kw_only=False, fn=None), ReprPlan.Field(name='repo', kw_only=False, fn=No"
        "ne), ReprPlan.Field(name='tag', kw_only=True, fn=OpRef(name='repr.fns.2.fn')), ReprPlan.Field(name='path', kw_"
        "only=True, fn=OpRef(name='repr.fns.3.fn'))), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='763b0424aa73f5ec852de236e39950f9c105259c',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
        '__dataclass__repr__fns__2__fn',
        '__dataclass__repr__fns__3__fn',
    ),
    cls_names=(
        ('ommlds.minichain.backends.catalogs.strings', 'ModelRepo'),
    ),
)
def _process_dataclass__763b0424aa73f5ec852de236e39950f9c105259c():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__3__default,
        __dataclass__repr__fns__2__fn,
        __dataclass__repr__fns__3__fn,
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
                namespace=self.namespace,
                repo=self.repo,
                tag=self.tag,
                path=self.path,
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
                self.namespace == other.namespace and
                self.repo == other.repo and
                self.tag == other.tag and
                self.path == other.path
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'namespace',
            'repo',
            'tag',
            'path',
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
            'namespace',
            'repo',
            'tag',
            'path',
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
                self.namespace,
                self.repo,
                self.tag,
                self.path,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            namespace: __dataclass__init__fields__0__annotation,
            repo: __dataclass__init__fields__1__annotation,
            *,
            tag: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            path: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'namespace', namespace)
            __dataclass__object_setattr(self, 'repo', repo)
            __dataclass__object_setattr(self, 'tag', tag)
            __dataclass__object_setattr(self, 'path', path)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"namespace={self.namespace!r}")
            parts.append(f"repo={self.repo!r}")
            if (s := __dataclass__repr__fns__2__fn(self.tag)) is not None:
                parts.append(f"tag={s}")
            if (s := __dataclass__repr__fns__3__fn(self.path)) is not None:
                parts.append(f"path={s}")
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
        "Plans(tup=(CopyPlan(fields=('backend', 'model')), EqPlan(fields=('backend', 'model')), FrozenPlan(fields=('bac"
        "kend', 'model'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('backend', 'model'), cache="
        "False), InitPlan(fields=(InitPlan.Field(name='backend', annotation=OpRef(name='init.fields.0.annotation'), def"
        "ault=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldTyp"
        "e.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='model', annotation=OpRef(name='"
        "init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldTyp"
        "e.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('"
        "backend', 'model'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(f"
        "ields=(ReprPlan.Field(name='backend', kw_only=True, fn=OpRef(name='repr.fns.0.fn')), ReprPlan.Field(name='mode"
        "l', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='b4a9277b8c9559fb4e325a8c35bc504f30ab2294',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__repr__fns__0__fn',
    ),
    cls_names=(
        ('ommlds.minichain.backends.catalogs.strings', 'ParsedBackendString'),
    ),
)
def _process_dataclass__b4a9277b8c9559fb4e325a8c35bc504f30ab2294():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__repr__fns__0__fn,
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
                backend=self.backend,
                model=self.model,
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
                self.backend == other.backend and
                self.model == other.model
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'backend',
            'model',
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
            'backend',
            'model',
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
                self.backend,
                self.model,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            backend: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            model: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'backend', backend)
            __dataclass__object_setattr(self, 'model', model)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__fns__0__fn(self.backend)) is not None:
                parts.append(f"backend={s}")
            parts.append(f"model={self.model!r}")
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
        "Plans(tup=(CopyPlan(fields=()), EqPlan(fields=()), FrozenPlan(fields=(), allow_dynamic_dunder_attrs=False), Ha"
        "shPlan(action='add', fields=(), cache=False), InitPlan(fields=(), self_param='self', std_params=(), kw_only_pa"
        "rams=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(), i"
        "d=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='e1f7edfe11f2b721d6a656c46e698fedc95461bb',
    op_ref_idents=(),
    cls_names=(
        ('ommlds.minichain.backends.catalogs.strings', 'ParsedBackendString.Model'),
        ('ommlds.minichain.backends.impls.anthropic.stream', 'AiDelta'),
        ('ommlds.minichain.backends.impls.mistral', 'ToolDtype'),
        ('ommlds.minichain.chat.formats', 'TextResponseFormat'),
        ('ommlds.minichain.chat.tools.execution', 'ToolFn.Impl'),
        ('ommlds.minichain.chat.tools.execution', 'ToolFn.Input'),
        ('ommlds.minichain.chat.tools.execution', 'ToolFn.Output'),
        ('ommlds.minichain.chat.tools.execution', 'ToolFn.RawKwargsInput'),
        ('ommlds.minichain.chat.tools.execution', 'ToolFn.RawStringOutput'),
    ),
)
def _process_dataclass__e1f7edfe11f2b721d6a656c46e698fedc95461bb():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
            return __dataclass__cls()  # noqa

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return True

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

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

        def __hash__(self):
            return hash(())

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

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
        "Plans(tup=(CopyPlan(fields=('name',)), EqPlan(fields=('name',)), FrozenPlan(fields=('name',), allow_dynamic_du"
        "nder_attrs=False), HashPlan(action='add', fields=('name',), cache=False), InitPlan(fields=(InitPlan.Field(name"
        "='name', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, ove"
        "rride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self',"
        " std_params=('name',), kw_only_params=(), frozen=True, slots=False, post_init_params=(), init_fns=(), validate"
        "_fns=()), ReprPlan(fields=(ReprPlan.Field(name='name', kw_only=False, fn=None),), id=False, terse=False, defau"
        "lt_fn=None)))"
    ),
    plan_repr_sha1='fa34713788012fde9d90d5102da095d7ac89b21e',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.backends.catalogs.strings', 'ParsedBackendString.NameModel'),
    ),
)
def _process_dataclass__fa34713788012fde9d90d5102da095d7ac89b21e():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                self.name == other.name
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'name',
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
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            name: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            self.__post_init__()

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
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

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('path',)), EqPlan(fields=('path',)), FrozenPlan(fields=('path',), allow_dynamic_du"
        "nder_attrs=False), HashPlan(action='add', fields=('path',), cache=False), InitPlan(fields=(InitPlan.Field(name"
        "='path', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, ove"
        "rride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self',"
        " std_params=('path',), kw_only_params=(), frozen=True, slots=False, post_init_params=(), init_fns=(), validate"
        "_fns=()), ReprPlan(fields=(ReprPlan.Field(name='path', kw_only=False, fn=None),), id=False, terse=False, defau"
        "lt_fn=None)))"
    ),
    plan_repr_sha1='41fb428eca6e7c8ff6749bae9db8d6f90ab874d0',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.backends.catalogs.strings', 'ParsedBackendString.PathModel'),
    ),
)
def _process_dataclass__41fb428eca6e7c8ff6749bae9db8d6f90ab874d0():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                path=self.path,
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
                self.path == other.path
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'path',
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
            'path',
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
                self.path,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            path: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'path', path)
            self.__post_init__()

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"path={self.path!r}")
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
        "Plans(tup=(CopyPlan(fields=('namespace', 'repo', 'tag', 'path')), EqPlan(fields=('namespace', 'repo', 'tag', '"
        "path')), FrozenPlan(fields=('namespace', 'repo', 'tag', 'path'), allow_dynamic_dunder_attrs=False), HashPlan(a"
        "ction='add', fields=('namespace', 'repo', 'tag', 'path'), cache=False), InitPlan(fields=(InitPlan.Field(name='"
        "namespace', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, "
        "override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(na"
        "me='repo', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, o"
        "verride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(nam"
        "e='tag', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), defau"
        "lt_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_t"
        "ype=None), InitPlan.Field(name='path', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='"
        "init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerc"
        "e=None, validate=None, check_type=None)), self_param='self', std_params=('namespace', 'repo'), kw_only_params="
        "('tag', 'path'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fiel"
        "ds=(ReprPlan.Field(name='namespace', kw_only=False, fn=None), ReprPlan.Field(name='repo', kw_only=False, fn=No"
        "ne), ReprPlan.Field(name='tag', kw_only=True, fn=None), ReprPlan.Field(name='path', kw_only=True, fn=None)), i"
        "d=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='01212b8db75220e8e4b07cdadb35bc394f9d696d',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ommlds.minichain.backends.catalogs.strings', 'ParsedBackendString.RepoModel'),
    ),
)
def _process_dataclass__01212b8db75220e8e4b07cdadb35bc394f9d696d():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__3__default,
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
                namespace=self.namespace,
                repo=self.repo,
                tag=self.tag,
                path=self.path,
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
                self.namespace == other.namespace and
                self.repo == other.repo and
                self.tag == other.tag and
                self.path == other.path
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'namespace',
            'repo',
            'tag',
            'path',
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
            'namespace',
            'repo',
            'tag',
            'path',
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
                self.namespace,
                self.repo,
                self.tag,
                self.path,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            namespace: __dataclass__init__fields__0__annotation,
            repo: __dataclass__init__fields__1__annotation,
            *,
            tag: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            path: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'namespace', namespace)
            __dataclass__object_setattr(self, 'repo', repo)
            __dataclass__object_setattr(self, 'tag', tag)
            __dataclass__object_setattr(self, 'path', path)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"namespace={self.namespace!r}")
            parts.append(f"repo={self.repo!r}")
            parts.append(f"tag={self.tag!r}")
            parts.append(f"path={self.path!r}")
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
        "Plans(tup=(CopyPlan(fields=('service_cls', 'parsed')), EqPlan(fields=('service_cls', 'parsed')), FrozenPlan(fi"
        "elds=('service_cls', 'parsed'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('service_cls"
        "', 'parsed'), cache=False), InitPlan(fields=(InitPlan.Field(name='service_cls', annotation=OpRef(name='init.fi"
        "elds.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTA"
        "NCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='parsed', annotation=OpRef(name='init.f"
        "ields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INST"
        "ANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=('service_cls', 'parsed'), "
        "kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fi"
        "elds=(ReprPlan.Field(name='service_cls', kw_only=False, fn=None), ReprPlan.Field(name='parsed', kw_only=False,"
        " fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='0454ccc53c07928f0fbec2218c3c5d6625ef623e',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.backends.catalogs.strings', 'ResolveBackendStringArgs'),
    ),
)
def _process_dataclass__0454ccc53c07928f0fbec2218c3c5d6625ef623e():
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
                service_cls=self.service_cls,
                parsed=self.parsed,
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
                self.service_cls == other.service_cls and
                self.parsed == other.parsed
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'service_cls',
            'parsed',
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
            'service_cls',
            'parsed',
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
                self.service_cls,
                self.parsed,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            service_cls: __dataclass__init__fields__0__annotation,
            parsed: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'service_cls', service_cls)
            __dataclass__object_setattr(self, 'parsed', parsed)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"service_cls={self.service_cls!r}")
            parts.append(f"parsed={self.parsed!r}")
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
        "Plans(tup=(CopyPlan(fields=('service_cls', 'name', 'args')), EqPlan(fields=('service_cls', 'name', 'args')), F"
        "rozenPlan(fields=('service_cls', 'name', 'args'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fi"
        "elds=('service_cls', 'name', 'args'), cache=False), InitPlan(fields=(InitPlan.Field(name='service_cls', annota"
        "tion=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, fi"
        "eld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='name', annotat"
        "ion=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, fie"
        "ld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='args', annotati"
        "on=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, "
        "init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_"
        "param='self', std_params=('service_cls', 'name'), kw_only_params=('args',), frozen=True, slots=False, post_ini"
        "t_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='service_cls', kw_only=Fals"
        "e, fn=None), ReprPlan.Field(name='name', kw_only=False, fn=None), ReprPlan.Field(name='args', kw_only=True, fn"
        "=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='9239d738d1384a469cf6a3a3791e0a52c045427a',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.minichain.backends.catalogs.strings', 'ResolveBackendStringResult'),
    ),
)
def _process_dataclass__9239d738d1384a469cf6a3a3791e0a52c045427a():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
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
                service_cls=self.service_cls,
                name=self.name,
                args=self.args,
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
                self.service_cls == other.service_cls and
                self.name == other.name and
                self.args == other.args
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'service_cls',
            'name',
            'args',
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
            'service_cls',
            'name',
            'args',
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
                self.service_cls,
                self.name,
                self.args,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            service_cls: __dataclass__init__fields__0__annotation,
            name: __dataclass__init__fields__1__annotation,
            *,
            args: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'service_cls', service_cls)
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'args', args)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"service_cls={self.service_cls!r}")
            parts.append(f"name={self.name!r}")
            parts.append(f"args={self.args!r}")
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
        "Plans(tup=(CopyPlan(fields=('strip_strings', 'block_separator')), EqPlan(fields=('strip_strings', 'block_separ"
        "ator')), FrozenPlan(fields=('strip_strings', 'block_separator'), allow_dynamic_dunder_attrs=False), HashPlan(a"
        "ction='add', fields=('strip_strings', 'block_separator'), cache=False), InitPlan(fields=(InitPlan.Field(name='"
        "strip_strings', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default')"
        ", default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, "
        "check_type=None), InitPlan.Field(name='block_separator', annotation=OpRef(name='init.fields.1.annotation'), de"
        "fault=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldTy"
        "pe.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=("
        "'strip_strings', 'block_separator'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fn"
        "s=()), ReprPlan(fields=(ReprPlan.Field(name='strip_strings', kw_only=True, fn=None), ReprPlan.Field(name='bloc"
        "k_separator', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='fb524d5ea93dc8d754817cceb8ef80700578a20b',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.anthropic.chat', 'DefaultContentPreparer'),
    ),
)
def _process_dataclass__fb524d5ea93dc8d754817cceb8ef80700578a20b():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
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
                strip_strings=self.strip_strings,
                block_separator=self.block_separator,
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
                self.strip_strings == other.strip_strings and
                self.block_separator == other.block_separator
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'strip_strings',
            'block_separator',
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
            'strip_strings',
            'block_separator',
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
                self.strip_strings,
                self.block_separator,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            strip_strings: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            block_separator: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'strip_strings', strip_strings)
            __dataclass__object_setattr(self, 'block_separator', block_separator)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"strip_strings={self.strip_strings!r}")
            parts.append(f"block_separator={self.block_separator!r}")
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
        "Plans(tup=(CopyPlan(fields=('content_preparer',)), EqPlan(fields=('content_preparer',)), FrozenPlan(fields=('c"
        "ontent_preparer',), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('content_preparer',), ca"
        "che=False), InitPlan(fields=(InitPlan.Field(name='content_preparer', annotation=OpRef(name='init.fields.0.anno"
        "tation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce"
        "=None, validate=None, check_type=None),), self_param='self', std_params=('content_preparer',), kw_only_params="
        "(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan."
        "Field(name='content_preparer', kw_only=False, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='35363258df752d37be526c05a33a4e10963d6e84',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.anthropic.chat', 'DefaultContentStrPreparer'),
    ),
)
def _process_dataclass__35363258df752d37be526c05a33a4e10963d6e84():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                content_preparer=self.content_preparer,
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
                self.content_preparer == other.content_preparer
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'content_preparer',
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
            'content_preparer',
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
                self.content_preparer,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            content_preparer: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'content_preparer', content_preparer)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"content_preparer={self.content_preparer!r}")
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
        "Plans(tup=(CopyPlan(fields=('_metadata', 'ns')), EqPlan(fields=('_metadata', 'ns')), FrozenPlan(fields=('_meta"
        "data', 'ns'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('_metadata', 'ns'), cache=Fals"
        "e), InitPlan(fields=(InitPlan.Field(name='_metadata', annotation=OpRef(name='init.fields.0.annotation'), defau"
        "lt=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType."
        "INSTANCE, coerce=OpRef(name='init.fields.0.coerce'), validate=None, check_type=None), InitPlan.Field(name='ns'"
        ", annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=F"
        "alse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_par"
        "ams=('ns',), kw_only_params=('_metadata',), frozen=True, slots=False, post_init_params=None, init_fns=(), vali"
        "date_fns=()), ReprPlan(fields=(ReprPlan.Field(name='_metadata', kw_only=True, fn=OpRef(name='repr.fns.0.fn')),"
        " ReprPlan.Field(name='ns', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='0f33bd4feb26aa84d3ce09fc68cea42d08f0a4ff',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__coerce',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__repr__fns__0__fn',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.anthropic.chat', 'NamespaceContent'),
    ),
)
def _process_dataclass__0f33bd4feb26aa84d3ce09fc68cea42d08f0a4ff():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__coerce,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__repr__fns__0__fn,
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
                _metadata=self._metadata,
                ns=self.ns,
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
                self._metadata == other._metadata and
                self.ns == other.ns
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '_metadata',
            'ns',
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
            '_metadata',
            'ns',
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
                self._metadata,
                self.ns,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            ns: __dataclass__init__fields__1__annotation,
            *,
            _metadata: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            _metadata = __dataclass__init__fields__0__coerce(_metadata)
            __dataclass__object_setattr(self, '_metadata', _metadata)
            __dataclass__object_setattr(self, 'ns', ns)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__fns__0__fn(self._metadata)) is not None:
                parts.append(f"_metadata={s}")
            parts.append(f"ns={self.ns!r}")
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
        "Plans(tup=(CopyPlan(fields=('_metadata', 'k')), EqPlan(fields=('_metadata', 'k')), FrozenPlan(fields=('_metada"
        "ta', 'k'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('_metadata', 'k'), cache=False), "
        "InitPlan(fields=(InitPlan.Field(name='_metadata', annotation=OpRef(name='init.fields.0.annotation'), default=O"
        "pRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INST"
        "ANCE, coerce=OpRef(name='init.fields.0.coerce'), validate=None, check_type=None), InitPlan.Field(name='k', ann"
        "otation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False,"
        " field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=("
        "'k',), kw_only_params=('_metadata',), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_f"
        "ns=()), ReprPlan(fields=(ReprPlan.Field(name='_metadata', kw_only=True, fn=OpRef(name='repr.fns.0.fn')), ReprP"
        "lan.Field(name='k', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='1cc33387d7e697b5a516373c8733717d303ca7dc',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__coerce',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__repr__fns__0__fn',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.anthropic.chat', 'PlaceholderContent'),
    ),
)
def _process_dataclass__1cc33387d7e697b5a516373c8733717d303ca7dc():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__coerce,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__repr__fns__0__fn,
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
                _metadata=self._metadata,
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
                self._metadata == other._metadata and
                self.k == other.k
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '_metadata',
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
            '_metadata',
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
            return hash((
                self._metadata,
                self.k,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            k: __dataclass__init__fields__1__annotation,
            *,
            _metadata: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            _metadata = __dataclass__init__fields__0__coerce(_metadata)
            __dataclass__object_setattr(self, '_metadata', _metadata)
            __dataclass__object_setattr(self, 'k', k)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__fns__0__fn(self._metadata)) is not None:
                parts.append(f"_metadata={s}")
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

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('key',)), EqPlan(fields=('key',)), HashPlan(action='set_none', fields=None, cache="
        "None), InitPlan(fields=(InitPlan.Field(name='key', annotation=OpRef(name='init.fields.0.annotation'), default="
        "None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=No"
        "ne, check_type=None),), self_param='self', std_params=('key',), kw_only_params=(), frozen=False, slots=False, "
        "post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='key', kw_only=Fals"
        "e, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='7e1881cd893ea68089f1fe26ad810799dd14a0d5',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.anthropic.chat', 'PlaceholderContentMissingError'),
    ),
)
def _process_dataclass__7e1881cd893ea68089f1fe26ad810799dd14a0d5():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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

        setattr(__dataclass__cls, '__hash__', None)

        def __init__(
            self,
            key: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            self.key = key

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

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('spec',)), EqPlan(fields=('spec',)), FrozenPlan(fields=('spec',), allow_dynamic_du"
        "nder_attrs=False), HashPlan(action='add', fields=('spec',), cache=False), InitPlan(fields=(InitPlan.Field(name"
        "='spec', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, ove"
        "rride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self',"
        " std_params=('spec',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), valida"
        "te_fns=()), ReprPlan(fields=(ReprPlan.Field(name='spec', kw_only=False, fn=None),), id=False, terse=False, def"
        "ault_fn=None)))"
    ),
    plan_repr_sha1='7e3901d21ea09aa23ed5fbe10c0b3872163af79f',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.anthropic.chat', 'Tool'),
    ),
)
def _process_dataclass__7e3901d21ea09aa23ed5fbe10c0b3872163af79f():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                spec=self.spec,
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
                self.spec == other.spec
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'spec',
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
            'spec',
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
                self.spec,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            spec: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'spec', spec)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"spec={self.spec!r}")
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
        "Plans(tup=(CopyPlan(fields=('deltas',)), EqPlan(fields=('deltas',)), FrozenPlan(fields=('deltas',), allow_dyna"
        "mic_dunder_attrs=False), HashPlan(action='add', fields=('deltas',), cache=False), InitPlan(fields=(InitPlan.Fi"
        "eld(name='deltas', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init"
        "=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_par"
        "am='self', std_params=('deltas',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fn"
        "s=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='deltas', kw_only=False, fn=None),), id=False, te"
        "rse=False, default_fn=None)))"
    ),
    plan_repr_sha1='1003b02dad553d007500114656708fbdf6d2db2e',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.anthropic.stream', 'AiChoiceDeltas'),
    ),
)
def _process_dataclass__1003b02dad553d007500114656708fbdf6d2db2e():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                deltas=self.deltas,
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
                self.deltas == other.deltas
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'deltas',
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
            'deltas',
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
                self.deltas,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            deltas: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'deltas', deltas)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"deltas={self.deltas!r}")
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
        "Plans(tup=(CopyPlan(fields=('choices',)), EqPlan(fields=('choices',)), FrozenPlan(fields=('choices',), allow_d"
        "ynamic_dunder_attrs=False), HashPlan(action='add', fields=('choices',), cache=False), InitPlan(fields=(InitPla"
        "n.Field(name='choices', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None,"
        " init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), sel"
        "f_param='self', std_params=('choices',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, i"
        "nit_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='choices', kw_only=False, fn=None),), id=Fa"
        "lse, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='4f63c0632d5deeaaca3a2cac8b16c190d46387cd',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.anthropic.stream', 'AiChoicesDeltas'),
    ),
)
def _process_dataclass__4f63c0632d5deeaaca3a2cac8b16c190d46387cd():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                choices=self.choices,
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
                self.choices == other.choices
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'choices',
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
            'choices',
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
                self.choices,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            choices: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'choices', choices)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"choices={self.choices!r}")
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
        "Plans(tup=(CopyPlan(fields=('id', 'name')), EqPlan(fields=('id', 'name')), FrozenPlan(fields=('id', 'name'), a"
        "llow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('id', 'name'), cache=False), InitPlan(fields="
        "(InitPlan.Field(name='id', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields."
        "0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, vali"
        "date=None, check_type=None), InitPlan.Field(name='name', annotation=OpRef(name='init.fields.1.annotation'), de"
        "fault=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldTy"
        "pe.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=("
        "'id', 'name'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields"
        "=(ReprPlan.Field(name='id', kw_only=True, fn=None), ReprPlan.Field(name='name', kw_only=True, fn=None)), id=Fa"
        "lse, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='8a0c9fe2c4d9f2351ede8bd96b873d4507e2617b',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.anthropic.stream', 'AnyToolUseAiDelta'),
    ),
)
def _process_dataclass__8a0c9fe2c4d9f2351ede8bd96b873d4507e2617b():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
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
                id=self.id,
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
                self.id == other.id and
                self.name == other.name
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'id',
            'name',
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
            'name',
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
                self.name,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            id: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            name: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'name', name)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"id={self.id!r}")
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

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('c',)), EqPlan(fields=('c',)), FrozenPlan(fields=('c',), allow_dynamic_dunder_attr"
        "s=False), HashPlan(action='add', fields=('c',), cache=False), InitPlan(fields=(InitPlan.Field(name='c', annota"
        "tion=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, fi"
        "eld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self', std_params=('c"
        "',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPl"
        "an(fields=(ReprPlan.Field(name='c', kw_only=False, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='236614658d6f97131f18c84f79eabfe1f3abcc04',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.anthropic.stream', 'ContentAiDelta'),
    ),
)
def _process_dataclass__236614658d6f97131f18c84f79eabfe1f3abcc04():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                c=self.c,
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
                self.c == other.c
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'c',
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
            'c',
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
                self.c,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            c: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'c', c)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"c={self.c!r}")
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
        "Plans(tup=(CopyPlan(fields=('id', 'name', 'raw_args')), EqPlan(fields=('id', 'name', 'raw_args')), FrozenPlan("
        "fields=('id', 'name', 'raw_args'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('id', 'na"
        "me', 'raw_args'), cache=False), InitPlan(fields=(InitPlan.Field(name='id', annotation=OpRef(name='init.fields."
        "0.annotation'), default=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, "
        "field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='name', annot"
        "ation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=Non"
        "e, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), Ini"
        "tPlan.Field(name='raw_args', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.field"
        "s.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, va"
        "lidate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('id', 'name', 'raw_args'), f"
        "rozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field"
        "(name='id', kw_only=True, fn=None), ReprPlan.Field(name='name', kw_only=True, fn=None), ReprPlan.Field(name='r"
        "aw_args', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='cfed714e6979875588ca1b2ed72ceb360b3b6a17',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.anthropic.stream', 'PartialToolUseAiDelta'),
    ),
)
def _process_dataclass__cfed714e6979875588ca1b2ed72ceb360b3b6a17():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
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
                id=self.id,
                name=self.name,
                raw_args=self.raw_args,
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
                self.id == other.id and
                self.name == other.name and
                self.raw_args == other.raw_args
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'id',
            'name',
            'raw_args',
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
            'name',
            'raw_args',
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
                self.name,
                self.raw_args,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            id: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            name: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            raw_args: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'raw_args', raw_args)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"id={self.id!r}")
            parts.append(f"name={self.name!r}")
            parts.append(f"raw_args={self.raw_args!r}")
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
        "Plans(tup=(CopyPlan(fields=('id', 'name', 'args')), EqPlan(fields=('id', 'name', 'args')), FrozenPlan(fields=("
        "'id', 'name', 'args'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('id', 'name', 'args')"
        ", cache=False), InitPlan(fields=(InitPlan.Field(name='id', annotation=OpRef(name='init.fields.0.annotation'), "
        "default=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=Field"
        "Type.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='name', annotation=OpRef(name"
        "='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, ov"
        "erride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name"
        "='args', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), defau"
        "lt_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_t"
        "ype=None)), self_param='self', std_params=(), kw_only_params=('id', 'name', 'args'), frozen=True, slots=False,"
        " post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='id', kw_only=True"
        ", fn=None), ReprPlan.Field(name='name', kw_only=True, fn=None), ReprPlan.Field(name='args', kw_only=True, fn=N"
        "one)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='ed63be27107f8491d8d4a297d57ae8cb6ce13cc0',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.anthropic.stream', 'ToolUseAiDelta'),
    ),
)
def _process_dataclass__ed63be27107f8491d8d4a297d57ae8cb6ce13cc0():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
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
                id=self.id,
                name=self.name,
                args=self.args,
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
                self.id == other.id and
                self.name == other.name and
                self.args == other.args
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'id',
            'name',
            'args',
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
            'name',
            'args',
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
                self.name,
                self.args,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            id: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            name: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            args: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'args', args)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"id={self.id!r}")
            parts.append(f"name={self.name!r}")
            parts.append(f"args={self.args!r}")
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
        "Plans(tup=(CopyPlan(fields=('search_time', 'total_results', 'x')), EqPlan(fields=('search_time', 'total_result"
        "s', 'x')), FrozenPlan(fields=('search_time', 'total_results', 'x'), allow_dynamic_dunder_attrs=False), HashPla"
        "n(action='add', fields=('search_time', 'total_results', 'x'), cache=False), InitPlan(fields=(InitPlan.Field(na"
        "me='search_time', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default"
        "'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None"
        ", check_type=None), InitPlan.Field(name='total_results', annotation=OpRef(name='init.fields.1.annotation'), de"
        "fault=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldTy"
        "pe.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='x', annotation=OpRef(name='ini"
        "t.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, overrid"
        "e=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_"
        "params=('search_time', 'total_results', 'x'), kw_only_params=(), frozen=True, slots=False, post_init_params=No"
        "ne, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='search_time', kw_only=False, fn=None)"
        ", ReprPlan.Field(name='total_results', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='9011cfb69ca0947e15e02520950d8710d0d53d0a',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.google.search', 'CseSearchInfo'),
    ),
)
def _process_dataclass__9011cfb69ca0947e15e02520950d8710d0d53d0a():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
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
                search_time=self.search_time,
                total_results=self.total_results,
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
                self.search_time == other.search_time and
                self.total_results == other.total_results and
                self.x == other.x
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'search_time',
            'total_results',
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
            'search_time',
            'total_results',
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
                self.search_time,
                self.total_results,
                self.x,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            search_time: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            total_results: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            x: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'search_time', search_time)
            __dataclass__object_setattr(self, 'total_results', total_results)
            __dataclass__object_setattr(self, 'x', x)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"search_time={self.search_time!r}")
            parts.append(f"total_results={self.total_results!r}")
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
        "Plans(tup=(CopyPlan(fields=('kind', 'info', 'items', 'x')), EqPlan(fields=('kind', 'info', 'items', 'x')), Fro"
        "zenPlan(fields=('kind', 'info', 'items', 'x'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', field"
        "s=('kind', 'info', 'items', 'x'), cache=False), InitPlan(fields=(InitPlan.Field(name='kind', annotation=OpRef("
        "name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'), default_factory=None, init=True"
        ", override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field("
        "name='info', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), d"
        "efault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, che"
        "ck_type=None), InitPlan.Field(name='items', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(n"
        "ame='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, "
        "coerce=None, validate=None, check_type=None), InitPlan.Field(name='x', annotation=OpRef(name='init.fields.3.an"
        "notation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, fiel"
        "d_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=('kind"
        "', 'info', 'items', 'x'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), val"
        "idate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='kind', kw_only=False, fn=None), ReprPlan.Field(name='info"
        "', kw_only=False, fn=None), ReprPlan.Field(name='items', kw_only=False, fn=None)), id=False, terse=False, defa"
        "ult_fn=None)))"
    ),
    plan_repr_sha1='6a5c9824784a2112a23d98269f609312c1509aad',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.google.search', 'CseSearchResponse'),
    ),
)
def _process_dataclass__6a5c9824784a2112a23d98269f609312c1509aad():
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
                kind=self.kind,
                info=self.info,
                items=self.items,
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
                self.kind == other.kind and
                self.info == other.info and
                self.items == other.items and
                self.x == other.x
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'kind',
            'info',
            'items',
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
            'kind',
            'info',
            'items',
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
                self.kind,
                self.info,
                self.items,
                self.x,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            kind: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            info: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            items: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            x: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'kind', kind)
            __dataclass__object_setattr(self, 'info', info)
            __dataclass__object_setattr(self, 'items', items)
            __dataclass__object_setattr(self, 'x', x)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"kind={self.kind!r}")
            parts.append(f"info={self.info!r}")
            parts.append(f"items={self.items!r}")
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
        "Plans(tup=(CopyPlan(fields=('kind', 'title', 'html_title', 'link', 'display_link', 'snippet', 'html_snippet', "
        "'cache_id', 'formatted_url', 'html_formatted_url', 'mime', 'file_format', 'x')), EqPlan(fields=('kind', 'title"
        "', 'html_title', 'link', 'display_link', 'snippet', 'html_snippet', 'cache_id', 'formatted_url', 'html_formatt"
        "ed_url', 'mime', 'file_format', 'x')), FrozenPlan(fields=('kind', 'title', 'html_title', 'link', 'display_link"
        "', 'snippet', 'html_snippet', 'cache_id', 'formatted_url', 'html_formatted_url', 'mime', 'file_format', 'x'), "
        "allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('kind', 'title', 'html_title', 'link', 'disp"
        "lay_link', 'snippet', 'html_snippet', 'cache_id', 'formatted_url', 'html_formatted_url', 'mime', 'file_format'"
        ", 'x'), cache=False), InitPlan(fields=(InitPlan.Field(name='kind', annotation=OpRef(name='init.fields.0.annota"
        "tion'), default=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_ty"
        "pe=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='title', annotation=O"
        "pRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init"
        "=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.F"
        "ield(name='html_title', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.d"
        "efault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validat"
        "e=None, check_type=None), InitPlan.Field(name='link', annotation=OpRef(name='init.fields.3.annotation'), defau"
        "lt=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType."
        "INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='display_link', annotation=OpRef(n"
        "ame='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True,"
        " override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(n"
        "ame='snippet', annotation=OpRef(name='init.fields.5.annotation'), default=OpRef(name='init.fields.5.default'),"
        " default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, c"
        "heck_type=None), InitPlan.Field(name='html_snippet', annotation=OpRef(name='init.fields.6.annotation'), defaul"
        "t=OpRef(name='init.fields.6.default'), default_factory=None, init=True, override=False, field_type=FieldType.I"
        "NSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='cache_id', annotation=OpRef(name='"
        "init.fields.7.annotation'), default=OpRef(name='init.fields.7.default'), default_factory=None, init=True, over"
        "ride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='"
        "formatted_url', annotation=OpRef(name='init.fields.8.annotation'), default=OpRef(name='init.fields.8.default')"
        ", default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, "
        "check_type=None), InitPlan.Field(name='html_formatted_url', annotation=OpRef(name='init.fields.9.annotation'),"
        " default=OpRef(name='init.fields.9.default'), default_factory=None, init=True, override=False, field_type=Fiel"
        "dType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='mime', annotation=OpRef(nam"
        "e='init.fields.10.annotation'), default=OpRef(name='init.fields.10.default'), default_factory=None, init=True,"
        " override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(n"
        "ame='file_format', annotation=OpRef(name='init.fields.11.annotation'), default=OpRef(name='init.fields.11.defa"
        "ult'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=N"
        "one, check_type=None), InitPlan.Field(name='x', annotation=OpRef(name='init.fields.12.annotation'), default=Op"
        "Ref(name='init.fields.12.default'), default_factory=None, init=True, override=False, field_type=FieldType.INST"
        "ANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=('kind', 'title', 'html_tit"
        "le', 'link', 'display_link', 'snippet', 'html_snippet', 'cache_id', 'formatted_url', 'html_formatted_url', 'mi"
        "me', 'file_format', 'x'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), val"
        "idate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='kind', kw_only=False, fn=None), ReprPlan.Field(name='titl"
        "e', kw_only=False, fn=None), ReprPlan.Field(name='html_title', kw_only=False, fn=None), ReprPlan.Field(name='l"
        "ink', kw_only=False, fn=None), ReprPlan.Field(name='display_link', kw_only=False, fn=None), ReprPlan.Field(nam"
        "e='snippet', kw_only=False, fn=None), ReprPlan.Field(name='html_snippet', kw_only=False, fn=None), ReprPlan.Fi"
        "eld(name='cache_id', kw_only=False, fn=None), ReprPlan.Field(name='formatted_url', kw_only=False, fn=None), Re"
        "prPlan.Field(name='html_formatted_url', kw_only=False, fn=None), ReprPlan.Field(name='mime', kw_only=False, fn"
        "=None), ReprPlan.Field(name='file_format', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='9a7ab73f68edd197196f8d58344e8bb2b4962d7f',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__10__annotation',
        '__dataclass__init__fields__10__default',
        '__dataclass__init__fields__11__annotation',
        '__dataclass__init__fields__11__default',
        '__dataclass__init__fields__12__annotation',
        '__dataclass__init__fields__12__default',
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
        '__dataclass__init__fields__6__annotation',
        '__dataclass__init__fields__6__default',
        '__dataclass__init__fields__7__annotation',
        '__dataclass__init__fields__7__default',
        '__dataclass__init__fields__8__annotation',
        '__dataclass__init__fields__8__default',
        '__dataclass__init__fields__9__annotation',
        '__dataclass__init__fields__9__default',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.google.search', 'CseSearchResult'),
    ),
)
def _process_dataclass__9a7ab73f68edd197196f8d58344e8bb2b4962d7f():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__10__annotation,
        __dataclass__init__fields__10__default,
        __dataclass__init__fields__11__annotation,
        __dataclass__init__fields__11__default,
        __dataclass__init__fields__12__annotation,
        __dataclass__init__fields__12__default,
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
        __dataclass__init__fields__6__annotation,
        __dataclass__init__fields__6__default,
        __dataclass__init__fields__7__annotation,
        __dataclass__init__fields__7__default,
        __dataclass__init__fields__8__annotation,
        __dataclass__init__fields__8__default,
        __dataclass__init__fields__9__annotation,
        __dataclass__init__fields__9__default,
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
                kind=self.kind,
                title=self.title,
                html_title=self.html_title,
                link=self.link,
                display_link=self.display_link,
                snippet=self.snippet,
                html_snippet=self.html_snippet,
                cache_id=self.cache_id,
                formatted_url=self.formatted_url,
                html_formatted_url=self.html_formatted_url,
                mime=self.mime,
                file_format=self.file_format,
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
                self.kind == other.kind and
                self.title == other.title and
                self.html_title == other.html_title and
                self.link == other.link and
                self.display_link == other.display_link and
                self.snippet == other.snippet and
                self.html_snippet == other.html_snippet and
                self.cache_id == other.cache_id and
                self.formatted_url == other.formatted_url and
                self.html_formatted_url == other.html_formatted_url and
                self.mime == other.mime and
                self.file_format == other.file_format and
                self.x == other.x
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'kind',
            'title',
            'html_title',
            'link',
            'display_link',
            'snippet',
            'html_snippet',
            'cache_id',
            'formatted_url',
            'html_formatted_url',
            'mime',
            'file_format',
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
            'kind',
            'title',
            'html_title',
            'link',
            'display_link',
            'snippet',
            'html_snippet',
            'cache_id',
            'formatted_url',
            'html_formatted_url',
            'mime',
            'file_format',
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
                self.kind,
                self.title,
                self.html_title,
                self.link,
                self.display_link,
                self.snippet,
                self.html_snippet,
                self.cache_id,
                self.formatted_url,
                self.html_formatted_url,
                self.mime,
                self.file_format,
                self.x,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            kind: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            title: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            html_title: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            link: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            display_link: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            snippet: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
            html_snippet: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
            cache_id: __dataclass__init__fields__7__annotation = __dataclass__init__fields__7__default,
            formatted_url: __dataclass__init__fields__8__annotation = __dataclass__init__fields__8__default,
            html_formatted_url: __dataclass__init__fields__9__annotation = __dataclass__init__fields__9__default,
            mime: __dataclass__init__fields__10__annotation = __dataclass__init__fields__10__default,
            file_format: __dataclass__init__fields__11__annotation = __dataclass__init__fields__11__default,
            x: __dataclass__init__fields__12__annotation = __dataclass__init__fields__12__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'kind', kind)
            __dataclass__object_setattr(self, 'title', title)
            __dataclass__object_setattr(self, 'html_title', html_title)
            __dataclass__object_setattr(self, 'link', link)
            __dataclass__object_setattr(self, 'display_link', display_link)
            __dataclass__object_setattr(self, 'snippet', snippet)
            __dataclass__object_setattr(self, 'html_snippet', html_snippet)
            __dataclass__object_setattr(self, 'cache_id', cache_id)
            __dataclass__object_setattr(self, 'formatted_url', formatted_url)
            __dataclass__object_setattr(self, 'html_formatted_url', html_formatted_url)
            __dataclass__object_setattr(self, 'mime', mime)
            __dataclass__object_setattr(self, 'file_format', file_format)
            __dataclass__object_setattr(self, 'x', x)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"kind={self.kind!r}")
            parts.append(f"title={self.title!r}")
            parts.append(f"html_title={self.html_title!r}")
            parts.append(f"link={self.link!r}")
            parts.append(f"display_link={self.display_link!r}")
            parts.append(f"snippet={self.snippet!r}")
            parts.append(f"html_snippet={self.html_snippet!r}")
            parts.append(f"cache_id={self.cache_id!r}")
            parts.append(f"formatted_url={self.formatted_url!r}")
            parts.append(f"html_formatted_url={self.html_formatted_url!r}")
            parts.append(f"mime={self.mime!r}")
            parts.append(f"file_format={self.file_format!r}")
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
        "Plans(tup=(CopyPlan(fields=('v',)), EqPlan(fields=('v',)), FrozenPlan(fields=('v',), allow_dynamic_dunder_attr"
        "s=False), HashPlan(action='add', fields=('v',), cache=False), InitPlan(fields=(InitPlan.Field(name='v', annota"
        "tion=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, fi"
        "eld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self', std_params=('v"
        "',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPl"
        "an(fields=(ReprPlan.Field(name='v', kw_only=False, fn=OpRef(name='repr.fns.0.fn')),), id=False, terse=True, de"
        "fault_fn=None)))"
    ),
    plan_repr_sha1='663f7924a951e0a39befa6d9c0c541bbf2575506',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__repr__fns__0__fn',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.huggingface.configs', 'HuggingfaceHubToken'),
        ('ommlds.minichain.standard', 'ApiKey'),
    ),
)
def _process_dataclass__663f7924a951e0a39befa6d9c0c541bbf2575506():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__repr__fns__0__fn,
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
            return hash((
                self.v,
            ))

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
            if (s := __dataclass__repr__fns__0__fn(self.v)) is not None:
                parts.append(f"{s}")
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
        "Plans(tup=(CopyPlan(fields=('ms',)), EqPlan(fields=('ms',)), FrozenPlan(fields=('ms',), allow_dynamic_dunder_a"
        "ttrs=False), HashPlan(action='add', fields=('ms',), cache=False), InitPlan(fields=(InitPlan.Field(name='ms', a"
        "nnotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=Fals"
        "e, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self', std_param"
        "s=('ms',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), "
        "ReprPlan(fields=(ReprPlan.Field(name='ms', kw_only=False, fn=None),), id=False, terse=False, default_fn=None))"
        ")"
    ),
    plan_repr_sha1='8c235aee49850ebae268d668bebad09ed68eee50',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.mistral', 'AiChoice'),
    ),
)
def _process_dataclass__8c235aee49850ebae268d668bebad09ed68eee50():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                ms=self.ms,
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
                self.ms == other.ms
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'ms',
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
            'ms',
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
                self.ms,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            ms: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'ms', ms)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"ms={self.ms!r}")
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
        "Plans(tup=(CopyPlan(fields=('_metadata', 'c')), EqPlan(fields=('_metadata', 'c')), FrozenPlan(fields=('_metada"
        "ta', 'c'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('_metadata', 'c'), cache=False), "
        "InitPlan(fields=(InitPlan.Field(name='_metadata', annotation=OpRef(name='init.fields.0.annotation'), default=O"
        "pRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INST"
        "ANCE, coerce=OpRef(name='init.fields.0.coerce'), validate=None, check_type=None), InitPlan.Field(name='c', ann"
        "otation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=N"
        "one, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), "
        "self_param='self', std_params=('c',), kw_only_params=('_metadata',), frozen=True, slots=False, post_init_param"
        "s=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='c', kw_only=False, fn=OpRef(name="
        "'repr.fns.1.fn')),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='72c59dbd029af1f55a739e4e5f92cc62c0cecb75',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__coerce',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__repr__fns__1__fn',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.mistral', 'AiMessage'),
    ),
)
def _process_dataclass__72c59dbd029af1f55a739e4e5f92cc62c0cecb75():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__coerce,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__repr__fns__1__fn,
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
                _metadata=self._metadata,
                c=self.c,
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
                self._metadata == other._metadata and
                self.c == other.c
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '_metadata',
            'c',
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
            '_metadata',
            'c',
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
                self._metadata,
                self.c,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            c: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            *,
            _metadata: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            _metadata = __dataclass__init__fields__0__coerce(_metadata)
            __dataclass__object_setattr(self, '_metadata', _metadata)
            __dataclass__object_setattr(self, 'c', c)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__fns__1__fn(self.c)) is not None:
                parts.append(f"c={s}")
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
        "Plans(tup=(CopyPlan(fields=('_metadata',)), EqPlan(fields=('_metadata',)), FrozenPlan(fields=('_metadata',), a"
        "llow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('_metadata',), cache=False), InitPlan(fields="
        "(InitPlan.Field(name='_metadata', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init."
        "fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=OpR"
        "ef(name='init.fields.0.coerce'), validate=None, check_type=None),), self_param='self', std_params=(), kw_only_"
        "params=('_metadata',), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPla"
        "n(fields=(), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='9e1d955ccb433717c9538685d2a5ad412ce027f5',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__coerce',
        '__dataclass__init__fields__0__default',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.mistral', 'AnyAiMessage'),
        ('ommlds.minichain.backends.impls.mistral', 'AnyUserMessage'),
        ('ommlds.minichain.backends.impls.mistral', 'Message'),
    ),
)
def _process_dataclass__9e1d955ccb433717c9538685d2a5ad412ce027f5():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__coerce,
        __dataclass__init__fields__0__default,
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
                _metadata=self._metadata,
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
                self._metadata == other._metadata
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '_metadata',
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
            '_metadata',
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
                self._metadata,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            _metadata: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            _metadata = __dataclass__init__fields__0__coerce(_metadata)
            __dataclass__object_setattr(self, '_metadata', _metadata)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
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
        "Plans(tup=(CopyPlan(fields=('_metadata', 'l')), EqPlan(fields=('_metadata', 'l')), FrozenPlan(fields=('_metada"
        "ta', 'l'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('_metadata', 'l'), cache=False), "
        "InitPlan(fields=(InitPlan.Field(name='_metadata', annotation=OpRef(name='init.fields.0.annotation'), default=O"
        "pRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INST"
        "ANCE, coerce=OpRef(name='init.fields.0.coerce'), validate=None, check_type=None), InitPlan.Field(name='l', ann"
        "otation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False,"
        " field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=("
        "'l',), kw_only_params=('_metadata',), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_f"
        "ns=()), ReprPlan(fields=(ReprPlan.Field(name='_metadata', kw_only=True, fn=OpRef(name='repr.fns.0.fn')), ReprP"
        "lan.Field(name='l', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='281796d144299e91ab063fdfbfabe3f0e8e89f9d',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__coerce',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__repr__fns__0__fn',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.mistral', 'BlockContent'),
        ('ommlds.minichain.backends.impls.mistral', 'InlineContent'),
        ('ommlds.minichain.backends.impls.mistral', 'ItemListContent'),
        ('ommlds.minichain.backends.impls.mistral', 'SequenceContent'),
    ),
)
def _process_dataclass__281796d144299e91ab063fdfbfabe3f0e8e89f9d():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__coerce,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__repr__fns__0__fn,
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
                _metadata=self._metadata,
                l=self.l,
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
                self._metadata == other._metadata and
                self.l == other.l
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '_metadata',
            'l',
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
            '_metadata',
            'l',
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
                self._metadata,
                self.l,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            l: __dataclass__init__fields__1__annotation,
            *,
            _metadata: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            _metadata = __dataclass__init__fields__0__coerce(_metadata)
            __dataclass__object_setattr(self, '_metadata', _metadata)
            __dataclass__object_setattr(self, 'l', l)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__fns__0__fn(self._metadata)) is not None:
                parts.append(f"_metadata={s}")
            parts.append(f"l={self.l!r}")
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
        "Plans(tup=(CopyPlan(fields=('_metadata', 's', 'lang')), EqPlan(fields=('_metadata', 's', 'lang')), FrozenPlan("
        "fields=('_metadata', 's', 'lang'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('_metadat"
        "a', 's', 'lang'), cache=False), InitPlan(fields=(InitPlan.Field(name='_metadata', annotation=OpRef(name='init."
        "fields.0.annotation'), default=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override="
        "False, field_type=FieldType.INSTANCE, coerce=OpRef(name='init.fields.0.coerce'), validate=None, check_type=Non"
        "e), InitPlan.Field(name='s', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory="
        "None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), "
        "InitPlan.Field(name='lang', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields"
        ".2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, val"
        "idate=None, check_type=None)), self_param='self', std_params=('s',), kw_only_params=('_metadata', 'lang'), fro"
        "zen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(n"
        "ame='_metadata', kw_only=True, fn=OpRef(name='repr.fns.0.fn')), ReprPlan.Field(name='s', kw_only=False, fn=Non"
        "e), ReprPlan.Field(name='lang', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='9193db962fdc440396655ef40965237c763fe790',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__coerce',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__repr__fns__0__fn',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.mistral', 'CodeContent'),
    ),
)
def _process_dataclass__9193db962fdc440396655ef40965237c763fe790():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__coerce,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
        __dataclass__repr__fns__0__fn,
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
                _metadata=self._metadata,
                s=self.s,
                lang=self.lang,
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
                self._metadata == other._metadata and
                self.s == other.s and
                self.lang == other.lang
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '_metadata',
            's',
            'lang',
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
            '_metadata',
            's',
            'lang',
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
                self._metadata,
                self.s,
                self.lang,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            s: __dataclass__init__fields__1__annotation,
            *,
            _metadata: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            lang: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            _metadata = __dataclass__init__fields__0__coerce(_metadata)
            __dataclass__object_setattr(self, '_metadata', _metadata)
            __dataclass__object_setattr(self, 's', s)
            __dataclass__object_setattr(self, 'lang', lang)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__fns__0__fn(self._metadata)) is not None:
                parts.append(f"_metadata={s}")
            parts.append(f"s={self.s!r}")
            parts.append(f"lang={self.lang!r}")
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
        "Plans(tup=(CopyPlan(fields=('_metadata',)), EqPlan(fields=('_metadata',)), FrozenPlan(fields=('_metadata',), a"
        "llow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('_metadata',), cache=False), InitPlan(fields="
        "(InitPlan.Field(name='_metadata', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init."
        "fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=OpR"
        "ef(name='init.fields.0.coerce'), validate=None, check_type=None),), self_param='self', std_params=(), kw_only_"
        "params=('_metadata',), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPla"
        "n(fields=(ReprPlan.Field(name='_metadata', kw_only=True, fn=OpRef(name='repr.fns.0.fn')),), id=False, terse=Fa"
        "lse, default_fn=None)))"
    ),
    plan_repr_sha1='bcf6088fdeff32c671aa2e5e0810822079fcba71',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__coerce',
        '__dataclass__init__fields__0__default',
        '__dataclass__repr__fns__0__fn',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.mistral', 'DynamicContent'),
        ('ommlds.minichain.backends.impls.mistral', 'StandardContent'),
    ),
)
def _process_dataclass__bcf6088fdeff32c671aa2e5e0810822079fcba71():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__coerce,
        __dataclass__init__fields__0__default,
        __dataclass__repr__fns__0__fn,
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
                _metadata=self._metadata,
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
                self._metadata == other._metadata
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '_metadata',
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
            '_metadata',
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
                self._metadata,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            _metadata: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            _metadata = __dataclass__init__fields__0__coerce(_metadata)
            __dataclass__object_setattr(self, '_metadata', _metadata)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__fns__0__fn(self._metadata)) is not None:
                parts.append(f"_metadata={s}")
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
        "Plans(tup=(CopyPlan(fields=('type', 'values')), EqPlan(fields=('type', 'values')), FrozenPlan(fields=('type', "
        "'values'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('type', 'values'), cache=False), "
        "InitPlan(fields=(InitPlan.Field(name='type', annotation=OpRef(name='init.fields.0.annotation'), default=None, "
        "default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, ch"
        "eck_type=None), InitPlan.Field(name='values', annotation=OpRef(name='init.fields.1.annotation'), default=None,"
        " default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, c"
        "heck_type=None)), self_param='self', std_params=('type', 'values'), kw_only_params=(), frozen=True, slots=Fals"
        "e, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='type', kw_only="
        "False, fn=None), ReprPlan.Field(name='values', kw_only=False, fn=None)), id=False, terse=True, default_fn=None"
        ")))"
    ),
    plan_repr_sha1='922e75739507bda9dce73a0d3dc05534b1cc9ae5',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.mistral', 'EnumToolDtype'),
    ),
)
def _process_dataclass__922e75739507bda9dce73a0d3dc05534b1cc9ae5():
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
                type=self.type,
                values=self.values,
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
                self.values == other.values
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'type',
            'values',
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
            'values',
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
                self.values,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            type: __dataclass__init__fields__0__annotation,
            values: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'type', type)
            __dataclass__object_setattr(self, 'values', values)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"{self.type!r}")
            parts.append(f"{self.values!r}")
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
        "Plans(tup=(CopyPlan(fields=('_metadata', 'i')), EqPlan(fields=('_metadata', 'i')), FrozenPlan(fields=('_metada"
        "ta', 'i'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('_metadata', 'i'), cache=False), "
        "InitPlan(fields=(InitPlan.Field(name='_metadata', annotation=OpRef(name='init.fields.0.annotation'), default=O"
        "pRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INST"
        "ANCE, coerce=OpRef(name='init.fields.0.coerce'), validate=None, check_type=None), InitPlan.Field(name='i', ann"
        "otation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False,"
        " field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=("
        "'i',), kw_only_params=('_metadata',), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_f"
        "ns=()), ReprPlan(fields=(ReprPlan.Field(name='_metadata', kw_only=True, fn=OpRef(name='repr.fns.0.fn')), ReprP"
        "lan.Field(name='i', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='9e4a59d711dc872608ff0daa695c75db9383f39a',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__coerce',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__repr__fns__0__fn',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.mistral', 'ImageContent'),
    ),
)
def _process_dataclass__9e4a59d711dc872608ff0daa695c75db9383f39a():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__coerce,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__repr__fns__0__fn,
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
                _metadata=self._metadata,
                i=self.i,
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
                self._metadata == other._metadata and
                self.i == other.i
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '_metadata',
            'i',
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
            '_metadata',
            'i',
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
                self._metadata,
                self.i,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            i: __dataclass__init__fields__1__annotation,
            *,
            _metadata: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            _metadata = __dataclass__init__fields__0__coerce(_metadata)
            __dataclass__object_setattr(self, '_metadata', _metadata)
            __dataclass__object_setattr(self, 'i', i)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__fns__0__fn(self._metadata)) is not None:
                parts.append(f"_metadata={s}")
            parts.append(f"i={self.i!r}")
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
        "Plans(tup=(CopyPlan(fields=('_metadata', 'v')), EqPlan(fields=('_metadata', 'v')), FrozenPlan(fields=('_metada"
        "ta', 'v'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('_metadata', 'v'), cache=False), "
        "InitPlan(fields=(InitPlan.Field(name='_metadata', annotation=OpRef(name='init.fields.0.annotation'), default=O"
        "pRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INST"
        "ANCE, coerce=OpRef(name='init.fields.0.coerce'), validate=None, check_type=None), InitPlan.Field(name='v', ann"
        "otation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False,"
        " field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=("
        "'v',), kw_only_params=('_metadata',), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_f"
        "ns=()), ReprPlan(fields=(ReprPlan.Field(name='_metadata', kw_only=True, fn=OpRef(name='repr.fns.0.fn')), ReprP"
        "lan.Field(name='v', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='296d7a1dff0c5084e83cbfd2ddd0e7460f1ea2c0',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__coerce',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__repr__fns__0__fn',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.mistral', 'JsonContent'),
    ),
)
def _process_dataclass__296d7a1dff0c5084e83cbfd2ddd0e7460f1ea2c0():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__coerce,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__repr__fns__0__fn,
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
                _metadata=self._metadata,
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
                self._metadata == other._metadata and
                self.v == other.v
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '_metadata',
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
            '_metadata',
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
            return hash((
                self._metadata,
                self.v,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            v: __dataclass__init__fields__1__annotation,
            *,
            _metadata: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            _metadata = __dataclass__init__fields__0__coerce(_metadata)
            __dataclass__object_setattr(self, '_metadata', _metadata)
            __dataclass__object_setattr(self, 'v', v)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__fns__0__fn(self._metadata)) is not None:
                parts.append(f"_metadata={s}")
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

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('key', 'value')), EqPlan(fields=('key', 'value')), FrozenPlan(fields=('key', 'valu"
        "e'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('key', 'value'), cache=False), InitPlan"
        "(fields=(InitPlan.Field(name='key', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_f"
        "actory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type="
        "None), InitPlan.Field(name='value', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_f"
        "actory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type="
        "None)), self_param='self', std_params=('key', 'value'), kw_only_params=(), frozen=True, slots=False, post_init"
        "_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='key', kw_only=False, fn=Non"
        "e), ReprPlan.Field(name='value', kw_only=False, fn=None)), id=False, terse=True, default_fn=None)))"
    ),
    plan_repr_sha1='2ded8afb50edd07329da6b7055981919a83dec56',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.mistral', 'MappingToolDtype'),
    ),
)
def _process_dataclass__2ded8afb50edd07329da6b7055981919a83dec56():
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
                key=self.key,
                value=self.value,
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
                self.value == other.value
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'key',
            'value',
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
            'value',
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
                self.key,
                self.value,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            key: __dataclass__init__fields__0__annotation,
            value: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'key', key)
            __dataclass__object_setattr(self, 'value', value)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"{self.key!r}")
            parts.append(f"{self.value!r}")
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
        "Plans(tup=(CopyPlan(fields=('type',)), EqPlan(fields=('type',)), FrozenPlan(fields=('type',), allow_dynamic_du"
        "nder_attrs=False), HashPlan(action='add', fields=('type',), cache=False), InitPlan(fields=(InitPlan.Field(name"
        "='type', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, ove"
        "rride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self',"
        " std_params=('type',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), valida"
        "te_fns=()), ReprPlan(fields=(ReprPlan.Field(name='type', kw_only=False, fn=None),), id=False, terse=True, defa"
        "ult_fn=None)))"
    ),
    plan_repr_sha1='1d0b04d8ebb0bdb077bc9721fb19aafcadf99422',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.mistral', 'NullableToolDtype'),
    ),
)
def _process_dataclass__1d0b04d8ebb0bdb077bc9721fb19aafcadf99422():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                self.type == other.type
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'type',
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
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            type: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'type', type)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"{self.type!r}")
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
        "Plans(tup=(CopyPlan(fields=('fields',)), EqPlan(fields=('fields',)), FrozenPlan(fields=('fields',), allow_dyna"
        "mic_dunder_attrs=False), HashPlan(action='add', fields=('fields',), cache=False), InitPlan(fields=(InitPlan.Fi"
        "eld(name='fields', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init"
        "=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_par"
        "am='self', std_params=('fields',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fn"
        "s=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='fields', kw_only=False, fn=None),), id=False, te"
        "rse=True, default_fn=None)))"
    ),
    plan_repr_sha1='178374af8c25e44a33c44ece98db0c96fe041247',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.mistral', 'ObjectToolDtype'),
    ),
)
def _process_dataclass__178374af8c25e44a33c44ece98db0c96fe041247():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                fields=self.fields,
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
                self.fields == other.fields
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'fields',
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
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            fields: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'fields', fields)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"{self.fields!r}")
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
        "Plans(tup=(CopyPlan(fields=('type',)), EqPlan(fields=('type',)), FrozenPlan(fields=('type',), allow_dynamic_du"
        "nder_attrs=False), HashPlan(action='add', fields=('type',), cache=False), InitPlan(fields=(InitPlan.Field(name"
        "='type', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, ove"
        "rride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self',"
        " std_params=('type',), kw_only_params=(), frozen=True, slots=False, post_init_params=(), init_fns=(), validate"
        "_fns=()), ReprPlan(fields=(ReprPlan.Field(name='type', kw_only=False, fn=None),), id=False, terse=True, defaul"
        "t_fn=None)))"
    ),
    plan_repr_sha1='b7657835eed1f3e17dbdae82eb197181dd5862db',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.mistral', 'PrimitiveToolDtype'),
    ),
)
def _process_dataclass__b7657835eed1f3e17dbdae82eb197181dd5862db():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                self.type == other.type
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'type',
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
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            type: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'type', type)
            self.__post_init__()

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"{self.type!r}")
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
        "Plans(tup=(CopyPlan(fields=('_metadata', 'body')), EqPlan(fields=('_metadata', 'body')), FrozenPlan(fields=('_"
        "metadata', 'body'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('_metadata', 'body'), ca"
        "che=False), InitPlan(fields=(InitPlan.Field(name='_metadata', annotation=OpRef(name='init.fields.0.annotation'"
        "), default=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=Fi"
        "eldType.INSTANCE, coerce=OpRef(name='init.fields.0.coerce'), validate=None, check_type=None), InitPlan.Field(n"
        "ame='body', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, "
        "override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self"
        "', std_params=('body',), kw_only_params=('_metadata',), frozen=True, slots=False, post_init_params=None, init_"
        "fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='_metadata', kw_only=True, fn=OpRef(name='repr."
        "fns.0.fn')), ReprPlan.Field(name='body', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='613cd3748f4063b004e2ac171fbf7e4248333e6b',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__coerce',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__repr__fns__0__fn',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.mistral', 'QuoteContent'),
    ),
)
def _process_dataclass__613cd3748f4063b004e2ac171fbf7e4248333e6b():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__coerce,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__repr__fns__0__fn,
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
                _metadata=self._metadata,
                body=self.body,
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
                self._metadata == other._metadata and
                self.body == other.body
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '_metadata',
            'body',
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
            '_metadata',
            'body',
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
                self._metadata,
                self.body,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            body: __dataclass__init__fields__1__annotation,
            *,
            _metadata: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            _metadata = __dataclass__init__fields__0__coerce(_metadata)
            __dataclass__object_setattr(self, '_metadata', _metadata)
            __dataclass__object_setattr(self, 'body', body)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__fns__0__fn(self._metadata)) is not None:
                parts.append(f"_metadata={s}")
            parts.append(f"body={self.body!r}")
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
        "Plans(tup=(CopyPlan(fields=('_metadata', 'header', 'body')), EqPlan(fields=('_metadata', 'header', 'body')), F"
        "rozenPlan(fields=('_metadata', 'header', 'body'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fi"
        "elds=('_metadata', 'header', 'body'), cache=False), InitPlan(fields=(InitPlan.Field(name='_metadata', annotati"
        "on=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'), default_factory=None, "
        "init=True, override=False, field_type=FieldType.INSTANCE, coerce=OpRef(name='init.fields.0.coerce'), validate="
        "None, check_type=None), InitPlan.Field(name='header', annotation=OpRef(name='init.fields.1.annotation'), defau"
        "lt=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate"
        "=None, check_type=None), InitPlan.Field(name='body', annotation=OpRef(name='init.fields.2.annotation'), defaul"
        "t=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate="
        "None, check_type=None)), self_param='self', std_params=('header', 'body'), kw_only_params=('_metadata',), froz"
        "en=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(na"
        "me='_metadata', kw_only=True, fn=OpRef(name='repr.fns.0.fn')), ReprPlan.Field(name='header', kw_only=False, fn"
        "=None), ReprPlan.Field(name='body', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='0fa4877e6cac6410b1b210697166cb95c606490e',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__coerce',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__repr__fns__0__fn',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.mistral', 'SectionContent'),
    ),
)
def _process_dataclass__0fa4877e6cac6410b1b210697166cb95c606490e():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__coerce,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__repr__fns__0__fn,
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
                _metadata=self._metadata,
                header=self.header,
                body=self.body,
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
                self._metadata == other._metadata and
                self.header == other.header and
                self.body == other.body
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '_metadata',
            'header',
            'body',
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
            '_metadata',
            'header',
            'body',
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
                self._metadata,
                self.header,
                self.body,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            header: __dataclass__init__fields__1__annotation,
            body: __dataclass__init__fields__2__annotation,
            *,
            _metadata: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            _metadata = __dataclass__init__fields__0__coerce(_metadata)
            __dataclass__object_setattr(self, '_metadata', _metadata)
            __dataclass__object_setattr(self, 'header', header)
            __dataclass__object_setattr(self, 'body', body)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__fns__0__fn(self._metadata)) is not None:
                parts.append(f"_metadata={s}")
            parts.append(f"header={self.header!r}")
            parts.append(f"body={self.body!r}")
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
        "Plans(tup=(CopyPlan(fields=('element',)), EqPlan(fields=('element',)), FrozenPlan(fields=('element',), allow_d"
        "ynamic_dunder_attrs=False), HashPlan(action='add', fields=('element',), cache=False), InitPlan(fields=(InitPla"
        "n.Field(name='element', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None,"
        " init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), sel"
        "f_param='self', std_params=('element',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, i"
        "nit_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='element', kw_only=False, fn=None),), id=Fa"
        "lse, terse=True, default_fn=None)))"
    ),
    plan_repr_sha1='95d65e05398b42908ba7d67d961be3c1dae7f5b4',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.mistral', 'SequenceToolDtype'),
    ),
)
def _process_dataclass__95d65e05398b42908ba7d67d961be3c1dae7f5b4():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                element=self.element,
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
                self.element == other.element
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'element',
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
            'element',
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
                self.element,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            element: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'element', element)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"{self.element!r}")
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
        "Plans(tup=(CopyPlan(fields=('_metadata', 'c')), EqPlan(fields=('_metadata', 'c')), FrozenPlan(fields=('_metada"
        "ta', 'c'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('_metadata', 'c'), cache=False), "
        "InitPlan(fields=(InitPlan.Field(name='_metadata', annotation=OpRef(name='init.fields.0.annotation'), default=O"
        "pRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INST"
        "ANCE, coerce=OpRef(name='init.fields.0.coerce'), validate=None, check_type=None), InitPlan.Field(name='c', ann"
        "otation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False,"
        " field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=("
        "'c',), kw_only_params=('_metadata',), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_f"
        "ns=()), ReprPlan(fields=(ReprPlan.Field(name='c', kw_only=False, fn=None),), id=False, terse=False, default_fn"
        "=None)))"
    ),
    plan_repr_sha1='5cf06a8666aafbd9f13b7cc116ca35266a2043de',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__coerce',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.mistral', 'SystemMessage'),
    ),
)
def _process_dataclass__5cf06a8666aafbd9f13b7cc116ca35266a2043de():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__coerce,
        __dataclass__init__fields__0__default,
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
                _metadata=self._metadata,
                c=self.c,
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
                self._metadata == other._metadata and
                self.c == other.c
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '_metadata',
            'c',
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
            '_metadata',
            'c',
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
                self._metadata,
                self.c,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            c: __dataclass__init__fields__1__annotation,
            *,
            _metadata: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            _metadata = __dataclass__init__fields__0__coerce(_metadata)
            __dataclass__object_setattr(self, '_metadata', _metadata)
            __dataclass__object_setattr(self, 'c', c)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"c={self.c!r}")
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
        "Plans(tup=(CopyPlan(fields=('_metadata', 'tag', 'body')), EqPlan(fields=('_metadata', 'tag', 'body')), FrozenP"
        "lan(fields=('_metadata', 'tag', 'body'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('_m"
        "etadata', 'tag', 'body'), cache=False), InitPlan(fields=(InitPlan.Field(name='_metadata', annotation=OpRef(nam"
        "e='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'), default_factory=None, init=True, o"
        "verride=False, field_type=FieldType.INSTANCE, coerce=OpRef(name='init.fields.0.coerce'), validate=None, check_"
        "type=None), InitPlan.Field(name='tag', annotation=OpRef(name='init.fields.1.annotation'), default=None, defaul"
        "t_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_ty"
        "pe=None), InitPlan.Field(name='body', annotation=OpRef(name='init.fields.2.annotation'), default=None, default"
        "_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_typ"
        "e=None)), self_param='self', std_params=('tag', 'body'), kw_only_params=('_metadata',), frozen=True, slots=Fal"
        "se, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='_metadata', kw"
        "_only=True, fn=OpRef(name='repr.fns.0.fn')), ReprPlan.Field(name='tag', kw_only=False, fn=None), ReprPlan.Fiel"
        "d(name='body', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='3cebe4c45faf434543bef35bc54753b0efb48327',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__coerce',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__repr__fns__0__fn',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.mistral', 'TagContent'),
    ),
)
def _process_dataclass__3cebe4c45faf434543bef35bc54753b0efb48327():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__coerce,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__repr__fns__0__fn,
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
                _metadata=self._metadata,
                tag=self.tag,
                body=self.body,
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
                self._metadata == other._metadata and
                self.tag == other.tag and
                self.body == other.body
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '_metadata',
            'tag',
            'body',
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
            '_metadata',
            'tag',
            'body',
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
                self._metadata,
                self.tag,
                self.body,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            tag: __dataclass__init__fields__1__annotation,
            body: __dataclass__init__fields__2__annotation,
            *,
            _metadata: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            _metadata = __dataclass__init__fields__0__coerce(_metadata)
            __dataclass__object_setattr(self, '_metadata', _metadata)
            __dataclass__object_setattr(self, 'tag', tag)
            __dataclass__object_setattr(self, 'body', body)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__fns__0__fn(self._metadata)) is not None:
                parts.append(f"_metadata={s}")
            parts.append(f"tag={self.tag!r}")
            parts.append(f"body={self.body!r}")
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
        "Plans(tup=(CopyPlan(fields=('_metadata', 't')), EqPlan(fields=('_metadata', 't')), FrozenPlan(fields=('_metada"
        "ta', 't'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('_metadata', 't'), cache=False), "
        "InitPlan(fields=(InitPlan.Field(name='_metadata', annotation=OpRef(name='init.fields.0.annotation'), default=O"
        "pRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INST"
        "ANCE, coerce=OpRef(name='init.fields.0.coerce'), validate=None, check_type=None), InitPlan.Field(name='t', ann"
        "otation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False,"
        " field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=("
        "'t',), kw_only_params=('_metadata',), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_f"
        "ns=()), ReprPlan(fields=(ReprPlan.Field(name='_metadata', kw_only=True, fn=OpRef(name='repr.fns.0.fn')), ReprP"
        "lan.Field(name='t', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='484b69d9acddc84ab225a2e06f4ed574a339e353',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__coerce',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__repr__fns__0__fn',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.mistral', 'TemplateContent'),
    ),
)
def _process_dataclass__484b69d9acddc84ab225a2e06f4ed574a339e353():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__coerce,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__repr__fns__0__fn,
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
                _metadata=self._metadata,
                t=self.t,
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
                self._metadata == other._metadata and
                self.t == other.t
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '_metadata',
            't',
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
            '_metadata',
            't',
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
                self._metadata,
                self.t,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            t: __dataclass__init__fields__1__annotation,
            *,
            _metadata: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            _metadata = __dataclass__init__fields__0__coerce(_metadata)
            __dataclass__object_setattr(self, '_metadata', _metadata)
            __dataclass__object_setattr(self, 't', t)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__fns__0__fn(self._metadata)) is not None:
                parts.append(f"_metadata={s}")
            parts.append(f"t={self.t!r}")
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
        "Plans(tup=(CopyPlan(fields=('_metadata', 's')), EqPlan(fields=('_metadata', 's')), FrozenPlan(fields=('_metada"
        "ta', 's'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('_metadata', 's'), cache=False), "
        "InitPlan(fields=(InitPlan.Field(name='_metadata', annotation=OpRef(name='init.fields.0.annotation'), default=O"
        "pRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INST"
        "ANCE, coerce=OpRef(name='init.fields.0.coerce'), validate=None, check_type=None), InitPlan.Field(name='s', ann"
        "otation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False,"
        " field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=("
        "'s',), kw_only_params=('_metadata',), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_f"
        "ns=()), ReprPlan(fields=(ReprPlan.Field(name='_metadata', kw_only=True, fn=OpRef(name='repr.fns.0.fn')), ReprP"
        "lan.Field(name='s', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='f723863afd85d55cffe70bb94e882a00fd581c11',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__coerce',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__repr__fns__0__fn',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.mistral', 'TextContent'),
    ),
)
def _process_dataclass__f723863afd85d55cffe70bb94e882a00fd581c11():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__coerce,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__repr__fns__0__fn,
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
                _metadata=self._metadata,
                s=self.s,
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
                self._metadata == other._metadata and
                self.s == other.s
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '_metadata',
            's',
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
            '_metadata',
            's',
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
                self._metadata,
                self.s,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            s: __dataclass__init__fields__1__annotation,
            *,
            _metadata: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            _metadata = __dataclass__init__fields__0__coerce(_metadata)
            __dataclass__object_setattr(self, '_metadata', _metadata)
            __dataclass__object_setattr(self, 's', s)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__fns__0__fn(self._metadata)) is not None:
                parts.append(f"_metadata={s}")
            parts.append(f"s={self.s!r}")
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
        "Plans(tup=(CopyPlan(fields=('name', 'desc', 'type', 'required')), EqPlan(fields=('name', 'desc', 'type', 'requ"
        "ired')), FrozenPlan(fields=('name', 'desc', 'type', 'required'), allow_dynamic_dunder_attrs=False), HashPlan(a"
        "ction='add', fields=('name', 'desc', 'type', 'required'), cache=False), InitPlan(fields=(InitPlan.Field(name='"
        "name', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'), default"
        "_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_typ"
        "e=None), InitPlan.Field(name='desc', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='in"
        "it.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce="
        "None, validate=None, check_type=None), InitPlan.Field(name='type', annotation=OpRef(name='init.fields.2.annota"
        "tion'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_ty"
        "pe=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='required', annotatio"
        "n=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, i"
        "nit=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_p"
        "aram='self', std_params=('name',), kw_only_params=('desc', 'type', 'required'), frozen=True, slots=False, post"
        "_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='name', kw_only=False, "
        "fn=None), ReprPlan.Field(name='desc', kw_only=True, fn=None), ReprPlan.Field(name='type', kw_only=True, fn=Non"
        "e), ReprPlan.Field(name='required', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='69f075887b34fec02953259b40566b486cb54f44',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.mistral', 'ToolParam'),
    ),
)
def _process_dataclass__69f075887b34fec02953259b40566b486cb54f44():
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
                desc=self.desc,
                type=self.type,
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
                self.name == other.name and
                self.desc == other.desc and
                self.type == other.type and
                self.required == other.required
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'name',
            'desc',
            'type',
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
            'name',
            'desc',
            'type',
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
                self.name,
                self.desc,
                self.type,
                self.required,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            name: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            *,
            desc: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            type: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            required: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'desc', desc)
            __dataclass__object_setattr(self, 'type', type)
            __dataclass__object_setattr(self, 'required', required)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"name={self.name!r}")
            parts.append(f"desc={self.desc!r}")
            parts.append(f"type={self.type!r}")
            parts.append(f"required={self.required!r}")
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
        "Plans(tup=(CopyPlan(fields=('name', 'desc', 'params', 'allow_additional_params', 'returns_desc', 'returns_type"
        "')), EqPlan(fields=('name', 'desc', 'params', 'allow_additional_params', 'returns_desc', 'returns_type')), Fro"
        "zenPlan(fields=('name', 'desc', 'params', 'allow_additional_params', 'returns_desc', 'returns_type'), allow_dy"
        "namic_dunder_attrs=False), HashPlan(action='add', fields=('name', 'desc', 'params', 'allow_additional_params',"
        " 'returns_desc', 'returns_type'), cache=False), InitPlan(fields=(InitPlan.Field(name='name', annotation=OpRef("
        "name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'), default_factory=None, init=True"
        ", override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field("
        "name='desc', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), d"
        "efault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, che"
        "ck_type=None), InitPlan.Field(name='params', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef("
        "name='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE,"
        " coerce=None, validate=None, check_type=None), InitPlan.Field(name='allow_additional_params', annotation=OpRef"
        "(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=Tru"
        "e, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field"
        "(name='returns_desc', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.def"
        "ault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate="
        "None, check_type=None), InitPlan.Field(name='returns_type', annotation=OpRef(name='init.fields.5.annotation'),"
        " default=OpRef(name='init.fields.5.default'), default_factory=None, init=True, override=False, field_type=Fiel"
        "dType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=('name',), kw_onl"
        "y_params=('desc', 'params', 'allow_additional_params', 'returns_desc', 'returns_type'), frozen=True, slots=Fal"
        "se, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='name', kw_only"
        "=False, fn=None), ReprPlan.Field(name='desc', kw_only=True, fn=None), ReprPlan.Field(name='params', kw_only=Tr"
        "ue, fn=None), ReprPlan.Field(name='allow_additional_params', kw_only=True, fn=None), ReprPlan.Field(name='retu"
        "rns_desc', kw_only=True, fn=None), ReprPlan.Field(name='returns_type', kw_only=True, fn=None)), id=False, ters"
        "e=False, default_fn=None)))"
    ),
    plan_repr_sha1='cdcccf0dc59860c0b19fed181a5bb59b8472bf93',
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
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.mistral', 'ToolSpec'),
        ('ommlds.minichain.lib.bash', '_ToolSpecAttach'),
        ('ommlds.minichain.lib.bash', '_ToolSpecOverride'),
    ),
)
def _process_dataclass__cdcccf0dc59860c0b19fed181a5bb59b8472bf93():
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
                desc=self.desc,
                params=self.params,
                allow_additional_params=self.allow_additional_params,
                returns_desc=self.returns_desc,
                returns_type=self.returns_type,
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
                self.desc == other.desc and
                self.params == other.params and
                self.allow_additional_params == other.allow_additional_params and
                self.returns_desc == other.returns_desc and
                self.returns_type == other.returns_type
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'name',
            'desc',
            'params',
            'allow_additional_params',
            'returns_desc',
            'returns_type',
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
            'desc',
            'params',
            'allow_additional_params',
            'returns_desc',
            'returns_type',
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
                self.desc,
                self.params,
                self.allow_additional_params,
                self.returns_desc,
                self.returns_type,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            name: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            *,
            desc: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            params: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            allow_additional_params: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            returns_desc: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            returns_type: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'desc', desc)
            __dataclass__object_setattr(self, 'params', params)
            __dataclass__object_setattr(self, 'allow_additional_params', allow_additional_params)
            __dataclass__object_setattr(self, 'returns_desc', returns_desc)
            __dataclass__object_setattr(self, 'returns_type', returns_type)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"name={self.name!r}")
            parts.append(f"desc={self.desc!r}")
            parts.append(f"params={self.params!r}")
            parts.append(f"allow_additional_params={self.allow_additional_params!r}")
            parts.append(f"returns_desc={self.returns_desc!r}")
            parts.append(f"returns_type={self.returns_type!r}")
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
        "Plans(tup=(CopyPlan(fields=('id', 'name', 'args', 'raw_args')), EqPlan(fields=('id', 'name', 'args', 'raw_args"
        "')), FrozenPlan(fields=('id', 'name', 'args', 'raw_args'), allow_dynamic_dunder_attrs=False), HashPlan(action="
        "'add', fields=('id', 'name', 'args', 'raw_args'), cache=False), InitPlan(fields=(InitPlan.Field(name='id', ann"
        "otation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'), default_factory=N"
        "one, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), I"
        "nitPlan.Field(name='name', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=No"
        "ne, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), In"
        "itPlan.Field(name='args', annotation=OpRef(name='init.fields.2.annotation'), default=None, default_factory=Non"
        "e, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), Ini"
        "tPlan.Field(name='raw_args', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.field"
        "s.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, va"
        "lidate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('id', 'name', 'args', 'raw_a"
        "rgs'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPl"
        "an.Field(name='id', kw_only=True, fn=None), ReprPlan.Field(name='name', kw_only=True, fn=None), ReprPlan.Field"
        "(name='args', kw_only=True, fn=None), ReprPlan.Field(name='raw_args', kw_only=True, fn=None)), id=False, terse"
        "=False, default_fn=None)))"
    ),
    plan_repr_sha1='4ed08c576fd7794679f9215d6bdcdce02d3f7c85',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.mistral', 'ToolUse'),
    ),
)
def _process_dataclass__4ed08c576fd7794679f9215d6bdcdce02d3f7c85():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__3__default,
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
                id=self.id,
                name=self.name,
                args=self.args,
                raw_args=self.raw_args,
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
                self.id == other.id and
                self.name == other.name and
                self.args == other.args and
                self.raw_args == other.raw_args
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'id',
            'name',
            'args',
            'raw_args',
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
            'name',
            'args',
            'raw_args',
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
                self.name,
                self.args,
                self.raw_args,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            id: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            name: __dataclass__init__fields__1__annotation,
            args: __dataclass__init__fields__2__annotation,
            raw_args: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'args', args)
            __dataclass__object_setattr(self, 'raw_args', raw_args)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"id={self.id!r}")
            parts.append(f"name={self.name!r}")
            parts.append(f"args={self.args!r}")
            parts.append(f"raw_args={self.raw_args!r}")
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
        "Plans(tup=(CopyPlan(fields=('_metadata', 'tu')), EqPlan(fields=('_metadata', 'tu')), FrozenPlan(fields=('_meta"
        "data', 'tu'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('_metadata', 'tu'), cache=Fals"
        "e), InitPlan(fields=(InitPlan.Field(name='_metadata', annotation=OpRef(name='init.fields.0.annotation'), defau"
        "lt=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType."
        "INSTANCE, coerce=OpRef(name='init.fields.0.coerce'), validate=None, check_type=None), InitPlan.Field(name='tu'"
        ", annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=F"
        "alse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_par"
        "ams=('tu',), kw_only_params=('_metadata',), frozen=True, slots=False, post_init_params=None, init_fns=(), vali"
        "date_fns=()), ReprPlan(fields=(ReprPlan.Field(name='tu', kw_only=False, fn=None),), id=False, terse=False, def"
        "ault_fn=None)))"
    ),
    plan_repr_sha1='57a136cad7298612bd491ff2d62b9ce882a7bcb7',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__coerce',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.mistral', 'ToolUseMessage'),
    ),
)
def _process_dataclass__57a136cad7298612bd491ff2d62b9ce882a7bcb7():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__coerce,
        __dataclass__init__fields__0__default,
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
                _metadata=self._metadata,
                tu=self.tu,
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
                self._metadata == other._metadata and
                self.tu == other.tu
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '_metadata',
            'tu',
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
            '_metadata',
            'tu',
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
                self._metadata,
                self.tu,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            tu: __dataclass__init__fields__1__annotation,
            *,
            _metadata: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            _metadata = __dataclass__init__fields__0__coerce(_metadata)
            __dataclass__object_setattr(self, '_metadata', _metadata)
            __dataclass__object_setattr(self, 'tu', tu)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"tu={self.tu!r}")
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
        "Plans(tup=(CopyPlan(fields=('id', 'name', 'c')), EqPlan(fields=('id', 'name', 'c')), FrozenPlan(fields=('id', "
        "'name', 'c'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('id', 'name', 'c'), cache=Fals"
        "e), InitPlan(fields=(InitPlan.Field(name='id', annotation=OpRef(name='init.fields.0.annotation'), default=OpRe"
        "f(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANC"
        "E, coerce=None, validate=None, check_type=None), InitPlan.Field(name='name', annotation=OpRef(name='init.field"
        "s.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE"
        ", coerce=None, validate=None, check_type=None), InitPlan.Field(name='c', annotation=OpRef(name='init.fields.2."
        "annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, co"
        "erce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('id', 'name', '"
        "c'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan"
        ".Field(name='id', kw_only=True, fn=None), ReprPlan.Field(name='name', kw_only=True, fn=None), ReprPlan.Field(n"
        "ame='c', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='63faf3c00ff50c28af3c47a1c0100980c46a8e31',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.mistral', 'ToolUseResult'),
    ),
)
def _process_dataclass__63faf3c00ff50c28af3c47a1c0100980c46a8e31():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
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
                id=self.id,
                name=self.name,
                c=self.c,
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
                self.id == other.id and
                self.name == other.name and
                self.c == other.c
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'id',
            'name',
            'c',
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
            'name',
            'c',
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
                self.name,
                self.c,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            id: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            name: __dataclass__init__fields__1__annotation,
            c: __dataclass__init__fields__2__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'c', c)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"id={self.id!r}")
            parts.append(f"name={self.name!r}")
            parts.append(f"c={self.c!r}")
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
        "Plans(tup=(CopyPlan(fields=('_metadata', 'tur')), EqPlan(fields=('_metadata', 'tur')), FrozenPlan(fields=('_me"
        "tadata', 'tur'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('_metadata', 'tur'), cache="
        "False), InitPlan(fields=(InitPlan.Field(name='_metadata', annotation=OpRef(name='init.fields.0.annotation'), d"
        "efault=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldT"
        "ype.INSTANCE, coerce=OpRef(name='init.fields.0.coerce'), validate=None, check_type=None), InitPlan.Field(name="
        "'tur', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, overr"
        "ide=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', st"
        "d_params=('tur',), kw_only_params=('_metadata',), frozen=True, slots=False, post_init_params=None, init_fns=()"
        ", validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='tur', kw_only=False, fn=None),), id=False, terse=Fal"
        "se, default_fn=None)))"
    ),
    plan_repr_sha1='2485750c5fdb59d4b773884ec150101aee4ccdce',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__coerce',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.mistral', 'ToolUseResultMessage'),
    ),
)
def _process_dataclass__2485750c5fdb59d4b773884ec150101aee4ccdce():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__coerce,
        __dataclass__init__fields__0__default,
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
                _metadata=self._metadata,
                tur=self.tur,
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
                self._metadata == other._metadata and
                self.tur == other.tur
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '_metadata',
            'tur',
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
            '_metadata',
            'tur',
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
                self._metadata,
                self.tur,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            tur: __dataclass__init__fields__1__annotation,
            *,
            _metadata: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            _metadata = __dataclass__init__fields__0__coerce(_metadata)
            __dataclass__object_setattr(self, '_metadata', _metadata)
            __dataclass__object_setattr(self, 'tur', tur)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"tur={self.tur!r}")
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
        "Plans(tup=(CopyPlan(fields=('elements',)), EqPlan(fields=('elements',)), FrozenPlan(fields=('elements',), allo"
        "w_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('elements',), cache=False), InitPlan(fields=(Ini"
        "tPlan.Field(name='elements', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory="
        "None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),)"
        ", self_param='self', std_params=('elements',), kw_only_params=(), frozen=True, slots=False, post_init_params=N"
        "one, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='elements', kw_only=False, fn=None),)"
        ", id=False, terse=True, default_fn=None)))"
    ),
    plan_repr_sha1='a72c7b37c724624d1543d1cc8dffce6fcbbad416',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.mistral', 'TupleToolDtype'),
    ),
)
def _process_dataclass__a72c7b37c724624d1543d1cc8dffce6fcbbad416():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
            return hash((
                self.elements,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            elements: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'elements', elements)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"{self.elements!r}")
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
        "Plans(tup=(CopyPlan(fields=('args',)), EqPlan(fields=('args',)), FrozenPlan(fields=('args',), allow_dynamic_du"
        "nder_attrs=False), HashPlan(action='add', fields=('args',), cache=False), InitPlan(fields=(InitPlan.Field(name"
        "='args', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, ove"
        "rride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self',"
        " std_params=('args',), kw_only_params=(), frozen=True, slots=False, post_init_params=(), init_fns=(), validate"
        "_fns=()), ReprPlan(fields=(ReprPlan.Field(name='args', kw_only=False, fn=None),), id=False, terse=True, defaul"
        "t_fn=None)))"
    ),
    plan_repr_sha1='ad919be3aed733ce0d02ac2f6d4c55bbced3d288',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.mistral', 'UnionToolDtype'),
    ),
)
def _process_dataclass__ad919be3aed733ce0d02ac2f6d4c55bbced3d288():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                args=self.args,
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
                self.args == other.args
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'args',
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
            'args',
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
                self.args,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            args: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'args', args)
            self.__post_init__()

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"{self.args!r}")
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
        "Plans(tup=(CopyPlan(fields=('_metadata', 'c', 'name')), EqPlan(fields=('_metadata', 'c', 'name')), FrozenPlan("
        "fields=('_metadata', 'c', 'name'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('_metadat"
        "a', 'c', 'name'), cache=False), InitPlan(fields=(InitPlan.Field(name='_metadata', annotation=OpRef(name='init."
        "fields.0.annotation'), default=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override="
        "False, field_type=FieldType.INSTANCE, coerce=OpRef(name='init.fields.0.coerce'), validate=None, check_type=Non"
        "e), InitPlan.Field(name='c', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory="
        "None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), "
        "InitPlan.Field(name='name', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields"
        ".2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, val"
        "idate=None, check_type=None)), self_param='self', std_params=('c', 'name'), kw_only_params=('_metadata',), fro"
        "zen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(n"
        "ame='c', kw_only=False, fn=None), ReprPlan.Field(name='name', kw_only=False, fn=OpRef(name='repr.fns.2.fn'))),"
        " id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='78434834a42584e4ebc7f4ae0b50787fc65e4c8e',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__coerce',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__repr__fns__2__fn',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.mistral', 'UserMessage'),
    ),
)
def _process_dataclass__78434834a42584e4ebc7f4ae0b50787fc65e4c8e():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__coerce,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
        __dataclass__repr__fns__2__fn,
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
                _metadata=self._metadata,
                c=self.c,
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
                self._metadata == other._metadata and
                self.c == other.c and
                self.name == other.name
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '_metadata',
            'c',
            'name',
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
            '_metadata',
            'c',
            'name',
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
                self._metadata,
                self.c,
                self.name,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            c: __dataclass__init__fields__1__annotation,
            name: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            *,
            _metadata: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            _metadata = __dataclass__init__fields__0__coerce(_metadata)
            __dataclass__object_setattr(self, '_metadata', _metadata)
            __dataclass__object_setattr(self, 'c', c)
            __dataclass__object_setattr(self, 'name', name)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"c={self.c!r}")
            if (s := __dataclass__repr__fns__2__fn(self.name)) is not None:
                parts.append(f"name={s}")
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
        "Plans(tup=(CopyPlan(fields=('tokens',)), EqPlan(fields=('tokens',)), HashPlan(action='set_none', fields=None, "
        "cache=None), InitPlan(fields=(InitPlan.Field(name='tokens', annotation=OpRef(name='init.fields.0.annotation'),"
        " default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, va"
        "lidate=None, check_type=None),), self_param='self', std_params=('tokens',), kw_only_params=(), frozen=False, s"
        "lots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='tokens"
        "', kw_only=False, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='992dded9f23b67474fa059fd50b4093578e27b85',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.sentencepiece.tokens', 'AmbiguousSpecialTokenError'),
    ),
)
def _process_dataclass__992dded9f23b67474fa059fd50b4093578e27b85():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                tokens=self.tokens,
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
                self.tokens == other.tokens
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        setattr(__dataclass__cls, '__hash__', None)

        def __init__(
            self,
            tokens: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            self.tokens = tokens

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"tokens={self.tokens!r}")
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
        "Plans(tup=(CopyPlan(fields=('given', 'expected')), EqPlan(fields=('given', 'expected')), HashPlan(action='set_"
        "none', fields=None, cache=None), InitPlan(fields=(InitPlan.Field(name='given', annotation=OpRef(name='init.fie"
        "lds.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTAN"
        "CE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='expected', annotation=OpRef(name='init."
        "fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INS"
        "TANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=('given', 'expected'), kw_"
        "only_params=(), frozen=False, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fiel"
        "ds=(ReprPlan.Field(name='given', kw_only=False, fn=None), ReprPlan.Field(name='expected', kw_only=False, fn=No"
        "ne)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='dd85158a53c93a82289b98788d08c557aa37e325',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.sentencepiece.tokens', 'MismatchedSpecialTokenError'),
    ),
)
def _process_dataclass__dd85158a53c93a82289b98788d08c557aa37e325():
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
                given=self.given,
                expected=self.expected,
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
                self.given == other.given and
                self.expected == other.expected
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        setattr(__dataclass__cls, '__hash__', None)

        def __init__(
            self,
            given: __dataclass__init__fields__0__annotation,
            expected: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            self.given = given
            self.expected = expected

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"given={self.given!r}")
            parts.append(f"expected={self.expected!r}")
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
        "Plans(tup=(CopyPlan(fields=('v', 'score')), EqPlan(fields=('v', 'score')), FrozenPlan(fields=('v', 'score'), a"
        "llow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('v', 'score'), cache=False), InitPlan(fields="
        "(InitPlan.Field(name='v', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=Non"
        "e, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), Ini"
        "tPlan.Field(name='score', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=Non"
        "e, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), se"
        "lf_param='self', std_params=('v', 'score'), kw_only_params=(), frozen=True, slots=False, post_init_params=None"
        ", init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='v', kw_only=False, fn=None), ReprPlan.F"
        "ield(name='score', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='781af6b7d63e022308ad09d0c6af2f862222da8f',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.sqlite', 'VectorHit'),
    ),
)
def _process_dataclass__781af6b7d63e022308ad09d0c6af2f862222da8f():
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
                v=self.v,
                score=self.score,
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
                self.score == other.score
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'v',
            'score',
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
            'score',
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
                self.v,
                self.score,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            v: __dataclass__init__fields__0__annotation,
            score: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'v', v)
            __dataclass__object_setattr(self, 'score', score)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"v={self.v!r}")
            parts.append(f"score={self.score!r}")
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
        "Plans(tup=(CopyPlan(fields=('l',)), EqPlan(fields=('l',)), FrozenPlan(fields=('l',), allow_dynamic_dunder_attr"
        "s=False), HashPlan(action='add', fields=('l',), cache=False), InitPlan(fields=(InitPlan.Field(name='l', annota"
        "tion=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, fi"
        "eld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self', std_params=('l"
        "',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPl"
        "an(fields=(ReprPlan.Field(name='l', kw_only=False, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='120515e449a82cc5be86f01473d5807ef9f05130',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.sqlite', 'VectorHits'),
        ('ommlds.minichain.llms._marshal', 'Tokens'),
    ),
)
def _process_dataclass__120515e449a82cc5be86f01473d5807ef9f05130():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                l=self.l,
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
                self.l == other.l
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'l',
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
            'l',
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
                self.l,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            l: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'l', l)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"l={self.l!r}")
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
        "Plans(tup=(CopyPlan(fields=('v', 'vec')), EqPlan(fields=('v', 'vec')), FrozenPlan(fields=('v', 'vec'), allow_d"
        "ynamic_dunder_attrs=False), HashPlan(action='add', fields=('v', 'vec'), cache=False), InitPlan(fields=(InitPla"
        "n.Field(name='v', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init="
        "True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fi"
        "eld(name='vec', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=Tr"
        "ue, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='"
        "self', std_params=('v', 'vec'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=("
        "), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='v', kw_only=False, fn=None), ReprPlan.Field(name='v"
        "ec', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='5ea4d9b4bffc7de6c6a04b9485d0523083ae6558',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.sqlite', 'VectorIndexed'),
    ),
)
def _process_dataclass__5ea4d9b4bffc7de6c6a04b9485d0523083ae6558():
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
                v=self.v,
                vec=self.vec,
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
                self.vec == other.vec
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'v',
            'vec',
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
            'vec',
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
                self.v,
                self.vec,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            v: __dataclass__init__fields__0__annotation,
            vec: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'v', v)
            __dataclass__object_setattr(self, 'vec', vec)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"v={self.v!r}")
            parts.append(f"vec={self.vec!r}")
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
        "Plans(tup=(CopyPlan(fields=('vec', 'k')), EqPlan(fields=('vec', 'k')), FrozenPlan(fields=('vec', 'k'), allow_d"
        "ynamic_dunder_attrs=False), HashPlan(action='add', fields=('vec', 'k'), cache=False), InitPlan(fields=(InitPla"
        "n.Field(name='vec', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, ini"
        "t=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan."
        "Field(name='k', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default')"
        ", default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, "
        "check_type=None)), self_param='self', std_params=('vec',), kw_only_params=('k',), frozen=True, slots=False, po"
        "st_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='vec', kw_only=False,"
        " fn=None), ReprPlan.Field(name='k', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='24182e1dbb4c659bdb337ab276f9ac3b06f71444',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.sqlite', 'VectorSearch'),
    ),
)
def _process_dataclass__24182e1dbb4c659bdb337ab276f9ac3b06f71444():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
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
                vec=self.vec,
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
                self.vec == other.vec and
                self.k == other.k
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'vec',
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
            'vec',
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
            return hash((
                self.vec,
                self.k,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            vec: __dataclass__init__fields__0__annotation,
            *,
            k: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'vec', vec)
            __dataclass__object_setattr(self, 'k', k)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"vec={self.vec!r}")
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

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('similarity',)), EqPlan(fields=('similarity',)), FrozenPlan(fields=('similarity',)"
        ", allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('similarity',), cache=False), InitPlan(fie"
        "lds=(InitPlan.Field(name='similarity', annotation=OpRef(name='init.fields.0.annotation'), default=None, defaul"
        "t_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_ty"
        "pe=None),), self_param='self', std_params=('similarity',), kw_only_params=(), frozen=True, slots=False, post_i"
        "nit_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='similarity', kw_only=Fal"
        "se, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='6ee6b20d9248a588cdacec2ceb396c5517b1412d',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.sqlite', 'VectorSearchSimilarity'),
    ),
)
def _process_dataclass__6ee6b20d9248a588cdacec2ceb396c5517b1412d():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                similarity=self.similarity,
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
                self.similarity == other.similarity
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'similarity',
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
            'similarity',
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
                self.similarity,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            similarity: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'similarity', similarity)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"similarity={self.similarity!r}")
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
        "Plans(tup=(CopyPlan(fields=('cls', 'ctor', 'is_np')), EqPlan(fields=('cls', 'ctor', 'is_np')), FrozenPlan(fiel"
        "ds=('cls', 'ctor', 'is_np'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('cls', 'ctor', "
        "'is_np'), cache=False), InitPlan(fields=(InitPlan.Field(name='cls', annotation=OpRef(name='init.fields.0.annot"
        "ation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce="
        "None, validate=None, check_type=None), InitPlan.Field(name='ctor', annotation=OpRef(name='init.fields.1.annota"
        "tion'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=N"
        "one, validate=None, check_type=None), InitPlan.Field(name='is_np', annotation=OpRef(name='init.fields.2.annota"
        "tion'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_ty"
        "pe=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=('cls', 'c"
        "tor'), kw_only_params=('is_np',), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=("
        ")), ReprPlan(fields=(ReprPlan.Field(name='cls', kw_only=False, fn=None), ReprPlan.Field(name='ctor', kw_only=F"
        "alse, fn=None), ReprPlan.Field(name='is_np', kw_only=True, fn=None)), id=False, terse=False, default_fn=None))"
        ")"
    ),
    plan_repr_sha1='7955baf54c2bb5ec0faef8b59a6d2d1df6355b6c',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.minichain.backends.impls.sqlite', '_StorageImpl'),
    ),
)
def _process_dataclass__7955baf54c2bb5ec0faef8b59a6d2d1df6355b6c():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
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
                cls=self.cls,
                ctor=self.ctor,
                is_np=self.is_np,
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
                self.cls == other.cls and
                self.ctor == other.ctor and
                self.is_np == other.is_np
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'cls',
            'ctor',
            'is_np',
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
            'cls',
            'ctor',
            'is_np',
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
                self.cls,
                self.ctor,
                self.is_np,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            cls: __dataclass__init__fields__0__annotation,
            ctor: __dataclass__init__fields__1__annotation,
            *,
            is_np: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'cls', cls)
            __dataclass__object_setattr(self, 'ctor', ctor)
            __dataclass__object_setattr(self, 'is_np', is_np)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"cls={self.cls!r}")
            parts.append(f"ctor={self.ctor!r}")
            parts.append(f"is_np={self.is_np!r}")
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
        "Plans(tup=(CopyPlan(fields=('service',)), EqPlan(fields=('service',)), FrozenPlan(fields=('service',), allow_d"
        "ynamic_dunder_attrs=False), HashPlan(action='add', fields=('service',), cache=False), InitPlan(fields=(InitPla"
        "n.Field(name='service', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None,"
        " init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), sel"
        "f_param='self', std_params=('service',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, i"
        "nit_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='service', kw_only=False, fn=None),), id=Fa"
        "lse, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='e8c5e181501fac7b5abbf4cd74b1e97ce7051392',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.chat.choices.adapters', 'ChatChoicesServiceChatService'),
        ('ommlds.minichain.chat.choices.stream.adapters', 'ChatChoicesStreamServiceChatChoicesService'),
    ),
)
def _process_dataclass__e8c5e181501fac7b5abbf4cd74b1e97ce7051392():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                service=self.service,
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
                self.service == other.service
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'service',
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
            'service',
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
                self.service,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            service: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'service', service)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"service={self.service!r}")
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
        "Plans(tup=(CopyPlan(fields=('schema',)), EqPlan(fields=('schema',)), FrozenPlan(fields=('schema',), allow_dyna"
        "mic_dunder_attrs=False), HashPlan(action='add', fields=('schema',), cache=False), InitPlan(fields=(InitPlan.Fi"
        "eld(name='schema', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.defaul"
        "t'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=Non"
        "e, check_type=None),), self_param='self', std_params=('schema',), kw_only_params=(), frozen=True, slots=False,"
        " post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='schema', kw_only="
        "False, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='b2744f4fae3f6b409187f78feac9442e7e1db7ac',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
    ),
    cls_names=(
        ('ommlds.minichain.chat.formats', 'JsonResponseFormat'),
    ),
)
def _process_dataclass__b2744f4fae3f6b409187f78feac9442e7e1db7ac():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
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
                self.schema == other.schema
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
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
                self.schema,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            schema: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'schema', schema)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
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


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('m',)), EqPlan(fields=('m',)), FrozenPlan(fields=('m',), allow_dynamic_dunder_attr"
        "s=False), HashPlan(action='add', fields=('m',), cache=False), InitPlan(fields=(InitPlan.Field(name='m', annota"
        "tion=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, fi"
        "eld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self', std_params=('m"
        "',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPl"
        "an(fields=(ReprPlan.Field(name='m', kw_only=False, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='00a32d02ca8d7c055f05a95a2073d8d5198c6d97',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.chat.templating', 'ChatTemplater._MessageStep'),
        ('ommlds.minichain.chat.tools.execution', 'ToolFn.MaysyncImpl'),
    ),
)
def _process_dataclass__00a32d02ca8d7c055f05a95a2073d8d5198c6d97():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
            m: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
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

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('p',)), EqPlan(fields=('p',)), FrozenPlan(fields=('p',), allow_dynamic_dunder_attr"
        "s=False), HashPlan(action='add', fields=('p',), cache=False), InitPlan(fields=(InitPlan.Field(name='p', annota"
        "tion=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, fi"
        "eld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self', std_params=('p"
        "',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPl"
        "an(fields=(ReprPlan.Field(name='p', kw_only=False, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='25598005d4986efc83d12d341829703b738d3f54',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.chat.templating', 'ChatTemplater._PlaceholderStep'),
    ),
)
def _process_dataclass__25598005d4986efc83d12d341829703b738d3f54():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                self.p == other.p
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

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

        def __hash__(self):
            return hash((
                self.p,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

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

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('m', 'd')), EqPlan(fields=('m', 'd')), FrozenPlan(fields=('m', 'd'), allow_dynamic"
        "_dunder_attrs=False), HashPlan(action='add', fields=('m', 'd'), cache=False), InitPlan(fields=(InitPlan.Field("
        "name='m', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, ov"
        "erride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name"
        "='d', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, overri"
        "de=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std"
        "_params=('m', 'd'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_"
        "fns=()), ReprPlan(fields=(ReprPlan.Field(name='m', kw_only=False, fn=None), ReprPlan.Field(name='d', kw_only=F"
        "alse, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='a6847b703ccb991096e8362e4bfbc91af7df37bf',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.chat.templating', 'ChatTemplater._TemplateStep'),
    ),
)
def _process_dataclass__a6847b703ccb991096e8362e4bfbc91af7df37bf():
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
                d=self.d,
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
                self.d == other.d
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'm',
            'd',
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
            'd',
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
                self.d,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            m: __dataclass__init__fields__0__annotation,
            d: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'm', m)
            __dataclass__object_setattr(self, 'd', d)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"m={self.m!r}")
            parts.append(f"d={self.d!r}")
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
        "Plans(tup=(CopyPlan(fields=('key',)), EqPlan(fields=('key',)), FrozenPlan(fields=('key',), allow_dynamic_dunde"
        "r_attrs=False), HashPlan(action='add', fields=('key',), cache=False), InitPlan(fields=(InitPlan.Field(name='ke"
        "y', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override"
        "=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self', std_"
        "params=('key',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns"
        "=()), ReprPlan(fields=(ReprPlan.Field(name='key', kw_only=False, fn=None),), id=False, terse=False, default_fn"
        "=None)))"
    ),
    plan_repr_sha1='4492a70e9341afc741b487e59ae5ea6624e3c95d',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.chat.templating', 'MessagePlaceholder'),
    ),
)
def _process_dataclass__4492a70e9341afc741b487e59ae5ea6624e3c95d():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
            return hash((
                self.key,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            key: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'key', key)

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

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('fn',)), EqPlan(fields=('fn',)), FrozenPlan(fields=('fn',), allow_dynamic_dunder_a"
        "ttrs=False), HashPlan(action='add', fields=('fn',), cache=False), InitPlan(fields=(InitPlan.Field(name='fn', a"
        "nnotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=Fals"
        "e, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self', std_param"
        "s=('fn',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), "
        "ReprPlan(fields=(ReprPlan.Field(name='fn', kw_only=False, fn=None),), id=False, terse=False, default_fn=None))"
        ")"
    ),
    plan_repr_sha1='9c26f5e7e2496284b4ba1e1072fb3e29dc4e0ec4',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.chat.templating', 'StringFnContentTransform'),
        ('ommlds.minichain.chat.tools.ids', 'FnChatTransform'),
        ('ommlds.minichain.chat.tools.ids', 'FnMessageTransform'),
    ),
)
def _process_dataclass__9c26f5e7e2496284b4ba1e1072fb3e29dc4e0ec4():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
            return hash((
                self.fn,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            fn: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
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

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('tool_executors_by_name',)), EqPlan(fields=('tool_executors_by_name',)), FrozenPla"
        "n(fields=('tool_executors_by_name',), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('tool_"
        "executors_by_name',), cache=False), InitPlan(fields=(InitPlan.Field(name='tool_executors_by_name', annotation="
        "OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_t"
        "ype=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self', std_params=('tool_e"
        "xecutors_by_name',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate"
        "_fns=()), ReprPlan(fields=(ReprPlan.Field(name='tool_executors_by_name', kw_only=False, fn=None),), id=False, "
        "terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='162af73bb618e913511f0554e122b477b9b9ec3c',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.chat.tools.execution', 'NameSwitchedToolExecutor'),
    ),
)
def _process_dataclass__162af73bb618e913511f0554e122b477b9b9ec3c():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                tool_executors_by_name=self.tool_executors_by_name,
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
                self.tool_executors_by_name == other.tool_executors_by_name
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'tool_executors_by_name',
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
            'tool_executors_by_name',
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
                self.tool_executors_by_name,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            tool_executors_by_name: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'tool_executors_by_name', tool_executors_by_name)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"tool_executors_by_name={self.tool_executors_by_name!r}")
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
        "Plans(tup=(CopyPlan(fields=('impl', 'input', 'output')), EqPlan(fields=('impl', 'input', 'output')), FrozenPla"
        "n(fields=('impl', 'input', 'output'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('impl'"
        ", 'input', 'output'), cache=False), InitPlan(fields=(InitPlan.Field(name='impl', annotation=OpRef(name='init.f"
        "ields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INST"
        "ANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='input', annotation=OpRef(name='init.f"
        "ields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INST"
        "ANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='output', annotation=OpRef(name='init."
        "fields.2.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INS"
        "TANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=('impl', 'input', 'output'"
        "), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan"
        "(fields=(ReprPlan.Field(name='impl', kw_only=False, fn=None), ReprPlan.Field(name='input', kw_only=False, fn=N"
        "one), ReprPlan.Field(name='output', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='de3be5fd6f60c4f97ffe6dc8063dfe0114df6340',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.chat.tools.execution', 'ToolFn'),
    ),
)
def _process_dataclass__de3be5fd6f60c4f97ffe6dc8063dfe0114df6340():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
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
                impl=self.impl,
                input=self.input,
                output=self.output,
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
                self.impl == other.impl and
                self.input == other.input and
                self.output == other.output
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'impl',
            'input',
            'output',
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
            'input',
            'output',
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
                self.impl,
                self.input,
                self.output,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            impl: __dataclass__init__fields__0__annotation,
            input: __dataclass__init__fields__1__annotation,
            output: __dataclass__init__fields__2__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'impl', impl)
            __dataclass__object_setattr(self, 'input', input)
            __dataclass__object_setattr(self, 'output', output)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"impl={self.impl!r}")
            parts.append(f"input={self.input!r}")
            parts.append(f"output={self.output!r}")
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
        "Plans(tup=(CopyPlan(fields=('cls',)), EqPlan(fields=('cls',)), FrozenPlan(fields=('cls',), allow_dynamic_dunde"
        "r_attrs=False), HashPlan(action='add', fields=('cls',), cache=False), InitPlan(fields=(InitPlan.Field(name='cl"
        "s', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override"
        "=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self', std_"
        "params=('cls',), kw_only_params=(), frozen=True, slots=False, post_init_params=(), init_fns=(), validate_fns=("
        ")), ReprPlan(fields=(ReprPlan.Field(name='cls', kw_only=False, fn=None),), id=False, terse=False, default_fn=N"
        "one)))"
    ),
    plan_repr_sha1='0ed2db2de0439b653c8fb6100e75bce7782ea8a0',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.chat.tools.execution', 'ToolFn.DataclassInput'),
        ('ommlds.minichain.chat.tools.execution', 'ToolFn.DataclassOutput'),
    ),
)
def _process_dataclass__0ed2db2de0439b653c8fb6100e75bce7782ea8a0():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                cls=self.cls,
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
                self.cls == other.cls
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'cls',
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
            'cls',
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
                self.cls,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            cls: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'cls', cls)
            self.__post_init__()

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"cls={self.cls!r}")
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
        "Plans(tup=(CopyPlan(fields=('s', 'a')), EqPlan(fields=('s', 'a')), FrozenPlan(fields=('s', 'a'), allow_dynamic"
        "_dunder_attrs=False), HashPlan(action='add', fields=('s', 'a'), cache=False), InitPlan(fields=(InitPlan.Field("
        "name='s', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'), defa"
        "ult_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_"
        "type=None), InitPlan.Field(name='a', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='in"
        "it.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce="
        "None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('s', 'a'), frozen=Tr"
        "ue, slots=False, post_init_params=(), init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='s',"
        " kw_only=True, fn=None), ReprPlan.Field(name='a', kw_only=True, fn=None)), id=False, terse=False, default_fn=N"
        "one)))"
    ),
    plan_repr_sha1='58456bc8a88d4a91404f149d73fdda6a16fd22a9',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.minichain.chat.tools.execution', 'ToolFn.FnImpl'),
    ),
)
def _process_dataclass__58456bc8a88d4a91404f149d73fdda6a16fd22a9():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
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
                s=self.s,
                a=self.a,
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
                self.s == other.s and
                self.a == other.a
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            's',
            'a',
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
            's',
            'a',
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
                self.s,
                self.a,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            s: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            a: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 's', s)
            __dataclass__object_setattr(self, 'a', a)
            self.__post_init__()

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"s={self.s!r}")
            parts.append(f"a={self.a!r}")
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
        "Plans(tup=(CopyPlan(fields=('rtys',)), EqPlan(fields=('rtys',)), FrozenPlan(fields=('rtys',), allow_dynamic_du"
        "nder_attrs=False), HashPlan(action='add', fields=('rtys',), cache=False), InitPlan(fields=(InitPlan.Field(name"
        "='rtys', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, ove"
        "rride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self',"
        " std_params=('rtys',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), valida"
        "te_fns=()), ReprPlan(fields=(ReprPlan.Field(name='rtys', kw_only=False, fn=None),), id=False, terse=False, def"
        "ault_fn=None)))"
    ),
    plan_repr_sha1='414809a505ec9965b78a8a29b59757d13b787f5c',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.chat.tools.execution', 'ToolFn.MarshalInput'),
    ),
)
def _process_dataclass__414809a505ec9965b78a8a29b59757d13b787f5c():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                rtys=self.rtys,
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
                self.rtys == other.rtys
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'rtys',
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
            'rtys',
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
                self.rtys,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            rtys: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'rtys', rtys)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"rtys={self.rtys!r}")
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
        "Plans(tup=(CopyPlan(fields=('rty',)), EqPlan(fields=('rty',)), FrozenPlan(fields=('rty',), allow_dynamic_dunde"
        "r_attrs=False), HashPlan(action='add', fields=('rty',), cache=False), InitPlan(fields=(InitPlan.Field(name='rt"
        "y', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override"
        "=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self', std_"
        "params=('rty',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns"
        "=()), ReprPlan(fields=(ReprPlan.Field(name='rty', kw_only=False, fn=None),), id=False, terse=False, default_fn"
        "=None)))"
    ),
    plan_repr_sha1='e0d54ba87512abba1f90372a952285f136dc040e',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.chat.tools.execution', 'ToolFn.MarshalOutput'),
    ),
)
def _process_dataclass__e0d54ba87512abba1f90372a952285f136dc040e():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                rty=self.rty,
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
                self.rty == other.rty
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'rty',
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
            'rty',
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
                self.rty,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            rty: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'rty', rty)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"rty={self.rty!r}")
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
        "Plans(tup=(CopyPlan(fields=('tool_fn',)), EqPlan(fields=('tool_fn',)), FrozenPlan(fields=('tool_fn',), allow_d"
        "ynamic_dunder_attrs=False), HashPlan(action='add', fields=('tool_fn',), cache=False), InitPlan(fields=(InitPla"
        "n.Field(name='tool_fn', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None,"
        " init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), sel"
        "f_param='self', std_params=('tool_fn',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, i"
        "nit_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='tool_fn', kw_only=False, fn=None),), id=Fa"
        "lse, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='512f54ae8b68c29c74c7815b448db1e085d548b4',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.chat.tools.execution', 'ToolFnToolExecutor'),
    ),
)
def _process_dataclass__512f54ae8b68c29c74c7815b448db1e085d548b4():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                tool_fn=self.tool_fn,
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
                self.tool_fn == other.tool_fn
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'tool_fn',
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
            'tool_fn',
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
                self.tool_fn,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            tool_fn: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'tool_fn', tool_fn)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"tool_fn={self.tool_fn!r}")
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
        "Plans(tup=(CopyPlan(fields=('cts',)), EqPlan(fields=('cts',)), FrozenPlan(fields=('cts',), allow_dynamic_dunde"
        "r_attrs=False), HashPlan(action='add', fields=('cts',), cache=False), InitPlan(fields=(InitPlan.Field(name='ct"
        "s', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override"
        "=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self', std_"
        "params=('cts',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns"
        "=()), ReprPlan(fields=(ReprPlan.Field(name='cts', kw_only=False, fn=None),), id=False, terse=False, default_fn"
        "=None)))"
    ),
    plan_repr_sha1='68d062858a9894949b2c170a3763346ddc35bf1d',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.chat.tools.ids', 'CompositeChatTransform'),
    ),
)
def _process_dataclass__68d062858a9894949b2c170a3763346ddc35bf1d():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                cts=self.cts,
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
                self.cts == other.cts
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'cts',
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
            'cts',
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
                self.cts,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            cts: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'cts', cts)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"cts={self.cts!r}")
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
        "Plans(tup=(CopyPlan(fields=('mts',)), EqPlan(fields=('mts',)), FrozenPlan(fields=('mts',), allow_dynamic_dunde"
        "r_attrs=False), HashPlan(action='add', fields=('mts',), cache=False), InitPlan(fields=(InitPlan.Field(name='mt"
        "s', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override"
        "=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self', std_"
        "params=('mts',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns"
        "=()), ReprPlan(fields=(ReprPlan.Field(name='mts', kw_only=False, fn=None),), id=False, terse=False, default_fn"
        "=None)))"
    ),
    plan_repr_sha1='7c77afa1c0f5f02889fd2b827e06017e86ba5373',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.chat.tools.ids', 'CompositeMessageTransform'),
    ),
)
def _process_dataclass__7c77afa1c0f5f02889fd2b827e06017e86ba5373():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                mts=self.mts,
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
                self.mts == other.mts
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'mts',
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
            'mts',
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
                self.mts,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            mts: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'mts', mts)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"mts={self.mts!r}")
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
        "Plans(tup=(CopyPlan(fields=('mt',)), EqPlan(fields=('mt',)), FrozenPlan(fields=('mt',), allow_dynamic_dunder_a"
        "ttrs=False), HashPlan(action='add', fields=('mt',), cache=False), InitPlan(fields=(InitPlan.Field(name='mt', a"
        "nnotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=Fals"
        "e, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self', std_param"
        "s=('mt',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), "
        "ReprPlan(fields=(ReprPlan.Field(name='mt', kw_only=False, fn=None),), id=False, terse=False, default_fn=None))"
        ")"
    ),
    plan_repr_sha1='d3a5e675a8403dc89efd95a66ba5da2cdf738d2e',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.chat.tools.ids', 'LastMessageTransformChatTransform'),
        ('ommlds.minichain.chat.tools.ids', 'MessageTransformChatTransform'),
    ),
)
def _process_dataclass__d3a5e675a8403dc89efd95a66ba5da2cdf738d2e():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                mt=self.mt,
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
                self.mt == other.mt
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'mt',
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
            'mt',
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
                self.mt,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            mt: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'mt', mt)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"mt={self.mt!r}")
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
        "Plans(tup=(CopyPlan(fields=('id_factory',)), EqPlan(fields=('id_factory',)), FrozenPlan(fields=('id_factory',)"
        ", allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('id_factory',), cache=False), InitPlan(fie"
        "lds=(InitPlan.Field(name='id_factory', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='"
        "init.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerc"
        "e=None, validate=None, check_type=None),), self_param='self', std_params=('id_factory',), kw_only_params=(), f"
        "rozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field"
        "(name='id_factory', kw_only=False, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='56dfe391de5b28798606c2e0e96f2f9f6f367b48',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
    ),
    cls_names=(
        ('ommlds.minichain.chat.tools.ids', 'ToolUseIdAddingMessageTransform'),
    ),
)
def _process_dataclass__56dfe391de5b28798606c2e0e96f2f9f6f367b48():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
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
                id_factory=self.id_factory,
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
                self.id_factory == other.id_factory
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'id_factory',
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
            'id_factory',
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
                self.id_factory,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            id_factory: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'id_factory', id_factory)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"id_factory={self.id_factory!r}")
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
        "Plans(tup=(CopyPlan(fields=('ty', 'mt')), EqPlan(fields=('ty', 'mt')), FrozenPlan(fields=('ty', 'mt'), allow_d"
        "ynamic_dunder_attrs=False), HashPlan(action='add', fields=('ty', 'mt'), cache=False), InitPlan(fields=(InitPla"
        "n.Field(name='ty', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init"
        "=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.F"
        "ield(name='mt', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=Tr"
        "ue, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='"
        "self', std_params=('ty', 'mt'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=("
        "), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='ty', kw_only=False, fn=None), ReprPlan.Field(name='"
        "mt', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='dd461b9bf78b0af6ae2af593dfd0f556db66339c',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.chat.tools.ids', 'TypeFilteredMessageTransform'),
    ),
)
def _process_dataclass__dd461b9bf78b0af6ae2af593dfd0f556db66339c():
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
                ty=self.ty,
                mt=self.mt,
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
                self.mt == other.mt
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'ty',
            'mt',
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
            'mt',
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
                self.mt,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            ty: __dataclass__init__fields__0__annotation,
            mt: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'ty', ty)
            __dataclass__object_setattr(self, 'mt', mt)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"ty={self.ty!r}")
            parts.append(f"mt={self.mt!r}")
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
        "Plans(tup=(CopyPlan(fields=('name', 'args', 'raw_text', 'raw_body', 'id', 'reasoning')), EqPlan(fields=('name'"
        ", 'args', 'raw_text', 'raw_body', 'id', 'reasoning')), FrozenPlan(fields=('name', 'args', 'raw_text', 'raw_bod"
        "y', 'id', 'reasoning'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('name', 'args', 'raw"
        "_text', 'raw_body', 'id', 'reasoning'), cache=False), InitPlan(fields=(InitPlan.Field(name='name', annotation="
        "OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_t"
        "ype=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='args', annotation=O"
        "pRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_ty"
        "pe=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='raw_text', annotatio"
        "n=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, i"
        "nit=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPla"
        "n.Field(name='raw_body', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3."
        "default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valida"
        "te=None, check_type=None), InitPlan.Field(name='id', annotation=OpRef(name='init.fields.4.annotation'), defaul"
        "t=OpRef(name='init.fields.4.default'), default_factory=None, init=True, override=False, field_type=FieldType.I"
        "NSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='reasoning', annotation=OpRef(name="
        "'init.fields.5.annotation'), default=OpRef(name='init.fields.5.default'), default_factory=None, init=True, ove"
        "rride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', "
        "std_params=('name', 'args'), kw_only_params=('raw_text', 'raw_body', 'id', 'reasoning'), frozen=True, slots=Fa"
        "lse, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='name', kw_onl"
        "y=False, fn=None), ReprPlan.Field(name='args', kw_only=False, fn=None), ReprPlan.Field(name='raw_text', kw_onl"
        "y=True, fn=None), ReprPlan.Field(name='raw_body', kw_only=True, fn=None), ReprPlan.Field(name='id', kw_only=Tr"
        "ue, fn=None), ReprPlan.Field(name='reasoning', kw_only=True, fn=None)), id=False, terse=False, default_fn=None"
        ")))"
    ),
    plan_repr_sha1='c7cb99a1bdd01fb9ec10d2e00a23f26953d5ef8d',
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
    ),
    cls_names=(
        ('ommlds.minichain.chat.tools.parsing', 'ParsedToolExec'),
    ),
)
def _process_dataclass__c7cb99a1bdd01fb9ec10d2e00a23f26953d5ef8d():
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
                args=self.args,
                raw_text=self.raw_text,
                raw_body=self.raw_body,
                id=self.id,
                reasoning=self.reasoning,
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
                self.args == other.args and
                self.raw_text == other.raw_text and
                self.raw_body == other.raw_body and
                self.id == other.id and
                self.reasoning == other.reasoning
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'name',
            'args',
            'raw_text',
            'raw_body',
            'id',
            'reasoning',
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
            'args',
            'raw_text',
            'raw_body',
            'id',
            'reasoning',
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
                self.args,
                self.raw_text,
                self.raw_body,
                self.id,
                self.reasoning,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            name: __dataclass__init__fields__0__annotation,
            args: __dataclass__init__fields__1__annotation,
            *,
            raw_text: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            raw_body: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            id: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            reasoning: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'args', args)
            __dataclass__object_setattr(self, 'raw_text', raw_text)
            __dataclass__object_setattr(self, 'raw_body', raw_body)
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'reasoning', reasoning)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"name={self.name!r}")
            parts.append(f"args={self.args!r}")
            parts.append(f"raw_text={self.raw_text!r}")
            parts.append(f"raw_body={self.raw_body!r}")
            parts.append(f"id={self.id!r}")
            parts.append(f"reasoning={self.reasoning!r}")
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
        "Plans(tup=(CopyPlan(fields=('parser',)), EqPlan(fields=('parser',)), FrozenPlan(fields=('parser',), allow_dyna"
        "mic_dunder_attrs=False), HashPlan(action='add', fields=('parser',), cache=False), InitPlan(fields=(InitPlan.Fi"
        "eld(name='parser', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init"
        "=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_par"
        "am='self', std_params=('parser',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fn"
        "s=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='parser', kw_only=False, fn=None),), id=False, te"
        "rse=False, default_fn=None)))"
    ),
    plan_repr_sha1='ba8e1dc2838842b2168f1fd4b6c82d3b33a109da',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.chat.tools.parsing', 'ToolExecParsingMessageTransform'),
    ),
)
def _process_dataclass__ba8e1dc2838842b2168f1fd4b6c82d3b33a109da():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                parser=self.parser,
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
                self.parser == other.parser
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'parser',
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
            'parser',
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
                self.parser,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            parser: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'parser', parser)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"parser={self.parser!r}")
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
        "Plans(tup=(CopyPlan(fields=('clock',)), EqPlan(fields=('clock',)), FrozenPlan(fields=('clock',), allow_dynamic"
        "_dunder_attrs=False), HashPlan(action='add', fields=('clock',), cache=False), InitPlan(fields=(InitPlan.Field("
        "name='clock', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'), "
        "default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, ch"
        "eck_type=None),), self_param='self', std_params=('clock',), kw_only_params=(), frozen=True, slots=False, post_"
        "init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='clock', kw_only=False, "
        "fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='a89375a36223a889920e8b93b4e42846a4cfffa0',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
    ),
    cls_names=(
        ('ommlds.minichain.chat.transforms.metadata', 'CreatedAtAddingMessageTransform'),
    ),
)
def _process_dataclass__a89375a36223a889920e8b93b4e42846a4cfffa0():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
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
                clock=self.clock,
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
                self.clock == other.clock
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'clock',
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
            'clock',
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
                self.clock,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            clock: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'clock', clock)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"clock={self.clock!r}")
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
        "Plans(tup=(CopyPlan(fields=('child',)), EqPlan(fields=('child',)), FrozenPlan(fields=('child',), allow_dynamic"
        "_dunder_attrs=False), HashPlan(action='add', fields=('child',), cache=False), InitPlan(fields=(InitPlan.Field("
        "name='child', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True"
        ", override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='s"
        "elf', std_params=('child',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), "
        "validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='child', kw_only=False, fn=None),), id=False, terse=Fal"
        "se, default_fn=None)))"
    ),
    plan_repr_sha1='9024fb7569f3cdb9de637a9068a1db5ef0178937',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.chat.transforms.metadata', 'OriginAddingMessageTransform'),
    ),
)
def _process_dataclass__9024fb7569f3cdb9de637a9068a1db5ef0178937():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                child=self.child,
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
                self.child == other.child
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'child',
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
            'child',
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
                self.child,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            child: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'child', child)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"child={self.child!r}")
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
        "Plans(tup=(CopyPlan(fields=('uuid_factory',)), EqPlan(fields=('uuid_factory',)), FrozenPlan(fields=('uuid_fact"
        "ory',), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('uuid_factory',), cache=False), Init"
        "Plan(fields=(InitPlan.Field(name='uuid_factory', annotation=OpRef(name='init.fields.0.annotation'), default=No"
        "ne, default_factory=OpRef(name='init.fields.0.default_factory'), init=True, override=False, field_type=FieldTy"
        "pe.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self', std_params=('uuid_factory',), "
        "kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fi"
        "elds=(ReprPlan.Field(name='uuid_factory', kw_only=False, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='19ef2cebd031d990f735e4c579538f81f6196e5e',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default_factory',
    ),
    cls_names=(
        ('ommlds.minichain.chat.transforms.metadata', 'UuidAddingMessageTransform'),
    ),
)
def _process_dataclass__19ef2cebd031d990f735e4c579538f81f6196e5e():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default_factory,
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
                uuid_factory=self.uuid_factory,
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
                self.uuid_factory == other.uuid_factory
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'uuid_factory',
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
            'uuid_factory',
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
                self.uuid_factory,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            uuid_factory: __dataclass__init__fields__0__annotation = __dataclass__HAS_DEFAULT_FACTORY,
        ) -> __dataclass__None:
            if uuid_factory is __dataclass__HAS_DEFAULT_FACTORY:
                uuid_factory = __dataclass__init__fields__0__default_factory()
            __dataclass__object_setattr(self, 'uuid_factory', uuid_factory)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"uuid_factory={self.uuid_factory!r}")
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
        "Plans(tup=(CopyPlan(fields=('ct', 'svc')), EqPlan(fields=('ct', 'svc')), FrozenPlan(fields=('ct', 'svc'), allo"
        "w_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('ct', 'svc'), cache=False), InitPlan(fields=(Ini"
        "tPlan.Field(name='ct', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, "
        "init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPl"
        "an.Field(name='svc', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, in"
        "it=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_pa"
        "ram='self', std_params=('ct', 'svc'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init"
        "_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='ct', kw_only=False, fn=None), ReprPlan.Field("
        "name='svc', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='5db03d7874dd018e98dde3e8e5f4d6528cc10d09',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.chat.transforms.services', 'RequestChatTransformingChatService'),
        ('ommlds.minichain.chat.transforms.services', 'ResponseChatTransformingChatService'),
    ),
)
def _process_dataclass__5db03d7874dd018e98dde3e8e5f4d6528cc10d09():
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
                ct=self.ct,
                svc=self.svc,
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
                self.ct == other.ct and
                self.svc == other.svc
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'ct',
            'svc',
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
            'ct',
            'svc',
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
                self.ct,
                self.svc,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            ct: __dataclass__init__fields__0__annotation,
            svc: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'ct', ct)
            __dataclass__object_setattr(self, 'svc', svc)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"ct={self.ct!r}")
            parts.append(f"svc={self.svc!r}")
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
        "Plans(tup=(CopyPlan(fields=('name', 'registry_type_manifests', 'unresolved_type_manifests')), EqPlan(fields=('"
        "name', 'registry_type_manifests', 'unresolved_type_manifests')), HashPlan(action='set_none', fields=None, cach"
        "e=None), InitPlan(fields=(InitPlan.Field(name='name', annotation=OpRef(name='init.fields.0.annotation'), defau"
        "lt=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate"
        "=None, check_type=None), InitPlan.Field(name='registry_type_manifests', annotation=OpRef(name='init.fields.1.a"
        "nnotation'), default=None, default_factory=OpRef(name='init.fields.1.default_factory'), init=True, override=Fa"
        "lse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='unresol"
        "ved_type_manifests', annotation=OpRef(name='init.fields.2.annotation'), default=None, default_factory=OpRef(na"
        "me='init.fields.2.default_factory'), init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, va"
        "lidate=None, check_type=None)), self_param='self', std_params=('name', 'registry_type_manifests', 'unresolved_"
        "type_manifests'), kw_only_params=(), frozen=False, slots=False, post_init_params=None, init_fns=(), validate_f"
        "ns=()), ReprPlan(fields=(ReprPlan.Field(name='name', kw_only=False, fn=None), ReprPlan.Field(name='registry_ty"
        "pe_manifests', kw_only=False, fn=None), ReprPlan.Field(name='unresolved_type_manifests', kw_only=False, fn=Non"
        "e)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='882633e03a2ba1fe33d217133f32cc88d8d1858b',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default_factory',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default_factory',
    ),
    cls_names=(
        ('ommlds.minichain.completion', 'Registry._Module'),
    ),
)
def _process_dataclass__882633e03a2ba1fe33d217133f32cc88d8d1858b():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default_factory,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default_factory,
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
                registry_type_manifests=self.registry_type_manifests,
                unresolved_type_manifests=self.unresolved_type_manifests,
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
                self.registry_type_manifests == other.registry_type_manifests and
                self.unresolved_type_manifests == other.unresolved_type_manifests
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        setattr(__dataclass__cls, '__hash__', None)

        def __init__(
            self,
            name: __dataclass__init__fields__0__annotation,
            registry_type_manifests: __dataclass__init__fields__1__annotation = __dataclass__HAS_DEFAULT_FACTORY,
            unresolved_type_manifests: __dataclass__init__fields__2__annotation = __dataclass__HAS_DEFAULT_FACTORY,
        ) -> __dataclass__None:
            if registry_type_manifests is __dataclass__HAS_DEFAULT_FACTORY:
                registry_type_manifests = __dataclass__init__fields__1__default_factory()
            if unresolved_type_manifests is __dataclass__HAS_DEFAULT_FACTORY:
                unresolved_type_manifests = __dataclass__init__fields__2__default_factory()
            self.name = name
            self.registry_type_manifests = registry_type_manifests
            self.unresolved_type_manifests = unresolved_type_manifests

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"name={self.name!r}")
            parts.append(f"registry_type_manifests={self.registry_type_manifests!r}")
            parts.append(f"unresolved_type_manifests={self.unresolved_type_manifests!r}")
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
        "Plans(tup=(CopyPlan(fields=('cls', 'module')), EqPlan(fields=('cls', 'module')), FrozenPlan(fields=('cls', 'mo"
        "dule'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('cls', 'module'), cache=False), Init"
        "Plan(fields=(InitPlan.Field(name='cls', annotation=OpRef(name='init.fields.0.annotation'), default=None, defau"
        "lt_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_t"
        "ype=None), InitPlan.Field(name='module', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name"
        "='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coe"
        "rce=None, validate=None, check_type=None)), self_param='self', std_params=('cls',), kw_only_params=('module',)"
        ", frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Fi"
        "eld(name='cls', kw_only=False, fn=None), ReprPlan.Field(name='module', kw_only=True, fn=None)), id=False, ters"
        "e=False, default_fn=None)))"
    ),
    plan_repr_sha1='d72d4cb54b9db0acfd7fd34ce25e4ee90e0eb91e',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.minichain.completion', 'Registry._RegisteredType'),
    ),
)
def _process_dataclass__d72d4cb54b9db0acfd7fd34ce25e4ee90e0eb91e():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
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
                cls=self.cls,
                module=self.module,
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
                self.cls == other.cls and
                self.module == other.module
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'cls',
            'module',
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
            'cls',
            'module',
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
                self.cls,
                self.module,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            cls: __dataclass__init__fields__0__annotation,
            *,
            module: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'cls', cls)
            __dataclass__object_setattr(self, 'module', module)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"cls={self.cls!r}")
            parts.append(f"module={self.module!r}")
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
        "Plans(tup=(CopyPlan(fields=('module', 'attr', 'name', 'aliases', 'type')), EqPlan(fields=('module', 'attr', 'n"
        "ame', 'aliases', 'type')), FrozenPlan(fields=('module', 'attr', 'name', 'aliases', 'type'), allow_dynamic_dund"
        "er_attrs=False), HashPlan(action='add', fields=('module', 'attr', 'name', 'aliases', 'type'), cache=False), In"
        "itPlan(fields=(InitPlan.Field(name='module', annotation=OpRef(name='init.fields.0.annotation'), default=None, "
        "default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, ch"
        "eck_type=None), InitPlan.Field(name='attr', annotation=OpRef(name='init.fields.1.annotation'), default=None, d"
        "efault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, che"
        "ck_type=None), InitPlan.Field(name='name', annotation=OpRef(name='init.fields.2.annotation'), default=None, de"
        "fault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, chec"
        "k_type=None), InitPlan.Field(name='aliases', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef("
        "name='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE,"
        " coerce=None, validate=None, check_type=None), InitPlan.Field(name='type', annotation=OpRef(name='init.fields."
        "4.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, "
        "coerce=None, validate=None, check_type=None)), self_param='self', std_params=('module', 'attr', 'name', 'alias"
        "es'), kw_only_params=('type',), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=())"
        ", ReprPlan(fields=(ReprPlan.Field(name='module', kw_only=False, fn=None), ReprPlan.Field(name='attr', kw_only="
        "False, fn=None), ReprPlan.Field(name='name', kw_only=False, fn=None), ReprPlan.Field(name='aliases', kw_only=F"
        "alse, fn=None), ReprPlan.Field(name='type', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='036bbc6009feb74ecbec68e786760ecc81b07f33',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
        '__dataclass__init__fields__4__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.completion', 'RegistryManifest'),
    ),
)
def _process_dataclass__036bbc6009feb74ecbec68e786760ecc81b07f33():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__3__default,
        __dataclass__init__fields__4__annotation,
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
                module=self.module,
                attr=self.attr,
                name=self.name,
                aliases=self.aliases,
                type=self.type,
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
                self.module == other.module and
                self.attr == other.attr and
                self.name == other.name and
                self.aliases == other.aliases and
                self.type == other.type
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'module',
            'attr',
            'name',
            'aliases',
            'type',
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
            'module',
            'attr',
            'name',
            'aliases',
            'type',
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
                self.module,
                self.attr,
                self.name,
                self.aliases,
                self.type,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            module: __dataclass__init__fields__0__annotation,
            attr: __dataclass__init__fields__1__annotation,
            name: __dataclass__init__fields__2__annotation,
            aliases: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            *,
            type: __dataclass__init__fields__4__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'module', module)
            __dataclass__object_setattr(self, 'attr', attr)
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'aliases', aliases)
            __dataclass__object_setattr(self, 'type', type)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"module={self.module!r}")
            parts.append(f"attr={self.attr!r}")
            parts.append(f"name={self.name!r}")
            parts.append(f"aliases={self.aliases!r}")
            parts.append(f"type={self.type!r}")
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
        "Plans(tup=(CopyPlan(fields=('module', 'attr')), EqPlan(fields=('module', 'attr')), FrozenPlan(fields=('module'"
        ", 'attr'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('module', 'attr'), cache=False), "
        "InitPlan(fields=(InitPlan.Field(name='module', annotation=OpRef(name='init.fields.0.annotation'), default=None"
        ", default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, "
        "check_type=None), InitPlan.Field(name='attr', annotation=OpRef(name='init.fields.1.annotation'), default=None,"
        " default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, c"
        "heck_type=None)), self_param='self', std_params=('module', 'attr'), kw_only_params=(), frozen=True, slots=Fals"
        "e, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='module', kw_onl"
        "y=False, fn=None), ReprPlan.Field(name='attr', kw_only=False, fn=None)), id=False, terse=False, default_fn=Non"
        "e)))"
    ),
    plan_repr_sha1='6c2988a8870fad207eb0703de627596cae1b7381',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.completion', 'RegistryTypeManifest'),
    ),
)
def _process_dataclass__6c2988a8870fad207eb0703de627596cae1b7381():
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
                module=self.module,
                attr=self.attr,
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
                self.module == other.module and
                self.attr == other.attr
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'module',
            'attr',
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
            'module',
            'attr',
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
                self.module,
                self.attr,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            module: __dataclass__init__fields__0__annotation,
            attr: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'module', module)
            __dataclass__object_setattr(self, 'attr', attr)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"module={self.module!r}")
            parts.append(f"attr={self.attr!r}")
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
        "Plans(tup=(CopyPlan(fields=('v', '_options')), EqPlan(fields=('v', '_options')), FrozenPlan(fields=('v', '_opt"
        "ions'), allow_dynamic_dunder_attrs=True), HashPlan(action='add', fields=('v', '_options'), cache=False), InitP"
        "lan(fields=(InitPlan.Field(name='v', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_"
        "factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type"
        "=None), InitPlan.Field(name='_options', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name="
        "'init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coer"
        "ce=OpRef(name='init.fields.1.coerce'), validate=None, check_type=None)), self_param='self', std_params=('v', '"
        "_options'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()),"
        " ReprPlan(fields=(ReprPlan.Field(name='v', kw_only=False, fn=None), ReprPlan.Field(name='_options', kw_only=Fa"
        "lse, fn=OpRef(name='repr.fns.1.fn'))), id=False, terse=True, default_fn=None)))"
    ),
    plan_repr_sha1='0023b16f6689ceccd2788050f6aa52d8eb36a4b3',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__coerce',
        '__dataclass__init__fields__1__default',
        '__dataclass__repr__fns__1__fn',
    ),
    cls_names=(
        ('ommlds.minichain.completion', 'Request'),
    ),
)
def _process_dataclass__0023b16f6689ceccd2788050f6aa52d8eb36a4b3():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__coerce,
        __dataclass__init__fields__1__default,
        __dataclass__repr__fns__1__fn,
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
                v=self.v,
                _options=self._options,
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
                self._options == other._options
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'v',
            '_options',
        }

        def __setattr__(self, name, value):
            if (
                (
                    type(self) is __dataclass__cls
                    and not (len(name) > 4 and name[:2] == name[-2:] == "__")
                )
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
            '_options',
        }

        def __delattr__(self, name):
            if (
                (
                    type(self) is __dataclass__cls
                    and not (len(name) > 4 and name[:2] == name[-2:] == "__")
                )
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
                self.v,
                self._options,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            v: __dataclass__init__fields__0__annotation,
            _options: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            _options = __dataclass__init__fields__1__coerce(_options)
            __dataclass__object_setattr(self, 'v', v)
            __dataclass__object_setattr(self, '_options', _options)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"{self.v!r}")
            if (s := __dataclass__repr__fns__1__fn(self._options)) is not None:
                parts.append(f"{s}")
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
        "Plans(tup=(CopyPlan(fields=('v', '_outputs')), EqPlan(fields=('v', '_outputs')), FrozenPlan(fields=('v', '_out"
        "puts'), allow_dynamic_dunder_attrs=True), HashPlan(action='add', fields=('v', '_outputs'), cache=False), InitP"
        "lan(fields=(InitPlan.Field(name='v', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_"
        "factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type"
        "=None), InitPlan.Field(name='_outputs', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name="
        "'init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coer"
        "ce=OpRef(name='init.fields.1.coerce'), validate=None, check_type=None)), self_param='self', std_params=('v', '"
        "_outputs'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()),"
        " ReprPlan(fields=(ReprPlan.Field(name='v', kw_only=False, fn=None), ReprPlan.Field(name='_outputs', kw_only=Fa"
        "lse, fn=OpRef(name='repr.fns.1.fn'))), id=False, terse=True, default_fn=None)))"
    ),
    plan_repr_sha1='c2386e505e36d7c0a884a75edc8c58926b6fae2c',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__coerce',
        '__dataclass__init__fields__1__default',
        '__dataclass__repr__fns__1__fn',
    ),
    cls_names=(
        ('ommlds.minichain.completion', 'Response'),
    ),
)
def _process_dataclass__c2386e505e36d7c0a884a75edc8c58926b6fae2c():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__coerce,
        __dataclass__init__fields__1__default,
        __dataclass__repr__fns__1__fn,
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
                v=self.v,
                _outputs=self._outputs,
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
                self._outputs == other._outputs
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'v',
            '_outputs',
        }

        def __setattr__(self, name, value):
            if (
                (
                    type(self) is __dataclass__cls
                    and not (len(name) > 4 and name[:2] == name[-2:] == "__")
                )
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
            '_outputs',
        }

        def __delattr__(self, name):
            if (
                (
                    type(self) is __dataclass__cls
                    and not (len(name) > 4 and name[:2] == name[-2:] == "__")
                )
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
                self.v,
                self._outputs,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            v: __dataclass__init__fields__0__annotation,
            _outputs: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            _outputs = __dataclass__init__fields__1__coerce(_outputs)
            __dataclass__object_setattr(self, 'v', v)
            __dataclass__object_setattr(self, '_outputs', _outputs)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"{self.v!r}")
            if (s := __dataclass__repr__fns__1__fn(self._outputs)) is not None:
                parts.append(f"{s}")
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
        "Plans(tup=(CopyPlan(fields=('service',)), EqPlan(fields=('service',)), FrozenPlan(fields=('service',), allow_d"
        "ynamic_dunder_attrs=True), HashPlan(action='add', fields=('service',), cache=False), InitPlan(fields=(InitPlan"
        ".Field(name='service', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, "
        "init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self"
        "_param='self', std_params=('service',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, in"
        "it_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='service', kw_only=False, fn=None),), id=Fal"
        "se, terse=True, default_fn=None)))"
    ),
    plan_repr_sha1='9582883e8b789fb5864ce555ef9d6348525b7c92',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.completion', 'ServiceFacade'),
    ),
)
def _process_dataclass__9582883e8b789fb5864ce555ef9d6348525b7c92():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                service=self.service,
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
                self.service == other.service
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'service',
        }

        def __setattr__(self, name, value):
            if (
                (
                    type(self) is __dataclass__cls
                    and not (len(name) > 4 and name[:2] == name[-2:] == "__")
                )
                 or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'service',
        }

        def __delattr__(self, name):
            if (
                (
                    type(self) is __dataclass__cls
                    and not (len(name) > 4 and name[:2] == name[-2:] == "__")
                )
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
                self.service,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            service: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'service', service)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"{self.service!r}")
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
        "Plans(tup=(CopyPlan(fields=('input', 'output', 'total')), EqPlan(fields=('input', 'output', 'total')), FrozenP"
        "lan(fields=('input', 'output', 'total'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('in"
        "put', 'output', 'total'), cache=False), InitPlan(fields=(InitPlan.Field(name='input', annotation=OpRef(name='i"
        "nit.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType"
        ".INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='output', annotation=OpRef(name='"
        "init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldTyp"
        "e.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='total', annotation=OpRef(name='"
        "init.fields.2.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldTyp"
        "e.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=('input', 'output', '"
        "total'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), Re"
        "prPlan(fields=(ReprPlan.Field(name='input', kw_only=False, fn=None), ReprPlan.Field(name='output', kw_only=Fal"
        "se, fn=None), ReprPlan.Field(name='total', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='9ed4b52f5bfcbb314cdfb3a8f1e9986b2f75afd2',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.completion', 'TokenUsage'),
    ),
)
def _process_dataclass__9ed4b52f5bfcbb314cdfb3a8f1e9986b2f75afd2():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
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
                input=self.input,
                output=self.output,
                total=self.total,
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
                self.input == other.input and
                self.output == other.output and
                self.total == other.total
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'input',
            'output',
            'total',
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
            'input',
            'output',
            'total',
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
                self.input,
                self.output,
                self.total,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            input: __dataclass__init__fields__0__annotation,
            output: __dataclass__init__fields__1__annotation,
            total: __dataclass__init__fields__2__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'input', input)
            __dataclass__object_setattr(self, 'output', output)
            __dataclass__object_setattr(self, 'total', total)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"input={self.input!r}")
            parts.append(f"output={self.output!r}")
            parts.append(f"total={self.total!r}")
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
        "Plans(tup=(CopyPlan(fields=('orig_class', 'rty', 'tv_types', 'tv_types_set')), EqPlan(fields=('orig_class', 'r"
        "ty', 'tv_types', 'tv_types_set')), FrozenPlan(fields=('orig_class', 'rty', 'tv_types', 'tv_types_set'), allow_"
        "dynamic_dunder_attrs=False), HashPlan(action='add', fields=('orig_class', 'rty', 'tv_types', 'tv_types_set'), "
        "cache=False), InitPlan(fields=(InitPlan.Field(name='orig_class', annotation=OpRef(name='init.fields.0.annotati"
        "on'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=Non"
        "e, validate=None, check_type=None), InitPlan.Field(name='rty', annotation=OpRef(name='init.fields.1.annotation"
        "'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None,"
        " validate=None, check_type=None), InitPlan.Field(name='tv_types', annotation=OpRef(name='init.fields.2.annotat"
        "ion'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=No"
        "ne, validate=None, check_type=None), InitPlan.Field(name='tv_types_set', annotation=OpRef(name='init.fields.3."
        "annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, co"
        "erce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('orig_class', '"
        "rty', 'tv_types', 'tv_types_set'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns="
        "()), ReprPlan(fields=(ReprPlan.Field(name='orig_class', kw_only=True, fn=None), ReprPlan.Field(name='rty', kw_"
        "only=True, fn=None), ReprPlan.Field(name='tv_types', kw_only=True, fn=None), ReprPlan.Field(name='tv_types_set"
        "', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='2e0ee5f871e01baad4d7b4595f08402a8e3c231d',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.completion', '_TypedValuesInfo'),
    ),
)
def _process_dataclass__2e0ee5f871e01baad4d7b4595f08402a8e3c231d():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__3__annotation,
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
                orig_class=self.orig_class,
                rty=self.rty,
                tv_types=self.tv_types,
                tv_types_set=self.tv_types_set,
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
                self.orig_class == other.orig_class and
                self.rty == other.rty and
                self.tv_types == other.tv_types and
                self.tv_types_set == other.tv_types_set
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'orig_class',
            'rty',
            'tv_types',
            'tv_types_set',
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
            'orig_class',
            'rty',
            'tv_types',
            'tv_types_set',
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
                self.orig_class,
                self.rty,
                self.tv_types,
                self.tv_types_set,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            orig_class: __dataclass__init__fields__0__annotation,
            rty: __dataclass__init__fields__1__annotation,
            tv_types: __dataclass__init__fields__2__annotation,
            tv_types_set: __dataclass__init__fields__3__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'orig_class', orig_class)
            __dataclass__object_setattr(self, 'rty', rty)
            __dataclass__object_setattr(self, 'tv_types', tv_types)
            __dataclass__object_setattr(self, 'tv_types_set', tv_types_set)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"orig_class={self.orig_class!r}")
            parts.append(f"rty={self.rty!r}")
            parts.append(f"tv_types={self.tv_types!r}")
            parts.append(f"tv_types_set={self.tv_types_set!r}")
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
        "Plans(tup=(CopyPlan(fields=('tv',)), EqPlan(fields=('tv',)), HashPlan(action='set_none', fields=None, cache=No"
        "ne), InitPlan(fields=(InitPlan.Field(name='tv', annotation=OpRef(name='init.fields.0.annotation'), default=Non"
        "e, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None,"
        " check_type=None),), self_param='self', std_params=('tv',), kw_only_params=(), frozen=False, slots=False, post"
        "_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='tv', kw_only=False, fn"
        "=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='31d6043cba49e8c3536c1fcec4a0a7878597293b',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.completion', '_TypedValuesTypeError'),
    ),
)
def _process_dataclass__31d6043cba49e8c3536c1fcec4a0a7878597293b():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                tv=self.tv,
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
                self.tv == other.tv
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        setattr(__dataclass__cls, '__hash__', None)

        def __init__(
            self,
            tv: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            self.tv = tv

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"tv={self.tv!r}")
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
        "Plans(tup=(CopyPlan(fields=('bt',)), EqPlan(fields=('bt',)), FrozenPlan(fields=('bt',), allow_dynamic_dunder_a"
        "ttrs=False), HashPlan(action='add', fields=('bt',), cache=False), InitPlan(fields=(InitPlan.Field(name='bt', a"
        "nnotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=Fals"
        "e, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self', std_param"
        "s=('bt',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), "
        "ReprPlan(fields=(ReprPlan.Field(name='bt', kw_only=False, fn=None),), id=False, terse=False, default_fn=None))"
        ")"
    ),
    plan_repr_sha1='067065e74081110c65541a65bb94b80602f53a97',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.content._marshal', '_ContentMarshaler'),
        ('ommlds.minichain.content._marshal', '_ContentUnmarshaler'),
    ),
)
def _process_dataclass__067065e74081110c65541a65bb94b80602f53a97():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                bt=self.bt,
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
                self.bt == other.bt
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'bt',
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
            'bt',
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
                self.bt,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            bt: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'bt', bt)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"bt={self.bt!r}")
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
        "Plans(tup=(CopyPlan(fields=('nst',)), EqPlan(fields=('nst',)), FrozenPlan(fields=('nst',), allow_dynamic_dunde"
        "r_attrs=False), HashPlan(action='add', fields=('nst',), cache=False), InitPlan(fields=(InitPlan.Field(name='ns"
        "t', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override"
        "=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self', std_"
        "params=('nst',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns"
        "=()), ReprPlan(fields=(ReprPlan.Field(name='nst', kw_only=False, fn=None),), id=False, terse=False, default_fn"
        "=None)))"
    ),
    plan_repr_sha1='7bd00bc183c33c685a7face5f89c35923e22df93',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.content._marshal', '_RawContentMarshaler'),
        ('ommlds.minichain.content._marshal', '_RawContentUnmarshaler'),
        ('ommlds.minichain.content._marshal', '_SingleRawContentMarshaler'),
        ('ommlds.minichain.content._marshal', '_SingleRawContentUnmarshaler'),
    ),
)
def _process_dataclass__7bd00bc183c33c685a7face5f89c35923e22df93():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                nst=self.nst,
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
                self.nst == other.nst
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'nst',
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
            'nst',
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
                self.nst,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            nst: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'nst', nst)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"nst={self.nst!r}")
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
        "Plans(tup=(CopyPlan(fields=('op', 'field', 'value')), EqPlan(fields=('op', 'field', 'value')), FrozenPlan(fiel"
        "ds=('op', 'field', 'value'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('op', 'field', "
        "'value'), cache=False), InitPlan(fields=(InitPlan.Field(name='op', annotation=OpRef(name='init.fields.0.annota"
        "tion'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=N"
        "one, validate=None, check_type=OpRef(name='init.fields.0.check_type')), InitPlan.Field(name='field', annotatio"
        "n=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field"
        "_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=OpRef(name='init.fields.1.check_type')), Init"
        "Plan.Field(name='value', annotation=OpRef(name='init.fields.2.annotation'), default=None, default_factory=None"
        ", init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), sel"
        "f_param='self', std_params=('op', 'field', 'value'), kw_only_params=(), frozen=True, slots=False, post_init_pa"
        "rams=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='op', kw_only=False, fn=None), "
        "ReprPlan.Field(name='field', kw_only=False, fn=None), ReprPlan.Field(name='value', kw_only=False, fn=None)), i"
        "d=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='79ca9cb99a2a338ac1df5f86d497bd9b5fe5274b',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__check_type',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__check_type',
        '__dataclass__init__fields__2__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.docs', 'Cmp'),
    ),
)
def _process_dataclass__79ca9cb99a2a338ac1df5f86d497bd9b5fe5274b():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__check_type,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__check_type,
        __dataclass__init__fields__2__annotation,
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
                op=self.op,
                field=self.field,
                value=self.value,
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
                self.op == other.op and
                self.field == other.field and
                self.value == other.value
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'op',
            'field',
            'value',
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
            'op',
            'field',
            'value',
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
                self.op,
                self.field,
                self.value,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            op: __dataclass__init__fields__0__annotation,
            field: __dataclass__init__fields__1__annotation,
            value: __dataclass__init__fields__2__annotation,
        ) -> __dataclass__None:
            if not __dataclass__isinstance(op, __dataclass__init__fields__0__check_type): 
                raise __dataclass__FieldTypeValidationError(
                    obj=self,
                    type=__dataclass__init__fields__0__check_type,
                    field='op',
                    value=op,
                )
            if not __dataclass__isinstance(field, __dataclass__init__fields__1__check_type): 
                raise __dataclass__FieldTypeValidationError(
                    obj=self,
                    type=__dataclass__init__fields__1__check_type,
                    field='field',
                    value=field,
                )
            __dataclass__object_setattr(self, 'op', op)
            __dataclass__object_setattr(self, 'field', field)
            __dataclass__object_setattr(self, 'value', value)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"op={self.op!r}")
            parts.append(f"field={self.field!r}")
            parts.append(f"value={self.value!r}")
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
        "Plans(tup=(CopyPlan(fields=('values',)), EqPlan(fields=('values',)), FrozenPlan(fields=('values',), allow_dyna"
        "mic_dunder_attrs=False), HashPlan(action='add', fields=('values',), cache=False), InitPlan(fields=(InitPlan.Fi"
        "eld(name='values', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init"
        "=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_par"
        "am='self', std_params=('values',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fn"
        "s=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='values', kw_only=False, fn=None),), id=False, te"
        "rse=False, default_fn=None)))"
    ),
    plan_repr_sha1='a7abe5eeac180c2c591f3d3a53805368068716bd',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.docs', 'Doc'),
    ),
)
def _process_dataclass__a7abe5eeac180c2c591f3d3a53805368068716bd():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                values=self.values,
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
                self.values == other.values
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'values',
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
            'values',
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
                self.values,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            values: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'values', values)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"values={self.values!r}")
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
        "Plans(tup=(CopyPlan(fields=('name', 'dtype')), EqPlan(fields=('name', 'dtype')), FrozenPlan(fields=('name', 'd"
        "type'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('name', 'dtype'), cache=False), Init"
        "Plan(fields=(InitPlan.Field(name='name', annotation=OpRef(name='init.fields.0.annotation'), default=None, defa"
        "ult_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_"
        "type=None), InitPlan.Field(name='dtype', annotation=OpRef(name='init.fields.1.annotation'), default=None, defa"
        "ult_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_"
        "type=None)), self_param='self', std_params=('name', 'dtype'), kw_only_params=(), frozen=True, slots=False, pos"
        "t_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='name', kw_only=False,"
        " fn=None), ReprPlan.Field(name='dtype', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='701ed985cfa822fc06c63b453395b927805fd829',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.docs', 'DocField'),
    ),
)
def _process_dataclass__701ed985cfa822fc06c63b453395b927805fd829():
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
                dtype=self.dtype,
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
                self.dtype == other.dtype
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'name',
            'dtype',
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
            'dtype',
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
                self.dtype,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            name: __dataclass__init__fields__0__annotation,
            dtype: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'dtype', dtype)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"name={self.name!r}")
            parts.append(f"dtype={self.dtype!r}")
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
        "Plans(tup=(CopyPlan(fields=('fields',)), EqPlan(fields=('fields',)), FrozenPlan(fields=('fields',), allow_dyna"
        "mic_dunder_attrs=False), HashPlan(action='add', fields=('fields',), cache=False), InitPlan(fields=(InitPlan.Fi"
        "eld(name='fields', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init"
        "=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=OpRef(name='init.fields.0.validate"
        "'), check_type=None),), self_param='self', std_params=('fields',), kw_only_params=(), frozen=True, slots=False"
        ", post_init_params=None, init_fns=(OpRef(name='init.init_fns.0'),), validate_fns=()), ReprPlan(fields=(ReprPla"
        "n.Field(name='fields', kw_only=False, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='bb990d6af2fbcbd6d1da7c8137c2544acd358e50',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__validate',
        '__dataclass__init__init_fns__0',
    ),
    cls_names=(
        ('ommlds.minichain.docs', 'DocSchema'),
    ),
)
def _process_dataclass__bb990d6af2fbcbd6d1da7c8137c2544acd358e50():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__validate,
        __dataclass__init__init_fns__0,
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
                fields=self.fields,
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
                self.fields == other.fields
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'fields',
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
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            fields: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            if not __dataclass__init__fields__0__validate(fields): 
                raise __dataclass__FieldFnValidationError(
                    obj=self,
                    fn=__dataclass__init__fields__0__validate,
                    field='fields',
                    value=fields,
                )
            __dataclass__object_setattr(self, 'fields', fields)
            __dataclass__init__init_fns__0(self)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"fields={self.fields!r}")
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
        "Plans(tup=(CopyPlan(fields=('name', 'cls', 'primitive')), EqPlan(fields=('name', 'cls', 'primitive')), FrozenP"
        "lan(fields=('name', 'cls', 'primitive'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('na"
        "me', 'cls', 'primitive'), cache=False), InitPlan(fields=(InitPlan.Field(name='name', annotation=OpRef(name='in"
        "it.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType."
        "INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='cls', annotation=OpRef(name='init"
        ".fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.IN"
        "STANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='primitive', annotation=OpRef(name='"
        "init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, over"
        "ride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', s"
        "td_params=('name', 'cls'), kw_only_params=('primitive',), frozen=True, slots=False, post_init_params=None, ini"
        "t_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='name', kw_only=False, fn=None), ReprPlan.Fie"
        "ld(name='cls', kw_only=False, fn=None), ReprPlan.Field(name='primitive', kw_only=True, fn=None)), id=False, te"
        "rse=False, default_fn=None)))"
    ),
    plan_repr_sha1='bd59138317a2d7c95911cd942d22c39a5dbc6ce9',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.minichain.docs', 'Dtype'),
    ),
)
def _process_dataclass__bd59138317a2d7c95911cd942d22c39a5dbc6ce9():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
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
                cls=self.cls,
                primitive=self.primitive,
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
                self.cls == other.cls and
                self.primitive == other.primitive
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'name',
            'cls',
            'primitive',
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
            'cls',
            'primitive',
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
                self.cls,
                self.primitive,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            name: __dataclass__init__fields__0__annotation,
            cls: __dataclass__init__fields__1__annotation,
            *,
            primitive: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'cls', cls)
            __dataclass__object_setattr(self, 'primitive', primitive)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"name={self.name!r}")
            parts.append(f"cls={self.cls!r}")
            parts.append(f"primitive={self.primitive!r}")
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
        "Plans(tup=(CopyPlan(fields=('n',)), EqPlan(fields=('n',)), FrozenPlan(fields=('n',), allow_dynamic_dunder_attr"
        "s=False), HashPlan(action='add', fields=('n',), cache=False), InitPlan(fields=(InitPlan.Field(name='n', annota"
        "tion=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, fi"
        "eld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=OpRef(name='init.fields.0.check_type')),),"
        " self_param='self', std_params=('n',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, ini"
        "t_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='n', kw_only=False, fn=None),), id=False, ter"
        "se=False, default_fn=None)))"
    ),
    plan_repr_sha1='d634aaef3ca82b3d7f0a9842bfaeb2af08fdcd83',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__check_type',
    ),
    cls_names=(
        ('ommlds.minichain.docs', 'FieldRef'),
    ),
)
def _process_dataclass__d634aaef3ca82b3d7f0a9842bfaeb2af08fdcd83():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__check_type,
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
                n=self.n,
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
                self.n == other.n
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'n',
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
            'n',
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
                self.n,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            n: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            if not __dataclass__isinstance(n, __dataclass__init__fields__0__check_type): 
                raise __dataclass__FieldTypeValidationError(
                    obj=self,
                    type=__dataclass__init__fields__0__check_type,
                    field='n',
                    value=n,
                )
            __dataclass__object_setattr(self, 'n', n)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"n={self.n!r}")
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
        "Plans(tup=(CopyPlan(fields=('op', 'children')), EqPlan(fields=('op', 'children')), FrozenPlan(fields=('op', 'c"
        "hildren'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('op', 'children'), cache=False), "
        "InitPlan(fields=(InitPlan.Field(name='op', annotation=OpRef(name='init.fields.0.annotation'), default=None, de"
        "fault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, chec"
        "k_type=OpRef(name='init.fields.0.check_type')), InitPlan.Field(name='children', annotation=OpRef(name='init.fi"
        "elds.1.annotation'), default=None, default_factory=None, init=True, override=True, field_type=FieldType.INSTAN"
        "CE, coerce=None, validate=OpRef(name='init.fields.1.validate'), check_type=None)), self_param='self', std_para"
        "ms=('op', 'children'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), valida"
        "te_fns=()), OverridePlan(fields=(OverridePlan.Field(name='children', annotation=OpRef(name='override.fields.1."
        "annotation')),), frozen=True), ReprPlan(fields=(ReprPlan.Field(name='op', kw_only=False, fn=None), ReprPlan.Fi"
        "eld(name='children', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='6c09a6beb5d85cdd42b177414c303bc876b420da',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__check_type',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__validate',
        '__dataclass__override__fields__1__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.docs', 'MultiFilter'),
    ),
)
def _process_dataclass__6c09a6beb5d85cdd42b177414c303bc876b420da():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__check_type,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__validate,
        __dataclass__override__fields__1__annotation,
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
                op=self.op,
                children=self.children,
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
                self.op == other.op and
                self.children == other.children
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'op',
            'children',
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
            'op',
            'children',
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
                self.op,
                self.children,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            op: __dataclass__init__fields__0__annotation,
            children: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            if not __dataclass__isinstance(op, __dataclass__init__fields__0__check_type): 
                raise __dataclass__FieldTypeValidationError(
                    obj=self,
                    type=__dataclass__init__fields__0__check_type,
                    field='op',
                    value=op,
                )
            if not __dataclass__init__fields__1__validate(children): 
                raise __dataclass__FieldFnValidationError(
                    obj=self,
                    fn=__dataclass__init__fields__1__validate,
                    field='children',
                    value=children,
                )
            __dataclass__object_setattr(self, 'op', op)
            __dataclass__self_dict = self.__dict__
            __dataclass__self_dict['children'] = children

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        def __dataclass__property__children():
            @__dataclass__property
            def children(__dataclass__self) -> __dataclass__override__fields__1__annotation:
                return __dataclass__self.__dict__['children']

            return children

        setattr(__dataclass__cls, 'children', __dataclass__property__children())

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"op={self.op!r}")
            parts.append(f"children={self.children!r}")
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
        "Plans(tup=(CopyPlan(fields=('child',)), EqPlan(fields=('child',)), FrozenPlan(fields=('child',), allow_dynamic"
        "_dunder_attrs=False), HashPlan(action='add', fields=('child',), cache=False), InitPlan(fields=(InitPlan.Field("
        "name='child', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True"
        ", override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=OpRef(name='init.field"
        "s.0.check_type')),), self_param='self', std_params=('child',), kw_only_params=(), frozen=True, slots=False, po"
        "st_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='child', kw_only=Fals"
        "e, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='41479800d543a13021d10abebe38c460252c0c73',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__check_type',
    ),
    cls_names=(
        ('ommlds.minichain.docs', 'Not'),
    ),
)
def _process_dataclass__41479800d543a13021d10abebe38c460252c0c73():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__check_type,
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
                child=self.child,
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
                self.child == other.child
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'child',
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
            'child',
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
                self.child,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            child: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            if not __dataclass__isinstance(child, __dataclass__init__fields__0__check_type): 
                raise __dataclass__FieldTypeValidationError(
                    obj=self,
                    type=__dataclass__init__fields__0__check_type,
                    field='child',
                    value=child,
                )
            __dataclass__object_setattr(self, 'child', child)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"child={self.child!r}")
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
        "Plans(tup=(CopyPlan(fields=('spec', 'target', 'name_override')), FrozenPlan(fields=('spec', 'target', 'name_ov"
        "erride'), allow_dynamic_dunder_attrs=False), InitPlan(fields=(InitPlan.Field(name='spec', annotation=OpRef(nam"
        "e='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=Field"
        "Type.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='target', annotation=OpRef(na"
        "me='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=Fiel"
        "dType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='name_override', annotation="
        "OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, ini"
        "t=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_par"
        "am='self', std_params=('spec', 'target'), kw_only_params=('name_override',), frozen=True, slots=False, post_in"
        "it_params=(), init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='spec', kw_only=False, fn=No"
        "ne), ReprPlan.Field(name='target', kw_only=False, fn=None), ReprPlan.Field(name='name_override', kw_only=True,"
        " fn=OpRef(name='repr.fns.2.fn'))), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='f92c2b600e9ab772595277d8dcfde959106424fb',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__repr__fns__2__fn',
    ),
    cls_names=(
        ('ommlds.minichain.lib.bash', 'ToolCatalogEntry'),
    ),
)
def _process_dataclass__f92c2b600e9ab772595277d8dcfde959106424fb():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
        __dataclass__repr__fns__2__fn,
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
                spec=self.spec,
                target=self.target,
                name_override=self.name_override,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        __dataclass___setattr_frozen_fields = {
            'spec',
            'target',
            'name_override',
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
            'spec',
            'target',
            'name_override',
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
            spec: __dataclass__init__fields__0__annotation,
            target: __dataclass__init__fields__1__annotation,
            *,
            name_override: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'spec', spec)
            __dataclass__object_setattr(self, 'target', target)
            __dataclass__object_setattr(self, 'name_override', name_override)
            self.__post_init__()

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"spec={self.spec!r}")
            parts.append(f"target={self.target!r}")
            if (s := __dataclass__repr__fns__2__fn(self.name_override)) is not None:
                parts.append(f"name_override={s}")
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
        "Plans(tup=(CopyPlan(fields=('name', 'path', 'children')), EqPlan(fields=('name', 'path', 'children')), FrozenP"
        "lan(fields=('name', 'path', 'children'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('na"
        "me', 'path', 'children'), cache=False), InitPlan(fields=(InitPlan.Field(name='name', annotation=OpRef(name='in"
        "it.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType."
        "INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='path', annotation=OpRef(name='ini"
        "t.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.I"
        "NSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='children', annotation=OpRef(name='"
        "init.fields.2.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldTyp"
        "e.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=('name', 'path', 'chi"
        "ldren'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), Re"
        "prPlan(fields=(ReprPlan.Field(name='name', kw_only=False, fn=None), ReprPlan.Field(name='path', kw_only=False,"
        " fn=None), ReprPlan.Field(name='children', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='8fc7babd1081656cee23d33050b77c4791d93c20',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.lib.fs.tools.recursivels.execution', 'DirLsItem'),
    ),
)
def _process_dataclass__8fc7babd1081656cee23d33050b77c4791d93c20():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
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
                path=self.path,
                children=self.children,
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
                self.path == other.path and
                self.children == other.children
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'name',
            'path',
            'children',
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
            'path',
            'children',
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
                self.path,
                self.children,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            name: __dataclass__init__fields__0__annotation,
            path: __dataclass__init__fields__1__annotation,
            children: __dataclass__init__fields__2__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'path', path)
            __dataclass__object_setattr(self, 'children', children)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"name={self.name!r}")
            parts.append(f"path={self.path!r}")
            parts.append(f"children={self.children!r}")
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
        "Plans(tup=(CopyPlan(fields=('name', 'path')), EqPlan(fields=('name', 'path')), FrozenPlan(fields=('name', 'pat"
        "h'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('name', 'path'), cache=False), InitPlan"
        "(fields=(InitPlan.Field(name='name', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_"
        "factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type"
        "=None), InitPlan.Field(name='path', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_f"
        "actory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type="
        "None)), self_param='self', std_params=('name', 'path'), kw_only_params=(), frozen=True, slots=False, post_init"
        "_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='name', kw_only=False, fn=No"
        "ne), ReprPlan.Field(name='path', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='9a639e5124ba99ab9dbe43d0f65a5795e369a423',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.lib.fs.tools.recursivels.execution', 'FileLsItem'),
        ('ommlds.minichain.lib.fs.tools.recursivels.execution', 'LsItem'),
    ),
)
def _process_dataclass__9a639e5124ba99ab9dbe43d0f65a5795e369a423():
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
                path=self.path,
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
                self.path == other.path
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'name',
            'path',
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
            'path',
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
                self.path,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            name: __dataclass__init__fields__0__annotation,
            path: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'path', path)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"name={self.name!r}")
            parts.append(f"path={self.path!r}")
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
        "Plans(tup=(CopyPlan(fields=('item', 'd', 's', 'children')), InitPlan(fields=(InitPlan.Field(name='item', annot"
        "ation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, f"
        "ield_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='d', annotatio"
        "n=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field"
        "_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='s', annotation=Op"
        "Ref(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init="
        "True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fi"
        "eld(name='children', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.defa"
        "ult'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=N"
        "one, check_type=None)), self_param='self', std_params=('item', 'd'), kw_only_params=('s', 'children'), frozen="
        "False, slots=False, post_init_params=None, init_fns=(), validate_fns=())))"
    ),
    plan_repr_sha1='0ffe7e6981ca897a53904accd1fc4d5bb759d34b',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ommlds.minichain.lib.fs.tools.recursivels.execution', '_LsLine'),
    ),
)
def _process_dataclass__0ffe7e6981ca897a53904accd1fc4d5bb759d34b():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__3__default,
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
                item=self.item,
                d=self.d,
                s=self.s,
                children=self.children,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __init__(
            self,
            item: __dataclass__init__fields__0__annotation,
            d: __dataclass__init__fields__1__annotation,
            *,
            s: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            children: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            self.item = item
            self.d = d
            self.s = s
            self.children = children

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('root', 'soft_max_len')), EqPlan(fields=('root', 'soft_max_len')), HashPlan(action"
        "='set_none', fields=None, cache=None), InitPlan(fields=(InitPlan.Field(name='root', annotation=OpRef(name='ini"
        "t.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.I"
        "NSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='soft_max_len', annotation=OpRef(na"
        "me='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, "
        "override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self"
        "', std_params=('root',), kw_only_params=('soft_max_len',), frozen=False, slots=False, post_init_params=None, i"
        "nit_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='root', kw_only=False, fn=None), ReprPlan.F"
        "ield(name='soft_max_len', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='68ec51656ec2810b10c4b88f8e5fa731750d733f',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.minichain.lib.fs.tools.recursivels.execution', '_LsRenderRun'),
    ),
)
def _process_dataclass__68ec51656ec2810b10c4b88f8e5fa731750d733f():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
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
                root=self.root,
                soft_max_len=self.soft_max_len,
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
                self.soft_max_len == other.soft_max_len
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        setattr(__dataclass__cls, '__hash__', None)

        def __init__(
            self,
            root: __dataclass__init__fields__0__annotation,
            *,
            soft_max_len: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            self.root = root
            self.soft_max_len = soft_max_len

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"root={self.root!r}")
            parts.append(f"soft_max_len={self.soft_max_len!r}")
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
        "Plans(tup=(CopyPlan(fields=('id', 'content', 'priority', 'status')), EqPlan(fields=('id', 'content', 'priority"
        "', 'status')), FrozenPlan(fields=('id', 'content', 'priority', 'status'), allow_dynamic_dunder_attrs=False), H"
        "ashPlan(action='add', fields=('id', 'content', 'priority', 'status'), cache=False), InitPlan(fields=(InitPlan."
        "Field(name='id', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'"
        "), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None,"
        " check_type=None), InitPlan.Field(name='content', annotation=OpRef(name='init.fields.1.annotation'), default=N"
        "one, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=Non"
        "e, check_type=None), InitPlan.Field(name='priority', annotation=OpRef(name='init.fields.2.annotation'), defaul"
        "t=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate="
        "None, check_type=None), InitPlan.Field(name='status', annotation=OpRef(name='init.fields.3.annotation'), defau"
        "lt=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate"
        "=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('id', 'content', 'priority', 'stat"
        "us'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPla"
        "n.Field(name='id', kw_only=True, fn=None), ReprPlan.Field(name='content', kw_only=True, fn=None), ReprPlan.Fie"
        "ld(name='priority', kw_only=True, fn=None), ReprPlan.Field(name='status', kw_only=True, fn=None)), id=False, t"
        "erse=False, default_fn=None)))"
    ),
    plan_repr_sha1='90327d7499fc348378f37c29946fda05f802116e',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.lib.todo.context', 'TodoItem'),
    ),
)
def _process_dataclass__90327d7499fc348378f37c29946fda05f802116e():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__3__annotation,
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
                id=self.id,
                content=self.content,
                priority=self.priority,
                status=self.status,
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
                self.id == other.id and
                self.content == other.content and
                self.priority == other.priority and
                self.status == other.status
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'id',
            'content',
            'priority',
            'status',
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
            'content',
            'priority',
            'status',
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
                self.content,
                self.priority,
                self.status,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            id: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            content: __dataclass__init__fields__1__annotation,
            priority: __dataclass__init__fields__2__annotation,
            status: __dataclass__init__fields__3__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'content', content)
            __dataclass__object_setattr(self, 'priority', priority)
            __dataclass__object_setattr(self, 'status', status)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"id={self.id!r}")
            parts.append(f"content={self.content!r}")
            parts.append(f"priority={self.priority!r}")
            parts.append(f"status={self.status!r}")
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
        "Plans(tup=(CopyPlan(fields=('e',)), EqPlan(fields=('e',)), FrozenPlan(fields=('e',), allow_dynamic_dunder_attr"
        "s=False), HashPlan(action='add', fields=('e',), cache=False), InitPlan(fields=(InitPlan.Field(name='e', annota"
        "tion=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, fi"
        "eld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self', std_params=('e"
        "',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPl"
        "an(fields=(ReprPlan.Field(name='e', kw_only=False, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='09d620230085f2ec30d46bc47d392ca3f53879f5',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.meta.firstinwins', 'FirstInWinsServiceCancelledError'),
    ),
)
def _process_dataclass__09d620230085f2ec30d46bc47d392ca3f53879f5():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                e=self.e,
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
                self.e == other.e
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'e',
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
            'e',
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
                self.e,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            e: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'e', e)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"e={self.e!r}")
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
        "Plans(tup=(CopyPlan(fields=('first_in_wins_service', 'response_service', 'service_exceptions')), EqPlan(fields"
        "=('first_in_wins_service', 'response_service', 'service_exceptions')), FrozenPlan(fields=('first_in_wins_servi"
        "ce', 'response_service', 'service_exceptions'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fiel"
        "ds=('first_in_wins_service', 'response_service', 'service_exceptions'), cache=False), InitPlan(fields=(InitPla"
        "n.Field(name='first_in_wins_service', annotation=OpRef(name='init.fields.0.annotation'), default=None, default"
        "_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_typ"
        "e=None), InitPlan.Field(name='response_service', annotation=OpRef(name='init.fields.1.annotation'), default=No"
        "ne, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None"
        ", check_type=None), InitPlan.Field(name='service_exceptions', annotation=OpRef(name='init.fields.2.annotation'"
        "), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=Fi"
        "eldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=('first_in_wins"
        "_service', 'response_service', 'service_exceptions'), kw_only_params=(), frozen=True, slots=False, post_init_p"
        "arams=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='first_in_wins_service', kw_on"
        "ly=False, fn=None), ReprPlan.Field(name='response_service', kw_only=False, fn=None), ReprPlan.Field(name='serv"
        "ice_exceptions', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='338ef6c7e8d95c07d43101aa3fb2e5001c70b0ab',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.minichain.meta.firstinwins', 'FirstInWinsServiceOutput'),
    ),
)
def _process_dataclass__338ef6c7e8d95c07d43101aa3fb2e5001c70b0ab():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
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
                first_in_wins_service=self.first_in_wins_service,
                response_service=self.response_service,
                service_exceptions=self.service_exceptions,
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
                self.first_in_wins_service == other.first_in_wins_service and
                self.response_service == other.response_service and
                self.service_exceptions == other.service_exceptions
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'first_in_wins_service',
            'response_service',
            'service_exceptions',
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
            'first_in_wins_service',
            'response_service',
            'service_exceptions',
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
                self.first_in_wins_service,
                self.response_service,
                self.service_exceptions,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            first_in_wins_service: __dataclass__init__fields__0__annotation,
            response_service: __dataclass__init__fields__1__annotation,
            service_exceptions: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'first_in_wins_service', first_in_wins_service)
            __dataclass__object_setattr(self, 'response_service', response_service)
            __dataclass__object_setattr(self, 'service_exceptions', service_exceptions)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"first_in_wins_service={self.first_in_wins_service!r}")
            parts.append(f"response_service={self.response_service!r}")
            parts.append(f"service_exceptions={self.service_exceptions!r}")
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
        "Plans(tup=(CopyPlan(fields=('title', 'url', 'description', 'snippets')), EqPlan(fields=('title', 'url', 'descr"
        "iption', 'snippets')), FrozenPlan(fields=('title', 'url', 'description', 'snippets'), allow_dynamic_dunder_att"
        "rs=False), HashPlan(action='add', fields=('title', 'url', 'description', 'snippets'), cache=False), InitPlan(f"
        "ields=(InitPlan.Field(name='title', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_f"
        "actory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type="
        "None), InitPlan.Field(name='url', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_fac"
        "tory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=No"
        "ne), InitPlan.Field(name='description', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name="
        "'init.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coer"
        "ce=None, validate=None, check_type=None), InitPlan.Field(name='snippets', annotation=OpRef(name='init.fields.3"
        ".annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, f"
        "ield_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(),"
        " kw_only_params=('title', 'url', 'description', 'snippets'), frozen=True, slots=False, post_init_params=None, "
        "init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='title', kw_only=True, fn=None), ReprPlan."
        "Field(name='url', kw_only=True, fn=None), ReprPlan.Field(name='description', kw_only=True, fn=None), ReprPlan."
        "Field(name='snippets', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='f8383b0455fb7c3ce8ec3dace2df263307387c53',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ommlds.minichain.search', 'SearchHit'),
    ),
)
def _process_dataclass__f8383b0455fb7c3ce8ec3dace2df263307387c53():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__3__default,
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
                url=self.url,
                description=self.description,
                snippets=self.snippets,
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
                self.url == other.url and
                self.description == other.description and
                self.snippets == other.snippets
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'title',
            'url',
            'description',
            'snippets',
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
            'url',
            'description',
            'snippets',
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
                self.url,
                self.description,
                self.snippets,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            title: __dataclass__init__fields__0__annotation,
            url: __dataclass__init__fields__1__annotation,
            description: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            snippets: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'title', title)
            __dataclass__object_setattr(self, 'url', url)
            __dataclass__object_setattr(self, 'description', description)
            __dataclass__object_setattr(self, 'snippets', snippets)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"title={self.title!r}")
            parts.append(f"url={self.url!r}")
            parts.append(f"description={self.description!r}")
            parts.append(f"snippets={self.snippets!r}")
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
        "Plans(tup=(CopyPlan(fields=('l', 'total_results')), EqPlan(fields=('l', 'total_results')), FrozenPlan(fields=("
        "'l', 'total_results'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('l', 'total_results')"
        ", cache=False), InitPlan(fields=(InitPlan.Field(name='l', annotation=OpRef(name='init.fields.0.annotation'), d"
        "efault=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, vali"
        "date=None, check_type=None), InitPlan.Field(name='total_results', annotation=OpRef(name='init.fields.1.annotat"
        "ion'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_typ"
        "e=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only"
        "_params=('l', 'total_results'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=())"
        ", ReprPlan(fields=(ReprPlan.Field(name='l', kw_only=True, fn=None), ReprPlan.Field(name='total_results', kw_on"
        "ly=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='c5ebc75df7787604091e8a5696458c845a88b433',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.minichain.search', 'SearchHits'),
    ),
)
def _process_dataclass__c5ebc75df7787604091e8a5696458c845a88b433():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
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
                l=self.l,
                total_results=self.total_results,
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
                self.l == other.l and
                self.total_results == other.total_results
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'l',
            'total_results',
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
            'l',
            'total_results',
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
                self.l,
                self.total_results,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            l: __dataclass__init__fields__0__annotation,
            total_results: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'l', l)
            __dataclass__object_setattr(self, 'total_results', total_results)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"l={self.l!r}")
            parts.append(f"total_results={self.total_results!r}")
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
        "Plans(tup=(CopyPlan(fields=('rty', 'tv_fld', 'v_m')), EqPlan(fields=('rty', 'tv_fld', 'v_m')), FrozenPlan(fiel"
        "ds=('rty', 'tv_fld', 'v_m'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('rty', 'tv_fld'"
        ", 'v_m'), cache=False), InitPlan(fields=(InitPlan.Field(name='rty', annotation=OpRef(name='init.fields.0.annot"
        "ation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce="
        "None, validate=None, check_type=None), InitPlan.Field(name='tv_fld', annotation=OpRef(name='init.fields.1.anno"
        "tation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce"
        "=None, validate=None, check_type=None), InitPlan.Field(name='v_m', annotation=OpRef(name='init.fields.2.annota"
        "tion'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=N"
        "one, validate=None, check_type=None)), self_param='self', std_params=('rty', 'tv_fld', 'v_m'), kw_only_params="
        "(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan."
        "Field(name='rty', kw_only=False, fn=None), ReprPlan.Field(name='tv_fld', kw_only=False, fn=None), ReprPlan.Fie"
        "ld(name='v_m', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='3351f2836d3548cfa09118e14f4aabcde84625f4',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.services._marshal', '_RequestResponseMarshaler'),
    ),
)
def _process_dataclass__3351f2836d3548cfa09118e14f4aabcde84625f4():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
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
                rty=self.rty,
                tv_fld=self.tv_fld,
                v_m=self.v_m,
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
                self.rty == other.rty and
                self.tv_fld == other.tv_fld and
                self.v_m == other.v_m
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'rty',
            'tv_fld',
            'v_m',
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
            'rty',
            'tv_fld',
            'v_m',
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
                self.rty,
                self.tv_fld,
                self.v_m,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            rty: __dataclass__init__fields__0__annotation,
            tv_fld: __dataclass__init__fields__1__annotation,
            v_m: __dataclass__init__fields__2__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'rty', rty)
            __dataclass__object_setattr(self, 'tv_fld', tv_fld)
            __dataclass__object_setattr(self, 'v_m', v_m)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"rty={self.rty!r}")
            parts.append(f"tv_fld={self.tv_fld!r}")
            parts.append(f"v_m={self.v_m!r}")
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
        "Plans(tup=(CopyPlan(fields=('rty', 'tv_fld', 'v_u', 'tv_u')), EqPlan(fields=('rty', 'tv_fld', 'v_u', 'tv_u')),"
        " FrozenPlan(fields=('rty', 'tv_fld', 'v_u', 'tv_u'), allow_dynamic_dunder_attrs=False), HashPlan(action='add',"
        " fields=('rty', 'tv_fld', 'v_u', 'tv_u'), cache=False), InitPlan(fields=(InitPlan.Field(name='rty', annotation"
        "=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_"
        "type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='tv_fld', annotatio"
        "n=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field"
        "_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='v_u', annotation="
        "OpRef(name='init.fields.2.annotation'), default=None, default_factory=None, init=True, override=False, field_t"
        "ype=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='tv_u', annotation=O"
        "pRef(name='init.fields.3.annotation'), default=None, default_factory=None, init=True, override=False, field_ty"
        "pe=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=('rty', 't"
        "v_fld', 'v_u', 'tv_u'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), valid"
        "ate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='rty', kw_only=False, fn=None), ReprPlan.Field(name='tv_fld'"
        ", kw_only=False, fn=None), ReprPlan.Field(name='v_u', kw_only=False, fn=None), ReprPlan.Field(name='tv_u', kw_"
        "only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='48fce044c70087260e75d4a7c33663b383fb8b2a',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.services._marshal', '_RequestResponseUnmarshaler'),
    ),
)
def _process_dataclass__48fce044c70087260e75d4a7c33663b383fb8b2a():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__3__annotation,
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
                rty=self.rty,
                tv_fld=self.tv_fld,
                v_u=self.v_u,
                tv_u=self.tv_u,
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
                self.rty == other.rty and
                self.tv_fld == other.tv_fld and
                self.v_u == other.v_u and
                self.tv_u == other.tv_u
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'rty',
            'tv_fld',
            'v_u',
            'tv_u',
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
            'rty',
            'tv_fld',
            'v_u',
            'tv_u',
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
                self.rty,
                self.tv_fld,
                self.v_u,
                self.tv_u,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            rty: __dataclass__init__fields__0__annotation,
            tv_fld: __dataclass__init__fields__1__annotation,
            v_u: __dataclass__init__fields__2__annotation,
            tv_u: __dataclass__init__fields__3__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'rty', rty)
            __dataclass__object_setattr(self, 'tv_fld', tv_fld)
            __dataclass__object_setattr(self, 'v_u', v_u)
            __dataclass__object_setattr(self, 'tv_u', tv_u)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"rty={self.rty!r}")
            parts.append(f"tv_fld={self.tv_fld!r}")
            parts.append(f"v_u={self.v_u!r}")
            parts.append(f"tv_u={self.tv_u!r}")
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
        "Plans(tup=(CopyPlan(fields=('v',)), EqPlan(fields=('v',)), FrozenPlan(fields=('v',), allow_dynamic_dunder_attr"
        "s=False), HashPlan(action='add', fields=('v',), cache=False), InitPlan(fields=(InitPlan.Field(name='v', annota"
        "tion=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, fi"
        "eld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self', std_params=('v"
        "',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(OpRef(name='init.init_fns.0"
        "'),), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='v', kw_only=False, fn=None),), id=False, terse=T"
        "rue, default_fn=None)))"
    ),
    plan_repr_sha1='51fa5d3a6be91e1d96445ebeeacacf7a64173c0a',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__init_fns__0',
    ),
    cls_names=(
        ('ommlds.minichain.standard', 'DefaultOptions'),
    ),
)
def _process_dataclass__51fa5d3a6be91e1d96445ebeeacacf7a64173c0a():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__init_fns__0,
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
            return hash((
                self.v,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            v: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'v', v)
            __dataclass__init__init_fns__0(self)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"{self.v!r}")
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
        "Plans(tup=(CopyPlan(fields=('v',)), EqPlan(fields=('v',)), FrozenPlan(fields=('v',), allow_dynamic_dunder_attr"
        "s=False), HashPlan(action='add', fields=('v',), cache=False), InitPlan(fields=(InitPlan.Field(name='v', annota"
        "tion=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, fi"
        "eld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self', std_params=('v"
        "',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPl"
        "an(fields=(ReprPlan.Field(name='v', kw_only=False, fn=OpRef(name='repr.fns.0.fn')),), id=False, terse=False, d"
        "efault_fn=None)))"
    ),
    plan_repr_sha1='10841bf976c6bfcd0f71cfa59b935fcc98fe5d92',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__repr__fns__0__fn',
    ),
    cls_names=(
        ('ommlds.minichain.standard', 'SecretConfig'),
    ),
)
def _process_dataclass__10841bf976c6bfcd0f71cfa59b935fcc98fe5d92():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__repr__fns__0__fn,
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
            return hash((
                self.v,
            ))

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
            if (s := __dataclass__repr__fns__0__fn(self.v)) is not None:
                parts.append(f"v={s}")
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
        "Plans(tup=(CopyPlan(fields=('orig_index', 'del_lines', 'ins_lines')), EqPlan(fields=('orig_index', 'del_lines'"
        ", 'ins_lines')), HashPlan(action='set_none', fields=None, cache=None), InitPlan(fields=(InitPlan.Field(name='o"
        "rig_index', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'), de"
        "fault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, chec"
        "k_type=None), InitPlan.Field(name='del_lines', annotation=OpRef(name='init.fields.1.annotation'), default=None"
        ", default_factory=OpRef(name='init.fields.1.default_factory'), init=True, override=False, field_type=FieldType"
        ".INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='ins_lines', annotation=OpRef(nam"
        "e='init.fields.2.annotation'), default=None, default_factory=OpRef(name='init.fields.2.default_factory'), init"
        "=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_para"
        "m='self', std_params=('orig_index', 'del_lines', 'ins_lines'), kw_only_params=(), frozen=False, slots=False, p"
        "ost_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='orig_index', kw_onl"
        "y=False, fn=None), ReprPlan.Field(name='del_lines', kw_only=False, fn=None), ReprPlan.Field(name='ins_lines', "
        "kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='c017e31222f3a81bbf35abf261881763aa9c217b',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default_factory',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default_factory',
    ),
    cls_names=(
        ('ommlds.minichain.text.applypatch', 'Chunk'),
    ),
)
def _process_dataclass__c017e31222f3a81bbf35abf261881763aa9c217b():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default_factory,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default_factory,
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
                orig_index=self.orig_index,
                del_lines=self.del_lines,
                ins_lines=self.ins_lines,
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
                self.orig_index == other.orig_index and
                self.del_lines == other.del_lines and
                self.ins_lines == other.ins_lines
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        setattr(__dataclass__cls, '__hash__', None)

        def __init__(
            self,
            orig_index: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            del_lines: __dataclass__init__fields__1__annotation = __dataclass__HAS_DEFAULT_FACTORY,
            ins_lines: __dataclass__init__fields__2__annotation = __dataclass__HAS_DEFAULT_FACTORY,
        ) -> __dataclass__None:
            if del_lines is __dataclass__HAS_DEFAULT_FACTORY:
                del_lines = __dataclass__init__fields__1__default_factory()
            if ins_lines is __dataclass__HAS_DEFAULT_FACTORY:
                ins_lines = __dataclass__init__fields__2__default_factory()
            self.orig_index = orig_index
            self.del_lines = del_lines
            self.ins_lines = ins_lines

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"orig_index={self.orig_index!r}")
            parts.append(f"del_lines={self.del_lines!r}")
            parts.append(f"ins_lines={self.ins_lines!r}")
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
        "Plans(tup=(CopyPlan(fields=('changes',)), EqPlan(fields=('changes',)), HashPlan(action='set_none', fields=None"
        ", cache=None), InitPlan(fields=(InitPlan.Field(name='changes', annotation=OpRef(name='init.fields.0.annotation"
        "'), default=None, default_factory=OpRef(name='init.fields.0.default_factory'), init=True, override=False, fiel"
        "d_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self', std_params=('cha"
        "nges',), kw_only_params=(), frozen=False, slots=False, post_init_params=None, init_fns=(), validate_fns=()), R"
        "eprPlan(fields=(ReprPlan.Field(name='changes', kw_only=False, fn=None),), id=False, terse=False, default_fn=No"
        "ne)))"
    ),
    plan_repr_sha1='c0973292edf861e47cf17a1263882af0811cb98c',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default_factory',
    ),
    cls_names=(
        ('ommlds.minichain.text.applypatch', 'Commit'),
    ),
)
def _process_dataclass__c0973292edf861e47cf17a1263882af0811cb98c():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default_factory,
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
                changes=self.changes,
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
                self.changes == other.changes
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        setattr(__dataclass__cls, '__hash__', None)

        def __init__(
            self,
            changes: __dataclass__init__fields__0__annotation = __dataclass__HAS_DEFAULT_FACTORY,
        ) -> __dataclass__None:
            if changes is __dataclass__HAS_DEFAULT_FACTORY:
                changes = __dataclass__init__fields__0__default_factory()
            self.changes = changes

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"changes={self.changes!r}")
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
        "Plans(tup=(CopyPlan(fields=('type', 'old_content', 'new_content', 'move_path')), EqPlan(fields=('type', 'old_c"
        "ontent', 'new_content', 'move_path')), HashPlan(action='set_none', fields=None, cache=None), InitPlan(fields=("
        "InitPlan.Field(name='type', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=N"
        "one, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), I"
        "nitPlan.Field(name='old_content', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init."
        "fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=Non"
        "e, validate=None, check_type=None), InitPlan.Field(name='new_content', annotation=OpRef(name='init.fields.2.an"
        "notation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, fiel"
        "d_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='move_path', anno"
        "tation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=No"
        "ne, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), s"
        "elf_param='self', std_params=('type', 'old_content', 'new_content', 'move_path'), kw_only_params=(), frozen=Fa"
        "lse, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='"
        "type', kw_only=False, fn=None), ReprPlan.Field(name='old_content', kw_only=False, fn=None), ReprPlan.Field(nam"
        "e='new_content', kw_only=False, fn=None), ReprPlan.Field(name='move_path', kw_only=False, fn=None)), id=False,"
        " terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='08ed71763cbffe119aa76fffc962ebb7b49e0133',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ommlds.minichain.text.applypatch', 'FileChange'),
    ),
)
def _process_dataclass__08ed71763cbffe119aa76fffc962ebb7b49e0133():
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
                old_content=self.old_content,
                new_content=self.new_content,
                move_path=self.move_path,
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
                self.old_content == other.old_content and
                self.new_content == other.new_content and
                self.move_path == other.move_path
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        setattr(__dataclass__cls, '__hash__', None)

        def __init__(
            self,
            type: __dataclass__init__fields__0__annotation,
            old_content: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            new_content: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            move_path: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            self.type = type
            self.old_content = old_content
            self.new_content = new_content
            self.move_path = move_path

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"type={self.type!r}")
            parts.append(f"old_content={self.old_content!r}")
            parts.append(f"new_content={self.new_content!r}")
            parts.append(f"move_path={self.move_path!r}")
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
        "Plans(tup=(CopyPlan(fields=('current_files', 'lines', 'index', 'patch', 'fuzz')), EqPlan(fields=('current_file"
        "s', 'lines', 'index', 'patch', 'fuzz')), HashPlan(action='set_none', fields=None, cache=None), InitPlan(fields"
        "=(InitPlan.Field(name='current_files', annotation=OpRef(name='init.fields.0.annotation'), default=None, defaul"
        "t_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_ty"
        "pe=None), InitPlan.Field(name='lines', annotation=OpRef(name='init.fields.1.annotation'), default=None, defaul"
        "t_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_ty"
        "pe=None), InitPlan.Field(name='index', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='"
        "init.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerc"
        "e=None, validate=None, check_type=None), InitPlan.Field(name='patch', annotation=OpRef(name='init.fields.3.ann"
        "otation'), default=None, default_factory=OpRef(name='init.fields.3.default_factory'), init=True, override=Fals"
        "e, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='fuzz', an"
        "notation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_factory="
        "None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)),"
        " self_param='self', std_params=('current_files', 'lines', 'index', 'patch', 'fuzz'), kw_only_params=(), frozen"
        "=False, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(nam"
        "e='current_files', kw_only=False, fn=None), ReprPlan.Field(name='lines', kw_only=False, fn=None), ReprPlan.Fie"
        "ld(name='index', kw_only=False, fn=None), ReprPlan.Field(name='patch', kw_only=False, fn=None), ReprPlan.Field"
        "(name='fuzz', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='b92d453cb05ec45f21af65005f00df3f007e04b8',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default_factory',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__4__default',
    ),
    cls_names=(
        ('ommlds.minichain.text.applypatch', 'Parser'),
    ),
)
def _process_dataclass__b92d453cb05ec45f21af65005f00df3f007e04b8():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__3__default_factory,
        __dataclass__init__fields__4__annotation,
        __dataclass__init__fields__4__default,
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
                current_files=self.current_files,
                lines=self.lines,
                index=self.index,
                patch=self.patch,
                fuzz=self.fuzz,
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
                self.current_files == other.current_files and
                self.lines == other.lines and
                self.index == other.index and
                self.patch == other.patch and
                self.fuzz == other.fuzz
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        setattr(__dataclass__cls, '__hash__', None)

        def __init__(
            self,
            current_files: __dataclass__init__fields__0__annotation,
            lines: __dataclass__init__fields__1__annotation,
            index: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            patch: __dataclass__init__fields__3__annotation = __dataclass__HAS_DEFAULT_FACTORY,
            fuzz: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            if patch is __dataclass__HAS_DEFAULT_FACTORY:
                patch = __dataclass__init__fields__3__default_factory()
            self.current_files = current_files
            self.lines = lines
            self.index = index
            self.patch = patch
            self.fuzz = fuzz

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"current_files={self.current_files!r}")
            parts.append(f"lines={self.lines!r}")
            parts.append(f"index={self.index!r}")
            parts.append(f"patch={self.patch!r}")
            parts.append(f"fuzz={self.fuzz!r}")
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
        "Plans(tup=(CopyPlan(fields=('actions',)), EqPlan(fields=('actions',)), HashPlan(action='set_none', fields=None"
        ", cache=None), InitPlan(fields=(InitPlan.Field(name='actions', annotation=OpRef(name='init.fields.0.annotation"
        "'), default=None, default_factory=OpRef(name='init.fields.0.default_factory'), init=True, override=False, fiel"
        "d_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self', std_params=('act"
        "ions',), kw_only_params=(), frozen=False, slots=False, post_init_params=None, init_fns=(), validate_fns=()), R"
        "eprPlan(fields=(ReprPlan.Field(name='actions', kw_only=False, fn=None),), id=False, terse=False, default_fn=No"
        "ne)))"
    ),
    plan_repr_sha1='00bdcdd6e2f18731e9c63b5db7cefb1ee7e98dc9',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default_factory',
    ),
    cls_names=(
        ('ommlds.minichain.text.applypatch', 'Patch'),
    ),
)
def _process_dataclass__00bdcdd6e2f18731e9c63b5db7cefb1ee7e98dc9():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default_factory,
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
                actions=self.actions,
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
                self.actions == other.actions
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        setattr(__dataclass__cls, '__hash__', None)

        def __init__(
            self,
            actions: __dataclass__init__fields__0__annotation = __dataclass__HAS_DEFAULT_FACTORY,
        ) -> __dataclass__None:
            if actions is __dataclass__HAS_DEFAULT_FACTORY:
                actions = __dataclass__init__fields__0__default_factory()
            self.actions = actions

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"actions={self.actions!r}")
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
        "Plans(tup=(CopyPlan(fields=('type', 'new_file', 'chunks', 'move_path')), EqPlan(fields=('type', 'new_file', 'c"
        "hunks', 'move_path')), HashPlan(action='set_none', fields=None, cache=None), InitPlan(fields=(InitPlan.Field(n"
        "ame='type', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, "
        "override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(na"
        "me='new_file', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'),"
        " default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, c"
        "heck_type=None), InitPlan.Field(name='chunks', annotation=OpRef(name='init.fields.2.annotation'), default=None"
        ", default_factory=OpRef(name='init.fields.2.default_factory'), init=True, override=False, field_type=FieldType"
        ".INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='move_path', annotation=OpRef(nam"
        "e='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, o"
        "verride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self'"
        ", std_params=('type', 'new_file', 'chunks', 'move_path'), kw_only_params=(), frozen=False, slots=False, post_i"
        "nit_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='type', kw_only=False, fn"
        "=None), ReprPlan.Field(name='new_file', kw_only=False, fn=None), ReprPlan.Field(name='chunks', kw_only=False, "
        "fn=None), ReprPlan.Field(name='move_path', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='f7473f8f73f3d63ddea853bd4a405abd76cf2b14',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default_factory',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ommlds.minichain.text.applypatch', 'PatchAction'),
    ),
)
def _process_dataclass__f7473f8f73f3d63ddea853bd4a405abd76cf2b14():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default_factory,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__3__default,
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
                new_file=self.new_file,
                chunks=self.chunks,
                move_path=self.move_path,
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
                self.new_file == other.new_file and
                self.chunks == other.chunks and
                self.move_path == other.move_path
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        setattr(__dataclass__cls, '__hash__', None)

        def __init__(
            self,
            type: __dataclass__init__fields__0__annotation,
            new_file: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            chunks: __dataclass__init__fields__2__annotation = __dataclass__HAS_DEFAULT_FACTORY,
            move_path: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            if chunks is __dataclass__HAS_DEFAULT_FACTORY:
                chunks = __dataclass__init__fields__2__default_factory()
            self.type = type
            self.new_file = new_file
            self.chunks = chunks
            self.move_path = move_path

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"type={self.type!r}")
            parts.append(f"new_file={self.new_file!r}")
            parts.append(f"chunks={self.chunks!r}")
            parts.append(f"move_path={self.move_path!r}")
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
        "Plans(tup=(CopyPlan(fields=('content', 'tool_calls', 'reasoning_content')), EqPlan(fields=('content', 'tool_ca"
        "lls', 'reasoning_content')), HashPlan(action='set_none', fields=None, cache=None), InitPlan(fields=(InitPlan.F"
        "ield(name='content', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.defa"
        "ult'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=N"
        "one, check_type=None), InitPlan.Field(name='tool_calls', annotation=OpRef(name='init.fields.1.annotation'), de"
        "fault=None, default_factory=OpRef(name='init.fields.1.default_factory'), init=True, override=False, field_type"
        "=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='reasoning_content', an"
        "notation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory="
        "None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)),"
        " self_param='self', std_params=('content', 'tool_calls', 'reasoning_content'), kw_only_params=(), frozen=False"
        ", slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='con"
        "tent', kw_only=False, fn=None), ReprPlan.Field(name='tool_calls', kw_only=False, fn=None), ReprPlan.Field(name"
        "='reasoning_content', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='b776b6d80e5ca64f228627161435152ae282463b',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default_factory',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.minichain.text.toolparsing.llamacpp.hermes2', 'ChatMsg'),
    ),
)
def _process_dataclass__b776b6d80e5ca64f228627161435152ae282463b():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default_factory,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
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
                tool_calls=self.tool_calls,
                reasoning_content=self.reasoning_content,
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
                self.tool_calls == other.tool_calls and
                self.reasoning_content == other.reasoning_content
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        setattr(__dataclass__cls, '__hash__', None)

        def __init__(
            self,
            content: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            tool_calls: __dataclass__init__fields__1__annotation = __dataclass__HAS_DEFAULT_FACTORY,
            reasoning_content: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            if tool_calls is __dataclass__HAS_DEFAULT_FACTORY:
                tool_calls = __dataclass__init__fields__1__default_factory()
            self.content = content
            self.tool_calls = tool_calls
            self.reasoning_content = reasoning_content

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"content={self.content!r}")
            parts.append(f"tool_calls={self.tool_calls!r}")
            parts.append(f"reasoning_content={self.reasoning_content!r}")
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
        "Plans(tup=(CopyPlan(fields=('name', 'arguments', 'id')), EqPlan(fields=('name', 'arguments', 'id')), HashPlan("
        "action='set_none', fields=None, cache=None), InitPlan(fields=(InitPlan.Field(name='name', annotation=OpRef(nam"
        "e='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=Field"
        "Type.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='arguments', annotation=OpRef"
        "(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=F"
        "ieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='id', annotation=OpRef(na"
        "me='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, "
        "override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self"
        "', std_params=('name', 'arguments', 'id'), kw_only_params=(), frozen=False, slots=False, post_init_params=None"
        ", init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='name', kw_only=False, fn=None), ReprPla"
        "n.Field(name='arguments', kw_only=False, fn=None), ReprPlan.Field(name='id', kw_only=False, fn=None)), id=Fals"
        "e, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='3d6d34f0c6b17b808a0f4afd043a0fd6b13a3c0c',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.minichain.text.toolparsing.llamacpp.hermes2', 'ChatToolCall'),
    ),
)
def _process_dataclass__3d6d34f0c6b17b808a0f4afd043a0fd6b13a3c0c():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
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
                arguments=self.arguments,
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
                self.name == other.name and
                self.arguments == other.arguments and
                self.id == other.id
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        setattr(__dataclass__cls, '__hash__', None)

        def __init__(
            self,
            name: __dataclass__init__fields__0__annotation,
            arguments: __dataclass__init__fields__1__annotation,
            id: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            self.name = name
            self.arguments = arguments
            self.id = id

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"name={self.name!r}")
            parts.append(f"arguments={self.arguments!r}")
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

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('et',)), EqPlan(fields=('et',)), FrozenPlan(fields=('et',), allow_dynamic_dunder_a"
        "ttrs=False), HashPlan(action='add', fields=('et',), cache=False), InitPlan(fields=(InitPlan.Field(name='et', a"
        "nnotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=Fals"
        "e, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self', std_param"
        "s=('et',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), "
        "ReprPlan(fields=(ReprPlan.Field(name='et', kw_only=False, fn=None),), id=False, terse=False, default_fn=None))"
        ")"
    ),
    plan_repr_sha1='d1dcd40f048e6560420787a4291f3f9d415c2cf3',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.vectors._marshal', '_VectorMarshaler'),
        ('ommlds.minichain.vectors._marshal', '_VectorUnmarshaler'),
    ),
)
def _process_dataclass__d1dcd40f048e6560420787a4291f3f9d415c2cf3():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                et=self.et,
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
                self.et == other.et
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'et',
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
            'et',
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
                self.et,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            et: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'et', et)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"et={self.et!r}")
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
