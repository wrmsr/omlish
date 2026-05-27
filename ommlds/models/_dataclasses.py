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
        "Plans(tup=(CopyPlan(fields=('input', 'output', 'reasoning', 'cache_read', 'cache_write', 'input_audio', 'outpu"
        "t_audio', 'x', 'context_over_200k', 'tiers')), EqPlan(fields=('input', 'output', 'reasoning', 'cache_read', 'c"
        "ache_write', 'input_audio', 'output_audio', 'x', 'context_over_200k', 'tiers')), FrozenPlan(fields=('input', '"
        "output', 'reasoning', 'cache_read', 'cache_write', 'input_audio', 'output_audio', 'x', 'context_over_200k', 't"
        "iers'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('input', 'output', 'reasoning', 'cac"
        "he_read', 'cache_write', 'input_audio', 'output_audio', 'x', 'context_over_200k', 'tiers'), cache=False), Init"
        "Plan(fields=(InitPlan.Field(name='input', annotation=OpRef(name='init.fields.00.annotation'), default=None, de"
        "fault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, chec"
        "k_type=None), InitPlan.Field(name='output', annotation=OpRef(name='init.fields.01.annotation'), default=None, "
        "default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, ch"
        "eck_type=None), InitPlan.Field(name='reasoning', annotation=OpRef(name='init.fields.02.annotation'), default=O"
        "pRef(name='init.fields.02.default'), default_factory=None, init=True, override=False, field_type=FieldType.INS"
        "TANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='cache_read', annotation=OpRef(name='"
        "init.fields.03.annotation'), default=OpRef(name='init.fields.03.default'), default_factory=None, init=True, ov"
        "erride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name"
        "='cache_write', annotation=OpRef(name='init.fields.04.annotation'), default=OpRef(name='init.fields.04.default"
        "'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None"
        ", check_type=None), InitPlan.Field(name='input_audio', annotation=OpRef(name='init.fields.05.annotation'), def"
        "ault=OpRef(name='init.fields.05.default'), default_factory=None, init=True, override=False, field_type=FieldTy"
        "pe.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='output_audio', annotation=OpRe"
        "f(name='init.fields.06.annotation'), default=OpRef(name='init.fields.06.default'), default_factory=None, init="
        "True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fi"
        "eld(name='x', annotation=OpRef(name='init.fields.07.annotation'), default=OpRef(name='init.fields.07.default')"
        ", default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, "
        "check_type=None), InitPlan.Field(name='context_over_200k', annotation=OpRef(name='init.fields.08.annotation'),"
        " default=OpRef(name='init.fields.08.default'), default_factory=None, init=True, override=False, field_type=Fie"
        "ldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='tiers', annotation=OpRef(n"
        "ame='init.fields.09.annotation'), default=OpRef(name='init.fields.09.default'), default_factory=None, init=Tru"
        "e, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='s"
        "elf', std_params=(), kw_only_params=('input', 'output', 'reasoning', 'cache_read', 'cache_write', 'input_audio"
        "', 'output_audio', 'x', 'context_over_200k', 'tiers'), frozen=True, slots=False, post_init_params=None, init_f"
        "ns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='input', kw_only=True, fn=None), ReprPlan.Field("
        "name='output', kw_only=True, fn=None), ReprPlan.Field(name='reasoning', kw_only=True, fn=None), ReprPlan.Field"
        "(name='cache_read', kw_only=True, fn=None), ReprPlan.Field(name='cache_write', kw_only=True, fn=None), ReprPla"
        "n.Field(name='input_audio', kw_only=True, fn=None), ReprPlan.Field(name='output_audio', kw_only=True, fn=None)"
        ", ReprPlan.Field(name='x', kw_only=True, fn=None), ReprPlan.Field(name='context_over_200k', kw_only=True, fn=N"
        "one), ReprPlan.Field(name='tiers', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='61498cf644d82dfe1fc2c93b44484d966059aebf',
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
    ),
    cls_names=(
        ('ommlds.models.types', 'AuthoredCost'),
        ('ommlds.models.types', 'OutputCost'),
    ),
)
def _process_dataclass__61498cf644d82dfe1fc2c93b44484d966059aebf():
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
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
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
                reasoning=self.reasoning,
                cache_read=self.cache_read,
                cache_write=self.cache_write,
                input_audio=self.input_audio,
                output_audio=self.output_audio,
                x=self.x,
                context_over_200k=self.context_over_200k,
                tiers=self.tiers,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
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
                self.reasoning == other.reasoning and
                self.cache_read == other.cache_read and
                self.cache_write == other.cache_write and
                self.input_audio == other.input_audio and
                self.output_audio == other.output_audio and
                self.x == other.x and
                self.context_over_200k == other.context_over_200k and
                self.tiers == other.tiers
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'input',
            'output',
            'reasoning',
            'cache_read',
            'cache_write',
            'input_audio',
            'output_audio',
            'x',
            'context_over_200k',
            'tiers',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'reasoning',
            'cache_read',
            'cache_write',
            'input_audio',
            'output_audio',
            'x',
            'context_over_200k',
            'tiers',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
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
                self.reasoning,
                self.cache_read,
                self.cache_write,
                self.input_audio,
                self.output_audio,
                self.x,
                self.context_over_200k,
                self.tiers,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            input: __dataclass__init__fields__00__annotation,
            output: __dataclass__init__fields__01__annotation,
            reasoning: __dataclass__init__fields__02__annotation = __dataclass__init__fields__02__default,
            cache_read: __dataclass__init__fields__03__annotation = __dataclass__init__fields__03__default,
            cache_write: __dataclass__init__fields__04__annotation = __dataclass__init__fields__04__default,
            input_audio: __dataclass__init__fields__05__annotation = __dataclass__init__fields__05__default,
            output_audio: __dataclass__init__fields__06__annotation = __dataclass__init__fields__06__default,
            x: __dataclass__init__fields__07__annotation = __dataclass__init__fields__07__default,
            context_over_200k: __dataclass__init__fields__08__annotation = __dataclass__init__fields__08__default,
            tiers: __dataclass__init__fields__09__annotation = __dataclass__init__fields__09__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'input', input)
            __dataclass__object_setattr(self, 'output', output)
            __dataclass__object_setattr(self, 'reasoning', reasoning)
            __dataclass__object_setattr(self, 'cache_read', cache_read)
            __dataclass__object_setattr(self, 'cache_write', cache_write)
            __dataclass__object_setattr(self, 'input_audio', input_audio)
            __dataclass__object_setattr(self, 'output_audio', output_audio)
            __dataclass__object_setattr(self, 'x', x)
            __dataclass__object_setattr(self, 'context_over_200k', context_over_200k)
            __dataclass__object_setattr(self, 'tiers', tiers)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"input={self.input!r}")
            parts.append(f"output={self.output!r}")
            parts.append(f"reasoning={self.reasoning!r}")
            parts.append(f"cache_read={self.cache_read!r}")
            parts.append(f"cache_write={self.cache_write!r}")
            parts.append(f"input_audio={self.input_audio!r}")
            parts.append(f"output_audio={self.output_audio!r}")
            parts.append(f"x={self.x!r}")
            parts.append(f"context_over_200k={self.context_over_200k!r}")
            parts.append(f"tiers={self.tiers!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('id', 'name', 'attachment', 'reasoning', 'tool_call', 'release_date', 'last_update"
        "d', 'modalities', 'open_weights', 'limit', 'family', 'interleaved', 'structured_output', 'temperature', 'knowl"
        "edge', 'status', 'experimental', 'provider', 'cost', 'x')), EqPlan(fields=('id', 'name', 'attachment', 'reason"
        "ing', 'tool_call', 'release_date', 'last_updated', 'modalities', 'open_weights', 'limit', 'family', 'interleav"
        "ed', 'structured_output', 'temperature', 'knowledge', 'status', 'experimental', 'provider', 'cost', 'x')), Fro"
        "zenPlan(fields=('id', 'name', 'attachment', 'reasoning', 'tool_call', 'release_date', 'last_updated', 'modalit"
        "ies', 'open_weights', 'limit', 'family', 'interleaved', 'structured_output', 'temperature', 'knowledge', 'stat"
        "us', 'experimental', 'provider', 'cost', 'x'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', field"
        "s=('id', 'name', 'attachment', 'reasoning', 'tool_call', 'release_date', 'last_updated', 'modalities', 'open_w"
        "eights', 'limit', 'family', 'interleaved', 'structured_output', 'temperature', 'knowledge', 'status', 'experim"
        "ental', 'provider', 'cost', 'x'), cache=False), InitPlan(fields=(InitPlan.Field(name='id', annotation=OpRef(na"
        "me='init.fields.00.annotation'), default=None, default_factory=None, init=True, override=False, field_type=Fie"
        "ldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='name', annotation=OpRef(na"
        "me='init.fields.01.annotation'), default=None, default_factory=None, init=True, override=False, field_type=Fie"
        "ldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='attachment', annotation=Op"
        "Ref(name='init.fields.02.annotation'), default=None, default_factory=None, init=True, override=False, field_ty"
        "pe=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='reasoning', annotati"
        "on=OpRef(name='init.fields.03.annotation'), default=None, default_factory=None, init=True, override=False, fie"
        "ld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='tool_call', ann"
        "otation=OpRef(name='init.fields.04.annotation'), default=None, default_factory=None, init=True, override=False"
        ", field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='release_da"
        "te', annotation=OpRef(name='init.fields.05.annotation'), default=None, default_factory=None, init=True, overri"
        "de=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='la"
        "st_updated', annotation=OpRef(name='init.fields.06.annotation'), default=None, default_factory=None, init=True"
        ", override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field("
        "name='modalities', annotation=OpRef(name='init.fields.07.annotation'), default=None, default_factory=None, ini"
        "t=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan."
        "Field(name='open_weights', annotation=OpRef(name='init.fields.08.annotation'), default=None, default_factory=N"
        "one, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), I"
        "nitPlan.Field(name='limit', annotation=OpRef(name='init.fields.09.annotation'), default=None, default_factory="
        "None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), "
        "InitPlan.Field(name='family', annotation=OpRef(name='init.fields.10.annotation'), default=OpRef(name='init.fie"
        "lds.10.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None,"
        " validate=None, check_type=None), InitPlan.Field(name='interleaved', annotation=OpRef(name='init.fields.11.ann"
        "otation'), default=OpRef(name='init.fields.11.default'), default_factory=None, init=True, override=False, fiel"
        "d_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='structured_outpu"
        "t', annotation=OpRef(name='init.fields.12.annotation'), default=OpRef(name='init.fields.12.default'), default_"
        "factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type"
        "=None), InitPlan.Field(name='temperature', annotation=OpRef(name='init.fields.13.annotation'), default=OpRef(n"
        "ame='init.fields.13.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE,"
        " coerce=None, validate=None, check_type=None), InitPlan.Field(name='knowledge', annotation=OpRef(name='init.fi"
        "elds.14.annotation'), default=OpRef(name='init.fields.14.default'), default_factory=None, init=True, override="
        "False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='statu"
        "s', annotation=OpRef(name='init.fields.15.annotation'), default=OpRef(name='init.fields.15.default'), default_"
        "factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type"
        "=None), InitPlan.Field(name='experimental', annotation=OpRef(name='init.fields.16.annotation'), default=OpRef("
        "name='init.fields.16.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE"
        ", coerce=None, validate=None, check_type=None), InitPlan.Field(name='provider', annotation=OpRef(name='init.fi"
        "elds.17.annotation'), default=OpRef(name='init.fields.17.default'), default_factory=None, init=True, override="
        "False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='cost'"
        ", annotation=OpRef(name='init.fields.18.annotation'), default=OpRef(name='init.fields.18.default'), default_fa"
        "ctory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=N"
        "one), InitPlan.Field(name='x', annotation=OpRef(name='init.fields.19.annotation'), default=OpRef(name='init.fi"
        "elds.19.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None"
        ", validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('id', 'name', 'attachmen"
        "t', 'reasoning', 'tool_call', 'release_date', 'last_updated', 'modalities', 'open_weights', 'limit', 'family',"
        " 'interleaved', 'structured_output', 'temperature', 'knowledge', 'status', 'experimental', 'provider', 'cost',"
        " 'x'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPl"
        "an.Field(name='id', kw_only=True, fn=None), ReprPlan.Field(name='name', kw_only=True, fn=None), ReprPlan.Field"
        "(name='attachment', kw_only=True, fn=None), ReprPlan.Field(name='reasoning', kw_only=True, fn=None), ReprPlan."
        "Field(name='tool_call', kw_only=True, fn=None), ReprPlan.Field(name='release_date', kw_only=True, fn=None), Re"
        "prPlan.Field(name='last_updated', kw_only=True, fn=None), ReprPlan.Field(name='modalities', kw_only=True, fn=N"
        "one), ReprPlan.Field(name='open_weights', kw_only=True, fn=None), ReprPlan.Field(name='limit', kw_only=True, f"
        "n=None), ReprPlan.Field(name='family', kw_only=True, fn=None), ReprPlan.Field(name='interleaved', kw_only=True"
        ", fn=None), ReprPlan.Field(name='structured_output', kw_only=True, fn=None), ReprPlan.Field(name='temperature'"
        ", kw_only=True, fn=None), ReprPlan.Field(name='knowledge', kw_only=True, fn=None), ReprPlan.Field(name='status"
        "', kw_only=True, fn=None), ReprPlan.Field(name='experimental', kw_only=True, fn=None), ReprPlan.Field(name='pr"
        "ovider', kw_only=True, fn=None), ReprPlan.Field(name='cost', kw_only=True, fn=None), ReprPlan.Field(name='x', "
        "kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='96d40ba793c0b985e7bdccf131eb50377264de9c',
    op_ref_idents=(
        '__dataclass__init__fields__00__annotation',
        '__dataclass__init__fields__01__annotation',
        '__dataclass__init__fields__02__annotation',
        '__dataclass__init__fields__03__annotation',
        '__dataclass__init__fields__04__annotation',
        '__dataclass__init__fields__05__annotation',
        '__dataclass__init__fields__06__annotation',
        '__dataclass__init__fields__07__annotation',
        '__dataclass__init__fields__08__annotation',
        '__dataclass__init__fields__09__annotation',
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
    ),
    cls_names=(
        ('ommlds.models.types', 'AuthoredModel'),
        ('ommlds.models.types', 'Model'),
    ),
)
def _process_dataclass__96d40ba793c0b985e7bdccf131eb50377264de9c():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__00__annotation,
        __dataclass__init__fields__01__annotation,
        __dataclass__init__fields__02__annotation,
        __dataclass__init__fields__03__annotation,
        __dataclass__init__fields__04__annotation,
        __dataclass__init__fields__05__annotation,
        __dataclass__init__fields__06__annotation,
        __dataclass__init__fields__07__annotation,
        __dataclass__init__fields__08__annotation,
        __dataclass__init__fields__09__annotation,
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
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
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
                attachment=self.attachment,
                reasoning=self.reasoning,
                tool_call=self.tool_call,
                release_date=self.release_date,
                last_updated=self.last_updated,
                modalities=self.modalities,
                open_weights=self.open_weights,
                limit=self.limit,
                family=self.family,
                interleaved=self.interleaved,
                structured_output=self.structured_output,
                temperature=self.temperature,
                knowledge=self.knowledge,
                status=self.status,
                experimental=self.experimental,
                provider=self.provider,
                cost=self.cost,
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
                self.id == other.id and
                self.name == other.name and
                self.attachment == other.attachment and
                self.reasoning == other.reasoning and
                self.tool_call == other.tool_call and
                self.release_date == other.release_date and
                self.last_updated == other.last_updated and
                self.modalities == other.modalities and
                self.open_weights == other.open_weights and
                self.limit == other.limit and
                self.family == other.family and
                self.interleaved == other.interleaved and
                self.structured_output == other.structured_output and
                self.temperature == other.temperature and
                self.knowledge == other.knowledge and
                self.status == other.status and
                self.experimental == other.experimental and
                self.provider == other.provider and
                self.cost == other.cost and
                self.x == other.x
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'id',
            'name',
            'attachment',
            'reasoning',
            'tool_call',
            'release_date',
            'last_updated',
            'modalities',
            'open_weights',
            'limit',
            'family',
            'interleaved',
            'structured_output',
            'temperature',
            'knowledge',
            'status',
            'experimental',
            'provider',
            'cost',
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
            'id',
            'name',
            'attachment',
            'reasoning',
            'tool_call',
            'release_date',
            'last_updated',
            'modalities',
            'open_weights',
            'limit',
            'family',
            'interleaved',
            'structured_output',
            'temperature',
            'knowledge',
            'status',
            'experimental',
            'provider',
            'cost',
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
                self.id,
                self.name,
                self.attachment,
                self.reasoning,
                self.tool_call,
                self.release_date,
                self.last_updated,
                self.modalities,
                self.open_weights,
                self.limit,
                self.family,
                self.interleaved,
                self.structured_output,
                self.temperature,
                self.knowledge,
                self.status,
                self.experimental,
                self.provider,
                self.cost,
                self.x,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            id: __dataclass__init__fields__00__annotation,
            name: __dataclass__init__fields__01__annotation,
            attachment: __dataclass__init__fields__02__annotation,
            reasoning: __dataclass__init__fields__03__annotation,
            tool_call: __dataclass__init__fields__04__annotation,
            release_date: __dataclass__init__fields__05__annotation,
            last_updated: __dataclass__init__fields__06__annotation,
            modalities: __dataclass__init__fields__07__annotation,
            open_weights: __dataclass__init__fields__08__annotation,
            limit: __dataclass__init__fields__09__annotation,
            family: __dataclass__init__fields__10__annotation = __dataclass__init__fields__10__default,
            interleaved: __dataclass__init__fields__11__annotation = __dataclass__init__fields__11__default,
            structured_output: __dataclass__init__fields__12__annotation = __dataclass__init__fields__12__default,
            temperature: __dataclass__init__fields__13__annotation = __dataclass__init__fields__13__default,
            knowledge: __dataclass__init__fields__14__annotation = __dataclass__init__fields__14__default,
            status: __dataclass__init__fields__15__annotation = __dataclass__init__fields__15__default,
            experimental: __dataclass__init__fields__16__annotation = __dataclass__init__fields__16__default,
            provider: __dataclass__init__fields__17__annotation = __dataclass__init__fields__17__default,
            cost: __dataclass__init__fields__18__annotation = __dataclass__init__fields__18__default,
            x: __dataclass__init__fields__19__annotation = __dataclass__init__fields__19__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'attachment', attachment)
            __dataclass__object_setattr(self, 'reasoning', reasoning)
            __dataclass__object_setattr(self, 'tool_call', tool_call)
            __dataclass__object_setattr(self, 'release_date', release_date)
            __dataclass__object_setattr(self, 'last_updated', last_updated)
            __dataclass__object_setattr(self, 'modalities', modalities)
            __dataclass__object_setattr(self, 'open_weights', open_weights)
            __dataclass__object_setattr(self, 'limit', limit)
            __dataclass__object_setattr(self, 'family', family)
            __dataclass__object_setattr(self, 'interleaved', interleaved)
            __dataclass__object_setattr(self, 'structured_output', structured_output)
            __dataclass__object_setattr(self, 'temperature', temperature)
            __dataclass__object_setattr(self, 'knowledge', knowledge)
            __dataclass__object_setattr(self, 'status', status)
            __dataclass__object_setattr(self, 'experimental', experimental)
            __dataclass__object_setattr(self, 'provider', provider)
            __dataclass__object_setattr(self, 'cost', cost)
            __dataclass__object_setattr(self, 'x', x)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"id={self.id!r}")
            parts.append(f"name={self.name!r}")
            parts.append(f"attachment={self.attachment!r}")
            parts.append(f"reasoning={self.reasoning!r}")
            parts.append(f"tool_call={self.tool_call!r}")
            parts.append(f"release_date={self.release_date!r}")
            parts.append(f"last_updated={self.last_updated!r}")
            parts.append(f"modalities={self.modalities!r}")
            parts.append(f"open_weights={self.open_weights!r}")
            parts.append(f"limit={self.limit!r}")
            parts.append(f"family={self.family!r}")
            parts.append(f"interleaved={self.interleaved!r}")
            parts.append(f"structured_output={self.structured_output!r}")
            parts.append(f"temperature={self.temperature!r}")
            parts.append(f"knowledge={self.knowledge!r}")
            parts.append(f"status={self.status!r}")
            parts.append(f"experimental={self.experimental!r}")
            parts.append(f"provider={self.provider!r}")
            parts.append(f"cost={self.cost!r}")
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

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('input', 'output', 'reasoning', 'cache_read', 'cache_write', 'input_audio', 'outpu"
        "t_audio', 'x')), EqPlan(fields=('input', 'output', 'reasoning', 'cache_read', 'cache_write', 'input_audio', 'o"
        "utput_audio', 'x')), FrozenPlan(fields=('input', 'output', 'reasoning', 'cache_read', 'cache_write', 'input_au"
        "dio', 'output_audio', 'x'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('input', 'output"
        "', 'reasoning', 'cache_read', 'cache_write', 'input_audio', 'output_audio', 'x'), cache=False), InitPlan(field"
        "s=(InitPlan.Field(name='input', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_facto"
        "ry=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None"
        "), InitPlan.Field(name='output', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_fact"
        "ory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=Non"
        "e), InitPlan.Field(name='reasoning', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='in"
        "it.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce="
        "None, validate=None, check_type=None), InitPlan.Field(name='cache_read', annotation=OpRef(name='init.fields.3."
        "annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, fi"
        "eld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='cache_write', "
        "annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_factor"
        "y=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)"
        ", InitPlan.Field(name='input_audio', annotation=OpRef(name='init.fields.5.annotation'), default=OpRef(name='in"
        "it.fields.5.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce="
        "None, validate=None, check_type=None), InitPlan.Field(name='output_audio', annotation=OpRef(name='init.fields."
        "6.annotation'), default=OpRef(name='init.fields.6.default'), default_factory=None, init=True, override=False, "
        "field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='x', annotati"
        "on=OpRef(name='init.fields.7.annotation'), default=OpRef(name='init.fields.7.default'), default_factory=None, "
        "init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_"
        "param='self', std_params=(), kw_only_params=('input', 'output', 'reasoning', 'cache_read', 'cache_write', 'inp"
        "ut_audio', 'output_audio', 'x'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()"
        "), ReprPlan(fields=(ReprPlan.Field(name='input', kw_only=True, fn=None), ReprPlan.Field(name='output', kw_only"
        "=True, fn=None), ReprPlan.Field(name='reasoning', kw_only=True, fn=None), ReprPlan.Field(name='cache_read', kw"
        "_only=True, fn=None), ReprPlan.Field(name='cache_write', kw_only=True, fn=None), ReprPlan.Field(name='input_au"
        "dio', kw_only=True, fn=None), ReprPlan.Field(name='output_audio', kw_only=True, fn=None), ReprPlan.Field(name="
        "'x', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='64f89442bfd33e1438b2681bfdab9337ee7c2477',
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
    ),
    cls_names=(
        ('ommlds.models.types', 'Cost'),
    ),
)
def _process_dataclass__64f89442bfd33e1438b2681bfdab9337ee7c2477():
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
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
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
                reasoning=self.reasoning,
                cache_read=self.cache_read,
                cache_write=self.cache_write,
                input_audio=self.input_audio,
                output_audio=self.output_audio,
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
                self.input == other.input and
                self.output == other.output and
                self.reasoning == other.reasoning and
                self.cache_read == other.cache_read and
                self.cache_write == other.cache_write and
                self.input_audio == other.input_audio and
                self.output_audio == other.output_audio and
                self.x == other.x
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'input',
            'output',
            'reasoning',
            'cache_read',
            'cache_write',
            'input_audio',
            'output_audio',
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
            'input',
            'output',
            'reasoning',
            'cache_read',
            'cache_write',
            'input_audio',
            'output_audio',
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
                self.input,
                self.output,
                self.reasoning,
                self.cache_read,
                self.cache_write,
                self.input_audio,
                self.output_audio,
                self.x,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            input: __dataclass__init__fields__0__annotation,
            output: __dataclass__init__fields__1__annotation,
            reasoning: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            cache_read: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            cache_write: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            input_audio: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
            output_audio: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
            x: __dataclass__init__fields__7__annotation = __dataclass__init__fields__7__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'input', input)
            __dataclass__object_setattr(self, 'output', output)
            __dataclass__object_setattr(self, 'reasoning', reasoning)
            __dataclass__object_setattr(self, 'cache_read', cache_read)
            __dataclass__object_setattr(self, 'cache_write', cache_write)
            __dataclass__object_setattr(self, 'input_audio', input_audio)
            __dataclass__object_setattr(self, 'output_audio', output_audio)
            __dataclass__object_setattr(self, 'x', x)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"input={self.input!r}")
            parts.append(f"output={self.output!r}")
            parts.append(f"reasoning={self.reasoning!r}")
            parts.append(f"cache_read={self.cache_read!r}")
            parts.append(f"cache_write={self.cache_write!r}")
            parts.append(f"input_audio={self.input_audio!r}")
            parts.append(f"output_audio={self.output_audio!r}")
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

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('input', 'output', 'reasoning', 'cache_read', 'cache_write', 'input_audio', 'outpu"
        "t_audio', 'x', 'tier')), EqPlan(fields=('input', 'output', 'reasoning', 'cache_read', 'cache_write', 'input_au"
        "dio', 'output_audio', 'x', 'tier')), FrozenPlan(fields=('input', 'output', 'reasoning', 'cache_read', 'cache_w"
        "rite', 'input_audio', 'output_audio', 'x', 'tier'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', "
        "fields=('input', 'output', 'reasoning', 'cache_read', 'cache_write', 'input_audio', 'output_audio', 'x', 'tier"
        "'), cache=False), InitPlan(fields=(InitPlan.Field(name='input', annotation=OpRef(name='init.fields.0.annotatio"
        "n'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None"
        ", validate=None, check_type=None), InitPlan.Field(name='output', annotation=OpRef(name='init.fields.1.annotati"
        "on'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=Non"
        "e, validate=None, check_type=None), InitPlan.Field(name='reasoning', annotation=OpRef(name='init.fields.2.anno"
        "tation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_"
        "type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='cache_read', annot"
        "ation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=Non"
        "e, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), Ini"
        "tPlan.Field(name='cache_write', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fi"
        "elds.4.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None,"
        " validate=None, check_type=None), InitPlan.Field(name='input_audio', annotation=OpRef(name='init.fields.5.anno"
        "tation'), default=OpRef(name='init.fields.5.default'), default_factory=None, init=True, override=False, field_"
        "type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='output_audio', ann"
        "otation=OpRef(name='init.fields.6.annotation'), default=OpRef(name='init.fields.6.default'), default_factory=N"
        "one, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), I"
        "nitPlan.Field(name='x', annotation=OpRef(name='init.fields.7.annotation'), default=OpRef(name='init.fields.7.d"
        "efault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validat"
        "e=None, check_type=None), InitPlan.Field(name='tier', annotation=OpRef(name='init.fields.8.annotation'), defau"
        "lt=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate"
        "=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('input', 'output', 'reasoning', 'c"
        "ache_read', 'cache_write', 'input_audio', 'output_audio', 'x', 'tier'), frozen=True, slots=False, post_init_pa"
        "rams=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='input', kw_only=True, fn=None)"
        ", ReprPlan.Field(name='output', kw_only=True, fn=None), ReprPlan.Field(name='reasoning', kw_only=True, fn=None"
        "), ReprPlan.Field(name='cache_read', kw_only=True, fn=None), ReprPlan.Field(name='cache_write', kw_only=True, "
        "fn=None), ReprPlan.Field(name='input_audio', kw_only=True, fn=None), ReprPlan.Field(name='output_audio', kw_on"
        "ly=True, fn=None), ReprPlan.Field(name='x', kw_only=True, fn=None), ReprPlan.Field(name='tier', kw_only=True, "
        "fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='7ec1e3d9c4cc2cf01c46d8e5290bb64a7e065e13',
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
    ),
    cls_names=(
        ('ommlds.models.types', 'CostTier'),
    ),
)
def _process_dataclass__7ec1e3d9c4cc2cf01c46d8e5290bb64a7e065e13():
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
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
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
                reasoning=self.reasoning,
                cache_read=self.cache_read,
                cache_write=self.cache_write,
                input_audio=self.input_audio,
                output_audio=self.output_audio,
                x=self.x,
                tier=self.tier,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
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
                self.reasoning == other.reasoning and
                self.cache_read == other.cache_read and
                self.cache_write == other.cache_write and
                self.input_audio == other.input_audio and
                self.output_audio == other.output_audio and
                self.x == other.x and
                self.tier == other.tier
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'input',
            'output',
            'reasoning',
            'cache_read',
            'cache_write',
            'input_audio',
            'output_audio',
            'x',
            'tier',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'reasoning',
            'cache_read',
            'cache_write',
            'input_audio',
            'output_audio',
            'x',
            'tier',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
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
                self.reasoning,
                self.cache_read,
                self.cache_write,
                self.input_audio,
                self.output_audio,
                self.x,
                self.tier,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            input: __dataclass__init__fields__0__annotation,
            output: __dataclass__init__fields__1__annotation,
            reasoning: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            cache_read: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            cache_write: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            input_audio: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
            output_audio: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
            x: __dataclass__init__fields__7__annotation = __dataclass__init__fields__7__default,
            tier: __dataclass__init__fields__8__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'input', input)
            __dataclass__object_setattr(self, 'output', output)
            __dataclass__object_setattr(self, 'reasoning', reasoning)
            __dataclass__object_setattr(self, 'cache_read', cache_read)
            __dataclass__object_setattr(self, 'cache_write', cache_write)
            __dataclass__object_setattr(self, 'input_audio', input_audio)
            __dataclass__object_setattr(self, 'output_audio', output_audio)
            __dataclass__object_setattr(self, 'x', x)
            __dataclass__object_setattr(self, 'tier', tier)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"input={self.input!r}")
            parts.append(f"output={self.output!r}")
            parts.append(f"reasoning={self.reasoning!r}")
            parts.append(f"cache_read={self.cache_read!r}")
            parts.append(f"cache_write={self.cache_write!r}")
            parts.append(f"input_audio={self.input_audio!r}")
            parts.append(f"output_audio={self.output_audio!r}")
            parts.append(f"x={self.x!r}")
            parts.append(f"tier={self.tier!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('size', 'type', 'x')), EqPlan(fields=('size', 'type', 'x')), FrozenPlan(fields=('s"
        "ize', 'type', 'x'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('size', 'type', 'x'), ca"
        "che=False), InitPlan(fields=(InitPlan.Field(name='size', annotation=OpRef(name='init.fields.0.annotation'), de"
        "fault=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valid"
        "ate=None, check_type=None), InitPlan.Field(name='type', annotation=OpRef(name='init.fields.1.annotation'), def"
        "ault=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldTyp"
        "e.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='x', annotation=OpRef(name='init"
        ".fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override"
        "=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_p"
        "arams=(), kw_only_params=('size', 'type', 'x'), frozen=True, slots=False, post_init_params=None, init_fns=(), "
        "validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='size', kw_only=True, fn=None), ReprPlan.Field(name='ty"
        "pe', kw_only=True, fn=None), ReprPlan.Field(name='x', kw_only=True, fn=None)), id=False, terse=False, default_"
        "fn=None)))"
    ),
    plan_repr_sha1='abb0d290b2c97ca669a2f9ca5aa3ecb68302f6dd',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.models.types', 'CostTierTier'),
    ),
)
def _process_dataclass__abb0d290b2c97ca669a2f9ca5aa3ecb68302f6dd():
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
                size=self.size,
                type=self.type,
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
                self.size == other.size and
                self.type == other.type and
                self.x == other.x
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'size',
            'type',
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
            'size',
            'type',
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
                self.size,
                self.type,
                self.x,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            size: __dataclass__init__fields__0__annotation,
            type: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            x: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'size', size)
            __dataclass__object_setattr(self, 'type', type)
            __dataclass__object_setattr(self, 'x', x)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"size={self.size!r}")
            parts.append(f"type={self.type!r}")
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

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('modes', 'x')), EqPlan(fields=('modes', 'x')), FrozenPlan(fields=('modes', 'x'), a"
        "llow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('modes', 'x'), cache=False), InitPlan(fields="
        "(InitPlan.Field(name='modes', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fiel"
        "ds.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, v"
        "alidate=None, check_type=None), InitPlan.Field(name='x', annotation=OpRef(name='init.fields.1.annotation'), de"
        "fault=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldTy"
        "pe.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=("
        "'modes', 'x'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields"
        "=(ReprPlan.Field(name='modes', kw_only=True, fn=None), ReprPlan.Field(name='x', kw_only=True, fn=None)), id=Fa"
        "lse, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='8a8240cd6f4d13bab2dd761fd7aa774036fa1dc9',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.models.types', 'Experimental'),
    ),
)
def _process_dataclass__8a8240cd6f4d13bab2dd761fd7aa774036fa1dc9():
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
                modes=self.modes,
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
                self.modes == other.modes and
                self.x == other.x
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'modes',
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
            'modes',
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
                self.modes,
                self.x,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            modes: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            x: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'modes', modes)
            __dataclass__object_setattr(self, 'x', x)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"modes={self.modes!r}")
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

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('cost', 'provider', 'x')), EqPlan(fields=('cost', 'provider', 'x')), FrozenPlan(fi"
        "elds=('cost', 'provider', 'x'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('cost', 'pro"
        "vider', 'x'), cache=False), InitPlan(fields=(InitPlan.Field(name='cost', annotation=OpRef(name='init.fields.0."
        "annotation'), default=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, fi"
        "eld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='provider', ann"
        "otation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=N"
        "one, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), I"
        "nitPlan.Field(name='x', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.d"
        "efault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validat"
        "e=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('cost', 'provider', 'x'), frozen="
        "True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name="
        "'cost', kw_only=True, fn=None), ReprPlan.Field(name='provider', kw_only=True, fn=None), ReprPlan.Field(name='x"
        "', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='578691179d0b5f27fc9f73ed1a4711e2ba97310f',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.models.types', 'ExperimentalMode'),
    ),
)
def _process_dataclass__578691179d0b5f27fc9f73ed1a4711e2ba97310f():
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
                cost=self.cost,
                provider=self.provider,
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
                self.cost == other.cost and
                self.provider == other.provider and
                self.x == other.x
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'cost',
            'provider',
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
            'cost',
            'provider',
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
                self.cost,
                self.provider,
                self.x,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            cost: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            provider: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            x: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'cost', cost)
            __dataclass__object_setattr(self, 'provider', provider)
            __dataclass__object_setattr(self, 'x', x)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"cost={self.cost!r}")
            parts.append(f"provider={self.provider!r}")
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

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('body', 'headers', 'x')), EqPlan(fields=('body', 'headers', 'x')), FrozenPlan(fiel"
        "ds=('body', 'headers', 'x'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('body', 'header"
        "s', 'x'), cache=False), InitPlan(fields=(InitPlan.Field(name='body', annotation=OpRef(name='init.fields.0.anno"
        "tation'), default=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_"
        "type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='headers', annotati"
        "on=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, "
        "init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPl"
        "an.Field(name='x', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.defaul"
        "t'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=Non"
        "e, check_type=None)), self_param='self', std_params=(), kw_only_params=('body', 'headers', 'x'), frozen=True, "
        "slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='body'"
        ", kw_only=True, fn=None), ReprPlan.Field(name='headers', kw_only=True, fn=None), ReprPlan.Field(name='x', kw_o"
        "nly=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='5bca72421d06a9eead64a5df90e3d7f793cade1c',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.models.types', 'ExperimentalModeProvider'),
    ),
)
def _process_dataclass__5bca72421d06a9eead64a5df90e3d7f793cade1c():
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
                body=self.body,
                headers=self.headers,
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
                self.body == other.body and
                self.headers == other.headers and
                self.x == other.x
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'body',
            'headers',
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
            'body',
            'headers',
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
                self.body,
                self.headers,
                self.x,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            body: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            headers: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            x: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'body', body)
            __dataclass__object_setattr(self, 'headers', headers)
            __dataclass__object_setattr(self, 'x', x)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"body={self.body!r}")
            parts.append(f"headers={self.headers!r}")
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

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('field', 'x')), EqPlan(fields=('field', 'x')), FrozenPlan(fields=('field', 'x'), a"
        "llow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('field', 'x'), cache=False), InitPlan(fields="
        "(InitPlan.Field(name='field', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory"
        "=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),"
        " InitPlan.Field(name='x', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1"
        ".default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valid"
        "ate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('field', 'x'), frozen=True, slo"
        "ts=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='field', "
        "kw_only=True, fn=None), ReprPlan.Field(name='x', kw_only=True, fn=None)), id=False, terse=False, default_fn=No"
        "ne)))"
    ),
    plan_repr_sha1='11739faa37f665b4304128938db3eafd7a7ca0ce',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.models.types', 'Interleaved'),
    ),
)
def _process_dataclass__11739faa37f665b4304128938db3eafd7a7ca0ce():
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
                field=self.field,
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
                self.field == other.field and
                self.x == other.x
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'field',
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
            'field',
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
                self.field,
                self.x,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            field: __dataclass__init__fields__0__annotation,
            x: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'field', field)
            __dataclass__object_setattr(self, 'x', x)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"field={self.field!r}")
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

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('context', 'output', 'input', 'x')), EqPlan(fields=('context', 'output', 'input', "
        "'x')), FrozenPlan(fields=('context', 'output', 'input', 'x'), allow_dynamic_dunder_attrs=False), HashPlan(acti"
        "on='add', fields=('context', 'output', 'input', 'x'), cache=False), InitPlan(fields=(InitPlan.Field(name='cont"
        "ext', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, overri"
        "de=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='ou"
        "tput', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, overr"
        "ide=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='i"
        "nput', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default"
        "_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_typ"
        "e=None), InitPlan.Field(name='x', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init."
        "fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=Non"
        "e, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('context', 'output', 'i"
        "nput', 'x'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=("
        "ReprPlan.Field(name='context', kw_only=True, fn=None), ReprPlan.Field(name='output', kw_only=True, fn=None), R"
        "eprPlan.Field(name='input', kw_only=True, fn=None), ReprPlan.Field(name='x', kw_only=True, fn=None)), id=False"
        ", terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='6e1be5172133ea88a1c54f987967e78890eaab91',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ommlds.models.types', 'Limit'),
    ),
)
def _process_dataclass__6e1be5172133ea88a1c54f987967e78890eaab91():
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
                context=self.context,
                output=self.output,
                input=self.input,
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
                self.context == other.context and
                self.output == other.output and
                self.input == other.input and
                self.x == other.x
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'context',
            'output',
            'input',
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
            'context',
            'output',
            'input',
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
                self.context,
                self.output,
                self.input,
                self.x,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            context: __dataclass__init__fields__0__annotation,
            output: __dataclass__init__fields__1__annotation,
            input: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            x: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'context', context)
            __dataclass__object_setattr(self, 'output', output)
            __dataclass__object_setattr(self, 'input', input)
            __dataclass__object_setattr(self, 'x', x)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"context={self.context!r}")
            parts.append(f"output={self.output!r}")
            parts.append(f"input={self.input!r}")
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

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('input', 'output', 'x')), EqPlan(fields=('input', 'output', 'x')), FrozenPlan(fiel"
        "ds=('input', 'output', 'x'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('input', 'outpu"
        "t', 'x'), cache=False), InitPlan(fields=(InitPlan.Field(name='input', annotation=OpRef(name='init.fields.0.ann"
        "otation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerc"
        "e=None, validate=None, check_type=None), InitPlan.Field(name='output', annotation=OpRef(name='init.fields.1.an"
        "notation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coer"
        "ce=None, validate=None, check_type=None), InitPlan.Field(name='x', annotation=OpRef(name='init.fields.2.annota"
        "tion'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_ty"
        "pe=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_onl"
        "y_params=('input', 'output', 'x'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns="
        "()), ReprPlan(fields=(ReprPlan.Field(name='input', kw_only=True, fn=None), ReprPlan.Field(name='output', kw_on"
        "ly=True, fn=None), ReprPlan.Field(name='x', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='0474babc2a319e1f5b6ea8ccbb0d38d418c74e8a',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.models.types', 'Modalities'),
    ),
)
def _process_dataclass__0474babc2a319e1f5b6ea8ccbb0d38d418c74e8a():
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
                input=self.input,
                output=self.output,
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
                self.input == other.input and
                self.output == other.output and
                self.x == other.x
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'input',
            'output',
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
            'input',
            'output',
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
                self.input,
                self.output,
                self.x,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            input: __dataclass__init__fields__0__annotation,
            output: __dataclass__init__fields__1__annotation,
            x: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'input', input)
            __dataclass__object_setattr(self, 'output', output)
            __dataclass__object_setattr(self, 'x', x)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"input={self.input!r}")
            parts.append(f"output={self.output!r}")
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

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('id', 'name', 'attachment', 'reasoning', 'tool_call', 'release_date', 'last_update"
        "d', 'modalities', 'open_weights', 'limit', 'family', 'interleaved', 'structured_output', 'temperature', 'knowl"
        "edge', 'status', 'experimental', 'provider')), EqPlan(fields=('id', 'name', 'attachment', 'reasoning', 'tool_c"
        "all', 'release_date', 'last_updated', 'modalities', 'open_weights', 'limit', 'family', 'interleaved', 'structu"
        "red_output', 'temperature', 'knowledge', 'status', 'experimental', 'provider')), FrozenPlan(fields=('id', 'nam"
        "e', 'attachment', 'reasoning', 'tool_call', 'release_date', 'last_updated', 'modalities', 'open_weights', 'lim"
        "it', 'family', 'interleaved', 'structured_output', 'temperature', 'knowledge', 'status', 'experimental', 'prov"
        "ider'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('id', 'name', 'attachment', 'reasoni"
        "ng', 'tool_call', 'release_date', 'last_updated', 'modalities', 'open_weights', 'limit', 'family', 'interleave"
        "d', 'structured_output', 'temperature', 'knowledge', 'status', 'experimental', 'provider'), cache=False), Init"
        "Plan(fields=(InitPlan.Field(name='id', annotation=OpRef(name='init.fields.00.annotation'), default=None, defau"
        "lt_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_t"
        "ype=None), InitPlan.Field(name='name', annotation=OpRef(name='init.fields.01.annotation'), default=None, defau"
        "lt_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_t"
        "ype=None), InitPlan.Field(name='attachment', annotation=OpRef(name='init.fields.02.annotation'), default=None,"
        " default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, c"
        "heck_type=None), InitPlan.Field(name='reasoning', annotation=OpRef(name='init.fields.03.annotation'), default="
        "None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=No"
        "ne, check_type=None), InitPlan.Field(name='tool_call', annotation=OpRef(name='init.fields.04.annotation'), def"
        "ault=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valida"
        "te=None, check_type=None), InitPlan.Field(name='release_date', annotation=OpRef(name='init.fields.05.annotatio"
        "n'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None"
        ", validate=None, check_type=None), InitPlan.Field(name='last_updated', annotation=OpRef(name='init.fields.06.a"
        "nnotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coe"
        "rce=None, validate=None, check_type=None), InitPlan.Field(name='modalities', annotation=OpRef(name='init.field"
        "s.07.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANC"
        "E, coerce=None, validate=None, check_type=None), InitPlan.Field(name='open_weights', annotation=OpRef(name='in"
        "it.fields.08.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType"
        ".INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='limit', annotation=OpRef(name='i"
        "nit.fields.09.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldTyp"
        "e.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='family', annotation=OpRef(name="
        "'init.fields.10.annotation'), default=OpRef(name='init.fields.10.default'), default_factory=None, init=True, o"
        "verride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(nam"
        "e='interleaved', annotation=OpRef(name='init.fields.11.annotation'), default=OpRef(name='init.fields.11.defaul"
        "t'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=Non"
        "e, check_type=None), InitPlan.Field(name='structured_output', annotation=OpRef(name='init.fields.12.annotation"
        "'), default=OpRef(name='init.fields.12.default'), default_factory=None, init=True, override=False, field_type="
        "FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='temperature', annotatio"
        "n=OpRef(name='init.fields.13.annotation'), default=OpRef(name='init.fields.13.default'), default_factory=None,"
        " init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitP"
        "lan.Field(name='knowledge', annotation=OpRef(name='init.fields.14.annotation'), default=OpRef(name='init.field"
        "s.14.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, v"
        "alidate=None, check_type=None), InitPlan.Field(name='status', annotation=OpRef(name='init.fields.15.annotation"
        "'), default=OpRef(name='init.fields.15.default'), default_factory=None, init=True, override=False, field_type="
        "FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='experimental', annotati"
        "on=OpRef(name='init.fields.16.annotation'), default=OpRef(name='init.fields.16.default'), default_factory=None"
        ", init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), Init"
        "Plan.Field(name='provider', annotation=OpRef(name='init.fields.17.annotation'), default=OpRef(name='init.field"
        "s.17.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, v"
        "alidate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('id', 'name', 'attachment',"
        " 'reasoning', 'tool_call', 'release_date', 'last_updated', 'modalities', 'open_weights', 'limit', 'family', 'i"
        "nterleaved', 'structured_output', 'temperature', 'knowledge', 'status', 'experimental', 'provider'), frozen=Tr"
        "ue, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='i"
        "d', kw_only=True, fn=None), ReprPlan.Field(name='name', kw_only=True, fn=None), ReprPlan.Field(name='attachmen"
        "t', kw_only=True, fn=None), ReprPlan.Field(name='reasoning', kw_only=True, fn=None), ReprPlan.Field(name='tool"
        "_call', kw_only=True, fn=None), ReprPlan.Field(name='release_date', kw_only=True, fn=None), ReprPlan.Field(nam"
        "e='last_updated', kw_only=True, fn=None), ReprPlan.Field(name='modalities', kw_only=True, fn=None), ReprPlan.F"
        "ield(name='open_weights', kw_only=True, fn=None), ReprPlan.Field(name='limit', kw_only=True, fn=None), ReprPla"
        "n.Field(name='family', kw_only=True, fn=None), ReprPlan.Field(name='interleaved', kw_only=True, fn=None), Repr"
        "Plan.Field(name='structured_output', kw_only=True, fn=None), ReprPlan.Field(name='temperature', kw_only=True, "
        "fn=None), ReprPlan.Field(name='knowledge', kw_only=True, fn=None), ReprPlan.Field(name='status', kw_only=True,"
        " fn=None), ReprPlan.Field(name='experimental', kw_only=True, fn=None), ReprPlan.Field(name='provider', kw_only"
        "=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='362664056191c441c1d0eaf1f28189295d01b0d6',
    op_ref_idents=(
        '__dataclass__init__fields__00__annotation',
        '__dataclass__init__fields__01__annotation',
        '__dataclass__init__fields__02__annotation',
        '__dataclass__init__fields__03__annotation',
        '__dataclass__init__fields__04__annotation',
        '__dataclass__init__fields__05__annotation',
        '__dataclass__init__fields__06__annotation',
        '__dataclass__init__fields__07__annotation',
        '__dataclass__init__fields__08__annotation',
        '__dataclass__init__fields__09__annotation',
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
    ),
    cls_names=(
        ('ommlds.models.types', 'ModelBase'),
    ),
)
def _process_dataclass__362664056191c441c1d0eaf1f28189295d01b0d6():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__00__annotation,
        __dataclass__init__fields__01__annotation,
        __dataclass__init__fields__02__annotation,
        __dataclass__init__fields__03__annotation,
        __dataclass__init__fields__04__annotation,
        __dataclass__init__fields__05__annotation,
        __dataclass__init__fields__06__annotation,
        __dataclass__init__fields__07__annotation,
        __dataclass__init__fields__08__annotation,
        __dataclass__init__fields__09__annotation,
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
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
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
                attachment=self.attachment,
                reasoning=self.reasoning,
                tool_call=self.tool_call,
                release_date=self.release_date,
                last_updated=self.last_updated,
                modalities=self.modalities,
                open_weights=self.open_weights,
                limit=self.limit,
                family=self.family,
                interleaved=self.interleaved,
                structured_output=self.structured_output,
                temperature=self.temperature,
                knowledge=self.knowledge,
                status=self.status,
                experimental=self.experimental,
                provider=self.provider,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
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
                self.attachment == other.attachment and
                self.reasoning == other.reasoning and
                self.tool_call == other.tool_call and
                self.release_date == other.release_date and
                self.last_updated == other.last_updated and
                self.modalities == other.modalities and
                self.open_weights == other.open_weights and
                self.limit == other.limit and
                self.family == other.family and
                self.interleaved == other.interleaved and
                self.structured_output == other.structured_output and
                self.temperature == other.temperature and
                self.knowledge == other.knowledge and
                self.status == other.status and
                self.experimental == other.experimental and
                self.provider == other.provider
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'id',
            'name',
            'attachment',
            'reasoning',
            'tool_call',
            'release_date',
            'last_updated',
            'modalities',
            'open_weights',
            'limit',
            'family',
            'interleaved',
            'structured_output',
            'temperature',
            'knowledge',
            'status',
            'experimental',
            'provider',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'attachment',
            'reasoning',
            'tool_call',
            'release_date',
            'last_updated',
            'modalities',
            'open_weights',
            'limit',
            'family',
            'interleaved',
            'structured_output',
            'temperature',
            'knowledge',
            'status',
            'experimental',
            'provider',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
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
                self.attachment,
                self.reasoning,
                self.tool_call,
                self.release_date,
                self.last_updated,
                self.modalities,
                self.open_weights,
                self.limit,
                self.family,
                self.interleaved,
                self.structured_output,
                self.temperature,
                self.knowledge,
                self.status,
                self.experimental,
                self.provider,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            id: __dataclass__init__fields__00__annotation,
            name: __dataclass__init__fields__01__annotation,
            attachment: __dataclass__init__fields__02__annotation,
            reasoning: __dataclass__init__fields__03__annotation,
            tool_call: __dataclass__init__fields__04__annotation,
            release_date: __dataclass__init__fields__05__annotation,
            last_updated: __dataclass__init__fields__06__annotation,
            modalities: __dataclass__init__fields__07__annotation,
            open_weights: __dataclass__init__fields__08__annotation,
            limit: __dataclass__init__fields__09__annotation,
            family: __dataclass__init__fields__10__annotation = __dataclass__init__fields__10__default,
            interleaved: __dataclass__init__fields__11__annotation = __dataclass__init__fields__11__default,
            structured_output: __dataclass__init__fields__12__annotation = __dataclass__init__fields__12__default,
            temperature: __dataclass__init__fields__13__annotation = __dataclass__init__fields__13__default,
            knowledge: __dataclass__init__fields__14__annotation = __dataclass__init__fields__14__default,
            status: __dataclass__init__fields__15__annotation = __dataclass__init__fields__15__default,
            experimental: __dataclass__init__fields__16__annotation = __dataclass__init__fields__16__default,
            provider: __dataclass__init__fields__17__annotation = __dataclass__init__fields__17__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'attachment', attachment)
            __dataclass__object_setattr(self, 'reasoning', reasoning)
            __dataclass__object_setattr(self, 'tool_call', tool_call)
            __dataclass__object_setattr(self, 'release_date', release_date)
            __dataclass__object_setattr(self, 'last_updated', last_updated)
            __dataclass__object_setattr(self, 'modalities', modalities)
            __dataclass__object_setattr(self, 'open_weights', open_weights)
            __dataclass__object_setattr(self, 'limit', limit)
            __dataclass__object_setattr(self, 'family', family)
            __dataclass__object_setattr(self, 'interleaved', interleaved)
            __dataclass__object_setattr(self, 'structured_output', structured_output)
            __dataclass__object_setattr(self, 'temperature', temperature)
            __dataclass__object_setattr(self, 'knowledge', knowledge)
            __dataclass__object_setattr(self, 'status', status)
            __dataclass__object_setattr(self, 'experimental', experimental)
            __dataclass__object_setattr(self, 'provider', provider)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"id={self.id!r}")
            parts.append(f"name={self.name!r}")
            parts.append(f"attachment={self.attachment!r}")
            parts.append(f"reasoning={self.reasoning!r}")
            parts.append(f"tool_call={self.tool_call!r}")
            parts.append(f"release_date={self.release_date!r}")
            parts.append(f"last_updated={self.last_updated!r}")
            parts.append(f"modalities={self.modalities!r}")
            parts.append(f"open_weights={self.open_weights!r}")
            parts.append(f"limit={self.limit!r}")
            parts.append(f"family={self.family!r}")
            parts.append(f"interleaved={self.interleaved!r}")
            parts.append(f"structured_output={self.structured_output!r}")
            parts.append(f"temperature={self.temperature!r}")
            parts.append(f"knowledge={self.knowledge!r}")
            parts.append(f"status={self.status!r}")
            parts.append(f"experimental={self.experimental!r}")
            parts.append(f"provider={self.provider!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('npm', 'api', 'shape', 'body', 'headers', 'x')), EqPlan(fields=('npm', 'api', 'sha"
        "pe', 'body', 'headers', 'x')), FrozenPlan(fields=('npm', 'api', 'shape', 'body', 'headers', 'x'), allow_dynami"
        "c_dunder_attrs=False), HashPlan(action='add', fields=('npm', 'api', 'shape', 'body', 'headers', 'x'), cache=Fa"
        "lse), InitPlan(fields=(InitPlan.Field(name='npm', annotation=OpRef(name='init.fields.0.annotation'), default=O"
        "pRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INST"
        "ANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='api', annotation=OpRef(name='init.fie"
        "lds.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=Fal"
        "se, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='shape', "
        "annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factor"
        "y=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)"
        ", InitPlan.Field(name='body', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fiel"
        "ds.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, v"
        "alidate=None, check_type=None), InitPlan.Field(name='headers', annotation=OpRef(name='init.fields.4.annotation"
        "'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, override=False, field_type=F"
        "ieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='x', annotation=OpRef(nam"
        "e='init.fields.5.annotation'), default=OpRef(name='init.fields.5.default'), default_factory=None, init=True, o"
        "verride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self'"
        ", std_params=(), kw_only_params=('npm', 'api', 'shape', 'body', 'headers', 'x'), frozen=True, slots=False, pos"
        "t_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='npm', kw_only=True, f"
        "n=None), ReprPlan.Field(name='api', kw_only=True, fn=None), ReprPlan.Field(name='shape', kw_only=True, fn=None"
        "), ReprPlan.Field(name='body', kw_only=True, fn=None), ReprPlan.Field(name='headers', kw_only=True, fn=None), "
        "ReprPlan.Field(name='x', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='ac4c1e23253918eaca953d4b4b84de7546192c6c',
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
        ('ommlds.models.types', 'ModelProvider'),
    ),
)
def _process_dataclass__ac4c1e23253918eaca953d4b4b84de7546192c6c():
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
                npm=self.npm,
                api=self.api,
                shape=self.shape,
                body=self.body,
                headers=self.headers,
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
                self.npm == other.npm and
                self.api == other.api and
                self.shape == other.shape and
                self.body == other.body and
                self.headers == other.headers and
                self.x == other.x
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'npm',
            'api',
            'shape',
            'body',
            'headers',
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
            'npm',
            'api',
            'shape',
            'body',
            'headers',
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
                self.npm,
                self.api,
                self.shape,
                self.body,
                self.headers,
                self.x,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            npm: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            api: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            shape: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            body: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            headers: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            x: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'npm', npm)
            __dataclass__object_setattr(self, 'api', api)
            __dataclass__object_setattr(self, 'shape', shape)
            __dataclass__object_setattr(self, 'body', body)
            __dataclass__object_setattr(self, 'headers', headers)
            __dataclass__object_setattr(self, 'x', x)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"npm={self.npm!r}")
            parts.append(f"api={self.api!r}")
            parts.append(f"shape={self.shape!r}")
            parts.append(f"body={self.body!r}")
            parts.append(f"headers={self.headers!r}")
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

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('id', 'env', 'npm', 'name', 'doc', 'models', 'api', 'x')), EqPlan(fields=('id', 'e"
        "nv', 'npm', 'name', 'doc', 'models', 'api', 'x')), FrozenPlan(fields=('id', 'env', 'npm', 'name', 'doc', 'mode"
        "ls', 'api', 'x'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('id', 'env', 'npm', 'name'"
        ", 'doc', 'models', 'api', 'x'), cache=False), InitPlan(fields=(InitPlan.Field(name='id', annotation=OpRef(name"
        "='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldT"
        "ype.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='env', annotation=OpRef(name='"
        "init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldTyp"
        "e.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='npm', annotation=OpRef(name='in"
        "it.fields.2.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType."
        "INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='name', annotation=OpRef(name='ini"
        "t.fields.3.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.I"
        "NSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='doc', annotation=OpRef(name='init."
        "fields.4.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INS"
        "TANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='models', annotation=OpRef(name='init"
        ".fields.5.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.IN"
        "STANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='api', annotation=OpRef(name='init.f"
        "ields.6.annotation'), default=OpRef(name='init.fields.6.default'), default_factory=None, init=True, override=F"
        "alse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='x', an"
        "notation=OpRef(name='init.fields.7.annotation'), default=OpRef(name='init.fields.7.default'), default_factory="
        "None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)),"
        " self_param='self', std_params=(), kw_only_params=('id', 'env', 'npm', 'name', 'doc', 'models', 'api', 'x'), f"
        "rozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field"
        "(name='id', kw_only=True, fn=None), ReprPlan.Field(name='env', kw_only=True, fn=None), ReprPlan.Field(name='np"
        "m', kw_only=True, fn=None), ReprPlan.Field(name='name', kw_only=True, fn=None), ReprPlan.Field(name='doc', kw_"
        "only=True, fn=None), ReprPlan.Field(name='models', kw_only=True, fn=None), ReprPlan.Field(name='api', kw_only="
        "True, fn=None), ReprPlan.Field(name='x', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='356396990ceb6d70e1f855edf834fc9410df483a',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__5__annotation',
        '__dataclass__init__fields__6__annotation',
        '__dataclass__init__fields__6__default',
        '__dataclass__init__fields__7__annotation',
        '__dataclass__init__fields__7__default',
    ),
    cls_names=(
        ('ommlds.models.types', 'Provider'),
    ),
)
def _process_dataclass__356396990ceb6d70e1f855edf834fc9410df483a():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__4__annotation,
        __dataclass__init__fields__5__annotation,
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
                env=self.env,
                npm=self.npm,
                name=self.name,
                doc=self.doc,
                models=self.models,
                api=self.api,
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
                self.id == other.id and
                self.env == other.env and
                self.npm == other.npm and
                self.name == other.name and
                self.doc == other.doc and
                self.models == other.models and
                self.api == other.api and
                self.x == other.x
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'id',
            'env',
            'npm',
            'name',
            'doc',
            'models',
            'api',
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
            'id',
            'env',
            'npm',
            'name',
            'doc',
            'models',
            'api',
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
                self.id,
                self.env,
                self.npm,
                self.name,
                self.doc,
                self.models,
                self.api,
                self.x,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            id: __dataclass__init__fields__0__annotation,
            env: __dataclass__init__fields__1__annotation,
            npm: __dataclass__init__fields__2__annotation,
            name: __dataclass__init__fields__3__annotation,
            doc: __dataclass__init__fields__4__annotation,
            models: __dataclass__init__fields__5__annotation,
            api: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
            x: __dataclass__init__fields__7__annotation = __dataclass__init__fields__7__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'env', env)
            __dataclass__object_setattr(self, 'npm', npm)
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'doc', doc)
            __dataclass__object_setattr(self, 'models', models)
            __dataclass__object_setattr(self, 'api', api)
            __dataclass__object_setattr(self, 'x', x)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"id={self.id!r}")
            parts.append(f"env={self.env!r}")
            parts.append(f"npm={self.npm!r}")
            parts.append(f"name={self.name!r}")
            parts.append(f"doc={self.doc!r}")
            parts.append(f"models={self.models!r}")
            parts.append(f"api={self.api!r}")
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

    return _process_dataclass
