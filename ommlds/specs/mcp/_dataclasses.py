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
        "Plans(tup=(CopyPlan(fields=('name', 'arguments')), EqPlan(fields=('name', 'arguments')), FrozenPlan(fields=('j"
        "son_rpc_method_name', 'name', 'arguments'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=("
        "'name', 'arguments'), cache=False), InitPlan(fields=(InitPlan.Field(name='json_rpc_method_name', annotation=Op"
        "Ref(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'), default_factory=None, init="
        "True, override=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.F"
        "ield(name='name', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init="
        "True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fi"
        "eld(name='arguments', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.def"
        "ault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate="
        "None, check_type=None)), self_param='self', std_params=(), kw_only_params=('name', 'arguments'), frozen=True, "
        "slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='name'"
        ", kw_only=True, fn=None), ReprPlan.Field(name='arguments', kw_only=True, fn=None)), id=False, terse=False, def"
        "ault_fn=None)))"
    ),
    plan_repr_sha1='2f03740b99dc8066cfcbcc46b7cb91d872fdef60',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp._marshal', 'CallToolRequest'),
    ),
)
def _process_dataclass__2f03740b99dc8066cfcbcc46b7cb91d872fdef60():
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
                name=self.name,
                arguments=self.arguments,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
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
                self.arguments == other.arguments
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'json_rpc_method_name',
            'name',
            'arguments',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'json_rpc_method_name',
            'name',
            'arguments',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
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
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            name: __dataclass__init__fields__1__annotation,
            arguments: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'arguments', arguments)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"name={self.name!r}")
            parts.append(f"arguments={self.arguments!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('meta_', 'content', 'is_error', 'structured_content')), EqPlan(fields=('meta_', 'c"
        "ontent', 'is_error', 'structured_content')), FrozenPlan(fields=('meta_', 'json_rpc_method_name', 'content', 'i"
        "s_error', 'structured_content'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('meta_', 'c"
        "ontent', 'is_error', 'structured_content'), cache=False), InitPlan(fields=(InitPlan.Field(name='meta_', annota"
        "tion=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'), default_factory=None"
        ", init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), Init"
        "Plan.Field(name='json_rpc_method_name', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name="
        "'init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.CLASS_VAR, coe"
        "rce=None, validate=None, check_type=None), InitPlan.Field(name='content', annotation=OpRef(name='init.fields.2"
        ".annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, c"
        "oerce=None, validate=None, check_type=None), InitPlan.Field(name='is_error', annotation=OpRef(name='init.field"
        "s.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False"
        ", field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='structured"
        "_content', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), def"
        "ault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check"
        "_type=None)), self_param='self', std_params=(), kw_only_params=('meta_', 'content', 'is_error', 'structured_co"
        "ntent'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(Repr"
        "Plan.Field(name='meta_', kw_only=True, fn=None), ReprPlan.Field(name='content', kw_only=True, fn=None), ReprPl"
        "an.Field(name='is_error', kw_only=True, fn=None), ReprPlan.Field(name='structured_content', kw_only=True, fn=N"
        "one)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='d67af412fc2e5e82d7729f9452c092674a3f36b3',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__4__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp._marshal', 'CallToolResult'),
    ),
)
def _process_dataclass__d67af412fc2e5e82d7729f9452c092674a3f36b3():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
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
                meta_=self.meta_,
                content=self.content,
                is_error=self.is_error,
                structured_content=self.structured_content,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.meta_ == other.meta_ and
                self.content == other.content and
                self.is_error == other.is_error and
                self.structured_content == other.structured_content
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'meta_',
            'json_rpc_method_name',
            'content',
            'is_error',
            'structured_content',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'meta_',
            'json_rpc_method_name',
            'content',
            'is_error',
            'structured_content',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.meta_,
                self.content,
                self.is_error,
                self.structured_content,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            meta_: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            content: __dataclass__init__fields__2__annotation,
            is_error: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            structured_content: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'meta_', meta_)
            __dataclass__object_setattr(self, 'content', content)
            __dataclass__object_setattr(self, 'is_error', is_error)
            __dataclass__object_setattr(self, 'structured_content', structured_content)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"meta_={self.meta_!r}")
            parts.append(f"content={self.content!r}")
            parts.append(f"is_error={self.is_error!r}")
            parts.append(f"structured_content={self.structured_content!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('elicitation', 'experimental', 'roots', 'sampling')), EqPlan(fields=('elicitation'"
        ", 'experimental', 'roots', 'sampling')), FrozenPlan(fields=('elicitation', 'experimental', 'roots', 'sampling'"
        "), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('elicitation', 'experimental', 'roots', '"
        "sampling'), cache=False), InitPlan(fields=(InitPlan.Field(name='elicitation', annotation=OpRef(name='init.fiel"
        "ds.0.annotation'), default=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=Fals"
        "e, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='experimen"
        "tal', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_"
        "factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type"
        "=None), InitPlan.Field(name='roots', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='in"
        "it.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce="
        "None, validate=None, check_type=None), InitPlan.Field(name='sampling', annotation=OpRef(name='init.fields.3.an"
        "notation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, fiel"
        "d_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw"
        "_only_params=('elicitation', 'experimental', 'roots', 'sampling'), frozen=True, slots=False, post_init_params="
        "None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='elicitation', kw_only=True, fn=None"
        "), ReprPlan.Field(name='experimental', kw_only=True, fn=None), ReprPlan.Field(name='roots', kw_only=True, fn=N"
        "one), ReprPlan.Field(name='sampling', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='170da6364b7625208100edb082d6e5c1dfa008cf',
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
        ('ommlds.specs.mcp._marshal', 'ClientCapabilities'),
    ),
)
def _process_dataclass__170da6364b7625208100edb082d6e5c1dfa008cf():
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
                elicitation=self.elicitation,
                experimental=self.experimental,
                roots=self.roots,
                sampling=self.sampling,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.elicitation == other.elicitation and
                self.experimental == other.experimental and
                self.roots == other.roots and
                self.sampling == other.sampling
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'elicitation',
            'experimental',
            'roots',
            'sampling',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'elicitation',
            'experimental',
            'roots',
            'sampling',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.elicitation,
                self.experimental,
                self.roots,
                self.sampling,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            elicitation: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            experimental: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            roots: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            sampling: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'elicitation', elicitation)
            __dataclass__object_setattr(self, 'experimental', experimental)
            __dataclass__object_setattr(self, 'roots', roots)
            __dataclass__object_setattr(self, 'sampling', sampling)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"elicitation={self.elicitation!r}")
            parts.append(f"experimental={self.experimental!r}")
            parts.append(f"roots={self.roots!r}")
            parts.append(f"sampling={self.sampling!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('list_changed',)), EqPlan(fields=('list_changed',)), FrozenPlan(fields=('list_chan"
        "ged',), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('list_changed',), cache=False), Init"
        "Plan(fields=(InitPlan.Field(name='list_changed', annotation=OpRef(name='init.fields.0.annotation'), default=Op"
        "Ref(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTA"
        "NCE, coerce=None, validate=None, check_type=None),), self_param='self', std_params=(), kw_only_params=('list_c"
        "hanged',), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(Re"
        "prPlan.Field(name='list_changed', kw_only=True, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='d78dfa0a1b3d36442ff997752e3282d062066773',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp._marshal', 'ClientCapabilities.Roots'),
        ('ommlds.specs.mcp._marshal', 'ServerCapabilities.Prompts'),
        ('ommlds.specs.mcp._marshal', 'ServerCapabilities.Tools'),
    ),
)
def _process_dataclass__d78dfa0a1b3d36442ff997752e3282d062066773():
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
                list_changed=self.list_changed,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.list_changed == other.list_changed
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'list_changed',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'list_changed',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.list_changed,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            list_changed: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'list_changed', list_changed)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"list_changed={self.list_changed!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('cursor',)), EqPlan(fields=('cursor',)), FrozenPlan(fields=('cursor',), allow_dyna"
        "mic_dunder_attrs=False), HashPlan(action='add', fields=('cursor',), cache=False), InitPlan(fields=(InitPlan.Fi"
        "eld(name='cursor', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.defaul"
        "t'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=Non"
        "e, check_type=None),), self_param='self', std_params=(), kw_only_params=('cursor',), frozen=True, slots=False,"
        " post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='cursor', kw_only="
        "True, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='f766093bd61562f127e07346cb0cd7c991dfe209',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp._marshal', 'CursorClientRequest'),
    ),
)
def _process_dataclass__f766093bd61562f127e07346cb0cd7c991dfe209():
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
                cursor=self.cursor,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.cursor == other.cursor
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'cursor',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'cursor',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.cursor,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            cursor: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'cursor', cursor)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"cursor={self.cursor!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('next_cursor',)), EqPlan(fields=('next_cursor',)), FrozenPlan(fields=('next_cursor"
        "',), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('next_cursor',), cache=False), InitPlan"
        "(fields=(InitPlan.Field(name='next_cursor', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(n"
        "ame='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, "
        "coerce=None, validate=None, check_type=None),), self_param='self', std_params=(), kw_only_params=('next_cursor"
        "',), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan"
        ".Field(name='next_cursor', kw_only=True, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='108625303d9cc86f36aa2da5265e213ac698f51f',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp._marshal', 'CursorClientResult'),
    ),
)
def _process_dataclass__108625303d9cc86f36aa2da5265e213ac698f51f():
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
                next_cursor=self.next_cursor,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.next_cursor == other.next_cursor
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'next_cursor',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'next_cursor',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.next_cursor,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            next_cursor: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'next_cursor', next_cursor)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"next_cursor={self.next_cursor!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('name', 'version')), EqPlan(fields=('name', 'version')), FrozenPlan(fields=('name'"
        ", 'version'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('name', 'version'), cache=Fals"
        "e), InitPlan(fields=(InitPlan.Field(name='name', annotation=OpRef(name='init.fields.0.annotation'), default=No"
        "ne, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None"
        ", check_type=None), InitPlan.Field(name='version', annotation=OpRef(name='init.fields.1.annotation'), default="
        "None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=No"
        "ne, check_type=None)), self_param='self', std_params=(), kw_only_params=('name', 'version'), frozen=True, slot"
        "s=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='name', kw"
        "_only=True, fn=None), ReprPlan.Field(name='version', kw_only=True, fn=None)), id=False, terse=False, default_f"
        "n=None)))"
    ),
    plan_repr_sha1='562f8e7e3d1263be9853f4a5c6ffd0a211afb158',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('ommlds.specs.mcp._marshal', 'Implementation'),
    ),
)
def _process_dataclass__562f8e7e3d1263be9853f4a5c6ffd0a211afb158():
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
                version=self.version,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
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
                self.version == other.version
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'name',
            'version',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'version',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
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
                self.version,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            name: __dataclass__init__fields__0__annotation,
            version: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'version', version)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"name={self.name!r}")
            parts.append(f"version={self.version!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('client_info', 'protocol_version', 'capabilities')), EqPlan(fields=('client_info',"
        " 'protocol_version', 'capabilities')), FrozenPlan(fields=('json_rpc_method_name', 'client_info', 'protocol_ver"
        "sion', 'capabilities'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('client_info', 'prot"
        "ocol_version', 'capabilities'), cache=False), InitPlan(fields=(InitPlan.Field(name='json_rpc_method_name', ann"
        "otation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'), default_factory=N"
        "one, init=True, override=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), "
        "InitPlan.Field(name='client_info', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_fa"
        "ctory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=N"
        "one), InitPlan.Field(name='protocol_version', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef"
        "(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE"
        ", coerce=None, validate=None, check_type=None), InitPlan.Field(name='capabilities', annotation=OpRef(name='ini"
        "t.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, overrid"
        "e=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_"
        "params=(), kw_only_params=('client_info', 'protocol_version', 'capabilities'), frozen=True, slots=False, post_"
        "init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='client_info', kw_only=T"
        "rue, fn=None), ReprPlan.Field(name='protocol_version', kw_only=True, fn=None), ReprPlan.Field(name='capabiliti"
        "es', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='dfa967e29d93ab10275d0ebd2618c39c2c967745',
    op_ref_idents=(
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp._marshal', 'InitializeRequest'),
    ),
)
def _process_dataclass__dfa967e29d93ab10275d0ebd2618c39c2c967745():
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
                client_info=self.client_info,
                protocol_version=self.protocol_version,
                capabilities=self.capabilities,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.client_info == other.client_info and
                self.protocol_version == other.protocol_version and
                self.capabilities == other.capabilities
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'json_rpc_method_name',
            'client_info',
            'protocol_version',
            'capabilities',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'json_rpc_method_name',
            'client_info',
            'protocol_version',
            'capabilities',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.client_info,
                self.protocol_version,
                self.capabilities,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            client_info: __dataclass__init__fields__1__annotation,
            protocol_version: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            capabilities: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'client_info', client_info)
            __dataclass__object_setattr(self, 'protocol_version', protocol_version)
            __dataclass__object_setattr(self, 'capabilities', capabilities)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"client_info={self.client_info!r}")
            parts.append(f"protocol_version={self.protocol_version!r}")
            parts.append(f"capabilities={self.capabilities!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('meta_', 'server_info', 'protocol_version', 'capabilities', 'instructions')), EqPl"
        "an(fields=('meta_', 'server_info', 'protocol_version', 'capabilities', 'instructions')), FrozenPlan(fields=('m"
        "eta_', 'json_rpc_method_name', 'server_info', 'protocol_version', 'capabilities', 'instructions'), allow_dynam"
        "ic_dunder_attrs=False), HashPlan(action='add', fields=('meta_', 'server_info', 'protocol_version', 'capabiliti"
        "es', 'instructions'), cache=False), InitPlan(fields=(InitPlan.Field(name='meta_', annotation=OpRef(name='init."
        "fields.0.annotation'), default=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override="
        "False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='json_"
        "rpc_method_name', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default"
        "'), default_factory=None, init=True, override=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=Non"
        "e, check_type=None), InitPlan.Field(name='server_info', annotation=OpRef(name='init.fields.2.annotation'), def"
        "ault=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valida"
        "te=None, check_type=None), InitPlan.Field(name='protocol_version', annotation=OpRef(name='init.fields.3.annota"
        "tion'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=N"
        "one, validate=None, check_type=None), InitPlan.Field(name='capabilities', annotation=OpRef(name='init.fields.4"
        ".annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, c"
        "oerce=None, validate=None, check_type=None), InitPlan.Field(name='instructions', annotation=OpRef(name='init.f"
        "ields.5.annotation'), default=OpRef(name='init.fields.5.default'), default_factory=None, init=True, override=F"
        "alse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_par"
        "ams=(), kw_only_params=('meta_', 'server_info', 'protocol_version', 'capabilities', 'instructions'), frozen=Tr"
        "ue, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='m"
        "eta_', kw_only=True, fn=None), ReprPlan.Field(name='server_info', kw_only=True, fn=None), ReprPlan.Field(name="
        "'protocol_version', kw_only=True, fn=None), ReprPlan.Field(name='capabilities', kw_only=True, fn=None), ReprPl"
        "an.Field(name='instructions', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='6a4c93d451d52a62674673241fca7e7164f79af1',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__5__annotation',
        '__dataclass__init__fields__5__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp._marshal', 'InitializeResult'),
    ),
)
def _process_dataclass__6a4c93d451d52a62674673241fca7e7164f79af1():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__4__annotation,
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
                meta_=self.meta_,
                server_info=self.server_info,
                protocol_version=self.protocol_version,
                capabilities=self.capabilities,
                instructions=self.instructions,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.meta_ == other.meta_ and
                self.server_info == other.server_info and
                self.protocol_version == other.protocol_version and
                self.capabilities == other.capabilities and
                self.instructions == other.instructions
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'meta_',
            'json_rpc_method_name',
            'server_info',
            'protocol_version',
            'capabilities',
            'instructions',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'meta_',
            'json_rpc_method_name',
            'server_info',
            'protocol_version',
            'capabilities',
            'instructions',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.meta_,
                self.server_info,
                self.protocol_version,
                self.capabilities,
                self.instructions,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            meta_: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            server_info: __dataclass__init__fields__2__annotation,
            protocol_version: __dataclass__init__fields__3__annotation,
            capabilities: __dataclass__init__fields__4__annotation,
            instructions: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'meta_', meta_)
            __dataclass__object_setattr(self, 'server_info', server_info)
            __dataclass__object_setattr(self, 'protocol_version', protocol_version)
            __dataclass__object_setattr(self, 'capabilities', capabilities)
            __dataclass__object_setattr(self, 'instructions', instructions)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"meta_={self.meta_!r}")
            parts.append(f"server_info={self.server_info!r}")
            parts.append(f"protocol_version={self.protocol_version!r}")
            parts.append(f"capabilities={self.capabilities!r}")
            parts.append(f"instructions={self.instructions!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=()), EqPlan(fields=()), FrozenPlan(fields=('json_rpc_method_name',), allow_dynamic_"
        "dunder_attrs=False), HashPlan(action='add', fields=(), cache=False), InitPlan(fields=(InitPlan.Field(name='jso"
        "n_rpc_method_name', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.defau"
        "lt'), default_factory=None, init=True, override=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=N"
        "one, check_type=None),), self_param='self', std_params=(), kw_only_params=(), frozen=True, slots=False, post_i"
        "nit_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='ed35b9cf3e3cd1bf5b385570823394625579cf9d',
    op_ref_idents=(),
    cls_names=(
        ('ommlds.specs.mcp._marshal', 'InitializedNotification'),
        ('ommlds.specs.mcp._marshal', 'PingClientResult'),
        ('ommlds.specs.mcp._marshal', 'PingServerResult'),
    ),
)
def _process_dataclass__ed35b9cf3e3cd1bf5b385570823394625579cf9d():
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
            'json_rpc_method_name',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'json_rpc_method_name',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
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
        "Plans(tup=(CopyPlan(fields=('cursor',)), EqPlan(fields=('cursor',)), FrozenPlan(fields=('cursor', 'json_rpc_me"
        "thod_name'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('cursor',), cache=False), InitP"
        "lan(fields=(InitPlan.Field(name='cursor', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(nam"
        "e='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, co"
        "erce=None, validate=None, check_type=None), InitPlan.Field(name='json_rpc_method_name', annotation=OpRef(name="
        "'init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, ove"
        "rride=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None)), self_param='self',"
        " std_params=(), kw_only_params=('cursor',), frozen=True, slots=False, post_init_params=None, init_fns=(), vali"
        "date_fns=()), ReprPlan(fields=(ReprPlan.Field(name='cursor', kw_only=True, fn=None),), id=False, terse=False, "
        "default_fn=None)))"
    ),
    plan_repr_sha1='a1b41055ff58a2964f0e25aae5ad9515639a4d58',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp._marshal', 'ListPromptsRequest'),
        ('ommlds.specs.mcp._marshal', 'ListToolsRequest'),
    ),
)
def _process_dataclass__a1b41055ff58a2964f0e25aae5ad9515639a4d58():
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
                cursor=self.cursor,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.cursor == other.cursor
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'cursor',
            'json_rpc_method_name',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'cursor',
            'json_rpc_method_name',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.cursor,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            cursor: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'cursor', cursor)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"cursor={self.cursor!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('meta_', 'next_cursor', 'prompts')), EqPlan(fields=('meta_', 'next_cursor', 'promp"
        "ts')), FrozenPlan(fields=('meta_', 'next_cursor', 'json_rpc_method_name', 'prompts'), allow_dynamic_dunder_att"
        "rs=False), HashPlan(action='add', fields=('meta_', 'next_cursor', 'prompts'), cache=False), InitPlan(fields=(I"
        "nitPlan.Field(name='meta_', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields"
        ".0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, val"
        "idate=None, check_type=None), InitPlan.Field(name='next_cursor', annotation=OpRef(name='init.fields.1.annotati"
        "on'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type"
        "=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='json_rpc_method_name',"
        " annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_facto"
        "ry=None, init=True, override=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=Non"
        "e), InitPlan.Field(name='prompts', annotation=OpRef(name='init.fields.3.annotation'), default=None, default_fa"
        "ctory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=N"
        "one)), self_param='self', std_params=(), kw_only_params=('meta_', 'next_cursor', 'prompts'), frozen=True, slot"
        "s=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='meta_', k"
        "w_only=True, fn=None), ReprPlan.Field(name='next_cursor', kw_only=True, fn=None), ReprPlan.Field(name='prompts"
        "', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='4f9887cb1136aa1e731da1375b0df1156e0ab16b',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__3__annotation',
    ),
    cls_names=(
        ('ommlds.specs.mcp._marshal', 'ListPromptsResult'),
    ),
)
def _process_dataclass__4f9887cb1136aa1e731da1375b0df1156e0ab16b():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
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
                meta_=self.meta_,
                next_cursor=self.next_cursor,
                prompts=self.prompts,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.meta_ == other.meta_ and
                self.next_cursor == other.next_cursor and
                self.prompts == other.prompts
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'meta_',
            'next_cursor',
            'json_rpc_method_name',
            'prompts',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'meta_',
            'next_cursor',
            'json_rpc_method_name',
            'prompts',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.meta_,
                self.next_cursor,
                self.prompts,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            meta_: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            next_cursor: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            prompts: __dataclass__init__fields__3__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'meta_', meta_)
            __dataclass__object_setattr(self, 'next_cursor', next_cursor)
            __dataclass__object_setattr(self, 'prompts', prompts)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"meta_={self.meta_!r}")
            parts.append(f"next_cursor={self.next_cursor!r}")
            parts.append(f"prompts={self.prompts!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('meta_', 'next_cursor', 'tools')), EqPlan(fields=('meta_', 'next_cursor', 'tools')"
        "), FrozenPlan(fields=('meta_', 'next_cursor', 'json_rpc_method_name', 'tools'), allow_dynamic_dunder_attrs=Fal"
        "se), HashPlan(action='add', fields=('meta_', 'next_cursor', 'tools'), cache=False), InitPlan(fields=(InitPlan."
        "Field(name='meta_', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.defau"
        "lt'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=No"
        "ne, check_type=None), InitPlan.Field(name='next_cursor', annotation=OpRef(name='init.fields.1.annotation'), de"
        "fault=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldTy"
        "pe.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='json_rpc_method_name', annotat"
        "ion=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None,"
        " init=True, override=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), Init"
        "Plan.Field(name='tools', annotation=OpRef(name='init.fields.3.annotation'), default=None, default_factory=None"
        ", init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), sel"
        "f_param='self', std_params=(), kw_only_params=('meta_', 'next_cursor', 'tools'), frozen=True, slots=False, pos"
        "t_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='meta_', kw_only=True,"
        " fn=None), ReprPlan.Field(name='next_cursor', kw_only=True, fn=None), ReprPlan.Field(name='tools', kw_only=Tru"
        "e, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='3a00e3d924bc002c85980317fcc32aaac988be1f',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__3__annotation',
    ),
    cls_names=(
        ('ommlds.specs.mcp._marshal', 'ListToolsResult'),
    ),
)
def _process_dataclass__3a00e3d924bc002c85980317fcc32aaac988be1f():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
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
                meta_=self.meta_,
                next_cursor=self.next_cursor,
                tools=self.tools,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.meta_ == other.meta_ and
                self.next_cursor == other.next_cursor and
                self.tools == other.tools
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'meta_',
            'next_cursor',
            'json_rpc_method_name',
            'tools',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'meta_',
            'next_cursor',
            'json_rpc_method_name',
            'tools',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.meta_,
                self.next_cursor,
                self.tools,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            meta_: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            next_cursor: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            tools: __dataclass__init__fields__3__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'meta_', meta_)
            __dataclass__object_setattr(self, 'next_cursor', next_cursor)
            __dataclass__object_setattr(self, 'tools', tools)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"meta_={self.meta_!r}")
            parts.append(f"next_cursor={self.next_cursor!r}")
            parts.append(f"tools={self.tools!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
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
        ('ommlds.specs.mcp._marshal', 'Message'),
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
        "Plans(tup=(CopyPlan(fields=('meta_',)), EqPlan(fields=('meta_',)), FrozenPlan(fields=('meta_', 'json_rpc_metho"
        "d_name'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('meta_',), cache=False), InitPlan("
        "fields=(InitPlan.Field(name='meta_', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='in"
        "it.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce="
        "None, validate=None, check_type=None), InitPlan.Field(name='json_rpc_method_name', annotation=OpRef(name='init"
        ".fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override"
        "=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None)), self_param='self', std_"
        "params=(), kw_only_params=('meta_',), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_f"
        "ns=()), ReprPlan(fields=(ReprPlan.Field(name='meta_', kw_only=True, fn=None),), id=False, terse=False, default"
        "_fn=None)))"
    ),
    plan_repr_sha1='d7418a8cca2aa773c3a1ef3fa87a07dc73768748',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp._marshal', 'PingClientRequest'),
        ('ommlds.specs.mcp._marshal', 'PingServerRequest'),
    ),
)
def _process_dataclass__d7418a8cca2aa773c3a1ef3fa87a07dc73768748():
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
                meta_=self.meta_,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.meta_ == other.meta_
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'meta_',
            'json_rpc_method_name',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'meta_',
            'json_rpc_method_name',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.meta_,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            meta_: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'meta_', meta_)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"meta_={self.meta_!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('meta_', 'name', 'title', 'description', 'arguments')), EqPlan(fields=('meta_', 'n"
        "ame', 'title', 'description', 'arguments')), FrozenPlan(fields=('meta_', 'name', 'title', 'description', 'argu"
        "ments'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('meta_', 'name', 'title', 'descript"
        "ion', 'arguments'), cache=False), InitPlan(fields=(InitPlan.Field(name='meta_', annotation=OpRef(name='init.fi"
        "elds.0.annotation'), default=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=Fa"
        "lse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='name', "
        "annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=Fal"
        "se, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='title', "
        "annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factor"
        "y=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)"
        ", InitPlan.Field(name='description', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='in"
        "it.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce="
        "None, validate=None, check_type=None), InitPlan.Field(name='arguments', annotation=OpRef(name='init.fields.4.a"
        "nnotation'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, override=False, fie"
        "ld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), k"
        "w_only_params=('meta_', 'name', 'title', 'description', 'arguments'), frozen=True, slots=False, post_init_para"
        "ms=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='meta_', kw_only=True, fn=None), "
        "ReprPlan.Field(name='name', kw_only=True, fn=None), ReprPlan.Field(name='title', kw_only=True, fn=None), ReprP"
        "lan.Field(name='description', kw_only=True, fn=None), ReprPlan.Field(name='arguments', kw_only=True, fn=None))"
        ", id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='2aa0c6160b68764b4737f79b76a7211fd320c708',
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
    ),
    cls_names=(
        ('ommlds.specs.mcp._marshal', 'Prompt'),
    ),
)
def _process_dataclass__2aa0c6160b68764b4737f79b76a7211fd320c708():
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
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                meta_=self.meta_,
                name=self.name,
                title=self.title,
                description=self.description,
                arguments=self.arguments,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.meta_ == other.meta_ and
                self.name == other.name and
                self.title == other.title and
                self.description == other.description and
                self.arguments == other.arguments
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'meta_',
            'name',
            'title',
            'description',
            'arguments',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'meta_',
            'name',
            'title',
            'description',
            'arguments',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.meta_,
                self.name,
                self.title,
                self.description,
                self.arguments,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            meta_: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            name: __dataclass__init__fields__1__annotation,
            title: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            description: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            arguments: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'meta_', meta_)
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'title', title)
            __dataclass__object_setattr(self, 'description', description)
            __dataclass__object_setattr(self, 'arguments', arguments)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"meta_={self.meta_!r}")
            parts.append(f"name={self.name!r}")
            parts.append(f"title={self.title!r}")
            parts.append(f"description={self.description!r}")
            parts.append(f"arguments={self.arguments!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('name', 'title', 'description', 'required')), EqPlan(fields=('name', 'title', 'des"
        "cription', 'required')), FrozenPlan(fields=('name', 'title', 'description', 'required'), allow_dynamic_dunder_"
        "attrs=False), HashPlan(action='add', fields=('name', 'title', 'description', 'required'), cache=False), InitPl"
        "an(fields=(InitPlan.Field(name='name', annotation=OpRef(name='init.fields.0.annotation'), default=None, defaul"
        "t_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_ty"
        "pe=None), InitPlan.Field(name='title', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='"
        "init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerc"
        "e=None, validate=None, check_type=None), InitPlan.Field(name='description', annotation=OpRef(name='init.fields"
        ".2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False,"
        " field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='required', "
        "annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factor"
        "y=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)"
        "), self_param='self', std_params=(), kw_only_params=('name', 'title', 'description', 'required'), frozen=True,"
        " slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='name"
        "', kw_only=True, fn=None), ReprPlan.Field(name='title', kw_only=True, fn=None), ReprPlan.Field(name='descripti"
        "on', kw_only=True, fn=None), ReprPlan.Field(name='required', kw_only=True, fn=None)), id=False, terse=False, d"
        "efault_fn=None)))"
    ),
    plan_repr_sha1='f49ebe3867d8d04657e10bd99b1f1faf792e98ec',
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
        ('ommlds.specs.mcp._marshal', 'PromptArgument'),
    ),
)
def _process_dataclass__f49ebe3867d8d04657e10bd99b1f1faf792e98ec():
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
                title=self.title,
                description=self.description,
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
                self.title == other.title and
                self.description == other.description and
                self.required == other.required
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'name',
            'title',
            'description',
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
            'title',
            'description',
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
                self.title,
                self.description,
                self.required,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            name: __dataclass__init__fields__0__annotation,
            title: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            description: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            required: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'title', title)
            __dataclass__object_setattr(self, 'description', description)
            __dataclass__object_setattr(self, 'required', required)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"name={self.name!r}")
            parts.append(f"title={self.title!r}")
            parts.append(f"description={self.description!r}")
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
        "Plans(tup=(CopyPlan(fields=('completions', 'experimental', 'logging', 'prompts', 'resources', 'tools')), EqPla"
        "n(fields=('completions', 'experimental', 'logging', 'prompts', 'resources', 'tools')), FrozenPlan(fields=('com"
        "pletions', 'experimental', 'logging', 'prompts', 'resources', 'tools'), allow_dynamic_dunder_attrs=False), Has"
        "hPlan(action='add', fields=('completions', 'experimental', 'logging', 'prompts', 'resources', 'tools'), cache="
        "False), InitPlan(fields=(InitPlan.Field(name='completions', annotation=OpRef(name='init.fields.0.annotation'),"
        " default=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=Fiel"
        "dType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='experimental', annotation=O"
        "pRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init"
        "=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.F"
        "ield(name='logging', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.defa"
        "ult'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=N"
        "one, check_type=None), InitPlan.Field(name='prompts', annotation=OpRef(name='init.fields.3.annotation'), defau"
        "lt=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType."
        "INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='resources', annotation=OpRef(name"
        "='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, ov"
        "erride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name"
        "='tools', annotation=OpRef(name='init.fields.5.annotation'), default=OpRef(name='init.fields.5.default'), defa"
        "ult_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_"
        "type=None)), self_param='self', std_params=(), kw_only_params=('completions', 'experimental', 'logging', 'prom"
        "pts', 'resources', 'tools'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), R"
        "eprPlan(fields=(ReprPlan.Field(name='completions', kw_only=True, fn=None), ReprPlan.Field(name='experimental',"
        " kw_only=True, fn=None), ReprPlan.Field(name='logging', kw_only=True, fn=None), ReprPlan.Field(name='prompts',"
        " kw_only=True, fn=None), ReprPlan.Field(name='resources', kw_only=True, fn=None), ReprPlan.Field(name='tools',"
        " kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='0604ae887e3d1ab59338acbd6630052994c6f8d7',
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
        ('ommlds.specs.mcp._marshal', 'ServerCapabilities'),
    ),
)
def _process_dataclass__0604ae887e3d1ab59338acbd6630052994c6f8d7():
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
                completions=self.completions,
                experimental=self.experimental,
                logging=self.logging,
                prompts=self.prompts,
                resources=self.resources,
                tools=self.tools,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.completions == other.completions and
                self.experimental == other.experimental and
                self.logging == other.logging and
                self.prompts == other.prompts and
                self.resources == other.resources and
                self.tools == other.tools
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'completions',
            'experimental',
            'logging',
            'prompts',
            'resources',
            'tools',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'completions',
            'experimental',
            'logging',
            'prompts',
            'resources',
            'tools',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.completions,
                self.experimental,
                self.logging,
                self.prompts,
                self.resources,
                self.tools,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            completions: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            experimental: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            logging: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            prompts: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            resources: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            tools: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'completions', completions)
            __dataclass__object_setattr(self, 'experimental', experimental)
            __dataclass__object_setattr(self, 'logging', logging)
            __dataclass__object_setattr(self, 'prompts', prompts)
            __dataclass__object_setattr(self, 'resources', resources)
            __dataclass__object_setattr(self, 'tools', tools)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"completions={self.completions!r}")
            parts.append(f"experimental={self.experimental!r}")
            parts.append(f"logging={self.logging!r}")
            parts.append(f"prompts={self.prompts!r}")
            parts.append(f"resources={self.resources!r}")
            parts.append(f"tools={self.tools!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('list_changed', 'subscribe')), EqPlan(fields=('list_changed', 'subscribe')), Froze"
        "nPlan(fields=('list_changed', 'subscribe'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=("
        "'list_changed', 'subscribe'), cache=False), InitPlan(fields=(InitPlan.Field(name='list_changed', annotation=Op"
        "Ref(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'), default_factory=None, init="
        "True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fi"
        "eld(name='subscribe', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.def"
        "ault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate="
        "None, check_type=None)), self_param='self', std_params=(), kw_only_params=('list_changed', 'subscribe'), froze"
        "n=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(nam"
        "e='list_changed', kw_only=True, fn=None), ReprPlan.Field(name='subscribe', kw_only=True, fn=None)), id=False, "
        "terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='42bc667dce1ec8940899ca3e66ca6e82c18ef4ea',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp._marshal', 'ServerCapabilities.Resources'),
    ),
)
def _process_dataclass__42bc667dce1ec8940899ca3e66ca6e82c18ef4ea():
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
                list_changed=self.list_changed,
                subscribe=self.subscribe,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.list_changed == other.list_changed and
                self.subscribe == other.subscribe
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'list_changed',
            'subscribe',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'list_changed',
            'subscribe',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.list_changed,
                self.subscribe,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            list_changed: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            subscribe: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'list_changed', list_changed)
            __dataclass__object_setattr(self, 'subscribe', subscribe)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"list_changed={self.list_changed!r}")
            parts.append(f"subscribe={self.subscribe!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
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
        ('ommlds.specs.mcp._marshal', 'TextContentBlock'),
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
        "Plans(tup=(CopyPlan(fields=('meta_', 'name', 'title', 'description', 'annotations', 'input_schema', 'output_sc"
        "hema')), EqPlan(fields=('meta_', 'name', 'title', 'description', 'annotations', 'input_schema', 'output_schema"
        "')), FrozenPlan(fields=('meta_', 'name', 'title', 'description', 'annotations', 'input_schema', 'output_schema"
        "'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('meta_', 'name', 'title', 'description',"
        " 'annotations', 'input_schema', 'output_schema'), cache=False), InitPlan(fields=(InitPlan.Field(name='meta_', "
        "annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'), default_factor"
        "y=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)"
        ", InitPlan.Field(name='name', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory"
        "=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),"
        " InitPlan.Field(name='title', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fiel"
        "ds.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, v"
        "alidate=None, check_type=None), InitPlan.Field(name='description', annotation=OpRef(name='init.fields.3.annota"
        "tion'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, field_ty"
        "pe=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='annotations', annota"
        "tion=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_factory=None"
        ", init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), Init"
        "Plan.Field(name='input_schema', annotation=OpRef(name='init.fields.5.annotation'), default=None, default_facto"
        "ry=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None"
        "), InitPlan.Field(name='output_schema', annotation=OpRef(name='init.fields.6.annotation'), default=OpRef(name="
        "'init.fields.6.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coer"
        "ce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('meta_', 'name', "
        "'title', 'description', 'annotations', 'input_schema', 'output_schema'), frozen=True, slots=False, post_init_p"
        "arams=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='meta_', kw_only=True, fn=None"
        "), ReprPlan.Field(name='name', kw_only=True, fn=None), ReprPlan.Field(name='title', kw_only=True, fn=None), Re"
        "prPlan.Field(name='description', kw_only=True, fn=None), ReprPlan.Field(name='annotations', kw_only=True, fn=N"
        "one), ReprPlan.Field(name='input_schema', kw_only=True, fn=None), ReprPlan.Field(name='output_schema', kw_only"
        "=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='71b741a91f4a3186af46caf3ce63596c7f62fa3f',
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
        '__dataclass__init__fields__6__annotation',
        '__dataclass__init__fields__6__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp._marshal', 'Tool'),
    ),
)
def _process_dataclass__71b741a91f4a3186af46caf3ce63596c7f62fa3f():
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
                meta_=self.meta_,
                name=self.name,
                title=self.title,
                description=self.description,
                annotations=self.annotations,
                input_schema=self.input_schema,
                output_schema=self.output_schema,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.meta_ == other.meta_ and
                self.name == other.name and
                self.title == other.title and
                self.description == other.description and
                self.annotations == other.annotations and
                self.input_schema == other.input_schema and
                self.output_schema == other.output_schema
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'meta_',
            'name',
            'title',
            'description',
            'annotations',
            'input_schema',
            'output_schema',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'meta_',
            'name',
            'title',
            'description',
            'annotations',
            'input_schema',
            'output_schema',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.meta_,
                self.name,
                self.title,
                self.description,
                self.annotations,
                self.input_schema,
                self.output_schema,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            meta_: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            name: __dataclass__init__fields__1__annotation,
            title: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            description: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            annotations: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            input_schema: __dataclass__init__fields__5__annotation,
            output_schema: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'meta_', meta_)
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'title', title)
            __dataclass__object_setattr(self, 'description', description)
            __dataclass__object_setattr(self, 'annotations', annotations)
            __dataclass__object_setattr(self, 'input_schema', input_schema)
            __dataclass__object_setattr(self, 'output_schema', output_schema)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"meta_={self.meta_!r}")
            parts.append(f"name={self.name!r}")
            parts.append(f"title={self.title!r}")
            parts.append(f"description={self.description!r}")
            parts.append(f"annotations={self.annotations!r}")
            parts.append(f"input_schema={self.input_schema!r}")
            parts.append(f"output_schema={self.output_schema!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('destructive_hint', 'idempotent_hint', 'open_world_hint', 'read_only_hint', 'title"
        "')), EqPlan(fields=('destructive_hint', 'idempotent_hint', 'open_world_hint', 'read_only_hint', 'title')), Fro"
        "zenPlan(fields=('destructive_hint', 'idempotent_hint', 'open_world_hint', 'read_only_hint', 'title'), allow_dy"
        "namic_dunder_attrs=False), HashPlan(action='add', fields=('destructive_hint', 'idempotent_hint', 'open_world_h"
        "int', 'read_only_hint', 'title'), cache=False), InitPlan(fields=(InitPlan.Field(name='destructive_hint', annot"
        "ation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'), default_factory=Non"
        "e, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), Ini"
        "tPlan.Field(name='idempotent_hint', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='ini"
        "t.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=N"
        "one, validate=None, check_type=None), InitPlan.Field(name='open_world_hint', annotation=OpRef(name='init.field"
        "s.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False"
        ", field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='read_only_"
        "hint', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default"
        "_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_typ"
        "e=None), InitPlan.Field(name='title', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='i"
        "nit.fields.4.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce"
        "=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('destructive_hint',"
        " 'idempotent_hint', 'open_world_hint', 'read_only_hint', 'title'), frozen=True, slots=False, post_init_params="
        "None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='destructive_hint', kw_only=True, fn"
        "=None), ReprPlan.Field(name='idempotent_hint', kw_only=True, fn=None), ReprPlan.Field(name='open_world_hint', "
        "kw_only=True, fn=None), ReprPlan.Field(name='read_only_hint', kw_only=True, fn=None), ReprPlan.Field(name='tit"
        "le', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='e22803d32e39ac5461f07f6c2170c01280b5f7b9',
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
        ('ommlds.specs.mcp._marshal', 'ToolAnnotations'),
    ),
)
def _process_dataclass__e22803d32e39ac5461f07f6c2170c01280b5f7b9():
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
                destructive_hint=self.destructive_hint,
                idempotent_hint=self.idempotent_hint,
                open_world_hint=self.open_world_hint,
                read_only_hint=self.read_only_hint,
                title=self.title,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.destructive_hint == other.destructive_hint and
                self.idempotent_hint == other.idempotent_hint and
                self.open_world_hint == other.open_world_hint and
                self.read_only_hint == other.read_only_hint and
                self.title == other.title
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'destructive_hint',
            'idempotent_hint',
            'open_world_hint',
            'read_only_hint',
            'title',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'destructive_hint',
            'idempotent_hint',
            'open_world_hint',
            'read_only_hint',
            'title',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.destructive_hint,
                self.idempotent_hint,
                self.open_world_hint,
                self.read_only_hint,
                self.title,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            destructive_hint: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            idempotent_hint: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            open_world_hint: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            read_only_hint: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            title: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'destructive_hint', destructive_hint)
            __dataclass__object_setattr(self, 'idempotent_hint', idempotent_hint)
            __dataclass__object_setattr(self, 'open_world_hint', open_world_hint)
            __dataclass__object_setattr(self, 'read_only_hint', read_only_hint)
            __dataclass__object_setattr(self, 'title', title)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"destructive_hint={self.destructive_hint!r}")
            parts.append(f"idempotent_hint={self.idempotent_hint!r}")
            parts.append(f"open_world_hint={self.open_world_hint!r}")
            parts.append(f"read_only_hint={self.read_only_hint!r}")
            parts.append(f"title={self.title!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('meta_',)), EqPlan(fields=('meta_',)), FrozenPlan(fields=('meta_',), allow_dynamic"
        "_dunder_attrs=False), HashPlan(action='add', fields=('meta_',), cache=False), InitPlan(fields=(InitPlan.Field("
        "name='meta_', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'), "
        "default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, ch"
        "eck_type=None),), self_param='self', std_params=(), kw_only_params=('meta_',), frozen=True, slots=False, post_"
        "init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='meta_', kw_only=True, f"
        "n=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='b672ff406614f672ad0f891cad4e3a1cdeba7586',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp._marshal', 'WithMeta'),
    ),
)
def _process_dataclass__b672ff406614f672ad0f891cad4e3a1cdeba7586():
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
                meta_=self.meta_,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.meta_ == other.meta_
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'meta_',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'meta_',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.meta_,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            meta_: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'meta_', meta_)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"meta_={self.meta_!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass
