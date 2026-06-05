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
        "Plans(tup=(CopyPlan(fields=('uuid', 'timeline_id', 'watermark')), EqPlan(fields=('uuid', 'timeline_id', 'water"
        "mark')), FrozenPlan(fields=('uuid', 'timeline_id', 'watermark'), allow_dynamic_dunder_attrs=False), HashPlan(a"
        "ction='add', fields=('uuid', 'timeline_id', 'watermark'), cache=False), InitPlan(fields=(InitPlan.Field(name='"
        "uuid', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=OpRef(name='init.field"
        "s.0.default_factory'), init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, c"
        "heck_type=None), InitPlan.Field(name='timeline_id', annotation=OpRef(name='init.fields.1.annotation'), default"
        "=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=N"
        "one, check_type=None), InitPlan.Field(name='watermark', annotation=OpRef(name='init.fields.2.annotation'), def"
        "ault=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valida"
        "te=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('uuid', 'timeline_id', 'watermar"
        "k'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan"
        ".Field(name='timeline_id', kw_only=True, fn=None), ReprPlan.Field(name='watermark', kw_only=True, fn=None)), i"
        "d=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='051a41a599c7313b360006b2c643780270367341',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default_factory',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.facades.timelines.events', 'TimelineEvent'),
    ),
)
def _process_dataclass__051a41a599c7313b360006b2c643780270367341():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default_factory,
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
                uuid=self.uuid,
                timeline_id=self.timeline_id,
                watermark=self.watermark,
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
                self.uuid == other.uuid and
                self.timeline_id == other.timeline_id and
                self.watermark == other.watermark
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'uuid',
            'timeline_id',
            'watermark',
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
            'uuid',
            'timeline_id',
            'watermark',
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
                self.uuid,
                self.timeline_id,
                self.watermark,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            uuid: __dataclass__init__fields__0__annotation = __dataclass__HAS_DEFAULT_FACTORY,
            timeline_id: __dataclass__init__fields__1__annotation,
            watermark: __dataclass__init__fields__2__annotation,
        ) -> __dataclass__None:
            if uuid is __dataclass__HAS_DEFAULT_FACTORY:
                uuid = __dataclass__init__fields__0__default_factory()
            __dataclass__object_setattr(self, 'uuid', uuid)
            __dataclass__object_setattr(self, 'timeline_id', timeline_id)
            __dataclass__object_setattr(self, 'watermark', watermark)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"timeline_id={self.timeline_id!r}")
            parts.append(f"watermark={self.watermark!r}")
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
        "Plans(tup=(CopyPlan(fields=('uuid', 'timeline_id', 'watermark', 'item', 'position')), EqPlan(fields=('uuid', '"
        "timeline_id', 'watermark', 'item', 'position')), FrozenPlan(fields=('uuid', 'timeline_id', 'watermark', 'item'"
        ", 'position'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('uuid', 'timeline_id', 'water"
        "mark', 'item', 'position'), cache=False), InitPlan(fields=(InitPlan.Field(name='uuid', annotation=OpRef(name='"
        "init.fields.0.annotation'), default=None, default_factory=OpRef(name='init.fields.0.default_factory'), init=Tr"
        "ue, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fiel"
        "d(name='timeline_id', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, i"
        "nit=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPla"
        "n.Field(name='watermark', annotation=OpRef(name='init.fields.2.annotation'), default=None, default_factory=Non"
        "e, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), Ini"
        "tPlan.Field(name='item', annotation=OpRef(name='init.fields.3.annotation'), default=None, default_factory=None"
        ", init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), Init"
        "Plan.Field(name='position', annotation=OpRef(name='init.fields.4.annotation'), default=None, default_factory=N"
        "one, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), "
        "self_param='self', std_params=(), kw_only_params=('uuid', 'timeline_id', 'watermark', 'item', 'position'), fro"
        "zen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(n"
        "ame='timeline_id', kw_only=True, fn=None), ReprPlan.Field(name='watermark', kw_only=True, fn=None), ReprPlan.F"
        "ield(name='item', kw_only=True, fn=None), ReprPlan.Field(name='position', kw_only=True, fn=None)), id=False, t"
        "erse=False, default_fn=None)))"
    ),
    plan_repr_sha1='863ab90a8a3b232cc9d72ab8ae0bb31f3de9a308',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default_factory',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__4__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.facades.timelines.events', 'TimelineItemAppendedEvent'),
    ),
)
def _process_dataclass__863ab90a8a3b232cc9d72ab8ae0bb31f3de9a308():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default_factory,
        __dataclass__init__fields__1__annotation,
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
                uuid=self.uuid,
                timeline_id=self.timeline_id,
                watermark=self.watermark,
                item=self.item,
                position=self.position,
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
                self.uuid == other.uuid and
                self.timeline_id == other.timeline_id and
                self.watermark == other.watermark and
                self.item == other.item and
                self.position == other.position
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'uuid',
            'timeline_id',
            'watermark',
            'item',
            'position',
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
            'uuid',
            'timeline_id',
            'watermark',
            'item',
            'position',
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
                self.uuid,
                self.timeline_id,
                self.watermark,
                self.item,
                self.position,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            uuid: __dataclass__init__fields__0__annotation = __dataclass__HAS_DEFAULT_FACTORY,
            timeline_id: __dataclass__init__fields__1__annotation,
            watermark: __dataclass__init__fields__2__annotation,
            item: __dataclass__init__fields__3__annotation,
            position: __dataclass__init__fields__4__annotation,
        ) -> __dataclass__None:
            if uuid is __dataclass__HAS_DEFAULT_FACTORY:
                uuid = __dataclass__init__fields__0__default_factory()
            __dataclass__object_setattr(self, 'uuid', uuid)
            __dataclass__object_setattr(self, 'timeline_id', timeline_id)
            __dataclass__object_setattr(self, 'watermark', watermark)
            __dataclass__object_setattr(self, 'item', item)
            __dataclass__object_setattr(self, 'position', position)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"timeline_id={self.timeline_id!r}")
            parts.append(f"watermark={self.watermark!r}")
            parts.append(f"item={self.item!r}")
            parts.append(f"position={self.position!r}")
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
        "Plans(tup=(CopyPlan(fields=('uuid', 'timeline_id', 'watermark', 'item_id', 'revision', 'appended')), EqPlan(fi"
        "elds=('uuid', 'timeline_id', 'watermark', 'item_id', 'revision', 'appended')), FrozenPlan(fields=('uuid', 'tim"
        "eline_id', 'watermark', 'item_id', 'revision', 'appended'), allow_dynamic_dunder_attrs=False), HashPlan(action"
        "='add', fields=('uuid', 'timeline_id', 'watermark', 'item_id', 'revision', 'appended'), cache=False), InitPlan"
        "(fields=(InitPlan.Field(name='uuid', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_"
        "factory=OpRef(name='init.fields.0.default_factory'), init=True, override=False, field_type=FieldType.INSTANCE,"
        " coerce=None, validate=None, check_type=None), InitPlan.Field(name='timeline_id', annotation=OpRef(name='init."
        "fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INS"
        "TANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='watermark', annotation=OpRef(name='i"
        "nit.fields.2.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType"
        ".INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='item_id', annotation=OpRef(name="
        "'init.fields.3.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldTy"
        "pe.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='revision', annotation=OpRef(na"
        "me='init.fields.4.annotation'), default=None, default_factory=None, init=True, override=False, field_type=Fiel"
        "dType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='appended', annotation=OpRef"
        "(name='init.fields.5.annotation'), default=None, default_factory=None, init=True, override=False, field_type=F"
        "ieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_pa"
        "rams=('uuid', 'timeline_id', 'watermark', 'item_id', 'revision', 'appended'), frozen=True, slots=False, post_i"
        "nit_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='timeline_id', kw_only=Tr"
        "ue, fn=None), ReprPlan.Field(name='watermark', kw_only=True, fn=None), ReprPlan.Field(name='item_id', kw_only="
        "True, fn=None), ReprPlan.Field(name='revision', kw_only=True, fn=None), ReprPlan.Field(name='appended', kw_onl"
        "y=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='4a379634c57b1153bc6065ba53beed0fa3da9951',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default_factory',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__5__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.facades.timelines.events', 'TimelineItemDeltaEvent'),
    ),
)
def _process_dataclass__4a379634c57b1153bc6065ba53beed0fa3da9951():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default_factory,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__4__annotation,
        __dataclass__init__fields__5__annotation,
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
                uuid=self.uuid,
                timeline_id=self.timeline_id,
                watermark=self.watermark,
                item_id=self.item_id,
                revision=self.revision,
                appended=self.appended,
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
                self.uuid == other.uuid and
                self.timeline_id == other.timeline_id and
                self.watermark == other.watermark and
                self.item_id == other.item_id and
                self.revision == other.revision and
                self.appended == other.appended
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'uuid',
            'timeline_id',
            'watermark',
            'item_id',
            'revision',
            'appended',
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
            'uuid',
            'timeline_id',
            'watermark',
            'item_id',
            'revision',
            'appended',
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
                self.uuid,
                self.timeline_id,
                self.watermark,
                self.item_id,
                self.revision,
                self.appended,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            uuid: __dataclass__init__fields__0__annotation = __dataclass__HAS_DEFAULT_FACTORY,
            timeline_id: __dataclass__init__fields__1__annotation,
            watermark: __dataclass__init__fields__2__annotation,
            item_id: __dataclass__init__fields__3__annotation,
            revision: __dataclass__init__fields__4__annotation,
            appended: __dataclass__init__fields__5__annotation,
        ) -> __dataclass__None:
            if uuid is __dataclass__HAS_DEFAULT_FACTORY:
                uuid = __dataclass__init__fields__0__default_factory()
            __dataclass__object_setattr(self, 'uuid', uuid)
            __dataclass__object_setattr(self, 'timeline_id', timeline_id)
            __dataclass__object_setattr(self, 'watermark', watermark)
            __dataclass__object_setattr(self, 'item_id', item_id)
            __dataclass__object_setattr(self, 'revision', revision)
            __dataclass__object_setattr(self, 'appended', appended)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"timeline_id={self.timeline_id!r}")
            parts.append(f"watermark={self.watermark!r}")
            parts.append(f"item_id={self.item_id!r}")
            parts.append(f"revision={self.revision!r}")
            parts.append(f"appended={self.appended!r}")
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
        "Plans(tup=(CopyPlan(fields=('uuid', 'timeline_id', 'watermark', 'item')), EqPlan(fields=('uuid', 'timeline_id'"
        ", 'watermark', 'item')), FrozenPlan(fields=('uuid', 'timeline_id', 'watermark', 'item'), allow_dynamic_dunder_"
        "attrs=False), HashPlan(action='add', fields=('uuid', 'timeline_id', 'watermark', 'item'), cache=False), InitPl"
        "an(fields=(InitPlan.Field(name='uuid', annotation=OpRef(name='init.fields.0.annotation'), default=None, defaul"
        "t_factory=OpRef(name='init.fields.0.default_factory'), init=True, override=False, field_type=FieldType.INSTANC"
        "E, coerce=None, validate=None, check_type=None), InitPlan.Field(name='timeline_id', annotation=OpRef(name='ini"
        "t.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.I"
        "NSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='watermark', annotation=OpRef(name="
        "'init.fields.2.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldTy"
        "pe.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='item', annotation=OpRef(name='"
        "init.fields.3.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldTyp"
        "e.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('"
        "uuid', 'timeline_id', 'watermark', 'item'), frozen=True, slots=False, post_init_params=None, init_fns=(), vali"
        "date_fns=()), ReprPlan(fields=(ReprPlan.Field(name='timeline_id', kw_only=True, fn=None), ReprPlan.Field(name="
        "'watermark', kw_only=True, fn=None), ReprPlan.Field(name='item', kw_only=True, fn=None)), id=False, terse=Fals"
        "e, default_fn=None)))"
    ),
    plan_repr_sha1='2de9774ae6ae7ef369ee247cd18716f87584b887',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default_factory',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.facades.timelines.events', 'TimelineItemUpdatedEvent'),
    ),
)
def _process_dataclass__2de9774ae6ae7ef369ee247cd18716f87584b887():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default_factory,
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
                uuid=self.uuid,
                timeline_id=self.timeline_id,
                watermark=self.watermark,
                item=self.item,
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
                self.uuid == other.uuid and
                self.timeline_id == other.timeline_id and
                self.watermark == other.watermark and
                self.item == other.item
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'uuid',
            'timeline_id',
            'watermark',
            'item',
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
            'uuid',
            'timeline_id',
            'watermark',
            'item',
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
                self.uuid,
                self.timeline_id,
                self.watermark,
                self.item,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            uuid: __dataclass__init__fields__0__annotation = __dataclass__HAS_DEFAULT_FACTORY,
            timeline_id: __dataclass__init__fields__1__annotation,
            watermark: __dataclass__init__fields__2__annotation,
            item: __dataclass__init__fields__3__annotation,
        ) -> __dataclass__None:
            if uuid is __dataclass__HAS_DEFAULT_FACTORY:
                uuid = __dataclass__init__fields__0__default_factory()
            __dataclass__object_setattr(self, 'uuid', uuid)
            __dataclass__object_setattr(self, 'timeline_id', timeline_id)
            __dataclass__object_setattr(self, 'watermark', watermark)
            __dataclass__object_setattr(self, 'item', item)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"timeline_id={self.timeline_id!r}")
            parts.append(f"watermark={self.watermark!r}")
            parts.append(f"item={self.item!r}")
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
        "Plans(tup=(CopyPlan(fields=('item_id', 'realm', 'key')), EqPlan(fields=('item_id', 'realm', 'key')), FrozenPla"
        "n(fields=('item_id', 'realm', 'key'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('item_"
        "id', 'realm', 'key'), cache=False), InitPlan(fields=(InitPlan.Field(name='item_id', annotation=OpRef(name='ini"
        "t.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.I"
        "NSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='realm', annotation=OpRef(name='ini"
        "t.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.I"
        "NSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='key', annotation=OpRef(name='init."
        "fields.2.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INS"
        "TANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=('item_id', 'realm', 'key'"
        "), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan"
        "(fields=(ReprPlan.Field(name='item_id', kw_only=False, fn=None), ReprPlan.Field(name='realm', kw_only=False, f"
        "n=None), ReprPlan.Field(name='key', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='38dee6b335debc6cb10c31189911fd9fac2a048c',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.facades.timelines.history', 'TimelineCursor'),
    ),
)
def _process_dataclass__38dee6b335debc6cb10c31189911fd9fac2a048c():
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
                item_id=self.item_id,
                realm=self.realm,
                key=self.key,
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
                self.realm == other.realm and
                self.key == other.key
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'item_id',
            'realm',
            'key',
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
            'realm',
            'key',
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
                self.realm,
                self.key,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            item_id: __dataclass__init__fields__0__annotation,
            realm: __dataclass__init__fields__1__annotation,
            key: __dataclass__init__fields__2__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'item_id', item_id)
            __dataclass__object_setattr(self, 'realm', realm)
            __dataclass__object_setattr(self, 'key', key)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"item_id={self.item_id!r}")
            parts.append(f"realm={self.realm!r}")
            parts.append(f"key={self.key!r}")
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
        "Plans(tup=(CopyPlan(fields=('items', 'has_before', 'has_after', 'before_cursor', 'after_cursor')), EqPlan(fiel"
        "ds=('items', 'has_before', 'has_after', 'before_cursor', 'after_cursor')), FrozenPlan(fields=('items', 'has_be"
        "fore', 'has_after', 'before_cursor', 'after_cursor'), allow_dynamic_dunder_attrs=False), HashPlan(action='add'"
        ", fields=('items', 'has_before', 'has_after', 'before_cursor', 'after_cursor'), cache=False), InitPlan(fields="
        "(InitPlan.Field(name='items', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory"
        "=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),"
        " InitPlan.Field(name='has_before', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init"
        ".fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=No"
        "ne, validate=None, check_type=None), InitPlan.Field(name='has_after', annotation=OpRef(name='init.fields.2.ann"
        "otation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field"
        "_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='before_cursor', a"
        "nnotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory"
        "=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),"
        " InitPlan.Field(name='after_cursor', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='in"
        "it.fields.4.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce="
        "None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('items', 'has_before"
        "', 'has_after', 'before_cursor', 'after_cursor'), frozen=True, slots=False, post_init_params=None, init_fns=()"
        ", validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='items', kw_only=True, fn=None), ReprPlan.Field(name="
        "'has_before', kw_only=True, fn=None), ReprPlan.Field(name='has_after', kw_only=True, fn=None), ReprPlan.Field("
        "name='before_cursor', kw_only=True, fn=None), ReprPlan.Field(name='after_cursor', kw_only=True, fn=None)), id="
        "False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='0b72c123e72745e23929ff5226e59c5ee3150002',
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
        ('ommlds.minichain.facades.timelines.history', 'TimelineWindow'),
    ),
)
def _process_dataclass__0b72c123e72745e23929ff5226e59c5ee3150002():
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
                items=self.items,
                has_before=self.has_before,
                has_after=self.has_after,
                before_cursor=self.before_cursor,
                after_cursor=self.after_cursor,
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
                self.items == other.items and
                self.has_before == other.has_before and
                self.has_after == other.has_after and
                self.before_cursor == other.before_cursor and
                self.after_cursor == other.after_cursor
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'items',
            'has_before',
            'has_after',
            'before_cursor',
            'after_cursor',
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
            'items',
            'has_before',
            'has_after',
            'before_cursor',
            'after_cursor',
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
                self.items,
                self.has_before,
                self.has_after,
                self.before_cursor,
                self.after_cursor,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            items: __dataclass__init__fields__0__annotation,
            has_before: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            has_after: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            before_cursor: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            after_cursor: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'items', items)
            __dataclass__object_setattr(self, 'has_before', has_before)
            __dataclass__object_setattr(self, 'has_after', has_after)
            __dataclass__object_setattr(self, 'before_cursor', before_cursor)
            __dataclass__object_setattr(self, 'after_cursor', after_cursor)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"items={self.items!r}")
            parts.append(f"has_before={self.has_before!r}")
            parts.append(f"has_after={self.has_after!r}")
            parts.append(f"before_cursor={self.before_cursor!r}")
            parts.append(f"after_cursor={self.after_cursor!r}")
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
        "Plans(tup=(CopyPlan(fields=('cursor',)), EqPlan(fields=('cursor',)), HashPlan(action='set_none', fields=None, "
        "cache=None), InitPlan(fields=(InitPlan.Field(name='cursor', annotation=OpRef(name='init.fields.0.annotation'),"
        " default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, va"
        "lidate=None, check_type=None),), self_param='self', std_params=('cursor',), kw_only_params=(), frozen=False, s"
        "lots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='cursor"
        "', kw_only=False, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='a644e5b5af53939effaf54d8248efab942d09a92',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.facades.timelines.history', 'UnresolvableTimelineCursorError'),
    ),
)
def _process_dataclass__a644e5b5af53939effaf54d8248efab942d09a92():
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

        setattr(__dataclass__cls, '__hash__', None)

        def __init__(
            self,
            cursor: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            self.cursor = cursor

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
        "Plans(tup=(CopyPlan(fields=('id', 'revision', 'finalized', 'message')), EqPlan(fields=('id', 'revision', 'fina"
        "lized', 'message')), FrozenPlan(fields=('id', 'revision', 'finalized', 'message'), allow_dynamic_dunder_attrs="
        "False), HashPlan(action='add', fields=('id', 'revision', 'finalized', 'message'), cache=False), InitPlan(field"
        "s=(InitPlan.Field(name='id', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory="
        "OpRef(name='init.fields.0.default_factory'), init=True, override=False, field_type=FieldType.INSTANCE, coerce="
        "None, validate=None, check_type=None), InitPlan.Field(name='revision', annotation=OpRef(name='init.fields.1.an"
        "notation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, fiel"
        "d_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='finalized', anno"
        "tation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=No"
        "ne, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), In"
        "itPlan.Field(name='message', annotation=OpRef(name='init.fields.3.annotation'), default=None, default_factory="
        "None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)),"
        " self_param='self', std_params=(), kw_only_params=('id', 'revision', 'finalized', 'message'), frozen=True, slo"
        "ts=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='id', kw_"
        "only=True, fn=None), ReprPlan.Field(name='revision', kw_only=True, fn=None), ReprPlan.Field(name='finalized', "
        "kw_only=True, fn=None), ReprPlan.Field(name='message', kw_only=True, fn=None)), id=False, terse=False, default"
        "_fn=None)))"
    ),
    plan_repr_sha1='125ef5336140507b6fa15917ff4fadb3c102a468',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default_factory',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.facades.timelines.items', 'AiMessageTimelineItem'),
        ('ommlds.minichain.facades.timelines.items', 'MessageTimelineItem'),
        ('ommlds.minichain.facades.timelines.items', 'ThinkingTimelineItem'),
        ('ommlds.minichain.facades.timelines.items', 'UserMessageTimelineItem'),
    ),
)
def _process_dataclass__125ef5336140507b6fa15917ff4fadb3c102a468():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default_factory,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
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
                id=self.id,
                revision=self.revision,
                finalized=self.finalized,
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
                self.id == other.id and
                self.revision == other.revision and
                self.finalized == other.finalized and
                self.message == other.message
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'id',
            'revision',
            'finalized',
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
            'id',
            'revision',
            'finalized',
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
                self.id,
                self.revision,
                self.finalized,
                self.message,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            id: __dataclass__init__fields__0__annotation = __dataclass__HAS_DEFAULT_FACTORY,
            revision: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            finalized: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            message: __dataclass__init__fields__3__annotation,
        ) -> __dataclass__None:
            if id is __dataclass__HAS_DEFAULT_FACTORY:
                id = __dataclass__init__fields__0__default_factory()
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'revision', revision)
            __dataclass__object_setattr(self, 'finalized', finalized)
            __dataclass__object_setattr(self, 'message', message)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"id={self.id!r}")
            parts.append(f"revision={self.revision!r}")
            parts.append(f"finalized={self.finalized!r}")
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
        "Plans(tup=(CopyPlan(fields=('id', 'revision', 'finalized', 'message_uuid', 'content', 'error')), EqPlan(fields"
        "=('id', 'revision', 'finalized', 'message_uuid', 'content', 'error')), FrozenPlan(fields=('id', 'revision', 'f"
        "inalized', 'message_uuid', 'content', 'error'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fiel"
        "ds=('id', 'revision', 'finalized', 'message_uuid', 'content', 'error'), cache=False), InitPlan(fields=(InitPla"
        "n.Field(name='id', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=OpRef(name"
        "='init.fields.0.default_factory'), init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, vali"
        "date=None, check_type=None), InitPlan.Field(name='revision', annotation=OpRef(name='init.fields.1.annotation')"
        ", default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=Fie"
        "ldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='finalized', annotation=OpR"
        "ef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=T"
        "rue, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fie"
        "ld(name='message_uuid', annotation=OpRef(name='init.fields.3.annotation'), default=None, default_factory=None,"
        " init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitP"
        "lan.Field(name='content', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4"
        ".default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valid"
        "ate=None, check_type=None), InitPlan.Field(name='error', annotation=OpRef(name='init.fields.5.annotation'), de"
        "fault=OpRef(name='init.fields.5.default'), default_factory=None, init=True, override=False, field_type=FieldTy"
        "pe.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=("
        "'id', 'revision', 'finalized', 'message_uuid', 'content', 'error'), frozen=True, slots=False, post_init_params"
        "=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='id', kw_only=True, fn=None), ReprP"
        "lan.Field(name='revision', kw_only=True, fn=None), ReprPlan.Field(name='finalized', kw_only=True, fn=None), Re"
        "prPlan.Field(name='message_uuid', kw_only=True, fn=None), ReprPlan.Field(name='content', kw_only=True, fn=None"
        "), ReprPlan.Field(name='error', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='2b70b0b8406255c4f81c12f57b69152b0828f97f',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default_factory',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__4__default',
        '__dataclass__init__fields__5__annotation',
        '__dataclass__init__fields__5__default',
    ),
    cls_names=(
        ('ommlds.minichain.facades.timelines.items', 'AiStreamTimelineItem'),
    ),
)
def _process_dataclass__2b70b0b8406255c4f81c12f57b69152b0828f97f():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default_factory,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
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
                id=self.id,
                revision=self.revision,
                finalized=self.finalized,
                message_uuid=self.message_uuid,
                content=self.content,
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
                self.id == other.id and
                self.revision == other.revision and
                self.finalized == other.finalized and
                self.message_uuid == other.message_uuid and
                self.content == other.content and
                self.error == other.error
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'id',
            'revision',
            'finalized',
            'message_uuid',
            'content',
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
            'id',
            'revision',
            'finalized',
            'message_uuid',
            'content',
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
                self.id,
                self.revision,
                self.finalized,
                self.message_uuid,
                self.content,
                self.error,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            id: __dataclass__init__fields__0__annotation = __dataclass__HAS_DEFAULT_FACTORY,
            revision: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            finalized: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            message_uuid: __dataclass__init__fields__3__annotation,
            content: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            error: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
        ) -> __dataclass__None:
            if id is __dataclass__HAS_DEFAULT_FACTORY:
                id = __dataclass__init__fields__0__default_factory()
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'revision', revision)
            __dataclass__object_setattr(self, 'finalized', finalized)
            __dataclass__object_setattr(self, 'message_uuid', message_uuid)
            __dataclass__object_setattr(self, 'content', content)
            __dataclass__object_setattr(self, 'error', error)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"id={self.id!r}")
            parts.append(f"revision={self.revision!r}")
            parts.append(f"finalized={self.finalized!r}")
            parts.append(f"message_uuid={self.message_uuid!r}")
            parts.append(f"content={self.content!r}")
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
        "Plans(tup=(CopyPlan(fields=('id', 'revision', 'finalized', 'message', 'error')), EqPlan(fields=('id', 'revisio"
        "n', 'finalized', 'message', 'error')), FrozenPlan(fields=('id', 'revision', 'finalized', 'message', 'error'), "
        "allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('id', 'revision', 'finalized', 'message', 'e"
        "rror'), cache=False), InitPlan(fields=(InitPlan.Field(name='id', annotation=OpRef(name='init.fields.0.annotati"
        "on'), default=None, default_factory=OpRef(name='init.fields.0.default_factory'), init=True, override=False, fi"
        "eld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='revision', ann"
        "otation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=N"
        "one, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), I"
        "nitPlan.Field(name='finalized', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fi"
        "elds.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None,"
        " validate=None, check_type=None), InitPlan.Field(name='message', annotation=OpRef(name='init.fields.3.annotati"
        "on'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, field_type"
        "=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='error', annotation=OpR"
        "ef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=T"
        "rue, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param="
        "'self', std_params=(), kw_only_params=('id', 'revision', 'finalized', 'message', 'error'), frozen=True, slots="
        "False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='id', kw_onl"
        "y=True, fn=None), ReprPlan.Field(name='revision', kw_only=True, fn=None), ReprPlan.Field(name='finalized', kw_"
        "only=True, fn=None), ReprPlan.Field(name='message', kw_only=True, fn=None), ReprPlan.Field(name='error', kw_on"
        "ly=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='bc965302cabeb2d9f13f7505106b69392d6d19c2',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default_factory',
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
        ('ommlds.minichain.facades.timelines.items', 'ErrorTimelineItem'),
    ),
)
def _process_dataclass__bc965302cabeb2d9f13f7505106b69392d6d19c2():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default_factory,
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
                id=self.id,
                revision=self.revision,
                finalized=self.finalized,
                message=self.message,
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
                self.id == other.id and
                self.revision == other.revision and
                self.finalized == other.finalized and
                self.message == other.message and
                self.error == other.error
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'id',
            'revision',
            'finalized',
            'message',
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
            'id',
            'revision',
            'finalized',
            'message',
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
                self.id,
                self.revision,
                self.finalized,
                self.message,
                self.error,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            id: __dataclass__init__fields__0__annotation = __dataclass__HAS_DEFAULT_FACTORY,
            revision: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            finalized: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            message: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            error: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            if id is __dataclass__HAS_DEFAULT_FACTORY:
                id = __dataclass__init__fields__0__default_factory()
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'revision', revision)
            __dataclass__object_setattr(self, 'finalized', finalized)
            __dataclass__object_setattr(self, 'message', message)
            __dataclass__object_setattr(self, 'error', error)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"id={self.id!r}")
            parts.append(f"revision={self.revision!r}")
            parts.append(f"finalized={self.finalized!r}")
            parts.append(f"message={self.message!r}")
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
        "Plans(tup=(CopyPlan(fields=('id', 'revision', 'finalized', 'message_uuid', 'text', 'error')), EqPlan(fields=('"
        "id', 'revision', 'finalized', 'message_uuid', 'text', 'error')), FrozenPlan(fields=('id', 'revision', 'finaliz"
        "ed', 'message_uuid', 'text', 'error'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('id',"
        " 'revision', 'finalized', 'message_uuid', 'text', 'error'), cache=False), InitPlan(fields=(InitPlan.Field(name"
        "='id', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=OpRef(name='init.field"
        "s.0.default_factory'), init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, c"
        "heck_type=None), InitPlan.Field(name='revision', annotation=OpRef(name='init.fields.1.annotation'), default=Op"
        "Ref(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTA"
        "NCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='finalized', annotation=OpRef(name='ini"
        "t.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, overrid"
        "e=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='mes"
        "sage_uuid', annotation=OpRef(name='init.fields.3.annotation'), default=None, default_factory=None, init=True, "
        "override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(na"
        "me='text', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), def"
        "ault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check"
        "_type=None), InitPlan.Field(name='error', annotation=OpRef(name='init.fields.5.annotation'), default=OpRef(nam"
        "e='init.fields.5.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, co"
        "erce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('id', 'revision"
        "', 'finalized', 'message_uuid', 'text', 'error'), frozen=True, slots=False, post_init_params=None, init_fns=()"
        ", validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='id', kw_only=True, fn=None), ReprPlan.Field(name='re"
        "vision', kw_only=True, fn=None), ReprPlan.Field(name='finalized', kw_only=True, fn=None), ReprPlan.Field(name="
        "'message_uuid', kw_only=True, fn=None), ReprPlan.Field(name='text', kw_only=True, fn=None), ReprPlan.Field(nam"
        "e='error', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='d37802f8b9c9d7d2f34e90a4904cc73efcd554c1',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default_factory',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__4__default',
        '__dataclass__init__fields__5__annotation',
        '__dataclass__init__fields__5__default',
    ),
    cls_names=(
        ('ommlds.minichain.facades.timelines.items', 'ThinkingStreamTimelineItem'),
    ),
)
def _process_dataclass__d37802f8b9c9d7d2f34e90a4904cc73efcd554c1():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default_factory,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
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
                id=self.id,
                revision=self.revision,
                finalized=self.finalized,
                message_uuid=self.message_uuid,
                text=self.text,
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
                self.id == other.id and
                self.revision == other.revision and
                self.finalized == other.finalized and
                self.message_uuid == other.message_uuid and
                self.text == other.text and
                self.error == other.error
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'id',
            'revision',
            'finalized',
            'message_uuid',
            'text',
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
            'id',
            'revision',
            'finalized',
            'message_uuid',
            'text',
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
                self.id,
                self.revision,
                self.finalized,
                self.message_uuid,
                self.text,
                self.error,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            id: __dataclass__init__fields__0__annotation = __dataclass__HAS_DEFAULT_FACTORY,
            revision: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            finalized: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            message_uuid: __dataclass__init__fields__3__annotation,
            text: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            error: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
        ) -> __dataclass__None:
            if id is __dataclass__HAS_DEFAULT_FACTORY:
                id = __dataclass__init__fields__0__default_factory()
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'revision', revision)
            __dataclass__object_setattr(self, 'finalized', finalized)
            __dataclass__object_setattr(self, 'message_uuid', message_uuid)
            __dataclass__object_setattr(self, 'text', text)
            __dataclass__object_setattr(self, 'error', error)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"id={self.id!r}")
            parts.append(f"revision={self.revision!r}")
            parts.append(f"finalized={self.finalized!r}")
            parts.append(f"message_uuid={self.message_uuid!r}")
            parts.append(f"text={self.text!r}")
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
        "Plans(tup=(CopyPlan(fields=('id', 'revision', 'finalized')), EqPlan(fields=('id', 'revision', 'finalized')), F"
        "rozenPlan(fields=('id', 'revision', 'finalized'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fi"
        "elds=('id', 'revision', 'finalized'), cache=False), InitPlan(fields=(InitPlan.Field(name='id', annotation=OpRe"
        "f(name='init.fields.0.annotation'), default=None, default_factory=OpRef(name='init.fields.0.default_factory'),"
        " init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitP"
        "lan.Field(name='revision', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields."
        "1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, vali"
        "date=None, check_type=None), InitPlan.Field(name='finalized', annotation=OpRef(name='init.fields.2.annotation'"
        "), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=Fi"
        "eldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_par"
        "ams=('id', 'revision', 'finalized'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fn"
        "s=()), ReprPlan(fields=(ReprPlan.Field(name='id', kw_only=True, fn=None), ReprPlan.Field(name='revision', kw_o"
        "nly=True, fn=None), ReprPlan.Field(name='finalized', kw_only=True, fn=None)), id=False, terse=False, default_f"
        "n=None)))"
    ),
    plan_repr_sha1='ae8ddb39a27e32f56f71f73d579ac3e143dd5c30',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default_factory',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.minichain.facades.timelines.items', 'TimelineItem'),
    ),
)
def _process_dataclass__ae8ddb39a27e32f56f71f73d579ac3e143dd5c30():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default_factory,
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
                id=self.id,
                revision=self.revision,
                finalized=self.finalized,
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
                self.revision == other.revision and
                self.finalized == other.finalized
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'id',
            'revision',
            'finalized',
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
            'revision',
            'finalized',
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
                self.revision,
                self.finalized,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            id: __dataclass__init__fields__0__annotation = __dataclass__HAS_DEFAULT_FACTORY,
            revision: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            finalized: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            if id is __dataclass__HAS_DEFAULT_FACTORY:
                id = __dataclass__init__fields__0__default_factory()
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'revision', revision)
            __dataclass__object_setattr(self, 'finalized', finalized)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"id={self.id!r}")
            parts.append(f"revision={self.revision!r}")
            parts.append(f"finalized={self.finalized!r}")
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
        "Plans(tup=(CopyPlan(fields=('id', 'revision', 'finalized', 'state', 'use', 'partial_name', 'partial_raw_args',"
        " 'result', 'error', 'execution')), EqPlan(fields=('id', 'revision', 'finalized', 'state', 'use', 'partial_name"
        "', 'partial_raw_args', 'result', 'error', 'execution')), FrozenPlan(fields=('id', 'revision', 'finalized', 'st"
        "ate', 'use', 'partial_name', 'partial_raw_args', 'result', 'error', 'execution'), allow_dynamic_dunder_attrs=F"
        "alse), HashPlan(action='add', fields=('id', 'revision', 'finalized', 'state', 'use', 'partial_name', 'partial_"
        "raw_args', 'result', 'error', 'execution'), cache=False), InitPlan(fields=(InitPlan.Field(name='id', annotatio"
        "n=OpRef(name='init.fields.00.annotation'), default=None, default_factory=OpRef(name='init.fields.00.default_fa"
        "ctory'), init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None"
        "), InitPlan.Field(name='revision', annotation=OpRef(name='init.fields.01.annotation'), default=OpRef(name='ini"
        "t.fields.01.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce="
        "None, validate=None, check_type=None), InitPlan.Field(name='finalized', annotation=OpRef(name='init.fields.02."
        "annotation'), default=OpRef(name='init.fields.02.default'), default_factory=None, init=True, override=False, f"
        "ield_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='state', annot"
        "ation=OpRef(name='init.fields.03.annotation'), default=None, default_factory=None, init=True, override=False, "
        "field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='use', annota"
        "tion=OpRef(name='init.fields.04.annotation'), default=OpRef(name='init.fields.04.default'), default_factory=No"
        "ne, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), In"
        "itPlan.Field(name='partial_name', annotation=OpRef(name='init.fields.05.annotation'), default=OpRef(name='init"
        ".fields.05.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=N"
        "one, validate=None, check_type=None), InitPlan.Field(name='partial_raw_args', annotation=OpRef(name='init.fiel"
        "ds.06.annotation'), default=OpRef(name='init.fields.06.default'), default_factory=None, init=True, override=Fa"
        "lse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='result'"
        ", annotation=OpRef(name='init.fields.07.annotation'), default=OpRef(name='init.fields.07.default'), default_fa"
        "ctory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=N"
        "one), InitPlan.Field(name='error', annotation=OpRef(name='init.fields.08.annotation'), default=OpRef(name='ini"
        "t.fields.08.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce="
        "None, validate=None, check_type=None), InitPlan.Field(name='execution', annotation=OpRef(name='init.fields.09."
        "annotation'), default=OpRef(name='init.fields.09.default'), default_factory=None, init=True, override=False, f"
        "ield_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(),"
        " kw_only_params=('id', 'revision', 'finalized', 'state', 'use', 'partial_name', 'partial_raw_args', 'result', "
        "'error', 'execution'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPla"
        "n(fields=(ReprPlan.Field(name='id', kw_only=True, fn=None), ReprPlan.Field(name='revision', kw_only=True, fn=N"
        "one), ReprPlan.Field(name='finalized', kw_only=True, fn=None), ReprPlan.Field(name='state', kw_only=True, fn=N"
        "one), ReprPlan.Field(name='use', kw_only=True, fn=None), ReprPlan.Field(name='partial_name', kw_only=True, fn="
        "None), ReprPlan.Field(name='partial_raw_args', kw_only=True, fn=None), ReprPlan.Field(name='result', kw_only=T"
        "rue, fn=None), ReprPlan.Field(name='error', kw_only=True, fn=None), ReprPlan.Field(name='execution', kw_only=T"
        "rue, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='d55cd43d3537d53d8bd2c3f33ac017be85b1916f',
    op_ref_idents=(
        '__dataclass__init__fields__00__annotation',
        '__dataclass__init__fields__00__default_factory',
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
    ),
    cls_names=(
        ('ommlds.minichain.facades.timelines.items', 'ToolUseTimelineItem'),
    ),
)
def _process_dataclass__d55cd43d3537d53d8bd2c3f33ac017be85b1916f():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__00__annotation,
        __dataclass__init__fields__00__default_factory,
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
                revision=self.revision,
                finalized=self.finalized,
                state=self.state,
                use=self.use,
                partial_name=self.partial_name,
                partial_raw_args=self.partial_raw_args,
                result=self.result,
                error=self.error,
                execution=self.execution,
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
                self.revision == other.revision and
                self.finalized == other.finalized and
                self.state == other.state and
                self.use == other.use and
                self.partial_name == other.partial_name and
                self.partial_raw_args == other.partial_raw_args and
                self.result == other.result and
                self.error == other.error and
                self.execution == other.execution
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'id',
            'revision',
            'finalized',
            'state',
            'use',
            'partial_name',
            'partial_raw_args',
            'result',
            'error',
            'execution',
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
            'revision',
            'finalized',
            'state',
            'use',
            'partial_name',
            'partial_raw_args',
            'result',
            'error',
            'execution',
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
                self.revision,
                self.finalized,
                self.state,
                self.use,
                self.partial_name,
                self.partial_raw_args,
                self.result,
                self.error,
                self.execution,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            id: __dataclass__init__fields__00__annotation = __dataclass__HAS_DEFAULT_FACTORY,
            revision: __dataclass__init__fields__01__annotation = __dataclass__init__fields__01__default,
            finalized: __dataclass__init__fields__02__annotation = __dataclass__init__fields__02__default,
            state: __dataclass__init__fields__03__annotation,
            use: __dataclass__init__fields__04__annotation = __dataclass__init__fields__04__default,
            partial_name: __dataclass__init__fields__05__annotation = __dataclass__init__fields__05__default,
            partial_raw_args: __dataclass__init__fields__06__annotation = __dataclass__init__fields__06__default,
            result: __dataclass__init__fields__07__annotation = __dataclass__init__fields__07__default,
            error: __dataclass__init__fields__08__annotation = __dataclass__init__fields__08__default,
            execution: __dataclass__init__fields__09__annotation = __dataclass__init__fields__09__default,
        ) -> __dataclass__None:
            if id is __dataclass__HAS_DEFAULT_FACTORY:
                id = __dataclass__init__fields__00__default_factory()
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'revision', revision)
            __dataclass__object_setattr(self, 'finalized', finalized)
            __dataclass__object_setattr(self, 'state', state)
            __dataclass__object_setattr(self, 'use', use)
            __dataclass__object_setattr(self, 'partial_name', partial_name)
            __dataclass__object_setattr(self, 'partial_raw_args', partial_raw_args)
            __dataclass__object_setattr(self, 'result', result)
            __dataclass__object_setattr(self, 'error', error)
            __dataclass__object_setattr(self, 'execution', execution)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"id={self.id!r}")
            parts.append(f"revision={self.revision!r}")
            parts.append(f"finalized={self.finalized!r}")
            parts.append(f"state={self.state!r}")
            parts.append(f"use={self.use!r}")
            parts.append(f"partial_name={self.partial_name!r}")
            parts.append(f"partial_raw_args={self.partial_raw_args!r}")
            parts.append(f"result={self.result!r}")
            parts.append(f"error={self.error!r}")
            parts.append(f"execution={self.execution!r}")
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
        "Plans(tup=(CopyPlan(fields=('id', 'revision', 'finalized', 'text')), EqPlan(fields=('id', 'revision', 'finaliz"
        "ed', 'text')), FrozenPlan(fields=('id', 'revision', 'finalized', 'text'), allow_dynamic_dunder_attrs=False), H"
        "ashPlan(action='add', fields=('id', 'revision', 'finalized', 'text'), cache=False), InitPlan(fields=(InitPlan."
        "Field(name='id', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=OpRef(name='"
        "init.fields.0.default_factory'), init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valida"
        "te=None, check_type=None), InitPlan.Field(name='revision', annotation=OpRef(name='init.fields.1.annotation'), "
        "default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=Field"
        "Type.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='finalized', annotation=OpRef"
        "(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=Tru"
        "e, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field"
        "(name='text', annotation=OpRef(name='init.fields.3.annotation'), default=None, default_factory=None, init=True"
        ", override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='se"
        "lf', std_params=(), kw_only_params=('id', 'revision', 'finalized', 'text'), frozen=True, slots=False, post_ini"
        "t_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='id', kw_only=True, fn=None"
        "), ReprPlan.Field(name='revision', kw_only=True, fn=None), ReprPlan.Field(name='finalized', kw_only=True, fn=N"
        "one), ReprPlan.Field(name='text', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='38e73a4e029dc10c97b05042847ff951f3264797',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default_factory',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.facades.timelines.items', 'UiMessageTimelineItem'),
    ),
)
def _process_dataclass__38e73a4e029dc10c97b05042847ff951f3264797():
    def _process_dataclass(
        *,
        __dataclass__cls,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default_factory,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
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
                id=self.id,
                revision=self.revision,
                finalized=self.finalized,
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
                self.id == other.id and
                self.revision == other.revision and
                self.finalized == other.finalized and
                self.text == other.text
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'id',
            'revision',
            'finalized',
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
            'id',
            'revision',
            'finalized',
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
                self.id,
                self.revision,
                self.finalized,
                self.text,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            id: __dataclass__init__fields__0__annotation = __dataclass__HAS_DEFAULT_FACTORY,
            revision: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            finalized: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            text: __dataclass__init__fields__3__annotation,
        ) -> __dataclass__None:
            if id is __dataclass__HAS_DEFAULT_FACTORY:
                id = __dataclass__init__fields__0__default_factory()
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'revision', revision)
            __dataclass__object_setattr(self, 'finalized', finalized)
            __dataclass__object_setattr(self, 'text', text)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"id={self.id!r}")
            parts.append(f"revision={self.revision!r}")
            parts.append(f"finalized={self.finalized!r}")
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
        "Plans(tup=(CopyPlan(fields=('item_id', 'have', 'got')), EqPlan(fields=('item_id', 'have', 'got')), HashPlan(ac"
        "tion='set_none', fields=None, cache=None), InitPlan(fields=(InitPlan.Field(name='item_id', annotation=OpRef(na"
        "me='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=Fiel"
        "dType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='have', annotation=OpRef(nam"
        "e='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=Field"
        "Type.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='got', annotation=OpRef(name="
        "'init.fields.2.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldTy"
        "pe.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=('item_id', 'have', "
        "'got'), kw_only_params=(), frozen=False, slots=False, post_init_params=None, init_fns=(), validate_fns=()), Re"
        "prPlan(fields=(ReprPlan.Field(name='item_id', kw_only=False, fn=None), ReprPlan.Field(name='have', kw_only=Fal"
        "se, fn=None), ReprPlan.Field(name='got', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='447a3c42d2e327389d617fc9e808442f58fcda75',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.facades.timelines.projection', 'StaleProjectionRevisionError'),
    ),
)
def _process_dataclass__447a3c42d2e327389d617fc9e808442f58fcda75():
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
                item_id=self.item_id,
                have=self.have,
                got=self.got,
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
                self.have == other.have and
                self.got == other.got
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        setattr(__dataclass__cls, '__hash__', None)

        def __init__(
            self,
            item_id: __dataclass__init__fields__0__annotation,
            have: __dataclass__init__fields__1__annotation,
            got: __dataclass__init__fields__2__annotation,
        ) -> __dataclass__None:
            self.item_id = item_id
            self.have = have
            self.got = got

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"item_id={self.item_id!r}")
            parts.append(f"have={self.have!r}")
            parts.append(f"got={self.got!r}")
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
        "Plans(tup=(CopyPlan(fields=('item_id',)), EqPlan(fields=('item_id',)), HashPlan(action='set_none', fields=None"
        ", cache=None), InitPlan(fields=(InitPlan.Field(name='item_id', annotation=OpRef(name='init.fields.0.annotation"
        "'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None,"
        " validate=None, check_type=None),), self_param='self', std_params=('item_id',), kw_only_params=(), frozen=Fals"
        "e, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='it"
        "em_id', kw_only=False, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='d318b1616e3a46b89b368de310912d8cf17ba635',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.facades.timelines.projection', 'UnknownProjectionItemError'),
    ),
)
def _process_dataclass__d318b1616e3a46b89b368de310912d8cf17ba635():
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
                item_id=self.item_id,
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
                self.item_id == other.item_id
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        setattr(__dataclass__cls, '__hash__', None)

        def __init__(
            self,
            item_id: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            self.item_id = item_id

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"item_id={self.item_id!r}")
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
        "Plans(tup=(CopyPlan(fields=('window', 'watermark', 'subscription')), EqPlan(fields=('window', 'watermark', 'su"
        "bscription')), FrozenPlan(fields=('window', 'watermark', 'subscription'), allow_dynamic_dunder_attrs=False), H"
        "ashPlan(action='add', fields=('window', 'watermark', 'subscription'), cache=False), InitPlan(fields=(InitPlan."
        "Field(name='window', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, in"
        "it=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan"
        ".Field(name='watermark', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None"
        ", init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), Init"
        "Plan.Field(name='subscription', annotation=OpRef(name='init.fields.2.annotation'), default=None, default_facto"
        "ry=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None"
        ")), self_param='self', std_params=('window', 'watermark', 'subscription'), kw_only_params=(), frozen=True, slo"
        "ts=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='window',"
        " kw_only=False, fn=None), ReprPlan.Field(name='watermark', kw_only=False, fn=None), ReprPlan.Field(name='subsc"
        "ription', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='0db05e18fa59b6aefa7a015c5f28e64a8a683854',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.facades.timelines.timeline', 'TimelineAttachment'),
    ),
)
def _process_dataclass__0db05e18fa59b6aefa7a015c5f28e64a8a683854():
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
                window=self.window,
                watermark=self.watermark,
                subscription=self.subscription,
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
                self.window == other.window and
                self.watermark == other.watermark and
                self.subscription == other.subscription
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'window',
            'watermark',
            'subscription',
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
            'window',
            'watermark',
            'subscription',
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
                self.window,
                self.watermark,
                self.subscription,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            window: __dataclass__init__fields__0__annotation,
            watermark: __dataclass__init__fields__1__annotation,
            subscription: __dataclass__init__fields__2__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'window', window)
            __dataclass__object_setattr(self, 'watermark', watermark)
            __dataclass__object_setattr(self, 'subscription', subscription)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"window={self.window!r}")
            parts.append(f"watermark={self.watermark!r}")
            parts.append(f"subscription={self.subscription!r}")
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
        "Plans(tup=(CopyPlan(fields=('anchor', 'item')), EqPlan(fields=('anchor', 'item')), FrozenPlan(fields=('anchor'"
        ", 'item'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('anchor', 'item'), cache=False), "
        "InitPlan(fields=(InitPlan.Field(name='anchor', annotation=OpRef(name='init.fields.0.annotation'), default=None"
        ", default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, "
        "check_type=None), InitPlan.Field(name='item', annotation=OpRef(name='init.fields.1.annotation'), default=None,"
        " default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, c"
        "heck_type=None)), self_param='self', std_params=('anchor', 'item'), kw_only_params=(), frozen=True, slots=Fals"
        "e, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='anchor', kw_onl"
        "y=False, fn=None), ReprPlan.Field(name='item', kw_only=False, fn=None)), id=False, terse=False, default_fn=Non"
        "e)))"
    ),
    plan_repr_sha1='cb4039941c3279978248c7eb0c227f2046f22cc7',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('ommlds.minichain.facades.timelines.translate', 'AnchoredTimelineItem'),
    ),
)
def _process_dataclass__cb4039941c3279978248c7eb0c227f2046f22cc7():
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
                anchor=self.anchor,
                item=self.item,
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
                self.anchor == other.anchor and
                self.item == other.item
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'anchor',
            'item',
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
            'anchor',
            'item',
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
                self.anchor,
                self.item,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            anchor: __dataclass__init__fields__0__annotation,
            item: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'anchor', anchor)
            __dataclass__object_setattr(self, 'item', item)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"anchor={self.anchor!r}")
            parts.append(f"item={self.item!r}")
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
