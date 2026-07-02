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
        "Plans(tup=(CopyPlan(fields=('load_session', 'mcp_capabilities', 'prompt_capabilities', 'session_capabilities',"
        " 'meta')), EqPlan(fields=('load_session', 'mcp_capabilities', 'prompt_capabilities', 'session_capabilities', '"
        "meta')), FrozenPlan(fields=('load_session', 'mcp_capabilities', 'prompt_capabilities', 'session_capabilities',"
        " 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('load_session', 'mcp_capabilities'"
        ", 'prompt_capabilities', 'session_capabilities', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='"
        "load_session', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'),"
        " default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, c"
        "heck_type=None), InitPlan.Field(name='mcp_capabilities', annotation=OpRef(name='init.fields.1.annotation'), de"
        "fault=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldTy"
        "pe.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='prompt_capabilities', annotati"
        "on=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, "
        "init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPl"
        "an.Field(name='session_capabilities', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='i"
        "nit.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce"
        "=None, validate=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.4.annot"
        "ation'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, override=False, field_t"
        "ype=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_on"
        "ly_params=('load_session', 'mcp_capabilities', 'prompt_capabilities', 'session_capabilities', 'meta'), frozen="
        "True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name="
        "'load_session', kw_only=True, fn=None), ReprPlan.Field(name='mcp_capabilities', kw_only=True, fn=None), ReprPl"
        "an.Field(name='prompt_capabilities', kw_only=True, fn=None), ReprPlan.Field(name='session_capabilities', kw_on"
        "ly=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), id=False, terse=False, default_fn=None"
        ")))"
    ),
    plan_repr_sha1='ee4d52c828b1db53b2acb8b345849cae44e53e33',
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
        ('ommlds.specs.acp.protocol', 'AgentCapabilities'),
    ),
)
def _process_dataclass__ee4d52c828b1db53b2acb8b345849cae44e53e33():
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
                load_session=self.load_session,
                mcp_capabilities=self.mcp_capabilities,
                prompt_capabilities=self.prompt_capabilities,
                session_capabilities=self.session_capabilities,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.load_session == other.load_session and
                self.mcp_capabilities == other.mcp_capabilities and
                self.prompt_capabilities == other.prompt_capabilities and
                self.session_capabilities == other.session_capabilities and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'load_session',
            'mcp_capabilities',
            'prompt_capabilities',
            'session_capabilities',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'load_session',
            'mcp_capabilities',
            'prompt_capabilities',
            'session_capabilities',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.load_session,
                self.mcp_capabilities,
                self.prompt_capabilities,
                self.session_capabilities,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            load_session: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            mcp_capabilities: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            prompt_capabilities: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            session_capabilities: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            meta: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'load_session', load_session)
            __dataclass__object_setattr(self, 'mcp_capabilities', mcp_capabilities)
            __dataclass__object_setattr(self, 'prompt_capabilities', prompt_capabilities)
            __dataclass__object_setattr(self, 'session_capabilities', session_capabilities)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"load_session={self.load_session!r}")
            parts.append(f"mcp_capabilities={self.mcp_capabilities!r}")
            parts.append(f"prompt_capabilities={self.prompt_capabilities!r}")
            parts.append(f"session_capabilities={self.session_capabilities!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('content', 'session_update', 'meta')), EqPlan(fields=('content', 'session_update',"
        " 'meta')), FrozenPlan(fields=('content', 'session_update', 'meta'), allow_dynamic_dunder_attrs=False), HashPla"
        "n(action='add', fields=('content', 'session_update', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(na"
        "me='content', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True"
        ", override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field("
        "name='session_update', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.de"
        "fault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate"
        "=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.2.annotation'), defaul"
        "t=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.I"
        "NSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('con"
        "tent', 'session_update', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=("
        ")), ReprPlan(fields=(ReprPlan.Field(name='content', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_onl"
        "y=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='31ed430692c23fb3cbca1bed435729411ef598a2',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'AgentMessageChunkSessionUpdate'),
        ('ommlds.specs.acp.protocol', 'AgentThoughtChunkSessionUpdate'),
        ('ommlds.specs.acp.protocol', 'UserMessageChunkSessionUpdate'),
    ),
)
def _process_dataclass__31ed430692c23fb3cbca1bed435729411ef598a2():
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
                content=self.content,
                session_update=self.session_update,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.content == other.content and
                self.session_update == other.session_update and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'content',
            'session_update',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'content',
            'session_update',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.content,
                self.session_update,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            content: __dataclass__init__fields__0__annotation,
            session_update: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            meta: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'content', content)
            __dataclass__object_setattr(self, 'session_update', session_update)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"content={self.content!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('method', 'params')), EqPlan(fields=('method', 'params')), FrozenPlan(fields=('met"
        "hod', 'params'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('method', 'params'), cache="
        "False), InitPlan(fields=(InitPlan.Field(name='method', annotation=OpRef(name='init.fields.0.annotation'), defa"
        "ult=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validat"
        "e=None, check_type=None), InitPlan.Field(name='params', annotation=OpRef(name='init.fields.1.annotation'), def"
        "ault=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldTyp"
        "e.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('"
        "method', 'params'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(f"
        "ields=(ReprPlan.Field(name='method', kw_only=True, fn=None), ReprPlan.Field(name='params', kw_only=True, fn=No"
        "ne)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='2b0747cf2def5e479b402841b795a7dd2e6fb91c',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'AgentNotification'),
        ('ommlds.specs.acp.protocol', 'ClientNotification'),
    ),
)
def _process_dataclass__2b0747cf2def5e479b402841b795a7dd2e6fb91c():
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
                method=self.method,
                params=self.params,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.method == other.method and
                self.params == other.params
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'method',
            'params',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'method',
            'params',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.method,
                self.params,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            method: __dataclass__init__fields__0__annotation,
            params: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'method', method)
            __dataclass__object_setattr(self, 'params', params)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"method={self.method!r}")
            parts.append(f"params={self.params!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('id', 'method', 'params')), EqPlan(fields=('id', 'method', 'params')), FrozenPlan("
        "fields=('id', 'method', 'params'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('id', 'me"
        "thod', 'params'), cache=False), InitPlan(fields=(InitPlan.Field(name='id', annotation=OpRef(name='init.fields."
        "0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, "
        "coerce=None, validate=None, check_type=None), InitPlan.Field(name='method', annotation=OpRef(name='init.fields"
        ".1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE,"
        " coerce=None, validate=None, check_type=None), InitPlan.Field(name='params', annotation=OpRef(name='init.field"
        "s.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False"
        ", field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params="
        "(), kw_only_params=('id', 'method', 'params'), frozen=True, slots=False, post_init_params=None, init_fns=(), v"
        "alidate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='id', kw_only=True, fn=None), ReprPlan.Field(name='metho"
        "d', kw_only=True, fn=None), ReprPlan.Field(name='params', kw_only=True, fn=None)), id=False, terse=False, defa"
        "ult_fn=None)))"
    ),
    plan_repr_sha1='0c7f37642e561c61aa4ab609553040ec7fcc503e',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'AgentRequest'),
        ('ommlds.specs.acp.protocol', 'ClientRequest'),
    ),
)
def _process_dataclass__0c7f37642e561c61aa4ab609553040ec7fcc503e():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
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
                id=self.id,
                method=self.method,
                params=self.params,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.id == other.id and
                self.method == other.method and
                self.params == other.params
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'id',
            'method',
            'params',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'id',
            'method',
            'params',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.id,
                self.method,
                self.params,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            id: __dataclass__init__fields__0__annotation,
            method: __dataclass__init__fields__1__annotation,
            params: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'method', method)
            __dataclass__object_setattr(self, 'params', params)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"id={self.id!r}")
            parts.append(f"method={self.method!r}")
            parts.append(f"params={self.params!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('error', 'id')), EqPlan(fields=('error', 'id')), FrozenPlan(fields=('error', 'id')"
        ", allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('error', 'id'), cache=False), InitPlan(fie"
        "lds=(InitPlan.Field(name='error', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_fac"
        "tory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=No"
        "ne), InitPlan.Field(name='id', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factor"
        "y=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)"
        "), self_param='self', std_params=(), kw_only_params=('error', 'id'), frozen=True, slots=False, post_init_param"
        "s=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='error', kw_only=True, fn=None), R"
        "eprPlan.Field(name='id', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='4b0948e5f368737e30e63e06f2f28da1159aa958',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'AgentresponseError'),
        ('ommlds.specs.acp.protocol', 'ClientresponseError'),
    ),
)
def _process_dataclass__4b0948e5f368737e30e63e06f2f28da1159aa958():
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
                error=self.error,
                id=self.id,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.error == other.error and
                self.id == other.id
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'error',
            'id',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'error',
            'id',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.error,
                self.id,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            error: __dataclass__init__fields__0__annotation,
            id: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'error', error)
            __dataclass__object_setattr(self, 'id', id)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"error={self.error!r}")
            parts.append(f"id={self.id!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('id', 'result')), EqPlan(fields=('id', 'result')), FrozenPlan(fields=('id', 'resul"
        "t'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('id', 'result'), cache=False), InitPlan"
        "(fields=(InitPlan.Field(name='id', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_fa"
        "ctory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=N"
        "one), InitPlan.Field(name='result', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_f"
        "actory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type="
        "None)), self_param='self', std_params=(), kw_only_params=('id', 'result'), frozen=True, slots=False, post_init"
        "_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='id', kw_only=True, fn=None)"
        ", ReprPlan.Field(name='result', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='47dc9231421fd90fda2e3a8b4096c69e2650fe37',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'AgentresponseResult'),
        ('ommlds.specs.acp.protocol', 'ClientresponseResult'),
    ),
)
def _process_dataclass__47dc9231421fd90fda2e3a8b4096c69e2650fe37():
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
                id=self.id,
                result=self.result,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.id == other.id and
                self.result == other.result
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'id',
            'result',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'id',
            'result',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.id,
                self.result,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            id: __dataclass__init__fields__0__annotation,
            result: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'result', result)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"id={self.id!r}")
            parts.append(f"result={self.result!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('audience', 'last_modified', 'priority', 'meta')), EqPlan(fields=('audience', 'las"
        "t_modified', 'priority', 'meta')), FrozenPlan(fields=('audience', 'last_modified', 'priority', 'meta'), allow_"
        "dynamic_dunder_attrs=False), HashPlan(action='add', fields=('audience', 'last_modified', 'priority', 'meta'), "
        "cache=False), InitPlan(fields=(InitPlan.Field(name='audience', annotation=OpRef(name='init.fields.0.annotation"
        "'), default=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=F"
        "ieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='last_modified', annotati"
        "on=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, "
        "init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPl"
        "an.Field(name='priority', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2"
        ".default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valid"
        "ate=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.3.annotation'), def"
        "ault=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldTyp"
        "e.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('"
        "audience', 'last_modified', 'priority', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(),"
        " validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='audience', kw_only=True, fn=None), ReprPlan.Field(nam"
        "e='last_modified', kw_only=True, fn=None), ReprPlan.Field(name='priority', kw_only=True, fn=None), ReprPlan.Fi"
        "eld(name='meta', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='9fcd599f66de88b7c8bff2ec200188ce287b1faa',
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
        ('ommlds.specs.acp.protocol', 'Annotations'),
    ),
)
def _process_dataclass__9fcd599f66de88b7c8bff2ec200188ce287b1faa():
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
                audience=self.audience,
                last_modified=self.last_modified,
                priority=self.priority,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.audience == other.audience and
                self.last_modified == other.last_modified and
                self.priority == other.priority and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'audience',
            'last_modified',
            'priority',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'audience',
            'last_modified',
            'priority',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.audience,
                self.last_modified,
                self.priority,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            audience: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            last_modified: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            priority: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            meta: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'audience', audience)
            __dataclass__object_setattr(self, 'last_modified', last_modified)
            __dataclass__object_setattr(self, 'priority', priority)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"audience={self.audience!r}")
            parts.append(f"last_modified={self.last_modified!r}")
            parts.append(f"priority={self.priority!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('data', 'mime_type', 'annotations', 'meta')), EqPlan(fields=('data', 'mime_type', "
        "'annotations', 'meta')), FrozenPlan(fields=('data', 'mime_type', 'annotations', 'meta'), allow_dynamic_dunder_"
        "attrs=False), HashPlan(action='add', fields=('data', 'mime_type', 'annotations', 'meta'), cache=False), InitPl"
        "an(fields=(InitPlan.Field(name='data', annotation=OpRef(name='init.fields.0.annotation'), default=None, defaul"
        "t_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_ty"
        "pe=None), InitPlan.Field(name='mime_type', annotation=OpRef(name='init.fields.1.annotation'), default=None, de"
        "fault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, chec"
        "k_type=None), InitPlan.Field(name='annotations', annotation=OpRef(name='init.fields.2.annotation'), default=Op"
        "Ref(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTA"
        "NCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fie"
        "lds.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=Fal"
        "se, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_param"
        "s=(), kw_only_params=('data', 'mime_type', 'annotations', 'meta'), frozen=True, slots=False, post_init_params="
        "None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='data', kw_only=True, fn=None), Repr"
        "Plan.Field(name='mime_type', kw_only=True, fn=None), ReprPlan.Field(name='annotations', kw_only=True, fn=None)"
        ", ReprPlan.Field(name='meta', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='2d0f8a601d454549923309fe3278e1e83fed4a0a',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'AudioContent'),
    ),
)
def _process_dataclass__2d0f8a601d454549923309fe3278e1e83fed4a0a():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
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
                data=self.data,
                mime_type=self.mime_type,
                annotations=self.annotations,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.data == other.data and
                self.mime_type == other.mime_type and
                self.annotations == other.annotations and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'data',
            'mime_type',
            'annotations',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'data',
            'mime_type',
            'annotations',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.data,
                self.mime_type,
                self.annotations,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            data: __dataclass__init__fields__0__annotation,
            mime_type: __dataclass__init__fields__1__annotation,
            annotations: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            meta: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'data', data)
            __dataclass__object_setattr(self, 'mime_type', mime_type)
            __dataclass__object_setattr(self, 'annotations', annotations)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"data={self.data!r}")
            parts.append(f"mime_type={self.mime_type!r}")
            parts.append(f"annotations={self.annotations!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('data', 'mime_type', 'type', 'annotations', 'meta')), EqPlan(fields=('data', 'mime"
        "_type', 'type', 'annotations', 'meta')), FrozenPlan(fields=('data', 'mime_type', 'type', 'annotations', 'meta'"
        "), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('data', 'mime_type', 'type', 'annotations"
        "', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='data', annotation=OpRef(name='init.fields.0.an"
        "notation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coer"
        "ce=None, validate=None, check_type=None), InitPlan.Field(name='mime_type', annotation=OpRef(name='init.fields."
        "1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, "
        "coerce=None, validate=None, check_type=None), InitPlan.Field(name='type', annotation=OpRef(name='init.fields.2"
        ".annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, f"
        "ield_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='annotations',"
        " annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_facto"
        "ry=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None"
        "), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fie"
        "lds.4.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, "
        "validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('data', 'mime_type', 'type"
        "', 'annotations', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), Rep"
        "rPlan(fields=(ReprPlan.Field(name='data', kw_only=True, fn=None), ReprPlan.Field(name='mime_type', kw_only=Tru"
        "e, fn=None), ReprPlan.Field(name='annotations', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=Tr"
        "ue, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='822c8da77516b9a3b4df3fde7a0521efc6651259',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__4__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'AudioContentBlock'),
    ),
)
def _process_dataclass__822c8da77516b9a3b4df3fde7a0521efc6651259():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
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
                data=self.data,
                mime_type=self.mime_type,
                type=self.type,
                annotations=self.annotations,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.data == other.data and
                self.mime_type == other.mime_type and
                self.type == other.type and
                self.annotations == other.annotations and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'data',
            'mime_type',
            'type',
            'annotations',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'data',
            'mime_type',
            'type',
            'annotations',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.data,
                self.mime_type,
                self.type,
                self.annotations,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            data: __dataclass__init__fields__0__annotation,
            mime_type: __dataclass__init__fields__1__annotation,
            type: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            annotations: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            meta: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'data', data)
            __dataclass__object_setattr(self, 'mime_type', mime_type)
            __dataclass__object_setattr(self, 'type', type)
            __dataclass__object_setattr(self, 'annotations', annotations)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"data={self.data!r}")
            parts.append(f"mime_type={self.mime_type!r}")
            parts.append(f"annotations={self.annotations!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('id', 'name', 'description', 'meta')), EqPlan(fields=('id', 'name', 'description',"
        " 'meta')), FrozenPlan(fields=('id', 'name', 'description', 'meta'), allow_dynamic_dunder_attrs=False), HashPla"
        "n(action='add', fields=('id', 'name', 'description', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(na"
        "me='id', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, ove"
        "rride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name="
        "'name', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, over"
        "ride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='"
        "description', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), "
        "default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, ch"
        "eck_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(n"
        "ame='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, "
        "coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('id', 'name',"
        " 'description', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprP"
        "lan(fields=(ReprPlan.Field(name='id', kw_only=True, fn=None), ReprPlan.Field(name='name', kw_only=True, fn=Non"
        "e), ReprPlan.Field(name='description', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=No"
        "ne)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='1414489816e89243ff67356feafaa816a54e8337',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'AuthMethodAgent'),
        ('ommlds.specs.acp.protocol', 'SessionMode'),
    ),
)
def _process_dataclass__1414489816e89243ff67356feafaa816a54e8337():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
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
                id=self.id,
                name=self.name,
                description=self.description,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.id == other.id and
                self.name == other.name and
                self.description == other.description and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'id',
            'name',
            'description',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'id',
            'name',
            'description',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.id,
                self.name,
                self.description,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            id: __dataclass__init__fields__0__annotation,
            name: __dataclass__init__fields__1__annotation,
            description: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            meta: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'description', description)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"id={self.id!r}")
            parts.append(f"name={self.name!r}")
            parts.append(f"description={self.description!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('method_id', 'meta')), EqPlan(fields=('method_id', 'meta')), FrozenPlan(fields=('m"
        "ethod_id', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('method_id', 'meta'), ca"
        "che=False), InitPlan(fields=(InitPlan.Field(name='method_id', annotation=OpRef(name='init.fields.0.annotation'"
        "), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, "
        "validate=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.1.annotation')"
        ", default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=Fie"
        "ldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_para"
        "ms=('method_id', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), Repr"
        "Plan(fields=(ReprPlan.Field(name='method_id', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True"
        ", fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='24a229e26003b88758af5fa80826f21143a2143f',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'AuthenticateRequest'),
    ),
)
def _process_dataclass__24a229e26003b88758af5fa80826f21143a2143f():
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
                method_id=self.method_id,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.method_id == other.method_id and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'method_id',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'method_id',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.method_id,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            method_id: __dataclass__init__fields__0__annotation,
            meta: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'method_id', method_id)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"method_id={self.method_id!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('meta',)), EqPlan(fields=('meta',)), FrozenPlan(fields=('meta',), allow_dynamic_du"
        "nder_attrs=False), HashPlan(action='add', fields=('meta',), cache=False), InitPlan(fields=(InitPlan.Field(name"
        "='meta', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'), defau"
        "lt_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_t"
        "ype=None),), self_param='self', std_params=(), kw_only_params=('meta',), frozen=True, slots=False, post_init_p"
        "arams=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='meta', kw_only=True, fn=None)"
        ",), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='8800ad55a52dc8adc704496cbd2ecf06aa7df222',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'AuthenticateResponse'),
        ('ommlds.specs.acp.protocol', 'KillTerminalResponse'),
        ('ommlds.specs.acp.protocol', 'ReleaseTerminalResponse'),
        ('ommlds.specs.acp.protocol', 'SessionListCapabilities'),
        ('ommlds.specs.acp.protocol', 'SetSessionModeResponse'),
        ('ommlds.specs.acp.protocol', 'WriteTextFileResponse'),
    ),
)
def _process_dataclass__8800ad55a52dc8adc704496cbd2ecf06aa7df222():
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
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            meta: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('description', 'name', 'input', 'meta')), EqPlan(fields=('description', 'name', 'i"
        "nput', 'meta')), FrozenPlan(fields=('description', 'name', 'input', 'meta'), allow_dynamic_dunder_attrs=False)"
        ", HashPlan(action='add', fields=('description', 'name', 'input', 'meta'), cache=False), InitPlan(fields=(InitP"
        "lan.Field(name='description', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory"
        "=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),"
        " InitPlan.Field(name='name', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory="
        "None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), "
        "InitPlan.Field(name='input', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.field"
        "s.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, va"
        "lidate=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.3.annotation'), "
        "default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=Field"
        "Type.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params"
        "=('description', 'name', 'input', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), valid"
        "ate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='description', kw_only=True, fn=None), ReprPlan.Field(name='"
        "name', kw_only=True, fn=None), ReprPlan.Field(name='input', kw_only=True, fn=None), ReprPlan.Field(name='meta'"
        ", kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='92aab022349f23491bad20d4108c174fc72959a8',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'AvailableCommand'),
    ),
)
def _process_dataclass__92aab022349f23491bad20d4108c174fc72959a8():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
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
                description=self.description,
                name=self.name,
                input=self.input,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.description == other.description and
                self.name == other.name and
                self.input == other.input and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'description',
            'name',
            'input',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'description',
            'name',
            'input',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.description,
                self.name,
                self.input,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            description: __dataclass__init__fields__0__annotation,
            name: __dataclass__init__fields__1__annotation,
            input: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            meta: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'description', description)
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'input', input)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"description={self.description!r}")
            parts.append(f"name={self.name!r}")
            parts.append(f"input={self.input!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('available_commands', 'meta')), EqPlan(fields=('available_commands', 'meta')), Fro"
        "zenPlan(fields=('available_commands', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', field"
        "s=('available_commands', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='available_commands', ann"
        "otation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False,"
        " field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='meta', anno"
        "tation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=No"
        "ne, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), s"
        "elf_param='self', std_params=(), kw_only_params=('available_commands', 'meta'), frozen=True, slots=False, post"
        "_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='available_commands', k"
        "w_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), id=False, terse=False, default_fn="
        "None)))"
    ),
    plan_repr_sha1='e864435390a33b6be864ac48e759a03da6b811f1',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'AvailableCommandsUpdate'),
    ),
)
def _process_dataclass__e864435390a33b6be864ac48e759a03da6b811f1():
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
                available_commands=self.available_commands,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.available_commands == other.available_commands and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'available_commands',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'available_commands',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.available_commands,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            available_commands: __dataclass__init__fields__0__annotation,
            meta: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'available_commands', available_commands)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"available_commands={self.available_commands!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('available_commands', 'session_update', 'meta')), EqPlan(fields=('available_comman"
        "ds', 'session_update', 'meta')), FrozenPlan(fields=('available_commands', 'session_update', 'meta'), allow_dyn"
        "amic_dunder_attrs=False), HashPlan(action='add', fields=('available_commands', 'session_update', 'meta'), cach"
        "e=False), InitPlan(fields=(InitPlan.Field(name='available_commands', annotation=OpRef(name='init.fields.0.anno"
        "tation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce"
        "=None, validate=None, check_type=None), InitPlan.Field(name='session_update', annotation=OpRef(name='init.fiel"
        "ds.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=Fals"
        "e, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='meta', an"
        "notation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory="
        "None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)),"
        " self_param='self', std_params=(), kw_only_params=('available_commands', 'session_update', 'meta'), frozen=Tru"
        "e, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='av"
        "ailable_commands', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), id=False, ters"
        "e=False, default_fn=None)))"
    ),
    plan_repr_sha1='88103cf16f7b84ac162b9a9d14b407ff492926a7',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'AvailableCommandsUpdateSessionUpdate'),
    ),
)
def _process_dataclass__88103cf16f7b84ac162b9a9d14b407ff492926a7():
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
                available_commands=self.available_commands,
                session_update=self.session_update,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.available_commands == other.available_commands and
                self.session_update == other.session_update and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'available_commands',
            'session_update',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'available_commands',
            'session_update',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.available_commands,
                self.session_update,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            available_commands: __dataclass__init__fields__0__annotation,
            session_update: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            meta: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'available_commands', available_commands)
            __dataclass__object_setattr(self, 'session_update', session_update)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"available_commands={self.available_commands!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('blob', 'uri', 'mime_type', 'meta')), EqPlan(fields=('blob', 'uri', 'mime_type', '"
        "meta')), FrozenPlan(fields=('blob', 'uri', 'mime_type', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(a"
        "ction='add', fields=('blob', 'uri', 'mime_type', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='"
        "blob', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, overr"
        "ide=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='u"
        "ri', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, overrid"
        "e=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='mim"
        "e_type', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), defau"
        "lt_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_t"
        "ype=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='"
        "init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerc"
        "e=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('blob', 'uri', 'mi"
        "me_type', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fi"
        "elds=(ReprPlan.Field(name='blob', kw_only=True, fn=None), ReprPlan.Field(name='uri', kw_only=True, fn=None), R"
        "eprPlan.Field(name='mime_type', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), i"
        "d=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='8859d4c06c52c0510c84a06b53643745e0d9e622',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'BlobResourceContents'),
    ),
)
def _process_dataclass__8859d4c06c52c0510c84a06b53643745e0d9e622():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
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
                blob=self.blob,
                uri=self.uri,
                mime_type=self.mime_type,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.blob == other.blob and
                self.uri == other.uri and
                self.mime_type == other.mime_type and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'blob',
            'uri',
            'mime_type',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'blob',
            'uri',
            'mime_type',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.blob,
                self.uri,
                self.mime_type,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            blob: __dataclass__init__fields__0__annotation,
            uri: __dataclass__init__fields__1__annotation,
            mime_type: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            meta: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'blob', blob)
            __dataclass__object_setattr(self, 'uri', uri)
            __dataclass__object_setattr(self, 'mime_type', mime_type)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"blob={self.blob!r}")
            parts.append(f"uri={self.uri!r}")
            parts.append(f"mime_type={self.mime_type!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('session_id', 'meta')), EqPlan(fields=('session_id', 'meta')), FrozenPlan(fields=("
        "'session_id', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('session_id', 'meta')"
        ", cache=False), InitPlan(fields=(InitPlan.Field(name='session_id', annotation=OpRef(name='init.fields.0.annota"
        "tion'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=N"
        "one, validate=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.1.annotat"
        "ion'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_typ"
        "e=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only"
        "_params=('session_id', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=())"
        ", ReprPlan(fields=(ReprPlan.Field(name='session_id', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_on"
        "ly=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='e1d0ca65be775287ff4194ad8d12f6ae986882d2',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'CancelNotification'),
    ),
)
def _process_dataclass__e1d0ca65be775287ff4194ad8d12f6ae986882d2():
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
                session_id=self.session_id,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.session_id == other.session_id and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'session_id',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'session_id',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.session_id,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            session_id: __dataclass__init__fields__0__annotation,
            meta: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'session_id', session_id)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"session_id={self.session_id!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('outcome',)), EqPlan(fields=('outcome',)), FrozenPlan(fields=('outcome',), allow_d"
        "ynamic_dunder_attrs=False), HashPlan(action='add', fields=('outcome',), cache=False), InitPlan(fields=(InitPla"
        "n.Field(name='outcome', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.d"
        "efault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validat"
        "e=None, check_type=None),), self_param='self', std_params=(), kw_only_params=('outcome',), frozen=True, slots="
        "False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(), id=False, terse=False, defaul"
        "t_fn=None)))"
    ),
    plan_repr_sha1='e320679251b39fb8499ce869994c99f14e4af60c',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'CancelledRequestPermissionOutcome'),
    ),
)
def _process_dataclass__e320679251b39fb8499ce869994c99f14e4af60c():
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
                outcome=self.outcome,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.outcome == other.outcome
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'outcome',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'outcome',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.outcome,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            outcome: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'outcome', outcome)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('fs', 'terminal', 'meta')), EqPlan(fields=('fs', 'terminal', 'meta')), FrozenPlan("
        "fields=('fs', 'terminal', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('fs', 'te"
        "rminal', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='fs', annotation=OpRef(name='init.fields."
        "0.annotation'), default=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, "
        "field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='terminal', a"
        "nnotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory"
        "=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),"
        " InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.field"
        "s.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, va"
        "lidate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('fs', 'terminal', 'meta'), f"
        "rozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field"
        "(name='fs', kw_only=True, fn=None), ReprPlan.Field(name='terminal', kw_only=True, fn=None), ReprPlan.Field(nam"
        "e='meta', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='e938ca2b6aa6b612212c83e983c08dfac05753ed',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'ClientCapabilities'),
    ),
)
def _process_dataclass__e938ca2b6aa6b612212c83e983c08dfac05753ed():
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
                fs=self.fs,
                terminal=self.terminal,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.fs == other.fs and
                self.terminal == other.terminal and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'fs',
            'terminal',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'fs',
            'terminal',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.fs,
                self.terminal,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            fs: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            terminal: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            meta: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'fs', fs)
            __dataclass__object_setattr(self, 'terminal', terminal)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"fs={self.fs!r}")
            parts.append(f"terminal={self.terminal!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('config_options', 'meta')), EqPlan(fields=('config_options', 'meta')), FrozenPlan("
        "fields=('config_options', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('config_o"
        "ptions', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='config_options', annotation=OpRef(name='"
        "init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldTyp"
        "e.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='i"
        "nit.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, overr"
        "ide=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', st"
        "d_params=(), kw_only_params=('config_options', 'meta'), frozen=True, slots=False, post_init_params=None, init_"
        "fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='config_options', kw_only=True, fn=None), ReprP"
        "lan.Field(name='meta', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='8404b66be6d31761c6b0433d59d6e27a485fc8d4',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'ConfigOptionUpdate'),
        ('ommlds.specs.acp.protocol', 'SetSessionConfigOptionResponse'),
    ),
)
def _process_dataclass__8404b66be6d31761c6b0433d59d6e27a485fc8d4():
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
                config_options=self.config_options,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.config_options == other.config_options and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'config_options',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'config_options',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.config_options,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            config_options: __dataclass__init__fields__0__annotation,
            meta: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'config_options', config_options)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"config_options={self.config_options!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('config_options', 'session_update', 'meta')), EqPlan(fields=('config_options', 'se"
        "ssion_update', 'meta')), FrozenPlan(fields=('config_options', 'session_update', 'meta'), allow_dynamic_dunder_"
        "attrs=False), HashPlan(action='add', fields=('config_options', 'session_update', 'meta'), cache=False), InitPl"
        "an(fields=(InitPlan.Field(name='config_options', annotation=OpRef(name='init.fields.0.annotation'), default=No"
        "ne, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None"
        ", check_type=None), InitPlan.Field(name='session_update', annotation=OpRef(name='init.fields.1.annotation'), d"
        "efault=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldT"
        "ype.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name="
        "'init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, ove"
        "rride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', "
        "std_params=(), kw_only_params=('config_options', 'session_update', 'meta'), frozen=True, slots=False, post_ini"
        "t_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='config_options', kw_only=T"
        "rue, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='b80bce18690bf47cb1d3559c234ae02ae7155872',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'ConfigOptionUpdateSessionUpdate'),
    ),
)
def _process_dataclass__b80bce18690bf47cb1d3559c234ae02ae7155872():
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
                config_options=self.config_options,
                session_update=self.session_update,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.config_options == other.config_options and
                self.session_update == other.session_update and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'config_options',
            'session_update',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'config_options',
            'session_update',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.config_options,
                self.session_update,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            config_options: __dataclass__init__fields__0__annotation,
            session_update: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            meta: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'config_options', config_options)
            __dataclass__object_setattr(self, 'session_update', session_update)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"config_options={self.config_options!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('content', 'meta')), EqPlan(fields=('content', 'meta')), FrozenPlan(fields=('conte"
        "nt', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('content', 'meta'), cache=Fals"
        "e), InitPlan(fields=(InitPlan.Field(name='content', annotation=OpRef(name='init.fields.0.annotation'), default"
        "=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=N"
        "one, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.1.annotation'), default="
        "OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INS"
        "TANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('conte"
        "nt', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields="
        "(ReprPlan.Field(name='content', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), i"
        "d=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='79b94c18ca7f2404e31d3742ceb876c627ec5e4b',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'Content'),
        ('ommlds.specs.acp.protocol', 'ContentChunk'),
        ('ommlds.specs.acp.protocol', 'ReadTextFileResponse'),
    ),
)
def _process_dataclass__79b94c18ca7f2404e31d3742ceb876c627ec5e4b():
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
                content=self.content,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.content == other.content and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'content',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'content',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.content,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            content: __dataclass__init__fields__0__annotation,
            meta: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'content', content)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"content={self.content!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('content', 'type', 'meta')), EqPlan(fields=('content', 'type', 'meta')), FrozenPla"
        "n(fields=('content', 'type', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('conte"
        "nt', 'type', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='content', annotation=OpRef(name='ini"
        "t.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.I"
        "NSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='type', annotation=OpRef(name='init"
        ".fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override"
        "=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='meta"
        "', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_fac"
        "tory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=No"
        "ne)), self_param='self', std_params=(), kw_only_params=('content', 'type', 'meta'), frozen=True, slots=False, "
        "post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='content', kw_only="
        "True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='2355dcaa7955d3b3d1deb153ad0366245a82c126',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'ContentToolCallContent'),
    ),
)
def _process_dataclass__2355dcaa7955d3b3d1deb153ad0366245a82c126():
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
                content=self.content,
                type=self.type,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.content == other.content and
                self.type == other.type and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'content',
            'type',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'content',
            'type',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.content,
                self.type,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            content: __dataclass__init__fields__0__annotation,
            type: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            meta: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'content', content)
            __dataclass__object_setattr(self, 'type', type)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"content={self.content!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('command', 'session_id', 'args', 'cwd', 'env', 'output_byte_limit', 'meta')), EqPl"
        "an(fields=('command', 'session_id', 'args', 'cwd', 'env', 'output_byte_limit', 'meta')), FrozenPlan(fields=('c"
        "ommand', 'session_id', 'args', 'cwd', 'env', 'output_byte_limit', 'meta'), allow_dynamic_dunder_attrs=False), "
        "HashPlan(action='add', fields=('command', 'session_id', 'args', 'cwd', 'env', 'output_byte_limit', 'meta'), ca"
        "che=False), InitPlan(fields=(InitPlan.Field(name='command', annotation=OpRef(name='init.fields.0.annotation'),"
        " default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, va"
        "lidate=None, check_type=None), InitPlan.Field(name='session_id', annotation=OpRef(name='init.fields.1.annotati"
        "on'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=Non"
        "e, validate=None, check_type=None), InitPlan.Field(name='args', annotation=OpRef(name='init.fields.2.annotatio"
        "n'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_type="
        "FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='cwd', annotation=OpRef("
        "name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True"
        ", override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field("
        "name='env', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), de"
        "fault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, chec"
        "k_type=None), InitPlan.Field(name='output_byte_limit', annotation=OpRef(name='init.fields.5.annotation'), defa"
        "ult=OpRef(name='init.fields.5.default'), default_factory=None, init=True, override=False, field_type=FieldType"
        ".INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='in"
        "it.fields.6.annotation'), default=OpRef(name='init.fields.6.default'), default_factory=None, init=True, overri"
        "de=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std"
        "_params=(), kw_only_params=('command', 'session_id', 'args', 'cwd', 'env', 'output_byte_limit', 'meta'), froze"
        "n=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(nam"
        "e='command', kw_only=True, fn=None), ReprPlan.Field(name='session_id', kw_only=True, fn=None), ReprPlan.Field("
        "name='args', kw_only=True, fn=None), ReprPlan.Field(name='cwd', kw_only=True, fn=None), ReprPlan.Field(name='e"
        "nv', kw_only=True, fn=None), ReprPlan.Field(name='output_byte_limit', kw_only=True, fn=None), ReprPlan.Field(n"
        "ame='meta', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='8c7c249376b2905044ad4537f593875f014ddd47',
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
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'CreateTerminalRequest'),
    ),
)
def _process_dataclass__8c7c249376b2905044ad4537f593875f014ddd47():
    def _process_dataclass(
        *,
        __class__,
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
                command=self.command,
                session_id=self.session_id,
                args=self.args,
                cwd=self.cwd,
                env=self.env,
                output_byte_limit=self.output_byte_limit,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.command == other.command and
                self.session_id == other.session_id and
                self.args == other.args and
                self.cwd == other.cwd and
                self.env == other.env and
                self.output_byte_limit == other.output_byte_limit and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'command',
            'session_id',
            'args',
            'cwd',
            'env',
            'output_byte_limit',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'command',
            'session_id',
            'args',
            'cwd',
            'env',
            'output_byte_limit',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.command,
                self.session_id,
                self.args,
                self.cwd,
                self.env,
                self.output_byte_limit,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            command: __dataclass__init__fields__0__annotation,
            session_id: __dataclass__init__fields__1__annotation,
            args: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            cwd: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            env: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            output_byte_limit: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
            meta: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'command', command)
            __dataclass__object_setattr(self, 'session_id', session_id)
            __dataclass__object_setattr(self, 'args', args)
            __dataclass__object_setattr(self, 'cwd', cwd)
            __dataclass__object_setattr(self, 'env', env)
            __dataclass__object_setattr(self, 'output_byte_limit', output_byte_limit)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"command={self.command!r}")
            parts.append(f"session_id={self.session_id!r}")
            parts.append(f"args={self.args!r}")
            parts.append(f"cwd={self.cwd!r}")
            parts.append(f"env={self.env!r}")
            parts.append(f"output_byte_limit={self.output_byte_limit!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('terminal_id', 'meta')), EqPlan(fields=('terminal_id', 'meta')), FrozenPlan(fields"
        "=('terminal_id', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('terminal_id', 'me"
        "ta'), cache=False), InitPlan(fields=(InitPlan.Field(name='terminal_id', annotation=OpRef(name='init.fields.0.a"
        "nnotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coe"
        "rce=None, validate=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.1.an"
        "notation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, fiel"
        "d_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw"
        "_only_params=('terminal_id', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_f"
        "ns=()), ReprPlan(fields=(ReprPlan.Field(name='terminal_id', kw_only=True, fn=None), ReprPlan.Field(name='meta'"
        ", kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='567b6432536369af19c30400c5be327950a1dec9',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'CreateTerminalResponse'),
        ('ommlds.specs.acp.protocol', 'Terminal'),
    ),
)
def _process_dataclass__567b6432536369af19c30400c5be327950a1dec9():
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
                terminal_id=self.terminal_id,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.terminal_id == other.terminal_id and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'terminal_id',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'terminal_id',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.terminal_id,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            terminal_id: __dataclass__init__fields__0__annotation,
            meta: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'terminal_id', terminal_id)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"terminal_id={self.terminal_id!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('current_mode_id', 'meta')), EqPlan(fields=('current_mode_id', 'meta')), FrozenPla"
        "n(fields=('current_mode_id', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('curre"
        "nt_mode_id', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='current_mode_id', annotation=OpRef(n"
        "ame='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=Fie"
        "ldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(na"
        "me='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, "
        "override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self"
        "', std_params=(), kw_only_params=('current_mode_id', 'meta'), frozen=True, slots=False, post_init_params=None,"
        " init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='current_mode_id', kw_only=True, fn=None)"
        ", ReprPlan.Field(name='meta', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='06a2e412dd36eabcb107e2ed09ac258b435044df',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'CurrentModeUpdate'),
    ),
)
def _process_dataclass__06a2e412dd36eabcb107e2ed09ac258b435044df():
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
                current_mode_id=self.current_mode_id,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.current_mode_id == other.current_mode_id and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'current_mode_id',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'current_mode_id',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.current_mode_id,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            current_mode_id: __dataclass__init__fields__0__annotation,
            meta: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'current_mode_id', current_mode_id)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"current_mode_id={self.current_mode_id!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('current_mode_id', 'session_update', 'meta')), EqPlan(fields=('current_mode_id', '"
        "session_update', 'meta')), FrozenPlan(fields=('current_mode_id', 'session_update', 'meta'), allow_dynamic_dund"
        "er_attrs=False), HashPlan(action='add', fields=('current_mode_id', 'session_update', 'meta'), cache=False), In"
        "itPlan(fields=(InitPlan.Field(name='current_mode_id', annotation=OpRef(name='init.fields.0.annotation'), defau"
        "lt=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate"
        "=None, check_type=None), InitPlan.Field(name='session_update', annotation=OpRef(name='init.fields.1.annotation"
        "'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=F"
        "ieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef("
        "name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True"
        ", override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='se"
        "lf', std_params=(), kw_only_params=('current_mode_id', 'session_update', 'meta'), frozen=True, slots=False, po"
        "st_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='current_mode_id', kw"
        "_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), id=False, terse=False, default_fn=N"
        "one)))"
    ),
    plan_repr_sha1='48e2d9ad56aef2be992716e7234686f4803512c6',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'CurrentModeUpdateSessionUpdate'),
    ),
)
def _process_dataclass__48e2d9ad56aef2be992716e7234686f4803512c6():
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
                current_mode_id=self.current_mode_id,
                session_update=self.session_update,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.current_mode_id == other.current_mode_id and
                self.session_update == other.session_update and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'current_mode_id',
            'session_update',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'current_mode_id',
            'session_update',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.current_mode_id,
                self.session_update,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            current_mode_id: __dataclass__init__fields__0__annotation,
            session_update: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            meta: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'current_mode_id', current_mode_id)
            __dataclass__object_setattr(self, 'session_update', session_update)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"current_mode_id={self.current_mode_id!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('new_text', 'path', 'old_text', 'meta')), EqPlan(fields=('new_text', 'path', 'old_"
        "text', 'meta')), FrozenPlan(fields=('new_text', 'path', 'old_text', 'meta'), allow_dynamic_dunder_attrs=False)"
        ", HashPlan(action='add', fields=('new_text', 'path', 'old_text', 'meta'), cache=False), InitPlan(fields=(InitP"
        "lan.Field(name='new_text', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=No"
        "ne, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), In"
        "itPlan.Field(name='path', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=Non"
        "e, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), Ini"
        "tPlan.Field(name='old_text', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.field"
        "s.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, va"
        "lidate=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.3.annotation'), "
        "default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=Field"
        "Type.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params"
        "=('new_text', 'path', 'old_text', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), valid"
        "ate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='new_text', kw_only=True, fn=None), ReprPlan.Field(name='pat"
        "h', kw_only=True, fn=None), ReprPlan.Field(name='old_text', kw_only=True, fn=None), ReprPlan.Field(name='meta'"
        ", kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='349560dd1e95253b98e0dfc9af0e58167a113cee',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'Diff'),
    ),
)
def _process_dataclass__349560dd1e95253b98e0dfc9af0e58167a113cee():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
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
                new_text=self.new_text,
                path=self.path,
                old_text=self.old_text,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.new_text == other.new_text and
                self.path == other.path and
                self.old_text == other.old_text and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'new_text',
            'path',
            'old_text',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'new_text',
            'path',
            'old_text',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.new_text,
                self.path,
                self.old_text,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            new_text: __dataclass__init__fields__0__annotation,
            path: __dataclass__init__fields__1__annotation,
            old_text: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            meta: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'new_text', new_text)
            __dataclass__object_setattr(self, 'path', path)
            __dataclass__object_setattr(self, 'old_text', old_text)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"new_text={self.new_text!r}")
            parts.append(f"path={self.path!r}")
            parts.append(f"old_text={self.old_text!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('new_text', 'path', 'type', 'old_text', 'meta')), EqPlan(fields=('new_text', 'path"
        "', 'type', 'old_text', 'meta')), FrozenPlan(fields=('new_text', 'path', 'type', 'old_text', 'meta'), allow_dyn"
        "amic_dunder_attrs=False), HashPlan(action='add', fields=('new_text', 'path', 'type', 'old_text', 'meta'), cach"
        "e=False), InitPlan(fields=(InitPlan.Field(name='new_text', annotation=OpRef(name='init.fields.0.annotation'), "
        "default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, val"
        "idate=None, check_type=None), InitPlan.Field(name='path', annotation=OpRef(name='init.fields.1.annotation'), d"
        "efault=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, vali"
        "date=None, check_type=None), InitPlan.Field(name='type', annotation=OpRef(name='init.fields.2.annotation'), de"
        "fault=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldTy"
        "pe.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='old_text', annotation=OpRef(na"
        "me='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, "
        "override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(na"
        "me='meta', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), def"
        "ault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check"
        "_type=None)), self_param='self', std_params=(), kw_only_params=('new_text', 'path', 'type', 'old_text', 'meta'"
        "), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.F"
        "ield(name='new_text', kw_only=True, fn=None), ReprPlan.Field(name='path', kw_only=True, fn=None), ReprPlan.Fie"
        "ld(name='old_text', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), id=False, ter"
        "se=False, default_fn=None)))"
    ),
    plan_repr_sha1='ef2ed0d1a12e61a7fb6550924cdbb966ec8f32ba',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__4__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'DiffToolCallContent'),
    ),
)
def _process_dataclass__ef2ed0d1a12e61a7fb6550924cdbb966ec8f32ba():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
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
                new_text=self.new_text,
                path=self.path,
                type=self.type,
                old_text=self.old_text,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.new_text == other.new_text and
                self.path == other.path and
                self.type == other.type and
                self.old_text == other.old_text and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'new_text',
            'path',
            'type',
            'old_text',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'new_text',
            'path',
            'type',
            'old_text',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.new_text,
                self.path,
                self.type,
                self.old_text,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            new_text: __dataclass__init__fields__0__annotation,
            path: __dataclass__init__fields__1__annotation,
            type: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            old_text: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            meta: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'new_text', new_text)
            __dataclass__object_setattr(self, 'path', path)
            __dataclass__object_setattr(self, 'type', type)
            __dataclass__object_setattr(self, 'old_text', old_text)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"new_text={self.new_text!r}")
            parts.append(f"path={self.path!r}")
            parts.append(f"old_text={self.old_text!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('resource', 'annotations', 'meta')), EqPlan(fields=('resource', 'annotations', 'me"
        "ta')), FrozenPlan(fields=('resource', 'annotations', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(acti"
        "on='add', fields=('resource', 'annotations', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='reso"
        "urce', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, overr"
        "ide=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='a"
        "nnotations', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), d"
        "efault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, che"
        "ck_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(na"
        "me='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, c"
        "oerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('resource', 'a"
        "nnotations', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan"
        "(fields=(ReprPlan.Field(name='resource', kw_only=True, fn=None), ReprPlan.Field(name='annotations', kw_only=Tr"
        "ue, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='872f10c4a51bb5bca05ed3c6ab7e32621515354a',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'EmbeddedResource'),
    ),
)
def _process_dataclass__872f10c4a51bb5bca05ed3c6ab7e32621515354a():
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
                resource=self.resource,
                annotations=self.annotations,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.resource == other.resource and
                self.annotations == other.annotations and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'resource',
            'annotations',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'resource',
            'annotations',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.resource,
                self.annotations,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            resource: __dataclass__init__fields__0__annotation,
            annotations: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            meta: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'resource', resource)
            __dataclass__object_setattr(self, 'annotations', annotations)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"resource={self.resource!r}")
            parts.append(f"annotations={self.annotations!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('name', 'value', 'meta')), EqPlan(fields=('name', 'value', 'meta')), FrozenPlan(fi"
        "elds=('name', 'value', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('name', 'val"
        "ue', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='name', annotation=OpRef(name='init.fields.0."
        "annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, co"
        "erce=None, validate=None, check_type=None), InitPlan.Field(name='value', annotation=OpRef(name='init.fields.1."
        "annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, co"
        "erce=None, validate=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.2.a"
        "nnotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, fie"
        "ld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), k"
        "w_only_params=('name', 'value', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validat"
        "e_fns=()), ReprPlan(fields=(ReprPlan.Field(name='name', kw_only=True, fn=None), ReprPlan.Field(name='value', k"
        "w_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), id=False, terse=False, default_fn="
        "None)))"
    ),
    plan_repr_sha1='a74dbccc1be43eb892bbbd8622320859755b7d11',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'EnvVariable'),
        ('ommlds.specs.acp.protocol', 'HttpHeader'),
    ),
)
def _process_dataclass__a74dbccc1be43eb892bbbd8622320859755b7d11():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
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
                name=self.name,
                value=self.value,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.name == other.name and
                self.value == other.value and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'name',
            'value',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'name',
            'value',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.name,
                self.value,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            name: __dataclass__init__fields__0__annotation,
            value: __dataclass__init__fields__1__annotation,
            meta: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'value', value)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"name={self.name!r}")
            parts.append(f"value={self.value!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('code', 'message', 'data')), EqPlan(fields=('code', 'message', 'data')), FrozenPla"
        "n(fields=('code', 'message', 'data'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('code'"
        ", 'message', 'data'), cache=False), InitPlan(fields=(InitPlan.Field(name='code', annotation=OpRef(name='init.f"
        "ields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INST"
        "ANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='message', annotation=OpRef(name='init"
        ".fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.IN"
        "STANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='data', annotation=OpRef(name='init."
        "fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override="
        "False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_pa"
        "rams=(), kw_only_params=('code', 'message', 'data'), frozen=True, slots=False, post_init_params=None, init_fns"
        "=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='code', kw_only=True, fn=None), ReprPlan.Field(nam"
        "e='message', kw_only=True, fn=None), ReprPlan.Field(name='data', kw_only=True, fn=None)), id=False, terse=Fals"
        "e, default_fn=None)))"
    ),
    plan_repr_sha1='3f2d37275ba736bdbacfbc4100b49a39d31fe9b3',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'Error'),
    ),
)
def _process_dataclass__3f2d37275ba736bdbacfbc4100b49a39d31fe9b3():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
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
                code=self.code,
                message=self.message,
                data=self.data,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.code == other.code and
                self.message == other.message and
                self.data == other.data
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'code',
            'message',
            'data',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'code',
            'message',
            'data',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.code,
                self.message,
                self.data,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            code: __dataclass__init__fields__0__annotation,
            message: __dataclass__init__fields__1__annotation,
            data: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'code', code)
            __dataclass__object_setattr(self, 'message', message)
            __dataclass__object_setattr(self, 'data', data)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"code={self.code!r}")
            parts.append(f"message={self.message!r}")
            parts.append(f"data={self.data!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

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
        ('ommlds.specs.acp.protocol', 'ExtNotification'),
        ('ommlds.specs.acp.protocol', 'ExtRequest'),
        ('ommlds.specs.acp.protocol', 'ExtResponse'),
    ),
)
def _process_dataclass__e1f7edfe11f2b721d6a656c46e698fedc95461bb():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__FrozenInstanceError=dataclasses.FrozenInstanceError,  # noqa
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

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        def __delattr__(self, name):
            if (
                type(self) is __class__
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash(())

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
        ) -> __dataclass__None:
            pass

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('read_text_file', 'write_text_file', 'meta')), EqPlan(fields=('read_text_file', 'w"
        "rite_text_file', 'meta')), FrozenPlan(fields=('read_text_file', 'write_text_file', 'meta'), allow_dynamic_dund"
        "er_attrs=False), HashPlan(action='add', fields=('read_text_file', 'write_text_file', 'meta'), cache=False), In"
        "itPlan(fields=(InitPlan.Field(name='read_text_file', annotation=OpRef(name='init.fields.0.annotation'), defaul"
        "t=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.I"
        "NSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='write_text_file', annotation=OpRef"
        "(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=Tru"
        "e, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field"
        "(name='meta', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), "
        "default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, ch"
        "eck_type=None)), self_param='self', std_params=(), kw_only_params=('read_text_file', 'write_text_file', 'meta'"
        "), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.F"
        "ield(name='read_text_file', kw_only=True, fn=None), ReprPlan.Field(name='write_text_file', kw_only=True, fn=No"
        "ne), ReprPlan.Field(name='meta', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='c8cc0fcc4fa8b0b00adfddd7f75df9270457a2b4',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'FileSystemCapabilities'),
    ),
)
def _process_dataclass__c8cc0fcc4fa8b0b00adfddd7f75df9270457a2b4():
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
                read_text_file=self.read_text_file,
                write_text_file=self.write_text_file,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.read_text_file == other.read_text_file and
                self.write_text_file == other.write_text_file and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'read_text_file',
            'write_text_file',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'read_text_file',
            'write_text_file',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.read_text_file,
                self.write_text_file,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            read_text_file: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            write_text_file: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            meta: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'read_text_file', read_text_file)
            __dataclass__object_setattr(self, 'write_text_file', write_text_file)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"read_text_file={self.read_text_file!r}")
            parts.append(f"write_text_file={self.write_text_file!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('headers', 'name', 'url', 'type', 'meta')), EqPlan(fields=('headers', 'name', 'url"
        "', 'type', 'meta')), FrozenPlan(fields=('headers', 'name', 'url', 'type', 'meta'), allow_dynamic_dunder_attrs="
        "False), HashPlan(action='add', fields=('headers', 'name', 'url', 'type', 'meta'), cache=False), InitPlan(field"
        "s=(InitPlan.Field(name='headers', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_fac"
        "tory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=No"
        "ne), InitPlan.Field(name='name', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_fact"
        "ory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=Non"
        "e), InitPlan.Field(name='url', annotation=OpRef(name='init.fields.2.annotation'), default=None, default_factor"
        "y=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)"
        ", InitPlan.Field(name='type', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fiel"
        "ds.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, v"
        "alidate=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.4.annotation'),"
        " default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, override=False, field_type=Fiel"
        "dType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_param"
        "s=('headers', 'name', 'url', 'type', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), va"
        "lidate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='headers', kw_only=True, fn=None), ReprPlan.Field(name='n"
        "ame', kw_only=True, fn=None), ReprPlan.Field(name='url', kw_only=True, fn=None), ReprPlan.Field(name='meta', k"
        "w_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='2bf17f7b8c58828e706a59ed9f8f3af6f388ed75',
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
        ('ommlds.specs.acp.protocol', 'HttpMcpServer'),
        ('ommlds.specs.acp.protocol', 'SseMcpServer'),
    ),
)
def _process_dataclass__2bf17f7b8c58828e706a59ed9f8f3af6f388ed75():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
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
                headers=self.headers,
                name=self.name,
                url=self.url,
                type=self.type,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.headers == other.headers and
                self.name == other.name and
                self.url == other.url and
                self.type == other.type and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'headers',
            'name',
            'url',
            'type',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'headers',
            'name',
            'url',
            'type',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.headers,
                self.name,
                self.url,
                self.type,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            headers: __dataclass__init__fields__0__annotation,
            name: __dataclass__init__fields__1__annotation,
            url: __dataclass__init__fields__2__annotation,
            type: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            meta: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'headers', headers)
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'url', url)
            __dataclass__object_setattr(self, 'type', type)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"headers={self.headers!r}")
            parts.append(f"name={self.name!r}")
            parts.append(f"url={self.url!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('data', 'mime_type', 'annotations', 'uri', 'meta')), EqPlan(fields=('data', 'mime_"
        "type', 'annotations', 'uri', 'meta')), FrozenPlan(fields=('data', 'mime_type', 'annotations', 'uri', 'meta'), "
        "allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('data', 'mime_type', 'annotations', 'uri', '"
        "meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='data', annotation=OpRef(name='init.fields.0.annota"
        "tion'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=N"
        "one, validate=None, check_type=None), InitPlan.Field(name='mime_type', annotation=OpRef(name='init.fields.1.an"
        "notation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coer"
        "ce=None, validate=None, check_type=None), InitPlan.Field(name='annotations', annotation=OpRef(name='init.field"
        "s.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False"
        ", field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='uri', anno"
        "tation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=No"
        "ne, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), In"
        "itPlan.Field(name='meta', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4"
        ".default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valid"
        "ate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('data', 'mime_type', 'annotatio"
        "ns', 'uri', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan("
        "fields=(ReprPlan.Field(name='data', kw_only=True, fn=None), ReprPlan.Field(name='mime_type', kw_only=True, fn="
        "None), ReprPlan.Field(name='annotations', kw_only=True, fn=None), ReprPlan.Field(name='uri', kw_only=True, fn="
        "None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='2d9a17457f1b154807e92294727394e0c017d42b',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__4__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'ImageContent'),
    ),
)
def _process_dataclass__2d9a17457f1b154807e92294727394e0c017d42b():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
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
                data=self.data,
                mime_type=self.mime_type,
                annotations=self.annotations,
                uri=self.uri,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.data == other.data and
                self.mime_type == other.mime_type and
                self.annotations == other.annotations and
                self.uri == other.uri and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'data',
            'mime_type',
            'annotations',
            'uri',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'data',
            'mime_type',
            'annotations',
            'uri',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.data,
                self.mime_type,
                self.annotations,
                self.uri,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            data: __dataclass__init__fields__0__annotation,
            mime_type: __dataclass__init__fields__1__annotation,
            annotations: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            uri: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            meta: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'data', data)
            __dataclass__object_setattr(self, 'mime_type', mime_type)
            __dataclass__object_setattr(self, 'annotations', annotations)
            __dataclass__object_setattr(self, 'uri', uri)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"data={self.data!r}")
            parts.append(f"mime_type={self.mime_type!r}")
            parts.append(f"annotations={self.annotations!r}")
            parts.append(f"uri={self.uri!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('data', 'mime_type', 'type', 'annotations', 'uri', 'meta')), EqPlan(fields=('data'"
        ", 'mime_type', 'type', 'annotations', 'uri', 'meta')), FrozenPlan(fields=('data', 'mime_type', 'type', 'annota"
        "tions', 'uri', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('data', 'mime_type',"
        " 'type', 'annotations', 'uri', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='data', annotation="
        "OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_t"
        "ype=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='mime_type', annotat"
        "ion=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, fie"
        "ld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='type', annotati"
        "on=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, "
        "init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPl"
        "an.Field(name='annotations', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.field"
        "s.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, va"
        "lidate=None, check_type=None), InitPlan.Field(name='uri', annotation=OpRef(name='init.fields.4.annotation'), d"
        "efault=OpRef(name='init.fields.4.default'), default_factory=None, init=True, override=False, field_type=FieldT"
        "ype.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name="
        "'init.fields.5.annotation'), default=OpRef(name='init.fields.5.default'), default_factory=None, init=True, ove"
        "rride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', "
        "std_params=(), kw_only_params=('data', 'mime_type', 'type', 'annotations', 'uri', 'meta'), frozen=True, slots="
        "False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='data', kw_o"
        "nly=True, fn=None), ReprPlan.Field(name='mime_type', kw_only=True, fn=None), ReprPlan.Field(name='annotations'"
        ", kw_only=True, fn=None), ReprPlan.Field(name='uri', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_on"
        "ly=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='c25de1d54caa79509e798c4c00d49a754cd9c531',
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
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'ImageContentBlock'),
    ),
)
def _process_dataclass__c25de1d54caa79509e798c4c00d49a754cd9c531():
    def _process_dataclass(
        *,
        __class__,
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
                data=self.data,
                mime_type=self.mime_type,
                type=self.type,
                annotations=self.annotations,
                uri=self.uri,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.data == other.data and
                self.mime_type == other.mime_type and
                self.type == other.type and
                self.annotations == other.annotations and
                self.uri == other.uri and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'data',
            'mime_type',
            'type',
            'annotations',
            'uri',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'data',
            'mime_type',
            'type',
            'annotations',
            'uri',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.data,
                self.mime_type,
                self.type,
                self.annotations,
                self.uri,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            data: __dataclass__init__fields__0__annotation,
            mime_type: __dataclass__init__fields__1__annotation,
            type: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            annotations: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            uri: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            meta: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'data', data)
            __dataclass__object_setattr(self, 'mime_type', mime_type)
            __dataclass__object_setattr(self, 'type', type)
            __dataclass__object_setattr(self, 'annotations', annotations)
            __dataclass__object_setattr(self, 'uri', uri)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"data={self.data!r}")
            parts.append(f"mime_type={self.mime_type!r}")
            parts.append(f"annotations={self.annotations!r}")
            parts.append(f"uri={self.uri!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('name', 'version', 'title', 'meta')), EqPlan(fields=('name', 'version', 'title', '"
        "meta')), FrozenPlan(fields=('name', 'version', 'title', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(a"
        "ction='add', fields=('name', 'version', 'title', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='"
        "name', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, overr"
        "ide=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='v"
        "ersion', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, ove"
        "rride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name="
        "'title', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), defau"
        "lt_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_t"
        "ype=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='"
        "init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerc"
        "e=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('name', 'version',"
        " 'title', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fi"
        "elds=(ReprPlan.Field(name='name', kw_only=True, fn=None), ReprPlan.Field(name='version', kw_only=True, fn=None"
        "), ReprPlan.Field(name='title', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), i"
        "d=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='01285feeb3bd2694a4550302da4b2b0055b6f9fc',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'Implementation'),
    ),
)
def _process_dataclass__01285feeb3bd2694a4550302da4b2b0055b6f9fc():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
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
                name=self.name,
                version=self.version,
                title=self.title,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.name == other.name and
                self.version == other.version and
                self.title == other.title and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'name',
            'version',
            'title',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'name',
            'version',
            'title',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.name,
                self.version,
                self.title,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            name: __dataclass__init__fields__0__annotation,
            version: __dataclass__init__fields__1__annotation,
            title: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            meta: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'version', version)
            __dataclass__object_setattr(self, 'title', title)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"name={self.name!r}")
            parts.append(f"version={self.version!r}")
            parts.append(f"title={self.title!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('protocol_version', 'client_capabilities', 'client_info', 'meta')), EqPlan(fields="
        "('protocol_version', 'client_capabilities', 'client_info', 'meta')), FrozenPlan(fields=('protocol_version', 'c"
        "lient_capabilities', 'client_info', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields="
        "('protocol_version', 'client_capabilities', 'client_info', 'meta'), cache=False), InitPlan(fields=(InitPlan.Fi"
        "eld(name='protocol_version', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory="
        "None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), "
        "InitPlan.Field(name='client_capabilities', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(na"
        "me='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, c"
        "oerce=None, validate=None, check_type=None), InitPlan.Field(name='client_info', annotation=OpRef(name='init.fi"
        "elds.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=Fa"
        "lse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='meta', "
        "annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factor"
        "y=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)"
        "), self_param='self', std_params=(), kw_only_params=('protocol_version', 'client_capabilities', 'client_info',"
        " 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(Rep"
        "rPlan.Field(name='protocol_version', kw_only=True, fn=None), ReprPlan.Field(name='client_capabilities', kw_onl"
        "y=True, fn=None), ReprPlan.Field(name='client_info', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_on"
        "ly=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='6ee9945416c82a81b48f8738be72161d3c21e29e',
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
        ('ommlds.specs.acp.protocol', 'InitializeRequest'),
    ),
)
def _process_dataclass__6ee9945416c82a81b48f8738be72161d3c21e29e():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
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
                protocol_version=self.protocol_version,
                client_capabilities=self.client_capabilities,
                client_info=self.client_info,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.protocol_version == other.protocol_version and
                self.client_capabilities == other.client_capabilities and
                self.client_info == other.client_info and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'protocol_version',
            'client_capabilities',
            'client_info',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'protocol_version',
            'client_capabilities',
            'client_info',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.protocol_version,
                self.client_capabilities,
                self.client_info,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            protocol_version: __dataclass__init__fields__0__annotation,
            client_capabilities: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            client_info: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            meta: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'protocol_version', protocol_version)
            __dataclass__object_setattr(self, 'client_capabilities', client_capabilities)
            __dataclass__object_setattr(self, 'client_info', client_info)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"protocol_version={self.protocol_version!r}")
            parts.append(f"client_capabilities={self.client_capabilities!r}")
            parts.append(f"client_info={self.client_info!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('protocol_version', 'agent_capabilities', 'agent_info', 'auth_methods', 'meta')), "
        "EqPlan(fields=('protocol_version', 'agent_capabilities', 'agent_info', 'auth_methods', 'meta')), FrozenPlan(fi"
        "elds=('protocol_version', 'agent_capabilities', 'agent_info', 'auth_methods', 'meta'), allow_dynamic_dunder_at"
        "trs=False), HashPlan(action='add', fields=('protocol_version', 'agent_capabilities', 'agent_info', 'auth_metho"
        "ds', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='protocol_version', annotation=OpRef(name='in"
        "it.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType."
        "INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='agent_capabilities', annotation=O"
        "pRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init"
        "=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.F"
        "ield(name='agent_info', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.d"
        "efault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validat"
        "e=None, check_type=None), InitPlan.Field(name='auth_methods', annotation=OpRef(name='init.fields.3.annotation'"
        "), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=Fi"
        "eldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(n"
        "ame='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True,"
        " override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='sel"
        "f', std_params=(), kw_only_params=('protocol_version', 'agent_capabilities', 'agent_info', 'auth_methods', 'me"
        "ta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPla"
        "n.Field(name='protocol_version', kw_only=True, fn=None), ReprPlan.Field(name='agent_capabilities', kw_only=Tru"
        "e, fn=None), ReprPlan.Field(name='agent_info', kw_only=True, fn=None), ReprPlan.Field(name='auth_methods', kw_"
        "only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), id=False, terse=False, default_fn=No"
        "ne)))"
    ),
    plan_repr_sha1='6a0e639b0203dfb168859dcafc619fae76a787a4',
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
        ('ommlds.specs.acp.protocol', 'InitializeResponse'),
    ),
)
def _process_dataclass__6a0e639b0203dfb168859dcafc619fae76a787a4():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
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
                protocol_version=self.protocol_version,
                agent_capabilities=self.agent_capabilities,
                agent_info=self.agent_info,
                auth_methods=self.auth_methods,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.protocol_version == other.protocol_version and
                self.agent_capabilities == other.agent_capabilities and
                self.agent_info == other.agent_info and
                self.auth_methods == other.auth_methods and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'protocol_version',
            'agent_capabilities',
            'agent_info',
            'auth_methods',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'protocol_version',
            'agent_capabilities',
            'agent_info',
            'auth_methods',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.protocol_version,
                self.agent_capabilities,
                self.agent_info,
                self.auth_methods,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            protocol_version: __dataclass__init__fields__0__annotation,
            agent_capabilities: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            agent_info: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            auth_methods: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            meta: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'protocol_version', protocol_version)
            __dataclass__object_setattr(self, 'agent_capabilities', agent_capabilities)
            __dataclass__object_setattr(self, 'agent_info', agent_info)
            __dataclass__object_setattr(self, 'auth_methods', auth_methods)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"protocol_version={self.protocol_version!r}")
            parts.append(f"agent_capabilities={self.agent_capabilities!r}")
            parts.append(f"agent_info={self.agent_info!r}")
            parts.append(f"auth_methods={self.auth_methods!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('session_id', 'terminal_id', 'meta')), EqPlan(fields=('session_id', 'terminal_id',"
        " 'meta')), FrozenPlan(fields=('session_id', 'terminal_id', 'meta'), allow_dynamic_dunder_attrs=False), HashPla"
        "n(action='add', fields=('session_id', 'terminal_id', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(na"
        "me='session_id', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=T"
        "rue, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fie"
        "ld(name='terminal_id', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, "
        "init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPl"
        "an.Field(name='meta', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.def"
        "ault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate="
        "None, check_type=None)), self_param='self', std_params=(), kw_only_params=('session_id', 'terminal_id', 'meta'"
        "), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.F"
        "ield(name='session_id', kw_only=True, fn=None), ReprPlan.Field(name='terminal_id', kw_only=True, fn=None), Rep"
        "rPlan.Field(name='meta', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='6150b41b7dabd6e85ddc10546e8878919c4970fc',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'KillTerminalRequest'),
        ('ommlds.specs.acp.protocol', 'ReleaseTerminalRequest'),
        ('ommlds.specs.acp.protocol', 'TerminalOutputRequest'),
        ('ommlds.specs.acp.protocol', 'WaitForTerminalExitRequest'),
    ),
)
def _process_dataclass__6150b41b7dabd6e85ddc10546e8878919c4970fc():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
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
                session_id=self.session_id,
                terminal_id=self.terminal_id,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.session_id == other.session_id and
                self.terminal_id == other.terminal_id and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'session_id',
            'terminal_id',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'session_id',
            'terminal_id',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.session_id,
                self.terminal_id,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            session_id: __dataclass__init__fields__0__annotation,
            terminal_id: __dataclass__init__fields__1__annotation,
            meta: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'session_id', session_id)
            __dataclass__object_setattr(self, 'terminal_id', terminal_id)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"session_id={self.session_id!r}")
            parts.append(f"terminal_id={self.terminal_id!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('cursor', 'cwd', 'meta')), EqPlan(fields=('cursor', 'cwd', 'meta')), FrozenPlan(fi"
        "elds=('cursor', 'cwd', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('cursor', 'c"
        "wd', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='cursor', annotation=OpRef(name='init.fields."
        "0.annotation'), default=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, "
        "field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='cwd', annota"
        "tion=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None"
        ", init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), Init"
        "Plan.Field(name='meta', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.d"
        "efault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validat"
        "e=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('cursor', 'cwd', 'meta'), frozen="
        "True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name="
        "'cursor', kw_only=True, fn=None), ReprPlan.Field(name='cwd', kw_only=True, fn=None), ReprPlan.Field(name='meta"
        "', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='ead46e4bf3f341f8d289f7277b383878448e6ed5',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'ListSessionsRequest'),
    ),
)
def _process_dataclass__ead46e4bf3f341f8d289f7277b383878448e6ed5():
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
                cursor=self.cursor,
                cwd=self.cwd,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.cursor == other.cursor and
                self.cwd == other.cwd and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'cursor',
            'cwd',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'cursor',
            'cwd',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.cursor,
                self.cwd,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            cursor: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            cwd: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            meta: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'cursor', cursor)
            __dataclass__object_setattr(self, 'cwd', cwd)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"cursor={self.cursor!r}")
            parts.append(f"cwd={self.cwd!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('sessions', 'next_cursor', 'meta')), EqPlan(fields=('sessions', 'next_cursor', 'me"
        "ta')), FrozenPlan(fields=('sessions', 'next_cursor', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(acti"
        "on='add', fields=('sessions', 'next_cursor', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='sess"
        "ions', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, overr"
        "ide=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='n"
        "ext_cursor', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), d"
        "efault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, che"
        "ck_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(na"
        "me='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, c"
        "oerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('sessions', 'n"
        "ext_cursor', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan"
        "(fields=(ReprPlan.Field(name='sessions', kw_only=True, fn=None), ReprPlan.Field(name='next_cursor', kw_only=Tr"
        "ue, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='0221f4106276f8923c4ac54e4f2963864e056892',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'ListSessionsResponse'),
    ),
)
def _process_dataclass__0221f4106276f8923c4ac54e4f2963864e056892():
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
                sessions=self.sessions,
                next_cursor=self.next_cursor,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.sessions == other.sessions and
                self.next_cursor == other.next_cursor and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'sessions',
            'next_cursor',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'sessions',
            'next_cursor',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.sessions,
                self.next_cursor,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            sessions: __dataclass__init__fields__0__annotation,
            next_cursor: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            meta: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'sessions', sessions)
            __dataclass__object_setattr(self, 'next_cursor', next_cursor)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"sessions={self.sessions!r}")
            parts.append(f"next_cursor={self.next_cursor!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('cwd', 'mcp_servers', 'session_id', 'meta')), EqPlan(fields=('cwd', 'mcp_servers',"
        " 'session_id', 'meta')), FrozenPlan(fields=('cwd', 'mcp_servers', 'session_id', 'meta'), allow_dynamic_dunder_"
        "attrs=False), HashPlan(action='add', fields=('cwd', 'mcp_servers', 'session_id', 'meta'), cache=False), InitPl"
        "an(fields=(InitPlan.Field(name='cwd', annotation=OpRef(name='init.fields.0.annotation'), default=None, default"
        "_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_typ"
        "e=None), InitPlan.Field(name='mcp_servers', annotation=OpRef(name='init.fields.1.annotation'), default=None, d"
        "efault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, che"
        "ck_type=None), InitPlan.Field(name='session_id', annotation=OpRef(name='init.fields.2.annotation'), default=No"
        "ne, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None"
        ", check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.3.annotation'), default=OpR"
        "ef(name='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTAN"
        "CE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('cwd', 'm"
        "cp_servers', 'session_id', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns"
        "=()), ReprPlan(fields=(ReprPlan.Field(name='cwd', kw_only=True, fn=None), ReprPlan.Field(name='mcp_servers', k"
        "w_only=True, fn=None), ReprPlan.Field(name='session_id', kw_only=True, fn=None), ReprPlan.Field(name='meta', k"
        "w_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='1cc62ff4b89bda3e662088d487a880e3fb83e20a',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'LoadSessionRequest'),
    ),
)
def _process_dataclass__1cc62ff4b89bda3e662088d487a880e3fb83e20a():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
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
                cwd=self.cwd,
                mcp_servers=self.mcp_servers,
                session_id=self.session_id,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.cwd == other.cwd and
                self.mcp_servers == other.mcp_servers and
                self.session_id == other.session_id and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'cwd',
            'mcp_servers',
            'session_id',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'cwd',
            'mcp_servers',
            'session_id',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.cwd,
                self.mcp_servers,
                self.session_id,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            cwd: __dataclass__init__fields__0__annotation,
            mcp_servers: __dataclass__init__fields__1__annotation,
            session_id: __dataclass__init__fields__2__annotation,
            meta: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'cwd', cwd)
            __dataclass__object_setattr(self, 'mcp_servers', mcp_servers)
            __dataclass__object_setattr(self, 'session_id', session_id)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"cwd={self.cwd!r}")
            parts.append(f"mcp_servers={self.mcp_servers!r}")
            parts.append(f"session_id={self.session_id!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('config_options', 'modes', 'meta')), EqPlan(fields=('config_options', 'modes', 'me"
        "ta')), FrozenPlan(fields=('config_options', 'modes', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(acti"
        "on='add', fields=('config_options', 'modes', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='conf"
        "ig_options', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'), d"
        "efault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, che"
        "ck_type=None), InitPlan.Field(name='modes', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(n"
        "ame='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, "
        "coerce=None, validate=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.2"
        ".annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, f"
        "ield_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(),"
        " kw_only_params=('config_options', 'modes', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns"
        "=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='config_options', kw_only=True, fn=None), ReprPlan"
        ".Field(name='modes', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), id=False, te"
        "rse=False, default_fn=None)))"
    ),
    plan_repr_sha1='389b1375e48d8bee6c17546f5aa00cd9a0f12e92',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'LoadSessionResponse'),
    ),
)
def _process_dataclass__389b1375e48d8bee6c17546f5aa00cd9a0f12e92():
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
                config_options=self.config_options,
                modes=self.modes,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.config_options == other.config_options and
                self.modes == other.modes and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'config_options',
            'modes',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'config_options',
            'modes',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.config_options,
                self.modes,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            config_options: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            modes: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            meta: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'config_options', config_options)
            __dataclass__object_setattr(self, 'modes', modes)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"config_options={self.config_options!r}")
            parts.append(f"modes={self.modes!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('http', 'sse', 'meta')), EqPlan(fields=('http', 'sse', 'meta')), FrozenPlan(fields"
        "=('http', 'sse', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('http', 'sse', 'me"
        "ta'), cache=False), InitPlan(fields=(InitPlan.Field(name='http', annotation=OpRef(name='init.fields.0.annotati"
        "on'), default=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type"
        "=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='sse', annotation=OpRef"
        "(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=Tru"
        "e, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field"
        "(name='meta', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), "
        "default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, ch"
        "eck_type=None)), self_param='self', std_params=(), kw_only_params=('http', 'sse', 'meta'), frozen=True, slots="
        "False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='http', kw_o"
        "nly=True, fn=None), ReprPlan.Field(name='sse', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=Tru"
        "e, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='2e6cc6281b473f03fc4ac88a9a9805071f7aa922',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'McpCapabilities'),
    ),
)
def _process_dataclass__2e6cc6281b473f03fc4ac88a9a9805071f7aa922():
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
                http=self.http,
                sse=self.sse,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.http == other.http and
                self.sse == other.sse and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'http',
            'sse',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'http',
            'sse',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.http,
                self.sse,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            http: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            sse: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            meta: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'http', http)
            __dataclass__object_setattr(self, 'sse', sse)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"http={self.http!r}")
            parts.append(f"sse={self.sse!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('headers', 'name', 'url', 'meta')), EqPlan(fields=('headers', 'name', 'url', 'meta"
        "')), FrozenPlan(fields=('headers', 'name', 'url', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action="
        "'add', fields=('headers', 'name', 'url', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='headers'"
        ", annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=F"
        "alse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='name',"
        " annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=Fa"
        "lse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='url', a"
        "nnotation=OpRef(name='init.fields.2.annotation'), default=None, default_factory=None, init=True, override=Fals"
        "e, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='meta', an"
        "notation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory="
        "None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)),"
        " self_param='self', std_params=(), kw_only_params=('headers', 'name', 'url', 'meta'), frozen=True, slots=False"
        ", post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='headers', kw_onl"
        "y=True, fn=None), ReprPlan.Field(name='name', kw_only=True, fn=None), ReprPlan.Field(name='url', kw_only=True,"
        " fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='728207e462c6624ce78ae9c17850d196e373c080',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'McpServerHttp'),
        ('ommlds.specs.acp.protocol', 'McpServerSse'),
    ),
)
def _process_dataclass__728207e462c6624ce78ae9c17850d196e373c080():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
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
                headers=self.headers,
                name=self.name,
                url=self.url,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.headers == other.headers and
                self.name == other.name and
                self.url == other.url and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'headers',
            'name',
            'url',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'headers',
            'name',
            'url',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.headers,
                self.name,
                self.url,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            headers: __dataclass__init__fields__0__annotation,
            name: __dataclass__init__fields__1__annotation,
            url: __dataclass__init__fields__2__annotation,
            meta: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'headers', headers)
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'url', url)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"headers={self.headers!r}")
            parts.append(f"name={self.name!r}")
            parts.append(f"url={self.url!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('args', 'command', 'env', 'name', 'meta')), EqPlan(fields=('args', 'command', 'env"
        "', 'name', 'meta')), FrozenPlan(fields=('args', 'command', 'env', 'name', 'meta'), allow_dynamic_dunder_attrs="
        "False), HashPlan(action='add', fields=('args', 'command', 'env', 'name', 'meta'), cache=False), InitPlan(field"
        "s=(InitPlan.Field(name='args', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factor"
        "y=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)"
        ", InitPlan.Field(name='command', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_fact"
        "ory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=Non"
        "e), InitPlan.Field(name='env', annotation=OpRef(name='init.fields.2.annotation'), default=None, default_factor"
        "y=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)"
        ", InitPlan.Field(name='name', annotation=OpRef(name='init.fields.3.annotation'), default=None, default_factory"
        "=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),"
        " InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.field"
        "s.4.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, va"
        "lidate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('args', 'command', 'env', 'n"
        "ame', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields"
        "=(ReprPlan.Field(name='args', kw_only=True, fn=None), ReprPlan.Field(name='command', kw_only=True, fn=None), R"
        "eprPlan.Field(name='env', kw_only=True, fn=None), ReprPlan.Field(name='name', kw_only=True, fn=None), ReprPlan"
        ".Field(name='meta', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='615e21d7c205cc410b8de923095692c4f28667c8',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__4__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'McpServerStdio'),
    ),
)
def _process_dataclass__615e21d7c205cc410b8de923095692c4f28667c8():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__3__annotation,
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
                args=self.args,
                command=self.command,
                env=self.env,
                name=self.name,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.args == other.args and
                self.command == other.command and
                self.env == other.env and
                self.name == other.name and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'args',
            'command',
            'env',
            'name',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'args',
            'command',
            'env',
            'name',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.args,
                self.command,
                self.env,
                self.name,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            args: __dataclass__init__fields__0__annotation,
            command: __dataclass__init__fields__1__annotation,
            env: __dataclass__init__fields__2__annotation,
            name: __dataclass__init__fields__3__annotation,
            meta: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'args', args)
            __dataclass__object_setattr(self, 'command', command)
            __dataclass__object_setattr(self, 'env', env)
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"args={self.args!r}")
            parts.append(f"command={self.command!r}")
            parts.append(f"env={self.env!r}")
            parts.append(f"name={self.name!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('cwd', 'mcp_servers', 'meta')), EqPlan(fields=('cwd', 'mcp_servers', 'meta')), Fro"
        "zenPlan(fields=('cwd', 'mcp_servers', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', field"
        "s=('cwd', 'mcp_servers', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='cwd', annotation=OpRef(n"
        "ame='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=Fie"
        "ldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='mcp_servers', annotation=O"
        "pRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_ty"
        "pe=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='meta', annotation=Op"
        "Ref(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init="
        "True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param"
        "='self', std_params=(), kw_only_params=('cwd', 'mcp_servers', 'meta'), frozen=True, slots=False, post_init_par"
        "ams=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='cwd', kw_only=True, fn=None), R"
        "eprPlan.Field(name='mcp_servers', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)),"
        " id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='19b2619b0439234965c066efff3fea0ffff4b008',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'NewSessionRequest'),
    ),
)
def _process_dataclass__19b2619b0439234965c066efff3fea0ffff4b008():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
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
                cwd=self.cwd,
                mcp_servers=self.mcp_servers,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.cwd == other.cwd and
                self.mcp_servers == other.mcp_servers and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'cwd',
            'mcp_servers',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'cwd',
            'mcp_servers',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.cwd,
                self.mcp_servers,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            cwd: __dataclass__init__fields__0__annotation,
            mcp_servers: __dataclass__init__fields__1__annotation,
            meta: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'cwd', cwd)
            __dataclass__object_setattr(self, 'mcp_servers', mcp_servers)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"cwd={self.cwd!r}")
            parts.append(f"mcp_servers={self.mcp_servers!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('session_id', 'config_options', 'modes', 'meta')), EqPlan(fields=('session_id', 'c"
        "onfig_options', 'modes', 'meta')), FrozenPlan(fields=('session_id', 'config_options', 'modes', 'meta'), allow_"
        "dynamic_dunder_attrs=False), HashPlan(action='add', fields=('session_id', 'config_options', 'modes', 'meta'), "
        "cache=False), InitPlan(fields=(InitPlan.Field(name='session_id', annotation=OpRef(name='init.fields.0.annotati"
        "on'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=Non"
        "e, validate=None, check_type=None), InitPlan.Field(name='config_options', annotation=OpRef(name='init.fields.1"
        ".annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, f"
        "ield_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='modes', annot"
        "ation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=Non"
        "e, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), Ini"
        "tPlan.Field(name='meta', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3."
        "default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valida"
        "te=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('session_id', 'config_options', "
        "'modes', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fie"
        "lds=(ReprPlan.Field(name='session_id', kw_only=True, fn=None), ReprPlan.Field(name='config_options', kw_only=T"
        "rue, fn=None), ReprPlan.Field(name='modes', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, "
        "fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='50c32effbf1626cafddeffefb9b874bd813b11f4',
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
        ('ommlds.specs.acp.protocol', 'NewSessionResponse'),
    ),
)
def _process_dataclass__50c32effbf1626cafddeffefb9b874bd813b11f4():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
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
                session_id=self.session_id,
                config_options=self.config_options,
                modes=self.modes,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.session_id == other.session_id and
                self.config_options == other.config_options and
                self.modes == other.modes and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'session_id',
            'config_options',
            'modes',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'session_id',
            'config_options',
            'modes',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.session_id,
                self.config_options,
                self.modes,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            session_id: __dataclass__init__fields__0__annotation,
            config_options: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            modes: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            meta: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'session_id', session_id)
            __dataclass__object_setattr(self, 'config_options', config_options)
            __dataclass__object_setattr(self, 'modes', modes)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"session_id={self.session_id!r}")
            parts.append(f"config_options={self.config_options!r}")
            parts.append(f"modes={self.modes!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('kind', 'name', 'option_id', 'meta')), EqPlan(fields=('kind', 'name', 'option_id',"
        " 'meta')), FrozenPlan(fields=('kind', 'name', 'option_id', 'meta'), allow_dynamic_dunder_attrs=False), HashPla"
        "n(action='add', fields=('kind', 'name', 'option_id', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(na"
        "me='kind', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, o"
        "verride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(nam"
        "e='name', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, ov"
        "erride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name"
        "='option_id', annotation=OpRef(name='init.fields.2.annotation'), default=None, default_factory=None, init=True"
        ", override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field("
        "name='meta', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), d"
        "efault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, che"
        "ck_type=None)), self_param='self', std_params=(), kw_only_params=('kind', 'name', 'option_id', 'meta'), frozen"
        "=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name"
        "='kind', kw_only=True, fn=None), ReprPlan.Field(name='name', kw_only=True, fn=None), ReprPlan.Field(name='opti"
        "on_id', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), id=False, terse=False, de"
        "fault_fn=None)))"
    ),
    plan_repr_sha1='d468549cffd2ae4f16883a7c6759c7103da0769c',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'PermissionOption'),
    ),
)
def _process_dataclass__d468549cffd2ae4f16883a7c6759c7103da0769c():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
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
                kind=self.kind,
                name=self.name,
                option_id=self.option_id,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.kind == other.kind and
                self.name == other.name and
                self.option_id == other.option_id and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'kind',
            'name',
            'option_id',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'kind',
            'name',
            'option_id',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.kind,
                self.name,
                self.option_id,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            kind: __dataclass__init__fields__0__annotation,
            name: __dataclass__init__fields__1__annotation,
            option_id: __dataclass__init__fields__2__annotation,
            meta: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'kind', kind)
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'option_id', option_id)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"kind={self.kind!r}")
            parts.append(f"name={self.name!r}")
            parts.append(f"option_id={self.option_id!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('entries', 'meta')), EqPlan(fields=('entries', 'meta')), FrozenPlan(fields=('entri"
        "es', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('entries', 'meta'), cache=Fals"
        "e), InitPlan(fields=(InitPlan.Field(name='entries', annotation=OpRef(name='init.fields.0.annotation'), default"
        "=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=N"
        "one, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.1.annotation'), default="
        "OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INS"
        "TANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('entri"
        "es', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields="
        "(ReprPlan.Field(name='entries', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), i"
        "d=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='2456074c414a2fcd275441d897db41ca9e5a29da',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'Plan'),
    ),
)
def _process_dataclass__2456074c414a2fcd275441d897db41ca9e5a29da():
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
                entries=self.entries,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.entries == other.entries and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'entries',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'entries',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.entries,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            entries: __dataclass__init__fields__0__annotation,
            meta: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'entries', entries)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"entries={self.entries!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('content', 'priority', 'status', 'meta')), EqPlan(fields=('content', 'priority', '"
        "status', 'meta')), FrozenPlan(fields=('content', 'priority', 'status', 'meta'), allow_dynamic_dunder_attrs=Fal"
        "se), HashPlan(action='add', fields=('content', 'priority', 'status', 'meta'), cache=False), InitPlan(fields=(I"
        "nitPlan.Field(name='content', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory"
        "=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),"
        " InitPlan.Field(name='priority', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_fact"
        "ory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=Non"
        "e), InitPlan.Field(name='status', annotation=OpRef(name='init.fields.2.annotation'), default=None, default_fac"
        "tory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=No"
        "ne), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.f"
        "ields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None"
        ", validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('content', 'priority', '"
        "status', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fie"
        "lds=(ReprPlan.Field(name='content', kw_only=True, fn=None), ReprPlan.Field(name='priority', kw_only=True, fn=N"
        "one), ReprPlan.Field(name='status', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)"
        "), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='ff0cfdbb4243f8851f3696049fa83593049a3743',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'PlanEntry'),
    ),
)
def _process_dataclass__ff0cfdbb4243f8851f3696049fa83593049a3743():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
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
                content=self.content,
                priority=self.priority,
                status=self.status,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.content == other.content and
                self.priority == other.priority and
                self.status == other.status and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'content',
            'priority',
            'status',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'content',
            'priority',
            'status',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.content,
                self.priority,
                self.status,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            content: __dataclass__init__fields__0__annotation,
            priority: __dataclass__init__fields__1__annotation,
            status: __dataclass__init__fields__2__annotation,
            meta: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'content', content)
            __dataclass__object_setattr(self, 'priority', priority)
            __dataclass__object_setattr(self, 'status', status)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"content={self.content!r}")
            parts.append(f"priority={self.priority!r}")
            parts.append(f"status={self.status!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('entries', 'session_update', 'meta')), EqPlan(fields=('entries', 'session_update',"
        " 'meta')), FrozenPlan(fields=('entries', 'session_update', 'meta'), allow_dynamic_dunder_attrs=False), HashPla"
        "n(action='add', fields=('entries', 'session_update', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(na"
        "me='entries', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True"
        ", override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field("
        "name='session_update', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.de"
        "fault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate"
        "=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.2.annotation'), defaul"
        "t=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.I"
        "NSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('ent"
        "ries', 'session_update', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=("
        ")), ReprPlan(fields=(ReprPlan.Field(name='entries', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_onl"
        "y=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='7207a8f2e5c2889fcc03c1001328a3a08985c5a2',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'PlanSessionUpdate'),
    ),
)
def _process_dataclass__7207a8f2e5c2889fcc03c1001328a3a08985c5a2():
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
                entries=self.entries,
                session_update=self.session_update,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.entries == other.entries and
                self.session_update == other.session_update and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'entries',
            'session_update',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'entries',
            'session_update',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.entries,
                self.session_update,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            entries: __dataclass__init__fields__0__annotation,
            session_update: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            meta: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'entries', entries)
            __dataclass__object_setattr(self, 'session_update', session_update)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"entries={self.entries!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('audio', 'embedded_context', 'image', 'meta')), EqPlan(fields=('audio', 'embedded_"
        "context', 'image', 'meta')), FrozenPlan(fields=('audio', 'embedded_context', 'image', 'meta'), allow_dynamic_d"
        "under_attrs=False), HashPlan(action='add', fields=('audio', 'embedded_context', 'image', 'meta'), cache=False)"
        ", InitPlan(fields=(InitPlan.Field(name='audio', annotation=OpRef(name='init.fields.0.annotation'), default=OpR"
        "ef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTAN"
        "CE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='embedded_context', annotation=OpRef(nam"
        "e='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, o"
        "verride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(nam"
        "e='image', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), def"
        "ault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check"
        "_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name"
        "='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coe"
        "rce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('audio', 'embedd"
        "ed_context', 'image', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()),"
        " ReprPlan(fields=(ReprPlan.Field(name='audio', kw_only=True, fn=None), ReprPlan.Field(name='embedded_context',"
        " kw_only=True, fn=None), ReprPlan.Field(name='image', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_o"
        "nly=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='79bb521aa33479b153245b5f117689448b7235be',
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
        ('ommlds.specs.acp.protocol', 'PromptCapabilities'),
    ),
)
def _process_dataclass__79bb521aa33479b153245b5f117689448b7235be():
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
                audio=self.audio,
                embedded_context=self.embedded_context,
                image=self.image,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.audio == other.audio and
                self.embedded_context == other.embedded_context and
                self.image == other.image and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'audio',
            'embedded_context',
            'image',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'audio',
            'embedded_context',
            'image',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.audio,
                self.embedded_context,
                self.image,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            audio: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            embedded_context: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            image: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            meta: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'audio', audio)
            __dataclass__object_setattr(self, 'embedded_context', embedded_context)
            __dataclass__object_setattr(self, 'image', image)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"audio={self.audio!r}")
            parts.append(f"embedded_context={self.embedded_context!r}")
            parts.append(f"image={self.image!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('prompt', 'session_id', 'meta')), EqPlan(fields=('prompt', 'session_id', 'meta')),"
        " FrozenPlan(fields=('prompt', 'session_id', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add',"
        " fields=('prompt', 'session_id', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='prompt', annotat"
        "ion=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, fie"
        "ld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='session_id', an"
        "notation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False"
        ", field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='meta', ann"
        "otation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=N"
        "one, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), "
        "self_param='self', std_params=(), kw_only_params=('prompt', 'session_id', 'meta'), frozen=True, slots=False, p"
        "ost_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='prompt', kw_only=Tr"
        "ue, fn=None), ReprPlan.Field(name='session_id', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=Tr"
        "ue, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='dedffe3ad43ebbf0f377839fbc1c661ac0c51397',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'PromptRequest'),
    ),
)
def _process_dataclass__dedffe3ad43ebbf0f377839fbc1c661ac0c51397():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
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
                prompt=self.prompt,
                session_id=self.session_id,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.prompt == other.prompt and
                self.session_id == other.session_id and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'prompt',
            'session_id',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'prompt',
            'session_id',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.prompt,
                self.session_id,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            prompt: __dataclass__init__fields__0__annotation,
            session_id: __dataclass__init__fields__1__annotation,
            meta: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'prompt', prompt)
            __dataclass__object_setattr(self, 'session_id', session_id)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"prompt={self.prompt!r}")
            parts.append(f"session_id={self.session_id!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('stop_reason', 'meta')), EqPlan(fields=('stop_reason', 'meta')), FrozenPlan(fields"
        "=('stop_reason', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('stop_reason', 'me"
        "ta'), cache=False), InitPlan(fields=(InitPlan.Field(name='stop_reason', annotation=OpRef(name='init.fields.0.a"
        "nnotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coe"
        "rce=None, validate=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.1.an"
        "notation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, fiel"
        "d_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw"
        "_only_params=('stop_reason', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_f"
        "ns=()), ReprPlan(fields=(ReprPlan.Field(name='stop_reason', kw_only=True, fn=None), ReprPlan.Field(name='meta'"
        ", kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='a187764d40284aa904dd820cd176363268bff78e',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'PromptResponse'),
    ),
)
def _process_dataclass__a187764d40284aa904dd820cd176363268bff78e():
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
                stop_reason=self.stop_reason,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.stop_reason == other.stop_reason and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'stop_reason',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'stop_reason',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.stop_reason,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            stop_reason: __dataclass__init__fields__0__annotation,
            meta: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'stop_reason', stop_reason)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"stop_reason={self.stop_reason!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('path', 'session_id', 'limit', 'line', 'meta')), EqPlan(fields=('path', 'session_i"
        "d', 'limit', 'line', 'meta')), FrozenPlan(fields=('path', 'session_id', 'limit', 'line', 'meta'), allow_dynami"
        "c_dunder_attrs=False), HashPlan(action='add', fields=('path', 'session_id', 'limit', 'line', 'meta'), cache=Fa"
        "lse), InitPlan(fields=(InitPlan.Field(name='path', annotation=OpRef(name='init.fields.0.annotation'), default="
        "None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=No"
        "ne, check_type=None), InitPlan.Field(name='session_id', annotation=OpRef(name='init.fields.1.annotation'), def"
        "ault=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valida"
        "te=None, check_type=None), InitPlan.Field(name='limit', annotation=OpRef(name='init.fields.2.annotation'), def"
        "ault=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldTyp"
        "e.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='line', annotation=OpRef(name='i"
        "nit.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, overr"
        "ide=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='m"
        "eta', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_"
        "factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type"
        "=None)), self_param='self', std_params=(), kw_only_params=('path', 'session_id', 'limit', 'line', 'meta'), fro"
        "zen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(n"
        "ame='path', kw_only=True, fn=None), ReprPlan.Field(name='session_id', kw_only=True, fn=None), ReprPlan.Field(n"
        "ame='limit', kw_only=True, fn=None), ReprPlan.Field(name='line', kw_only=True, fn=None), ReprPlan.Field(name='"
        "meta', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='04dfcd702fe36e6c8bc1885c6588f295840bfd6c',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__4__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'ReadTextFileRequest'),
    ),
)
def _process_dataclass__04dfcd702fe36e6c8bc1885c6588f295840bfd6c():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
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
                path=self.path,
                session_id=self.session_id,
                limit=self.limit,
                line=self.line,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.path == other.path and
                self.session_id == other.session_id and
                self.limit == other.limit and
                self.line == other.line and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'path',
            'session_id',
            'limit',
            'line',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'path',
            'session_id',
            'limit',
            'line',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.path,
                self.session_id,
                self.limit,
                self.line,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            path: __dataclass__init__fields__0__annotation,
            session_id: __dataclass__init__fields__1__annotation,
            limit: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            line: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            meta: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'path', path)
            __dataclass__object_setattr(self, 'session_id', session_id)
            __dataclass__object_setattr(self, 'limit', limit)
            __dataclass__object_setattr(self, 'line', line)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"path={self.path!r}")
            parts.append(f"session_id={self.session_id!r}")
            parts.append(f"limit={self.limit!r}")
            parts.append(f"line={self.line!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('options', 'session_id', 'tool_call', 'meta')), EqPlan(fields=('options', 'session"
        "_id', 'tool_call', 'meta')), FrozenPlan(fields=('options', 'session_id', 'tool_call', 'meta'), allow_dynamic_d"
        "under_attrs=False), HashPlan(action='add', fields=('options', 'session_id', 'tool_call', 'meta'), cache=False)"
        ", InitPlan(fields=(InitPlan.Field(name='options', annotation=OpRef(name='init.fields.0.annotation'), default=N"
        "one, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=Non"
        "e, check_type=None), InitPlan.Field(name='session_id', annotation=OpRef(name='init.fields.1.annotation'), defa"
        "ult=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validat"
        "e=None, check_type=None), InitPlan.Field(name='tool_call', annotation=OpRef(name='init.fields.2.annotation'), "
        "default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, val"
        "idate=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.3.annotation'), d"
        "efault=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldT"
        "ype.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params="
        "('options', 'session_id', 'tool_call', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), "
        "validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='options', kw_only=True, fn=None), ReprPlan.Field(name="
        "'session_id', kw_only=True, fn=None), ReprPlan.Field(name='tool_call', kw_only=True, fn=None), ReprPlan.Field("
        "name='meta', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='bc0f498a626da6415d123f047312a8d868f42b24',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'RequestPermissionRequest'),
    ),
)
def _process_dataclass__bc0f498a626da6415d123f047312a8d868f42b24():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
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
                options=self.options,
                session_id=self.session_id,
                tool_call=self.tool_call,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.options == other.options and
                self.session_id == other.session_id and
                self.tool_call == other.tool_call and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'options',
            'session_id',
            'tool_call',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'options',
            'session_id',
            'tool_call',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.options,
                self.session_id,
                self.tool_call,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            options: __dataclass__init__fields__0__annotation,
            session_id: __dataclass__init__fields__1__annotation,
            tool_call: __dataclass__init__fields__2__annotation,
            meta: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'options', options)
            __dataclass__object_setattr(self, 'session_id', session_id)
            __dataclass__object_setattr(self, 'tool_call', tool_call)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"options={self.options!r}")
            parts.append(f"session_id={self.session_id!r}")
            parts.append(f"tool_call={self.tool_call!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('outcome', 'meta')), EqPlan(fields=('outcome', 'meta')), FrozenPlan(fields=('outco"
        "me', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('outcome', 'meta'), cache=Fals"
        "e), InitPlan(fields=(InitPlan.Field(name='outcome', annotation=OpRef(name='init.fields.0.annotation'), default"
        "=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=N"
        "one, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.1.annotation'), default="
        "OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INS"
        "TANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('outco"
        "me', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields="
        "(ReprPlan.Field(name='outcome', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), i"
        "d=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='49fcca1dc856608730fefa6635181ab724867950',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'RequestPermissionResponse'),
    ),
)
def _process_dataclass__49fcca1dc856608730fefa6635181ab724867950():
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
                outcome=self.outcome,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.outcome == other.outcome and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'outcome',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'outcome',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.outcome,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            outcome: __dataclass__init__fields__0__annotation,
            meta: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'outcome', outcome)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"outcome={self.outcome!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('resource', 'type', 'annotations', 'meta')), EqPlan(fields=('resource', 'type', 'a"
        "nnotations', 'meta')), FrozenPlan(fields=('resource', 'type', 'annotations', 'meta'), allow_dynamic_dunder_att"
        "rs=False), HashPlan(action='add', fields=('resource', 'type', 'annotations', 'meta'), cache=False), InitPlan(f"
        "ields=(InitPlan.Field(name='resource', annotation=OpRef(name='init.fields.0.annotation'), default=None, defaul"
        "t_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_ty"
        "pe=None), InitPlan.Field(name='type', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='i"
        "nit.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce"
        "=None, validate=None, check_type=None), InitPlan.Field(name='annotations', annotation=OpRef(name='init.fields."
        "2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, "
        "field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='meta', annot"
        "ation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=Non"
        "e, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), se"
        "lf_param='self', std_params=(), kw_only_params=('resource', 'type', 'annotations', 'meta'), frozen=True, slots"
        "=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='resource',"
        " kw_only=True, fn=None), ReprPlan.Field(name='annotations', kw_only=True, fn=None), ReprPlan.Field(name='meta'"
        ", kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='f43096e058ee91ee55f8145a15e01b7ad36a0096',
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
        ('ommlds.specs.acp.protocol', 'ResourceContentBlock'),
    ),
)
def _process_dataclass__f43096e058ee91ee55f8145a15e01b7ad36a0096():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
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
                resource=self.resource,
                type=self.type,
                annotations=self.annotations,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.resource == other.resource and
                self.type == other.type and
                self.annotations == other.annotations and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'resource',
            'type',
            'annotations',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'resource',
            'type',
            'annotations',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.resource,
                self.type,
                self.annotations,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            resource: __dataclass__init__fields__0__annotation,
            type: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            annotations: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            meta: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'resource', resource)
            __dataclass__object_setattr(self, 'type', type)
            __dataclass__object_setattr(self, 'annotations', annotations)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"resource={self.resource!r}")
            parts.append(f"annotations={self.annotations!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('name', 'uri', 'annotations', 'description', 'mime_type', 'size', 'title', 'meta')"
        "), EqPlan(fields=('name', 'uri', 'annotations', 'description', 'mime_type', 'size', 'title', 'meta')), FrozenP"
        "lan(fields=('name', 'uri', 'annotations', 'description', 'mime_type', 'size', 'title', 'meta'), allow_dynamic_"
        "dunder_attrs=False), HashPlan(action='add', fields=('name', 'uri', 'annotations', 'description', 'mime_type', "
        "'size', 'title', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='name', annotation=OpRef(name='in"
        "it.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType."
        "INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='uri', annotation=OpRef(name='init"
        ".fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.IN"
        "STANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='annotations', annotation=OpRef(name"
        "='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, ov"
        "erride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name"
        "='description', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default')"
        ", default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, "
        "check_type=None), InitPlan.Field(name='mime_type', annotation=OpRef(name='init.fields.4.annotation'), default="
        "OpRef(name='init.fields.4.default'), default_factory=None, init=True, override=False, field_type=FieldType.INS"
        "TANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='size', annotation=OpRef(name='init.f"
        "ields.5.annotation'), default=OpRef(name='init.fields.5.default'), default_factory=None, init=True, override=F"
        "alse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='title'"
        ", annotation=OpRef(name='init.fields.6.annotation'), default=OpRef(name='init.fields.6.default'), default_fact"
        "ory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=Non"
        "e), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.7.annotation'), default=OpRef(name='init.fi"
        "elds.7.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None,"
        " validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('name', 'uri', 'annotatio"
        "ns', 'description', 'mime_type', 'size', 'title', 'meta'), frozen=True, slots=False, post_init_params=None, in"
        "it_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='name', kw_only=True, fn=None), ReprPlan.Fie"
        "ld(name='uri', kw_only=True, fn=None), ReprPlan.Field(name='annotations', kw_only=True, fn=None), ReprPlan.Fie"
        "ld(name='description', kw_only=True, fn=None), ReprPlan.Field(name='mime_type', kw_only=True, fn=None), ReprPl"
        "an.Field(name='size', kw_only=True, fn=None), ReprPlan.Field(name='title', kw_only=True, fn=None), ReprPlan.Fi"
        "eld(name='meta', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='a506908c7b060215cd39188eeb85194a68a0e880',
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
        ('ommlds.specs.acp.protocol', 'ResourceLink'),
    ),
)
def _process_dataclass__a506908c7b060215cd39188eeb85194a68a0e880():
    def _process_dataclass(
        *,
        __class__,
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
                name=self.name,
                uri=self.uri,
                annotations=self.annotations,
                description=self.description,
                mime_type=self.mime_type,
                size=self.size,
                title=self.title,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.name == other.name and
                self.uri == other.uri and
                self.annotations == other.annotations and
                self.description == other.description and
                self.mime_type == other.mime_type and
                self.size == other.size and
                self.title == other.title and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'name',
            'uri',
            'annotations',
            'description',
            'mime_type',
            'size',
            'title',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'name',
            'uri',
            'annotations',
            'description',
            'mime_type',
            'size',
            'title',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.name,
                self.uri,
                self.annotations,
                self.description,
                self.mime_type,
                self.size,
                self.title,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            name: __dataclass__init__fields__0__annotation,
            uri: __dataclass__init__fields__1__annotation,
            annotations: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            description: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            mime_type: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            size: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
            title: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
            meta: __dataclass__init__fields__7__annotation = __dataclass__init__fields__7__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'uri', uri)
            __dataclass__object_setattr(self, 'annotations', annotations)
            __dataclass__object_setattr(self, 'description', description)
            __dataclass__object_setattr(self, 'mime_type', mime_type)
            __dataclass__object_setattr(self, 'size', size)
            __dataclass__object_setattr(self, 'title', title)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"name={self.name!r}")
            parts.append(f"uri={self.uri!r}")
            parts.append(f"annotations={self.annotations!r}")
            parts.append(f"description={self.description!r}")
            parts.append(f"mime_type={self.mime_type!r}")
            parts.append(f"size={self.size!r}")
            parts.append(f"title={self.title!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('name', 'uri', 'type', 'annotations', 'description', 'mime_type', 'size', 'title',"
        " 'meta')), EqPlan(fields=('name', 'uri', 'type', 'annotations', 'description', 'mime_type', 'size', 'title', '"
        "meta')), FrozenPlan(fields=('name', 'uri', 'type', 'annotations', 'description', 'mime_type', 'size', 'title',"
        " 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('name', 'uri', 'type', 'annotation"
        "s', 'description', 'mime_type', 'size', 'title', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='"
        "name', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, overr"
        "ide=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='u"
        "ri', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, overrid"
        "e=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='typ"
        "e', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_fa"
        "ctory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=N"
        "one), InitPlan.Field(name='annotations', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name"
        "='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coe"
        "rce=None, validate=None, check_type=None), InitPlan.Field(name='description', annotation=OpRef(name='init.fiel"
        "ds.4.annotation'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, override=Fals"
        "e, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='mime_type"
        "', annotation=OpRef(name='init.fields.5.annotation'), default=OpRef(name='init.fields.5.default'), default_fac"
        "tory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=No"
        "ne), InitPlan.Field(name='size', annotation=OpRef(name='init.fields.6.annotation'), default=OpRef(name='init.f"
        "ields.6.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None"
        ", validate=None, check_type=None), InitPlan.Field(name='title', annotation=OpRef(name='init.fields.7.annotatio"
        "n'), default=OpRef(name='init.fields.7.default'), default_factory=None, init=True, override=False, field_type="
        "FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef"
        "(name='init.fields.8.annotation'), default=OpRef(name='init.fields.8.default'), default_factory=None, init=Tru"
        "e, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='s"
        "elf', std_params=(), kw_only_params=('name', 'uri', 'type', 'annotations', 'description', 'mime_type', 'size',"
        " 'title', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fi"
        "elds=(ReprPlan.Field(name='name', kw_only=True, fn=None), ReprPlan.Field(name='uri', kw_only=True, fn=None), R"
        "eprPlan.Field(name='annotations', kw_only=True, fn=None), ReprPlan.Field(name='description', kw_only=True, fn="
        "None), ReprPlan.Field(name='mime_type', kw_only=True, fn=None), ReprPlan.Field(name='size', kw_only=True, fn=N"
        "one), ReprPlan.Field(name='title', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None))"
        ", id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='537223d86cb1d4b513a97dd71a335869561e8b49',
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
        ('ommlds.specs.acp.protocol', 'ResourceLinkContentBlock'),
    ),
)
def _process_dataclass__537223d86cb1d4b513a97dd71a335869561e8b49():
    def _process_dataclass(
        *,
        __class__,
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
                name=self.name,
                uri=self.uri,
                type=self.type,
                annotations=self.annotations,
                description=self.description,
                mime_type=self.mime_type,
                size=self.size,
                title=self.title,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.name == other.name and
                self.uri == other.uri and
                self.type == other.type and
                self.annotations == other.annotations and
                self.description == other.description and
                self.mime_type == other.mime_type and
                self.size == other.size and
                self.title == other.title and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'name',
            'uri',
            'type',
            'annotations',
            'description',
            'mime_type',
            'size',
            'title',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'name',
            'uri',
            'type',
            'annotations',
            'description',
            'mime_type',
            'size',
            'title',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.name,
                self.uri,
                self.type,
                self.annotations,
                self.description,
                self.mime_type,
                self.size,
                self.title,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            name: __dataclass__init__fields__0__annotation,
            uri: __dataclass__init__fields__1__annotation,
            type: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            annotations: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            description: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            mime_type: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
            size: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
            title: __dataclass__init__fields__7__annotation = __dataclass__init__fields__7__default,
            meta: __dataclass__init__fields__8__annotation = __dataclass__init__fields__8__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'uri', uri)
            __dataclass__object_setattr(self, 'type', type)
            __dataclass__object_setattr(self, 'annotations', annotations)
            __dataclass__object_setattr(self, 'description', description)
            __dataclass__object_setattr(self, 'mime_type', mime_type)
            __dataclass__object_setattr(self, 'size', size)
            __dataclass__object_setattr(self, 'title', title)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"name={self.name!r}")
            parts.append(f"uri={self.uri!r}")
            parts.append(f"annotations={self.annotations!r}")
            parts.append(f"description={self.description!r}")
            parts.append(f"mime_type={self.mime_type!r}")
            parts.append(f"size={self.size!r}")
            parts.append(f"title={self.title!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('current_value', 'options', 'type')), EqPlan(fields=('current_value', 'options', '"
        "type')), FrozenPlan(fields=('current_value', 'options', 'type'), allow_dynamic_dunder_attrs=False), HashPlan(a"
        "ction='add', fields=('current_value', 'options', 'type'), cache=False), InitPlan(fields=(InitPlan.Field(name='"
        "current_value', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=Tr"
        "ue, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fiel"
        "d(name='options', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init="
        "True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fi"
        "eld(name='type', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'"
        "), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None,"
        " check_type=None)), self_param='self', std_params=(), kw_only_params=('current_value', 'options', 'type'), fro"
        "zen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(n"
        "ame='current_value', kw_only=True, fn=None), ReprPlan.Field(name='options', kw_only=True, fn=None)), id=False,"
        " terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='d6045c59e2b9ddd287d50bdc7a3314b97e1246c7',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'SelectSessionConfigOption'),
    ),
)
def _process_dataclass__d6045c59e2b9ddd287d50bdc7a3314b97e1246c7():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
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
                current_value=self.current_value,
                options=self.options,
                type=self.type,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.current_value == other.current_value and
                self.options == other.options and
                self.type == other.type
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'current_value',
            'options',
            'type',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'current_value',
            'options',
            'type',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.current_value,
                self.options,
                self.type,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            current_value: __dataclass__init__fields__0__annotation,
            options: __dataclass__init__fields__1__annotation,
            type: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'current_value', current_value)
            __dataclass__object_setattr(self, 'options', options)
            __dataclass__object_setattr(self, 'type', type)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"current_value={self.current_value!r}")
            parts.append(f"options={self.options!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('option_id', 'meta')), EqPlan(fields=('option_id', 'meta')), FrozenPlan(fields=('o"
        "ption_id', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('option_id', 'meta'), ca"
        "che=False), InitPlan(fields=(InitPlan.Field(name='option_id', annotation=OpRef(name='init.fields.0.annotation'"
        "), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, "
        "validate=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.1.annotation')"
        ", default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=Fie"
        "ldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_para"
        "ms=('option_id', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), Repr"
        "Plan(fields=(ReprPlan.Field(name='option_id', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True"
        ", fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='611d5d7d01baff06f75eb0fc432dab7e646a56ea',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'SelectedPermissionOutcome'),
    ),
)
def _process_dataclass__611d5d7d01baff06f75eb0fc432dab7e646a56ea():
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
                option_id=self.option_id,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.option_id == other.option_id and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'option_id',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'option_id',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.option_id,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            option_id: __dataclass__init__fields__0__annotation,
            meta: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'option_id', option_id)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"option_id={self.option_id!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('option_id', 'outcome', 'meta')), EqPlan(fields=('option_id', 'outcome', 'meta')),"
        " FrozenPlan(fields=('option_id', 'outcome', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add',"
        " fields=('option_id', 'outcome', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='option_id', anno"
        "tation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, "
        "field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='outcome', an"
        "notation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory="
        "None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), "
        "InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields"
        ".2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, val"
        "idate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('option_id', 'outcome', 'meta"
        "'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan."
        "Field(name='option_id', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), id=False,"
        " terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='e351cfdd4f5e1a324cf43c4d0042ce23efc22c3a',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'SelectedRequestPermissionOutcome'),
    ),
)
def _process_dataclass__e351cfdd4f5e1a324cf43c4d0042ce23efc22c3a():
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
                option_id=self.option_id,
                outcome=self.outcome,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.option_id == other.option_id and
                self.outcome == other.outcome and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'option_id',
            'outcome',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'option_id',
            'outcome',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.option_id,
                self.outcome,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            option_id: __dataclass__init__fields__0__annotation,
            outcome: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            meta: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'option_id', option_id)
            __dataclass__object_setattr(self, 'outcome', outcome)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"option_id={self.option_id!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('list', 'meta')), EqPlan(fields=('list', 'meta')), FrozenPlan(fields=('list', 'met"
        "a'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('list', 'meta'), cache=False), InitPlan"
        "(fields=(InitPlan.Field(name='list', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='in"
        "it.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce="
        "None, validate=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.1.annota"
        "tion'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_ty"
        "pe=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_onl"
        "y_params=('list', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), Rep"
        "rPlan(fields=(ReprPlan.Field(name='list', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn"
        "=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='19181ac8205e3b06b2d832950d5103dd90b219df',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'SessionCapabilities'),
    ),
)
def _process_dataclass__19181ac8205e3b06b2d832950d5103dd90b219df():
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
                list=self.list,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.list == other.list and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'list',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'list',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.list,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            list: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            meta: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'list', list)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"list={self.list!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('current_value', 'options')), EqPlan(fields=('current_value', 'options')), FrozenP"
        "lan(fields=('current_value', 'options'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('cu"
        "rrent_value', 'options'), cache=False), InitPlan(fields=(InitPlan.Field(name='current_value', annotation=OpRef"
        "(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=F"
        "ieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='options', annotation=OpR"
        "ef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type"
        "=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_"
        "params=('current_value', 'options'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fn"
        "s=()), ReprPlan(fields=(ReprPlan.Field(name='current_value', kw_only=True, fn=None), ReprPlan.Field(name='opti"
        "ons', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='233831d4725c650e4680a853b193e597c3397f3f',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'SessionConfigSelect'),
    ),
)
def _process_dataclass__233831d4725c650e4680a853b193e597c3397f3f():
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
                current_value=self.current_value,
                options=self.options,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.current_value == other.current_value and
                self.options == other.options
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'current_value',
            'options',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'current_value',
            'options',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.current_value,
                self.options,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            current_value: __dataclass__init__fields__0__annotation,
            options: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'current_value', current_value)
            __dataclass__object_setattr(self, 'options', options)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"current_value={self.current_value!r}")
            parts.append(f"options={self.options!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('group', 'name', 'options', 'meta')), EqPlan(fields=('group', 'name', 'options', '"
        "meta')), FrozenPlan(fields=('group', 'name', 'options', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(a"
        "ction='add', fields=('group', 'name', 'options', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='"
        "group', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, over"
        "ride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='"
        "name', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, overr"
        "ide=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='o"
        "ptions', annotation=OpRef(name='init.fields.2.annotation'), default=None, default_factory=None, init=True, ove"
        "rride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name="
        "'meta', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), defaul"
        "t_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_ty"
        "pe=None)), self_param='self', std_params=(), kw_only_params=('group', 'name', 'options', 'meta'), frozen=True,"
        " slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='grou"
        "p', kw_only=True, fn=None), ReprPlan.Field(name='name', kw_only=True, fn=None), ReprPlan.Field(name='options',"
        " kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), id=False, terse=False, default_f"
        "n=None)))"
    ),
    plan_repr_sha1='ef4bb32eb1805300e980b4e0294ff3811e68f850',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'SessionConfigSelectGroup'),
    ),
)
def _process_dataclass__ef4bb32eb1805300e980b4e0294ff3811e68f850():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
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
                group=self.group,
                name=self.name,
                options=self.options,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.group == other.group and
                self.name == other.name and
                self.options == other.options and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'group',
            'name',
            'options',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'group',
            'name',
            'options',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.group,
                self.name,
                self.options,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            group: __dataclass__init__fields__0__annotation,
            name: __dataclass__init__fields__1__annotation,
            options: __dataclass__init__fields__2__annotation,
            meta: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'group', group)
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'options', options)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"group={self.group!r}")
            parts.append(f"name={self.name!r}")
            parts.append(f"options={self.options!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('name', 'value', 'description', 'meta')), EqPlan(fields=('name', 'value', 'descrip"
        "tion', 'meta')), FrozenPlan(fields=('name', 'value', 'description', 'meta'), allow_dynamic_dunder_attrs=False)"
        ", HashPlan(action='add', fields=('name', 'value', 'description', 'meta'), cache=False), InitPlan(fields=(InitP"
        "lan.Field(name='name', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, "
        "init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPl"
        "an.Field(name='value', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, "
        "init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPl"
        "an.Field(name='description', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.field"
        "s.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, va"
        "lidate=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.3.annotation'), "
        "default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=Field"
        "Type.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params"
        "=('name', 'value', 'description', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), valid"
        "ate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='name', kw_only=True, fn=None), ReprPlan.Field(name='value',"
        " kw_only=True, fn=None), ReprPlan.Field(name='description', kw_only=True, fn=None), ReprPlan.Field(name='meta'"
        ", kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='3b7bb867c3ee95fa308cd47e1124a4e7e470f748',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'SessionConfigSelectOption'),
    ),
)
def _process_dataclass__3b7bb867c3ee95fa308cd47e1124a4e7e470f748():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
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
                name=self.name,
                value=self.value,
                description=self.description,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.name == other.name and
                self.value == other.value and
                self.description == other.description and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'name',
            'value',
            'description',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'name',
            'value',
            'description',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.name,
                self.value,
                self.description,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            name: __dataclass__init__fields__0__annotation,
            value: __dataclass__init__fields__1__annotation,
            description: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            meta: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'value', value)
            __dataclass__object_setattr(self, 'description', description)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"name={self.name!r}")
            parts.append(f"value={self.value!r}")
            parts.append(f"description={self.description!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('cwd', 'session_id', 'title', 'updated_at', 'meta')), EqPlan(fields=('cwd', 'sessi"
        "on_id', 'title', 'updated_at', 'meta')), FrozenPlan(fields=('cwd', 'session_id', 'title', 'updated_at', 'meta'"
        "), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('cwd', 'session_id', 'title', 'updated_at"
        "', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='cwd', annotation=OpRef(name='init.fields.0.ann"
        "otation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerc"
        "e=None, validate=None, check_type=None), InitPlan.Field(name='session_id', annotation=OpRef(name='init.fields."
        "1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, "
        "coerce=None, validate=None, check_type=None), InitPlan.Field(name='title', annotation=OpRef(name='init.fields."
        "2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, "
        "field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='updated_at',"
        " annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_facto"
        "ry=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None"
        "), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fie"
        "lds.4.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, "
        "validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('cwd', 'session_id', 'titl"
        "e', 'updated_at', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), Rep"
        "rPlan(fields=(ReprPlan.Field(name='cwd', kw_only=True, fn=None), ReprPlan.Field(name='session_id', kw_only=Tru"
        "e, fn=None), ReprPlan.Field(name='title', kw_only=True, fn=None), ReprPlan.Field(name='updated_at', kw_only=Tr"
        "ue, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='0c48ebcd288005f41ca056557eb316a557e0f8a4',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
        '__dataclass__init__fields__4__annotation',
        '__dataclass__init__fields__4__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'SessionInfo'),
    ),
)
def _process_dataclass__0c48ebcd288005f41ca056557eb316a557e0f8a4():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
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
                cwd=self.cwd,
                session_id=self.session_id,
                title=self.title,
                updated_at=self.updated_at,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.cwd == other.cwd and
                self.session_id == other.session_id and
                self.title == other.title and
                self.updated_at == other.updated_at and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'cwd',
            'session_id',
            'title',
            'updated_at',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'cwd',
            'session_id',
            'title',
            'updated_at',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.cwd,
                self.session_id,
                self.title,
                self.updated_at,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            cwd: __dataclass__init__fields__0__annotation,
            session_id: __dataclass__init__fields__1__annotation,
            title: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            updated_at: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            meta: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'cwd', cwd)
            __dataclass__object_setattr(self, 'session_id', session_id)
            __dataclass__object_setattr(self, 'title', title)
            __dataclass__object_setattr(self, 'updated_at', updated_at)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"cwd={self.cwd!r}")
            parts.append(f"session_id={self.session_id!r}")
            parts.append(f"title={self.title!r}")
            parts.append(f"updated_at={self.updated_at!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('title', 'updated_at', 'meta')), EqPlan(fields=('title', 'updated_at', 'meta')), F"
        "rozenPlan(fields=('title', 'updated_at', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fi"
        "elds=('title', 'updated_at', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='title', annotation=O"
        "pRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'), default_factory=None, init"
        "=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.F"
        "ield(name='updated_at', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.d"
        "efault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validat"
        "e=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.2.annotation'), defau"
        "lt=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType."
        "INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('ti"
        "tle', 'updated_at', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), R"
        "eprPlan(fields=(ReprPlan.Field(name='title', kw_only=True, fn=None), ReprPlan.Field(name='updated_at', kw_only"
        "=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), id=False, terse=False, default_fn=None))"
        ")"
    ),
    plan_repr_sha1='8884321ddff9ee3ca465afc21508731106646faf',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'SessionInfoUpdate'),
    ),
)
def _process_dataclass__8884321ddff9ee3ca465afc21508731106646faf():
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
                title=self.title,
                updated_at=self.updated_at,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.title == other.title and
                self.updated_at == other.updated_at and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'title',
            'updated_at',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'title',
            'updated_at',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.title,
                self.updated_at,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            title: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            updated_at: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            meta: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'title', title)
            __dataclass__object_setattr(self, 'updated_at', updated_at)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"title={self.title!r}")
            parts.append(f"updated_at={self.updated_at!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('session_update', 'title', 'updated_at', 'meta')), EqPlan(fields=('session_update'"
        ", 'title', 'updated_at', 'meta')), FrozenPlan(fields=('session_update', 'title', 'updated_at', 'meta'), allow_"
        "dynamic_dunder_attrs=False), HashPlan(action='add', fields=('session_update', 'title', 'updated_at', 'meta'), "
        "cache=False), InitPlan(fields=(InitPlan.Field(name='session_update', annotation=OpRef(name='init.fields.0.anno"
        "tation'), default=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_"
        "type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='title', annotation"
        "=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, in"
        "it=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan"
        ".Field(name='updated_at', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2"
        ".default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valid"
        "ate=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.3.annotation'), def"
        "ault=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldTyp"
        "e.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('"
        "session_update', 'title', 'updated_at', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(),"
        " validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='title', kw_only=True, fn=None), ReprPlan.Field(name='"
        "updated_at', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), id=False, terse=Fals"
        "e, default_fn=None)))"
    ),
    plan_repr_sha1='6781ce1d6ce59cd7459a3b5db4a348f807a046b3',
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
        ('ommlds.specs.acp.protocol', 'SessionInfoUpdateSessionUpdate'),
    ),
)
def _process_dataclass__6781ce1d6ce59cd7459a3b5db4a348f807a046b3():
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
                session_update=self.session_update,
                title=self.title,
                updated_at=self.updated_at,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.session_update == other.session_update and
                self.title == other.title and
                self.updated_at == other.updated_at and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'session_update',
            'title',
            'updated_at',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'session_update',
            'title',
            'updated_at',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.session_update,
                self.title,
                self.updated_at,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            session_update: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            title: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            updated_at: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            meta: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'session_update', session_update)
            __dataclass__object_setattr(self, 'title', title)
            __dataclass__object_setattr(self, 'updated_at', updated_at)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"title={self.title!r}")
            parts.append(f"updated_at={self.updated_at!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('available_modes', 'current_mode_id', 'meta')), EqPlan(fields=('available_modes', "
        "'current_mode_id', 'meta')), FrozenPlan(fields=('available_modes', 'current_mode_id', 'meta'), allow_dynamic_d"
        "under_attrs=False), HashPlan(action='add', fields=('available_modes', 'current_mode_id', 'meta'), cache=False)"
        ", InitPlan(fields=(InitPlan.Field(name='available_modes', annotation=OpRef(name='init.fields.0.annotation'), d"
        "efault=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, vali"
        "date=None, check_type=None), InitPlan.Field(name='current_mode_id', annotation=OpRef(name='init.fields.1.annot"
        "ation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce="
        "None, validate=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.2.annota"
        "tion'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_ty"
        "pe=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_onl"
        "y_params=('available_modes', 'current_mode_id', 'meta'), frozen=True, slots=False, post_init_params=None, init"
        "_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='available_modes', kw_only=True, fn=None), Rep"
        "rPlan.Field(name='current_mode_id', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)"
        "), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='dc32dc785bdac608508d1412f45b17907d8faf50',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'SessionModeState'),
    ),
)
def _process_dataclass__dc32dc785bdac608508d1412f45b17907d8faf50():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
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
                available_modes=self.available_modes,
                current_mode_id=self.current_mode_id,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.available_modes == other.available_modes and
                self.current_mode_id == other.current_mode_id and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'available_modes',
            'current_mode_id',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'available_modes',
            'current_mode_id',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.available_modes,
                self.current_mode_id,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            available_modes: __dataclass__init__fields__0__annotation,
            current_mode_id: __dataclass__init__fields__1__annotation,
            meta: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'available_modes', available_modes)
            __dataclass__object_setattr(self, 'current_mode_id', current_mode_id)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"available_modes={self.available_modes!r}")
            parts.append(f"current_mode_id={self.current_mode_id!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('session_id', 'update', 'meta')), EqPlan(fields=('session_id', 'update', 'meta')),"
        " FrozenPlan(fields=('session_id', 'update', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add',"
        " fields=('session_id', 'update', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='session_id', ann"
        "otation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False,"
        " field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='update', an"
        "notation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False"
        ", field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='meta', ann"
        "otation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=N"
        "one, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), "
        "self_param='self', std_params=(), kw_only_params=('session_id', 'update', 'meta'), frozen=True, slots=False, p"
        "ost_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='session_id', kw_onl"
        "y=True, fn=None), ReprPlan.Field(name='update', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=Tr"
        "ue, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='442eba46336a87f6583c31cc5d239c7fd20a719d',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'SessionNotification'),
    ),
)
def _process_dataclass__442eba46336a87f6583c31cc5d239c7fd20a719d():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
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
                session_id=self.session_id,
                update=self.update,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.session_id == other.session_id and
                self.update == other.update and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'session_id',
            'update',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'session_id',
            'update',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.session_id,
                self.update,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            session_id: __dataclass__init__fields__0__annotation,
            update: __dataclass__init__fields__1__annotation,
            meta: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'session_id', session_id)
            __dataclass__object_setattr(self, 'update', update)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"session_id={self.session_id!r}")
            parts.append(f"update={self.update!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('config_id', 'session_id', 'value', 'meta')), EqPlan(fields=('config_id', 'session"
        "_id', 'value', 'meta')), FrozenPlan(fields=('config_id', 'session_id', 'value', 'meta'), allow_dynamic_dunder_"
        "attrs=False), HashPlan(action='add', fields=('config_id', 'session_id', 'value', 'meta'), cache=False), InitPl"
        "an(fields=(InitPlan.Field(name='config_id', annotation=OpRef(name='init.fields.0.annotation'), default=None, d"
        "efault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, che"
        "ck_type=None), InitPlan.Field(name='session_id', annotation=OpRef(name='init.fields.1.annotation'), default=No"
        "ne, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None"
        ", check_type=None), InitPlan.Field(name='value', annotation=OpRef(name='init.fields.2.annotation'), default=No"
        "ne, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None"
        ", check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.3.annotation'), default=OpR"
        "ef(name='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTAN"
        "CE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('config_i"
        "d', 'session_id', 'value', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns"
        "=()), ReprPlan(fields=(ReprPlan.Field(name='config_id', kw_only=True, fn=None), ReprPlan.Field(name='session_i"
        "d', kw_only=True, fn=None), ReprPlan.Field(name='value', kw_only=True, fn=None), ReprPlan.Field(name='meta', k"
        "w_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='bc589d12fd76d2fd5ecf5ba8c187885152142509',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'SetSessionConfigOptionRequest'),
    ),
)
def _process_dataclass__bc589d12fd76d2fd5ecf5ba8c187885152142509():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
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
                config_id=self.config_id,
                session_id=self.session_id,
                value=self.value,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.config_id == other.config_id and
                self.session_id == other.session_id and
                self.value == other.value and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'config_id',
            'session_id',
            'value',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'config_id',
            'session_id',
            'value',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.config_id,
                self.session_id,
                self.value,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            config_id: __dataclass__init__fields__0__annotation,
            session_id: __dataclass__init__fields__1__annotation,
            value: __dataclass__init__fields__2__annotation,
            meta: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'config_id', config_id)
            __dataclass__object_setattr(self, 'session_id', session_id)
            __dataclass__object_setattr(self, 'value', value)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"config_id={self.config_id!r}")
            parts.append(f"session_id={self.session_id!r}")
            parts.append(f"value={self.value!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('mode_id', 'session_id', 'meta')), EqPlan(fields=('mode_id', 'session_id', 'meta')"
        "), FrozenPlan(fields=('mode_id', 'session_id', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='ad"
        "d', fields=('mode_id', 'session_id', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='mode_id', an"
        "notation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False"
        ", field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='session_id"
        "', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override="
        "False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='meta'"
        ", annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_fact"
        "ory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=Non"
        "e)), self_param='self', std_params=(), kw_only_params=('mode_id', 'session_id', 'meta'), frozen=True, slots=Fa"
        "lse, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='mode_id', kw_"
        "only=True, fn=None), ReprPlan.Field(name='session_id', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_"
        "only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='2363afd9c48e9b7a99ffdfd776f0f8f14c30b3a7',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'SetSessionModeRequest'),
    ),
)
def _process_dataclass__2363afd9c48e9b7a99ffdfd776f0f8f14c30b3a7():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
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
                mode_id=self.mode_id,
                session_id=self.session_id,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.mode_id == other.mode_id and
                self.session_id == other.session_id and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'mode_id',
            'session_id',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'mode_id',
            'session_id',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.mode_id,
                self.session_id,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            mode_id: __dataclass__init__fields__0__annotation,
            session_id: __dataclass__init__fields__1__annotation,
            meta: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'mode_id', mode_id)
            __dataclass__object_setattr(self, 'session_id', session_id)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"mode_id={self.mode_id!r}")
            parts.append(f"session_id={self.session_id!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('exit_code', 'signal', 'meta')), EqPlan(fields=('exit_code', 'signal', 'meta')), F"
        "rozenPlan(fields=('exit_code', 'signal', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fi"
        "elds=('exit_code', 'signal', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='exit_code', annotati"
        "on=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'), default_factory=None, "
        "init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPl"
        "an.Field(name='signal', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.d"
        "efault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validat"
        "e=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.2.annotation'), defau"
        "lt=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType."
        "INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('ex"
        "it_code', 'signal', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), R"
        "eprPlan(fields=(ReprPlan.Field(name='exit_code', kw_only=True, fn=None), ReprPlan.Field(name='signal', kw_only"
        "=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), id=False, terse=False, default_fn=None))"
        ")"
    ),
    plan_repr_sha1='fe849c8247eedf27a219d81352351103c7fb8cab',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'TerminalExitStatus'),
        ('ommlds.specs.acp.protocol', 'WaitForTerminalExitResponse'),
    ),
)
def _process_dataclass__fe849c8247eedf27a219d81352351103c7fb8cab():
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
                exit_code=self.exit_code,
                signal=self.signal,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.exit_code == other.exit_code and
                self.signal == other.signal and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'exit_code',
            'signal',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'exit_code',
            'signal',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.exit_code,
                self.signal,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            exit_code: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            signal: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            meta: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'exit_code', exit_code)
            __dataclass__object_setattr(self, 'signal', signal)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"exit_code={self.exit_code!r}")
            parts.append(f"signal={self.signal!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('output', 'truncated', 'exit_status', 'meta')), EqPlan(fields=('output', 'truncate"
        "d', 'exit_status', 'meta')), FrozenPlan(fields=('output', 'truncated', 'exit_status', 'meta'), allow_dynamic_d"
        "under_attrs=False), HashPlan(action='add', fields=('output', 'truncated', 'exit_status', 'meta'), cache=False)"
        ", InitPlan(fields=(InitPlan.Field(name='output', annotation=OpRef(name='init.fields.0.annotation'), default=No"
        "ne, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None"
        ", check_type=None), InitPlan.Field(name='truncated', annotation=OpRef(name='init.fields.1.annotation'), defaul"
        "t=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate="
        "None, check_type=None), InitPlan.Field(name='exit_status', annotation=OpRef(name='init.fields.2.annotation'), "
        "default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=Field"
        "Type.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name"
        "='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, ov"
        "erride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self',"
        " std_params=(), kw_only_params=('output', 'truncated', 'exit_status', 'meta'), frozen=True, slots=False, post_"
        "init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='output', kw_only=True, "
        "fn=None), ReprPlan.Field(name='truncated', kw_only=True, fn=None), ReprPlan.Field(name='exit_status', kw_only="
        "True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='eaca5140d86cc5520f91c11e4852a56232b27a66',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'TerminalOutputResponse'),
    ),
)
def _process_dataclass__eaca5140d86cc5520f91c11e4852a56232b27a66():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
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
                output=self.output,
                truncated=self.truncated,
                exit_status=self.exit_status,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.output == other.output and
                self.truncated == other.truncated and
                self.exit_status == other.exit_status and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'output',
            'truncated',
            'exit_status',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'output',
            'truncated',
            'exit_status',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.output,
                self.truncated,
                self.exit_status,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            output: __dataclass__init__fields__0__annotation,
            truncated: __dataclass__init__fields__1__annotation,
            exit_status: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            meta: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'output', output)
            __dataclass__object_setattr(self, 'truncated', truncated)
            __dataclass__object_setattr(self, 'exit_status', exit_status)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"output={self.output!r}")
            parts.append(f"truncated={self.truncated!r}")
            parts.append(f"exit_status={self.exit_status!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('terminal_id', 'type', 'meta')), EqPlan(fields=('terminal_id', 'type', 'meta')), F"
        "rozenPlan(fields=('terminal_id', 'type', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fi"
        "elds=('terminal_id', 'type', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='terminal_id', annota"
        "tion=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, fi"
        "eld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='type', annotat"
        "ion=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None,"
        " init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitP"
        "lan.Field(name='meta', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.de"
        "fault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate"
        "=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('terminal_id', 'type', 'meta'), fr"
        "ozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field("
        "name='terminal_id', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), id=False, ter"
        "se=False, default_fn=None)))"
    ),
    plan_repr_sha1='f96581d6ee0b2d7b21a64893a5c3b685394440e5',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'TerminalToolCallContent'),
    ),
)
def _process_dataclass__f96581d6ee0b2d7b21a64893a5c3b685394440e5():
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
                terminal_id=self.terminal_id,
                type=self.type,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.terminal_id == other.terminal_id and
                self.type == other.type and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'terminal_id',
            'type',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'terminal_id',
            'type',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.terminal_id,
                self.type,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            terminal_id: __dataclass__init__fields__0__annotation,
            type: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            meta: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'terminal_id', terminal_id)
            __dataclass__object_setattr(self, 'type', type)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"terminal_id={self.terminal_id!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('text', 'annotations', 'meta')), EqPlan(fields=('text', 'annotations', 'meta')), F"
        "rozenPlan(fields=('text', 'annotations', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fi"
        "elds=('text', 'annotations', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='text', annotation=Op"
        "Ref(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_typ"
        "e=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='annotations', annotat"
        "ion=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None,"
        " init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitP"
        "lan.Field(name='meta', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.de"
        "fault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate"
        "=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('text', 'annotations', 'meta'), fr"
        "ozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field("
        "name='text', kw_only=True, fn=None), ReprPlan.Field(name='annotations', kw_only=True, fn=None), ReprPlan.Field"
        "(name='meta', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='d92dd2fa1df8c425c285f314f2b949d5f5cd49d8',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'TextContent'),
    ),
)
def _process_dataclass__d92dd2fa1df8c425c285f314f2b949d5f5cd49d8():
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
                text=self.text,
                annotations=self.annotations,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.text == other.text and
                self.annotations == other.annotations and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'text',
            'annotations',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'text',
            'annotations',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.text,
                self.annotations,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            text: __dataclass__init__fields__0__annotation,
            annotations: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            meta: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'text', text)
            __dataclass__object_setattr(self, 'annotations', annotations)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"text={self.text!r}")
            parts.append(f"annotations={self.annotations!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('text', 'type', 'annotations', 'meta')), EqPlan(fields=('text', 'type', 'annotatio"
        "ns', 'meta')), FrozenPlan(fields=('text', 'type', 'annotations', 'meta'), allow_dynamic_dunder_attrs=False), H"
        "ashPlan(action='add', fields=('text', 'type', 'annotations', 'meta'), cache=False), InitPlan(fields=(InitPlan."
        "Field(name='text', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init"
        "=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.F"
        "ield(name='type', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default"
        "'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None"
        ", check_type=None), InitPlan.Field(name='annotations', annotation=OpRef(name='init.fields.2.annotation'), defa"
        "ult=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType"
        ".INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='in"
        "it.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, overri"
        "de=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std"
        "_params=(), kw_only_params=('text', 'type', 'annotations', 'meta'), frozen=True, slots=False, post_init_params"
        "=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='text', kw_only=True, fn=None), Rep"
        "rPlan.Field(name='annotations', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), i"
        "d=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='b74e5bfc5758c1ddb6d9766e30f9271a1fed73ac',
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
        ('ommlds.specs.acp.protocol', 'TextContentBlock'),
    ),
)
def _process_dataclass__b74e5bfc5758c1ddb6d9766e30f9271a1fed73ac():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
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
                text=self.text,
                type=self.type,
                annotations=self.annotations,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.text == other.text and
                self.type == other.type and
                self.annotations == other.annotations and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'text',
            'type',
            'annotations',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'text',
            'type',
            'annotations',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.text,
                self.type,
                self.annotations,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            text: __dataclass__init__fields__0__annotation,
            type: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            annotations: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            meta: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'text', text)
            __dataclass__object_setattr(self, 'type', type)
            __dataclass__object_setattr(self, 'annotations', annotations)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"text={self.text!r}")
            parts.append(f"annotations={self.annotations!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('text', 'uri', 'mime_type', 'meta')), EqPlan(fields=('text', 'uri', 'mime_type', '"
        "meta')), FrozenPlan(fields=('text', 'uri', 'mime_type', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(a"
        "ction='add', fields=('text', 'uri', 'mime_type', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='"
        "text', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, overr"
        "ide=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='u"
        "ri', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, overrid"
        "e=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='mim"
        "e_type', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), defau"
        "lt_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_t"
        "ype=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='"
        "init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerc"
        "e=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('text', 'uri', 'mi"
        "me_type', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fi"
        "elds=(ReprPlan.Field(name='text', kw_only=True, fn=None), ReprPlan.Field(name='uri', kw_only=True, fn=None), R"
        "eprPlan.Field(name='mime_type', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), i"
        "d=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='3fc8183553f9245f169fbdecdfe57eee98302ad0',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'TextResourceContents'),
    ),
)
def _process_dataclass__3fc8183553f9245f169fbdecdfe57eee98302ad0():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
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
                text=self.text,
                uri=self.uri,
                mime_type=self.mime_type,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.text == other.text and
                self.uri == other.uri and
                self.mime_type == other.mime_type and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'text',
            'uri',
            'mime_type',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'text',
            'uri',
            'mime_type',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.text,
                self.uri,
                self.mime_type,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            text: __dataclass__init__fields__0__annotation,
            uri: __dataclass__init__fields__1__annotation,
            mime_type: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            meta: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'text', text)
            __dataclass__object_setattr(self, 'uri', uri)
            __dataclass__object_setattr(self, 'mime_type', mime_type)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"text={self.text!r}")
            parts.append(f"uri={self.uri!r}")
            parts.append(f"mime_type={self.mime_type!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('title', 'tool_call_id', 'content', 'kind', 'locations', 'raw_input', 'raw_output'"
        ", 'status', 'meta')), EqPlan(fields=('title', 'tool_call_id', 'content', 'kind', 'locations', 'raw_input', 'ra"
        "w_output', 'status', 'meta')), FrozenPlan(fields=('title', 'tool_call_id', 'content', 'kind', 'locations', 'ra"
        "w_input', 'raw_output', 'status', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('"
        "title', 'tool_call_id', 'content', 'kind', 'locations', 'raw_input', 'raw_output', 'status', 'meta'), cache=Fa"
        "lse), InitPlan(fields=(InitPlan.Field(name='title', annotation=OpRef(name='init.fields.0.annotation'), default"
        "=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=N"
        "one, check_type=None), InitPlan.Field(name='tool_call_id', annotation=OpRef(name='init.fields.1.annotation'), "
        "default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, val"
        "idate=None, check_type=None), InitPlan.Field(name='content', annotation=OpRef(name='init.fields.2.annotation')"
        ", default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=Fie"
        "ldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='kind', annotation=OpRef(na"
        "me='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, "
        "override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(na"
        "me='locations', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default')"
        ", default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, "
        "check_type=None), InitPlan.Field(name='raw_input', annotation=OpRef(name='init.fields.5.annotation'), default="
        "OpRef(name='init.fields.5.default'), default_factory=None, init=True, override=False, field_type=FieldType.INS"
        "TANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='raw_output', annotation=OpRef(name='"
        "init.fields.6.annotation'), default=OpRef(name='init.fields.6.default'), default_factory=None, init=True, over"
        "ride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='"
        "status', annotation=OpRef(name='init.fields.7.annotation'), default=OpRef(name='init.fields.7.default'), defau"
        "lt_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_t"
        "ype=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.8.annotation'), default=OpRef(name='"
        "init.fields.8.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerc"
        "e=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('title', 'tool_cal"
        "l_id', 'content', 'kind', 'locations', 'raw_input', 'raw_output', 'status', 'meta'), frozen=True, slots=False,"
        " post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='title', kw_only=T"
        "rue, fn=None), ReprPlan.Field(name='tool_call_id', kw_only=True, fn=None), ReprPlan.Field(name='content', kw_o"
        "nly=True, fn=None), ReprPlan.Field(name='kind', kw_only=True, fn=None), ReprPlan.Field(name='locations', kw_on"
        "ly=True, fn=None), ReprPlan.Field(name='raw_input', kw_only=True, fn=None), ReprPlan.Field(name='raw_output', "
        "kw_only=True, fn=None), ReprPlan.Field(name='status', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_o"
        "nly=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='0898549135baf4847922e41b67a2ca8751a84700',
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
        ('ommlds.specs.acp.protocol', 'ToolCall'),
    ),
)
def _process_dataclass__0898549135baf4847922e41b67a2ca8751a84700():
    def _process_dataclass(
        *,
        __class__,
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
                title=self.title,
                tool_call_id=self.tool_call_id,
                content=self.content,
                kind=self.kind,
                locations=self.locations,
                raw_input=self.raw_input,
                raw_output=self.raw_output,
                status=self.status,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.title == other.title and
                self.tool_call_id == other.tool_call_id and
                self.content == other.content and
                self.kind == other.kind and
                self.locations == other.locations and
                self.raw_input == other.raw_input and
                self.raw_output == other.raw_output and
                self.status == other.status and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'title',
            'tool_call_id',
            'content',
            'kind',
            'locations',
            'raw_input',
            'raw_output',
            'status',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'title',
            'tool_call_id',
            'content',
            'kind',
            'locations',
            'raw_input',
            'raw_output',
            'status',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.title,
                self.tool_call_id,
                self.content,
                self.kind,
                self.locations,
                self.raw_input,
                self.raw_output,
                self.status,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            title: __dataclass__init__fields__0__annotation,
            tool_call_id: __dataclass__init__fields__1__annotation,
            content: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            kind: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            locations: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            raw_input: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
            raw_output: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
            status: __dataclass__init__fields__7__annotation = __dataclass__init__fields__7__default,
            meta: __dataclass__init__fields__8__annotation = __dataclass__init__fields__8__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'title', title)
            __dataclass__object_setattr(self, 'tool_call_id', tool_call_id)
            __dataclass__object_setattr(self, 'content', content)
            __dataclass__object_setattr(self, 'kind', kind)
            __dataclass__object_setattr(self, 'locations', locations)
            __dataclass__object_setattr(self, 'raw_input', raw_input)
            __dataclass__object_setattr(self, 'raw_output', raw_output)
            __dataclass__object_setattr(self, 'status', status)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"title={self.title!r}")
            parts.append(f"tool_call_id={self.tool_call_id!r}")
            parts.append(f"content={self.content!r}")
            parts.append(f"kind={self.kind!r}")
            parts.append(f"locations={self.locations!r}")
            parts.append(f"raw_input={self.raw_input!r}")
            parts.append(f"raw_output={self.raw_output!r}")
            parts.append(f"status={self.status!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('path', 'line', 'meta')), EqPlan(fields=('path', 'line', 'meta')), FrozenPlan(fiel"
        "ds=('path', 'line', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('path', 'line',"
        " 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='path', annotation=OpRef(name='init.fields.0.anno"
        "tation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce"
        "=None, validate=None, check_type=None), InitPlan.Field(name='line', annotation=OpRef(name='init.fields.1.annot"
        "ation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_t"
        "ype=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='meta', annotation=O"
        "pRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init"
        "=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_para"
        "m='self', std_params=(), kw_only_params=('path', 'line', 'meta'), frozen=True, slots=False, post_init_params=N"
        "one, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='path', kw_only=True, fn=None), ReprP"
        "lan.Field(name='line', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), id=False, "
        "terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='1d850d56797ecc52123ba805c7fa0e35599c10db',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'ToolCallLocation'),
    ),
)
def _process_dataclass__1d850d56797ecc52123ba805c7fa0e35599c10db():
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
                path=self.path,
                line=self.line,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.path == other.path and
                self.line == other.line and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'path',
            'line',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'path',
            'line',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.path,
                self.line,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            path: __dataclass__init__fields__0__annotation,
            line: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            meta: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'path', path)
            __dataclass__object_setattr(self, 'line', line)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"path={self.path!r}")
            parts.append(f"line={self.line!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('title', 'tool_call_id', 'session_update', 'content', 'kind', 'locations', 'raw_in"
        "put', 'raw_output', 'status', 'meta')), EqPlan(fields=('title', 'tool_call_id', 'session_update', 'content', '"
        "kind', 'locations', 'raw_input', 'raw_output', 'status', 'meta')), FrozenPlan(fields=('title', 'tool_call_id',"
        " 'session_update', 'content', 'kind', 'locations', 'raw_input', 'raw_output', 'status', 'meta'), allow_dynamic"
        "_dunder_attrs=False), HashPlan(action='add', fields=('title', 'tool_call_id', 'session_update', 'content', 'ki"
        "nd', 'locations', 'raw_input', 'raw_output', 'status', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field("
        "name='title', annotation=OpRef(name='init.fields.00.annotation'), default=None, default_factory=None, init=Tru"
        "e, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field"
        "(name='tool_call_id', annotation=OpRef(name='init.fields.01.annotation'), default=None, default_factory=None, "
        "init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPl"
        "an.Field(name='session_update', annotation=OpRef(name='init.fields.02.annotation'), default=OpRef(name='init.f"
        "ields.02.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=Non"
        "e, validate=None, check_type=None), InitPlan.Field(name='content', annotation=OpRef(name='init.fields.03.annot"
        "ation'), default=OpRef(name='init.fields.03.default'), default_factory=None, init=True, override=False, field_"
        "type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='kind', annotation="
        "OpRef(name='init.fields.04.annotation'), default=OpRef(name='init.fields.04.default'), default_factory=None, i"
        "nit=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPla"
        "n.Field(name='locations', annotation=OpRef(name='init.fields.05.annotation'), default=OpRef(name='init.fields."
        "05.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, val"
        "idate=None, check_type=None), InitPlan.Field(name='raw_input', annotation=OpRef(name='init.fields.06.annotatio"
        "n'), default=OpRef(name='init.fields.06.default'), default_factory=None, init=True, override=False, field_type"
        "=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='raw_output', annotatio"
        "n=OpRef(name='init.fields.07.annotation'), default=OpRef(name='init.fields.07.default'), default_factory=None,"
        " init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitP"
        "lan.Field(name='status', annotation=OpRef(name='init.fields.08.annotation'), default=OpRef(name='init.fields.0"
        "8.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, vali"
        "date=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.09.annotation'), d"
        "efault=OpRef(name='init.fields.09.default'), default_factory=None, init=True, override=False, field_type=Field"
        "Type.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params"
        "=('title', 'tool_call_id', 'session_update', 'content', 'kind', 'locations', 'raw_input', 'raw_output', 'statu"
        "s', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=("
        "ReprPlan.Field(name='title', kw_only=True, fn=None), ReprPlan.Field(name='tool_call_id', kw_only=True, fn=None"
        "), ReprPlan.Field(name='content', kw_only=True, fn=None), ReprPlan.Field(name='kind', kw_only=True, fn=None), "
        "ReprPlan.Field(name='locations', kw_only=True, fn=None), ReprPlan.Field(name='raw_input', kw_only=True, fn=Non"
        "e), ReprPlan.Field(name='raw_output', kw_only=True, fn=None), ReprPlan.Field(name='status', kw_only=True, fn=N"
        "one), ReprPlan.Field(name='meta', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='0fa8cf010c6b08cf530bea02be919dbdae2c9d5f',
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
        ('ommlds.specs.acp.protocol', 'ToolCallSessionUpdate'),
    ),
)
def _process_dataclass__0fa8cf010c6b08cf530bea02be919dbdae2c9d5f():
    def _process_dataclass(
        *,
        __class__,
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
                title=self.title,
                tool_call_id=self.tool_call_id,
                session_update=self.session_update,
                content=self.content,
                kind=self.kind,
                locations=self.locations,
                raw_input=self.raw_input,
                raw_output=self.raw_output,
                status=self.status,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.title == other.title and
                self.tool_call_id == other.tool_call_id and
                self.session_update == other.session_update and
                self.content == other.content and
                self.kind == other.kind and
                self.locations == other.locations and
                self.raw_input == other.raw_input and
                self.raw_output == other.raw_output and
                self.status == other.status and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'title',
            'tool_call_id',
            'session_update',
            'content',
            'kind',
            'locations',
            'raw_input',
            'raw_output',
            'status',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'title',
            'tool_call_id',
            'session_update',
            'content',
            'kind',
            'locations',
            'raw_input',
            'raw_output',
            'status',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.title,
                self.tool_call_id,
                self.session_update,
                self.content,
                self.kind,
                self.locations,
                self.raw_input,
                self.raw_output,
                self.status,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            title: __dataclass__init__fields__00__annotation,
            tool_call_id: __dataclass__init__fields__01__annotation,
            session_update: __dataclass__init__fields__02__annotation = __dataclass__init__fields__02__default,
            content: __dataclass__init__fields__03__annotation = __dataclass__init__fields__03__default,
            kind: __dataclass__init__fields__04__annotation = __dataclass__init__fields__04__default,
            locations: __dataclass__init__fields__05__annotation = __dataclass__init__fields__05__default,
            raw_input: __dataclass__init__fields__06__annotation = __dataclass__init__fields__06__default,
            raw_output: __dataclass__init__fields__07__annotation = __dataclass__init__fields__07__default,
            status: __dataclass__init__fields__08__annotation = __dataclass__init__fields__08__default,
            meta: __dataclass__init__fields__09__annotation = __dataclass__init__fields__09__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'title', title)
            __dataclass__object_setattr(self, 'tool_call_id', tool_call_id)
            __dataclass__object_setattr(self, 'session_update', session_update)
            __dataclass__object_setattr(self, 'content', content)
            __dataclass__object_setattr(self, 'kind', kind)
            __dataclass__object_setattr(self, 'locations', locations)
            __dataclass__object_setattr(self, 'raw_input', raw_input)
            __dataclass__object_setattr(self, 'raw_output', raw_output)
            __dataclass__object_setattr(self, 'status', status)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"title={self.title!r}")
            parts.append(f"tool_call_id={self.tool_call_id!r}")
            parts.append(f"content={self.content!r}")
            parts.append(f"kind={self.kind!r}")
            parts.append(f"locations={self.locations!r}")
            parts.append(f"raw_input={self.raw_input!r}")
            parts.append(f"raw_output={self.raw_output!r}")
            parts.append(f"status={self.status!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('tool_call_id', 'content', 'kind', 'locations', 'raw_input', 'raw_output', 'status"
        "', 'title', 'meta')), EqPlan(fields=('tool_call_id', 'content', 'kind', 'locations', 'raw_input', 'raw_output'"
        ", 'status', 'title', 'meta')), FrozenPlan(fields=('tool_call_id', 'content', 'kind', 'locations', 'raw_input',"
        " 'raw_output', 'status', 'title', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('"
        "tool_call_id', 'content', 'kind', 'locations', 'raw_input', 'raw_output', 'status', 'title', 'meta'), cache=Fa"
        "lse), InitPlan(fields=(InitPlan.Field(name='tool_call_id', annotation=OpRef(name='init.fields.0.annotation'), "
        "default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, val"
        "idate=None, check_type=None), InitPlan.Field(name='content', annotation=OpRef(name='init.fields.1.annotation')"
        ", default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=Fie"
        "ldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='kind', annotation=OpRef(na"
        "me='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, "
        "override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(na"
        "me='locations', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default')"
        ", default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, "
        "check_type=None), InitPlan.Field(name='raw_input', annotation=OpRef(name='init.fields.4.annotation'), default="
        "OpRef(name='init.fields.4.default'), default_factory=None, init=True, override=False, field_type=FieldType.INS"
        "TANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='raw_output', annotation=OpRef(name='"
        "init.fields.5.annotation'), default=OpRef(name='init.fields.5.default'), default_factory=None, init=True, over"
        "ride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='"
        "status', annotation=OpRef(name='init.fields.6.annotation'), default=OpRef(name='init.fields.6.default'), defau"
        "lt_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_t"
        "ype=None), InitPlan.Field(name='title', annotation=OpRef(name='init.fields.7.annotation'), default=OpRef(name="
        "'init.fields.7.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coer"
        "ce=None, validate=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.8.ann"
        "otation'), default=OpRef(name='init.fields.8.default'), default_factory=None, init=True, override=False, field"
        "_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_"
        "only_params=('tool_call_id', 'content', 'kind', 'locations', 'raw_input', 'raw_output', 'status', 'title', 'me"
        "ta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPla"
        "n.Field(name='tool_call_id', kw_only=True, fn=None), ReprPlan.Field(name='content', kw_only=True, fn=None), Re"
        "prPlan.Field(name='kind', kw_only=True, fn=None), ReprPlan.Field(name='locations', kw_only=True, fn=None), Rep"
        "rPlan.Field(name='raw_input', kw_only=True, fn=None), ReprPlan.Field(name='raw_output', kw_only=True, fn=None)"
        ", ReprPlan.Field(name='status', kw_only=True, fn=None), ReprPlan.Field(name='title', kw_only=True, fn=None), R"
        "eprPlan.Field(name='meta', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='6f5cf08e9766f1ae72397e340be20a5e76f99121',
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
        '__dataclass__init__fields__8__annotation',
        '__dataclass__init__fields__8__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'ToolCallUpdate'),
    ),
)
def _process_dataclass__6f5cf08e9766f1ae72397e340be20a5e76f99121():
    def _process_dataclass(
        *,
        __class__,
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
        __dataclass__init__fields__8__annotation,
        __dataclass__init__fields__8__default,
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
                tool_call_id=self.tool_call_id,
                content=self.content,
                kind=self.kind,
                locations=self.locations,
                raw_input=self.raw_input,
                raw_output=self.raw_output,
                status=self.status,
                title=self.title,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.tool_call_id == other.tool_call_id and
                self.content == other.content and
                self.kind == other.kind and
                self.locations == other.locations and
                self.raw_input == other.raw_input and
                self.raw_output == other.raw_output and
                self.status == other.status and
                self.title == other.title and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'tool_call_id',
            'content',
            'kind',
            'locations',
            'raw_input',
            'raw_output',
            'status',
            'title',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'tool_call_id',
            'content',
            'kind',
            'locations',
            'raw_input',
            'raw_output',
            'status',
            'title',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.tool_call_id,
                self.content,
                self.kind,
                self.locations,
                self.raw_input,
                self.raw_output,
                self.status,
                self.title,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            tool_call_id: __dataclass__init__fields__0__annotation,
            content: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            kind: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            locations: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            raw_input: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            raw_output: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
            status: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
            title: __dataclass__init__fields__7__annotation = __dataclass__init__fields__7__default,
            meta: __dataclass__init__fields__8__annotation = __dataclass__init__fields__8__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'tool_call_id', tool_call_id)
            __dataclass__object_setattr(self, 'content', content)
            __dataclass__object_setattr(self, 'kind', kind)
            __dataclass__object_setattr(self, 'locations', locations)
            __dataclass__object_setattr(self, 'raw_input', raw_input)
            __dataclass__object_setattr(self, 'raw_output', raw_output)
            __dataclass__object_setattr(self, 'status', status)
            __dataclass__object_setattr(self, 'title', title)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"tool_call_id={self.tool_call_id!r}")
            parts.append(f"content={self.content!r}")
            parts.append(f"kind={self.kind!r}")
            parts.append(f"locations={self.locations!r}")
            parts.append(f"raw_input={self.raw_input!r}")
            parts.append(f"raw_output={self.raw_output!r}")
            parts.append(f"status={self.status!r}")
            parts.append(f"title={self.title!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('tool_call_id', 'session_update', 'content', 'kind', 'locations', 'raw_input', 'ra"
        "w_output', 'status', 'title', 'meta')), EqPlan(fields=('tool_call_id', 'session_update', 'content', 'kind', 'l"
        "ocations', 'raw_input', 'raw_output', 'status', 'title', 'meta')), FrozenPlan(fields=('tool_call_id', 'session"
        "_update', 'content', 'kind', 'locations', 'raw_input', 'raw_output', 'status', 'title', 'meta'), allow_dynamic"
        "_dunder_attrs=False), HashPlan(action='add', fields=('tool_call_id', 'session_update', 'content', 'kind', 'loc"
        "ations', 'raw_input', 'raw_output', 'status', 'title', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field("
        "name='tool_call_id', annotation=OpRef(name='init.fields.00.annotation'), default=None, default_factory=None, i"
        "nit=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPla"
        "n.Field(name='session_update', annotation=OpRef(name='init.fields.01.annotation'), default=OpRef(name='init.fi"
        "elds.01.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None"
        ", validate=None, check_type=None), InitPlan.Field(name='content', annotation=OpRef(name='init.fields.02.annota"
        "tion'), default=OpRef(name='init.fields.02.default'), default_factory=None, init=True, override=False, field_t"
        "ype=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='kind', annotation=O"
        "pRef(name='init.fields.03.annotation'), default=OpRef(name='init.fields.03.default'), default_factory=None, in"
        "it=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan"
        ".Field(name='locations', annotation=OpRef(name='init.fields.04.annotation'), default=OpRef(name='init.fields.0"
        "4.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, vali"
        "date=None, check_type=None), InitPlan.Field(name='raw_input', annotation=OpRef(name='init.fields.05.annotation"
        "'), default=OpRef(name='init.fields.05.default'), default_factory=None, init=True, override=False, field_type="
        "FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='raw_output', annotation"
        "=OpRef(name='init.fields.06.annotation'), default=OpRef(name='init.fields.06.default'), default_factory=None, "
        "init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPl"
        "an.Field(name='status', annotation=OpRef(name='init.fields.07.annotation'), default=OpRef(name='init.fields.07"
        ".default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valid"
        "ate=None, check_type=None), InitPlan.Field(name='title', annotation=OpRef(name='init.fields.08.annotation'), d"
        "efault=OpRef(name='init.fields.08.default'), default_factory=None, init=True, override=False, field_type=Field"
        "Type.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name"
        "='init.fields.09.annotation'), default=OpRef(name='init.fields.09.default'), default_factory=None, init=True, "
        "override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self"
        "', std_params=(), kw_only_params=('tool_call_id', 'session_update', 'content', 'kind', 'locations', 'raw_input"
        "', 'raw_output', 'status', 'title', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), val"
        "idate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='tool_call_id', kw_only=True, fn=None), ReprPlan.Field(nam"
        "e='content', kw_only=True, fn=None), ReprPlan.Field(name='kind', kw_only=True, fn=None), ReprPlan.Field(name='"
        "locations', kw_only=True, fn=None), ReprPlan.Field(name='raw_input', kw_only=True, fn=None), ReprPlan.Field(na"
        "me='raw_output', kw_only=True, fn=None), ReprPlan.Field(name='status', kw_only=True, fn=None), ReprPlan.Field("
        "name='title', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), id=False, terse=Fal"
        "se, default_fn=None)))"
    ),
    plan_repr_sha1='38fa643486bd36d80327b6c196c32b6b909f00b3',
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
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'ToolCallUpdateSessionUpdate'),
    ),
)
def _process_dataclass__38fa643486bd36d80327b6c196c32b6b909f00b3():
    def _process_dataclass(
        *,
        __class__,
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
                tool_call_id=self.tool_call_id,
                session_update=self.session_update,
                content=self.content,
                kind=self.kind,
                locations=self.locations,
                raw_input=self.raw_input,
                raw_output=self.raw_output,
                status=self.status,
                title=self.title,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.tool_call_id == other.tool_call_id and
                self.session_update == other.session_update and
                self.content == other.content and
                self.kind == other.kind and
                self.locations == other.locations and
                self.raw_input == other.raw_input and
                self.raw_output == other.raw_output and
                self.status == other.status and
                self.title == other.title and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'tool_call_id',
            'session_update',
            'content',
            'kind',
            'locations',
            'raw_input',
            'raw_output',
            'status',
            'title',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'tool_call_id',
            'session_update',
            'content',
            'kind',
            'locations',
            'raw_input',
            'raw_output',
            'status',
            'title',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.tool_call_id,
                self.session_update,
                self.content,
                self.kind,
                self.locations,
                self.raw_input,
                self.raw_output,
                self.status,
                self.title,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            tool_call_id: __dataclass__init__fields__00__annotation,
            session_update: __dataclass__init__fields__01__annotation = __dataclass__init__fields__01__default,
            content: __dataclass__init__fields__02__annotation = __dataclass__init__fields__02__default,
            kind: __dataclass__init__fields__03__annotation = __dataclass__init__fields__03__default,
            locations: __dataclass__init__fields__04__annotation = __dataclass__init__fields__04__default,
            raw_input: __dataclass__init__fields__05__annotation = __dataclass__init__fields__05__default,
            raw_output: __dataclass__init__fields__06__annotation = __dataclass__init__fields__06__default,
            status: __dataclass__init__fields__07__annotation = __dataclass__init__fields__07__default,
            title: __dataclass__init__fields__08__annotation = __dataclass__init__fields__08__default,
            meta: __dataclass__init__fields__09__annotation = __dataclass__init__fields__09__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'tool_call_id', tool_call_id)
            __dataclass__object_setattr(self, 'session_update', session_update)
            __dataclass__object_setattr(self, 'content', content)
            __dataclass__object_setattr(self, 'kind', kind)
            __dataclass__object_setattr(self, 'locations', locations)
            __dataclass__object_setattr(self, 'raw_input', raw_input)
            __dataclass__object_setattr(self, 'raw_output', raw_output)
            __dataclass__object_setattr(self, 'status', status)
            __dataclass__object_setattr(self, 'title', title)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"tool_call_id={self.tool_call_id!r}")
            parts.append(f"content={self.content!r}")
            parts.append(f"kind={self.kind!r}")
            parts.append(f"locations={self.locations!r}")
            parts.append(f"raw_input={self.raw_input!r}")
            parts.append(f"raw_output={self.raw_output!r}")
            parts.append(f"status={self.status!r}")
            parts.append(f"title={self.title!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('hint', 'meta')), EqPlan(fields=('hint', 'meta')), FrozenPlan(fields=('hint', 'met"
        "a'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('hint', 'meta'), cache=False), InitPlan"
        "(fields=(InitPlan.Field(name='hint', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_"
        "factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type"
        "=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='ini"
        "t.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=N"
        "one, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('hint', 'meta'), froz"
        "en=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(na"
        "me='hint', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), id=False, terse=False,"
        " default_fn=None)))"
    ),
    plan_repr_sha1='9780bcc164a6000cf084d03c5e966a83c49f074d',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'UnstructuredCommandInput'),
    ),
)
def _process_dataclass__9780bcc164a6000cf084d03c5e966a83c49f074d():
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
                hint=self.hint,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.hint == other.hint and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'hint',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'hint',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.hint,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            hint: __dataclass__init__fields__0__annotation,
            meta: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'hint', hint)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"hint={self.hint!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('content', 'path', 'session_id', 'meta')), EqPlan(fields=('content', 'path', 'sess"
        "ion_id', 'meta')), FrozenPlan(fields=('content', 'path', 'session_id', 'meta'), allow_dynamic_dunder_attrs=Fal"
        "se), HashPlan(action='add', fields=('content', 'path', 'session_id', 'meta'), cache=False), InitPlan(fields=(I"
        "nitPlan.Field(name='content', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory"
        "=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),"
        " InitPlan.Field(name='path', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory="
        "None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), "
        "InitPlan.Field(name='session_id', annotation=OpRef(name='init.fields.2.annotation'), default=None, default_fac"
        "tory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=No"
        "ne), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.f"
        "ields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None"
        ", validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('content', 'path', 'sess"
        "ion_id', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fie"
        "lds=(ReprPlan.Field(name='content', kw_only=True, fn=None), ReprPlan.Field(name='path', kw_only=True, fn=None)"
        ", ReprPlan.Field(name='session_id', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)"
        "), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='af72e6356b5595eaae40793b6dd5328138c5abb3',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ommlds.specs.acp.protocol', 'WriteTextFileRequest'),
    ),
)
def _process_dataclass__af72e6356b5595eaae40793b6dd5328138c5abb3():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__2__annotation,
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
                content=self.content,
                path=self.path,
                session_id=self.session_id,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.content == other.content and
                self.path == other.path and
                self.session_id == other.session_id and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'content',
            'path',
            'session_id',
            'meta',
        }

        def __setattr__(self, name, value):
            if (
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

        __dataclass___delattr_frozen_fields = {
            'content',
            'path',
            'session_id',
            'meta',
        }

        def __delattr__(self, name):
            if (
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.content,
                self.path,
                self.session_id,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            content: __dataclass__init__fields__0__annotation,
            path: __dataclass__init__fields__1__annotation,
            session_id: __dataclass__init__fields__2__annotation,
            meta: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'content', content)
            __dataclass__object_setattr(self, 'path', path)
            __dataclass__object_setattr(self, 'session_id', session_id)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"content={self.content!r}")
            parts.append(f"path={self.path!r}")
            parts.append(f"session_id={self.session_id!r}")
            parts.append(f"meta={self.meta!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass
