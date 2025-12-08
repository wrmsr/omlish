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
        "Plans(tup=(CopyPlan(fields=('id', 'object', 'created', 'model', 'system_fingerprint', 'choices', 'x_groq', 'se"
        "rvice_tier', 'usage')), EqPlan(fields=('id', 'object', 'created', 'model', 'system_fingerprint', 'choices', 'x"
        "_groq', 'service_tier', 'usage')), FrozenPlan(fields=('id', 'object', 'created', 'model', 'system_fingerprint'"
        ", 'choices', 'x_groq', 'service_tier', 'usage'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fie"
        "lds=('id', 'object', 'created', 'model', 'system_fingerprint', 'choices', 'x_groq', 'service_tier', 'usage'), "
        "cache=False), InitPlan(fields=(InitPlan.Field(name='id', annotation=OpRef(name='init.fields.0.annotation'), de"
        "fault=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valid"
        "ate=None, check_type=None), InitPlan.Field(name='object', annotation=OpRef(name='init.fields.1.annotation'), d"
        "efault=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldT"
        "ype.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='created', annotation=OpRef(na"
        "me='init.fields.2.annotation'), default=None, default_factory=None, init=True, override=False, field_type=Fiel"
        "dType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='model', annotation=OpRef(na"
        "me='init.fields.3.annotation'), default=None, default_factory=None, init=True, override=False, field_type=Fiel"
        "dType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='system_fingerprint', annota"
        "tion=OpRef(name='init.fields.4.annotation'), default=None, default_factory=None, init=True, override=False, fi"
        "eld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='choices', anno"
        "tation=OpRef(name='init.fields.5.annotation'), default=None, default_factory=None, init=True, override=False, "
        "field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='x_groq', ann"
        "otation=OpRef(name='init.fields.6.annotation'), default=OpRef(name='init.fields.6.default'), default_factory=N"
        "one, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), I"
        "nitPlan.Field(name='service_tier', annotation=OpRef(name='init.fields.7.annotation'), default=OpRef(name='init"
        ".fields.7.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=No"
        "ne, validate=None, check_type=None), InitPlan.Field(name='usage', annotation=OpRef(name='init.fields.8.annotat"
        "ion'), default=OpRef(name='init.fields.8.default'), default_factory=None, init=True, override=False, field_typ"
        "e=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only"
        "_params=('id', 'object', 'created', 'model', 'system_fingerprint', 'choices', 'x_groq', 'service_tier', 'usage"
        "'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan."
        "Field(name='id', kw_only=True, fn=None), ReprPlan.Field(name='object', kw_only=True, fn=None), ReprPlan.Field("
        "name='created', kw_only=True, fn=None), ReprPlan.Field(name='model', kw_only=True, fn=None), ReprPlan.Field(na"
        "me='system_fingerprint', kw_only=True, fn=None), ReprPlan.Field(name='choices', kw_only=True, fn=None), ReprPl"
        "an.Field(name='x_groq', kw_only=True, fn=None), ReprPlan.Field(name='service_tier', kw_only=True, fn=None), Re"
        "prPlan.Field(name='usage', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='e9fd011b88dd09b9d07234a0bed31c70cc048544',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__5__annotation',
        '__dataclass__init__fields__6__annotation',
        '__dataclass__init__fields__6__default',
        '__dataclass__init__fields__7__annotation',
        '__dataclass__init__fields__7__default',
        '__dataclass__init__fields__8__annotation',
        '__dataclass__init__fields__8__default',
    ),
    cls_names=(
        ('ommlds.backends.groq._marshal', 'ChatCompletionChunk'),
    ),
)
def _process_dataclass__e9fd011b88dd09b9d07234a0bed31c70cc048544():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__4__annotation,
        __dataclass__init__fields__5__annotation,
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
                object=self.object,
                created=self.created,
                model=self.model,
                system_fingerprint=self.system_fingerprint,
                choices=self.choices,
                x_groq=self.x_groq,
                service_tier=self.service_tier,
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
                self.object == other.object and
                self.created == other.created and
                self.model == other.model and
                self.system_fingerprint == other.system_fingerprint and
                self.choices == other.choices and
                self.x_groq == other.x_groq and
                self.service_tier == other.service_tier and
                self.usage == other.usage
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'id',
            'object',
            'created',
            'model',
            'system_fingerprint',
            'choices',
            'x_groq',
            'service_tier',
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
            'object',
            'created',
            'model',
            'system_fingerprint',
            'choices',
            'x_groq',
            'service_tier',
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
                self.object,
                self.created,
                self.model,
                self.system_fingerprint,
                self.choices,
                self.x_groq,
                self.service_tier,
                self.usage,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            id: __dataclass__init__fields__0__annotation,
            object: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            created: __dataclass__init__fields__2__annotation,
            model: __dataclass__init__fields__3__annotation,
            system_fingerprint: __dataclass__init__fields__4__annotation,
            choices: __dataclass__init__fields__5__annotation,
            x_groq: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
            service_tier: __dataclass__init__fields__7__annotation = __dataclass__init__fields__7__default,
            usage: __dataclass__init__fields__8__annotation = __dataclass__init__fields__8__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'object', object)
            __dataclass__object_setattr(self, 'created', created)
            __dataclass__object_setattr(self, 'model', model)
            __dataclass__object_setattr(self, 'system_fingerprint', system_fingerprint)
            __dataclass__object_setattr(self, 'choices', choices)
            __dataclass__object_setattr(self, 'x_groq', x_groq)
            __dataclass__object_setattr(self, 'service_tier', service_tier)
            __dataclass__object_setattr(self, 'usage', usage)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"id={self.id!r}")
            parts.append(f"object={self.object!r}")
            parts.append(f"created={self.created!r}")
            parts.append(f"model={self.model!r}")
            parts.append(f"system_fingerprint={self.system_fingerprint!r}")
            parts.append(f"choices={self.choices!r}")
            parts.append(f"x_groq={self.x_groq!r}")
            parts.append(f"service_tier={self.service_tier!r}")
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
        "Plans(tup=(CopyPlan(fields=('index', 'delta', 'logprobs', 'finish_reason')), EqPlan(fields=('index', 'delta', "
        "'logprobs', 'finish_reason')), FrozenPlan(fields=('index', 'delta', 'logprobs', 'finish_reason'), allow_dynami"
        "c_dunder_attrs=False), HashPlan(action='add', fields=('index', 'delta', 'logprobs', 'finish_reason'), cache=Fa"
        "lse), InitPlan(fields=(InitPlan.Field(name='index', annotation=OpRef(name='init.fields.0.annotation'), default"
        "=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=N"
        "one, check_type=None), InitPlan.Field(name='delta', annotation=OpRef(name='init.fields.1.annotation'), default"
        "=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=N"
        "one, check_type=None), InitPlan.Field(name='logprobs', annotation=OpRef(name='init.fields.2.annotation'), defa"
        "ult=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType"
        ".INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='finish_reason', annotation=OpRef"
        "(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=Tru"
        "e, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='s"
        "elf', std_params=(), kw_only_params=('index', 'delta', 'logprobs', 'finish_reason'), frozen=True, slots=False,"
        " post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='index', kw_only=T"
        "rue, fn=None), ReprPlan.Field(name='delta', kw_only=True, fn=None), ReprPlan.Field(name='logprobs', kw_only=Tr"
        "ue, fn=None), ReprPlan.Field(name='finish_reason', kw_only=True, fn=None)), id=False, terse=False, default_fn="
        "None)))"
    ),
    plan_repr_sha1='467d73fbbfc4ae23999c6b11c3b9336ff3fd0745',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ommlds.backends.groq._marshal', 'ChatCompletionChunk.Choice'),
    ),
)
def _process_dataclass__467d73fbbfc4ae23999c6b11c3b9336ff3fd0745():
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
                index=self.index,
                delta=self.delta,
                logprobs=self.logprobs,
                finish_reason=self.finish_reason,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
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
                self.delta == other.delta and
                self.logprobs == other.logprobs and
                self.finish_reason == other.finish_reason
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'index',
            'delta',
            'logprobs',
            'finish_reason',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'delta',
            'logprobs',
            'finish_reason',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                 or name in __dataclass___delattr_frozen_fields
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
                self.delta,
                self.logprobs,
                self.finish_reason,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            index: __dataclass__init__fields__0__annotation,
            delta: __dataclass__init__fields__1__annotation,
            logprobs: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            finish_reason: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'index', index)
            __dataclass__object_setattr(self, 'delta', delta)
            __dataclass__object_setattr(self, 'logprobs', logprobs)
            __dataclass__object_setattr(self, 'finish_reason', finish_reason)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"index={self.index!r}")
            parts.append(f"delta={self.delta!r}")
            parts.append(f"logprobs={self.logprobs!r}")
            parts.append(f"finish_reason={self.finish_reason!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('role', 'content', 'channel', 'reasoning', 'tool_calls', 'executed_tools')), EqPla"
        "n(fields=('role', 'content', 'channel', 'reasoning', 'tool_calls', 'executed_tools')), FrozenPlan(fields=('rol"
        "e', 'content', 'channel', 'reasoning', 'tool_calls', 'executed_tools'), allow_dynamic_dunder_attrs=False), Has"
        "hPlan(action='add', fields=('role', 'content', 'channel', 'reasoning', 'tool_calls', 'executed_tools'), cache="
        "False), InitPlan(fields=(InitPlan.Field(name='role', annotation=OpRef(name='init.fields.0.annotation'), defaul"
        "t=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.I"
        "NSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='content', annotation=OpRef(name='i"
        "nit.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, overr"
        "ide=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='c"
        "hannel', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), defau"
        "lt_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_t"
        "ype=None), InitPlan.Field(name='reasoning', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(n"
        "ame='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, "
        "coerce=None, validate=None, check_type=None), InitPlan.Field(name='tool_calls', annotation=OpRef(name='init.fi"
        "elds.4.annotation'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, override=Fa"
        "lse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='execute"
        "d_tools', annotation=OpRef(name='init.fields.5.annotation'), default=OpRef(name='init.fields.5.default'), defa"
        "ult_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_"
        "type=None)), self_param='self', std_params=(), kw_only_params=('role', 'content', 'channel', 'reasoning', 'too"
        "l_calls', 'executed_tools'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), R"
        "eprPlan(fields=(ReprPlan.Field(name='role', kw_only=True, fn=None), ReprPlan.Field(name='content', kw_only=Tru"
        "e, fn=None), ReprPlan.Field(name='channel', kw_only=True, fn=None), ReprPlan.Field(name='reasoning', kw_only=T"
        "rue, fn=None), ReprPlan.Field(name='tool_calls', kw_only=True, fn=None), ReprPlan.Field(name='executed_tools',"
        " kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='e17f86dab4d47b211aac3e6e4afe0442050a7a86',
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
        ('ommlds.backends.groq._marshal', 'ChatCompletionChunk.Choice.Delta'),
    ),
)
def _process_dataclass__e17f86dab4d47b211aac3e6e4afe0442050a7a86():
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
                role=self.role,
                content=self.content,
                channel=self.channel,
                reasoning=self.reasoning,
                tool_calls=self.tool_calls,
                executed_tools=self.executed_tools,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
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
                self.channel == other.channel and
                self.reasoning == other.reasoning and
                self.tool_calls == other.tool_calls and
                self.executed_tools == other.executed_tools
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'role',
            'content',
            'channel',
            'reasoning',
            'tool_calls',
            'executed_tools',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'channel',
            'reasoning',
            'tool_calls',
            'executed_tools',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                 or name in __dataclass___delattr_frozen_fields
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
                self.channel,
                self.reasoning,
                self.tool_calls,
                self.executed_tools,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            role: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            content: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            channel: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            reasoning: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            tool_calls: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            executed_tools: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'role', role)
            __dataclass__object_setattr(self, 'content', content)
            __dataclass__object_setattr(self, 'channel', channel)
            __dataclass__object_setattr(self, 'reasoning', reasoning)
            __dataclass__object_setattr(self, 'tool_calls', tool_calls)
            __dataclass__object_setattr(self, 'executed_tools', executed_tools)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"role={self.role!r}")
            parts.append(f"content={self.content!r}")
            parts.append(f"channel={self.channel!r}")
            parts.append(f"reasoning={self.reasoning!r}")
            parts.append(f"tool_calls={self.tool_calls!r}")
            parts.append(f"executed_tools={self.executed_tools!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
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
        "kw_only=True, fn=None), ReprPlan.Field(name='function', kw_only=True, fn=None), ReprPlan.Field(name='type', kw"
        "_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='60dd172cc10b3281c0cf9cea0a9cccff26bad0f2',
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
        ('ommlds.backends.groq._marshal', 'ChatCompletionChunk.Choice.Delta.ToolCall'),
    ),
)
def _process_dataclass__60dd172cc10b3281c0cf9cea0a9cccff26bad0f2():
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
        ('ommlds.backends.groq._marshal', 'ChatCompletionChunk.Choice.Delta.ToolCall.Function'),
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
        "Plans(tup=(CopyPlan(fields=('messages', 'model', 'citation_options', 'compound_custom', 'disable_tool_validati"
        "on', 'documents', 'frequency_penalty', 'include_reasoning', 'logit_bias', 'logprobs', 'max_completion_tokens',"
        " 'n', 'parallel_tool_calls', 'presence_penalty', 'reasoning_effort', 'reasoning_format', 'response_format', 's"
        "earch_settings', 'seed', 'service_tier', 'stop', 'store', 'stream', 'stream_options', 'temperature', 'ool_choi"
        "ce', 'tools', 'top_logprobs', 'top_p', 'user')), EqPlan(fields=('messages', 'model', 'citation_options', 'comp"
        "ound_custom', 'disable_tool_validation', 'documents', 'frequency_penalty', 'include_reasoning', 'logit_bias', "
        "'logprobs', 'max_completion_tokens', 'n', 'parallel_tool_calls', 'presence_penalty', 'reasoning_effort', 'reas"
        "oning_format', 'response_format', 'search_settings', 'seed', 'service_tier', 'stop', 'store', 'stream', 'strea"
        "m_options', 'temperature', 'ool_choice', 'tools', 'top_logprobs', 'top_p', 'user')), FrozenPlan(fields=('messa"
        "ges', 'model', 'citation_options', 'compound_custom', 'disable_tool_validation', 'documents', 'frequency_penal"
        "ty', 'include_reasoning', 'logit_bias', 'logprobs', 'max_completion_tokens', 'n', 'parallel_tool_calls', 'pres"
        "ence_penalty', 'reasoning_effort', 'reasoning_format', 'response_format', 'search_settings', 'seed', 'service_"
        "tier', 'stop', 'store', 'stream', 'stream_options', 'temperature', 'ool_choice', 'tools', 'top_logprobs', 'top"
        "_p', 'user'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('messages', 'model', 'citation"
        "_options', 'compound_custom', 'disable_tool_validation', 'documents', 'frequency_penalty', 'include_reasoning'"
        ", 'logit_bias', 'logprobs', 'max_completion_tokens', 'n', 'parallel_tool_calls', 'presence_penalty', 'reasonin"
        "g_effort', 'reasoning_format', 'response_format', 'search_settings', 'seed', 'service_tier', 'stop', 'store', "
        "'stream', 'stream_options', 'temperature', 'ool_choice', 'tools', 'top_logprobs', 'top_p', 'user'), cache=Fals"
        "e), InitPlan(fields=(InitPlan.Field(name='messages', annotation=OpRef(name='init.fields.0.annotation'), defaul"
        "t=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate="
        "None, check_type=None), InitPlan.Field(name='model', annotation=OpRef(name='init.fields.1.annotation'), defaul"
        "t=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate="
        "None, check_type=None), InitPlan.Field(name='citation_options', annotation=OpRef(name='init.fields.2.annotatio"
        "n'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_type="
        "FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='compound_custom', annot"
        "ation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=Non"
        "e, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), Ini"
        "tPlan.Field(name='disable_tool_validation', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(n"
        "ame='init.fields.4.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, "
        "coerce=None, validate=None, check_type=None), InitPlan.Field(name='documents', annotation=OpRef(name='init.fie"
        "lds.5.annotation'), default=OpRef(name='init.fields.5.default'), default_factory=None, init=True, override=Fal"
        "se, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='frequenc"
        "y_penalty', annotation=OpRef(name='init.fields.6.annotation'), default=OpRef(name='init.fields.6.default'), de"
        "fault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, chec"
        "k_type=None), InitPlan.Field(name='include_reasoning', annotation=OpRef(name='init.fields.7.annotation'), defa"
        "ult=OpRef(name='init.fields.7.default'), default_factory=None, init=True, override=False, field_type=FieldType"
        ".INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='logit_bias', annotation=OpRef(na"
        "me='init.fields.8.annotation'), default=OpRef(name='init.fields.8.default'), default_factory=None, init=True, "
        "override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(na"
        "me='logprobs', annotation=OpRef(name='init.fields.9.annotation'), default=OpRef(name='init.fields.9.default'),"
        " default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, c"
        "heck_type=None), InitPlan.Field(name='max_completion_tokens', annotation=OpRef(name='init.fields.10.annotation"
        "'), default=OpRef(name='init.fields.10.default'), default_factory=None, init=True, override=False, field_type="
        "FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='n', annotation=OpRef(na"
        "me='init.fields.11.annotation'), default=OpRef(name='init.fields.11.default'), default_factory=None, init=True"
        ", override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field("
        "name='parallel_tool_calls', annotation=OpRef(name='init.fields.12.annotation'), default=OpRef(name='init.field"
        "s.12.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, v"
        "alidate=None, check_type=None), InitPlan.Field(name='presence_penalty', annotation=OpRef(name='init.fields.13."
        "annotation'), default=OpRef(name='init.fields.13.default'), default_factory=None, init=True, override=False, f"
        "ield_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='reasoning_eff"
        "ort', annotation=OpRef(name='init.fields.14.annotation'), default=OpRef(name='init.fields.14.default'), defaul"
        "t_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_ty"
        "pe=None), InitPlan.Field(name='reasoning_format', annotation=OpRef(name='init.fields.15.annotation'), default="
        "OpRef(name='init.fields.15.default'), default_factory=None, init=True, override=False, field_type=FieldType.IN"
        "STANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='response_format', annotation=OpRef("
        "name='init.fields.16.annotation'), default=OpRef(name='init.fields.16.default'), default_factory=None, init=Tr"
        "ue, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fiel"
        "d(name='search_settings', annotation=OpRef(name='init.fields.17.annotation'), default=OpRef(name='init.fields."
        "17.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, val"
        "idate=None, check_type=None), InitPlan.Field(name='seed', annotation=OpRef(name='init.fields.18.annotation'), "
        "default=OpRef(name='init.fields.18.default'), default_factory=None, init=True, override=False, field_type=Fiel"
        "dType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='service_tier', annotation=O"
        "pRef(name='init.fields.19.annotation'), default=OpRef(name='init.fields.19.default'), default_factory=None, in"
        "it=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan"
        ".Field(name='stop', annotation=OpRef(name='init.fields.20.annotation'), default=OpRef(name='init.fields.20.def"
        "ault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate="
        "None, check_type=None), InitPlan.Field(name='store', annotation=OpRef(name='init.fields.21.annotation'), defau"
        "lt=OpRef(name='init.fields.21.default'), default_factory=None, init=True, override=False, field_type=FieldType"
        ".INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='stream', annotation=OpRef(name='"
        "init.fields.22.annotation'), default=OpRef(name='init.fields.22.default'), default_factory=None, init=True, ov"
        "erride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name"
        "='stream_options', annotation=OpRef(name='init.fields.23.annotation'), default=OpRef(name='init.fields.23.defa"
        "ult'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=N"
        "one, check_type=None), InitPlan.Field(name='temperature', annotation=OpRef(name='init.fields.24.annotation'), "
        "default=OpRef(name='init.fields.24.default'), default_factory=None, init=True, override=False, field_type=Fiel"
        "dType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='ool_choice', annotation=OpR"
        "ef(name='init.fields.25.annotation'), default=OpRef(name='init.fields.25.default'), default_factory=None, init"
        "=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.F"
        "ield(name='tools', annotation=OpRef(name='init.fields.26.annotation'), default=OpRef(name='init.fields.26.defa"
        "ult'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=N"
        "one, check_type=None), InitPlan.Field(name='top_logprobs', annotation=OpRef(name='init.fields.27.annotation'),"
        " default=OpRef(name='init.fields.27.default'), default_factory=None, init=True, override=False, field_type=Fie"
        "ldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='top_p', annotation=OpRef(n"
        "ame='init.fields.28.annotation'), default=OpRef(name='init.fields.28.default'), default_factory=None, init=Tru"
        "e, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field"
        "(name='user', annotation=OpRef(name='init.fields.29.annotation'), default=OpRef(name='init.fields.29.default')"
        ", default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, "
        "check_type=None)), self_param='self', std_params=(), kw_only_params=('messages', 'model', 'citation_options', "
        "'compound_custom', 'disable_tool_validation', 'documents', 'frequency_penalty', 'include_reasoning', 'logit_bi"
        "as', 'logprobs', 'max_completion_tokens', 'n', 'parallel_tool_calls', 'presence_penalty', 'reasoning_effort', "
        "'reasoning_format', 'response_format', 'search_settings', 'seed', 'service_tier', 'stop', 'store', 'stream', '"
        "stream_options', 'temperature', 'ool_choice', 'tools', 'top_logprobs', 'top_p', 'user'), frozen=True, slots=Fa"
        "lse, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='messages', kw"
        "_only=True, fn=None), ReprPlan.Field(name='model', kw_only=True, fn=None), ReprPlan.Field(name='citation_optio"
        "ns', kw_only=True, fn=None), ReprPlan.Field(name='compound_custom', kw_only=True, fn=None), ReprPlan.Field(nam"
        "e='disable_tool_validation', kw_only=True, fn=None), ReprPlan.Field(name='documents', kw_only=True, fn=None), "
        "ReprPlan.Field(name='frequency_penalty', kw_only=True, fn=None), ReprPlan.Field(name='include_reasoning', kw_o"
        "nly=True, fn=None), ReprPlan.Field(name='logit_bias', kw_only=True, fn=None), ReprPlan.Field(name='logprobs', "
        "kw_only=True, fn=None), ReprPlan.Field(name='max_completion_tokens', kw_only=True, fn=None), ReprPlan.Field(na"
        "me='n', kw_only=True, fn=None), ReprPlan.Field(name='parallel_tool_calls', kw_only=True, fn=None), ReprPlan.Fi"
        "eld(name='presence_penalty', kw_only=True, fn=None), ReprPlan.Field(name='reasoning_effort', kw_only=True, fn="
        "None), ReprPlan.Field(name='reasoning_format', kw_only=True, fn=None), ReprPlan.Field(name='response_format', "
        "kw_only=True, fn=None), ReprPlan.Field(name='search_settings', kw_only=True, fn=None), ReprPlan.Field(name='se"
        "ed', kw_only=True, fn=None), ReprPlan.Field(name='service_tier', kw_only=True, fn=None), ReprPlan.Field(name='"
        "stop', kw_only=True, fn=None), ReprPlan.Field(name='store', kw_only=True, fn=None), ReprPlan.Field(name='strea"
        "m', kw_only=True, fn=None), ReprPlan.Field(name='stream_options', kw_only=True, fn=None), ReprPlan.Field(name="
        "'temperature', kw_only=True, fn=None), ReprPlan.Field(name='ool_choice', kw_only=True, fn=None), ReprPlan.Fiel"
        "d(name='tools', kw_only=True, fn=None), ReprPlan.Field(name='top_logprobs', kw_only=True, fn=None), ReprPlan.F"
        "ield(name='top_p', kw_only=True, fn=None), ReprPlan.Field(name='user', kw_only=True, fn=None)), id=False, ters"
        "e=False, default_fn=None)))"
    ),
    plan_repr_sha1='e1491e80a9c22594a08c75d1ecf8caab2dd47a88',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
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
        ('ommlds.backends.groq._marshal', 'ChatCompletionRequest'),
    ),
)
def _process_dataclass__e1491e80a9c22594a08c75d1ecf8caab2dd47a88():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                messages=self.messages,
                model=self.model,
                citation_options=self.citation_options,
                compound_custom=self.compound_custom,
                disable_tool_validation=self.disable_tool_validation,
                documents=self.documents,
                frequency_penalty=self.frequency_penalty,
                include_reasoning=self.include_reasoning,
                logit_bias=self.logit_bias,
                logprobs=self.logprobs,
                max_completion_tokens=self.max_completion_tokens,
                n=self.n,
                parallel_tool_calls=self.parallel_tool_calls,
                presence_penalty=self.presence_penalty,
                reasoning_effort=self.reasoning_effort,
                reasoning_format=self.reasoning_format,
                response_format=self.response_format,
                search_settings=self.search_settings,
                seed=self.seed,
                service_tier=self.service_tier,
                stop=self.stop,
                store=self.store,
                stream=self.stream,
                stream_options=self.stream_options,
                temperature=self.temperature,
                ool_choice=self.ool_choice,
                tools=self.tools,
                top_logprobs=self.top_logprobs,
                top_p=self.top_p,
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
                self.messages == other.messages and
                self.model == other.model and
                self.citation_options == other.citation_options and
                self.compound_custom == other.compound_custom and
                self.disable_tool_validation == other.disable_tool_validation and
                self.documents == other.documents and
                self.frequency_penalty == other.frequency_penalty and
                self.include_reasoning == other.include_reasoning and
                self.logit_bias == other.logit_bias and
                self.logprobs == other.logprobs and
                self.max_completion_tokens == other.max_completion_tokens and
                self.n == other.n and
                self.parallel_tool_calls == other.parallel_tool_calls and
                self.presence_penalty == other.presence_penalty and
                self.reasoning_effort == other.reasoning_effort and
                self.reasoning_format == other.reasoning_format and
                self.response_format == other.response_format and
                self.search_settings == other.search_settings and
                self.seed == other.seed and
                self.service_tier == other.service_tier and
                self.stop == other.stop and
                self.store == other.store and
                self.stream == other.stream and
                self.stream_options == other.stream_options and
                self.temperature == other.temperature and
                self.ool_choice == other.ool_choice and
                self.tools == other.tools and
                self.top_logprobs == other.top_logprobs and
                self.top_p == other.top_p and
                self.user == other.user
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'messages',
            'model',
            'citation_options',
            'compound_custom',
            'disable_tool_validation',
            'documents',
            'frequency_penalty',
            'include_reasoning',
            'logit_bias',
            'logprobs',
            'max_completion_tokens',
            'n',
            'parallel_tool_calls',
            'presence_penalty',
            'reasoning_effort',
            'reasoning_format',
            'response_format',
            'search_settings',
            'seed',
            'service_tier',
            'stop',
            'store',
            'stream',
            'stream_options',
            'temperature',
            'ool_choice',
            'tools',
            'top_logprobs',
            'top_p',
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
            'messages',
            'model',
            'citation_options',
            'compound_custom',
            'disable_tool_validation',
            'documents',
            'frequency_penalty',
            'include_reasoning',
            'logit_bias',
            'logprobs',
            'max_completion_tokens',
            'n',
            'parallel_tool_calls',
            'presence_penalty',
            'reasoning_effort',
            'reasoning_format',
            'response_format',
            'search_settings',
            'seed',
            'service_tier',
            'stop',
            'store',
            'stream',
            'stream_options',
            'temperature',
            'ool_choice',
            'tools',
            'top_logprobs',
            'top_p',
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
                self.messages,
                self.model,
                self.citation_options,
                self.compound_custom,
                self.disable_tool_validation,
                self.documents,
                self.frequency_penalty,
                self.include_reasoning,
                self.logit_bias,
                self.logprobs,
                self.max_completion_tokens,
                self.n,
                self.parallel_tool_calls,
                self.presence_penalty,
                self.reasoning_effort,
                self.reasoning_format,
                self.response_format,
                self.search_settings,
                self.seed,
                self.service_tier,
                self.stop,
                self.store,
                self.stream,
                self.stream_options,
                self.temperature,
                self.ool_choice,
                self.tools,
                self.top_logprobs,
                self.top_p,
                self.user,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            messages: __dataclass__init__fields__0__annotation,
            model: __dataclass__init__fields__1__annotation,
            citation_options: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            compound_custom: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            disable_tool_validation: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            documents: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
            frequency_penalty: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
            include_reasoning: __dataclass__init__fields__7__annotation = __dataclass__init__fields__7__default,
            logit_bias: __dataclass__init__fields__8__annotation = __dataclass__init__fields__8__default,
            logprobs: __dataclass__init__fields__9__annotation = __dataclass__init__fields__9__default,
            max_completion_tokens: __dataclass__init__fields__10__annotation = __dataclass__init__fields__10__default,
            n: __dataclass__init__fields__11__annotation = __dataclass__init__fields__11__default,
            parallel_tool_calls: __dataclass__init__fields__12__annotation = __dataclass__init__fields__12__default,
            presence_penalty: __dataclass__init__fields__13__annotation = __dataclass__init__fields__13__default,
            reasoning_effort: __dataclass__init__fields__14__annotation = __dataclass__init__fields__14__default,
            reasoning_format: __dataclass__init__fields__15__annotation = __dataclass__init__fields__15__default,
            response_format: __dataclass__init__fields__16__annotation = __dataclass__init__fields__16__default,
            search_settings: __dataclass__init__fields__17__annotation = __dataclass__init__fields__17__default,
            seed: __dataclass__init__fields__18__annotation = __dataclass__init__fields__18__default,
            service_tier: __dataclass__init__fields__19__annotation = __dataclass__init__fields__19__default,
            stop: __dataclass__init__fields__20__annotation = __dataclass__init__fields__20__default,
            store: __dataclass__init__fields__21__annotation = __dataclass__init__fields__21__default,
            stream: __dataclass__init__fields__22__annotation = __dataclass__init__fields__22__default,
            stream_options: __dataclass__init__fields__23__annotation = __dataclass__init__fields__23__default,
            temperature: __dataclass__init__fields__24__annotation = __dataclass__init__fields__24__default,
            ool_choice: __dataclass__init__fields__25__annotation = __dataclass__init__fields__25__default,
            tools: __dataclass__init__fields__26__annotation = __dataclass__init__fields__26__default,
            top_logprobs: __dataclass__init__fields__27__annotation = __dataclass__init__fields__27__default,
            top_p: __dataclass__init__fields__28__annotation = __dataclass__init__fields__28__default,
            user: __dataclass__init__fields__29__annotation = __dataclass__init__fields__29__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'messages', messages)
            __dataclass__object_setattr(self, 'model', model)
            __dataclass__object_setattr(self, 'citation_options', citation_options)
            __dataclass__object_setattr(self, 'compound_custom', compound_custom)
            __dataclass__object_setattr(self, 'disable_tool_validation', disable_tool_validation)
            __dataclass__object_setattr(self, 'documents', documents)
            __dataclass__object_setattr(self, 'frequency_penalty', frequency_penalty)
            __dataclass__object_setattr(self, 'include_reasoning', include_reasoning)
            __dataclass__object_setattr(self, 'logit_bias', logit_bias)
            __dataclass__object_setattr(self, 'logprobs', logprobs)
            __dataclass__object_setattr(self, 'max_completion_tokens', max_completion_tokens)
            __dataclass__object_setattr(self, 'n', n)
            __dataclass__object_setattr(self, 'parallel_tool_calls', parallel_tool_calls)
            __dataclass__object_setattr(self, 'presence_penalty', presence_penalty)
            __dataclass__object_setattr(self, 'reasoning_effort', reasoning_effort)
            __dataclass__object_setattr(self, 'reasoning_format', reasoning_format)
            __dataclass__object_setattr(self, 'response_format', response_format)
            __dataclass__object_setattr(self, 'search_settings', search_settings)
            __dataclass__object_setattr(self, 'seed', seed)
            __dataclass__object_setattr(self, 'service_tier', service_tier)
            __dataclass__object_setattr(self, 'stop', stop)
            __dataclass__object_setattr(self, 'store', store)
            __dataclass__object_setattr(self, 'stream', stream)
            __dataclass__object_setattr(self, 'stream_options', stream_options)
            __dataclass__object_setattr(self, 'temperature', temperature)
            __dataclass__object_setattr(self, 'ool_choice', ool_choice)
            __dataclass__object_setattr(self, 'tools', tools)
            __dataclass__object_setattr(self, 'top_logprobs', top_logprobs)
            __dataclass__object_setattr(self, 'top_p', top_p)
            __dataclass__object_setattr(self, 'user', user)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"messages={self.messages!r}")
            parts.append(f"model={self.model!r}")
            parts.append(f"citation_options={self.citation_options!r}")
            parts.append(f"compound_custom={self.compound_custom!r}")
            parts.append(f"disable_tool_validation={self.disable_tool_validation!r}")
            parts.append(f"documents={self.documents!r}")
            parts.append(f"frequency_penalty={self.frequency_penalty!r}")
            parts.append(f"include_reasoning={self.include_reasoning!r}")
            parts.append(f"logit_bias={self.logit_bias!r}")
            parts.append(f"logprobs={self.logprobs!r}")
            parts.append(f"max_completion_tokens={self.max_completion_tokens!r}")
            parts.append(f"n={self.n!r}")
            parts.append(f"parallel_tool_calls={self.parallel_tool_calls!r}")
            parts.append(f"presence_penalty={self.presence_penalty!r}")
            parts.append(f"reasoning_effort={self.reasoning_effort!r}")
            parts.append(f"reasoning_format={self.reasoning_format!r}")
            parts.append(f"response_format={self.response_format!r}")
            parts.append(f"search_settings={self.search_settings!r}")
            parts.append(f"seed={self.seed!r}")
            parts.append(f"service_tier={self.service_tier!r}")
            parts.append(f"stop={self.stop!r}")
            parts.append(f"store={self.store!r}")
            parts.append(f"stream={self.stream!r}")
            parts.append(f"stream_options={self.stream_options!r}")
            parts.append(f"temperature={self.temperature!r}")
            parts.append(f"ool_choice={self.ool_choice!r}")
            parts.append(f"tools={self.tools!r}")
            parts.append(f"top_logprobs={self.top_logprobs!r}")
            parts.append(f"top_p={self.top_p!r}")
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
        "Plans(tup=(CopyPlan(fields=('content', 'name', 'reasoning', 'role', 'tool_calls')), EqPlan(fields=('content', "
        "'name', 'reasoning', 'role', 'tool_calls')), FrozenPlan(fields=('content', 'name', 'reasoning', 'role', 'tool_"
        "calls'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('content', 'name', 'reasoning', 'ro"
        "le', 'tool_calls'), cache=False), InitPlan(fields=(InitPlan.Field(name='content', annotation=OpRef(name='init."
        "fields.0.annotation'), default=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override="
        "False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='name'"
        ", annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_fact"
        "ory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=Non"
        "e), InitPlan.Field(name='reasoning', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='in"
        "it.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce="
        "None, validate=None, check_type=None), InitPlan.Field(name='role', annotation=OpRef(name='init.fields.3.annota"
        "tion'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, field_ty"
        "pe=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='tool_calls', annotat"
        "ion=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_factory=None,"
        " init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self"
        "_param='self', std_params=(), kw_only_params=('content', 'name', 'reasoning', 'role', 'tool_calls'), frozen=Tr"
        "ue, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='c"
        "ontent', kw_only=True, fn=None), ReprPlan.Field(name='name', kw_only=True, fn=None), ReprPlan.Field(name='reas"
        "oning', kw_only=True, fn=None), ReprPlan.Field(name='role', kw_only=True, fn=None), ReprPlan.Field(name='tool_"
        "calls', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='2de9ecb1f74a62bcebb0d3b0ecfb40da845e6d29',
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
        ('ommlds.backends.groq._marshal', 'ChatCompletionRequest.AssistantMessage'),
    ),
)
def _process_dataclass__2de9ecb1f74a62bcebb0d3b0ecfb40da845e6d29():
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
                name=self.name,
                reasoning=self.reasoning,
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
                self.name == other.name and
                self.reasoning == other.reasoning and
                self.role == other.role and
                self.tool_calls == other.tool_calls
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'content',
            'name',
            'reasoning',
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
            'name',
            'reasoning',
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
                self.name,
                self.reasoning,
                self.role,
                self.tool_calls,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            content: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            name: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            reasoning: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            role: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            tool_calls: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'content', content)
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'reasoning', reasoning)
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
            parts.append(f"name={self.name!r}")
            parts.append(f"reasoning={self.reasoning!r}")
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
        "Plans(tup=(CopyPlan(fields=('function', 'id', 'type')), EqPlan(fields=('function', 'id', 'type')), FrozenPlan("
        "fields=('function', 'id', 'type'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('function"
        "', 'id', 'type'), cache=False), InitPlan(fields=(InitPlan.Field(name='function', annotation=OpRef(name='init.f"
        "ields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INST"
        "ANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='id', annotation=OpRef(name='init.fiel"
        "ds.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANC"
        "E, coerce=None, validate=None, check_type=None), InitPlan.Field(name='type', annotation=OpRef(name='init.field"
        "s.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False"
        ", field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params="
        "(), kw_only_params=('function', 'id', 'type'), frozen=True, slots=False, post_init_params=None, init_fns=(), v"
        "alidate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='function', kw_only=True, fn=None), ReprPlan.Field(name="
        "'id', kw_only=True, fn=None), ReprPlan.Field(name='type', kw_only=True, fn=None)), id=False, terse=False, defa"
        "ult_fn=None)))"
    ),
    plan_repr_sha1='9a547257d5667228bf1cc9153bb81540dd355566',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.backends.groq._marshal', 'ChatCompletionRequest.AssistantMessage.ToolCall'),
    ),
)
def _process_dataclass__9a547257d5667228bf1cc9153bb81540dd355566():
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
                function=self.function,
                id=self.id,
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
                self.id == other.id and
                self.type == other.type
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'function',
            'id',
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
            'id',
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
                self.id,
                self.type,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            function: __dataclass__init__fields__0__annotation,
            id: __dataclass__init__fields__1__annotation,
            type: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'function', function)
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'type', type)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"function={self.function!r}")
            parts.append(f"id={self.id!r}")
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
        ('ommlds.backends.groq._marshal', 'ChatCompletionRequest.AssistantMessage.ToolCall.Function'),
        ('ommlds.backends.groq._marshal', 'ChatCompletionResponse.Choice.Message.ToolCall.Function'),
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
        "Plans(tup=(CopyPlan(fields=()), EqPlan(fields=()), FrozenPlan(fields=(), allow_dynamic_dunder_attrs=False), Ha"
        "shPlan(action='add', fields=(), cache=False), InitPlan(fields=(), self_param='self', std_params=(), kw_only_pa"
        "rams=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(), i"
        "d=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='e1f7edfe11f2b721d6a656c46e698fedc95461bb',
    op_ref_idents=(),
    cls_names=(
        ('ommlds.backends.groq._marshal', 'ChatCompletionRequest.Message'),
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
        "Plans(tup=(CopyPlan(fields=('content', 'name', 'role')), EqPlan(fields=('content', 'name', 'role')), FrozenPla"
        "n(fields=('content', 'name', 'role'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('conte"
        "nt', 'name', 'role'), cache=False), InitPlan(fields=(InitPlan.Field(name='content', annotation=OpRef(name='ini"
        "t.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.I"
        "NSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='name', annotation=OpRef(name='init"
        ".fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override"
        "=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='role"
        "', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_fac"
        "tory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=No"
        "ne)), self_param='self', std_params=(), kw_only_params=('content', 'name', 'role'), frozen=True, slots=False, "
        "post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='content', kw_only="
        "True, fn=None), ReprPlan.Field(name='name', kw_only=True, fn=None), ReprPlan.Field(name='role', kw_only=True, "
        "fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='949874790b7bd392e18566e3aaeab60bc9f5b3ca',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.backends.groq._marshal', 'ChatCompletionRequest.SystemMessage'),
        ('ommlds.backends.groq._marshal', 'ChatCompletionRequest.UserMessage'),
    ),
)
def _process_dataclass__949874790b7bd392e18566e3aaeab60bc9f5b3ca():
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
                content=self.content,
                name=self.name,
                role=self.role,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
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
                self.name == other.name and
                self.role == other.role
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'content',
            'name',
            'role',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'role',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                 or name in __dataclass___delattr_frozen_fields
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
                self.role,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            content: __dataclass__init__fields__0__annotation,
            name: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            role: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'content', content)
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'role', role)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"content={self.content!r}")
            parts.append(f"name={self.name!r}")
            parts.append(f"role={self.role!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
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
        "e.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('"
        "function', 'type'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(f"
        "ields=(ReprPlan.Field(name='function', kw_only=True, fn=None), ReprPlan.Field(name='type', kw_only=True, fn=No"
        "ne)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='bd6ded8da6444356e49af8ebb589982d11d87580',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.backends.groq._marshal', 'ChatCompletionRequest.Tool'),
    ),
)
def _process_dataclass__bd6ded8da6444356e49af8ebb589982d11d87580():
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
            *,
            function: __dataclass__init__fields__0__annotation,
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
        "Plans(tup=(CopyPlan(fields=('description', 'name', 'parameters', 'strict')), EqPlan(fields=('description', 'na"
        "me', 'parameters', 'strict')), FrozenPlan(fields=('description', 'name', 'parameters', 'strict'), allow_dynami"
        "c_dunder_attrs=False), HashPlan(action='add', fields=('description', 'name', 'parameters', 'strict'), cache=Fa"
        "lse), InitPlan(fields=(InitPlan.Field(name='description', annotation=OpRef(name='init.fields.0.annotation'), d"
        "efault=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldT"
        "ype.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='name', annotation=OpRef(name="
        "'init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldTy"
        "pe.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='parameters', annotation=OpRef("
        "name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True"
        ", override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field("
        "name='strict', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'),"
        " default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, c"
        "heck_type=None)), self_param='self', std_params=(), kw_only_params=('description', 'name', 'parameters', 'stri"
        "ct'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPla"
        "n.Field(name='description', kw_only=True, fn=None), ReprPlan.Field(name='name', kw_only=True, fn=None), ReprPl"
        "an.Field(name='parameters', kw_only=True, fn=None), ReprPlan.Field(name='strict', kw_only=True, fn=None)), id="
        "False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='4ed9c56354a4cd79fa0c26411404bbac3a601050',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ommlds.backends.groq._marshal', 'ChatCompletionRequest.Tool.Function'),
    ),
)
def _process_dataclass__4ed9c56354a4cd79fa0c26411404bbac3a601050():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
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
                description=self.description,
                name=self.name,
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
                self.description == other.description and
                self.name == other.name and
                self.parameters == other.parameters and
                self.strict == other.strict
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'description',
            'name',
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
            'description',
            'name',
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
                self.description,
                self.name,
                self.parameters,
                self.strict,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            description: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            name: __dataclass__init__fields__1__annotation,
            parameters: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            strict: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'description', description)
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'parameters', parameters)
            __dataclass__object_setattr(self, 'strict', strict)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"description={self.description!r}")
            parts.append(f"name={self.name!r}")
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
        "Plans(tup=(CopyPlan(fields=('content', 'role', 'tool_call_id')), EqPlan(fields=('content', 'role', 'tool_call_"
        "id')), FrozenPlan(fields=('content', 'role', 'tool_call_id'), allow_dynamic_dunder_attrs=False), HashPlan(acti"
        "on='add', fields=('content', 'role', 'tool_call_id'), cache=False), InitPlan(fields=(InitPlan.Field(name='cont"
        "ent', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, overri"
        "de=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='ro"
        "le', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_f"
        "actory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type="
        "None), InitPlan.Field(name='tool_call_id', annotation=OpRef(name='init.fields.2.annotation'), default=None, de"
        "fault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, chec"
        "k_type=None)), self_param='self', std_params=(), kw_only_params=('content', 'role', 'tool_call_id'), frozen=Tr"
        "ue, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='c"
        "ontent', kw_only=True, fn=None), ReprPlan.Field(name='role', kw_only=True, fn=None), ReprPlan.Field(name='tool"
        "_call_id', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='18ba47404a1fa13e445ea63b3aea366cf6d89a2f',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
    ),
    cls_names=(
        ('ommlds.backends.groq._marshal', 'ChatCompletionRequest.ToolMessage'),
    ),
)
def _process_dataclass__18ba47404a1fa13e445ea63b3aea366cf6d89a2f():
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
                content=self.content,
                role=self.role,
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
                self.role == other.role and
                self.tool_call_id == other.tool_call_id
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'content',
            'role',
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
            'role',
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
                self.role,
                self.tool_call_id,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            content: __dataclass__init__fields__0__annotation,
            role: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            tool_call_id: __dataclass__init__fields__2__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'content', content)
            __dataclass__object_setattr(self, 'role', role)
            __dataclass__object_setattr(self, 'tool_call_id', tool_call_id)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"content={self.content!r}")
            parts.append(f"role={self.role!r}")
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
        "Plans(tup=(CopyPlan(fields=('choices', 'created', 'id', 'model', 'object', 'system_fingerprint', 'usage', 'usa"
        "ge_breakdown', 'x_groq', 'service_tier')), EqPlan(fields=('choices', 'created', 'id', 'model', 'object', 'syst"
        "em_fingerprint', 'usage', 'usage_breakdown', 'x_groq', 'service_tier')), FrozenPlan(fields=('choices', 'create"
        "d', 'id', 'model', 'object', 'system_fingerprint', 'usage', 'usage_breakdown', 'x_groq', 'service_tier'), allo"
        "w_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('choices', 'created', 'id', 'model', 'object', '"
        "system_fingerprint', 'usage', 'usage_breakdown', 'x_groq', 'service_tier'), cache=False), InitPlan(fields=(Ini"
        "tPlan.Field(name='choices', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=N"
        "one, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), I"
        "nitPlan.Field(name='created', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory"
        "=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),"
        " InitPlan.Field(name='id', annotation=OpRef(name='init.fields.2.annotation'), default=None, default_factory=No"
        "ne, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), In"
        "itPlan.Field(name='model', annotation=OpRef(name='init.fields.3.annotation'), default=None, default_factory=No"
        "ne, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), In"
        "itPlan.Field(name='object', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields"
        ".4.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, val"
        "idate=None, check_type=None), InitPlan.Field(name='system_fingerprint', annotation=OpRef(name='init.fields.5.a"
        "nnotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coe"
        "rce=None, validate=None, check_type=None), InitPlan.Field(name='usage', annotation=OpRef(name='init.fields.6.a"
        "nnotation'), default=OpRef(name='init.fields.6.default'), default_factory=None, init=True, override=False, fie"
        "ld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='usage_breakdown"
        "', annotation=OpRef(name='init.fields.7.annotation'), default=OpRef(name='init.fields.7.default'), default_fac"
        "tory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=No"
        "ne), InitPlan.Field(name='x_groq', annotation=OpRef(name='init.fields.8.annotation'), default=OpRef(name='init"
        ".fields.8.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=No"
        "ne, validate=None, check_type=None), InitPlan.Field(name='service_tier', annotation=OpRef(name='init.fields.9."
        "annotation'), default=OpRef(name='init.fields.9.default'), default_factory=None, init=True, override=False, fi"
        "eld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), "
        "kw_only_params=('choices', 'created', 'id', 'model', 'object', 'system_fingerprint', 'usage', 'usage_breakdown"
        "', 'x_groq', 'service_tier'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), "
        "ReprPlan(fields=(ReprPlan.Field(name='choices', kw_only=True, fn=None), ReprPlan.Field(name='created', kw_only"
        "=True, fn=None), ReprPlan.Field(name='id', kw_only=True, fn=None), ReprPlan.Field(name='model', kw_only=True, "
        "fn=None), ReprPlan.Field(name='object', kw_only=True, fn=None), ReprPlan.Field(name='system_fingerprint', kw_o"
        "nly=True, fn=None), ReprPlan.Field(name='usage', kw_only=True, fn=None), ReprPlan.Field(name='usage_breakdown'"
        ", kw_only=True, fn=None), ReprPlan.Field(name='x_groq', kw_only=True, fn=None), ReprPlan.Field(name='service_t"
        "ier', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='22f83c20a81ad41b49ccfde5256b25d3df3dd90c',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__4__default',
        '__dataclass__init__fields__5__annotation',
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
        ('ommlds.backends.groq._marshal', 'ChatCompletionResponse'),
    ),
)
def _process_dataclass__22f83c20a81ad41b49ccfde5256b25d3df3dd90c():
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
                choices=self.choices,
                created=self.created,
                id=self.id,
                model=self.model,
                object=self.object,
                system_fingerprint=self.system_fingerprint,
                usage=self.usage,
                usage_breakdown=self.usage_breakdown,
                x_groq=self.x_groq,
                service_tier=self.service_tier,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.choices == other.choices and
                self.created == other.created and
                self.id == other.id and
                self.model == other.model and
                self.object == other.object and
                self.system_fingerprint == other.system_fingerprint and
                self.usage == other.usage and
                self.usage_breakdown == other.usage_breakdown and
                self.x_groq == other.x_groq and
                self.service_tier == other.service_tier
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'choices',
            'created',
            'id',
            'model',
            'object',
            'system_fingerprint',
            'usage',
            'usage_breakdown',
            'x_groq',
            'service_tier',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'created',
            'id',
            'model',
            'object',
            'system_fingerprint',
            'usage',
            'usage_breakdown',
            'x_groq',
            'service_tier',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                 or name in __dataclass___delattr_frozen_fields
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
                self.created,
                self.id,
                self.model,
                self.object,
                self.system_fingerprint,
                self.usage,
                self.usage_breakdown,
                self.x_groq,
                self.service_tier,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            choices: __dataclass__init__fields__0__annotation,
            created: __dataclass__init__fields__1__annotation,
            id: __dataclass__init__fields__2__annotation,
            model: __dataclass__init__fields__3__annotation,
            object: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            system_fingerprint: __dataclass__init__fields__5__annotation,
            usage: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
            usage_breakdown: __dataclass__init__fields__7__annotation = __dataclass__init__fields__7__default,
            x_groq: __dataclass__init__fields__8__annotation = __dataclass__init__fields__8__default,
            service_tier: __dataclass__init__fields__9__annotation = __dataclass__init__fields__9__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'choices', choices)
            __dataclass__object_setattr(self, 'created', created)
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'model', model)
            __dataclass__object_setattr(self, 'object', object)
            __dataclass__object_setattr(self, 'system_fingerprint', system_fingerprint)
            __dataclass__object_setattr(self, 'usage', usage)
            __dataclass__object_setattr(self, 'usage_breakdown', usage_breakdown)
            __dataclass__object_setattr(self, 'x_groq', x_groq)
            __dataclass__object_setattr(self, 'service_tier', service_tier)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"choices={self.choices!r}")
            parts.append(f"created={self.created!r}")
            parts.append(f"id={self.id!r}")
            parts.append(f"model={self.model!r}")
            parts.append(f"object={self.object!r}")
            parts.append(f"system_fingerprint={self.system_fingerprint!r}")
            parts.append(f"usage={self.usage!r}")
            parts.append(f"usage_breakdown={self.usage_breakdown!r}")
            parts.append(f"x_groq={self.x_groq!r}")
            parts.append(f"service_tier={self.service_tier!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
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
        ('ommlds.backends.groq._marshal', 'ChatCompletionResponse.Choice'),
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
        "Plans(tup=(CopyPlan(fields=('annotations', 'content', 'executed_tools', 'reasoning', 'role', 'tool_calls')), E"
        "qPlan(fields=('annotations', 'content', 'executed_tools', 'reasoning', 'role', 'tool_calls')), FrozenPlan(fiel"
        "ds=('annotations', 'content', 'executed_tools', 'reasoning', 'role', 'tool_calls'), allow_dynamic_dunder_attrs"
        "=False), HashPlan(action='add', fields=('annotations', 'content', 'executed_tools', 'reasoning', 'role', 'tool"
        "_calls'), cache=False), InitPlan(fields=(InitPlan.Field(name='annotations', annotation=OpRef(name='init.fields"
        ".0.annotation'), default=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=False,"
        " field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='content', a"
        "nnotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory"
        "=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),"
        " InitPlan.Field(name='executed_tools', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='"
        "init.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerc"
        "e=None, validate=None, check_type=None), InitPlan.Field(name='reasoning', annotation=OpRef(name='init.fields.3"
        ".annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, f"
        "ield_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='role', annota"
        "tion=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_factory=None"
        ", init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), Init"
        "Plan.Field(name='tool_calls', annotation=OpRef(name='init.fields.5.annotation'), default=OpRef(name='init.fiel"
        "ds.5.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, v"
        "alidate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('annotations', 'content', '"
        "executed_tools', 'reasoning', 'role', 'tool_calls'), frozen=True, slots=False, post_init_params=None, init_fns"
        "=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='annotations', kw_only=True, fn=None), ReprPlan.Fi"
        "eld(name='content', kw_only=True, fn=None), ReprPlan.Field(name='executed_tools', kw_only=True, fn=None), Repr"
        "Plan.Field(name='reasoning', kw_only=True, fn=None), ReprPlan.Field(name='role', kw_only=True, fn=None), ReprP"
        "lan.Field(name='tool_calls', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='9130d639b5468f8ff473adfc8b544dc6ef79a71a',
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
        ('ommlds.backends.groq._marshal', 'ChatCompletionResponse.Choice.Message'),
    ),
)
def _process_dataclass__9130d639b5468f8ff473adfc8b544dc6ef79a71a():
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
                annotations=self.annotations,
                content=self.content,
                executed_tools=self.executed_tools,
                reasoning=self.reasoning,
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
                self.annotations == other.annotations and
                self.content == other.content and
                self.executed_tools == other.executed_tools and
                self.reasoning == other.reasoning and
                self.role == other.role and
                self.tool_calls == other.tool_calls
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'annotations',
            'content',
            'executed_tools',
            'reasoning',
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
            'annotations',
            'content',
            'executed_tools',
            'reasoning',
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
                self.annotations,
                self.content,
                self.executed_tools,
                self.reasoning,
                self.role,
                self.tool_calls,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            annotations: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            content: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            executed_tools: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            reasoning: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            role: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            tool_calls: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'annotations', annotations)
            __dataclass__object_setattr(self, 'content', content)
            __dataclass__object_setattr(self, 'executed_tools', executed_tools)
            __dataclass__object_setattr(self, 'reasoning', reasoning)
            __dataclass__object_setattr(self, 'role', role)
            __dataclass__object_setattr(self, 'tool_calls', tool_calls)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"annotations={self.annotations!r}")
            parts.append(f"content={self.content!r}")
            parts.append(f"executed_tools={self.executed_tools!r}")
            parts.append(f"reasoning={self.reasoning!r}")
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
        "ion', kw_only=True, fn=None), ReprPlan.Field(name='type', kw_only=True, fn=None)), id=False, terse=False, defa"
        "ult_fn=None)))"
    ),
    plan_repr_sha1='7cd19137ccf16704c343ecf64cbb8bbbe65a626b',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.backends.groq._marshal', 'ChatCompletionResponse.Choice.Message.ToolCall'),
    ),
)
def _process_dataclass__7cd19137ccf16704c343ecf64cbb8bbbe65a626b():
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
        "Plans(tup=(CopyPlan(fields=('arguments', 'index', 'type', 'browser_results', 'code_results', 'output', 'search"
        "_results')), EqPlan(fields=('arguments', 'index', 'type', 'browser_results', 'code_results', 'output', 'search"
        "_results')), FrozenPlan(fields=('arguments', 'index', 'type', 'browser_results', 'code_results', 'output', 'se"
        "arch_results'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('arguments', 'index', 'type'"
        ", 'browser_results', 'code_results', 'output', 'search_results'), cache=False), InitPlan(fields=(InitPlan.Fiel"
        "d(name='arguments', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, ini"
        "t=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan."
        "Field(name='index', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, ini"
        "t=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan."
        "Field(name='type', annotation=OpRef(name='init.fields.2.annotation'), default=None, default_factory=None, init"
        "=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.F"
        "ield(name='browser_results', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.field"
        "s.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, va"
        "lidate=None, check_type=None), InitPlan.Field(name='code_results', annotation=OpRef(name='init.fields.4.annota"
        "tion'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, override=False, field_ty"
        "pe=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='output', annotation="
        "OpRef(name='init.fields.5.annotation'), default=OpRef(name='init.fields.5.default'), default_factory=None, ini"
        "t=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan."
        "Field(name='search_results', annotation=OpRef(name='init.fields.6.annotation'), default=OpRef(name='init.field"
        "s.6.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, va"
        "lidate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('arguments', 'index', 'type'"
        ", 'browser_results', 'code_results', 'output', 'search_results'), frozen=True, slots=False, post_init_params=N"
        "one, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='arguments', kw_only=True, fn=None), "
        "ReprPlan.Field(name='index', kw_only=True, fn=None), ReprPlan.Field(name='type', kw_only=True, fn=None), ReprP"
        "lan.Field(name='browser_results', kw_only=True, fn=None), ReprPlan.Field(name='code_results', kw_only=True, fn"
        "=None), ReprPlan.Field(name='output', kw_only=True, fn=None), ReprPlan.Field(name='search_results', kw_only=Tr"
        "ue, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='0af7551195bca061ad193c49ddcf78305ce3d840',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
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
        ('ommlds.backends.groq._marshal', 'ExecutedTool'),
    ),
)
def _process_dataclass__0af7551195bca061ad193c49ddcf78305ce3d840():
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
                arguments=self.arguments,
                index=self.index,
                type=self.type,
                browser_results=self.browser_results,
                code_results=self.code_results,
                output=self.output,
                search_results=self.search_results,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
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
                self.index == other.index and
                self.type == other.type and
                self.browser_results == other.browser_results and
                self.code_results == other.code_results and
                self.output == other.output and
                self.search_results == other.search_results
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'arguments',
            'index',
            'type',
            'browser_results',
            'code_results',
            'output',
            'search_results',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'index',
            'type',
            'browser_results',
            'code_results',
            'output',
            'search_results',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                 or name in __dataclass___delattr_frozen_fields
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
                self.index,
                self.type,
                self.browser_results,
                self.code_results,
                self.output,
                self.search_results,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            arguments: __dataclass__init__fields__0__annotation,
            index: __dataclass__init__fields__1__annotation,
            type: __dataclass__init__fields__2__annotation,
            browser_results: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            code_results: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            output: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
            search_results: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'arguments', arguments)
            __dataclass__object_setattr(self, 'index', index)
            __dataclass__object_setattr(self, 'type', type)
            __dataclass__object_setattr(self, 'browser_results', browser_results)
            __dataclass__object_setattr(self, 'code_results', code_results)
            __dataclass__object_setattr(self, 'output', output)
            __dataclass__object_setattr(self, 'search_results', search_results)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"arguments={self.arguments!r}")
            parts.append(f"index={self.index!r}")
            parts.append(f"type={self.type!r}")
            parts.append(f"browser_results={self.browser_results!r}")
            parts.append(f"code_results={self.code_results!r}")
            parts.append(f"output={self.output!r}")
            parts.append(f"search_results={self.search_results!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass
