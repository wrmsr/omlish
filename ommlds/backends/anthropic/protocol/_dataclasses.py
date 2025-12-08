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
        "Plans(tup=(CopyPlan(fields=('ephemeral_5m_input_tokens', 'ephemeral_1h_input_tokens')), EqPlan(fields=('epheme"
        "ral_5m_input_tokens', 'ephemeral_1h_input_tokens')), FrozenPlan(fields=('ephemeral_5m_input_tokens', 'ephemera"
        "l_1h_input_tokens'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('ephemeral_5m_input_tok"
        "ens', 'ephemeral_1h_input_tokens'), cache=False), InitPlan(fields=(InitPlan.Field(name='ephemeral_5m_input_tok"
        "ens', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'), default_"
        "factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type"
        "=None), InitPlan.Field(name='ephemeral_1h_input_tokens', annotation=OpRef(name='init.fields.1.annotation'), de"
        "fault=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldTy"
        "pe.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=("
        "'ephemeral_5m_input_tokens', 'ephemeral_1h_input_tokens'), frozen=True, slots=False, post_init_params=None, in"
        "it_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='ephemeral_5m_input_tokens', kw_only=True, f"
        "n=None), ReprPlan.Field(name='ephemeral_1h_input_tokens', kw_only=True, fn=None)), id=False, terse=False, defa"
        "ult_fn=None)))"
    ),
    plan_repr_sha1='5c5ca30d2c7c7eb47b5926b664cd0fabb3279da5',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.backends.anthropic.protocol', 'CacheCreation'),
    ),
)
def _process_dataclass__5c5ca30d2c7c7eb47b5926b664cd0fabb3279da5():
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
                ephemeral_5m_input_tokens=self.ephemeral_5m_input_tokens,
                ephemeral_1h_input_tokens=self.ephemeral_1h_input_tokens,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.ephemeral_5m_input_tokens == other.ephemeral_5m_input_tokens and
                self.ephemeral_1h_input_tokens == other.ephemeral_1h_input_tokens
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'ephemeral_5m_input_tokens',
            'ephemeral_1h_input_tokens',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                 or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'ephemeral_5m_input_tokens',
            'ephemeral_1h_input_tokens',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                 or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.ephemeral_5m_input_tokens,
                self.ephemeral_1h_input_tokens,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            ephemeral_5m_input_tokens: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            ephemeral_1h_input_tokens: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'ephemeral_5m_input_tokens', ephemeral_5m_input_tokens)
            __dataclass__object_setattr(self, 'ephemeral_1h_input_tokens', ephemeral_1h_input_tokens)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"ephemeral_5m_input_tokens={self.ephemeral_5m_input_tokens!r}")
            parts.append(f"ephemeral_1h_input_tokens={self.ephemeral_1h_input_tokens!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
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
        ('ommlds.backends.anthropic.protocol', 'Content.EphemeralCacheControl'),
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
        "Plans(tup=(CopyPlan(fields=('id', 'role', 'model', 'content', 'stop_reason', 'stop_sequence', 'usage')), EqPla"
        "n(fields=('id', 'role', 'model', 'content', 'stop_reason', 'stop_sequence', 'usage')), FrozenPlan(fields=('id'"
        ", 'role', 'model', 'content', 'stop_reason', 'stop_sequence', 'usage'), allow_dynamic_dunder_attrs=False), Has"
        "hPlan(action='add', fields=('id', 'role', 'model', 'content', 'stop_reason', 'stop_sequence', 'usage'), cache="
        "False), InitPlan(fields=(InitPlan.Field(name='id', annotation=OpRef(name='init.fields.0.annotation'), default="
        "OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INS"
        "TANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='role', annotation=OpRef(name='init.f"
        "ields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INST"
        "ANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='model', annotation=OpRef(name='init.f"
        "ields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=F"
        "alse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='conten"
        "t', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_fa"
        "ctory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=N"
        "one), InitPlan.Field(name='stop_reason', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name"
        "='init.fields.4.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coe"
        "rce=None, validate=None, check_type=None), InitPlan.Field(name='stop_sequence', annotation=OpRef(name='init.fi"
        "elds.5.annotation'), default=OpRef(name='init.fields.5.default'), default_factory=None, init=True, override=Fa"
        "lse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='usage',"
        " annotation=OpRef(name='init.fields.6.annotation'), default=OpRef(name='init.fields.6.default'), default_facto"
        "ry=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None"
        ")), self_param='self', std_params=(), kw_only_params=('id', 'role', 'model', 'content', 'stop_reason', 'stop_s"
        "equence', 'usage'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(f"
        "ields=(ReprPlan.Field(name='id', kw_only=True, fn=None), ReprPlan.Field(name='role', kw_only=True, fn=None), R"
        "eprPlan.Field(name='model', kw_only=True, fn=None), ReprPlan.Field(name='content', kw_only=True, fn=None), Rep"
        "rPlan.Field(name='stop_reason', kw_only=True, fn=None), ReprPlan.Field(name='stop_sequence', kw_only=True, fn="
        "None), ReprPlan.Field(name='usage', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='0015c87bf45f234d7348dcf89efe0412c3e6435c',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
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
        ('ommlds.backends.anthropic.protocol', 'Message'),
    ),
)
def _process_dataclass__0015c87bf45f234d7348dcf89efe0412c3e6435c():
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
                id=self.id,
                role=self.role,
                model=self.model,
                content=self.content,
                stop_reason=self.stop_reason,
                stop_sequence=self.stop_sequence,
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
                self.role == other.role and
                self.model == other.model and
                self.content == other.content and
                self.stop_reason == other.stop_reason and
                self.stop_sequence == other.stop_sequence and
                self.usage == other.usage
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'id',
            'role',
            'model',
            'content',
            'stop_reason',
            'stop_sequence',
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
            'role',
            'model',
            'content',
            'stop_reason',
            'stop_sequence',
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
                self.role,
                self.model,
                self.content,
                self.stop_reason,
                self.stop_sequence,
                self.usage,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            id: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            role: __dataclass__init__fields__1__annotation,
            model: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            content: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            stop_reason: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            stop_sequence: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
            usage: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'role', role)
            __dataclass__object_setattr(self, 'model', model)
            __dataclass__object_setattr(self, 'content', content)
            __dataclass__object_setattr(self, 'stop_reason', stop_reason)
            __dataclass__object_setattr(self, 'stop_sequence', stop_sequence)
            __dataclass__object_setattr(self, 'usage', usage)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"id={self.id!r}")
            parts.append(f"role={self.role!r}")
            parts.append(f"model={self.model!r}")
            parts.append(f"content={self.content!r}")
            parts.append(f"stop_reason={self.stop_reason!r}")
            parts.append(f"stop_sequence={self.stop_sequence!r}")
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
        "Plans(tup=(CopyPlan(fields=('model', 'messages', 'system', 'tools', 'temperature', 'max_tokens', 'stream', 'be"
        "tas', 'metadata')), EqPlan(fields=('model', 'messages', 'system', 'tools', 'temperature', 'max_tokens', 'strea"
        "m', 'betas', 'metadata')), FrozenPlan(fields=('model', 'messages', 'system', 'tools', 'temperature', 'max_toke"
        "ns', 'stream', 'betas', 'metadata'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('model'"
        ", 'messages', 'system', 'tools', 'temperature', 'max_tokens', 'stream', 'betas', 'metadata'), cache=False), In"
        "itPlan(fields=(InitPlan.Field(name='model', annotation=OpRef(name='init.fields.0.annotation'), default=None, d"
        "efault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, che"
        "ck_type=None), InitPlan.Field(name='messages', annotation=OpRef(name='init.fields.1.annotation'), default=None"
        ", default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, "
        "check_type=None), InitPlan.Field(name='system', annotation=OpRef(name='init.fields.2.annotation'), default=OpR"
        "ef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTAN"
        "CE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='tools', annotation=OpRef(name='init.fie"
        "lds.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=Fal"
        "se, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='temperat"
        "ure', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_"
        "factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type"
        "=None), InitPlan.Field(name='max_tokens', annotation=OpRef(name='init.fields.5.annotation'), default=OpRef(nam"
        "e='init.fields.5.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, co"
        "erce=None, validate=None, check_type=None), InitPlan.Field(name='stream', annotation=OpRef(name='init.fields.6"
        ".annotation'), default=OpRef(name='init.fields.6.default'), default_factory=None, init=True, override=False, f"
        "ield_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='betas', annot"
        "ation=OpRef(name='init.fields.7.annotation'), default=OpRef(name='init.fields.7.default'), default_factory=Non"
        "e, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), Ini"
        "tPlan.Field(name='metadata', annotation=OpRef(name='init.fields.8.annotation'), default=OpRef(name='init.field"
        "s.8.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, va"
        "lidate=None, check_type=None)), self_param='self', std_params=('model', 'messages'), kw_only_params=('system',"
        " 'tools', 'temperature', 'max_tokens', 'stream', 'betas', 'metadata'), frozen=True, slots=False, post_init_par"
        "ams=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='model', kw_only=False, fn=None)"
        ", ReprPlan.Field(name='messages', kw_only=False, fn=None), ReprPlan.Field(name='system', kw_only=True, fn=None"
        "), ReprPlan.Field(name='tools', kw_only=True, fn=None), ReprPlan.Field(name='temperature', kw_only=True, fn=No"
        "ne), ReprPlan.Field(name='max_tokens', kw_only=True, fn=None), ReprPlan.Field(name='stream', kw_only=True, fn="
        "None), ReprPlan.Field(name='betas', kw_only=True, fn=None), ReprPlan.Field(name='metadata', kw_only=True, fn=N"
        "one)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='0463f328955d284d5544ccd611d1fd041bc308ab',
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
        '__dataclass__init__fields__8__annotation',
        '__dataclass__init__fields__8__default',
    ),
    cls_names=(
        ('ommlds.backends.anthropic.protocol', 'MessagesRequest'),
    ),
)
def _process_dataclass__0463f328955d284d5544ccd611d1fd041bc308ab():
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
                model=self.model,
                messages=self.messages,
                system=self.system,
                tools=self.tools,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=self.stream,
                betas=self.betas,
                metadata=self.metadata,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
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
                self.messages == other.messages and
                self.system == other.system and
                self.tools == other.tools and
                self.temperature == other.temperature and
                self.max_tokens == other.max_tokens and
                self.stream == other.stream and
                self.betas == other.betas and
                self.metadata == other.metadata
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'model',
            'messages',
            'system',
            'tools',
            'temperature',
            'max_tokens',
            'stream',
            'betas',
            'metadata',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'messages',
            'system',
            'tools',
            'temperature',
            'max_tokens',
            'stream',
            'betas',
            'metadata',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                 or name in __dataclass___delattr_frozen_fields
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
                self.messages,
                self.system,
                self.tools,
                self.temperature,
                self.max_tokens,
                self.stream,
                self.betas,
                self.metadata,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            model: __dataclass__init__fields__0__annotation,
            messages: __dataclass__init__fields__1__annotation,
            *,
            system: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            tools: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            temperature: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            max_tokens: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
            stream: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
            betas: __dataclass__init__fields__7__annotation = __dataclass__init__fields__7__default,
            metadata: __dataclass__init__fields__8__annotation = __dataclass__init__fields__8__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'model', model)
            __dataclass__object_setattr(self, 'messages', messages)
            __dataclass__object_setattr(self, 'system', system)
            __dataclass__object_setattr(self, 'tools', tools)
            __dataclass__object_setattr(self, 'temperature', temperature)
            __dataclass__object_setattr(self, 'max_tokens', max_tokens)
            __dataclass__object_setattr(self, 'stream', stream)
            __dataclass__object_setattr(self, 'betas', betas)
            __dataclass__object_setattr(self, 'metadata', metadata)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"model={self.model!r}")
            parts.append(f"messages={self.messages!r}")
            parts.append(f"system={self.system!r}")
            parts.append(f"tools={self.tools!r}")
            parts.append(f"temperature={self.temperature!r}")
            parts.append(f"max_tokens={self.max_tokens!r}")
            parts.append(f"stream={self.stream!r}")
            parts.append(f"betas={self.betas!r}")
            parts.append(f"metadata={self.metadata!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('text', 'cache_control')), EqPlan(fields=('text', 'cache_control')), FrozenPlan(fi"
        "elds=('text', 'cache_control'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('text', 'cac"
        "he_control'), cache=False), InitPlan(fields=(InitPlan.Field(name='text', annotation=OpRef(name='init.fields.0."
        "annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, co"
        "erce=None, validate=None, check_type=None), InitPlan.Field(name='cache_control', annotation=OpRef(name='init.f"
        "ields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=F"
        "alse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_par"
        "ams=('text',), kw_only_params=('cache_control',), frozen=True, slots=False, post_init_params=None, init_fns=()"
        ", validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='text', kw_only=False, fn=None), ReprPlan.Field(name="
        "'cache_control', kw_only=True, fn=OpRef(name='repr.fns.1.fn'))), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='75e01105e84631f3c02c90f25368d746f1826680',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__repr__fns__1__fn',
    ),
    cls_names=(
        ('ommlds.backends.anthropic.protocol', 'Text'),
    ),
)
def _process_dataclass__75e01105e84631f3c02c90f25368d746f1826680():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
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
                text=self.text,
                cache_control=self.cache_control,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
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
                self.cache_control == other.cache_control
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'text',
            'cache_control',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'cache_control',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                 or name in __dataclass___delattr_frozen_fields
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
                self.cache_control,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            text: __dataclass__init__fields__0__annotation,
            *,
            cache_control: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'text', text)
            __dataclass__object_setattr(self, 'cache_control', cache_control)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"text={self.text!r}")
            if (s := __dataclass__repr__fns__1__fn(self.cache_control)) is not None:
                parts.append(f"cache_control={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('tool_use_id', 'content')), EqPlan(fields=('tool_use_id', 'content')), FrozenPlan("
        "fields=('tool_use_id', 'content'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('tool_use"
        "_id', 'content'), cache=False), InitPlan(fields=(InitPlan.Field(name='tool_use_id', annotation=OpRef(name='ini"
        "t.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.I"
        "NSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='content', annotation=OpRef(name='i"
        "nit.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType"
        ".INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=('tool_use_id', 'conte"
        "nt'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprP"
        "lan(fields=(ReprPlan.Field(name='tool_use_id', kw_only=False, fn=None), ReprPlan.Field(name='content', kw_only"
        "=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='c784ae3d44b6988e2459abc84ce5f705b6eca3b5',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('ommlds.backends.anthropic.protocol', 'ToolResult'),
    ),
)
def _process_dataclass__c784ae3d44b6988e2459abc84ce5f705b6eca3b5():
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
                tool_use_id=self.tool_use_id,
                content=self.content,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.tool_use_id == other.tool_use_id and
                self.content == other.content
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'tool_use_id',
            'content',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                 or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'tool_use_id',
            'content',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                 or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.tool_use_id,
                self.content,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            tool_use_id: __dataclass__init__fields__0__annotation,
            content: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'tool_use_id', tool_use_id)
            __dataclass__object_setattr(self, 'content', content)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"tool_use_id={self.tool_use_id!r}")
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
        "Plans(tup=(CopyPlan(fields=('name', 'description', 'input_schema')), EqPlan(fields=('name', 'description', 'in"
        "put_schema')), FrozenPlan(fields=('name', 'description', 'input_schema'), allow_dynamic_dunder_attrs=False), H"
        "ashPlan(action='add', fields=('name', 'description', 'input_schema'), cache=False), InitPlan(fields=(InitPlan."
        "Field(name='name', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init"
        "=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.F"
        "ield(name='description', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None"
        ", init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), Init"
        "Plan.Field(name='input_schema', annotation=OpRef(name='init.fields.2.annotation'), default=None, default_facto"
        "ry=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None"
        ")), self_param='self', std_params=('name', 'description', 'input_schema'), kw_only_params=(), frozen=True, slo"
        "ts=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='name', k"
        "w_only=False, fn=None), ReprPlan.Field(name='description', kw_only=False, fn=None), ReprPlan.Field(name='input"
        "_schema', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='a0bb088e6d220904a11db30de04c9b3fb2ddce42',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
    ),
    cls_names=(
        ('ommlds.backends.anthropic.protocol', 'ToolSpec'),
    ),
)
def _process_dataclass__a0bb088e6d220904a11db30de04c9b3fb2ddce42():
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
                description=self.description,
                input_schema=self.input_schema,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
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
                self.input_schema == other.input_schema
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'name',
            'description',
            'input_schema',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'input_schema',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                 or name in __dataclass___delattr_frozen_fields
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
                self.input_schema,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            name: __dataclass__init__fields__0__annotation,
            description: __dataclass__init__fields__1__annotation,
            input_schema: __dataclass__init__fields__2__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'description', description)
            __dataclass__object_setattr(self, 'input_schema', input_schema)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"name={self.name!r}")
            parts.append(f"description={self.description!r}")
            parts.append(f"input_schema={self.input_schema!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('id', 'name', 'input', 'cache_control')), EqPlan(fields=('id', 'name', 'input', 'c"
        "ache_control')), FrozenPlan(fields=('id', 'name', 'input', 'cache_control'), allow_dynamic_dunder_attrs=False)"
        ", HashPlan(action='add', fields=('id', 'name', 'input', 'cache_control'), cache=False), InitPlan(fields=(InitP"
        "lan.Field(name='id', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, in"
        "it=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan"
        ".Field(name='name', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, ini"
        "t=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan."
        "Field(name='input', annotation=OpRef(name='init.fields.2.annotation'), default=None, default_factory=None, ini"
        "t=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan."
        "Field(name='cache_control', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields"
        ".3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, val"
        "idate=None, check_type=None)), self_param='self', std_params=('id', 'name', 'input'), kw_only_params=('cache_c"
        "ontrol',), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(Re"
        "prPlan.Field(name='id', kw_only=False, fn=None), ReprPlan.Field(name='name', kw_only=False, fn=None), ReprPlan"
        ".Field(name='input', kw_only=False, fn=None), ReprPlan.Field(name='cache_control', kw_only=True, fn=OpRef(name"
        "='repr.fns.3.fn'))), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='51ac2f5bc2410c36bb667aa3a8f0ed87eb16813e',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
        '__dataclass__repr__fns__3__fn',
    ),
    cls_names=(
        ('ommlds.backends.anthropic.protocol', 'ToolUse'),
    ),
)
def _process_dataclass__51ac2f5bc2410c36bb667aa3a8f0ed87eb16813e():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__3__default,
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
                id=self.id,
                name=self.name,
                input=self.input,
                cache_control=self.cache_control,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
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
                self.input == other.input and
                self.cache_control == other.cache_control
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'id',
            'name',
            'input',
            'cache_control',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'input',
            'cache_control',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                 or name in __dataclass___delattr_frozen_fields
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
                self.input,
                self.cache_control,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            id: __dataclass__init__fields__0__annotation,
            name: __dataclass__init__fields__1__annotation,
            input: __dataclass__init__fields__2__annotation,
            *,
            cache_control: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'input', input)
            __dataclass__object_setattr(self, 'cache_control', cache_control)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"id={self.id!r}")
            parts.append(f"name={self.name!r}")
            parts.append(f"input={self.input!r}")
            if (s := __dataclass__repr__fns__3__fn(self.cache_control)) is not None:
                parts.append(f"cache_control={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('input_tokens', 'output_tokens', 'cache_creation_input_tokens', 'cache_read_input_"
        "tokens', 'cache_creation', 'service_tier')), EqPlan(fields=('input_tokens', 'output_tokens', 'cache_creation_i"
        "nput_tokens', 'cache_read_input_tokens', 'cache_creation', 'service_tier')), FrozenPlan(fields=('input_tokens'"
        ", 'output_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens', 'cache_creation', 'service_tier')"
        ", allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('input_tokens', 'output_tokens', 'cache_cr"
        "eation_input_tokens', 'cache_read_input_tokens', 'cache_creation', 'service_tier'), cache=False), InitPlan(fie"
        "lds=(InitPlan.Field(name='input_tokens', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name"
        "='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coe"
        "rce=None, validate=None, check_type=None), InitPlan.Field(name='output_tokens', annotation=OpRef(name='init.fi"
        "elds.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=Fa"
        "lse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='cache_c"
        "reation_input_tokens', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.de"
        "fault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate"
        "=None, check_type=None), InitPlan.Field(name='cache_read_input_tokens', annotation=OpRef(name='init.fields.3.a"
        "nnotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, fie"
        "ld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='cache_creation'"
        ", annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_fact"
        "ory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=Non"
        "e), InitPlan.Field(name='service_tier', annotation=OpRef(name='init.fields.5.annotation'), default=OpRef(name="
        "'init.fields.5.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coer"
        "ce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('input_tokens', '"
        "output_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens', 'cache_creation', 'service_tier'), f"
        "rozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field"
        "(name='input_tokens', kw_only=True, fn=None), ReprPlan.Field(name='output_tokens', kw_only=True, fn=None), Rep"
        "rPlan.Field(name='cache_creation_input_tokens', kw_only=True, fn=None), ReprPlan.Field(name='cache_read_input_"
        "tokens', kw_only=True, fn=None), ReprPlan.Field(name='cache_creation', kw_only=True, fn=None), ReprPlan.Field("
        "name='service_tier', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='a47ab44cf512908b7a879f4d6bafd7aa6de84f97',
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
        ('ommlds.backends.anthropic.protocol', 'Usage'),
    ),
)
def _process_dataclass__a47ab44cf512908b7a879f4d6bafd7aa6de84f97():
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
                input_tokens=self.input_tokens,
                output_tokens=self.output_tokens,
                cache_creation_input_tokens=self.cache_creation_input_tokens,
                cache_read_input_tokens=self.cache_read_input_tokens,
                cache_creation=self.cache_creation,
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
                self.input_tokens == other.input_tokens and
                self.output_tokens == other.output_tokens and
                self.cache_creation_input_tokens == other.cache_creation_input_tokens and
                self.cache_read_input_tokens == other.cache_read_input_tokens and
                self.cache_creation == other.cache_creation and
                self.service_tier == other.service_tier
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'input_tokens',
            'output_tokens',
            'cache_creation_input_tokens',
            'cache_read_input_tokens',
            'cache_creation',
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
            'input_tokens',
            'output_tokens',
            'cache_creation_input_tokens',
            'cache_read_input_tokens',
            'cache_creation',
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
                self.input_tokens,
                self.output_tokens,
                self.cache_creation_input_tokens,
                self.cache_read_input_tokens,
                self.cache_creation,
                self.service_tier,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            input_tokens: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            output_tokens: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            cache_creation_input_tokens: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            cache_read_input_tokens: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            cache_creation: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            service_tier: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'input_tokens', input_tokens)
            __dataclass__object_setattr(self, 'output_tokens', output_tokens)
            __dataclass__object_setattr(self, 'cache_creation_input_tokens', cache_creation_input_tokens)
            __dataclass__object_setattr(self, 'cache_read_input_tokens', cache_read_input_tokens)
            __dataclass__object_setattr(self, 'cache_creation', cache_creation)
            __dataclass__object_setattr(self, 'service_tier', service_tier)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"input_tokens={self.input_tokens!r}")
            parts.append(f"output_tokens={self.output_tokens!r}")
            parts.append(f"cache_creation_input_tokens={self.cache_creation_input_tokens!r}")
            parts.append(f"cache_read_input_tokens={self.cache_read_input_tokens!r}")
            parts.append(f"cache_creation={self.cache_creation!r}")
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
