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
        "Plans(tup=(CopyPlan(fields=('id', 'choices', 'created', 'model', 'object', 'service_tier', 'system_fingerprint"
        "', 'usage', 'obfuscation')), EqPlan(fields=('id', 'choices', 'created', 'model', 'object', 'service_tier', 'sy"
        "stem_fingerprint', 'usage', 'obfuscation')), FrozenPlan(fields=('id', 'choices', 'created', 'model', 'object',"
        " 'service_tier', 'system_fingerprint', 'usage', 'obfuscation'), allow_dynamic_dunder_attrs=False), HashPlan(ac"
        "tion='add', fields=('id', 'choices', 'created', 'model', 'object', 'service_tier', 'system_fingerprint', 'usag"
        "e', 'obfuscation'), cache=False), InitPlan(fields=(InitPlan.Field(name='id', annotation=OpRef(name='init.field"
        "s.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE"
        ", coerce=None, validate=None, check_type=None), InitPlan.Field(name='choices', annotation=OpRef(name='init.fie"
        "lds.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTAN"
        "CE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='created', annotation=OpRef(name='init.f"
        "ields.2.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INST"
        "ANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='model', annotation=OpRef(name='init.f"
        "ields.3.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INST"
        "ANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='object', annotation=OpRef(name='init."
        "fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, override="
        "False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='servi"
        "ce_tier', annotation=OpRef(name='init.fields.5.annotation'), default=OpRef(name='init.fields.5.default'), defa"
        "ult_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_"
        "type=None), InitPlan.Field(name='system_fingerprint', annotation=OpRef(name='init.fields.6.annotation'), defau"
        "lt=OpRef(name='init.fields.6.default'), default_factory=None, init=True, override=False, field_type=FieldType."
        "INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='usage', annotation=OpRef(name='in"
        "it.fields.7.annotation'), default=OpRef(name='init.fields.7.default'), default_factory=None, init=True, overri"
        "de=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='ob"
        "fuscation', annotation=OpRef(name='init.fields.8.annotation'), default=OpRef(name='init.fields.8.default'), de"
        "fault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, chec"
        "k_type=None)), self_param='self', std_params=(), kw_only_params=('id', 'choices', 'created', 'model', 'object'"
        ", 'service_tier', 'system_fingerprint', 'usage', 'obfuscation'), frozen=True, slots=False, post_init_params=No"
        "ne, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='id', kw_only=True, fn=None), ReprPlan"
        ".Field(name='choices', kw_only=True, fn=None), ReprPlan.Field(name='created', kw_only=True, fn=None), ReprPlan"
        ".Field(name='model', kw_only=True, fn=None), ReprPlan.Field(name='service_tier', kw_only=True, fn=None), ReprP"
        "lan.Field(name='system_fingerprint', kw_only=True, fn=None), ReprPlan.Field(name='usage', kw_only=True, fn=Non"
        "e), ReprPlan.Field(name='obfuscation', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='1528694c451d444dbd9a99d7712a716f1a99dbd1',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
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
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.chatcompletion.chunk', 'ChatCompletionChunk'),
    ),
)
def _process_dataclass__1528694c451d444dbd9a99d7712a716f1a99dbd1():
    def _process_dataclass(
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
        __dataclass__init__fields__6__annotation,
        __dataclass__init__fields__6__default,
        __dataclass__init__fields__7__annotation,
        __dataclass__init__fields__7__default,
        __dataclass__init__fields__8__annotation,
        __dataclass__init__fields__8__default,
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
                choices=self.choices,
                created=self.created,
                model=self.model,
                object=self.object,
                service_tier=self.service_tier,
                system_fingerprint=self.system_fingerprint,
                usage=self.usage,
                obfuscation=self.obfuscation,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
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
                self.choices == other.choices and
                self.created == other.created and
                self.model == other.model and
                self.object == other.object and
                self.service_tier == other.service_tier and
                self.system_fingerprint == other.system_fingerprint and
                self.usage == other.usage and
                self.obfuscation == other.obfuscation
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'id',
            'choices',
            'created',
            'model',
            'object',
            'service_tier',
            'system_fingerprint',
            'usage',
            'obfuscation',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'choices',
            'created',
            'model',
            'object',
            'service_tier',
            'system_fingerprint',
            'usage',
            'obfuscation',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.choices,
                self.created,
                self.model,
                self.object,
                self.service_tier,
                self.system_fingerprint,
                self.usage,
                self.obfuscation,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            id: __dataclass__init__fields__0__annotation,
            choices: __dataclass__init__fields__1__annotation,
            created: __dataclass__init__fields__2__annotation,
            model: __dataclass__init__fields__3__annotation,
            object: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            service_tier: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
            system_fingerprint: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
            usage: __dataclass__init__fields__7__annotation = __dataclass__init__fields__7__default,
            obfuscation: __dataclass__init__fields__8__annotation = __dataclass__init__fields__8__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'choices', choices)
            __dataclass__object_setattr(self, 'created', created)
            __dataclass__object_setattr(self, 'model', model)
            __dataclass__object_setattr(self, 'object', object)
            __dataclass__object_setattr(self, 'service_tier', service_tier)
            __dataclass__object_setattr(self, 'system_fingerprint', system_fingerprint)
            __dataclass__object_setattr(self, 'usage', usage)
            __dataclass__object_setattr(self, 'obfuscation', obfuscation)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"id={self.id!r}")
            parts.append(f"choices={self.choices!r}")
            parts.append(f"created={self.created!r}")
            parts.append(f"model={self.model!r}")
            parts.append(f"service_tier={self.service_tier!r}")
            parts.append(f"system_fingerprint={self.system_fingerprint!r}")
            parts.append(f"usage={self.usage!r}")
            parts.append(f"obfuscation={self.obfuscation!r}")
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
        "Plans(tup=(CopyPlan(fields=('delta', 'finish_reason', 'index', 'logprobs')), EqPlan(fields=('delta', 'finish_r"
        "eason', 'index', 'logprobs')), FrozenPlan(fields=('delta', 'finish_reason', 'index', 'logprobs'), allow_dynami"
        "c_dunder_attrs=False), HashPlan(action='add', fields=('delta', 'finish_reason', 'index', 'logprobs'), cache=Fa"
        "lse), InitPlan(fields=(InitPlan.Field(name='delta', annotation=OpRef(name='init.fields.0.annotation'), default"
        "=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=N"
        "one, check_type=None), InitPlan.Field(name='finish_reason', annotation=OpRef(name='init.fields.1.annotation'),"
        " default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=Fiel"
        "dType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='index', annotation=OpRef(na"
        "me='init.fields.2.annotation'), default=None, default_factory=None, init=True, override=False, field_type=Fiel"
        "dType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='logprobs', annotation=OpRef"
        "(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=Tru"
        "e, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='s"
        "elf', std_params=(), kw_only_params=('delta', 'finish_reason', 'index', 'logprobs'), frozen=True, slots=False,"
        " post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='delta', kw_only=T"
        "rue, fn=None), ReprPlan.Field(name='finish_reason', kw_only=True, fn=None), ReprPlan.Field(name='index', kw_on"
        "ly=True, fn=None), ReprPlan.Field(name='logprobs', kw_only=True, fn=None)), id=False, terse=False, default_fn="
        "None)))"
    ),
    plan_repr_sha1='b51ffbeca51133b17d92cc2ab8fc3403de71e202',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.chatcompletion.chunk', 'ChatCompletionChunkChoice'),
    ),
)
def _process_dataclass__b51ffbeca51133b17d92cc2ab8fc3403de71e202():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
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
                delta=self.delta,
                finish_reason=self.finish_reason,
                index=self.index,
                logprobs=self.logprobs,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.delta == other.delta and
                self.finish_reason == other.finish_reason and
                self.index == other.index and
                self.logprobs == other.logprobs
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'delta',
            'finish_reason',
            'index',
            'logprobs',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'delta',
            'finish_reason',
            'index',
            'logprobs',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.delta,
                self.finish_reason,
                self.index,
                self.logprobs,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            delta: __dataclass__init__fields__0__annotation,
            finish_reason: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            index: __dataclass__init__fields__2__annotation,
            logprobs: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'delta', delta)
            __dataclass__object_setattr(self, 'finish_reason', finish_reason)
            __dataclass__object_setattr(self, 'index', index)
            __dataclass__object_setattr(self, 'logprobs', logprobs)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"delta={self.delta!r}")
            parts.append(f"finish_reason={self.finish_reason!r}")
            parts.append(f"index={self.index!r}")
            parts.append(f"logprobs={self.logprobs!r}")
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
        "Plans(tup=(CopyPlan(fields=('content', 'refusal')), EqPlan(fields=('content', 'refusal')), FrozenPlan(fields=("
        "'content', 'refusal'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('content', 'refusal')"
        ", cache=False), InitPlan(fields=(InitPlan.Field(name='content', annotation=OpRef(name='init.fields.0.annotatio"
        "n'), default=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type="
        "FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='refusal', annotation=Op"
        "Ref(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init="
        "True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param"
        "='self', std_params=(), kw_only_params=('content', 'refusal'), frozen=True, slots=False, post_init_params=None"
        ", init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='content', kw_only=True, fn=None), ReprP"
        "lan.Field(name='refusal', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='a784a12ebcb916e633672bf2c35c6579e020ff31',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.chatcompletion.chunk', 'ChatCompletionChunkChoice.Logprobs'),
        ('ommlds.backends.openai.protocol.chatcompletion.response', 'ChatCompletionResponseChoice.Logprobs'),
    ),
)
def _process_dataclass__a784a12ebcb916e633672bf2c35c6579e020ff31():
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
                content=self.content,
                refusal=self.refusal,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
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
                self.refusal == other.refusal
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'content',
            'refusal',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'refusal',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.refusal,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            content: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            refusal: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'content', content)
            __dataclass__object_setattr(self, 'refusal', refusal)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"content={self.content!r}")
            parts.append(f"refusal={self.refusal!r}")
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
        "Plans(tup=(CopyPlan(fields=('content', 'refusal', 'channel', 'role', 'tool_calls')), EqPlan(fields=('content',"
        " 'refusal', 'channel', 'role', 'tool_calls')), FrozenPlan(fields=('content', 'refusal', 'channel', 'role', 'to"
        "ol_calls'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('content', 'refusal', 'channel',"
        " 'role', 'tool_calls'), cache=False), InitPlan(fields=(InitPlan.Field(name='content', annotation=OpRef(name='i"
        "nit.fields.0.annotation'), default=OpRef(name='init.fields.0.default'), default_factory=None, init=True, overr"
        "ide=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='r"
        "efusal', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), defau"
        "lt_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_t"
        "ype=None), InitPlan.Field(name='channel', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(nam"
        "e='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, co"
        "erce=None, validate=None, check_type=None), InitPlan.Field(name='role', annotation=OpRef(name='init.fields.3.a"
        "nnotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, fie"
        "ld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='tool_calls', an"
        "notation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_factory="
        "None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)),"
        " self_param='self', std_params=(), kw_only_params=('content', 'refusal', 'channel', 'role', 'tool_calls'), fro"
        "zen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(n"
        "ame='content', kw_only=True, fn=None), ReprPlan.Field(name='refusal', kw_only=True, fn=None), ReprPlan.Field(n"
        "ame='channel', kw_only=True, fn=None), ReprPlan.Field(name='role', kw_only=True, fn=None), ReprPlan.Field(name"
        "='tool_calls', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='aa76a085715c704bda9c0731aa3769f95d66c826',
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
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.chatcompletion.chunk', 'ChatCompletionChunkChoiceDelta'),
    ),
)
def _process_dataclass__aa76a085715c704bda9c0731aa3769f95d66c826():
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
                refusal=self.refusal,
                channel=self.channel,
                role=self.role,
                tool_calls=self.tool_calls,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
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
                self.refusal == other.refusal and
                self.channel == other.channel and
                self.role == other.role and
                self.tool_calls == other.tool_calls
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'content',
            'refusal',
            'channel',
            'role',
            'tool_calls',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'refusal',
            'channel',
            'role',
            'tool_calls',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.refusal,
                self.channel,
                self.role,
                self.tool_calls,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            content: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            refusal: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            channel: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            role: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            tool_calls: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'content', content)
            __dataclass__object_setattr(self, 'refusal', refusal)
            __dataclass__object_setattr(self, 'channel', channel)
            __dataclass__object_setattr(self, 'role', role)
            __dataclass__object_setattr(self, 'tool_calls', tool_calls)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"content={self.content!r}")
            parts.append(f"refusal={self.refusal!r}")
            parts.append(f"channel={self.channel!r}")
            parts.append(f"role={self.role!r}")
            parts.append(f"tool_calls={self.tool_calls!r}")
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
        "Plans(tup=(CopyPlan(fields=('index', 'id', 'function', 'type')), EqPlan(fields=('index', 'id', 'function', 'ty"
        "pe')), FrozenPlan(fields=('index', 'id', 'function', 'type'), allow_dynamic_dunder_attrs=False), HashPlan(acti"
        "on='add', fields=('index', 'id', 'function', 'type'), cache=False), InitPlan(fields=(InitPlan.Field(name='inde"
        "x', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override"
        "=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='id',"
        " annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_facto"
        "ry=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None"
        "), InitPlan.Field(name='function', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init"
        ".fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=No"
        "ne, validate=None, check_type=None), InitPlan.Field(name='type', annotation=OpRef(name='init.fields.3.annotati"
        "on'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, field_type"
        "=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_"
        "params=('index', 'id', 'function', 'type'), frozen=True, slots=False, post_init_params=None, init_fns=(), vali"
        "date_fns=()), ReprPlan(fields=(ReprPlan.Field(name='index', kw_only=True, fn=None), ReprPlan.Field(name='id', "
        "kw_only=True, fn=None), ReprPlan.Field(name='function', kw_only=True, fn=None)), id=False, terse=False, defaul"
        "t_fn=None)))"
    ),
    plan_repr_sha1='3b71b04cca7e8d3354a5bb5cdc6ba69d294b61c9',
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
        ('ommlds.backends.openai.protocol.chatcompletion.chunk', 'ChatCompletionChunkChoiceDelta.ToolCall'),
    ),
)
def _process_dataclass__3b71b04cca7e8d3354a5bb5cdc6ba69d294b61c9():
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
                index=self.index,
                id=self.id,
                function=self.function,
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
                self.index == other.index and
                self.id == other.id and
                self.function == other.function and
                self.type == other.type
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'index',
            'id',
            'function',
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
            'index',
            'id',
            'function',
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
                self.index,
                self.id,
                self.function,
                self.type,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            index: __dataclass__init__fields__0__annotation,
            id: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            function: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            type: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'index', index)
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'function', function)
            __dataclass__object_setattr(self, 'type', type)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"index={self.index!r}")
            parts.append(f"id={self.id!r}")
            parts.append(f"function={self.function!r}")
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
        "Plans(tup=(CopyPlan(fields=('arguments', 'name')), EqPlan(fields=('arguments', 'name')), FrozenPlan(fields=('a"
        "rguments', 'name'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('arguments', 'name'), ca"
        "che=False), InitPlan(fields=(InitPlan.Field(name='arguments', annotation=OpRef(name='init.fields.0.annotation'"
        "), default=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=Fi"
        "eldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='name', annotation=OpRef(n"
        "ame='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True,"
        " override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='sel"
        "f', std_params=(), kw_only_params=('arguments', 'name'), frozen=True, slots=False, post_init_params=None, init"
        "_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='arguments', kw_only=True, fn=None), ReprPlan."
        "Field(name='name', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='ca1d4dad922b4f93571cc14b86fcfb93e4c5f278',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.chatcompletion.chunk', 'ChatCompletionChunkChoiceDelta.ToolCall.Function'),
    ),
)
def _process_dataclass__ca1d4dad922b4f93571cc14b86fcfb93e4c5f278():
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
                arguments=self.arguments,
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
                self.arguments == other.arguments and
                self.name == other.name
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'arguments',
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
            'arguments',
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
                self.arguments,
                self.name,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            arguments: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            name: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'arguments', arguments)
            __dataclass__object_setattr(self, 'name', name)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"arguments={self.arguments!r}")
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
        "Plans(tup=(CopyPlan(fields=('file',)), EqPlan(fields=('file',)), FrozenPlan(fields=('file',), allow_dynamic_du"
        "nder_attrs=False), HashPlan(action='add', fields=('file',), cache=False), InitPlan(fields=(InitPlan.Field(name"
        "='file', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, ove"
        "rride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self',"
        " std_params=('file',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), valida"
        "te_fns=()), ReprPlan(fields=(ReprPlan.Field(name='file', kw_only=False, fn=None),), id=False, terse=False, def"
        "ault_fn=None)))"
    ),
    plan_repr_sha1='820703dde31327beb60e5aac6d470c0773d6e7ec',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.chatcompletion.contentpart', 'FileChatCompletionContentPart'),
    ),
)
def _process_dataclass__820703dde31327beb60e5aac6d470c0773d6e7ec():
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
                file=self.file,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.file == other.file
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'file',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'file',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.file,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            file: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'file', file)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"file={self.file!r}")
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
        "Plans(tup=(CopyPlan(fields=('file_data', 'file_id', 'filename')), EqPlan(fields=('file_data', 'file_id', 'file"
        "name')), FrozenPlan(fields=('file_data', 'file_id', 'filename'), allow_dynamic_dunder_attrs=False), HashPlan(a"
        "ction='add', fields=('file_data', 'file_id', 'filename'), cache=False), InitPlan(fields=(InitPlan.Field(name='"
        "file_data', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'), de"
        "fault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, chec"
        "k_type=None), InitPlan.Field(name='file_id', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef("
        "name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE,"
        " coerce=None, validate=None, check_type=None), InitPlan.Field(name='filename', annotation=OpRef(name='init.fie"
        "lds.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=Fal"
        "se, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_param"
        "s=(), kw_only_params=('file_data', 'file_id', 'filename'), frozen=True, slots=False, post_init_params=None, in"
        "it_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='file_data', kw_only=True, fn=None), ReprPla"
        "n.Field(name='file_id', kw_only=True, fn=None), ReprPlan.Field(name='filename', kw_only=True, fn=None)), id=Fa"
        "lse, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='c02271796516dea2e671f76da4eb47ad2ea8e54e',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.chatcompletion.contentpart', 'FileChatCompletionContentPart.File'),
    ),
)
def _process_dataclass__c02271796516dea2e671f76da4eb47ad2ea8e54e():
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
                file_data=self.file_data,
                file_id=self.file_id,
                filename=self.filename,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.file_data == other.file_data and
                self.file_id == other.file_id and
                self.filename == other.filename
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'file_data',
            'file_id',
            'filename',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'file_data',
            'file_id',
            'filename',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.file_data,
                self.file_id,
                self.filename,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            file_data: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            file_id: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            filename: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'file_data', file_data)
            __dataclass__object_setattr(self, 'file_id', file_id)
            __dataclass__object_setattr(self, 'filename', filename)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"file_data={self.file_data!r}")
            parts.append(f"file_id={self.file_id!r}")
            parts.append(f"filename={self.filename!r}")
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
        "Plans(tup=(CopyPlan(fields=('image_url',)), EqPlan(fields=('image_url',)), FrozenPlan(fields=('image_url',), a"
        "llow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('image_url',), cache=False), InitPlan(fields="
        "(InitPlan.Field(name='image_url', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_fac"
        "tory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=No"
        "ne),), self_param='self', std_params=('image_url',), kw_only_params=(), frozen=True, slots=False, post_init_pa"
        "rams=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='image_url', kw_only=False, fn="
        "None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='0613bb79b7ba3f407646dd7913e28b991291f4ba',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.chatcompletion.contentpart', 'ImageUrlChatCompletionContentPart'),
    ),
)
def _process_dataclass__0613bb79b7ba3f407646dd7913e28b991291f4ba():
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
                image_url=self.image_url,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.image_url == other.image_url
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'image_url',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'image_url',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.image_url,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            image_url: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'image_url', image_url)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"image_url={self.image_url!r}")
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
        "Plans(tup=(CopyPlan(fields=('url', 'detail')), EqPlan(fields=('url', 'detail')), FrozenPlan(fields=('url', 'de"
        "tail'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('url', 'detail'), cache=False), Init"
        "Plan(fields=(InitPlan.Field(name='url', annotation=OpRef(name='init.fields.0.annotation'), default=None, defau"
        "lt_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_t"
        "ype=None), InitPlan.Field(name='detail', annotation=OpRef(name='init.fields.1.annotation'), default=None, defa"
        "ult_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_"
        "type=None)), self_param='self', std_params=('url', 'detail'), kw_only_params=(), frozen=True, slots=False, pos"
        "t_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='url', kw_only=False, "
        "fn=None), ReprPlan.Field(name='detail', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='0e6cdad9d5cc244f6f448ffe4a9b42d55254d07a',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.chatcompletion.contentpart', 'ImageUrlChatCompletionContentPart.ImageUrl'),
    ),
)
def _process_dataclass__0e6cdad9d5cc244f6f448ffe4a9b42d55254d07a():
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
                url=self.url,
                detail=self.detail,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
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
                self.detail == other.detail
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'url',
            'detail',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'detail',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.detail,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            url: __dataclass__init__fields__0__annotation,
            detail: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'url', url)
            __dataclass__object_setattr(self, 'detail', detail)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"url={self.url!r}")
            parts.append(f"detail={self.detail!r}")
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
        "Plans(tup=(CopyPlan(fields=('input_audio',)), EqPlan(fields=('input_audio',)), FrozenPlan(fields=('input_audio"
        "',), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('input_audio',), cache=False), InitPlan"
        "(fields=(InitPlan.Field(name='input_audio', annotation=OpRef(name='init.fields.0.annotation'), default=None, d"
        "efault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, che"
        "ck_type=None),), self_param='self', std_params=('input_audio',), kw_only_params=(), frozen=True, slots=False, "
        "post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='input_audio', kw_o"
        "nly=False, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='0d200bd5732bf8acefc4982cb9f4faf1b94e1f59',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.chatcompletion.contentpart', 'InputAudioChatCompletionContentPart'),
    ),
)
def _process_dataclass__0d200bd5732bf8acefc4982cb9f4faf1b94e1f59():
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
                input_audio=self.input_audio,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.input_audio == other.input_audio
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'input_audio',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'input_audio',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.input_audio,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            input_audio: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'input_audio', input_audio)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"input_audio={self.input_audio!r}")
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
        "Plans(tup=(CopyPlan(fields=('data', 'format')), EqPlan(fields=('data', 'format')), FrozenPlan(fields=('data', "
        "'format'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('data', 'format'), cache=False), "
        "InitPlan(fields=(InitPlan.Field(name='data', annotation=OpRef(name='init.fields.0.annotation'), default=None, "
        "default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, ch"
        "eck_type=None), InitPlan.Field(name='format', annotation=OpRef(name='init.fields.1.annotation'), default=None,"
        " default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, c"
        "heck_type=None)), self_param='self', std_params=('data', 'format'), kw_only_params=(), frozen=True, slots=Fals"
        "e, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='data', kw_only="
        "False, fn=None), ReprPlan.Field(name='format', kw_only=False, fn=None)), id=False, terse=False, default_fn=Non"
        "e)))"
    ),
    plan_repr_sha1='66e8d7302e31e7aff7ac2f26496aad56e225e3d1',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.chatcompletion.contentpart', 'InputAudioChatCompletionContentPart.InputAudio'),
    ),
)
def _process_dataclass__66e8d7302e31e7aff7ac2f26496aad56e225e3d1():
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
                data=self.data,
                format=self.format,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.data == other.data and
                self.format == other.format
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'data',
            'format',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'data',
            'format',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.data,
                self.format,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            data: __dataclass__init__fields__0__annotation,
            format: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'data', data)
            __dataclass__object_setattr(self, 'format', format)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"data={self.data!r}")
            parts.append(f"format={self.format!r}")
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
        "Plans(tup=(CopyPlan(fields=('refusal',)), EqPlan(fields=('refusal',)), FrozenPlan(fields=('refusal',), allow_d"
        "ynamic_dunder_attrs=False), HashPlan(action='add', fields=('refusal',), cache=False), InitPlan(fields=(InitPla"
        "n.Field(name='refusal', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None,"
        " init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), sel"
        "f_param='self', std_params=('refusal',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, i"
        "nit_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='refusal', kw_only=False, fn=None),), id=Fa"
        "lse, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='f8dffa13018e7a78dec0c87f480c530d68cb619c',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.chatcompletion.contentpart', 'RefusalChatCompletionContentPart'),
    ),
)
def _process_dataclass__f8dffa13018e7a78dec0c87f480c530d68cb619c():
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
                refusal=self.refusal,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.refusal == other.refusal
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'refusal',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'refusal',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.refusal,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            refusal: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'refusal', refusal)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"refusal={self.refusal!r}")
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
        "Plans(tup=(CopyPlan(fields=('text',)), EqPlan(fields=('text',)), FrozenPlan(fields=('text',), allow_dynamic_du"
        "nder_attrs=False), HashPlan(action='add', fields=('text',), cache=False), InitPlan(fields=(InitPlan.Field(name"
        "='text', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, ove"
        "rride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self',"
        " std_params=('text',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), valida"
        "te_fns=()), ReprPlan(fields=(ReprPlan.Field(name='text', kw_only=False, fn=None),), id=False, terse=False, def"
        "ault_fn=None)))"
    ),
    plan_repr_sha1='ce2a4c81e0f66e62a54ea3adfdc532902daece78',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.chatcompletion.contentpart', 'TextChatCompletionContentPart'),
    ),
)
def _process_dataclass__ce2a4c81e0f66e62a54ea3adfdc532902daece78():
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
                text=self.text,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.text == other.text
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'text',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'text',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.text,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            text: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'text', text)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"text={self.text!r}")
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
        "Plans(tup=(CopyPlan(fields=('reasoning', 'audio', 'content', 'name', 'refusal', 'tool_calls')), EqPlan(fields="
        "('reasoning', 'audio', 'content', 'name', 'refusal', 'tool_calls')), FrozenPlan(fields=('reasoning', 'audio', "
        "'content', 'name', 'refusal', 'tool_calls'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields="
        "('reasoning', 'audio', 'content', 'name', 'refusal', 'tool_calls'), cache=False), InitPlan(fields=(InitPlan.Fi"
        "eld(name='reasoning', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.def"
        "ault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate="
        "None, check_type=None), InitPlan.Field(name='audio', annotation=OpRef(name='init.fields.1.annotation'), defaul"
        "t=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.I"
        "NSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='content', annotation=OpRef(name='i"
        "nit.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, overr"
        "ide=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='n"
        "ame', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_"
        "factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type"
        "=None), InitPlan.Field(name='refusal', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='"
        "init.fields.4.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerc"
        "e=None, validate=None, check_type=None), InitPlan.Field(name='tool_calls', annotation=OpRef(name='init.fields."
        "5.annotation'), default=OpRef(name='init.fields.5.default'), default_factory=None, init=True, override=False, "
        "field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=()"
        ", kw_only_params=('reasoning', 'audio', 'content', 'name', 'refusal', 'tool_calls'), frozen=True, slots=False,"
        " post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='reasoning', kw_on"
        "ly=True, fn=None), ReprPlan.Field(name='audio', kw_only=True, fn=None), ReprPlan.Field(name='content', kw_only"
        "=True, fn=None), ReprPlan.Field(name='name', kw_only=True, fn=None), ReprPlan.Field(name='refusal', kw_only=Tr"
        "ue, fn=None), ReprPlan.Field(name='tool_calls', kw_only=True, fn=None)), id=False, terse=False, default_fn=Non"
        "e)))"
    ),
    plan_repr_sha1='52ca6f1ee19ff4580236cf91b4d8dc7744bbbea3',
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
        ('ommlds.backends.openai.protocol.chatcompletion.message', 'AssistantChatCompletionMessage'),
    ),
)
def _process_dataclass__52ca6f1ee19ff4580236cf91b4d8dc7744bbbea3():
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
                reasoning=self.reasoning,
                audio=self.audio,
                content=self.content,
                name=self.name,
                refusal=self.refusal,
                tool_calls=self.tool_calls,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.reasoning == other.reasoning and
                self.audio == other.audio and
                self.content == other.content and
                self.name == other.name and
                self.refusal == other.refusal and
                self.tool_calls == other.tool_calls
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'reasoning',
            'audio',
            'content',
            'name',
            'refusal',
            'tool_calls',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'reasoning',
            'audio',
            'content',
            'name',
            'refusal',
            'tool_calls',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.reasoning,
                self.audio,
                self.content,
                self.name,
                self.refusal,
                self.tool_calls,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            reasoning: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            audio: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            content: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            name: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            refusal: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            tool_calls: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'reasoning', reasoning)
            __dataclass__object_setattr(self, 'audio', audio)
            __dataclass__object_setattr(self, 'content', content)
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'refusal', refusal)
            __dataclass__object_setattr(self, 'tool_calls', tool_calls)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"reasoning={self.reasoning!r}")
            parts.append(f"audio={self.audio!r}")
            parts.append(f"content={self.content!r}")
            parts.append(f"name={self.name!r}")
            parts.append(f"refusal={self.refusal!r}")
            parts.append(f"tool_calls={self.tool_calls!r}")
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
        "Plans(tup=(CopyPlan(fields=('id',)), EqPlan(fields=('id',)), FrozenPlan(fields=('id',), allow_dynamic_dunder_a"
        "ttrs=False), HashPlan(action='add', fields=('id',), cache=False), InitPlan(fields=(InitPlan.Field(name='id', a"
        "nnotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=Fals"
        "e, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self', std_param"
        "s=(), kw_only_params=('id',), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), "
        "ReprPlan(fields=(ReprPlan.Field(name='id', kw_only=True, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='c5af6f307dd107bda40bc7313a644e62e9f79b78',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.chatcompletion.message', 'AssistantChatCompletionMessage.Audio'),
    ),
)
def _process_dataclass__c5af6f307dd107bda40bc7313a644e62e9f79b78():
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
            *,
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

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('id', 'function', 'type')), EqPlan(fields=('id', 'function', 'type')), FrozenPlan("
        "fields=('id', 'function', 'type'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('id', 'fu"
        "nction', 'type'), cache=False), InitPlan(fields=(InitPlan.Field(name='id', annotation=OpRef(name='init.fields."
        "0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, "
        "coerce=None, validate=None, check_type=None), InitPlan.Field(name='function', annotation=OpRef(name='init.fiel"
        "ds.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANC"
        "E, coerce=None, validate=None, check_type=None), InitPlan.Field(name='type', annotation=OpRef(name='init.field"
        "s.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False"
        ", field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params="
        "(), kw_only_params=('id', 'function', 'type'), frozen=True, slots=False, post_init_params=None, init_fns=(), v"
        "alidate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='id', kw_only=True, fn=None), ReprPlan.Field(name='funct"
        "ion', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='83872bdd3ec48e6894ce8e035bdc4708a2dd6e64',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.chatcompletion.message', 'AssistantChatCompletionMessage.ToolCall'),
        ('ommlds.backends.openai.protocol.chatcompletion.response', 'ChatCompletionResponseMessage.ToolCall'),
    ),
)
def _process_dataclass__83872bdd3ec48e6894ce8e035bdc4708a2dd6e64():
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
                id=self.id,
                function=self.function,
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
                self.id == other.id and
                self.function == other.function and
                self.type == other.type
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'id',
            'function',
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
            'id',
            'function',
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
                self.id,
                self.function,
                self.type,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            id: __dataclass__init__fields__0__annotation,
            function: __dataclass__init__fields__1__annotation,
            type: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'function', function)
            __dataclass__object_setattr(self, 'type', type)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"id={self.id!r}")
            parts.append(f"function={self.function!r}")
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
        "Plans(tup=(CopyPlan(fields=('arguments', 'name')), EqPlan(fields=('arguments', 'name')), FrozenPlan(fields=('a"
        "rguments', 'name'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('arguments', 'name'), ca"
        "che=False), InitPlan(fields=(InitPlan.Field(name='arguments', annotation=OpRef(name='init.fields.0.annotation'"
        "), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, "
        "validate=None, check_type=None), InitPlan.Field(name='name', annotation=OpRef(name='init.fields.1.annotation')"
        ", default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, v"
        "alidate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('arguments', 'name'), froze"
        "n=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(nam"
        "e='arguments', kw_only=True, fn=None), ReprPlan.Field(name='name', kw_only=True, fn=None)), id=False, terse=Fa"
        "lse, default_fn=None)))"
    ),
    plan_repr_sha1='74d1fa47dc3c867f85203a9e43e792c7b1202dab',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.chatcompletion.message', 'AssistantChatCompletionMessage.ToolCall.Function'),
        ('ommlds.backends.openai.protocol.chatcompletion.response', 'ChatCompletionResponseMessage.ToolCall.Function'),
    ),
)
def _process_dataclass__74d1fa47dc3c867f85203a9e43e792c7b1202dab():
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
                arguments=self.arguments,
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
                self.arguments == other.arguments and
                self.name == other.name
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'arguments',
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
            'arguments',
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
                self.arguments,
                self.name,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            arguments: __dataclass__init__fields__0__annotation,
            name: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'arguments', arguments)
            __dataclass__object_setattr(self, 'name', name)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"arguments={self.arguments!r}")
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
        "Plans(tup=(CopyPlan(fields=('content', 'name')), EqPlan(fields=('content', 'name')), FrozenPlan(fields=('conte"
        "nt', 'name'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('content', 'name'), cache=Fals"
        "e), InitPlan(fields=(InitPlan.Field(name='content', annotation=OpRef(name='init.fields.0.annotation'), default"
        "=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=N"
        "one, check_type=None), InitPlan.Field(name='name', annotation=OpRef(name='init.fields.1.annotation'), default="
        "OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INS"
        "TANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('conte"
        "nt', 'name'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields="
        "(ReprPlan.Field(name='content', kw_only=True, fn=None), ReprPlan.Field(name='name', kw_only=True, fn=None)), i"
        "d=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='6aaca6eef447e0e6906a14b2f1c0516c67cdc965',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.chatcompletion.message', 'DeveloperChatCompletionMessage'),
        ('ommlds.backends.openai.protocol.chatcompletion.message', 'SystemChatCompletionMessage'),
        ('ommlds.backends.openai.protocol.chatcompletion.message', 'UserChatCompletionMessage'),
    ),
)
def _process_dataclass__6aaca6eef447e0e6906a14b2f1c0516c67cdc965():
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
                content=self.content,
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
                self.content == other.content and
                self.name == other.name
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'content',
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
            'content',
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
                self.content,
                self.name,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            content: __dataclass__init__fields__0__annotation,
            name: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'content', content)
            __dataclass__object_setattr(self, 'name', name)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"content={self.content!r}")
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
        "Plans(tup=(CopyPlan(fields=('content', 'name')), EqPlan(fields=('content', 'name')), FrozenPlan(fields=('conte"
        "nt', 'name'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('content', 'name'), cache=Fals"
        "e), InitPlan(fields=(InitPlan.Field(name='content', annotation=OpRef(name='init.fields.0.annotation'), default"
        "=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=N"
        "one, check_type=None), InitPlan.Field(name='name', annotation=OpRef(name='init.fields.1.annotation'), default="
        "None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=No"
        "ne, check_type=None)), self_param='self', std_params=(), kw_only_params=('content', 'name'), frozen=True, slot"
        "s=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='content',"
        " kw_only=True, fn=None), ReprPlan.Field(name='name', kw_only=True, fn=None)), id=False, terse=False, default_f"
        "n=None)))"
    ),
    plan_repr_sha1='acfb7b4dec2626f8e5d56a629978189fa92883c2',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.chatcompletion.message', 'FunctionChatCompletionMessage'),
    ),
)
def _process_dataclass__acfb7b4dec2626f8e5d56a629978189fa92883c2():
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
                content=self.content,
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
                self.content == other.content and
                self.name == other.name
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'content',
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
            'content',
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
                self.content,
                self.name,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            content: __dataclass__init__fields__0__annotation,
            name: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'content', content)
            __dataclass__object_setattr(self, 'name', name)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"content={self.content!r}")
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
        "Plans(tup=(CopyPlan(fields=('content', 'tool_call_id')), EqPlan(fields=('content', 'tool_call_id')), FrozenPla"
        "n(fields=('content', 'tool_call_id'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('conte"
        "nt', 'tool_call_id'), cache=False), InitPlan(fields=(InitPlan.Field(name='content', annotation=OpRef(name='ini"
        "t.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.I"
        "NSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='tool_call_id', annotation=OpRef(na"
        "me='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=Fiel"
        "dType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_param"
        "s=('content', 'tool_call_id'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()),"
        " ReprPlan(fields=(ReprPlan.Field(name='content', kw_only=True, fn=None), ReprPlan.Field(name='tool_call_id', k"
        "w_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='7b34fa2c51a834eeac98aeb3f7bbdf422b553272',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.chatcompletion.message', 'ToolChatCompletionMessage'),
    ),
)
def _process_dataclass__7b34fa2c51a834eeac98aeb3f7bbdf422b553272():
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
                content=self.content,
                tool_call_id=self.tool_call_id,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
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
                self.tool_call_id == other.tool_call_id
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'content',
            'tool_call_id',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'tool_call_id',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.tool_call_id,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            content: __dataclass__init__fields__0__annotation,
            tool_call_id: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'content', content)
            __dataclass__object_setattr(self, 'tool_call_id', tool_call_id)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"content={self.content!r}")
            parts.append(f"tool_call_id={self.tool_call_id!r}")
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
        "Plans(tup=(CopyPlan(fields=('messages', 'model', 'audio', 'frequency_penalty', 'logit_bias', 'logprobs', 'max_"
        "completion_tokens', 'max_tokens', 'metadata', 'modalities', 'n', 'parallel_tool_calls', 'prediction', 'presenc"
        "e_penalty', 'reasoning_effort', 'response_format', 'seed', 'service_tier', 'stop', 'store', 'stream', 'stream_"
        "options', 'temperature', 'tool_choice', 'tools', 'top_logprobs', 'top_p', 'user', 'web_search_options')), EqPl"
        "an(fields=('messages', 'model', 'audio', 'frequency_penalty', 'logit_bias', 'logprobs', 'max_completion_tokens"
        "', 'max_tokens', 'metadata', 'modalities', 'n', 'parallel_tool_calls', 'prediction', 'presence_penalty', 'reas"
        "oning_effort', 'response_format', 'seed', 'service_tier', 'stop', 'store', 'stream', 'stream_options', 'temper"
        "ature', 'tool_choice', 'tools', 'top_logprobs', 'top_p', 'user', 'web_search_options')), FrozenPlan(fields=('m"
        "essages', 'model', 'audio', 'frequency_penalty', 'logit_bias', 'logprobs', 'max_completion_tokens', 'max_token"
        "s', 'metadata', 'modalities', 'n', 'parallel_tool_calls', 'prediction', 'presence_penalty', 'reasoning_effort'"
        ", 'response_format', 'seed', 'service_tier', 'stop', 'store', 'stream', 'stream_options', 'temperature', 'tool"
        "_choice', 'tools', 'top_logprobs', 'top_p', 'user', 'web_search_options'), allow_dynamic_dunder_attrs=False), "
        "HashPlan(action='add', fields=('messages', 'model', 'audio', 'frequency_penalty', 'logit_bias', 'logprobs', 'm"
        "ax_completion_tokens', 'max_tokens', 'metadata', 'modalities', 'n', 'parallel_tool_calls', 'prediction', 'pres"
        "ence_penalty', 'reasoning_effort', 'response_format', 'seed', 'service_tier', 'stop', 'store', 'stream', 'stre"
        "am_options', 'temperature', 'tool_choice', 'tools', 'top_logprobs', 'top_p', 'user', 'web_search_options'), ca"
        "che=False), InitPlan(fields=(InitPlan.Field(name='messages', annotation=OpRef(name='init.fields.00.annotation'"
        "), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, "
        "validate=None, check_type=None), InitPlan.Field(name='model', annotation=OpRef(name='init.fields.01.annotation"
        "'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None,"
        " validate=None, check_type=None), InitPlan.Field(name='audio', annotation=OpRef(name='init.fields.02.annotatio"
        "n'), default=OpRef(name='init.fields.02.default'), default_factory=None, init=True, override=False, field_type"
        "=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='frequency_penalty', an"
        "notation=OpRef(name='init.fields.03.annotation'), default=OpRef(name='init.fields.03.default'), default_factor"
        "y=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)"
        ", InitPlan.Field(name='logit_bias', annotation=OpRef(name='init.fields.04.annotation'), default=OpRef(name='in"
        "it.fields.04.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce"
        "=None, validate=None, check_type=None), InitPlan.Field(name='logprobs', annotation=OpRef(name='init.fields.05."
        "annotation'), default=OpRef(name='init.fields.05.default'), default_factory=None, init=True, override=False, f"
        "ield_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='max_completio"
        "n_tokens', annotation=OpRef(name='init.fields.06.annotation'), default=OpRef(name='init.fields.06.default'), d"
        "efault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, che"
        "ck_type=None), InitPlan.Field(name='max_tokens', annotation=OpRef(name='init.fields.07.annotation'), default=O"
        "pRef(name='init.fields.07.default'), default_factory=None, init=True, override=False, field_type=FieldType.INS"
        "TANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='metadata', annotation=OpRef(name='in"
        "it.fields.08.annotation'), default=OpRef(name='init.fields.08.default'), default_factory=None, init=True, over"
        "ride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='"
        "modalities', annotation=OpRef(name='init.fields.09.annotation'), default=OpRef(name='init.fields.09.default'),"
        " default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, c"
        "heck_type=None), InitPlan.Field(name='n', annotation=OpRef(name='init.fields.10.annotation'), default=OpRef(na"
        "me='init.fields.10.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, "
        "coerce=None, validate=None, check_type=None), InitPlan.Field(name='parallel_tool_calls', annotation=OpRef(name"
        "='init.fields.11.annotation'), default=OpRef(name='init.fields.11.default'), default_factory=None, init=True, "
        "override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(na"
        "me='prediction', annotation=OpRef(name='init.fields.12.annotation'), default=OpRef(name='init.fields.12.defaul"
        "t'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=Non"
        "e, check_type=None), InitPlan.Field(name='presence_penalty', annotation=OpRef(name='init.fields.13.annotation'"
        "), default=OpRef(name='init.fields.13.default'), default_factory=None, init=True, override=False, field_type=F"
        "ieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='reasoning_effort', annot"
        "ation=OpRef(name='init.fields.14.annotation'), default=OpRef(name='init.fields.14.default'), default_factory=N"
        "one, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), I"
        "nitPlan.Field(name='response_format', annotation=OpRef(name='init.fields.15.annotation'), default=OpRef(name='"
        "init.fields.15.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coer"
        "ce=None, validate=None, check_type=None), InitPlan.Field(name='seed', annotation=OpRef(name='init.fields.16.an"
        "notation'), default=OpRef(name='init.fields.16.default'), default_factory=None, init=True, override=False, fie"
        "ld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='service_tier', "
        "annotation=OpRef(name='init.fields.17.annotation'), default=OpRef(name='init.fields.17.default'), default_fact"
        "ory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=Non"
        "e), InitPlan.Field(name='stop', annotation=OpRef(name='init.fields.18.annotation'), default=OpRef(name='init.f"
        "ields.18.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=Non"
        "e, validate=None, check_type=None), InitPlan.Field(name='store', annotation=OpRef(name='init.fields.19.annotat"
        "ion'), default=OpRef(name='init.fields.19.default'), default_factory=None, init=True, override=False, field_ty"
        "pe=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='stream', annotation="
        "OpRef(name='init.fields.20.annotation'), default=OpRef(name='init.fields.20.default'), default_factory=None, i"
        "nit=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPla"
        "n.Field(name='stream_options', annotation=OpRef(name='init.fields.21.annotation'), default=OpRef(name='init.fi"
        "elds.21.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None"
        ", validate=None, check_type=None), InitPlan.Field(name='temperature', annotation=OpRef(name='init.fields.22.an"
        "notation'), default=OpRef(name='init.fields.22.default'), default_factory=None, init=True, override=False, fie"
        "ld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='tool_choice', a"
        "nnotation=OpRef(name='init.fields.23.annotation'), default=OpRef(name='init.fields.23.default'), default_facto"
        "ry=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None"
        "), InitPlan.Field(name='tools', annotation=OpRef(name='init.fields.24.annotation'), default=OpRef(name='init.f"
        "ields.24.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=Non"
        "e, validate=None, check_type=None), InitPlan.Field(name='top_logprobs', annotation=OpRef(name='init.fields.25."
        "annotation'), default=OpRef(name='init.fields.25.default'), default_factory=None, init=True, override=False, f"
        "ield_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='top_p', annot"
        "ation=OpRef(name='init.fields.26.annotation'), default=OpRef(name='init.fields.26.default'), default_factory=N"
        "one, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), I"
        "nitPlan.Field(name='user', annotation=OpRef(name='init.fields.27.annotation'), default=OpRef(name='init.fields"
        ".27.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, va"
        "lidate=None, check_type=None), InitPlan.Field(name='web_search_options', annotation=OpRef(name='init.fields.28"
        ".annotation'), default=OpRef(name='init.fields.28.default'), default_factory=None, init=True, override=False, "
        "field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=()"
        ", kw_only_params=('messages', 'model', 'audio', 'frequency_penalty', 'logit_bias', 'logprobs', 'max_completion"
        "_tokens', 'max_tokens', 'metadata', 'modalities', 'n', 'parallel_tool_calls', 'prediction', 'presence_penalty'"
        ", 'reasoning_effort', 'response_format', 'seed', 'service_tier', 'stop', 'store', 'stream', 'stream_options', "
        "'temperature', 'tool_choice', 'tools', 'top_logprobs', 'top_p', 'user', 'web_search_options'), frozen=True, sl"
        "ots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='message"
        "s', kw_only=True, fn=None), ReprPlan.Field(name='model', kw_only=True, fn=None), ReprPlan.Field(name='audio', "
        "kw_only=True, fn=None), ReprPlan.Field(name='frequency_penalty', kw_only=True, fn=None), ReprPlan.Field(name='"
        "logit_bias', kw_only=True, fn=None), ReprPlan.Field(name='logprobs', kw_only=True, fn=None), ReprPlan.Field(na"
        "me='max_completion_tokens', kw_only=True, fn=None), ReprPlan.Field(name='max_tokens', kw_only=True, fn=None), "
        "ReprPlan.Field(name='metadata', kw_only=True, fn=None), ReprPlan.Field(name='modalities', kw_only=True, fn=Non"
        "e), ReprPlan.Field(name='n', kw_only=True, fn=None), ReprPlan.Field(name='parallel_tool_calls', kw_only=True, "
        "fn=None), ReprPlan.Field(name='prediction', kw_only=True, fn=None), ReprPlan.Field(name='presence_penalty', kw"
        "_only=True, fn=None), ReprPlan.Field(name='reasoning_effort', kw_only=True, fn=None), ReprPlan.Field(name='res"
        "ponse_format', kw_only=True, fn=None), ReprPlan.Field(name='seed', kw_only=True, fn=None), ReprPlan.Field(name"
        "='service_tier', kw_only=True, fn=None), ReprPlan.Field(name='stop', kw_only=True, fn=None), ReprPlan.Field(na"
        "me='store', kw_only=True, fn=None), ReprPlan.Field(name='stream', kw_only=True, fn=None), ReprPlan.Field(name="
        "'stream_options', kw_only=True, fn=None), ReprPlan.Field(name='temperature', kw_only=True, fn=None), ReprPlan."
        "Field(name='tool_choice', kw_only=True, fn=None), ReprPlan.Field(name='tools', kw_only=True, fn=None), ReprPla"
        "n.Field(name='top_logprobs', kw_only=True, fn=None), ReprPlan.Field(name='top_p', kw_only=True, fn=None), Repr"
        "Plan.Field(name='user', kw_only=True, fn=None), ReprPlan.Field(name='web_search_options', kw_only=True, fn=Non"
        "e)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='28976b0e5a23647ebf234c82017dc5f8c1d7ab3e',
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
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.chatcompletion.request', 'ChatCompletionRequest'),
    ),
)
def _process_dataclass__28976b0e5a23647ebf234c82017dc5f8c1d7ab3e():
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
                messages=self.messages,
                model=self.model,
                audio=self.audio,
                frequency_penalty=self.frequency_penalty,
                logit_bias=self.logit_bias,
                logprobs=self.logprobs,
                max_completion_tokens=self.max_completion_tokens,
                max_tokens=self.max_tokens,
                metadata=self.metadata,
                modalities=self.modalities,
                n=self.n,
                parallel_tool_calls=self.parallel_tool_calls,
                prediction=self.prediction,
                presence_penalty=self.presence_penalty,
                reasoning_effort=self.reasoning_effort,
                response_format=self.response_format,
                seed=self.seed,
                service_tier=self.service_tier,
                stop=self.stop,
                store=self.store,
                stream=self.stream,
                stream_options=self.stream_options,
                temperature=self.temperature,
                tool_choice=self.tool_choice,
                tools=self.tools,
                top_logprobs=self.top_logprobs,
                top_p=self.top_p,
                user=self.user,
                web_search_options=self.web_search_options,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.messages == other.messages and
                self.model == other.model and
                self.audio == other.audio and
                self.frequency_penalty == other.frequency_penalty and
                self.logit_bias == other.logit_bias and
                self.logprobs == other.logprobs and
                self.max_completion_tokens == other.max_completion_tokens and
                self.max_tokens == other.max_tokens and
                self.metadata == other.metadata and
                self.modalities == other.modalities and
                self.n == other.n and
                self.parallel_tool_calls == other.parallel_tool_calls and
                self.prediction == other.prediction and
                self.presence_penalty == other.presence_penalty and
                self.reasoning_effort == other.reasoning_effort and
                self.response_format == other.response_format and
                self.seed == other.seed and
                self.service_tier == other.service_tier and
                self.stop == other.stop and
                self.store == other.store and
                self.stream == other.stream and
                self.stream_options == other.stream_options and
                self.temperature == other.temperature and
                self.tool_choice == other.tool_choice and
                self.tools == other.tools and
                self.top_logprobs == other.top_logprobs and
                self.top_p == other.top_p and
                self.user == other.user and
                self.web_search_options == other.web_search_options
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'messages',
            'model',
            'audio',
            'frequency_penalty',
            'logit_bias',
            'logprobs',
            'max_completion_tokens',
            'max_tokens',
            'metadata',
            'modalities',
            'n',
            'parallel_tool_calls',
            'prediction',
            'presence_penalty',
            'reasoning_effort',
            'response_format',
            'seed',
            'service_tier',
            'stop',
            'store',
            'stream',
            'stream_options',
            'temperature',
            'tool_choice',
            'tools',
            'top_logprobs',
            'top_p',
            'user',
            'web_search_options',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'messages',
            'model',
            'audio',
            'frequency_penalty',
            'logit_bias',
            'logprobs',
            'max_completion_tokens',
            'max_tokens',
            'metadata',
            'modalities',
            'n',
            'parallel_tool_calls',
            'prediction',
            'presence_penalty',
            'reasoning_effort',
            'response_format',
            'seed',
            'service_tier',
            'stop',
            'store',
            'stream',
            'stream_options',
            'temperature',
            'tool_choice',
            'tools',
            'top_logprobs',
            'top_p',
            'user',
            'web_search_options',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.messages,
                self.model,
                self.audio,
                self.frequency_penalty,
                self.logit_bias,
                self.logprobs,
                self.max_completion_tokens,
                self.max_tokens,
                self.metadata,
                self.modalities,
                self.n,
                self.parallel_tool_calls,
                self.prediction,
                self.presence_penalty,
                self.reasoning_effort,
                self.response_format,
                self.seed,
                self.service_tier,
                self.stop,
                self.store,
                self.stream,
                self.stream_options,
                self.temperature,
                self.tool_choice,
                self.tools,
                self.top_logprobs,
                self.top_p,
                self.user,
                self.web_search_options,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            messages: __dataclass__init__fields__00__annotation,
            model: __dataclass__init__fields__01__annotation,
            audio: __dataclass__init__fields__02__annotation = __dataclass__init__fields__02__default,
            frequency_penalty: __dataclass__init__fields__03__annotation = __dataclass__init__fields__03__default,
            logit_bias: __dataclass__init__fields__04__annotation = __dataclass__init__fields__04__default,
            logprobs: __dataclass__init__fields__05__annotation = __dataclass__init__fields__05__default,
            max_completion_tokens: __dataclass__init__fields__06__annotation = __dataclass__init__fields__06__default,
            max_tokens: __dataclass__init__fields__07__annotation = __dataclass__init__fields__07__default,
            metadata: __dataclass__init__fields__08__annotation = __dataclass__init__fields__08__default,
            modalities: __dataclass__init__fields__09__annotation = __dataclass__init__fields__09__default,
            n: __dataclass__init__fields__10__annotation = __dataclass__init__fields__10__default,
            parallel_tool_calls: __dataclass__init__fields__11__annotation = __dataclass__init__fields__11__default,
            prediction: __dataclass__init__fields__12__annotation = __dataclass__init__fields__12__default,
            presence_penalty: __dataclass__init__fields__13__annotation = __dataclass__init__fields__13__default,
            reasoning_effort: __dataclass__init__fields__14__annotation = __dataclass__init__fields__14__default,
            response_format: __dataclass__init__fields__15__annotation = __dataclass__init__fields__15__default,
            seed: __dataclass__init__fields__16__annotation = __dataclass__init__fields__16__default,
            service_tier: __dataclass__init__fields__17__annotation = __dataclass__init__fields__17__default,
            stop: __dataclass__init__fields__18__annotation = __dataclass__init__fields__18__default,
            store: __dataclass__init__fields__19__annotation = __dataclass__init__fields__19__default,
            stream: __dataclass__init__fields__20__annotation = __dataclass__init__fields__20__default,
            stream_options: __dataclass__init__fields__21__annotation = __dataclass__init__fields__21__default,
            temperature: __dataclass__init__fields__22__annotation = __dataclass__init__fields__22__default,
            tool_choice: __dataclass__init__fields__23__annotation = __dataclass__init__fields__23__default,
            tools: __dataclass__init__fields__24__annotation = __dataclass__init__fields__24__default,
            top_logprobs: __dataclass__init__fields__25__annotation = __dataclass__init__fields__25__default,
            top_p: __dataclass__init__fields__26__annotation = __dataclass__init__fields__26__default,
            user: __dataclass__init__fields__27__annotation = __dataclass__init__fields__27__default,
            web_search_options: __dataclass__init__fields__28__annotation = __dataclass__init__fields__28__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'messages', messages)
            __dataclass__object_setattr(self, 'model', model)
            __dataclass__object_setattr(self, 'audio', audio)
            __dataclass__object_setattr(self, 'frequency_penalty', frequency_penalty)
            __dataclass__object_setattr(self, 'logit_bias', logit_bias)
            __dataclass__object_setattr(self, 'logprobs', logprobs)
            __dataclass__object_setattr(self, 'max_completion_tokens', max_completion_tokens)
            __dataclass__object_setattr(self, 'max_tokens', max_tokens)
            __dataclass__object_setattr(self, 'metadata', metadata)
            __dataclass__object_setattr(self, 'modalities', modalities)
            __dataclass__object_setattr(self, 'n', n)
            __dataclass__object_setattr(self, 'parallel_tool_calls', parallel_tool_calls)
            __dataclass__object_setattr(self, 'prediction', prediction)
            __dataclass__object_setattr(self, 'presence_penalty', presence_penalty)
            __dataclass__object_setattr(self, 'reasoning_effort', reasoning_effort)
            __dataclass__object_setattr(self, 'response_format', response_format)
            __dataclass__object_setattr(self, 'seed', seed)
            __dataclass__object_setattr(self, 'service_tier', service_tier)
            __dataclass__object_setattr(self, 'stop', stop)
            __dataclass__object_setattr(self, 'store', store)
            __dataclass__object_setattr(self, 'stream', stream)
            __dataclass__object_setattr(self, 'stream_options', stream_options)
            __dataclass__object_setattr(self, 'temperature', temperature)
            __dataclass__object_setattr(self, 'tool_choice', tool_choice)
            __dataclass__object_setattr(self, 'tools', tools)
            __dataclass__object_setattr(self, 'top_logprobs', top_logprobs)
            __dataclass__object_setattr(self, 'top_p', top_p)
            __dataclass__object_setattr(self, 'user', user)
            __dataclass__object_setattr(self, 'web_search_options', web_search_options)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"messages={self.messages!r}")
            parts.append(f"model={self.model!r}")
            parts.append(f"audio={self.audio!r}")
            parts.append(f"frequency_penalty={self.frequency_penalty!r}")
            parts.append(f"logit_bias={self.logit_bias!r}")
            parts.append(f"logprobs={self.logprobs!r}")
            parts.append(f"max_completion_tokens={self.max_completion_tokens!r}")
            parts.append(f"max_tokens={self.max_tokens!r}")
            parts.append(f"metadata={self.metadata!r}")
            parts.append(f"modalities={self.modalities!r}")
            parts.append(f"n={self.n!r}")
            parts.append(f"parallel_tool_calls={self.parallel_tool_calls!r}")
            parts.append(f"prediction={self.prediction!r}")
            parts.append(f"presence_penalty={self.presence_penalty!r}")
            parts.append(f"reasoning_effort={self.reasoning_effort!r}")
            parts.append(f"response_format={self.response_format!r}")
            parts.append(f"seed={self.seed!r}")
            parts.append(f"service_tier={self.service_tier!r}")
            parts.append(f"stop={self.stop!r}")
            parts.append(f"store={self.store!r}")
            parts.append(f"stream={self.stream!r}")
            parts.append(f"stream_options={self.stream_options!r}")
            parts.append(f"temperature={self.temperature!r}")
            parts.append(f"tool_choice={self.tool_choice!r}")
            parts.append(f"tools={self.tools!r}")
            parts.append(f"top_logprobs={self.top_logprobs!r}")
            parts.append(f"top_p={self.top_p!r}")
            parts.append(f"user={self.user!r}")
            parts.append(f"web_search_options={self.web_search_options!r}")
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
        "Plans(tup=(CopyPlan(fields=('include_usage',)), EqPlan(fields=('include_usage',)), FrozenPlan(fields=('include"
        "_usage',), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('include_usage',), cache=False), "
        "InitPlan(fields=(InitPlan.Field(name='include_usage', annotation=OpRef(name='init.fields.0.annotation'), defau"
        "lt=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType."
        "INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self', std_params=(), kw_only_params=('i"
        "nclude_usage',), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fiel"
        "ds=(ReprPlan.Field(name='include_usage', kw_only=True, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='89e270d921a6b67e79d7a3d1935a58c8228c8d17',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.chatcompletion.request', 'ChatCompletionRequest.StreamOptions'),
    ),
)
def _process_dataclass__89e270d921a6b67e79d7a3d1935a58c8228c8d17():
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
                include_usage=self.include_usage,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.include_usage == other.include_usage
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'include_usage',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'include_usage',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.include_usage,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            include_usage: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'include_usage', include_usage)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"include_usage={self.include_usage!r}")
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
        "Plans(tup=(CopyPlan(fields=('format', 'voice')), EqPlan(fields=('format', 'voice')), FrozenPlan(fields=('forma"
        "t', 'voice'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('format', 'voice'), cache=Fals"
        "e), InitPlan(fields=(InitPlan.Field(name='format', annotation=OpRef(name='init.fields.0.annotation'), default="
        "None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=No"
        "ne, check_type=None), InitPlan.Field(name='voice', annotation=OpRef(name='init.fields.1.annotation'), default="
        "None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=No"
        "ne, check_type=None)), self_param='self', std_params=(), kw_only_params=('format', 'voice'), frozen=True, slot"
        "s=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='format', "
        "kw_only=True, fn=None), ReprPlan.Field(name='voice', kw_only=True, fn=None)), id=False, terse=False, default_f"
        "n=None)))"
    ),
    plan_repr_sha1='c047ab836faa261ad70d3dfc0fa37873ecb1ed61',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.chatcompletion.request', 'ChatCompletionRequestAudio'),
    ),
)
def _process_dataclass__c047ab836faa261ad70d3dfc0fa37873ecb1ed61():
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
                format=self.format,
                voice=self.voice,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.format == other.format and
                self.voice == other.voice
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'format',
            'voice',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'format',
            'voice',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.format,
                self.voice,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            format: __dataclass__init__fields__0__annotation,
            voice: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'format', format)
            __dataclass__object_setattr(self, 'voice', voice)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"format={self.format!r}")
            parts.append(f"voice={self.voice!r}")
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
        "Plans(tup=(CopyPlan(fields=('function', 'type')), EqPlan(fields=('function', 'type')), FrozenPlan(fields=('fun"
        "ction', 'type'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('function', 'type'), cache="
        "False), InitPlan(fields=(InitPlan.Field(name='function', annotation=OpRef(name='init.fields.0.annotation'), de"
        "fault=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valid"
        "ate=None, check_type=None), InitPlan.Field(name='type', annotation=OpRef(name='init.fields.1.annotation'), def"
        "ault=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldTyp"
        "e.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=('function',), kw_onl"
        "y_params=('type',), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(f"
        "ields=(ReprPlan.Field(name='function', kw_only=False, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='ee16f2c04dad1b5d2c06434a3cbf758d293ba00e',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.chatcompletion.request', 'ChatCompletionRequestNamedToolChoice'),
        ('ommlds.backends.openai.protocol.chatcompletion.request', 'ChatCompletionRequestTool'),
    ),
)
def _process_dataclass__ee16f2c04dad1b5d2c06434a3cbf758d293ba00e():
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
                function=self.function,
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
                self.function == other.function and
                self.type == other.type
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'function',
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
            'function',
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
                self.function,
                self.type,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            function: __dataclass__init__fields__0__annotation,
            *,
            type: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'function', function)
            __dataclass__object_setattr(self, 'type', type)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"function={self.function!r}")
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
        " std_params=('name',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), valida"
        "te_fns=()), ReprPlan(fields=(ReprPlan.Field(name='name', kw_only=False, fn=None),), id=False, terse=False, def"
        "ault_fn=None)))"
    ),
    plan_repr_sha1='a8c678a92ec79b6aa505feedefe70ee7fef92ccd',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.chatcompletion.request', 'ChatCompletionRequestNamedToolChoice.Function'),
    ),
)
def _process_dataclass__a8c678a92ec79b6aa505feedefe70ee7fef92ccd():
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
        "Plans(tup=(CopyPlan(fields=('content', 'type')), EqPlan(fields=('content', 'type')), FrozenPlan(fields=('conte"
        "nt', 'type'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('content', 'type'), cache=Fals"
        "e), InitPlan(fields=(InitPlan.Field(name='content', annotation=OpRef(name='init.fields.0.annotation'), default"
        "=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=N"
        "one, check_type=None), InitPlan.Field(name='type', annotation=OpRef(name='init.fields.1.annotation'), default="
        "OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INS"
        "TANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('conte"
        "nt', 'type'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields="
        "(ReprPlan.Field(name='content', kw_only=True, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='0411eeee08fe6bc992a54c035c1a7fbcbdc3ce8d',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.chatcompletion.request', 'ChatCompletionRequestPrediction'),
    ),
)
def _process_dataclass__0411eeee08fe6bc992a54c035c1a7fbcbdc3ce8d():
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
                content=self.content,
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
                self.content == other.content and
                self.type == other.type
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'content',
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
            'content',
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
                self.content,
                self.type,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            content: __dataclass__init__fields__0__annotation,
            type: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'content', content)
            __dataclass__object_setattr(self, 'type', type)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"content={self.content!r}")
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
        "Plans(tup=(CopyPlan(fields=('name', 'description', 'parameters', 'strict')), EqPlan(fields=('name', 'descripti"
        "on', 'parameters', 'strict')), FrozenPlan(fields=('name', 'description', 'parameters', 'strict'), allow_dynami"
        "c_dunder_attrs=False), HashPlan(action='add', fields=('name', 'description', 'parameters', 'strict'), cache=Fa"
        "lse), InitPlan(fields=(InitPlan.Field(name='name', annotation=OpRef(name='init.fields.0.annotation'), default="
        "None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=No"
        "ne, check_type=None), InitPlan.Field(name='description', annotation=OpRef(name='init.fields.1.annotation'), de"
        "fault=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldTy"
        "pe.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='parameters', annotation=OpRef("
        "name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True"
        ", override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field("
        "name='strict', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'),"
        " default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, c"
        "heck_type=None)), self_param='self', std_params=(), kw_only_params=('name', 'description', 'parameters', 'stri"
        "ct'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPla"
        "n.Field(name='name', kw_only=True, fn=None), ReprPlan.Field(name='description', kw_only=True, fn=None), ReprPl"
        "an.Field(name='parameters', kw_only=True, fn=None), ReprPlan.Field(name='strict', kw_only=True, fn=None)), id="
        "False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='01898cc3dbb4ed54bd59e50ec3af9225452f6483',
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
        ('ommlds.backends.openai.protocol.chatcompletion.request', 'ChatCompletionRequestTool.Function'),
        ('ommlds.backends.openai.protocol.responses.request', 'FunctionResponsesTool'),
    ),
)
def _process_dataclass__01898cc3dbb4ed54bd59e50ec3af9225452f6483():
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
                name=self.name,
                description=self.description,
                parameters=self.parameters,
                strict=self.strict,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
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
                self.parameters == other.parameters and
                self.strict == other.strict
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'name',
            'description',
            'parameters',
            'strict',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'parameters',
            'strict',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.parameters,
                self.strict,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            name: __dataclass__init__fields__0__annotation,
            description: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            parameters: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            strict: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'description', description)
            __dataclass__object_setattr(self, 'parameters', parameters)
            __dataclass__object_setattr(self, 'strict', strict)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"name={self.name!r}")
            parts.append(f"description={self.description!r}")
            parts.append(f"parameters={self.parameters!r}")
            parts.append(f"strict={self.strict!r}")
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
        "Plans(tup=(CopyPlan(fields=('search_context_size', 'user_location')), EqPlan(fields=('search_context_size', 'u"
        "ser_location')), FrozenPlan(fields=('search_context_size', 'user_location'), allow_dynamic_dunder_attrs=False)"
        ", HashPlan(action='add', fields=('search_context_size', 'user_location'), cache=False), InitPlan(fields=(InitP"
        "lan.Field(name='search_context_size', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='i"
        "nit.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce"
        "=None, validate=None, check_type=None), InitPlan.Field(name='user_location', annotation=OpRef(name='init.field"
        "s.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False"
        ", field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params="
        "(), kw_only_params=('search_context_size', 'user_location'), frozen=True, slots=False, post_init_params=None, "
        "init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='search_context_size', kw_only=True, fn=No"
        "ne), ReprPlan.Field(name='user_location', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='6b7fa47f25fef7c23ef841a417d4da27143c6699',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.chatcompletion.request', 'ChatCompletionRequestWebSearchOptions'),
    ),
)
def _process_dataclass__6b7fa47f25fef7c23ef841a417d4da27143c6699():
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
                search_context_size=self.search_context_size,
                user_location=self.user_location,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.search_context_size == other.search_context_size and
                self.user_location == other.user_location
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'search_context_size',
            'user_location',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'search_context_size',
            'user_location',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.search_context_size,
                self.user_location,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            search_context_size: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            user_location: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'search_context_size', search_context_size)
            __dataclass__object_setattr(self, 'user_location', user_location)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"search_context_size={self.search_context_size!r}")
            parts.append(f"user_location={self.user_location!r}")
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
        "Plans(tup=(CopyPlan(fields=('approximate', 'type')), EqPlan(fields=('approximate', 'type')), FrozenPlan(fields"
        "=('approximate', 'type'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('approximate', 'ty"
        "pe'), cache=False), InitPlan(fields=(InitPlan.Field(name='approximate', annotation=OpRef(name='init.fields.0.a"
        "nnotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coe"
        "rce=None, validate=None, check_type=None), InitPlan.Field(name='type', annotation=OpRef(name='init.fields.1.an"
        "notation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, fiel"
        "d_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw"
        "_only_params=('approximate', 'type'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_f"
        "ns=()), ReprPlan(fields=(ReprPlan.Field(name='approximate', kw_only=True, fn=None),), id=False, terse=False, d"
        "efault_fn=None)))"
    ),
    plan_repr_sha1='e71e091e435af06aadbfa9172601238d550ec877',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.chatcompletion.request', 'ChatCompletionRequestWebSearchOptions.UserLocation'),
    ),
)
def _process_dataclass__e71e091e435af06aadbfa9172601238d550ec877():
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
                approximate=self.approximate,
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
                self.approximate == other.approximate and
                self.type == other.type
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'approximate',
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
            'approximate',
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
                self.approximate,
                self.type,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            approximate: __dataclass__init__fields__0__annotation,
            type: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'approximate', approximate)
            __dataclass__object_setattr(self, 'type', type)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"approximate={self.approximate!r}")
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
        "Plans(tup=(CopyPlan(fields=('city', 'country', 'region', 'timezone')), EqPlan(fields=('city', 'country', 'regi"
        "on', 'timezone')), FrozenPlan(fields=('city', 'country', 'region', 'timezone'), allow_dynamic_dunder_attrs=Fal"
        "se), HashPlan(action='add', fields=('city', 'country', 'region', 'timezone'), cache=False), InitPlan(fields=(I"
        "nitPlan.Field(name='city', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields."
        "0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, vali"
        "date=None, check_type=None), InitPlan.Field(name='country', annotation=OpRef(name='init.fields.1.annotation'),"
        " default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=Fiel"
        "dType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='region', annotation=OpRef(n"
        "ame='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True,"
        " override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(n"
        "ame='timezone', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default')"
        ", default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, "
        "check_type=None)), self_param='self', std_params=(), kw_only_params=('city', 'country', 'region', 'timezone'),"
        " frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Fie"
        "ld(name='city', kw_only=True, fn=None), ReprPlan.Field(name='country', kw_only=True, fn=None), ReprPlan.Field("
        "name='region', kw_only=True, fn=None), ReprPlan.Field(name='timezone', kw_only=True, fn=None)), id=False, ters"
        "e=False, default_fn=None)))"
    ),
    plan_repr_sha1='57f153c4c546fa5429d79eedff004cd245c9ba6f',
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
        ('ommlds.backends.openai.protocol.chatcompletion.request', 'ChatCompletionRequestWebSearchOptions.UserLocation.Approximate'),
    ),
)
def _process_dataclass__57f153c4c546fa5429d79eedff004cd245c9ba6f():
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
                city=self.city,
                country=self.country,
                region=self.region,
                timezone=self.timezone,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.city == other.city and
                self.country == other.country and
                self.region == other.region and
                self.timezone == other.timezone
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'city',
            'country',
            'region',
            'timezone',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'city',
            'country',
            'region',
            'timezone',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.city,
                self.country,
                self.region,
                self.timezone,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            city: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            country: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            region: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            timezone: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'city', city)
            __dataclass__object_setattr(self, 'country', country)
            __dataclass__object_setattr(self, 'region', region)
            __dataclass__object_setattr(self, 'timezone', timezone)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"city={self.city!r}")
            parts.append(f"country={self.country!r}")
            parts.append(f"region={self.region!r}")
            parts.append(f"timezone={self.timezone!r}")
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
        "Plans(tup=(CopyPlan(fields=('id', 'choices', 'created', 'model', 'object', 'service_tier', 'system_fingerprint"
        "', 'usage')), EqPlan(fields=('id', 'choices', 'created', 'model', 'object', 'service_tier', 'system_fingerprin"
        "t', 'usage')), FrozenPlan(fields=('id', 'choices', 'created', 'model', 'object', 'service_tier', 'system_finge"
        "rprint', 'usage'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('id', 'choices', 'created"
        "', 'model', 'object', 'service_tier', 'system_fingerprint', 'usage'), cache=False), InitPlan(fields=(InitPlan."
        "Field(name='id', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=T"
        "rue, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fie"
        "ld(name='choices', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init"
        "=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.F"
        "ield(name='created', annotation=OpRef(name='init.fields.2.annotation'), default=None, default_factory=None, in"
        "it=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan"
        ".Field(name='model', annotation=OpRef(name='init.fields.3.annotation'), default=None, default_factory=None, in"
        "it=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan"
        ".Field(name='object', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.def"
        "ault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate="
        "None, check_type=None), InitPlan.Field(name='service_tier', annotation=OpRef(name='init.fields.5.annotation'),"
        " default=OpRef(name='init.fields.5.default'), default_factory=None, init=True, override=False, field_type=Fiel"
        "dType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='system_fingerprint', annota"
        "tion=OpRef(name='init.fields.6.annotation'), default=OpRef(name='init.fields.6.default'), default_factory=None"
        ", init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), Init"
        "Plan.Field(name='usage', annotation=OpRef(name='init.fields.7.annotation'), default=OpRef(name='init.fields.7."
        "default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valida"
        "te=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('id', 'choices', 'created', 'mod"
        "el', 'object', 'service_tier', 'system_fingerprint', 'usage'), frozen=True, slots=False, post_init_params=None"
        ", init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='id', kw_only=True, fn=None), ReprPlan.F"
        "ield(name='choices', kw_only=True, fn=None), ReprPlan.Field(name='created', kw_only=True, fn=None), ReprPlan.F"
        "ield(name='model', kw_only=True, fn=None), ReprPlan.Field(name='service_tier', kw_only=True, fn=None), ReprPla"
        "n.Field(name='system_fingerprint', kw_only=True, fn=None), ReprPlan.Field(name='usage', kw_only=True, fn=None)"
        "), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='b602fb539c3c1ecfe31a941173b179f373b5dade',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
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
        ('ommlds.backends.openai.protocol.chatcompletion.response', 'ChatCompletionResponse'),
    ),
)
def _process_dataclass__b602fb539c3c1ecfe31a941173b179f373b5dade():
    def _process_dataclass(
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
                id=self.id,
                choices=self.choices,
                created=self.created,
                model=self.model,
                object=self.object,
                service_tier=self.service_tier,
                system_fingerprint=self.system_fingerprint,
                usage=self.usage,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
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
                self.choices == other.choices and
                self.created == other.created and
                self.model == other.model and
                self.object == other.object and
                self.service_tier == other.service_tier and
                self.system_fingerprint == other.system_fingerprint and
                self.usage == other.usage
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'id',
            'choices',
            'created',
            'model',
            'object',
            'service_tier',
            'system_fingerprint',
            'usage',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'choices',
            'created',
            'model',
            'object',
            'service_tier',
            'system_fingerprint',
            'usage',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.choices,
                self.created,
                self.model,
                self.object,
                self.service_tier,
                self.system_fingerprint,
                self.usage,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            id: __dataclass__init__fields__0__annotation,
            choices: __dataclass__init__fields__1__annotation,
            created: __dataclass__init__fields__2__annotation,
            model: __dataclass__init__fields__3__annotation,
            object: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            service_tier: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
            system_fingerprint: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
            usage: __dataclass__init__fields__7__annotation = __dataclass__init__fields__7__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'choices', choices)
            __dataclass__object_setattr(self, 'created', created)
            __dataclass__object_setattr(self, 'model', model)
            __dataclass__object_setattr(self, 'object', object)
            __dataclass__object_setattr(self, 'service_tier', service_tier)
            __dataclass__object_setattr(self, 'system_fingerprint', system_fingerprint)
            __dataclass__object_setattr(self, 'usage', usage)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"id={self.id!r}")
            parts.append(f"choices={self.choices!r}")
            parts.append(f"created={self.created!r}")
            parts.append(f"model={self.model!r}")
            parts.append(f"service_tier={self.service_tier!r}")
            parts.append(f"system_fingerprint={self.system_fingerprint!r}")
            parts.append(f"usage={self.usage!r}")
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
        "Plans(tup=(CopyPlan(fields=('finish_reason', 'index', 'logprobs', 'message')), EqPlan(fields=('finish_reason',"
        " 'index', 'logprobs', 'message')), FrozenPlan(fields=('finish_reason', 'index', 'logprobs', 'message'), allow_"
        "dynamic_dunder_attrs=False), HashPlan(action='add', fields=('finish_reason', 'index', 'logprobs', 'message'), "
        "cache=False), InitPlan(fields=(InitPlan.Field(name='finish_reason', annotation=OpRef(name='init.fields.0.annot"
        "ation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce="
        "None, validate=None, check_type=None), InitPlan.Field(name='index', annotation=OpRef(name='init.fields.1.annot"
        "ation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce="
        "None, validate=None, check_type=None), InitPlan.Field(name='logprobs', annotation=OpRef(name='init.fields.2.an"
        "notation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, fiel"
        "d_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='message', annota"
        "tion=OpRef(name='init.fields.3.annotation'), default=None, default_factory=None, init=True, override=False, fi"
        "eld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), "
        "kw_only_params=('finish_reason', 'index', 'logprobs', 'message'), frozen=True, slots=False, post_init_params=N"
        "one, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='finish_reason', kw_only=True, fn=Non"
        "e), ReprPlan.Field(name='index', kw_only=True, fn=None), ReprPlan.Field(name='logprobs', kw_only=True, fn=None"
        "), ReprPlan.Field(name='message', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='44b10f936c3932df17be0708f2449a883036da63',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.chatcompletion.response', 'ChatCompletionResponseChoice'),
    ),
)
def _process_dataclass__44b10f936c3932df17be0708f2449a883036da63():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
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
                finish_reason=self.finish_reason,
                index=self.index,
                logprobs=self.logprobs,
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
                self.finish_reason == other.finish_reason and
                self.index == other.index and
                self.logprobs == other.logprobs and
                self.message == other.message
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'finish_reason',
            'index',
            'logprobs',
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
            'finish_reason',
            'index',
            'logprobs',
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
                self.finish_reason,
                self.index,
                self.logprobs,
                self.message,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            finish_reason: __dataclass__init__fields__0__annotation,
            index: __dataclass__init__fields__1__annotation,
            logprobs: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            message: __dataclass__init__fields__3__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'finish_reason', finish_reason)
            __dataclass__object_setattr(self, 'index', index)
            __dataclass__object_setattr(self, 'logprobs', logprobs)
            __dataclass__object_setattr(self, 'message', message)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"finish_reason={self.finish_reason!r}")
            parts.append(f"index={self.index!r}")
            parts.append(f"logprobs={self.logprobs!r}")
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
        "Plans(tup=(CopyPlan(fields=('content', 'refusal', 'reasoning', 'role', 'annotations', 'audio', 'tool_calls')),"
        " EqPlan(fields=('content', 'refusal', 'reasoning', 'role', 'annotations', 'audio', 'tool_calls')), FrozenPlan("
        "fields=('content', 'refusal', 'reasoning', 'role', 'annotations', 'audio', 'tool_calls'), allow_dynamic_dunder"
        "_attrs=False), HashPlan(action='add', fields=('content', 'refusal', 'reasoning', 'role', 'annotations', 'audio"
        "', 'tool_calls'), cache=False), InitPlan(fields=(InitPlan.Field(name='content', annotation=OpRef(name='init.fi"
        "elds.0.annotation'), default=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=Fa"
        "lse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='refusal"
        "', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_fac"
        "tory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=No"
        "ne), InitPlan.Field(name='reasoning', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='i"
        "nit.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce"
        "=None, validate=None, check_type=None), InitPlan.Field(name='role', annotation=OpRef(name='init.fields.3.annot"
        "ation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, field_t"
        "ype=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='annotations', annot"
        "ation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_factory=Non"
        "e, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), Ini"
        "tPlan.Field(name='audio', annotation=OpRef(name='init.fields.5.annotation'), default=OpRef(name='init.fields.5"
        ".default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valid"
        "ate=None, check_type=None), InitPlan.Field(name='tool_calls', annotation=OpRef(name='init.fields.6.annotation'"
        "), default=OpRef(name='init.fields.6.default'), default_factory=None, init=True, override=False, field_type=Fi"
        "eldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_par"
        "ams=('content', 'refusal', 'reasoning', 'role', 'annotations', 'audio', 'tool_calls'), frozen=True, slots=Fals"
        "e, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='content', kw_on"
        "ly=True, fn=None), ReprPlan.Field(name='refusal', kw_only=True, fn=None), ReprPlan.Field(name='reasoning', kw_"
        "only=True, fn=None), ReprPlan.Field(name='annotations', kw_only=True, fn=None), ReprPlan.Field(name='audio', k"
        "w_only=True, fn=None), ReprPlan.Field(name='tool_calls', kw_only=True, fn=None)), id=False, terse=False, defau"
        "lt_fn=None)))"
    ),
    plan_repr_sha1='e20169c11dfa5f0256c063c8677513b9785fd428',
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
        '__dataclass__init__fields__6__annotation',
        '__dataclass__init__fields__6__default',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.chatcompletion.response', 'ChatCompletionResponseMessage'),
    ),
)
def _process_dataclass__e20169c11dfa5f0256c063c8677513b9785fd428():
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
                content=self.content,
                refusal=self.refusal,
                reasoning=self.reasoning,
                role=self.role,
                annotations=self.annotations,
                audio=self.audio,
                tool_calls=self.tool_calls,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
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
                self.refusal == other.refusal and
                self.reasoning == other.reasoning and
                self.role == other.role and
                self.annotations == other.annotations and
                self.audio == other.audio and
                self.tool_calls == other.tool_calls
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'content',
            'refusal',
            'reasoning',
            'role',
            'annotations',
            'audio',
            'tool_calls',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'refusal',
            'reasoning',
            'role',
            'annotations',
            'audio',
            'tool_calls',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.refusal,
                self.reasoning,
                self.role,
                self.annotations,
                self.audio,
                self.tool_calls,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            content: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            refusal: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            reasoning: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            role: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            annotations: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            audio: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
            tool_calls: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'content', content)
            __dataclass__object_setattr(self, 'refusal', refusal)
            __dataclass__object_setattr(self, 'reasoning', reasoning)
            __dataclass__object_setattr(self, 'role', role)
            __dataclass__object_setattr(self, 'annotations', annotations)
            __dataclass__object_setattr(self, 'audio', audio)
            __dataclass__object_setattr(self, 'tool_calls', tool_calls)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"content={self.content!r}")
            parts.append(f"refusal={self.refusal!r}")
            parts.append(f"reasoning={self.reasoning!r}")
            parts.append(f"annotations={self.annotations!r}")
            parts.append(f"audio={self.audio!r}")
            parts.append(f"tool_calls={self.tool_calls!r}")
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
        "Plans(tup=(CopyPlan(fields=('type', 'url_citation')), EqPlan(fields=('type', 'url_citation')), FrozenPlan(fiel"
        "ds=('type', 'url_citation'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('type', 'url_ci"
        "tation'), cache=False), InitPlan(fields=(InitPlan.Field(name='type', annotation=OpRef(name='init.fields.0.anno"
        "tation'), default=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_"
        "type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='url_citation', ann"
        "otation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False,"
        " field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=("
        "), kw_only_params=('type', 'url_citation'), frozen=True, slots=False, post_init_params=None, init_fns=(), vali"
        "date_fns=()), ReprPlan(fields=(ReprPlan.Field(name='url_citation', kw_only=True, fn=None),), id=False, terse=F"
        "alse, default_fn=None)))"
    ),
    plan_repr_sha1='e247f654503e25d14969a16a33fb7ce13e734134',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.chatcompletion.response', 'ChatCompletionResponseMessage.Annotation'),
    ),
)
def _process_dataclass__e247f654503e25d14969a16a33fb7ce13e734134():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                type=self.type,
                url_citation=self.url_citation,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
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
                self.url_citation == other.url_citation
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'type',
            'url_citation',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'url_citation',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.url_citation,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            type: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            url_citation: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'type', type)
            __dataclass__object_setattr(self, 'url_citation', url_citation)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"url_citation={self.url_citation!r}")
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
        "Plans(tup=(CopyPlan(fields=('end_index', 'start_index', 'title', 'url')), EqPlan(fields=('end_index', 'start_i"
        "ndex', 'title', 'url')), FrozenPlan(fields=('end_index', 'start_index', 'title', 'url'), allow_dynamic_dunder_"
        "attrs=False), HashPlan(action='add', fields=('end_index', 'start_index', 'title', 'url'), cache=False), InitPl"
        "an(fields=(InitPlan.Field(name='end_index', annotation=OpRef(name='init.fields.0.annotation'), default=None, d"
        "efault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, che"
        "ck_type=None), InitPlan.Field(name='start_index', annotation=OpRef(name='init.fields.1.annotation'), default=N"
        "one, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=Non"
        "e, check_type=None), InitPlan.Field(name='title', annotation=OpRef(name='init.fields.2.annotation'), default=N"
        "one, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=Non"
        "e, check_type=None), InitPlan.Field(name='url', annotation=OpRef(name='init.fields.3.annotation'), default=Non"
        "e, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None,"
        " check_type=None)), self_param='self', std_params=(), kw_only_params=('end_index', 'start_index', 'title', 'ur"
        "l'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan"
        ".Field(name='end_index', kw_only=True, fn=None), ReprPlan.Field(name='start_index', kw_only=True, fn=None), Re"
        "prPlan.Field(name='title', kw_only=True, fn=None), ReprPlan.Field(name='url', kw_only=True, fn=None)), id=Fals"
        "e, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='892693ba44c86e2caeb208be04dd1dce08c7249e',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.chatcompletion.response', 'ChatCompletionResponseMessage.Annotation.UrlCitation'),
    ),
)
def _process_dataclass__892693ba44c86e2caeb208be04dd1dce08c7249e():
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
                end_index=self.end_index,
                start_index=self.start_index,
                title=self.title,
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
                self.end_index == other.end_index and
                self.start_index == other.start_index and
                self.title == other.title and
                self.url == other.url
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'end_index',
            'start_index',
            'title',
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
            'end_index',
            'start_index',
            'title',
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
                self.end_index,
                self.start_index,
                self.title,
                self.url,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            end_index: __dataclass__init__fields__0__annotation,
            start_index: __dataclass__init__fields__1__annotation,
            title: __dataclass__init__fields__2__annotation,
            url: __dataclass__init__fields__3__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'end_index', end_index)
            __dataclass__object_setattr(self, 'start_index', start_index)
            __dataclass__object_setattr(self, 'title', title)
            __dataclass__object_setattr(self, 'url', url)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"end_index={self.end_index!r}")
            parts.append(f"start_index={self.start_index!r}")
            parts.append(f"title={self.title!r}")
            parts.append(f"url={self.url!r}")
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
        "Plans(tup=(CopyPlan(fields=('id', 'data', 'expires_at', 'transcript')), EqPlan(fields=('id', 'data', 'expires_"
        "at', 'transcript')), FrozenPlan(fields=('id', 'data', 'expires_at', 'transcript'), allow_dynamic_dunder_attrs="
        "False), HashPlan(action='add', fields=('id', 'data', 'expires_at', 'transcript'), cache=False), InitPlan(field"
        "s=(InitPlan.Field(name='id', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory="
        "None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), "
        "InitPlan.Field(name='data', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=N"
        "one, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), I"
        "nitPlan.Field(name='expires_at', annotation=OpRef(name='init.fields.2.annotation'), default=None, default_fact"
        "ory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=Non"
        "e), InitPlan.Field(name='transcript', annotation=OpRef(name='init.fields.3.annotation'), default=None, default"
        "_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_typ"
        "e=None)), self_param='self', std_params=(), kw_only_params=('id', 'data', 'expires_at', 'transcript'), frozen="
        "True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name="
        "'id', kw_only=True, fn=None), ReprPlan.Field(name='data', kw_only=True, fn=None), ReprPlan.Field(name='expires"
        "_at', kw_only=True, fn=None), ReprPlan.Field(name='transcript', kw_only=True, fn=None)), id=False, terse=False"
        ", default_fn=None)))"
    ),
    plan_repr_sha1='4f00965a6065cd8a0d1c970720f564d433563eb6',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.chatcompletion.response', 'ChatCompletionResponseMessage.Audio'),
    ),
)
def _process_dataclass__4f00965a6065cd8a0d1c970720f564d433563eb6():
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
                id=self.id,
                data=self.data,
                expires_at=self.expires_at,
                transcript=self.transcript,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
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
                self.data == other.data and
                self.expires_at == other.expires_at and
                self.transcript == other.transcript
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'id',
            'data',
            'expires_at',
            'transcript',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'data',
            'expires_at',
            'transcript',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.data,
                self.expires_at,
                self.transcript,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            id: __dataclass__init__fields__0__annotation,
            data: __dataclass__init__fields__1__annotation,
            expires_at: __dataclass__init__fields__2__annotation,
            transcript: __dataclass__init__fields__3__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'data', data)
            __dataclass__object_setattr(self, 'expires_at', expires_at)
            __dataclass__object_setattr(self, 'transcript', transcript)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"id={self.id!r}")
            parts.append(f"data={self.data!r}")
            parts.append(f"expires_at={self.expires_at!r}")
            parts.append(f"transcript={self.transcript!r}")
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
        ('ommlds.backends.openai.protocol.chatcompletion.responseformat', 'JsonObjectChatCompletionResponseFormat'),
        ('ommlds.backends.openai.protocol.chatcompletion.responseformat', 'TextChatCompletionResponseFormat'),
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
        "Plans(tup=(CopyPlan(fields=('json_schema',)), EqPlan(fields=('json_schema',)), FrozenPlan(fields=('json_schema"
        "',), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('json_schema',), cache=False), InitPlan"
        "(fields=(InitPlan.Field(name='json_schema', annotation=OpRef(name='init.fields.0.annotation'), default=None, d"
        "efault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, che"
        "ck_type=None),), self_param='self', std_params=(), kw_only_params=('json_schema',), frozen=True, slots=False, "
        "post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='json_schema', kw_o"
        "nly=True, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='6082104726540db00af83187c5f190d98e893ded',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.chatcompletion.responseformat', 'JsonSchemaChatCompletionResponseFormat'),
    ),
)
def _process_dataclass__6082104726540db00af83187c5f190d98e893ded():
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
                json_schema=self.json_schema,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.json_schema == other.json_schema
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'json_schema',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'json_schema',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.json_schema,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            json_schema: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'json_schema', json_schema)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"json_schema={self.json_schema!r}")
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
        "Plans(tup=(CopyPlan(fields=('name', 'description', 'schema', 'strict')), EqPlan(fields=('name', 'description',"
        " 'schema', 'strict')), FrozenPlan(fields=('name', 'description', 'schema', 'strict'), allow_dynamic_dunder_att"
        "rs=False), HashPlan(action='add', fields=('name', 'description', 'schema', 'strict'), cache=False), InitPlan(f"
        "ields=(InitPlan.Field(name='name', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_fa"
        "ctory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=N"
        "one), InitPlan.Field(name='description', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name"
        "='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coe"
        "rce=None, validate=None, check_type=None), InitPlan.Field(name='schema', annotation=OpRef(name='init.fields.2."
        "annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, fi"
        "eld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='strict', annot"
        "ation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=Non"
        "e, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), se"
        "lf_param='self', std_params=(), kw_only_params=('name', 'description', 'schema', 'strict'), frozen=True, slots"
        "=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='name', kw_"
        "only=True, fn=None), ReprPlan.Field(name='description', kw_only=True, fn=None), ReprPlan.Field(name='schema', "
        "kw_only=True, fn=None), ReprPlan.Field(name='strict', kw_only=True, fn=None)), id=False, terse=False, default_"
        "fn=None)))"
    ),
    plan_repr_sha1='fe9949b6c4c778fd87c0573554efffc59636dd5b',
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
        ('ommlds.backends.openai.protocol.chatcompletion.responseformat', 'JsonSchemaChatCompletionResponseFormat.JsonSchema'),
    ),
)
def _process_dataclass__fe9949b6c4c778fd87c0573554efffc59636dd5b():
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
                name=self.name,
                description=self.description,
                schema=self.schema,
                strict=self.strict,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
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
                self.schema == other.schema and
                self.strict == other.strict
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'name',
            'description',
            'schema',
            'strict',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'schema',
            'strict',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.schema,
                self.strict,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            name: __dataclass__init__fields__0__annotation,
            description: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            schema: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            strict: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'description', description)
            __dataclass__object_setattr(self, 'schema', schema)
            __dataclass__object_setattr(self, 'strict', strict)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"name={self.name!r}")
            parts.append(f"description={self.description!r}")
            parts.append(f"schema={self.schema!r}")
            parts.append(f"strict={self.strict!r}")
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
        "Plans(tup=(CopyPlan(fields=('token', 'bytes', 'logprob', 'top_logprobs')), EqPlan(fields=('token', 'bytes', 'l"
        "ogprob', 'top_logprobs')), FrozenPlan(fields=('token', 'bytes', 'logprob', 'top_logprobs'), allow_dynamic_dund"
        "er_attrs=False), HashPlan(action='add', fields=('token', 'bytes', 'logprob', 'top_logprobs'), cache=False), In"
        "itPlan(fields=(InitPlan.Field(name='token', annotation=OpRef(name='init.fields.0.annotation'), default=None, d"
        "efault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, che"
        "ck_type=None), InitPlan.Field(name='bytes', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(n"
        "ame='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, "
        "coerce=None, validate=None, check_type=None), InitPlan.Field(name='logprob', annotation=OpRef(name='init.field"
        "s.2.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE"
        ", coerce=None, validate=None, check_type=None), InitPlan.Field(name='top_logprobs', annotation=OpRef(name='ini"
        "t.fields.3.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.I"
        "NSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('tok"
        "en', 'bytes', 'logprob', 'top_logprobs'), frozen=True, slots=False, post_init_params=None, init_fns=(), valida"
        "te_fns=()), ReprPlan(fields=(ReprPlan.Field(name='token', kw_only=True, fn=None), ReprPlan.Field(name='bytes',"
        " kw_only=True, fn=None), ReprPlan.Field(name='logprob', kw_only=True, fn=None), ReprPlan.Field(name='top_logpr"
        "obs', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='bfcb20219fa7ab1adf092df40f2b3ca41d9bcdb8',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.chatcompletion.tokenlogprob', 'ChatCompletionTokenLogprob'),
    ),
)
def _process_dataclass__bfcb20219fa7ab1adf092df40f2b3ca41d9bcdb8():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
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
                token=self.token,
                bytes=self.bytes,
                logprob=self.logprob,
                top_logprobs=self.top_logprobs,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.token == other.token and
                self.bytes == other.bytes and
                self.logprob == other.logprob and
                self.top_logprobs == other.top_logprobs
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'token',
            'bytes',
            'logprob',
            'top_logprobs',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'token',
            'bytes',
            'logprob',
            'top_logprobs',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.token,
                self.bytes,
                self.logprob,
                self.top_logprobs,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            token: __dataclass__init__fields__0__annotation,
            bytes: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            logprob: __dataclass__init__fields__2__annotation,
            top_logprobs: __dataclass__init__fields__3__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'token', token)
            __dataclass__object_setattr(self, 'bytes', bytes)
            __dataclass__object_setattr(self, 'logprob', logprob)
            __dataclass__object_setattr(self, 'top_logprobs', top_logprobs)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"token={self.token!r}")
            parts.append(f"bytes={self.bytes!r}")
            parts.append(f"logprob={self.logprob!r}")
            parts.append(f"top_logprobs={self.top_logprobs!r}")
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
        "Plans(tup=(CopyPlan(fields=('token', 'bytes', 'logprob')), EqPlan(fields=('token', 'bytes', 'logprob')), Froze"
        "nPlan(fields=('token', 'bytes', 'logprob'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=("
        "'token', 'bytes', 'logprob'), cache=False), InitPlan(fields=(InitPlan.Field(name='token', annotation=OpRef(nam"
        "e='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=Field"
        "Type.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='bytes', annotation=OpRef(nam"
        "e='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, o"
        "verride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(nam"
        "e='logprob', annotation=OpRef(name='init.fields.2.annotation'), default=None, default_factory=None, init=True,"
        " override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='sel"
        "f', std_params=(), kw_only_params=('token', 'bytes', 'logprob'), frozen=True, slots=False, post_init_params=No"
        "ne, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='token', kw_only=True, fn=None), ReprP"
        "lan.Field(name='bytes', kw_only=True, fn=None), ReprPlan.Field(name='logprob', kw_only=True, fn=None)), id=Fal"
        "se, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='e1af9be7f64c4eea692034674c3d64de8d125f04',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.chatcompletion.tokenlogprob', 'ChatCompletionTokenLogprob.TopLogprob'),
    ),
)
def _process_dataclass__e1af9be7f64c4eea692034674c3d64de8d125f04():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
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
                token=self.token,
                bytes=self.bytes,
                logprob=self.logprob,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.token == other.token and
                self.bytes == other.bytes and
                self.logprob == other.logprob
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'token',
            'bytes',
            'logprob',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'token',
            'bytes',
            'logprob',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.token,
                self.bytes,
                self.logprob,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            token: __dataclass__init__fields__0__annotation,
            bytes: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            logprob: __dataclass__init__fields__2__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'token', token)
            __dataclass__object_setattr(self, 'bytes', bytes)
            __dataclass__object_setattr(self, 'logprob', logprob)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"token={self.token!r}")
            parts.append(f"bytes={self.bytes!r}")
            parts.append(f"logprob={self.logprob!r}")
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
        "Plans(tup=(CopyPlan(fields=('completion_tokens', 'prompt_tokens', 'total_tokens', 'completion_tokens_details',"
        " 'prompt_tokens_details')), EqPlan(fields=('completion_tokens', 'prompt_tokens', 'total_tokens', 'completion_t"
        "okens_details', 'prompt_tokens_details')), FrozenPlan(fields=('completion_tokens', 'prompt_tokens', 'total_tok"
        "ens', 'completion_tokens_details', 'prompt_tokens_details'), allow_dynamic_dunder_attrs=False), HashPlan(actio"
        "n='add', fields=('completion_tokens', 'prompt_tokens', 'total_tokens', 'completion_tokens_details', 'prompt_to"
        "kens_details'), cache=False), InitPlan(fields=(InitPlan.Field(name='completion_tokens', annotation=OpRef(name="
        "'init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldTy"
        "pe.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='prompt_tokens', annotation=OpR"
        "ef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type"
        "=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='total_tokens', annotat"
        "ion=OpRef(name='init.fields.2.annotation'), default=None, default_factory=None, init=True, override=False, fie"
        "ld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='completion_toke"
        "ns_details', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), d"
        "efault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, che"
        "ck_type=None), InitPlan.Field(name='prompt_tokens_details', annotation=OpRef(name='init.fields.4.annotation'),"
        " default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, override=False, field_type=Fiel"
        "dType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_param"
        "s=('completion_tokens', 'prompt_tokens', 'total_tokens', 'completion_tokens_details', 'prompt_tokens_details')"
        ", frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Fi"
        "eld(name='completion_tokens', kw_only=True, fn=None), ReprPlan.Field(name='prompt_tokens', kw_only=True, fn=No"
        "ne), ReprPlan.Field(name='total_tokens', kw_only=True, fn=None), ReprPlan.Field(name='completion_tokens_detail"
        "s', kw_only=True, fn=None), ReprPlan.Field(name='prompt_tokens_details', kw_only=True, fn=None)), id=False, te"
        "rse=False, default_fn=None)))"
    ),
    plan_repr_sha1='defe4c6ebb95ab53b9b74a4c2ebfec018c761bd5',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__4__default',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.completionusage', 'CompletionUsage'),
    ),
)
def _process_dataclass__defe4c6ebb95ab53b9b74a4c2ebfec018c761bd5():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
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
                completion_tokens=self.completion_tokens,
                prompt_tokens=self.prompt_tokens,
                total_tokens=self.total_tokens,
                completion_tokens_details=self.completion_tokens_details,
                prompt_tokens_details=self.prompt_tokens_details,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.completion_tokens == other.completion_tokens and
                self.prompt_tokens == other.prompt_tokens and
                self.total_tokens == other.total_tokens and
                self.completion_tokens_details == other.completion_tokens_details and
                self.prompt_tokens_details == other.prompt_tokens_details
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'completion_tokens',
            'prompt_tokens',
            'total_tokens',
            'completion_tokens_details',
            'prompt_tokens_details',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'completion_tokens',
            'prompt_tokens',
            'total_tokens',
            'completion_tokens_details',
            'prompt_tokens_details',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.completion_tokens,
                self.prompt_tokens,
                self.total_tokens,
                self.completion_tokens_details,
                self.prompt_tokens_details,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            completion_tokens: __dataclass__init__fields__0__annotation,
            prompt_tokens: __dataclass__init__fields__1__annotation,
            total_tokens: __dataclass__init__fields__2__annotation,
            completion_tokens_details: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            prompt_tokens_details: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'completion_tokens', completion_tokens)
            __dataclass__object_setattr(self, 'prompt_tokens', prompt_tokens)
            __dataclass__object_setattr(self, 'total_tokens', total_tokens)
            __dataclass__object_setattr(self, 'completion_tokens_details', completion_tokens_details)
            __dataclass__object_setattr(self, 'prompt_tokens_details', prompt_tokens_details)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"completion_tokens={self.completion_tokens!r}")
            parts.append(f"prompt_tokens={self.prompt_tokens!r}")
            parts.append(f"total_tokens={self.total_tokens!r}")
            parts.append(f"completion_tokens_details={self.completion_tokens_details!r}")
            parts.append(f"prompt_tokens_details={self.prompt_tokens_details!r}")
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
        "Plans(tup=(CopyPlan(fields=('accepted_prediction_tokens', 'audio_tokens', 'reasoning_tokens', 'rejected_predic"
        "tion_tokens')), EqPlan(fields=('accepted_prediction_tokens', 'audio_tokens', 'reasoning_tokens', 'rejected_pre"
        "diction_tokens')), FrozenPlan(fields=('accepted_prediction_tokens', 'audio_tokens', 'reasoning_tokens', 'rejec"
        "ted_prediction_tokens'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('accepted_predictio"
        "n_tokens', 'audio_tokens', 'reasoning_tokens', 'rejected_prediction_tokens'), cache=False), InitPlan(fields=(I"
        "nitPlan.Field(name='accepted_prediction_tokens', annotation=OpRef(name='init.fields.0.annotation'), default=Op"
        "Ref(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTA"
        "NCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='audio_tokens', annotation=OpRef(name='"
        "init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, over"
        "ride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='"
        "reasoning_tokens', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.defaul"
        "t'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=Non"
        "e, check_type=None), InitPlan.Field(name='rejected_prediction_tokens', annotation=OpRef(name='init.fields.3.an"
        "notation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, fiel"
        "d_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw"
        "_only_params=('accepted_prediction_tokens', 'audio_tokens', 'reasoning_tokens', 'rejected_prediction_tokens'),"
        " frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Fie"
        "ld(name='accepted_prediction_tokens', kw_only=True, fn=None), ReprPlan.Field(name='audio_tokens', kw_only=True"
        ", fn=None), ReprPlan.Field(name='reasoning_tokens', kw_only=True, fn=None), ReprPlan.Field(name='rejected_pred"
        "iction_tokens', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='c969bdd7d26912a21d9f9e305de5d8853c89c70e',
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
        ('ommlds.backends.openai.protocol.completionusage', 'CompletionUsage.CompletionTokensDetails'),
    ),
)
def _process_dataclass__c969bdd7d26912a21d9f9e305de5d8853c89c70e():
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
                accepted_prediction_tokens=self.accepted_prediction_tokens,
                audio_tokens=self.audio_tokens,
                reasoning_tokens=self.reasoning_tokens,
                rejected_prediction_tokens=self.rejected_prediction_tokens,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.accepted_prediction_tokens == other.accepted_prediction_tokens and
                self.audio_tokens == other.audio_tokens and
                self.reasoning_tokens == other.reasoning_tokens and
                self.rejected_prediction_tokens == other.rejected_prediction_tokens
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'accepted_prediction_tokens',
            'audio_tokens',
            'reasoning_tokens',
            'rejected_prediction_tokens',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'accepted_prediction_tokens',
            'audio_tokens',
            'reasoning_tokens',
            'rejected_prediction_tokens',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.accepted_prediction_tokens,
                self.audio_tokens,
                self.reasoning_tokens,
                self.rejected_prediction_tokens,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            accepted_prediction_tokens: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            audio_tokens: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            reasoning_tokens: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            rejected_prediction_tokens: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'accepted_prediction_tokens', accepted_prediction_tokens)
            __dataclass__object_setattr(self, 'audio_tokens', audio_tokens)
            __dataclass__object_setattr(self, 'reasoning_tokens', reasoning_tokens)
            __dataclass__object_setattr(self, 'rejected_prediction_tokens', rejected_prediction_tokens)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"accepted_prediction_tokens={self.accepted_prediction_tokens!r}")
            parts.append(f"audio_tokens={self.audio_tokens!r}")
            parts.append(f"reasoning_tokens={self.reasoning_tokens!r}")
            parts.append(f"rejected_prediction_tokens={self.rejected_prediction_tokens!r}")
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
        "Plans(tup=(CopyPlan(fields=('audio_tokens', 'cached_tokens')), EqPlan(fields=('audio_tokens', 'cached_tokens')"
        "), FrozenPlan(fields=('audio_tokens', 'cached_tokens'), allow_dynamic_dunder_attrs=False), HashPlan(action='ad"
        "d', fields=('audio_tokens', 'cached_tokens'), cache=False), InitPlan(fields=(InitPlan.Field(name='audio_tokens"
        "', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'), default_fac"
        "tory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=No"
        "ne), InitPlan.Field(name='cached_tokens', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(nam"
        "e='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, co"
        "erce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('audio_tokens',"
        " 'cached_tokens'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fi"
        "elds=(ReprPlan.Field(name='audio_tokens', kw_only=True, fn=None), ReprPlan.Field(name='cached_tokens', kw_only"
        "=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='744b3ed5c7058f444d11e07c7f9028f5dd7ff59b',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.completionusage', 'CompletionUsage.PromptTokensDetails'),
    ),
)
def _process_dataclass__744b3ed5c7058f444d11e07c7f9028f5dd7ff59b():
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
                audio_tokens=self.audio_tokens,
                cached_tokens=self.cached_tokens,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.audio_tokens == other.audio_tokens and
                self.cached_tokens == other.cached_tokens
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'audio_tokens',
            'cached_tokens',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'audio_tokens',
            'cached_tokens',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.audio_tokens,
                self.cached_tokens,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            audio_tokens: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            cached_tokens: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'audio_tokens', audio_tokens)
            __dataclass__object_setattr(self, 'cached_tokens', cached_tokens)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"audio_tokens={self.audio_tokens!r}")
            parts.append(f"cached_tokens={self.cached_tokens!r}")
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
        "Plans(tup=(CopyPlan(fields=('item_id', 'output_index', 'content_index', 'part', 'sequence_number')), EqPlan(fi"
        "elds=('item_id', 'output_index', 'content_index', 'part', 'sequence_number')), FrozenPlan(fields=('item_id', '"
        "output_index', 'content_index', 'part', 'sequence_number'), allow_dynamic_dunder_attrs=False), HashPlan(action"
        "='add', fields=('item_id', 'output_index', 'content_index', 'part', 'sequence_number'), cache=False), InitPlan"
        "(fields=(InitPlan.Field(name='item_id', annotation=OpRef(name='init.fields.0.annotation'), default=None, defau"
        "lt_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_t"
        "ype=None), InitPlan.Field(name='output_index', annotation=OpRef(name='init.fields.1.annotation'), default=None"
        ", default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, "
        "check_type=None), InitPlan.Field(name='content_index', annotation=OpRef(name='init.fields.2.annotation'), defa"
        "ult=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validat"
        "e=None, check_type=None), InitPlan.Field(name='part', annotation=OpRef(name='init.fields.3.annotation'), defau"
        "lt=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate"
        "=None, check_type=None), InitPlan.Field(name='sequence_number', annotation=OpRef(name='init.fields.4.annotatio"
        "n'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, override=False, field_type="
        "FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_p"
        "arams=('item_id', 'output_index', 'content_index', 'part', 'sequence_number'), frozen=True, slots=False, post_"
        "init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='item_id', kw_only=True,"
        " fn=None), ReprPlan.Field(name='output_index', kw_only=True, fn=None), ReprPlan.Field(name='content_index', kw"
        "_only=True, fn=None), ReprPlan.Field(name='part', kw_only=True, fn=None), ReprPlan.Field(name='sequence_number"
        "', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='41d3dc8d391856d839ba3888447032f23a46c8e1',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__4__default',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.responses.events', 'ResponsesSseEvents.ContentPartEvent'),
    ),
)
def _process_dataclass__41d3dc8d391856d839ba3888447032f23a46c8e1():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__3__annotation,
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
                item_id=self.item_id,
                output_index=self.output_index,
                content_index=self.content_index,
                part=self.part,
                sequence_number=self.sequence_number,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.item_id == other.item_id and
                self.output_index == other.output_index and
                self.content_index == other.content_index and
                self.part == other.part and
                self.sequence_number == other.sequence_number
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'item_id',
            'output_index',
            'content_index',
            'part',
            'sequence_number',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'item_id',
            'output_index',
            'content_index',
            'part',
            'sequence_number',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.item_id,
                self.output_index,
                self.content_index,
                self.part,
                self.sequence_number,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            item_id: __dataclass__init__fields__0__annotation,
            output_index: __dataclass__init__fields__1__annotation,
            content_index: __dataclass__init__fields__2__annotation,
            part: __dataclass__init__fields__3__annotation,
            sequence_number: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'item_id', item_id)
            __dataclass__object_setattr(self, 'output_index', output_index)
            __dataclass__object_setattr(self, 'content_index', content_index)
            __dataclass__object_setattr(self, 'part', part)
            __dataclass__object_setattr(self, 'sequence_number', sequence_number)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"item_id={self.item_id!r}")
            parts.append(f"output_index={self.output_index!r}")
            parts.append(f"content_index={self.content_index!r}")
            parts.append(f"part={self.part!r}")
            parts.append(f"sequence_number={self.sequence_number!r}")
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
        "Plans(tup=(CopyPlan(fields=('message', 'code', 'param', 'sequence_number')), EqPlan(fields=('message', 'code',"
        " 'param', 'sequence_number')), FrozenPlan(fields=('message', 'code', 'param', 'sequence_number'), allow_dynami"
        "c_dunder_attrs=False), HashPlan(action='add', fields=('message', 'code', 'param', 'sequence_number'), cache=Fa"
        "lse), InitPlan(fields=(InitPlan.Field(name='message', annotation=OpRef(name='init.fields.0.annotation'), defau"
        "lt=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate"
        "=None, check_type=None), InitPlan.Field(name='code', annotation=OpRef(name='init.fields.1.annotation'), defaul"
        "t=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.I"
        "NSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='param', annotation=OpRef(name='ini"
        "t.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, overrid"
        "e=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='seq"
        "uence_number', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'),"
        " default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, c"
        "heck_type=None)), self_param='self', std_params=(), kw_only_params=('message', 'code', 'param', 'sequence_numb"
        "er'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPla"
        "n.Field(name='message', kw_only=True, fn=None), ReprPlan.Field(name='code', kw_only=True, fn=None), ReprPlan.F"
        "ield(name='param', kw_only=True, fn=None), ReprPlan.Field(name='sequence_number', kw_only=True, fn=None)), id="
        "False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='aeb2942e91d837c6674e2d04872576d047515e4e',
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
        ('ommlds.backends.openai.protocol.responses.events', 'ResponsesSseEvents.Error'),
    ),
)
def _process_dataclass__aeb2942e91d837c6674e2d04872576d047515e4e():
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
                message=self.message,
                code=self.code,
                param=self.param,
                sequence_number=self.sequence_number,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.message == other.message and
                self.code == other.code and
                self.param == other.param and
                self.sequence_number == other.sequence_number
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'message',
            'code',
            'param',
            'sequence_number',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'message',
            'code',
            'param',
            'sequence_number',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.message,
                self.code,
                self.param,
                self.sequence_number,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            message: __dataclass__init__fields__0__annotation,
            code: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            param: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            sequence_number: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'message', message)
            __dataclass__object_setattr(self, 'code', code)
            __dataclass__object_setattr(self, 'param', param)
            __dataclass__object_setattr(self, 'sequence_number', sequence_number)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"message={self.message!r}")
            parts.append(f"code={self.code!r}")
            parts.append(f"param={self.param!r}")
            parts.append(f"sequence_number={self.sequence_number!r}")
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
        "Plans(tup=(CopyPlan(fields=('item_id', 'output_index', 'delta', 'obfuscation', 'sequence_number')), EqPlan(fie"
        "lds=('item_id', 'output_index', 'delta', 'obfuscation', 'sequence_number')), FrozenPlan(fields=('item_id', 'ou"
        "tput_index', 'delta', 'obfuscation', 'sequence_number'), allow_dynamic_dunder_attrs=False), HashPlan(action='a"
        "dd', fields=('item_id', 'output_index', 'delta', 'obfuscation', 'sequence_number'), cache=False), InitPlan(fie"
        "lds=(InitPlan.Field(name='item_id', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_f"
        "actory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type="
        "None), InitPlan.Field(name='output_index', annotation=OpRef(name='init.fields.1.annotation'), default=None, de"
        "fault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, chec"
        "k_type=None), InitPlan.Field(name='delta', annotation=OpRef(name='init.fields.2.annotation'), default=None, de"
        "fault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, chec"
        "k_type=None), InitPlan.Field(name='obfuscation', annotation=OpRef(name='init.fields.3.annotation'), default=Op"
        "Ref(name='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTA"
        "NCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='sequence_number', annotation=OpRef(nam"
        "e='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, o"
        "verride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self'"
        ", std_params=(), kw_only_params=('item_id', 'output_index', 'delta', 'obfuscation', 'sequence_number'), frozen"
        "=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name"
        "='item_id', kw_only=True, fn=None), ReprPlan.Field(name='output_index', kw_only=True, fn=None), ReprPlan.Field"
        "(name='delta', kw_only=True, fn=None), ReprPlan.Field(name='obfuscation', kw_only=True, fn=None), ReprPlan.Fie"
        "ld(name='sequence_number', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='b068f9642c578a32eb62c1e6a8277357ca9b8dba',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__4__default',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.responses.events', 'ResponsesSseEvents.FunctionCallArgumentsDelta'),
    ),
)
def _process_dataclass__b068f9642c578a32eb62c1e6a8277357ca9b8dba():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
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
                item_id=self.item_id,
                output_index=self.output_index,
                delta=self.delta,
                obfuscation=self.obfuscation,
                sequence_number=self.sequence_number,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.item_id == other.item_id and
                self.output_index == other.output_index and
                self.delta == other.delta and
                self.obfuscation == other.obfuscation and
                self.sequence_number == other.sequence_number
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'item_id',
            'output_index',
            'delta',
            'obfuscation',
            'sequence_number',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'item_id',
            'output_index',
            'delta',
            'obfuscation',
            'sequence_number',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.item_id,
                self.output_index,
                self.delta,
                self.obfuscation,
                self.sequence_number,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            item_id: __dataclass__init__fields__0__annotation,
            output_index: __dataclass__init__fields__1__annotation,
            delta: __dataclass__init__fields__2__annotation,
            obfuscation: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            sequence_number: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'item_id', item_id)
            __dataclass__object_setattr(self, 'output_index', output_index)
            __dataclass__object_setattr(self, 'delta', delta)
            __dataclass__object_setattr(self, 'obfuscation', obfuscation)
            __dataclass__object_setattr(self, 'sequence_number', sequence_number)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"item_id={self.item_id!r}")
            parts.append(f"output_index={self.output_index!r}")
            parts.append(f"delta={self.delta!r}")
            parts.append(f"obfuscation={self.obfuscation!r}")
            parts.append(f"sequence_number={self.sequence_number!r}")
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
        "Plans(tup=(CopyPlan(fields=('item_id', 'output_index', 'arguments', 'name', 'sequence_number')), EqPlan(fields"
        "=('item_id', 'output_index', 'arguments', 'name', 'sequence_number')), FrozenPlan(fields=('item_id', 'output_i"
        "ndex', 'arguments', 'name', 'sequence_number'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fiel"
        "ds=('item_id', 'output_index', 'arguments', 'name', 'sequence_number'), cache=False), InitPlan(fields=(InitPla"
        "n.Field(name='item_id', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None,"
        " init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitP"
        "lan.Field(name='output_index', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factor"
        "y=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)"
        ", InitPlan.Field(name='arguments', annotation=OpRef(name='init.fields.2.annotation'), default=None, default_fa"
        "ctory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=N"
        "one), InitPlan.Field(name='name', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init."
        "fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=Non"
        "e, validate=None, check_type=None), InitPlan.Field(name='sequence_number', annotation=OpRef(name='init.fields."
        "4.annotation'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, override=False, "
        "field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=()"
        ", kw_only_params=('item_id', 'output_index', 'arguments', 'name', 'sequence_number'), frozen=True, slots=False"
        ", post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='item_id', kw_onl"
        "y=True, fn=None), ReprPlan.Field(name='output_index', kw_only=True, fn=None), ReprPlan.Field(name='arguments',"
        " kw_only=True, fn=None), ReprPlan.Field(name='name', kw_only=True, fn=None), ReprPlan.Field(name='sequence_num"
        "ber', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='737a291dfa894b9d500230288a33db7c0e01b501',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__4__default',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.responses.events', 'ResponsesSseEvents.FunctionCallArgumentsDone'),
    ),
)
def _process_dataclass__737a291dfa894b9d500230288a33db7c0e01b501():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
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
                item_id=self.item_id,
                output_index=self.output_index,
                arguments=self.arguments,
                name=self.name,
                sequence_number=self.sequence_number,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.item_id == other.item_id and
                self.output_index == other.output_index and
                self.arguments == other.arguments and
                self.name == other.name and
                self.sequence_number == other.sequence_number
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'item_id',
            'output_index',
            'arguments',
            'name',
            'sequence_number',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'item_id',
            'output_index',
            'arguments',
            'name',
            'sequence_number',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.item_id,
                self.output_index,
                self.arguments,
                self.name,
                self.sequence_number,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            item_id: __dataclass__init__fields__0__annotation,
            output_index: __dataclass__init__fields__1__annotation,
            arguments: __dataclass__init__fields__2__annotation,
            name: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            sequence_number: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'item_id', item_id)
            __dataclass__object_setattr(self, 'output_index', output_index)
            __dataclass__object_setattr(self, 'arguments', arguments)
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'sequence_number', sequence_number)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"item_id={self.item_id!r}")
            parts.append(f"output_index={self.output_index!r}")
            parts.append(f"arguments={self.arguments!r}")
            parts.append(f"name={self.name!r}")
            parts.append(f"sequence_number={self.sequence_number!r}")
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
        "Plans(tup=(CopyPlan(fields=('output_index', 'item', 'sequence_number')), EqPlan(fields=('output_index', 'item'"
        ", 'sequence_number')), FrozenPlan(fields=('output_index', 'item', 'sequence_number'), allow_dynamic_dunder_att"
        "rs=False), HashPlan(action='add', fields=('output_index', 'item', 'sequence_number'), cache=False), InitPlan(f"
        "ields=(InitPlan.Field(name='output_index', annotation=OpRef(name='init.fields.0.annotation'), default=None, de"
        "fault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, chec"
        "k_type=None), InitPlan.Field(name='item', annotation=OpRef(name='init.fields.1.annotation'), default=None, def"
        "ault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check"
        "_type=None), InitPlan.Field(name='sequence_number', annotation=OpRef(name='init.fields.2.annotation'), default"
        "=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.IN"
        "STANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('outp"
        "ut_index', 'item', 'sequence_number'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_"
        "fns=()), ReprPlan(fields=(ReprPlan.Field(name='output_index', kw_only=True, fn=None), ReprPlan.Field(name='ite"
        "m', kw_only=True, fn=None), ReprPlan.Field(name='sequence_number', kw_only=True, fn=None)), id=False, terse=Fa"
        "lse, default_fn=None)))"
    ),
    plan_repr_sha1='04ee48c20bf1bfa63514129843fe9b5ab33f1406',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.responses.events', 'ResponsesSseEvents.OutputItemEvent'),
    ),
)
def _process_dataclass__04ee48c20bf1bfa63514129843fe9b5ab33f1406():
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
                output_index=self.output_index,
                item=self.item,
                sequence_number=self.sequence_number,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.output_index == other.output_index and
                self.item == other.item and
                self.sequence_number == other.sequence_number
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'output_index',
            'item',
            'sequence_number',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'output_index',
            'item',
            'sequence_number',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.output_index,
                self.item,
                self.sequence_number,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            output_index: __dataclass__init__fields__0__annotation,
            item: __dataclass__init__fields__1__annotation,
            sequence_number: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'output_index', output_index)
            __dataclass__object_setattr(self, 'item', item)
            __dataclass__object_setattr(self, 'sequence_number', sequence_number)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"output_index={self.output_index!r}")
            parts.append(f"item={self.item!r}")
            parts.append(f"sequence_number={self.sequence_number!r}")
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
        "Plans(tup=(CopyPlan(fields=('item_id', 'output_index', 'content_index', 'delta', 'logprobs', 'obfuscation', 's"
        "equence_number')), EqPlan(fields=('item_id', 'output_index', 'content_index', 'delta', 'logprobs', 'obfuscatio"
        "n', 'sequence_number')), FrozenPlan(fields=('item_id', 'output_index', 'content_index', 'delta', 'logprobs', '"
        "obfuscation', 'sequence_number'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('item_id',"
        " 'output_index', 'content_index', 'delta', 'logprobs', 'obfuscation', 'sequence_number'), cache=False), InitPl"
        "an(fields=(InitPlan.Field(name='item_id', annotation=OpRef(name='init.fields.0.annotation'), default=None, def"
        "ault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check"
        "_type=None), InitPlan.Field(name='output_index', annotation=OpRef(name='init.fields.1.annotation'), default=No"
        "ne, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None"
        ", check_type=None), InitPlan.Field(name='content_index', annotation=OpRef(name='init.fields.2.annotation'), de"
        "fault=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valid"
        "ate=None, check_type=None), InitPlan.Field(name='delta', annotation=OpRef(name='init.fields.3.annotation'), de"
        "fault=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valid"
        "ate=None, check_type=None), InitPlan.Field(name='logprobs', annotation=OpRef(name='init.fields.4.annotation'),"
        " default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, override=False, field_type=Fiel"
        "dType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='obfuscation', annotation=Op"
        "Ref(name='init.fields.5.annotation'), default=OpRef(name='init.fields.5.default'), default_factory=None, init="
        "True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fi"
        "eld(name='sequence_number', annotation=OpRef(name='init.fields.6.annotation'), default=OpRef(name='init.fields"
        ".6.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, val"
        "idate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('item_id', 'output_index', 'c"
        "ontent_index', 'delta', 'logprobs', 'obfuscation', 'sequence_number'), frozen=True, slots=False, post_init_par"
        "ams=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='item_id', kw_only=True, fn=None"
        "), ReprPlan.Field(name='output_index', kw_only=True, fn=None), ReprPlan.Field(name='content_index', kw_only=Tr"
        "ue, fn=None), ReprPlan.Field(name='delta', kw_only=True, fn=None), ReprPlan.Field(name='logprobs', kw_only=Tru"
        "e, fn=None), ReprPlan.Field(name='obfuscation', kw_only=True, fn=None), ReprPlan.Field(name='sequence_number',"
        " kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='a8c8bb354c63beb0f99e7f9cb143c84476d1febf',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__4__default',
        '__dataclass__init__fields__5__annotation',
        '__dataclass__init__fields__5__default',
        '__dataclass__init__fields__6__annotation',
        '__dataclass__init__fields__6__default',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.responses.events', 'ResponsesSseEvents.OutputTextDelta'),
    ),
)
def _process_dataclass__a8c8bb354c63beb0f99e7f9cb143c84476d1febf():
    def _process_dataclass(
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
                item_id=self.item_id,
                output_index=self.output_index,
                content_index=self.content_index,
                delta=self.delta,
                logprobs=self.logprobs,
                obfuscation=self.obfuscation,
                sequence_number=self.sequence_number,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.item_id == other.item_id and
                self.output_index == other.output_index and
                self.content_index == other.content_index and
                self.delta == other.delta and
                self.logprobs == other.logprobs and
                self.obfuscation == other.obfuscation and
                self.sequence_number == other.sequence_number
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'item_id',
            'output_index',
            'content_index',
            'delta',
            'logprobs',
            'obfuscation',
            'sequence_number',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'item_id',
            'output_index',
            'content_index',
            'delta',
            'logprobs',
            'obfuscation',
            'sequence_number',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.item_id,
                self.output_index,
                self.content_index,
                self.delta,
                self.logprobs,
                self.obfuscation,
                self.sequence_number,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            item_id: __dataclass__init__fields__0__annotation,
            output_index: __dataclass__init__fields__1__annotation,
            content_index: __dataclass__init__fields__2__annotation,
            delta: __dataclass__init__fields__3__annotation,
            logprobs: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            obfuscation: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
            sequence_number: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'item_id', item_id)
            __dataclass__object_setattr(self, 'output_index', output_index)
            __dataclass__object_setattr(self, 'content_index', content_index)
            __dataclass__object_setattr(self, 'delta', delta)
            __dataclass__object_setattr(self, 'logprobs', logprobs)
            __dataclass__object_setattr(self, 'obfuscation', obfuscation)
            __dataclass__object_setattr(self, 'sequence_number', sequence_number)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"item_id={self.item_id!r}")
            parts.append(f"output_index={self.output_index!r}")
            parts.append(f"content_index={self.content_index!r}")
            parts.append(f"delta={self.delta!r}")
            parts.append(f"logprobs={self.logprobs!r}")
            parts.append(f"obfuscation={self.obfuscation!r}")
            parts.append(f"sequence_number={self.sequence_number!r}")
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
        "Plans(tup=(CopyPlan(fields=('item_id', 'output_index', 'content_index', 'text', 'logprobs', 'sequence_number')"
        "), EqPlan(fields=('item_id', 'output_index', 'content_index', 'text', 'logprobs', 'sequence_number')), FrozenP"
        "lan(fields=('item_id', 'output_index', 'content_index', 'text', 'logprobs', 'sequence_number'), allow_dynamic_"
        "dunder_attrs=False), HashPlan(action='add', fields=('item_id', 'output_index', 'content_index', 'text', 'logpr"
        "obs', 'sequence_number'), cache=False), InitPlan(fields=(InitPlan.Field(name='item_id', annotation=OpRef(name="
        "'init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldTy"
        "pe.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='output_index', annotation=OpRe"
        "f(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type="
        "FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='content_index', annotat"
        "ion=OpRef(name='init.fields.2.annotation'), default=None, default_factory=None, init=True, override=False, fie"
        "ld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='text', annotati"
        "on=OpRef(name='init.fields.3.annotation'), default=None, default_factory=None, init=True, override=False, fiel"
        "d_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='logprobs', annot"
        "ation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_factory=Non"
        "e, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), Ini"
        "tPlan.Field(name='sequence_number', annotation=OpRef(name='init.fields.5.annotation'), default=OpRef(name='ini"
        "t.fields.5.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=N"
        "one, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('item_id', 'output_in"
        "dex', 'content_index', 'text', 'logprobs', 'sequence_number'), frozen=True, slots=False, post_init_params=None"
        ", init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='item_id', kw_only=True, fn=None), ReprP"
        "lan.Field(name='output_index', kw_only=True, fn=None), ReprPlan.Field(name='content_index', kw_only=True, fn=N"
        "one), ReprPlan.Field(name='text', kw_only=True, fn=None), ReprPlan.Field(name='logprobs', kw_only=True, fn=Non"
        "e), ReprPlan.Field(name='sequence_number', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='c6cf2680659508c3c6cbc06abd71d56dd98b63e1',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__4__default',
        '__dataclass__init__fields__5__annotation',
        '__dataclass__init__fields__5__default',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.responses.events', 'ResponsesSseEvents.OutputTextDone'),
    ),
)
def _process_dataclass__c6cf2680659508c3c6cbc06abd71d56dd98b63e1():
    def _process_dataclass(
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
                item_id=self.item_id,
                output_index=self.output_index,
                content_index=self.content_index,
                text=self.text,
                logprobs=self.logprobs,
                sequence_number=self.sequence_number,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.item_id == other.item_id and
                self.output_index == other.output_index and
                self.content_index == other.content_index and
                self.text == other.text and
                self.logprobs == other.logprobs and
                self.sequence_number == other.sequence_number
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'item_id',
            'output_index',
            'content_index',
            'text',
            'logprobs',
            'sequence_number',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'item_id',
            'output_index',
            'content_index',
            'text',
            'logprobs',
            'sequence_number',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.item_id,
                self.output_index,
                self.content_index,
                self.text,
                self.logprobs,
                self.sequence_number,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            item_id: __dataclass__init__fields__0__annotation,
            output_index: __dataclass__init__fields__1__annotation,
            content_index: __dataclass__init__fields__2__annotation,
            text: __dataclass__init__fields__3__annotation,
            logprobs: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            sequence_number: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'item_id', item_id)
            __dataclass__object_setattr(self, 'output_index', output_index)
            __dataclass__object_setattr(self, 'content_index', content_index)
            __dataclass__object_setattr(self, 'text', text)
            __dataclass__object_setattr(self, 'logprobs', logprobs)
            __dataclass__object_setattr(self, 'sequence_number', sequence_number)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"item_id={self.item_id!r}")
            parts.append(f"output_index={self.output_index!r}")
            parts.append(f"content_index={self.content_index!r}")
            parts.append(f"text={self.text!r}")
            parts.append(f"logprobs={self.logprobs!r}")
            parts.append(f"sequence_number={self.sequence_number!r}")
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
        "Plans(tup=(CopyPlan(fields=('item_id', 'output_index', 'summary_index', 'part', 'sequence_number')), EqPlan(fi"
        "elds=('item_id', 'output_index', 'summary_index', 'part', 'sequence_number')), FrozenPlan(fields=('item_id', '"
        "output_index', 'summary_index', 'part', 'sequence_number'), allow_dynamic_dunder_attrs=False), HashPlan(action"
        "='add', fields=('item_id', 'output_index', 'summary_index', 'part', 'sequence_number'), cache=False), InitPlan"
        "(fields=(InitPlan.Field(name='item_id', annotation=OpRef(name='init.fields.0.annotation'), default=None, defau"
        "lt_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_t"
        "ype=None), InitPlan.Field(name='output_index', annotation=OpRef(name='init.fields.1.annotation'), default=None"
        ", default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, "
        "check_type=None), InitPlan.Field(name='summary_index', annotation=OpRef(name='init.fields.2.annotation'), defa"
        "ult=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validat"
        "e=None, check_type=None), InitPlan.Field(name='part', annotation=OpRef(name='init.fields.3.annotation'), defau"
        "lt=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate"
        "=None, check_type=None), InitPlan.Field(name='sequence_number', annotation=OpRef(name='init.fields.4.annotatio"
        "n'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, override=False, field_type="
        "FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_p"
        "arams=('item_id', 'output_index', 'summary_index', 'part', 'sequence_number'), frozen=True, slots=False, post_"
        "init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='item_id', kw_only=True,"
        " fn=None), ReprPlan.Field(name='output_index', kw_only=True, fn=None), ReprPlan.Field(name='summary_index', kw"
        "_only=True, fn=None), ReprPlan.Field(name='part', kw_only=True, fn=None), ReprPlan.Field(name='sequence_number"
        "', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='c1584ffcbb72484b98c9b2cdd14f4fb821547544',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__4__default',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.responses.events', 'ResponsesSseEvents.ReasoningSummaryPartEvent'),
    ),
)
def _process_dataclass__c1584ffcbb72484b98c9b2cdd14f4fb821547544():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__3__annotation,
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
                item_id=self.item_id,
                output_index=self.output_index,
                summary_index=self.summary_index,
                part=self.part,
                sequence_number=self.sequence_number,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.item_id == other.item_id and
                self.output_index == other.output_index and
                self.summary_index == other.summary_index and
                self.part == other.part and
                self.sequence_number == other.sequence_number
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'item_id',
            'output_index',
            'summary_index',
            'part',
            'sequence_number',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'item_id',
            'output_index',
            'summary_index',
            'part',
            'sequence_number',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.item_id,
                self.output_index,
                self.summary_index,
                self.part,
                self.sequence_number,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            item_id: __dataclass__init__fields__0__annotation,
            output_index: __dataclass__init__fields__1__annotation,
            summary_index: __dataclass__init__fields__2__annotation,
            part: __dataclass__init__fields__3__annotation,
            sequence_number: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'item_id', item_id)
            __dataclass__object_setattr(self, 'output_index', output_index)
            __dataclass__object_setattr(self, 'summary_index', summary_index)
            __dataclass__object_setattr(self, 'part', part)
            __dataclass__object_setattr(self, 'sequence_number', sequence_number)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"item_id={self.item_id!r}")
            parts.append(f"output_index={self.output_index!r}")
            parts.append(f"summary_index={self.summary_index!r}")
            parts.append(f"part={self.part!r}")
            parts.append(f"sequence_number={self.sequence_number!r}")
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
        "Plans(tup=(CopyPlan(fields=('item_id', 'output_index', 'summary_index', 'delta', 'obfuscation', 'sequence_numb"
        "er')), EqPlan(fields=('item_id', 'output_index', 'summary_index', 'delta', 'obfuscation', 'sequence_number')),"
        " FrozenPlan(fields=('item_id', 'output_index', 'summary_index', 'delta', 'obfuscation', 'sequence_number'), al"
        "low_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('item_id', 'output_index', 'summary_index', 'd"
        "elta', 'obfuscation', 'sequence_number'), cache=False), InitPlan(fields=(InitPlan.Field(name='item_id', annota"
        "tion=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, fi"
        "eld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='output_index',"
        " annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=Fa"
        "lse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='summary"
        "_index', annotation=OpRef(name='init.fields.2.annotation'), default=None, default_factory=None, init=True, ove"
        "rride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name="
        "'delta', annotation=OpRef(name='init.fields.3.annotation'), default=None, default_factory=None, init=True, ove"
        "rride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name="
        "'obfuscation', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'),"
        " default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, c"
        "heck_type=None), InitPlan.Field(name='sequence_number', annotation=OpRef(name='init.fields.5.annotation'), def"
        "ault=OpRef(name='init.fields.5.default'), default_factory=None, init=True, override=False, field_type=FieldTyp"
        "e.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('"
        "item_id', 'output_index', 'summary_index', 'delta', 'obfuscation', 'sequence_number'), frozen=True, slots=Fals"
        "e, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='item_id', kw_on"
        "ly=True, fn=None), ReprPlan.Field(name='output_index', kw_only=True, fn=None), ReprPlan.Field(name='summary_in"
        "dex', kw_only=True, fn=None), ReprPlan.Field(name='delta', kw_only=True, fn=None), ReprPlan.Field(name='obfusc"
        "ation', kw_only=True, fn=None), ReprPlan.Field(name='sequence_number', kw_only=True, fn=None)), id=False, ters"
        "e=False, default_fn=None)))"
    ),
    plan_repr_sha1='c89f110b1ce7623ecfd1656f7c0f7af460598313',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__4__default',
        '__dataclass__init__fields__5__annotation',
        '__dataclass__init__fields__5__default',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.responses.events', 'ResponsesSseEvents.ReasoningSummaryTextDelta'),
    ),
)
def _process_dataclass__c89f110b1ce7623ecfd1656f7c0f7af460598313():
    def _process_dataclass(
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
                item_id=self.item_id,
                output_index=self.output_index,
                summary_index=self.summary_index,
                delta=self.delta,
                obfuscation=self.obfuscation,
                sequence_number=self.sequence_number,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.item_id == other.item_id and
                self.output_index == other.output_index and
                self.summary_index == other.summary_index and
                self.delta == other.delta and
                self.obfuscation == other.obfuscation and
                self.sequence_number == other.sequence_number
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'item_id',
            'output_index',
            'summary_index',
            'delta',
            'obfuscation',
            'sequence_number',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'item_id',
            'output_index',
            'summary_index',
            'delta',
            'obfuscation',
            'sequence_number',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.item_id,
                self.output_index,
                self.summary_index,
                self.delta,
                self.obfuscation,
                self.sequence_number,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            item_id: __dataclass__init__fields__0__annotation,
            output_index: __dataclass__init__fields__1__annotation,
            summary_index: __dataclass__init__fields__2__annotation,
            delta: __dataclass__init__fields__3__annotation,
            obfuscation: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            sequence_number: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'item_id', item_id)
            __dataclass__object_setattr(self, 'output_index', output_index)
            __dataclass__object_setattr(self, 'summary_index', summary_index)
            __dataclass__object_setattr(self, 'delta', delta)
            __dataclass__object_setattr(self, 'obfuscation', obfuscation)
            __dataclass__object_setattr(self, 'sequence_number', sequence_number)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"item_id={self.item_id!r}")
            parts.append(f"output_index={self.output_index!r}")
            parts.append(f"summary_index={self.summary_index!r}")
            parts.append(f"delta={self.delta!r}")
            parts.append(f"obfuscation={self.obfuscation!r}")
            parts.append(f"sequence_number={self.sequence_number!r}")
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
        "Plans(tup=(CopyPlan(fields=('item_id', 'output_index', 'summary_index', 'text', 'sequence_number')), EqPlan(fi"
        "elds=('item_id', 'output_index', 'summary_index', 'text', 'sequence_number')), FrozenPlan(fields=('item_id', '"
        "output_index', 'summary_index', 'text', 'sequence_number'), allow_dynamic_dunder_attrs=False), HashPlan(action"
        "='add', fields=('item_id', 'output_index', 'summary_index', 'text', 'sequence_number'), cache=False), InitPlan"
        "(fields=(InitPlan.Field(name='item_id', annotation=OpRef(name='init.fields.0.annotation'), default=None, defau"
        "lt_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_t"
        "ype=None), InitPlan.Field(name='output_index', annotation=OpRef(name='init.fields.1.annotation'), default=None"
        ", default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, "
        "check_type=None), InitPlan.Field(name='summary_index', annotation=OpRef(name='init.fields.2.annotation'), defa"
        "ult=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validat"
        "e=None, check_type=None), InitPlan.Field(name='text', annotation=OpRef(name='init.fields.3.annotation'), defau"
        "lt=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate"
        "=None, check_type=None), InitPlan.Field(name='sequence_number', annotation=OpRef(name='init.fields.4.annotatio"
        "n'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, override=False, field_type="
        "FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_p"
        "arams=('item_id', 'output_index', 'summary_index', 'text', 'sequence_number'), frozen=True, slots=False, post_"
        "init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='item_id', kw_only=True,"
        " fn=None), ReprPlan.Field(name='output_index', kw_only=True, fn=None), ReprPlan.Field(name='summary_index', kw"
        "_only=True, fn=None), ReprPlan.Field(name='text', kw_only=True, fn=None), ReprPlan.Field(name='sequence_number"
        "', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='ffd0e5b88ac6d331d99c2ccc4e072fcc46b9c374',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__4__default',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.responses.events', 'ResponsesSseEvents.ReasoningSummaryTextDone'),
    ),
)
def _process_dataclass__ffd0e5b88ac6d331d99c2ccc4e072fcc46b9c374():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__3__annotation,
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
                item_id=self.item_id,
                output_index=self.output_index,
                summary_index=self.summary_index,
                text=self.text,
                sequence_number=self.sequence_number,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.item_id == other.item_id and
                self.output_index == other.output_index and
                self.summary_index == other.summary_index and
                self.text == other.text and
                self.sequence_number == other.sequence_number
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'item_id',
            'output_index',
            'summary_index',
            'text',
            'sequence_number',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'item_id',
            'output_index',
            'summary_index',
            'text',
            'sequence_number',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.item_id,
                self.output_index,
                self.summary_index,
                self.text,
                self.sequence_number,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            item_id: __dataclass__init__fields__0__annotation,
            output_index: __dataclass__init__fields__1__annotation,
            summary_index: __dataclass__init__fields__2__annotation,
            text: __dataclass__init__fields__3__annotation,
            sequence_number: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'item_id', item_id)
            __dataclass__object_setattr(self, 'output_index', output_index)
            __dataclass__object_setattr(self, 'summary_index', summary_index)
            __dataclass__object_setattr(self, 'text', text)
            __dataclass__object_setattr(self, 'sequence_number', sequence_number)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"item_id={self.item_id!r}")
            parts.append(f"output_index={self.output_index!r}")
            parts.append(f"summary_index={self.summary_index!r}")
            parts.append(f"text={self.text!r}")
            parts.append(f"sequence_number={self.sequence_number!r}")
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
        "Plans(tup=(CopyPlan(fields=('item_id', 'output_index', 'content_index', 'delta', 'obfuscation', 'sequence_numb"
        "er')), EqPlan(fields=('item_id', 'output_index', 'content_index', 'delta', 'obfuscation', 'sequence_number')),"
        " FrozenPlan(fields=('item_id', 'output_index', 'content_index', 'delta', 'obfuscation', 'sequence_number'), al"
        "low_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('item_id', 'output_index', 'content_index', 'd"
        "elta', 'obfuscation', 'sequence_number'), cache=False), InitPlan(fields=(InitPlan.Field(name='item_id', annota"
        "tion=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, fi"
        "eld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='output_index',"
        " annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=Fa"
        "lse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='content"
        "_index', annotation=OpRef(name='init.fields.2.annotation'), default=None, default_factory=None, init=True, ove"
        "rride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name="
        "'delta', annotation=OpRef(name='init.fields.3.annotation'), default=None, default_factory=None, init=True, ove"
        "rride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name="
        "'obfuscation', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'),"
        " default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, c"
        "heck_type=None), InitPlan.Field(name='sequence_number', annotation=OpRef(name='init.fields.5.annotation'), def"
        "ault=OpRef(name='init.fields.5.default'), default_factory=None, init=True, override=False, field_type=FieldTyp"
        "e.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('"
        "item_id', 'output_index', 'content_index', 'delta', 'obfuscation', 'sequence_number'), frozen=True, slots=Fals"
        "e, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='item_id', kw_on"
        "ly=True, fn=None), ReprPlan.Field(name='output_index', kw_only=True, fn=None), ReprPlan.Field(name='content_in"
        "dex', kw_only=True, fn=None), ReprPlan.Field(name='delta', kw_only=True, fn=None), ReprPlan.Field(name='obfusc"
        "ation', kw_only=True, fn=None), ReprPlan.Field(name='sequence_number', kw_only=True, fn=None)), id=False, ters"
        "e=False, default_fn=None)))"
    ),
    plan_repr_sha1='38ec2a07e5070d8257e127550ecc5b4b90c45218',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__4__default',
        '__dataclass__init__fields__5__annotation',
        '__dataclass__init__fields__5__default',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.responses.events', 'ResponsesSseEvents.ReasoningTextDelta'),
    ),
)
def _process_dataclass__38ec2a07e5070d8257e127550ecc5b4b90c45218():
    def _process_dataclass(
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
                item_id=self.item_id,
                output_index=self.output_index,
                content_index=self.content_index,
                delta=self.delta,
                obfuscation=self.obfuscation,
                sequence_number=self.sequence_number,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.item_id == other.item_id and
                self.output_index == other.output_index and
                self.content_index == other.content_index and
                self.delta == other.delta and
                self.obfuscation == other.obfuscation and
                self.sequence_number == other.sequence_number
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'item_id',
            'output_index',
            'content_index',
            'delta',
            'obfuscation',
            'sequence_number',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'item_id',
            'output_index',
            'content_index',
            'delta',
            'obfuscation',
            'sequence_number',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.item_id,
                self.output_index,
                self.content_index,
                self.delta,
                self.obfuscation,
                self.sequence_number,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            item_id: __dataclass__init__fields__0__annotation,
            output_index: __dataclass__init__fields__1__annotation,
            content_index: __dataclass__init__fields__2__annotation,
            delta: __dataclass__init__fields__3__annotation,
            obfuscation: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            sequence_number: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'item_id', item_id)
            __dataclass__object_setattr(self, 'output_index', output_index)
            __dataclass__object_setattr(self, 'content_index', content_index)
            __dataclass__object_setattr(self, 'delta', delta)
            __dataclass__object_setattr(self, 'obfuscation', obfuscation)
            __dataclass__object_setattr(self, 'sequence_number', sequence_number)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"item_id={self.item_id!r}")
            parts.append(f"output_index={self.output_index!r}")
            parts.append(f"content_index={self.content_index!r}")
            parts.append(f"delta={self.delta!r}")
            parts.append(f"obfuscation={self.obfuscation!r}")
            parts.append(f"sequence_number={self.sequence_number!r}")
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
        "Plans(tup=(CopyPlan(fields=('item_id', 'output_index', 'content_index', 'text', 'sequence_number')), EqPlan(fi"
        "elds=('item_id', 'output_index', 'content_index', 'text', 'sequence_number')), FrozenPlan(fields=('item_id', '"
        "output_index', 'content_index', 'text', 'sequence_number'), allow_dynamic_dunder_attrs=False), HashPlan(action"
        "='add', fields=('item_id', 'output_index', 'content_index', 'text', 'sequence_number'), cache=False), InitPlan"
        "(fields=(InitPlan.Field(name='item_id', annotation=OpRef(name='init.fields.0.annotation'), default=None, defau"
        "lt_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_t"
        "ype=None), InitPlan.Field(name='output_index', annotation=OpRef(name='init.fields.1.annotation'), default=None"
        ", default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, "
        "check_type=None), InitPlan.Field(name='content_index', annotation=OpRef(name='init.fields.2.annotation'), defa"
        "ult=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validat"
        "e=None, check_type=None), InitPlan.Field(name='text', annotation=OpRef(name='init.fields.3.annotation'), defau"
        "lt=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate"
        "=None, check_type=None), InitPlan.Field(name='sequence_number', annotation=OpRef(name='init.fields.4.annotatio"
        "n'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, override=False, field_type="
        "FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_p"
        "arams=('item_id', 'output_index', 'content_index', 'text', 'sequence_number'), frozen=True, slots=False, post_"
        "init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='item_id', kw_only=True,"
        " fn=None), ReprPlan.Field(name='output_index', kw_only=True, fn=None), ReprPlan.Field(name='content_index', kw"
        "_only=True, fn=None), ReprPlan.Field(name='text', kw_only=True, fn=None), ReprPlan.Field(name='sequence_number"
        "', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='d946387723573b42ce6ee3f9e381c66e2779bbdb',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__4__default',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.responses.events', 'ResponsesSseEvents.ReasoningTextDone'),
    ),
)
def _process_dataclass__d946387723573b42ce6ee3f9e381c66e2779bbdb():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__3__annotation,
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
                item_id=self.item_id,
                output_index=self.output_index,
                content_index=self.content_index,
                text=self.text,
                sequence_number=self.sequence_number,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.item_id == other.item_id and
                self.output_index == other.output_index and
                self.content_index == other.content_index and
                self.text == other.text and
                self.sequence_number == other.sequence_number
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'item_id',
            'output_index',
            'content_index',
            'text',
            'sequence_number',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'item_id',
            'output_index',
            'content_index',
            'text',
            'sequence_number',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.item_id,
                self.output_index,
                self.content_index,
                self.text,
                self.sequence_number,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            item_id: __dataclass__init__fields__0__annotation,
            output_index: __dataclass__init__fields__1__annotation,
            content_index: __dataclass__init__fields__2__annotation,
            text: __dataclass__init__fields__3__annotation,
            sequence_number: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'item_id', item_id)
            __dataclass__object_setattr(self, 'output_index', output_index)
            __dataclass__object_setattr(self, 'content_index', content_index)
            __dataclass__object_setattr(self, 'text', text)
            __dataclass__object_setattr(self, 'sequence_number', sequence_number)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"item_id={self.item_id!r}")
            parts.append(f"output_index={self.output_index!r}")
            parts.append(f"content_index={self.content_index!r}")
            parts.append(f"text={self.text!r}")
            parts.append(f"sequence_number={self.sequence_number!r}")
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
        "Plans(tup=(CopyPlan(fields=('response', 'sequence_number')), EqPlan(fields=('response', 'sequence_number')), F"
        "rozenPlan(fields=('response', 'sequence_number'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fi"
        "elds=('response', 'sequence_number'), cache=False), InitPlan(fields=(InitPlan.Field(name='response', annotatio"
        "n=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field"
        "_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='sequence_number',"
        " annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_facto"
        "ry=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None"
        ")), self_param='self', std_params=(), kw_only_params=('response', 'sequence_number'), frozen=True, slots=False"
        ", post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='response', kw_on"
        "ly=True, fn=None), ReprPlan.Field(name='sequence_number', kw_only=True, fn=None)), id=False, terse=False, defa"
        "ult_fn=None)))"
    ),
    plan_repr_sha1='2b74f9cea18bfaf5c9d52b33cc2c5592b24bb0ae',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.responses.events', 'ResponsesSseEvents.ResponseEvent'),
    ),
)
def _process_dataclass__2b74f9cea18bfaf5c9d52b33cc2c5592b24bb0ae():
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
                response=self.response,
                sequence_number=self.sequence_number,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.response == other.response and
                self.sequence_number == other.sequence_number
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'response',
            'sequence_number',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'response',
            'sequence_number',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.response,
                self.sequence_number,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            response: __dataclass__init__fields__0__annotation,
            sequence_number: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'response', response)
            __dataclass__object_setattr(self, 'sequence_number', sequence_number)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"response={self.response!r}")
            parts.append(f"sequence_number={self.sequence_number!r}")
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
        "Plans(tup=(CopyPlan(fields=('call_id', 'output', 'id', 'status')), EqPlan(fields=('call_id', 'output', 'id', '"
        "status')), FrozenPlan(fields=('call_id', 'output', 'id', 'status'), allow_dynamic_dunder_attrs=False), HashPla"
        "n(action='add', fields=('call_id', 'output', 'id', 'status'), cache=False), InitPlan(fields=(InitPlan.Field(na"
        "me='call_id', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True"
        ", override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field("
        "name='output', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=Tru"
        "e, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field"
        "(name='id', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), de"
        "fault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, chec"
        "k_type=None), InitPlan.Field(name='status', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(n"
        "ame='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, "
        "coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('call_id', 'o"
        "utput', 'id', 'status'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprP"
        "lan(fields=(ReprPlan.Field(name='call_id', kw_only=True, fn=None), ReprPlan.Field(name='output', kw_only=True,"
        " fn=None), ReprPlan.Field(name='id', kw_only=True, fn=None), ReprPlan.Field(name='status', kw_only=True, fn=No"
        "ne)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='14c7e9d6ecf3310f7daf772de8d9de2a7d82c402',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.responses.request', 'FunctionCallOutputResponsesInputItem'),
    ),
)
def _process_dataclass__14c7e9d6ecf3310f7daf772de8d9de2a7d82c402():
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
                call_id=self.call_id,
                output=self.output,
                id=self.id,
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
                self.call_id == other.call_id and
                self.output == other.output and
                self.id == other.id and
                self.status == other.status
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'call_id',
            'output',
            'id',
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
            'call_id',
            'output',
            'id',
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
                self.call_id,
                self.output,
                self.id,
                self.status,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            call_id: __dataclass__init__fields__0__annotation,
            output: __dataclass__init__fields__1__annotation,
            id: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            status: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'call_id', call_id)
            __dataclass__object_setattr(self, 'output', output)
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'status', status)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"call_id={self.call_id!r}")
            parts.append(f"output={self.output!r}")
            parts.append(f"id={self.id!r}")
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
        "Plans(tup=(CopyPlan(fields=('call_id', 'name', 'arguments', 'id', 'status')), EqPlan(fields=('call_id', 'name'"
        ", 'arguments', 'id', 'status')), FrozenPlan(fields=('call_id', 'name', 'arguments', 'id', 'status'), allow_dyn"
        "amic_dunder_attrs=False), HashPlan(action='add', fields=('call_id', 'name', 'arguments', 'id', 'status'), cach"
        "e=False), InitPlan(fields=(InitPlan.Field(name='call_id', annotation=OpRef(name='init.fields.0.annotation'), d"
        "efault=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, vali"
        "date=None, check_type=None), InitPlan.Field(name='name', annotation=OpRef(name='init.fields.1.annotation'), de"
        "fault=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valid"
        "ate=None, check_type=None), InitPlan.Field(name='arguments', annotation=OpRef(name='init.fields.2.annotation')"
        ", default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, v"
        "alidate=None, check_type=None), InitPlan.Field(name='id', annotation=OpRef(name='init.fields.3.annotation'), d"
        "efault=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldT"
        "ype.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='status', annotation=OpRef(nam"
        "e='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, o"
        "verride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self'"
        ", std_params=(), kw_only_params=('call_id', 'name', 'arguments', 'id', 'status'), frozen=True, slots=False, po"
        "st_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='call_id', kw_only=Tr"
        "ue, fn=None), ReprPlan.Field(name='name', kw_only=True, fn=None), ReprPlan.Field(name='arguments', kw_only=Tru"
        "e, fn=None), ReprPlan.Field(name='id', kw_only=True, fn=None), ReprPlan.Field(name='status', kw_only=True, fn="
        "None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='f6915274c784a3ae98bae3414bdcbae07632ca99',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__4__default',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.responses.request', 'FunctionCallResponsesInputItem'),
        ('ommlds.backends.openai.protocol.responses.response', 'FunctionCallResponsesOutputItem'),
    ),
)
def _process_dataclass__f6915274c784a3ae98bae3414bdcbae07632ca99():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
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
                call_id=self.call_id,
                name=self.name,
                arguments=self.arguments,
                id=self.id,
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
                self.call_id == other.call_id and
                self.name == other.name and
                self.arguments == other.arguments and
                self.id == other.id and
                self.status == other.status
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'call_id',
            'name',
            'arguments',
            'id',
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
            'call_id',
            'name',
            'arguments',
            'id',
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
                self.call_id,
                self.name,
                self.arguments,
                self.id,
                self.status,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            call_id: __dataclass__init__fields__0__annotation,
            name: __dataclass__init__fields__1__annotation,
            arguments: __dataclass__init__fields__2__annotation,
            id: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            status: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'call_id', call_id)
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'arguments', arguments)
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'status', status)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"call_id={self.call_id!r}")
            parts.append(f"name={self.name!r}")
            parts.append(f"arguments={self.arguments!r}")
            parts.append(f"id={self.id!r}")
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
        "Plans(tup=(CopyPlan(fields=('image_url', 'file_id', 'detail')), EqPlan(fields=('image_url', 'file_id', 'detail"
        "')), FrozenPlan(fields=('image_url', 'file_id', 'detail'), allow_dynamic_dunder_attrs=False), HashPlan(action="
        "'add', fields=('image_url', 'file_id', 'detail'), cache=False), InitPlan(fields=(InitPlan.Field(name='image_ur"
        "l', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'), default_fa"
        "ctory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=N"
        "one), InitPlan.Field(name='file_id', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='in"
        "it.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce="
        "None, validate=None, check_type=None), InitPlan.Field(name='detail', annotation=OpRef(name='init.fields.2.anno"
        "tation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_"
        "type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_o"
        "nly_params=('image_url', 'file_id', 'detail'), frozen=True, slots=False, post_init_params=None, init_fns=(), v"
        "alidate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='image_url', kw_only=True, fn=None), ReprPlan.Field(name"
        "='file_id', kw_only=True, fn=None), ReprPlan.Field(name='detail', kw_only=True, fn=None)), id=False, terse=Fal"
        "se, default_fn=None)))"
    ),
    plan_repr_sha1='82355dfeb05bc4fdf26ca137b444a50dab8248ce',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.responses.request', 'InputImageResponsesInputContentPart'),
    ),
)
def _process_dataclass__82355dfeb05bc4fdf26ca137b444a50dab8248ce():
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
                image_url=self.image_url,
                file_id=self.file_id,
                detail=self.detail,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.image_url == other.image_url and
                self.file_id == other.file_id and
                self.detail == other.detail
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'image_url',
            'file_id',
            'detail',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'image_url',
            'file_id',
            'detail',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.image_url,
                self.file_id,
                self.detail,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            image_url: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            file_id: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            detail: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'image_url', image_url)
            __dataclass__object_setattr(self, 'file_id', file_id)
            __dataclass__object_setattr(self, 'detail', detail)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"image_url={self.image_url!r}")
            parts.append(f"file_id={self.file_id!r}")
            parts.append(f"detail={self.detail!r}")
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
        "Plans(tup=(CopyPlan(fields=('text',)), EqPlan(fields=('text',)), FrozenPlan(fields=('text',), allow_dynamic_du"
        "nder_attrs=False), HashPlan(action='add', fields=('text',), cache=False), InitPlan(fields=(InitPlan.Field(name"
        "='text', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, ove"
        "rride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self',"
        " std_params=(), kw_only_params=('text',), frozen=True, slots=False, post_init_params=None, init_fns=(), valida"
        "te_fns=()), ReprPlan(fields=(ReprPlan.Field(name='text', kw_only=True, fn=None),), id=False, terse=False, defa"
        "ult_fn=None)))"
    ),
    plan_repr_sha1='981a3fd6730d2d619e2c7c14e7ef8cc88d193ce6',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.responses.request', 'InputTextResponsesInputContentPart'),
    ),
)
def _process_dataclass__981a3fd6730d2d619e2c7c14e7ef8cc88d193ce6():
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
                text=self.text,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.text == other.text
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'text',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'text',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.text,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            text: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'text', text)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"text={self.text!r}")
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
        "Plans(tup=(CopyPlan(fields=('role', 'content', 'id', 'status')), EqPlan(fields=('role', 'content', 'id', 'stat"
        "us')), FrozenPlan(fields=('role', 'content', 'id', 'status'), allow_dynamic_dunder_attrs=False), HashPlan(acti"
        "on='add', fields=('role', 'content', 'id', 'status'), cache=False), InitPlan(fields=(InitPlan.Field(name='role"
        "', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override="
        "False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='conte"
        "nt', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, overrid"
        "e=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='id'"
        ", annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_fact"
        "ory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=Non"
        "e), InitPlan.Field(name='status', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init."
        "fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=Non"
        "e, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('role', 'content', 'id'"
        ", 'status'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=("
        "ReprPlan.Field(name='role', kw_only=True, fn=None), ReprPlan.Field(name='content', kw_only=True, fn=None), Rep"
        "rPlan.Field(name='id', kw_only=True, fn=None), ReprPlan.Field(name='status', kw_only=True, fn=None)), id=False"
        ", terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='ca283e188088e4d68bde848f1419ebc9a1dd1211',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.responses.request', 'MessageResponsesInputItem'),
    ),
)
def _process_dataclass__ca283e188088e4d68bde848f1419ebc9a1dd1211():
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
                role=self.role,
                content=self.content,
                id=self.id,
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
                self.role == other.role and
                self.content == other.content and
                self.id == other.id and
                self.status == other.status
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'role',
            'content',
            'id',
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
            'role',
            'content',
            'id',
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
                self.role,
                self.content,
                self.id,
                self.status,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            role: __dataclass__init__fields__0__annotation,
            content: __dataclass__init__fields__1__annotation,
            id: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            status: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'role', role)
            __dataclass__object_setattr(self, 'content', content)
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'status', status)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"role={self.role!r}")
            parts.append(f"content={self.content!r}")
            parts.append(f"id={self.id!r}")
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
        "Plans(tup=(CopyPlan(fields=('text', 'annotations')), EqPlan(fields=('text', 'annotations')), FrozenPlan(fields"
        "=('text', 'annotations'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('text', 'annotatio"
        "ns'), cache=False), InitPlan(fields=(InitPlan.Field(name='text', annotation=OpRef(name='init.fields.0.annotati"
        "on'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=Non"
        "e, validate=None, check_type=None), InitPlan.Field(name='annotations', annotation=OpRef(name='init.fields.1.an"
        "notation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, fiel"
        "d_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw"
        "_only_params=('text', 'annotations'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_f"
        "ns=()), ReprPlan(fields=(ReprPlan.Field(name='text', kw_only=True, fn=None), ReprPlan.Field(name='annotations'"
        ", kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='3cd47c6974b3e434f016a6f9708e17dcc850340f',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.responses.request', 'OutputTextResponsesInputContentPart'),
    ),
)
def _process_dataclass__3cd47c6974b3e434f016a6f9708e17dcc850340f():
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
                text=self.text,
                annotations=self.annotations,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.text == other.text and
                self.annotations == other.annotations
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'text',
            'annotations',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'text',
            'annotations',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.text,
                self.annotations,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            text: __dataclass__init__fields__0__annotation,
            annotations: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'text', text)
            __dataclass__object_setattr(self, 'annotations', annotations)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"text={self.text!r}")
            parts.append(f"annotations={self.annotations!r}")
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
        "Plans(tup=(CopyPlan(fields=('summary', 'id', 'content', 'encrypted_content', 'status')), EqPlan(fields=('summa"
        "ry', 'id', 'content', 'encrypted_content', 'status')), FrozenPlan(fields=('summary', 'id', 'content', 'encrypt"
        "ed_content', 'status'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('summary', 'id', 'co"
        "ntent', 'encrypted_content', 'status'), cache=False), InitPlan(fields=(InitPlan.Field(name='summary', annotati"
        "on=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'), default_factory=None, "
        "init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPl"
        "an.Field(name='id', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.defau"
        "lt'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=No"
        "ne, check_type=None), InitPlan.Field(name='content', annotation=OpRef(name='init.fields.2.annotation'), defaul"
        "t=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.I"
        "NSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='encrypted_content', annotation=OpR"
        "ef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=T"
        "rue, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fie"
        "ld(name='status', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default"
        "'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None"
        ", check_type=None)), self_param='self', std_params=(), kw_only_params=('summary', 'id', 'content', 'encrypted_"
        "content', 'status'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan("
        "fields=(ReprPlan.Field(name='summary', kw_only=True, fn=None), ReprPlan.Field(name='id', kw_only=True, fn=None"
        "), ReprPlan.Field(name='content', kw_only=True, fn=None), ReprPlan.Field(name='encrypted_content', kw_only=Tru"
        "e, fn=None), ReprPlan.Field(name='status', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='432812d6dad4b8e6c76e14c1ad3e87bf9e18bbea',
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
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.responses.request', 'ReasoningResponsesInputItem'),
        ('ommlds.backends.openai.protocol.responses.response', 'ReasoningResponsesOutputItem'),
    ),
)
def _process_dataclass__432812d6dad4b8e6c76e14c1ad3e87bf9e18bbea():
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
                id=self.id,
                content=self.content,
                encrypted_content=self.encrypted_content,
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
                self.summary == other.summary and
                self.id == other.id and
                self.content == other.content and
                self.encrypted_content == other.encrypted_content and
                self.status == other.status
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'summary',
            'id',
            'content',
            'encrypted_content',
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
            'summary',
            'id',
            'content',
            'encrypted_content',
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
                self.summary,
                self.id,
                self.content,
                self.encrypted_content,
                self.status,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            summary: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            id: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            content: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            encrypted_content: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            status: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'summary', summary)
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'content', content)
            __dataclass__object_setattr(self, 'encrypted_content', encrypted_content)
            __dataclass__object_setattr(self, 'status', status)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"summary={self.summary!r}")
            parts.append(f"id={self.id!r}")
            parts.append(f"content={self.content!r}")
            parts.append(f"encrypted_content={self.encrypted_content!r}")
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
        "Plans(tup=(CopyPlan(fields=('text', 'type')), EqPlan(fields=('text', 'type')), FrozenPlan(fields=('text', 'typ"
        "e'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('text', 'type'), cache=False), InitPlan"
        "(fields=(InitPlan.Field(name='text', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_"
        "factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type"
        "=None), InitPlan.Field(name='type', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='ini"
        "t.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=N"
        "one, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('text', 'type'), froz"
        "en=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(na"
        "me='text', kw_only=True, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='953f32063cf89facee83c6681c46db52e4592f93',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.responses.request', 'ReasoningResponsesInputItem.SummaryText'),
        ('ommlds.backends.openai.protocol.responses.response', 'ReasoningResponsesOutputItem.SummaryText'),
    ),
)
def _process_dataclass__953f32063cf89facee83c6681c46db52e4592f93():
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
                text=self.text,
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
                self.text == other.text and
                self.type == other.type
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'text',
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
            'text',
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
                self.text,
                self.type,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            text: __dataclass__init__fields__0__annotation,
            type: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'text', text)
            __dataclass__object_setattr(self, 'type', type)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"text={self.text!r}")
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
        "Plans(tup=(CopyPlan(fields=('model', 'input', 'instructions', 'tools', 'tool_choice', 'parallel_tool_calls', '"
        "max_output_tokens', 'temperature', 'top_p', 'reasoning', 'previous_response_id', 'store', 'stream', 'include',"
        " 'metadata', 'truncation', 'user')), EqPlan(fields=('model', 'input', 'instructions', 'tools', 'tool_choice', "
        "'parallel_tool_calls', 'max_output_tokens', 'temperature', 'top_p', 'reasoning', 'previous_response_id', 'stor"
        "e', 'stream', 'include', 'metadata', 'truncation', 'user')), FrozenPlan(fields=('model', 'input', 'instruction"
        "s', 'tools', 'tool_choice', 'parallel_tool_calls', 'max_output_tokens', 'temperature', 'top_p', 'reasoning', '"
        "previous_response_id', 'store', 'stream', 'include', 'metadata', 'truncation', 'user'), allow_dynamic_dunder_a"
        "ttrs=False), HashPlan(action='add', fields=('model', 'input', 'instructions', 'tools', 'tool_choice', 'paralle"
        "l_tool_calls', 'max_output_tokens', 'temperature', 'top_p', 'reasoning', 'previous_response_id', 'store', 'str"
        "eam', 'include', 'metadata', 'truncation', 'user'), cache=False), InitPlan(fields=(InitPlan.Field(name='model'"
        ", annotation=OpRef(name='init.fields.00.annotation'), default=None, default_factory=None, init=True, override="
        "False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='input"
        "', annotation=OpRef(name='init.fields.01.annotation'), default=None, default_factory=None, init=True, override"
        "=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='inst"
        "ructions', annotation=OpRef(name='init.fields.02.annotation'), default=OpRef(name='init.fields.02.default'), d"
        "efault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, che"
        "ck_type=None), InitPlan.Field(name='tools', annotation=OpRef(name='init.fields.03.annotation'), default=OpRef("
        "name='init.fields.03.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE"
        ", coerce=None, validate=None, check_type=None), InitPlan.Field(name='tool_choice', annotation=OpRef(name='init"
        ".fields.04.annotation'), default=OpRef(name='init.fields.04.default'), default_factory=None, init=True, overri"
        "de=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='pa"
        "rallel_tool_calls', annotation=OpRef(name='init.fields.05.annotation'), default=OpRef(name='init.fields.05.def"
        "ault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate="
        "None, check_type=None), InitPlan.Field(name='max_output_tokens', annotation=OpRef(name='init.fields.06.annotat"
        "ion'), default=OpRef(name='init.fields.06.default'), default_factory=None, init=True, override=False, field_ty"
        "pe=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='temperature', annota"
        "tion=OpRef(name='init.fields.07.annotation'), default=OpRef(name='init.fields.07.default'), default_factory=No"
        "ne, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), In"
        "itPlan.Field(name='top_p', annotation=OpRef(name='init.fields.08.annotation'), default=OpRef(name='init.fields"
        ".08.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, va"
        "lidate=None, check_type=None), InitPlan.Field(name='reasoning', annotation=OpRef(name='init.fields.09.annotati"
        "on'), default=OpRef(name='init.fields.09.default'), default_factory=None, init=True, override=False, field_typ"
        "e=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='previous_response_id'"
        ", annotation=OpRef(name='init.fields.10.annotation'), default=OpRef(name='init.fields.10.default'), default_fa"
        "ctory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=N"
        "one), InitPlan.Field(name='store', annotation=OpRef(name='init.fields.11.annotation'), default=OpRef(name='ini"
        "t.fields.11.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce="
        "None, validate=None, check_type=None), InitPlan.Field(name='stream', annotation=OpRef(name='init.fields.12.ann"
        "otation'), default=OpRef(name='init.fields.12.default'), default_factory=None, init=True, override=False, fiel"
        "d_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='include', annota"
        "tion=OpRef(name='init.fields.13.annotation'), default=OpRef(name='init.fields.13.default'), default_factory=No"
        "ne, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), In"
        "itPlan.Field(name='metadata', annotation=OpRef(name='init.fields.14.annotation'), default=OpRef(name='init.fie"
        "lds.14.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None,"
        " validate=None, check_type=None), InitPlan.Field(name='truncation', annotation=OpRef(name='init.fields.15.anno"
        "tation'), default=OpRef(name='init.fields.15.default'), default_factory=None, init=True, override=False, field"
        "_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='user', annotation"
        "=OpRef(name='init.fields.16.annotation'), default=OpRef(name='init.fields.16.default'), default_factory=None, "
        "init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_"
        "param='self', std_params=(), kw_only_params=('model', 'input', 'instructions', 'tools', 'tool_choice', 'parall"
        "el_tool_calls', 'max_output_tokens', 'temperature', 'top_p', 'reasoning', 'previous_response_id', 'store', 'st"
        "ream', 'include', 'metadata', 'truncation', 'user'), frozen=True, slots=False, post_init_params=None, init_fns"
        "=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='model', kw_only=True, fn=None), ReprPlan.Field(na"
        "me='input', kw_only=True, fn=None), ReprPlan.Field(name='instructions', kw_only=True, fn=None), ReprPlan.Field"
        "(name='tools', kw_only=True, fn=None), ReprPlan.Field(name='tool_choice', kw_only=True, fn=None), ReprPlan.Fie"
        "ld(name='parallel_tool_calls', kw_only=True, fn=None), ReprPlan.Field(name='max_output_tokens', kw_only=True, "
        "fn=None), ReprPlan.Field(name='temperature', kw_only=True, fn=None), ReprPlan.Field(name='top_p', kw_only=True"
        ", fn=None), ReprPlan.Field(name='reasoning', kw_only=True, fn=None), ReprPlan.Field(name='previous_response_id"
        "', kw_only=True, fn=None), ReprPlan.Field(name='store', kw_only=True, fn=None), ReprPlan.Field(name='stream', "
        "kw_only=True, fn=None), ReprPlan.Field(name='include', kw_only=True, fn=None), ReprPlan.Field(name='metadata',"
        " kw_only=True, fn=None), ReprPlan.Field(name='truncation', kw_only=True, fn=None), ReprPlan.Field(name='user',"
        " kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='24d8af079f41c6d473808e4f1fed7ee72bec697c',
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
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.responses.request', 'ResponsesRequest'),
    ),
)
def _process_dataclass__24d8af079f41c6d473808e4f1fed7ee72bec697c():
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
                model=self.model,
                input=self.input,
                instructions=self.instructions,
                tools=self.tools,
                tool_choice=self.tool_choice,
                parallel_tool_calls=self.parallel_tool_calls,
                max_output_tokens=self.max_output_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                reasoning=self.reasoning,
                previous_response_id=self.previous_response_id,
                store=self.store,
                stream=self.stream,
                include=self.include,
                metadata=self.metadata,
                truncation=self.truncation,
                user=self.user,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.model == other.model and
                self.input == other.input and
                self.instructions == other.instructions and
                self.tools == other.tools and
                self.tool_choice == other.tool_choice and
                self.parallel_tool_calls == other.parallel_tool_calls and
                self.max_output_tokens == other.max_output_tokens and
                self.temperature == other.temperature and
                self.top_p == other.top_p and
                self.reasoning == other.reasoning and
                self.previous_response_id == other.previous_response_id and
                self.store == other.store and
                self.stream == other.stream and
                self.include == other.include and
                self.metadata == other.metadata and
                self.truncation == other.truncation and
                self.user == other.user
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'model',
            'input',
            'instructions',
            'tools',
            'tool_choice',
            'parallel_tool_calls',
            'max_output_tokens',
            'temperature',
            'top_p',
            'reasoning',
            'previous_response_id',
            'store',
            'stream',
            'include',
            'metadata',
            'truncation',
            'user',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'model',
            'input',
            'instructions',
            'tools',
            'tool_choice',
            'parallel_tool_calls',
            'max_output_tokens',
            'temperature',
            'top_p',
            'reasoning',
            'previous_response_id',
            'store',
            'stream',
            'include',
            'metadata',
            'truncation',
            'user',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.model,
                self.input,
                self.instructions,
                self.tools,
                self.tool_choice,
                self.parallel_tool_calls,
                self.max_output_tokens,
                self.temperature,
                self.top_p,
                self.reasoning,
                self.previous_response_id,
                self.store,
                self.stream,
                self.include,
                self.metadata,
                self.truncation,
                self.user,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            model: __dataclass__init__fields__00__annotation,
            input: __dataclass__init__fields__01__annotation,
            instructions: __dataclass__init__fields__02__annotation = __dataclass__init__fields__02__default,
            tools: __dataclass__init__fields__03__annotation = __dataclass__init__fields__03__default,
            tool_choice: __dataclass__init__fields__04__annotation = __dataclass__init__fields__04__default,
            parallel_tool_calls: __dataclass__init__fields__05__annotation = __dataclass__init__fields__05__default,
            max_output_tokens: __dataclass__init__fields__06__annotation = __dataclass__init__fields__06__default,
            temperature: __dataclass__init__fields__07__annotation = __dataclass__init__fields__07__default,
            top_p: __dataclass__init__fields__08__annotation = __dataclass__init__fields__08__default,
            reasoning: __dataclass__init__fields__09__annotation = __dataclass__init__fields__09__default,
            previous_response_id: __dataclass__init__fields__10__annotation = __dataclass__init__fields__10__default,
            store: __dataclass__init__fields__11__annotation = __dataclass__init__fields__11__default,
            stream: __dataclass__init__fields__12__annotation = __dataclass__init__fields__12__default,
            include: __dataclass__init__fields__13__annotation = __dataclass__init__fields__13__default,
            metadata: __dataclass__init__fields__14__annotation = __dataclass__init__fields__14__default,
            truncation: __dataclass__init__fields__15__annotation = __dataclass__init__fields__15__default,
            user: __dataclass__init__fields__16__annotation = __dataclass__init__fields__16__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'model', model)
            __dataclass__object_setattr(self, 'input', input)
            __dataclass__object_setattr(self, 'instructions', instructions)
            __dataclass__object_setattr(self, 'tools', tools)
            __dataclass__object_setattr(self, 'tool_choice', tool_choice)
            __dataclass__object_setattr(self, 'parallel_tool_calls', parallel_tool_calls)
            __dataclass__object_setattr(self, 'max_output_tokens', max_output_tokens)
            __dataclass__object_setattr(self, 'temperature', temperature)
            __dataclass__object_setattr(self, 'top_p', top_p)
            __dataclass__object_setattr(self, 'reasoning', reasoning)
            __dataclass__object_setattr(self, 'previous_response_id', previous_response_id)
            __dataclass__object_setattr(self, 'store', store)
            __dataclass__object_setattr(self, 'stream', stream)
            __dataclass__object_setattr(self, 'include', include)
            __dataclass__object_setattr(self, 'metadata', metadata)
            __dataclass__object_setattr(self, 'truncation', truncation)
            __dataclass__object_setattr(self, 'user', user)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"model={self.model!r}")
            parts.append(f"input={self.input!r}")
            parts.append(f"instructions={self.instructions!r}")
            parts.append(f"tools={self.tools!r}")
            parts.append(f"tool_choice={self.tool_choice!r}")
            parts.append(f"parallel_tool_calls={self.parallel_tool_calls!r}")
            parts.append(f"max_output_tokens={self.max_output_tokens!r}")
            parts.append(f"temperature={self.temperature!r}")
            parts.append(f"top_p={self.top_p!r}")
            parts.append(f"reasoning={self.reasoning!r}")
            parts.append(f"previous_response_id={self.previous_response_id!r}")
            parts.append(f"store={self.store!r}")
            parts.append(f"stream={self.stream!r}")
            parts.append(f"include={self.include!r}")
            parts.append(f"metadata={self.metadata!r}")
            parts.append(f"truncation={self.truncation!r}")
            parts.append(f"user={self.user!r}")
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
        "Plans(tup=(CopyPlan(fields=('effort', 'summary')), EqPlan(fields=('effort', 'summary')), FrozenPlan(fields=('e"
        "ffort', 'summary'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('effort', 'summary'), ca"
        "che=False), InitPlan(fields=(InitPlan.Field(name='effort', annotation=OpRef(name='init.fields.0.annotation'), "
        "default=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=Field"
        "Type.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='summary', annotation=OpRef(n"
        "ame='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True,"
        " override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='sel"
        "f', std_params=(), kw_only_params=('effort', 'summary'), frozen=True, slots=False, post_init_params=None, init"
        "_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='effort', kw_only=True, fn=None), ReprPlan.Fie"
        "ld(name='summary', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='2d69a02d767b46e5e129fc121b967e7adddaae5d',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.responses.request', 'ResponsesRequest.Reasoning'),
    ),
)
def _process_dataclass__2d69a02d767b46e5e129fc121b967e7adddaae5d():
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
                effort=self.effort,
                summary=self.summary,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.effort == other.effort and
                self.summary == other.summary
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'effort',
            'summary',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'effort',
            'summary',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.effort,
                self.summary,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            effort: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            summary: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'effort', effort)
            __dataclass__object_setattr(self, 'summary', summary)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"effort={self.effort!r}")
            parts.append(f"summary={self.summary!r}")
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
        "Plans(tup=(CopyPlan(fields=('content', 'role', 'id', 'status')), EqPlan(fields=('content', 'role', 'id', 'stat"
        "us')), FrozenPlan(fields=('content', 'role', 'id', 'status'), allow_dynamic_dunder_attrs=False), HashPlan(acti"
        "on='add', fields=('content', 'role', 'id', 'status'), cache=False), InitPlan(fields=(InitPlan.Field(name='cont"
        "ent', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, overri"
        "de=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='ro"
        "le', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_f"
        "actory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type="
        "None), InitPlan.Field(name='id', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.f"
        "ields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None"
        ", validate=None, check_type=None), InitPlan.Field(name='status', annotation=OpRef(name='init.fields.3.annotati"
        "on'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, field_type"
        "=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_"
        "params=('content', 'role', 'id', 'status'), frozen=True, slots=False, post_init_params=None, init_fns=(), vali"
        "date_fns=()), ReprPlan(fields=(ReprPlan.Field(name='content', kw_only=True, fn=None), ReprPlan.Field(name='id'"
        ", kw_only=True, fn=None), ReprPlan.Field(name='status', kw_only=True, fn=None)), id=False, terse=False, defaul"
        "t_fn=None)))"
    ),
    plan_repr_sha1='4a8640fb7b53bdf1866d114653e393aeb22a7e4e',
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
        ('ommlds.backends.openai.protocol.responses.response', 'MessageResponsesOutputItem'),
    ),
)
def _process_dataclass__4a8640fb7b53bdf1866d114653e393aeb22a7e4e():
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
                content=self.content,
                role=self.role,
                id=self.id,
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
                self.content == other.content and
                self.role == other.role and
                self.id == other.id and
                self.status == other.status
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'content',
            'role',
            'id',
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
            'content',
            'role',
            'id',
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
                self.content,
                self.role,
                self.id,
                self.status,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            content: __dataclass__init__fields__0__annotation,
            role: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            id: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            status: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'content', content)
            __dataclass__object_setattr(self, 'role', role)
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'status', status)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"content={self.content!r}")
            parts.append(f"id={self.id!r}")
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
        "Plans(tup=(CopyPlan(fields=('text', 'annotations', 'logprobs')), EqPlan(fields=('text', 'annotations', 'logpro"
        "bs')), FrozenPlan(fields=('text', 'annotations', 'logprobs'), allow_dynamic_dunder_attrs=False), HashPlan(acti"
        "on='add', fields=('text', 'annotations', 'logprobs'), cache=False), InitPlan(fields=(InitPlan.Field(name='text"
        "', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override="
        "False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='annot"
        "ations', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), defau"
        "lt_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_t"
        "ype=None), InitPlan.Field(name='logprobs', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(na"
        "me='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, c"
        "oerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('text', 'annot"
        "ations', 'logprobs'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan"
        "(fields=(ReprPlan.Field(name='text', kw_only=True, fn=None), ReprPlan.Field(name='annotations', kw_only=True, "
        "fn=None), ReprPlan.Field(name='logprobs', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='b2dee028f4884602c92a23c56d707817044e4f72',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.responses.response', 'OutputTextResponsesOutputContentPart'),
    ),
)
def _process_dataclass__b2dee028f4884602c92a23c56d707817044e4f72():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                text=self.text,
                annotations=self.annotations,
                logprobs=self.logprobs,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.text == other.text and
                self.annotations == other.annotations and
                self.logprobs == other.logprobs
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'text',
            'annotations',
            'logprobs',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'text',
            'annotations',
            'logprobs',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.text,
                self.annotations,
                self.logprobs,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            text: __dataclass__init__fields__0__annotation,
            annotations: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            logprobs: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'text', text)
            __dataclass__object_setattr(self, 'annotations', annotations)
            __dataclass__object_setattr(self, 'logprobs', logprobs)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"text={self.text!r}")
            parts.append(f"annotations={self.annotations!r}")
            parts.append(f"logprobs={self.logprobs!r}")
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
        "Plans(tup=(CopyPlan(fields=('refusal',)), EqPlan(fields=('refusal',)), FrozenPlan(fields=('refusal',), allow_d"
        "ynamic_dunder_attrs=False), HashPlan(action='add', fields=('refusal',), cache=False), InitPlan(fields=(InitPla"
        "n.Field(name='refusal', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None,"
        " init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), sel"
        "f_param='self', std_params=(), kw_only_params=('refusal',), frozen=True, slots=False, post_init_params=None, i"
        "nit_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='refusal', kw_only=True, fn=None),), id=Fal"
        "se, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='2396d382372f5c7cf195de56b22d50ac907f8aea',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.responses.response', 'RefusalResponsesOutputContentPart'),
    ),
)
def _process_dataclass__2396d382372f5c7cf195de56b22d50ac907f8aea():
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
                refusal=self.refusal,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.refusal == other.refusal
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'refusal',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'refusal',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.refusal,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            refusal: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'refusal', refusal)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"refusal={self.refusal!r}")
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
        "Plans(tup=(CopyPlan(fields=('id', 'object', 'created_at', 'status', 'model', 'output', 'usage', 'error', 'inco"
        "mplete_details', 'instructions', 'tools', 'tool_choice', 'parallel_tool_calls', 'max_output_tokens', 'max_tool"
        "_calls', 'temperature', 'top_p', 'top_logprobs', 'reasoning', 'text', 'previous_response_id', 'store', 'backgr"
        "ound', 'truncation', 'metadata', 'user', 'safety_identifier', 'prompt_cache_key', 'service_tier', 'billing', '"
        "output_text')), EqPlan(fields=('id', 'object', 'created_at', 'status', 'model', 'output', 'usage', 'error', 'i"
        "ncomplete_details', 'instructions', 'tools', 'tool_choice', 'parallel_tool_calls', 'max_output_tokens', 'max_t"
        "ool_calls', 'temperature', 'top_p', 'top_logprobs', 'reasoning', 'text', 'previous_response_id', 'store', 'bac"
        "kground', 'truncation', 'metadata', 'user', 'safety_identifier', 'prompt_cache_key', 'service_tier', 'billing'"
        ", 'output_text')), FrozenPlan(fields=('id', 'object', 'created_at', 'status', 'model', 'output', 'usage', 'err"
        "or', 'incomplete_details', 'instructions', 'tools', 'tool_choice', 'parallel_tool_calls', 'max_output_tokens',"
        " 'max_tool_calls', 'temperature', 'top_p', 'top_logprobs', 'reasoning', 'text', 'previous_response_id', 'store"
        "', 'background', 'truncation', 'metadata', 'user', 'safety_identifier', 'prompt_cache_key', 'service_tier', 'b"
        "illing', 'output_text'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('id', 'object', 'cr"
        "eated_at', 'status', 'model', 'output', 'usage', 'error', 'incomplete_details', 'instructions', 'tools', 'tool"
        "_choice', 'parallel_tool_calls', 'max_output_tokens', 'max_tool_calls', 'temperature', 'top_p', 'top_logprobs'"
        ", 'reasoning', 'text', 'previous_response_id', 'store', 'background', 'truncation', 'metadata', 'user', 'safet"
        "y_identifier', 'prompt_cache_key', 'service_tier', 'billing', 'output_text'), cache=False), InitPlan(fields=(I"
        "nitPlan.Field(name='id', annotation=OpRef(name='init.fields.00.annotation'), default=None, default_factory=Non"
        "e, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), Ini"
        "tPlan.Field(name='object', annotation=OpRef(name='init.fields.01.annotation'), default=OpRef(name='init.fields"
        ".01.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, va"
        "lidate=None, check_type=None), InitPlan.Field(name='created_at', annotation=OpRef(name='init.fields.02.annotat"
        "ion'), default=OpRef(name='init.fields.02.default'), default_factory=None, init=True, override=False, field_ty"
        "pe=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='status', annotation="
        "OpRef(name='init.fields.03.annotation'), default=OpRef(name='init.fields.03.default'), default_factory=None, i"
        "nit=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPla"
        "n.Field(name='model', annotation=OpRef(name='init.fields.04.annotation'), default=OpRef(name='init.fields.04.d"
        "efault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validat"
        "e=None, check_type=None), InitPlan.Field(name='output', annotation=OpRef(name='init.fields.05.annotation'), de"
        "fault=OpRef(name='init.fields.05.default'), default_factory=None, init=True, override=False, field_type=FieldT"
        "ype.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='usage', annotation=OpRef(name"
        "='init.fields.06.annotation'), default=OpRef(name='init.fields.06.default'), default_factory=None, init=True, "
        "override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(na"
        "me='error', annotation=OpRef(name='init.fields.07.annotation'), default=OpRef(name='init.fields.07.default'), "
        "default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, ch"
        "eck_type=None), InitPlan.Field(name='incomplete_details', annotation=OpRef(name='init.fields.08.annotation'), "
        "default=OpRef(name='init.fields.08.default'), default_factory=None, init=True, override=False, field_type=Fiel"
        "dType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='instructions', annotation=O"
        "pRef(name='init.fields.09.annotation'), default=OpRef(name='init.fields.09.default'), default_factory=None, in"
        "it=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan"
        ".Field(name='tools', annotation=OpRef(name='init.fields.10.annotation'), default=OpRef(name='init.fields.10.de"
        "fault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate"
        "=None, check_type=None), InitPlan.Field(name='tool_choice', annotation=OpRef(name='init.fields.11.annotation')"
        ", default=OpRef(name='init.fields.11.default'), default_factory=None, init=True, override=False, field_type=Fi"
        "eldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='parallel_tool_calls', ann"
        "otation=OpRef(name='init.fields.12.annotation'), default=OpRef(name='init.fields.12.default'), default_factory"
        "=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),"
        " InitPlan.Field(name='max_output_tokens', annotation=OpRef(name='init.fields.13.annotation'), default=OpRef(na"
        "me='init.fields.13.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, "
        "coerce=None, validate=None, check_type=None), InitPlan.Field(name='max_tool_calls', annotation=OpRef(name='ini"
        "t.fields.14.annotation'), default=OpRef(name='init.fields.14.default'), default_factory=None, init=True, overr"
        "ide=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='t"
        "emperature', annotation=OpRef(name='init.fields.15.annotation'), default=OpRef(name='init.fields.15.default'),"
        " default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, c"
        "heck_type=None), InitPlan.Field(name='top_p', annotation=OpRef(name='init.fields.16.annotation'), default=OpRe"
        "f(name='init.fields.16.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTAN"
        "CE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='top_logprobs', annotation=OpRef(name='i"
        "nit.fields.17.annotation'), default=OpRef(name='init.fields.17.default'), default_factory=None, init=True, ove"
        "rride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name="
        "'reasoning', annotation=OpRef(name='init.fields.18.annotation'), default=OpRef(name='init.fields.18.default'),"
        " default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, c"
        "heck_type=None), InitPlan.Field(name='text', annotation=OpRef(name='init.fields.19.annotation'), default=OpRef"
        "(name='init.fields.19.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANC"
        "E, coerce=None, validate=None, check_type=None), InitPlan.Field(name='previous_response_id', annotation=OpRef("
        "name='init.fields.20.annotation'), default=OpRef(name='init.fields.20.default'), default_factory=None, init=Tr"
        "ue, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fiel"
        "d(name='store', annotation=OpRef(name='init.fields.21.annotation'), default=OpRef(name='init.fields.21.default"
        "'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None"
        ", check_type=None), InitPlan.Field(name='background', annotation=OpRef(name='init.fields.22.annotation'), defa"
        "ult=OpRef(name='init.fields.22.default'), default_factory=None, init=True, override=False, field_type=FieldTyp"
        "e.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='truncation', annotation=OpRef(n"
        "ame='init.fields.23.annotation'), default=OpRef(name='init.fields.23.default'), default_factory=None, init=Tru"
        "e, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field"
        "(name='metadata', annotation=OpRef(name='init.fields.24.annotation'), default=OpRef(name='init.fields.24.defau"
        "lt'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=No"
        "ne, check_type=None), InitPlan.Field(name='user', annotation=OpRef(name='init.fields.25.annotation'), default="
        "OpRef(name='init.fields.25.default'), default_factory=None, init=True, override=False, field_type=FieldType.IN"
        "STANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='safety_identifier', annotation=OpRe"
        "f(name='init.fields.26.annotation'), default=OpRef(name='init.fields.26.default'), default_factory=None, init="
        "True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fi"
        "eld(name='prompt_cache_key', annotation=OpRef(name='init.fields.27.annotation'), default=OpRef(name='init.fiel"
        "ds.27.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, "
        "validate=None, check_type=None), InitPlan.Field(name='service_tier', annotation=OpRef(name='init.fields.28.ann"
        "otation'), default=OpRef(name='init.fields.28.default'), default_factory=None, init=True, override=False, fiel"
        "d_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='billing', annota"
        "tion=OpRef(name='init.fields.29.annotation'), default=OpRef(name='init.fields.29.default'), default_factory=No"
        "ne, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), In"
        "itPlan.Field(name='output_text', annotation=OpRef(name='init.fields.30.annotation'), default=OpRef(name='init."
        "fields.30.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=No"
        "ne, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('id', 'object', 'creat"
        "ed_at', 'status', 'model', 'output', 'usage', 'error', 'incomplete_details', 'instructions', 'tools', 'tool_ch"
        "oice', 'parallel_tool_calls', 'max_output_tokens', 'max_tool_calls', 'temperature', 'top_p', 'top_logprobs', '"
        "reasoning', 'text', 'previous_response_id', 'store', 'background', 'truncation', 'metadata', 'user', 'safety_i"
        "dentifier', 'prompt_cache_key', 'service_tier', 'billing', 'output_text'), frozen=True, slots=False, post_init"
        "_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='id', kw_only=True, fn=None)"
        ", ReprPlan.Field(name='created_at', kw_only=True, fn=None), ReprPlan.Field(name='status', kw_only=True, fn=Non"
        "e), ReprPlan.Field(name='model', kw_only=True, fn=None), ReprPlan.Field(name='output', kw_only=True, fn=None),"
        " ReprPlan.Field(name='usage', kw_only=True, fn=None), ReprPlan.Field(name='error', kw_only=True, fn=None), Rep"
        "rPlan.Field(name='incomplete_details', kw_only=True, fn=None), ReprPlan.Field(name='instructions', kw_only=Tru"
        "e, fn=None), ReprPlan.Field(name='tools', kw_only=True, fn=None), ReprPlan.Field(name='tool_choice', kw_only=T"
        "rue, fn=None), ReprPlan.Field(name='parallel_tool_calls', kw_only=True, fn=None), ReprPlan.Field(name='max_out"
        "put_tokens', kw_only=True, fn=None), ReprPlan.Field(name='max_tool_calls', kw_only=True, fn=None), ReprPlan.Fi"
        "eld(name='temperature', kw_only=True, fn=None), ReprPlan.Field(name='top_p', kw_only=True, fn=None), ReprPlan."
        "Field(name='top_logprobs', kw_only=True, fn=None), ReprPlan.Field(name='reasoning', kw_only=True, fn=None), Re"
        "prPlan.Field(name='text', kw_only=True, fn=None), ReprPlan.Field(name='previous_response_id', kw_only=True, fn"
        "=None), ReprPlan.Field(name='store', kw_only=True, fn=None), ReprPlan.Field(name='background', kw_only=True, f"
        "n=None), ReprPlan.Field(name='truncation', kw_only=True, fn=None), ReprPlan.Field(name='metadata', kw_only=Tru"
        "e, fn=None), ReprPlan.Field(name='user', kw_only=True, fn=None), ReprPlan.Field(name='safety_identifier', kw_o"
        "nly=True, fn=None), ReprPlan.Field(name='prompt_cache_key', kw_only=True, fn=None), ReprPlan.Field(name='servi"
        "ce_tier', kw_only=True, fn=None), ReprPlan.Field(name='billing', kw_only=True, fn=None), ReprPlan.Field(name='"
        "output_text', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='b29abbb2838d907c30261356eba7fdb40d4e91fd',
    op_ref_idents=(
        '__dataclass__init__fields__00__annotation',
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
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.responses.response', 'ResponsesResponse'),
    ),
)
def _process_dataclass__b29abbb2838d907c30261356eba7fdb40d4e91fd():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__00__annotation,
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
                object=self.object,
                created_at=self.created_at,
                status=self.status,
                model=self.model,
                output=self.output,
                usage=self.usage,
                error=self.error,
                incomplete_details=self.incomplete_details,
                instructions=self.instructions,
                tools=self.tools,
                tool_choice=self.tool_choice,
                parallel_tool_calls=self.parallel_tool_calls,
                max_output_tokens=self.max_output_tokens,
                max_tool_calls=self.max_tool_calls,
                temperature=self.temperature,
                top_p=self.top_p,
                top_logprobs=self.top_logprobs,
                reasoning=self.reasoning,
                text=self.text,
                previous_response_id=self.previous_response_id,
                store=self.store,
                background=self.background,
                truncation=self.truncation,
                metadata=self.metadata,
                user=self.user,
                safety_identifier=self.safety_identifier,
                prompt_cache_key=self.prompt_cache_key,
                service_tier=self.service_tier,
                billing=self.billing,
                output_text=self.output_text,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
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
                self.object == other.object and
                self.created_at == other.created_at and
                self.status == other.status and
                self.model == other.model and
                self.output == other.output and
                self.usage == other.usage and
                self.error == other.error and
                self.incomplete_details == other.incomplete_details and
                self.instructions == other.instructions and
                self.tools == other.tools and
                self.tool_choice == other.tool_choice and
                self.parallel_tool_calls == other.parallel_tool_calls and
                self.max_output_tokens == other.max_output_tokens and
                self.max_tool_calls == other.max_tool_calls and
                self.temperature == other.temperature and
                self.top_p == other.top_p and
                self.top_logprobs == other.top_logprobs and
                self.reasoning == other.reasoning and
                self.text == other.text and
                self.previous_response_id == other.previous_response_id and
                self.store == other.store and
                self.background == other.background and
                self.truncation == other.truncation and
                self.metadata == other.metadata and
                self.user == other.user and
                self.safety_identifier == other.safety_identifier and
                self.prompt_cache_key == other.prompt_cache_key and
                self.service_tier == other.service_tier and
                self.billing == other.billing and
                self.output_text == other.output_text
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'id',
            'object',
            'created_at',
            'status',
            'model',
            'output',
            'usage',
            'error',
            'incomplete_details',
            'instructions',
            'tools',
            'tool_choice',
            'parallel_tool_calls',
            'max_output_tokens',
            'max_tool_calls',
            'temperature',
            'top_p',
            'top_logprobs',
            'reasoning',
            'text',
            'previous_response_id',
            'store',
            'background',
            'truncation',
            'metadata',
            'user',
            'safety_identifier',
            'prompt_cache_key',
            'service_tier',
            'billing',
            'output_text',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'object',
            'created_at',
            'status',
            'model',
            'output',
            'usage',
            'error',
            'incomplete_details',
            'instructions',
            'tools',
            'tool_choice',
            'parallel_tool_calls',
            'max_output_tokens',
            'max_tool_calls',
            'temperature',
            'top_p',
            'top_logprobs',
            'reasoning',
            'text',
            'previous_response_id',
            'store',
            'background',
            'truncation',
            'metadata',
            'user',
            'safety_identifier',
            'prompt_cache_key',
            'service_tier',
            'billing',
            'output_text',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.object,
                self.created_at,
                self.status,
                self.model,
                self.output,
                self.usage,
                self.error,
                self.incomplete_details,
                self.instructions,
                self.tools,
                self.tool_choice,
                self.parallel_tool_calls,
                self.max_output_tokens,
                self.max_tool_calls,
                self.temperature,
                self.top_p,
                self.top_logprobs,
                self.reasoning,
                self.text,
                self.previous_response_id,
                self.store,
                self.background,
                self.truncation,
                self.metadata,
                self.user,
                self.safety_identifier,
                self.prompt_cache_key,
                self.service_tier,
                self.billing,
                self.output_text,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            id: __dataclass__init__fields__00__annotation,
            object: __dataclass__init__fields__01__annotation = __dataclass__init__fields__01__default,
            created_at: __dataclass__init__fields__02__annotation = __dataclass__init__fields__02__default,
            status: __dataclass__init__fields__03__annotation = __dataclass__init__fields__03__default,
            model: __dataclass__init__fields__04__annotation = __dataclass__init__fields__04__default,
            output: __dataclass__init__fields__05__annotation = __dataclass__init__fields__05__default,
            usage: __dataclass__init__fields__06__annotation = __dataclass__init__fields__06__default,
            error: __dataclass__init__fields__07__annotation = __dataclass__init__fields__07__default,
            incomplete_details: __dataclass__init__fields__08__annotation = __dataclass__init__fields__08__default,
            instructions: __dataclass__init__fields__09__annotation = __dataclass__init__fields__09__default,
            tools: __dataclass__init__fields__10__annotation = __dataclass__init__fields__10__default,
            tool_choice: __dataclass__init__fields__11__annotation = __dataclass__init__fields__11__default,
            parallel_tool_calls: __dataclass__init__fields__12__annotation = __dataclass__init__fields__12__default,
            max_output_tokens: __dataclass__init__fields__13__annotation = __dataclass__init__fields__13__default,
            max_tool_calls: __dataclass__init__fields__14__annotation = __dataclass__init__fields__14__default,
            temperature: __dataclass__init__fields__15__annotation = __dataclass__init__fields__15__default,
            top_p: __dataclass__init__fields__16__annotation = __dataclass__init__fields__16__default,
            top_logprobs: __dataclass__init__fields__17__annotation = __dataclass__init__fields__17__default,
            reasoning: __dataclass__init__fields__18__annotation = __dataclass__init__fields__18__default,
            text: __dataclass__init__fields__19__annotation = __dataclass__init__fields__19__default,
            previous_response_id: __dataclass__init__fields__20__annotation = __dataclass__init__fields__20__default,
            store: __dataclass__init__fields__21__annotation = __dataclass__init__fields__21__default,
            background: __dataclass__init__fields__22__annotation = __dataclass__init__fields__22__default,
            truncation: __dataclass__init__fields__23__annotation = __dataclass__init__fields__23__default,
            metadata: __dataclass__init__fields__24__annotation = __dataclass__init__fields__24__default,
            user: __dataclass__init__fields__25__annotation = __dataclass__init__fields__25__default,
            safety_identifier: __dataclass__init__fields__26__annotation = __dataclass__init__fields__26__default,
            prompt_cache_key: __dataclass__init__fields__27__annotation = __dataclass__init__fields__27__default,
            service_tier: __dataclass__init__fields__28__annotation = __dataclass__init__fields__28__default,
            billing: __dataclass__init__fields__29__annotation = __dataclass__init__fields__29__default,
            output_text: __dataclass__init__fields__30__annotation = __dataclass__init__fields__30__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'object', object)
            __dataclass__object_setattr(self, 'created_at', created_at)
            __dataclass__object_setattr(self, 'status', status)
            __dataclass__object_setattr(self, 'model', model)
            __dataclass__object_setattr(self, 'output', output)
            __dataclass__object_setattr(self, 'usage', usage)
            __dataclass__object_setattr(self, 'error', error)
            __dataclass__object_setattr(self, 'incomplete_details', incomplete_details)
            __dataclass__object_setattr(self, 'instructions', instructions)
            __dataclass__object_setattr(self, 'tools', tools)
            __dataclass__object_setattr(self, 'tool_choice', tool_choice)
            __dataclass__object_setattr(self, 'parallel_tool_calls', parallel_tool_calls)
            __dataclass__object_setattr(self, 'max_output_tokens', max_output_tokens)
            __dataclass__object_setattr(self, 'max_tool_calls', max_tool_calls)
            __dataclass__object_setattr(self, 'temperature', temperature)
            __dataclass__object_setattr(self, 'top_p', top_p)
            __dataclass__object_setattr(self, 'top_logprobs', top_logprobs)
            __dataclass__object_setattr(self, 'reasoning', reasoning)
            __dataclass__object_setattr(self, 'text', text)
            __dataclass__object_setattr(self, 'previous_response_id', previous_response_id)
            __dataclass__object_setattr(self, 'store', store)
            __dataclass__object_setattr(self, 'background', background)
            __dataclass__object_setattr(self, 'truncation', truncation)
            __dataclass__object_setattr(self, 'metadata', metadata)
            __dataclass__object_setattr(self, 'user', user)
            __dataclass__object_setattr(self, 'safety_identifier', safety_identifier)
            __dataclass__object_setattr(self, 'prompt_cache_key', prompt_cache_key)
            __dataclass__object_setattr(self, 'service_tier', service_tier)
            __dataclass__object_setattr(self, 'billing', billing)
            __dataclass__object_setattr(self, 'output_text', output_text)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"id={self.id!r}")
            parts.append(f"created_at={self.created_at!r}")
            parts.append(f"status={self.status!r}")
            parts.append(f"model={self.model!r}")
            parts.append(f"output={self.output!r}")
            parts.append(f"usage={self.usage!r}")
            parts.append(f"error={self.error!r}")
            parts.append(f"incomplete_details={self.incomplete_details!r}")
            parts.append(f"instructions={self.instructions!r}")
            parts.append(f"tools={self.tools!r}")
            parts.append(f"tool_choice={self.tool_choice!r}")
            parts.append(f"parallel_tool_calls={self.parallel_tool_calls!r}")
            parts.append(f"max_output_tokens={self.max_output_tokens!r}")
            parts.append(f"max_tool_calls={self.max_tool_calls!r}")
            parts.append(f"temperature={self.temperature!r}")
            parts.append(f"top_p={self.top_p!r}")
            parts.append(f"top_logprobs={self.top_logprobs!r}")
            parts.append(f"reasoning={self.reasoning!r}")
            parts.append(f"text={self.text!r}")
            parts.append(f"previous_response_id={self.previous_response_id!r}")
            parts.append(f"store={self.store!r}")
            parts.append(f"background={self.background!r}")
            parts.append(f"truncation={self.truncation!r}")
            parts.append(f"metadata={self.metadata!r}")
            parts.append(f"user={self.user!r}")
            parts.append(f"safety_identifier={self.safety_identifier!r}")
            parts.append(f"prompt_cache_key={self.prompt_cache_key!r}")
            parts.append(f"service_tier={self.service_tier!r}")
            parts.append(f"billing={self.billing!r}")
            parts.append(f"output_text={self.output_text!r}")
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
        "Plans(tup=(CopyPlan(fields=('input_tokens', 'output_tokens', 'total_tokens', 'input_tokens_details', 'output_t"
        "okens_details')), EqPlan(fields=('input_tokens', 'output_tokens', 'total_tokens', 'input_tokens_details', 'out"
        "put_tokens_details')), FrozenPlan(fields=('input_tokens', 'output_tokens', 'total_tokens', 'input_tokens_detai"
        "ls', 'output_tokens_details'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('input_tokens"
        "', 'output_tokens', 'total_tokens', 'input_tokens_details', 'output_tokens_details'), cache=False), InitPlan(f"
        "ields=(InitPlan.Field(name='input_tokens', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(na"
        "me='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, c"
        "oerce=None, validate=None, check_type=None), InitPlan.Field(name='output_tokens', annotation=OpRef(name='init."
        "fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override="
        "False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='total"
        "_tokens', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), defa"
        "ult_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_"
        "type=None), InitPlan.Field(name='input_tokens_details', annotation=OpRef(name='init.fields.3.annotation'), def"
        "ault=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldTyp"
        "e.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='output_tokens_details', annotat"
        "ion=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_factory=None,"
        " init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self"
        "_param='self', std_params=(), kw_only_params=('input_tokens', 'output_tokens', 'total_tokens', 'input_tokens_d"
        "etails', 'output_tokens_details'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns="
        "()), ReprPlan(fields=(ReprPlan.Field(name='input_tokens', kw_only=True, fn=None), ReprPlan.Field(name='output_"
        "tokens', kw_only=True, fn=None), ReprPlan.Field(name='total_tokens', kw_only=True, fn=None), ReprPlan.Field(na"
        "me='input_tokens_details', kw_only=True, fn=None), ReprPlan.Field(name='output_tokens_details', kw_only=True, "
        "fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='a822d0f45a5a217381abb9751204aeb3cf2e62c7',
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
    ),
    cls_names=(
        ('ommlds.backends.openai.protocol.responses.response', 'ResponsesUsage'),
    ),
)
def _process_dataclass__a822d0f45a5a217381abb9751204aeb3cf2e62c7():
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
                input_tokens=self.input_tokens,
                output_tokens=self.output_tokens,
                total_tokens=self.total_tokens,
                input_tokens_details=self.input_tokens_details,
                output_tokens_details=self.output_tokens_details,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.input_tokens == other.input_tokens and
                self.output_tokens == other.output_tokens and
                self.total_tokens == other.total_tokens and
                self.input_tokens_details == other.input_tokens_details and
                self.output_tokens_details == other.output_tokens_details
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'input_tokens',
            'output_tokens',
            'total_tokens',
            'input_tokens_details',
            'output_tokens_details',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'input_tokens',
            'output_tokens',
            'total_tokens',
            'input_tokens_details',
            'output_tokens_details',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
                self.input_tokens,
                self.output_tokens,
                self.total_tokens,
                self.input_tokens_details,
                self.output_tokens_details,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            input_tokens: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            output_tokens: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            total_tokens: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            input_tokens_details: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            output_tokens_details: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'input_tokens', input_tokens)
            __dataclass__object_setattr(self, 'output_tokens', output_tokens)
            __dataclass__object_setattr(self, 'total_tokens', total_tokens)
            __dataclass__object_setattr(self, 'input_tokens_details', input_tokens_details)
            __dataclass__object_setattr(self, 'output_tokens_details', output_tokens_details)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"input_tokens={self.input_tokens!r}")
            parts.append(f"output_tokens={self.output_tokens!r}")
            parts.append(f"total_tokens={self.total_tokens!r}")
            parts.append(f"input_tokens_details={self.input_tokens_details!r}")
            parts.append(f"output_tokens_details={self.output_tokens_details!r}")
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
