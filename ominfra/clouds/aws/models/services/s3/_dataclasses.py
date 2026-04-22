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
        "Plans(tup=(CopyPlan(fields=('name', 'creation_date', 'bucket_region', 'bucket_arn')), EqPlan(fields=('name', '"
        "creation_date', 'bucket_region', 'bucket_arn')), FrozenPlan(fields=('__shape__', 'name', 'creation_date', 'buc"
        "ket_region', 'bucket_arn'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('name', 'creatio"
        "n_date', 'bucket_region', 'bucket_arn'), cache=False), InitPlan(fields=(InitPlan.Field(name='__shape__', annot"
        "ation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, f"
        "ield_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='name', annot"
        "ation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=Non"
        "e, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), Ini"
        "tPlan.Field(name='creation_date', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init."
        "fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=Non"
        "e, validate=None, check_type=None), InitPlan.Field(name='bucket_region', annotation=OpRef(name='init.fields.3."
        "annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, fi"
        "eld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='bucket_arn', a"
        "nnotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_factory"
        "=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None))"
        ", self_param='self', std_params=(), kw_only_params=('name', 'creation_date', 'bucket_region', 'bucket_arn'), f"
        "rozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field"
        "(name='name', kw_only=True, fn=None), ReprPlan.Field(name='creation_date', kw_only=True, fn=None), ReprPlan.Fi"
        "eld(name='bucket_region', kw_only=True, fn=None), ReprPlan.Field(name='bucket_arn', kw_only=True, fn=None)), i"
        "d=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='0ba4959af046e5f753c22c868059f5fc7bb853f8',
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
        ('ominfra.clouds.aws.models.services.s3', 'Bucket'),
    ),
)
def _process_dataclass__0ba4959af046e5f753c22c868059f5fc7bb853f8():
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
                name=self.name,
                creation_date=self.creation_date,
                bucket_region=self.bucket_region,
                bucket_arn=self.bucket_arn,
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
                self.creation_date == other.creation_date and
                self.bucket_region == other.bucket_region and
                self.bucket_arn == other.bucket_arn
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'name',
            'creation_date',
            'bucket_region',
            'bucket_arn',
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
            'creation_date',
            'bucket_region',
            'bucket_arn',
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
                self.creation_date,
                self.bucket_region,
                self.bucket_arn,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            name: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            creation_date: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            bucket_region: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            bucket_arn: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'creation_date', creation_date)
            __dataclass__object_setattr(self, 'bucket_region', bucket_region)
            __dataclass__object_setattr(self, 'bucket_arn', bucket_arn)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"name={self.name!r}")
            parts.append(f"creation_date={self.creation_date!r}")
            parts.append(f"bucket_region={self.bucket_region!r}")
            parts.append(f"bucket_arn={self.bucket_arn!r}")
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
        "Plans(tup=(CopyPlan(fields=('prefix',)), EqPlan(fields=('prefix',)), FrozenPlan(fields=('__shape__', 'prefix')"
        ", allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('prefix',), cache=False), InitPlan(fields="
        "(InitPlan.Field(name='__shape__', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_fac"
        "tory=None, init=True, override=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=N"
        "one), InitPlan.Field(name='prefix', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='ini"
        "t.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=N"
        "one, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('prefix',), frozen=Tr"
        "ue, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='p"
        "refix', kw_only=True, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='50832bf2c74ab08578a3f9566ba6bd3f114aa4fd',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.s3', 'CommonPrefix'),
    ),
)
def _process_dataclass__50832bf2c74ab08578a3f9566ba6bd3f114aa4fd():
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
                prefix=self.prefix,
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
                self.prefix == other.prefix
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'prefix',
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
            'prefix',
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
                self.prefix,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            prefix: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'prefix', prefix)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"prefix={self.prefix!r}")
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
        "Plans(tup=(CopyPlan(fields=('delete_marker', 'version_id', 'request_charged')), EqPlan(fields=('delete_marker'"
        ", 'version_id', 'request_charged')), FrozenPlan(fields=('__shape__', 'delete_marker', 'version_id', 'request_c"
        "harged'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('delete_marker', 'version_id', 're"
        "quest_charged'), cache=False), InitPlan(fields=(InitPlan.Field(name='__shape__', annotation=OpRef(name='init.f"
        "ields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLAS"
        "S_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='delete_marker', annotation=OpRef(nam"
        "e='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, o"
        "verride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(nam"
        "e='version_id', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default')"
        ", default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, "
        "check_type=None), InitPlan.Field(name='request_charged', annotation=OpRef(name='init.fields.3.annotation'), de"
        "fault=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldTy"
        "pe.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=("
        "'delete_marker', 'version_id', 'request_charged'), frozen=True, slots=False, post_init_params=None, init_fns=("
        "), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='delete_marker', kw_only=True, fn=None), ReprPlan.Fi"
        "eld(name='version_id', kw_only=True, fn=None), ReprPlan.Field(name='request_charged', kw_only=True, fn=None)),"
        " id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='5c39bd4aeaeb4d1400d167fcf34d220b90689df3',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.s3', 'DeleteObjectOutput'),
    ),
)
def _process_dataclass__5c39bd4aeaeb4d1400d167fcf34d220b90689df3():
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
                delete_marker=self.delete_marker,
                version_id=self.version_id,
                request_charged=self.request_charged,
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
                self.delete_marker == other.delete_marker and
                self.version_id == other.version_id and
                self.request_charged == other.request_charged
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'delete_marker',
            'version_id',
            'request_charged',
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
            'delete_marker',
            'version_id',
            'request_charged',
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
                self.delete_marker,
                self.version_id,
                self.request_charged,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            delete_marker: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            version_id: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            request_charged: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'delete_marker', delete_marker)
            __dataclass__object_setattr(self, 'version_id', version_id)
            __dataclass__object_setattr(self, 'request_charged', request_charged)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"delete_marker={self.delete_marker!r}")
            parts.append(f"version_id={self.version_id!r}")
            parts.append(f"request_charged={self.request_charged!r}")
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
        "Plans(tup=(CopyPlan(fields=('bucket', 'key', 'mfa', 'version_id', 'request_payer', 'bypass_governance_retentio"
        "n', 'expected_bucket_owner', 'if_match', 'if_match_last_modified_time', 'if_match_size')), EqPlan(fields=('buc"
        "ket', 'key', 'mfa', 'version_id', 'request_payer', 'bypass_governance_retention', 'expected_bucket_owner', 'if"
        "_match', 'if_match_last_modified_time', 'if_match_size')), FrozenPlan(fields=('__shape__', 'bucket', 'key', 'm"
        "fa', 'version_id', 'request_payer', 'bypass_governance_retention', 'expected_bucket_owner', 'if_match', 'if_ma"
        "tch_last_modified_time', 'if_match_size'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('"
        "bucket', 'key', 'mfa', 'version_id', 'request_payer', 'bypass_governance_retention', 'expected_bucket_owner', "
        "'if_match', 'if_match_last_modified_time', 'if_match_size'), cache=False), InitPlan(fields=(InitPlan.Field(nam"
        "e='__shape__', annotation=OpRef(name='init.fields.00.annotation'), default=None, default_factory=None, init=Tr"
        "ue, override=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Fie"
        "ld(name='bucket', annotation=OpRef(name='init.fields.01.annotation'), default=None, default_factory=None, init"
        "=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.F"
        "ield(name='key', annotation=OpRef(name='init.fields.02.annotation'), default=None, default_factory=None, init="
        "True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fi"
        "eld(name='mfa', annotation=OpRef(name='init.fields.03.annotation'), default=OpRef(name='init.fields.03.default"
        "'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None"
        ", check_type=None), InitPlan.Field(name='version_id', annotation=OpRef(name='init.fields.04.annotation'), defa"
        "ult=OpRef(name='init.fields.04.default'), default_factory=None, init=True, override=False, field_type=FieldTyp"
        "e.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='request_payer', annotation=OpRe"
        "f(name='init.fields.05.annotation'), default=OpRef(name='init.fields.05.default'), default_factory=None, init="
        "True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fi"
        "eld(name='bypass_governance_retention', annotation=OpRef(name='init.fields.06.annotation'), default=OpRef(name"
        "='init.fields.06.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, co"
        "erce=None, validate=None, check_type=None), InitPlan.Field(name='expected_bucket_owner', annotation=OpRef(name"
        "='init.fields.07.annotation'), default=OpRef(name='init.fields.07.default'), default_factory=None, init=True, "
        "override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(na"
        "me='if_match', annotation=OpRef(name='init.fields.08.annotation'), default=OpRef(name='init.fields.08.default'"
        "), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None,"
        " check_type=None), InitPlan.Field(name='if_match_last_modified_time', annotation=OpRef(name='init.fields.09.an"
        "notation'), default=OpRef(name='init.fields.09.default'), default_factory=None, init=True, override=False, fie"
        "ld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='if_match_size',"
        " annotation=OpRef(name='init.fields.10.annotation'), default=OpRef(name='init.fields.10.default'), default_fac"
        "tory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=No"
        "ne)), self_param='self', std_params=(), kw_only_params=('bucket', 'key', 'mfa', 'version_id', 'request_payer',"
        " 'bypass_governance_retention', 'expected_bucket_owner', 'if_match', 'if_match_last_modified_time', 'if_match_"
        "size'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprP"
        "lan.Field(name='bucket', kw_only=True, fn=None), ReprPlan.Field(name='key', kw_only=True, fn=None), ReprPlan.F"
        "ield(name='mfa', kw_only=True, fn=None), ReprPlan.Field(name='version_id', kw_only=True, fn=None), ReprPlan.Fi"
        "eld(name='request_payer', kw_only=True, fn=None), ReprPlan.Field(name='bypass_governance_retention', kw_only=T"
        "rue, fn=None), ReprPlan.Field(name='expected_bucket_owner', kw_only=True, fn=None), ReprPlan.Field(name='if_ma"
        "tch', kw_only=True, fn=None), ReprPlan.Field(name='if_match_last_modified_time', kw_only=True, fn=None), ReprP"
        "lan.Field(name='if_match_size', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='0d24f0e649023f9d2f4eea942c719541cf5cc865',
    op_ref_idents=(
        '__dataclass__init__fields__01__annotation',
        '__dataclass__init__fields__02__annotation',
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
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.s3', 'DeleteObjectRequest'),
    ),
)
def _process_dataclass__0d24f0e649023f9d2f4eea942c719541cf5cc865():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__01__annotation,
        __dataclass__init__fields__02__annotation,
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
                bucket=self.bucket,
                key=self.key,
                mfa=self.mfa,
                version_id=self.version_id,
                request_payer=self.request_payer,
                bypass_governance_retention=self.bypass_governance_retention,
                expected_bucket_owner=self.expected_bucket_owner,
                if_match=self.if_match,
                if_match_last_modified_time=self.if_match_last_modified_time,
                if_match_size=self.if_match_size,
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
                self.bucket == other.bucket and
                self.key == other.key and
                self.mfa == other.mfa and
                self.version_id == other.version_id and
                self.request_payer == other.request_payer and
                self.bypass_governance_retention == other.bypass_governance_retention and
                self.expected_bucket_owner == other.expected_bucket_owner and
                self.if_match == other.if_match and
                self.if_match_last_modified_time == other.if_match_last_modified_time and
                self.if_match_size == other.if_match_size
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'bucket',
            'key',
            'mfa',
            'version_id',
            'request_payer',
            'bypass_governance_retention',
            'expected_bucket_owner',
            'if_match',
            'if_match_last_modified_time',
            'if_match_size',
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
            'bucket',
            'key',
            'mfa',
            'version_id',
            'request_payer',
            'bypass_governance_retention',
            'expected_bucket_owner',
            'if_match',
            'if_match_last_modified_time',
            'if_match_size',
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
                self.bucket,
                self.key,
                self.mfa,
                self.version_id,
                self.request_payer,
                self.bypass_governance_retention,
                self.expected_bucket_owner,
                self.if_match,
                self.if_match_last_modified_time,
                self.if_match_size,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            bucket: __dataclass__init__fields__01__annotation,
            key: __dataclass__init__fields__02__annotation,
            mfa: __dataclass__init__fields__03__annotation = __dataclass__init__fields__03__default,
            version_id: __dataclass__init__fields__04__annotation = __dataclass__init__fields__04__default,
            request_payer: __dataclass__init__fields__05__annotation = __dataclass__init__fields__05__default,
            bypass_governance_retention: __dataclass__init__fields__06__annotation = __dataclass__init__fields__06__default,
            expected_bucket_owner: __dataclass__init__fields__07__annotation = __dataclass__init__fields__07__default,
            if_match: __dataclass__init__fields__08__annotation = __dataclass__init__fields__08__default,
            if_match_last_modified_time: __dataclass__init__fields__09__annotation = __dataclass__init__fields__09__default,
            if_match_size: __dataclass__init__fields__10__annotation = __dataclass__init__fields__10__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'bucket', bucket)
            __dataclass__object_setattr(self, 'key', key)
            __dataclass__object_setattr(self, 'mfa', mfa)
            __dataclass__object_setattr(self, 'version_id', version_id)
            __dataclass__object_setattr(self, 'request_payer', request_payer)
            __dataclass__object_setattr(self, 'bypass_governance_retention', bypass_governance_retention)
            __dataclass__object_setattr(self, 'expected_bucket_owner', expected_bucket_owner)
            __dataclass__object_setattr(self, 'if_match', if_match)
            __dataclass__object_setattr(self, 'if_match_last_modified_time', if_match_last_modified_time)
            __dataclass__object_setattr(self, 'if_match_size', if_match_size)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"bucket={self.bucket!r}")
            parts.append(f"key={self.key!r}")
            parts.append(f"mfa={self.mfa!r}")
            parts.append(f"version_id={self.version_id!r}")
            parts.append(f"request_payer={self.request_payer!r}")
            parts.append(f"bypass_governance_retention={self.bypass_governance_retention!r}")
            parts.append(f"expected_bucket_owner={self.expected_bucket_owner!r}")
            parts.append(f"if_match={self.if_match!r}")
            parts.append(f"if_match_last_modified_time={self.if_match_last_modified_time!r}")
            parts.append(f"if_match_size={self.if_match_size!r}")
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
        ('ominfra.clouds.aws.models.services.s3', 'EncryptionTypeMismatch'),
        ('ominfra.clouds.aws.models.services.s3', 'InvalidRequest'),
        ('ominfra.clouds.aws.models.services.s3', 'InvalidWriteOffset'),
        ('ominfra.clouds.aws.models.services.s3', 'NoSuchBucket'),
        ('ominfra.clouds.aws.models.services.s3', 'NoSuchKey'),
        ('ominfra.clouds.aws.models.services.s3', 'TooManyParts'),
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
        "Plans(tup=(CopyPlan(fields=('body', 'delete_marker', 'accept_ranges', 'expiration', 'restore', 'last_modified'"
        ", 'content_length', 'etag', 'checksum_crc32', 'checksum_crc32c', 'checksum_crc64nvme', 'checksum_sha1', 'check"
        "sum_sha256', 'checksum_sha512', 'checksum_md5', 'checksum_xxhash64', 'checksum_xxhash3', 'checksum_xxhash128',"
        " 'checksum_type', 'missing_meta', 'version_id', 'cache_control', 'content_disposition', 'content_encoding', 'c"
        "ontent_language', 'content_range', 'content_type', 'expires', 'website_redirect_location', 'server_side_encryp"
        "tion', 'metadata', 'sse_customer_algorithm', 'sse_customer_key_md5', 'sse_kms_key_id', 'bucket_key_enabled', '"
        "storage_class', 'request_charged', 'replication_status', 'parts_count', 'tag_count', 'object_lock_mode', 'obje"
        "ct_lock_retain_until_date', 'object_lock_legal_hold_status')), EqPlan(fields=('body', 'delete_marker', 'accept"
        "_ranges', 'expiration', 'restore', 'last_modified', 'content_length', 'etag', 'checksum_crc32', 'checksum_crc3"
        "2c', 'checksum_crc64nvme', 'checksum_sha1', 'checksum_sha256', 'checksum_sha512', 'checksum_md5', 'checksum_xx"
        "hash64', 'checksum_xxhash3', 'checksum_xxhash128', 'checksum_type', 'missing_meta', 'version_id', 'cache_contr"
        "ol', 'content_disposition', 'content_encoding', 'content_language', 'content_range', 'content_type', 'expires'"
        ", 'website_redirect_location', 'server_side_encryption', 'metadata', 'sse_customer_algorithm', 'sse_customer_k"
        "ey_md5', 'sse_kms_key_id', 'bucket_key_enabled', 'storage_class', 'request_charged', 'replication_status', 'pa"
        "rts_count', 'tag_count', 'object_lock_mode', 'object_lock_retain_until_date', 'object_lock_legal_hold_status')"
        "), FrozenPlan(fields=('__shape__', 'body', 'delete_marker', 'accept_ranges', 'expiration', 'restore', 'last_mo"
        "dified', 'content_length', 'etag', 'checksum_crc32', 'checksum_crc32c', 'checksum_crc64nvme', 'checksum_sha1',"
        " 'checksum_sha256', 'checksum_sha512', 'checksum_md5', 'checksum_xxhash64', 'checksum_xxhash3', 'checksum_xxha"
        "sh128', 'checksum_type', 'missing_meta', 'version_id', 'cache_control', 'content_disposition', 'content_encodi"
        "ng', 'content_language', 'content_range', 'content_type', 'expires', 'website_redirect_location', 'server_side"
        "_encryption', 'metadata', 'sse_customer_algorithm', 'sse_customer_key_md5', 'sse_kms_key_id', 'bucket_key_enab"
        "led', 'storage_class', 'request_charged', 'replication_status', 'parts_count', 'tag_count', 'object_lock_mode'"
        ", 'object_lock_retain_until_date', 'object_lock_legal_hold_status'), allow_dynamic_dunder_attrs=False), HashPl"
        "an(action='add', fields=('body', 'delete_marker', 'accept_ranges', 'expiration', 'restore', 'last_modified', '"
        "content_length', 'etag', 'checksum_crc32', 'checksum_crc32c', 'checksum_crc64nvme', 'checksum_sha1', 'checksum"
        "_sha256', 'checksum_sha512', 'checksum_md5', 'checksum_xxhash64', 'checksum_xxhash3', 'checksum_xxhash128', 'c"
        "hecksum_type', 'missing_meta', 'version_id', 'cache_control', 'content_disposition', 'content_encoding', 'cont"
        "ent_language', 'content_range', 'content_type', 'expires', 'website_redirect_location', 'server_side_encryptio"
        "n', 'metadata', 'sse_customer_algorithm', 'sse_customer_key_md5', 'sse_kms_key_id', 'bucket_key_enabled', 'sto"
        "rage_class', 'request_charged', 'replication_status', 'parts_count', 'tag_count', 'object_lock_mode', 'object_"
        "lock_retain_until_date', 'object_lock_legal_hold_status'), cache=False), InitPlan(fields=(InitPlan.Field(name="
        "'__shape__', annotation=OpRef(name='init.fields.00.annotation'), default=None, default_factory=None, init=True"
        ", override=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field"
        "(name='body', annotation=OpRef(name='init.fields.01.annotation'), default=OpRef(name='init.fields.01.default')"
        ", default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, "
        "check_type=None), InitPlan.Field(name='delete_marker', annotation=OpRef(name='init.fields.02.annotation'), def"
        "ault=OpRef(name='init.fields.02.default'), default_factory=None, init=True, override=False, field_type=FieldTy"
        "pe.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='accept_ranges', annotation=OpR"
        "ef(name='init.fields.03.annotation'), default=OpRef(name='init.fields.03.default'), default_factory=None, init"
        "=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.F"
        "ield(name='expiration', annotation=OpRef(name='init.fields.04.annotation'), default=OpRef(name='init.fields.04"
        ".default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valid"
        "ate=None, check_type=None), InitPlan.Field(name='restore', annotation=OpRef(name='init.fields.05.annotation'),"
        " default=OpRef(name='init.fields.05.default'), default_factory=None, init=True, override=False, field_type=Fie"
        "ldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='last_modified', annotation"
        "=OpRef(name='init.fields.06.annotation'), default=OpRef(name='init.fields.06.default'), default_factory=None, "
        "init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPl"
        "an.Field(name='content_length', annotation=OpRef(name='init.fields.07.annotation'), default=OpRef(name='init.f"
        "ields.07.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=Non"
        "e, validate=None, check_type=None), InitPlan.Field(name='etag', annotation=OpRef(name='init.fields.08.annotati"
        "on'), default=OpRef(name='init.fields.08.default'), default_factory=None, init=True, override=False, field_typ"
        "e=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='checksum_crc32', anno"
        "tation=OpRef(name='init.fields.09.annotation'), default=OpRef(name='init.fields.09.default'), default_factory="
        "None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), "
        "InitPlan.Field(name='checksum_crc32c', annotation=OpRef(name='init.fields.10.annotation'), default=OpRef(name="
        "'init.fields.10.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coe"
        "rce=None, validate=None, check_type=None), InitPlan.Field(name='checksum_crc64nvme', annotation=OpRef(name='in"
        "it.fields.11.annotation'), default=OpRef(name='init.fields.11.default'), default_factory=None, init=True, over"
        "ride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='"
        "checksum_sha1', annotation=OpRef(name='init.fields.12.annotation'), default=OpRef(name='init.fields.12.default"
        "'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None"
        ", check_type=None), InitPlan.Field(name='checksum_sha256', annotation=OpRef(name='init.fields.13.annotation'),"
        " default=OpRef(name='init.fields.13.default'), default_factory=None, init=True, override=False, field_type=Fie"
        "ldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='checksum_sha512', annotati"
        "on=OpRef(name='init.fields.14.annotation'), default=OpRef(name='init.fields.14.default'), default_factory=None"
        ", init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), Init"
        "Plan.Field(name='checksum_md5', annotation=OpRef(name='init.fields.15.annotation'), default=OpRef(name='init.f"
        "ields.15.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=Non"
        "e, validate=None, check_type=None), InitPlan.Field(name='checksum_xxhash64', annotation=OpRef(name='init.field"
        "s.16.annotation'), default=OpRef(name='init.fields.16.default'), default_factory=None, init=True, override=Fal"
        "se, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='checksum"
        "_xxhash3', annotation=OpRef(name='init.fields.17.annotation'), default=OpRef(name='init.fields.17.default'), d"
        "efault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, che"
        "ck_type=None), InitPlan.Field(name='checksum_xxhash128', annotation=OpRef(name='init.fields.18.annotation'), d"
        "efault=OpRef(name='init.fields.18.default'), default_factory=None, init=True, override=False, field_type=Field"
        "Type.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='checksum_type', annotation=O"
        "pRef(name='init.fields.19.annotation'), default=OpRef(name='init.fields.19.default'), default_factory=None, in"
        "it=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan"
        ".Field(name='missing_meta', annotation=OpRef(name='init.fields.20.annotation'), default=OpRef(name='init.field"
        "s.20.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, v"
        "alidate=None, check_type=None), InitPlan.Field(name='version_id', annotation=OpRef(name='init.fields.21.annota"
        "tion'), default=OpRef(name='init.fields.21.default'), default_factory=None, init=True, override=False, field_t"
        "ype=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='cache_control', ann"
        "otation=OpRef(name='init.fields.22.annotation'), default=OpRef(name='init.fields.22.default'), default_factory"
        "=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),"
        " InitPlan.Field(name='content_disposition', annotation=OpRef(name='init.fields.23.annotation'), default=OpRef("
        "name='init.fields.23.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE"
        ", coerce=None, validate=None, check_type=None), InitPlan.Field(name='content_encoding', annotation=OpRef(name="
        "'init.fields.24.annotation'), default=OpRef(name='init.fields.24.default'), default_factory=None, init=True, o"
        "verride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(nam"
        "e='content_language', annotation=OpRef(name='init.fields.25.annotation'), default=OpRef(name='init.fields.25.d"
        "efault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validat"
        "e=None, check_type=None), InitPlan.Field(name='content_range', annotation=OpRef(name='init.fields.26.annotatio"
        "n'), default=OpRef(name='init.fields.26.default'), default_factory=None, init=True, override=False, field_type"
        "=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='content_type', annotat"
        "ion=OpRef(name='init.fields.27.annotation'), default=OpRef(name='init.fields.27.default'), default_factory=Non"
        "e, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), Ini"
        "tPlan.Field(name='expires', annotation=OpRef(name='init.fields.28.annotation'), default=OpRef(name='init.field"
        "s.28.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, v"
        "alidate=None, check_type=None), InitPlan.Field(name='website_redirect_location', annotation=OpRef(name='init.f"
        "ields.29.annotation'), default=OpRef(name='init.fields.29.default'), default_factory=None, init=True, override"
        "=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='serv"
        "er_side_encryption', annotation=OpRef(name='init.fields.30.annotation'), default=OpRef(name='init.fields.30.de"
        "fault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate"
        "=None, check_type=None), InitPlan.Field(name='metadata', annotation=OpRef(name='init.fields.31.annotation'), d"
        "efault=OpRef(name='init.fields.31.default'), default_factory=None, init=True, override=False, field_type=Field"
        "Type.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='sse_customer_algorithm', ann"
        "otation=OpRef(name='init.fields.32.annotation'), default=OpRef(name='init.fields.32.default'), default_factory"
        "=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),"
        " InitPlan.Field(name='sse_customer_key_md5', annotation=OpRef(name='init.fields.33.annotation'), default=OpRef"
        "(name='init.fields.33.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANC"
        "E, coerce=None, validate=None, check_type=None), InitPlan.Field(name='sse_kms_key_id', annotation=OpRef(name='"
        "init.fields.34.annotation'), default=OpRef(name='init.fields.34.default'), default_factory=None, init=True, ov"
        "erride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name"
        "='bucket_key_enabled', annotation=OpRef(name='init.fields.35.annotation'), default=OpRef(name='init.fields.35."
        "default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valida"
        "te=None, check_type=None), InitPlan.Field(name='storage_class', annotation=OpRef(name='init.fields.36.annotati"
        "on'), default=OpRef(name='init.fields.36.default'), default_factory=None, init=True, override=False, field_typ"
        "e=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='request_charged', ann"
        "otation=OpRef(name='init.fields.37.annotation'), default=OpRef(name='init.fields.37.default'), default_factory"
        "=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),"
        " InitPlan.Field(name='replication_status', annotation=OpRef(name='init.fields.38.annotation'), default=OpRef(n"
        "ame='init.fields.38.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE,"
        " coerce=None, validate=None, check_type=None), InitPlan.Field(name='parts_count', annotation=OpRef(name='init."
        "fields.39.annotation'), default=OpRef(name='init.fields.39.default'), default_factory=None, init=True, overrid"
        "e=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='tag"
        "_count', annotation=OpRef(name='init.fields.40.annotation'), default=OpRef(name='init.fields.40.default'), def"
        "ault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check"
        "_type=None), InitPlan.Field(name='object_lock_mode', annotation=OpRef(name='init.fields.41.annotation'), defau"
        "lt=OpRef(name='init.fields.41.default'), default_factory=None, init=True, override=False, field_type=FieldType"
        ".INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='object_lock_retain_until_date', "
        "annotation=OpRef(name='init.fields.42.annotation'), default=OpRef(name='init.fields.42.default'), default_fact"
        "ory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=Non"
        "e), InitPlan.Field(name='object_lock_legal_hold_status', annotation=OpRef(name='init.fields.43.annotation'), d"
        "efault=OpRef(name='init.fields.43.default'), default_factory=None, init=True, override=False, field_type=Field"
        "Type.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params"
        "=('body', 'delete_marker', 'accept_ranges', 'expiration', 'restore', 'last_modified', 'content_length', 'etag'"
        ", 'checksum_crc32', 'checksum_crc32c', 'checksum_crc64nvme', 'checksum_sha1', 'checksum_sha256', 'checksum_sha"
        "512', 'checksum_md5', 'checksum_xxhash64', 'checksum_xxhash3', 'checksum_xxhash128', 'checksum_type', 'missing"
        "_meta', 'version_id', 'cache_control', 'content_disposition', 'content_encoding', 'content_language', 'content"
        "_range', 'content_type', 'expires', 'website_redirect_location', 'server_side_encryption', 'metadata', 'sse_cu"
        "stomer_algorithm', 'sse_customer_key_md5', 'sse_kms_key_id', 'bucket_key_enabled', 'storage_class', 'request_c"
        "harged', 'replication_status', 'parts_count', 'tag_count', 'object_lock_mode', 'object_lock_retain_until_date'"
        ", 'object_lock_legal_hold_status'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns"
        "=()), ReprPlan(fields=(ReprPlan.Field(name='body', kw_only=True, fn=None), ReprPlan.Field(name='delete_marker'"
        ", kw_only=True, fn=None), ReprPlan.Field(name='accept_ranges', kw_only=True, fn=None), ReprPlan.Field(name='ex"
        "piration', kw_only=True, fn=None), ReprPlan.Field(name='restore', kw_only=True, fn=None), ReprPlan.Field(name="
        "'last_modified', kw_only=True, fn=None), ReprPlan.Field(name='content_length', kw_only=True, fn=None), ReprPla"
        "n.Field(name='etag', kw_only=True, fn=None), ReprPlan.Field(name='checksum_crc32', kw_only=True, fn=None), Rep"
        "rPlan.Field(name='checksum_crc32c', kw_only=True, fn=None), ReprPlan.Field(name='checksum_crc64nvme', kw_only="
        "True, fn=None), ReprPlan.Field(name='checksum_sha1', kw_only=True, fn=None), ReprPlan.Field(name='checksum_sha"
        "256', kw_only=True, fn=None), ReprPlan.Field(name='checksum_sha512', kw_only=True, fn=None), ReprPlan.Field(na"
        "me='checksum_md5', kw_only=True, fn=None), ReprPlan.Field(name='checksum_xxhash64', kw_only=True, fn=None), Re"
        "prPlan.Field(name='checksum_xxhash3', kw_only=True, fn=None), ReprPlan.Field(name='checksum_xxhash128', kw_onl"
        "y=True, fn=None), ReprPlan.Field(name='checksum_type', kw_only=True, fn=None), ReprPlan.Field(name='missing_me"
        "ta', kw_only=True, fn=None), ReprPlan.Field(name='version_id', kw_only=True, fn=None), ReprPlan.Field(name='ca"
        "che_control', kw_only=True, fn=None), ReprPlan.Field(name='content_disposition', kw_only=True, fn=None), ReprP"
        "lan.Field(name='content_encoding', kw_only=True, fn=None), ReprPlan.Field(name='content_language', kw_only=Tru"
        "e, fn=None), ReprPlan.Field(name='content_range', kw_only=True, fn=None), ReprPlan.Field(name='content_type', "
        "kw_only=True, fn=None), ReprPlan.Field(name='expires', kw_only=True, fn=None), ReprPlan.Field(name='website_re"
        "direct_location', kw_only=True, fn=None), ReprPlan.Field(name='server_side_encryption', kw_only=True, fn=None)"
        ", ReprPlan.Field(name='metadata', kw_only=True, fn=None), ReprPlan.Field(name='sse_customer_algorithm', kw_onl"
        "y=True, fn=None), ReprPlan.Field(name='sse_customer_key_md5', kw_only=True, fn=None), ReprPlan.Field(name='sse"
        "_kms_key_id', kw_only=True, fn=None), ReprPlan.Field(name='bucket_key_enabled', kw_only=True, fn=None), ReprPl"
        "an.Field(name='storage_class', kw_only=True, fn=None), ReprPlan.Field(name='request_charged', kw_only=True, fn"
        "=None), ReprPlan.Field(name='replication_status', kw_only=True, fn=None), ReprPlan.Field(name='parts_count', k"
        "w_only=True, fn=None), ReprPlan.Field(name='tag_count', kw_only=True, fn=None), ReprPlan.Field(name='object_lo"
        "ck_mode', kw_only=True, fn=None), ReprPlan.Field(name='object_lock_retain_until_date', kw_only=True, fn=None),"
        " ReprPlan.Field(name='object_lock_legal_hold_status', kw_only=True, fn=None)), id=False, terse=False, default_"
        "fn=None)))"
    ),
    plan_repr_sha1='f2d61c623503edbdc3b3083fe9dc65eae2e4ccba',
    op_ref_idents=(
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
        '__dataclass__init__fields__18__annotation',
        '__dataclass__init__fields__18__default',
        '__dataclass__init__fields__19__annotation',
        '__dataclass__init__fields__19__default',
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
        '__dataclass__init__fields__40__annotation',
        '__dataclass__init__fields__40__default',
        '__dataclass__init__fields__41__annotation',
        '__dataclass__init__fields__41__default',
        '__dataclass__init__fields__42__annotation',
        '__dataclass__init__fields__42__default',
        '__dataclass__init__fields__43__annotation',
        '__dataclass__init__fields__43__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.s3', 'GetObjectOutput'),
    ),
)
def _process_dataclass__f2d61c623503edbdc3b3083fe9dc65eae2e4ccba():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
        __dataclass__init__fields__18__annotation,
        __dataclass__init__fields__18__default,
        __dataclass__init__fields__19__annotation,
        __dataclass__init__fields__19__default,
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
        __dataclass__init__fields__40__annotation,
        __dataclass__init__fields__40__default,
        __dataclass__init__fields__41__annotation,
        __dataclass__init__fields__41__default,
        __dataclass__init__fields__42__annotation,
        __dataclass__init__fields__42__default,
        __dataclass__init__fields__43__annotation,
        __dataclass__init__fields__43__default,
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
                body=self.body,
                delete_marker=self.delete_marker,
                accept_ranges=self.accept_ranges,
                expiration=self.expiration,
                restore=self.restore,
                last_modified=self.last_modified,
                content_length=self.content_length,
                etag=self.etag,
                checksum_crc32=self.checksum_crc32,
                checksum_crc32c=self.checksum_crc32c,
                checksum_crc64nvme=self.checksum_crc64nvme,
                checksum_sha1=self.checksum_sha1,
                checksum_sha256=self.checksum_sha256,
                checksum_sha512=self.checksum_sha512,
                checksum_md5=self.checksum_md5,
                checksum_xxhash64=self.checksum_xxhash64,
                checksum_xxhash3=self.checksum_xxhash3,
                checksum_xxhash128=self.checksum_xxhash128,
                checksum_type=self.checksum_type,
                missing_meta=self.missing_meta,
                version_id=self.version_id,
                cache_control=self.cache_control,
                content_disposition=self.content_disposition,
                content_encoding=self.content_encoding,
                content_language=self.content_language,
                content_range=self.content_range,
                content_type=self.content_type,
                expires=self.expires,
                website_redirect_location=self.website_redirect_location,
                server_side_encryption=self.server_side_encryption,
                metadata=self.metadata,
                sse_customer_algorithm=self.sse_customer_algorithm,
                sse_customer_key_md5=self.sse_customer_key_md5,
                sse_kms_key_id=self.sse_kms_key_id,
                bucket_key_enabled=self.bucket_key_enabled,
                storage_class=self.storage_class,
                request_charged=self.request_charged,
                replication_status=self.replication_status,
                parts_count=self.parts_count,
                tag_count=self.tag_count,
                object_lock_mode=self.object_lock_mode,
                object_lock_retain_until_date=self.object_lock_retain_until_date,
                object_lock_legal_hold_status=self.object_lock_legal_hold_status,
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
                self.body == other.body and
                self.delete_marker == other.delete_marker and
                self.accept_ranges == other.accept_ranges and
                self.expiration == other.expiration and
                self.restore == other.restore and
                self.last_modified == other.last_modified and
                self.content_length == other.content_length and
                self.etag == other.etag and
                self.checksum_crc32 == other.checksum_crc32 and
                self.checksum_crc32c == other.checksum_crc32c and
                self.checksum_crc64nvme == other.checksum_crc64nvme and
                self.checksum_sha1 == other.checksum_sha1 and
                self.checksum_sha256 == other.checksum_sha256 and
                self.checksum_sha512 == other.checksum_sha512 and
                self.checksum_md5 == other.checksum_md5 and
                self.checksum_xxhash64 == other.checksum_xxhash64 and
                self.checksum_xxhash3 == other.checksum_xxhash3 and
                self.checksum_xxhash128 == other.checksum_xxhash128 and
                self.checksum_type == other.checksum_type and
                self.missing_meta == other.missing_meta and
                self.version_id == other.version_id and
                self.cache_control == other.cache_control and
                self.content_disposition == other.content_disposition and
                self.content_encoding == other.content_encoding and
                self.content_language == other.content_language and
                self.content_range == other.content_range and
                self.content_type == other.content_type and
                self.expires == other.expires and
                self.website_redirect_location == other.website_redirect_location and
                self.server_side_encryption == other.server_side_encryption and
                self.metadata == other.metadata and
                self.sse_customer_algorithm == other.sse_customer_algorithm and
                self.sse_customer_key_md5 == other.sse_customer_key_md5 and
                self.sse_kms_key_id == other.sse_kms_key_id and
                self.bucket_key_enabled == other.bucket_key_enabled and
                self.storage_class == other.storage_class and
                self.request_charged == other.request_charged and
                self.replication_status == other.replication_status and
                self.parts_count == other.parts_count and
                self.tag_count == other.tag_count and
                self.object_lock_mode == other.object_lock_mode and
                self.object_lock_retain_until_date == other.object_lock_retain_until_date and
                self.object_lock_legal_hold_status == other.object_lock_legal_hold_status
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'body',
            'delete_marker',
            'accept_ranges',
            'expiration',
            'restore',
            'last_modified',
            'content_length',
            'etag',
            'checksum_crc32',
            'checksum_crc32c',
            'checksum_crc64nvme',
            'checksum_sha1',
            'checksum_sha256',
            'checksum_sha512',
            'checksum_md5',
            'checksum_xxhash64',
            'checksum_xxhash3',
            'checksum_xxhash128',
            'checksum_type',
            'missing_meta',
            'version_id',
            'cache_control',
            'content_disposition',
            'content_encoding',
            'content_language',
            'content_range',
            'content_type',
            'expires',
            'website_redirect_location',
            'server_side_encryption',
            'metadata',
            'sse_customer_algorithm',
            'sse_customer_key_md5',
            'sse_kms_key_id',
            'bucket_key_enabled',
            'storage_class',
            'request_charged',
            'replication_status',
            'parts_count',
            'tag_count',
            'object_lock_mode',
            'object_lock_retain_until_date',
            'object_lock_legal_hold_status',
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
            'body',
            'delete_marker',
            'accept_ranges',
            'expiration',
            'restore',
            'last_modified',
            'content_length',
            'etag',
            'checksum_crc32',
            'checksum_crc32c',
            'checksum_crc64nvme',
            'checksum_sha1',
            'checksum_sha256',
            'checksum_sha512',
            'checksum_md5',
            'checksum_xxhash64',
            'checksum_xxhash3',
            'checksum_xxhash128',
            'checksum_type',
            'missing_meta',
            'version_id',
            'cache_control',
            'content_disposition',
            'content_encoding',
            'content_language',
            'content_range',
            'content_type',
            'expires',
            'website_redirect_location',
            'server_side_encryption',
            'metadata',
            'sse_customer_algorithm',
            'sse_customer_key_md5',
            'sse_kms_key_id',
            'bucket_key_enabled',
            'storage_class',
            'request_charged',
            'replication_status',
            'parts_count',
            'tag_count',
            'object_lock_mode',
            'object_lock_retain_until_date',
            'object_lock_legal_hold_status',
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
                self.body,
                self.delete_marker,
                self.accept_ranges,
                self.expiration,
                self.restore,
                self.last_modified,
                self.content_length,
                self.etag,
                self.checksum_crc32,
                self.checksum_crc32c,
                self.checksum_crc64nvme,
                self.checksum_sha1,
                self.checksum_sha256,
                self.checksum_sha512,
                self.checksum_md5,
                self.checksum_xxhash64,
                self.checksum_xxhash3,
                self.checksum_xxhash128,
                self.checksum_type,
                self.missing_meta,
                self.version_id,
                self.cache_control,
                self.content_disposition,
                self.content_encoding,
                self.content_language,
                self.content_range,
                self.content_type,
                self.expires,
                self.website_redirect_location,
                self.server_side_encryption,
                self.metadata,
                self.sse_customer_algorithm,
                self.sse_customer_key_md5,
                self.sse_kms_key_id,
                self.bucket_key_enabled,
                self.storage_class,
                self.request_charged,
                self.replication_status,
                self.parts_count,
                self.tag_count,
                self.object_lock_mode,
                self.object_lock_retain_until_date,
                self.object_lock_legal_hold_status,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            body: __dataclass__init__fields__01__annotation = __dataclass__init__fields__01__default,
            delete_marker: __dataclass__init__fields__02__annotation = __dataclass__init__fields__02__default,
            accept_ranges: __dataclass__init__fields__03__annotation = __dataclass__init__fields__03__default,
            expiration: __dataclass__init__fields__04__annotation = __dataclass__init__fields__04__default,
            restore: __dataclass__init__fields__05__annotation = __dataclass__init__fields__05__default,
            last_modified: __dataclass__init__fields__06__annotation = __dataclass__init__fields__06__default,
            content_length: __dataclass__init__fields__07__annotation = __dataclass__init__fields__07__default,
            etag: __dataclass__init__fields__08__annotation = __dataclass__init__fields__08__default,
            checksum_crc32: __dataclass__init__fields__09__annotation = __dataclass__init__fields__09__default,
            checksum_crc32c: __dataclass__init__fields__10__annotation = __dataclass__init__fields__10__default,
            checksum_crc64nvme: __dataclass__init__fields__11__annotation = __dataclass__init__fields__11__default,
            checksum_sha1: __dataclass__init__fields__12__annotation = __dataclass__init__fields__12__default,
            checksum_sha256: __dataclass__init__fields__13__annotation = __dataclass__init__fields__13__default,
            checksum_sha512: __dataclass__init__fields__14__annotation = __dataclass__init__fields__14__default,
            checksum_md5: __dataclass__init__fields__15__annotation = __dataclass__init__fields__15__default,
            checksum_xxhash64: __dataclass__init__fields__16__annotation = __dataclass__init__fields__16__default,
            checksum_xxhash3: __dataclass__init__fields__17__annotation = __dataclass__init__fields__17__default,
            checksum_xxhash128: __dataclass__init__fields__18__annotation = __dataclass__init__fields__18__default,
            checksum_type: __dataclass__init__fields__19__annotation = __dataclass__init__fields__19__default,
            missing_meta: __dataclass__init__fields__20__annotation = __dataclass__init__fields__20__default,
            version_id: __dataclass__init__fields__21__annotation = __dataclass__init__fields__21__default,
            cache_control: __dataclass__init__fields__22__annotation = __dataclass__init__fields__22__default,
            content_disposition: __dataclass__init__fields__23__annotation = __dataclass__init__fields__23__default,
            content_encoding: __dataclass__init__fields__24__annotation = __dataclass__init__fields__24__default,
            content_language: __dataclass__init__fields__25__annotation = __dataclass__init__fields__25__default,
            content_range: __dataclass__init__fields__26__annotation = __dataclass__init__fields__26__default,
            content_type: __dataclass__init__fields__27__annotation = __dataclass__init__fields__27__default,
            expires: __dataclass__init__fields__28__annotation = __dataclass__init__fields__28__default,
            website_redirect_location: __dataclass__init__fields__29__annotation = __dataclass__init__fields__29__default,
            server_side_encryption: __dataclass__init__fields__30__annotation = __dataclass__init__fields__30__default,
            metadata: __dataclass__init__fields__31__annotation = __dataclass__init__fields__31__default,
            sse_customer_algorithm: __dataclass__init__fields__32__annotation = __dataclass__init__fields__32__default,
            sse_customer_key_md5: __dataclass__init__fields__33__annotation = __dataclass__init__fields__33__default,
            sse_kms_key_id: __dataclass__init__fields__34__annotation = __dataclass__init__fields__34__default,
            bucket_key_enabled: __dataclass__init__fields__35__annotation = __dataclass__init__fields__35__default,
            storage_class: __dataclass__init__fields__36__annotation = __dataclass__init__fields__36__default,
            request_charged: __dataclass__init__fields__37__annotation = __dataclass__init__fields__37__default,
            replication_status: __dataclass__init__fields__38__annotation = __dataclass__init__fields__38__default,
            parts_count: __dataclass__init__fields__39__annotation = __dataclass__init__fields__39__default,
            tag_count: __dataclass__init__fields__40__annotation = __dataclass__init__fields__40__default,
            object_lock_mode: __dataclass__init__fields__41__annotation = __dataclass__init__fields__41__default,
            object_lock_retain_until_date: __dataclass__init__fields__42__annotation = __dataclass__init__fields__42__default,
            object_lock_legal_hold_status: __dataclass__init__fields__43__annotation = __dataclass__init__fields__43__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'body', body)
            __dataclass__object_setattr(self, 'delete_marker', delete_marker)
            __dataclass__object_setattr(self, 'accept_ranges', accept_ranges)
            __dataclass__object_setattr(self, 'expiration', expiration)
            __dataclass__object_setattr(self, 'restore', restore)
            __dataclass__object_setattr(self, 'last_modified', last_modified)
            __dataclass__object_setattr(self, 'content_length', content_length)
            __dataclass__object_setattr(self, 'etag', etag)
            __dataclass__object_setattr(self, 'checksum_crc32', checksum_crc32)
            __dataclass__object_setattr(self, 'checksum_crc32c', checksum_crc32c)
            __dataclass__object_setattr(self, 'checksum_crc64nvme', checksum_crc64nvme)
            __dataclass__object_setattr(self, 'checksum_sha1', checksum_sha1)
            __dataclass__object_setattr(self, 'checksum_sha256', checksum_sha256)
            __dataclass__object_setattr(self, 'checksum_sha512', checksum_sha512)
            __dataclass__object_setattr(self, 'checksum_md5', checksum_md5)
            __dataclass__object_setattr(self, 'checksum_xxhash64', checksum_xxhash64)
            __dataclass__object_setattr(self, 'checksum_xxhash3', checksum_xxhash3)
            __dataclass__object_setattr(self, 'checksum_xxhash128', checksum_xxhash128)
            __dataclass__object_setattr(self, 'checksum_type', checksum_type)
            __dataclass__object_setattr(self, 'missing_meta', missing_meta)
            __dataclass__object_setattr(self, 'version_id', version_id)
            __dataclass__object_setattr(self, 'cache_control', cache_control)
            __dataclass__object_setattr(self, 'content_disposition', content_disposition)
            __dataclass__object_setattr(self, 'content_encoding', content_encoding)
            __dataclass__object_setattr(self, 'content_language', content_language)
            __dataclass__object_setattr(self, 'content_range', content_range)
            __dataclass__object_setattr(self, 'content_type', content_type)
            __dataclass__object_setattr(self, 'expires', expires)
            __dataclass__object_setattr(self, 'website_redirect_location', website_redirect_location)
            __dataclass__object_setattr(self, 'server_side_encryption', server_side_encryption)
            __dataclass__object_setattr(self, 'metadata', metadata)
            __dataclass__object_setattr(self, 'sse_customer_algorithm', sse_customer_algorithm)
            __dataclass__object_setattr(self, 'sse_customer_key_md5', sse_customer_key_md5)
            __dataclass__object_setattr(self, 'sse_kms_key_id', sse_kms_key_id)
            __dataclass__object_setattr(self, 'bucket_key_enabled', bucket_key_enabled)
            __dataclass__object_setattr(self, 'storage_class', storage_class)
            __dataclass__object_setattr(self, 'request_charged', request_charged)
            __dataclass__object_setattr(self, 'replication_status', replication_status)
            __dataclass__object_setattr(self, 'parts_count', parts_count)
            __dataclass__object_setattr(self, 'tag_count', tag_count)
            __dataclass__object_setattr(self, 'object_lock_mode', object_lock_mode)
            __dataclass__object_setattr(self, 'object_lock_retain_until_date', object_lock_retain_until_date)
            __dataclass__object_setattr(self, 'object_lock_legal_hold_status', object_lock_legal_hold_status)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"body={self.body!r}")
            parts.append(f"delete_marker={self.delete_marker!r}")
            parts.append(f"accept_ranges={self.accept_ranges!r}")
            parts.append(f"expiration={self.expiration!r}")
            parts.append(f"restore={self.restore!r}")
            parts.append(f"last_modified={self.last_modified!r}")
            parts.append(f"content_length={self.content_length!r}")
            parts.append(f"etag={self.etag!r}")
            parts.append(f"checksum_crc32={self.checksum_crc32!r}")
            parts.append(f"checksum_crc32c={self.checksum_crc32c!r}")
            parts.append(f"checksum_crc64nvme={self.checksum_crc64nvme!r}")
            parts.append(f"checksum_sha1={self.checksum_sha1!r}")
            parts.append(f"checksum_sha256={self.checksum_sha256!r}")
            parts.append(f"checksum_sha512={self.checksum_sha512!r}")
            parts.append(f"checksum_md5={self.checksum_md5!r}")
            parts.append(f"checksum_xxhash64={self.checksum_xxhash64!r}")
            parts.append(f"checksum_xxhash3={self.checksum_xxhash3!r}")
            parts.append(f"checksum_xxhash128={self.checksum_xxhash128!r}")
            parts.append(f"checksum_type={self.checksum_type!r}")
            parts.append(f"missing_meta={self.missing_meta!r}")
            parts.append(f"version_id={self.version_id!r}")
            parts.append(f"cache_control={self.cache_control!r}")
            parts.append(f"content_disposition={self.content_disposition!r}")
            parts.append(f"content_encoding={self.content_encoding!r}")
            parts.append(f"content_language={self.content_language!r}")
            parts.append(f"content_range={self.content_range!r}")
            parts.append(f"content_type={self.content_type!r}")
            parts.append(f"expires={self.expires!r}")
            parts.append(f"website_redirect_location={self.website_redirect_location!r}")
            parts.append(f"server_side_encryption={self.server_side_encryption!r}")
            parts.append(f"metadata={self.metadata!r}")
            parts.append(f"sse_customer_algorithm={self.sse_customer_algorithm!r}")
            parts.append(f"sse_customer_key_md5={self.sse_customer_key_md5!r}")
            parts.append(f"sse_kms_key_id={self.sse_kms_key_id!r}")
            parts.append(f"bucket_key_enabled={self.bucket_key_enabled!r}")
            parts.append(f"storage_class={self.storage_class!r}")
            parts.append(f"request_charged={self.request_charged!r}")
            parts.append(f"replication_status={self.replication_status!r}")
            parts.append(f"parts_count={self.parts_count!r}")
            parts.append(f"tag_count={self.tag_count!r}")
            parts.append(f"object_lock_mode={self.object_lock_mode!r}")
            parts.append(f"object_lock_retain_until_date={self.object_lock_retain_until_date!r}")
            parts.append(f"object_lock_legal_hold_status={self.object_lock_legal_hold_status!r}")
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
        "Plans(tup=(CopyPlan(fields=('bucket', 'if_match', 'if_modified_since', 'if_none_match', 'if_unmodified_since',"
        " 'key', 'range', 'response_cache_control', 'response_content_disposition', 'response_content_encoding', 'respo"
        "nse_content_language', 'response_content_type', 'response_expires', 'version_id', 'sse_customer_algorithm', 's"
        "se_customer_key', 'sse_customer_key_md5', 'request_payer', 'part_number', 'expected_bucket_owner', 'checksum_m"
        "ode')), EqPlan(fields=('bucket', 'if_match', 'if_modified_since', 'if_none_match', 'if_unmodified_since', 'key"
        "', 'range', 'response_cache_control', 'response_content_disposition', 'response_content_encoding', 'response_c"
        "ontent_language', 'response_content_type', 'response_expires', 'version_id', 'sse_customer_algorithm', 'sse_cu"
        "stomer_key', 'sse_customer_key_md5', 'request_payer', 'part_number', 'expected_bucket_owner', 'checksum_mode')"
        "), FrozenPlan(fields=('__shape__', 'bucket', 'if_match', 'if_modified_since', 'if_none_match', 'if_unmodified_"
        "since', 'key', 'range', 'response_cache_control', 'response_content_disposition', 'response_content_encoding',"
        " 'response_content_language', 'response_content_type', 'response_expires', 'version_id', 'sse_customer_algorit"
        "hm', 'sse_customer_key', 'sse_customer_key_md5', 'request_payer', 'part_number', 'expected_bucket_owner', 'che"
        "cksum_mode'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('bucket', 'if_match', 'if_modi"
        "fied_since', 'if_none_match', 'if_unmodified_since', 'key', 'range', 'response_cache_control', 'response_conte"
        "nt_disposition', 'response_content_encoding', 'response_content_language', 'response_content_type', 'response_"
        "expires', 'version_id', 'sse_customer_algorithm', 'sse_customer_key', 'sse_customer_key_md5', 'request_payer',"
        " 'part_number', 'expected_bucket_owner', 'checksum_mode'), cache=False), InitPlan(fields=(InitPlan.Field(name="
        "'__shape__', annotation=OpRef(name='init.fields.00.annotation'), default=None, default_factory=None, init=True"
        ", override=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field"
        "(name='bucket', annotation=OpRef(name='init.fields.01.annotation'), default=None, default_factory=None, init=T"
        "rue, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fie"
        "ld(name='if_match', annotation=OpRef(name='init.fields.02.annotation'), default=OpRef(name='init.fields.02.def"
        "ault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate="
        "None, check_type=None), InitPlan.Field(name='if_modified_since', annotation=OpRef(name='init.fields.03.annotat"
        "ion'), default=OpRef(name='init.fields.03.default'), default_factory=None, init=True, override=False, field_ty"
        "pe=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='if_none_match', anno"
        "tation=OpRef(name='init.fields.04.annotation'), default=OpRef(name='init.fields.04.default'), default_factory="
        "None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), "
        "InitPlan.Field(name='if_unmodified_since', annotation=OpRef(name='init.fields.05.annotation'), default=OpRef(n"
        "ame='init.fields.05.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE,"
        " coerce=None, validate=None, check_type=None), InitPlan.Field(name='key', annotation=OpRef(name='init.fields.0"
        "6.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, "
        "coerce=None, validate=None, check_type=None), InitPlan.Field(name='range', annotation=OpRef(name='init.fields."
        "07.annotation'), default=OpRef(name='init.fields.07.default'), default_factory=None, init=True, override=False"
        ", field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='response_c"
        "ache_control', annotation=OpRef(name='init.fields.08.annotation'), default=OpRef(name='init.fields.08.default'"
        "), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None,"
        " check_type=None), InitPlan.Field(name='response_content_disposition', annotation=OpRef(name='init.fields.09.a"
        "nnotation'), default=OpRef(name='init.fields.09.default'), default_factory=None, init=True, override=False, fi"
        "eld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='response_conte"
        "nt_encoding', annotation=OpRef(name='init.fields.10.annotation'), default=OpRef(name='init.fields.10.default')"
        ", default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, "
        "check_type=None), InitPlan.Field(name='response_content_language', annotation=OpRef(name='init.fields.11.annot"
        "ation'), default=OpRef(name='init.fields.11.default'), default_factory=None, init=True, override=False, field_"
        "type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='response_content_t"
        "ype', annotation=OpRef(name='init.fields.12.annotation'), default=OpRef(name='init.fields.12.default'), defaul"
        "t_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_ty"
        "pe=None), InitPlan.Field(name='response_expires', annotation=OpRef(name='init.fields.13.annotation'), default="
        "OpRef(name='init.fields.13.default'), default_factory=None, init=True, override=False, field_type=FieldType.IN"
        "STANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='version_id', annotation=OpRef(name="
        "'init.fields.14.annotation'), default=OpRef(name='init.fields.14.default'), default_factory=None, init=True, o"
        "verride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(nam"
        "e='sse_customer_algorithm', annotation=OpRef(name='init.fields.15.annotation'), default=OpRef(name='init.field"
        "s.15.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, v"
        "alidate=None, check_type=None), InitPlan.Field(name='sse_customer_key', annotation=OpRef(name='init.fields.16."
        "annotation'), default=OpRef(name='init.fields.16.default'), default_factory=None, init=True, override=False, f"
        "ield_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='sse_customer_"
        "key_md5', annotation=OpRef(name='init.fields.17.annotation'), default=OpRef(name='init.fields.17.default'), de"
        "fault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, chec"
        "k_type=None), InitPlan.Field(name='request_payer', annotation=OpRef(name='init.fields.18.annotation'), default"
        "=OpRef(name='init.fields.18.default'), default_factory=None, init=True, override=False, field_type=FieldType.I"
        "NSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='part_number', annotation=OpRef(nam"
        "e='init.fields.19.annotation'), default=OpRef(name='init.fields.19.default'), default_factory=None, init=True,"
        " override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(n"
        "ame='expected_bucket_owner', annotation=OpRef(name='init.fields.20.annotation'), default=OpRef(name='init.fiel"
        "ds.20.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, "
        "validate=None, check_type=None), InitPlan.Field(name='checksum_mode', annotation=OpRef(name='init.fields.21.an"
        "notation'), default=OpRef(name='init.fields.21.default'), default_factory=None, init=True, override=False, fie"
        "ld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), k"
        "w_only_params=('bucket', 'if_match', 'if_modified_since', 'if_none_match', 'if_unmodified_since', 'key', 'rang"
        "e', 'response_cache_control', 'response_content_disposition', 'response_content_encoding', 'response_content_l"
        "anguage', 'response_content_type', 'response_expires', 'version_id', 'sse_customer_algorithm', 'sse_customer_k"
        "ey', 'sse_customer_key_md5', 'request_payer', 'part_number', 'expected_bucket_owner', 'checksum_mode'), frozen"
        "=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name"
        "='bucket', kw_only=True, fn=None), ReprPlan.Field(name='if_match', kw_only=True, fn=None), ReprPlan.Field(name"
        "='if_modified_since', kw_only=True, fn=None), ReprPlan.Field(name='if_none_match', kw_only=True, fn=None), Rep"
        "rPlan.Field(name='if_unmodified_since', kw_only=True, fn=None), ReprPlan.Field(name='key', kw_only=True, fn=No"
        "ne), ReprPlan.Field(name='range', kw_only=True, fn=None), ReprPlan.Field(name='response_cache_control', kw_onl"
        "y=True, fn=None), ReprPlan.Field(name='response_content_disposition', kw_only=True, fn=None), ReprPlan.Field(n"
        "ame='response_content_encoding', kw_only=True, fn=None), ReprPlan.Field(name='response_content_language', kw_o"
        "nly=True, fn=None), ReprPlan.Field(name='response_content_type', kw_only=True, fn=None), ReprPlan.Field(name='"
        "response_expires', kw_only=True, fn=None), ReprPlan.Field(name='version_id', kw_only=True, fn=None), ReprPlan."
        "Field(name='sse_customer_algorithm', kw_only=True, fn=None), ReprPlan.Field(name='sse_customer_key', kw_only=T"
        "rue, fn=None), ReprPlan.Field(name='sse_customer_key_md5', kw_only=True, fn=None), ReprPlan.Field(name='reques"
        "t_payer', kw_only=True, fn=None), ReprPlan.Field(name='part_number', kw_only=True, fn=None), ReprPlan.Field(na"
        "me='expected_bucket_owner', kw_only=True, fn=None), ReprPlan.Field(name='checksum_mode', kw_only=True, fn=None"
        ")), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='4fa97a96968bb2d6638f4f859057e914ac311d3a',
    op_ref_idents=(
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
        '__dataclass__init__fields__18__annotation',
        '__dataclass__init__fields__18__default',
        '__dataclass__init__fields__19__annotation',
        '__dataclass__init__fields__19__default',
        '__dataclass__init__fields__20__annotation',
        '__dataclass__init__fields__20__default',
        '__dataclass__init__fields__21__annotation',
        '__dataclass__init__fields__21__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.s3', 'GetObjectRequest'),
    ),
)
def _process_dataclass__4fa97a96968bb2d6638f4f859057e914ac311d3a():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
        __dataclass__init__fields__18__annotation,
        __dataclass__init__fields__18__default,
        __dataclass__init__fields__19__annotation,
        __dataclass__init__fields__19__default,
        __dataclass__init__fields__20__annotation,
        __dataclass__init__fields__20__default,
        __dataclass__init__fields__21__annotation,
        __dataclass__init__fields__21__default,
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
                bucket=self.bucket,
                if_match=self.if_match,
                if_modified_since=self.if_modified_since,
                if_none_match=self.if_none_match,
                if_unmodified_since=self.if_unmodified_since,
                key=self.key,
                range=self.range,
                response_cache_control=self.response_cache_control,
                response_content_disposition=self.response_content_disposition,
                response_content_encoding=self.response_content_encoding,
                response_content_language=self.response_content_language,
                response_content_type=self.response_content_type,
                response_expires=self.response_expires,
                version_id=self.version_id,
                sse_customer_algorithm=self.sse_customer_algorithm,
                sse_customer_key=self.sse_customer_key,
                sse_customer_key_md5=self.sse_customer_key_md5,
                request_payer=self.request_payer,
                part_number=self.part_number,
                expected_bucket_owner=self.expected_bucket_owner,
                checksum_mode=self.checksum_mode,
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
                self.bucket == other.bucket and
                self.if_match == other.if_match and
                self.if_modified_since == other.if_modified_since and
                self.if_none_match == other.if_none_match and
                self.if_unmodified_since == other.if_unmodified_since and
                self.key == other.key and
                self.range == other.range and
                self.response_cache_control == other.response_cache_control and
                self.response_content_disposition == other.response_content_disposition and
                self.response_content_encoding == other.response_content_encoding and
                self.response_content_language == other.response_content_language and
                self.response_content_type == other.response_content_type and
                self.response_expires == other.response_expires and
                self.version_id == other.version_id and
                self.sse_customer_algorithm == other.sse_customer_algorithm and
                self.sse_customer_key == other.sse_customer_key and
                self.sse_customer_key_md5 == other.sse_customer_key_md5 and
                self.request_payer == other.request_payer and
                self.part_number == other.part_number and
                self.expected_bucket_owner == other.expected_bucket_owner and
                self.checksum_mode == other.checksum_mode
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'bucket',
            'if_match',
            'if_modified_since',
            'if_none_match',
            'if_unmodified_since',
            'key',
            'range',
            'response_cache_control',
            'response_content_disposition',
            'response_content_encoding',
            'response_content_language',
            'response_content_type',
            'response_expires',
            'version_id',
            'sse_customer_algorithm',
            'sse_customer_key',
            'sse_customer_key_md5',
            'request_payer',
            'part_number',
            'expected_bucket_owner',
            'checksum_mode',
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
            'bucket',
            'if_match',
            'if_modified_since',
            'if_none_match',
            'if_unmodified_since',
            'key',
            'range',
            'response_cache_control',
            'response_content_disposition',
            'response_content_encoding',
            'response_content_language',
            'response_content_type',
            'response_expires',
            'version_id',
            'sse_customer_algorithm',
            'sse_customer_key',
            'sse_customer_key_md5',
            'request_payer',
            'part_number',
            'expected_bucket_owner',
            'checksum_mode',
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
                self.bucket,
                self.if_match,
                self.if_modified_since,
                self.if_none_match,
                self.if_unmodified_since,
                self.key,
                self.range,
                self.response_cache_control,
                self.response_content_disposition,
                self.response_content_encoding,
                self.response_content_language,
                self.response_content_type,
                self.response_expires,
                self.version_id,
                self.sse_customer_algorithm,
                self.sse_customer_key,
                self.sse_customer_key_md5,
                self.request_payer,
                self.part_number,
                self.expected_bucket_owner,
                self.checksum_mode,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            bucket: __dataclass__init__fields__01__annotation,
            if_match: __dataclass__init__fields__02__annotation = __dataclass__init__fields__02__default,
            if_modified_since: __dataclass__init__fields__03__annotation = __dataclass__init__fields__03__default,
            if_none_match: __dataclass__init__fields__04__annotation = __dataclass__init__fields__04__default,
            if_unmodified_since: __dataclass__init__fields__05__annotation = __dataclass__init__fields__05__default,
            key: __dataclass__init__fields__06__annotation,
            range: __dataclass__init__fields__07__annotation = __dataclass__init__fields__07__default,
            response_cache_control: __dataclass__init__fields__08__annotation = __dataclass__init__fields__08__default,
            response_content_disposition: __dataclass__init__fields__09__annotation = __dataclass__init__fields__09__default,
            response_content_encoding: __dataclass__init__fields__10__annotation = __dataclass__init__fields__10__default,
            response_content_language: __dataclass__init__fields__11__annotation = __dataclass__init__fields__11__default,
            response_content_type: __dataclass__init__fields__12__annotation = __dataclass__init__fields__12__default,
            response_expires: __dataclass__init__fields__13__annotation = __dataclass__init__fields__13__default,
            version_id: __dataclass__init__fields__14__annotation = __dataclass__init__fields__14__default,
            sse_customer_algorithm: __dataclass__init__fields__15__annotation = __dataclass__init__fields__15__default,
            sse_customer_key: __dataclass__init__fields__16__annotation = __dataclass__init__fields__16__default,
            sse_customer_key_md5: __dataclass__init__fields__17__annotation = __dataclass__init__fields__17__default,
            request_payer: __dataclass__init__fields__18__annotation = __dataclass__init__fields__18__default,
            part_number: __dataclass__init__fields__19__annotation = __dataclass__init__fields__19__default,
            expected_bucket_owner: __dataclass__init__fields__20__annotation = __dataclass__init__fields__20__default,
            checksum_mode: __dataclass__init__fields__21__annotation = __dataclass__init__fields__21__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'bucket', bucket)
            __dataclass__object_setattr(self, 'if_match', if_match)
            __dataclass__object_setattr(self, 'if_modified_since', if_modified_since)
            __dataclass__object_setattr(self, 'if_none_match', if_none_match)
            __dataclass__object_setattr(self, 'if_unmodified_since', if_unmodified_since)
            __dataclass__object_setattr(self, 'key', key)
            __dataclass__object_setattr(self, 'range', range)
            __dataclass__object_setattr(self, 'response_cache_control', response_cache_control)
            __dataclass__object_setattr(self, 'response_content_disposition', response_content_disposition)
            __dataclass__object_setattr(self, 'response_content_encoding', response_content_encoding)
            __dataclass__object_setattr(self, 'response_content_language', response_content_language)
            __dataclass__object_setattr(self, 'response_content_type', response_content_type)
            __dataclass__object_setattr(self, 'response_expires', response_expires)
            __dataclass__object_setattr(self, 'version_id', version_id)
            __dataclass__object_setattr(self, 'sse_customer_algorithm', sse_customer_algorithm)
            __dataclass__object_setattr(self, 'sse_customer_key', sse_customer_key)
            __dataclass__object_setattr(self, 'sse_customer_key_md5', sse_customer_key_md5)
            __dataclass__object_setattr(self, 'request_payer', request_payer)
            __dataclass__object_setattr(self, 'part_number', part_number)
            __dataclass__object_setattr(self, 'expected_bucket_owner', expected_bucket_owner)
            __dataclass__object_setattr(self, 'checksum_mode', checksum_mode)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"bucket={self.bucket!r}")
            parts.append(f"if_match={self.if_match!r}")
            parts.append(f"if_modified_since={self.if_modified_since!r}")
            parts.append(f"if_none_match={self.if_none_match!r}")
            parts.append(f"if_unmodified_since={self.if_unmodified_since!r}")
            parts.append(f"key={self.key!r}")
            parts.append(f"range={self.range!r}")
            parts.append(f"response_cache_control={self.response_cache_control!r}")
            parts.append(f"response_content_disposition={self.response_content_disposition!r}")
            parts.append(f"response_content_encoding={self.response_content_encoding!r}")
            parts.append(f"response_content_language={self.response_content_language!r}")
            parts.append(f"response_content_type={self.response_content_type!r}")
            parts.append(f"response_expires={self.response_expires!r}")
            parts.append(f"version_id={self.version_id!r}")
            parts.append(f"sse_customer_algorithm={self.sse_customer_algorithm!r}")
            parts.append(f"sse_customer_key={self.sse_customer_key!r}")
            parts.append(f"sse_customer_key_md5={self.sse_customer_key_md5!r}")
            parts.append(f"request_payer={self.request_payer!r}")
            parts.append(f"part_number={self.part_number!r}")
            parts.append(f"expected_bucket_owner={self.expected_bucket_owner!r}")
            parts.append(f"checksum_mode={self.checksum_mode!r}")
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
        "Plans(tup=(CopyPlan(fields=('storage_class', 'access_tier')), EqPlan(fields=('storage_class', 'access_tier')),"
        " FrozenPlan(fields=('__shape__', 'storage_class', 'access_tier'), allow_dynamic_dunder_attrs=False), HashPlan("
        "action='add', fields=('storage_class', 'access_tier'), cache=False), InitPlan(fields=(InitPlan.Field(name='__s"
        "hape__', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, ove"
        "rride=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name"
        "='storage_class', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default"
        "'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None"
        ", check_type=None), InitPlan.Field(name='access_tier', annotation=OpRef(name='init.fields.2.annotation'), defa"
        "ult=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType"
        ".INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('s"
        "torage_class', 'access_tier'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()),"
        " ReprPlan(fields=(ReprPlan.Field(name='storage_class', kw_only=True, fn=None), ReprPlan.Field(name='access_tie"
        "r', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='6e1556eb8f47a5fb63c82d958b0cc397873f9549',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.s3', 'InvalidObjectState'),
    ),
)
def _process_dataclass__6e1556eb8f47a5fb63c82d958b0cc397873f9549():
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
                storage_class=self.storage_class,
                access_tier=self.access_tier,
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
                self.storage_class == other.storage_class and
                self.access_tier == other.access_tier
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'storage_class',
            'access_tier',
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
            'storage_class',
            'access_tier',
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
                self.storage_class,
                self.access_tier,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            storage_class: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            access_tier: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'storage_class', storage_class)
            __dataclass__object_setattr(self, 'access_tier', access_tier)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"storage_class={self.storage_class!r}")
            parts.append(f"access_tier={self.access_tier!r}")
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
        "Plans(tup=(CopyPlan(fields=('buckets', 'owner', 'continuation_token', 'prefix')), EqPlan(fields=('buckets', 'o"
        "wner', 'continuation_token', 'prefix')), FrozenPlan(fields=('__shape__', 'buckets', 'owner', 'continuation_tok"
        "en', 'prefix'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('buckets', 'owner', 'continu"
        "ation_token', 'prefix'), cache=False), InitPlan(fields=(InitPlan.Field(name='__shape__', annotation=OpRef(name"
        "='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldT"
        "ype.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='buckets', annotation=OpRef(n"
        "ame='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True,"
        " override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(n"
        "ame='owner', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), d"
        "efault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, che"
        "ck_type=None), InitPlan.Field(name='continuation_token', annotation=OpRef(name='init.fields.3.annotation'), de"
        "fault=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldTy"
        "pe.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='prefix', annotation=OpRef(name"
        "='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, ov"
        "erride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self',"
        " std_params=(), kw_only_params=('buckets', 'owner', 'continuation_token', 'prefix'), frozen=True, slots=False,"
        " post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='buckets', kw_only"
        "=True, fn=None), ReprPlan.Field(name='owner', kw_only=True, fn=None), ReprPlan.Field(name='continuation_token'"
        ", kw_only=True, fn=None), ReprPlan.Field(name='prefix', kw_only=True, fn=None)), id=False, terse=False, defaul"
        "t_fn=None)))"
    ),
    plan_repr_sha1='49305ebba61e91e8f6d7f880182941b9410aa17a',
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
        ('ominfra.clouds.aws.models.services.s3', 'ListBucketsOutput'),
    ),
)
def _process_dataclass__49305ebba61e91e8f6d7f880182941b9410aa17a():
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
                buckets=self.buckets,
                owner=self.owner,
                continuation_token=self.continuation_token,
                prefix=self.prefix,
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
                self.buckets == other.buckets and
                self.owner == other.owner and
                self.continuation_token == other.continuation_token and
                self.prefix == other.prefix
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'buckets',
            'owner',
            'continuation_token',
            'prefix',
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
            'buckets',
            'owner',
            'continuation_token',
            'prefix',
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
                self.buckets,
                self.owner,
                self.continuation_token,
                self.prefix,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            buckets: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            owner: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            continuation_token: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            prefix: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'buckets', buckets)
            __dataclass__object_setattr(self, 'owner', owner)
            __dataclass__object_setattr(self, 'continuation_token', continuation_token)
            __dataclass__object_setattr(self, 'prefix', prefix)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"buckets={self.buckets!r}")
            parts.append(f"owner={self.owner!r}")
            parts.append(f"continuation_token={self.continuation_token!r}")
            parts.append(f"prefix={self.prefix!r}")
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
        "Plans(tup=(CopyPlan(fields=('max_buckets', 'continuation_token', 'prefix', 'bucket_region')), EqPlan(fields=('"
        "max_buckets', 'continuation_token', 'prefix', 'bucket_region')), FrozenPlan(fields=('__shape__', 'max_buckets'"
        ", 'continuation_token', 'prefix', 'bucket_region'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', "
        "fields=('max_buckets', 'continuation_token', 'prefix', 'bucket_region'), cache=False), InitPlan(fields=(InitPl"
        "an.Field(name='__shape__', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=No"
        "ne, init=True, override=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), I"
        "nitPlan.Field(name='max_buckets', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init."
        "fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=Non"
        "e, validate=None, check_type=None), InitPlan.Field(name='continuation_token', annotation=OpRef(name='init.fiel"
        "ds.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=Fals"
        "e, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='prefix', "
        "annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factor"
        "y=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)"
        ", InitPlan.Field(name='bucket_region', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='"
        "init.fields.4.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerc"
        "e=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('max_buckets', 'co"
        "ntinuation_token', 'prefix', 'bucket_region'), frozen=True, slots=False, post_init_params=None, init_fns=(), v"
        "alidate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='max_buckets', kw_only=True, fn=None), ReprPlan.Field(na"
        "me='continuation_token', kw_only=True, fn=None), ReprPlan.Field(name='prefix', kw_only=True, fn=None), ReprPla"
        "n.Field(name='bucket_region', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='827685e3cb57e47f66486205586cef97c9a0dd1a',
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
        ('ominfra.clouds.aws.models.services.s3', 'ListBucketsRequest'),
    ),
)
def _process_dataclass__827685e3cb57e47f66486205586cef97c9a0dd1a():
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
                max_buckets=self.max_buckets,
                continuation_token=self.continuation_token,
                prefix=self.prefix,
                bucket_region=self.bucket_region,
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
                self.max_buckets == other.max_buckets and
                self.continuation_token == other.continuation_token and
                self.prefix == other.prefix and
                self.bucket_region == other.bucket_region
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'max_buckets',
            'continuation_token',
            'prefix',
            'bucket_region',
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
            'max_buckets',
            'continuation_token',
            'prefix',
            'bucket_region',
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
                self.max_buckets,
                self.continuation_token,
                self.prefix,
                self.bucket_region,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            max_buckets: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            continuation_token: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            prefix: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            bucket_region: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'max_buckets', max_buckets)
            __dataclass__object_setattr(self, 'continuation_token', continuation_token)
            __dataclass__object_setattr(self, 'prefix', prefix)
            __dataclass__object_setattr(self, 'bucket_region', bucket_region)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"max_buckets={self.max_buckets!r}")
            parts.append(f"continuation_token={self.continuation_token!r}")
            parts.append(f"prefix={self.prefix!r}")
            parts.append(f"bucket_region={self.bucket_region!r}")
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
        "Plans(tup=(CopyPlan(fields=('is_truncated', 'contents', 'name', 'prefix', 'delimiter', 'max_keys', 'common_pre"
        "fixes', 'encoding_type', 'key_count', 'continuation_token', 'next_continuation_token', 'start_after', 'request"
        "_charged')), EqPlan(fields=('is_truncated', 'contents', 'name', 'prefix', 'delimiter', 'max_keys', 'common_pre"
        "fixes', 'encoding_type', 'key_count', 'continuation_token', 'next_continuation_token', 'start_after', 'request"
        "_charged')), FrozenPlan(fields=('__shape__', 'is_truncated', 'contents', 'name', 'prefix', 'delimiter', 'max_k"
        "eys', 'common_prefixes', 'encoding_type', 'key_count', 'continuation_token', 'next_continuation_token', 'start"
        "_after', 'request_charged'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('is_truncated',"
        " 'contents', 'name', 'prefix', 'delimiter', 'max_keys', 'common_prefixes', 'encoding_type', 'key_count', 'cont"
        "inuation_token', 'next_continuation_token', 'start_after', 'request_charged'), cache=False), InitPlan(fields=("
        "InitPlan.Field(name='__shape__', annotation=OpRef(name='init.fields.00.annotation'), default=None, default_fac"
        "tory=None, init=True, override=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=N"
        "one), InitPlan.Field(name='is_truncated', annotation=OpRef(name='init.fields.01.annotation'), default=OpRef(na"
        "me='init.fields.01.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, "
        "coerce=None, validate=None, check_type=None), InitPlan.Field(name='contents', annotation=OpRef(name='init.fiel"
        "ds.02.annotation'), default=OpRef(name='init.fields.02.default'), default_factory=None, init=True, override=Fa"
        "lse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='name', "
        "annotation=OpRef(name='init.fields.03.annotation'), default=OpRef(name='init.fields.03.default'), default_fact"
        "ory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=Non"
        "e), InitPlan.Field(name='prefix', annotation=OpRef(name='init.fields.04.annotation'), default=OpRef(name='init"
        ".fields.04.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=N"
        "one, validate=None, check_type=None), InitPlan.Field(name='delimiter', annotation=OpRef(name='init.fields.05.a"
        "nnotation'), default=OpRef(name='init.fields.05.default'), default_factory=None, init=True, override=False, fi"
        "eld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='max_keys', ann"
        "otation=OpRef(name='init.fields.06.annotation'), default=OpRef(name='init.fields.06.default'), default_factory"
        "=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),"
        " InitPlan.Field(name='common_prefixes', annotation=OpRef(name='init.fields.07.annotation'), default=OpRef(name"
        "='init.fields.07.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, co"
        "erce=None, validate=None, check_type=None), InitPlan.Field(name='encoding_type', annotation=OpRef(name='init.f"
        "ields.08.annotation'), default=OpRef(name='init.fields.08.default'), default_factory=None, init=True, override"
        "=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='key_"
        "count', annotation=OpRef(name='init.fields.09.annotation'), default=OpRef(name='init.fields.09.default'), defa"
        "ult_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_"
        "type=None), InitPlan.Field(name='continuation_token', annotation=OpRef(name='init.fields.10.annotation'), defa"
        "ult=OpRef(name='init.fields.10.default'), default_factory=None, init=True, override=False, field_type=FieldTyp"
        "e.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='next_continuation_token', annot"
        "ation=OpRef(name='init.fields.11.annotation'), default=OpRef(name='init.fields.11.default'), default_factory=N"
        "one, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), I"
        "nitPlan.Field(name='start_after', annotation=OpRef(name='init.fields.12.annotation'), default=OpRef(name='init"
        ".fields.12.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=N"
        "one, validate=None, check_type=None), InitPlan.Field(name='request_charged', annotation=OpRef(name='init.field"
        "s.13.annotation'), default=OpRef(name='init.fields.13.default'), default_factory=None, init=True, override=Fal"
        "se, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_param"
        "s=(), kw_only_params=('is_truncated', 'contents', 'name', 'prefix', 'delimiter', 'max_keys', 'common_prefixes'"
        ", 'encoding_type', 'key_count', 'continuation_token', 'next_continuation_token', 'start_after', 'request_charg"
        "ed'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPla"
        "n.Field(name='is_truncated', kw_only=True, fn=None), ReprPlan.Field(name='contents', kw_only=True, fn=None), R"
        "eprPlan.Field(name='name', kw_only=True, fn=None), ReprPlan.Field(name='prefix', kw_only=True, fn=None), ReprP"
        "lan.Field(name='delimiter', kw_only=True, fn=None), ReprPlan.Field(name='max_keys', kw_only=True, fn=None), Re"
        "prPlan.Field(name='common_prefixes', kw_only=True, fn=None), ReprPlan.Field(name='encoding_type', kw_only=True"
        ", fn=None), ReprPlan.Field(name='key_count', kw_only=True, fn=None), ReprPlan.Field(name='continuation_token',"
        " kw_only=True, fn=None), ReprPlan.Field(name='next_continuation_token', kw_only=True, fn=None), ReprPlan.Field"
        "(name='start_after', kw_only=True, fn=None), ReprPlan.Field(name='request_charged', kw_only=True, fn=None)), i"
        "d=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='84542b778f11e789e004de1debef5dbc46929fc1',
    op_ref_idents=(
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
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.s3', 'ListObjectsV2Output'),
    ),
)
def _process_dataclass__84542b778f11e789e004de1debef5dbc46929fc1():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
                is_truncated=self.is_truncated,
                contents=self.contents,
                name=self.name,
                prefix=self.prefix,
                delimiter=self.delimiter,
                max_keys=self.max_keys,
                common_prefixes=self.common_prefixes,
                encoding_type=self.encoding_type,
                key_count=self.key_count,
                continuation_token=self.continuation_token,
                next_continuation_token=self.next_continuation_token,
                start_after=self.start_after,
                request_charged=self.request_charged,
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
                self.is_truncated == other.is_truncated and
                self.contents == other.contents and
                self.name == other.name and
                self.prefix == other.prefix and
                self.delimiter == other.delimiter and
                self.max_keys == other.max_keys and
                self.common_prefixes == other.common_prefixes and
                self.encoding_type == other.encoding_type and
                self.key_count == other.key_count and
                self.continuation_token == other.continuation_token and
                self.next_continuation_token == other.next_continuation_token and
                self.start_after == other.start_after and
                self.request_charged == other.request_charged
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'is_truncated',
            'contents',
            'name',
            'prefix',
            'delimiter',
            'max_keys',
            'common_prefixes',
            'encoding_type',
            'key_count',
            'continuation_token',
            'next_continuation_token',
            'start_after',
            'request_charged',
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
            'is_truncated',
            'contents',
            'name',
            'prefix',
            'delimiter',
            'max_keys',
            'common_prefixes',
            'encoding_type',
            'key_count',
            'continuation_token',
            'next_continuation_token',
            'start_after',
            'request_charged',
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
                self.is_truncated,
                self.contents,
                self.name,
                self.prefix,
                self.delimiter,
                self.max_keys,
                self.common_prefixes,
                self.encoding_type,
                self.key_count,
                self.continuation_token,
                self.next_continuation_token,
                self.start_after,
                self.request_charged,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            is_truncated: __dataclass__init__fields__01__annotation = __dataclass__init__fields__01__default,
            contents: __dataclass__init__fields__02__annotation = __dataclass__init__fields__02__default,
            name: __dataclass__init__fields__03__annotation = __dataclass__init__fields__03__default,
            prefix: __dataclass__init__fields__04__annotation = __dataclass__init__fields__04__default,
            delimiter: __dataclass__init__fields__05__annotation = __dataclass__init__fields__05__default,
            max_keys: __dataclass__init__fields__06__annotation = __dataclass__init__fields__06__default,
            common_prefixes: __dataclass__init__fields__07__annotation = __dataclass__init__fields__07__default,
            encoding_type: __dataclass__init__fields__08__annotation = __dataclass__init__fields__08__default,
            key_count: __dataclass__init__fields__09__annotation = __dataclass__init__fields__09__default,
            continuation_token: __dataclass__init__fields__10__annotation = __dataclass__init__fields__10__default,
            next_continuation_token: __dataclass__init__fields__11__annotation = __dataclass__init__fields__11__default,
            start_after: __dataclass__init__fields__12__annotation = __dataclass__init__fields__12__default,
            request_charged: __dataclass__init__fields__13__annotation = __dataclass__init__fields__13__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'is_truncated', is_truncated)
            __dataclass__object_setattr(self, 'contents', contents)
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'prefix', prefix)
            __dataclass__object_setattr(self, 'delimiter', delimiter)
            __dataclass__object_setattr(self, 'max_keys', max_keys)
            __dataclass__object_setattr(self, 'common_prefixes', common_prefixes)
            __dataclass__object_setattr(self, 'encoding_type', encoding_type)
            __dataclass__object_setattr(self, 'key_count', key_count)
            __dataclass__object_setattr(self, 'continuation_token', continuation_token)
            __dataclass__object_setattr(self, 'next_continuation_token', next_continuation_token)
            __dataclass__object_setattr(self, 'start_after', start_after)
            __dataclass__object_setattr(self, 'request_charged', request_charged)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"is_truncated={self.is_truncated!r}")
            parts.append(f"contents={self.contents!r}")
            parts.append(f"name={self.name!r}")
            parts.append(f"prefix={self.prefix!r}")
            parts.append(f"delimiter={self.delimiter!r}")
            parts.append(f"max_keys={self.max_keys!r}")
            parts.append(f"common_prefixes={self.common_prefixes!r}")
            parts.append(f"encoding_type={self.encoding_type!r}")
            parts.append(f"key_count={self.key_count!r}")
            parts.append(f"continuation_token={self.continuation_token!r}")
            parts.append(f"next_continuation_token={self.next_continuation_token!r}")
            parts.append(f"start_after={self.start_after!r}")
            parts.append(f"request_charged={self.request_charged!r}")
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
        "Plans(tup=(CopyPlan(fields=('bucket', 'delimiter', 'encoding_type', 'max_keys', 'prefix', 'continuation_token'"
        ", 'fetch_owner', 'start_after', 'request_payer', 'expected_bucket_owner', 'optional_object_attributes')), EqPl"
        "an(fields=('bucket', 'delimiter', 'encoding_type', 'max_keys', 'prefix', 'continuation_token', 'fetch_owner', "
        "'start_after', 'request_payer', 'expected_bucket_owner', 'optional_object_attributes')), FrozenPlan(fields=('_"
        "_shape__', 'bucket', 'delimiter', 'encoding_type', 'max_keys', 'prefix', 'continuation_token', 'fetch_owner', "
        "'start_after', 'request_payer', 'expected_bucket_owner', 'optional_object_attributes'), allow_dynamic_dunder_a"
        "ttrs=False), HashPlan(action='add', fields=('bucket', 'delimiter', 'encoding_type', 'max_keys', 'prefix', 'con"
        "tinuation_token', 'fetch_owner', 'start_after', 'request_payer', 'expected_bucket_owner', 'optional_object_att"
        "ributes'), cache=False), InitPlan(fields=(InitPlan.Field(name='__shape__', annotation=OpRef(name='init.fields."
        "00.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS_VAR"
        ", coerce=None, validate=None, check_type=None), InitPlan.Field(name='bucket', annotation=OpRef(name='init.fiel"
        "ds.01.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTAN"
        "CE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='delimiter', annotation=OpRef(name='init"
        ".fields.02.annotation'), default=OpRef(name='init.fields.02.default'), default_factory=None, init=True, overri"
        "de=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='en"
        "coding_type', annotation=OpRef(name='init.fields.03.annotation'), default=OpRef(name='init.fields.03.default')"
        ", default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, "
        "check_type=None), InitPlan.Field(name='max_keys', annotation=OpRef(name='init.fields.04.annotation'), default="
        "OpRef(name='init.fields.04.default'), default_factory=None, init=True, override=False, field_type=FieldType.IN"
        "STANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='prefix', annotation=OpRef(name='ini"
        "t.fields.05.annotation'), default=OpRef(name='init.fields.05.default'), default_factory=None, init=True, overr"
        "ide=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='c"
        "ontinuation_token', annotation=OpRef(name='init.fields.06.annotation'), default=OpRef(name='init.fields.06.def"
        "ault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate="
        "None, check_type=None), InitPlan.Field(name='fetch_owner', annotation=OpRef(name='init.fields.07.annotation'),"
        " default=OpRef(name='init.fields.07.default'), default_factory=None, init=True, override=False, field_type=Fie"
        "ldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='start_after', annotation=O"
        "pRef(name='init.fields.08.annotation'), default=OpRef(name='init.fields.08.default'), default_factory=None, in"
        "it=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan"
        ".Field(name='request_payer', annotation=OpRef(name='init.fields.09.annotation'), default=OpRef(name='init.fiel"
        "ds.09.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, "
        "validate=None, check_type=None), InitPlan.Field(name='expected_bucket_owner', annotation=OpRef(name='init.fiel"
        "ds.10.annotation'), default=OpRef(name='init.fields.10.default'), default_factory=None, init=True, override=Fa"
        "lse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='optiona"
        "l_object_attributes', annotation=OpRef(name='init.fields.11.annotation'), default=OpRef(name='init.fields.11.d"
        "efault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validat"
        "e=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('bucket', 'delimiter', 'encoding_"
        "type', 'max_keys', 'prefix', 'continuation_token', 'fetch_owner', 'start_after', 'request_payer', 'expected_bu"
        "cket_owner', 'optional_object_attributes'), frozen=True, slots=False, post_init_params=None, init_fns=(), vali"
        "date_fns=()), ReprPlan(fields=(ReprPlan.Field(name='bucket', kw_only=True, fn=None), ReprPlan.Field(name='deli"
        "miter', kw_only=True, fn=None), ReprPlan.Field(name='encoding_type', kw_only=True, fn=None), ReprPlan.Field(na"
        "me='max_keys', kw_only=True, fn=None), ReprPlan.Field(name='prefix', kw_only=True, fn=None), ReprPlan.Field(na"
        "me='continuation_token', kw_only=True, fn=None), ReprPlan.Field(name='fetch_owner', kw_only=True, fn=None), Re"
        "prPlan.Field(name='start_after', kw_only=True, fn=None), ReprPlan.Field(name='request_payer', kw_only=True, fn"
        "=None), ReprPlan.Field(name='expected_bucket_owner', kw_only=True, fn=None), ReprPlan.Field(name='optional_obj"
        "ect_attributes', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='ac3fbcb0bf51cc5424964d515ad683216088ec20',
    op_ref_idents=(
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
        '__dataclass__init__fields__11__annotation',
        '__dataclass__init__fields__11__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.s3', 'ListObjectsV2Request'),
    ),
)
def _process_dataclass__ac3fbcb0bf51cc5424964d515ad683216088ec20():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
        __dataclass__init__fields__11__annotation,
        __dataclass__init__fields__11__default,
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
                bucket=self.bucket,
                delimiter=self.delimiter,
                encoding_type=self.encoding_type,
                max_keys=self.max_keys,
                prefix=self.prefix,
                continuation_token=self.continuation_token,
                fetch_owner=self.fetch_owner,
                start_after=self.start_after,
                request_payer=self.request_payer,
                expected_bucket_owner=self.expected_bucket_owner,
                optional_object_attributes=self.optional_object_attributes,
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
                self.bucket == other.bucket and
                self.delimiter == other.delimiter and
                self.encoding_type == other.encoding_type and
                self.max_keys == other.max_keys and
                self.prefix == other.prefix and
                self.continuation_token == other.continuation_token and
                self.fetch_owner == other.fetch_owner and
                self.start_after == other.start_after and
                self.request_payer == other.request_payer and
                self.expected_bucket_owner == other.expected_bucket_owner and
                self.optional_object_attributes == other.optional_object_attributes
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'bucket',
            'delimiter',
            'encoding_type',
            'max_keys',
            'prefix',
            'continuation_token',
            'fetch_owner',
            'start_after',
            'request_payer',
            'expected_bucket_owner',
            'optional_object_attributes',
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
            'bucket',
            'delimiter',
            'encoding_type',
            'max_keys',
            'prefix',
            'continuation_token',
            'fetch_owner',
            'start_after',
            'request_payer',
            'expected_bucket_owner',
            'optional_object_attributes',
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
                self.bucket,
                self.delimiter,
                self.encoding_type,
                self.max_keys,
                self.prefix,
                self.continuation_token,
                self.fetch_owner,
                self.start_after,
                self.request_payer,
                self.expected_bucket_owner,
                self.optional_object_attributes,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            bucket: __dataclass__init__fields__01__annotation,
            delimiter: __dataclass__init__fields__02__annotation = __dataclass__init__fields__02__default,
            encoding_type: __dataclass__init__fields__03__annotation = __dataclass__init__fields__03__default,
            max_keys: __dataclass__init__fields__04__annotation = __dataclass__init__fields__04__default,
            prefix: __dataclass__init__fields__05__annotation = __dataclass__init__fields__05__default,
            continuation_token: __dataclass__init__fields__06__annotation = __dataclass__init__fields__06__default,
            fetch_owner: __dataclass__init__fields__07__annotation = __dataclass__init__fields__07__default,
            start_after: __dataclass__init__fields__08__annotation = __dataclass__init__fields__08__default,
            request_payer: __dataclass__init__fields__09__annotation = __dataclass__init__fields__09__default,
            expected_bucket_owner: __dataclass__init__fields__10__annotation = __dataclass__init__fields__10__default,
            optional_object_attributes: __dataclass__init__fields__11__annotation = __dataclass__init__fields__11__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'bucket', bucket)
            __dataclass__object_setattr(self, 'delimiter', delimiter)
            __dataclass__object_setattr(self, 'encoding_type', encoding_type)
            __dataclass__object_setattr(self, 'max_keys', max_keys)
            __dataclass__object_setattr(self, 'prefix', prefix)
            __dataclass__object_setattr(self, 'continuation_token', continuation_token)
            __dataclass__object_setattr(self, 'fetch_owner', fetch_owner)
            __dataclass__object_setattr(self, 'start_after', start_after)
            __dataclass__object_setattr(self, 'request_payer', request_payer)
            __dataclass__object_setattr(self, 'expected_bucket_owner', expected_bucket_owner)
            __dataclass__object_setattr(self, 'optional_object_attributes', optional_object_attributes)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"bucket={self.bucket!r}")
            parts.append(f"delimiter={self.delimiter!r}")
            parts.append(f"encoding_type={self.encoding_type!r}")
            parts.append(f"max_keys={self.max_keys!r}")
            parts.append(f"prefix={self.prefix!r}")
            parts.append(f"continuation_token={self.continuation_token!r}")
            parts.append(f"fetch_owner={self.fetch_owner!r}")
            parts.append(f"start_after={self.start_after!r}")
            parts.append(f"request_payer={self.request_payer!r}")
            parts.append(f"expected_bucket_owner={self.expected_bucket_owner!r}")
            parts.append(f"optional_object_attributes={self.optional_object_attributes!r}")
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
        "Plans(tup=(CopyPlan(fields=('key', 'last_modified', 'etag', 'checksum_algorithm', 'checksum_type', 'size', 'st"
        "orage_class', 'owner', 'restore_status')), EqPlan(fields=('key', 'last_modified', 'etag', 'checksum_algorithm'"
        ", 'checksum_type', 'size', 'storage_class', 'owner', 'restore_status')), FrozenPlan(fields=('__shape__', 'key'"
        ", 'last_modified', 'etag', 'checksum_algorithm', 'checksum_type', 'size', 'storage_class', 'owner', 'restore_s"
        "tatus'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('key', 'last_modified', 'etag', 'ch"
        "ecksum_algorithm', 'checksum_type', 'size', 'storage_class', 'owner', 'restore_status'), cache=False), InitPla"
        "n(fields=(InitPlan.Field(name='__shape__', annotation=OpRef(name='init.fields.00.annotation'), default=None, d"
        "efault_factory=None, init=True, override=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, ch"
        "eck_type=None), InitPlan.Field(name='key', annotation=OpRef(name='init.fields.01.annotation'), default=OpRef(n"
        "ame='init.fields.01.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE,"
        " coerce=None, validate=None, check_type=None), InitPlan.Field(name='last_modified', annotation=OpRef(name='ini"
        "t.fields.02.annotation'), default=OpRef(name='init.fields.02.default'), default_factory=None, init=True, overr"
        "ide=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='e"
        "tag', annotation=OpRef(name='init.fields.03.annotation'), default=OpRef(name='init.fields.03.default'), defaul"
        "t_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_ty"
        "pe=None), InitPlan.Field(name='checksum_algorithm', annotation=OpRef(name='init.fields.04.annotation'), defaul"
        "t=OpRef(name='init.fields.04.default'), default_factory=None, init=True, override=False, field_type=FieldType."
        "INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='checksum_type', annotation=OpRef("
        "name='init.fields.05.annotation'), default=OpRef(name='init.fields.05.default'), default_factory=None, init=Tr"
        "ue, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fiel"
        "d(name='size', annotation=OpRef(name='init.fields.06.annotation'), default=OpRef(name='init.fields.06.default'"
        "), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None,"
        " check_type=None), InitPlan.Field(name='storage_class', annotation=OpRef(name='init.fields.07.annotation'), de"
        "fault=OpRef(name='init.fields.07.default'), default_factory=None, init=True, override=False, field_type=FieldT"
        "ype.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='owner', annotation=OpRef(name"
        "='init.fields.08.annotation'), default=OpRef(name='init.fields.08.default'), default_factory=None, init=True, "
        "override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(na"
        "me='restore_status', annotation=OpRef(name='init.fields.09.annotation'), default=OpRef(name='init.fields.09.de"
        "fault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate"
        "=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('key', 'last_modified', 'etag', 'c"
        "hecksum_algorithm', 'checksum_type', 'size', 'storage_class', 'owner', 'restore_status'), frozen=True, slots=F"
        "alse, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='key', kw_onl"
        "y=True, fn=None), ReprPlan.Field(name='last_modified', kw_only=True, fn=None), ReprPlan.Field(name='etag', kw_"
        "only=True, fn=None), ReprPlan.Field(name='checksum_algorithm', kw_only=True, fn=None), ReprPlan.Field(name='ch"
        "ecksum_type', kw_only=True, fn=None), ReprPlan.Field(name='size', kw_only=True, fn=None), ReprPlan.Field(name="
        "'storage_class', kw_only=True, fn=None), ReprPlan.Field(name='owner', kw_only=True, fn=None), ReprPlan.Field(n"
        "ame='restore_status', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='59c9c5c8f5c3676da55e9bd6b688774c2f9aeddf',
    op_ref_idents=(
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
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.s3', 'Object'),
    ),
)
def _process_dataclass__59c9c5c8f5c3676da55e9bd6b688774c2f9aeddf():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
                last_modified=self.last_modified,
                etag=self.etag,
                checksum_algorithm=self.checksum_algorithm,
                checksum_type=self.checksum_type,
                size=self.size,
                storage_class=self.storage_class,
                owner=self.owner,
                restore_status=self.restore_status,
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
                self.last_modified == other.last_modified and
                self.etag == other.etag and
                self.checksum_algorithm == other.checksum_algorithm and
                self.checksum_type == other.checksum_type and
                self.size == other.size and
                self.storage_class == other.storage_class and
                self.owner == other.owner and
                self.restore_status == other.restore_status
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'key',
            'last_modified',
            'etag',
            'checksum_algorithm',
            'checksum_type',
            'size',
            'storage_class',
            'owner',
            'restore_status',
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
            'key',
            'last_modified',
            'etag',
            'checksum_algorithm',
            'checksum_type',
            'size',
            'storage_class',
            'owner',
            'restore_status',
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
                self.last_modified,
                self.etag,
                self.checksum_algorithm,
                self.checksum_type,
                self.size,
                self.storage_class,
                self.owner,
                self.restore_status,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            key: __dataclass__init__fields__01__annotation = __dataclass__init__fields__01__default,
            last_modified: __dataclass__init__fields__02__annotation = __dataclass__init__fields__02__default,
            etag: __dataclass__init__fields__03__annotation = __dataclass__init__fields__03__default,
            checksum_algorithm: __dataclass__init__fields__04__annotation = __dataclass__init__fields__04__default,
            checksum_type: __dataclass__init__fields__05__annotation = __dataclass__init__fields__05__default,
            size: __dataclass__init__fields__06__annotation = __dataclass__init__fields__06__default,
            storage_class: __dataclass__init__fields__07__annotation = __dataclass__init__fields__07__default,
            owner: __dataclass__init__fields__08__annotation = __dataclass__init__fields__08__default,
            restore_status: __dataclass__init__fields__09__annotation = __dataclass__init__fields__09__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'key', key)
            __dataclass__object_setattr(self, 'last_modified', last_modified)
            __dataclass__object_setattr(self, 'etag', etag)
            __dataclass__object_setattr(self, 'checksum_algorithm', checksum_algorithm)
            __dataclass__object_setattr(self, 'checksum_type', checksum_type)
            __dataclass__object_setattr(self, 'size', size)
            __dataclass__object_setattr(self, 'storage_class', storage_class)
            __dataclass__object_setattr(self, 'owner', owner)
            __dataclass__object_setattr(self, 'restore_status', restore_status)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"key={self.key!r}")
            parts.append(f"last_modified={self.last_modified!r}")
            parts.append(f"etag={self.etag!r}")
            parts.append(f"checksum_algorithm={self.checksum_algorithm!r}")
            parts.append(f"checksum_type={self.checksum_type!r}")
            parts.append(f"size={self.size!r}")
            parts.append(f"storage_class={self.storage_class!r}")
            parts.append(f"owner={self.owner!r}")
            parts.append(f"restore_status={self.restore_status!r}")
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
        "Plans(tup=(CopyPlan(fields=('display_name', 'i_d')), EqPlan(fields=('display_name', 'i_d')), FrozenPlan(fields"
        "=('__shape__', 'display_name', 'i_d'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('disp"
        "lay_name', 'i_d'), cache=False), InitPlan(fields=(InitPlan.Field(name='__shape__', annotation=OpRef(name='init"
        ".fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CL"
        "ASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='display_name', annotation=OpRef(na"
        "me='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, "
        "override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(na"
        "me='i_d', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), defa"
        "ult_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_"
        "type=None)), self_param='self', std_params=(), kw_only_params=('display_name', 'i_d'), frozen=True, slots=Fals"
        "e, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='display_name', "
        "kw_only=True, fn=None), ReprPlan.Field(name='i_d', kw_only=True, fn=None)), id=False, terse=False, default_fn="
        "None)))"
    ),
    plan_repr_sha1='406cda8dbd315809e1f63f385601152edbb21e83',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.s3', 'Owner'),
    ),
)
def _process_dataclass__406cda8dbd315809e1f63f385601152edbb21e83():
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
                display_name=self.display_name,
                i_d=self.i_d,
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
                self.display_name == other.display_name and
                self.i_d == other.i_d
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'display_name',
            'i_d',
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
            'display_name',
            'i_d',
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
                self.display_name,
                self.i_d,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            display_name: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            i_d: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'display_name', display_name)
            __dataclass__object_setattr(self, 'i_d', i_d)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"display_name={self.display_name!r}")
            parts.append(f"i_d={self.i_d!r}")
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
        "Plans(tup=(CopyPlan(fields=('expiration', 'etag', 'checksum_crc32', 'checksum_crc32c', 'checksum_crc64nvme', '"
        "checksum_sha1', 'checksum_sha256', 'checksum_sha512', 'checksum_md5', 'checksum_xxhash64', 'checksum_xxhash3',"
        " 'checksum_xxhash128', 'checksum_type', 'server_side_encryption', 'version_id', 'sse_customer_algorithm', 'sse"
        "_customer_key_md5', 'sse_kms_key_id', 'sse_kms_encryption_context', 'bucket_key_enabled', 'size', 'request_cha"
        "rged')), EqPlan(fields=('expiration', 'etag', 'checksum_crc32', 'checksum_crc32c', 'checksum_crc64nvme', 'chec"
        "ksum_sha1', 'checksum_sha256', 'checksum_sha512', 'checksum_md5', 'checksum_xxhash64', 'checksum_xxhash3', 'ch"
        "ecksum_xxhash128', 'checksum_type', 'server_side_encryption', 'version_id', 'sse_customer_algorithm', 'sse_cus"
        "tomer_key_md5', 'sse_kms_key_id', 'sse_kms_encryption_context', 'bucket_key_enabled', 'size', 'request_charged"
        "')), FrozenPlan(fields=('__shape__', 'expiration', 'etag', 'checksum_crc32', 'checksum_crc32c', 'checksum_crc6"
        "4nvme', 'checksum_sha1', 'checksum_sha256', 'checksum_sha512', 'checksum_md5', 'checksum_xxhash64', 'checksum_"
        "xxhash3', 'checksum_xxhash128', 'checksum_type', 'server_side_encryption', 'version_id', 'sse_customer_algorit"
        "hm', 'sse_customer_key_md5', 'sse_kms_key_id', 'sse_kms_encryption_context', 'bucket_key_enabled', 'size', 're"
        "quest_charged'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('expiration', 'etag', 'chec"
        "ksum_crc32', 'checksum_crc32c', 'checksum_crc64nvme', 'checksum_sha1', 'checksum_sha256', 'checksum_sha512', '"
        "checksum_md5', 'checksum_xxhash64', 'checksum_xxhash3', 'checksum_xxhash128', 'checksum_type', 'server_side_en"
        "cryption', 'version_id', 'sse_customer_algorithm', 'sse_customer_key_md5', 'sse_kms_key_id', 'sse_kms_encrypti"
        "on_context', 'bucket_key_enabled', 'size', 'request_charged'), cache=False), InitPlan(fields=(InitPlan.Field(n"
        "ame='__shape__', annotation=OpRef(name='init.fields.00.annotation'), default=None, default_factory=None, init="
        "True, override=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.F"
        "ield(name='expiration', annotation=OpRef(name='init.fields.01.annotation'), default=OpRef(name='init.fields.01"
        ".default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valid"
        "ate=None, check_type=None), InitPlan.Field(name='etag', annotation=OpRef(name='init.fields.02.annotation'), de"
        "fault=OpRef(name='init.fields.02.default'), default_factory=None, init=True, override=False, field_type=FieldT"
        "ype.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='checksum_crc32', annotation=O"
        "pRef(name='init.fields.03.annotation'), default=OpRef(name='init.fields.03.default'), default_factory=None, in"
        "it=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan"
        ".Field(name='checksum_crc32c', annotation=OpRef(name='init.fields.04.annotation'), default=OpRef(name='init.fi"
        "elds.04.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None"
        ", validate=None, check_type=None), InitPlan.Field(name='checksum_crc64nvme', annotation=OpRef(name='init.field"
        "s.05.annotation'), default=OpRef(name='init.fields.05.default'), default_factory=None, init=True, override=Fal"
        "se, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='checksum"
        "_sha1', annotation=OpRef(name='init.fields.06.annotation'), default=OpRef(name='init.fields.06.default'), defa"
        "ult_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_"
        "type=None), InitPlan.Field(name='checksum_sha256', annotation=OpRef(name='init.fields.07.annotation'), default"
        "=OpRef(name='init.fields.07.default'), default_factory=None, init=True, override=False, field_type=FieldType.I"
        "NSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='checksum_sha512', annotation=OpRef"
        "(name='init.fields.08.annotation'), default=OpRef(name='init.fields.08.default'), default_factory=None, init=T"
        "rue, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fie"
        "ld(name='checksum_md5', annotation=OpRef(name='init.fields.09.annotation'), default=OpRef(name='init.fields.09"
        ".default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valid"
        "ate=None, check_type=None), InitPlan.Field(name='checksum_xxhash64', annotation=OpRef(name='init.fields.10.ann"
        "otation'), default=OpRef(name='init.fields.10.default'), default_factory=None, init=True, override=False, fiel"
        "d_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='checksum_xxhash3"
        "', annotation=OpRef(name='init.fields.11.annotation'), default=OpRef(name='init.fields.11.default'), default_f"
        "actory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type="
        "None), InitPlan.Field(name='checksum_xxhash128', annotation=OpRef(name='init.fields.12.annotation'), default=O"
        "pRef(name='init.fields.12.default'), default_factory=None, init=True, override=False, field_type=FieldType.INS"
        "TANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='checksum_type', annotation=OpRef(nam"
        "e='init.fields.13.annotation'), default=OpRef(name='init.fields.13.default'), default_factory=None, init=True,"
        " override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(n"
        "ame='server_side_encryption', annotation=OpRef(name='init.fields.14.annotation'), default=OpRef(name='init.fie"
        "lds.14.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None,"
        " validate=None, check_type=None), InitPlan.Field(name='version_id', annotation=OpRef(name='init.fields.15.anno"
        "tation'), default=OpRef(name='init.fields.15.default'), default_factory=None, init=True, override=False, field"
        "_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='sse_customer_algo"
        "rithm', annotation=OpRef(name='init.fields.16.annotation'), default=OpRef(name='init.fields.16.default'), defa"
        "ult_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_"
        "type=None), InitPlan.Field(name='sse_customer_key_md5', annotation=OpRef(name='init.fields.17.annotation'), de"
        "fault=OpRef(name='init.fields.17.default'), default_factory=None, init=True, override=False, field_type=FieldT"
        "ype.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='sse_kms_key_id', annotation=O"
        "pRef(name='init.fields.18.annotation'), default=OpRef(name='init.fields.18.default'), default_factory=None, in"
        "it=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan"
        ".Field(name='sse_kms_encryption_context', annotation=OpRef(name='init.fields.19.annotation'), default=OpRef(na"
        "me='init.fields.19.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, "
        "coerce=None, validate=None, check_type=None), InitPlan.Field(name='bucket_key_enabled', annotation=OpRef(name="
        "'init.fields.20.annotation'), default=OpRef(name='init.fields.20.default'), default_factory=None, init=True, o"
        "verride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(nam"
        "e='size', annotation=OpRef(name='init.fields.21.annotation'), default=OpRef(name='init.fields.21.default'), de"
        "fault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, chec"
        "k_type=None), InitPlan.Field(name='request_charged', annotation=OpRef(name='init.fields.22.annotation'), defau"
        "lt=OpRef(name='init.fields.22.default'), default_factory=None, init=True, override=False, field_type=FieldType"
        ".INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('e"
        "xpiration', 'etag', 'checksum_crc32', 'checksum_crc32c', 'checksum_crc64nvme', 'checksum_sha1', 'checksum_sha2"
        "56', 'checksum_sha512', 'checksum_md5', 'checksum_xxhash64', 'checksum_xxhash3', 'checksum_xxhash128', 'checks"
        "um_type', 'server_side_encryption', 'version_id', 'sse_customer_algorithm', 'sse_customer_key_md5', 'sse_kms_k"
        "ey_id', 'sse_kms_encryption_context', 'bucket_key_enabled', 'size', 'request_charged'), frozen=True, slots=Fal"
        "se, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='expiration', k"
        "w_only=True, fn=None), ReprPlan.Field(name='etag', kw_only=True, fn=None), ReprPlan.Field(name='checksum_crc32"
        "', kw_only=True, fn=None), ReprPlan.Field(name='checksum_crc32c', kw_only=True, fn=None), ReprPlan.Field(name="
        "'checksum_crc64nvme', kw_only=True, fn=None), ReprPlan.Field(name='checksum_sha1', kw_only=True, fn=None), Rep"
        "rPlan.Field(name='checksum_sha256', kw_only=True, fn=None), ReprPlan.Field(name='checksum_sha512', kw_only=Tru"
        "e, fn=None), ReprPlan.Field(name='checksum_md5', kw_only=True, fn=None), ReprPlan.Field(name='checksum_xxhash6"
        "4', kw_only=True, fn=None), ReprPlan.Field(name='checksum_xxhash3', kw_only=True, fn=None), ReprPlan.Field(nam"
        "e='checksum_xxhash128', kw_only=True, fn=None), ReprPlan.Field(name='checksum_type', kw_only=True, fn=None), R"
        "eprPlan.Field(name='server_side_encryption', kw_only=True, fn=None), ReprPlan.Field(name='version_id', kw_only"
        "=True, fn=None), ReprPlan.Field(name='sse_customer_algorithm', kw_only=True, fn=None), ReprPlan.Field(name='ss"
        "e_customer_key_md5', kw_only=True, fn=None), ReprPlan.Field(name='sse_kms_key_id', kw_only=True, fn=None), Rep"
        "rPlan.Field(name='sse_kms_encryption_context', kw_only=True, fn=None), ReprPlan.Field(name='bucket_key_enabled"
        "', kw_only=True, fn=None), ReprPlan.Field(name='size', kw_only=True, fn=None), ReprPlan.Field(name='request_ch"
        "arged', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='4ebb688d0c3b7d7548c25489691ad4f455f83dd5',
    op_ref_idents=(
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
        '__dataclass__init__fields__18__annotation',
        '__dataclass__init__fields__18__default',
        '__dataclass__init__fields__19__annotation',
        '__dataclass__init__fields__19__default',
        '__dataclass__init__fields__20__annotation',
        '__dataclass__init__fields__20__default',
        '__dataclass__init__fields__21__annotation',
        '__dataclass__init__fields__21__default',
        '__dataclass__init__fields__22__annotation',
        '__dataclass__init__fields__22__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.s3', 'PutObjectOutput'),
    ),
)
def _process_dataclass__4ebb688d0c3b7d7548c25489691ad4f455f83dd5():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
        __dataclass__init__fields__18__annotation,
        __dataclass__init__fields__18__default,
        __dataclass__init__fields__19__annotation,
        __dataclass__init__fields__19__default,
        __dataclass__init__fields__20__annotation,
        __dataclass__init__fields__20__default,
        __dataclass__init__fields__21__annotation,
        __dataclass__init__fields__21__default,
        __dataclass__init__fields__22__annotation,
        __dataclass__init__fields__22__default,
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
                expiration=self.expiration,
                etag=self.etag,
                checksum_crc32=self.checksum_crc32,
                checksum_crc32c=self.checksum_crc32c,
                checksum_crc64nvme=self.checksum_crc64nvme,
                checksum_sha1=self.checksum_sha1,
                checksum_sha256=self.checksum_sha256,
                checksum_sha512=self.checksum_sha512,
                checksum_md5=self.checksum_md5,
                checksum_xxhash64=self.checksum_xxhash64,
                checksum_xxhash3=self.checksum_xxhash3,
                checksum_xxhash128=self.checksum_xxhash128,
                checksum_type=self.checksum_type,
                server_side_encryption=self.server_side_encryption,
                version_id=self.version_id,
                sse_customer_algorithm=self.sse_customer_algorithm,
                sse_customer_key_md5=self.sse_customer_key_md5,
                sse_kms_key_id=self.sse_kms_key_id,
                sse_kms_encryption_context=self.sse_kms_encryption_context,
                bucket_key_enabled=self.bucket_key_enabled,
                size=self.size,
                request_charged=self.request_charged,
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
                self.expiration == other.expiration and
                self.etag == other.etag and
                self.checksum_crc32 == other.checksum_crc32 and
                self.checksum_crc32c == other.checksum_crc32c and
                self.checksum_crc64nvme == other.checksum_crc64nvme and
                self.checksum_sha1 == other.checksum_sha1 and
                self.checksum_sha256 == other.checksum_sha256 and
                self.checksum_sha512 == other.checksum_sha512 and
                self.checksum_md5 == other.checksum_md5 and
                self.checksum_xxhash64 == other.checksum_xxhash64 and
                self.checksum_xxhash3 == other.checksum_xxhash3 and
                self.checksum_xxhash128 == other.checksum_xxhash128 and
                self.checksum_type == other.checksum_type and
                self.server_side_encryption == other.server_side_encryption and
                self.version_id == other.version_id and
                self.sse_customer_algorithm == other.sse_customer_algorithm and
                self.sse_customer_key_md5 == other.sse_customer_key_md5 and
                self.sse_kms_key_id == other.sse_kms_key_id and
                self.sse_kms_encryption_context == other.sse_kms_encryption_context and
                self.bucket_key_enabled == other.bucket_key_enabled and
                self.size == other.size and
                self.request_charged == other.request_charged
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'expiration',
            'etag',
            'checksum_crc32',
            'checksum_crc32c',
            'checksum_crc64nvme',
            'checksum_sha1',
            'checksum_sha256',
            'checksum_sha512',
            'checksum_md5',
            'checksum_xxhash64',
            'checksum_xxhash3',
            'checksum_xxhash128',
            'checksum_type',
            'server_side_encryption',
            'version_id',
            'sse_customer_algorithm',
            'sse_customer_key_md5',
            'sse_kms_key_id',
            'sse_kms_encryption_context',
            'bucket_key_enabled',
            'size',
            'request_charged',
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
            'expiration',
            'etag',
            'checksum_crc32',
            'checksum_crc32c',
            'checksum_crc64nvme',
            'checksum_sha1',
            'checksum_sha256',
            'checksum_sha512',
            'checksum_md5',
            'checksum_xxhash64',
            'checksum_xxhash3',
            'checksum_xxhash128',
            'checksum_type',
            'server_side_encryption',
            'version_id',
            'sse_customer_algorithm',
            'sse_customer_key_md5',
            'sse_kms_key_id',
            'sse_kms_encryption_context',
            'bucket_key_enabled',
            'size',
            'request_charged',
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
                self.expiration,
                self.etag,
                self.checksum_crc32,
                self.checksum_crc32c,
                self.checksum_crc64nvme,
                self.checksum_sha1,
                self.checksum_sha256,
                self.checksum_sha512,
                self.checksum_md5,
                self.checksum_xxhash64,
                self.checksum_xxhash3,
                self.checksum_xxhash128,
                self.checksum_type,
                self.server_side_encryption,
                self.version_id,
                self.sse_customer_algorithm,
                self.sse_customer_key_md5,
                self.sse_kms_key_id,
                self.sse_kms_encryption_context,
                self.bucket_key_enabled,
                self.size,
                self.request_charged,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            expiration: __dataclass__init__fields__01__annotation = __dataclass__init__fields__01__default,
            etag: __dataclass__init__fields__02__annotation = __dataclass__init__fields__02__default,
            checksum_crc32: __dataclass__init__fields__03__annotation = __dataclass__init__fields__03__default,
            checksum_crc32c: __dataclass__init__fields__04__annotation = __dataclass__init__fields__04__default,
            checksum_crc64nvme: __dataclass__init__fields__05__annotation = __dataclass__init__fields__05__default,
            checksum_sha1: __dataclass__init__fields__06__annotation = __dataclass__init__fields__06__default,
            checksum_sha256: __dataclass__init__fields__07__annotation = __dataclass__init__fields__07__default,
            checksum_sha512: __dataclass__init__fields__08__annotation = __dataclass__init__fields__08__default,
            checksum_md5: __dataclass__init__fields__09__annotation = __dataclass__init__fields__09__default,
            checksum_xxhash64: __dataclass__init__fields__10__annotation = __dataclass__init__fields__10__default,
            checksum_xxhash3: __dataclass__init__fields__11__annotation = __dataclass__init__fields__11__default,
            checksum_xxhash128: __dataclass__init__fields__12__annotation = __dataclass__init__fields__12__default,
            checksum_type: __dataclass__init__fields__13__annotation = __dataclass__init__fields__13__default,
            server_side_encryption: __dataclass__init__fields__14__annotation = __dataclass__init__fields__14__default,
            version_id: __dataclass__init__fields__15__annotation = __dataclass__init__fields__15__default,
            sse_customer_algorithm: __dataclass__init__fields__16__annotation = __dataclass__init__fields__16__default,
            sse_customer_key_md5: __dataclass__init__fields__17__annotation = __dataclass__init__fields__17__default,
            sse_kms_key_id: __dataclass__init__fields__18__annotation = __dataclass__init__fields__18__default,
            sse_kms_encryption_context: __dataclass__init__fields__19__annotation = __dataclass__init__fields__19__default,
            bucket_key_enabled: __dataclass__init__fields__20__annotation = __dataclass__init__fields__20__default,
            size: __dataclass__init__fields__21__annotation = __dataclass__init__fields__21__default,
            request_charged: __dataclass__init__fields__22__annotation = __dataclass__init__fields__22__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'expiration', expiration)
            __dataclass__object_setattr(self, 'etag', etag)
            __dataclass__object_setattr(self, 'checksum_crc32', checksum_crc32)
            __dataclass__object_setattr(self, 'checksum_crc32c', checksum_crc32c)
            __dataclass__object_setattr(self, 'checksum_crc64nvme', checksum_crc64nvme)
            __dataclass__object_setattr(self, 'checksum_sha1', checksum_sha1)
            __dataclass__object_setattr(self, 'checksum_sha256', checksum_sha256)
            __dataclass__object_setattr(self, 'checksum_sha512', checksum_sha512)
            __dataclass__object_setattr(self, 'checksum_md5', checksum_md5)
            __dataclass__object_setattr(self, 'checksum_xxhash64', checksum_xxhash64)
            __dataclass__object_setattr(self, 'checksum_xxhash3', checksum_xxhash3)
            __dataclass__object_setattr(self, 'checksum_xxhash128', checksum_xxhash128)
            __dataclass__object_setattr(self, 'checksum_type', checksum_type)
            __dataclass__object_setattr(self, 'server_side_encryption', server_side_encryption)
            __dataclass__object_setattr(self, 'version_id', version_id)
            __dataclass__object_setattr(self, 'sse_customer_algorithm', sse_customer_algorithm)
            __dataclass__object_setattr(self, 'sse_customer_key_md5', sse_customer_key_md5)
            __dataclass__object_setattr(self, 'sse_kms_key_id', sse_kms_key_id)
            __dataclass__object_setattr(self, 'sse_kms_encryption_context', sse_kms_encryption_context)
            __dataclass__object_setattr(self, 'bucket_key_enabled', bucket_key_enabled)
            __dataclass__object_setattr(self, 'size', size)
            __dataclass__object_setattr(self, 'request_charged', request_charged)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"expiration={self.expiration!r}")
            parts.append(f"etag={self.etag!r}")
            parts.append(f"checksum_crc32={self.checksum_crc32!r}")
            parts.append(f"checksum_crc32c={self.checksum_crc32c!r}")
            parts.append(f"checksum_crc64nvme={self.checksum_crc64nvme!r}")
            parts.append(f"checksum_sha1={self.checksum_sha1!r}")
            parts.append(f"checksum_sha256={self.checksum_sha256!r}")
            parts.append(f"checksum_sha512={self.checksum_sha512!r}")
            parts.append(f"checksum_md5={self.checksum_md5!r}")
            parts.append(f"checksum_xxhash64={self.checksum_xxhash64!r}")
            parts.append(f"checksum_xxhash3={self.checksum_xxhash3!r}")
            parts.append(f"checksum_xxhash128={self.checksum_xxhash128!r}")
            parts.append(f"checksum_type={self.checksum_type!r}")
            parts.append(f"server_side_encryption={self.server_side_encryption!r}")
            parts.append(f"version_id={self.version_id!r}")
            parts.append(f"sse_customer_algorithm={self.sse_customer_algorithm!r}")
            parts.append(f"sse_customer_key_md5={self.sse_customer_key_md5!r}")
            parts.append(f"sse_kms_key_id={self.sse_kms_key_id!r}")
            parts.append(f"sse_kms_encryption_context={self.sse_kms_encryption_context!r}")
            parts.append(f"bucket_key_enabled={self.bucket_key_enabled!r}")
            parts.append(f"size={self.size!r}")
            parts.append(f"request_charged={self.request_charged!r}")
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
        "Plans(tup=(CopyPlan(fields=('acl', 'body', 'bucket', 'cache_control', 'content_disposition', 'content_encoding"
        "', 'content_language', 'content_length', 'content_md5', 'content_type', 'checksum_algorithm', 'checksum_crc32'"
        ", 'checksum_crc32c', 'checksum_crc64nvme', 'checksum_sha1', 'checksum_sha256', 'checksum_sha512', 'checksum_md"
        "5', 'checksum_xxhash64', 'checksum_xxhash3', 'checksum_xxhash128', 'expires', 'if_match', 'if_none_match', 'gr"
        "ant_full_control', 'grant_read', 'grant_read_acp', 'grant_write_acp', 'key', 'write_offset_bytes', 'metadata',"
        " 'server_side_encryption', 'storage_class', 'website_redirect_location', 'sse_customer_algorithm', 'sse_custom"
        "er_key', 'sse_customer_key_md5', 'sse_kms_key_id', 'sse_kms_encryption_context', 'bucket_key_enabled', 'reques"
        "t_payer', 'tagging', 'object_lock_mode', 'object_lock_retain_until_date', 'object_lock_legal_hold_status', 'ex"
        "pected_bucket_owner')), EqPlan(fields=('acl', 'body', 'bucket', 'cache_control', 'content_disposition', 'conte"
        "nt_encoding', 'content_language', 'content_length', 'content_md5', 'content_type', 'checksum_algorithm', 'chec"
        "ksum_crc32', 'checksum_crc32c', 'checksum_crc64nvme', 'checksum_sha1', 'checksum_sha256', 'checksum_sha512', '"
        "checksum_md5', 'checksum_xxhash64', 'checksum_xxhash3', 'checksum_xxhash128', 'expires', 'if_match', 'if_none_"
        "match', 'grant_full_control', 'grant_read', 'grant_read_acp', 'grant_write_acp', 'key', 'write_offset_bytes', "
        "'metadata', 'server_side_encryption', 'storage_class', 'website_redirect_location', 'sse_customer_algorithm', "
        "'sse_customer_key', 'sse_customer_key_md5', 'sse_kms_key_id', 'sse_kms_encryption_context', 'bucket_key_enable"
        "d', 'request_payer', 'tagging', 'object_lock_mode', 'object_lock_retain_until_date', 'object_lock_legal_hold_s"
        "tatus', 'expected_bucket_owner')), FrozenPlan(fields=('__shape__', 'acl', 'body', 'bucket', 'cache_control', '"
        "content_disposition', 'content_encoding', 'content_language', 'content_length', 'content_md5', 'content_type',"
        " 'checksum_algorithm', 'checksum_crc32', 'checksum_crc32c', 'checksum_crc64nvme', 'checksum_sha1', 'checksum_s"
        "ha256', 'checksum_sha512', 'checksum_md5', 'checksum_xxhash64', 'checksum_xxhash3', 'checksum_xxhash128', 'exp"
        "ires', 'if_match', 'if_none_match', 'grant_full_control', 'grant_read', 'grant_read_acp', 'grant_write_acp', '"
        "key', 'write_offset_bytes', 'metadata', 'server_side_encryption', 'storage_class', 'website_redirect_location'"
        ", 'sse_customer_algorithm', 'sse_customer_key', 'sse_customer_key_md5', 'sse_kms_key_id', 'sse_kms_encryption_"
        "context', 'bucket_key_enabled', 'request_payer', 'tagging', 'object_lock_mode', 'object_lock_retain_until_date"
        "', 'object_lock_legal_hold_status', 'expected_bucket_owner'), allow_dynamic_dunder_attrs=False), HashPlan(acti"
        "on='add', fields=('acl', 'body', 'bucket', 'cache_control', 'content_disposition', 'content_encoding', 'conten"
        "t_language', 'content_length', 'content_md5', 'content_type', 'checksum_algorithm', 'checksum_crc32', 'checksu"
        "m_crc32c', 'checksum_crc64nvme', 'checksum_sha1', 'checksum_sha256', 'checksum_sha512', 'checksum_md5', 'check"
        "sum_xxhash64', 'checksum_xxhash3', 'checksum_xxhash128', 'expires', 'if_match', 'if_none_match', 'grant_full_c"
        "ontrol', 'grant_read', 'grant_read_acp', 'grant_write_acp', 'key', 'write_offset_bytes', 'metadata', 'server_s"
        "ide_encryption', 'storage_class', 'website_redirect_location', 'sse_customer_algorithm', 'sse_customer_key', '"
        "sse_customer_key_md5', 'sse_kms_key_id', 'sse_kms_encryption_context', 'bucket_key_enabled', 'request_payer', "
        "'tagging', 'object_lock_mode', 'object_lock_retain_until_date', 'object_lock_legal_hold_status', 'expected_buc"
        "ket_owner'), cache=False), InitPlan(fields=(InitPlan.Field(name='__shape__', annotation=OpRef(name='init.field"
        "s.00.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS_V"
        "AR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='acl', annotation=OpRef(name='init.field"
        "s.01.annotation'), default=OpRef(name='init.fields.01.default'), default_factory=None, init=True, override=Fal"
        "se, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='body', a"
        "nnotation=OpRef(name='init.fields.02.annotation'), default=OpRef(name='init.fields.02.default'), default_facto"
        "ry=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None"
        "), InitPlan.Field(name='bucket', annotation=OpRef(name='init.fields.03.annotation'), default=None, default_fac"
        "tory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=No"
        "ne), InitPlan.Field(name='cache_control', annotation=OpRef(name='init.fields.04.annotation'), default=OpRef(na"
        "me='init.fields.04.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, "
        "coerce=None, validate=None, check_type=None), InitPlan.Field(name='content_disposition', annotation=OpRef(name"
        "='init.fields.05.annotation'), default=OpRef(name='init.fields.05.default'), default_factory=None, init=True, "
        "override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(na"
        "me='content_encoding', annotation=OpRef(name='init.fields.06.annotation'), default=OpRef(name='init.fields.06."
        "default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valida"
        "te=None, check_type=None), InitPlan.Field(name='content_language', annotation=OpRef(name='init.fields.07.annot"
        "ation'), default=OpRef(name='init.fields.07.default'), default_factory=None, init=True, override=False, field_"
        "type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='content_length', a"
        "nnotation=OpRef(name='init.fields.08.annotation'), default=OpRef(name='init.fields.08.default'), default_facto"
        "ry=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None"
        "), InitPlan.Field(name='content_md5', annotation=OpRef(name='init.fields.09.annotation'), default=OpRef(name='"
        "init.fields.09.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coer"
        "ce=None, validate=None, check_type=None), InitPlan.Field(name='content_type', annotation=OpRef(name='init.fiel"
        "ds.10.annotation'), default=OpRef(name='init.fields.10.default'), default_factory=None, init=True, override=Fa"
        "lse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='checksu"
        "m_algorithm', annotation=OpRef(name='init.fields.11.annotation'), default=OpRef(name='init.fields.11.default')"
        ", default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, "
        "check_type=None), InitPlan.Field(name='checksum_crc32', annotation=OpRef(name='init.fields.12.annotation'), de"
        "fault=OpRef(name='init.fields.12.default'), default_factory=None, init=True, override=False, field_type=FieldT"
        "ype.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='checksum_crc32c', annotation="
        "OpRef(name='init.fields.13.annotation'), default=OpRef(name='init.fields.13.default'), default_factory=None, i"
        "nit=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPla"
        "n.Field(name='checksum_crc64nvme', annotation=OpRef(name='init.fields.14.annotation'), default=OpRef(name='ini"
        "t.fields.14.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce="
        "None, validate=None, check_type=None), InitPlan.Field(name='checksum_sha1', annotation=OpRef(name='init.fields"
        ".15.annotation'), default=OpRef(name='init.fields.15.default'), default_factory=None, init=True, override=Fals"
        "e, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='checksum_"
        "sha256', annotation=OpRef(name='init.fields.16.annotation'), default=OpRef(name='init.fields.16.default'), def"
        "ault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check"
        "_type=None), InitPlan.Field(name='checksum_sha512', annotation=OpRef(name='init.fields.17.annotation'), defaul"
        "t=OpRef(name='init.fields.17.default'), default_factory=None, init=True, override=False, field_type=FieldType."
        "INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='checksum_md5', annotation=OpRef(n"
        "ame='init.fields.18.annotation'), default=OpRef(name='init.fields.18.default'), default_factory=None, init=Tru"
        "e, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field"
        "(name='checksum_xxhash64', annotation=OpRef(name='init.fields.19.annotation'), default=OpRef(name='init.fields"
        ".19.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, va"
        "lidate=None, check_type=None), InitPlan.Field(name='checksum_xxhash3', annotation=OpRef(name='init.fields.20.a"
        "nnotation'), default=OpRef(name='init.fields.20.default'), default_factory=None, init=True, override=False, fi"
        "eld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='checksum_xxhas"
        "h128', annotation=OpRef(name='init.fields.21.annotation'), default=OpRef(name='init.fields.21.default'), defau"
        "lt_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_t"
        "ype=None), InitPlan.Field(name='expires', annotation=OpRef(name='init.fields.22.annotation'), default=OpRef(na"
        "me='init.fields.22.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, "
        "coerce=None, validate=None, check_type=None), InitPlan.Field(name='if_match', annotation=OpRef(name='init.fiel"
        "ds.23.annotation'), default=OpRef(name='init.fields.23.default'), default_factory=None, init=True, override=Fa"
        "lse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='if_none"
        "_match', annotation=OpRef(name='init.fields.24.annotation'), default=OpRef(name='init.fields.24.default'), def"
        "ault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check"
        "_type=None), InitPlan.Field(name='grant_full_control', annotation=OpRef(name='init.fields.25.annotation'), def"
        "ault=OpRef(name='init.fields.25.default'), default_factory=None, init=True, override=False, field_type=FieldTy"
        "pe.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='grant_read', annotation=OpRef("
        "name='init.fields.26.annotation'), default=OpRef(name='init.fields.26.default'), default_factory=None, init=Tr"
        "ue, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fiel"
        "d(name='grant_read_acp', annotation=OpRef(name='init.fields.27.annotation'), default=OpRef(name='init.fields.2"
        "7.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, vali"
        "date=None, check_type=None), InitPlan.Field(name='grant_write_acp', annotation=OpRef(name='init.fields.28.anno"
        "tation'), default=OpRef(name='init.fields.28.default'), default_factory=None, init=True, override=False, field"
        "_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='key', annotation="
        "OpRef(name='init.fields.29.annotation'), default=None, default_factory=None, init=True, override=False, field_"
        "type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='write_offset_bytes"
        "', annotation=OpRef(name='init.fields.30.annotation'), default=OpRef(name='init.fields.30.default'), default_f"
        "actory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type="
        "None), InitPlan.Field(name='metadata', annotation=OpRef(name='init.fields.31.annotation'), default=OpRef(name="
        "'init.fields.31.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coe"
        "rce=None, validate=None, check_type=None), InitPlan.Field(name='server_side_encryption', annotation=OpRef(name"
        "='init.fields.32.annotation'), default=OpRef(name='init.fields.32.default'), default_factory=None, init=True, "
        "override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(na"
        "me='storage_class', annotation=OpRef(name='init.fields.33.annotation'), default=OpRef(name='init.fields.33.def"
        "ault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate="
        "None, check_type=None), InitPlan.Field(name='website_redirect_location', annotation=OpRef(name='init.fields.34"
        ".annotation'), default=OpRef(name='init.fields.34.default'), default_factory=None, init=True, override=False, "
        "field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='sse_customer"
        "_algorithm', annotation=OpRef(name='init.fields.35.annotation'), default=OpRef(name='init.fields.35.default'),"
        " default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, c"
        "heck_type=None), InitPlan.Field(name='sse_customer_key', annotation=OpRef(name='init.fields.36.annotation'), d"
        "efault=OpRef(name='init.fields.36.default'), default_factory=None, init=True, override=False, field_type=Field"
        "Type.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='sse_customer_key_md5', annot"
        "ation=OpRef(name='init.fields.37.annotation'), default=OpRef(name='init.fields.37.default'), default_factory=N"
        "one, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), I"
        "nitPlan.Field(name='sse_kms_key_id', annotation=OpRef(name='init.fields.38.annotation'), default=OpRef(name='i"
        "nit.fields.38.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerc"
        "e=None, validate=None, check_type=None), InitPlan.Field(name='sse_kms_encryption_context', annotation=OpRef(na"
        "me='init.fields.39.annotation'), default=OpRef(name='init.fields.39.default'), default_factory=None, init=True"
        ", override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field("
        "name='bucket_key_enabled', annotation=OpRef(name='init.fields.40.annotation'), default=OpRef(name='init.fields"
        ".40.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, va"
        "lidate=None, check_type=None), InitPlan.Field(name='request_payer', annotation=OpRef(name='init.fields.41.anno"
        "tation'), default=OpRef(name='init.fields.41.default'), default_factory=None, init=True, override=False, field"
        "_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='tagging', annotat"
        "ion=OpRef(name='init.fields.42.annotation'), default=OpRef(name='init.fields.42.default'), default_factory=Non"
        "e, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), Ini"
        "tPlan.Field(name='object_lock_mode', annotation=OpRef(name='init.fields.43.annotation'), default=OpRef(name='i"
        "nit.fields.43.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerc"
        "e=None, validate=None, check_type=None), InitPlan.Field(name='object_lock_retain_until_date', annotation=OpRef"
        "(name='init.fields.44.annotation'), default=OpRef(name='init.fields.44.default'), default_factory=None, init=T"
        "rue, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fie"
        "ld(name='object_lock_legal_hold_status', annotation=OpRef(name='init.fields.45.annotation'), default=OpRef(nam"
        "e='init.fields.45.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, c"
        "oerce=None, validate=None, check_type=None), InitPlan.Field(name='expected_bucket_owner', annotation=OpRef(nam"
        "e='init.fields.46.annotation'), default=OpRef(name='init.fields.46.default'), default_factory=None, init=True,"
        " override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='sel"
        "f', std_params=(), kw_only_params=('acl', 'body', 'bucket', 'cache_control', 'content_disposition', 'content_e"
        "ncoding', 'content_language', 'content_length', 'content_md5', 'content_type', 'checksum_algorithm', 'checksum"
        "_crc32', 'checksum_crc32c', 'checksum_crc64nvme', 'checksum_sha1', 'checksum_sha256', 'checksum_sha512', 'chec"
        "ksum_md5', 'checksum_xxhash64', 'checksum_xxhash3', 'checksum_xxhash128', 'expires', 'if_match', 'if_none_matc"
        "h', 'grant_full_control', 'grant_read', 'grant_read_acp', 'grant_write_acp', 'key', 'write_offset_bytes', 'met"
        "adata', 'server_side_encryption', 'storage_class', 'website_redirect_location', 'sse_customer_algorithm', 'sse"
        "_customer_key', 'sse_customer_key_md5', 'sse_kms_key_id', 'sse_kms_encryption_context', 'bucket_key_enabled', "
        "'request_payer', 'tagging', 'object_lock_mode', 'object_lock_retain_until_date', 'object_lock_legal_hold_statu"
        "s', 'expected_bucket_owner'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), "
        "ReprPlan(fields=(ReprPlan.Field(name='acl', kw_only=True, fn=None), ReprPlan.Field(name='body', kw_only=True, "
        "fn=None), ReprPlan.Field(name='bucket', kw_only=True, fn=None), ReprPlan.Field(name='cache_control', kw_only=T"
        "rue, fn=None), ReprPlan.Field(name='content_disposition', kw_only=True, fn=None), ReprPlan.Field(name='content"
        "_encoding', kw_only=True, fn=None), ReprPlan.Field(name='content_language', kw_only=True, fn=None), ReprPlan.F"
        "ield(name='content_length', kw_only=True, fn=None), ReprPlan.Field(name='content_md5', kw_only=True, fn=None),"
        " ReprPlan.Field(name='content_type', kw_only=True, fn=None), ReprPlan.Field(name='checksum_algorithm', kw_only"
        "=True, fn=None), ReprPlan.Field(name='checksum_crc32', kw_only=True, fn=None), ReprPlan.Field(name='checksum_c"
        "rc32c', kw_only=True, fn=None), ReprPlan.Field(name='checksum_crc64nvme', kw_only=True, fn=None), ReprPlan.Fie"
        "ld(name='checksum_sha1', kw_only=True, fn=None), ReprPlan.Field(name='checksum_sha256', kw_only=True, fn=None)"
        ", ReprPlan.Field(name='checksum_sha512', kw_only=True, fn=None), ReprPlan.Field(name='checksum_md5', kw_only=T"
        "rue, fn=None), ReprPlan.Field(name='checksum_xxhash64', kw_only=True, fn=None), ReprPlan.Field(name='checksum_"
        "xxhash3', kw_only=True, fn=None), ReprPlan.Field(name='checksum_xxhash128', kw_only=True, fn=None), ReprPlan.F"
        "ield(name='expires', kw_only=True, fn=None), ReprPlan.Field(name='if_match', kw_only=True, fn=None), ReprPlan."
        "Field(name='if_none_match', kw_only=True, fn=None), ReprPlan.Field(name='grant_full_control', kw_only=True, fn"
        "=None), ReprPlan.Field(name='grant_read', kw_only=True, fn=None), ReprPlan.Field(name='grant_read_acp', kw_onl"
        "y=True, fn=None), ReprPlan.Field(name='grant_write_acp', kw_only=True, fn=None), ReprPlan.Field(name='key', kw"
        "_only=True, fn=None), ReprPlan.Field(name='write_offset_bytes', kw_only=True, fn=None), ReprPlan.Field(name='m"
        "etadata', kw_only=True, fn=None), ReprPlan.Field(name='server_side_encryption', kw_only=True, fn=None), ReprPl"
        "an.Field(name='storage_class', kw_only=True, fn=None), ReprPlan.Field(name='website_redirect_location', kw_onl"
        "y=True, fn=None), ReprPlan.Field(name='sse_customer_algorithm', kw_only=True, fn=None), ReprPlan.Field(name='s"
        "se_customer_key', kw_only=True, fn=None), ReprPlan.Field(name='sse_customer_key_md5', kw_only=True, fn=None), "
        "ReprPlan.Field(name='sse_kms_key_id', kw_only=True, fn=None), ReprPlan.Field(name='sse_kms_encryption_context'"
        ", kw_only=True, fn=None), ReprPlan.Field(name='bucket_key_enabled', kw_only=True, fn=None), ReprPlan.Field(nam"
        "e='request_payer', kw_only=True, fn=None), ReprPlan.Field(name='tagging', kw_only=True, fn=None), ReprPlan.Fie"
        "ld(name='object_lock_mode', kw_only=True, fn=None), ReprPlan.Field(name='object_lock_retain_until_date', kw_on"
        "ly=True, fn=None), ReprPlan.Field(name='object_lock_legal_hold_status', kw_only=True, fn=None), ReprPlan.Field"
        "(name='expected_bucket_owner', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='6e8d51e9fff8bd18f4a4d51bc21a3a64c5b3842f',
    op_ref_idents=(
        '__dataclass__init__fields__01__annotation',
        '__dataclass__init__fields__01__default',
        '__dataclass__init__fields__02__annotation',
        '__dataclass__init__fields__02__default',
        '__dataclass__init__fields__03__annotation',
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
        '__dataclass__init__fields__18__annotation',
        '__dataclass__init__fields__18__default',
        '__dataclass__init__fields__19__annotation',
        '__dataclass__init__fields__19__default',
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
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.s3', 'PutObjectRequest'),
    ),
)
def _process_dataclass__6e8d51e9fff8bd18f4a4d51bc21a3a64c5b3842f():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__01__annotation,
        __dataclass__init__fields__01__default,
        __dataclass__init__fields__02__annotation,
        __dataclass__init__fields__02__default,
        __dataclass__init__fields__03__annotation,
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
        __dataclass__init__fields__18__annotation,
        __dataclass__init__fields__18__default,
        __dataclass__init__fields__19__annotation,
        __dataclass__init__fields__19__default,
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
                acl=self.acl,
                body=self.body,
                bucket=self.bucket,
                cache_control=self.cache_control,
                content_disposition=self.content_disposition,
                content_encoding=self.content_encoding,
                content_language=self.content_language,
                content_length=self.content_length,
                content_md5=self.content_md5,
                content_type=self.content_type,
                checksum_algorithm=self.checksum_algorithm,
                checksum_crc32=self.checksum_crc32,
                checksum_crc32c=self.checksum_crc32c,
                checksum_crc64nvme=self.checksum_crc64nvme,
                checksum_sha1=self.checksum_sha1,
                checksum_sha256=self.checksum_sha256,
                checksum_sha512=self.checksum_sha512,
                checksum_md5=self.checksum_md5,
                checksum_xxhash64=self.checksum_xxhash64,
                checksum_xxhash3=self.checksum_xxhash3,
                checksum_xxhash128=self.checksum_xxhash128,
                expires=self.expires,
                if_match=self.if_match,
                if_none_match=self.if_none_match,
                grant_full_control=self.grant_full_control,
                grant_read=self.grant_read,
                grant_read_acp=self.grant_read_acp,
                grant_write_acp=self.grant_write_acp,
                key=self.key,
                write_offset_bytes=self.write_offset_bytes,
                metadata=self.metadata,
                server_side_encryption=self.server_side_encryption,
                storage_class=self.storage_class,
                website_redirect_location=self.website_redirect_location,
                sse_customer_algorithm=self.sse_customer_algorithm,
                sse_customer_key=self.sse_customer_key,
                sse_customer_key_md5=self.sse_customer_key_md5,
                sse_kms_key_id=self.sse_kms_key_id,
                sse_kms_encryption_context=self.sse_kms_encryption_context,
                bucket_key_enabled=self.bucket_key_enabled,
                request_payer=self.request_payer,
                tagging=self.tagging,
                object_lock_mode=self.object_lock_mode,
                object_lock_retain_until_date=self.object_lock_retain_until_date,
                object_lock_legal_hold_status=self.object_lock_legal_hold_status,
                expected_bucket_owner=self.expected_bucket_owner,
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
                self.acl == other.acl and
                self.body == other.body and
                self.bucket == other.bucket and
                self.cache_control == other.cache_control and
                self.content_disposition == other.content_disposition and
                self.content_encoding == other.content_encoding and
                self.content_language == other.content_language and
                self.content_length == other.content_length and
                self.content_md5 == other.content_md5 and
                self.content_type == other.content_type and
                self.checksum_algorithm == other.checksum_algorithm and
                self.checksum_crc32 == other.checksum_crc32 and
                self.checksum_crc32c == other.checksum_crc32c and
                self.checksum_crc64nvme == other.checksum_crc64nvme and
                self.checksum_sha1 == other.checksum_sha1 and
                self.checksum_sha256 == other.checksum_sha256 and
                self.checksum_sha512 == other.checksum_sha512 and
                self.checksum_md5 == other.checksum_md5 and
                self.checksum_xxhash64 == other.checksum_xxhash64 and
                self.checksum_xxhash3 == other.checksum_xxhash3 and
                self.checksum_xxhash128 == other.checksum_xxhash128 and
                self.expires == other.expires and
                self.if_match == other.if_match and
                self.if_none_match == other.if_none_match and
                self.grant_full_control == other.grant_full_control and
                self.grant_read == other.grant_read and
                self.grant_read_acp == other.grant_read_acp and
                self.grant_write_acp == other.grant_write_acp and
                self.key == other.key and
                self.write_offset_bytes == other.write_offset_bytes and
                self.metadata == other.metadata and
                self.server_side_encryption == other.server_side_encryption and
                self.storage_class == other.storage_class and
                self.website_redirect_location == other.website_redirect_location and
                self.sse_customer_algorithm == other.sse_customer_algorithm and
                self.sse_customer_key == other.sse_customer_key and
                self.sse_customer_key_md5 == other.sse_customer_key_md5 and
                self.sse_kms_key_id == other.sse_kms_key_id and
                self.sse_kms_encryption_context == other.sse_kms_encryption_context and
                self.bucket_key_enabled == other.bucket_key_enabled and
                self.request_payer == other.request_payer and
                self.tagging == other.tagging and
                self.object_lock_mode == other.object_lock_mode and
                self.object_lock_retain_until_date == other.object_lock_retain_until_date and
                self.object_lock_legal_hold_status == other.object_lock_legal_hold_status and
                self.expected_bucket_owner == other.expected_bucket_owner
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'acl',
            'body',
            'bucket',
            'cache_control',
            'content_disposition',
            'content_encoding',
            'content_language',
            'content_length',
            'content_md5',
            'content_type',
            'checksum_algorithm',
            'checksum_crc32',
            'checksum_crc32c',
            'checksum_crc64nvme',
            'checksum_sha1',
            'checksum_sha256',
            'checksum_sha512',
            'checksum_md5',
            'checksum_xxhash64',
            'checksum_xxhash3',
            'checksum_xxhash128',
            'expires',
            'if_match',
            'if_none_match',
            'grant_full_control',
            'grant_read',
            'grant_read_acp',
            'grant_write_acp',
            'key',
            'write_offset_bytes',
            'metadata',
            'server_side_encryption',
            'storage_class',
            'website_redirect_location',
            'sse_customer_algorithm',
            'sse_customer_key',
            'sse_customer_key_md5',
            'sse_kms_key_id',
            'sse_kms_encryption_context',
            'bucket_key_enabled',
            'request_payer',
            'tagging',
            'object_lock_mode',
            'object_lock_retain_until_date',
            'object_lock_legal_hold_status',
            'expected_bucket_owner',
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
            'acl',
            'body',
            'bucket',
            'cache_control',
            'content_disposition',
            'content_encoding',
            'content_language',
            'content_length',
            'content_md5',
            'content_type',
            'checksum_algorithm',
            'checksum_crc32',
            'checksum_crc32c',
            'checksum_crc64nvme',
            'checksum_sha1',
            'checksum_sha256',
            'checksum_sha512',
            'checksum_md5',
            'checksum_xxhash64',
            'checksum_xxhash3',
            'checksum_xxhash128',
            'expires',
            'if_match',
            'if_none_match',
            'grant_full_control',
            'grant_read',
            'grant_read_acp',
            'grant_write_acp',
            'key',
            'write_offset_bytes',
            'metadata',
            'server_side_encryption',
            'storage_class',
            'website_redirect_location',
            'sse_customer_algorithm',
            'sse_customer_key',
            'sse_customer_key_md5',
            'sse_kms_key_id',
            'sse_kms_encryption_context',
            'bucket_key_enabled',
            'request_payer',
            'tagging',
            'object_lock_mode',
            'object_lock_retain_until_date',
            'object_lock_legal_hold_status',
            'expected_bucket_owner',
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
                self.acl,
                self.body,
                self.bucket,
                self.cache_control,
                self.content_disposition,
                self.content_encoding,
                self.content_language,
                self.content_length,
                self.content_md5,
                self.content_type,
                self.checksum_algorithm,
                self.checksum_crc32,
                self.checksum_crc32c,
                self.checksum_crc64nvme,
                self.checksum_sha1,
                self.checksum_sha256,
                self.checksum_sha512,
                self.checksum_md5,
                self.checksum_xxhash64,
                self.checksum_xxhash3,
                self.checksum_xxhash128,
                self.expires,
                self.if_match,
                self.if_none_match,
                self.grant_full_control,
                self.grant_read,
                self.grant_read_acp,
                self.grant_write_acp,
                self.key,
                self.write_offset_bytes,
                self.metadata,
                self.server_side_encryption,
                self.storage_class,
                self.website_redirect_location,
                self.sse_customer_algorithm,
                self.sse_customer_key,
                self.sse_customer_key_md5,
                self.sse_kms_key_id,
                self.sse_kms_encryption_context,
                self.bucket_key_enabled,
                self.request_payer,
                self.tagging,
                self.object_lock_mode,
                self.object_lock_retain_until_date,
                self.object_lock_legal_hold_status,
                self.expected_bucket_owner,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            acl: __dataclass__init__fields__01__annotation = __dataclass__init__fields__01__default,
            body: __dataclass__init__fields__02__annotation = __dataclass__init__fields__02__default,
            bucket: __dataclass__init__fields__03__annotation,
            cache_control: __dataclass__init__fields__04__annotation = __dataclass__init__fields__04__default,
            content_disposition: __dataclass__init__fields__05__annotation = __dataclass__init__fields__05__default,
            content_encoding: __dataclass__init__fields__06__annotation = __dataclass__init__fields__06__default,
            content_language: __dataclass__init__fields__07__annotation = __dataclass__init__fields__07__default,
            content_length: __dataclass__init__fields__08__annotation = __dataclass__init__fields__08__default,
            content_md5: __dataclass__init__fields__09__annotation = __dataclass__init__fields__09__default,
            content_type: __dataclass__init__fields__10__annotation = __dataclass__init__fields__10__default,
            checksum_algorithm: __dataclass__init__fields__11__annotation = __dataclass__init__fields__11__default,
            checksum_crc32: __dataclass__init__fields__12__annotation = __dataclass__init__fields__12__default,
            checksum_crc32c: __dataclass__init__fields__13__annotation = __dataclass__init__fields__13__default,
            checksum_crc64nvme: __dataclass__init__fields__14__annotation = __dataclass__init__fields__14__default,
            checksum_sha1: __dataclass__init__fields__15__annotation = __dataclass__init__fields__15__default,
            checksum_sha256: __dataclass__init__fields__16__annotation = __dataclass__init__fields__16__default,
            checksum_sha512: __dataclass__init__fields__17__annotation = __dataclass__init__fields__17__default,
            checksum_md5: __dataclass__init__fields__18__annotation = __dataclass__init__fields__18__default,
            checksum_xxhash64: __dataclass__init__fields__19__annotation = __dataclass__init__fields__19__default,
            checksum_xxhash3: __dataclass__init__fields__20__annotation = __dataclass__init__fields__20__default,
            checksum_xxhash128: __dataclass__init__fields__21__annotation = __dataclass__init__fields__21__default,
            expires: __dataclass__init__fields__22__annotation = __dataclass__init__fields__22__default,
            if_match: __dataclass__init__fields__23__annotation = __dataclass__init__fields__23__default,
            if_none_match: __dataclass__init__fields__24__annotation = __dataclass__init__fields__24__default,
            grant_full_control: __dataclass__init__fields__25__annotation = __dataclass__init__fields__25__default,
            grant_read: __dataclass__init__fields__26__annotation = __dataclass__init__fields__26__default,
            grant_read_acp: __dataclass__init__fields__27__annotation = __dataclass__init__fields__27__default,
            grant_write_acp: __dataclass__init__fields__28__annotation = __dataclass__init__fields__28__default,
            key: __dataclass__init__fields__29__annotation,
            write_offset_bytes: __dataclass__init__fields__30__annotation = __dataclass__init__fields__30__default,
            metadata: __dataclass__init__fields__31__annotation = __dataclass__init__fields__31__default,
            server_side_encryption: __dataclass__init__fields__32__annotation = __dataclass__init__fields__32__default,
            storage_class: __dataclass__init__fields__33__annotation = __dataclass__init__fields__33__default,
            website_redirect_location: __dataclass__init__fields__34__annotation = __dataclass__init__fields__34__default,
            sse_customer_algorithm: __dataclass__init__fields__35__annotation = __dataclass__init__fields__35__default,
            sse_customer_key: __dataclass__init__fields__36__annotation = __dataclass__init__fields__36__default,
            sse_customer_key_md5: __dataclass__init__fields__37__annotation = __dataclass__init__fields__37__default,
            sse_kms_key_id: __dataclass__init__fields__38__annotation = __dataclass__init__fields__38__default,
            sse_kms_encryption_context: __dataclass__init__fields__39__annotation = __dataclass__init__fields__39__default,
            bucket_key_enabled: __dataclass__init__fields__40__annotation = __dataclass__init__fields__40__default,
            request_payer: __dataclass__init__fields__41__annotation = __dataclass__init__fields__41__default,
            tagging: __dataclass__init__fields__42__annotation = __dataclass__init__fields__42__default,
            object_lock_mode: __dataclass__init__fields__43__annotation = __dataclass__init__fields__43__default,
            object_lock_retain_until_date: __dataclass__init__fields__44__annotation = __dataclass__init__fields__44__default,
            object_lock_legal_hold_status: __dataclass__init__fields__45__annotation = __dataclass__init__fields__45__default,
            expected_bucket_owner: __dataclass__init__fields__46__annotation = __dataclass__init__fields__46__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'acl', acl)
            __dataclass__object_setattr(self, 'body', body)
            __dataclass__object_setattr(self, 'bucket', bucket)
            __dataclass__object_setattr(self, 'cache_control', cache_control)
            __dataclass__object_setattr(self, 'content_disposition', content_disposition)
            __dataclass__object_setattr(self, 'content_encoding', content_encoding)
            __dataclass__object_setattr(self, 'content_language', content_language)
            __dataclass__object_setattr(self, 'content_length', content_length)
            __dataclass__object_setattr(self, 'content_md5', content_md5)
            __dataclass__object_setattr(self, 'content_type', content_type)
            __dataclass__object_setattr(self, 'checksum_algorithm', checksum_algorithm)
            __dataclass__object_setattr(self, 'checksum_crc32', checksum_crc32)
            __dataclass__object_setattr(self, 'checksum_crc32c', checksum_crc32c)
            __dataclass__object_setattr(self, 'checksum_crc64nvme', checksum_crc64nvme)
            __dataclass__object_setattr(self, 'checksum_sha1', checksum_sha1)
            __dataclass__object_setattr(self, 'checksum_sha256', checksum_sha256)
            __dataclass__object_setattr(self, 'checksum_sha512', checksum_sha512)
            __dataclass__object_setattr(self, 'checksum_md5', checksum_md5)
            __dataclass__object_setattr(self, 'checksum_xxhash64', checksum_xxhash64)
            __dataclass__object_setattr(self, 'checksum_xxhash3', checksum_xxhash3)
            __dataclass__object_setattr(self, 'checksum_xxhash128', checksum_xxhash128)
            __dataclass__object_setattr(self, 'expires', expires)
            __dataclass__object_setattr(self, 'if_match', if_match)
            __dataclass__object_setattr(self, 'if_none_match', if_none_match)
            __dataclass__object_setattr(self, 'grant_full_control', grant_full_control)
            __dataclass__object_setattr(self, 'grant_read', grant_read)
            __dataclass__object_setattr(self, 'grant_read_acp', grant_read_acp)
            __dataclass__object_setattr(self, 'grant_write_acp', grant_write_acp)
            __dataclass__object_setattr(self, 'key', key)
            __dataclass__object_setattr(self, 'write_offset_bytes', write_offset_bytes)
            __dataclass__object_setattr(self, 'metadata', metadata)
            __dataclass__object_setattr(self, 'server_side_encryption', server_side_encryption)
            __dataclass__object_setattr(self, 'storage_class', storage_class)
            __dataclass__object_setattr(self, 'website_redirect_location', website_redirect_location)
            __dataclass__object_setattr(self, 'sse_customer_algorithm', sse_customer_algorithm)
            __dataclass__object_setattr(self, 'sse_customer_key', sse_customer_key)
            __dataclass__object_setattr(self, 'sse_customer_key_md5', sse_customer_key_md5)
            __dataclass__object_setattr(self, 'sse_kms_key_id', sse_kms_key_id)
            __dataclass__object_setattr(self, 'sse_kms_encryption_context', sse_kms_encryption_context)
            __dataclass__object_setattr(self, 'bucket_key_enabled', bucket_key_enabled)
            __dataclass__object_setattr(self, 'request_payer', request_payer)
            __dataclass__object_setattr(self, 'tagging', tagging)
            __dataclass__object_setattr(self, 'object_lock_mode', object_lock_mode)
            __dataclass__object_setattr(self, 'object_lock_retain_until_date', object_lock_retain_until_date)
            __dataclass__object_setattr(self, 'object_lock_legal_hold_status', object_lock_legal_hold_status)
            __dataclass__object_setattr(self, 'expected_bucket_owner', expected_bucket_owner)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"acl={self.acl!r}")
            parts.append(f"body={self.body!r}")
            parts.append(f"bucket={self.bucket!r}")
            parts.append(f"cache_control={self.cache_control!r}")
            parts.append(f"content_disposition={self.content_disposition!r}")
            parts.append(f"content_encoding={self.content_encoding!r}")
            parts.append(f"content_language={self.content_language!r}")
            parts.append(f"content_length={self.content_length!r}")
            parts.append(f"content_md5={self.content_md5!r}")
            parts.append(f"content_type={self.content_type!r}")
            parts.append(f"checksum_algorithm={self.checksum_algorithm!r}")
            parts.append(f"checksum_crc32={self.checksum_crc32!r}")
            parts.append(f"checksum_crc32c={self.checksum_crc32c!r}")
            parts.append(f"checksum_crc64nvme={self.checksum_crc64nvme!r}")
            parts.append(f"checksum_sha1={self.checksum_sha1!r}")
            parts.append(f"checksum_sha256={self.checksum_sha256!r}")
            parts.append(f"checksum_sha512={self.checksum_sha512!r}")
            parts.append(f"checksum_md5={self.checksum_md5!r}")
            parts.append(f"checksum_xxhash64={self.checksum_xxhash64!r}")
            parts.append(f"checksum_xxhash3={self.checksum_xxhash3!r}")
            parts.append(f"checksum_xxhash128={self.checksum_xxhash128!r}")
            parts.append(f"expires={self.expires!r}")
            parts.append(f"if_match={self.if_match!r}")
            parts.append(f"if_none_match={self.if_none_match!r}")
            parts.append(f"grant_full_control={self.grant_full_control!r}")
            parts.append(f"grant_read={self.grant_read!r}")
            parts.append(f"grant_read_acp={self.grant_read_acp!r}")
            parts.append(f"grant_write_acp={self.grant_write_acp!r}")
            parts.append(f"key={self.key!r}")
            parts.append(f"write_offset_bytes={self.write_offset_bytes!r}")
            parts.append(f"metadata={self.metadata!r}")
            parts.append(f"server_side_encryption={self.server_side_encryption!r}")
            parts.append(f"storage_class={self.storage_class!r}")
            parts.append(f"website_redirect_location={self.website_redirect_location!r}")
            parts.append(f"sse_customer_algorithm={self.sse_customer_algorithm!r}")
            parts.append(f"sse_customer_key={self.sse_customer_key!r}")
            parts.append(f"sse_customer_key_md5={self.sse_customer_key_md5!r}")
            parts.append(f"sse_kms_key_id={self.sse_kms_key_id!r}")
            parts.append(f"sse_kms_encryption_context={self.sse_kms_encryption_context!r}")
            parts.append(f"bucket_key_enabled={self.bucket_key_enabled!r}")
            parts.append(f"request_payer={self.request_payer!r}")
            parts.append(f"tagging={self.tagging!r}")
            parts.append(f"object_lock_mode={self.object_lock_mode!r}")
            parts.append(f"object_lock_retain_until_date={self.object_lock_retain_until_date!r}")
            parts.append(f"object_lock_legal_hold_status={self.object_lock_legal_hold_status!r}")
            parts.append(f"expected_bucket_owner={self.expected_bucket_owner!r}")
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
        "Plans(tup=(CopyPlan(fields=('is_restore_in_progress', 'restore_expiry_date')), EqPlan(fields=('is_restore_in_p"
        "rogress', 'restore_expiry_date')), FrozenPlan(fields=('__shape__', 'is_restore_in_progress', 'restore_expiry_d"
        "ate'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('is_restore_in_progress', 'restore_ex"
        "piry_date'), cache=False), InitPlan(fields=(InitPlan.Field(name='__shape__', annotation=OpRef(name='init.field"
        "s.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS_VA"
        "R, coerce=None, validate=None, check_type=None), InitPlan.Field(name='is_restore_in_progress', annotation=OpRe"
        "f(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=Tr"
        "ue, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fiel"
        "d(name='restore_expiry_date', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fiel"
        "ds.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, v"
        "alidate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('is_restore_in_progress', '"
        "restore_expiry_date'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPla"
        "n(fields=(ReprPlan.Field(name='is_restore_in_progress', kw_only=True, fn=None), ReprPlan.Field(name='restore_e"
        "xpiry_date', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='6806d7dddb4fb9f5936333eb79517dfb8542221e',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.s3', 'RestoreStatus'),
    ),
)
def _process_dataclass__6806d7dddb4fb9f5936333eb79517dfb8542221e():
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
                is_restore_in_progress=self.is_restore_in_progress,
                restore_expiry_date=self.restore_expiry_date,
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
                self.is_restore_in_progress == other.is_restore_in_progress and
                self.restore_expiry_date == other.restore_expiry_date
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'is_restore_in_progress',
            'restore_expiry_date',
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
            'is_restore_in_progress',
            'restore_expiry_date',
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
                self.is_restore_in_progress,
                self.restore_expiry_date,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            is_restore_in_progress: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            restore_expiry_date: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'is_restore_in_progress', is_restore_in_progress)
            __dataclass__object_setattr(self, 'restore_expiry_date', restore_expiry_date)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"is_restore_in_progress={self.is_restore_in_progress!r}")
            parts.append(f"restore_expiry_date={self.restore_expiry_date!r}")
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
