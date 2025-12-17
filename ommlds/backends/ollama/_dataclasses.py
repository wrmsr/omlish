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
        "Plans(tup=(CopyPlan(fields=('model', 'stream', 'options', 'format', 'keep_alive')), EqPlan(fields=('model', 's"
        "tream', 'options', 'format', 'keep_alive')), FrozenPlan(fields=('model', 'stream', 'options', 'format', 'keep_"
        "alive'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('model', 'stream', 'options', 'form"
        "at', 'keep_alive'), cache=False), InitPlan(fields=(InitPlan.Field(name='model', annotation=OpRef(name='init.fi"
        "elds.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTA"
        "NCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='stream', annotation=OpRef(name='init.f"
        "ields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=F"
        "alse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='option"
        "s', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_fa"
        "ctory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=N"
        "one), InitPlan.Field(name='format', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='ini"
        "t.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=N"
        "one, validate=None, check_type=None), InitPlan.Field(name='keep_alive', annotation=OpRef(name='init.fields.4.a"
        "nnotation'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, override=False, fie"
        "ld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), k"
        "w_only_params=('model', 'stream', 'options', 'format', 'keep_alive'), frozen=True, slots=False, post_init_para"
        "ms=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='model', kw_only=True, fn=None), "
        "ReprPlan.Field(name='stream', kw_only=True, fn=None), ReprPlan.Field(name='options', kw_only=True, fn=None), R"
        "eprPlan.Field(name='format', kw_only=True, fn=None), ReprPlan.Field(name='keep_alive', kw_only=True, fn=None))"
        ", id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='845e863b03ee92ab7c5b27be3dfabfb54b948c5d',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
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
        ('ommlds.backends.ollama.protocol', 'BaseGenerateRequest'),
    ),
)
def _process_dataclass__845e863b03ee92ab7c5b27be3dfabfb54b948c5d():
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
                model=self.model,
                stream=self.stream,
                options=self.options,
                format=self.format,
                keep_alive=self.keep_alive,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
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
                self.stream == other.stream and
                self.options == other.options and
                self.format == other.format and
                self.keep_alive == other.keep_alive
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'model',
            'stream',
            'options',
            'format',
            'keep_alive',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'stream',
            'options',
            'format',
            'keep_alive',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                 or name in __dataclass___delattr_frozen_fields
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
                self.stream,
                self.options,
                self.format,
                self.keep_alive,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            model: __dataclass__init__fields__0__annotation,
            stream: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            options: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            format: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            keep_alive: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'model', model)
            __dataclass__object_setattr(self, 'stream', stream)
            __dataclass__object_setattr(self, 'options', options)
            __dataclass__object_setattr(self, 'format', format)
            __dataclass__object_setattr(self, 'keep_alive', keep_alive)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"model={self.model!r}")
            parts.append(f"stream={self.stream!r}")
            parts.append(f"options={self.options!r}")
            parts.append(f"format={self.format!r}")
            parts.append(f"keep_alive={self.keep_alive!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('model', 'created_at', 'done', 'done_reason', 'total_duration', 'load_duration', '"
        "prompt_eval_count', 'prompt_eval_duration', 'eval_count', 'eval_duration')), EqPlan(fields=('model', 'created_"
        "at', 'done', 'done_reason', 'total_duration', 'load_duration', 'prompt_eval_count', 'prompt_eval_duration', 'e"
        "val_count', 'eval_duration')), FrozenPlan(fields=('model', 'created_at', 'done', 'done_reason', 'total_duratio"
        "n', 'load_duration', 'prompt_eval_count', 'prompt_eval_duration', 'eval_count', 'eval_duration'), allow_dynami"
        "c_dunder_attrs=False), HashPlan(action='add', fields=('model', 'created_at', 'done', 'done_reason', 'total_dur"
        "ation', 'load_duration', 'prompt_eval_count', 'prompt_eval_duration', 'eval_count', 'eval_duration'), cache=Fa"
        "lse), InitPlan(fields=(InitPlan.Field(name='model', annotation=OpRef(name='init.fields.0.annotation'), default"
        "=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.IN"
        "STANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='created_at', annotation=OpRef(name="
        "'init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, ove"
        "rride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name="
        "'done', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), defaul"
        "t_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_ty"
        "pe=None), InitPlan.Field(name='done_reason', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef("
        "name='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE,"
        " coerce=None, validate=None, check_type=None), InitPlan.Field(name='total_duration', annotation=OpRef(name='in"
        "it.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, overri"
        "de=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='lo"
        "ad_duration', annotation=OpRef(name='init.fields.5.annotation'), default=OpRef(name='init.fields.5.default'), "
        "default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, ch"
        "eck_type=None), InitPlan.Field(name='prompt_eval_count', annotation=OpRef(name='init.fields.6.annotation'), de"
        "fault=OpRef(name='init.fields.6.default'), default_factory=None, init=True, override=False, field_type=FieldTy"
        "pe.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='prompt_eval_duration', annotat"
        "ion=OpRef(name='init.fields.7.annotation'), default=OpRef(name='init.fields.7.default'), default_factory=None,"
        " init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitP"
        "lan.Field(name='eval_count', annotation=OpRef(name='init.fields.8.annotation'), default=OpRef(name='init.field"
        "s.8.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, va"
        "lidate=None, check_type=None), InitPlan.Field(name='eval_duration', annotation=OpRef(name='init.fields.9.annot"
        "ation'), default=OpRef(name='init.fields.9.default'), default_factory=None, init=True, override=False, field_t"
        "ype=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_on"
        "ly_params=('model', 'created_at', 'done', 'done_reason', 'total_duration', 'load_duration', 'prompt_eval_count"
        "', 'prompt_eval_duration', 'eval_count', 'eval_duration'), frozen=True, slots=False, post_init_params=None, in"
        "it_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='model', kw_only=True, fn=None), ReprPlan.Fi"
        "eld(name='created_at', kw_only=True, fn=None), ReprPlan.Field(name='done', kw_only=True, fn=None), ReprPlan.Fi"
        "eld(name='done_reason', kw_only=True, fn=None), ReprPlan.Field(name='total_duration', kw_only=True, fn=None), "
        "ReprPlan.Field(name='load_duration', kw_only=True, fn=None), ReprPlan.Field(name='prompt_eval_count', kw_only="
        "True, fn=None), ReprPlan.Field(name='prompt_eval_duration', kw_only=True, fn=None), ReprPlan.Field(name='eval_"
        "count', kw_only=True, fn=None), ReprPlan.Field(name='eval_duration', kw_only=True, fn=None)), id=False, terse="
        "False, default_fn=None)))"
    ),
    plan_repr_sha1='205d41e5f20db210da1989c24f7b9e3bf1ebccd3',
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
        '__dataclass__init__fields__7__annotation',
        '__dataclass__init__fields__7__default',
        '__dataclass__init__fields__8__annotation',
        '__dataclass__init__fields__8__default',
        '__dataclass__init__fields__9__annotation',
        '__dataclass__init__fields__9__default',
    ),
    cls_names=(
        ('ommlds.backends.ollama.protocol', 'BaseGenerateResponse'),
    ),
)
def _process_dataclass__205d41e5f20db210da1989c24f7b9e3bf1ebccd3():
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
                model=self.model,
                created_at=self.created_at,
                done=self.done,
                done_reason=self.done_reason,
                total_duration=self.total_duration,
                load_duration=self.load_duration,
                prompt_eval_count=self.prompt_eval_count,
                prompt_eval_duration=self.prompt_eval_duration,
                eval_count=self.eval_count,
                eval_duration=self.eval_duration,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
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
                self.created_at == other.created_at and
                self.done == other.done and
                self.done_reason == other.done_reason and
                self.total_duration == other.total_duration and
                self.load_duration == other.load_duration and
                self.prompt_eval_count == other.prompt_eval_count and
                self.prompt_eval_duration == other.prompt_eval_duration and
                self.eval_count == other.eval_count and
                self.eval_duration == other.eval_duration
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'model',
            'created_at',
            'done',
            'done_reason',
            'total_duration',
            'load_duration',
            'prompt_eval_count',
            'prompt_eval_duration',
            'eval_count',
            'eval_duration',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'created_at',
            'done',
            'done_reason',
            'total_duration',
            'load_duration',
            'prompt_eval_count',
            'prompt_eval_duration',
            'eval_count',
            'eval_duration',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                 or name in __dataclass___delattr_frozen_fields
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
                self.created_at,
                self.done,
                self.done_reason,
                self.total_duration,
                self.load_duration,
                self.prompt_eval_count,
                self.prompt_eval_duration,
                self.eval_count,
                self.eval_duration,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            model: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            created_at: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            done: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            done_reason: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            total_duration: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            load_duration: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
            prompt_eval_count: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
            prompt_eval_duration: __dataclass__init__fields__7__annotation = __dataclass__init__fields__7__default,
            eval_count: __dataclass__init__fields__8__annotation = __dataclass__init__fields__8__default,
            eval_duration: __dataclass__init__fields__9__annotation = __dataclass__init__fields__9__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'model', model)
            __dataclass__object_setattr(self, 'created_at', created_at)
            __dataclass__object_setattr(self, 'done', done)
            __dataclass__object_setattr(self, 'done_reason', done_reason)
            __dataclass__object_setattr(self, 'total_duration', total_duration)
            __dataclass__object_setattr(self, 'load_duration', load_duration)
            __dataclass__object_setattr(self, 'prompt_eval_count', prompt_eval_count)
            __dataclass__object_setattr(self, 'prompt_eval_duration', prompt_eval_duration)
            __dataclass__object_setattr(self, 'eval_count', eval_count)
            __dataclass__object_setattr(self, 'eval_duration', eval_duration)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"model={self.model!r}")
            parts.append(f"created_at={self.created_at!r}")
            parts.append(f"done={self.done!r}")
            parts.append(f"done_reason={self.done_reason!r}")
            parts.append(f"total_duration={self.total_duration!r}")
            parts.append(f"load_duration={self.load_duration!r}")
            parts.append(f"prompt_eval_count={self.prompt_eval_count!r}")
            parts.append(f"prompt_eval_duration={self.prompt_eval_duration!r}")
            parts.append(f"eval_count={self.eval_count!r}")
            parts.append(f"eval_duration={self.eval_duration!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('model',)), EqPlan(fields=('model',)), FrozenPlan(fields=('model',), allow_dynamic"
        "_dunder_attrs=False), HashPlan(action='add', fields=('model',), cache=False), InitPlan(fields=(InitPlan.Field("
        "name='model', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True"
        ", override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='s"
        "elf', std_params=(), kw_only_params=('model',), frozen=True, slots=False, post_init_params=None, init_fns=(), "
        "validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='model', kw_only=True, fn=None),), id=False, terse=Fals"
        "e, default_fn=None)))"
    ),
    plan_repr_sha1='3310a48624d055c5c24df97f58e5c8f296523505',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.backends.ollama.protocol', 'BaseRequest'),
    ),
)
def _process_dataclass__3310a48624d055c5c24df97f58e5c8f296523505():
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
                self.model == other.model
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
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
                self.model,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            model: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'model', model)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
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
        "Plans(tup=(CopyPlan(fields=('model', 'stream')), EqPlan(fields=('model', 'stream')), FrozenPlan(fields=('model"
        "', 'stream'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('model', 'stream'), cache=Fals"
        "e), InitPlan(fields=(InitPlan.Field(name='model', annotation=OpRef(name='init.fields.0.annotation'), default=N"
        "one, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=Non"
        "e, check_type=None), InitPlan.Field(name='stream', annotation=OpRef(name='init.fields.1.annotation'), default="
        "OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INS"
        "TANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('model"
        "', 'stream'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields="
        "(ReprPlan.Field(name='model', kw_only=True, fn=None), ReprPlan.Field(name='stream', kw_only=True, fn=None)), i"
        "d=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='a0c68d946968391197d0c66f362ca6c3fed8d7a2',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.backends.ollama.protocol', 'BaseStreamableRequest'),
    ),
)
def _process_dataclass__a0c68d946968391197d0c66f362ca6c3fed8d7a2():
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
                model=self.model,
                stream=self.stream,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
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
                self.stream == other.stream
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'model',
            'stream',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'stream',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                 or name in __dataclass___delattr_frozen_fields
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
                self.stream,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            model: __dataclass__init__fields__0__annotation,
            stream: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'model', model)
            __dataclass__object_setattr(self, 'stream', stream)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"model={self.model!r}")
            parts.append(f"stream={self.stream!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('model', 'stream', 'options', 'format', 'keep_alive', 'messages', 'tools', 'think'"
        ")), EqPlan(fields=('model', 'stream', 'options', 'format', 'keep_alive', 'messages', 'tools', 'think')), Froze"
        "nPlan(fields=('model', 'stream', 'options', 'format', 'keep_alive', 'messages', 'tools', 'think'), allow_dynam"
        "ic_dunder_attrs=False), HashPlan(action='add', fields=('model', 'stream', 'options', 'format', 'keep_alive', '"
        "messages', 'tools', 'think'), cache=False), InitPlan(fields=(InitPlan.Field(name='model', annotation=OpRef(nam"
        "e='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=Field"
        "Type.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='stream', annotation=OpRef(na"
        "me='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, "
        "override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(na"
        "me='options', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), "
        "default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, ch"
        "eck_type=None), InitPlan.Field(name='format', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef"
        "(name='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE"
        ", coerce=None, validate=None, check_type=None), InitPlan.Field(name='keep_alive', annotation=OpRef(name='init."
        "fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, override="
        "False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='messa"
        "ges', annotation=OpRef(name='init.fields.5.annotation'), default=OpRef(name='init.fields.5.default'), default_"
        "factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type"
        "=None), InitPlan.Field(name='tools', annotation=OpRef(name='init.fields.6.annotation'), default=OpRef(name='in"
        "it.fields.6.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce="
        "None, validate=None, check_type=None), InitPlan.Field(name='think', annotation=OpRef(name='init.fields.7.annot"
        "ation'), default=OpRef(name='init.fields.7.default'), default_factory=None, init=True, override=False, field_t"
        "ype=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_on"
        "ly_params=('model', 'stream', 'options', 'format', 'keep_alive', 'messages', 'tools', 'think'), frozen=True, s"
        "lots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='model'"
        ", kw_only=True, fn=None), ReprPlan.Field(name='stream', kw_only=True, fn=None), ReprPlan.Field(name='options',"
        " kw_only=True, fn=None), ReprPlan.Field(name='format', kw_only=True, fn=None), ReprPlan.Field(name='keep_alive"
        "', kw_only=True, fn=None), ReprPlan.Field(name='messages', kw_only=True, fn=None), ReprPlan.Field(name='tools'"
        ", kw_only=True, fn=None), ReprPlan.Field(name='think', kw_only=True, fn=None)), id=False, terse=False, default"
        "_fn=OpRef(name='repr.default_fn'))))"
    ),
    plan_repr_sha1='82c5163f58a3474e87891ea77e9a516262229fcb',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
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
        '__dataclass__repr__default_fn',
    ),
    cls_names=(
        ('ommlds.backends.ollama.protocol', 'ChatRequest'),
    ),
)
def _process_dataclass__82c5163f58a3474e87891ea77e9a516262229fcb():
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
                model=self.model,
                stream=self.stream,
                options=self.options,
                format=self.format,
                keep_alive=self.keep_alive,
                messages=self.messages,
                tools=self.tools,
                think=self.think,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
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
                self.stream == other.stream and
                self.options == other.options and
                self.format == other.format and
                self.keep_alive == other.keep_alive and
                self.messages == other.messages and
                self.tools == other.tools and
                self.think == other.think
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'model',
            'stream',
            'options',
            'format',
            'keep_alive',
            'messages',
            'tools',
            'think',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'stream',
            'options',
            'format',
            'keep_alive',
            'messages',
            'tools',
            'think',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                 or name in __dataclass___delattr_frozen_fields
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
                self.stream,
                self.options,
                self.format,
                self.keep_alive,
                self.messages,
                self.tools,
                self.think,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            model: __dataclass__init__fields__0__annotation,
            stream: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            options: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            format: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            keep_alive: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            messages: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
            tools: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
            think: __dataclass__init__fields__7__annotation = __dataclass__init__fields__7__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'model', model)
            __dataclass__object_setattr(self, 'stream', stream)
            __dataclass__object_setattr(self, 'options', options)
            __dataclass__object_setattr(self, 'format', format)
            __dataclass__object_setattr(self, 'keep_alive', keep_alive)
            __dataclass__object_setattr(self, 'messages', messages)
            __dataclass__object_setattr(self, 'tools', tools)
            __dataclass__object_setattr(self, 'think', think)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__default_fn(self.model)) is not None:
                parts.append(f"model={s}")
            if (s := __dataclass__repr__default_fn(self.stream)) is not None:
                parts.append(f"stream={s}")
            if (s := __dataclass__repr__default_fn(self.options)) is not None:
                parts.append(f"options={s}")
            if (s := __dataclass__repr__default_fn(self.format)) is not None:
                parts.append(f"format={s}")
            if (s := __dataclass__repr__default_fn(self.keep_alive)) is not None:
                parts.append(f"keep_alive={s}")
            if (s := __dataclass__repr__default_fn(self.messages)) is not None:
                parts.append(f"messages={s}")
            if (s := __dataclass__repr__default_fn(self.tools)) is not None:
                parts.append(f"tools={s}")
            if (s := __dataclass__repr__default_fn(self.think)) is not None:
                parts.append(f"think={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('model', 'created_at', 'done', 'done_reason', 'total_duration', 'load_duration', '"
        "prompt_eval_count', 'prompt_eval_duration', 'eval_count', 'eval_duration', 'message')), EqPlan(fields=('model'"
        ", 'created_at', 'done', 'done_reason', 'total_duration', 'load_duration', 'prompt_eval_count', 'prompt_eval_du"
        "ration', 'eval_count', 'eval_duration', 'message')), FrozenPlan(fields=('model', 'created_at', 'done', 'done_r"
        "eason', 'total_duration', 'load_duration', 'prompt_eval_count', 'prompt_eval_duration', 'eval_count', 'eval_du"
        "ration', 'message'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('model', 'created_at', "
        "'done', 'done_reason', 'total_duration', 'load_duration', 'prompt_eval_count', 'prompt_eval_duration', 'eval_c"
        "ount', 'eval_duration', 'message'), cache=False), InitPlan(fields=(InitPlan.Field(name='model', annotation=OpR"
        "ef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'), default_factory=None, init=T"
        "rue, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fie"
        "ld(name='created_at', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.def"
        "ault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate="
        "None, check_type=None), InitPlan.Field(name='done', annotation=OpRef(name='init.fields.2.annotation'), default"
        "=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.IN"
        "STANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='done_reason', annotation=OpRef(name"
        "='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, ov"
        "erride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name"
        "='total_duration', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.defaul"
        "t'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=Non"
        "e, check_type=None), InitPlan.Field(name='load_duration', annotation=OpRef(name='init.fields.5.annotation'), d"
        "efault=OpRef(name='init.fields.5.default'), default_factory=None, init=True, override=False, field_type=FieldT"
        "ype.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='prompt_eval_count', annotatio"
        "n=OpRef(name='init.fields.6.annotation'), default=OpRef(name='init.fields.6.default'), default_factory=None, i"
        "nit=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPla"
        "n.Field(name='prompt_eval_duration', annotation=OpRef(name='init.fields.7.annotation'), default=OpRef(name='in"
        "it.fields.7.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce="
        "None, validate=None, check_type=None), InitPlan.Field(name='eval_count', annotation=OpRef(name='init.fields.8."
        "annotation'), default=OpRef(name='init.fields.8.default'), default_factory=None, init=True, override=False, fi"
        "eld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='eval_duration'"
        ", annotation=OpRef(name='init.fields.9.annotation'), default=OpRef(name='init.fields.9.default'), default_fact"
        "ory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=Non"
        "e), InitPlan.Field(name='message', annotation=OpRef(name='init.fields.10.annotation'), default=None, default_f"
        "actory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type="
        "None)), self_param='self', std_params=(), kw_only_params=('model', 'created_at', 'done', 'done_reason', 'total"
        "_duration', 'load_duration', 'prompt_eval_count', 'prompt_eval_duration', 'eval_count', 'eval_duration', 'mess"
        "age'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPl"
        "an.Field(name='model', kw_only=True, fn=None), ReprPlan.Field(name='created_at', kw_only=True, fn=None), ReprP"
        "lan.Field(name='done', kw_only=True, fn=None), ReprPlan.Field(name='done_reason', kw_only=True, fn=None), Repr"
        "Plan.Field(name='total_duration', kw_only=True, fn=None), ReprPlan.Field(name='load_duration', kw_only=True, f"
        "n=None), ReprPlan.Field(name='prompt_eval_count', kw_only=True, fn=None), ReprPlan.Field(name='prompt_eval_dur"
        "ation', kw_only=True, fn=None), ReprPlan.Field(name='eval_count', kw_only=True, fn=None), ReprPlan.Field(name="
        "'eval_duration', kw_only=True, fn=None), ReprPlan.Field(name='message', kw_only=True, fn=None)), id=False, ter"
        "se=False, default_fn=OpRef(name='repr.default_fn'))))"
    ),
    plan_repr_sha1='f14f2c9137552599b1b611852176514b259abb93',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__10__annotation',
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
        '__dataclass__repr__default_fn',
    ),
    cls_names=(
        ('ommlds.backends.ollama.protocol', 'ChatResponse'),
    ),
)
def _process_dataclass__f14f2c9137552599b1b611852176514b259abb93():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__10__annotation,
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
                model=self.model,
                created_at=self.created_at,
                done=self.done,
                done_reason=self.done_reason,
                total_duration=self.total_duration,
                load_duration=self.load_duration,
                prompt_eval_count=self.prompt_eval_count,
                prompt_eval_duration=self.prompt_eval_duration,
                eval_count=self.eval_count,
                eval_duration=self.eval_duration,
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
                self.model == other.model and
                self.created_at == other.created_at and
                self.done == other.done and
                self.done_reason == other.done_reason and
                self.total_duration == other.total_duration and
                self.load_duration == other.load_duration and
                self.prompt_eval_count == other.prompt_eval_count and
                self.prompt_eval_duration == other.prompt_eval_duration and
                self.eval_count == other.eval_count and
                self.eval_duration == other.eval_duration and
                self.message == other.message
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'model',
            'created_at',
            'done',
            'done_reason',
            'total_duration',
            'load_duration',
            'prompt_eval_count',
            'prompt_eval_duration',
            'eval_count',
            'eval_duration',
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
            'model',
            'created_at',
            'done',
            'done_reason',
            'total_duration',
            'load_duration',
            'prompt_eval_count',
            'prompt_eval_duration',
            'eval_count',
            'eval_duration',
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
                self.model,
                self.created_at,
                self.done,
                self.done_reason,
                self.total_duration,
                self.load_duration,
                self.prompt_eval_count,
                self.prompt_eval_duration,
                self.eval_count,
                self.eval_duration,
                self.message,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            model: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            created_at: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            done: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            done_reason: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            total_duration: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            load_duration: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
            prompt_eval_count: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
            prompt_eval_duration: __dataclass__init__fields__7__annotation = __dataclass__init__fields__7__default,
            eval_count: __dataclass__init__fields__8__annotation = __dataclass__init__fields__8__default,
            eval_duration: __dataclass__init__fields__9__annotation = __dataclass__init__fields__9__default,
            message: __dataclass__init__fields__10__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'model', model)
            __dataclass__object_setattr(self, 'created_at', created_at)
            __dataclass__object_setattr(self, 'done', done)
            __dataclass__object_setattr(self, 'done_reason', done_reason)
            __dataclass__object_setattr(self, 'total_duration', total_duration)
            __dataclass__object_setattr(self, 'load_duration', load_duration)
            __dataclass__object_setattr(self, 'prompt_eval_count', prompt_eval_count)
            __dataclass__object_setattr(self, 'prompt_eval_duration', prompt_eval_duration)
            __dataclass__object_setattr(self, 'eval_count', eval_count)
            __dataclass__object_setattr(self, 'eval_duration', eval_duration)
            __dataclass__object_setattr(self, 'message', message)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__default_fn(self.model)) is not None:
                parts.append(f"model={s}")
            if (s := __dataclass__repr__default_fn(self.created_at)) is not None:
                parts.append(f"created_at={s}")
            if (s := __dataclass__repr__default_fn(self.done)) is not None:
                parts.append(f"done={s}")
            if (s := __dataclass__repr__default_fn(self.done_reason)) is not None:
                parts.append(f"done_reason={s}")
            if (s := __dataclass__repr__default_fn(self.total_duration)) is not None:
                parts.append(f"total_duration={s}")
            if (s := __dataclass__repr__default_fn(self.load_duration)) is not None:
                parts.append(f"load_duration={s}")
            if (s := __dataclass__repr__default_fn(self.prompt_eval_count)) is not None:
                parts.append(f"prompt_eval_count={s}")
            if (s := __dataclass__repr__default_fn(self.prompt_eval_duration)) is not None:
                parts.append(f"prompt_eval_duration={s}")
            if (s := __dataclass__repr__default_fn(self.eval_count)) is not None:
                parts.append(f"eval_count={s}")
            if (s := __dataclass__repr__default_fn(self.eval_duration)) is not None:
                parts.append(f"eval_duration={s}")
            if (s := __dataclass__repr__default_fn(self.message)) is not None:
                parts.append(f"message={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('model', 'stream', 'options', 'format', 'keep_alive', 'prompt', 'suffix', 'system'"
        ", 'template', 'context', 'raw', 'images', 'think')), EqPlan(fields=('model', 'stream', 'options', 'format', 'k"
        "eep_alive', 'prompt', 'suffix', 'system', 'template', 'context', 'raw', 'images', 'think')), FrozenPlan(fields"
        "=('model', 'stream', 'options', 'format', 'keep_alive', 'prompt', 'suffix', 'system', 'template', 'context', '"
        "raw', 'images', 'think'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('model', 'stream',"
        " 'options', 'format', 'keep_alive', 'prompt', 'suffix', 'system', 'template', 'context', 'raw', 'images', 'thi"
        "nk'), cache=False), InitPlan(fields=(InitPlan.Field(name='model', annotation=OpRef(name='init.fields.0.annotat"
        "ion'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=No"
        "ne, validate=None, check_type=None), InitPlan.Field(name='stream', annotation=OpRef(name='init.fields.1.annota"
        "tion'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_ty"
        "pe=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='options', annotation"
        "=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, in"
        "it=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan"
        ".Field(name='format', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.def"
        "ault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate="
        "None, check_type=None), InitPlan.Field(name='keep_alive', annotation=OpRef(name='init.fields.4.annotation'), d"
        "efault=OpRef(name='init.fields.4.default'), default_factory=None, init=True, override=False, field_type=FieldT"
        "ype.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='prompt', annotation=OpRef(nam"
        "e='init.fields.5.annotation'), default=OpRef(name='init.fields.5.default'), default_factory=None, init=True, o"
        "verride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(nam"
        "e='suffix', annotation=OpRef(name='init.fields.6.annotation'), default=OpRef(name='init.fields.6.default'), de"
        "fault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, chec"
        "k_type=None), InitPlan.Field(name='system', annotation=OpRef(name='init.fields.7.annotation'), default=OpRef(n"
        "ame='init.fields.7.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, "
        "coerce=None, validate=None, check_type=None), InitPlan.Field(name='template', annotation=OpRef(name='init.fiel"
        "ds.8.annotation'), default=OpRef(name='init.fields.8.default'), default_factory=None, init=True, override=Fals"
        "e, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='context',"
        " annotation=OpRef(name='init.fields.9.annotation'), default=OpRef(name='init.fields.9.default'), default_facto"
        "ry=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None"
        "), InitPlan.Field(name='raw', annotation=OpRef(name='init.fields.10.annotation'), default=OpRef(name='init.fie"
        "lds.10.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None,"
        " validate=None, check_type=None), InitPlan.Field(name='images', annotation=OpRef(name='init.fields.11.annotati"
        "on'), default=OpRef(name='init.fields.11.default'), default_factory=None, init=True, override=False, field_typ"
        "e=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='think', annotation=Op"
        "Ref(name='init.fields.12.annotation'), default=OpRef(name='init.fields.12.default'), default_factory=None, ini"
        "t=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_par"
        "am='self', std_params=(), kw_only_params=('model', 'stream', 'options', 'format', 'keep_alive', 'prompt', 'suf"
        "fix', 'system', 'template', 'context', 'raw', 'images', 'think'), frozen=True, slots=False, post_init_params=N"
        "one, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='model', kw_only=True, fn=None), Repr"
        "Plan.Field(name='stream', kw_only=True, fn=None), ReprPlan.Field(name='options', kw_only=True, fn=None), ReprP"
        "lan.Field(name='format', kw_only=True, fn=None), ReprPlan.Field(name='keep_alive', kw_only=True, fn=None), Rep"
        "rPlan.Field(name='prompt', kw_only=True, fn=None), ReprPlan.Field(name='suffix', kw_only=True, fn=None), ReprP"
        "lan.Field(name='system', kw_only=True, fn=None), ReprPlan.Field(name='template', kw_only=True, fn=None), ReprP"
        "lan.Field(name='context', kw_only=True, fn=None), ReprPlan.Field(name='raw', kw_only=True, fn=None), ReprPlan."
        "Field(name='images', kw_only=True, fn=None), ReprPlan.Field(name='think', kw_only=True, fn=None)), id=False, t"
        "erse=False, default_fn=OpRef(name='repr.default_fn'))))"
    ),
    plan_repr_sha1='e8b909b51aff3e1fd8203ee672cfc0bab5067233',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
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
        '__dataclass__repr__default_fn',
    ),
    cls_names=(
        ('ommlds.backends.ollama.protocol', 'GenerateRequest'),
    ),
)
def _process_dataclass__e8b909b51aff3e1fd8203ee672cfc0bab5067233():
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
                model=self.model,
                stream=self.stream,
                options=self.options,
                format=self.format,
                keep_alive=self.keep_alive,
                prompt=self.prompt,
                suffix=self.suffix,
                system=self.system,
                template=self.template,
                context=self.context,
                raw=self.raw,
                images=self.images,
                think=self.think,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
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
                self.stream == other.stream and
                self.options == other.options and
                self.format == other.format and
                self.keep_alive == other.keep_alive and
                self.prompt == other.prompt and
                self.suffix == other.suffix and
                self.system == other.system and
                self.template == other.template and
                self.context == other.context and
                self.raw == other.raw and
                self.images == other.images and
                self.think == other.think
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'model',
            'stream',
            'options',
            'format',
            'keep_alive',
            'prompt',
            'suffix',
            'system',
            'template',
            'context',
            'raw',
            'images',
            'think',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'stream',
            'options',
            'format',
            'keep_alive',
            'prompt',
            'suffix',
            'system',
            'template',
            'context',
            'raw',
            'images',
            'think',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                 or name in __dataclass___delattr_frozen_fields
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
                self.stream,
                self.options,
                self.format,
                self.keep_alive,
                self.prompt,
                self.suffix,
                self.system,
                self.template,
                self.context,
                self.raw,
                self.images,
                self.think,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            model: __dataclass__init__fields__0__annotation,
            stream: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            options: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            format: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            keep_alive: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            prompt: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
            suffix: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
            system: __dataclass__init__fields__7__annotation = __dataclass__init__fields__7__default,
            template: __dataclass__init__fields__8__annotation = __dataclass__init__fields__8__default,
            context: __dataclass__init__fields__9__annotation = __dataclass__init__fields__9__default,
            raw: __dataclass__init__fields__10__annotation = __dataclass__init__fields__10__default,
            images: __dataclass__init__fields__11__annotation = __dataclass__init__fields__11__default,
            think: __dataclass__init__fields__12__annotation = __dataclass__init__fields__12__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'model', model)
            __dataclass__object_setattr(self, 'stream', stream)
            __dataclass__object_setattr(self, 'options', options)
            __dataclass__object_setattr(self, 'format', format)
            __dataclass__object_setattr(self, 'keep_alive', keep_alive)
            __dataclass__object_setattr(self, 'prompt', prompt)
            __dataclass__object_setattr(self, 'suffix', suffix)
            __dataclass__object_setattr(self, 'system', system)
            __dataclass__object_setattr(self, 'template', template)
            __dataclass__object_setattr(self, 'context', context)
            __dataclass__object_setattr(self, 'raw', raw)
            __dataclass__object_setattr(self, 'images', images)
            __dataclass__object_setattr(self, 'think', think)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__default_fn(self.model)) is not None:
                parts.append(f"model={s}")
            if (s := __dataclass__repr__default_fn(self.stream)) is not None:
                parts.append(f"stream={s}")
            if (s := __dataclass__repr__default_fn(self.options)) is not None:
                parts.append(f"options={s}")
            if (s := __dataclass__repr__default_fn(self.format)) is not None:
                parts.append(f"format={s}")
            if (s := __dataclass__repr__default_fn(self.keep_alive)) is not None:
                parts.append(f"keep_alive={s}")
            if (s := __dataclass__repr__default_fn(self.prompt)) is not None:
                parts.append(f"prompt={s}")
            if (s := __dataclass__repr__default_fn(self.suffix)) is not None:
                parts.append(f"suffix={s}")
            if (s := __dataclass__repr__default_fn(self.system)) is not None:
                parts.append(f"system={s}")
            if (s := __dataclass__repr__default_fn(self.template)) is not None:
                parts.append(f"template={s}")
            if (s := __dataclass__repr__default_fn(self.context)) is not None:
                parts.append(f"context={s}")
            if (s := __dataclass__repr__default_fn(self.raw)) is not None:
                parts.append(f"raw={s}")
            if (s := __dataclass__repr__default_fn(self.images)) is not None:
                parts.append(f"images={s}")
            if (s := __dataclass__repr__default_fn(self.think)) is not None:
                parts.append(f"think={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('model', 'created_at', 'done', 'done_reason', 'total_duration', 'load_duration', '"
        "prompt_eval_count', 'prompt_eval_duration', 'eval_count', 'eval_duration', 'response', 'thinking', 'context'))"
        ", EqPlan(fields=('model', 'created_at', 'done', 'done_reason', 'total_duration', 'load_duration', 'prompt_eval"
        "_count', 'prompt_eval_duration', 'eval_count', 'eval_duration', 'response', 'thinking', 'context')), FrozenPla"
        "n(fields=('model', 'created_at', 'done', 'done_reason', 'total_duration', 'load_duration', 'prompt_eval_count'"
        ", 'prompt_eval_duration', 'eval_count', 'eval_duration', 'response', 'thinking', 'context'), allow_dynamic_dun"
        "der_attrs=False), HashPlan(action='add', fields=('model', 'created_at', 'done', 'done_reason', 'total_duration"
        "', 'load_duration', 'prompt_eval_count', 'prompt_eval_duration', 'eval_count', 'eval_duration', 'response', 't"
        "hinking', 'context'), cache=False), InitPlan(fields=(InitPlan.Field(name='model', annotation=OpRef(name='init."
        "fields.0.annotation'), default=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override="
        "False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='creat"
        "ed_at', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), defaul"
        "t_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_ty"
        "pe=None), InitPlan.Field(name='done', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='i"
        "nit.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce"
        "=None, validate=None, check_type=None), InitPlan.Field(name='done_reason', annotation=OpRef(name='init.fields."
        "3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, "
        "field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='total_durati"
        "on', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_f"
        "actory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type="
        "None), InitPlan.Field(name='load_duration', annotation=OpRef(name='init.fields.5.annotation'), default=OpRef(n"
        "ame='init.fields.5.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, "
        "coerce=None, validate=None, check_type=None), InitPlan.Field(name='prompt_eval_count', annotation=OpRef(name='"
        "init.fields.6.annotation'), default=OpRef(name='init.fields.6.default'), default_factory=None, init=True, over"
        "ride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='"
        "prompt_eval_duration', annotation=OpRef(name='init.fields.7.annotation'), default=OpRef(name='init.fields.7.de"
        "fault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate"
        "=None, check_type=None), InitPlan.Field(name='eval_count', annotation=OpRef(name='init.fields.8.annotation'), "
        "default=OpRef(name='init.fields.8.default'), default_factory=None, init=True, override=False, field_type=Field"
        "Type.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='eval_duration', annotation=O"
        "pRef(name='init.fields.9.annotation'), default=OpRef(name='init.fields.9.default'), default_factory=None, init"
        "=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.F"
        "ield(name='response', annotation=OpRef(name='init.fields.10.annotation'), default=None, default_factory=None, "
        "init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPl"
        "an.Field(name='thinking', annotation=OpRef(name='init.fields.11.annotation'), default=OpRef(name='init.fields."
        "11.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, val"
        "idate=None, check_type=None), InitPlan.Field(name='context', annotation=OpRef(name='init.fields.12.annotation'"
        "), default=OpRef(name='init.fields.12.default'), default_factory=None, init=True, override=False, field_type=F"
        "ieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_pa"
        "rams=('model', 'created_at', 'done', 'done_reason', 'total_duration', 'load_duration', 'prompt_eval_count', 'p"
        "rompt_eval_duration', 'eval_count', 'eval_duration', 'response', 'thinking', 'context'), frozen=True, slots=Fa"
        "lse, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='model', kw_on"
        "ly=True, fn=None), ReprPlan.Field(name='created_at', kw_only=True, fn=None), ReprPlan.Field(name='done', kw_on"
        "ly=True, fn=None), ReprPlan.Field(name='done_reason', kw_only=True, fn=None), ReprPlan.Field(name='total_durat"
        "ion', kw_only=True, fn=None), ReprPlan.Field(name='load_duration', kw_only=True, fn=None), ReprPlan.Field(name"
        "='prompt_eval_count', kw_only=True, fn=None), ReprPlan.Field(name='prompt_eval_duration', kw_only=True, fn=Non"
        "e), ReprPlan.Field(name='eval_count', kw_only=True, fn=None), ReprPlan.Field(name='eval_duration', kw_only=Tru"
        "e, fn=None), ReprPlan.Field(name='response', kw_only=True, fn=None), ReprPlan.Field(name='thinking', kw_only=T"
        "rue, fn=None), ReprPlan.Field(name='context', kw_only=True, fn=None)), id=False, terse=False, default_fn=OpRef"
        "(name='repr.default_fn'))))"
    ),
    plan_repr_sha1='d4de027591ccf1da84a98a2734b94a36c6340c4b',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__10__annotation',
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
        '__dataclass__repr__default_fn',
    ),
    cls_names=(
        ('ommlds.backends.ollama.protocol', 'GenerateResponse'),
    ),
)
def _process_dataclass__d4de027591ccf1da84a98a2734b94a36c6340c4b():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__10__annotation,
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
                model=self.model,
                created_at=self.created_at,
                done=self.done,
                done_reason=self.done_reason,
                total_duration=self.total_duration,
                load_duration=self.load_duration,
                prompt_eval_count=self.prompt_eval_count,
                prompt_eval_duration=self.prompt_eval_duration,
                eval_count=self.eval_count,
                eval_duration=self.eval_duration,
                response=self.response,
                thinking=self.thinking,
                context=self.context,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
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
                self.created_at == other.created_at and
                self.done == other.done and
                self.done_reason == other.done_reason and
                self.total_duration == other.total_duration and
                self.load_duration == other.load_duration and
                self.prompt_eval_count == other.prompt_eval_count and
                self.prompt_eval_duration == other.prompt_eval_duration and
                self.eval_count == other.eval_count and
                self.eval_duration == other.eval_duration and
                self.response == other.response and
                self.thinking == other.thinking and
                self.context == other.context
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'model',
            'created_at',
            'done',
            'done_reason',
            'total_duration',
            'load_duration',
            'prompt_eval_count',
            'prompt_eval_duration',
            'eval_count',
            'eval_duration',
            'response',
            'thinking',
            'context',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'created_at',
            'done',
            'done_reason',
            'total_duration',
            'load_duration',
            'prompt_eval_count',
            'prompt_eval_duration',
            'eval_count',
            'eval_duration',
            'response',
            'thinking',
            'context',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                 or name in __dataclass___delattr_frozen_fields
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
                self.created_at,
                self.done,
                self.done_reason,
                self.total_duration,
                self.load_duration,
                self.prompt_eval_count,
                self.prompt_eval_duration,
                self.eval_count,
                self.eval_duration,
                self.response,
                self.thinking,
                self.context,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            model: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            created_at: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            done: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            done_reason: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            total_duration: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            load_duration: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
            prompt_eval_count: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
            prompt_eval_duration: __dataclass__init__fields__7__annotation = __dataclass__init__fields__7__default,
            eval_count: __dataclass__init__fields__8__annotation = __dataclass__init__fields__8__default,
            eval_duration: __dataclass__init__fields__9__annotation = __dataclass__init__fields__9__default,
            response: __dataclass__init__fields__10__annotation,
            thinking: __dataclass__init__fields__11__annotation = __dataclass__init__fields__11__default,
            context: __dataclass__init__fields__12__annotation = __dataclass__init__fields__12__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'model', model)
            __dataclass__object_setattr(self, 'created_at', created_at)
            __dataclass__object_setattr(self, 'done', done)
            __dataclass__object_setattr(self, 'done_reason', done_reason)
            __dataclass__object_setattr(self, 'total_duration', total_duration)
            __dataclass__object_setattr(self, 'load_duration', load_duration)
            __dataclass__object_setattr(self, 'prompt_eval_count', prompt_eval_count)
            __dataclass__object_setattr(self, 'prompt_eval_duration', prompt_eval_duration)
            __dataclass__object_setattr(self, 'eval_count', eval_count)
            __dataclass__object_setattr(self, 'eval_duration', eval_duration)
            __dataclass__object_setattr(self, 'response', response)
            __dataclass__object_setattr(self, 'thinking', thinking)
            __dataclass__object_setattr(self, 'context', context)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__default_fn(self.model)) is not None:
                parts.append(f"model={s}")
            if (s := __dataclass__repr__default_fn(self.created_at)) is not None:
                parts.append(f"created_at={s}")
            if (s := __dataclass__repr__default_fn(self.done)) is not None:
                parts.append(f"done={s}")
            if (s := __dataclass__repr__default_fn(self.done_reason)) is not None:
                parts.append(f"done_reason={s}")
            if (s := __dataclass__repr__default_fn(self.total_duration)) is not None:
                parts.append(f"total_duration={s}")
            if (s := __dataclass__repr__default_fn(self.load_duration)) is not None:
                parts.append(f"load_duration={s}")
            if (s := __dataclass__repr__default_fn(self.prompt_eval_count)) is not None:
                parts.append(f"prompt_eval_count={s}")
            if (s := __dataclass__repr__default_fn(self.prompt_eval_duration)) is not None:
                parts.append(f"prompt_eval_duration={s}")
            if (s := __dataclass__repr__default_fn(self.eval_count)) is not None:
                parts.append(f"eval_count={s}")
            if (s := __dataclass__repr__default_fn(self.eval_duration)) is not None:
                parts.append(f"eval_duration={s}")
            if (s := __dataclass__repr__default_fn(self.response)) is not None:
                parts.append(f"response={s}")
            if (s := __dataclass__repr__default_fn(self.thinking)) is not None:
                parts.append(f"thinking={s}")
            if (s := __dataclass__repr__default_fn(self.context)) is not None:
                parts.append(f"context={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('role', 'content', 'thinking', 'images', 'tool_name', 'tool_calls')), EqPlan(field"
        "s=('role', 'content', 'thinking', 'images', 'tool_name', 'tool_calls')), FrozenPlan(fields=('role', 'content',"
        " 'thinking', 'images', 'tool_name', 'tool_calls'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', f"
        "ields=('role', 'content', 'thinking', 'images', 'tool_name', 'tool_calls'), cache=False), InitPlan(fields=(Ini"
        "tPlan.Field(name='role', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None"
        ", init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), Init"
        "Plan.Field(name='content', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields."
        "1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, vali"
        "date=None, check_type=None), InitPlan.Field(name='thinking', annotation=OpRef(name='init.fields.2.annotation')"
        ", default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=Fie"
        "ldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='images', annotation=OpRef("
        "name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True"
        ", override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field("
        "name='tool_name', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default"
        "'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None"
        ", check_type=None), InitPlan.Field(name='tool_calls', annotation=OpRef(name='init.fields.5.annotation'), defau"
        "lt=OpRef(name='init.fields.5.default'), default_factory=None, init=True, override=False, field_type=FieldType."
        "INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('ro"
        "le', 'content', 'thinking', 'images', 'tool_name', 'tool_calls'), frozen=True, slots=False, post_init_params=N"
        "one, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='role', kw_only=True, fn=None), ReprP"
        "lan.Field(name='content', kw_only=True, fn=None), ReprPlan.Field(name='thinking', kw_only=True, fn=None), Repr"
        "Plan.Field(name='images', kw_only=True, fn=None), ReprPlan.Field(name='tool_name', kw_only=True, fn=None), Rep"
        "rPlan.Field(name='tool_calls', kw_only=True, fn=None)), id=False, terse=False, default_fn=OpRef(name='repr.def"
        "ault_fn'))))"
    ),
    plan_repr_sha1='5ed26fc5132f873daeaffa682785bd1b47768acb',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
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
        ('ommlds.backends.ollama.protocol', 'Message'),
    ),
)
def _process_dataclass__5ed26fc5132f873daeaffa682785bd1b47768acb():
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
                role=self.role,
                content=self.content,
                thinking=self.thinking,
                images=self.images,
                tool_name=self.tool_name,
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
                self.role == other.role and
                self.content == other.content and
                self.thinking == other.thinking and
                self.images == other.images and
                self.tool_name == other.tool_name and
                self.tool_calls == other.tool_calls
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'role',
            'content',
            'thinking',
            'images',
            'tool_name',
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
            'role',
            'content',
            'thinking',
            'images',
            'tool_name',
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
                self.role,
                self.content,
                self.thinking,
                self.images,
                self.tool_name,
                self.tool_calls,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            role: __dataclass__init__fields__0__annotation,
            content: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            thinking: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            images: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            tool_name: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            tool_calls: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'role', role)
            __dataclass__object_setattr(self, 'content', content)
            __dataclass__object_setattr(self, 'thinking', thinking)
            __dataclass__object_setattr(self, 'images', images)
            __dataclass__object_setattr(self, 'tool_name', tool_name)
            __dataclass__object_setattr(self, 'tool_calls', tool_calls)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__default_fn(self.role)) is not None:
                parts.append(f"role={s}")
            if (s := __dataclass__repr__default_fn(self.content)) is not None:
                parts.append(f"content={s}")
            if (s := __dataclass__repr__default_fn(self.thinking)) is not None:
                parts.append(f"thinking={s}")
            if (s := __dataclass__repr__default_fn(self.images)) is not None:
                parts.append(f"images={s}")
            if (s := __dataclass__repr__default_fn(self.tool_name)) is not None:
                parts.append(f"tool_name={s}")
            if (s := __dataclass__repr__default_fn(self.tool_calls)) is not None:
                parts.append(f"tool_calls={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('id', 'function')), EqPlan(fields=('id', 'function')), FrozenPlan(fields=('id', 'f"
        "unction'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('id', 'function'), cache=False), "
        "InitPlan(fields=(InitPlan.Field(name='id', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(na"
        "me='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, c"
        "oerce=None, validate=None, check_type=None), InitPlan.Field(name='function', annotation=OpRef(name='init.field"
        "s.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE"
        ", coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('id', 'func"
        "tion'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprP"
        "lan.Field(name='id', kw_only=True, fn=None), ReprPlan.Field(name='function', kw_only=True, fn=None)), id=False"
        ", terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='7d5771c082d3ad6a1d478102e83deb352ad93e34',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('ommlds.backends.ollama.protocol', 'Message.ToolCall'),
    ),
)
def _process_dataclass__7d5771c082d3ad6a1d478102e83deb352ad93e34():
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
                id=self.id,
                function=self.function,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
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
                self.function == other.function
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'id',
            'function',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                 or name in __dataclass___delattr_frozen_fields
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
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            id: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            function: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'function', function)

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
        "Plans(tup=(CopyPlan(fields=('name', 'arguments', 'index')), EqPlan(fields=('name', 'arguments', 'index')), Fro"
        "zenPlan(fields=('name', 'arguments', 'index'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', field"
        "s=('name', 'arguments', 'index'), cache=False), InitPlan(fields=(InitPlan.Field(name='name', annotation=OpRef("
        "name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=Fi"
        "eldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='arguments', annotation=Op"
        "Ref(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_typ"
        "e=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='index', annotation=Op"
        "Ref(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init="
        "True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param"
        "='self', std_params=(), kw_only_params=('name', 'arguments', 'index'), frozen=True, slots=False, post_init_par"
        "ams=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='name', kw_only=True, fn=None), "
        "ReprPlan.Field(name='arguments', kw_only=True, fn=None), ReprPlan.Field(name='index', kw_only=True, fn=None)),"
        " id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='c679b8dd972a245826381e3200fe81df0cd736c1',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.backends.ollama.protocol', 'Message.ToolCall.Function'),
    ),
)
def _process_dataclass__c679b8dd972a245826381e3200fe81df0cd736c1():
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
                index=self.index,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
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
                self.index == other.index
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'name',
            'arguments',
            'index',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'arguments',
            'index',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                 or name in __dataclass___delattr_frozen_fields
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
                self.arguments,
                self.index,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            name: __dataclass__init__fields__0__annotation,
            arguments: __dataclass__init__fields__1__annotation,
            index: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'arguments', arguments)
            __dataclass__object_setattr(self, 'index', index)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"name={self.name!r}")
            parts.append(f"arguments={self.arguments!r}")
            parts.append(f"index={self.index!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('numa', 'num_ctx', 'num_batch', 'num_gpu', 'main_gpu', 'low_vram', 'f16_kv', 'logi"
        "ts_all', 'vocab_only', 'use_mmap', 'use_mlock', 'embedding_only', 'num_thread', 'num_keep', 'seed', 'num_predi"
        "ct', 'top_k', 'top_p', 'tfs_z', 'typical_p', 'repeat_last_n', 'temperature', 'repeat_penalty', 'presence_penal"
        "ty', 'frequency_penalty', 'mirostat', 'mirostat_tau', 'mirostat_eta', 'penalize_newline', 'stop')), EqPlan(fie"
        "lds=('numa', 'num_ctx', 'num_batch', 'num_gpu', 'main_gpu', 'low_vram', 'f16_kv', 'logits_all', 'vocab_only', "
        "'use_mmap', 'use_mlock', 'embedding_only', 'num_thread', 'num_keep', 'seed', 'num_predict', 'top_k', 'top_p', "
        "'tfs_z', 'typical_p', 'repeat_last_n', 'temperature', 'repeat_penalty', 'presence_penalty', 'frequency_penalty"
        "', 'mirostat', 'mirostat_tau', 'mirostat_eta', 'penalize_newline', 'stop')), FrozenPlan(fields=('numa', 'num_c"
        "tx', 'num_batch', 'num_gpu', 'main_gpu', 'low_vram', 'f16_kv', 'logits_all', 'vocab_only', 'use_mmap', 'use_ml"
        "ock', 'embedding_only', 'num_thread', 'num_keep', 'seed', 'num_predict', 'top_k', 'top_p', 'tfs_z', 'typical_p"
        "', 'repeat_last_n', 'temperature', 'repeat_penalty', 'presence_penalty', 'frequency_penalty', 'mirostat', 'mir"
        "ostat_tau', 'mirostat_eta', 'penalize_newline', 'stop'), allow_dynamic_dunder_attrs=False), HashPlan(action='a"
        "dd', fields=('numa', 'num_ctx', 'num_batch', 'num_gpu', 'main_gpu', 'low_vram', 'f16_kv', 'logits_all', 'vocab"
        "_only', 'use_mmap', 'use_mlock', 'embedding_only', 'num_thread', 'num_keep', 'seed', 'num_predict', 'top_k', '"
        "top_p', 'tfs_z', 'typical_p', 'repeat_last_n', 'temperature', 'repeat_penalty', 'presence_penalty', 'frequency"
        "_penalty', 'mirostat', 'mirostat_tau', 'mirostat_eta', 'penalize_newline', 'stop'), cache=False), InitPlan(fie"
        "lds=(InitPlan.Field(name='numa', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.f"
        "ields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None"
        ", validate=None, check_type=None), InitPlan.Field(name='num_ctx', annotation=OpRef(name='init.fields.1.annotat"
        "ion'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_typ"
        "e=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='num_batch', annotatio"
        "n=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, i"
        "nit=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPla"
        "n.Field(name='num_gpu', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.d"
        "efault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validat"
        "e=None, check_type=None), InitPlan.Field(name='main_gpu', annotation=OpRef(name='init.fields.4.annotation'), d"
        "efault=OpRef(name='init.fields.4.default'), default_factory=None, init=True, override=False, field_type=FieldT"
        "ype.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='low_vram', annotation=OpRef(n"
        "ame='init.fields.5.annotation'), default=OpRef(name='init.fields.5.default'), default_factory=None, init=True,"
        " override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(n"
        "ame='f16_kv', annotation=OpRef(name='init.fields.6.annotation'), default=OpRef(name='init.fields.6.default'), "
        "default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, ch"
        "eck_type=None), InitPlan.Field(name='logits_all', annotation=OpRef(name='init.fields.7.annotation'), default=O"
        "pRef(name='init.fields.7.default'), default_factory=None, init=True, override=False, field_type=FieldType.INST"
        "ANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='vocab_only', annotation=OpRef(name='i"
        "nit.fields.8.annotation'), default=OpRef(name='init.fields.8.default'), default_factory=None, init=True, overr"
        "ide=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='u"
        "se_mmap', annotation=OpRef(name='init.fields.9.annotation'), default=OpRef(name='init.fields.9.default'), defa"
        "ult_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_"
        "type=None), InitPlan.Field(name='use_mlock', annotation=OpRef(name='init.fields.10.annotation'), default=OpRef"
        "(name='init.fields.10.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANC"
        "E, coerce=None, validate=None, check_type=None), InitPlan.Field(name='embedding_only', annotation=OpRef(name='"
        "init.fields.11.annotation'), default=OpRef(name='init.fields.11.default'), default_factory=None, init=True, ov"
        "erride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name"
        "='num_thread', annotation=OpRef(name='init.fields.12.annotation'), default=OpRef(name='init.fields.12.default'"
        "), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None,"
        " check_type=None), InitPlan.Field(name='num_keep', annotation=OpRef(name='init.fields.13.annotation'), default"
        "=OpRef(name='init.fields.13.default'), default_factory=None, init=True, override=False, field_type=FieldType.I"
        "NSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='seed', annotation=OpRef(name='init"
        ".fields.14.annotation'), default=OpRef(name='init.fields.14.default'), default_factory=None, init=True, overri"
        "de=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='nu"
        "m_predict', annotation=OpRef(name='init.fields.15.annotation'), default=OpRef(name='init.fields.15.default'), "
        "default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, ch"
        "eck_type=None), InitPlan.Field(name='top_k', annotation=OpRef(name='init.fields.16.annotation'), default=OpRef"
        "(name='init.fields.16.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANC"
        "E, coerce=None, validate=None, check_type=None), InitPlan.Field(name='top_p', annotation=OpRef(name='init.fiel"
        "ds.17.annotation'), default=OpRef(name='init.fields.17.default'), default_factory=None, init=True, override=Fa"
        "lse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='tfs_z',"
        " annotation=OpRef(name='init.fields.18.annotation'), default=OpRef(name='init.fields.18.default'), default_fac"
        "tory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=No"
        "ne), InitPlan.Field(name='typical_p', annotation=OpRef(name='init.fields.19.annotation'), default=OpRef(name='"
        "init.fields.19.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coer"
        "ce=None, validate=None, check_type=None), InitPlan.Field(name='repeat_last_n', annotation=OpRef(name='init.fie"
        "lds.20.annotation'), default=OpRef(name='init.fields.20.default'), default_factory=None, init=True, override=F"
        "alse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='temper"
        "ature', annotation=OpRef(name='init.fields.21.annotation'), default=OpRef(name='init.fields.21.default'), defa"
        "ult_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_"
        "type=None), InitPlan.Field(name='repeat_penalty', annotation=OpRef(name='init.fields.22.annotation'), default="
        "OpRef(name='init.fields.22.default'), default_factory=None, init=True, override=False, field_type=FieldType.IN"
        "STANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='presence_penalty', annotation=OpRef"
        "(name='init.fields.23.annotation'), default=OpRef(name='init.fields.23.default'), default_factory=None, init=T"
        "rue, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fie"
        "ld(name='frequency_penalty', annotation=OpRef(name='init.fields.24.annotation'), default=OpRef(name='init.fiel"
        "ds.24.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, "
        "validate=None, check_type=None), InitPlan.Field(name='mirostat', annotation=OpRef(name='init.fields.25.annotat"
        "ion'), default=OpRef(name='init.fields.25.default'), default_factory=None, init=True, override=False, field_ty"
        "pe=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='mirostat_tau', annot"
        "ation=OpRef(name='init.fields.26.annotation'), default=OpRef(name='init.fields.26.default'), default_factory=N"
        "one, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), I"
        "nitPlan.Field(name='mirostat_eta', annotation=OpRef(name='init.fields.27.annotation'), default=OpRef(name='ini"
        "t.fields.27.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce="
        "None, validate=None, check_type=None), InitPlan.Field(name='penalize_newline', annotation=OpRef(name='init.fie"
        "lds.28.annotation'), default=OpRef(name='init.fields.28.default'), default_factory=None, init=True, override=F"
        "alse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='stop',"
        " annotation=OpRef(name='init.fields.29.annotation'), default=OpRef(name='init.fields.29.default'), default_fac"
        "tory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=No"
        "ne)), self_param='self', std_params=(), kw_only_params=('numa', 'num_ctx', 'num_batch', 'num_gpu', 'main_gpu',"
        " 'low_vram', 'f16_kv', 'logits_all', 'vocab_only', 'use_mmap', 'use_mlock', 'embedding_only', 'num_thread', 'n"
        "um_keep', 'seed', 'num_predict', 'top_k', 'top_p', 'tfs_z', 'typical_p', 'repeat_last_n', 'temperature', 'repe"
        "at_penalty', 'presence_penalty', 'frequency_penalty', 'mirostat', 'mirostat_tau', 'mirostat_eta', 'penalize_ne"
        "wline', 'stop'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fiel"
        "ds=(ReprPlan.Field(name='numa', kw_only=True, fn=None), ReprPlan.Field(name='num_ctx', kw_only=True, fn=None),"
        " ReprPlan.Field(name='num_batch', kw_only=True, fn=None), ReprPlan.Field(name='num_gpu', kw_only=True, fn=None"
        "), ReprPlan.Field(name='main_gpu', kw_only=True, fn=None), ReprPlan.Field(name='low_vram', kw_only=True, fn=No"
        "ne), ReprPlan.Field(name='f16_kv', kw_only=True, fn=None), ReprPlan.Field(name='logits_all', kw_only=True, fn="
        "None), ReprPlan.Field(name='vocab_only', kw_only=True, fn=None), ReprPlan.Field(name='use_mmap', kw_only=True,"
        " fn=None), ReprPlan.Field(name='use_mlock', kw_only=True, fn=None), ReprPlan.Field(name='embedding_only', kw_o"
        "nly=True, fn=None), ReprPlan.Field(name='num_thread', kw_only=True, fn=None), ReprPlan.Field(name='num_keep', "
        "kw_only=True, fn=None), ReprPlan.Field(name='seed', kw_only=True, fn=None), ReprPlan.Field(name='num_predict',"
        " kw_only=True, fn=None), ReprPlan.Field(name='top_k', kw_only=True, fn=None), ReprPlan.Field(name='top_p', kw_"
        "only=True, fn=None), ReprPlan.Field(name='tfs_z', kw_only=True, fn=None), ReprPlan.Field(name='typical_p', kw_"
        "only=True, fn=None), ReprPlan.Field(name='repeat_last_n', kw_only=True, fn=None), ReprPlan.Field(name='tempera"
        "ture', kw_only=True, fn=None), ReprPlan.Field(name='repeat_penalty', kw_only=True, fn=None), ReprPlan.Field(na"
        "me='presence_penalty', kw_only=True, fn=None), ReprPlan.Field(name='frequency_penalty', kw_only=True, fn=None)"
        ", ReprPlan.Field(name='mirostat', kw_only=True, fn=None), ReprPlan.Field(name='mirostat_tau', kw_only=True, fn"
        "=None), ReprPlan.Field(name='mirostat_eta', kw_only=True, fn=None), ReprPlan.Field(name='penalize_newline', kw"
        "_only=True, fn=None), ReprPlan.Field(name='stop', kw_only=True, fn=None)), id=False, terse=False, default_fn=O"
        "pRef(name='repr.default_fn'))))"
    ),
    plan_repr_sha1='ee676a855d03365888791d5b18db34dc1c6d5e77',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
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
        '__dataclass__repr__default_fn',
    ),
    cls_names=(
        ('ommlds.backends.ollama.protocol', 'Options'),
    ),
)
def _process_dataclass__ee676a855d03365888791d5b18db34dc1c6d5e77():
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
                numa=self.numa,
                num_ctx=self.num_ctx,
                num_batch=self.num_batch,
                num_gpu=self.num_gpu,
                main_gpu=self.main_gpu,
                low_vram=self.low_vram,
                f16_kv=self.f16_kv,
                logits_all=self.logits_all,
                vocab_only=self.vocab_only,
                use_mmap=self.use_mmap,
                use_mlock=self.use_mlock,
                embedding_only=self.embedding_only,
                num_thread=self.num_thread,
                num_keep=self.num_keep,
                seed=self.seed,
                num_predict=self.num_predict,
                top_k=self.top_k,
                top_p=self.top_p,
                tfs_z=self.tfs_z,
                typical_p=self.typical_p,
                repeat_last_n=self.repeat_last_n,
                temperature=self.temperature,
                repeat_penalty=self.repeat_penalty,
                presence_penalty=self.presence_penalty,
                frequency_penalty=self.frequency_penalty,
                mirostat=self.mirostat,
                mirostat_tau=self.mirostat_tau,
                mirostat_eta=self.mirostat_eta,
                penalize_newline=self.penalize_newline,
                stop=self.stop,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.numa == other.numa and
                self.num_ctx == other.num_ctx and
                self.num_batch == other.num_batch and
                self.num_gpu == other.num_gpu and
                self.main_gpu == other.main_gpu and
                self.low_vram == other.low_vram and
                self.f16_kv == other.f16_kv and
                self.logits_all == other.logits_all and
                self.vocab_only == other.vocab_only and
                self.use_mmap == other.use_mmap and
                self.use_mlock == other.use_mlock and
                self.embedding_only == other.embedding_only and
                self.num_thread == other.num_thread and
                self.num_keep == other.num_keep and
                self.seed == other.seed and
                self.num_predict == other.num_predict and
                self.top_k == other.top_k and
                self.top_p == other.top_p and
                self.tfs_z == other.tfs_z and
                self.typical_p == other.typical_p and
                self.repeat_last_n == other.repeat_last_n and
                self.temperature == other.temperature and
                self.repeat_penalty == other.repeat_penalty and
                self.presence_penalty == other.presence_penalty and
                self.frequency_penalty == other.frequency_penalty and
                self.mirostat == other.mirostat and
                self.mirostat_tau == other.mirostat_tau and
                self.mirostat_eta == other.mirostat_eta and
                self.penalize_newline == other.penalize_newline and
                self.stop == other.stop
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'numa',
            'num_ctx',
            'num_batch',
            'num_gpu',
            'main_gpu',
            'low_vram',
            'f16_kv',
            'logits_all',
            'vocab_only',
            'use_mmap',
            'use_mlock',
            'embedding_only',
            'num_thread',
            'num_keep',
            'seed',
            'num_predict',
            'top_k',
            'top_p',
            'tfs_z',
            'typical_p',
            'repeat_last_n',
            'temperature',
            'repeat_penalty',
            'presence_penalty',
            'frequency_penalty',
            'mirostat',
            'mirostat_tau',
            'mirostat_eta',
            'penalize_newline',
            'stop',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                 or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'numa',
            'num_ctx',
            'num_batch',
            'num_gpu',
            'main_gpu',
            'low_vram',
            'f16_kv',
            'logits_all',
            'vocab_only',
            'use_mmap',
            'use_mlock',
            'embedding_only',
            'num_thread',
            'num_keep',
            'seed',
            'num_predict',
            'top_k',
            'top_p',
            'tfs_z',
            'typical_p',
            'repeat_last_n',
            'temperature',
            'repeat_penalty',
            'presence_penalty',
            'frequency_penalty',
            'mirostat',
            'mirostat_tau',
            'mirostat_eta',
            'penalize_newline',
            'stop',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                 or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.numa,
                self.num_ctx,
                self.num_batch,
                self.num_gpu,
                self.main_gpu,
                self.low_vram,
                self.f16_kv,
                self.logits_all,
                self.vocab_only,
                self.use_mmap,
                self.use_mlock,
                self.embedding_only,
                self.num_thread,
                self.num_keep,
                self.seed,
                self.num_predict,
                self.top_k,
                self.top_p,
                self.tfs_z,
                self.typical_p,
                self.repeat_last_n,
                self.temperature,
                self.repeat_penalty,
                self.presence_penalty,
                self.frequency_penalty,
                self.mirostat,
                self.mirostat_tau,
                self.mirostat_eta,
                self.penalize_newline,
                self.stop,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            numa: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            num_ctx: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            num_batch: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            num_gpu: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            main_gpu: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            low_vram: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
            f16_kv: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
            logits_all: __dataclass__init__fields__7__annotation = __dataclass__init__fields__7__default,
            vocab_only: __dataclass__init__fields__8__annotation = __dataclass__init__fields__8__default,
            use_mmap: __dataclass__init__fields__9__annotation = __dataclass__init__fields__9__default,
            use_mlock: __dataclass__init__fields__10__annotation = __dataclass__init__fields__10__default,
            embedding_only: __dataclass__init__fields__11__annotation = __dataclass__init__fields__11__default,
            num_thread: __dataclass__init__fields__12__annotation = __dataclass__init__fields__12__default,
            num_keep: __dataclass__init__fields__13__annotation = __dataclass__init__fields__13__default,
            seed: __dataclass__init__fields__14__annotation = __dataclass__init__fields__14__default,
            num_predict: __dataclass__init__fields__15__annotation = __dataclass__init__fields__15__default,
            top_k: __dataclass__init__fields__16__annotation = __dataclass__init__fields__16__default,
            top_p: __dataclass__init__fields__17__annotation = __dataclass__init__fields__17__default,
            tfs_z: __dataclass__init__fields__18__annotation = __dataclass__init__fields__18__default,
            typical_p: __dataclass__init__fields__19__annotation = __dataclass__init__fields__19__default,
            repeat_last_n: __dataclass__init__fields__20__annotation = __dataclass__init__fields__20__default,
            temperature: __dataclass__init__fields__21__annotation = __dataclass__init__fields__21__default,
            repeat_penalty: __dataclass__init__fields__22__annotation = __dataclass__init__fields__22__default,
            presence_penalty: __dataclass__init__fields__23__annotation = __dataclass__init__fields__23__default,
            frequency_penalty: __dataclass__init__fields__24__annotation = __dataclass__init__fields__24__default,
            mirostat: __dataclass__init__fields__25__annotation = __dataclass__init__fields__25__default,
            mirostat_tau: __dataclass__init__fields__26__annotation = __dataclass__init__fields__26__default,
            mirostat_eta: __dataclass__init__fields__27__annotation = __dataclass__init__fields__27__default,
            penalize_newline: __dataclass__init__fields__28__annotation = __dataclass__init__fields__28__default,
            stop: __dataclass__init__fields__29__annotation = __dataclass__init__fields__29__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'numa', numa)
            __dataclass__object_setattr(self, 'num_ctx', num_ctx)
            __dataclass__object_setattr(self, 'num_batch', num_batch)
            __dataclass__object_setattr(self, 'num_gpu', num_gpu)
            __dataclass__object_setattr(self, 'main_gpu', main_gpu)
            __dataclass__object_setattr(self, 'low_vram', low_vram)
            __dataclass__object_setattr(self, 'f16_kv', f16_kv)
            __dataclass__object_setattr(self, 'logits_all', logits_all)
            __dataclass__object_setattr(self, 'vocab_only', vocab_only)
            __dataclass__object_setattr(self, 'use_mmap', use_mmap)
            __dataclass__object_setattr(self, 'use_mlock', use_mlock)
            __dataclass__object_setattr(self, 'embedding_only', embedding_only)
            __dataclass__object_setattr(self, 'num_thread', num_thread)
            __dataclass__object_setattr(self, 'num_keep', num_keep)
            __dataclass__object_setattr(self, 'seed', seed)
            __dataclass__object_setattr(self, 'num_predict', num_predict)
            __dataclass__object_setattr(self, 'top_k', top_k)
            __dataclass__object_setattr(self, 'top_p', top_p)
            __dataclass__object_setattr(self, 'tfs_z', tfs_z)
            __dataclass__object_setattr(self, 'typical_p', typical_p)
            __dataclass__object_setattr(self, 'repeat_last_n', repeat_last_n)
            __dataclass__object_setattr(self, 'temperature', temperature)
            __dataclass__object_setattr(self, 'repeat_penalty', repeat_penalty)
            __dataclass__object_setattr(self, 'presence_penalty', presence_penalty)
            __dataclass__object_setattr(self, 'frequency_penalty', frequency_penalty)
            __dataclass__object_setattr(self, 'mirostat', mirostat)
            __dataclass__object_setattr(self, 'mirostat_tau', mirostat_tau)
            __dataclass__object_setattr(self, 'mirostat_eta', mirostat_eta)
            __dataclass__object_setattr(self, 'penalize_newline', penalize_newline)
            __dataclass__object_setattr(self, 'stop', stop)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__default_fn(self.numa)) is not None:
                parts.append(f"numa={s}")
            if (s := __dataclass__repr__default_fn(self.num_ctx)) is not None:
                parts.append(f"num_ctx={s}")
            if (s := __dataclass__repr__default_fn(self.num_batch)) is not None:
                parts.append(f"num_batch={s}")
            if (s := __dataclass__repr__default_fn(self.num_gpu)) is not None:
                parts.append(f"num_gpu={s}")
            if (s := __dataclass__repr__default_fn(self.main_gpu)) is not None:
                parts.append(f"main_gpu={s}")
            if (s := __dataclass__repr__default_fn(self.low_vram)) is not None:
                parts.append(f"low_vram={s}")
            if (s := __dataclass__repr__default_fn(self.f16_kv)) is not None:
                parts.append(f"f16_kv={s}")
            if (s := __dataclass__repr__default_fn(self.logits_all)) is not None:
                parts.append(f"logits_all={s}")
            if (s := __dataclass__repr__default_fn(self.vocab_only)) is not None:
                parts.append(f"vocab_only={s}")
            if (s := __dataclass__repr__default_fn(self.use_mmap)) is not None:
                parts.append(f"use_mmap={s}")
            if (s := __dataclass__repr__default_fn(self.use_mlock)) is not None:
                parts.append(f"use_mlock={s}")
            if (s := __dataclass__repr__default_fn(self.embedding_only)) is not None:
                parts.append(f"embedding_only={s}")
            if (s := __dataclass__repr__default_fn(self.num_thread)) is not None:
                parts.append(f"num_thread={s}")
            if (s := __dataclass__repr__default_fn(self.num_keep)) is not None:
                parts.append(f"num_keep={s}")
            if (s := __dataclass__repr__default_fn(self.seed)) is not None:
                parts.append(f"seed={s}")
            if (s := __dataclass__repr__default_fn(self.num_predict)) is not None:
                parts.append(f"num_predict={s}")
            if (s := __dataclass__repr__default_fn(self.top_k)) is not None:
                parts.append(f"top_k={s}")
            if (s := __dataclass__repr__default_fn(self.top_p)) is not None:
                parts.append(f"top_p={s}")
            if (s := __dataclass__repr__default_fn(self.tfs_z)) is not None:
                parts.append(f"tfs_z={s}")
            if (s := __dataclass__repr__default_fn(self.typical_p)) is not None:
                parts.append(f"typical_p={s}")
            if (s := __dataclass__repr__default_fn(self.repeat_last_n)) is not None:
                parts.append(f"repeat_last_n={s}")
            if (s := __dataclass__repr__default_fn(self.temperature)) is not None:
                parts.append(f"temperature={s}")
            if (s := __dataclass__repr__default_fn(self.repeat_penalty)) is not None:
                parts.append(f"repeat_penalty={s}")
            if (s := __dataclass__repr__default_fn(self.presence_penalty)) is not None:
                parts.append(f"presence_penalty={s}")
            if (s := __dataclass__repr__default_fn(self.frequency_penalty)) is not None:
                parts.append(f"frequency_penalty={s}")
            if (s := __dataclass__repr__default_fn(self.mirostat)) is not None:
                parts.append(f"mirostat={s}")
            if (s := __dataclass__repr__default_fn(self.mirostat_tau)) is not None:
                parts.append(f"mirostat_tau={s}")
            if (s := __dataclass__repr__default_fn(self.mirostat_eta)) is not None:
                parts.append(f"mirostat_eta={s}")
            if (s := __dataclass__repr__default_fn(self.penalize_newline)) is not None:
                parts.append(f"penalize_newline={s}")
            if (s := __dataclass__repr__default_fn(self.stop)) is not None:
                parts.append(f"stop={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('type', 'function')), EqPlan(fields=('type', 'function')), FrozenPlan(fields=('typ"
        "e', 'function'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('type', 'function'), cache="
        "False), InitPlan(fields=(InitPlan.Field(name='type', annotation=OpRef(name='init.fields.0.annotation'), defaul"
        "t=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.I"
        "NSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='function', annotation=OpRef(name='"
        "init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, over"
        "ride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', s"
        "td_params=(), kw_only_params=('type', 'function'), frozen=True, slots=False, post_init_params=None, init_fns=("
        "), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='type', kw_only=True, fn=None), ReprPlan.Field(name="
        "'function', kw_only=True, fn=None)), id=False, terse=False, default_fn=OpRef(name='repr.default_fn'))))"
    ),
    plan_repr_sha1='98e20371eacca6bc272118f8eb67b1dcfcf27443',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__repr__default_fn',
    ),
    cls_names=(
        ('ommlds.backends.ollama.protocol', 'Tool'),
    ),
)
def _process_dataclass__98e20371eacca6bc272118f8eb67b1dcfcf27443():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
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
                type=self.type,
                function=self.function,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
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
                self.function == other.function
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'type',
            'function',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'function',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                 or name in __dataclass___delattr_frozen_fields
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
                self.function,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            type: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            function: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'type', type)
            __dataclass__object_setattr(self, 'function', function)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            if (s := __dataclass__repr__default_fn(self.type)) is not None:
                parts.append(f"type={s}")
            if (s := __dataclass__repr__default_fn(self.function)) is not None:
                parts.append(f"function={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('name', 'description', 'parameters')), EqPlan(fields=('name', 'description', 'para"
        "meters')), FrozenPlan(fields=('name', 'description', 'parameters'), allow_dynamic_dunder_attrs=False), HashPla"
        "n(action='add', fields=('name', 'description', 'parameters'), cache=False), InitPlan(fields=(InitPlan.Field(na"
        "me='name', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'), def"
        "ault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check"
        "_type=None), InitPlan.Field(name='description', annotation=OpRef(name='init.fields.1.annotation'), default=OpR"
        "ef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTAN"
        "CE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='parameters', annotation=OpRef(name='ini"
        "t.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, overrid"
        "e=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_"
        "params=(), kw_only_params=('name', 'description', 'parameters'), frozen=True, slots=False, post_init_params=No"
        "ne, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='name', kw_only=True, fn=None), ReprPl"
        "an.Field(name='description', kw_only=True, fn=None), ReprPlan.Field(name='parameters', kw_only=True, fn=None))"
        ", id=False, terse=False, default_fn=OpRef(name='repr.default_fn'))))"
    ),
    plan_repr_sha1='c2256e8aae1a7cdef13cab0a48a15a27471904f0',
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
        ('ommlds.backends.ollama.protocol', 'Tool.Function'),
    ),
)
def _process_dataclass__c2256e8aae1a7cdef13cab0a48a15a27471904f0():
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
                description=self.description,
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
                self.name == other.name and
                self.description == other.description and
                self.parameters == other.parameters
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'name',
            'description',
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
            'name',
            'description',
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
                self.name,
                self.description,
                self.parameters,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            name: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            description: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            parameters: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'description', description)
            __dataclass__object_setattr(self, 'parameters', parameters)

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
