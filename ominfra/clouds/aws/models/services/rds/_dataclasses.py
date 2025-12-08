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
        "Plans(tup=(CopyPlan(fields=('volume_name', 'allocated_storage', 'io_p_s', 'max_allocated_storage', 'storage_th"
        "roughput', 'storage_type')), EqPlan(fields=('volume_name', 'allocated_storage', 'io_p_s', 'max_allocated_stora"
        "ge', 'storage_throughput', 'storage_type')), FrozenPlan(fields=('__shape__', 'volume_name', 'allocated_storage"
        "', 'io_p_s', 'max_allocated_storage', 'storage_throughput', 'storage_type'), allow_dynamic_dunder_attrs=False)"
        ", HashPlan(action='add', fields=('volume_name', 'allocated_storage', 'io_p_s', 'max_allocated_storage', 'stora"
        "ge_throughput', 'storage_type'), cache=False), InitPlan(fields=(InitPlan.Field(name='__shape__', annotation=Op"
        "Ref(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_typ"
        "e=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='volume_name', annota"
        "tion=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, fi"
        "eld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='allocated_stor"
        "age', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_"
        "factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type"
        "=None), InitPlan.Field(name='io_p_s', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='i"
        "nit.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce"
        "=None, validate=None, check_type=None), InitPlan.Field(name='max_allocated_storage', annotation=OpRef(name='in"
        "it.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, overri"
        "de=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='st"
        "orage_throughput', annotation=OpRef(name='init.fields.5.annotation'), default=OpRef(name='init.fields.5.defaul"
        "t'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=Non"
        "e, check_type=None), InitPlan.Field(name='storage_type', annotation=OpRef(name='init.fields.6.annotation'), de"
        "fault=OpRef(name='init.fields.6.default'), default_factory=None, init=True, override=False, field_type=FieldTy"
        "pe.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=("
        "'volume_name', 'allocated_storage', 'io_p_s', 'max_allocated_storage', 'storage_throughput', 'storage_type'), "
        "frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Fiel"
        "d(name='volume_name', kw_only=True, fn=None), ReprPlan.Field(name='allocated_storage', kw_only=True, fn=None),"
        " ReprPlan.Field(name='io_p_s', kw_only=True, fn=None), ReprPlan.Field(name='max_allocated_storage', kw_only=Tr"
        "ue, fn=None), ReprPlan.Field(name='storage_throughput', kw_only=True, fn=None), ReprPlan.Field(name='storage_t"
        "ype', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='b3d2bb68eb416c40051d4dcb36992bd90e305604',
    op_ref_idents=(
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
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.rds', 'AdditionalStorageVolume'),
    ),
)
def _process_dataclass__b3d2bb68eb416c40051d4dcb36992bd90e305604():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
                volume_name=self.volume_name,
                allocated_storage=self.allocated_storage,
                io_p_s=self.io_p_s,
                max_allocated_storage=self.max_allocated_storage,
                storage_throughput=self.storage_throughput,
                storage_type=self.storage_type,
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
                self.volume_name == other.volume_name and
                self.allocated_storage == other.allocated_storage and
                self.io_p_s == other.io_p_s and
                self.max_allocated_storage == other.max_allocated_storage and
                self.storage_throughput == other.storage_throughput and
                self.storage_type == other.storage_type
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'volume_name',
            'allocated_storage',
            'io_p_s',
            'max_allocated_storage',
            'storage_throughput',
            'storage_type',
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
            '__shape__',
            'volume_name',
            'allocated_storage',
            'io_p_s',
            'max_allocated_storage',
            'storage_throughput',
            'storage_type',
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
                self.volume_name,
                self.allocated_storage,
                self.io_p_s,
                self.max_allocated_storage,
                self.storage_throughput,
                self.storage_type,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            volume_name: __dataclass__init__fields__1__annotation,
            allocated_storage: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            io_p_s: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            max_allocated_storage: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            storage_throughput: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
            storage_type: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'volume_name', volume_name)
            __dataclass__object_setattr(self, 'allocated_storage', allocated_storage)
            __dataclass__object_setattr(self, 'io_p_s', io_p_s)
            __dataclass__object_setattr(self, 'max_allocated_storage', max_allocated_storage)
            __dataclass__object_setattr(self, 'storage_throughput', storage_throughput)
            __dataclass__object_setattr(self, 'storage_type', storage_type)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"volume_name={self.volume_name!r}")
            parts.append(f"allocated_storage={self.allocated_storage!r}")
            parts.append(f"io_p_s={self.io_p_s!r}")
            parts.append(f"max_allocated_storage={self.max_allocated_storage!r}")
            parts.append(f"storage_throughput={self.storage_throughput!r}")
            parts.append(f"storage_type={self.storage_type!r}")
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
        "Plans(tup=(CopyPlan(fields=('volume_name', 'storage_volume_status', 'allocated_storage', 'io_p_s', 'max_alloca"
        "ted_storage', 'storage_throughput', 'storage_type')), EqPlan(fields=('volume_name', 'storage_volume_status', '"
        "allocated_storage', 'io_p_s', 'max_allocated_storage', 'storage_throughput', 'storage_type')), FrozenPlan(fiel"
        "ds=('__shape__', 'volume_name', 'storage_volume_status', 'allocated_storage', 'io_p_s', 'max_allocated_storage"
        "', 'storage_throughput', 'storage_type'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('v"
        "olume_name', 'storage_volume_status', 'allocated_storage', 'io_p_s', 'max_allocated_storage', 'storage_through"
        "put', 'storage_type'), cache=False), InitPlan(fields=(InitPlan.Field(name='__shape__', annotation=OpRef(name='"
        "init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldTyp"
        "e.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='volume_name', annotation=OpRef"
        "(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=Tru"
        "e, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field"
        "(name='storage_volume_status', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fie"
        "lds.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, "
        "validate=None, check_type=None), InitPlan.Field(name='allocated_storage', annotation=OpRef(name='init.fields.3"
        ".annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, f"
        "ield_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='io_p_s', anno"
        "tation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_factory=No"
        "ne, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), In"
        "itPlan.Field(name='max_allocated_storage', annotation=OpRef(name='init.fields.5.annotation'), default=OpRef(na"
        "me='init.fields.5.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, c"
        "oerce=None, validate=None, check_type=None), InitPlan.Field(name='storage_throughput', annotation=OpRef(name='"
        "init.fields.6.annotation'), default=OpRef(name='init.fields.6.default'), default_factory=None, init=True, over"
        "ride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='"
        "storage_type', annotation=OpRef(name='init.fields.7.annotation'), default=OpRef(name='init.fields.7.default'),"
        " default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, c"
        "heck_type=None)), self_param='self', std_params=(), kw_only_params=('volume_name', 'storage_volume_status', 'a"
        "llocated_storage', 'io_p_s', 'max_allocated_storage', 'storage_throughput', 'storage_type'), frozen=True, slot"
        "s=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='volume_na"
        "me', kw_only=True, fn=None), ReprPlan.Field(name='storage_volume_status', kw_only=True, fn=None), ReprPlan.Fie"
        "ld(name='allocated_storage', kw_only=True, fn=None), ReprPlan.Field(name='io_p_s', kw_only=True, fn=None), Rep"
        "rPlan.Field(name='max_allocated_storage', kw_only=True, fn=None), ReprPlan.Field(name='storage_throughput', kw"
        "_only=True, fn=None), ReprPlan.Field(name='storage_type', kw_only=True, fn=None)), id=False, terse=False, defa"
        "ult_fn=None)))"
    ),
    plan_repr_sha1='fc87793e7821f2416bbe6cd808c7ead2d5e84c58',
    op_ref_idents=(
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
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.rds', 'AdditionalStorageVolumeOutput'),
    ),
)
def _process_dataclass__fc87793e7821f2416bbe6cd808c7ead2d5e84c58():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
                volume_name=self.volume_name,
                storage_volume_status=self.storage_volume_status,
                allocated_storage=self.allocated_storage,
                io_p_s=self.io_p_s,
                max_allocated_storage=self.max_allocated_storage,
                storage_throughput=self.storage_throughput,
                storage_type=self.storage_type,
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
                self.volume_name == other.volume_name and
                self.storage_volume_status == other.storage_volume_status and
                self.allocated_storage == other.allocated_storage and
                self.io_p_s == other.io_p_s and
                self.max_allocated_storage == other.max_allocated_storage and
                self.storage_throughput == other.storage_throughput and
                self.storage_type == other.storage_type
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'volume_name',
            'storage_volume_status',
            'allocated_storage',
            'io_p_s',
            'max_allocated_storage',
            'storage_throughput',
            'storage_type',
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
            '__shape__',
            'volume_name',
            'storage_volume_status',
            'allocated_storage',
            'io_p_s',
            'max_allocated_storage',
            'storage_throughput',
            'storage_type',
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
                self.volume_name,
                self.storage_volume_status,
                self.allocated_storage,
                self.io_p_s,
                self.max_allocated_storage,
                self.storage_throughput,
                self.storage_type,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            volume_name: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            storage_volume_status: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            allocated_storage: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            io_p_s: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            max_allocated_storage: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
            storage_throughput: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
            storage_type: __dataclass__init__fields__7__annotation = __dataclass__init__fields__7__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'volume_name', volume_name)
            __dataclass__object_setattr(self, 'storage_volume_status', storage_volume_status)
            __dataclass__object_setattr(self, 'allocated_storage', allocated_storage)
            __dataclass__object_setattr(self, 'io_p_s', io_p_s)
            __dataclass__object_setattr(self, 'max_allocated_storage', max_allocated_storage)
            __dataclass__object_setattr(self, 'storage_throughput', storage_throughput)
            __dataclass__object_setattr(self, 'storage_type', storage_type)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"volume_name={self.volume_name!r}")
            parts.append(f"storage_volume_status={self.storage_volume_status!r}")
            parts.append(f"allocated_storage={self.allocated_storage!r}")
            parts.append(f"io_p_s={self.io_p_s!r}")
            parts.append(f"max_allocated_storage={self.max_allocated_storage!r}")
            parts.append(f"storage_throughput={self.storage_throughput!r}")
            parts.append(f"storage_type={self.storage_type!r}")
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
        "Plans(tup=(CopyPlan(fields=()), EqPlan(fields=()), FrozenPlan(fields=('__shape__',), allow_dynamic_dunder_attr"
        "s=False), HashPlan(action='add', fields=(), cache=False), InitPlan(fields=(InitPlan.Field(name='__shape__', an"
        "notation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False"
        ", field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None),), self_param='self', std_param"
        "s=(), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprP"
        "lan(fields=(), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='fe6ee985e5454d23ff07c1fb86524a86d9239cf5',
    op_ref_idents=(),
    cls_names=(
        ('ominfra.clouds.aws.models.services.rds', 'AuthorizationNotFoundFault'),
        ('ominfra.clouds.aws.models.services.rds', 'BackupPolicyNotFoundFault'),
        ('ominfra.clouds.aws.models.services.rds', 'CertificateNotFoundFault'),
        ('ominfra.clouds.aws.models.services.rds', 'DBClusterNotFoundFault'),
        ('ominfra.clouds.aws.models.services.rds', 'DBInstanceAlreadyExistsFault'),
        ('ominfra.clouds.aws.models.services.rds', 'DBInstanceAutomatedBackupQuotaExceededFault'),
        ('ominfra.clouds.aws.models.services.rds', 'DBInstanceNotFoundFault'),
        ('ominfra.clouds.aws.models.services.rds', 'DBParameterGroupNotFoundFault'),
        ('ominfra.clouds.aws.models.services.rds', 'DBSecurityGroupNotFoundFault'),
        ('ominfra.clouds.aws.models.services.rds', 'DBSnapshotAlreadyExistsFault'),
        ('ominfra.clouds.aws.models.services.rds', 'DBSubnetGroupDoesNotCoverEnoughAZs'),
        ('ominfra.clouds.aws.models.services.rds', 'DBSubnetGroupNotFoundFault'),
        ('ominfra.clouds.aws.models.services.rds', 'DomainNotFoundFault'),
        ('ominfra.clouds.aws.models.services.rds', 'InstanceQuotaExceededFault'),
        ('ominfra.clouds.aws.models.services.rds', 'InsufficientDBInstanceCapacityFault'),
        ('ominfra.clouds.aws.models.services.rds', 'InvalidDBClusterStateFault'),
        ('ominfra.clouds.aws.models.services.rds', 'InvalidDBInstanceStateFault'),
        ('ominfra.clouds.aws.models.services.rds', 'InvalidSubnet'),
        ('ominfra.clouds.aws.models.services.rds', 'InvalidVPCNetworkStateFault'),
        ('ominfra.clouds.aws.models.services.rds', 'KMSKeyNotAccessibleFault'),
        ('ominfra.clouds.aws.models.services.rds', 'NetworkTypeNotSupported'),
        ('ominfra.clouds.aws.models.services.rds', 'OptionGroupNotFoundFault'),
        ('ominfra.clouds.aws.models.services.rds', 'ProvisionedIopsNotAvailableInAZFault'),
        ('ominfra.clouds.aws.models.services.rds', 'SnapshotQuotaExceededFault'),
        ('ominfra.clouds.aws.models.services.rds', 'StorageQuotaExceededFault'),
        ('ominfra.clouds.aws.models.services.rds', 'StorageTypeNotSupportedFault'),
        ('ominfra.clouds.aws.models.services.rds', 'TenantDatabaseQuotaExceededFault'),
        ('ominfra.clouds.aws.models.services.rds', 'VpcEncryptionControlViolationException'),
    ),
)
def _process_dataclass__fe6ee985e5454d23ff07c1fb86524a86d9239cf5():
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

        __dataclass___setattr_frozen_fields = {
            '__shape__',
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
            '__shape__',
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
        "Plans(tup=(CopyPlan(fields=('name',)), EqPlan(fields=('name',)), FrozenPlan(fields=('__shape__', 'name'), allo"
        "w_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('name',), cache=False), InitPlan(fields=(InitPla"
        "n.Field(name='__shape__', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=Non"
        "e, init=True, override=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), In"
        "itPlan.Field(name='name', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1"
        ".default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valid"
        "ate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('name',), frozen=True, slots=Fa"
        "lse, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='name', kw_onl"
        "y=True, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='c34f3093a6550242a3325f4944a4df47a9b48420',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.rds', 'AvailabilityZone'),
    ),
)
def _process_dataclass__c34f3093a6550242a3325f4944a4df47a9b48420():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
            '__shape__',
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
            '__shape__',
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
            *,
            name: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)

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
        "Plans(tup=(CopyPlan(fields=('ca_identifier', 'valid_till')), EqPlan(fields=('ca_identifier', 'valid_till')), F"
        "rozenPlan(fields=('__shape__', 'ca_identifier', 'valid_till'), allow_dynamic_dunder_attrs=False), HashPlan(act"
        "ion='add', fields=('ca_identifier', 'valid_till'), cache=False), InitPlan(fields=(InitPlan.Field(name='__shape"
        "__', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, overrid"
        "e=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='ca"
        "_identifier', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), "
        "default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, ch"
        "eck_type=None), InitPlan.Field(name='valid_till', annotation=OpRef(name='init.fields.2.annotation'), default=O"
        "pRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INST"
        "ANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('ca_ide"
        "ntifier', 'valid_till'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprP"
        "lan(fields=(ReprPlan.Field(name='ca_identifier', kw_only=True, fn=None), ReprPlan.Field(name='valid_till', kw_"
        "only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='d06e7fd09a465a218bf317b3d6b6c4d46dec5ff4',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.rds', 'CertificateDetails'),
    ),
)
def _process_dataclass__d06e7fd09a465a218bf317b3d6b6c4d46dec5ff4():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
                ca_identifier=self.ca_identifier,
                valid_till=self.valid_till,
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
                self.ca_identifier == other.ca_identifier and
                self.valid_till == other.valid_till
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'ca_identifier',
            'valid_till',
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
            '__shape__',
            'ca_identifier',
            'valid_till',
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
                self.ca_identifier,
                self.valid_till,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            ca_identifier: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            valid_till: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'ca_identifier', ca_identifier)
            __dataclass__object_setattr(self, 'valid_till', valid_till)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"ca_identifier={self.ca_identifier!r}")
            parts.append(f"valid_till={self.valid_till!r}")
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
        "Plans(tup=(CopyPlan(fields=('db_name', 'db_instance_identifier', 'allocated_storage', 'db_instance_class', 'en"
        "gine', 'master_username', 'master_user_password', 'db_security_groups', 'vpc_security_group_ids', 'availabilit"
        "y_zone', 'db_subnet_group_name', 'preferred_maintenance_window', 'db_parameter_group_name', 'backup_retention_"
        "period', 'preferred_backup_window', 'port', 'multi_az', 'engine_version', 'auto_minor_version_upgrade', 'licen"
        "se_model', 'iops', 'storage_throughput', 'option_group_name', 'character_set_name', 'nchar_character_set_name'"
        ", 'publicly_accessible', 'tags', 'db_cluster_identifier', 'storage_type', 'tde_credential_arn', 'tde_credentia"
        "l_password', 'storage_encrypted', 'kms_key_id', 'domain', 'domain_fqdn', 'domain_ou', 'domain_auth_secret_arn'"
        ", 'domain_dns_ips', 'copy_tags_to_snapshot', 'monitoring_interval', 'monitoring_role_arn', 'domain_iam_role_na"
        "me', 'promotion_tier', 'timezone', 'enable_iam_database_authentication', 'database_insights_mode', 'enable_per"
        "formance_insights', 'performance_insights_kms_key_id', 'performance_insights_retention_period', 'enable_cloudw"
        "atch_logs_exports', 'processor_features', 'deletion_protection', 'max_allocated_storage', 'enable_customer_own"
        "ed_ip', 'network_type', 'backup_target', 'custom_iam_instance_profile', 'db_system_id', 'ca_certificate_identi"
        "fier', 'manage_master_user_password', 'master_user_secret_kms_key_id', 'multi_tenant', 'dedicated_log_volume',"
        " 'engine_lifecycle_support', 'tag_specifications', 'master_user_authentication_type', 'additional_storage_volu"
        "mes')), EqPlan(fields=('db_name', 'db_instance_identifier', 'allocated_storage', 'db_instance_class', 'engine'"
        ", 'master_username', 'master_user_password', 'db_security_groups', 'vpc_security_group_ids', 'availability_zon"
        "e', 'db_subnet_group_name', 'preferred_maintenance_window', 'db_parameter_group_name', 'backup_retention_perio"
        "d', 'preferred_backup_window', 'port', 'multi_az', 'engine_version', 'auto_minor_version_upgrade', 'license_mo"
        "del', 'iops', 'storage_throughput', 'option_group_name', 'character_set_name', 'nchar_character_set_name', 'pu"
        "blicly_accessible', 'tags', 'db_cluster_identifier', 'storage_type', 'tde_credential_arn', 'tde_credential_pas"
        "sword', 'storage_encrypted', 'kms_key_id', 'domain', 'domain_fqdn', 'domain_ou', 'domain_auth_secret_arn', 'do"
        "main_dns_ips', 'copy_tags_to_snapshot', 'monitoring_interval', 'monitoring_role_arn', 'domain_iam_role_name', "
        "'promotion_tier', 'timezone', 'enable_iam_database_authentication', 'database_insights_mode', 'enable_performa"
        "nce_insights', 'performance_insights_kms_key_id', 'performance_insights_retention_period', 'enable_cloudwatch_"
        "logs_exports', 'processor_features', 'deletion_protection', 'max_allocated_storage', 'enable_customer_owned_ip"
        "', 'network_type', 'backup_target', 'custom_iam_instance_profile', 'db_system_id', 'ca_certificate_identifier'"
        ", 'manage_master_user_password', 'master_user_secret_kms_key_id', 'multi_tenant', 'dedicated_log_volume', 'eng"
        "ine_lifecycle_support', 'tag_specifications', 'master_user_authentication_type', 'additional_storage_volumes')"
        "), FrozenPlan(fields=('__shape__', 'db_name', 'db_instance_identifier', 'allocated_storage', 'db_instance_clas"
        "s', 'engine', 'master_username', 'master_user_password', 'db_security_groups', 'vpc_security_group_ids', 'avai"
        "lability_zone', 'db_subnet_group_name', 'preferred_maintenance_window', 'db_parameter_group_name', 'backup_ret"
        "ention_period', 'preferred_backup_window', 'port', 'multi_az', 'engine_version', 'auto_minor_version_upgrade',"
        " 'license_model', 'iops', 'storage_throughput', 'option_group_name', 'character_set_name', 'nchar_character_se"
        "t_name', 'publicly_accessible', 'tags', 'db_cluster_identifier', 'storage_type', 'tde_credential_arn', 'tde_cr"
        "edential_password', 'storage_encrypted', 'kms_key_id', 'domain', 'domain_fqdn', 'domain_ou', 'domain_auth_secr"
        "et_arn', 'domain_dns_ips', 'copy_tags_to_snapshot', 'monitoring_interval', 'monitoring_role_arn', 'domain_iam_"
        "role_name', 'promotion_tier', 'timezone', 'enable_iam_database_authentication', 'database_insights_mode', 'ena"
        "ble_performance_insights', 'performance_insights_kms_key_id', 'performance_insights_retention_period', 'enable"
        "_cloudwatch_logs_exports', 'processor_features', 'deletion_protection', 'max_allocated_storage', 'enable_custo"
        "mer_owned_ip', 'network_type', 'backup_target', 'custom_iam_instance_profile', 'db_system_id', 'ca_certificate"
        "_identifier', 'manage_master_user_password', 'master_user_secret_kms_key_id', 'multi_tenant', 'dedicated_log_v"
        "olume', 'engine_lifecycle_support', 'tag_specifications', 'master_user_authentication_type', 'additional_stora"
        "ge_volumes'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('db_name', 'db_instance_identi"
        "fier', 'allocated_storage', 'db_instance_class', 'engine', 'master_username', 'master_user_password', 'db_secu"
        "rity_groups', 'vpc_security_group_ids', 'availability_zone', 'db_subnet_group_name', 'preferred_maintenance_wi"
        "ndow', 'db_parameter_group_name', 'backup_retention_period', 'preferred_backup_window', 'port', 'multi_az', 'e"
        "ngine_version', 'auto_minor_version_upgrade', 'license_model', 'iops', 'storage_throughput', 'option_group_nam"
        "e', 'character_set_name', 'nchar_character_set_name', 'publicly_accessible', 'tags', 'db_cluster_identifier', "
        "'storage_type', 'tde_credential_arn', 'tde_credential_password', 'storage_encrypted', 'kms_key_id', 'domain', "
        "'domain_fqdn', 'domain_ou', 'domain_auth_secret_arn', 'domain_dns_ips', 'copy_tags_to_snapshot', 'monitoring_i"
        "nterval', 'monitoring_role_arn', 'domain_iam_role_name', 'promotion_tier', 'timezone', 'enable_iam_database_au"
        "thentication', 'database_insights_mode', 'enable_performance_insights', 'performance_insights_kms_key_id', 'pe"
        "rformance_insights_retention_period', 'enable_cloudwatch_logs_exports', 'processor_features', 'deletion_protec"
        "tion', 'max_allocated_storage', 'enable_customer_owned_ip', 'network_type', 'backup_target', 'custom_iam_insta"
        "nce_profile', 'db_system_id', 'ca_certificate_identifier', 'manage_master_user_password', 'master_user_secret_"
        "kms_key_id', 'multi_tenant', 'dedicated_log_volume', 'engine_lifecycle_support', 'tag_specifications', 'master"
        "_user_authentication_type', 'additional_storage_volumes'), cache=False), InitPlan(fields=(InitPlan.Field(name="
        "'__shape__', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True,"
        " override=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field("
        "name='db_name', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default')"
        ", default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, "
        "check_type=None), InitPlan.Field(name='db_instance_identifier', annotation=OpRef(name='init.fields.2.annotatio"
        "n'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None"
        ", validate=None, check_type=None), InitPlan.Field(name='allocated_storage', annotation=OpRef(name='init.fields"
        ".3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False,"
        " field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='db_instance"
        "_class', annotation=OpRef(name='init.fields.4.annotation'), default=None, default_factory=None, init=True, ove"
        "rride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name="
        "'engine', annotation=OpRef(name='init.fields.5.annotation'), default=None, default_factory=None, init=True, ov"
        "erride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name"
        "='master_username', annotation=OpRef(name='init.fields.6.annotation'), default=OpRef(name='init.fields.6.defau"
        "lt'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=No"
        "ne, check_type=None), InitPlan.Field(name='master_user_password', annotation=OpRef(name='init.fields.7.annotat"
        "ion'), default=OpRef(name='init.fields.7.default'), default_factory=None, init=True, override=False, field_typ"
        "e=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='db_security_groups', "
        "annotation=OpRef(name='init.fields.8.annotation'), default=OpRef(name='init.fields.8.default'), default_factor"
        "y=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)"
        ", InitPlan.Field(name='vpc_security_group_ids', annotation=OpRef(name='init.fields.9.annotation'), default=OpR"
        "ef(name='init.fields.9.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTAN"
        "CE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='availability_zone', annotation=OpRef(na"
        "me='init.fields.10.annotation'), default=OpRef(name='init.fields.10.default'), default_factory=None, init=True"
        ", override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field("
        "name='db_subnet_group_name', annotation=OpRef(name='init.fields.11.annotation'), default=OpRef(name='init.fiel"
        "ds.11.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, "
        "validate=None, check_type=None), InitPlan.Field(name='preferred_maintenance_window', annotation=OpRef(name='in"
        "it.fields.12.annotation'), default=OpRef(name='init.fields.12.default'), default_factory=None, init=True, over"
        "ride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='"
        "db_parameter_group_name', annotation=OpRef(name='init.fields.13.annotation'), default=OpRef(name='init.fields."
        "13.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, val"
        "idate=None, check_type=None), InitPlan.Field(name='backup_retention_period', annotation=OpRef(name='init.field"
        "s.14.annotation'), default=OpRef(name='init.fields.14.default'), default_factory=None, init=True, override=Fal"
        "se, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='preferre"
        "d_backup_window', annotation=OpRef(name='init.fields.15.annotation'), default=OpRef(name='init.fields.15.defau"
        "lt'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=No"
        "ne, check_type=None), InitPlan.Field(name='port', annotation=OpRef(name='init.fields.16.annotation'), default="
        "OpRef(name='init.fields.16.default'), default_factory=None, init=True, override=False, field_type=FieldType.IN"
        "STANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='multi_az', annotation=OpRef(name='i"
        "nit.fields.17.annotation'), default=OpRef(name='init.fields.17.default'), default_factory=None, init=True, ove"
        "rride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name="
        "'engine_version', annotation=OpRef(name='init.fields.18.annotation'), default=OpRef(name='init.fields.18.defau"
        "lt'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=No"
        "ne, check_type=None), InitPlan.Field(name='auto_minor_version_upgrade', annotation=OpRef(name='init.fields.19."
        "annotation'), default=OpRef(name='init.fields.19.default'), default_factory=None, init=True, override=False, f"
        "ield_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='license_model"
        "', annotation=OpRef(name='init.fields.20.annotation'), default=OpRef(name='init.fields.20.default'), default_f"
        "actory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type="
        "None), InitPlan.Field(name='iops', annotation=OpRef(name='init.fields.21.annotation'), default=OpRef(name='ini"
        "t.fields.21.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce="
        "None, validate=None, check_type=None), InitPlan.Field(name='storage_throughput', annotation=OpRef(name='init.f"
        "ields.22.annotation'), default=OpRef(name='init.fields.22.default'), default_factory=None, init=True, override"
        "=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='opti"
        "on_group_name', annotation=OpRef(name='init.fields.23.annotation'), default=OpRef(name='init.fields.23.default"
        "'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None"
        ", check_type=None), InitPlan.Field(name='character_set_name', annotation=OpRef(name='init.fields.24.annotation"
        "'), default=OpRef(name='init.fields.24.default'), default_factory=None, init=True, override=False, field_type="
        "FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='nchar_character_set_nam"
        "e', annotation=OpRef(name='init.fields.25.annotation'), default=OpRef(name='init.fields.25.default'), default_"
        "factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type"
        "=None), InitPlan.Field(name='publicly_accessible', annotation=OpRef(name='init.fields.26.annotation'), default"
        "=OpRef(name='init.fields.26.default'), default_factory=None, init=True, override=False, field_type=FieldType.I"
        "NSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='tags', annotation=OpRef(name='init"
        ".fields.27.annotation'), default=OpRef(name='init.fields.27.default'), default_factory=None, init=True, overri"
        "de=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='db"
        "_cluster_identifier', annotation=OpRef(name='init.fields.28.annotation'), default=OpRef(name='init.fields.28.d"
        "efault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validat"
        "e=None, check_type=None), InitPlan.Field(name='storage_type', annotation=OpRef(name='init.fields.29.annotation"
        "'), default=OpRef(name='init.fields.29.default'), default_factory=None, init=True, override=False, field_type="
        "FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='tde_credential_arn', an"
        "notation=OpRef(name='init.fields.30.annotation'), default=OpRef(name='init.fields.30.default'), default_factor"
        "y=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)"
        ", InitPlan.Field(name='tde_credential_password', annotation=OpRef(name='init.fields.31.annotation'), default=O"
        "pRef(name='init.fields.31.default'), default_factory=None, init=True, override=False, field_type=FieldType.INS"
        "TANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='storage_encrypted', annotation=OpRef"
        "(name='init.fields.32.annotation'), default=OpRef(name='init.fields.32.default'), default_factory=None, init=T"
        "rue, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fie"
        "ld(name='kms_key_id', annotation=OpRef(name='init.fields.33.annotation'), default=OpRef(name='init.fields.33.d"
        "efault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validat"
        "e=None, check_type=None), InitPlan.Field(name='domain', annotation=OpRef(name='init.fields.34.annotation'), de"
        "fault=OpRef(name='init.fields.34.default'), default_factory=None, init=True, override=False, field_type=FieldT"
        "ype.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='domain_fqdn', annotation=OpRe"
        "f(name='init.fields.35.annotation'), default=OpRef(name='init.fields.35.default'), default_factory=None, init="
        "True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fi"
        "eld(name='domain_ou', annotation=OpRef(name='init.fields.36.annotation'), default=OpRef(name='init.fields.36.d"
        "efault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validat"
        "e=None, check_type=None), InitPlan.Field(name='domain_auth_secret_arn', annotation=OpRef(name='init.fields.37."
        "annotation'), default=OpRef(name='init.fields.37.default'), default_factory=None, init=True, override=False, f"
        "ield_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='domain_dns_ip"
        "s', annotation=OpRef(name='init.fields.38.annotation'), default=OpRef(name='init.fields.38.default'), default_"
        "factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type"
        "=None), InitPlan.Field(name='copy_tags_to_snapshot', annotation=OpRef(name='init.fields.39.annotation'), defau"
        "lt=OpRef(name='init.fields.39.default'), default_factory=None, init=True, override=False, field_type=FieldType"
        ".INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='monitoring_interval', annotation"
        "=OpRef(name='init.fields.40.annotation'), default=OpRef(name='init.fields.40.default'), default_factory=None, "
        "init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPl"
        "an.Field(name='monitoring_role_arn', annotation=OpRef(name='init.fields.41.annotation'), default=OpRef(name='i"
        "nit.fields.41.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerc"
        "e=None, validate=None, check_type=None), InitPlan.Field(name='domain_iam_role_name', annotation=OpRef(name='in"
        "it.fields.42.annotation'), default=OpRef(name='init.fields.42.default'), default_factory=None, init=True, over"
        "ride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='"
        "promotion_tier', annotation=OpRef(name='init.fields.43.annotation'), default=OpRef(name='init.fields.43.defaul"
        "t'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=Non"
        "e, check_type=None), InitPlan.Field(name='timezone', annotation=OpRef(name='init.fields.44.annotation'), defau"
        "lt=OpRef(name='init.fields.44.default'), default_factory=None, init=True, override=False, field_type=FieldType"
        ".INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='enable_iam_database_authenticati"
        "on', annotation=OpRef(name='init.fields.45.annotation'), default=OpRef(name='init.fields.45.default'), default"
        "_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_typ"
        "e=None), InitPlan.Field(name='database_insights_mode', annotation=OpRef(name='init.fields.46.annotation'), def"
        "ault=OpRef(name='init.fields.46.default'), default_factory=None, init=True, override=False, field_type=FieldTy"
        "pe.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='enable_performance_insights', "
        "annotation=OpRef(name='init.fields.47.annotation'), default=OpRef(name='init.fields.47.default'), default_fact"
        "ory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=Non"
        "e), InitPlan.Field(name='performance_insights_kms_key_id', annotation=OpRef(name='init.fields.48.annotation'),"
        " default=OpRef(name='init.fields.48.default'), default_factory=None, init=True, override=False, field_type=Fie"
        "ldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='performance_insights_reten"
        "tion_period', annotation=OpRef(name='init.fields.49.annotation'), default=OpRef(name='init.fields.49.default')"
        ", default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, "
        "check_type=None), InitPlan.Field(name='enable_cloudwatch_logs_exports', annotation=OpRef(name='init.fields.50."
        "annotation'), default=OpRef(name='init.fields.50.default'), default_factory=None, init=True, override=False, f"
        "ield_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='processor_fea"
        "tures', annotation=OpRef(name='init.fields.51.annotation'), default=OpRef(name='init.fields.51.default'), defa"
        "ult_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_"
        "type=None), InitPlan.Field(name='deletion_protection', annotation=OpRef(name='init.fields.52.annotation'), def"
        "ault=OpRef(name='init.fields.52.default'), default_factory=None, init=True, override=False, field_type=FieldTy"
        "pe.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='max_allocated_storage', annota"
        "tion=OpRef(name='init.fields.53.annotation'), default=OpRef(name='init.fields.53.default'), default_factory=No"
        "ne, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), In"
        "itPlan.Field(name='enable_customer_owned_ip', annotation=OpRef(name='init.fields.54.annotation'), default=OpRe"
        "f(name='init.fields.54.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTAN"
        "CE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='network_type', annotation=OpRef(name='i"
        "nit.fields.55.annotation'), default=OpRef(name='init.fields.55.default'), default_factory=None, init=True, ove"
        "rride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name="
        "'backup_target', annotation=OpRef(name='init.fields.56.annotation'), default=OpRef(name='init.fields.56.defaul"
        "t'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=Non"
        "e, check_type=None), InitPlan.Field(name='custom_iam_instance_profile', annotation=OpRef(name='init.fields.57."
        "annotation'), default=OpRef(name='init.fields.57.default'), default_factory=None, init=True, override=False, f"
        "ield_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='db_system_id'"
        ", annotation=OpRef(name='init.fields.58.annotation'), default=OpRef(name='init.fields.58.default'), default_fa"
        "ctory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=N"
        "one), InitPlan.Field(name='ca_certificate_identifier', annotation=OpRef(name='init.fields.59.annotation'), def"
        "ault=OpRef(name='init.fields.59.default'), default_factory=None, init=True, override=False, field_type=FieldTy"
        "pe.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='manage_master_user_password', "
        "annotation=OpRef(name='init.fields.60.annotation'), default=OpRef(name='init.fields.60.default'), default_fact"
        "ory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=Non"
        "e), InitPlan.Field(name='master_user_secret_kms_key_id', annotation=OpRef(name='init.fields.61.annotation'), d"
        "efault=OpRef(name='init.fields.61.default'), default_factory=None, init=True, override=False, field_type=Field"
        "Type.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='multi_tenant', annotation=Op"
        "Ref(name='init.fields.62.annotation'), default=OpRef(name='init.fields.62.default'), default_factory=None, ini"
        "t=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan."
        "Field(name='dedicated_log_volume', annotation=OpRef(name='init.fields.63.annotation'), default=OpRef(name='ini"
        "t.fields.63.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce="
        "None, validate=None, check_type=None), InitPlan.Field(name='engine_lifecycle_support', annotation=OpRef(name='"
        "init.fields.64.annotation'), default=OpRef(name='init.fields.64.default'), default_factory=None, init=True, ov"
        "erride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name"
        "='tag_specifications', annotation=OpRef(name='init.fields.65.annotation'), default=OpRef(name='init.fields.65."
        "default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valida"
        "te=None, check_type=None), InitPlan.Field(name='master_user_authentication_type', annotation=OpRef(name='init."
        "fields.66.annotation'), default=OpRef(name='init.fields.66.default'), default_factory=None, init=True, overrid"
        "e=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='add"
        "itional_storage_volumes', annotation=OpRef(name='init.fields.67.annotation'), default=OpRef(name='init.fields."
        "67.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, val"
        "idate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('db_name', 'db_instance_ident"
        "ifier', 'allocated_storage', 'db_instance_class', 'engine', 'master_username', 'master_user_password', 'db_sec"
        "urity_groups', 'vpc_security_group_ids', 'availability_zone', 'db_subnet_group_name', 'preferred_maintenance_w"
        "indow', 'db_parameter_group_name', 'backup_retention_period', 'preferred_backup_window', 'port', 'multi_az', '"
        "engine_version', 'auto_minor_version_upgrade', 'license_model', 'iops', 'storage_throughput', 'option_group_na"
        "me', 'character_set_name', 'nchar_character_set_name', 'publicly_accessible', 'tags', 'db_cluster_identifier',"
        " 'storage_type', 'tde_credential_arn', 'tde_credential_password', 'storage_encrypted', 'kms_key_id', 'domain',"
        " 'domain_fqdn', 'domain_ou', 'domain_auth_secret_arn', 'domain_dns_ips', 'copy_tags_to_snapshot', 'monitoring_"
        "interval', 'monitoring_role_arn', 'domain_iam_role_name', 'promotion_tier', 'timezone', 'enable_iam_database_a"
        "uthentication', 'database_insights_mode', 'enable_performance_insights', 'performance_insights_kms_key_id', 'p"
        "erformance_insights_retention_period', 'enable_cloudwatch_logs_exports', 'processor_features', 'deletion_prote"
        "ction', 'max_allocated_storage', 'enable_customer_owned_ip', 'network_type', 'backup_target', 'custom_iam_inst"
        "ance_profile', 'db_system_id', 'ca_certificate_identifier', 'manage_master_user_password', 'master_user_secret"
        "_kms_key_id', 'multi_tenant', 'dedicated_log_volume', 'engine_lifecycle_support', 'tag_specifications', 'maste"
        "r_user_authentication_type', 'additional_storage_volumes'), frozen=True, slots=False, post_init_params=None, i"
        "nit_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='db_name', kw_only=True, fn=None), ReprPlan"
        ".Field(name='db_instance_identifier', kw_only=True, fn=None), ReprPlan.Field(name='allocated_storage', kw_only"
        "=True, fn=None), ReprPlan.Field(name='db_instance_class', kw_only=True, fn=None), ReprPlan.Field(name='engine'"
        ", kw_only=True, fn=None), ReprPlan.Field(name='master_username', kw_only=True, fn=None), ReprPlan.Field(name='"
        "master_user_password', kw_only=True, fn=None), ReprPlan.Field(name='db_security_groups', kw_only=True, fn=None"
        "), ReprPlan.Field(name='vpc_security_group_ids', kw_only=True, fn=None), ReprPlan.Field(name='availability_zon"
        "e', kw_only=True, fn=None), ReprPlan.Field(name='db_subnet_group_name', kw_only=True, fn=None), ReprPlan.Field"
        "(name='preferred_maintenance_window', kw_only=True, fn=None), ReprPlan.Field(name='db_parameter_group_name', k"
        "w_only=True, fn=None), ReprPlan.Field(name='backup_retention_period', kw_only=True, fn=None), ReprPlan.Field(n"
        "ame='preferred_backup_window', kw_only=True, fn=None), ReprPlan.Field(name='port', kw_only=True, fn=None), Rep"
        "rPlan.Field(name='multi_az', kw_only=True, fn=None), ReprPlan.Field(name='engine_version', kw_only=True, fn=No"
        "ne), ReprPlan.Field(name='auto_minor_version_upgrade', kw_only=True, fn=None), ReprPlan.Field(name='license_mo"
        "del', kw_only=True, fn=None), ReprPlan.Field(name='iops', kw_only=True, fn=None), ReprPlan.Field(name='storage"
        "_throughput', kw_only=True, fn=None), ReprPlan.Field(name='option_group_name', kw_only=True, fn=None), ReprPla"
        "n.Field(name='character_set_name', kw_only=True, fn=None), ReprPlan.Field(name='nchar_character_set_name', kw_"
        "only=True, fn=None), ReprPlan.Field(name='publicly_accessible', kw_only=True, fn=None), ReprPlan.Field(name='t"
        "ags', kw_only=True, fn=None), ReprPlan.Field(name='db_cluster_identifier', kw_only=True, fn=None), ReprPlan.Fi"
        "eld(name='storage_type', kw_only=True, fn=None), ReprPlan.Field(name='tde_credential_arn', kw_only=True, fn=No"
        "ne), ReprPlan.Field(name='tde_credential_password', kw_only=True, fn=None), ReprPlan.Field(name='storage_encry"
        "pted', kw_only=True, fn=None), ReprPlan.Field(name='kms_key_id', kw_only=True, fn=None), ReprPlan.Field(name='"
        "domain', kw_only=True, fn=None), ReprPlan.Field(name='domain_fqdn', kw_only=True, fn=None), ReprPlan.Field(nam"
        "e='domain_ou', kw_only=True, fn=None), ReprPlan.Field(name='domain_auth_secret_arn', kw_only=True, fn=None), R"
        "eprPlan.Field(name='domain_dns_ips', kw_only=True, fn=None), ReprPlan.Field(name='copy_tags_to_snapshot', kw_o"
        "nly=True, fn=None), ReprPlan.Field(name='monitoring_interval', kw_only=True, fn=None), ReprPlan.Field(name='mo"
        "nitoring_role_arn', kw_only=True, fn=None), ReprPlan.Field(name='domain_iam_role_name', kw_only=True, fn=None)"
        ", ReprPlan.Field(name='promotion_tier', kw_only=True, fn=None), ReprPlan.Field(name='timezone', kw_only=True, "
        "fn=None), ReprPlan.Field(name='enable_iam_database_authentication', kw_only=True, fn=None), ReprPlan.Field(nam"
        "e='database_insights_mode', kw_only=True, fn=None), ReprPlan.Field(name='enable_performance_insights', kw_only"
        "=True, fn=None), ReprPlan.Field(name='performance_insights_kms_key_id', kw_only=True, fn=None), ReprPlan.Field"
        "(name='performance_insights_retention_period', kw_only=True, fn=None), ReprPlan.Field(name='enable_cloudwatch_"
        "logs_exports', kw_only=True, fn=None), ReprPlan.Field(name='processor_features', kw_only=True, fn=None), ReprP"
        "lan.Field(name='deletion_protection', kw_only=True, fn=None), ReprPlan.Field(name='max_allocated_storage', kw_"
        "only=True, fn=None), ReprPlan.Field(name='enable_customer_owned_ip', kw_only=True, fn=None), ReprPlan.Field(na"
        "me='network_type', kw_only=True, fn=None), ReprPlan.Field(name='backup_target', kw_only=True, fn=None), ReprPl"
        "an.Field(name='custom_iam_instance_profile', kw_only=True, fn=None), ReprPlan.Field(name='db_system_id', kw_on"
        "ly=True, fn=None), ReprPlan.Field(name='ca_certificate_identifier', kw_only=True, fn=None), ReprPlan.Field(nam"
        "e='manage_master_user_password', kw_only=True, fn=None), ReprPlan.Field(name='master_user_secret_kms_key_id', "
        "kw_only=True, fn=None), ReprPlan.Field(name='multi_tenant', kw_only=True, fn=None), ReprPlan.Field(name='dedic"
        "ated_log_volume', kw_only=True, fn=None), ReprPlan.Field(name='engine_lifecycle_support', kw_only=True, fn=Non"
        "e), ReprPlan.Field(name='tag_specifications', kw_only=True, fn=None), ReprPlan.Field(name='master_user_authent"
        "ication_type', kw_only=True, fn=None), ReprPlan.Field(name='additional_storage_volumes', kw_only=True, fn=None"
        ")), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='31ff148188ee1c0bf5d5ca29183ea035d0dc7541',
    op_ref_idents=(
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
        '__dataclass__init__fields__18__annotation',
        '__dataclass__init__fields__18__default',
        '__dataclass__init__fields__19__annotation',
        '__dataclass__init__fields__19__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__20__annotation',
        '__dataclass__init__fields__20__default',
        '__dataclass__init__fields__21__annotation',
        '__dataclass__init__fields__21__default',
        '__dataclass__init__fields__22__annotation',
        '__dataclass__init__fields__22__default',
        '__dataclass__init__fields__23__annotation',
        '__dataclass__init__fields__23__default',
        '__dataclass__init__fields__24__annotation',
        '__dataclass__init__fields__24__default',
        '__dataclass__init__fields__25__annotation',
        '__dataclass__init__fields__25__default',
        '__dataclass__init__fields__26__annotation',
        '__dataclass__init__fields__26__default',
        '__dataclass__init__fields__27__annotation',
        '__dataclass__init__fields__27__default',
        '__dataclass__init__fields__28__annotation',
        '__dataclass__init__fields__28__default',
        '__dataclass__init__fields__29__annotation',
        '__dataclass__init__fields__29__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__30__annotation',
        '__dataclass__init__fields__30__default',
        '__dataclass__init__fields__31__annotation',
        '__dataclass__init__fields__31__default',
        '__dataclass__init__fields__32__annotation',
        '__dataclass__init__fields__32__default',
        '__dataclass__init__fields__33__annotation',
        '__dataclass__init__fields__33__default',
        '__dataclass__init__fields__34__annotation',
        '__dataclass__init__fields__34__default',
        '__dataclass__init__fields__35__annotation',
        '__dataclass__init__fields__35__default',
        '__dataclass__init__fields__36__annotation',
        '__dataclass__init__fields__36__default',
        '__dataclass__init__fields__37__annotation',
        '__dataclass__init__fields__37__default',
        '__dataclass__init__fields__38__annotation',
        '__dataclass__init__fields__38__default',
        '__dataclass__init__fields__39__annotation',
        '__dataclass__init__fields__39__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
        '__dataclass__init__fields__40__annotation',
        '__dataclass__init__fields__40__default',
        '__dataclass__init__fields__41__annotation',
        '__dataclass__init__fields__41__default',
        '__dataclass__init__fields__42__annotation',
        '__dataclass__init__fields__42__default',
        '__dataclass__init__fields__43__annotation',
        '__dataclass__init__fields__43__default',
        '__dataclass__init__fields__44__annotation',
        '__dataclass__init__fields__44__default',
        '__dataclass__init__fields__45__annotation',
        '__dataclass__init__fields__45__default',
        '__dataclass__init__fields__46__annotation',
        '__dataclass__init__fields__46__default',
        '__dataclass__init__fields__47__annotation',
        '__dataclass__init__fields__47__default',
        '__dataclass__init__fields__48__annotation',
        '__dataclass__init__fields__48__default',
        '__dataclass__init__fields__49__annotation',
        '__dataclass__init__fields__49__default',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__50__annotation',
        '__dataclass__init__fields__50__default',
        '__dataclass__init__fields__51__annotation',
        '__dataclass__init__fields__51__default',
        '__dataclass__init__fields__52__annotation',
        '__dataclass__init__fields__52__default',
        '__dataclass__init__fields__53__annotation',
        '__dataclass__init__fields__53__default',
        '__dataclass__init__fields__54__annotation',
        '__dataclass__init__fields__54__default',
        '__dataclass__init__fields__55__annotation',
        '__dataclass__init__fields__55__default',
        '__dataclass__init__fields__56__annotation',
        '__dataclass__init__fields__56__default',
        '__dataclass__init__fields__57__annotation',
        '__dataclass__init__fields__57__default',
        '__dataclass__init__fields__58__annotation',
        '__dataclass__init__fields__58__default',
        '__dataclass__init__fields__59__annotation',
        '__dataclass__init__fields__59__default',
        '__dataclass__init__fields__5__annotation',
        '__dataclass__init__fields__60__annotation',
        '__dataclass__init__fields__60__default',
        '__dataclass__init__fields__61__annotation',
        '__dataclass__init__fields__61__default',
        '__dataclass__init__fields__62__annotation',
        '__dataclass__init__fields__62__default',
        '__dataclass__init__fields__63__annotation',
        '__dataclass__init__fields__63__default',
        '__dataclass__init__fields__64__annotation',
        '__dataclass__init__fields__64__default',
        '__dataclass__init__fields__65__annotation',
        '__dataclass__init__fields__65__default',
        '__dataclass__init__fields__66__annotation',
        '__dataclass__init__fields__66__default',
        '__dataclass__init__fields__67__annotation',
        '__dataclass__init__fields__67__default',
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
        ('ominfra.clouds.aws.models.services.rds', 'CreateDBInstanceMessage'),
    ),
)
def _process_dataclass__31ff148188ee1c0bf5d5ca29183ea035d0dc7541():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
        __dataclass__init__fields__18__annotation,
        __dataclass__init__fields__18__default,
        __dataclass__init__fields__19__annotation,
        __dataclass__init__fields__19__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__init__fields__20__annotation,
        __dataclass__init__fields__20__default,
        __dataclass__init__fields__21__annotation,
        __dataclass__init__fields__21__default,
        __dataclass__init__fields__22__annotation,
        __dataclass__init__fields__22__default,
        __dataclass__init__fields__23__annotation,
        __dataclass__init__fields__23__default,
        __dataclass__init__fields__24__annotation,
        __dataclass__init__fields__24__default,
        __dataclass__init__fields__25__annotation,
        __dataclass__init__fields__25__default,
        __dataclass__init__fields__26__annotation,
        __dataclass__init__fields__26__default,
        __dataclass__init__fields__27__annotation,
        __dataclass__init__fields__27__default,
        __dataclass__init__fields__28__annotation,
        __dataclass__init__fields__28__default,
        __dataclass__init__fields__29__annotation,
        __dataclass__init__fields__29__default,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__30__annotation,
        __dataclass__init__fields__30__default,
        __dataclass__init__fields__31__annotation,
        __dataclass__init__fields__31__default,
        __dataclass__init__fields__32__annotation,
        __dataclass__init__fields__32__default,
        __dataclass__init__fields__33__annotation,
        __dataclass__init__fields__33__default,
        __dataclass__init__fields__34__annotation,
        __dataclass__init__fields__34__default,
        __dataclass__init__fields__35__annotation,
        __dataclass__init__fields__35__default,
        __dataclass__init__fields__36__annotation,
        __dataclass__init__fields__36__default,
        __dataclass__init__fields__37__annotation,
        __dataclass__init__fields__37__default,
        __dataclass__init__fields__38__annotation,
        __dataclass__init__fields__38__default,
        __dataclass__init__fields__39__annotation,
        __dataclass__init__fields__39__default,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__3__default,
        __dataclass__init__fields__40__annotation,
        __dataclass__init__fields__40__default,
        __dataclass__init__fields__41__annotation,
        __dataclass__init__fields__41__default,
        __dataclass__init__fields__42__annotation,
        __dataclass__init__fields__42__default,
        __dataclass__init__fields__43__annotation,
        __dataclass__init__fields__43__default,
        __dataclass__init__fields__44__annotation,
        __dataclass__init__fields__44__default,
        __dataclass__init__fields__45__annotation,
        __dataclass__init__fields__45__default,
        __dataclass__init__fields__46__annotation,
        __dataclass__init__fields__46__default,
        __dataclass__init__fields__47__annotation,
        __dataclass__init__fields__47__default,
        __dataclass__init__fields__48__annotation,
        __dataclass__init__fields__48__default,
        __dataclass__init__fields__49__annotation,
        __dataclass__init__fields__49__default,
        __dataclass__init__fields__4__annotation,
        __dataclass__init__fields__50__annotation,
        __dataclass__init__fields__50__default,
        __dataclass__init__fields__51__annotation,
        __dataclass__init__fields__51__default,
        __dataclass__init__fields__52__annotation,
        __dataclass__init__fields__52__default,
        __dataclass__init__fields__53__annotation,
        __dataclass__init__fields__53__default,
        __dataclass__init__fields__54__annotation,
        __dataclass__init__fields__54__default,
        __dataclass__init__fields__55__annotation,
        __dataclass__init__fields__55__default,
        __dataclass__init__fields__56__annotation,
        __dataclass__init__fields__56__default,
        __dataclass__init__fields__57__annotation,
        __dataclass__init__fields__57__default,
        __dataclass__init__fields__58__annotation,
        __dataclass__init__fields__58__default,
        __dataclass__init__fields__59__annotation,
        __dataclass__init__fields__59__default,
        __dataclass__init__fields__5__annotation,
        __dataclass__init__fields__60__annotation,
        __dataclass__init__fields__60__default,
        __dataclass__init__fields__61__annotation,
        __dataclass__init__fields__61__default,
        __dataclass__init__fields__62__annotation,
        __dataclass__init__fields__62__default,
        __dataclass__init__fields__63__annotation,
        __dataclass__init__fields__63__default,
        __dataclass__init__fields__64__annotation,
        __dataclass__init__fields__64__default,
        __dataclass__init__fields__65__annotation,
        __dataclass__init__fields__65__default,
        __dataclass__init__fields__66__annotation,
        __dataclass__init__fields__66__default,
        __dataclass__init__fields__67__annotation,
        __dataclass__init__fields__67__default,
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
                db_name=self.db_name,
                db_instance_identifier=self.db_instance_identifier,
                allocated_storage=self.allocated_storage,
                db_instance_class=self.db_instance_class,
                engine=self.engine,
                master_username=self.master_username,
                master_user_password=self.master_user_password,
                db_security_groups=self.db_security_groups,
                vpc_security_group_ids=self.vpc_security_group_ids,
                availability_zone=self.availability_zone,
                db_subnet_group_name=self.db_subnet_group_name,
                preferred_maintenance_window=self.preferred_maintenance_window,
                db_parameter_group_name=self.db_parameter_group_name,
                backup_retention_period=self.backup_retention_period,
                preferred_backup_window=self.preferred_backup_window,
                port=self.port,
                multi_az=self.multi_az,
                engine_version=self.engine_version,
                auto_minor_version_upgrade=self.auto_minor_version_upgrade,
                license_model=self.license_model,
                iops=self.iops,
                storage_throughput=self.storage_throughput,
                option_group_name=self.option_group_name,
                character_set_name=self.character_set_name,
                nchar_character_set_name=self.nchar_character_set_name,
                publicly_accessible=self.publicly_accessible,
                tags=self.tags,
                db_cluster_identifier=self.db_cluster_identifier,
                storage_type=self.storage_type,
                tde_credential_arn=self.tde_credential_arn,
                tde_credential_password=self.tde_credential_password,
                storage_encrypted=self.storage_encrypted,
                kms_key_id=self.kms_key_id,
                domain=self.domain,
                domain_fqdn=self.domain_fqdn,
                domain_ou=self.domain_ou,
                domain_auth_secret_arn=self.domain_auth_secret_arn,
                domain_dns_ips=self.domain_dns_ips,
                copy_tags_to_snapshot=self.copy_tags_to_snapshot,
                monitoring_interval=self.monitoring_interval,
                monitoring_role_arn=self.monitoring_role_arn,
                domain_iam_role_name=self.domain_iam_role_name,
                promotion_tier=self.promotion_tier,
                timezone=self.timezone,
                enable_iam_database_authentication=self.enable_iam_database_authentication,
                database_insights_mode=self.database_insights_mode,
                enable_performance_insights=self.enable_performance_insights,
                performance_insights_kms_key_id=self.performance_insights_kms_key_id,
                performance_insights_retention_period=self.performance_insights_retention_period,
                enable_cloudwatch_logs_exports=self.enable_cloudwatch_logs_exports,
                processor_features=self.processor_features,
                deletion_protection=self.deletion_protection,
                max_allocated_storage=self.max_allocated_storage,
                enable_customer_owned_ip=self.enable_customer_owned_ip,
                network_type=self.network_type,
                backup_target=self.backup_target,
                custom_iam_instance_profile=self.custom_iam_instance_profile,
                db_system_id=self.db_system_id,
                ca_certificate_identifier=self.ca_certificate_identifier,
                manage_master_user_password=self.manage_master_user_password,
                master_user_secret_kms_key_id=self.master_user_secret_kms_key_id,
                multi_tenant=self.multi_tenant,
                dedicated_log_volume=self.dedicated_log_volume,
                engine_lifecycle_support=self.engine_lifecycle_support,
                tag_specifications=self.tag_specifications,
                master_user_authentication_type=self.master_user_authentication_type,
                additional_storage_volumes=self.additional_storage_volumes,
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
                self.db_name == other.db_name and
                self.db_instance_identifier == other.db_instance_identifier and
                self.allocated_storage == other.allocated_storage and
                self.db_instance_class == other.db_instance_class and
                self.engine == other.engine and
                self.master_username == other.master_username and
                self.master_user_password == other.master_user_password and
                self.db_security_groups == other.db_security_groups and
                self.vpc_security_group_ids == other.vpc_security_group_ids and
                self.availability_zone == other.availability_zone and
                self.db_subnet_group_name == other.db_subnet_group_name and
                self.preferred_maintenance_window == other.preferred_maintenance_window and
                self.db_parameter_group_name == other.db_parameter_group_name and
                self.backup_retention_period == other.backup_retention_period and
                self.preferred_backup_window == other.preferred_backup_window and
                self.port == other.port and
                self.multi_az == other.multi_az and
                self.engine_version == other.engine_version and
                self.auto_minor_version_upgrade == other.auto_minor_version_upgrade and
                self.license_model == other.license_model and
                self.iops == other.iops and
                self.storage_throughput == other.storage_throughput and
                self.option_group_name == other.option_group_name and
                self.character_set_name == other.character_set_name and
                self.nchar_character_set_name == other.nchar_character_set_name and
                self.publicly_accessible == other.publicly_accessible and
                self.tags == other.tags and
                self.db_cluster_identifier == other.db_cluster_identifier and
                self.storage_type == other.storage_type and
                self.tde_credential_arn == other.tde_credential_arn and
                self.tde_credential_password == other.tde_credential_password and
                self.storage_encrypted == other.storage_encrypted and
                self.kms_key_id == other.kms_key_id and
                self.domain == other.domain and
                self.domain_fqdn == other.domain_fqdn and
                self.domain_ou == other.domain_ou and
                self.domain_auth_secret_arn == other.domain_auth_secret_arn and
                self.domain_dns_ips == other.domain_dns_ips and
                self.copy_tags_to_snapshot == other.copy_tags_to_snapshot and
                self.monitoring_interval == other.monitoring_interval and
                self.monitoring_role_arn == other.monitoring_role_arn and
                self.domain_iam_role_name == other.domain_iam_role_name and
                self.promotion_tier == other.promotion_tier and
                self.timezone == other.timezone and
                self.enable_iam_database_authentication == other.enable_iam_database_authentication and
                self.database_insights_mode == other.database_insights_mode and
                self.enable_performance_insights == other.enable_performance_insights and
                self.performance_insights_kms_key_id == other.performance_insights_kms_key_id and
                self.performance_insights_retention_period == other.performance_insights_retention_period and
                self.enable_cloudwatch_logs_exports == other.enable_cloudwatch_logs_exports and
                self.processor_features == other.processor_features and
                self.deletion_protection == other.deletion_protection and
                self.max_allocated_storage == other.max_allocated_storage and
                self.enable_customer_owned_ip == other.enable_customer_owned_ip and
                self.network_type == other.network_type and
                self.backup_target == other.backup_target and
                self.custom_iam_instance_profile == other.custom_iam_instance_profile and
                self.db_system_id == other.db_system_id and
                self.ca_certificate_identifier == other.ca_certificate_identifier and
                self.manage_master_user_password == other.manage_master_user_password and
                self.master_user_secret_kms_key_id == other.master_user_secret_kms_key_id and
                self.multi_tenant == other.multi_tenant and
                self.dedicated_log_volume == other.dedicated_log_volume and
                self.engine_lifecycle_support == other.engine_lifecycle_support and
                self.tag_specifications == other.tag_specifications and
                self.master_user_authentication_type == other.master_user_authentication_type and
                self.additional_storage_volumes == other.additional_storage_volumes
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'db_name',
            'db_instance_identifier',
            'allocated_storage',
            'db_instance_class',
            'engine',
            'master_username',
            'master_user_password',
            'db_security_groups',
            'vpc_security_group_ids',
            'availability_zone',
            'db_subnet_group_name',
            'preferred_maintenance_window',
            'db_parameter_group_name',
            'backup_retention_period',
            'preferred_backup_window',
            'port',
            'multi_az',
            'engine_version',
            'auto_minor_version_upgrade',
            'license_model',
            'iops',
            'storage_throughput',
            'option_group_name',
            'character_set_name',
            'nchar_character_set_name',
            'publicly_accessible',
            'tags',
            'db_cluster_identifier',
            'storage_type',
            'tde_credential_arn',
            'tde_credential_password',
            'storage_encrypted',
            'kms_key_id',
            'domain',
            'domain_fqdn',
            'domain_ou',
            'domain_auth_secret_arn',
            'domain_dns_ips',
            'copy_tags_to_snapshot',
            'monitoring_interval',
            'monitoring_role_arn',
            'domain_iam_role_name',
            'promotion_tier',
            'timezone',
            'enable_iam_database_authentication',
            'database_insights_mode',
            'enable_performance_insights',
            'performance_insights_kms_key_id',
            'performance_insights_retention_period',
            'enable_cloudwatch_logs_exports',
            'processor_features',
            'deletion_protection',
            'max_allocated_storage',
            'enable_customer_owned_ip',
            'network_type',
            'backup_target',
            'custom_iam_instance_profile',
            'db_system_id',
            'ca_certificate_identifier',
            'manage_master_user_password',
            'master_user_secret_kms_key_id',
            'multi_tenant',
            'dedicated_log_volume',
            'engine_lifecycle_support',
            'tag_specifications',
            'master_user_authentication_type',
            'additional_storage_volumes',
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
            '__shape__',
            'db_name',
            'db_instance_identifier',
            'allocated_storage',
            'db_instance_class',
            'engine',
            'master_username',
            'master_user_password',
            'db_security_groups',
            'vpc_security_group_ids',
            'availability_zone',
            'db_subnet_group_name',
            'preferred_maintenance_window',
            'db_parameter_group_name',
            'backup_retention_period',
            'preferred_backup_window',
            'port',
            'multi_az',
            'engine_version',
            'auto_minor_version_upgrade',
            'license_model',
            'iops',
            'storage_throughput',
            'option_group_name',
            'character_set_name',
            'nchar_character_set_name',
            'publicly_accessible',
            'tags',
            'db_cluster_identifier',
            'storage_type',
            'tde_credential_arn',
            'tde_credential_password',
            'storage_encrypted',
            'kms_key_id',
            'domain',
            'domain_fqdn',
            'domain_ou',
            'domain_auth_secret_arn',
            'domain_dns_ips',
            'copy_tags_to_snapshot',
            'monitoring_interval',
            'monitoring_role_arn',
            'domain_iam_role_name',
            'promotion_tier',
            'timezone',
            'enable_iam_database_authentication',
            'database_insights_mode',
            'enable_performance_insights',
            'performance_insights_kms_key_id',
            'performance_insights_retention_period',
            'enable_cloudwatch_logs_exports',
            'processor_features',
            'deletion_protection',
            'max_allocated_storage',
            'enable_customer_owned_ip',
            'network_type',
            'backup_target',
            'custom_iam_instance_profile',
            'db_system_id',
            'ca_certificate_identifier',
            'manage_master_user_password',
            'master_user_secret_kms_key_id',
            'multi_tenant',
            'dedicated_log_volume',
            'engine_lifecycle_support',
            'tag_specifications',
            'master_user_authentication_type',
            'additional_storage_volumes',
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
                self.db_name,
                self.db_instance_identifier,
                self.allocated_storage,
                self.db_instance_class,
                self.engine,
                self.master_username,
                self.master_user_password,
                self.db_security_groups,
                self.vpc_security_group_ids,
                self.availability_zone,
                self.db_subnet_group_name,
                self.preferred_maintenance_window,
                self.db_parameter_group_name,
                self.backup_retention_period,
                self.preferred_backup_window,
                self.port,
                self.multi_az,
                self.engine_version,
                self.auto_minor_version_upgrade,
                self.license_model,
                self.iops,
                self.storage_throughput,
                self.option_group_name,
                self.character_set_name,
                self.nchar_character_set_name,
                self.publicly_accessible,
                self.tags,
                self.db_cluster_identifier,
                self.storage_type,
                self.tde_credential_arn,
                self.tde_credential_password,
                self.storage_encrypted,
                self.kms_key_id,
                self.domain,
                self.domain_fqdn,
                self.domain_ou,
                self.domain_auth_secret_arn,
                self.domain_dns_ips,
                self.copy_tags_to_snapshot,
                self.monitoring_interval,
                self.monitoring_role_arn,
                self.domain_iam_role_name,
                self.promotion_tier,
                self.timezone,
                self.enable_iam_database_authentication,
                self.database_insights_mode,
                self.enable_performance_insights,
                self.performance_insights_kms_key_id,
                self.performance_insights_retention_period,
                self.enable_cloudwatch_logs_exports,
                self.processor_features,
                self.deletion_protection,
                self.max_allocated_storage,
                self.enable_customer_owned_ip,
                self.network_type,
                self.backup_target,
                self.custom_iam_instance_profile,
                self.db_system_id,
                self.ca_certificate_identifier,
                self.manage_master_user_password,
                self.master_user_secret_kms_key_id,
                self.multi_tenant,
                self.dedicated_log_volume,
                self.engine_lifecycle_support,
                self.tag_specifications,
                self.master_user_authentication_type,
                self.additional_storage_volumes,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            db_name: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            db_instance_identifier: __dataclass__init__fields__2__annotation,
            allocated_storage: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            db_instance_class: __dataclass__init__fields__4__annotation,
            engine: __dataclass__init__fields__5__annotation,
            master_username: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
            master_user_password: __dataclass__init__fields__7__annotation = __dataclass__init__fields__7__default,
            db_security_groups: __dataclass__init__fields__8__annotation = __dataclass__init__fields__8__default,
            vpc_security_group_ids: __dataclass__init__fields__9__annotation = __dataclass__init__fields__9__default,
            availability_zone: __dataclass__init__fields__10__annotation = __dataclass__init__fields__10__default,
            db_subnet_group_name: __dataclass__init__fields__11__annotation = __dataclass__init__fields__11__default,
            preferred_maintenance_window: __dataclass__init__fields__12__annotation = __dataclass__init__fields__12__default,
            db_parameter_group_name: __dataclass__init__fields__13__annotation = __dataclass__init__fields__13__default,
            backup_retention_period: __dataclass__init__fields__14__annotation = __dataclass__init__fields__14__default,
            preferred_backup_window: __dataclass__init__fields__15__annotation = __dataclass__init__fields__15__default,
            port: __dataclass__init__fields__16__annotation = __dataclass__init__fields__16__default,
            multi_az: __dataclass__init__fields__17__annotation = __dataclass__init__fields__17__default,
            engine_version: __dataclass__init__fields__18__annotation = __dataclass__init__fields__18__default,
            auto_minor_version_upgrade: __dataclass__init__fields__19__annotation = __dataclass__init__fields__19__default,
            license_model: __dataclass__init__fields__20__annotation = __dataclass__init__fields__20__default,
            iops: __dataclass__init__fields__21__annotation = __dataclass__init__fields__21__default,
            storage_throughput: __dataclass__init__fields__22__annotation = __dataclass__init__fields__22__default,
            option_group_name: __dataclass__init__fields__23__annotation = __dataclass__init__fields__23__default,
            character_set_name: __dataclass__init__fields__24__annotation = __dataclass__init__fields__24__default,
            nchar_character_set_name: __dataclass__init__fields__25__annotation = __dataclass__init__fields__25__default,
            publicly_accessible: __dataclass__init__fields__26__annotation = __dataclass__init__fields__26__default,
            tags: __dataclass__init__fields__27__annotation = __dataclass__init__fields__27__default,
            db_cluster_identifier: __dataclass__init__fields__28__annotation = __dataclass__init__fields__28__default,
            storage_type: __dataclass__init__fields__29__annotation = __dataclass__init__fields__29__default,
            tde_credential_arn: __dataclass__init__fields__30__annotation = __dataclass__init__fields__30__default,
            tde_credential_password: __dataclass__init__fields__31__annotation = __dataclass__init__fields__31__default,
            storage_encrypted: __dataclass__init__fields__32__annotation = __dataclass__init__fields__32__default,
            kms_key_id: __dataclass__init__fields__33__annotation = __dataclass__init__fields__33__default,
            domain: __dataclass__init__fields__34__annotation = __dataclass__init__fields__34__default,
            domain_fqdn: __dataclass__init__fields__35__annotation = __dataclass__init__fields__35__default,
            domain_ou: __dataclass__init__fields__36__annotation = __dataclass__init__fields__36__default,
            domain_auth_secret_arn: __dataclass__init__fields__37__annotation = __dataclass__init__fields__37__default,
            domain_dns_ips: __dataclass__init__fields__38__annotation = __dataclass__init__fields__38__default,
            copy_tags_to_snapshot: __dataclass__init__fields__39__annotation = __dataclass__init__fields__39__default,
            monitoring_interval: __dataclass__init__fields__40__annotation = __dataclass__init__fields__40__default,
            monitoring_role_arn: __dataclass__init__fields__41__annotation = __dataclass__init__fields__41__default,
            domain_iam_role_name: __dataclass__init__fields__42__annotation = __dataclass__init__fields__42__default,
            promotion_tier: __dataclass__init__fields__43__annotation = __dataclass__init__fields__43__default,
            timezone: __dataclass__init__fields__44__annotation = __dataclass__init__fields__44__default,
            enable_iam_database_authentication: __dataclass__init__fields__45__annotation = __dataclass__init__fields__45__default,
            database_insights_mode: __dataclass__init__fields__46__annotation = __dataclass__init__fields__46__default,
            enable_performance_insights: __dataclass__init__fields__47__annotation = __dataclass__init__fields__47__default,
            performance_insights_kms_key_id: __dataclass__init__fields__48__annotation = __dataclass__init__fields__48__default,
            performance_insights_retention_period: __dataclass__init__fields__49__annotation = __dataclass__init__fields__49__default,
            enable_cloudwatch_logs_exports: __dataclass__init__fields__50__annotation = __dataclass__init__fields__50__default,
            processor_features: __dataclass__init__fields__51__annotation = __dataclass__init__fields__51__default,
            deletion_protection: __dataclass__init__fields__52__annotation = __dataclass__init__fields__52__default,
            max_allocated_storage: __dataclass__init__fields__53__annotation = __dataclass__init__fields__53__default,
            enable_customer_owned_ip: __dataclass__init__fields__54__annotation = __dataclass__init__fields__54__default,
            network_type: __dataclass__init__fields__55__annotation = __dataclass__init__fields__55__default,
            backup_target: __dataclass__init__fields__56__annotation = __dataclass__init__fields__56__default,
            custom_iam_instance_profile: __dataclass__init__fields__57__annotation = __dataclass__init__fields__57__default,
            db_system_id: __dataclass__init__fields__58__annotation = __dataclass__init__fields__58__default,
            ca_certificate_identifier: __dataclass__init__fields__59__annotation = __dataclass__init__fields__59__default,
            manage_master_user_password: __dataclass__init__fields__60__annotation = __dataclass__init__fields__60__default,
            master_user_secret_kms_key_id: __dataclass__init__fields__61__annotation = __dataclass__init__fields__61__default,
            multi_tenant: __dataclass__init__fields__62__annotation = __dataclass__init__fields__62__default,
            dedicated_log_volume: __dataclass__init__fields__63__annotation = __dataclass__init__fields__63__default,
            engine_lifecycle_support: __dataclass__init__fields__64__annotation = __dataclass__init__fields__64__default,
            tag_specifications: __dataclass__init__fields__65__annotation = __dataclass__init__fields__65__default,
            master_user_authentication_type: __dataclass__init__fields__66__annotation = __dataclass__init__fields__66__default,
            additional_storage_volumes: __dataclass__init__fields__67__annotation = __dataclass__init__fields__67__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'db_name', db_name)
            __dataclass__object_setattr(self, 'db_instance_identifier', db_instance_identifier)
            __dataclass__object_setattr(self, 'allocated_storage', allocated_storage)
            __dataclass__object_setattr(self, 'db_instance_class', db_instance_class)
            __dataclass__object_setattr(self, 'engine', engine)
            __dataclass__object_setattr(self, 'master_username', master_username)
            __dataclass__object_setattr(self, 'master_user_password', master_user_password)
            __dataclass__object_setattr(self, 'db_security_groups', db_security_groups)
            __dataclass__object_setattr(self, 'vpc_security_group_ids', vpc_security_group_ids)
            __dataclass__object_setattr(self, 'availability_zone', availability_zone)
            __dataclass__object_setattr(self, 'db_subnet_group_name', db_subnet_group_name)
            __dataclass__object_setattr(self, 'preferred_maintenance_window', preferred_maintenance_window)
            __dataclass__object_setattr(self, 'db_parameter_group_name', db_parameter_group_name)
            __dataclass__object_setattr(self, 'backup_retention_period', backup_retention_period)
            __dataclass__object_setattr(self, 'preferred_backup_window', preferred_backup_window)
            __dataclass__object_setattr(self, 'port', port)
            __dataclass__object_setattr(self, 'multi_az', multi_az)
            __dataclass__object_setattr(self, 'engine_version', engine_version)
            __dataclass__object_setattr(self, 'auto_minor_version_upgrade', auto_minor_version_upgrade)
            __dataclass__object_setattr(self, 'license_model', license_model)
            __dataclass__object_setattr(self, 'iops', iops)
            __dataclass__object_setattr(self, 'storage_throughput', storage_throughput)
            __dataclass__object_setattr(self, 'option_group_name', option_group_name)
            __dataclass__object_setattr(self, 'character_set_name', character_set_name)
            __dataclass__object_setattr(self, 'nchar_character_set_name', nchar_character_set_name)
            __dataclass__object_setattr(self, 'publicly_accessible', publicly_accessible)
            __dataclass__object_setattr(self, 'tags', tags)
            __dataclass__object_setattr(self, 'db_cluster_identifier', db_cluster_identifier)
            __dataclass__object_setattr(self, 'storage_type', storage_type)
            __dataclass__object_setattr(self, 'tde_credential_arn', tde_credential_arn)
            __dataclass__object_setattr(self, 'tde_credential_password', tde_credential_password)
            __dataclass__object_setattr(self, 'storage_encrypted', storage_encrypted)
            __dataclass__object_setattr(self, 'kms_key_id', kms_key_id)
            __dataclass__object_setattr(self, 'domain', domain)
            __dataclass__object_setattr(self, 'domain_fqdn', domain_fqdn)
            __dataclass__object_setattr(self, 'domain_ou', domain_ou)
            __dataclass__object_setattr(self, 'domain_auth_secret_arn', domain_auth_secret_arn)
            __dataclass__object_setattr(self, 'domain_dns_ips', domain_dns_ips)
            __dataclass__object_setattr(self, 'copy_tags_to_snapshot', copy_tags_to_snapshot)
            __dataclass__object_setattr(self, 'monitoring_interval', monitoring_interval)
            __dataclass__object_setattr(self, 'monitoring_role_arn', monitoring_role_arn)
            __dataclass__object_setattr(self, 'domain_iam_role_name', domain_iam_role_name)
            __dataclass__object_setattr(self, 'promotion_tier', promotion_tier)
            __dataclass__object_setattr(self, 'timezone', timezone)
            __dataclass__object_setattr(self, 'enable_iam_database_authentication', enable_iam_database_authentication)
            __dataclass__object_setattr(self, 'database_insights_mode', database_insights_mode)
            __dataclass__object_setattr(self, 'enable_performance_insights', enable_performance_insights)
            __dataclass__object_setattr(self, 'performance_insights_kms_key_id', performance_insights_kms_key_id)
            __dataclass__object_setattr(self, 'performance_insights_retention_period', performance_insights_retention_period)
            __dataclass__object_setattr(self, 'enable_cloudwatch_logs_exports', enable_cloudwatch_logs_exports)
            __dataclass__object_setattr(self, 'processor_features', processor_features)
            __dataclass__object_setattr(self, 'deletion_protection', deletion_protection)
            __dataclass__object_setattr(self, 'max_allocated_storage', max_allocated_storage)
            __dataclass__object_setattr(self, 'enable_customer_owned_ip', enable_customer_owned_ip)
            __dataclass__object_setattr(self, 'network_type', network_type)
            __dataclass__object_setattr(self, 'backup_target', backup_target)
            __dataclass__object_setattr(self, 'custom_iam_instance_profile', custom_iam_instance_profile)
            __dataclass__object_setattr(self, 'db_system_id', db_system_id)
            __dataclass__object_setattr(self, 'ca_certificate_identifier', ca_certificate_identifier)
            __dataclass__object_setattr(self, 'manage_master_user_password', manage_master_user_password)
            __dataclass__object_setattr(self, 'master_user_secret_kms_key_id', master_user_secret_kms_key_id)
            __dataclass__object_setattr(self, 'multi_tenant', multi_tenant)
            __dataclass__object_setattr(self, 'dedicated_log_volume', dedicated_log_volume)
            __dataclass__object_setattr(self, 'engine_lifecycle_support', engine_lifecycle_support)
            __dataclass__object_setattr(self, 'tag_specifications', tag_specifications)
            __dataclass__object_setattr(self, 'master_user_authentication_type', master_user_authentication_type)
            __dataclass__object_setattr(self, 'additional_storage_volumes', additional_storage_volumes)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"db_name={self.db_name!r}")
            parts.append(f"db_instance_identifier={self.db_instance_identifier!r}")
            parts.append(f"allocated_storage={self.allocated_storage!r}")
            parts.append(f"db_instance_class={self.db_instance_class!r}")
            parts.append(f"engine={self.engine!r}")
            parts.append(f"master_username={self.master_username!r}")
            parts.append(f"master_user_password={self.master_user_password!r}")
            parts.append(f"db_security_groups={self.db_security_groups!r}")
            parts.append(f"vpc_security_group_ids={self.vpc_security_group_ids!r}")
            parts.append(f"availability_zone={self.availability_zone!r}")
            parts.append(f"db_subnet_group_name={self.db_subnet_group_name!r}")
            parts.append(f"preferred_maintenance_window={self.preferred_maintenance_window!r}")
            parts.append(f"db_parameter_group_name={self.db_parameter_group_name!r}")
            parts.append(f"backup_retention_period={self.backup_retention_period!r}")
            parts.append(f"preferred_backup_window={self.preferred_backup_window!r}")
            parts.append(f"port={self.port!r}")
            parts.append(f"multi_az={self.multi_az!r}")
            parts.append(f"engine_version={self.engine_version!r}")
            parts.append(f"auto_minor_version_upgrade={self.auto_minor_version_upgrade!r}")
            parts.append(f"license_model={self.license_model!r}")
            parts.append(f"iops={self.iops!r}")
            parts.append(f"storage_throughput={self.storage_throughput!r}")
            parts.append(f"option_group_name={self.option_group_name!r}")
            parts.append(f"character_set_name={self.character_set_name!r}")
            parts.append(f"nchar_character_set_name={self.nchar_character_set_name!r}")
            parts.append(f"publicly_accessible={self.publicly_accessible!r}")
            parts.append(f"tags={self.tags!r}")
            parts.append(f"db_cluster_identifier={self.db_cluster_identifier!r}")
            parts.append(f"storage_type={self.storage_type!r}")
            parts.append(f"tde_credential_arn={self.tde_credential_arn!r}")
            parts.append(f"tde_credential_password={self.tde_credential_password!r}")
            parts.append(f"storage_encrypted={self.storage_encrypted!r}")
            parts.append(f"kms_key_id={self.kms_key_id!r}")
            parts.append(f"domain={self.domain!r}")
            parts.append(f"domain_fqdn={self.domain_fqdn!r}")
            parts.append(f"domain_ou={self.domain_ou!r}")
            parts.append(f"domain_auth_secret_arn={self.domain_auth_secret_arn!r}")
            parts.append(f"domain_dns_ips={self.domain_dns_ips!r}")
            parts.append(f"copy_tags_to_snapshot={self.copy_tags_to_snapshot!r}")
            parts.append(f"monitoring_interval={self.monitoring_interval!r}")
            parts.append(f"monitoring_role_arn={self.monitoring_role_arn!r}")
            parts.append(f"domain_iam_role_name={self.domain_iam_role_name!r}")
            parts.append(f"promotion_tier={self.promotion_tier!r}")
            parts.append(f"timezone={self.timezone!r}")
            parts.append(f"enable_iam_database_authentication={self.enable_iam_database_authentication!r}")
            parts.append(f"database_insights_mode={self.database_insights_mode!r}")
            parts.append(f"enable_performance_insights={self.enable_performance_insights!r}")
            parts.append(f"performance_insights_kms_key_id={self.performance_insights_kms_key_id!r}")
            parts.append(f"performance_insights_retention_period={self.performance_insights_retention_period!r}")
            parts.append(f"enable_cloudwatch_logs_exports={self.enable_cloudwatch_logs_exports!r}")
            parts.append(f"processor_features={self.processor_features!r}")
            parts.append(f"deletion_protection={self.deletion_protection!r}")
            parts.append(f"max_allocated_storage={self.max_allocated_storage!r}")
            parts.append(f"enable_customer_owned_ip={self.enable_customer_owned_ip!r}")
            parts.append(f"network_type={self.network_type!r}")
            parts.append(f"backup_target={self.backup_target!r}")
            parts.append(f"custom_iam_instance_profile={self.custom_iam_instance_profile!r}")
            parts.append(f"db_system_id={self.db_system_id!r}")
            parts.append(f"ca_certificate_identifier={self.ca_certificate_identifier!r}")
            parts.append(f"manage_master_user_password={self.manage_master_user_password!r}")
            parts.append(f"master_user_secret_kms_key_id={self.master_user_secret_kms_key_id!r}")
            parts.append(f"multi_tenant={self.multi_tenant!r}")
            parts.append(f"dedicated_log_volume={self.dedicated_log_volume!r}")
            parts.append(f"engine_lifecycle_support={self.engine_lifecycle_support!r}")
            parts.append(f"tag_specifications={self.tag_specifications!r}")
            parts.append(f"master_user_authentication_type={self.master_user_authentication_type!r}")
            parts.append(f"additional_storage_volumes={self.additional_storage_volumes!r}")
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
        "Plans(tup=(CopyPlan(fields=('db_instance',)), EqPlan(fields=('db_instance',)), FrozenPlan(fields=('__shape__',"
        " 'db_instance'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('db_instance',), cache=Fals"
        "e), InitPlan(fields=(InitPlan.Field(name='__shape__', annotation=OpRef(name='init.fields.0.annotation'), defau"
        "lt=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS_VAR, coerce=None, validat"
        "e=None, check_type=None), InitPlan.Field(name='db_instance', annotation=OpRef(name='init.fields.1.annotation')"
        ", default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=Fie"
        "ldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_para"
        "ms=('db_instance',), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan("
        "fields=(ReprPlan.Field(name='db_instance', kw_only=True, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='e370acdd02f632f5ffa5833dfc2b29fa253e1324',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.rds', 'CreateDBInstanceResult'),
        ('ominfra.clouds.aws.models.services.rds', 'DeleteDBInstanceResult'),
        ('ominfra.clouds.aws.models.services.rds', 'RebootDBInstanceResult'),
        ('ominfra.clouds.aws.models.services.rds', 'StartDBInstanceResult'),
        ('ominfra.clouds.aws.models.services.rds', 'StopDBInstanceResult'),
    ),
)
def _process_dataclass__e370acdd02f632f5ffa5833dfc2b29fa253e1324():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
                db_instance=self.db_instance,
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
                self.db_instance == other.db_instance
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'db_instance',
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
            '__shape__',
            'db_instance',
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
                self.db_instance,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            db_instance: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'db_instance', db_instance)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"db_instance={self.db_instance!r}")
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
        "Plans(tup=(CopyPlan(fields=('db_instance_identifier', 'db_instance_class', 'engine', 'db_instance_status', 'ma"
        "ster_username', 'db_name', 'endpoint', 'allocated_storage', 'instance_create_time', 'preferred_backup_window',"
        " 'backup_retention_period', 'db_security_groups', 'vpc_security_groups', 'db_parameter_groups', 'availability_"
        "zone', 'db_subnet_group', 'preferred_maintenance_window', 'upgrade_rollout_order', 'pending_modified_values', "
        "'latest_restorable_time', 'multi_az', 'engine_version', 'auto_minor_version_upgrade', 'read_replica_source_db_"
        "instance_identifier', 'read_replica_db_instance_identifiers', 'read_replica_db_cluster_identifiers', 'replica_"
        "mode', 'license_model', 'iops', 'storage_throughput', 'option_group_memberships', 'character_set_name', 'nchar"
        "_character_set_name', 'secondary_availability_zone', 'publicly_accessible', 'status_infos', 'storage_type', 't"
        "de_credential_arn', 'db_instance_port', 'db_cluster_identifier', 'storage_encrypted', 'kms_key_id', 'dbi_resou"
        "rce_id', 'ca_certificate_identifier', 'domain_memberships', 'copy_tags_to_snapshot', 'monitoring_interval', 'e"
        "nhanced_monitoring_resource_arn', 'monitoring_role_arn', 'promotion_tier', 'db_instance_arn', 'timezone', 'iam"
        "_database_authentication_enabled', 'database_insights_mode', 'performance_insights_enabled', 'performance_insi"
        "ghts_kms_key_id', 'performance_insights_retention_period', 'enabled_cloudwatch_logs_exports', 'processor_featu"
        "res', 'deletion_protection', 'associated_roles', 'listener_endpoint', 'max_allocated_storage', 'tag_list', 'au"
        "tomation_mode', 'resume_full_automation_mode_time', 'customer_owned_ip_enabled', 'network_type', 'activity_str"
        "eam_status', 'activity_stream_kms_key_id', 'activity_stream_kinesis_stream_name', 'activity_stream_mode', 'act"
        "ivity_stream_engine_native_audit_fields_included', 'aws_backup_recovery_point_arn', 'db_instance_automated_bac"
        "kups_replications', 'backup_target', 'automatic_restart_time', 'custom_iam_instance_profile', 'activity_stream"
        "_policy_status', 'certificate_details', 'db_system_id', 'master_user_secret', 'read_replica_source_db_cluster_"
        "identifier', 'percent_progress', 'multi_tenant', 'dedicated_log_volume', 'is_storage_config_upgrade_available'"
        ", 'engine_lifecycle_support', 'additional_storage_volumes', 'storage_volume_status')), EqPlan(fields=('db_inst"
        "ance_identifier', 'db_instance_class', 'engine', 'db_instance_status', 'master_username', 'db_name', 'endpoint"
        "', 'allocated_storage', 'instance_create_time', 'preferred_backup_window', 'backup_retention_period', 'db_secu"
        "rity_groups', 'vpc_security_groups', 'db_parameter_groups', 'availability_zone', 'db_subnet_group', 'preferred"
        "_maintenance_window', 'upgrade_rollout_order', 'pending_modified_values', 'latest_restorable_time', 'multi_az'"
        ", 'engine_version', 'auto_minor_version_upgrade', 'read_replica_source_db_instance_identifier', 'read_replica_"
        "db_instance_identifiers', 'read_replica_db_cluster_identifiers', 'replica_mode', 'license_model', 'iops', 'sto"
        "rage_throughput', 'option_group_memberships', 'character_set_name', 'nchar_character_set_name', 'secondary_ava"
        "ilability_zone', 'publicly_accessible', 'status_infos', 'storage_type', 'tde_credential_arn', 'db_instance_por"
        "t', 'db_cluster_identifier', 'storage_encrypted', 'kms_key_id', 'dbi_resource_id', 'ca_certificate_identifier'"
        ", 'domain_memberships', 'copy_tags_to_snapshot', 'monitoring_interval', 'enhanced_monitoring_resource_arn', 'm"
        "onitoring_role_arn', 'promotion_tier', 'db_instance_arn', 'timezone', 'iam_database_authentication_enabled', '"
        "database_insights_mode', 'performance_insights_enabled', 'performance_insights_kms_key_id', 'performance_insig"
        "hts_retention_period', 'enabled_cloudwatch_logs_exports', 'processor_features', 'deletion_protection', 'associ"
        "ated_roles', 'listener_endpoint', 'max_allocated_storage', 'tag_list', 'automation_mode', 'resume_full_automat"
        "ion_mode_time', 'customer_owned_ip_enabled', 'network_type', 'activity_stream_status', 'activity_stream_kms_ke"
        "y_id', 'activity_stream_kinesis_stream_name', 'activity_stream_mode', 'activity_stream_engine_native_audit_fie"
        "lds_included', 'aws_backup_recovery_point_arn', 'db_instance_automated_backups_replications', 'backup_target',"
        " 'automatic_restart_time', 'custom_iam_instance_profile', 'activity_stream_policy_status', 'certificate_detail"
        "s', 'db_system_id', 'master_user_secret', 'read_replica_source_db_cluster_identifier', 'percent_progress', 'mu"
        "lti_tenant', 'dedicated_log_volume', 'is_storage_config_upgrade_available', 'engine_lifecycle_support', 'addit"
        "ional_storage_volumes', 'storage_volume_status')), FrozenPlan(fields=('__shape__', 'db_instance_identifier', '"
        "db_instance_class', 'engine', 'db_instance_status', 'master_username', 'db_name', 'endpoint', 'allocated_stora"
        "ge', 'instance_create_time', 'preferred_backup_window', 'backup_retention_period', 'db_security_groups', 'vpc_"
        "security_groups', 'db_parameter_groups', 'availability_zone', 'db_subnet_group', 'preferred_maintenance_window"
        "', 'upgrade_rollout_order', 'pending_modified_values', 'latest_restorable_time', 'multi_az', 'engine_version',"
        " 'auto_minor_version_upgrade', 'read_replica_source_db_instance_identifier', 'read_replica_db_instance_identif"
        "iers', 'read_replica_db_cluster_identifiers', 'replica_mode', 'license_model', 'iops', 'storage_throughput', '"
        "option_group_memberships', 'character_set_name', 'nchar_character_set_name', 'secondary_availability_zone', 'p"
        "ublicly_accessible', 'status_infos', 'storage_type', 'tde_credential_arn', 'db_instance_port', 'db_cluster_ide"
        "ntifier', 'storage_encrypted', 'kms_key_id', 'dbi_resource_id', 'ca_certificate_identifier', 'domain_membershi"
        "ps', 'copy_tags_to_snapshot', 'monitoring_interval', 'enhanced_monitoring_resource_arn', 'monitoring_role_arn'"
        ", 'promotion_tier', 'db_instance_arn', 'timezone', 'iam_database_authentication_enabled', 'database_insights_m"
        "ode', 'performance_insights_enabled', 'performance_insights_kms_key_id', 'performance_insights_retention_perio"
        "d', 'enabled_cloudwatch_logs_exports', 'processor_features', 'deletion_protection', 'associated_roles', 'liste"
        "ner_endpoint', 'max_allocated_storage', 'tag_list', 'automation_mode', 'resume_full_automation_mode_time', 'cu"
        "stomer_owned_ip_enabled', 'network_type', 'activity_stream_status', 'activity_stream_kms_key_id', 'activity_st"
        "ream_kinesis_stream_name', 'activity_stream_mode', 'activity_stream_engine_native_audit_fields_included', 'aws"
        "_backup_recovery_point_arn', 'db_instance_automated_backups_replications', 'backup_target', 'automatic_restart"
        "_time', 'custom_iam_instance_profile', 'activity_stream_policy_status', 'certificate_details', 'db_system_id',"
        " 'master_user_secret', 'read_replica_source_db_cluster_identifier', 'percent_progress', 'multi_tenant', 'dedic"
        "ated_log_volume', 'is_storage_config_upgrade_available', 'engine_lifecycle_support', 'additional_storage_volum"
        "es', 'storage_volume_status'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('db_instance_"
        "identifier', 'db_instance_class', 'engine', 'db_instance_status', 'master_username', 'db_name', 'endpoint', 'a"
        "llocated_storage', 'instance_create_time', 'preferred_backup_window', 'backup_retention_period', 'db_security_"
        "groups', 'vpc_security_groups', 'db_parameter_groups', 'availability_zone', 'db_subnet_group', 'preferred_main"
        "tenance_window', 'upgrade_rollout_order', 'pending_modified_values', 'latest_restorable_time', 'multi_az', 'en"
        "gine_version', 'auto_minor_version_upgrade', 'read_replica_source_db_instance_identifier', 'read_replica_db_in"
        "stance_identifiers', 'read_replica_db_cluster_identifiers', 'replica_mode', 'license_model', 'iops', 'storage_"
        "throughput', 'option_group_memberships', 'character_set_name', 'nchar_character_set_name', 'secondary_availabi"
        "lity_zone', 'publicly_accessible', 'status_infos', 'storage_type', 'tde_credential_arn', 'db_instance_port', '"
        "db_cluster_identifier', 'storage_encrypted', 'kms_key_id', 'dbi_resource_id', 'ca_certificate_identifier', 'do"
        "main_memberships', 'copy_tags_to_snapshot', 'monitoring_interval', 'enhanced_monitoring_resource_arn', 'monito"
        "ring_role_arn', 'promotion_tier', 'db_instance_arn', 'timezone', 'iam_database_authentication_enabled', 'datab"
        "ase_insights_mode', 'performance_insights_enabled', 'performance_insights_kms_key_id', 'performance_insights_r"
        "etention_period', 'enabled_cloudwatch_logs_exports', 'processor_features', 'deletion_protection', 'associated_"
        "roles', 'listener_endpoint', 'max_allocated_storage', 'tag_list', 'automation_mode', 'resume_full_automation_m"
        "ode_time', 'customer_owned_ip_enabled', 'network_type', 'activity_stream_status', 'activity_stream_kms_key_id'"
        ", 'activity_stream_kinesis_stream_name', 'activity_stream_mode', 'activity_stream_engine_native_audit_fields_i"
        "ncluded', 'aws_backup_recovery_point_arn', 'db_instance_automated_backups_replications', 'backup_target', 'aut"
        "omatic_restart_time', 'custom_iam_instance_profile', 'activity_stream_policy_status', 'certificate_details', '"
        "db_system_id', 'master_user_secret', 'read_replica_source_db_cluster_identifier', 'percent_progress', 'multi_t"
        "enant', 'dedicated_log_volume', 'is_storage_config_upgrade_available', 'engine_lifecycle_support', 'additional"
        "_storage_volumes', 'storage_volume_status'), cache=False), InitPlan(fields=(InitPlan.Field(name='__shape__', a"
        "nnotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=Fals"
        "e, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='db_insta"
        "nce_identifier', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'"
        "), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None,"
        " check_type=None), InitPlan.Field(name='db_instance_class', annotation=OpRef(name='init.fields.2.annotation'),"
        " default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=Fiel"
        "dType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='engine', annotation=OpRef(n"
        "ame='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True,"
        " override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(n"
        "ame='db_instance_status', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4"
        ".default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valid"
        "ate=None, check_type=None), InitPlan.Field(name='master_username', annotation=OpRef(name='init.fields.5.annota"
        "tion'), default=OpRef(name='init.fields.5.default'), default_factory=None, init=True, override=False, field_ty"
        "pe=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='db_name', annotation"
        "=OpRef(name='init.fields.6.annotation'), default=OpRef(name='init.fields.6.default'), default_factory=None, in"
        "it=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan"
        ".Field(name='endpoint', annotation=OpRef(name='init.fields.7.annotation'), default=OpRef(name='init.fields.7.d"
        "efault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validat"
        "e=None, check_type=None), InitPlan.Field(name='allocated_storage', annotation=OpRef(name='init.fields.8.annota"
        "tion'), default=OpRef(name='init.fields.8.default'), default_factory=None, init=True, override=False, field_ty"
        "pe=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='instance_create_time"
        "', annotation=OpRef(name='init.fields.9.annotation'), default=OpRef(name='init.fields.9.default'), default_fac"
        "tory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=No"
        "ne), InitPlan.Field(name='preferred_backup_window', annotation=OpRef(name='init.fields.10.annotation'), defaul"
        "t=OpRef(name='init.fields.10.default'), default_factory=None, init=True, override=False, field_type=FieldType."
        "INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='backup_retention_period', annotat"
        "ion=OpRef(name='init.fields.11.annotation'), default=OpRef(name='init.fields.11.default'), default_factory=Non"
        "e, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), Ini"
        "tPlan.Field(name='db_security_groups', annotation=OpRef(name='init.fields.12.annotation'), default=OpRef(name="
        "'init.fields.12.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coe"
        "rce=None, validate=None, check_type=None), InitPlan.Field(name='vpc_security_groups', annotation=OpRef(name='i"
        "nit.fields.13.annotation'), default=OpRef(name='init.fields.13.default'), default_factory=None, init=True, ove"
        "rride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name="
        "'db_parameter_groups', annotation=OpRef(name='init.fields.14.annotation'), default=OpRef(name='init.fields.14."
        "default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valida"
        "te=None, check_type=None), InitPlan.Field(name='availability_zone', annotation=OpRef(name='init.fields.15.anno"
        "tation'), default=OpRef(name='init.fields.15.default'), default_factory=None, init=True, override=False, field"
        "_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='db_subnet_group',"
        " annotation=OpRef(name='init.fields.16.annotation'), default=OpRef(name='init.fields.16.default'), default_fac"
        "tory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=No"
        "ne), InitPlan.Field(name='preferred_maintenance_window', annotation=OpRef(name='init.fields.17.annotation'), d"
        "efault=OpRef(name='init.fields.17.default'), default_factory=None, init=True, override=False, field_type=Field"
        "Type.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='upgrade_rollout_order', anno"
        "tation=OpRef(name='init.fields.18.annotation'), default=OpRef(name='init.fields.18.default'), default_factory="
        "None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), "
        "InitPlan.Field(name='pending_modified_values', annotation=OpRef(name='init.fields.19.annotation'), default=OpR"
        "ef(name='init.fields.19.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTA"
        "NCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='latest_restorable_time', annotation=Op"
        "Ref(name='init.fields.20.annotation'), default=OpRef(name='init.fields.20.default'), default_factory=None, ini"
        "t=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan."
        "Field(name='multi_az', annotation=OpRef(name='init.fields.21.annotation'), default=OpRef(name='init.fields.21."
        "default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valida"
        "te=None, check_type=None), InitPlan.Field(name='engine_version', annotation=OpRef(name='init.fields.22.annotat"
        "ion'), default=OpRef(name='init.fields.22.default'), default_factory=None, init=True, override=False, field_ty"
        "pe=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='auto_minor_version_u"
        "pgrade', annotation=OpRef(name='init.fields.23.annotation'), default=OpRef(name='init.fields.23.default'), def"
        "ault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check"
        "_type=None), InitPlan.Field(name='read_replica_source_db_instance_identifier', annotation=OpRef(name='init.fie"
        "lds.24.annotation'), default=OpRef(name='init.fields.24.default'), default_factory=None, init=True, override=F"
        "alse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='read_r"
        "eplica_db_instance_identifiers', annotation=OpRef(name='init.fields.25.annotation'), default=OpRef(name='init."
        "fields.25.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=No"
        "ne, validate=None, check_type=None), InitPlan.Field(name='read_replica_db_cluster_identifiers', annotation=OpR"
        "ef(name='init.fields.26.annotation'), default=OpRef(name='init.fields.26.default'), default_factory=None, init"
        "=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.F"
        "ield(name='replica_mode', annotation=OpRef(name='init.fields.27.annotation'), default=OpRef(name='init.fields."
        "27.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, val"
        "idate=None, check_type=None), InitPlan.Field(name='license_model', annotation=OpRef(name='init.fields.28.annot"
        "ation'), default=OpRef(name='init.fields.28.default'), default_factory=None, init=True, override=False, field_"
        "type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='iops', annotation="
        "OpRef(name='init.fields.29.annotation'), default=OpRef(name='init.fields.29.default'), default_factory=None, i"
        "nit=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPla"
        "n.Field(name='storage_throughput', annotation=OpRef(name='init.fields.30.annotation'), default=OpRef(name='ini"
        "t.fields.30.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce="
        "None, validate=None, check_type=None), InitPlan.Field(name='option_group_memberships', annotation=OpRef(name='"
        "init.fields.31.annotation'), default=OpRef(name='init.fields.31.default'), default_factory=None, init=True, ov"
        "erride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name"
        "='character_set_name', annotation=OpRef(name='init.fields.32.annotation'), default=OpRef(name='init.fields.32."
        "default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valida"
        "te=None, check_type=None), InitPlan.Field(name='nchar_character_set_name', annotation=OpRef(name='init.fields."
        "33.annotation'), default=OpRef(name='init.fields.33.default'), default_factory=None, init=True, override=False"
        ", field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='secondary_"
        "availability_zone', annotation=OpRef(name='init.fields.34.annotation'), default=OpRef(name='init.fields.34.def"
        "ault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate="
        "None, check_type=None), InitPlan.Field(name='publicly_accessible', annotation=OpRef(name='init.fields.35.annot"
        "ation'), default=OpRef(name='init.fields.35.default'), default_factory=None, init=True, override=False, field_"
        "type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='status_infos', ann"
        "otation=OpRef(name='init.fields.36.annotation'), default=OpRef(name='init.fields.36.default'), default_factory"
        "=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),"
        " InitPlan.Field(name='storage_type', annotation=OpRef(name='init.fields.37.annotation'), default=OpRef(name='i"
        "nit.fields.37.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerc"
        "e=None, validate=None, check_type=None), InitPlan.Field(name='tde_credential_arn', annotation=OpRef(name='init"
        ".fields.38.annotation'), default=OpRef(name='init.fields.38.default'), default_factory=None, init=True, overri"
        "de=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='db"
        "_instance_port', annotation=OpRef(name='init.fields.39.annotation'), default=OpRef(name='init.fields.39.defaul"
        "t'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=Non"
        "e, check_type=None), InitPlan.Field(name='db_cluster_identifier', annotation=OpRef(name='init.fields.40.annota"
        "tion'), default=OpRef(name='init.fields.40.default'), default_factory=None, init=True, override=False, field_t"
        "ype=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='storage_encrypted',"
        " annotation=OpRef(name='init.fields.41.annotation'), default=OpRef(name='init.fields.41.default'), default_fac"
        "tory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=No"
        "ne), InitPlan.Field(name='kms_key_id', annotation=OpRef(name='init.fields.42.annotation'), default=OpRef(name="
        "'init.fields.42.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coe"
        "rce=None, validate=None, check_type=None), InitPlan.Field(name='dbi_resource_id', annotation=OpRef(name='init."
        "fields.43.annotation'), default=OpRef(name='init.fields.43.default'), default_factory=None, init=True, overrid"
        "e=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='ca_"
        "certificate_identifier', annotation=OpRef(name='init.fields.44.annotation'), default=OpRef(name='init.fields.4"
        "4.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, vali"
        "date=None, check_type=None), InitPlan.Field(name='domain_memberships', annotation=OpRef(name='init.fields.45.a"
        "nnotation'), default=OpRef(name='init.fields.45.default'), default_factory=None, init=True, override=False, fi"
        "eld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='copy_tags_to_s"
        "napshot', annotation=OpRef(name='init.fields.46.annotation'), default=OpRef(name='init.fields.46.default'), de"
        "fault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, chec"
        "k_type=None), InitPlan.Field(name='monitoring_interval', annotation=OpRef(name='init.fields.47.annotation'), d"
        "efault=OpRef(name='init.fields.47.default'), default_factory=None, init=True, override=False, field_type=Field"
        "Type.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='enhanced_monitoring_resource"
        "_arn', annotation=OpRef(name='init.fields.48.annotation'), default=OpRef(name='init.fields.48.default'), defau"
        "lt_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_t"
        "ype=None), InitPlan.Field(name='monitoring_role_arn', annotation=OpRef(name='init.fields.49.annotation'), defa"
        "ult=OpRef(name='init.fields.49.default'), default_factory=None, init=True, override=False, field_type=FieldTyp"
        "e.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='promotion_tier', annotation=OpR"
        "ef(name='init.fields.50.annotation'), default=OpRef(name='init.fields.50.default'), default_factory=None, init"
        "=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.F"
        "ield(name='db_instance_arn', annotation=OpRef(name='init.fields.51.annotation'), default=OpRef(name='init.fiel"
        "ds.51.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, "
        "validate=None, check_type=None), InitPlan.Field(name='timezone', annotation=OpRef(name='init.fields.52.annotat"
        "ion'), default=OpRef(name='init.fields.52.default'), default_factory=None, init=True, override=False, field_ty"
        "pe=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='iam_database_authent"
        "ication_enabled', annotation=OpRef(name='init.fields.53.annotation'), default=OpRef(name='init.fields.53.defau"
        "lt'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=No"
        "ne, check_type=None), InitPlan.Field(name='database_insights_mode', annotation=OpRef(name='init.fields.54.anno"
        "tation'), default=OpRef(name='init.fields.54.default'), default_factory=None, init=True, override=False, field"
        "_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='performance_insig"
        "hts_enabled', annotation=OpRef(name='init.fields.55.annotation'), default=OpRef(name='init.fields.55.default')"
        ", default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, "
        "check_type=None), InitPlan.Field(name='performance_insights_kms_key_id', annotation=OpRef(name='init.fields.56"
        ".annotation'), default=OpRef(name='init.fields.56.default'), default_factory=None, init=True, override=False, "
        "field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='performance_"
        "insights_retention_period', annotation=OpRef(name='init.fields.57.annotation'), default=OpRef(name='init.field"
        "s.57.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, v"
        "alidate=None, check_type=None), InitPlan.Field(name='enabled_cloudwatch_logs_exports', annotation=OpRef(name='"
        "init.fields.58.annotation'), default=OpRef(name='init.fields.58.default'), default_factory=None, init=True, ov"
        "erride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name"
        "='processor_features', annotation=OpRef(name='init.fields.59.annotation'), default=OpRef(name='init.fields.59."
        "default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valida"
        "te=None, check_type=None), InitPlan.Field(name='deletion_protection', annotation=OpRef(name='init.fields.60.an"
        "notation'), default=OpRef(name='init.fields.60.default'), default_factory=None, init=True, override=False, fie"
        "ld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='associated_role"
        "s', annotation=OpRef(name='init.fields.61.annotation'), default=OpRef(name='init.fields.61.default'), default_"
        "factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type"
        "=None), InitPlan.Field(name='listener_endpoint', annotation=OpRef(name='init.fields.62.annotation'), default=O"
        "pRef(name='init.fields.62.default'), default_factory=None, init=True, override=False, field_type=FieldType.INS"
        "TANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='max_allocated_storage', annotation=O"
        "pRef(name='init.fields.63.annotation'), default=OpRef(name='init.fields.63.default'), default_factory=None, in"
        "it=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan"
        ".Field(name='tag_list', annotation=OpRef(name='init.fields.64.annotation'), default=OpRef(name='init.fields.64"
        ".default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valid"
        "ate=None, check_type=None), InitPlan.Field(name='automation_mode', annotation=OpRef(name='init.fields.65.annot"
        "ation'), default=OpRef(name='init.fields.65.default'), default_factory=None, init=True, override=False, field_"
        "type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='resume_full_automa"
        "tion_mode_time', annotation=OpRef(name='init.fields.66.annotation'), default=OpRef(name='init.fields.66.defaul"
        "t'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=Non"
        "e, check_type=None), InitPlan.Field(name='customer_owned_ip_enabled', annotation=OpRef(name='init.fields.67.an"
        "notation'), default=OpRef(name='init.fields.67.default'), default_factory=None, init=True, override=False, fie"
        "ld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='network_type', "
        "annotation=OpRef(name='init.fields.68.annotation'), default=OpRef(name='init.fields.68.default'), default_fact"
        "ory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=Non"
        "e), InitPlan.Field(name='activity_stream_status', annotation=OpRef(name='init.fields.69.annotation'), default="
        "OpRef(name='init.fields.69.default'), default_factory=None, init=True, override=False, field_type=FieldType.IN"
        "STANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='activity_stream_kms_key_id', annota"
        "tion=OpRef(name='init.fields.70.annotation'), default=OpRef(name='init.fields.70.default'), default_factory=No"
        "ne, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), In"
        "itPlan.Field(name='activity_stream_kinesis_stream_name', annotation=OpRef(name='init.fields.71.annotation'), d"
        "efault=OpRef(name='init.fields.71.default'), default_factory=None, init=True, override=False, field_type=Field"
        "Type.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='activity_stream_mode', annot"
        "ation=OpRef(name='init.fields.72.annotation'), default=OpRef(name='init.fields.72.default'), default_factory=N"
        "one, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), I"
        "nitPlan.Field(name='activity_stream_engine_native_audit_fields_included', annotation=OpRef(name='init.fields.7"
        "3.annotation'), default=OpRef(name='init.fields.73.default'), default_factory=None, init=True, override=False,"
        " field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='aws_backup_"
        "recovery_point_arn', annotation=OpRef(name='init.fields.74.annotation'), default=OpRef(name='init.fields.74.de"
        "fault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate"
        "=None, check_type=None), InitPlan.Field(name='db_instance_automated_backups_replications', annotation=OpRef(na"
        "me='init.fields.75.annotation'), default=OpRef(name='init.fields.75.default'), default_factory=None, init=True"
        ", override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field("
        "name='backup_target', annotation=OpRef(name='init.fields.76.annotation'), default=OpRef(name='init.fields.76.d"
        "efault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validat"
        "e=None, check_type=None), InitPlan.Field(name='automatic_restart_time', annotation=OpRef(name='init.fields.77."
        "annotation'), default=OpRef(name='init.fields.77.default'), default_factory=None, init=True, override=False, f"
        "ield_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='custom_iam_in"
        "stance_profile', annotation=OpRef(name='init.fields.78.annotation'), default=OpRef(name='init.fields.78.defaul"
        "t'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=Non"
        "e, check_type=None), InitPlan.Field(name='activity_stream_policy_status', annotation=OpRef(name='init.fields.7"
        "9.annotation'), default=OpRef(name='init.fields.79.default'), default_factory=None, init=True, override=False,"
        " field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='certificate"
        "_details', annotation=OpRef(name='init.fields.80.annotation'), default=OpRef(name='init.fields.80.default'), d"
        "efault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, che"
        "ck_type=None), InitPlan.Field(name='db_system_id', annotation=OpRef(name='init.fields.81.annotation'), default"
        "=OpRef(name='init.fields.81.default'), default_factory=None, init=True, override=False, field_type=FieldType.I"
        "NSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='master_user_secret', annotation=Op"
        "Ref(name='init.fields.82.annotation'), default=OpRef(name='init.fields.82.default'), default_factory=None, ini"
        "t=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan."
        "Field(name='read_replica_source_db_cluster_identifier', annotation=OpRef(name='init.fields.83.annotation'), de"
        "fault=OpRef(name='init.fields.83.default'), default_factory=None, init=True, override=False, field_type=FieldT"
        "ype.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='percent_progress', annotation"
        "=OpRef(name='init.fields.84.annotation'), default=OpRef(name='init.fields.84.default'), default_factory=None, "
        "init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPl"
        "an.Field(name='multi_tenant', annotation=OpRef(name='init.fields.85.annotation'), default=OpRef(name='init.fie"
        "lds.85.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None,"
        " validate=None, check_type=None), InitPlan.Field(name='dedicated_log_volume', annotation=OpRef(name='init.fiel"
        "ds.86.annotation'), default=OpRef(name='init.fields.86.default'), default_factory=None, init=True, override=Fa"
        "lse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='is_stor"
        "age_config_upgrade_available', annotation=OpRef(name='init.fields.87.annotation'), default=OpRef(name='init.fi"
        "elds.87.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None"
        ", validate=None, check_type=None), InitPlan.Field(name='engine_lifecycle_support', annotation=OpRef(name='init"
        ".fields.88.annotation'), default=OpRef(name='init.fields.88.default'), default_factory=None, init=True, overri"
        "de=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='ad"
        "ditional_storage_volumes', annotation=OpRef(name='init.fields.89.annotation'), default=OpRef(name='init.fields"
        ".89.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, va"
        "lidate=None, check_type=None), InitPlan.Field(name='storage_volume_status', annotation=OpRef(name='init.fields"
        ".90.annotation'), default=OpRef(name='init.fields.90.default'), default_factory=None, init=True, override=Fals"
        "e, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params"
        "=(), kw_only_params=('db_instance_identifier', 'db_instance_class', 'engine', 'db_instance_status', 'master_us"
        "ername', 'db_name', 'endpoint', 'allocated_storage', 'instance_create_time', 'preferred_backup_window', 'backu"
        "p_retention_period', 'db_security_groups', 'vpc_security_groups', 'db_parameter_groups', 'availability_zone', "
        "'db_subnet_group', 'preferred_maintenance_window', 'upgrade_rollout_order', 'pending_modified_values', 'latest"
        "_restorable_time', 'multi_az', 'engine_version', 'auto_minor_version_upgrade', 'read_replica_source_db_instanc"
        "e_identifier', 'read_replica_db_instance_identifiers', 'read_replica_db_cluster_identifiers', 'replica_mode', "
        "'license_model', 'iops', 'storage_throughput', 'option_group_memberships', 'character_set_name', 'nchar_charac"
        "ter_set_name', 'secondary_availability_zone', 'publicly_accessible', 'status_infos', 'storage_type', 'tde_cred"
        "ential_arn', 'db_instance_port', 'db_cluster_identifier', 'storage_encrypted', 'kms_key_id', 'dbi_resource_id'"
        ", 'ca_certificate_identifier', 'domain_memberships', 'copy_tags_to_snapshot', 'monitoring_interval', 'enhanced"
        "_monitoring_resource_arn', 'monitoring_role_arn', 'promotion_tier', 'db_instance_arn', 'timezone', 'iam_databa"
        "se_authentication_enabled', 'database_insights_mode', 'performance_insights_enabled', 'performance_insights_km"
        "s_key_id', 'performance_insights_retention_period', 'enabled_cloudwatch_logs_exports', 'processor_features', '"
        "deletion_protection', 'associated_roles', 'listener_endpoint', 'max_allocated_storage', 'tag_list', 'automatio"
        "n_mode', 'resume_full_automation_mode_time', 'customer_owned_ip_enabled', 'network_type', 'activity_stream_sta"
        "tus', 'activity_stream_kms_key_id', 'activity_stream_kinesis_stream_name', 'activity_stream_mode', 'activity_s"
        "tream_engine_native_audit_fields_included', 'aws_backup_recovery_point_arn', 'db_instance_automated_backups_re"
        "plications', 'backup_target', 'automatic_restart_time', 'custom_iam_instance_profile', 'activity_stream_policy"
        "_status', 'certificate_details', 'db_system_id', 'master_user_secret', 'read_replica_source_db_cluster_identif"
        "ier', 'percent_progress', 'multi_tenant', 'dedicated_log_volume', 'is_storage_config_upgrade_available', 'engi"
        "ne_lifecycle_support', 'additional_storage_volumes', 'storage_volume_status'), frozen=True, slots=False, post_"
        "init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='db_instance_identifier'"
        ", kw_only=True, fn=None), ReprPlan.Field(name='db_instance_class', kw_only=True, fn=None), ReprPlan.Field(name"
        "='engine', kw_only=True, fn=None), ReprPlan.Field(name='db_instance_status', kw_only=True, fn=None), ReprPlan."
        "Field(name='master_username', kw_only=True, fn=None), ReprPlan.Field(name='db_name', kw_only=True, fn=None), R"
        "eprPlan.Field(name='endpoint', kw_only=True, fn=None), ReprPlan.Field(name='allocated_storage', kw_only=True, "
        "fn=None), ReprPlan.Field(name='instance_create_time', kw_only=True, fn=None), ReprPlan.Field(name='preferred_b"
        "ackup_window', kw_only=True, fn=None), ReprPlan.Field(name='backup_retention_period', kw_only=True, fn=None), "
        "ReprPlan.Field(name='db_security_groups', kw_only=True, fn=None), ReprPlan.Field(name='vpc_security_groups', k"
        "w_only=True, fn=None), ReprPlan.Field(name='db_parameter_groups', kw_only=True, fn=None), ReprPlan.Field(name="
        "'availability_zone', kw_only=True, fn=None), ReprPlan.Field(name='db_subnet_group', kw_only=True, fn=None), Re"
        "prPlan.Field(name='preferred_maintenance_window', kw_only=True, fn=None), ReprPlan.Field(name='upgrade_rollout"
        "_order', kw_only=True, fn=None), ReprPlan.Field(name='pending_modified_values', kw_only=True, fn=None), ReprPl"
        "an.Field(name='latest_restorable_time', kw_only=True, fn=None), ReprPlan.Field(name='multi_az', kw_only=True, "
        "fn=None), ReprPlan.Field(name='engine_version', kw_only=True, fn=None), ReprPlan.Field(name='auto_minor_versio"
        "n_upgrade', kw_only=True, fn=None), ReprPlan.Field(name='read_replica_source_db_instance_identifier', kw_only="
        "True, fn=None), ReprPlan.Field(name='read_replica_db_instance_identifiers', kw_only=True, fn=None), ReprPlan.F"
        "ield(name='read_replica_db_cluster_identifiers', kw_only=True, fn=None), ReprPlan.Field(name='replica_mode', k"
        "w_only=True, fn=None), ReprPlan.Field(name='license_model', kw_only=True, fn=None), ReprPlan.Field(name='iops'"
        ", kw_only=True, fn=None), ReprPlan.Field(name='storage_throughput', kw_only=True, fn=None), ReprPlan.Field(nam"
        "e='option_group_memberships', kw_only=True, fn=None), ReprPlan.Field(name='character_set_name', kw_only=True, "
        "fn=None), ReprPlan.Field(name='nchar_character_set_name', kw_only=True, fn=None), ReprPlan.Field(name='seconda"
        "ry_availability_zone', kw_only=True, fn=None), ReprPlan.Field(name='publicly_accessible', kw_only=True, fn=Non"
        "e), ReprPlan.Field(name='status_infos', kw_only=True, fn=None), ReprPlan.Field(name='storage_type', kw_only=Tr"
        "ue, fn=None), ReprPlan.Field(name='tde_credential_arn', kw_only=True, fn=None), ReprPlan.Field(name='db_instan"
        "ce_port', kw_only=True, fn=None), ReprPlan.Field(name='db_cluster_identifier', kw_only=True, fn=None), ReprPla"
        "n.Field(name='storage_encrypted', kw_only=True, fn=None), ReprPlan.Field(name='kms_key_id', kw_only=True, fn=N"
        "one), ReprPlan.Field(name='dbi_resource_id', kw_only=True, fn=None), ReprPlan.Field(name='ca_certificate_ident"
        "ifier', kw_only=True, fn=None), ReprPlan.Field(name='domain_memberships', kw_only=True, fn=None), ReprPlan.Fie"
        "ld(name='copy_tags_to_snapshot', kw_only=True, fn=None), ReprPlan.Field(name='monitoring_interval', kw_only=Tr"
        "ue, fn=None), ReprPlan.Field(name='enhanced_monitoring_resource_arn', kw_only=True, fn=None), ReprPlan.Field(n"
        "ame='monitoring_role_arn', kw_only=True, fn=None), ReprPlan.Field(name='promotion_tier', kw_only=True, fn=None"
        "), ReprPlan.Field(name='db_instance_arn', kw_only=True, fn=None), ReprPlan.Field(name='timezone', kw_only=True"
        ", fn=None), ReprPlan.Field(name='iam_database_authentication_enabled', kw_only=True, fn=None), ReprPlan.Field("
        "name='database_insights_mode', kw_only=True, fn=None), ReprPlan.Field(name='performance_insights_enabled', kw_"
        "only=True, fn=None), ReprPlan.Field(name='performance_insights_kms_key_id', kw_only=True, fn=None), ReprPlan.F"
        "ield(name='performance_insights_retention_period', kw_only=True, fn=None), ReprPlan.Field(name='enabled_cloudw"
        "atch_logs_exports', kw_only=True, fn=None), ReprPlan.Field(name='processor_features', kw_only=True, fn=None), "
        "ReprPlan.Field(name='deletion_protection', kw_only=True, fn=None), ReprPlan.Field(name='associated_roles', kw_"
        "only=True, fn=None), ReprPlan.Field(name='listener_endpoint', kw_only=True, fn=None), ReprPlan.Field(name='max"
        "_allocated_storage', kw_only=True, fn=None), ReprPlan.Field(name='tag_list', kw_only=True, fn=None), ReprPlan."
        "Field(name='automation_mode', kw_only=True, fn=None), ReprPlan.Field(name='resume_full_automation_mode_time', "
        "kw_only=True, fn=None), ReprPlan.Field(name='customer_owned_ip_enabled', kw_only=True, fn=None), ReprPlan.Fiel"
        "d(name='network_type', kw_only=True, fn=None), ReprPlan.Field(name='activity_stream_status', kw_only=True, fn="
        "None), ReprPlan.Field(name='activity_stream_kms_key_id', kw_only=True, fn=None), ReprPlan.Field(name='activity"
        "_stream_kinesis_stream_name', kw_only=True, fn=None), ReprPlan.Field(name='activity_stream_mode', kw_only=True"
        ", fn=None), ReprPlan.Field(name='activity_stream_engine_native_audit_fields_included', kw_only=True, fn=None),"
        " ReprPlan.Field(name='aws_backup_recovery_point_arn', kw_only=True, fn=None), ReprPlan.Field(name='db_instance"
        "_automated_backups_replications', kw_only=True, fn=None), ReprPlan.Field(name='backup_target', kw_only=True, f"
        "n=None), ReprPlan.Field(name='automatic_restart_time', kw_only=True, fn=None), ReprPlan.Field(name='custom_iam"
        "_instance_profile', kw_only=True, fn=None), ReprPlan.Field(name='activity_stream_policy_status', kw_only=True,"
        " fn=None), ReprPlan.Field(name='certificate_details', kw_only=True, fn=None), ReprPlan.Field(name='db_system_i"
        "d', kw_only=True, fn=None), ReprPlan.Field(name='master_user_secret', kw_only=True, fn=None), ReprPlan.Field(n"
        "ame='read_replica_source_db_cluster_identifier', kw_only=True, fn=None), ReprPlan.Field(name='percent_progress"
        "', kw_only=True, fn=None), ReprPlan.Field(name='multi_tenant', kw_only=True, fn=None), ReprPlan.Field(name='de"
        "dicated_log_volume', kw_only=True, fn=None), ReprPlan.Field(name='is_storage_config_upgrade_available', kw_onl"
        "y=True, fn=None), ReprPlan.Field(name='engine_lifecycle_support', kw_only=True, fn=None), ReprPlan.Field(name="
        "'additional_storage_volumes', kw_only=True, fn=None), ReprPlan.Field(name='storage_volume_status', kw_only=Tru"
        "e, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='06d1d03f4b9d0ffc072cef69b6538b583c4a3931',
    op_ref_idents=(
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
        '__dataclass__init__fields__18__annotation',
        '__dataclass__init__fields__18__default',
        '__dataclass__init__fields__19__annotation',
        '__dataclass__init__fields__19__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__20__annotation',
        '__dataclass__init__fields__20__default',
        '__dataclass__init__fields__21__annotation',
        '__dataclass__init__fields__21__default',
        '__dataclass__init__fields__22__annotation',
        '__dataclass__init__fields__22__default',
        '__dataclass__init__fields__23__annotation',
        '__dataclass__init__fields__23__default',
        '__dataclass__init__fields__24__annotation',
        '__dataclass__init__fields__24__default',
        '__dataclass__init__fields__25__annotation',
        '__dataclass__init__fields__25__default',
        '__dataclass__init__fields__26__annotation',
        '__dataclass__init__fields__26__default',
        '__dataclass__init__fields__27__annotation',
        '__dataclass__init__fields__27__default',
        '__dataclass__init__fields__28__annotation',
        '__dataclass__init__fields__28__default',
        '__dataclass__init__fields__29__annotation',
        '__dataclass__init__fields__29__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__30__annotation',
        '__dataclass__init__fields__30__default',
        '__dataclass__init__fields__31__annotation',
        '__dataclass__init__fields__31__default',
        '__dataclass__init__fields__32__annotation',
        '__dataclass__init__fields__32__default',
        '__dataclass__init__fields__33__annotation',
        '__dataclass__init__fields__33__default',
        '__dataclass__init__fields__34__annotation',
        '__dataclass__init__fields__34__default',
        '__dataclass__init__fields__35__annotation',
        '__dataclass__init__fields__35__default',
        '__dataclass__init__fields__36__annotation',
        '__dataclass__init__fields__36__default',
        '__dataclass__init__fields__37__annotation',
        '__dataclass__init__fields__37__default',
        '__dataclass__init__fields__38__annotation',
        '__dataclass__init__fields__38__default',
        '__dataclass__init__fields__39__annotation',
        '__dataclass__init__fields__39__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
        '__dataclass__init__fields__40__annotation',
        '__dataclass__init__fields__40__default',
        '__dataclass__init__fields__41__annotation',
        '__dataclass__init__fields__41__default',
        '__dataclass__init__fields__42__annotation',
        '__dataclass__init__fields__42__default',
        '__dataclass__init__fields__43__annotation',
        '__dataclass__init__fields__43__default',
        '__dataclass__init__fields__44__annotation',
        '__dataclass__init__fields__44__default',
        '__dataclass__init__fields__45__annotation',
        '__dataclass__init__fields__45__default',
        '__dataclass__init__fields__46__annotation',
        '__dataclass__init__fields__46__default',
        '__dataclass__init__fields__47__annotation',
        '__dataclass__init__fields__47__default',
        '__dataclass__init__fields__48__annotation',
        '__dataclass__init__fields__48__default',
        '__dataclass__init__fields__49__annotation',
        '__dataclass__init__fields__49__default',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__4__default',
        '__dataclass__init__fields__50__annotation',
        '__dataclass__init__fields__50__default',
        '__dataclass__init__fields__51__annotation',
        '__dataclass__init__fields__51__default',
        '__dataclass__init__fields__52__annotation',
        '__dataclass__init__fields__52__default',
        '__dataclass__init__fields__53__annotation',
        '__dataclass__init__fields__53__default',
        '__dataclass__init__fields__54__annotation',
        '__dataclass__init__fields__54__default',
        '__dataclass__init__fields__55__annotation',
        '__dataclass__init__fields__55__default',
        '__dataclass__init__fields__56__annotation',
        '__dataclass__init__fields__56__default',
        '__dataclass__init__fields__57__annotation',
        '__dataclass__init__fields__57__default',
        '__dataclass__init__fields__58__annotation',
        '__dataclass__init__fields__58__default',
        '__dataclass__init__fields__59__annotation',
        '__dataclass__init__fields__59__default',
        '__dataclass__init__fields__5__annotation',
        '__dataclass__init__fields__5__default',
        '__dataclass__init__fields__60__annotation',
        '__dataclass__init__fields__60__default',
        '__dataclass__init__fields__61__annotation',
        '__dataclass__init__fields__61__default',
        '__dataclass__init__fields__62__annotation',
        '__dataclass__init__fields__62__default',
        '__dataclass__init__fields__63__annotation',
        '__dataclass__init__fields__63__default',
        '__dataclass__init__fields__64__annotation',
        '__dataclass__init__fields__64__default',
        '__dataclass__init__fields__65__annotation',
        '__dataclass__init__fields__65__default',
        '__dataclass__init__fields__66__annotation',
        '__dataclass__init__fields__66__default',
        '__dataclass__init__fields__67__annotation',
        '__dataclass__init__fields__67__default',
        '__dataclass__init__fields__68__annotation',
        '__dataclass__init__fields__68__default',
        '__dataclass__init__fields__69__annotation',
        '__dataclass__init__fields__69__default',
        '__dataclass__init__fields__6__annotation',
        '__dataclass__init__fields__6__default',
        '__dataclass__init__fields__70__annotation',
        '__dataclass__init__fields__70__default',
        '__dataclass__init__fields__71__annotation',
        '__dataclass__init__fields__71__default',
        '__dataclass__init__fields__72__annotation',
        '__dataclass__init__fields__72__default',
        '__dataclass__init__fields__73__annotation',
        '__dataclass__init__fields__73__default',
        '__dataclass__init__fields__74__annotation',
        '__dataclass__init__fields__74__default',
        '__dataclass__init__fields__75__annotation',
        '__dataclass__init__fields__75__default',
        '__dataclass__init__fields__76__annotation',
        '__dataclass__init__fields__76__default',
        '__dataclass__init__fields__77__annotation',
        '__dataclass__init__fields__77__default',
        '__dataclass__init__fields__78__annotation',
        '__dataclass__init__fields__78__default',
        '__dataclass__init__fields__79__annotation',
        '__dataclass__init__fields__79__default',
        '__dataclass__init__fields__7__annotation',
        '__dataclass__init__fields__7__default',
        '__dataclass__init__fields__80__annotation',
        '__dataclass__init__fields__80__default',
        '__dataclass__init__fields__81__annotation',
        '__dataclass__init__fields__81__default',
        '__dataclass__init__fields__82__annotation',
        '__dataclass__init__fields__82__default',
        '__dataclass__init__fields__83__annotation',
        '__dataclass__init__fields__83__default',
        '__dataclass__init__fields__84__annotation',
        '__dataclass__init__fields__84__default',
        '__dataclass__init__fields__85__annotation',
        '__dataclass__init__fields__85__default',
        '__dataclass__init__fields__86__annotation',
        '__dataclass__init__fields__86__default',
        '__dataclass__init__fields__87__annotation',
        '__dataclass__init__fields__87__default',
        '__dataclass__init__fields__88__annotation',
        '__dataclass__init__fields__88__default',
        '__dataclass__init__fields__89__annotation',
        '__dataclass__init__fields__89__default',
        '__dataclass__init__fields__8__annotation',
        '__dataclass__init__fields__8__default',
        '__dataclass__init__fields__90__annotation',
        '__dataclass__init__fields__90__default',
        '__dataclass__init__fields__9__annotation',
        '__dataclass__init__fields__9__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.rds', 'DBInstance'),
    ),
)
def _process_dataclass__06d1d03f4b9d0ffc072cef69b6538b583c4a3931():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
        __dataclass__init__fields__18__annotation,
        __dataclass__init__fields__18__default,
        __dataclass__init__fields__19__annotation,
        __dataclass__init__fields__19__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__init__fields__20__annotation,
        __dataclass__init__fields__20__default,
        __dataclass__init__fields__21__annotation,
        __dataclass__init__fields__21__default,
        __dataclass__init__fields__22__annotation,
        __dataclass__init__fields__22__default,
        __dataclass__init__fields__23__annotation,
        __dataclass__init__fields__23__default,
        __dataclass__init__fields__24__annotation,
        __dataclass__init__fields__24__default,
        __dataclass__init__fields__25__annotation,
        __dataclass__init__fields__25__default,
        __dataclass__init__fields__26__annotation,
        __dataclass__init__fields__26__default,
        __dataclass__init__fields__27__annotation,
        __dataclass__init__fields__27__default,
        __dataclass__init__fields__28__annotation,
        __dataclass__init__fields__28__default,
        __dataclass__init__fields__29__annotation,
        __dataclass__init__fields__29__default,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
        __dataclass__init__fields__30__annotation,
        __dataclass__init__fields__30__default,
        __dataclass__init__fields__31__annotation,
        __dataclass__init__fields__31__default,
        __dataclass__init__fields__32__annotation,
        __dataclass__init__fields__32__default,
        __dataclass__init__fields__33__annotation,
        __dataclass__init__fields__33__default,
        __dataclass__init__fields__34__annotation,
        __dataclass__init__fields__34__default,
        __dataclass__init__fields__35__annotation,
        __dataclass__init__fields__35__default,
        __dataclass__init__fields__36__annotation,
        __dataclass__init__fields__36__default,
        __dataclass__init__fields__37__annotation,
        __dataclass__init__fields__37__default,
        __dataclass__init__fields__38__annotation,
        __dataclass__init__fields__38__default,
        __dataclass__init__fields__39__annotation,
        __dataclass__init__fields__39__default,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__3__default,
        __dataclass__init__fields__40__annotation,
        __dataclass__init__fields__40__default,
        __dataclass__init__fields__41__annotation,
        __dataclass__init__fields__41__default,
        __dataclass__init__fields__42__annotation,
        __dataclass__init__fields__42__default,
        __dataclass__init__fields__43__annotation,
        __dataclass__init__fields__43__default,
        __dataclass__init__fields__44__annotation,
        __dataclass__init__fields__44__default,
        __dataclass__init__fields__45__annotation,
        __dataclass__init__fields__45__default,
        __dataclass__init__fields__46__annotation,
        __dataclass__init__fields__46__default,
        __dataclass__init__fields__47__annotation,
        __dataclass__init__fields__47__default,
        __dataclass__init__fields__48__annotation,
        __dataclass__init__fields__48__default,
        __dataclass__init__fields__49__annotation,
        __dataclass__init__fields__49__default,
        __dataclass__init__fields__4__annotation,
        __dataclass__init__fields__4__default,
        __dataclass__init__fields__50__annotation,
        __dataclass__init__fields__50__default,
        __dataclass__init__fields__51__annotation,
        __dataclass__init__fields__51__default,
        __dataclass__init__fields__52__annotation,
        __dataclass__init__fields__52__default,
        __dataclass__init__fields__53__annotation,
        __dataclass__init__fields__53__default,
        __dataclass__init__fields__54__annotation,
        __dataclass__init__fields__54__default,
        __dataclass__init__fields__55__annotation,
        __dataclass__init__fields__55__default,
        __dataclass__init__fields__56__annotation,
        __dataclass__init__fields__56__default,
        __dataclass__init__fields__57__annotation,
        __dataclass__init__fields__57__default,
        __dataclass__init__fields__58__annotation,
        __dataclass__init__fields__58__default,
        __dataclass__init__fields__59__annotation,
        __dataclass__init__fields__59__default,
        __dataclass__init__fields__5__annotation,
        __dataclass__init__fields__5__default,
        __dataclass__init__fields__60__annotation,
        __dataclass__init__fields__60__default,
        __dataclass__init__fields__61__annotation,
        __dataclass__init__fields__61__default,
        __dataclass__init__fields__62__annotation,
        __dataclass__init__fields__62__default,
        __dataclass__init__fields__63__annotation,
        __dataclass__init__fields__63__default,
        __dataclass__init__fields__64__annotation,
        __dataclass__init__fields__64__default,
        __dataclass__init__fields__65__annotation,
        __dataclass__init__fields__65__default,
        __dataclass__init__fields__66__annotation,
        __dataclass__init__fields__66__default,
        __dataclass__init__fields__67__annotation,
        __dataclass__init__fields__67__default,
        __dataclass__init__fields__68__annotation,
        __dataclass__init__fields__68__default,
        __dataclass__init__fields__69__annotation,
        __dataclass__init__fields__69__default,
        __dataclass__init__fields__6__annotation,
        __dataclass__init__fields__6__default,
        __dataclass__init__fields__70__annotation,
        __dataclass__init__fields__70__default,
        __dataclass__init__fields__71__annotation,
        __dataclass__init__fields__71__default,
        __dataclass__init__fields__72__annotation,
        __dataclass__init__fields__72__default,
        __dataclass__init__fields__73__annotation,
        __dataclass__init__fields__73__default,
        __dataclass__init__fields__74__annotation,
        __dataclass__init__fields__74__default,
        __dataclass__init__fields__75__annotation,
        __dataclass__init__fields__75__default,
        __dataclass__init__fields__76__annotation,
        __dataclass__init__fields__76__default,
        __dataclass__init__fields__77__annotation,
        __dataclass__init__fields__77__default,
        __dataclass__init__fields__78__annotation,
        __dataclass__init__fields__78__default,
        __dataclass__init__fields__79__annotation,
        __dataclass__init__fields__79__default,
        __dataclass__init__fields__7__annotation,
        __dataclass__init__fields__7__default,
        __dataclass__init__fields__80__annotation,
        __dataclass__init__fields__80__default,
        __dataclass__init__fields__81__annotation,
        __dataclass__init__fields__81__default,
        __dataclass__init__fields__82__annotation,
        __dataclass__init__fields__82__default,
        __dataclass__init__fields__83__annotation,
        __dataclass__init__fields__83__default,
        __dataclass__init__fields__84__annotation,
        __dataclass__init__fields__84__default,
        __dataclass__init__fields__85__annotation,
        __dataclass__init__fields__85__default,
        __dataclass__init__fields__86__annotation,
        __dataclass__init__fields__86__default,
        __dataclass__init__fields__87__annotation,
        __dataclass__init__fields__87__default,
        __dataclass__init__fields__88__annotation,
        __dataclass__init__fields__88__default,
        __dataclass__init__fields__89__annotation,
        __dataclass__init__fields__89__default,
        __dataclass__init__fields__8__annotation,
        __dataclass__init__fields__8__default,
        __dataclass__init__fields__90__annotation,
        __dataclass__init__fields__90__default,
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
                db_instance_identifier=self.db_instance_identifier,
                db_instance_class=self.db_instance_class,
                engine=self.engine,
                db_instance_status=self.db_instance_status,
                master_username=self.master_username,
                db_name=self.db_name,
                endpoint=self.endpoint,
                allocated_storage=self.allocated_storage,
                instance_create_time=self.instance_create_time,
                preferred_backup_window=self.preferred_backup_window,
                backup_retention_period=self.backup_retention_period,
                db_security_groups=self.db_security_groups,
                vpc_security_groups=self.vpc_security_groups,
                db_parameter_groups=self.db_parameter_groups,
                availability_zone=self.availability_zone,
                db_subnet_group=self.db_subnet_group,
                preferred_maintenance_window=self.preferred_maintenance_window,
                upgrade_rollout_order=self.upgrade_rollout_order,
                pending_modified_values=self.pending_modified_values,
                latest_restorable_time=self.latest_restorable_time,
                multi_az=self.multi_az,
                engine_version=self.engine_version,
                auto_minor_version_upgrade=self.auto_minor_version_upgrade,
                read_replica_source_db_instance_identifier=self.read_replica_source_db_instance_identifier,
                read_replica_db_instance_identifiers=self.read_replica_db_instance_identifiers,
                read_replica_db_cluster_identifiers=self.read_replica_db_cluster_identifiers,
                replica_mode=self.replica_mode,
                license_model=self.license_model,
                iops=self.iops,
                storage_throughput=self.storage_throughput,
                option_group_memberships=self.option_group_memberships,
                character_set_name=self.character_set_name,
                nchar_character_set_name=self.nchar_character_set_name,
                secondary_availability_zone=self.secondary_availability_zone,
                publicly_accessible=self.publicly_accessible,
                status_infos=self.status_infos,
                storage_type=self.storage_type,
                tde_credential_arn=self.tde_credential_arn,
                db_instance_port=self.db_instance_port,
                db_cluster_identifier=self.db_cluster_identifier,
                storage_encrypted=self.storage_encrypted,
                kms_key_id=self.kms_key_id,
                dbi_resource_id=self.dbi_resource_id,
                ca_certificate_identifier=self.ca_certificate_identifier,
                domain_memberships=self.domain_memberships,
                copy_tags_to_snapshot=self.copy_tags_to_snapshot,
                monitoring_interval=self.monitoring_interval,
                enhanced_monitoring_resource_arn=self.enhanced_monitoring_resource_arn,
                monitoring_role_arn=self.monitoring_role_arn,
                promotion_tier=self.promotion_tier,
                db_instance_arn=self.db_instance_arn,
                timezone=self.timezone,
                iam_database_authentication_enabled=self.iam_database_authentication_enabled,
                database_insights_mode=self.database_insights_mode,
                performance_insights_enabled=self.performance_insights_enabled,
                performance_insights_kms_key_id=self.performance_insights_kms_key_id,
                performance_insights_retention_period=self.performance_insights_retention_period,
                enabled_cloudwatch_logs_exports=self.enabled_cloudwatch_logs_exports,
                processor_features=self.processor_features,
                deletion_protection=self.deletion_protection,
                associated_roles=self.associated_roles,
                listener_endpoint=self.listener_endpoint,
                max_allocated_storage=self.max_allocated_storage,
                tag_list=self.tag_list,
                automation_mode=self.automation_mode,
                resume_full_automation_mode_time=self.resume_full_automation_mode_time,
                customer_owned_ip_enabled=self.customer_owned_ip_enabled,
                network_type=self.network_type,
                activity_stream_status=self.activity_stream_status,
                activity_stream_kms_key_id=self.activity_stream_kms_key_id,
                activity_stream_kinesis_stream_name=self.activity_stream_kinesis_stream_name,
                activity_stream_mode=self.activity_stream_mode,
                activity_stream_engine_native_audit_fields_included=self.activity_stream_engine_native_audit_fields_included,
                aws_backup_recovery_point_arn=self.aws_backup_recovery_point_arn,
                db_instance_automated_backups_replications=self.db_instance_automated_backups_replications,
                backup_target=self.backup_target,
                automatic_restart_time=self.automatic_restart_time,
                custom_iam_instance_profile=self.custom_iam_instance_profile,
                activity_stream_policy_status=self.activity_stream_policy_status,
                certificate_details=self.certificate_details,
                db_system_id=self.db_system_id,
                master_user_secret=self.master_user_secret,
                read_replica_source_db_cluster_identifier=self.read_replica_source_db_cluster_identifier,
                percent_progress=self.percent_progress,
                multi_tenant=self.multi_tenant,
                dedicated_log_volume=self.dedicated_log_volume,
                is_storage_config_upgrade_available=self.is_storage_config_upgrade_available,
                engine_lifecycle_support=self.engine_lifecycle_support,
                additional_storage_volumes=self.additional_storage_volumes,
                storage_volume_status=self.storage_volume_status,
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
                self.db_instance_identifier == other.db_instance_identifier and
                self.db_instance_class == other.db_instance_class and
                self.engine == other.engine and
                self.db_instance_status == other.db_instance_status and
                self.master_username == other.master_username and
                self.db_name == other.db_name and
                self.endpoint == other.endpoint and
                self.allocated_storage == other.allocated_storage and
                self.instance_create_time == other.instance_create_time and
                self.preferred_backup_window == other.preferred_backup_window and
                self.backup_retention_period == other.backup_retention_period and
                self.db_security_groups == other.db_security_groups and
                self.vpc_security_groups == other.vpc_security_groups and
                self.db_parameter_groups == other.db_parameter_groups and
                self.availability_zone == other.availability_zone and
                self.db_subnet_group == other.db_subnet_group and
                self.preferred_maintenance_window == other.preferred_maintenance_window and
                self.upgrade_rollout_order == other.upgrade_rollout_order and
                self.pending_modified_values == other.pending_modified_values and
                self.latest_restorable_time == other.latest_restorable_time and
                self.multi_az == other.multi_az and
                self.engine_version == other.engine_version and
                self.auto_minor_version_upgrade == other.auto_minor_version_upgrade and
                self.read_replica_source_db_instance_identifier == other.read_replica_source_db_instance_identifier and
                self.read_replica_db_instance_identifiers == other.read_replica_db_instance_identifiers and
                self.read_replica_db_cluster_identifiers == other.read_replica_db_cluster_identifiers and
                self.replica_mode == other.replica_mode and
                self.license_model == other.license_model and
                self.iops == other.iops and
                self.storage_throughput == other.storage_throughput and
                self.option_group_memberships == other.option_group_memberships and
                self.character_set_name == other.character_set_name and
                self.nchar_character_set_name == other.nchar_character_set_name and
                self.secondary_availability_zone == other.secondary_availability_zone and
                self.publicly_accessible == other.publicly_accessible and
                self.status_infos == other.status_infos and
                self.storage_type == other.storage_type and
                self.tde_credential_arn == other.tde_credential_arn and
                self.db_instance_port == other.db_instance_port and
                self.db_cluster_identifier == other.db_cluster_identifier and
                self.storage_encrypted == other.storage_encrypted and
                self.kms_key_id == other.kms_key_id and
                self.dbi_resource_id == other.dbi_resource_id and
                self.ca_certificate_identifier == other.ca_certificate_identifier and
                self.domain_memberships == other.domain_memberships and
                self.copy_tags_to_snapshot == other.copy_tags_to_snapshot and
                self.monitoring_interval == other.monitoring_interval and
                self.enhanced_monitoring_resource_arn == other.enhanced_monitoring_resource_arn and
                self.monitoring_role_arn == other.monitoring_role_arn and
                self.promotion_tier == other.promotion_tier and
                self.db_instance_arn == other.db_instance_arn and
                self.timezone == other.timezone and
                self.iam_database_authentication_enabled == other.iam_database_authentication_enabled and
                self.database_insights_mode == other.database_insights_mode and
                self.performance_insights_enabled == other.performance_insights_enabled and
                self.performance_insights_kms_key_id == other.performance_insights_kms_key_id and
                self.performance_insights_retention_period == other.performance_insights_retention_period and
                self.enabled_cloudwatch_logs_exports == other.enabled_cloudwatch_logs_exports and
                self.processor_features == other.processor_features and
                self.deletion_protection == other.deletion_protection and
                self.associated_roles == other.associated_roles and
                self.listener_endpoint == other.listener_endpoint and
                self.max_allocated_storage == other.max_allocated_storage and
                self.tag_list == other.tag_list and
                self.automation_mode == other.automation_mode and
                self.resume_full_automation_mode_time == other.resume_full_automation_mode_time and
                self.customer_owned_ip_enabled == other.customer_owned_ip_enabled and
                self.network_type == other.network_type and
                self.activity_stream_status == other.activity_stream_status and
                self.activity_stream_kms_key_id == other.activity_stream_kms_key_id and
                self.activity_stream_kinesis_stream_name == other.activity_stream_kinesis_stream_name and
                self.activity_stream_mode == other.activity_stream_mode and
                self.activity_stream_engine_native_audit_fields_included == other.activity_stream_engine_native_audit_fields_included and
                self.aws_backup_recovery_point_arn == other.aws_backup_recovery_point_arn and
                self.db_instance_automated_backups_replications == other.db_instance_automated_backups_replications and
                self.backup_target == other.backup_target and
                self.automatic_restart_time == other.automatic_restart_time and
                self.custom_iam_instance_profile == other.custom_iam_instance_profile and
                self.activity_stream_policy_status == other.activity_stream_policy_status and
                self.certificate_details == other.certificate_details and
                self.db_system_id == other.db_system_id and
                self.master_user_secret == other.master_user_secret and
                self.read_replica_source_db_cluster_identifier == other.read_replica_source_db_cluster_identifier and
                self.percent_progress == other.percent_progress and
                self.multi_tenant == other.multi_tenant and
                self.dedicated_log_volume == other.dedicated_log_volume and
                self.is_storage_config_upgrade_available == other.is_storage_config_upgrade_available and
                self.engine_lifecycle_support == other.engine_lifecycle_support and
                self.additional_storage_volumes == other.additional_storage_volumes and
                self.storage_volume_status == other.storage_volume_status
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'db_instance_identifier',
            'db_instance_class',
            'engine',
            'db_instance_status',
            'master_username',
            'db_name',
            'endpoint',
            'allocated_storage',
            'instance_create_time',
            'preferred_backup_window',
            'backup_retention_period',
            'db_security_groups',
            'vpc_security_groups',
            'db_parameter_groups',
            'availability_zone',
            'db_subnet_group',
            'preferred_maintenance_window',
            'upgrade_rollout_order',
            'pending_modified_values',
            'latest_restorable_time',
            'multi_az',
            'engine_version',
            'auto_minor_version_upgrade',
            'read_replica_source_db_instance_identifier',
            'read_replica_db_instance_identifiers',
            'read_replica_db_cluster_identifiers',
            'replica_mode',
            'license_model',
            'iops',
            'storage_throughput',
            'option_group_memberships',
            'character_set_name',
            'nchar_character_set_name',
            'secondary_availability_zone',
            'publicly_accessible',
            'status_infos',
            'storage_type',
            'tde_credential_arn',
            'db_instance_port',
            'db_cluster_identifier',
            'storage_encrypted',
            'kms_key_id',
            'dbi_resource_id',
            'ca_certificate_identifier',
            'domain_memberships',
            'copy_tags_to_snapshot',
            'monitoring_interval',
            'enhanced_monitoring_resource_arn',
            'monitoring_role_arn',
            'promotion_tier',
            'db_instance_arn',
            'timezone',
            'iam_database_authentication_enabled',
            'database_insights_mode',
            'performance_insights_enabled',
            'performance_insights_kms_key_id',
            'performance_insights_retention_period',
            'enabled_cloudwatch_logs_exports',
            'processor_features',
            'deletion_protection',
            'associated_roles',
            'listener_endpoint',
            'max_allocated_storage',
            'tag_list',
            'automation_mode',
            'resume_full_automation_mode_time',
            'customer_owned_ip_enabled',
            'network_type',
            'activity_stream_status',
            'activity_stream_kms_key_id',
            'activity_stream_kinesis_stream_name',
            'activity_stream_mode',
            'activity_stream_engine_native_audit_fields_included',
            'aws_backup_recovery_point_arn',
            'db_instance_automated_backups_replications',
            'backup_target',
            'automatic_restart_time',
            'custom_iam_instance_profile',
            'activity_stream_policy_status',
            'certificate_details',
            'db_system_id',
            'master_user_secret',
            'read_replica_source_db_cluster_identifier',
            'percent_progress',
            'multi_tenant',
            'dedicated_log_volume',
            'is_storage_config_upgrade_available',
            'engine_lifecycle_support',
            'additional_storage_volumes',
            'storage_volume_status',
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
            '__shape__',
            'db_instance_identifier',
            'db_instance_class',
            'engine',
            'db_instance_status',
            'master_username',
            'db_name',
            'endpoint',
            'allocated_storage',
            'instance_create_time',
            'preferred_backup_window',
            'backup_retention_period',
            'db_security_groups',
            'vpc_security_groups',
            'db_parameter_groups',
            'availability_zone',
            'db_subnet_group',
            'preferred_maintenance_window',
            'upgrade_rollout_order',
            'pending_modified_values',
            'latest_restorable_time',
            'multi_az',
            'engine_version',
            'auto_minor_version_upgrade',
            'read_replica_source_db_instance_identifier',
            'read_replica_db_instance_identifiers',
            'read_replica_db_cluster_identifiers',
            'replica_mode',
            'license_model',
            'iops',
            'storage_throughput',
            'option_group_memberships',
            'character_set_name',
            'nchar_character_set_name',
            'secondary_availability_zone',
            'publicly_accessible',
            'status_infos',
            'storage_type',
            'tde_credential_arn',
            'db_instance_port',
            'db_cluster_identifier',
            'storage_encrypted',
            'kms_key_id',
            'dbi_resource_id',
            'ca_certificate_identifier',
            'domain_memberships',
            'copy_tags_to_snapshot',
            'monitoring_interval',
            'enhanced_monitoring_resource_arn',
            'monitoring_role_arn',
            'promotion_tier',
            'db_instance_arn',
            'timezone',
            'iam_database_authentication_enabled',
            'database_insights_mode',
            'performance_insights_enabled',
            'performance_insights_kms_key_id',
            'performance_insights_retention_period',
            'enabled_cloudwatch_logs_exports',
            'processor_features',
            'deletion_protection',
            'associated_roles',
            'listener_endpoint',
            'max_allocated_storage',
            'tag_list',
            'automation_mode',
            'resume_full_automation_mode_time',
            'customer_owned_ip_enabled',
            'network_type',
            'activity_stream_status',
            'activity_stream_kms_key_id',
            'activity_stream_kinesis_stream_name',
            'activity_stream_mode',
            'activity_stream_engine_native_audit_fields_included',
            'aws_backup_recovery_point_arn',
            'db_instance_automated_backups_replications',
            'backup_target',
            'automatic_restart_time',
            'custom_iam_instance_profile',
            'activity_stream_policy_status',
            'certificate_details',
            'db_system_id',
            'master_user_secret',
            'read_replica_source_db_cluster_identifier',
            'percent_progress',
            'multi_tenant',
            'dedicated_log_volume',
            'is_storage_config_upgrade_available',
            'engine_lifecycle_support',
            'additional_storage_volumes',
            'storage_volume_status',
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
                self.db_instance_identifier,
                self.db_instance_class,
                self.engine,
                self.db_instance_status,
                self.master_username,
                self.db_name,
                self.endpoint,
                self.allocated_storage,
                self.instance_create_time,
                self.preferred_backup_window,
                self.backup_retention_period,
                self.db_security_groups,
                self.vpc_security_groups,
                self.db_parameter_groups,
                self.availability_zone,
                self.db_subnet_group,
                self.preferred_maintenance_window,
                self.upgrade_rollout_order,
                self.pending_modified_values,
                self.latest_restorable_time,
                self.multi_az,
                self.engine_version,
                self.auto_minor_version_upgrade,
                self.read_replica_source_db_instance_identifier,
                self.read_replica_db_instance_identifiers,
                self.read_replica_db_cluster_identifiers,
                self.replica_mode,
                self.license_model,
                self.iops,
                self.storage_throughput,
                self.option_group_memberships,
                self.character_set_name,
                self.nchar_character_set_name,
                self.secondary_availability_zone,
                self.publicly_accessible,
                self.status_infos,
                self.storage_type,
                self.tde_credential_arn,
                self.db_instance_port,
                self.db_cluster_identifier,
                self.storage_encrypted,
                self.kms_key_id,
                self.dbi_resource_id,
                self.ca_certificate_identifier,
                self.domain_memberships,
                self.copy_tags_to_snapshot,
                self.monitoring_interval,
                self.enhanced_monitoring_resource_arn,
                self.monitoring_role_arn,
                self.promotion_tier,
                self.db_instance_arn,
                self.timezone,
                self.iam_database_authentication_enabled,
                self.database_insights_mode,
                self.performance_insights_enabled,
                self.performance_insights_kms_key_id,
                self.performance_insights_retention_period,
                self.enabled_cloudwatch_logs_exports,
                self.processor_features,
                self.deletion_protection,
                self.associated_roles,
                self.listener_endpoint,
                self.max_allocated_storage,
                self.tag_list,
                self.automation_mode,
                self.resume_full_automation_mode_time,
                self.customer_owned_ip_enabled,
                self.network_type,
                self.activity_stream_status,
                self.activity_stream_kms_key_id,
                self.activity_stream_kinesis_stream_name,
                self.activity_stream_mode,
                self.activity_stream_engine_native_audit_fields_included,
                self.aws_backup_recovery_point_arn,
                self.db_instance_automated_backups_replications,
                self.backup_target,
                self.automatic_restart_time,
                self.custom_iam_instance_profile,
                self.activity_stream_policy_status,
                self.certificate_details,
                self.db_system_id,
                self.master_user_secret,
                self.read_replica_source_db_cluster_identifier,
                self.percent_progress,
                self.multi_tenant,
                self.dedicated_log_volume,
                self.is_storage_config_upgrade_available,
                self.engine_lifecycle_support,
                self.additional_storage_volumes,
                self.storage_volume_status,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            db_instance_identifier: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            db_instance_class: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            engine: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            db_instance_status: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            master_username: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
            db_name: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
            endpoint: __dataclass__init__fields__7__annotation = __dataclass__init__fields__7__default,
            allocated_storage: __dataclass__init__fields__8__annotation = __dataclass__init__fields__8__default,
            instance_create_time: __dataclass__init__fields__9__annotation = __dataclass__init__fields__9__default,
            preferred_backup_window: __dataclass__init__fields__10__annotation = __dataclass__init__fields__10__default,
            backup_retention_period: __dataclass__init__fields__11__annotation = __dataclass__init__fields__11__default,
            db_security_groups: __dataclass__init__fields__12__annotation = __dataclass__init__fields__12__default,
            vpc_security_groups: __dataclass__init__fields__13__annotation = __dataclass__init__fields__13__default,
            db_parameter_groups: __dataclass__init__fields__14__annotation = __dataclass__init__fields__14__default,
            availability_zone: __dataclass__init__fields__15__annotation = __dataclass__init__fields__15__default,
            db_subnet_group: __dataclass__init__fields__16__annotation = __dataclass__init__fields__16__default,
            preferred_maintenance_window: __dataclass__init__fields__17__annotation = __dataclass__init__fields__17__default,
            upgrade_rollout_order: __dataclass__init__fields__18__annotation = __dataclass__init__fields__18__default,
            pending_modified_values: __dataclass__init__fields__19__annotation = __dataclass__init__fields__19__default,
            latest_restorable_time: __dataclass__init__fields__20__annotation = __dataclass__init__fields__20__default,
            multi_az: __dataclass__init__fields__21__annotation = __dataclass__init__fields__21__default,
            engine_version: __dataclass__init__fields__22__annotation = __dataclass__init__fields__22__default,
            auto_minor_version_upgrade: __dataclass__init__fields__23__annotation = __dataclass__init__fields__23__default,
            read_replica_source_db_instance_identifier: __dataclass__init__fields__24__annotation = __dataclass__init__fields__24__default,
            read_replica_db_instance_identifiers: __dataclass__init__fields__25__annotation = __dataclass__init__fields__25__default,
            read_replica_db_cluster_identifiers: __dataclass__init__fields__26__annotation = __dataclass__init__fields__26__default,
            replica_mode: __dataclass__init__fields__27__annotation = __dataclass__init__fields__27__default,
            license_model: __dataclass__init__fields__28__annotation = __dataclass__init__fields__28__default,
            iops: __dataclass__init__fields__29__annotation = __dataclass__init__fields__29__default,
            storage_throughput: __dataclass__init__fields__30__annotation = __dataclass__init__fields__30__default,
            option_group_memberships: __dataclass__init__fields__31__annotation = __dataclass__init__fields__31__default,
            character_set_name: __dataclass__init__fields__32__annotation = __dataclass__init__fields__32__default,
            nchar_character_set_name: __dataclass__init__fields__33__annotation = __dataclass__init__fields__33__default,
            secondary_availability_zone: __dataclass__init__fields__34__annotation = __dataclass__init__fields__34__default,
            publicly_accessible: __dataclass__init__fields__35__annotation = __dataclass__init__fields__35__default,
            status_infos: __dataclass__init__fields__36__annotation = __dataclass__init__fields__36__default,
            storage_type: __dataclass__init__fields__37__annotation = __dataclass__init__fields__37__default,
            tde_credential_arn: __dataclass__init__fields__38__annotation = __dataclass__init__fields__38__default,
            db_instance_port: __dataclass__init__fields__39__annotation = __dataclass__init__fields__39__default,
            db_cluster_identifier: __dataclass__init__fields__40__annotation = __dataclass__init__fields__40__default,
            storage_encrypted: __dataclass__init__fields__41__annotation = __dataclass__init__fields__41__default,
            kms_key_id: __dataclass__init__fields__42__annotation = __dataclass__init__fields__42__default,
            dbi_resource_id: __dataclass__init__fields__43__annotation = __dataclass__init__fields__43__default,
            ca_certificate_identifier: __dataclass__init__fields__44__annotation = __dataclass__init__fields__44__default,
            domain_memberships: __dataclass__init__fields__45__annotation = __dataclass__init__fields__45__default,
            copy_tags_to_snapshot: __dataclass__init__fields__46__annotation = __dataclass__init__fields__46__default,
            monitoring_interval: __dataclass__init__fields__47__annotation = __dataclass__init__fields__47__default,
            enhanced_monitoring_resource_arn: __dataclass__init__fields__48__annotation = __dataclass__init__fields__48__default,
            monitoring_role_arn: __dataclass__init__fields__49__annotation = __dataclass__init__fields__49__default,
            promotion_tier: __dataclass__init__fields__50__annotation = __dataclass__init__fields__50__default,
            db_instance_arn: __dataclass__init__fields__51__annotation = __dataclass__init__fields__51__default,
            timezone: __dataclass__init__fields__52__annotation = __dataclass__init__fields__52__default,
            iam_database_authentication_enabled: __dataclass__init__fields__53__annotation = __dataclass__init__fields__53__default,
            database_insights_mode: __dataclass__init__fields__54__annotation = __dataclass__init__fields__54__default,
            performance_insights_enabled: __dataclass__init__fields__55__annotation = __dataclass__init__fields__55__default,
            performance_insights_kms_key_id: __dataclass__init__fields__56__annotation = __dataclass__init__fields__56__default,
            performance_insights_retention_period: __dataclass__init__fields__57__annotation = __dataclass__init__fields__57__default,
            enabled_cloudwatch_logs_exports: __dataclass__init__fields__58__annotation = __dataclass__init__fields__58__default,
            processor_features: __dataclass__init__fields__59__annotation = __dataclass__init__fields__59__default,
            deletion_protection: __dataclass__init__fields__60__annotation = __dataclass__init__fields__60__default,
            associated_roles: __dataclass__init__fields__61__annotation = __dataclass__init__fields__61__default,
            listener_endpoint: __dataclass__init__fields__62__annotation = __dataclass__init__fields__62__default,
            max_allocated_storage: __dataclass__init__fields__63__annotation = __dataclass__init__fields__63__default,
            tag_list: __dataclass__init__fields__64__annotation = __dataclass__init__fields__64__default,
            automation_mode: __dataclass__init__fields__65__annotation = __dataclass__init__fields__65__default,
            resume_full_automation_mode_time: __dataclass__init__fields__66__annotation = __dataclass__init__fields__66__default,
            customer_owned_ip_enabled: __dataclass__init__fields__67__annotation = __dataclass__init__fields__67__default,
            network_type: __dataclass__init__fields__68__annotation = __dataclass__init__fields__68__default,
            activity_stream_status: __dataclass__init__fields__69__annotation = __dataclass__init__fields__69__default,
            activity_stream_kms_key_id: __dataclass__init__fields__70__annotation = __dataclass__init__fields__70__default,
            activity_stream_kinesis_stream_name: __dataclass__init__fields__71__annotation = __dataclass__init__fields__71__default,
            activity_stream_mode: __dataclass__init__fields__72__annotation = __dataclass__init__fields__72__default,
            activity_stream_engine_native_audit_fields_included: __dataclass__init__fields__73__annotation = __dataclass__init__fields__73__default,
            aws_backup_recovery_point_arn: __dataclass__init__fields__74__annotation = __dataclass__init__fields__74__default,
            db_instance_automated_backups_replications: __dataclass__init__fields__75__annotation = __dataclass__init__fields__75__default,
            backup_target: __dataclass__init__fields__76__annotation = __dataclass__init__fields__76__default,
            automatic_restart_time: __dataclass__init__fields__77__annotation = __dataclass__init__fields__77__default,
            custom_iam_instance_profile: __dataclass__init__fields__78__annotation = __dataclass__init__fields__78__default,
            activity_stream_policy_status: __dataclass__init__fields__79__annotation = __dataclass__init__fields__79__default,
            certificate_details: __dataclass__init__fields__80__annotation = __dataclass__init__fields__80__default,
            db_system_id: __dataclass__init__fields__81__annotation = __dataclass__init__fields__81__default,
            master_user_secret: __dataclass__init__fields__82__annotation = __dataclass__init__fields__82__default,
            read_replica_source_db_cluster_identifier: __dataclass__init__fields__83__annotation = __dataclass__init__fields__83__default,
            percent_progress: __dataclass__init__fields__84__annotation = __dataclass__init__fields__84__default,
            multi_tenant: __dataclass__init__fields__85__annotation = __dataclass__init__fields__85__default,
            dedicated_log_volume: __dataclass__init__fields__86__annotation = __dataclass__init__fields__86__default,
            is_storage_config_upgrade_available: __dataclass__init__fields__87__annotation = __dataclass__init__fields__87__default,
            engine_lifecycle_support: __dataclass__init__fields__88__annotation = __dataclass__init__fields__88__default,
            additional_storage_volumes: __dataclass__init__fields__89__annotation = __dataclass__init__fields__89__default,
            storage_volume_status: __dataclass__init__fields__90__annotation = __dataclass__init__fields__90__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'db_instance_identifier', db_instance_identifier)
            __dataclass__object_setattr(self, 'db_instance_class', db_instance_class)
            __dataclass__object_setattr(self, 'engine', engine)
            __dataclass__object_setattr(self, 'db_instance_status', db_instance_status)
            __dataclass__object_setattr(self, 'master_username', master_username)
            __dataclass__object_setattr(self, 'db_name', db_name)
            __dataclass__object_setattr(self, 'endpoint', endpoint)
            __dataclass__object_setattr(self, 'allocated_storage', allocated_storage)
            __dataclass__object_setattr(self, 'instance_create_time', instance_create_time)
            __dataclass__object_setattr(self, 'preferred_backup_window', preferred_backup_window)
            __dataclass__object_setattr(self, 'backup_retention_period', backup_retention_period)
            __dataclass__object_setattr(self, 'db_security_groups', db_security_groups)
            __dataclass__object_setattr(self, 'vpc_security_groups', vpc_security_groups)
            __dataclass__object_setattr(self, 'db_parameter_groups', db_parameter_groups)
            __dataclass__object_setattr(self, 'availability_zone', availability_zone)
            __dataclass__object_setattr(self, 'db_subnet_group', db_subnet_group)
            __dataclass__object_setattr(self, 'preferred_maintenance_window', preferred_maintenance_window)
            __dataclass__object_setattr(self, 'upgrade_rollout_order', upgrade_rollout_order)
            __dataclass__object_setattr(self, 'pending_modified_values', pending_modified_values)
            __dataclass__object_setattr(self, 'latest_restorable_time', latest_restorable_time)
            __dataclass__object_setattr(self, 'multi_az', multi_az)
            __dataclass__object_setattr(self, 'engine_version', engine_version)
            __dataclass__object_setattr(self, 'auto_minor_version_upgrade', auto_minor_version_upgrade)
            __dataclass__object_setattr(self, 'read_replica_source_db_instance_identifier', read_replica_source_db_instance_identifier)
            __dataclass__object_setattr(self, 'read_replica_db_instance_identifiers', read_replica_db_instance_identifiers)
            __dataclass__object_setattr(self, 'read_replica_db_cluster_identifiers', read_replica_db_cluster_identifiers)
            __dataclass__object_setattr(self, 'replica_mode', replica_mode)
            __dataclass__object_setattr(self, 'license_model', license_model)
            __dataclass__object_setattr(self, 'iops', iops)
            __dataclass__object_setattr(self, 'storage_throughput', storage_throughput)
            __dataclass__object_setattr(self, 'option_group_memberships', option_group_memberships)
            __dataclass__object_setattr(self, 'character_set_name', character_set_name)
            __dataclass__object_setattr(self, 'nchar_character_set_name', nchar_character_set_name)
            __dataclass__object_setattr(self, 'secondary_availability_zone', secondary_availability_zone)
            __dataclass__object_setattr(self, 'publicly_accessible', publicly_accessible)
            __dataclass__object_setattr(self, 'status_infos', status_infos)
            __dataclass__object_setattr(self, 'storage_type', storage_type)
            __dataclass__object_setattr(self, 'tde_credential_arn', tde_credential_arn)
            __dataclass__object_setattr(self, 'db_instance_port', db_instance_port)
            __dataclass__object_setattr(self, 'db_cluster_identifier', db_cluster_identifier)
            __dataclass__object_setattr(self, 'storage_encrypted', storage_encrypted)
            __dataclass__object_setattr(self, 'kms_key_id', kms_key_id)
            __dataclass__object_setattr(self, 'dbi_resource_id', dbi_resource_id)
            __dataclass__object_setattr(self, 'ca_certificate_identifier', ca_certificate_identifier)
            __dataclass__object_setattr(self, 'domain_memberships', domain_memberships)
            __dataclass__object_setattr(self, 'copy_tags_to_snapshot', copy_tags_to_snapshot)
            __dataclass__object_setattr(self, 'monitoring_interval', monitoring_interval)
            __dataclass__object_setattr(self, 'enhanced_monitoring_resource_arn', enhanced_monitoring_resource_arn)
            __dataclass__object_setattr(self, 'monitoring_role_arn', monitoring_role_arn)
            __dataclass__object_setattr(self, 'promotion_tier', promotion_tier)
            __dataclass__object_setattr(self, 'db_instance_arn', db_instance_arn)
            __dataclass__object_setattr(self, 'timezone', timezone)
            __dataclass__object_setattr(self, 'iam_database_authentication_enabled', iam_database_authentication_enabled)
            __dataclass__object_setattr(self, 'database_insights_mode', database_insights_mode)
            __dataclass__object_setattr(self, 'performance_insights_enabled', performance_insights_enabled)
            __dataclass__object_setattr(self, 'performance_insights_kms_key_id', performance_insights_kms_key_id)
            __dataclass__object_setattr(self, 'performance_insights_retention_period', performance_insights_retention_period)
            __dataclass__object_setattr(self, 'enabled_cloudwatch_logs_exports', enabled_cloudwatch_logs_exports)
            __dataclass__object_setattr(self, 'processor_features', processor_features)
            __dataclass__object_setattr(self, 'deletion_protection', deletion_protection)
            __dataclass__object_setattr(self, 'associated_roles', associated_roles)
            __dataclass__object_setattr(self, 'listener_endpoint', listener_endpoint)
            __dataclass__object_setattr(self, 'max_allocated_storage', max_allocated_storage)
            __dataclass__object_setattr(self, 'tag_list', tag_list)
            __dataclass__object_setattr(self, 'automation_mode', automation_mode)
            __dataclass__object_setattr(self, 'resume_full_automation_mode_time', resume_full_automation_mode_time)
            __dataclass__object_setattr(self, 'customer_owned_ip_enabled', customer_owned_ip_enabled)
            __dataclass__object_setattr(self, 'network_type', network_type)
            __dataclass__object_setattr(self, 'activity_stream_status', activity_stream_status)
            __dataclass__object_setattr(self, 'activity_stream_kms_key_id', activity_stream_kms_key_id)
            __dataclass__object_setattr(self, 'activity_stream_kinesis_stream_name', activity_stream_kinesis_stream_name)
            __dataclass__object_setattr(self, 'activity_stream_mode', activity_stream_mode)
            __dataclass__object_setattr(self, 'activity_stream_engine_native_audit_fields_included', activity_stream_engine_native_audit_fields_included)
            __dataclass__object_setattr(self, 'aws_backup_recovery_point_arn', aws_backup_recovery_point_arn)
            __dataclass__object_setattr(self, 'db_instance_automated_backups_replications', db_instance_automated_backups_replications)
            __dataclass__object_setattr(self, 'backup_target', backup_target)
            __dataclass__object_setattr(self, 'automatic_restart_time', automatic_restart_time)
            __dataclass__object_setattr(self, 'custom_iam_instance_profile', custom_iam_instance_profile)
            __dataclass__object_setattr(self, 'activity_stream_policy_status', activity_stream_policy_status)
            __dataclass__object_setattr(self, 'certificate_details', certificate_details)
            __dataclass__object_setattr(self, 'db_system_id', db_system_id)
            __dataclass__object_setattr(self, 'master_user_secret', master_user_secret)
            __dataclass__object_setattr(self, 'read_replica_source_db_cluster_identifier', read_replica_source_db_cluster_identifier)
            __dataclass__object_setattr(self, 'percent_progress', percent_progress)
            __dataclass__object_setattr(self, 'multi_tenant', multi_tenant)
            __dataclass__object_setattr(self, 'dedicated_log_volume', dedicated_log_volume)
            __dataclass__object_setattr(self, 'is_storage_config_upgrade_available', is_storage_config_upgrade_available)
            __dataclass__object_setattr(self, 'engine_lifecycle_support', engine_lifecycle_support)
            __dataclass__object_setattr(self, 'additional_storage_volumes', additional_storage_volumes)
            __dataclass__object_setattr(self, 'storage_volume_status', storage_volume_status)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"db_instance_identifier={self.db_instance_identifier!r}")
            parts.append(f"db_instance_class={self.db_instance_class!r}")
            parts.append(f"engine={self.engine!r}")
            parts.append(f"db_instance_status={self.db_instance_status!r}")
            parts.append(f"master_username={self.master_username!r}")
            parts.append(f"db_name={self.db_name!r}")
            parts.append(f"endpoint={self.endpoint!r}")
            parts.append(f"allocated_storage={self.allocated_storage!r}")
            parts.append(f"instance_create_time={self.instance_create_time!r}")
            parts.append(f"preferred_backup_window={self.preferred_backup_window!r}")
            parts.append(f"backup_retention_period={self.backup_retention_period!r}")
            parts.append(f"db_security_groups={self.db_security_groups!r}")
            parts.append(f"vpc_security_groups={self.vpc_security_groups!r}")
            parts.append(f"db_parameter_groups={self.db_parameter_groups!r}")
            parts.append(f"availability_zone={self.availability_zone!r}")
            parts.append(f"db_subnet_group={self.db_subnet_group!r}")
            parts.append(f"preferred_maintenance_window={self.preferred_maintenance_window!r}")
            parts.append(f"upgrade_rollout_order={self.upgrade_rollout_order!r}")
            parts.append(f"pending_modified_values={self.pending_modified_values!r}")
            parts.append(f"latest_restorable_time={self.latest_restorable_time!r}")
            parts.append(f"multi_az={self.multi_az!r}")
            parts.append(f"engine_version={self.engine_version!r}")
            parts.append(f"auto_minor_version_upgrade={self.auto_minor_version_upgrade!r}")
            parts.append(f"read_replica_source_db_instance_identifier={self.read_replica_source_db_instance_identifier!r}")
            parts.append(f"read_replica_db_instance_identifiers={self.read_replica_db_instance_identifiers!r}")
            parts.append(f"read_replica_db_cluster_identifiers={self.read_replica_db_cluster_identifiers!r}")
            parts.append(f"replica_mode={self.replica_mode!r}")
            parts.append(f"license_model={self.license_model!r}")
            parts.append(f"iops={self.iops!r}")
            parts.append(f"storage_throughput={self.storage_throughput!r}")
            parts.append(f"option_group_memberships={self.option_group_memberships!r}")
            parts.append(f"character_set_name={self.character_set_name!r}")
            parts.append(f"nchar_character_set_name={self.nchar_character_set_name!r}")
            parts.append(f"secondary_availability_zone={self.secondary_availability_zone!r}")
            parts.append(f"publicly_accessible={self.publicly_accessible!r}")
            parts.append(f"status_infos={self.status_infos!r}")
            parts.append(f"storage_type={self.storage_type!r}")
            parts.append(f"tde_credential_arn={self.tde_credential_arn!r}")
            parts.append(f"db_instance_port={self.db_instance_port!r}")
            parts.append(f"db_cluster_identifier={self.db_cluster_identifier!r}")
            parts.append(f"storage_encrypted={self.storage_encrypted!r}")
            parts.append(f"kms_key_id={self.kms_key_id!r}")
            parts.append(f"dbi_resource_id={self.dbi_resource_id!r}")
            parts.append(f"ca_certificate_identifier={self.ca_certificate_identifier!r}")
            parts.append(f"domain_memberships={self.domain_memberships!r}")
            parts.append(f"copy_tags_to_snapshot={self.copy_tags_to_snapshot!r}")
            parts.append(f"monitoring_interval={self.monitoring_interval!r}")
            parts.append(f"enhanced_monitoring_resource_arn={self.enhanced_monitoring_resource_arn!r}")
            parts.append(f"monitoring_role_arn={self.monitoring_role_arn!r}")
            parts.append(f"promotion_tier={self.promotion_tier!r}")
            parts.append(f"db_instance_arn={self.db_instance_arn!r}")
            parts.append(f"timezone={self.timezone!r}")
            parts.append(f"iam_database_authentication_enabled={self.iam_database_authentication_enabled!r}")
            parts.append(f"database_insights_mode={self.database_insights_mode!r}")
            parts.append(f"performance_insights_enabled={self.performance_insights_enabled!r}")
            parts.append(f"performance_insights_kms_key_id={self.performance_insights_kms_key_id!r}")
            parts.append(f"performance_insights_retention_period={self.performance_insights_retention_period!r}")
            parts.append(f"enabled_cloudwatch_logs_exports={self.enabled_cloudwatch_logs_exports!r}")
            parts.append(f"processor_features={self.processor_features!r}")
            parts.append(f"deletion_protection={self.deletion_protection!r}")
            parts.append(f"associated_roles={self.associated_roles!r}")
            parts.append(f"listener_endpoint={self.listener_endpoint!r}")
            parts.append(f"max_allocated_storage={self.max_allocated_storage!r}")
            parts.append(f"tag_list={self.tag_list!r}")
            parts.append(f"automation_mode={self.automation_mode!r}")
            parts.append(f"resume_full_automation_mode_time={self.resume_full_automation_mode_time!r}")
            parts.append(f"customer_owned_ip_enabled={self.customer_owned_ip_enabled!r}")
            parts.append(f"network_type={self.network_type!r}")
            parts.append(f"activity_stream_status={self.activity_stream_status!r}")
            parts.append(f"activity_stream_kms_key_id={self.activity_stream_kms_key_id!r}")
            parts.append(f"activity_stream_kinesis_stream_name={self.activity_stream_kinesis_stream_name!r}")
            parts.append(f"activity_stream_mode={self.activity_stream_mode!r}")
            parts.append(f"activity_stream_engine_native_audit_fields_included={self.activity_stream_engine_native_audit_fields_included!r}")
            parts.append(f"aws_backup_recovery_point_arn={self.aws_backup_recovery_point_arn!r}")
            parts.append(f"db_instance_automated_backups_replications={self.db_instance_automated_backups_replications!r}")
            parts.append(f"backup_target={self.backup_target!r}")
            parts.append(f"automatic_restart_time={self.automatic_restart_time!r}")
            parts.append(f"custom_iam_instance_profile={self.custom_iam_instance_profile!r}")
            parts.append(f"activity_stream_policy_status={self.activity_stream_policy_status!r}")
            parts.append(f"certificate_details={self.certificate_details!r}")
            parts.append(f"db_system_id={self.db_system_id!r}")
            parts.append(f"master_user_secret={self.master_user_secret!r}")
            parts.append(f"read_replica_source_db_cluster_identifier={self.read_replica_source_db_cluster_identifier!r}")
            parts.append(f"percent_progress={self.percent_progress!r}")
            parts.append(f"multi_tenant={self.multi_tenant!r}")
            parts.append(f"dedicated_log_volume={self.dedicated_log_volume!r}")
            parts.append(f"is_storage_config_upgrade_available={self.is_storage_config_upgrade_available!r}")
            parts.append(f"engine_lifecycle_support={self.engine_lifecycle_support!r}")
            parts.append(f"additional_storage_volumes={self.additional_storage_volumes!r}")
            parts.append(f"storage_volume_status={self.storage_volume_status!r}")
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
        "Plans(tup=(CopyPlan(fields=('db_instance_automated_backups_arn',)), EqPlan(fields=('db_instance_automated_back"
        "ups_arn',)), FrozenPlan(fields=('__shape__', 'db_instance_automated_backups_arn'), allow_dynamic_dunder_attrs="
        "False), HashPlan(action='add', fields=('db_instance_automated_backups_arn',), cache=False), InitPlan(fields=(I"
        "nitPlan.Field(name='__shape__', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_facto"
        "ry=None, init=True, override=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=Non"
        "e), InitPlan.Field(name='db_instance_automated_backups_arn', annotation=OpRef(name='init.fields.1.annotation')"
        ", default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=Fie"
        "ldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_para"
        "ms=('db_instance_automated_backups_arn',), frozen=True, slots=False, post_init_params=None, init_fns=(), valid"
        "ate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='db_instance_automated_backups_arn', kw_only=True, fn=None),"
        "), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='f4f5e47cd22723462922683cb4fe9515739a3485',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.rds', 'DBInstanceAutomatedBackupsReplication'),
    ),
)
def _process_dataclass__f4f5e47cd22723462922683cb4fe9515739a3485():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
                db_instance_automated_backups_arn=self.db_instance_automated_backups_arn,
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
                self.db_instance_automated_backups_arn == other.db_instance_automated_backups_arn
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'db_instance_automated_backups_arn',
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
            '__shape__',
            'db_instance_automated_backups_arn',
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
                self.db_instance_automated_backups_arn,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            db_instance_automated_backups_arn: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'db_instance_automated_backups_arn', db_instance_automated_backups_arn)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"db_instance_automated_backups_arn={self.db_instance_automated_backups_arn!r}")
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
        "Plans(tup=(CopyPlan(fields=('marker', 'db_instances')), EqPlan(fields=('marker', 'db_instances')), FrozenPlan("
        "fields=('__shape__', 'marker', 'db_instances'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fiel"
        "ds=('marker', 'db_instances'), cache=False), InitPlan(fields=(InitPlan.Field(name='__shape__', annotation=OpRe"
        "f(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type="
        "FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='marker', annotation=Op"
        "Ref(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init="
        "True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fi"
        "eld(name='db_instances', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2."
        "default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valida"
        "te=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('marker', 'db_instances'), froze"
        "n=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(nam"
        "e='marker', kw_only=True, fn=None), ReprPlan.Field(name='db_instances', kw_only=True, fn=None)), id=False, ter"
        "se=False, default_fn=None)))"
    ),
    plan_repr_sha1='73f8c682b7489fa5d592e53237f171acb7a40089',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.rds', 'DBInstanceMessage'),
    ),
)
def _process_dataclass__73f8c682b7489fa5d592e53237f171acb7a40089():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
                marker=self.marker,
                db_instances=self.db_instances,
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
                self.marker == other.marker and
                self.db_instances == other.db_instances
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'marker',
            'db_instances',
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
            '__shape__',
            'marker',
            'db_instances',
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
                self.marker,
                self.db_instances,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            marker: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            db_instances: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'marker', marker)
            __dataclass__object_setattr(self, 'db_instances', db_instances)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"marker={self.marker!r}")
            parts.append(f"db_instances={self.db_instances!r}")
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
        "Plans(tup=(CopyPlan(fields=('role_arn', 'feature_name', 'status')), EqPlan(fields=('role_arn', 'feature_name',"
        " 'status')), FrozenPlan(fields=('__shape__', 'role_arn', 'feature_name', 'status'), allow_dynamic_dunder_attrs"
        "=False), HashPlan(action='add', fields=('role_arn', 'feature_name', 'status'), cache=False), InitPlan(fields=("
        "InitPlan.Field(name='__shape__', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_fact"
        "ory=None, init=True, override=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=No"
        "ne), InitPlan.Field(name='role_arn', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='in"
        "it.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce="
        "None, validate=None, check_type=None), InitPlan.Field(name='feature_name', annotation=OpRef(name='init.fields."
        "2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, "
        "field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='status', ann"
        "otation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=N"
        "one, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), "
        "self_param='self', std_params=(), kw_only_params=('role_arn', 'feature_name', 'status'), frozen=True, slots=Fa"
        "lse, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='role_arn', kw"
        "_only=True, fn=None), ReprPlan.Field(name='feature_name', kw_only=True, fn=None), ReprPlan.Field(name='status'"
        ", kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='b3fadeb3592e8dc008bb27dac3148f342ce359b3',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.rds', 'DBInstanceRole'),
    ),
)
def _process_dataclass__b3fadeb3592e8dc008bb27dac3148f342ce359b3():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
                role_arn=self.role_arn,
                feature_name=self.feature_name,
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
                self.role_arn == other.role_arn and
                self.feature_name == other.feature_name and
                self.status == other.status
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'role_arn',
            'feature_name',
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
            '__shape__',
            'role_arn',
            'feature_name',
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
                self.role_arn,
                self.feature_name,
                self.status,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            role_arn: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            feature_name: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            status: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'role_arn', role_arn)
            __dataclass__object_setattr(self, 'feature_name', feature_name)
            __dataclass__object_setattr(self, 'status', status)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"role_arn={self.role_arn!r}")
            parts.append(f"feature_name={self.feature_name!r}")
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
        "Plans(tup=(CopyPlan(fields=('status_type', 'normal', 'status', 'message')), EqPlan(fields=('status_type', 'nor"
        "mal', 'status', 'message')), FrozenPlan(fields=('__shape__', 'status_type', 'normal', 'status', 'message'), al"
        "low_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('status_type', 'normal', 'status', 'message'),"
        " cache=False), InitPlan(fields=(InitPlan.Field(name='__shape__', annotation=OpRef(name='init.fields.0.annotati"
        "on'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS_VAR, coerce=No"
        "ne, validate=None, check_type=None), InitPlan.Field(name='status_type', annotation=OpRef(name='init.fields.1.a"
        "nnotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, fie"
        "ld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='normal', annota"
        "tion=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None"
        ", init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), Init"
        "Plan.Field(name='status', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3"
        ".default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valid"
        "ate=None, check_type=None), InitPlan.Field(name='message', annotation=OpRef(name='init.fields.4.annotation'), "
        "default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, override=False, field_type=Field"
        "Type.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params"
        "=('status_type', 'normal', 'status', 'message'), frozen=True, slots=False, post_init_params=None, init_fns=(),"
        " validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='status_type', kw_only=True, fn=None), ReprPlan.Field("
        "name='normal', kw_only=True, fn=None), ReprPlan.Field(name='status', kw_only=True, fn=None), ReprPlan.Field(na"
        "me='message', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='dfef3bd76104061b462b6d622ccea966239e7922',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__4__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.rds', 'DBInstanceStatusInfo'),
    ),
)
def _process_dataclass__dfef3bd76104061b462b6d622ccea966239e7922():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__3__default,
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
                status_type=self.status_type,
                normal=self.normal,
                status=self.status,
                message=self.message,
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
                self.status_type == other.status_type and
                self.normal == other.normal and
                self.status == other.status and
                self.message == other.message
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'status_type',
            'normal',
            'status',
            'message',
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
            '__shape__',
            'status_type',
            'normal',
            'status',
            'message',
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
                self.status_type,
                self.normal,
                self.status,
                self.message,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            status_type: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            normal: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            status: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            message: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'status_type', status_type)
            __dataclass__object_setattr(self, 'normal', normal)
            __dataclass__object_setattr(self, 'status', status)
            __dataclass__object_setattr(self, 'message', message)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"status_type={self.status_type!r}")
            parts.append(f"normal={self.normal!r}")
            parts.append(f"status={self.status!r}")
            parts.append(f"message={self.message!r}")
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
        "Plans(tup=(CopyPlan(fields=('db_parameter_group_name', 'parameter_apply_status')), EqPlan(fields=('db_paramete"
        "r_group_name', 'parameter_apply_status')), FrozenPlan(fields=('__shape__', 'db_parameter_group_name', 'paramet"
        "er_apply_status'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('db_parameter_group_name'"
        ", 'parameter_apply_status'), cache=False), InitPlan(fields=(InitPlan.Field(name='__shape__', annotation=OpRef("
        "name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=Fi"
        "eldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='db_parameter_group_name'"
        ", annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_fact"
        "ory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=Non"
        "e), InitPlan.Field(name='parameter_apply_status', annotation=OpRef(name='init.fields.2.annotation'), default=O"
        "pRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INST"
        "ANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('db_par"
        "ameter_group_name', 'parameter_apply_status'), frozen=True, slots=False, post_init_params=None, init_fns=(), v"
        "alidate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='db_parameter_group_name', kw_only=True, fn=None), ReprP"
        "lan.Field(name='parameter_apply_status', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='a51c3ef9cca312b56d9868235ef7bc299c4a9d57',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.rds', 'DBParameterGroupStatus'),
    ),
)
def _process_dataclass__a51c3ef9cca312b56d9868235ef7bc299c4a9d57():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
                db_parameter_group_name=self.db_parameter_group_name,
                parameter_apply_status=self.parameter_apply_status,
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
                self.db_parameter_group_name == other.db_parameter_group_name and
                self.parameter_apply_status == other.parameter_apply_status
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'db_parameter_group_name',
            'parameter_apply_status',
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
            '__shape__',
            'db_parameter_group_name',
            'parameter_apply_status',
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
                self.db_parameter_group_name,
                self.parameter_apply_status,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            db_parameter_group_name: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            parameter_apply_status: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'db_parameter_group_name', db_parameter_group_name)
            __dataclass__object_setattr(self, 'parameter_apply_status', parameter_apply_status)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"db_parameter_group_name={self.db_parameter_group_name!r}")
            parts.append(f"parameter_apply_status={self.parameter_apply_status!r}")
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
        "Plans(tup=(CopyPlan(fields=('db_security_group_name', 'status')), EqPlan(fields=('db_security_group_name', 'st"
        "atus')), FrozenPlan(fields=('__shape__', 'db_security_group_name', 'status'), allow_dynamic_dunder_attrs=False"
        "), HashPlan(action='add', fields=('db_security_group_name', 'status'), cache=False), InitPlan(fields=(InitPlan"
        ".Field(name='__shape__', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None"
        ", init=True, override=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), Ini"
        "tPlan.Field(name='db_security_group_name', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(na"
        "me='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, c"
        "oerce=None, validate=None, check_type=None), InitPlan.Field(name='status', annotation=OpRef(name='init.fields."
        "2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, "
        "field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=()"
        ", kw_only_params=('db_security_group_name', 'status'), frozen=True, slots=False, post_init_params=None, init_f"
        "ns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='db_security_group_name', kw_only=True, fn=None)"
        ", ReprPlan.Field(name='status', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='5b874daf1f977f07597ba17556eee1fdb7257557',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.rds', 'DBSecurityGroupMembership'),
    ),
)
def _process_dataclass__5b874daf1f977f07597ba17556eee1fdb7257557():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
                db_security_group_name=self.db_security_group_name,
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
                self.db_security_group_name == other.db_security_group_name and
                self.status == other.status
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'db_security_group_name',
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
            '__shape__',
            'db_security_group_name',
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
                self.db_security_group_name,
                self.status,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            db_security_group_name: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            status: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'db_security_group_name', db_security_group_name)
            __dataclass__object_setattr(self, 'status', status)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"db_security_group_name={self.db_security_group_name!r}")
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
        "Plans(tup=(CopyPlan(fields=('db_subnet_group_name', 'db_subnet_group_description', 'vpc_id', 'subnet_group_sta"
        "tus', 'subnets', 'db_subnet_group_arn', 'supported_network_types')), EqPlan(fields=('db_subnet_group_name', 'd"
        "b_subnet_group_description', 'vpc_id', 'subnet_group_status', 'subnets', 'db_subnet_group_arn', 'supported_net"
        "work_types')), FrozenPlan(fields=('__shape__', 'db_subnet_group_name', 'db_subnet_group_description', 'vpc_id'"
        ", 'subnet_group_status', 'subnets', 'db_subnet_group_arn', 'supported_network_types'), allow_dynamic_dunder_at"
        "trs=False), HashPlan(action='add', fields=('db_subnet_group_name', 'db_subnet_group_description', 'vpc_id', 's"
        "ubnet_group_status', 'subnets', 'db_subnet_group_arn', 'supported_network_types'), cache=False), InitPlan(fiel"
        "ds=(InitPlan.Field(name='__shape__', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_"
        "factory=None, init=True, override=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_typ"
        "e=None), InitPlan.Field(name='db_subnet_group_name', annotation=OpRef(name='init.fields.1.annotation'), defaul"
        "t=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.I"
        "NSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='db_subnet_group_description', anno"
        "tation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=No"
        "ne, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), In"
        "itPlan.Field(name='vpc_id', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields"
        ".3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, val"
        "idate=None, check_type=None), InitPlan.Field(name='subnet_group_status', annotation=OpRef(name='init.fields.4."
        "annotation'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, override=False, fi"
        "eld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='subnets', anno"
        "tation=OpRef(name='init.fields.5.annotation'), default=OpRef(name='init.fields.5.default'), default_factory=No"
        "ne, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), In"
        "itPlan.Field(name='db_subnet_group_arn', annotation=OpRef(name='init.fields.6.annotation'), default=OpRef(name"
        "='init.fields.6.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coe"
        "rce=None, validate=None, check_type=None), InitPlan.Field(name='supported_network_types', annotation=OpRef(nam"
        "e='init.fields.7.annotation'), default=OpRef(name='init.fields.7.default'), default_factory=None, init=True, o"
        "verride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self'"
        ", std_params=(), kw_only_params=('db_subnet_group_name', 'db_subnet_group_description', 'vpc_id', 'subnet_grou"
        "p_status', 'subnets', 'db_subnet_group_arn', 'supported_network_types'), frozen=True, slots=False, post_init_p"
        "arams=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='db_subnet_group_name', kw_onl"
        "y=True, fn=None), ReprPlan.Field(name='db_subnet_group_description', kw_only=True, fn=None), ReprPlan.Field(na"
        "me='vpc_id', kw_only=True, fn=None), ReprPlan.Field(name='subnet_group_status', kw_only=True, fn=None), ReprPl"
        "an.Field(name='subnets', kw_only=True, fn=None), ReprPlan.Field(name='db_subnet_group_arn', kw_only=True, fn=N"
        "one), ReprPlan.Field(name='supported_network_types', kw_only=True, fn=None)), id=False, terse=False, default_f"
        "n=None)))"
    ),
    plan_repr_sha1='ce03050de49b8021c089e9bac61e7cf378cb13ea',
    op_ref_idents=(
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
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.rds', 'DBSubnetGroup'),
    ),
)
def _process_dataclass__ce03050de49b8021c089e9bac61e7cf378cb13ea():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
                db_subnet_group_name=self.db_subnet_group_name,
                db_subnet_group_description=self.db_subnet_group_description,
                vpc_id=self.vpc_id,
                subnet_group_status=self.subnet_group_status,
                subnets=self.subnets,
                db_subnet_group_arn=self.db_subnet_group_arn,
                supported_network_types=self.supported_network_types,
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
                self.db_subnet_group_name == other.db_subnet_group_name and
                self.db_subnet_group_description == other.db_subnet_group_description and
                self.vpc_id == other.vpc_id and
                self.subnet_group_status == other.subnet_group_status and
                self.subnets == other.subnets and
                self.db_subnet_group_arn == other.db_subnet_group_arn and
                self.supported_network_types == other.supported_network_types
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'db_subnet_group_name',
            'db_subnet_group_description',
            'vpc_id',
            'subnet_group_status',
            'subnets',
            'db_subnet_group_arn',
            'supported_network_types',
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
            '__shape__',
            'db_subnet_group_name',
            'db_subnet_group_description',
            'vpc_id',
            'subnet_group_status',
            'subnets',
            'db_subnet_group_arn',
            'supported_network_types',
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
                self.db_subnet_group_name,
                self.db_subnet_group_description,
                self.vpc_id,
                self.subnet_group_status,
                self.subnets,
                self.db_subnet_group_arn,
                self.supported_network_types,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            db_subnet_group_name: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            db_subnet_group_description: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            vpc_id: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            subnet_group_status: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            subnets: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
            db_subnet_group_arn: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
            supported_network_types: __dataclass__init__fields__7__annotation = __dataclass__init__fields__7__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'db_subnet_group_name', db_subnet_group_name)
            __dataclass__object_setattr(self, 'db_subnet_group_description', db_subnet_group_description)
            __dataclass__object_setattr(self, 'vpc_id', vpc_id)
            __dataclass__object_setattr(self, 'subnet_group_status', subnet_group_status)
            __dataclass__object_setattr(self, 'subnets', subnets)
            __dataclass__object_setattr(self, 'db_subnet_group_arn', db_subnet_group_arn)
            __dataclass__object_setattr(self, 'supported_network_types', supported_network_types)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"db_subnet_group_name={self.db_subnet_group_name!r}")
            parts.append(f"db_subnet_group_description={self.db_subnet_group_description!r}")
            parts.append(f"vpc_id={self.vpc_id!r}")
            parts.append(f"subnet_group_status={self.subnet_group_status!r}")
            parts.append(f"subnets={self.subnets!r}")
            parts.append(f"db_subnet_group_arn={self.db_subnet_group_arn!r}")
            parts.append(f"supported_network_types={self.supported_network_types!r}")
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
        "Plans(tup=(CopyPlan(fields=('db_instance_identifier', 'skip_final_snapshot', 'final_db_snapshot_identifier', '"
        "delete_automated_backups')), EqPlan(fields=('db_instance_identifier', 'skip_final_snapshot', 'final_db_snapsho"
        "t_identifier', 'delete_automated_backups')), FrozenPlan(fields=('__shape__', 'db_instance_identifier', 'skip_f"
        "inal_snapshot', 'final_db_snapshot_identifier', 'delete_automated_backups'), allow_dynamic_dunder_attrs=False)"
        ", HashPlan(action='add', fields=('db_instance_identifier', 'skip_final_snapshot', 'final_db_snapshot_identifie"
        "r', 'delete_automated_backups'), cache=False), InitPlan(fields=(InitPlan.Field(name='__shape__', annotation=Op"
        "Ref(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_typ"
        "e=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='db_instance_identifi"
        "er', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, overrid"
        "e=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='ski"
        "p_final_snapshot', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.defaul"
        "t'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=Non"
        "e, check_type=None), InitPlan.Field(name='final_db_snapshot_identifier', annotation=OpRef(name='init.fields.3."
        "annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, fi"
        "eld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='delete_automat"
        "ed_backups', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), d"
        "efault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, che"
        "ck_type=None)), self_param='self', std_params=(), kw_only_params=('db_instance_identifier', 'skip_final_snapsh"
        "ot', 'final_db_snapshot_identifier', 'delete_automated_backups'), frozen=True, slots=False, post_init_params=N"
        "one, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='db_instance_identifier', kw_only=Tru"
        "e, fn=None), ReprPlan.Field(name='skip_final_snapshot', kw_only=True, fn=None), ReprPlan.Field(name='final_db_"
        "snapshot_identifier', kw_only=True, fn=None), ReprPlan.Field(name='delete_automated_backups', kw_only=True, fn"
        "=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='d2a0a84e41592cea9c8d2689d8b23123fbb2dca2',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__4__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.rds', 'DeleteDBInstanceMessage'),
    ),
)
def _process_dataclass__d2a0a84e41592cea9c8d2689d8b23123fbb2dca2():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__3__default,
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
                db_instance_identifier=self.db_instance_identifier,
                skip_final_snapshot=self.skip_final_snapshot,
                final_db_snapshot_identifier=self.final_db_snapshot_identifier,
                delete_automated_backups=self.delete_automated_backups,
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
                self.db_instance_identifier == other.db_instance_identifier and
                self.skip_final_snapshot == other.skip_final_snapshot and
                self.final_db_snapshot_identifier == other.final_db_snapshot_identifier and
                self.delete_automated_backups == other.delete_automated_backups
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'db_instance_identifier',
            'skip_final_snapshot',
            'final_db_snapshot_identifier',
            'delete_automated_backups',
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
            '__shape__',
            'db_instance_identifier',
            'skip_final_snapshot',
            'final_db_snapshot_identifier',
            'delete_automated_backups',
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
                self.db_instance_identifier,
                self.skip_final_snapshot,
                self.final_db_snapshot_identifier,
                self.delete_automated_backups,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            db_instance_identifier: __dataclass__init__fields__1__annotation,
            skip_final_snapshot: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            final_db_snapshot_identifier: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            delete_automated_backups: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'db_instance_identifier', db_instance_identifier)
            __dataclass__object_setattr(self, 'skip_final_snapshot', skip_final_snapshot)
            __dataclass__object_setattr(self, 'final_db_snapshot_identifier', final_db_snapshot_identifier)
            __dataclass__object_setattr(self, 'delete_automated_backups', delete_automated_backups)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"db_instance_identifier={self.db_instance_identifier!r}")
            parts.append(f"skip_final_snapshot={self.skip_final_snapshot!r}")
            parts.append(f"final_db_snapshot_identifier={self.final_db_snapshot_identifier!r}")
            parts.append(f"delete_automated_backups={self.delete_automated_backups!r}")
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
        "Plans(tup=(CopyPlan(fields=('db_instance_identifier', 'filters', 'max_records', 'marker')), EqPlan(fields=('db"
        "_instance_identifier', 'filters', 'max_records', 'marker')), FrozenPlan(fields=('__shape__', 'db_instance_iden"
        "tifier', 'filters', 'max_records', 'marker'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields"
        "=('db_instance_identifier', 'filters', 'max_records', 'marker'), cache=False), InitPlan(fields=(InitPlan.Field"
        "(name='__shape__', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init"
        "=True, override=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan."
        "Field(name='db_instance_identifier', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='in"
        "it.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce="
        "None, validate=None, check_type=None), InitPlan.Field(name='filters', annotation=OpRef(name='init.fields.2.ann"
        "otation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field"
        "_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='max_records', ann"
        "otation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=N"
        "one, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), I"
        "nitPlan.Field(name='marker', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.field"
        "s.4.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, va"
        "lidate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('db_instance_identifier', 'f"
        "ilters', 'max_records', 'marker'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns="
        "()), ReprPlan(fields=(ReprPlan.Field(name='db_instance_identifier', kw_only=True, fn=None), ReprPlan.Field(nam"
        "e='filters', kw_only=True, fn=None), ReprPlan.Field(name='max_records', kw_only=True, fn=None), ReprPlan.Field"
        "(name='marker', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='ffdd6c338f4a6eedeec3d6928b24e8591a471f20',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__4__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.rds', 'DescribeDBInstancesMessage'),
    ),
)
def _process_dataclass__ffdd6c338f4a6eedeec3d6928b24e8591a471f20():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__3__default,
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
                db_instance_identifier=self.db_instance_identifier,
                filters=self.filters,
                max_records=self.max_records,
                marker=self.marker,
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
                self.db_instance_identifier == other.db_instance_identifier and
                self.filters == other.filters and
                self.max_records == other.max_records and
                self.marker == other.marker
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'db_instance_identifier',
            'filters',
            'max_records',
            'marker',
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
            '__shape__',
            'db_instance_identifier',
            'filters',
            'max_records',
            'marker',
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
                self.db_instance_identifier,
                self.filters,
                self.max_records,
                self.marker,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            db_instance_identifier: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            filters: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            max_records: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            marker: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'db_instance_identifier', db_instance_identifier)
            __dataclass__object_setattr(self, 'filters', filters)
            __dataclass__object_setattr(self, 'max_records', max_records)
            __dataclass__object_setattr(self, 'marker', marker)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"db_instance_identifier={self.db_instance_identifier!r}")
            parts.append(f"filters={self.filters!r}")
            parts.append(f"max_records={self.max_records!r}")
            parts.append(f"marker={self.marker!r}")
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
        "Plans(tup=(CopyPlan(fields=('domain', 'status', 'fqdn', 'iam_role_name', 'ou', 'auth_secret_arn', 'dns_ips')),"
        " EqPlan(fields=('domain', 'status', 'fqdn', 'iam_role_name', 'ou', 'auth_secret_arn', 'dns_ips')), FrozenPlan("
        "fields=('__shape__', 'domain', 'status', 'fqdn', 'iam_role_name', 'ou', 'auth_secret_arn', 'dns_ips'), allow_d"
        "ynamic_dunder_attrs=False), HashPlan(action='add', fields=('domain', 'status', 'fqdn', 'iam_role_name', 'ou', "
        "'auth_secret_arn', 'dns_ips'), cache=False), InitPlan(fields=(InitPlan.Field(name='__shape__', annotation=OpRe"
        "f(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type="
        "FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='domain', annotation=Op"
        "Ref(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init="
        "True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fi"
        "eld(name='status', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.defaul"
        "t'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=Non"
        "e, check_type=None), InitPlan.Field(name='fqdn', annotation=OpRef(name='init.fields.3.annotation'), default=Op"
        "Ref(name='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTA"
        "NCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='iam_role_name', annotation=OpRef(name="
        "'init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, ove"
        "rride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name="
        "'ou', annotation=OpRef(name='init.fields.5.annotation'), default=OpRef(name='init.fields.5.default'), default_"
        "factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type"
        "=None), InitPlan.Field(name='auth_secret_arn', annotation=OpRef(name='init.fields.6.annotation'), default=OpRe"
        "f(name='init.fields.6.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANC"
        "E, coerce=None, validate=None, check_type=None), InitPlan.Field(name='dns_ips', annotation=OpRef(name='init.fi"
        "elds.7.annotation'), default=OpRef(name='init.fields.7.default'), default_factory=None, init=True, override=Fa"
        "lse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_para"
        "ms=(), kw_only_params=('domain', 'status', 'fqdn', 'iam_role_name', 'ou', 'auth_secret_arn', 'dns_ips'), froze"
        "n=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(nam"
        "e='domain', kw_only=True, fn=None), ReprPlan.Field(name='status', kw_only=True, fn=None), ReprPlan.Field(name="
        "'fqdn', kw_only=True, fn=None), ReprPlan.Field(name='iam_role_name', kw_only=True, fn=None), ReprPlan.Field(na"
        "me='ou', kw_only=True, fn=None), ReprPlan.Field(name='auth_secret_arn', kw_only=True, fn=None), ReprPlan.Field"
        "(name='dns_ips', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='54b1a8431e5cb54950012516c8c38115234b7eb1',
    op_ref_idents=(
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
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.rds', 'DomainMembership'),
    ),
)
def _process_dataclass__54b1a8431e5cb54950012516c8c38115234b7eb1():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
                domain=self.domain,
                status=self.status,
                fqdn=self.fqdn,
                iam_role_name=self.iam_role_name,
                ou=self.ou,
                auth_secret_arn=self.auth_secret_arn,
                dns_ips=self.dns_ips,
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
                self.domain == other.domain and
                self.status == other.status and
                self.fqdn == other.fqdn and
                self.iam_role_name == other.iam_role_name and
                self.ou == other.ou and
                self.auth_secret_arn == other.auth_secret_arn and
                self.dns_ips == other.dns_ips
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'domain',
            'status',
            'fqdn',
            'iam_role_name',
            'ou',
            'auth_secret_arn',
            'dns_ips',
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
            '__shape__',
            'domain',
            'status',
            'fqdn',
            'iam_role_name',
            'ou',
            'auth_secret_arn',
            'dns_ips',
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
                self.domain,
                self.status,
                self.fqdn,
                self.iam_role_name,
                self.ou,
                self.auth_secret_arn,
                self.dns_ips,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            domain: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            status: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            fqdn: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            iam_role_name: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            ou: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
            auth_secret_arn: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
            dns_ips: __dataclass__init__fields__7__annotation = __dataclass__init__fields__7__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'domain', domain)
            __dataclass__object_setattr(self, 'status', status)
            __dataclass__object_setattr(self, 'fqdn', fqdn)
            __dataclass__object_setattr(self, 'iam_role_name', iam_role_name)
            __dataclass__object_setattr(self, 'ou', ou)
            __dataclass__object_setattr(self, 'auth_secret_arn', auth_secret_arn)
            __dataclass__object_setattr(self, 'dns_ips', dns_ips)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"domain={self.domain!r}")
            parts.append(f"status={self.status!r}")
            parts.append(f"fqdn={self.fqdn!r}")
            parts.append(f"iam_role_name={self.iam_role_name!r}")
            parts.append(f"ou={self.ou!r}")
            parts.append(f"auth_secret_arn={self.auth_secret_arn!r}")
            parts.append(f"dns_ips={self.dns_ips!r}")
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
        "Plans(tup=(CopyPlan(fields=('address', 'port', 'hosted_zone_id')), EqPlan(fields=('address', 'port', 'hosted_z"
        "one_id')), FrozenPlan(fields=('__shape__', 'address', 'port', 'hosted_zone_id'), allow_dynamic_dunder_attrs=Fa"
        "lse), HashPlan(action='add', fields=('address', 'port', 'hosted_zone_id'), cache=False), InitPlan(fields=(Init"
        "Plan.Field(name='__shape__', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory="
        "None, init=True, override=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None),"
        " InitPlan.Field(name='address', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fi"
        "elds.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None,"
        " validate=None, check_type=None), InitPlan.Field(name='port', annotation=OpRef(name='init.fields.2.annotation'"
        "), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=Fi"
        "eldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='hosted_zone_id', annotati"
        "on=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, "
        "init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_"
        "param='self', std_params=(), kw_only_params=('address', 'port', 'hosted_zone_id'), frozen=True, slots=False, p"
        "ost_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='address', kw_only=T"
        "rue, fn=None), ReprPlan.Field(name='port', kw_only=True, fn=None), ReprPlan.Field(name='hosted_zone_id', kw_on"
        "ly=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='e9db080acf593b4f064dabcf02ca124667d3f6ec',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.rds', 'Endpoint'),
    ),
)
def _process_dataclass__e9db080acf593b4f064dabcf02ca124667d3f6ec():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
                address=self.address,
                port=self.port,
                hosted_zone_id=self.hosted_zone_id,
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
                self.address == other.address and
                self.port == other.port and
                self.hosted_zone_id == other.hosted_zone_id
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'address',
            'port',
            'hosted_zone_id',
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
            '__shape__',
            'address',
            'port',
            'hosted_zone_id',
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
                self.address,
                self.port,
                self.hosted_zone_id,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            address: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            port: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            hosted_zone_id: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'address', address)
            __dataclass__object_setattr(self, 'port', port)
            __dataclass__object_setattr(self, 'hosted_zone_id', hosted_zone_id)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"address={self.address!r}")
            parts.append(f"port={self.port!r}")
            parts.append(f"hosted_zone_id={self.hosted_zone_id!r}")
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
        "Plans(tup=(CopyPlan(fields=('name', 'values')), EqPlan(fields=('name', 'values')), FrozenPlan(fields=('__shape"
        "__', 'name', 'values'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('name', 'values'), c"
        "ache=False), InitPlan(fields=(InitPlan.Field(name='__shape__', annotation=OpRef(name='init.fields.0.annotation"
        "'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS_VAR, coerce=None"
        ", validate=None, check_type=None), InitPlan.Field(name='name', annotation=OpRef(name='init.fields.1.annotation"
        "'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None,"
        " validate=None, check_type=None), InitPlan.Field(name='values', annotation=OpRef(name='init.fields.2.annotatio"
        "n'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None"
        ", validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('name', 'values'), froze"
        "n=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(nam"
        "e='name', kw_only=True, fn=None), ReprPlan.Field(name='values', kw_only=True, fn=None)), id=False, terse=False"
        ", default_fn=None)))"
    ),
    plan_repr_sha1='dfb68735498463724ba64285108de491926e61ec',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.rds', 'Filter'),
    ),
)
def _process_dataclass__dfb68735498463724ba64285108de491926e61ec():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
                self.name == other.name and
                self.values == other.values
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'name',
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
            '__shape__',
            'name',
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
                self.name,
                self.values,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            name: __dataclass__init__fields__1__annotation,
            values: __dataclass__init__fields__2__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'values', values)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"name={self.name!r}")
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
        "Plans(tup=(CopyPlan(fields=('secret_arn', 'secret_status', 'kms_key_id')), EqPlan(fields=('secret_arn', 'secre"
        "t_status', 'kms_key_id')), FrozenPlan(fields=('__shape__', 'secret_arn', 'secret_status', 'kms_key_id'), allow"
        "_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('secret_arn', 'secret_status', 'kms_key_id'), cac"
        "he=False), InitPlan(fields=(InitPlan.Field(name='__shape__', annotation=OpRef(name='init.fields.0.annotation')"
        ", default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS_VAR, coerce=None, "
        "validate=None, check_type=None), InitPlan.Field(name='secret_arn', annotation=OpRef(name='init.fields.1.annota"
        "tion'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_ty"
        "pe=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='secret_status', anno"
        "tation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=No"
        "ne, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), In"
        "itPlan.Field(name='kms_key_id', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fi"
        "elds.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None,"
        " validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('secret_arn', 'secret_sta"
        "tus', 'kms_key_id'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan("
        "fields=(ReprPlan.Field(name='secret_arn', kw_only=True, fn=None), ReprPlan.Field(name='secret_status', kw_only"
        "=True, fn=None), ReprPlan.Field(name='kms_key_id', kw_only=True, fn=None)), id=False, terse=False, default_fn="
        "None)))"
    ),
    plan_repr_sha1='257988ac1433a45fc765065121e7c50a1887c0cd',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.rds', 'MasterUserSecret'),
    ),
)
def _process_dataclass__257988ac1433a45fc765065121e7c50a1887c0cd():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
                secret_arn=self.secret_arn,
                secret_status=self.secret_status,
                kms_key_id=self.kms_key_id,
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
                self.secret_arn == other.secret_arn and
                self.secret_status == other.secret_status and
                self.kms_key_id == other.kms_key_id
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'secret_arn',
            'secret_status',
            'kms_key_id',
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
            '__shape__',
            'secret_arn',
            'secret_status',
            'kms_key_id',
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
                self.secret_arn,
                self.secret_status,
                self.kms_key_id,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            secret_arn: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            secret_status: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            kms_key_id: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'secret_arn', secret_arn)
            __dataclass__object_setattr(self, 'secret_status', secret_status)
            __dataclass__object_setattr(self, 'kms_key_id', kms_key_id)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"secret_arn={self.secret_arn!r}")
            parts.append(f"secret_status={self.secret_status!r}")
            parts.append(f"kms_key_id={self.kms_key_id!r}")
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
        "Plans(tup=(CopyPlan(fields=('option_group_name', 'status')), EqPlan(fields=('option_group_name', 'status')), F"
        "rozenPlan(fields=('__shape__', 'option_group_name', 'status'), allow_dynamic_dunder_attrs=False), HashPlan(act"
        "ion='add', fields=('option_group_name', 'status'), cache=False), InitPlan(fields=(InitPlan.Field(name='__shape"
        "__', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, overrid"
        "e=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='op"
        "tion_group_name', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default"
        "'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None"
        ", check_type=None), InitPlan.Field(name='status', annotation=OpRef(name='init.fields.2.annotation'), default=O"
        "pRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INST"
        "ANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('option"
        "_group_name', 'status'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprP"
        "lan(fields=(ReprPlan.Field(name='option_group_name', kw_only=True, fn=None), ReprPlan.Field(name='status', kw_"
        "only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='c79ef861fd4c5615b5f048e9aec3299540fa33f7',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.rds', 'OptionGroupMembership'),
    ),
)
def _process_dataclass__c79ef861fd4c5615b5f048e9aec3299540fa33f7():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
                option_group_name=self.option_group_name,
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
                self.option_group_name == other.option_group_name and
                self.status == other.status
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'option_group_name',
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
            '__shape__',
            'option_group_name',
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
                self.option_group_name,
                self.status,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            option_group_name: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            status: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'option_group_name', option_group_name)
            __dataclass__object_setattr(self, 'status', status)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"option_group_name={self.option_group_name!r}")
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
        "Plans(tup=(CopyPlan(fields=('arn',)), EqPlan(fields=('arn',)), FrozenPlan(fields=('__shape__', 'arn'), allow_d"
        "ynamic_dunder_attrs=False), HashPlan(action='add', fields=('arn',), cache=False), InitPlan(fields=(InitPlan.Fi"
        "eld(name='__shape__', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, i"
        "nit=True, override=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPl"
        "an.Field(name='arn', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.defa"
        "ult'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=N"
        "one, check_type=None)), self_param='self', std_params=(), kw_only_params=('arn',), frozen=True, slots=False, p"
        "ost_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='arn', kw_only=True,"
        " fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='6eeb5cf87ddee1bcad75c8766a916fd57479a19d',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.rds', 'Outpost'),
    ),
)
def _process_dataclass__6eeb5cf87ddee1bcad75c8766a916fd57479a19d():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
                arn=self.arn,
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
                self.arn == other.arn
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'arn',
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
            '__shape__',
            'arn',
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
                self.arn,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            arn: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'arn', arn)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"arn={self.arn!r}")
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
        "Plans(tup=(CopyPlan(fields=('log_types_to_enable', 'log_types_to_disable')), EqPlan(fields=('log_types_to_enab"
        "le', 'log_types_to_disable')), FrozenPlan(fields=('__shape__', 'log_types_to_enable', 'log_types_to_disable'),"
        " allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('log_types_to_enable', 'log_types_to_disabl"
        "e'), cache=False), InitPlan(fields=(InitPlan.Field(name='__shape__', annotation=OpRef(name='init.fields.0.anno"
        "tation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS_VAR, coerc"
        "e=None, validate=None, check_type=None), InitPlan.Field(name='log_types_to_enable', annotation=OpRef(name='ini"
        "t.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, overrid"
        "e=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='log"
        "_types_to_disable', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.defau"
        "lt'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=No"
        "ne, check_type=None)), self_param='self', std_params=(), kw_only_params=('log_types_to_enable', 'log_types_to_"
        "disable'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(Re"
        "prPlan.Field(name='log_types_to_enable', kw_only=True, fn=None), ReprPlan.Field(name='log_types_to_disable', k"
        "w_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='6c402681f08e7afb46231052156de336964e583e',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.rds', 'PendingCloudwatchLogsExports'),
    ),
)
def _process_dataclass__6c402681f08e7afb46231052156de336964e583e():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
                log_types_to_enable=self.log_types_to_enable,
                log_types_to_disable=self.log_types_to_disable,
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
                self.log_types_to_enable == other.log_types_to_enable and
                self.log_types_to_disable == other.log_types_to_disable
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'log_types_to_enable',
            'log_types_to_disable',
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
            '__shape__',
            'log_types_to_enable',
            'log_types_to_disable',
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
                self.log_types_to_enable,
                self.log_types_to_disable,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            log_types_to_enable: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            log_types_to_disable: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'log_types_to_enable', log_types_to_enable)
            __dataclass__object_setattr(self, 'log_types_to_disable', log_types_to_disable)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"log_types_to_enable={self.log_types_to_enable!r}")
            parts.append(f"log_types_to_disable={self.log_types_to_disable!r}")
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
        "Plans(tup=(CopyPlan(fields=('db_instance_class', 'allocated_storage', 'master_user_password', 'port', 'backup_"
        "retention_period', 'multi_az', 'engine_version', 'license_model', 'iops', 'storage_throughput', 'db_instance_i"
        "dentifier', 'storage_type', 'ca_certificate_identifier', 'db_subnet_group_name', 'pending_cloudwatch_logs_expo"
        "rts', 'processor_features', 'automation_mode', 'resume_full_automation_mode_time', 'multi_tenant', 'iam_databa"
        "se_authentication_enabled', 'dedicated_log_volume', 'engine', 'additional_storage_volumes')), EqPlan(fields=('"
        "db_instance_class', 'allocated_storage', 'master_user_password', 'port', 'backup_retention_period', 'multi_az'"
        ", 'engine_version', 'license_model', 'iops', 'storage_throughput', 'db_instance_identifier', 'storage_type', '"
        "ca_certificate_identifier', 'db_subnet_group_name', 'pending_cloudwatch_logs_exports', 'processor_features', '"
        "automation_mode', 'resume_full_automation_mode_time', 'multi_tenant', 'iam_database_authentication_enabled', '"
        "dedicated_log_volume', 'engine', 'additional_storage_volumes')), FrozenPlan(fields=('__shape__', 'db_instance_"
        "class', 'allocated_storage', 'master_user_password', 'port', 'backup_retention_period', 'multi_az', 'engine_ve"
        "rsion', 'license_model', 'iops', 'storage_throughput', 'db_instance_identifier', 'storage_type', 'ca_certifica"
        "te_identifier', 'db_subnet_group_name', 'pending_cloudwatch_logs_exports', 'processor_features', 'automation_m"
        "ode', 'resume_full_automation_mode_time', 'multi_tenant', 'iam_database_authentication_enabled', 'dedicated_lo"
        "g_volume', 'engine', 'additional_storage_volumes'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', "
        "fields=('db_instance_class', 'allocated_storage', 'master_user_password', 'port', 'backup_retention_period', '"
        "multi_az', 'engine_version', 'license_model', 'iops', 'storage_throughput', 'db_instance_identifier', 'storage"
        "_type', 'ca_certificate_identifier', 'db_subnet_group_name', 'pending_cloudwatch_logs_exports', 'processor_fea"
        "tures', 'automation_mode', 'resume_full_automation_mode_time', 'multi_tenant', 'iam_database_authentication_en"
        "abled', 'dedicated_log_volume', 'engine', 'additional_storage_volumes'), cache=False), InitPlan(fields=(InitPl"
        "an.Field(name='__shape__', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=No"
        "ne, init=True, override=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), I"
        "nitPlan.Field(name='db_instance_class', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name="
        "'init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coer"
        "ce=None, validate=None, check_type=None), InitPlan.Field(name='allocated_storage', annotation=OpRef(name='init"
        ".fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override"
        "=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='mast"
        "er_user_password', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.defaul"
        "t'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=Non"
        "e, check_type=None), InitPlan.Field(name='port', annotation=OpRef(name='init.fields.4.annotation'), default=Op"
        "Ref(name='init.fields.4.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTA"
        "NCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='backup_retention_period', annotation=O"
        "pRef(name='init.fields.5.annotation'), default=OpRef(name='init.fields.5.default'), default_factory=None, init"
        "=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.F"
        "ield(name='multi_az', annotation=OpRef(name='init.fields.6.annotation'), default=OpRef(name='init.fields.6.def"
        "ault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate="
        "None, check_type=None), InitPlan.Field(name='engine_version', annotation=OpRef(name='init.fields.7.annotation'"
        "), default=OpRef(name='init.fields.7.default'), default_factory=None, init=True, override=False, field_type=Fi"
        "eldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='license_model', annotatio"
        "n=OpRef(name='init.fields.8.annotation'), default=OpRef(name='init.fields.8.default'), default_factory=None, i"
        "nit=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPla"
        "n.Field(name='iops', annotation=OpRef(name='init.fields.9.annotation'), default=OpRef(name='init.fields.9.defa"
        "ult'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=N"
        "one, check_type=None), InitPlan.Field(name='storage_throughput', annotation=OpRef(name='init.fields.10.annotat"
        "ion'), default=OpRef(name='init.fields.10.default'), default_factory=None, init=True, override=False, field_ty"
        "pe=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='db_instance_identifi"
        "er', annotation=OpRef(name='init.fields.11.annotation'), default=OpRef(name='init.fields.11.default'), default"
        "_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_typ"
        "e=None), InitPlan.Field(name='storage_type', annotation=OpRef(name='init.fields.12.annotation'), default=OpRef"
        "(name='init.fields.12.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANC"
        "E, coerce=None, validate=None, check_type=None), InitPlan.Field(name='ca_certificate_identifier', annotation=O"
        "pRef(name='init.fields.13.annotation'), default=OpRef(name='init.fields.13.default'), default_factory=None, in"
        "it=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan"
        ".Field(name='db_subnet_group_name', annotation=OpRef(name='init.fields.14.annotation'), default=OpRef(name='in"
        "it.fields.14.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce"
        "=None, validate=None, check_type=None), InitPlan.Field(name='pending_cloudwatch_logs_exports', annotation=OpRe"
        "f(name='init.fields.15.annotation'), default=OpRef(name='init.fields.15.default'), default_factory=None, init="
        "True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fi"
        "eld(name='processor_features', annotation=OpRef(name='init.fields.16.annotation'), default=OpRef(name='init.fi"
        "elds.16.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None"
        ", validate=None, check_type=None), InitPlan.Field(name='automation_mode', annotation=OpRef(name='init.fields.1"
        "7.annotation'), default=OpRef(name='init.fields.17.default'), default_factory=None, init=True, override=False,"
        " field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='resume_full"
        "_automation_mode_time', annotation=OpRef(name='init.fields.18.annotation'), default=OpRef(name='init.fields.18"
        ".default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valid"
        "ate=None, check_type=None), InitPlan.Field(name='multi_tenant', annotation=OpRef(name='init.fields.19.annotati"
        "on'), default=OpRef(name='init.fields.19.default'), default_factory=None, init=True, override=False, field_typ"
        "e=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='iam_database_authenti"
        "cation_enabled', annotation=OpRef(name='init.fields.20.annotation'), default=OpRef(name='init.fields.20.defaul"
        "t'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=Non"
        "e, check_type=None), InitPlan.Field(name='dedicated_log_volume', annotation=OpRef(name='init.fields.21.annotat"
        "ion'), default=OpRef(name='init.fields.21.default'), default_factory=None, init=True, override=False, field_ty"
        "pe=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='engine', annotation="
        "OpRef(name='init.fields.22.annotation'), default=OpRef(name='init.fields.22.default'), default_factory=None, i"
        "nit=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPla"
        "n.Field(name='additional_storage_volumes', annotation=OpRef(name='init.fields.23.annotation'), default=OpRef(n"
        "ame='init.fields.23.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE,"
        " coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('db_instance"
        "_class', 'allocated_storage', 'master_user_password', 'port', 'backup_retention_period', 'multi_az', 'engine_v"
        "ersion', 'license_model', 'iops', 'storage_throughput', 'db_instance_identifier', 'storage_type', 'ca_certific"
        "ate_identifier', 'db_subnet_group_name', 'pending_cloudwatch_logs_exports', 'processor_features', 'automation_"
        "mode', 'resume_full_automation_mode_time', 'multi_tenant', 'iam_database_authentication_enabled', 'dedicated_l"
        "og_volume', 'engine', 'additional_storage_volumes'), frozen=True, slots=False, post_init_params=None, init_fns"
        "=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='db_instance_class', kw_only=True, fn=None), ReprP"
        "lan.Field(name='allocated_storage', kw_only=True, fn=None), ReprPlan.Field(name='master_user_password', kw_onl"
        "y=True, fn=None), ReprPlan.Field(name='port', kw_only=True, fn=None), ReprPlan.Field(name='backup_retention_pe"
        "riod', kw_only=True, fn=None), ReprPlan.Field(name='multi_az', kw_only=True, fn=None), ReprPlan.Field(name='en"
        "gine_version', kw_only=True, fn=None), ReprPlan.Field(name='license_model', kw_only=True, fn=None), ReprPlan.F"
        "ield(name='iops', kw_only=True, fn=None), ReprPlan.Field(name='storage_throughput', kw_only=True, fn=None), Re"
        "prPlan.Field(name='db_instance_identifier', kw_only=True, fn=None), ReprPlan.Field(name='storage_type', kw_onl"
        "y=True, fn=None), ReprPlan.Field(name='ca_certificate_identifier', kw_only=True, fn=None), ReprPlan.Field(name"
        "='db_subnet_group_name', kw_only=True, fn=None), ReprPlan.Field(name='pending_cloudwatch_logs_exports', kw_onl"
        "y=True, fn=None), ReprPlan.Field(name='processor_features', kw_only=True, fn=None), ReprPlan.Field(name='autom"
        "ation_mode', kw_only=True, fn=None), ReprPlan.Field(name='resume_full_automation_mode_time', kw_only=True, fn="
        "None), ReprPlan.Field(name='multi_tenant', kw_only=True, fn=None), ReprPlan.Field(name='iam_database_authentic"
        "ation_enabled', kw_only=True, fn=None), ReprPlan.Field(name='dedicated_log_volume', kw_only=True, fn=None), Re"
        "prPlan.Field(name='engine', kw_only=True, fn=None), ReprPlan.Field(name='additional_storage_volumes', kw_only="
        "True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='ea2952e2a2b5ae7f726cb2c9405e887805a60ab8',
    op_ref_idents=(
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
        '__dataclass__init__fields__18__annotation',
        '__dataclass__init__fields__18__default',
        '__dataclass__init__fields__19__annotation',
        '__dataclass__init__fields__19__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__20__annotation',
        '__dataclass__init__fields__20__default',
        '__dataclass__init__fields__21__annotation',
        '__dataclass__init__fields__21__default',
        '__dataclass__init__fields__22__annotation',
        '__dataclass__init__fields__22__default',
        '__dataclass__init__fields__23__annotation',
        '__dataclass__init__fields__23__default',
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
        ('ominfra.clouds.aws.models.services.rds', 'PendingModifiedValues'),
    ),
)
def _process_dataclass__ea2952e2a2b5ae7f726cb2c9405e887805a60ab8():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
        __dataclass__init__fields__18__annotation,
        __dataclass__init__fields__18__default,
        __dataclass__init__fields__19__annotation,
        __dataclass__init__fields__19__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__init__fields__20__annotation,
        __dataclass__init__fields__20__default,
        __dataclass__init__fields__21__annotation,
        __dataclass__init__fields__21__default,
        __dataclass__init__fields__22__annotation,
        __dataclass__init__fields__22__default,
        __dataclass__init__fields__23__annotation,
        __dataclass__init__fields__23__default,
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
                db_instance_class=self.db_instance_class,
                allocated_storage=self.allocated_storage,
                master_user_password=self.master_user_password,
                port=self.port,
                backup_retention_period=self.backup_retention_period,
                multi_az=self.multi_az,
                engine_version=self.engine_version,
                license_model=self.license_model,
                iops=self.iops,
                storage_throughput=self.storage_throughput,
                db_instance_identifier=self.db_instance_identifier,
                storage_type=self.storage_type,
                ca_certificate_identifier=self.ca_certificate_identifier,
                db_subnet_group_name=self.db_subnet_group_name,
                pending_cloudwatch_logs_exports=self.pending_cloudwatch_logs_exports,
                processor_features=self.processor_features,
                automation_mode=self.automation_mode,
                resume_full_automation_mode_time=self.resume_full_automation_mode_time,
                multi_tenant=self.multi_tenant,
                iam_database_authentication_enabled=self.iam_database_authentication_enabled,
                dedicated_log_volume=self.dedicated_log_volume,
                engine=self.engine,
                additional_storage_volumes=self.additional_storage_volumes,
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
                self.db_instance_class == other.db_instance_class and
                self.allocated_storage == other.allocated_storage and
                self.master_user_password == other.master_user_password and
                self.port == other.port and
                self.backup_retention_period == other.backup_retention_period and
                self.multi_az == other.multi_az and
                self.engine_version == other.engine_version and
                self.license_model == other.license_model and
                self.iops == other.iops and
                self.storage_throughput == other.storage_throughput and
                self.db_instance_identifier == other.db_instance_identifier and
                self.storage_type == other.storage_type and
                self.ca_certificate_identifier == other.ca_certificate_identifier and
                self.db_subnet_group_name == other.db_subnet_group_name and
                self.pending_cloudwatch_logs_exports == other.pending_cloudwatch_logs_exports and
                self.processor_features == other.processor_features and
                self.automation_mode == other.automation_mode and
                self.resume_full_automation_mode_time == other.resume_full_automation_mode_time and
                self.multi_tenant == other.multi_tenant and
                self.iam_database_authentication_enabled == other.iam_database_authentication_enabled and
                self.dedicated_log_volume == other.dedicated_log_volume and
                self.engine == other.engine and
                self.additional_storage_volumes == other.additional_storage_volumes
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'db_instance_class',
            'allocated_storage',
            'master_user_password',
            'port',
            'backup_retention_period',
            'multi_az',
            'engine_version',
            'license_model',
            'iops',
            'storage_throughput',
            'db_instance_identifier',
            'storage_type',
            'ca_certificate_identifier',
            'db_subnet_group_name',
            'pending_cloudwatch_logs_exports',
            'processor_features',
            'automation_mode',
            'resume_full_automation_mode_time',
            'multi_tenant',
            'iam_database_authentication_enabled',
            'dedicated_log_volume',
            'engine',
            'additional_storage_volumes',
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
            '__shape__',
            'db_instance_class',
            'allocated_storage',
            'master_user_password',
            'port',
            'backup_retention_period',
            'multi_az',
            'engine_version',
            'license_model',
            'iops',
            'storage_throughput',
            'db_instance_identifier',
            'storage_type',
            'ca_certificate_identifier',
            'db_subnet_group_name',
            'pending_cloudwatch_logs_exports',
            'processor_features',
            'automation_mode',
            'resume_full_automation_mode_time',
            'multi_tenant',
            'iam_database_authentication_enabled',
            'dedicated_log_volume',
            'engine',
            'additional_storage_volumes',
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
                self.db_instance_class,
                self.allocated_storage,
                self.master_user_password,
                self.port,
                self.backup_retention_period,
                self.multi_az,
                self.engine_version,
                self.license_model,
                self.iops,
                self.storage_throughput,
                self.db_instance_identifier,
                self.storage_type,
                self.ca_certificate_identifier,
                self.db_subnet_group_name,
                self.pending_cloudwatch_logs_exports,
                self.processor_features,
                self.automation_mode,
                self.resume_full_automation_mode_time,
                self.multi_tenant,
                self.iam_database_authentication_enabled,
                self.dedicated_log_volume,
                self.engine,
                self.additional_storage_volumes,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            db_instance_class: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            allocated_storage: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            master_user_password: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            port: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            backup_retention_period: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
            multi_az: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
            engine_version: __dataclass__init__fields__7__annotation = __dataclass__init__fields__7__default,
            license_model: __dataclass__init__fields__8__annotation = __dataclass__init__fields__8__default,
            iops: __dataclass__init__fields__9__annotation = __dataclass__init__fields__9__default,
            storage_throughput: __dataclass__init__fields__10__annotation = __dataclass__init__fields__10__default,
            db_instance_identifier: __dataclass__init__fields__11__annotation = __dataclass__init__fields__11__default,
            storage_type: __dataclass__init__fields__12__annotation = __dataclass__init__fields__12__default,
            ca_certificate_identifier: __dataclass__init__fields__13__annotation = __dataclass__init__fields__13__default,
            db_subnet_group_name: __dataclass__init__fields__14__annotation = __dataclass__init__fields__14__default,
            pending_cloudwatch_logs_exports: __dataclass__init__fields__15__annotation = __dataclass__init__fields__15__default,
            processor_features: __dataclass__init__fields__16__annotation = __dataclass__init__fields__16__default,
            automation_mode: __dataclass__init__fields__17__annotation = __dataclass__init__fields__17__default,
            resume_full_automation_mode_time: __dataclass__init__fields__18__annotation = __dataclass__init__fields__18__default,
            multi_tenant: __dataclass__init__fields__19__annotation = __dataclass__init__fields__19__default,
            iam_database_authentication_enabled: __dataclass__init__fields__20__annotation = __dataclass__init__fields__20__default,
            dedicated_log_volume: __dataclass__init__fields__21__annotation = __dataclass__init__fields__21__default,
            engine: __dataclass__init__fields__22__annotation = __dataclass__init__fields__22__default,
            additional_storage_volumes: __dataclass__init__fields__23__annotation = __dataclass__init__fields__23__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'db_instance_class', db_instance_class)
            __dataclass__object_setattr(self, 'allocated_storage', allocated_storage)
            __dataclass__object_setattr(self, 'master_user_password', master_user_password)
            __dataclass__object_setattr(self, 'port', port)
            __dataclass__object_setattr(self, 'backup_retention_period', backup_retention_period)
            __dataclass__object_setattr(self, 'multi_az', multi_az)
            __dataclass__object_setattr(self, 'engine_version', engine_version)
            __dataclass__object_setattr(self, 'license_model', license_model)
            __dataclass__object_setattr(self, 'iops', iops)
            __dataclass__object_setattr(self, 'storage_throughput', storage_throughput)
            __dataclass__object_setattr(self, 'db_instance_identifier', db_instance_identifier)
            __dataclass__object_setattr(self, 'storage_type', storage_type)
            __dataclass__object_setattr(self, 'ca_certificate_identifier', ca_certificate_identifier)
            __dataclass__object_setattr(self, 'db_subnet_group_name', db_subnet_group_name)
            __dataclass__object_setattr(self, 'pending_cloudwatch_logs_exports', pending_cloudwatch_logs_exports)
            __dataclass__object_setattr(self, 'processor_features', processor_features)
            __dataclass__object_setattr(self, 'automation_mode', automation_mode)
            __dataclass__object_setattr(self, 'resume_full_automation_mode_time', resume_full_automation_mode_time)
            __dataclass__object_setattr(self, 'multi_tenant', multi_tenant)
            __dataclass__object_setattr(self, 'iam_database_authentication_enabled', iam_database_authentication_enabled)
            __dataclass__object_setattr(self, 'dedicated_log_volume', dedicated_log_volume)
            __dataclass__object_setattr(self, 'engine', engine)
            __dataclass__object_setattr(self, 'additional_storage_volumes', additional_storage_volumes)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"db_instance_class={self.db_instance_class!r}")
            parts.append(f"allocated_storage={self.allocated_storage!r}")
            parts.append(f"master_user_password={self.master_user_password!r}")
            parts.append(f"port={self.port!r}")
            parts.append(f"backup_retention_period={self.backup_retention_period!r}")
            parts.append(f"multi_az={self.multi_az!r}")
            parts.append(f"engine_version={self.engine_version!r}")
            parts.append(f"license_model={self.license_model!r}")
            parts.append(f"iops={self.iops!r}")
            parts.append(f"storage_throughput={self.storage_throughput!r}")
            parts.append(f"db_instance_identifier={self.db_instance_identifier!r}")
            parts.append(f"storage_type={self.storage_type!r}")
            parts.append(f"ca_certificate_identifier={self.ca_certificate_identifier!r}")
            parts.append(f"db_subnet_group_name={self.db_subnet_group_name!r}")
            parts.append(f"pending_cloudwatch_logs_exports={self.pending_cloudwatch_logs_exports!r}")
            parts.append(f"processor_features={self.processor_features!r}")
            parts.append(f"automation_mode={self.automation_mode!r}")
            parts.append(f"resume_full_automation_mode_time={self.resume_full_automation_mode_time!r}")
            parts.append(f"multi_tenant={self.multi_tenant!r}")
            parts.append(f"iam_database_authentication_enabled={self.iam_database_authentication_enabled!r}")
            parts.append(f"dedicated_log_volume={self.dedicated_log_volume!r}")
            parts.append(f"engine={self.engine!r}")
            parts.append(f"additional_storage_volumes={self.additional_storage_volumes!r}")
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
        "Plans(tup=(CopyPlan(fields=('name', 'value')), EqPlan(fields=('name', 'value')), FrozenPlan(fields=('__shape__"
        "', 'name', 'value'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('name', 'value'), cache"
        "=False), InitPlan(fields=(InitPlan.Field(name='__shape__', annotation=OpRef(name='init.fields.0.annotation'), "
        "default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS_VAR, coerce=None, va"
        "lidate=None, check_type=None), InitPlan.Field(name='name', annotation=OpRef(name='init.fields.1.annotation'), "
        "default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=Field"
        "Type.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='value', annotation=OpRef(nam"
        "e='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, o"
        "verride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self'"
        ", std_params=(), kw_only_params=('name', 'value'), frozen=True, slots=False, post_init_params=None, init_fns=("
        "), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='name', kw_only=True, fn=None), ReprPlan.Field(name="
        "'value', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='895749f2203fe95718692e36384965b13d7c3e70',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.rds', 'ProcessorFeature'),
    ),
)
def _process_dataclass__895749f2203fe95718692e36384965b13d7c3e70():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
                name=self.name,
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
                self.name == other.name and
                self.value == other.value
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'name',
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
            '__shape__',
            'name',
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
                self.name,
                self.value,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            name: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            value: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'value', value)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"name={self.name!r}")
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
        "Plans(tup=(CopyPlan(fields=('db_instance_identifier', 'force_failover')), EqPlan(fields=('db_instance_identifi"
        "er', 'force_failover')), FrozenPlan(fields=('__shape__', 'db_instance_identifier', 'force_failover'), allow_dy"
        "namic_dunder_attrs=False), HashPlan(action='add', fields=('db_instance_identifier', 'force_failover'), cache=F"
        "alse), InitPlan(fields=(InitPlan.Field(name='__shape__', annotation=OpRef(name='init.fields.0.annotation'), de"
        "fault=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS_VAR, coerce=None, vali"
        "date=None, check_type=None), InitPlan.Field(name='db_instance_identifier', annotation=OpRef(name='init.fields."
        "1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, "
        "coerce=None, validate=None, check_type=None), InitPlan.Field(name='force_failover', annotation=OpRef(name='ini"
        "t.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, overrid"
        "e=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_"
        "params=(), kw_only_params=('db_instance_identifier', 'force_failover'), frozen=True, slots=False, post_init_pa"
        "rams=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='db_instance_identifier', kw_on"
        "ly=True, fn=None), ReprPlan.Field(name='force_failover', kw_only=True, fn=None)), id=False, terse=False, defau"
        "lt_fn=None)))"
    ),
    plan_repr_sha1='57df3a0abb409483de9a76ede74c282972bd0875',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.rds', 'RebootDBInstanceMessage'),
    ),
)
def _process_dataclass__57df3a0abb409483de9a76ede74c282972bd0875():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
                db_instance_identifier=self.db_instance_identifier,
                force_failover=self.force_failover,
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
                self.db_instance_identifier == other.db_instance_identifier and
                self.force_failover == other.force_failover
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'db_instance_identifier',
            'force_failover',
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
            '__shape__',
            'db_instance_identifier',
            'force_failover',
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
                self.db_instance_identifier,
                self.force_failover,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            db_instance_identifier: __dataclass__init__fields__1__annotation,
            force_failover: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'db_instance_identifier', db_instance_identifier)
            __dataclass__object_setattr(self, 'force_failover', force_failover)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"db_instance_identifier={self.db_instance_identifier!r}")
            parts.append(f"force_failover={self.force_failover!r}")
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
        "Plans(tup=(CopyPlan(fields=('db_instance_identifier',)), EqPlan(fields=('db_instance_identifier',)), FrozenPla"
        "n(fields=('__shape__', 'db_instance_identifier'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fi"
        "elds=('db_instance_identifier',), cache=False), InitPlan(fields=(InitPlan.Field(name='__shape__', annotation=O"
        "pRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_ty"
        "pe=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='db_instance_identif"
        "ier', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, overri"
        "de=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std"
        "_params=(), kw_only_params=('db_instance_identifier',), frozen=True, slots=False, post_init_params=None, init_"
        "fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='db_instance_identifier', kw_only=True, fn=None"
        "),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='2034c55d12ea687458603a4a24687aa6cff4ce7a',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.rds', 'StartDBInstanceMessage'),
    ),
)
def _process_dataclass__2034c55d12ea687458603a4a24687aa6cff4ce7a():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
                db_instance_identifier=self.db_instance_identifier,
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
                self.db_instance_identifier == other.db_instance_identifier
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'db_instance_identifier',
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
            '__shape__',
            'db_instance_identifier',
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
                self.db_instance_identifier,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            db_instance_identifier: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'db_instance_identifier', db_instance_identifier)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"db_instance_identifier={self.db_instance_identifier!r}")
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
        "Plans(tup=(CopyPlan(fields=('db_instance_identifier', 'db_snapshot_identifier')), EqPlan(fields=('db_instance_"
        "identifier', 'db_snapshot_identifier')), FrozenPlan(fields=('__shape__', 'db_instance_identifier', 'db_snapsho"
        "t_identifier'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('db_instance_identifier', 'd"
        "b_snapshot_identifier'), cache=False), InitPlan(fields=(InitPlan.Field(name='__shape__', annotation=OpRef(name"
        "='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldT"
        "ype.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='db_instance_identifier', ann"
        "otation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False,"
        " field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='db_snapshot"
        "_identifier', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), "
        "default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, ch"
        "eck_type=None)), self_param='self', std_params=(), kw_only_params=('db_instance_identifier', 'db_snapshot_iden"
        "tifier'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(Rep"
        "rPlan.Field(name='db_instance_identifier', kw_only=True, fn=None), ReprPlan.Field(name='db_snapshot_identifier"
        "', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='1bdfa49bf8aca9326c28bc8eb43f474569ed2369',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.rds', 'StopDBInstanceMessage'),
    ),
)
def _process_dataclass__1bdfa49bf8aca9326c28bc8eb43f474569ed2369():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
                db_instance_identifier=self.db_instance_identifier,
                db_snapshot_identifier=self.db_snapshot_identifier,
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
                self.db_instance_identifier == other.db_instance_identifier and
                self.db_snapshot_identifier == other.db_snapshot_identifier
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'db_instance_identifier',
            'db_snapshot_identifier',
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
            '__shape__',
            'db_instance_identifier',
            'db_snapshot_identifier',
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
                self.db_instance_identifier,
                self.db_snapshot_identifier,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            db_instance_identifier: __dataclass__init__fields__1__annotation,
            db_snapshot_identifier: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'db_instance_identifier', db_instance_identifier)
            __dataclass__object_setattr(self, 'db_snapshot_identifier', db_snapshot_identifier)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"db_instance_identifier={self.db_instance_identifier!r}")
            parts.append(f"db_snapshot_identifier={self.db_snapshot_identifier!r}")
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
        "Plans(tup=(CopyPlan(fields=('subnet_identifier', 'subnet_availability_zone', 'subnet_outpost', 'subnet_status'"
        ")), EqPlan(fields=('subnet_identifier', 'subnet_availability_zone', 'subnet_outpost', 'subnet_status')), Froze"
        "nPlan(fields=('__shape__', 'subnet_identifier', 'subnet_availability_zone', 'subnet_outpost', 'subnet_status')"
        ", allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('subnet_identifier', 'subnet_availability_"
        "zone', 'subnet_outpost', 'subnet_status'), cache=False), InitPlan(fields=(InitPlan.Field(name='__shape__', ann"
        "otation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False,"
        " field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='subnet_ide"
        "ntifier', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), defa"
        "ult_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_"
        "type=None), InitPlan.Field(name='subnet_availability_zone', annotation=OpRef(name='init.fields.2.annotation'),"
        " default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=Fiel"
        "dType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='subnet_outpost', annotation"
        "=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, in"
        "it=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan"
        ".Field(name='subnet_status', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.field"
        "s.4.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, va"
        "lidate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('subnet_identifier', 'subnet"
        "_availability_zone', 'subnet_outpost', 'subnet_status'), frozen=True, slots=False, post_init_params=None, init"
        "_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='subnet_identifier', kw_only=True, fn=None), R"
        "eprPlan.Field(name='subnet_availability_zone', kw_only=True, fn=None), ReprPlan.Field(name='subnet_outpost', k"
        "w_only=True, fn=None), ReprPlan.Field(name='subnet_status', kw_only=True, fn=None)), id=False, terse=False, de"
        "fault_fn=None)))"
    ),
    plan_repr_sha1='b82211610cc9a83bb833ac58c5308bb0733d9d00',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__4__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.rds', 'Subnet'),
    ),
)
def _process_dataclass__b82211610cc9a83bb833ac58c5308bb0733d9d00():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__3__default,
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
                subnet_identifier=self.subnet_identifier,
                subnet_availability_zone=self.subnet_availability_zone,
                subnet_outpost=self.subnet_outpost,
                subnet_status=self.subnet_status,
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
                self.subnet_identifier == other.subnet_identifier and
                self.subnet_availability_zone == other.subnet_availability_zone and
                self.subnet_outpost == other.subnet_outpost and
                self.subnet_status == other.subnet_status
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'subnet_identifier',
            'subnet_availability_zone',
            'subnet_outpost',
            'subnet_status',
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
            '__shape__',
            'subnet_identifier',
            'subnet_availability_zone',
            'subnet_outpost',
            'subnet_status',
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
                self.subnet_identifier,
                self.subnet_availability_zone,
                self.subnet_outpost,
                self.subnet_status,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            subnet_identifier: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            subnet_availability_zone: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            subnet_outpost: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            subnet_status: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'subnet_identifier', subnet_identifier)
            __dataclass__object_setattr(self, 'subnet_availability_zone', subnet_availability_zone)
            __dataclass__object_setattr(self, 'subnet_outpost', subnet_outpost)
            __dataclass__object_setattr(self, 'subnet_status', subnet_status)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"subnet_identifier={self.subnet_identifier!r}")
            parts.append(f"subnet_availability_zone={self.subnet_availability_zone!r}")
            parts.append(f"subnet_outpost={self.subnet_outpost!r}")
            parts.append(f"subnet_status={self.subnet_status!r}")
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
        "Plans(tup=(CopyPlan(fields=('resource_type', 'tags')), EqPlan(fields=('resource_type', 'tags')), FrozenPlan(fi"
        "elds=('__shape__', 'resource_type', 'tags'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields="
        "('resource_type', 'tags'), cache=False), InitPlan(fields=(InitPlan.Field(name='__shape__', annotation=OpRef(na"
        "me='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=Fiel"
        "dType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='resource_type', annotation"
        "=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, in"
        "it=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan"
        ".Field(name='tags', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.defau"
        "lt'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=No"
        "ne, check_type=None)), self_param='self', std_params=(), kw_only_params=('resource_type', 'tags'), frozen=True"
        ", slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='res"
        "ource_type', kw_only=True, fn=None), ReprPlan.Field(name='tags', kw_only=True, fn=None)), id=False, terse=Fals"
        "e, default_fn=None)))"
    ),
    plan_repr_sha1='72408a250113d7efc0131778f5e6fa438b55e772',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.rds', 'TagSpecification'),
    ),
)
def _process_dataclass__72408a250113d7efc0131778f5e6fa438b55e772():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
                resource_type=self.resource_type,
                tags=self.tags,
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
                self.resource_type == other.resource_type and
                self.tags == other.tags
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'resource_type',
            'tags',
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
            '__shape__',
            'resource_type',
            'tags',
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
                self.resource_type,
                self.tags,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            resource_type: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            tags: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'resource_type', resource_type)
            __dataclass__object_setattr(self, 'tags', tags)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"resource_type={self.resource_type!r}")
            parts.append(f"tags={self.tags!r}")
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
        "Plans(tup=(CopyPlan(fields=('vpc_security_group_id', 'status')), EqPlan(fields=('vpc_security_group_id', 'stat"
        "us')), FrozenPlan(fields=('__shape__', 'vpc_security_group_id', 'status'), allow_dynamic_dunder_attrs=False), "
        "HashPlan(action='add', fields=('vpc_security_group_id', 'status'), cache=False), InitPlan(fields=(InitPlan.Fie"
        "ld(name='__shape__', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, in"
        "it=True, override=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPla"
        "n.Field(name='vpc_security_group_id', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='i"
        "nit.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce"
        "=None, validate=None, check_type=None), InitPlan.Field(name='status', annotation=OpRef(name='init.fields.2.ann"
        "otation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field"
        "_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_"
        "only_params=('vpc_security_group_id', 'status'), frozen=True, slots=False, post_init_params=None, init_fns=(),"
        " validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='vpc_security_group_id', kw_only=True, fn=None), ReprP"
        "lan.Field(name='status', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='3d0aa6d7bd2c7a9f510ef82abbbea50c5d70db25',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.rds', 'VpcSecurityGroupMembership'),
    ),
)
def _process_dataclass__3d0aa6d7bd2c7a9f510ef82abbbea50c5d70db25():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
                vpc_security_group_id=self.vpc_security_group_id,
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
                self.vpc_security_group_id == other.vpc_security_group_id and
                self.status == other.status
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'vpc_security_group_id',
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
            '__shape__',
            'vpc_security_group_id',
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
                self.vpc_security_group_id,
                self.status,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            vpc_security_group_id: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            status: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'vpc_security_group_id', vpc_security_group_id)
            __dataclass__object_setattr(self, 'status', status)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"vpc_security_group_id={self.vpc_security_group_id!r}")
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
