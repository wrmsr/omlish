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
        "Plans(tup=(CopyPlan(fields=()), FrozenPlan(fields=('__node_fields__', '_hash'), allow_dynamic_dunder_attrs=Fal"
        "se), InitPlan(fields=(InitPlan.Field(name='__node_fields__', annotation=OpRef(name='init.fields.0.annotation')"
        ", default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS_VAR, coerce=None, "
        "validate=None, check_type=None), InitPlan.Field(name='_hash', annotation=OpRef(name='init.fields.1.annotation'"
        "), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS_VAR, coerce=None,"
        " validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=(), frozen=True, slots=Fal"
        "se, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(), id=False, terse=False, default_f"
        "n=None)))"
    ),
    plan_repr_sha1='e7ac46d5699937da7ac00d1b1d3ab0e79226ba6a',
    op_ref_idents=(),
    cls_names=(
        ('omlish.sql.queries', 'AllSelectItem'),
        ('omlish.sql.queries', 'Expr'),
        ('omlish.sql.queries', 'ExprStmt'),
        ('omlish.sql.queries', 'Keyword'),
        ('omlish.sql.queries', 'Node'),
        ('omlish.sql.queries', 'Relation'),
        ('omlish.sql.queries', 'SelectItem'),
        ('omlish.sql.queries', 'Star'),
        ('omlish.sql.queries', 'Stmt'),
    ),
)
def _process_dataclass__e7ac46d5699937da7ac00d1b1d3ab0e79226ba6a():
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

        __dataclass___setattr_frozen_fields = {
            '__node_fields__',
            '_hash',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            '__node_fields__',
            '_hash',
        }

        def __delattr__(self, name):
            if (
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
        "Plans(tup=(CopyPlan(fields=('op', 'l', 'r')), FrozenPlan(fields=('__node_fields__', '_hash', 'op', 'l', 'r'), "
        "allow_dynamic_dunder_attrs=False), InitPlan(fields=(InitPlan.Field(name='__node_fields__', annotation=OpRef(na"
        "me='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=Fiel"
        "dType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='_hash', annotation=OpRef(n"
        "ame='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=Fie"
        "ldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='op', annotation=OpRef(nam"
        "e='init.fields.2.annotation'), default=None, default_factory=None, init=True, override=False, field_type=Field"
        "Type.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='l', annotation=OpRef(name='i"
        "nit.fields.3.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType"
        ".INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='r', annotation=OpRef(name='init."
        "fields.4.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INS"
        "TANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=('op', 'l', 'r'), kw_only_"
        "params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(Re"
        "prPlan.Field(name='op', kw_only=False, fn=None), ReprPlan.Field(name='l', kw_only=False, fn=None), ReprPlan.Fi"
        "eld(name='r', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='63f8f88e5a70521d583838faae244bbdb653b9ea',
    op_ref_idents=(
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__4__annotation',
    ),
    cls_names=(
        ('omlish.sql.queries', 'Binary'),
    ),
)
def _process_dataclass__63f8f88e5a70521d583838faae244bbdb653b9ea():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__3__annotation,
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
                op=self.op,
                l=self.l,
                r=self.r,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        __dataclass___setattr_frozen_fields = {
            '__node_fields__',
            '_hash',
            'op',
            'l',
            'r',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            '__node_fields__',
            '_hash',
            'op',
            'l',
            'r',
        }

        def __delattr__(self, name):
            if (
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
            op: __dataclass__init__fields__2__annotation,
            l: __dataclass__init__fields__3__annotation,
            r: __dataclass__init__fields__4__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'op', op)
            __dataclass__object_setattr(self, 'l', l)
            __dataclass__object_setattr(self, 'r', r)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"op={self.op!r}")
            parts.append(f"l={self.l!r}")
            parts.append(f"r={self.r!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('name', 'kind')), FrozenPlan(fields=('name', 'kind'), allow_dynamic_dunder_attrs=F"
        "alse), InitPlan(fields=(InitPlan.Field(name='name', annotation=OpRef(name='init.fields.0.annotation'), default"
        "=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=N"
        "one, check_type=None), InitPlan.Field(name='kind', annotation=OpRef(name='init.fields.1.annotation'), default="
        "None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=No"
        "ne, check_type=None)), self_param='self', std_params=('name', 'kind'), kw_only_params=(), frozen=True, slots=F"
        "alse, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='name', kw_on"
        "ly=False, fn=None), ReprPlan.Field(name='kind', kw_only=False, fn=None)), id=False, terse=False, default_fn=No"
        "ne)))"
    ),
    plan_repr_sha1='03395a73e5848238cfd3d56817eee44e61539d59',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('omlish.sql.queries', 'BinaryOp'),
        ('omlish.sql.queries', 'UnaryOp'),
    ),
)
def _process_dataclass__03395a73e5848238cfd3d56817eee44e61539d59():
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
                kind=self.kind,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        __dataclass___setattr_frozen_fields = {
            'name',
            'kind',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'kind',
        }

        def __delattr__(self, name):
            if (
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
            name: __dataclass__init__fields__0__annotation,
            kind: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'kind', kind)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"name={self.name!r}")
            parts.append(f"kind={self.kind!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('from_', 'where')), FrozenPlan(fields=('__node_fields__', '_hash', 'from_', 'where"
        "'), allow_dynamic_dunder_attrs=False), InitPlan(fields=(InitPlan.Field(name='__node_fields__', annotation=OpRe"
        "f(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type="
        "FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='_hash', annotation=OpR"
        "ef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type"
        "=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='from_', annotation=Op"
        "Ref(name='init.fields.2.annotation'), default=None, default_factory=None, init=True, override=False, field_typ"
        "e=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='where', annotation=Op"
        "Ref(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init="
        "True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param"
        "='self', std_params=('from_', 'where'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, in"
        "it_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='from_', kw_only=False, fn=None), ReprPlan.F"
        "ield(name='where', kw_only=False, fn=OpRef(name='repr.fns.3.fn'))), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='f9ef84b81ab983ceb07ac83ee96caf3b85138ab7',
    op_ref_idents=(
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
        '__dataclass__repr__fns__3__fn',
    ),
    cls_names=(
        ('omlish.sql.queries', 'Delete'),
    ),
)
def _process_dataclass__f9ef84b81ab983ceb07ac83ee96caf3b85138ab7():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
                from_=self.from_,
                where=self.where,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        __dataclass___setattr_frozen_fields = {
            '__node_fields__',
            '_hash',
            'from_',
            'where',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            '__node_fields__',
            '_hash',
            'from_',
            'where',
        }

        def __delattr__(self, name):
            if (
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
            from_: __dataclass__init__fields__2__annotation,
            where: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'from_', from_)
            __dataclass__object_setattr(self, 'where', where)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"from_={self.from_!r}")
            if (s := __dataclass__repr__fns__3__fn(self.where)) is not None:
                parts.append(f"where={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('v', 'a')), FrozenPlan(fields=('__node_fields__', '_hash', 'v', 'a'), allow_dynami"
        "c_dunder_attrs=False), InitPlan(fields=(InitPlan.Field(name='__node_fields__', annotation=OpRef(name='init.fie"
        "lds.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS_"
        "VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='_hash', annotation=OpRef(name='init.fi"
        "elds.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS"
        "_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='v', annotation=OpRef(name='init.field"
        "s.2.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE"
        ", coerce=None, validate=None, check_type=None), InitPlan.Field(name='a', annotation=OpRef(name='init.fields.3."
        "annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, fi"
        "eld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=('v'"
        ", 'a'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), Rep"
        "rPlan(fields=(ReprPlan.Field(name='v', kw_only=False, fn=None), ReprPlan.Field(name='a', kw_only=False, fn=OpR"
        "ef(name='repr.fns.3.fn'))), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='37329a1a9079e19e80c5c65b47a92c28aec1b006',
    op_ref_idents=(
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
        '__dataclass__repr__fns__3__fn',
    ),
    cls_names=(
        ('omlish.sql.queries', 'ExprSelectItem'),
    ),
)
def _process_dataclass__37329a1a9079e19e80c5c65b47a92c28aec1b006():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
                v=self.v,
                a=self.a,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        __dataclass___setattr_frozen_fields = {
            '__node_fields__',
            '_hash',
            'v',
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
            '__node_fields__',
            '_hash',
            'v',
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

        def __init__(
            self,
            v: __dataclass__init__fields__2__annotation,
            a: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'v', v)
            __dataclass__object_setattr(self, 'a', a)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"v={self.v!r}")
            if (s := __dataclass__repr__fns__3__fn(self.a)) is not None:
                parts.append(f"a={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('c', 'v')), FrozenPlan(fields=('__node_fields__', '_hash', 'c', 'v'), allow_dynami"
        "c_dunder_attrs=False), InitPlan(fields=(InitPlan.Field(name='__node_fields__', annotation=OpRef(name='init.fie"
        "lds.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS_"
        "VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='_hash', annotation=OpRef(name='init.fi"
        "elds.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS"
        "_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='c', annotation=OpRef(name='init.field"
        "s.2.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE"
        ", coerce=None, validate=None, check_type=None), InitPlan.Field(name='v', annotation=OpRef(name='init.fields.3."
        "annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, co"
        "erce=None, validate=None, check_type=None)), self_param='self', std_params=('c', 'v'), kw_only_params=(), froz"
        "en=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(na"
        "me='c', kw_only=False, fn=None), ReprPlan.Field(name='v', kw_only=False, fn=None)), id=False, terse=False, def"
        "ault_fn=None)))"
    ),
    plan_repr_sha1='2e50d4b86a5cd9323eed41529cc4ba9d0dc1aee3',
    op_ref_idents=(
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
    ),
    cls_names=(
        ('omlish.sql.queries', 'Field'),
    ),
)
def _process_dataclass__2e50d4b86a5cd9323eed41529cc4ba9d0dc1aee3():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
                c=self.c,
                v=self.v,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        __dataclass___setattr_frozen_fields = {
            '__node_fields__',
            '_hash',
            'c',
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
            '__node_fields__',
            '_hash',
            'c',
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

        def __init__(
            self,
            c: __dataclass__init__fields__2__annotation,
            v: __dataclass__init__fields__3__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'c', c)
            __dataclass__object_setattr(self, 'v', v)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"c={self.c!r}")
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
        "Plans(tup=(CopyPlan(fields=('fields',)), FrozenPlan(fields=('__node_fields__', '_hash', 'fields'), allow_dynam"
        "ic_dunder_attrs=False), InitPlan(fields=(InitPlan.Field(name='__node_fields__', annotation=OpRef(name='init.fi"
        "elds.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS"
        "_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='_hash', annotation=OpRef(name='init.f"
        "ields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLAS"
        "S_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='fields', annotation=OpRef(name='init"
        ".fields.2.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.IN"
        "STANCE, coerce=OpRef(name='init.fields.2.coerce'), validate=None, check_type=None)), self_param='self', std_pa"
        "rams=('fields',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fn"
        "s=()), ReprPlan(fields=(ReprPlan.Field(name='fields', kw_only=False, fn=None),), id=False, terse=False, defaul"
        "t_fn=None)))"
    ),
    plan_repr_sha1='7e0e049a846197c10dd6eaa0088bb0cfa339c375',
    op_ref_idents=(
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__coerce',
    ),
    cls_names=(
        ('omlish.sql.queries', 'Fields'),
    ),
)
def _process_dataclass__7e0e049a846197c10dd6eaa0088bb0cfa339c375():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__coerce,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
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

        __dataclass___setattr_frozen_fields = {
            '__node_fields__',
            '_hash',
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
            '__node_fields__',
            '_hash',
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

        def __init__(
            self,
            fields: __dataclass__init__fields__2__annotation,
        ) -> __dataclass__None:
            fields = __dataclass__init__fields__2__coerce(fields)
            __dataclass__object_setattr(self, 'fields', fields)

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
        "Plans(tup=(CopyPlan(fields=('name', 'args')), FrozenPlan(fields=('__node_fields__', '_hash', 'name', 'args'), "
        "allow_dynamic_dunder_attrs=False), InitPlan(fields=(InitPlan.Field(name='__node_fields__', annotation=OpRef(na"
        "me='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=Fiel"
        "dType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='_hash', annotation=OpRef(n"
        "ame='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=Fie"
        "ldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='name', annotation=OpRef(n"
        "ame='init.fields.2.annotation'), default=None, default_factory=None, init=True, override=False, field_type=Fie"
        "ldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='args', annotation=OpRef(na"
        "me='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, "
        "override=False, field_type=FieldType.INSTANCE, coerce=OpRef(name='init.fields.3.coerce'), validate=None, check"
        "_type=None)), self_param='self', std_params=('name', 'args'), kw_only_params=(), frozen=True, slots=False, pos"
        "t_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='name', kw_only=False,"
        " fn=None), ReprPlan.Field(name='args', kw_only=False, fn=OpRef(name='repr.fns.3.fn'))), id=False, terse=False,"
        " default_fn=None)))"
    ),
    plan_repr_sha1='c1e8f109b3559d019b8282b53a37b52de4c4df85',
    op_ref_idents=(
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__coerce',
        '__dataclass__init__fields__3__default',
        '__dataclass__repr__fns__3__fn',
    ),
    cls_names=(
        ('omlish.sql.queries', 'Func'),
    ),
)
def _process_dataclass__c1e8f109b3559d019b8282b53a37b52de4c4df85():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__3__coerce,
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
                name=self.name,
                args=self.args,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        __dataclass___setattr_frozen_fields = {
            '__node_fields__',
            '_hash',
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
            '__node_fields__',
            '_hash',
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

        def __init__(
            self,
            name: __dataclass__init__fields__2__annotation,
            args: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            args = __dataclass__init__fields__3__coerce(args)
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'args', args)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"name={self.name!r}")
            if (s := __dataclass__repr__fns__3__fn(self.args)) is not None:
                parts.append(f"args={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('s',)), FrozenPlan(fields=('__node_fields__', '_hash', 's'), allow_dynamic_dunder_"
        "attrs=False), InitPlan(fields=(InitPlan.Field(name='__node_fields__', annotation=OpRef(name='init.fields.0.ann"
        "otation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS_VAR, coer"
        "ce=None, validate=None, check_type=None), InitPlan.Field(name='_hash', annotation=OpRef(name='init.fields.1.an"
        "notation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS_VAR, coe"
        "rce=None, validate=None, check_type=None), InitPlan.Field(name='s', annotation=OpRef(name='init.fields.2.annot"
        "ation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce="
        "None, validate=None, check_type=None)), self_param='self', std_params=('s',), kw_only_params=(), frozen=True, "
        "slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='s', k"
        "w_only=False, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='2de74e3f3fd0bdfa3ce205dae3e0c8e501e402b8',
    op_ref_idents=(
        '__dataclass__init__fields__2__annotation',
    ),
    cls_names=(
        ('omlish.sql.queries', 'Ident'),
    ),
)
def _process_dataclass__2de74e3f3fd0bdfa3ce205dae3e0c8e501e402b8():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
                s=self.s,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        __dataclass___setattr_frozen_fields = {
            '__node_fields__',
            '_hash',
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
            '__node_fields__',
            '_hash',
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

        def __init__(
            self,
            s: __dataclass__init__fields__2__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 's', s)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
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
        "Plans(tup=(CopyPlan(fields=('columns', 'into', 'data')), FrozenPlan(fields=('__node_fields__', '_hash', 'colum"
        "ns', 'into', 'data'), allow_dynamic_dunder_attrs=False), InitPlan(fields=(InitPlan.Field(name='__node_fields__"
        "', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override="
        "False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='_has"
        "h', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override"
        "=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='col"
        "umns', annotation=OpRef(name='init.fields.2.annotation'), default=None, default_factory=None, init=True, overr"
        "ide=False, field_type=FieldType.INSTANCE, coerce=OpRef(name='init.fields.2.coerce'), validate=None, check_type"
        "=None), InitPlan.Field(name='into', annotation=OpRef(name='init.fields.3.annotation'), default=None, default_f"
        "actory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type="
        "None), InitPlan.Field(name='data', annotation=OpRef(name='init.fields.4.annotation'), default=None, default_fa"
        "ctory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=N"
        "one)), self_param='self', std_params=('columns', 'into', 'data'), kw_only_params=(), frozen=True, slots=False,"
        " post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='columns', kw_only"
        "=False, fn=None), ReprPlan.Field(name='into', kw_only=False, fn=None), ReprPlan.Field(name='data', kw_only=Fal"
        "se, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='6227e6bc1c06f76ecd7903a2cacb41abcf70fe66',
    op_ref_idents=(
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__coerce',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__4__annotation',
    ),
    cls_names=(
        ('omlish.sql.queries', 'Insert'),
    ),
)
def _process_dataclass__6227e6bc1c06f76ecd7903a2cacb41abcf70fe66():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__coerce,
        __dataclass__init__fields__3__annotation,
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
                columns=self.columns,
                into=self.into,
                data=self.data,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        __dataclass___setattr_frozen_fields = {
            '__node_fields__',
            '_hash',
            'columns',
            'into',
            'data',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            '__node_fields__',
            '_hash',
            'columns',
            'into',
            'data',
        }

        def __delattr__(self, name):
            if (
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
            columns: __dataclass__init__fields__2__annotation,
            into: __dataclass__init__fields__3__annotation,
            data: __dataclass__init__fields__4__annotation,
        ) -> __dataclass__None:
            columns = __dataclass__init__fields__2__coerce(columns)
            __dataclass__object_setattr(self, 'columns', columns)
            __dataclass__object_setattr(self, 'into', into)
            __dataclass__object_setattr(self, 'data', data)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"columns={self.columns!r}")
            parts.append(f"into={self.into!r}")
            parts.append(f"data={self.data!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('k', 'l', 'r', 'c')), FrozenPlan(fields=('__node_fields__', '_hash', 'k', 'l', 'r'"
        ", 'c'), allow_dynamic_dunder_attrs=False), InitPlan(fields=(InitPlan.Field(name='__node_fields__', annotation="
        "OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_t"
        "ype=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='_hash', annotation"
        "=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_"
        "type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='k', annotation=Op"
        "Ref(name='init.fields.2.annotation'), default=None, default_factory=None, init=True, override=False, field_typ"
        "e=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='l', annotation=OpRef("
        "name='init.fields.3.annotation'), default=None, default_factory=None, init=True, override=False, field_type=Fi"
        "eldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='r', annotation=OpRef(name"
        "='init.fields.4.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldT"
        "ype.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='c', annotation=OpRef(name='in"
        "it.fields.5.annotation'), default=OpRef(name='init.fields.5.default'), default_factory=None, init=True, overri"
        "de=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std"
        "_params=('k', 'l', 'r', 'c'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(),"
        " validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='k', kw_only=False, fn=None), ReprPlan.Field(name='l',"
        " kw_only=False, fn=None), ReprPlan.Field(name='r', kw_only=False, fn=None), ReprPlan.Field(name='c', kw_only=F"
        "alse, fn=OpRef(name='repr.fns.5.fn'))), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='881ca45ca5bfe15a46c9e905723db869413af558',
    op_ref_idents=(
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__5__annotation',
        '__dataclass__init__fields__5__default',
        '__dataclass__repr__fns__5__fn',
    ),
    cls_names=(
        ('omlish.sql.queries', 'Join'),
    ),
)
def _process_dataclass__881ca45ca5bfe15a46c9e905723db869413af558():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__4__annotation,
        __dataclass__init__fields__5__annotation,
        __dataclass__init__fields__5__default,
        __dataclass__repr__fns__5__fn,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                k=self.k,
                l=self.l,
                r=self.r,
                c=self.c,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        __dataclass___setattr_frozen_fields = {
            '__node_fields__',
            '_hash',
            'k',
            'l',
            'r',
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
            '__node_fields__',
            '_hash',
            'k',
            'l',
            'r',
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

        def __init__(
            self,
            k: __dataclass__init__fields__2__annotation,
            l: __dataclass__init__fields__3__annotation,
            r: __dataclass__init__fields__4__annotation,
            c: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'k', k)
            __dataclass__object_setattr(self, 'l', l)
            __dataclass__object_setattr(self, 'r', r)
            __dataclass__object_setattr(self, 'c', c)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"k={self.k!r}")
            parts.append(f"l={self.l!r}")
            parts.append(f"r={self.r!r}")
            if (s := __dataclass__repr__fns__5__fn(self.c)) is not None:
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
        "Plans(tup=(CopyPlan(fields=('v',)), FrozenPlan(fields=('__node_fields__', '_hash', 'v'), allow_dynamic_dunder_"
        "attrs=False), InitPlan(fields=(InitPlan.Field(name='__node_fields__', annotation=OpRef(name='init.fields.0.ann"
        "otation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS_VAR, coer"
        "ce=None, validate=None, check_type=None), InitPlan.Field(name='_hash', annotation=OpRef(name='init.fields.1.an"
        "notation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS_VAR, coe"
        "rce=None, validate=None, check_type=None), InitPlan.Field(name='v', annotation=OpRef(name='init.fields.2.annot"
        "ation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce="
        "None, validate=None, check_type=None)), self_param='self', std_params=('v',), kw_only_params=(), frozen=True, "
        "slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='v', k"
        "w_only=False, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='c1ea5ee83a5a052663bfe80e9c01607d559b1406',
    op_ref_idents=(
        '__dataclass__init__fields__2__annotation',
    ),
    cls_names=(
        ('omlish.sql.queries', 'Literal'),
    ),
)
def _process_dataclass__c1ea5ee83a5a052663bfe80e9c01607d559b1406():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
                v=self.v,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        __dataclass___setattr_frozen_fields = {
            '__node_fields__',
            '_hash',
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
            '__node_fields__',
            '_hash',
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

        def __init__(
            self,
            v: __dataclass__init__fields__2__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'v', v)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
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
        "Plans(tup=(CopyPlan(fields=('s',)), FrozenPlan(fields=('__node_fields__', '_hash', 's'), allow_dynamic_dunder_"
        "attrs=False), InitPlan(fields=(InitPlan.Field(name='__node_fields__', annotation=OpRef(name='init.fields.0.ann"
        "otation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS_VAR, coer"
        "ce=None, validate=None, check_type=None), InitPlan.Field(name='_hash', annotation=OpRef(name='init.fields.1.an"
        "notation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS_VAR, coe"
        "rce=None, validate=None, check_type=None), InitPlan.Field(name='s', annotation=OpRef(name='init.fields.2.annot"
        "ation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce="
        "OpRef(name='init.fields.2.coerce'), validate=None, check_type=None)), self_param='self', std_params=('s',), kw"
        "_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fiel"
        "ds=(ReprPlan.Field(name='s', kw_only=False, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='bd9ef41fa5cfbd6c9e65b2e25959a41415b18102',
    op_ref_idents=(
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__coerce',
    ),
    cls_names=(
        ('omlish.sql.queries', 'LiteralKeyword'),
    ),
)
def _process_dataclass__bd9ef41fa5cfbd6c9e65b2e25959a41415b18102():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__coerce,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
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
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        __dataclass___setattr_frozen_fields = {
            '__node_fields__',
            '_hash',
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
            '__node_fields__',
            '_hash',
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

        def __init__(
            self,
            s: __dataclass__init__fields__2__annotation,
        ) -> __dataclass__None:
            s = __dataclass__init__fields__2__coerce(s)
            __dataclass__object_setattr(self, 's', s)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
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
        "Plans(tup=(CopyPlan(fields=('k', 'es')), FrozenPlan(fields=('__node_fields__', '_hash', 'k', 'es'), allow_dyna"
        "mic_dunder_attrs=False), InitPlan(fields=(InitPlan.Field(name='__node_fields__', annotation=OpRef(name='init.f"
        "ields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLAS"
        "S_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='_hash', annotation=OpRef(name='init."
        "fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLA"
        "SS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='k', annotation=OpRef(name='init.fie"
        "lds.2.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTAN"
        "CE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='es', annotation=OpRef(name='init.fields"
        ".3.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE,"
        " coerce=OpRef(name='init.fields.3.coerce'), validate=OpRef(name='init.fields.3.validate'), check_type=None)), "
        "self_param='self', std_params=('k', 'es'), kw_only_params=(), frozen=True, slots=False, post_init_params=None,"
        " init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='k', kw_only=False, fn=None), ReprPlan.Fi"
        "eld(name='es', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='f24b88c9598c5c3c5f46c01ad47544252b69e653',
    op_ref_idents=(
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__coerce',
        '__dataclass__init__fields__3__validate',
    ),
    cls_names=(
        ('omlish.sql.queries', 'Multi'),
    ),
)
def _process_dataclass__f24b88c9598c5c3c5f46c01ad47544252b69e653():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__3__coerce,
        __dataclass__init__fields__3__validate,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                k=self.k,
                es=self.es,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        __dataclass___setattr_frozen_fields = {
            '__node_fields__',
            '_hash',
            'k',
            'es',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            '__node_fields__',
            '_hash',
            'k',
            'es',
        }

        def __delattr__(self, name):
            if (
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
            k: __dataclass__init__fields__2__annotation,
            es: __dataclass__init__fields__3__annotation,
        ) -> __dataclass__None:
            es = __dataclass__init__fields__3__coerce(es)
            if not __dataclass__init__fields__3__validate(es): 
                raise __dataclass__FieldFnValidationError(
                    obj=self,
                    fn=__dataclass__init__fields__3__validate,
                    field='es',
                    value=es,
                )
            __dataclass__object_setattr(self, 'k', k)
            __dataclass__object_setattr(self, 'es', es)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"k={self.k!r}")
            parts.append(f"es={self.es!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('ps',)), FrozenPlan(fields=('__node_fields__', '_hash', 'ps'), allow_dynamic_dunde"
        "r_attrs=False), InitPlan(fields=(InitPlan.Field(name='__node_fields__', annotation=OpRef(name='init.fields.0.a"
        "nnotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS_VAR, co"
        "erce=None, validate=None, check_type=None), InitPlan.Field(name='_hash', annotation=OpRef(name='init.fields.1."
        "annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS_VAR, c"
        "oerce=None, validate=None, check_type=None), InitPlan.Field(name='ps', annotation=OpRef(name='init.fields.2.an"
        "notation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coer"
        "ce=OpRef(name='init.fields.2.coerce'), validate=None, check_type=None)), self_param='self', std_params=('ps',)"
        ", kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan("
        "fields=(ReprPlan.Field(name='ps', kw_only=False, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='7a6be768651873d9ab8a5e0c13df76d66899aa14',
    op_ref_idents=(
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__coerce',
    ),
    cls_names=(
        ('omlish.sql.queries', 'Name'),
    ),
)
def _process_dataclass__7a6be768651873d9ab8a5e0c13df76d66899aa14():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__coerce,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                ps=self.ps,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        __dataclass___setattr_frozen_fields = {
            '__node_fields__',
            '_hash',
            'ps',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            '__node_fields__',
            '_hash',
            'ps',
        }

        def __delattr__(self, name):
            if (
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
            ps: __dataclass__init__fields__2__annotation,
        ) -> __dataclass__None:
            ps = __dataclass__init__fields__2__coerce(ps)
            __dataclass__object_setattr(self, 'ps', ps)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"ps={self.ps!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('n',)), FrozenPlan(fields=('__node_fields__', '_hash', 'n'), allow_dynamic_dunder_"
        "attrs=False), InitPlan(fields=(InitPlan.Field(name='__node_fields__', annotation=OpRef(name='init.fields.0.ann"
        "otation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS_VAR, coer"
        "ce=None, validate=None, check_type=None), InitPlan.Field(name='_hash', annotation=OpRef(name='init.fields.1.an"
        "notation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS_VAR, coe"
        "rce=None, validate=None, check_type=None), InitPlan.Field(name='n', annotation=OpRef(name='init.fields.2.annot"
        "ation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce="
        "None, validate=None, check_type=None)), self_param='self', std_params=('n',), kw_only_params=(), frozen=True, "
        "slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='n', k"
        "w_only=False, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='f27defbd34b1c1b4991139ab5577379dd109657f',
    op_ref_idents=(
        '__dataclass__init__fields__2__annotation',
    ),
    cls_names=(
        ('omlish.sql.queries', 'NameExpr'),
    ),
)
def _process_dataclass__f27defbd34b1c1b4991139ab5577379dd109657f():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
                n=self.n,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        __dataclass___setattr_frozen_fields = {
            '__node_fields__',
            '_hash',
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
            '__node_fields__',
            '_hash',
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

        def __init__(
            self,
            n: __dataclass__init__fields__2__annotation,
        ) -> __dataclass__None:
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
        "Plans(tup=(CopyPlan(fields=('cmp_fields', 'hash_fields')), EqPlan(fields=('cmp_fields', 'hash_fields')), Froze"
        "nPlan(fields=('cmp_fields', 'hash_fields'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=("
        "'cmp_fields', 'hash_fields'), cache=False), InitPlan(fields=(InitPlan.Field(name='cmp_fields', annotation=OpRe"
        "f(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type="
        "FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='hash_fields', annotatio"
        "n=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field"
        "_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=('cmp_f"
        "ields', 'hash_fields'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), valid"
        "ate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='cmp_fields', kw_only=False, fn=None), ReprPlan.Field(name='"
        "hash_fields', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='b8c8a3ae58179edee1955035e0736f0a17b6c999',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('omlish.sql.queries', 'Node._Fields'),
    ),
)
def _process_dataclass__b8c8a3ae58179edee1955035e0736f0a17b6c999():
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
                cmp_fields=self.cmp_fields,
                hash_fields=self.hash_fields,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.cmp_fields == other.cmp_fields and
                self.hash_fields == other.hash_fields
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'cmp_fields',
            'hash_fields',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            'cmp_fields',
            'hash_fields',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__dataclass__cls, self).__delattr__(name)

        __delattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__delattr__"
        if '__delattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __delattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__delattr__', __delattr__)

        def __hash__(self):
            return hash((
                self.cmp_fields,
                self.hash_fields,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            cmp_fields: __dataclass__init__fields__0__annotation,
            hash_fields: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'cmp_fields', cmp_fields)
            __dataclass__object_setattr(self, 'hash_fields', hash_fields)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"cmp_fields={self.cmp_fields!r}")
            parts.append(f"hash_fields={self.hash_fields!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('n',)), FrozenPlan(fields=('n',), allow_dynamic_dunder_attrs=False), InitPlan(fiel"
        "ds=(InitPlan.Field(name='n', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.field"
        "s.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, va"
        "lidate=OpRef(name='init.fields.0.validate'), check_type=None),), self_param='self', std_params=('n',), kw_only"
        "_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=())))"
    ),
    plan_repr_sha1='97c6d2c139b3e6117df6ff1b1518893a288e097b',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__0__validate',
    ),
    cls_names=(
        ('omlish.sql.queries', 'Param'),
    ),
)
def _process_dataclass__97c6d2c139b3e6117df6ff1b1518893a288e097b():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__0__validate,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
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

        def __init__(
            self,
            n: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            if not __dataclass__init__fields__0__validate(n): 
                raise __dataclass__FieldFnValidationError(
                    obj=self,
                    fn=__dataclass__init__fields__0__validate,
                    field='n',
                    value=n,
                )
            __dataclass__object_setattr(self, 'n', n)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('p',)), FrozenPlan(fields=('__node_fields__', '_hash', 'p'), allow_dynamic_dunder_"
        "attrs=False), InitPlan(fields=(InitPlan.Field(name='__node_fields__', annotation=OpRef(name='init.fields.0.ann"
        "otation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS_VAR, coer"
        "ce=None, validate=None, check_type=None), InitPlan.Field(name='_hash', annotation=OpRef(name='init.fields.1.an"
        "notation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS_VAR, coe"
        "rce=None, validate=None, check_type=None), InitPlan.Field(name='p', annotation=OpRef(name='init.fields.2.annot"
        "ation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce="
        "None, validate=None, check_type=None)), self_param='self', std_params=('p',), kw_only_params=(), frozen=True, "
        "slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='p', k"
        "w_only=False, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='5d70b1e70ab35fa9bb3d99658dcd0f5231c19284',
    op_ref_idents=(
        '__dataclass__init__fields__2__annotation',
    ),
    cls_names=(
        ('omlish.sql.queries', 'ParamExpr'),
    ),
)
def _process_dataclass__5d70b1e70ab35fa9bb3d99658dcd0f5231c19284():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
                p=self.p,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        __dataclass___setattr_frozen_fields = {
            '__node_fields__',
            '_hash',
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
            '__node_fields__',
            '_hash',
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

        def __init__(
            self,
            p: __dataclass__init__fields__2__annotation,
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
        "Plans(tup=(CopyPlan(fields=('s', 'params')), EqPlan(fields=('s', 'params')), FrozenPlan(fields=('s', 'params')"
        ", allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('s', 'params'), cache=False), InitPlan(fie"
        "lds=(InitPlan.Field(name='s', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory"
        "=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),"
        " InitPlan.Field(name='params', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factor"
        "y=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)"
        "), self_param='self', std_params=('s', 'params'), kw_only_params=(), frozen=True, slots=False, post_init_param"
        "s=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='s', kw_only=False, fn=None), Repr"
        "Plan.Field(name='params', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='6445221c320dcc70a67fdd9a3ce4d8b2bddf1f12',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('omlish.sql.queries', 'RenderedQuery'),
    ),
)
def _process_dataclass__6445221c320dcc70a67fdd9a3ce4d8b2bddf1f12():
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
                s=self.s,
                params=self.params,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
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
                self.params == other.params
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            's',
            'params',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'params',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
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
                self.params,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            s: __dataclass__init__fields__0__annotation,
            params: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 's', s)
            __dataclass__object_setattr(self, 'params', params)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"s={self.s!r}")
            parts.append(f"params={self.params!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('p', 'params')), EqPlan(fields=('p', 'params')), FrozenPlan(fields=('p', 'params')"
        ", allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('p', 'params'), cache=False), InitPlan(fie"
        "lds=(InitPlan.Field(name='p', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory"
        "=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),"
        " InitPlan.Field(name='params', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factor"
        "y=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)"
        "), self_param='self', std_params=('p', 'params'), kw_only_params=(), frozen=True, slots=False, post_init_param"
        "s=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='p', kw_only=False, fn=None), Repr"
        "Plan.Field(name='params', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='e963a32ff542ef2a6c239f4d29d900e3a42f8338',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('omlish.sql.queries', 'RenderedQueryParts'),
    ),
)
def _process_dataclass__e963a32ff542ef2a6c239f4d29d900e3a42f8338():
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
                p=self.p,
                params=self.params,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.p == other.p and
                self.params == other.params
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'p',
            'params',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
            'params',
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
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
                self.params,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            p: __dataclass__init__fields__0__annotation,
            params: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'p', p)
            __dataclass__object_setattr(self, 'params', params)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"p={self.p!r}")
            parts.append(f"params={self.params!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('items', 'from_', 'where')), FrozenPlan(fields=('__node_fields__', '_hash', 'items"
        "', 'from_', 'where'), allow_dynamic_dunder_attrs=False), InitPlan(fields=(InitPlan.Field(name='__node_fields__"
        "', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override="
        "False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='_has"
        "h', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override"
        "=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='ite"
        "ms', annotation=OpRef(name='init.fields.2.annotation'), default=None, default_factory=None, init=True, overrid"
        "e=False, field_type=FieldType.INSTANCE, coerce=OpRef(name='init.fields.2.coerce'), validate=None, check_type=N"
        "one), InitPlan.Field(name='from_', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init"
        ".fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=No"
        "ne, validate=None, check_type=None), InitPlan.Field(name='where', annotation=OpRef(name='init.fields.4.annotat"
        "ion'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, override=False, field_typ"
        "e=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=('items', '"
        "from_', 'where'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fn"
        "s=()), ReprPlan(fields=(ReprPlan.Field(name='items', kw_only=False, fn=None), ReprPlan.Field(name='from_', kw_"
        "only=False, fn=OpRef(name='repr.fns.3.fn')), ReprPlan.Field(name='where', kw_only=False, fn=OpRef(name='repr.f"
        "ns.4.fn'))), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='21935ac05be913f6babd9a0b3e9aafa4e132b1f7',
    op_ref_idents=(
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__coerce',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__4__default',
        '__dataclass__repr__fns__3__fn',
        '__dataclass__repr__fns__4__fn',
    ),
    cls_names=(
        ('omlish.sql.queries', 'Select'),
    ),
)
def _process_dataclass__21935ac05be913f6babd9a0b3e9aafa4e132b1f7():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__coerce,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__3__default,
        __dataclass__init__fields__4__annotation,
        __dataclass__init__fields__4__default,
        __dataclass__repr__fns__3__fn,
        __dataclass__repr__fns__4__fn,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                items=self.items,
                from_=self.from_,
                where=self.where,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        __dataclass___setattr_frozen_fields = {
            '__node_fields__',
            '_hash',
            'items',
            'from_',
            'where',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            '__node_fields__',
            '_hash',
            'items',
            'from_',
            'where',
        }

        def __delattr__(self, name):
            if (
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
            items: __dataclass__init__fields__2__annotation,
            from_: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            where: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            items = __dataclass__init__fields__2__coerce(items)
            __dataclass__object_setattr(self, 'items', items)
            __dataclass__object_setattr(self, 'from_', from_)
            __dataclass__object_setattr(self, 'where', where)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"items={self.items!r}")
            if (s := __dataclass__repr__fns__3__fn(self.from_)) is not None:
                parts.append(f"from_={s}")
            if (s := __dataclass__repr__fns__4__fn(self.where)) is not None:
                parts.append(f"where={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('n', 'a')), FrozenPlan(fields=('__node_fields__', '_hash', 'n', 'a'), allow_dynami"
        "c_dunder_attrs=False), InitPlan(fields=(InitPlan.Field(name='__node_fields__', annotation=OpRef(name='init.fie"
        "lds.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS_"
        "VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='_hash', annotation=OpRef(name='init.fi"
        "elds.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS"
        "_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='n', annotation=OpRef(name='init.field"
        "s.2.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE"
        ", coerce=None, validate=None, check_type=None), InitPlan.Field(name='a', annotation=OpRef(name='init.fields.3."
        "annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, fi"
        "eld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=('n'"
        ", 'a'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), Rep"
        "rPlan(fields=(ReprPlan.Field(name='n', kw_only=False, fn=None), ReprPlan.Field(name='a', kw_only=False, fn=OpR"
        "ef(name='repr.fns.3.fn'))), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='62406300012bfb955e28c42e734bd2e6431977a2',
    op_ref_idents=(
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
        '__dataclass__repr__fns__3__fn',
    ),
    cls_names=(
        ('omlish.sql.queries', 'Table'),
    ),
)
def _process_dataclass__62406300012bfb955e28c42e734bd2e6431977a2():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
                n=self.n,
                a=self.a,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        __dataclass___setattr_frozen_fields = {
            '__node_fields__',
            '_hash',
            'n',
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
            '__node_fields__',
            '_hash',
            'n',
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

        def __init__(
            self,
            n: __dataclass__init__fields__2__annotation,
            a: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'n', n)
            __dataclass__object_setattr(self, 'a', a)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"n={self.n!r}")
            if (s := __dataclass__repr__fns__3__fn(self.a)) is not None:
                parts.append(f"a={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('op', 'v')), FrozenPlan(fields=('__node_fields__', '_hash', 'op', 'v'), allow_dyna"
        "mic_dunder_attrs=False), InitPlan(fields=(InitPlan.Field(name='__node_fields__', annotation=OpRef(name='init.f"
        "ields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLAS"
        "S_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='_hash', annotation=OpRef(name='init."
        "fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLA"
        "SS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='op', annotation=OpRef(name='init.fi"
        "elds.2.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTA"
        "NCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='v', annotation=OpRef(name='init.fields"
        ".3.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE,"
        " coerce=None, validate=None, check_type=None)), self_param='self', std_params=('op', 'v'), kw_only_params=(), "
        "frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Fiel"
        "d(name='op', kw_only=False, fn=None), ReprPlan.Field(name='v', kw_only=False, fn=None)), id=False, terse=False"
        ", default_fn=None)))"
    ),
    plan_repr_sha1='760d5eca56bfa89591b390dd743518d191e78f9a',
    op_ref_idents=(
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
    ),
    cls_names=(
        ('omlish.sql.queries', 'Unary'),
    ),
)
def _process_dataclass__760d5eca56bfa89591b390dd743518d191e78f9a():
    def _process_dataclass(
        *,
        __dataclass__cls,
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
                op=self.op,
                v=self.v,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        __dataclass___setattr_frozen_fields = {
            '__node_fields__',
            '_hash',
            'op',
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
            '__node_fields__',
            '_hash',
            'op',
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

        def __init__(
            self,
            op: __dataclass__init__fields__2__annotation,
            v: __dataclass__init__fields__3__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'op', op)
            __dataclass__object_setattr(self, 'v', v)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"op={self.op!r}")
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
        "Plans(tup=(CopyPlan(fields=('selects', 'all')), FrozenPlan(fields=('__node_fields__', '_hash', 'selects', 'all"
        "'), allow_dynamic_dunder_attrs=False), InitPlan(fields=(InitPlan.Field(name='__node_fields__', annotation=OpRe"
        "f(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type="
        "FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='_hash', annotation=OpR"
        "ef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type"
        "=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='selects', annotation="
        "OpRef(name='init.fields.2.annotation'), default=None, default_factory=None, init=True, override=False, field_t"
        "ype=FieldType.INSTANCE, coerce=OpRef(name='init.fields.2.coerce'), validate=None, check_type=None), InitPlan.F"
        "ield(name='all', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'"
        "), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None,"
        " check_type=None)), self_param='self', std_params=('selects',), kw_only_params=('all',), frozen=True, slots=Fa"
        "lse, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='selects', kw_"
        "only=False, fn=None), ReprPlan.Field(name='all', kw_only=True, fn=None)), id=False, terse=False, default_fn=No"
        "ne)))"
    ),
    plan_repr_sha1='8d880f8c43b5a9cc39657cdacce5bf45e5178c2d',
    op_ref_idents=(
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__coerce',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('omlish.sql.queries', 'Union'),
    ),
)
def _process_dataclass__8d880f8c43b5a9cc39657cdacce5bf45e5178c2d():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__coerce,
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
                selects=self.selects,
                all=self.all,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        __dataclass___setattr_frozen_fields = {
            '__node_fields__',
            '_hash',
            'selects',
            'all',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            '__node_fields__',
            '_hash',
            'selects',
            'all',
        }

        def __delattr__(self, name):
            if (
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
            selects: __dataclass__init__fields__2__annotation,
            *,
            all: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            selects = __dataclass__init__fields__2__coerce(selects)
            __dataclass__object_setattr(self, 'selects', selects)
            __dataclass__object_setattr(self, 'all', all)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"selects={self.selects!r}")
            parts.append(f"all={self.all!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('into', 'fields', 'where')), FrozenPlan(fields=('__node_fields__', '_hash', 'into'"
        ", 'fields', 'where'), allow_dynamic_dunder_attrs=False), InitPlan(fields=(InitPlan.Field(name='__node_fields__"
        "', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override="
        "False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='_has"
        "h', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override"
        "=False, field_type=FieldType.CLASS_VAR, coerce=None, validate=None, check_type=None), InitPlan.Field(name='int"
        "o', annotation=OpRef(name='init.fields.2.annotation'), default=None, default_factory=None, init=True, override"
        "=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='fiel"
        "ds', annotation=OpRef(name='init.fields.3.annotation'), default=None, default_factory=None, init=True, overrid"
        "e=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='whe"
        "re', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_f"
        "actory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type="
        "None)), self_param='self', std_params=('into', 'fields', 'where'), kw_only_params=(), frozen=True, slots=False"
        ", post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='into', kw_only=F"
        "alse, fn=None), ReprPlan.Field(name='fields', kw_only=False, fn=None), ReprPlan.Field(name='where', kw_only=Fa"
        "lse, fn=OpRef(name='repr.fns.4.fn'))), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='9c646a3db706ba806d4b2a21f48f3ee6c0c47996',
    op_ref_idents=(
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__4__default',
        '__dataclass__repr__fns__4__fn',
    ),
    cls_names=(
        ('omlish.sql.queries', 'Update'),
    ),
)
def _process_dataclass__9c646a3db706ba806d4b2a21f48f3ee6c0c47996():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__4__annotation,
        __dataclass__init__fields__4__default,
        __dataclass__repr__fns__4__fn,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                into=self.into,
                fields=self.fields,
                where=self.where,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        __dataclass___setattr_frozen_fields = {
            '__node_fields__',
            '_hash',
            'into',
            'fields',
            'where',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            '__node_fields__',
            '_hash',
            'into',
            'fields',
            'where',
        }

        def __delattr__(self, name):
            if (
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
            into: __dataclass__init__fields__2__annotation,
            fields: __dataclass__init__fields__3__annotation,
            where: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'into', into)
            __dataclass__object_setattr(self, 'fields', fields)
            __dataclass__object_setattr(self, 'where', where)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"into={self.into!r}")
            parts.append(f"fields={self.fields!r}")
            if (s := __dataclass__repr__fns__4__fn(self.where)) is not None:
                parts.append(f"where={s}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('vs',)), FrozenPlan(fields=('__node_fields__', '_hash', 'vs'), allow_dynamic_dunde"
        "r_attrs=False), InitPlan(fields=(InitPlan.Field(name='__node_fields__', annotation=OpRef(name='init.fields.0.a"
        "nnotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS_VAR, co"
        "erce=None, validate=None, check_type=None), InitPlan.Field(name='_hash', annotation=OpRef(name='init.fields.1."
        "annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.CLASS_VAR, c"
        "oerce=None, validate=None, check_type=None), InitPlan.Field(name='vs', annotation=OpRef(name='init.fields.2.an"
        "notation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coer"
        "ce=OpRef(name='init.fields.2.coerce'), validate=None, check_type=None)), self_param='self', std_params=('vs',)"
        ", kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan("
        "fields=(ReprPlan.Field(name='vs', kw_only=False, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='a2d26634979782a1294ffc26f9d212489f1dddb2',
    op_ref_idents=(
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__coerce',
    ),
    cls_names=(
        ('omlish.sql.queries', 'Values'),
    ),
)
def _process_dataclass__a2d26634979782a1294ffc26f9d212489f1dddb2():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__coerce,
        __dataclass__FieldFnValidationError,  # noqa
        __dataclass__FieldTypeValidationError,  # noqa
        __dataclass__FnValidationError,  # noqa
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__FunctionType=types.FunctionType,  # noqa
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__MISSING=dataclasses.MISSING,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass__TypeError=TypeError,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__isinstance=isinstance,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__property=property,  # noqa
    ):
        def __copy__(self):
            if self.__class__ is not __dataclass__cls:
                raise TypeError(self)
            return __dataclass__cls(  # noqa
                vs=self.vs,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        __dataclass___setattr_frozen_fields = {
            '__node_fields__',
            '_hash',
            'vs',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__dataclass__cls, self).__setattr__(name, value)

        __setattr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__setattr__"
        if '__setattr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __setattr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__setattr__', __setattr__)

        __dataclass___delattr_frozen_fields = {
            '__node_fields__',
            '_hash',
            'vs',
        }

        def __delattr__(self, name):
            if (
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
            vs: __dataclass__init__fields__2__annotation,
        ) -> __dataclass__None:
            vs = __dataclass__init__fields__2__coerce(vs)
            __dataclass__object_setattr(self, 'vs', vs)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"vs={self.vs!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('ty',)), EqPlan(fields=('ty',)), FrozenPlan(fields=('ty',), allow_dynamic_dunder_a"
        "ttrs=False), HashPlan(action='add', fields=('ty',), cache=False), InitPlan(fields=(InitPlan.Field(name='ty', a"
        "nnotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=Fals"
        "e, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self', std_param"
        "s=('ty',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(OpRef(name='init.init"
        "_fns.0'),), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='ty', kw_only=False, fn=None),), id=False, "
        "terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='9e4d7c79a5e41688346efa43025f741f934babc3',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__init_fns__0',
    ),
    cls_names=(
        ('omlish.sql.queries._marshal', 'LowerEnumMarshaler'),
    ),
)
def _process_dataclass__9e4d7c79a5e41688346efa43025f741f934babc3():
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
                ty=self.ty,
            )

        __copy__.__qualname__ = f"{__dataclass__cls.__qualname__}.__copy__"
        if '__copy__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __copy__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__copy__', __copy__)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.ty == other.ty
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'ty',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __dataclass__cls
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
        }

        def __delattr__(self, name):
            if (
                type(self) is __dataclass__cls
                or name in __dataclass___delattr_frozen_fields
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
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            ty: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'ty', ty)
            __dataclass__init__init_fns__0(self)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"ty={self.ty!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __repr__.__qualname__ = f"{__dataclass__cls.__qualname__}.__repr__"
        if '__repr__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __repr__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__repr__', __repr__)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('ty', 'ns')), EqPlan(fields=('ty', 'ns')), FrozenPlan(fields=('ty', 'ns'), allow_d"
        "ynamic_dunder_attrs=False), HashPlan(action='add', fields=('ty', 'ns'), cache=False), InitPlan(fields=(InitPla"
        "n.Field(name='ty', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init"
        "=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.F"
        "ield(name='ns', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=Tr"
        "ue, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='"
        "self', std_params=('ty', 'ns'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=("
        "OpRef(name='init.init_fns.0'),), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='ty', kw_only=False, f"
        "n=None), ReprPlan.Field(name='ns', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='8611a731548bd71bcbde73a887e568c9a927cdb8',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__init_fns__0',
    ),
    cls_names=(
        ('omlish.sql.queries._marshal', 'OpMarshalerUnmarshaler'),
    ),
)
def _process_dataclass__8611a731548bd71bcbde73a887e568c9a927cdb8():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
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
                ty=self.ty,
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
                self.ty == other.ty and
                self.ns == other.ns
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'ty',
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
            'ty',
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
                self.ty,
                self.ns,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            ty: __dataclass__init__fields__0__annotation,
            ns: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'ty', ty)
            __dataclass__object_setattr(self, 'ns', ns)
            __dataclass__init__init_fns__0(self)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"ty={self.ty!r}")
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
