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
        "Plans(tup=(CopyPlan(fields=('lambda_managed_instances_capacity_provider_config',)), EqPlan(fields=('lambda_man"
        "aged_instances_capacity_provider_config',)), FrozenPlan(fields=('__shape__', 'lambda_managed_instances_capacit"
        "y_provider_config'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('lambda_managed_instanc"
        "es_capacity_provider_config',), cache=False), InitPlan(fields=(InitPlan.Field(name='__shape__', annotation=OpR"
        "ef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type"
        "=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='lambda_managed_instan"
        "ces_capacity_provider_config', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factor"
        "y=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)"
        "), self_param='self', std_params=(), kw_only_params=('lambda_managed_instances_capacity_provider_config',), fr"
        "ozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field("
        "name='lambda_managed_instances_capacity_provider_config', kw_only=True, fn=None),), id=False, terse=False, def"
        "ault_fn=None)))"
    ),
    plan_repr_sha1='56a73cc80905fe58ffa6800ba93fc9b519922728',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.lambda_', 'CapacityProviderConfig'),
    ),
)
def _process_dataclass__56a73cc80905fe58ffa6800ba93fc9b519922728():
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
                lambda_managed_instances_capacity_provider_config=self.lambda_managed_instances_capacity_provider_config,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.lambda_managed_instances_capacity_provider_config == other.lambda_managed_instances_capacity_provider_config
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'lambda_managed_instances_capacity_provider_config',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'lambda_managed_instances_capacity_provider_config',
        }

        def __delattr__(self, name):
            if (
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
                self.lambda_managed_instances_capacity_provider_config,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            lambda_managed_instances_capacity_provider_config: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'lambda_managed_instances_capacity_provider_config', lambda_managed_instances_capacity_provider_config)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"lambda_managed_instances_capacity_provider_config={self.lambda_managed_instances_capacity_provider_config!r}")
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
        "Plans(tup=(CopyPlan(fields=('target_arn',)), EqPlan(fields=('target_arn',)), FrozenPlan(fields=('__shape__', '"
        "target_arn'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('target_arn',), cache=False), "
        "InitPlan(fields=(InitPlan.Field(name='__shape__', annotation=OpRef(name='init.fields.0.annotation'), default=N"
        "one, default_factory=None, init=True, override=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=No"
        "ne, check_type=None), InitPlan.Field(name='target_arn', annotation=OpRef(name='init.fields.1.annotation'), def"
        "ault=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldTyp"
        "e.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('"
        "target_arn',), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields"
        "=(ReprPlan.Field(name='target_arn', kw_only=True, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='a668802e6cc60181d0d91b2bd31db6e6a3724a65',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.lambda_', 'DeadLetterConfig'),
    ),
)
def _process_dataclass__a668802e6cc60181d0d91b2bd31db6e6a3724a65():
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
                target_arn=self.target_arn,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.target_arn == other.target_arn
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'target_arn',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'target_arn',
        }

        def __delattr__(self, name):
            if (
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
                self.target_arn,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            target_arn: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'target_arn', target_arn)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"target_arn={self.target_arn!r}")
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
        "Plans(tup=(CopyPlan(fields=('retention_period_in_days', 'execution_timeout')), EqPlan(fields=('retention_perio"
        "d_in_days', 'execution_timeout')), FrozenPlan(fields=('__shape__', 'retention_period_in_days', 'execution_time"
        "out'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('retention_period_in_days', 'executio"
        "n_timeout'), cache=False), InitPlan(fields=(InitPlan.Field(name='__shape__', annotation=OpRef(name='init.field"
        "s.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS_VA"
        "R, coerce=None, validate=None, check_type=None), InitPlan.Field(name='retention_period_in_days', annotation=Op"
        "Ref(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init="
        "True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fi"
        "eld(name='execution_timeout', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fiel"
        "ds.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, v"
        "alidate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('retention_period_in_days',"
        " 'execution_timeout'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPla"
        "n(fields=(ReprPlan.Field(name='retention_period_in_days', kw_only=True, fn=None), ReprPlan.Field(name='executi"
        "on_timeout', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='017f0ccfabf58bb95e85ed87d1549bbb2e98094f',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.lambda_', 'DurableConfig'),
    ),
)
def _process_dataclass__017f0ccfabf58bb95e85ed87d1549bbb2e98094f():
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
                retention_period_in_days=self.retention_period_in_days,
                execution_timeout=self.execution_timeout,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.retention_period_in_days == other.retention_period_in_days and
                self.execution_timeout == other.execution_timeout
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'retention_period_in_days',
            'execution_timeout',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'retention_period_in_days',
            'execution_timeout',
        }

        def __delattr__(self, name):
            if (
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
                self.retention_period_in_days,
                self.execution_timeout,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            retention_period_in_days: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            execution_timeout: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'retention_period_in_days', retention_period_in_days)
            __dataclass__object_setattr(self, 'execution_timeout', execution_timeout)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"retention_period_in_days={self.retention_period_in_days!r}")
            parts.append(f"execution_timeout={self.execution_timeout!r}")
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
        "Plans(tup=(CopyPlan(fields=('error_code', 'message')), EqPlan(fields=('error_code', 'message')), FrozenPlan(fi"
        "elds=('__shape__', 'error_code', 'message'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields="
        "('error_code', 'message'), cache=False), InitPlan(fields=(InitPlan.Field(name='__shape__', annotation=OpRef(na"
        "me='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=Fiel"
        "dType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='error_code', annotation=Op"
        "Ref(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init="
        "True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fi"
        "eld(name='message', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.defau"
        "lt'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=No"
        "ne, check_type=None)), self_param='self', std_params=(), kw_only_params=('error_code', 'message'), frozen=True"
        ", slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='err"
        "or_code', kw_only=True, fn=None), ReprPlan.Field(name='message', kw_only=True, fn=None)), id=False, terse=Fals"
        "e, default_fn=None)))"
    ),
    plan_repr_sha1='1d985e02ba3b7e1901dfcdb20eb2f1da1c066cf3',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.lambda_', 'EnvironmentError_'),
        ('ominfra.clouds.aws.models.services.lambda_', 'ImageConfigError'),
        ('ominfra.clouds.aws.models.services.lambda_', 'RuntimeVersionError'),
    ),
)
def _process_dataclass__1d985e02ba3b7e1901dfcdb20eb2f1da1c066cf3():
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
                error_code=self.error_code,
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
                self.error_code == other.error_code and
                self.message == other.message
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'error_code',
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
            'error_code',
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
                self.error_code,
                self.message,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            error_code: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            message: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'error_code', error_code)
            __dataclass__object_setattr(self, 'message', message)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"error_code={self.error_code!r}")
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
        "Plans(tup=(CopyPlan(fields=('variables', 'error')), EqPlan(fields=('variables', 'error')), FrozenPlan(fields=("
        "'__shape__', 'variables', 'error'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('variabl"
        "es', 'error'), cache=False), InitPlan(fields=(InitPlan.Field(name='__shape__', annotation=OpRef(name='init.fie"
        "lds.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS_"
        "VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='variables', annotation=OpRef(name='ini"
        "t.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, overrid"
        "e=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='err"
        "or', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_f"
        "actory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type="
        "None)), self_param='self', std_params=(), kw_only_params=('variables', 'error'), frozen=True, slots=False, pos"
        "t_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='variables', kw_only=T"
        "rue, fn=None), ReprPlan.Field(name='error', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='317c843e53bb9dfbb0f4e22012dab481c78eee00',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.lambda_', 'EnvironmentResponse'),
    ),
)
def _process_dataclass__317c843e53bb9dfbb0f4e22012dab481c78eee00():
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
                variables=self.variables,
                error=self.error,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.variables == other.variables and
                self.error == other.error
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'variables',
            'error',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'variables',
            'error',
        }

        def __delattr__(self, name):
            if (
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
                self.variables,
                self.error,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            variables: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            error: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'variables', variables)
            __dataclass__object_setattr(self, 'error', error)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"variables={self.variables!r}")
            parts.append(f"error={self.error!r}")
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
        "Plans(tup=(CopyPlan(fields=('size',)), EqPlan(fields=('size',)), FrozenPlan(fields=('__shape__', 'size'), allo"
        "w_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('size',), cache=False), InitPlan(fields=(InitPla"
        "n.Field(name='__shape__', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=Non"
        "e, init=True, override=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), In"
        "itPlan.Field(name='size', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=Non"
        "e, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), se"
        "lf_param='self', std_params=(), kw_only_params=('size',), frozen=True, slots=False, post_init_params=None, ini"
        "t_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='size', kw_only=True, fn=None),), id=False, t"
        "erse=False, default_fn=None)))"
    ),
    plan_repr_sha1='ba17cf6d4b72f343a67190bab2265616e5cbaebc',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.lambda_', 'EphemeralStorage'),
    ),
)
def _process_dataclass__ba17cf6d4b72f343a67190bab2265616e5cbaebc():
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
                size=self.size,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.size == other.size
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'size',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'size',
        }

        def __delattr__(self, name):
            if (
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
                self.size,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            size: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'size', size)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"size={self.size!r}")
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
        "Plans(tup=(CopyPlan(fields=('arn', 'local_mount_path')), EqPlan(fields=('arn', 'local_mount_path')), FrozenPla"
        "n(fields=('__shape__', 'arn', 'local_mount_path'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', f"
        "ields=('arn', 'local_mount_path'), cache=False), InitPlan(fields=(InitPlan.Field(name='__shape__', annotation="
        "OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_t"
        "ype=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='arn', annotation=O"
        "pRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_ty"
        "pe=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='local_mount_path', a"
        "nnotation=OpRef(name='init.fields.2.annotation'), default=None, default_factory=None, init=True, override=Fals"
        "e, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params"
        "=(), kw_only_params=('arn', 'local_mount_path'), frozen=True, slots=False, post_init_params=None, init_fns=(),"
        " validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='arn', kw_only=True, fn=None), ReprPlan.Field(name='lo"
        "cal_mount_path', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='782e9b5d3cf1915925c20121ed1c830c7d6ccaf2',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.lambda_', 'FileSystemConfig'),
    ),
)
def _process_dataclass__782e9b5d3cf1915925c20121ed1c830c7d6ccaf2():
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
                arn=self.arn,
                local_mount_path=self.local_mount_path,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.arn == other.arn and
                self.local_mount_path == other.local_mount_path
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'arn',
            'local_mount_path',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'local_mount_path',
        }

        def __delattr__(self, name):
            if (
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
                self.local_mount_path,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            arn: __dataclass__init__fields__1__annotation,
            local_mount_path: __dataclass__init__fields__2__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'arn', arn)
            __dataclass__object_setattr(self, 'local_mount_path', local_mount_path)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"arn={self.arn!r}")
            parts.append(f"local_mount_path={self.local_mount_path!r}")
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
        "Plans(tup=(CopyPlan(fields=('function_name', 'function_arn', 'runtime', 'role', 'handler', 'code_size', 'descr"
        "iption', 'timeout', 'memory_size', 'last_modified', 'code_sha256', 'version', 'vpc_config', 'dead_letter_confi"
        "g', 'environment', 'kms_key_arn', 'tracing_config', 'master_arn', 'revision_id', 'layers', 'state', 'state_rea"
        "son', 'state_reason_code', 'last_update_status', 'last_update_status_reason', 'last_update_status_reason_code'"
        ", 'file_system_configs', 'package_type', 'image_config_response', 'signing_profile_version_arn', 'signing_job_"
        "arn', 'architectures', 'ephemeral_storage', 'snap_start', 'runtime_version_config', 'logging_config', 'capacit"
        "y_provider_config', 'config_sha256', 'durable_config', 'tenancy_config')), EqPlan(fields=('function_name', 'fu"
        "nction_arn', 'runtime', 'role', 'handler', 'code_size', 'description', 'timeout', 'memory_size', 'last_modifie"
        "d', 'code_sha256', 'version', 'vpc_config', 'dead_letter_config', 'environment', 'kms_key_arn', 'tracing_confi"
        "g', 'master_arn', 'revision_id', 'layers', 'state', 'state_reason', 'state_reason_code', 'last_update_status',"
        " 'last_update_status_reason', 'last_update_status_reason_code', 'file_system_configs', 'package_type', 'image_"
        "config_response', 'signing_profile_version_arn', 'signing_job_arn', 'architectures', 'ephemeral_storage', 'sna"
        "p_start', 'runtime_version_config', 'logging_config', 'capacity_provider_config', 'config_sha256', 'durable_co"
        "nfig', 'tenancy_config')), FrozenPlan(fields=('__shape__', 'function_name', 'function_arn', 'runtime', 'role',"
        " 'handler', 'code_size', 'description', 'timeout', 'memory_size', 'last_modified', 'code_sha256', 'version', '"
        "vpc_config', 'dead_letter_config', 'environment', 'kms_key_arn', 'tracing_config', 'master_arn', 'revision_id'"
        ", 'layers', 'state', 'state_reason', 'state_reason_code', 'last_update_status', 'last_update_status_reason', '"
        "last_update_status_reason_code', 'file_system_configs', 'package_type', 'image_config_response', 'signing_prof"
        "ile_version_arn', 'signing_job_arn', 'architectures', 'ephemeral_storage', 'snap_start', 'runtime_version_conf"
        "ig', 'logging_config', 'capacity_provider_config', 'config_sha256', 'durable_config', 'tenancy_config'), allow"
        "_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('function_name', 'function_arn', 'runtime', 'role"
        "', 'handler', 'code_size', 'description', 'timeout', 'memory_size', 'last_modified', 'code_sha256', 'version',"
        " 'vpc_config', 'dead_letter_config', 'environment', 'kms_key_arn', 'tracing_config', 'master_arn', 'revision_i"
        "d', 'layers', 'state', 'state_reason', 'state_reason_code', 'last_update_status', 'last_update_status_reason',"
        " 'last_update_status_reason_code', 'file_system_configs', 'package_type', 'image_config_response', 'signing_pr"
        "ofile_version_arn', 'signing_job_arn', 'architectures', 'ephemeral_storage', 'snap_start', 'runtime_version_co"
        "nfig', 'logging_config', 'capacity_provider_config', 'config_sha256', 'durable_config', 'tenancy_config'), cac"
        "he=False), InitPlan(fields=(InitPlan.Field(name='__shape__', annotation=OpRef(name='init.fields.0.annotation')"
        ", default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS_VAR, coerce=None, "
        "validate=None, check_type=None), InitPlan.Field(name='function_name', annotation=OpRef(name='init.fields.1.ann"
        "otation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field"
        "_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='function_arn', an"
        "notation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory="
        "None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), "
        "InitPlan.Field(name='runtime', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fie"
        "lds.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, "
        "validate=None, check_type=None), InitPlan.Field(name='role', annotation=OpRef(name='init.fields.4.annotation')"
        ", default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, override=False, field_type=Fie"
        "ldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='handler', annotation=OpRef"
        "(name='init.fields.5.annotation'), default=OpRef(name='init.fields.5.default'), default_factory=None, init=Tru"
        "e, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field"
        "(name='code_size', annotation=OpRef(name='init.fields.6.annotation'), default=OpRef(name='init.fields.6.defaul"
        "t'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=Non"
        "e, check_type=None), InitPlan.Field(name='description', annotation=OpRef(name='init.fields.7.annotation'), def"
        "ault=OpRef(name='init.fields.7.default'), default_factory=None, init=True, override=False, field_type=FieldTyp"
        "e.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='timeout', annotation=OpRef(name"
        "='init.fields.8.annotation'), default=OpRef(name='init.fields.8.default'), default_factory=None, init=True, ov"
        "erride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name"
        "='memory_size', annotation=OpRef(name='init.fields.9.annotation'), default=OpRef(name='init.fields.9.default')"
        ", default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, "
        "check_type=None), InitPlan.Field(name='last_modified', annotation=OpRef(name='init.fields.10.annotation'), def"
        "ault=OpRef(name='init.fields.10.default'), default_factory=None, init=True, override=False, field_type=FieldTy"
        "pe.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='code_sha256', annotation=OpRef"
        "(name='init.fields.11.annotation'), default=OpRef(name='init.fields.11.default'), default_factory=None, init=T"
        "rue, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fie"
        "ld(name='version', annotation=OpRef(name='init.fields.12.annotation'), default=OpRef(name='init.fields.12.defa"
        "ult'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=N"
        "one, check_type=None), InitPlan.Field(name='vpc_config', annotation=OpRef(name='init.fields.13.annotation'), d"
        "efault=OpRef(name='init.fields.13.default'), default_factory=None, init=True, override=False, field_type=Field"
        "Type.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='dead_letter_config', annotat"
        "ion=OpRef(name='init.fields.14.annotation'), default=OpRef(name='init.fields.14.default'), default_factory=Non"
        "e, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), Ini"
        "tPlan.Field(name='environment', annotation=OpRef(name='init.fields.15.annotation'), default=OpRef(name='init.f"
        "ields.15.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=Non"
        "e, validate=None, check_type=None), InitPlan.Field(name='kms_key_arn', annotation=OpRef(name='init.fields.16.a"
        "nnotation'), default=OpRef(name='init.fields.16.default'), default_factory=None, init=True, override=False, fi"
        "eld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='tracing_config"
        "', annotation=OpRef(name='init.fields.17.annotation'), default=OpRef(name='init.fields.17.default'), default_f"
        "actory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type="
        "None), InitPlan.Field(name='master_arn', annotation=OpRef(name='init.fields.18.annotation'), default=OpRef(nam"
        "e='init.fields.18.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, c"
        "oerce=None, validate=None, check_type=None), InitPlan.Field(name='revision_id', annotation=OpRef(name='init.fi"
        "elds.19.annotation'), default=OpRef(name='init.fields.19.default'), default_factory=None, init=True, override="
        "False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='layer"
        "s', annotation=OpRef(name='init.fields.20.annotation'), default=OpRef(name='init.fields.20.default'), default_"
        "factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type"
        "=None), InitPlan.Field(name='state', annotation=OpRef(name='init.fields.21.annotation'), default=OpRef(name='i"
        "nit.fields.21.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerc"
        "e=None, validate=None, check_type=None), InitPlan.Field(name='state_reason', annotation=OpRef(name='init.field"
        "s.22.annotation'), default=OpRef(name='init.fields.22.default'), default_factory=None, init=True, override=Fal"
        "se, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='state_re"
        "ason_code', annotation=OpRef(name='init.fields.23.annotation'), default=OpRef(name='init.fields.23.default'), "
        "default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, ch"
        "eck_type=None), InitPlan.Field(name='last_update_status', annotation=OpRef(name='init.fields.24.annotation'), "
        "default=OpRef(name='init.fields.24.default'), default_factory=None, init=True, override=False, field_type=Fiel"
        "dType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='last_update_status_reason',"
        " annotation=OpRef(name='init.fields.25.annotation'), default=OpRef(name='init.fields.25.default'), default_fac"
        "tory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=No"
        "ne), InitPlan.Field(name='last_update_status_reason_code', annotation=OpRef(name='init.fields.26.annotation'),"
        " default=OpRef(name='init.fields.26.default'), default_factory=None, init=True, override=False, field_type=Fie"
        "ldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='file_system_configs', anno"
        "tation=OpRef(name='init.fields.27.annotation'), default=OpRef(name='init.fields.27.default'), default_factory="
        "None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), "
        "InitPlan.Field(name='package_type', annotation=OpRef(name='init.fields.28.annotation'), default=OpRef(name='in"
        "it.fields.28.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce"
        "=None, validate=None, check_type=None), InitPlan.Field(name='image_config_response', annotation=OpRef(name='in"
        "it.fields.29.annotation'), default=OpRef(name='init.fields.29.default'), default_factory=None, init=True, over"
        "ride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='"
        "signing_profile_version_arn', annotation=OpRef(name='init.fields.30.annotation'), default=OpRef(name='init.fie"
        "lds.30.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None,"
        " validate=None, check_type=None), InitPlan.Field(name='signing_job_arn', annotation=OpRef(name='init.fields.31"
        ".annotation'), default=OpRef(name='init.fields.31.default'), default_factory=None, init=True, override=False, "
        "field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='architecture"
        "s', annotation=OpRef(name='init.fields.32.annotation'), default=OpRef(name='init.fields.32.default'), default_"
        "factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type"
        "=None), InitPlan.Field(name='ephemeral_storage', annotation=OpRef(name='init.fields.33.annotation'), default=O"
        "pRef(name='init.fields.33.default'), default_factory=None, init=True, override=False, field_type=FieldType.INS"
        "TANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='snap_start', annotation=OpRef(name='"
        "init.fields.34.annotation'), default=OpRef(name='init.fields.34.default'), default_factory=None, init=True, ov"
        "erride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name"
        "='runtime_version_config', annotation=OpRef(name='init.fields.35.annotation'), default=OpRef(name='init.fields"
        ".35.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, va"
        "lidate=None, check_type=None), InitPlan.Field(name='logging_config', annotation=OpRef(name='init.fields.36.ann"
        "otation'), default=OpRef(name='init.fields.36.default'), default_factory=None, init=True, override=False, fiel"
        "d_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='capacity_provide"
        "r_config', annotation=OpRef(name='init.fields.37.annotation'), default=OpRef(name='init.fields.37.default'), d"
        "efault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, che"
        "ck_type=None), InitPlan.Field(name='config_sha256', annotation=OpRef(name='init.fields.38.annotation'), defaul"
        "t=OpRef(name='init.fields.38.default'), default_factory=None, init=True, override=False, field_type=FieldType."
        "INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='durable_config', annotation=OpRef"
        "(name='init.fields.39.annotation'), default=OpRef(name='init.fields.39.default'), default_factory=None, init=T"
        "rue, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fie"
        "ld(name='tenancy_config', annotation=OpRef(name='init.fields.40.annotation'), default=OpRef(name='init.fields."
        "40.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, val"
        "idate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('function_name', 'function_ar"
        "n', 'runtime', 'role', 'handler', 'code_size', 'description', 'timeout', 'memory_size', 'last_modified', 'code"
        "_sha256', 'version', 'vpc_config', 'dead_letter_config', 'environment', 'kms_key_arn', 'tracing_config', 'mast"
        "er_arn', 'revision_id', 'layers', 'state', 'state_reason', 'state_reason_code', 'last_update_status', 'last_up"
        "date_status_reason', 'last_update_status_reason_code', 'file_system_configs', 'package_type', 'image_config_re"
        "sponse', 'signing_profile_version_arn', 'signing_job_arn', 'architectures', 'ephemeral_storage', 'snap_start',"
        " 'runtime_version_config', 'logging_config', 'capacity_provider_config', 'config_sha256', 'durable_config', 't"
        "enancy_config'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fiel"
        "ds=(ReprPlan.Field(name='function_name', kw_only=True, fn=None), ReprPlan.Field(name='function_arn', kw_only=T"
        "rue, fn=None), ReprPlan.Field(name='runtime', kw_only=True, fn=None), ReprPlan.Field(name='role', kw_only=True"
        ", fn=None), ReprPlan.Field(name='handler', kw_only=True, fn=None), ReprPlan.Field(name='code_size', kw_only=Tr"
        "ue, fn=None), ReprPlan.Field(name='description', kw_only=True, fn=None), ReprPlan.Field(name='timeout', kw_onl"
        "y=True, fn=None), ReprPlan.Field(name='memory_size', kw_only=True, fn=None), ReprPlan.Field(name='last_modifie"
        "d', kw_only=True, fn=None), ReprPlan.Field(name='code_sha256', kw_only=True, fn=None), ReprPlan.Field(name='ve"
        "rsion', kw_only=True, fn=None), ReprPlan.Field(name='vpc_config', kw_only=True, fn=None), ReprPlan.Field(name="
        "'dead_letter_config', kw_only=True, fn=None), ReprPlan.Field(name='environment', kw_only=True, fn=None), ReprP"
        "lan.Field(name='kms_key_arn', kw_only=True, fn=None), ReprPlan.Field(name='tracing_config', kw_only=True, fn=N"
        "one), ReprPlan.Field(name='master_arn', kw_only=True, fn=None), ReprPlan.Field(name='revision_id', kw_only=Tru"
        "e, fn=None), ReprPlan.Field(name='layers', kw_only=True, fn=None), ReprPlan.Field(name='state', kw_only=True, "
        "fn=None), ReprPlan.Field(name='state_reason', kw_only=True, fn=None), ReprPlan.Field(name='state_reason_code',"
        " kw_only=True, fn=None), ReprPlan.Field(name='last_update_status', kw_only=True, fn=None), ReprPlan.Field(name"
        "='last_update_status_reason', kw_only=True, fn=None), ReprPlan.Field(name='last_update_status_reason_code', kw"
        "_only=True, fn=None), ReprPlan.Field(name='file_system_configs', kw_only=True, fn=None), ReprPlan.Field(name='"
        "package_type', kw_only=True, fn=None), ReprPlan.Field(name='image_config_response', kw_only=True, fn=None), Re"
        "prPlan.Field(name='signing_profile_version_arn', kw_only=True, fn=None), ReprPlan.Field(name='signing_job_arn'"
        ", kw_only=True, fn=None), ReprPlan.Field(name='architectures', kw_only=True, fn=None), ReprPlan.Field(name='ep"
        "hemeral_storage', kw_only=True, fn=None), ReprPlan.Field(name='snap_start', kw_only=True, fn=None), ReprPlan.F"
        "ield(name='runtime_version_config', kw_only=True, fn=None), ReprPlan.Field(name='logging_config', kw_only=True"
        ", fn=None), ReprPlan.Field(name='capacity_provider_config', kw_only=True, fn=None), ReprPlan.Field(name='confi"
        "g_sha256', kw_only=True, fn=None), ReprPlan.Field(name='durable_config', kw_only=True, fn=None), ReprPlan.Fiel"
        "d(name='tenancy_config', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='73a6aff22feac7761d197b901075deb9184371c9',
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
        ('ominfra.clouds.aws.models.services.lambda_', 'FunctionConfiguration'),
    ),
)
def _process_dataclass__73a6aff22feac7761d197b901075deb9184371c9():
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
                function_name=self.function_name,
                function_arn=self.function_arn,
                runtime=self.runtime,
                role=self.role,
                handler=self.handler,
                code_size=self.code_size,
                description=self.description,
                timeout=self.timeout,
                memory_size=self.memory_size,
                last_modified=self.last_modified,
                code_sha256=self.code_sha256,
                version=self.version,
                vpc_config=self.vpc_config,
                dead_letter_config=self.dead_letter_config,
                environment=self.environment,
                kms_key_arn=self.kms_key_arn,
                tracing_config=self.tracing_config,
                master_arn=self.master_arn,
                revision_id=self.revision_id,
                layers=self.layers,
                state=self.state,
                state_reason=self.state_reason,
                state_reason_code=self.state_reason_code,
                last_update_status=self.last_update_status,
                last_update_status_reason=self.last_update_status_reason,
                last_update_status_reason_code=self.last_update_status_reason_code,
                file_system_configs=self.file_system_configs,
                package_type=self.package_type,
                image_config_response=self.image_config_response,
                signing_profile_version_arn=self.signing_profile_version_arn,
                signing_job_arn=self.signing_job_arn,
                architectures=self.architectures,
                ephemeral_storage=self.ephemeral_storage,
                snap_start=self.snap_start,
                runtime_version_config=self.runtime_version_config,
                logging_config=self.logging_config,
                capacity_provider_config=self.capacity_provider_config,
                config_sha256=self.config_sha256,
                durable_config=self.durable_config,
                tenancy_config=self.tenancy_config,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.function_name == other.function_name and
                self.function_arn == other.function_arn and
                self.runtime == other.runtime and
                self.role == other.role and
                self.handler == other.handler and
                self.code_size == other.code_size and
                self.description == other.description and
                self.timeout == other.timeout and
                self.memory_size == other.memory_size and
                self.last_modified == other.last_modified and
                self.code_sha256 == other.code_sha256 and
                self.version == other.version and
                self.vpc_config == other.vpc_config and
                self.dead_letter_config == other.dead_letter_config and
                self.environment == other.environment and
                self.kms_key_arn == other.kms_key_arn and
                self.tracing_config == other.tracing_config and
                self.master_arn == other.master_arn and
                self.revision_id == other.revision_id and
                self.layers == other.layers and
                self.state == other.state and
                self.state_reason == other.state_reason and
                self.state_reason_code == other.state_reason_code and
                self.last_update_status == other.last_update_status and
                self.last_update_status_reason == other.last_update_status_reason and
                self.last_update_status_reason_code == other.last_update_status_reason_code and
                self.file_system_configs == other.file_system_configs and
                self.package_type == other.package_type and
                self.image_config_response == other.image_config_response and
                self.signing_profile_version_arn == other.signing_profile_version_arn and
                self.signing_job_arn == other.signing_job_arn and
                self.architectures == other.architectures and
                self.ephemeral_storage == other.ephemeral_storage and
                self.snap_start == other.snap_start and
                self.runtime_version_config == other.runtime_version_config and
                self.logging_config == other.logging_config and
                self.capacity_provider_config == other.capacity_provider_config and
                self.config_sha256 == other.config_sha256 and
                self.durable_config == other.durable_config and
                self.tenancy_config == other.tenancy_config
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'function_name',
            'function_arn',
            'runtime',
            'role',
            'handler',
            'code_size',
            'description',
            'timeout',
            'memory_size',
            'last_modified',
            'code_sha256',
            'version',
            'vpc_config',
            'dead_letter_config',
            'environment',
            'kms_key_arn',
            'tracing_config',
            'master_arn',
            'revision_id',
            'layers',
            'state',
            'state_reason',
            'state_reason_code',
            'last_update_status',
            'last_update_status_reason',
            'last_update_status_reason_code',
            'file_system_configs',
            'package_type',
            'image_config_response',
            'signing_profile_version_arn',
            'signing_job_arn',
            'architectures',
            'ephemeral_storage',
            'snap_start',
            'runtime_version_config',
            'logging_config',
            'capacity_provider_config',
            'config_sha256',
            'durable_config',
            'tenancy_config',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'function_name',
            'function_arn',
            'runtime',
            'role',
            'handler',
            'code_size',
            'description',
            'timeout',
            'memory_size',
            'last_modified',
            'code_sha256',
            'version',
            'vpc_config',
            'dead_letter_config',
            'environment',
            'kms_key_arn',
            'tracing_config',
            'master_arn',
            'revision_id',
            'layers',
            'state',
            'state_reason',
            'state_reason_code',
            'last_update_status',
            'last_update_status_reason',
            'last_update_status_reason_code',
            'file_system_configs',
            'package_type',
            'image_config_response',
            'signing_profile_version_arn',
            'signing_job_arn',
            'architectures',
            'ephemeral_storage',
            'snap_start',
            'runtime_version_config',
            'logging_config',
            'capacity_provider_config',
            'config_sha256',
            'durable_config',
            'tenancy_config',
        }

        def __delattr__(self, name):
            if (
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
                self.function_name,
                self.function_arn,
                self.runtime,
                self.role,
                self.handler,
                self.code_size,
                self.description,
                self.timeout,
                self.memory_size,
                self.last_modified,
                self.code_sha256,
                self.version,
                self.vpc_config,
                self.dead_letter_config,
                self.environment,
                self.kms_key_arn,
                self.tracing_config,
                self.master_arn,
                self.revision_id,
                self.layers,
                self.state,
                self.state_reason,
                self.state_reason_code,
                self.last_update_status,
                self.last_update_status_reason,
                self.last_update_status_reason_code,
                self.file_system_configs,
                self.package_type,
                self.image_config_response,
                self.signing_profile_version_arn,
                self.signing_job_arn,
                self.architectures,
                self.ephemeral_storage,
                self.snap_start,
                self.runtime_version_config,
                self.logging_config,
                self.capacity_provider_config,
                self.config_sha256,
                self.durable_config,
                self.tenancy_config,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            function_name: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            function_arn: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            runtime: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            role: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            handler: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
            code_size: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
            description: __dataclass__init__fields__7__annotation = __dataclass__init__fields__7__default,
            timeout: __dataclass__init__fields__8__annotation = __dataclass__init__fields__8__default,
            memory_size: __dataclass__init__fields__9__annotation = __dataclass__init__fields__9__default,
            last_modified: __dataclass__init__fields__10__annotation = __dataclass__init__fields__10__default,
            code_sha256: __dataclass__init__fields__11__annotation = __dataclass__init__fields__11__default,
            version: __dataclass__init__fields__12__annotation = __dataclass__init__fields__12__default,
            vpc_config: __dataclass__init__fields__13__annotation = __dataclass__init__fields__13__default,
            dead_letter_config: __dataclass__init__fields__14__annotation = __dataclass__init__fields__14__default,
            environment: __dataclass__init__fields__15__annotation = __dataclass__init__fields__15__default,
            kms_key_arn: __dataclass__init__fields__16__annotation = __dataclass__init__fields__16__default,
            tracing_config: __dataclass__init__fields__17__annotation = __dataclass__init__fields__17__default,
            master_arn: __dataclass__init__fields__18__annotation = __dataclass__init__fields__18__default,
            revision_id: __dataclass__init__fields__19__annotation = __dataclass__init__fields__19__default,
            layers: __dataclass__init__fields__20__annotation = __dataclass__init__fields__20__default,
            state: __dataclass__init__fields__21__annotation = __dataclass__init__fields__21__default,
            state_reason: __dataclass__init__fields__22__annotation = __dataclass__init__fields__22__default,
            state_reason_code: __dataclass__init__fields__23__annotation = __dataclass__init__fields__23__default,
            last_update_status: __dataclass__init__fields__24__annotation = __dataclass__init__fields__24__default,
            last_update_status_reason: __dataclass__init__fields__25__annotation = __dataclass__init__fields__25__default,
            last_update_status_reason_code: __dataclass__init__fields__26__annotation = __dataclass__init__fields__26__default,
            file_system_configs: __dataclass__init__fields__27__annotation = __dataclass__init__fields__27__default,
            package_type: __dataclass__init__fields__28__annotation = __dataclass__init__fields__28__default,
            image_config_response: __dataclass__init__fields__29__annotation = __dataclass__init__fields__29__default,
            signing_profile_version_arn: __dataclass__init__fields__30__annotation = __dataclass__init__fields__30__default,
            signing_job_arn: __dataclass__init__fields__31__annotation = __dataclass__init__fields__31__default,
            architectures: __dataclass__init__fields__32__annotation = __dataclass__init__fields__32__default,
            ephemeral_storage: __dataclass__init__fields__33__annotation = __dataclass__init__fields__33__default,
            snap_start: __dataclass__init__fields__34__annotation = __dataclass__init__fields__34__default,
            runtime_version_config: __dataclass__init__fields__35__annotation = __dataclass__init__fields__35__default,
            logging_config: __dataclass__init__fields__36__annotation = __dataclass__init__fields__36__default,
            capacity_provider_config: __dataclass__init__fields__37__annotation = __dataclass__init__fields__37__default,
            config_sha256: __dataclass__init__fields__38__annotation = __dataclass__init__fields__38__default,
            durable_config: __dataclass__init__fields__39__annotation = __dataclass__init__fields__39__default,
            tenancy_config: __dataclass__init__fields__40__annotation = __dataclass__init__fields__40__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'function_name', function_name)
            __dataclass__object_setattr(self, 'function_arn', function_arn)
            __dataclass__object_setattr(self, 'runtime', runtime)
            __dataclass__object_setattr(self, 'role', role)
            __dataclass__object_setattr(self, 'handler', handler)
            __dataclass__object_setattr(self, 'code_size', code_size)
            __dataclass__object_setattr(self, 'description', description)
            __dataclass__object_setattr(self, 'timeout', timeout)
            __dataclass__object_setattr(self, 'memory_size', memory_size)
            __dataclass__object_setattr(self, 'last_modified', last_modified)
            __dataclass__object_setattr(self, 'code_sha256', code_sha256)
            __dataclass__object_setattr(self, 'version', version)
            __dataclass__object_setattr(self, 'vpc_config', vpc_config)
            __dataclass__object_setattr(self, 'dead_letter_config', dead_letter_config)
            __dataclass__object_setattr(self, 'environment', environment)
            __dataclass__object_setattr(self, 'kms_key_arn', kms_key_arn)
            __dataclass__object_setattr(self, 'tracing_config', tracing_config)
            __dataclass__object_setattr(self, 'master_arn', master_arn)
            __dataclass__object_setattr(self, 'revision_id', revision_id)
            __dataclass__object_setattr(self, 'layers', layers)
            __dataclass__object_setattr(self, 'state', state)
            __dataclass__object_setattr(self, 'state_reason', state_reason)
            __dataclass__object_setattr(self, 'state_reason_code', state_reason_code)
            __dataclass__object_setattr(self, 'last_update_status', last_update_status)
            __dataclass__object_setattr(self, 'last_update_status_reason', last_update_status_reason)
            __dataclass__object_setattr(self, 'last_update_status_reason_code', last_update_status_reason_code)
            __dataclass__object_setattr(self, 'file_system_configs', file_system_configs)
            __dataclass__object_setattr(self, 'package_type', package_type)
            __dataclass__object_setattr(self, 'image_config_response', image_config_response)
            __dataclass__object_setattr(self, 'signing_profile_version_arn', signing_profile_version_arn)
            __dataclass__object_setattr(self, 'signing_job_arn', signing_job_arn)
            __dataclass__object_setattr(self, 'architectures', architectures)
            __dataclass__object_setattr(self, 'ephemeral_storage', ephemeral_storage)
            __dataclass__object_setattr(self, 'snap_start', snap_start)
            __dataclass__object_setattr(self, 'runtime_version_config', runtime_version_config)
            __dataclass__object_setattr(self, 'logging_config', logging_config)
            __dataclass__object_setattr(self, 'capacity_provider_config', capacity_provider_config)
            __dataclass__object_setattr(self, 'config_sha256', config_sha256)
            __dataclass__object_setattr(self, 'durable_config', durable_config)
            __dataclass__object_setattr(self, 'tenancy_config', tenancy_config)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"function_name={self.function_name!r}")
            parts.append(f"function_arn={self.function_arn!r}")
            parts.append(f"runtime={self.runtime!r}")
            parts.append(f"role={self.role!r}")
            parts.append(f"handler={self.handler!r}")
            parts.append(f"code_size={self.code_size!r}")
            parts.append(f"description={self.description!r}")
            parts.append(f"timeout={self.timeout!r}")
            parts.append(f"memory_size={self.memory_size!r}")
            parts.append(f"last_modified={self.last_modified!r}")
            parts.append(f"code_sha256={self.code_sha256!r}")
            parts.append(f"version={self.version!r}")
            parts.append(f"vpc_config={self.vpc_config!r}")
            parts.append(f"dead_letter_config={self.dead_letter_config!r}")
            parts.append(f"environment={self.environment!r}")
            parts.append(f"kms_key_arn={self.kms_key_arn!r}")
            parts.append(f"tracing_config={self.tracing_config!r}")
            parts.append(f"master_arn={self.master_arn!r}")
            parts.append(f"revision_id={self.revision_id!r}")
            parts.append(f"layers={self.layers!r}")
            parts.append(f"state={self.state!r}")
            parts.append(f"state_reason={self.state_reason!r}")
            parts.append(f"state_reason_code={self.state_reason_code!r}")
            parts.append(f"last_update_status={self.last_update_status!r}")
            parts.append(f"last_update_status_reason={self.last_update_status_reason!r}")
            parts.append(f"last_update_status_reason_code={self.last_update_status_reason_code!r}")
            parts.append(f"file_system_configs={self.file_system_configs!r}")
            parts.append(f"package_type={self.package_type!r}")
            parts.append(f"image_config_response={self.image_config_response!r}")
            parts.append(f"signing_profile_version_arn={self.signing_profile_version_arn!r}")
            parts.append(f"signing_job_arn={self.signing_job_arn!r}")
            parts.append(f"architectures={self.architectures!r}")
            parts.append(f"ephemeral_storage={self.ephemeral_storage!r}")
            parts.append(f"snap_start={self.snap_start!r}")
            parts.append(f"runtime_version_config={self.runtime_version_config!r}")
            parts.append(f"logging_config={self.logging_config!r}")
            parts.append(f"capacity_provider_config={self.capacity_provider_config!r}")
            parts.append(f"config_sha256={self.config_sha256!r}")
            parts.append(f"durable_config={self.durable_config!r}")
            parts.append(f"tenancy_config={self.tenancy_config!r}")
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
        "Plans(tup=(CopyPlan(fields=('entry_point', 'command', 'working_directory')), EqPlan(fields=('entry_point', 'co"
        "mmand', 'working_directory')), FrozenPlan(fields=('__shape__', 'entry_point', 'command', 'working_directory'),"
        " allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('entry_point', 'command', 'working_director"
        "y'), cache=False), InitPlan(fields=(InitPlan.Field(name='__shape__', annotation=OpRef(name='init.fields.0.anno"
        "tation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS_VAR, coerc"
        "e=None, validate=None, check_type=None), InitPlan.Field(name='entry_point', annotation=OpRef(name='init.fields"
        ".1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False,"
        " field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='command', a"
        "nnotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory"
        "=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),"
        " InitPlan.Field(name='working_directory', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(nam"
        "e='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, co"
        "erce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('entry_point', "
        "'command', 'working_directory'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()"
        "), ReprPlan(fields=(ReprPlan.Field(name='entry_point', kw_only=True, fn=None), ReprPlan.Field(name='command', "
        "kw_only=True, fn=None), ReprPlan.Field(name='working_directory', kw_only=True, fn=None)), id=False, terse=Fals"
        "e, default_fn=None)))"
    ),
    plan_repr_sha1='ae03700d2ed8d061b79f46b2ac2de69041ed914c',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.lambda_', 'ImageConfig'),
    ),
)
def _process_dataclass__ae03700d2ed8d061b79f46b2ac2de69041ed914c():
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
                entry_point=self.entry_point,
                command=self.command,
                working_directory=self.working_directory,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.entry_point == other.entry_point and
                self.command == other.command and
                self.working_directory == other.working_directory
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'entry_point',
            'command',
            'working_directory',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'entry_point',
            'command',
            'working_directory',
        }

        def __delattr__(self, name):
            if (
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
                self.entry_point,
                self.command,
                self.working_directory,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            entry_point: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            command: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            working_directory: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'entry_point', entry_point)
            __dataclass__object_setattr(self, 'command', command)
            __dataclass__object_setattr(self, 'working_directory', working_directory)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"entry_point={self.entry_point!r}")
            parts.append(f"command={self.command!r}")
            parts.append(f"working_directory={self.working_directory!r}")
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
        "Plans(tup=(CopyPlan(fields=('image_config', 'error')), EqPlan(fields=('image_config', 'error')), FrozenPlan(fi"
        "elds=('__shape__', 'image_config', 'error'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields="
        "('image_config', 'error'), cache=False), InitPlan(fields=(InitPlan.Field(name='__shape__', annotation=OpRef(na"
        "me='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=Fiel"
        "dType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='image_config', annotation="
        "OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, ini"
        "t=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan."
        "Field(name='error', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.defau"
        "lt'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=No"
        "ne, check_type=None)), self_param='self', std_params=(), kw_only_params=('image_config', 'error'), frozen=True"
        ", slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='ima"
        "ge_config', kw_only=True, fn=None), ReprPlan.Field(name='error', kw_only=True, fn=None)), id=False, terse=Fals"
        "e, default_fn=None)))"
    ),
    plan_repr_sha1='f187f9f7e4a3a31f7e7c47ced435e80463092461',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.lambda_', 'ImageConfigResponse'),
    ),
)
def _process_dataclass__f187f9f7e4a3a31f7e7c47ced435e80463092461():
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
                image_config=self.image_config,
                error=self.error,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.image_config == other.image_config and
                self.error == other.error
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'image_config',
            'error',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'image_config',
            'error',
        }

        def __delattr__(self, name):
            if (
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
                self.image_config,
                self.error,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            image_config: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            error: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'image_config', image_config)
            __dataclass__object_setattr(self, 'error', error)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"image_config={self.image_config!r}")
            parts.append(f"error={self.error!r}")
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
        "Plans(tup=(CopyPlan(fields=('type', 'message')), EqPlan(fields=('type', 'message')), FrozenPlan(fields=('__sha"
        "pe__', 'type', 'message'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('type', 'message'"
        "), cache=False), InitPlan(fields=(InitPlan.Field(name='__shape__', annotation=OpRef(name='init.fields.0.annota"
        "tion'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS_VAR, coerce="
        "None, validate=None, check_type=None), InitPlan.Field(name='type', annotation=OpRef(name='init.fields.1.annota"
        "tion'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_ty"
        "pe=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='message', annotation"
        "=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, in"
        "it=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_pa"
        "ram='self', std_params=(), kw_only_params=('type', 'message'), frozen=True, slots=False, post_init_params=None"
        ", init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='type', kw_only=True, fn=None), ReprPlan"
        ".Field(name='message', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='4727185bc15d0b892fa2952d4b56ab294b06b6b7',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.lambda_', 'InvalidParameterValueException'),
        ('ominfra.clouds.aws.models.services.lambda_', 'ServiceException'),
    ),
)
def _process_dataclass__4727185bc15d0b892fa2952d4b56ab294b06b6b7():
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
                type=self.type,
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
                self.type == other.type and
                self.message == other.message
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'type',
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
            'type',
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
                self.type,
                self.message,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            type: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            message: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'type', type)
            __dataclass__object_setattr(self, 'message', message)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"type={self.type!r}")
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
        "Plans(tup=(CopyPlan(fields=('capacity_provider_arn', 'per_execution_environment_max_concurrency', 'execution_e"
        "nvironment_memory_gi_b_per_v_cpu')), EqPlan(fields=('capacity_provider_arn', 'per_execution_environment_max_co"
        "ncurrency', 'execution_environment_memory_gi_b_per_v_cpu')), FrozenPlan(fields=('__shape__', 'capacity_provide"
        "r_arn', 'per_execution_environment_max_concurrency', 'execution_environment_memory_gi_b_per_v_cpu'), allow_dyn"
        "amic_dunder_attrs=False), HashPlan(action='add', fields=('capacity_provider_arn', 'per_execution_environment_m"
        "ax_concurrency', 'execution_environment_memory_gi_b_per_v_cpu'), cache=False), InitPlan(fields=(InitPlan.Field"
        "(name='__shape__', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init"
        "=True, override=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan."
        "Field(name='capacity_provider_arn', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_f"
        "actory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type="
        "None), InitPlan.Field(name='per_execution_environment_max_concurrency', annotation=OpRef(name='init.fields.2.a"
        "nnotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, fie"
        "ld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='execution_envir"
        "onment_memory_gi_b_per_v_cpu', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fie"
        "lds.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, "
        "validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('capacity_provider_arn', '"
        "per_execution_environment_max_concurrency', 'execution_environment_memory_gi_b_per_v_cpu'), frozen=True, slots"
        "=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='capacity_p"
        "rovider_arn', kw_only=True, fn=None), ReprPlan.Field(name='per_execution_environment_max_concurrency', kw_only"
        "=True, fn=None), ReprPlan.Field(name='execution_environment_memory_gi_b_per_v_cpu', kw_only=True, fn=None)), i"
        "d=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='02fae62a0f61feae0ec5fbd59f6801f513d2c3e6',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.lambda_', 'LambdaManagedInstancesCapacityProviderConfig'),
    ),
)
def _process_dataclass__02fae62a0f61feae0ec5fbd59f6801f513d2c3e6():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
                capacity_provider_arn=self.capacity_provider_arn,
                per_execution_environment_max_concurrency=self.per_execution_environment_max_concurrency,
                execution_environment_memory_gi_b_per_v_cpu=self.execution_environment_memory_gi_b_per_v_cpu,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.capacity_provider_arn == other.capacity_provider_arn and
                self.per_execution_environment_max_concurrency == other.per_execution_environment_max_concurrency and
                self.execution_environment_memory_gi_b_per_v_cpu == other.execution_environment_memory_gi_b_per_v_cpu
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'capacity_provider_arn',
            'per_execution_environment_max_concurrency',
            'execution_environment_memory_gi_b_per_v_cpu',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'capacity_provider_arn',
            'per_execution_environment_max_concurrency',
            'execution_environment_memory_gi_b_per_v_cpu',
        }

        def __delattr__(self, name):
            if (
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
                self.capacity_provider_arn,
                self.per_execution_environment_max_concurrency,
                self.execution_environment_memory_gi_b_per_v_cpu,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            capacity_provider_arn: __dataclass__init__fields__1__annotation,
            per_execution_environment_max_concurrency: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            execution_environment_memory_gi_b_per_v_cpu: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'capacity_provider_arn', capacity_provider_arn)
            __dataclass__object_setattr(self, 'per_execution_environment_max_concurrency', per_execution_environment_max_concurrency)
            __dataclass__object_setattr(self, 'execution_environment_memory_gi_b_per_v_cpu', execution_environment_memory_gi_b_per_v_cpu)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"capacity_provider_arn={self.capacity_provider_arn!r}")
            parts.append(f"per_execution_environment_max_concurrency={self.per_execution_environment_max_concurrency!r}")
            parts.append(f"execution_environment_memory_gi_b_per_v_cpu={self.execution_environment_memory_gi_b_per_v_cpu!r}")
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
        "Plans(tup=(CopyPlan(fields=('arn', 'code_size', 'signing_profile_version_arn', 'signing_job_arn')), EqPlan(fie"
        "lds=('arn', 'code_size', 'signing_profile_version_arn', 'signing_job_arn')), FrozenPlan(fields=('__shape__', '"
        "arn', 'code_size', 'signing_profile_version_arn', 'signing_job_arn'), allow_dynamic_dunder_attrs=False), HashP"
        "lan(action='add', fields=('arn', 'code_size', 'signing_profile_version_arn', 'signing_job_arn'), cache=False),"
        " InitPlan(fields=(InitPlan.Field(name='__shape__', annotation=OpRef(name='init.fields.0.annotation'), default="
        "None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=N"
        "one, check_type=None), InitPlan.Field(name='arn', annotation=OpRef(name='init.fields.1.annotation'), default=O"
        "pRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INST"
        "ANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='code_size', annotation=OpRef(name='in"
        "it.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, overri"
        "de=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='si"
        "gning_profile_version_arn', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields"
        ".3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, val"
        "idate=None, check_type=None), InitPlan.Field(name='signing_job_arn', annotation=OpRef(name='init.fields.4.anno"
        "tation'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, override=False, field_"
        "type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_o"
        "nly_params=('arn', 'code_size', 'signing_profile_version_arn', 'signing_job_arn'), frozen=True, slots=False, p"
        "ost_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='arn', kw_only=True,"
        " fn=None), ReprPlan.Field(name='code_size', kw_only=True, fn=None), ReprPlan.Field(name='signing_profile_versi"
        "on_arn', kw_only=True, fn=None), ReprPlan.Field(name='signing_job_arn', kw_only=True, fn=None)), id=False, ter"
        "se=False, default_fn=None)))"
    ),
    plan_repr_sha1='e1e72a9e7b3e49b7385462d8740c9876d598e19a',
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
        ('ominfra.clouds.aws.models.services.lambda_', 'Layer'),
    ),
)
def _process_dataclass__e1e72a9e7b3e49b7385462d8740c9876d598e19a():
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
                arn=self.arn,
                code_size=self.code_size,
                signing_profile_version_arn=self.signing_profile_version_arn,
                signing_job_arn=self.signing_job_arn,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.arn == other.arn and
                self.code_size == other.code_size and
                self.signing_profile_version_arn == other.signing_profile_version_arn and
                self.signing_job_arn == other.signing_job_arn
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'arn',
            'code_size',
            'signing_profile_version_arn',
            'signing_job_arn',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'code_size',
            'signing_profile_version_arn',
            'signing_job_arn',
        }

        def __delattr__(self, name):
            if (
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
                self.code_size,
                self.signing_profile_version_arn,
                self.signing_job_arn,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            arn: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            code_size: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            signing_profile_version_arn: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            signing_job_arn: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'arn', arn)
            __dataclass__object_setattr(self, 'code_size', code_size)
            __dataclass__object_setattr(self, 'signing_profile_version_arn', signing_profile_version_arn)
            __dataclass__object_setattr(self, 'signing_job_arn', signing_job_arn)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"arn={self.arn!r}")
            parts.append(f"code_size={self.code_size!r}")
            parts.append(f"signing_profile_version_arn={self.signing_profile_version_arn!r}")
            parts.append(f"signing_job_arn={self.signing_job_arn!r}")
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
        "Plans(tup=(CopyPlan(fields=('master_region', 'function_version', 'marker', 'max_items')), EqPlan(fields=('mast"
        "er_region', 'function_version', 'marker', 'max_items')), FrozenPlan(fields=('__shape__', 'master_region', 'fun"
        "ction_version', 'marker', 'max_items'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('mas"
        "ter_region', 'function_version', 'marker', 'max_items'), cache=False), InitPlan(fields=(InitPlan.Field(name='_"
        "_shape__', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, o"
        "verride=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(na"
        "me='master_region', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.defau"
        "lt'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=No"
        "ne, check_type=None), InitPlan.Field(name='function_version', annotation=OpRef(name='init.fields.2.annotation'"
        "), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=Fi"
        "eldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='marker', annotation=OpRef"
        "(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=Tru"
        "e, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field"
        "(name='max_items', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.defaul"
        "t'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=Non"
        "e, check_type=None)), self_param='self', std_params=(), kw_only_params=('master_region', 'function_version', '"
        "marker', 'max_items'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPla"
        "n(fields=(ReprPlan.Field(name='master_region', kw_only=True, fn=None), ReprPlan.Field(name='function_version',"
        " kw_only=True, fn=None), ReprPlan.Field(name='marker', kw_only=True, fn=None), ReprPlan.Field(name='max_items'"
        ", kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='380cb4006162c5599b728986e1364c0bb6b53532',
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
        ('ominfra.clouds.aws.models.services.lambda_', 'ListFunctionsRequest'),
    ),
)
def _process_dataclass__380cb4006162c5599b728986e1364c0bb6b53532():
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
                master_region=self.master_region,
                function_version=self.function_version,
                marker=self.marker,
                max_items=self.max_items,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.master_region == other.master_region and
                self.function_version == other.function_version and
                self.marker == other.marker and
                self.max_items == other.max_items
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'master_region',
            'function_version',
            'marker',
            'max_items',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'master_region',
            'function_version',
            'marker',
            'max_items',
        }

        def __delattr__(self, name):
            if (
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
                self.master_region,
                self.function_version,
                self.marker,
                self.max_items,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            master_region: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            function_version: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            marker: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            max_items: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'master_region', master_region)
            __dataclass__object_setattr(self, 'function_version', function_version)
            __dataclass__object_setattr(self, 'marker', marker)
            __dataclass__object_setattr(self, 'max_items', max_items)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"master_region={self.master_region!r}")
            parts.append(f"function_version={self.function_version!r}")
            parts.append(f"marker={self.marker!r}")
            parts.append(f"max_items={self.max_items!r}")
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
        "Plans(tup=(CopyPlan(fields=('next_marker', 'functions')), EqPlan(fields=('next_marker', 'functions')), FrozenP"
        "lan(fields=('__shape__', 'next_marker', 'functions'), allow_dynamic_dunder_attrs=False), HashPlan(action='add'"
        ", fields=('next_marker', 'functions'), cache=False), InitPlan(fields=(InitPlan.Field(name='__shape__', annotat"
        "ion=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, fie"
        "ld_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='next_marker', "
        "annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factor"
        "y=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)"
        ", InitPlan.Field(name='functions', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init"
        ".fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=No"
        "ne, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('next_marker', 'functi"
        "ons'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPl"
        "an.Field(name='next_marker', kw_only=True, fn=None), ReprPlan.Field(name='functions', kw_only=True, fn=None)),"
        " id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='eadc397a64213fa413966469ed9bbbd79b79aa63',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.lambda_', 'ListFunctionsResponse'),
    ),
)
def _process_dataclass__eadc397a64213fa413966469ed9bbbd79b79aa63():
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
                next_marker=self.next_marker,
                functions=self.functions,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.next_marker == other.next_marker and
                self.functions == other.functions
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'next_marker',
            'functions',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'next_marker',
            'functions',
        }

        def __delattr__(self, name):
            if (
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
                self.next_marker,
                self.functions,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            next_marker: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            functions: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'next_marker', next_marker)
            __dataclass__object_setattr(self, 'functions', functions)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"next_marker={self.next_marker!r}")
            parts.append(f"functions={self.functions!r}")
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
        "Plans(tup=(CopyPlan(fields=('log_format', 'application_log_level', 'system_log_level', 'log_group')), EqPlan(f"
        "ields=('log_format', 'application_log_level', 'system_log_level', 'log_group')), FrozenPlan(fields=('__shape__"
        "', 'log_format', 'application_log_level', 'system_log_level', 'log_group'), allow_dynamic_dunder_attrs=False),"
        " HashPlan(action='add', fields=('log_format', 'application_log_level', 'system_log_level', 'log_group'), cache"
        "=False), InitPlan(fields=(InitPlan.Field(name='__shape__', annotation=OpRef(name='init.fields.0.annotation'), "
        "default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS_VAR, coerce=None, va"
        "lidate=None, check_type=None), InitPlan.Field(name='log_format', annotation=OpRef(name='init.fields.1.annotati"
        "on'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type"
        "=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='application_log_level'"
        ", annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_fact"
        "ory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=Non"
        "e), InitPlan.Field(name='system_log_level', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(n"
        "ame='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, "
        "coerce=None, validate=None, check_type=None), InitPlan.Field(name='log_group', annotation=OpRef(name='init.fie"
        "lds.4.annotation'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, override=Fal"
        "se, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_param"
        "s=(), kw_only_params=('log_format', 'application_log_level', 'system_log_level', 'log_group'), frozen=True, sl"
        "ots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='log_for"
        "mat', kw_only=True, fn=None), ReprPlan.Field(name='application_log_level', kw_only=True, fn=None), ReprPlan.Fi"
        "eld(name='system_log_level', kw_only=True, fn=None), ReprPlan.Field(name='log_group', kw_only=True, fn=None)),"
        " id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='3789e83e8304a69b04615c05af44097dc01b657f',
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
        ('ominfra.clouds.aws.models.services.lambda_', 'LoggingConfig'),
    ),
)
def _process_dataclass__3789e83e8304a69b04615c05af44097dc01b657f():
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
                log_format=self.log_format,
                application_log_level=self.application_log_level,
                system_log_level=self.system_log_level,
                log_group=self.log_group,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.log_format == other.log_format and
                self.application_log_level == other.application_log_level and
                self.system_log_level == other.system_log_level and
                self.log_group == other.log_group
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'log_format',
            'application_log_level',
            'system_log_level',
            'log_group',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'log_format',
            'application_log_level',
            'system_log_level',
            'log_group',
        }

        def __delattr__(self, name):
            if (
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
                self.log_format,
                self.application_log_level,
                self.system_log_level,
                self.log_group,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            log_format: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            application_log_level: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            system_log_level: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            log_group: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'log_format', log_format)
            __dataclass__object_setattr(self, 'application_log_level', application_log_level)
            __dataclass__object_setattr(self, 'system_log_level', system_log_level)
            __dataclass__object_setattr(self, 'log_group', log_group)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"log_format={self.log_format!r}")
            parts.append(f"application_log_level={self.application_log_level!r}")
            parts.append(f"system_log_level={self.system_log_level!r}")
            parts.append(f"log_group={self.log_group!r}")
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
        "Plans(tup=(CopyPlan(fields=('runtime_version_arn', 'error')), EqPlan(fields=('runtime_version_arn', 'error')),"
        " FrozenPlan(fields=('__shape__', 'runtime_version_arn', 'error'), allow_dynamic_dunder_attrs=False), HashPlan("
        "action='add', fields=('runtime_version_arn', 'error'), cache=False), InitPlan(fields=(InitPlan.Field(name='__s"
        "hape__', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, ove"
        "rride=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name"
        "='runtime_version_arn', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.d"
        "efault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validat"
        "e=None, check_type=None), InitPlan.Field(name='error', annotation=OpRef(name='init.fields.2.annotation'), defa"
        "ult=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType"
        ".INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('r"
        "untime_version_arn', 'error'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()),"
        " ReprPlan(fields=(ReprPlan.Field(name='runtime_version_arn', kw_only=True, fn=None), ReprPlan.Field(name='erro"
        "r', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='f7b1a123934c098577316105a6d2620d7d9e6557',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.lambda_', 'RuntimeVersionConfig'),
    ),
)
def _process_dataclass__f7b1a123934c098577316105a6d2620d7d9e6557():
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
                runtime_version_arn=self.runtime_version_arn,
                error=self.error,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.runtime_version_arn == other.runtime_version_arn and
                self.error == other.error
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'runtime_version_arn',
            'error',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'runtime_version_arn',
            'error',
        }

        def __delattr__(self, name):
            if (
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
                self.runtime_version_arn,
                self.error,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            runtime_version_arn: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            error: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'runtime_version_arn', runtime_version_arn)
            __dataclass__object_setattr(self, 'error', error)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"runtime_version_arn={self.runtime_version_arn!r}")
            parts.append(f"error={self.error!r}")
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
        "Plans(tup=(CopyPlan(fields=('apply_on', 'optimization_status')), EqPlan(fields=('apply_on', 'optimization_stat"
        "us')), FrozenPlan(fields=('__shape__', 'apply_on', 'optimization_status'), allow_dynamic_dunder_attrs=False), "
        "HashPlan(action='add', fields=('apply_on', 'optimization_status'), cache=False), InitPlan(fields=(InitPlan.Fie"
        "ld(name='__shape__', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, in"
        "it=True, override=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPla"
        "n.Field(name='apply_on', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1."
        "default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valida"
        "te=None, check_type=None), InitPlan.Field(name='optimization_status', annotation=OpRef(name='init.fields.2.ann"
        "otation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field"
        "_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_"
        "only_params=('apply_on', 'optimization_status'), frozen=True, slots=False, post_init_params=None, init_fns=(),"
        " validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='apply_on', kw_only=True, fn=None), ReprPlan.Field(nam"
        "e='optimization_status', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='019cda7bb51f31d049f4fa706f3c46d80940f395',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.lambda_', 'SnapStartResponse'),
    ),
)
def _process_dataclass__019cda7bb51f31d049f4fa706f3c46d80940f395():
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
                apply_on=self.apply_on,
                optimization_status=self.optimization_status,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.apply_on == other.apply_on and
                self.optimization_status == other.optimization_status
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'apply_on',
            'optimization_status',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'apply_on',
            'optimization_status',
        }

        def __delattr__(self, name):
            if (
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
                self.apply_on,
                self.optimization_status,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            apply_on: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            optimization_status: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'apply_on', apply_on)
            __dataclass__object_setattr(self, 'optimization_status', optimization_status)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"apply_on={self.apply_on!r}")
            parts.append(f"optimization_status={self.optimization_status!r}")
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
        "Plans(tup=(CopyPlan(fields=('tenant_isolation_mode',)), EqPlan(fields=('tenant_isolation_mode',)), FrozenPlan("
        "fields=('__shape__', 'tenant_isolation_mode'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', field"
        "s=('tenant_isolation_mode',), cache=False), InitPlan(fields=(InitPlan.Field(name='__shape__', annotation=OpRef"
        "(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=F"
        "ieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='tenant_isolation_mode',"
        " annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=Fa"
        "lse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_para"
        "ms=(), kw_only_params=('tenant_isolation_mode',), frozen=True, slots=False, post_init_params=None, init_fns=()"
        ", validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='tenant_isolation_mode', kw_only=True, fn=None),), id"
        "=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='acba8e67f2ea6e7d9058cd7cead360bc0a73cf1a',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.lambda_', 'TenancyConfig'),
    ),
)
def _process_dataclass__acba8e67f2ea6e7d9058cd7cead360bc0a73cf1a():
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
                tenant_isolation_mode=self.tenant_isolation_mode,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.tenant_isolation_mode == other.tenant_isolation_mode
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'tenant_isolation_mode',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'tenant_isolation_mode',
        }

        def __delattr__(self, name):
            if (
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
                self.tenant_isolation_mode,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            tenant_isolation_mode: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'tenant_isolation_mode', tenant_isolation_mode)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"tenant_isolation_mode={self.tenant_isolation_mode!r}")
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
        "Plans(tup=(CopyPlan(fields=('retry_after_seconds', 'type', 'message', 'reason')), EqPlan(fields=('retry_after_"
        "seconds', 'type', 'message', 'reason')), FrozenPlan(fields=('__shape__', 'retry_after_seconds', 'type', 'messa"
        "ge', 'reason'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('retry_after_seconds', 'type"
        "', 'message', 'reason'), cache=False), InitPlan(fields=(InitPlan.Field(name='__shape__', annotation=OpRef(name"
        "='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldT"
        "ype.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='retry_after_seconds', annota"
        "tion=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None"
        ", init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), Init"
        "Plan.Field(name='type', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.d"
        "efault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validat"
        "e=None, check_type=None), InitPlan.Field(name='message', annotation=OpRef(name='init.fields.3.annotation'), de"
        "fault=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldTy"
        "pe.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='reason', annotation=OpRef(name"
        "='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, ov"
        "erride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self',"
        " std_params=(), kw_only_params=('retry_after_seconds', 'type', 'message', 'reason'), frozen=True, slots=False,"
        " post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='retry_after_secon"
        "ds', kw_only=True, fn=None), ReprPlan.Field(name='type', kw_only=True, fn=None), ReprPlan.Field(name='message'"
        ", kw_only=True, fn=None), ReprPlan.Field(name='reason', kw_only=True, fn=None)), id=False, terse=False, defaul"
        "t_fn=None)))"
    ),
    plan_repr_sha1='79dadd11fd00d21c8fe99901d2f1bb38785142ff',
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
        ('ominfra.clouds.aws.models.services.lambda_', 'TooManyRequestsException'),
    ),
)
def _process_dataclass__79dadd11fd00d21c8fe99901d2f1bb38785142ff():
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
                retry_after_seconds=self.retry_after_seconds,
                type=self.type,
                message=self.message,
                reason=self.reason,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.retry_after_seconds == other.retry_after_seconds and
                self.type == other.type and
                self.message == other.message and
                self.reason == other.reason
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'retry_after_seconds',
            'type',
            'message',
            'reason',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'retry_after_seconds',
            'type',
            'message',
            'reason',
        }

        def __delattr__(self, name):
            if (
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
                self.retry_after_seconds,
                self.type,
                self.message,
                self.reason,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            retry_after_seconds: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            type: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            message: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            reason: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'retry_after_seconds', retry_after_seconds)
            __dataclass__object_setattr(self, 'type', type)
            __dataclass__object_setattr(self, 'message', message)
            __dataclass__object_setattr(self, 'reason', reason)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"retry_after_seconds={self.retry_after_seconds!r}")
            parts.append(f"type={self.type!r}")
            parts.append(f"message={self.message!r}")
            parts.append(f"reason={self.reason!r}")
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
        "Plans(tup=(CopyPlan(fields=('mode',)), EqPlan(fields=('mode',)), FrozenPlan(fields=('__shape__', 'mode'), allo"
        "w_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('mode',), cache=False), InitPlan(fields=(InitPla"
        "n.Field(name='__shape__', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=Non"
        "e, init=True, override=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), In"
        "itPlan.Field(name='mode', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1"
        ".default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valid"
        "ate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('mode',), frozen=True, slots=Fa"
        "lse, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='mode', kw_onl"
        "y=True, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='3e1414118d801b3653e991849c989db02da4f8ab',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ominfra.clouds.aws.models.services.lambda_', 'TracingConfigResponse'),
    ),
)
def _process_dataclass__3e1414118d801b3653e991849c989db02da4f8ab():
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
                mode=self.mode,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.mode == other.mode
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'mode',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'mode',
        }

        def __delattr__(self, name):
            if (
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
                self.mode,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            mode: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'mode', mode)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"mode={self.mode!r}")
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
        "Plans(tup=(CopyPlan(fields=('subnet_ids', 'security_group_ids', 'vpc_id', 'ipv6_allowed_for_dual_stack')), EqP"
        "lan(fields=('subnet_ids', 'security_group_ids', 'vpc_id', 'ipv6_allowed_for_dual_stack')), FrozenPlan(fields=("
        "'__shape__', 'subnet_ids', 'security_group_ids', 'vpc_id', 'ipv6_allowed_for_dual_stack'), allow_dynamic_dunde"
        "r_attrs=False), HashPlan(action='add', fields=('subnet_ids', 'security_group_ids', 'vpc_id', 'ipv6_allowed_for"
        "_dual_stack'), cache=False), InitPlan(fields=(InitPlan.Field(name='__shape__', annotation=OpRef(name='init.fie"
        "lds.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS_"
        "VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='subnet_ids', annotation=OpRef(name='in"
        "it.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, overri"
        "de=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='se"
        "curity_group_ids', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.defaul"
        "t'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=Non"
        "e, check_type=None), InitPlan.Field(name='vpc_id', annotation=OpRef(name='init.fields.3.annotation'), default="
        "OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INS"
        "TANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='ipv6_allowed_for_dual_stack', annota"
        "tion=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_factory=None"
        ", init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), sel"
        "f_param='self', std_params=(), kw_only_params=('subnet_ids', 'security_group_ids', 'vpc_id', 'ipv6_allowed_for"
        "_dual_stack'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields"
        "=(ReprPlan.Field(name='subnet_ids', kw_only=True, fn=None), ReprPlan.Field(name='security_group_ids', kw_only="
        "True, fn=None), ReprPlan.Field(name='vpc_id', kw_only=True, fn=None), ReprPlan.Field(name='ipv6_allowed_for_du"
        "al_stack', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='adc0193a1c11249e7e0ecd78b9755bc5f0aaada7',
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
        ('ominfra.clouds.aws.models.services.lambda_', 'VpcConfigResponse'),
    ),
)
def _process_dataclass__adc0193a1c11249e7e0ecd78b9755bc5f0aaada7():
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
                subnet_ids=self.subnet_ids,
                security_group_ids=self.security_group_ids,
                vpc_id=self.vpc_id,
                ipv6_allowed_for_dual_stack=self.ipv6_allowed_for_dual_stack,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.subnet_ids == other.subnet_ids and
                self.security_group_ids == other.security_group_ids and
                self.vpc_id == other.vpc_id and
                self.ipv6_allowed_for_dual_stack == other.ipv6_allowed_for_dual_stack
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            '__shape__',
            'subnet_ids',
            'security_group_ids',
            'vpc_id',
            'ipv6_allowed_for_dual_stack',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'subnet_ids',
            'security_group_ids',
            'vpc_id',
            'ipv6_allowed_for_dual_stack',
        }

        def __delattr__(self, name):
            if (
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
                self.subnet_ids,
                self.security_group_ids,
                self.vpc_id,
                self.ipv6_allowed_for_dual_stack,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            subnet_ids: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            security_group_ids: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            vpc_id: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            ipv6_allowed_for_dual_stack: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'subnet_ids', subnet_ids)
            __dataclass__object_setattr(self, 'security_group_ids', security_group_ids)
            __dataclass__object_setattr(self, 'vpc_id', vpc_id)
            __dataclass__object_setattr(self, 'ipv6_allowed_for_dual_stack', ipv6_allowed_for_dual_stack)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"subnet_ids={self.subnet_ids!r}")
            parts.append(f"security_group_ids={self.security_group_ids!r}")
            parts.append(f"vpc_id={self.vpc_id!r}")
            parts.append(f"ipv6_allowed_for_dual_stack={self.ipv6_allowed_for_dual_stack!r}")
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
