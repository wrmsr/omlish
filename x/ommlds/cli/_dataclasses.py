# @om-generated
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
        "Plans(tup=(CopyPlan(fields=('backend',)), EqPlan(fields=('backend',)), FrozenPlan(fields=('backend',), allow_d"
        "ynamic_dunder_attrs=False), HashPlan(action='add', fields=('backend',), cache=False), InitPlan(fields=(InitPla"
        "n.Field(name='backend', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.d"
        "efault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validat"
        "e=None, check_type=None),), self_param='self', std_params=(), kw_only_params=('backend',), frozen=True, slots="
        "False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='backend', k"
        "w_only=True, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='fa5665ecddac4bdf52a6a47db3b5b5362a8b3c7a',
    cls_names=(
        ('ommlds.cli.backends.configs', 'BackendConfig'),
    ),
)
def _process_dataclass__fa5665ecddac4bdf52a6a47db3b5b5362a8b3c7a():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__set_cls_attr,
    ):
        def __copy__(self):
            if self.__class__ is not __class__:
                raise TypeError(self)
            return __class__(  # noqa
                backend=self.backend,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.backend == other.backend
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___frozen_fields = {
            'backend',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.backend,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            backend: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'backend', backend)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"backend={self.backend!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('modules', 'driver', 'facade', 'interface', 'printing')), EqPlan(fields=('modules'"
        ", 'driver', 'facade', 'interface', 'printing')), FrozenPlan(fields=('modules', 'driver', 'facade', 'interface'"
        ", 'printing'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('modules', 'driver', 'facade'"
        ", 'interface', 'printing'), cache=False), InitPlan(fields=(InitPlan.Field(name='modules', annotation=OpRef(nam"
        "e='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'), default_factory=None, init=True, o"
        "verride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(nam"
        "e='driver', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), de"
        "fault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, chec"
        "k_type=None), InitPlan.Field(name='facade', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(n"
        "ame='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, "
        "coerce=None, validate=None, check_type=None), InitPlan.Field(name='interface', annotation=OpRef(name='init.fie"
        "lds.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=Fal"
        "se, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='printing"
        "', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_fac"
        "tory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=No"
        "ne)), self_param='self', std_params=(), kw_only_params=('modules', 'driver', 'facade', 'interface', 'printing'"
        "), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.F"
        "ield(name='modules', kw_only=True, fn=None), ReprPlan.Field(name='driver', kw_only=True, fn=None), ReprPlan.Fi"
        "eld(name='facade', kw_only=True, fn=None), ReprPlan.Field(name='interface', kw_only=True, fn=None), ReprPlan.F"
        "ield(name='printing', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='349fd76d26747dd6cbed7dc4561c7137e925c9fc',
    cls_names=(
        ('ommlds.cli.chat.configs', 'ChatConfig'),
    ),
)
def _process_dataclass__349fd76d26747dd6cbed7dc4561c7137e925c9fc():
    def _process_dataclass(
        *,
        __class__,
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
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__set_cls_attr,
    ):
        def __copy__(self):
            if self.__class__ is not __class__:
                raise TypeError(self)
            return __class__(  # noqa
                modules=self.modules,
                driver=self.driver,
                facade=self.facade,
                interface=self.interface,
                printing=self.printing,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.modules == other.modules and
                self.driver == other.driver and
                self.facade == other.facade and
                self.interface == other.interface and
                self.printing == other.printing
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___frozen_fields = {
            'modules',
            'driver',
            'facade',
            'interface',
            'printing',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.modules,
                self.driver,
                self.facade,
                self.interface,
                self.printing,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            modules: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            driver: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            facade: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            interface: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            printing: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'modules', modules)
            __dataclass__object_setattr(self, 'driver', driver)
            __dataclass__object_setattr(self, 'facade', facade)
            __dataclass__object_setattr(self, 'interface', interface)
            __dataclass__object_setattr(self, 'printing', printing)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"modules={self.modules!r}")
            parts.append(f"driver={self.driver!r}")
            parts.append(f"facade={self.facade!r}")
            parts.append(f"interface={self.interface!r}")
            parts.append(f"printing={self.printing!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('ai', 'orm', 'session', 'storage', 'tools', 'user', 'backend', 'state')), EqPlan(f"
        "ields=('ai', 'orm', 'session', 'storage', 'tools', 'user', 'backend', 'state')), FrozenPlan(fields=('ai', 'orm"
        "', 'session', 'storage', 'tools', 'user', 'backend', 'state'), allow_dynamic_dunder_attrs=False), HashPlan(act"
        "ion='add', fields=('ai', 'orm', 'session', 'storage', 'tools', 'user', 'backend', 'state'), cache=False), Init"
        "Plan(fields=(InitPlan.Field(name='ai', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='"
        "init.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerc"
        "e=None, validate=None, check_type=None), InitPlan.Field(name='orm', annotation=OpRef(name='init.fields.1.annot"
        "ation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_t"
        "ype=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='session', annotatio"
        "n=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, i"
        "nit=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPla"
        "n.Field(name='storage', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.d"
        "efault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validat"
        "e=None, check_type=None), InitPlan.Field(name='tools', annotation=OpRef(name='init.fields.4.annotation'), defa"
        "ult=OpRef(name='init.fields.4.default'), default_factory=None, init=True, override=False, field_type=FieldType"
        ".INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='user', annotation=OpRef(name='in"
        "it.fields.5.annotation'), default=OpRef(name='init.fields.5.default'), default_factory=None, init=True, overri"
        "de=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='ba"
        "ckend', annotation=OpRef(name='init.fields.6.annotation'), default=OpRef(name='init.fields.6.default'), defaul"
        "t_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_ty"
        "pe=None), InitPlan.Field(name='state', annotation=OpRef(name='init.fields.7.annotation'), default=OpRef(name='"
        "init.fields.7.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerc"
        "e=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('ai', 'orm', 'sess"
        "ion', 'storage', 'tools', 'user', 'backend', 'state'), frozen=True, slots=False, post_init_params=None, init_f"
        "ns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='ai', kw_only=True, fn=None), ReprPlan.Field(nam"
        "e='orm', kw_only=True, fn=None), ReprPlan.Field(name='session', kw_only=True, fn=None), ReprPlan.Field(name='s"
        "torage', kw_only=True, fn=None), ReprPlan.Field(name='tools', kw_only=True, fn=None), ReprPlan.Field(name='use"
        "r', kw_only=True, fn=None), ReprPlan.Field(name='backend', kw_only=True, fn=None), ReprPlan.Field(name='state'"
        ", kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='10a0ff9a963b0444eb147246be1f5203f51f1949',
    cls_names=(
        ('ommlds.cli.chat.drivers.configs', 'DriverConfig'),
    ),
)
def _process_dataclass__10a0ff9a963b0444eb147246be1f5203f51f1949():
    def _process_dataclass(
        *,
        __class__,
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
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__set_cls_attr,
    ):
        def __copy__(self):
            if self.__class__ is not __class__:
                raise TypeError(self)
            return __class__(  # noqa
                ai=self.ai,
                orm=self.orm,
                session=self.session,
                storage=self.storage,
                tools=self.tools,
                user=self.user,
                backend=self.backend,
                state=self.state,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.ai == other.ai and
                self.orm == other.orm and
                self.session == other.session and
                self.storage == other.storage and
                self.tools == other.tools and
                self.user == other.user and
                self.backend == other.backend and
                self.state == other.state
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___frozen_fields = {
            'ai',
            'orm',
            'session',
            'storage',
            'tools',
            'user',
            'backend',
            'state',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.ai,
                self.orm,
                self.session,
                self.storage,
                self.tools,
                self.user,
                self.backend,
                self.state,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            ai: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            orm: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            session: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            storage: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            tools: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            user: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
            backend: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
            state: __dataclass__init__fields__7__annotation = __dataclass__init__fields__7__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'ai', ai)
            __dataclass__object_setattr(self, 'orm', orm)
            __dataclass__object_setattr(self, 'session', session)
            __dataclass__object_setattr(self, 'storage', storage)
            __dataclass__object_setattr(self, 'tools', tools)
            __dataclass__object_setattr(self, 'user', user)
            __dataclass__object_setattr(self, 'backend', backend)
            __dataclass__object_setattr(self, 'state', state)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"ai={self.ai!r}")
            parts.append(f"orm={self.orm!r}")
            parts.append(f"session={self.session!r}")
            parts.append(f"storage={self.storage!r}")
            parts.append(f"tools={self.tools!r}")
            parts.append(f"user={self.user!r}")
            parts.append(f"backend={self.backend!r}")
            parts.append(f"state={self.state!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('new', 'chat_id')), EqPlan(fields=('new', 'chat_id')), FrozenPlan(fields=('new', '"
        "chat_id'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('new', 'chat_id'), cache=False), "
        "InitPlan(fields=(InitPlan.Field(name='new', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(n"
        "ame='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, "
        "coerce=None, validate=None, check_type=None), InitPlan.Field(name='chat_id', annotation=OpRef(name='init.field"
        "s.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False"
        ", field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params="
        "(), kw_only_params=('new', 'chat_id'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_"
        "fns=()), ReprPlan(fields=(ReprPlan.Field(name='new', kw_only=True, fn=None), ReprPlan.Field(name='chat_id', kw"
        "_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='18ddc55be4f3b835e33c2f5607749808ade8b9ec',
    cls_names=(
        ('ommlds.cli.chat.drivers.state.configs', 'StateConfig'),
    ),
)
def _process_dataclass__18ddc55be4f3b835e33c2f5607749808ade8b9ec():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__set_cls_attr,
    ):
        def __copy__(self):
            if self.__class__ is not __class__:
                raise TypeError(self)
            return __class__(  # noqa
                new=self.new,
                chat_id=self.chat_id,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.new == other.new and
                self.chat_id == other.chat_id
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___frozen_fields = {
            'new',
            'chat_id',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.new,
                self.chat_id,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            new: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            chat_id: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'new', new)
            __dataclass__object_setattr(self, 'chat_id', chat_id)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"new={self.new!r}")
            parts.append(f"chat_id={self.chat_id!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('id', 'chat_id')), EqPlan(fields=('id', 'chat_id')), HashPlan(action='set_none', f"
        "ields=None, cache=None), InitPlan(fields=(InitPlan.Field(name='id', annotation=OpRef(name='init.fields.0.annot"
        "ation'), default=None, default_factory=OpRef(name='init.fields.0.default_factory'), init=True, override=False,"
        " field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='chat_id', a"
        "nnotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory"
        "=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None))"
        ", self_param='self', std_params=(), kw_only_params=('id', 'chat_id'), frozen=False, slots=False, post_init_par"
        "ams=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='id', kw_only=True, fn=None), Re"
        "prPlan.Field(name='chat_id', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='7e444005d72adfa0923b925c66293dae30c293cc',
    cls_names=(
        ('ommlds.cli.chat.drivers.state.last', 'LastChatId'),
    ),
)
def _process_dataclass__7e444005d72adfa0923b925c66293dae30c293cc():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default_factory,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__HAS_DEFAULT_FACTORY=dataclasses._HAS_DEFAULT_FACTORY,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__set_cls_attr,
    ):
        def __copy__(self):
            if self.__class__ is not __class__:
                raise TypeError(self)
            return __class__(  # noqa
                id=self.id,
                chat_id=self.chat_id,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.id == other.id and
                self.chat_id == other.chat_id
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass__set_cls_attr(__class__, '__hash__', None, 'replace')

        def __init__(
            self,
            *,
            id: __dataclass__init__fields__0__annotation = __dataclass__HAS_DEFAULT_FACTORY,
            chat_id: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            if id is __dataclass__HAS_DEFAULT_FACTORY:
                id = __dataclass__init__fields__0__default_factory()
            self.id = id
            self.chat_id = chat_id

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"id={self.id!r}")
            parts.append(f"chat_id={self.chat_id!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('enable_tools', 'dangerous_no_tool_confirmation', 'interactive', 'use_readline', '"
        "print_ai_responses', 'print_tool_use')), EqPlan(fields=('enable_tools', 'dangerous_no_tool_confirmation', 'int"
        "eractive', 'use_readline', 'print_ai_responses', 'print_tool_use')), FrozenPlan(fields=('enable_tools', 'dange"
        "rous_no_tool_confirmation', 'interactive', 'use_readline', 'print_ai_responses', 'print_tool_use'), allow_dyna"
        "mic_dunder_attrs=False), HashPlan(action='add', fields=('enable_tools', 'dangerous_no_tool_confirmation', 'int"
        "eractive', 'use_readline', 'print_ai_responses', 'print_tool_use'), cache=False), InitPlan(fields=(InitPlan.Fi"
        "eld(name='enable_tools', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0."
        "default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valida"
        "te=None, check_type=None), InitPlan.Field(name='dangerous_no_tool_confirmation', annotation=OpRef(name='init.f"
        "ields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=F"
        "alse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='intera"
        "ctive', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), defaul"
        "t_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_ty"
        "pe=None), InitPlan.Field(name='use_readline', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef"
        "(name='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE"
        ", coerce=None, validate=None, check_type=None), InitPlan.Field(name='print_ai_responses', annotation=OpRef(nam"
        "e='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, o"
        "verride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(nam"
        "e='print_tool_use', annotation=OpRef(name='init.fields.5.annotation'), default=OpRef(name='init.fields.5.defau"
        "lt'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=No"
        "ne, check_type=None)), self_param='self', std_params=(), kw_only_params=('enable_tools', 'dangerous_no_tool_co"
        "nfirmation', 'interactive', 'use_readline', 'print_ai_responses', 'print_tool_use'), frozen=True, slots=False,"
        " post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='enable_tools', kw"
        "_only=True, fn=None), ReprPlan.Field(name='dangerous_no_tool_confirmation', kw_only=True, fn=None), ReprPlan.F"
        "ield(name='interactive', kw_only=True, fn=None), ReprPlan.Field(name='use_readline', kw_only=True, fn=None), R"
        "eprPlan.Field(name='print_ai_responses', kw_only=True, fn=None), ReprPlan.Field(name='print_tool_use', kw_only"
        "=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='52a2d54a163fff09e0afbdcd47d432ceb7bf1a48',
    cls_names=(
        ('ommlds.cli.chat.interfaces.bare.configs', 'BareInterfaceConfig'),
    ),
)
def _process_dataclass__52a2d54a163fff09e0afbdcd47d432ceb7bf1a48():
    def _process_dataclass(
        *,
        __class__,
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
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__set_cls_attr,
    ):
        def __copy__(self):
            if self.__class__ is not __class__:
                raise TypeError(self)
            return __class__(  # noqa
                enable_tools=self.enable_tools,
                dangerous_no_tool_confirmation=self.dangerous_no_tool_confirmation,
                interactive=self.interactive,
                use_readline=self.use_readline,
                print_ai_responses=self.print_ai_responses,
                print_tool_use=self.print_tool_use,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.enable_tools == other.enable_tools and
                self.dangerous_no_tool_confirmation == other.dangerous_no_tool_confirmation and
                self.interactive == other.interactive and
                self.use_readline == other.use_readline and
                self.print_ai_responses == other.print_ai_responses and
                self.print_tool_use == other.print_tool_use
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___frozen_fields = {
            'enable_tools',
            'dangerous_no_tool_confirmation',
            'interactive',
            'use_readline',
            'print_ai_responses',
            'print_tool_use',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.enable_tools,
                self.dangerous_no_tool_confirmation,
                self.interactive,
                self.use_readline,
                self.print_ai_responses,
                self.print_tool_use,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            enable_tools: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            dangerous_no_tool_confirmation: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            interactive: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            use_readline: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            print_ai_responses: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            print_tool_use: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'enable_tools', enable_tools)
            __dataclass__object_setattr(self, 'dangerous_no_tool_confirmation', dangerous_no_tool_confirmation)
            __dataclass__object_setattr(self, 'interactive', interactive)
            __dataclass__object_setattr(self, 'use_readline', use_readline)
            __dataclass__object_setattr(self, 'print_ai_responses', print_ai_responses)
            __dataclass__object_setattr(self, 'print_tool_use', print_tool_use)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"enable_tools={self.enable_tools!r}")
            parts.append(f"dangerous_no_tool_confirmation={self.dangerous_no_tool_confirmation!r}")
            parts.append(f"interactive={self.interactive!r}")
            parts.append(f"use_readline={self.use_readline!r}")
            parts.append(f"print_ai_responses={self.print_ai_responses!r}")
            parts.append(f"print_tool_use={self.print_tool_use!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('enable_tools', 'dangerous_no_tool_confirmation')), EqPlan(fields=('enable_tools',"
        " 'dangerous_no_tool_confirmation')), FrozenPlan(fields=('enable_tools', 'dangerous_no_tool_confirmation'), all"
        "ow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('enable_tools', 'dangerous_no_tool_confirmation"
        "'), cache=False), InitPlan(fields=(InitPlan.Field(name='enable_tools', annotation=OpRef(name='init.fields.0.an"
        "notation'), default=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, fiel"
        "d_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='dangerous_no_too"
        "l_confirmation', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'"
        "), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None,"
        " check_type=None)), self_param='self', std_params=(), kw_only_params=('enable_tools', 'dangerous_no_tool_confi"
        "rmation'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(Re"
        "prPlan.Field(name='enable_tools', kw_only=True, fn=None), ReprPlan.Field(name='dangerous_no_tool_confirmation'"
        ", kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='d65d18393f357ae0fb02bb80268c6f1473462613',
    cls_names=(
        ('ommlds.cli.chat.interfaces.configs', 'InterfaceConfig'),
    ),
)
def _process_dataclass__d65d18393f357ae0fb02bb80268c6f1473462613():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__set_cls_attr,
    ):
        def __copy__(self):
            if self.__class__ is not __class__:
                raise TypeError(self)
            return __class__(  # noqa
                enable_tools=self.enable_tools,
                dangerous_no_tool_confirmation=self.dangerous_no_tool_confirmation,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.enable_tools == other.enable_tools and
                self.dangerous_no_tool_confirmation == other.dangerous_no_tool_confirmation
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___frozen_fields = {
            'enable_tools',
            'dangerous_no_tool_confirmation',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.enable_tools,
                self.dangerous_no_tool_confirmation,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            enable_tools: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            dangerous_no_tool_confirmation: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'enable_tools', enable_tools)
            __dataclass__object_setattr(self, 'dangerous_no_tool_confirmation', dangerous_no_tool_confirmation)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"enable_tools={self.enable_tools!r}")
            parts.append(f"dangerous_no_tool_confirmation={self.dangerous_no_tool_confirmation!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('enable_tools', 'dangerous_no_tool_confirmation', 'input_history_file', 'initial_t"
        "imeline_window')), EqPlan(fields=('enable_tools', 'dangerous_no_tool_confirmation', 'input_history_file', 'ini"
        "tial_timeline_window')), FrozenPlan(fields=('enable_tools', 'dangerous_no_tool_confirmation', 'input_history_f"
        "ile', 'initial_timeline_window'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('enable_to"
        "ols', 'dangerous_no_tool_confirmation', 'input_history_file', 'initial_timeline_window'), cache=False), InitPl"
        "an(fields=(InitPlan.Field(name='enable_tools', annotation=OpRef(name='init.fields.0.annotation'), default=OpRe"
        "f(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANC"
        "E, coerce=None, validate=None, check_type=None), InitPlan.Field(name='dangerous_no_tool_confirmation', annotat"
        "ion=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None,"
        " init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitP"
        "lan.Field(name='input_history_file', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='in"
        "it.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce="
        "None, validate=None, check_type=None), InitPlan.Field(name='initial_timeline_window', annotation=OpRef(name='i"
        "nit.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, overr"
        "ide=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', st"
        "d_params=(), kw_only_params=('enable_tools', 'dangerous_no_tool_confirmation', 'input_history_file', 'initial_"
        "timeline_window'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fi"
        "elds=(ReprPlan.Field(name='enable_tools', kw_only=True, fn=None), ReprPlan.Field(name='dangerous_no_tool_confi"
        "rmation', kw_only=True, fn=None), ReprPlan.Field(name='input_history_file', kw_only=True, fn=None), ReprPlan.F"
        "ield(name='initial_timeline_window', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='395225a24e95787741ef87bb2db8f54363855f4b',
    cls_names=(
        ('ommlds.cli.chat.interfaces.textual.configs', 'TextualInterfaceConfig'),
    ),
)
def _process_dataclass__395225a24e95787741ef87bb2db8f54363855f4b():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__3__default,
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__set_cls_attr,
    ):
        def __copy__(self):
            if self.__class__ is not __class__:
                raise TypeError(self)
            return __class__(  # noqa
                enable_tools=self.enable_tools,
                dangerous_no_tool_confirmation=self.dangerous_no_tool_confirmation,
                input_history_file=self.input_history_file,
                initial_timeline_window=self.initial_timeline_window,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.enable_tools == other.enable_tools and
                self.dangerous_no_tool_confirmation == other.dangerous_no_tool_confirmation and
                self.input_history_file == other.input_history_file and
                self.initial_timeline_window == other.initial_timeline_window
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___frozen_fields = {
            'enable_tools',
            'dangerous_no_tool_confirmation',
            'input_history_file',
            'initial_timeline_window',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.enable_tools,
                self.dangerous_no_tool_confirmation,
                self.input_history_file,
                self.initial_timeline_window,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            enable_tools: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            dangerous_no_tool_confirmation: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            input_history_file: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            initial_timeline_window: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'enable_tools', enable_tools)
            __dataclass__object_setattr(self, 'dangerous_no_tool_confirmation', dangerous_no_tool_confirmation)
            __dataclass__object_setattr(self, 'input_history_file', input_history_file)
            __dataclass__object_setattr(self, 'initial_timeline_window', initial_timeline_window)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"enable_tools={self.enable_tools!r}")
            parts.append(f"dangerous_no_tool_confirmation={self.dangerous_no_tool_confirmation!r}")
            parts.append(f"input_history_file={self.input_history_file!r}")
            parts.append(f"initial_timeline_window={self.initial_timeline_window!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('text', 'input_uuid')), EqPlan(fields=('text', 'input_uuid')), FrozenPlan(fields=("
        "'text', 'input_uuid'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('text', 'input_uuid')"
        ", cache=False), InitPlan(fields=(InitPlan.Field(name='text', annotation=OpRef(name='init.fields.0.annotation')"
        ", default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, v"
        "alidate=None, check_type=None), InitPlan.Field(name='input_uuid', annotation=OpRef(name='init.fields.1.annotat"
        "ion'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_typ"
        "e=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=('text',), "
        "kw_only_params=('input_uuid',), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=())"
        ", ReprPlan(fields=(ReprPlan.Field(name='text', kw_only=False, fn=None), ReprPlan.Field(name='input_uuid', kw_o"
        "nly=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='a147f14d22fda2880e5bb366e3496276b9fa48e1',
    cls_names=(
        ('ommlds.cli.chat.interfaces.textual.drivers.interface', 'ChatDriverInterface.UserInput'),
    ),
)
def _process_dataclass__a147f14d22fda2880e5bb366e3496276b9fa48e1():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__set_cls_attr,
    ):
        def __copy__(self):
            if self.__class__ is not __class__:
                raise TypeError(self)
            return __class__(  # noqa
                text=self.text,
                input_uuid=self.input_uuid,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.text == other.text and
                self.input_uuid == other.input_uuid
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___frozen_fields = {
            'text',
            'input_uuid',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.text,
                self.input_uuid,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            text: __dataclass__init__fields__0__annotation,
            *,
            input_uuid: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'text', text)
            __dataclass__object_setattr(self, 'input_uuid', input_uuid)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"text={self.text!r}")
            parts.append(f"input_uuid={self.input_uuid!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('widget', 'suppress_background_terminal_render')), EqPlan(fields=('widget', 'suppr"
        "ess_background_terminal_render')), FrozenPlan(fields=('widget', 'suppress_background_terminal_render'), allow_"
        "dynamic_dunder_attrs=False), HashPlan(action='add', fields=('widget', 'suppress_background_terminal_render'), "
        "cache=False), InitPlan(fields=(InitPlan.Field(name='widget', annotation=OpRef(name='init.fields.0.annotation')"
        ", default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, v"
        "alidate=None, check_type=None), InitPlan.Field(name='suppress_background_terminal_render', annotation=OpRef(na"
        "me='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, "
        "override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self"
        "', std_params=('widget',), kw_only_params=('suppress_background_terminal_render',), frozen=True, slots=False, "
        "post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='widget', kw_only=F"
        "alse, fn=None), ReprPlan.Field(name='suppress_background_terminal_render', kw_only=True, fn=None)), id=False, "
        "terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='9cff50c2c577123575c62011012f75c6f36c9841',
    cls_names=(
        ('ommlds.cli.chat.interfaces.textual.drivers.interface', '_MountWidgetDisplayOp'),
    ),
)
def _process_dataclass__9cff50c2c577123575c62011012f75c6f36c9841():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__set_cls_attr,
    ):
        def __copy__(self):
            if self.__class__ is not __class__:
                raise TypeError(self)
            return __class__(  # noqa
                widget=self.widget,
                suppress_background_terminal_render=self.suppress_background_terminal_render,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.widget == other.widget and
                self.suppress_background_terminal_render == other.suppress_background_terminal_render
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___frozen_fields = {
            'widget',
            'suppress_background_terminal_render',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.widget,
                self.suppress_background_terminal_render,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            widget: __dataclass__init__fields__0__annotation,
            *,
            suppress_background_terminal_render: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'widget', widget)
            __dataclass__object_setattr(self, 'suppress_background_terminal_render', suppress_background_terminal_render)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"widget={self.widget!r}")
            parts.append(f"suppress_background_terminal_render={self.suppress_background_terminal_render!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('widgets', 'anchor')), EqPlan(fields=('widgets', 'anchor')), FrozenPlan(fields=('w"
        "idgets', 'anchor'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('widgets', 'anchor'), ca"
        "che=False), InitPlan(fields=(InitPlan.Field(name='widgets', annotation=OpRef(name='init.fields.0.annotation'),"
        " default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, va"
        "lidate=None, check_type=None), InitPlan.Field(name='anchor', annotation=OpRef(name='init.fields.1.annotation')"
        ", default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, v"
        "alidate=None, check_type=None)), self_param='self', std_params=('widgets', 'anchor'), kw_only_params=(), froze"
        "n=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(nam"
        "e='widgets', kw_only=False, fn=None), ReprPlan.Field(name='anchor', kw_only=False, fn=None)), id=False, terse="
        "False, default_fn=None)))"
    ),
    plan_repr_sha1='c8a1672c8ceaf957e0a0adcc6bdcab5c38001b37',
    cls_names=(
        ('ommlds.cli.chat.interfaces.textual.drivers.interface', '_MountWidgetsBeforeDisplayOp'),
    ),
)
def _process_dataclass__c8a1672c8ceaf957e0a0adcc6bdcab5c38001b37():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__set_cls_attr,
    ):
        def __copy__(self):
            if self.__class__ is not __class__:
                raise TypeError(self)
            return __class__(  # noqa
                widgets=self.widgets,
                anchor=self.anchor,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.widgets == other.widgets and
                self.anchor == other.anchor
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___frozen_fields = {
            'widgets',
            'anchor',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.widgets,
                self.anchor,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            widgets: __dataclass__init__fields__0__annotation,
            anchor: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'widgets', widgets)
            __dataclass__object_setattr(self, 'anchor', anchor)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"widgets={self.widgets!r}")
            parts.append(f"anchor={self.anchor!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('item',)), EqPlan(fields=('item',)), FrozenPlan(fields=('item',), allow_dynamic_du"
        "nder_attrs=False), HashPlan(action='add', fields=('item',), cache=False), InitPlan(fields=(InitPlan.Field(name"
        "='item', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, ove"
        "rride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self',"
        " std_params=('item',), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_fns=(), valida"
        "te_fns=()), ReprPlan(fields=(ReprPlan.Field(name='item', kw_only=False, fn=None),), id=False, terse=False, def"
        "ault_fn=None)))"
    ),
    plan_repr_sha1='0072a5741bd0a60ad6f5c39690cf360882fbe293',
    cls_names=(
        ('ommlds.cli.chat.interfaces.textual.drivers.interface', '_UpdateToolDisplayOp'),
    ),
)
def _process_dataclass__0072a5741bd0a60ad6f5c39690cf360882fbe293():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__set_cls_attr,
    ):
        def __copy__(self):
            if self.__class__ is not __class__:
                raise TypeError(self)
            return __class__(  # noqa
                item=self.item,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.item == other.item
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___frozen_fields = {
            'item',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.item,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            item: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'item', item)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"item={self.item!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('label', 'description', 'selected')), EqPlan(fields=('label', 'description', 'sele"
        "cted')), FrozenPlan(fields=('label', 'description', 'selected'), allow_dynamic_dunder_attrs=False), HashPlan(a"
        "ction='add', fields=('label', 'description', 'selected'), cache=False), InitPlan(fields=(InitPlan.Field(name='"
        "label', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, over"
        "ride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='"
        "description', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), "
        "default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, ch"
        "eck_type=None), InitPlan.Field(name='selected', annotation=OpRef(name='init.fields.2.annotation'), default=OpR"
        "ef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTAN"
        "CE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=('label', 'description'), kw_"
        "only_params=('selected',), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), Rep"
        "rPlan(fields=(ReprPlan.Field(name='label', kw_only=False, fn=None), ReprPlan.Field(name='description', kw_only"
        "=False, fn=None), ReprPlan.Field(name='selected', kw_only=True, fn=None)), id=False, terse=False, default_fn=N"
        "one)))"
    ),
    plan_repr_sha1='27e469b5e8a66ab2f1817b6747e2f6b66cd79dbd',
    cls_names=(
        ('ommlds.cli.chat.interfaces.textual.suggestions', 'SuggestionItem'),
    ),
)
def _process_dataclass__27e469b5e8a66ab2f1817b6747e2f6b66cd79dbd():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__set_cls_attr,
    ):
        def __copy__(self):
            if self.__class__ is not __class__:
                raise TypeError(self)
            return __class__(  # noqa
                label=self.label,
                description=self.description,
                selected=self.selected,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.label == other.label and
                self.description == other.description and
                self.selected == other.selected
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___frozen_fields = {
            'label',
            'description',
            'selected',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.label,
                self.description,
                self.selected,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            label: __dataclass__init__fields__0__annotation,
            description: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            *,
            selected: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'label', label)
            __dataclass__object_setattr(self, 'description', description)
            __dataclass__object_setattr(self, 'selected', selected)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"label={self.label!r}")
            parts.append(f"description={self.description!r}")
            parts.append(f"selected={self.selected!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('max_items',)), EqPlan(fields=('max_items',)), FrozenPlan(fields=('max_items',), a"
        "llow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('max_items',), cache=False), InitPlan(fields="
        "(InitPlan.Field(name='max_items', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init."
        "fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=Non"
        "e, validate=None, check_type=None),), self_param='self', std_params=('max_items',), kw_only_params=(), frozen="
        "True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name="
        "'max_items', kw_only=False, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='6963b0f0c27facaf712095f140ca422be3935ff7',
    cls_names=(
        ('ommlds.cli.chat.interfaces.textual.suggestions', 'SuggestionsManager.Config'),
    ),
)
def _process_dataclass__6963b0f0c27facaf712095f140ca422be3935ff7():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__set_cls_attr,
    ):
        def __copy__(self):
            if self.__class__ is not __class__:
                raise TypeError(self)
            return __class__(  # noqa
                max_items=self.max_items,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.max_items == other.max_items
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___frozen_fields = {
            'max_items',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.max_items,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            max_items: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'max_items', max_items)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"max_items={self.max_items!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('text',)), EqPlan(fields=('text',)), HashPlan(action='set_none', fields=None, cach"
        "e=None), InitPlan(fields=(InitPlan.Field(name='text', annotation=OpRef(name='init.fields.0.annotation'), defau"
        "lt=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate"
        "=None, check_type=None),), self_param='self', std_params=('text',), kw_only_params=(), frozen=False, slots=Fal"
        "se, post_init_params=(), init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='text', kw_only=F"
        "alse, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='305f12128eb40e3772ab0fec3fd8182bde52bde6',
    cls_names=(
        ('ommlds.cli.chat.interfaces.textual.widgets.input', 'InputTextArea.HistoryNext'),
        ('ommlds.cli.chat.interfaces.textual.widgets.input', 'InputTextArea.HistoryPrevious'),
        ('ommlds.cli.chat.interfaces.textual.widgets.input', 'InputTextArea.Submitted'),
    ),
)
def _process_dataclass__305f12128eb40e3772ab0fec3fd8182bde52bde6():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__None=None,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__set_cls_attr,
    ):
        def __copy__(self):
            if self.__class__ is not __class__:
                raise TypeError(self)
            return __class__(  # noqa
                text=self.text,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.text == other.text
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass__set_cls_attr(__class__, '__hash__', None, 'replace')

        def __init__(
            self,
            text: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            self.text = text
            self.__post_init__()

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"text={self.text!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=()), EqPlan(fields=()), HashPlan(action='set_none', fields=None, cache=None), InitP"
        "lan(fields=(), self_param='self', std_params=(), kw_only_params=(), frozen=False, slots=False, post_init_param"
        "s=(), init_fns=(), validate_fns=()), ReprPlan(fields=(), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='d8b7f224596d6b56ca61048e31a647b16a3fb3fe',
    cls_names=(
        ('ommlds.cli.chat.interfaces.textual.widgets.input', 'InputTextArea.HistoryReset'),
    ),
)
def _process_dataclass__d8b7f224596d6b56ca61048e31a647b16a3fb3fe():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__None=None,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__set_cls_attr,
    ):
        def __copy__(self):
            if self.__class__ is not __class__:
                raise TypeError(self)
            return __class__()  # noqa

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return True

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass__set_cls_attr(__class__, '__hash__', None, 'replace')

        def __init__(
            self,
        ) -> __dataclass__None:
            self.__post_init__()

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            return f"{self.__class__.__qualname__}()"

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('widget',)), EqPlan(fields=('widget',)), HashPlan(action='set_none', fields=None, "
        "cache=None), InitPlan(fields=(InitPlan.Field(name='widget', annotation=OpRef(name='init.fields.0.annotation'),"
        " default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, va"
        "lidate=None, check_type=None),), self_param='self', std_params=('widget',), kw_only_params=(), frozen=False, s"
        "lots=False, post_init_params=(), init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='widget',"
        " kw_only=False, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='95d0b95631fc69464dd20fa9e5c73baceb4022ef',
    cls_names=(
        ('ommlds.cli.chat.interfaces.textual.widgets.messages.base', 'MessageFinalized'),
    ),
)
def _process_dataclass__95d0b95631fc69464dd20fa9e5c73baceb4022ef():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__None=None,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__set_cls_attr,
    ):
        def __copy__(self):
            if self.__class__ is not __class__:
                raise TypeError(self)
            return __class__(  # noqa
                widget=self.widget,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.widget == other.widget
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass__set_cls_attr(__class__, '__hash__', None, 'replace')

        def __init__(
            self,
            widget: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            self.widget = widget
            self.__post_init__()

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"widget={self.widget!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('event',)), EqPlan(fields=('event',)), HashPlan(action='set_none', fields=None, ca"
        "che=None), InitPlan(fields=(InitPlan.Field(name='event', annotation=OpRef(name='init.fields.0.annotation'), de"
        "fault=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valid"
        "ate=None, check_type=None),), self_param='self', std_params=('event',), kw_only_params=(), frozen=False, slots"
        "=False, post_init_params=(), init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='event', kw_o"
        "nly=False, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='83158fd71009009aca5b015ecb87be1b8e679204',
    cls_names=(
        ('ommlds.cli.chat.interfaces.textual.widgets.messages.divider', 'MessageDividerClicked'),
    ),
)
def _process_dataclass__83158fd71009009aca5b015ecb87be1b8e679204():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__None=None,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__set_cls_attr,
    ):
        def __copy__(self):
            if self.__class__ is not __class__:
                raise TypeError(self)
            return __class__(  # noqa
                event=self.event,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.event == other.event
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass__set_cls_attr(__class__, '__hash__', None, 'replace')

        def __init__(
            self,
            event: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            self.event = event
            self.__post_init__()

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"event={self.event!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('message_cls', 'message_uuid', 'content')), EqPlan(fields=('message_cls', 'message"
        "_uuid', 'content')), FrozenPlan(fields=('message_cls', 'message_uuid', 'content'), allow_dynamic_dunder_attrs="
        "False), HashPlan(action='add', fields=('message_cls', 'message_uuid', 'content'), cache=False), InitPlan(field"
        "s=(InitPlan.Field(name='message_cls', annotation=OpRef(name='init.fields.0.annotation'), default=None, default"
        "_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_typ"
        "e=None), InitPlan.Field(name='message_uuid', annotation=OpRef(name='init.fields.1.annotation'), default=None, "
        "default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, ch"
        "eck_type=None), InitPlan.Field(name='content', annotation=OpRef(name='init.fields.2.annotation'), default=None"
        ", default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, "
        "check_type=None)), self_param='self', std_params=('message_cls', 'message_uuid', 'content'), kw_only_params=()"
        ", frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Fi"
        "eld(name='message_cls', kw_only=False, fn=None), ReprPlan.Field(name='message_uuid', kw_only=False, fn=None), "
        "ReprPlan.Field(name='content', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='3917b2b788efbec688302f5dadedc283d4c50a2e',
    cls_names=(
        ('ommlds.cli.chat.interfaces.textual.widgets.messages.stream', 'ContentStreamMessagePart'),
    ),
)
def _process_dataclass__3917b2b788efbec688302f5dadedc283d4c50a2e():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__set_cls_attr,
    ):
        def __copy__(self):
            if self.__class__ is not __class__:
                raise TypeError(self)
            return __class__(  # noqa
                message_cls=self.message_cls,
                message_uuid=self.message_uuid,
                content=self.content,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.message_cls == other.message_cls and
                self.message_uuid == other.message_uuid and
                self.content == other.content
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___frozen_fields = {
            'message_cls',
            'message_uuid',
            'content',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.message_cls,
                self.message_uuid,
                self.content,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            message_cls: __dataclass__init__fields__0__annotation,
            message_uuid: __dataclass__init__fields__1__annotation,
            content: __dataclass__init__fields__2__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'message_cls', message_cls)
            __dataclass__object_setattr(self, 'message_uuid', message_uuid)
            __dataclass__object_setattr(self, 'content', content)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"message_cls={self.message_cls!r}")
            parts.append(f"message_uuid={self.message_uuid!r}")
            parts.append(f"content={self.content!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('message_cls', 'message_uuid')), EqPlan(fields=('message_cls', 'message_uuid')), F"
        "rozenPlan(fields=('message_cls', 'message_uuid'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fi"
        "elds=('message_cls', 'message_uuid'), cache=False), InitPlan(fields=(InitPlan.Field(name='message_cls', annota"
        "tion=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, fi"
        "eld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='message_uuid',"
        " annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=Fa"
        "lse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_para"
        "ms=('message_cls', 'message_uuid'), kw_only_params=(), frozen=True, slots=False, post_init_params=None, init_f"
        "ns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='message_cls', kw_only=False, fn=None), ReprPlan"
        ".Field(name='message_uuid', kw_only=False, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='6390dd582efec3ac653751cc487ba776aaf9f288',
    cls_names=(
        ('ommlds.cli.chat.interfaces.textual.widgets.messages.stream', 'FinalStreamMessagePart'),
        ('ommlds.cli.chat.interfaces.textual.widgets.messages.stream', 'StreamMessagePart'),
    ),
)
def _process_dataclass__6390dd582efec3ac653751cc487ba776aaf9f288():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__set_cls_attr,
    ):
        def __copy__(self):
            if self.__class__ is not __class__:
                raise TypeError(self)
            return __class__(  # noqa
                message_cls=self.message_cls,
                message_uuid=self.message_uuid,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.message_cls == other.message_cls and
                self.message_uuid == other.message_uuid
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___frozen_fields = {
            'message_cls',
            'message_uuid',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.message_cls,
                self.message_uuid,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            message_cls: __dataclass__init__fields__0__annotation,
            message_uuid: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'message_cls', message_cls)
            __dataclass__object_setattr(self, 'message_uuid', message_uuid)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"message_cls={self.message_cls!r}")
            parts.append(f"message_uuid={self.message_uuid!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('enable_tools', 'dangerous_no_tool_confirmation', 'port')), EqPlan(fields=('enable"
        "_tools', 'dangerous_no_tool_confirmation', 'port')), FrozenPlan(fields=('enable_tools', 'dangerous_no_tool_con"
        "firmation', 'port'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('enable_tools', 'danger"
        "ous_no_tool_confirmation', 'port'), cache=False), InitPlan(fields=(InitPlan.Field(name='enable_tools', annotat"
        "ion=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'), default_factory=None,"
        " init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitP"
        "lan.Field(name='dangerous_no_tool_confirmation', annotation=OpRef(name='init.fields.1.annotation'), default=Op"
        "Ref(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTA"
        "NCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='port', annotation=OpRef(name='init.fie"
        "lds.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=Fal"
        "se, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_param"
        "s=(), kw_only_params=('enable_tools', 'dangerous_no_tool_confirmation', 'port'), frozen=True, slots=False, pos"
        "t_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='enable_tools', kw_onl"
        "y=True, fn=None), ReprPlan.Field(name='dangerous_no_tool_confirmation', kw_only=True, fn=None), ReprPlan.Field"
        "(name='port', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='eec261fc7183d7eac72390ec16a7bdf778198fde',
    cls_names=(
        ('ommlds.cli.chat.interfaces.web.configs', 'WebInterfaceConfig'),
    ),
)
def _process_dataclass__eec261fc7183d7eac72390ec16a7bdf778198fde():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__2__default,
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__set_cls_attr,
    ):
        def __copy__(self):
            if self.__class__ is not __class__:
                raise TypeError(self)
            return __class__(  # noqa
                enable_tools=self.enable_tools,
                dangerous_no_tool_confirmation=self.dangerous_no_tool_confirmation,
                port=self.port,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.enable_tools == other.enable_tools and
                self.dangerous_no_tool_confirmation == other.dangerous_no_tool_confirmation and
                self.port == other.port
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___frozen_fields = {
            'enable_tools',
            'dangerous_no_tool_confirmation',
            'port',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.enable_tools,
                self.dangerous_no_tool_confirmation,
                self.port,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            enable_tools: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            dangerous_no_tool_confirmation: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            port: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'enable_tools', enable_tools)
            __dataclass__object_setattr(self, 'dangerous_no_tool_confirmation', dangerous_no_tool_confirmation)
            __dataclass__object_setattr(self, 'port', port)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"enable_tools={self.enable_tools!r}")
            parts.append(f"dangerous_no_tool_confirmation={self.dangerous_no_tool_confirmation!r}")
            parts.append(f"port={self.port!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('modules', 'backend', 'content')), EqPlan(fields=('modules', 'backend', 'content')"
        "), FrozenPlan(fields=('modules', 'backend', 'content'), allow_dynamic_dunder_attrs=False), HashPlan(action='ad"
        "d', fields=('modules', 'backend', 'content'), cache=False), InitPlan(fields=(InitPlan.Field(name='modules', an"
        "notation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'), default_factory="
        "None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), "
        "InitPlan.Field(name='backend', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fie"
        "lds.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, "
        "validate=None, check_type=None), InitPlan.Field(name='content', annotation=OpRef(name='init.fields.2.annotatio"
        "n'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None"
        ", validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('modules', 'backend', 'c"
        "ontent'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(Rep"
        "rPlan.Field(name='modules', kw_only=True, fn=None), ReprPlan.Field(name='backend', kw_only=True, fn=None), Rep"
        "rPlan.Field(name='content', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='d081083bc028fb9729b8423fbe45bb996d3e439f',
    cls_names=(
        ('ommlds.cli.completion.configs', 'CompletionConfig'),
        ('ommlds.cli.embedding.configs', 'EmbeddingConfig'),
    ),
)
def _process_dataclass__d081083bc028fb9729b8423fbe45bb996d3e439f():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__init__fields__2__annotation,
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__set_cls_attr,
    ):
        def __copy__(self):
            if self.__class__ is not __class__:
                raise TypeError(self)
            return __class__(  # noqa
                modules=self.modules,
                backend=self.backend,
                content=self.content,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.modules == other.modules and
                self.backend == other.backend and
                self.content == other.content
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___frozen_fields = {
            'modules',
            'backend',
            'content',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.modules,
                self.backend,
                self.content,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            modules: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            backend: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            content: __dataclass__init__fields__2__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'modules', modules)
            __dataclass__object_setattr(self, 'backend', backend)
            __dataclass__object_setattr(self, 'content', content)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"modules={self.modules!r}")
            parts.append(f"backend={self.backend!r}")
            parts.append(f"content={self.content!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('modules',)), EqPlan(fields=('modules',)), FrozenPlan(fields=('modules',), allow_d"
        "ynamic_dunder_attrs=False), HashPlan(action='add', fields=('modules',), cache=False), InitPlan(fields=(InitPla"
        "n.Field(name='modules', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.d"
        "efault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validat"
        "e=None, check_type=None),), self_param='self', std_params=(), kw_only_params=('modules',), frozen=True, slots="
        "False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='modules', k"
        "w_only=True, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='b3c5ceb1d3f2d52621e06fa7d3819d96ffea7347',
    cls_names=(
        ('ommlds.cli.configs', 'EntrypointConfig'),
    ),
)
def _process_dataclass__b3c5ceb1d3f2d52621e06fa7d3819d96ffea7347():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__set_cls_attr,
    ):
        def __copy__(self):
            if self.__class__ is not __class__:
                raise TypeError(self)
            return __class__(  # noqa
                modules=self.modules,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.modules == other.modules
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___frozen_fields = {
            'modules',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.modules,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            modules: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'modules', modules)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"modules={self.modules!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('markdown',)), EqPlan(fields=('markdown',)), FrozenPlan(fields=('markdown',), allo"
        "w_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('markdown',), cache=False), InitPlan(fields=(Ini"
        "tPlan.Field(name='markdown', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.field"
        "s.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, va"
        "lidate=None, check_type=None),), self_param='self', std_params=(), kw_only_params=('markdown',), frozen=True, "
        "slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='markd"
        "own', kw_only=True, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='254623427d52b86f69ed60d24a0e95b0b1b391ca',
    cls_names=(
        ('ommlds.cli.interfaces.bare.printing.configs', 'PrintingConfig'),
    ),
)
def _process_dataclass__254623427d52b86f69ed60d24a0e95b0b1b391ca():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__set_cls_attr,
    ):
        def __copy__(self):
            if self.__class__ is not __class__:
                raise TypeError(self)
            return __class__(  # noqa
                markdown=self.markdown,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.markdown == other.markdown
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___frozen_fields = {
            'markdown',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.markdown,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            markdown: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'markdown', markdown)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"markdown={self.markdown!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('profile', 'args')), EqPlan(fields=('profile', 'args')), FrozenPlan(fields=('profi"
        "le', 'args'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('profile', 'args'), cache=Fals"
        "e), InitPlan(fields=(InitPlan.Field(name='profile', annotation=OpRef(name='init.fields.0.annotation'), default"
        "=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=N"
        "one, check_type=None), InitPlan.Field(name='args', annotation=OpRef(name='init.fields.1.annotation'), default="
        "None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=No"
        "ne, check_type=None)), self_param='self', std_params=('profile', 'args'), kw_only_params=(), frozen=True, slot"
        "s=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='profile',"
        " kw_only=False, fn=None), ReprPlan.Field(name='args', kw_only=False, fn=None)), id=False, terse=False, default"
        "_fn=None)))"
    ),
    plan_repr_sha1='3ca2bdd121559ad92e95a0e4bdf8210452f20e5d',
    cls_names=(
        ('ommlds.cli.profiles', 'ProfileAspect.ConfigureContext'),
    ),
)
def _process_dataclass__3ca2bdd121559ad92e95a0e4bdf8210452f20e5d():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
        __dataclass__None=None,  # noqa
        __dataclass___recursive_repr=reprlib.recursive_repr,  # noqa
        __dataclass__object_setattr=object.__setattr__,  # noqa
        __dataclass__set_cls_attr,
    ):
        def __copy__(self):
            if self.__class__ is not __class__:
                raise TypeError(self)
            return __class__(  # noqa
                profile=self.profile,
                args=self.args,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.profile == other.profile and
                self.args == other.args
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___frozen_fields = {
            'profile',
            'args',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.profile,
                self.args,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            profile: __dataclass__init__fields__0__annotation,
            args: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'profile', profile)
            __dataclass__object_setattr(self, 'args', args)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"profile={self.profile!r}")
            parts.append(f"args={self.args!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass
