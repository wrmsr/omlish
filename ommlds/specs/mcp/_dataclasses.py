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
        "Plans(tup=(CopyPlan(fields=('audience', 'last_modified', 'priority')), EqPlan(fields=('audience', 'last_modifi"
        "ed', 'priority')), FrozenPlan(fields=('audience', 'last_modified', 'priority'), allow_dynamic_dunder_attrs=Fal"
        "se), HashPlan(action='add', fields=('audience', 'last_modified', 'priority'), cache=False), InitPlan(fields=(I"
        "nitPlan.Field(name='audience', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fie"
        "lds.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, "
        "validate=None, check_type=None), InitPlan.Field(name='last_modified', annotation=OpRef(name='init.fields.1.ann"
        "otation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field"
        "_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='priority', annota"
        "tion=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None"
        ", init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), sel"
        "f_param='self', std_params=(), kw_only_params=('audience', 'last_modified', 'priority'), frozen=True, slots=Fa"
        "lse, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='audience', kw"
        "_only=True, fn=None), ReprPlan.Field(name='last_modified', kw_only=True, fn=None), ReprPlan.Field(name='priori"
        "ty', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='e7e073505602ad6fb0c906edee22c19316202e38',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'Annotations'),
    ),
)
def _process_dataclass__e7e073505602ad6fb0c906edee22c19316202e38():
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
                audience=self.audience,
                last_modified=self.last_modified,
                priority=self.priority,
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
                self.priority == other.priority
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'audience',
            'last_modified',
            'priority',
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
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            audience: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            last_modified: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            priority: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'audience', audience)
            __dataclass__object_setattr(self, 'last_modified', last_modified)
            __dataclass__object_setattr(self, 'priority', priority)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"audience={self.audience!r}")
            parts.append(f"last_modified={self.last_modified!r}")
            parts.append(f"priority={self.priority!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('data', 'mime_type', 'annotations', 'type', 'meta')), EqPlan(fields=('data', 'mime"
        "_type', 'annotations', 'type', 'meta')), FrozenPlan(fields=('data', 'mime_type', 'annotations', 'type', 'meta'"
        "), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('data', 'mime_type', 'annotations', 'type"
        "', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='data', annotation=OpRef(name='init.fields.0.an"
        "notation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coer"
        "ce=None, validate=None, check_type=None), InitPlan.Field(name='mime_type', annotation=OpRef(name='init.fields."
        "1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, "
        "coerce=None, validate=None, check_type=None), InitPlan.Field(name='annotations', annotation=OpRef(name='init.f"
        "ields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=F"
        "alse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='type',"
        " annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_facto"
        "ry=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None"
        "), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fie"
        "lds.4.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, "
        "validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('data', 'mime_type', 'anno"
        "tations', 'type', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), Rep"
        "rPlan(fields=(ReprPlan.Field(name='data', kw_only=True, fn=None), ReprPlan.Field(name='mime_type', kw_only=Tru"
        "e, fn=None), ReprPlan.Field(name='annotations', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=Tr"
        "ue, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='8bc2fca36896ec5d9c1d572771a9b7e8234bd269',
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
        ('ommlds.specs.mcp.protocol', 'AudioContent'),
        ('ommlds.specs.mcp.protocol', 'ImageContent'),
    ),
)
def _process_dataclass__8bc2fca36896ec5d9c1d572771a9b7e8234bd269():
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
                self.data == other.data and
                self.mime_type == other.mime_type and
                self.annotations == other.annotations and
                self.type == other.type and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'data',
            'mime_type',
            'annotations',
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
            'data',
            'mime_type',
            'annotations',
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
                self.data,
                self.mime_type,
                self.annotations,
                self.type,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            data: __dataclass__init__fields__0__annotation,
            mime_type: __dataclass__init__fields__1__annotation,
            annotations: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            type: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            meta: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'data', data)
            __dataclass__object_setattr(self, 'mime_type', mime_type)
            __dataclass__object_setattr(self, 'annotations', annotations)
            __dataclass__object_setattr(self, 'type', type)
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
        "Plans(tup=(CopyPlan(fields=('name', 'title')), EqPlan(fields=('name', 'title')), FrozenPlan(fields=('name', 't"
        "itle'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('name', 'title'), cache=False), Init"
        "Plan(fields=(InitPlan.Field(name='name', annotation=OpRef(name='init.fields.0.annotation'), default=None, defa"
        "ult_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_"
        "type=None), InitPlan.Field(name='title', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name"
        "='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coe"
        "rce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('name', 'title')"
        ", frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Fi"
        "eld(name='name', kw_only=True, fn=None), ReprPlan.Field(name='title', kw_only=True, fn=None)), id=False, terse"
        "=False, default_fn=None)))"
    ),
    plan_repr_sha1='bd3748b60506e533f5a1c3395b6fd5bda4039d84',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'BaseMetadata'),
    ),
)
def _process_dataclass__bd3748b60506e533f5a1c3395b6fd5bda4039d84():
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
                name=self.name,
                title=self.title,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.name == other.name and
                self.title == other.title
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'name',
            'title',
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
            'title',
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
                self.title,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            name: __dataclass__init__fields__0__annotation,
            title: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'title', title)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"name={self.name!r}")
            parts.append(f"title={self.title!r}")
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
        ('ommlds.specs.mcp.protocol', 'BlobResourceContents'),
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
        "Plans(tup=(CopyPlan(fields=('default', 'description', 'title', 'type')), EqPlan(fields=('default', 'descriptio"
        "n', 'title', 'type')), FrozenPlan(fields=('default', 'description', 'title', 'type'), allow_dynamic_dunder_att"
        "rs=False), HashPlan(action='add', fields=('default', 'description', 'title', 'type'), cache=False), InitPlan(f"
        "ields=(InitPlan.Field(name='default', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='i"
        "nit.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce"
        "=None, validate=None, check_type=None), InitPlan.Field(name='description', annotation=OpRef(name='init.fields."
        "1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, "
        "field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='title', anno"
        "tation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=No"
        "ne, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), In"
        "itPlan.Field(name='type', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3"
        ".default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valid"
        "ate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('default', 'description', 'titl"
        "e', 'type'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=("
        "ReprPlan.Field(name='default', kw_only=True, fn=None), ReprPlan.Field(name='description', kw_only=True, fn=Non"
        "e), ReprPlan.Field(name='title', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='00e70aad2841a557afa43c4a5cdb6e50bf09f90f',
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
        ('ommlds.specs.mcp.protocol', 'BooleanSchema'),
    ),
)
def _process_dataclass__00e70aad2841a557afa43c4a5cdb6e50bf09f90f():
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
                default=self.default,
                description=self.description,
                title=self.title,
                type=self.type,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.default == other.default and
                self.description == other.description and
                self.title == other.title and
                self.type == other.type
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'default',
            'description',
            'title',
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
            'default',
            'description',
            'title',
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
                self.default,
                self.description,
                self.title,
                self.type,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            default: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            description: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            title: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            type: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'default', default)
            __dataclass__object_setattr(self, 'description', description)
            __dataclass__object_setattr(self, 'title', title)
            __dataclass__object_setattr(self, 'type', type)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"default={self.default!r}")
            parts.append(f"description={self.description!r}")
            parts.append(f"title={self.title!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('params', 'method')), EqPlan(fields=('params', 'method')), FrozenPlan(fields=('par"
        "ams', 'method'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('params', 'method'), cache="
        "False), InitPlan(fields=(InitPlan.Field(name='params', annotation=OpRef(name='init.fields.0.annotation'), defa"
        "ult=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validat"
        "e=None, check_type=None), InitPlan.Field(name='method', annotation=OpRef(name='init.fields.1.annotation'), def"
        "ault=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldTyp"
        "e.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('"
        "params', 'method'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(f"
        "ields=(ReprPlan.Field(name='params', kw_only=True, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='7c54754743ec92b4871184490a7ce2c8e15737f9',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'CallToolRequest'),
        ('ommlds.specs.mcp.protocol', 'CancelledNotification'),
        ('ommlds.specs.mcp.protocol', 'CompleteRequest'),
        ('ommlds.specs.mcp.protocol', 'CreateMessageRequest'),
        ('ommlds.specs.mcp.protocol', 'ElicitRequest'),
        ('ommlds.specs.mcp.protocol', 'GetPromptRequest'),
        ('ommlds.specs.mcp.protocol', 'InitializeRequest'),
        ('ommlds.specs.mcp.protocol', 'LoggingMessageNotification'),
        ('ommlds.specs.mcp.protocol', 'ProgressNotification'),
        ('ommlds.specs.mcp.protocol', 'ReadResourceRequest'),
        ('ommlds.specs.mcp.protocol', 'ResourceUpdatedNotification'),
        ('ommlds.specs.mcp.protocol', 'SetLevelRequest'),
        ('ommlds.specs.mcp.protocol', 'SubscribeRequest'),
        ('ommlds.specs.mcp.protocol', 'UnsubscribeRequest'),
    ),
)
def _process_dataclass__7c54754743ec92b4871184490a7ce2c8e15737f9():
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
                params=self.params,
                method=self.method,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.params == other.params and
                self.method == other.method
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'params',
            'method',
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
            'params',
            'method',
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
                self.params,
                self.method,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            params: __dataclass__init__fields__0__annotation,
            method: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'params', params)
            __dataclass__object_setattr(self, 'method', method)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
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
        "Plans(tup=(CopyPlan(fields=('name', 'arguments')), EqPlan(fields=('name', 'arguments')), FrozenPlan(fields=('n"
        "ame', 'arguments'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('name', 'arguments'), ca"
        "che=False), InitPlan(fields=(InitPlan.Field(name='name', annotation=OpRef(name='init.fields.0.annotation'), de"
        "fault=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valid"
        "ate=None, check_type=None), InitPlan.Field(name='arguments', annotation=OpRef(name='init.fields.1.annotation')"
        ", default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=Fie"
        "ldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_para"
        "ms=('name', 'arguments'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), Repr"
        "Plan(fields=(ReprPlan.Field(name='name', kw_only=True, fn=None), ReprPlan.Field(name='arguments', kw_only=True"
        ", fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='0826e4dc808ea4d3d1b2de8f4865f4255c3b8547',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'CallToolRequest.Params'),
        ('ommlds.specs.mcp.protocol', 'GetPromptRequest.Params'),
    ),
)
def _process_dataclass__0826e4dc808ea4d3d1b2de8f4865f4255c3b8547():
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
                name=self.name,
                arguments=self.arguments,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.name == other.name and
                self.arguments == other.arguments
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'name',
            'arguments',
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
            'arguments',
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
                self.arguments,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            name: __dataclass__init__fields__0__annotation,
            arguments: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'arguments', arguments)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

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

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('content', 'is_error', 'structured_content', 'meta')), EqPlan(fields=('content', '"
        "is_error', 'structured_content', 'meta')), FrozenPlan(fields=('content', 'is_error', 'structured_content', 'me"
        "ta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('content', 'is_error', 'structured_con"
        "tent', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='content', annotation=OpRef(name='init.fiel"
        "ds.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANC"
        "E, coerce=None, validate=None, check_type=None), InitPlan.Field(name='is_error', annotation=OpRef(name='init.f"
        "ields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=F"
        "alse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='struct"
        "ured_content', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'),"
        " default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, c"
        "heck_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef("
        "name='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE,"
        " coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('content', '"
        "is_error', 'structured_content', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), valida"
        "te_fns=()), ReprPlan(fields=(ReprPlan.Field(name='content', kw_only=True, fn=None), ReprPlan.Field(name='is_er"
        "ror', kw_only=True, fn=None), ReprPlan.Field(name='structured_content', kw_only=True, fn=None), ReprPlan.Field"
        "(name='meta', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='11d71320cdf675b4e9bc1ab89e85ea3ebe677e73',
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
        ('ommlds.specs.mcp.protocol', 'CallToolResult'),
    ),
)
def _process_dataclass__11d71320cdf675b4e9bc1ab89e85ea3ebe677e73():
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
                content=self.content,
                is_error=self.is_error,
                structured_content=self.structured_content,
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
                self.is_error == other.is_error and
                self.structured_content == other.structured_content and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'content',
            'is_error',
            'structured_content',
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
            'is_error',
            'structured_content',
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
                self.is_error,
                self.structured_content,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            content: __dataclass__init__fields__0__annotation,
            is_error: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            structured_content: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            meta: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'content', content)
            __dataclass__object_setattr(self, 'is_error', is_error)
            __dataclass__object_setattr(self, 'structured_content', structured_content)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"content={self.content!r}")
            parts.append(f"is_error={self.is_error!r}")
            parts.append(f"structured_content={self.structured_content!r}")
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
        "Plans(tup=(CopyPlan(fields=('request_id', 'reason')), EqPlan(fields=('request_id', 'reason')), FrozenPlan(fiel"
        "ds=('request_id', 'reason'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('request_id', '"
        "reason'), cache=False), InitPlan(fields=(InitPlan.Field(name='request_id', annotation=OpRef(name='init.fields."
        "0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, "
        "coerce=None, validate=None, check_type=None), InitPlan.Field(name='reason', annotation=OpRef(name='init.fields"
        ".1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False,"
        " field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=("
        "), kw_only_params=('request_id', 'reason'), frozen=True, slots=False, post_init_params=None, init_fns=(), vali"
        "date_fns=()), ReprPlan(fields=(ReprPlan.Field(name='request_id', kw_only=True, fn=None), ReprPlan.Field(name='"
        "reason', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='2496559b30977d739fa350baf8824086dc1aa15a',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'CancelledNotification.Params'),
    ),
)
def _process_dataclass__2496559b30977d739fa350baf8824086dc1aa15a():
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
                request_id=self.request_id,
                reason=self.reason,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.request_id == other.request_id and
                self.reason == other.reason
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'request_id',
            'reason',
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
            'request_id',
            'reason',
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
                self.request_id,
                self.reason,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            request_id: __dataclass__init__fields__0__annotation,
            reason: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'request_id', request_id)
            __dataclass__object_setattr(self, 'reason', reason)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"request_id={self.request_id!r}")
            parts.append(f"reason={self.reason!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

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
        ('ommlds.specs.mcp.protocol', 'ClientCapabilities'),
        ('ommlds.specs.mcp.protocolold', 'ClientCapabilities'),
    ),
)
def _process_dataclass__170da6364b7625208100edb082d6e5c1dfa008cf():
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
                elicitation=self.elicitation,
                experimental=self.experimental,
                roots=self.roots,
                sampling=self.sampling,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

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

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'elicitation',
            'experimental',
            'roots',
            'sampling',
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
            'elicitation',
            'experimental',
            'roots',
            'sampling',
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
                self.elicitation,
                self.experimental,
                self.roots,
                self.sampling,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

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

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

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

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

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
        ('ommlds.specs.mcp.protocol', 'ClientCapabilities.Roots'),
        ('ommlds.specs.mcp.protocol', 'ServerCapabilities.Prompts'),
        ('ommlds.specs.mcp.protocol', 'ServerCapabilities.Tools'),
        ('ommlds.specs.mcp.protocolold', 'ClientCapabilities.Roots'),
        ('ommlds.specs.mcp.protocolold', 'ServerCapabilities.Prompts'),
        ('ommlds.specs.mcp.protocolold', 'ServerCapabilities.Tools'),
    ),
)
def _process_dataclass__d78dfa0a1b3d36442ff997752e3282d062066773():
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
                list_changed=self.list_changed,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.list_changed == other.list_changed
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'list_changed',
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
            'list_changed',
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
                self.list_changed,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            list_changed: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'list_changed', list_changed)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"list_changed={self.list_changed!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('argument', 'ref', 'context')), EqPlan(fields=('argument', 'ref', 'context')), Fro"
        "zenPlan(fields=('argument', 'ref', 'context'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', field"
        "s=('argument', 'ref', 'context'), cache=False), InitPlan(fields=(InitPlan.Field(name='argument', annotation=Op"
        "Ref(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_typ"
        "e=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='ref', annotation=OpRe"
        "f(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type="
        "FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='context', annotation=Op"
        "Ref(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init="
        "True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param"
        "='self', std_params=(), kw_only_params=('argument', 'ref', 'context'), frozen=True, slots=False, post_init_par"
        "ams=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='argument', kw_only=True, fn=Non"
        "e), ReprPlan.Field(name='ref', kw_only=True, fn=None), ReprPlan.Field(name='context', kw_only=True, fn=None)),"
        " id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='54477abb572d5cc21b4af950216f46aa0187a8cf',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'CompleteRequest.Params'),
    ),
)
def _process_dataclass__54477abb572d5cc21b4af950216f46aa0187a8cf():
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
                argument=self.argument,
                ref=self.ref,
                context=self.context,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.argument == other.argument and
                self.ref == other.ref and
                self.context == other.context
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'argument',
            'ref',
            'context',
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
            'argument',
            'ref',
            'context',
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
                self.argument,
                self.ref,
                self.context,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            argument: __dataclass__init__fields__0__annotation,
            ref: __dataclass__init__fields__1__annotation,
            context: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'argument', argument)
            __dataclass__object_setattr(self, 'ref', ref)
            __dataclass__object_setattr(self, 'context', context)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"argument={self.argument!r}")
            parts.append(f"ref={self.ref!r}")
            parts.append(f"context={self.context!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('name', 'value')), EqPlan(fields=('name', 'value')), FrozenPlan(fields=('name', 'v"
        "alue'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('name', 'value'), cache=False), Init"
        "Plan(fields=(InitPlan.Field(name='name', annotation=OpRef(name='init.fields.0.annotation'), default=None, defa"
        "ult_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_"
        "type=None), InitPlan.Field(name='value', annotation=OpRef(name='init.fields.1.annotation'), default=None, defa"
        "ult_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_"
        "type=None)), self_param='self', std_params=(), kw_only_params=('name', 'value'), frozen=True, slots=False, pos"
        "t_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='name', kw_only=True, "
        "fn=None), ReprPlan.Field(name='value', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='fa4b84852a3b44f975d22b16bd1bc5a71d6d2697',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'CompleteRequest.Params.Argument'),
    ),
)
def _process_dataclass__fa4b84852a3b44f975d22b16bd1bc5a71d6d2697():
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
                name=self.name,
                value=self.value,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.name == other.name and
                self.value == other.value
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'name',
            'value',
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
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            name: __dataclass__init__fields__0__annotation,
            value: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'value', value)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"name={self.name!r}")
            parts.append(f"value={self.value!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('arguments',)), EqPlan(fields=('arguments',)), FrozenPlan(fields=('arguments',), a"
        "llow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('arguments',), cache=False), InitPlan(fields="
        "(InitPlan.Field(name='arguments', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init."
        "fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=Non"
        "e, validate=None, check_type=None),), self_param='self', std_params=(), kw_only_params=('arguments',), frozen="
        "True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name="
        "'arguments', kw_only=True, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='94d4ff7c88c45a0052fe981979fc04c5a7eaed46',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'CompleteRequest.Params.Context'),
    ),
)
def _process_dataclass__94d4ff7c88c45a0052fe981979fc04c5a7eaed46():
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
                arguments=self.arguments,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.arguments == other.arguments
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'arguments',
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
            'arguments',
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
                self.arguments,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            arguments: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'arguments', arguments)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"arguments={self.arguments!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('completion', 'meta')), EqPlan(fields=('completion', 'meta')), FrozenPlan(fields=("
        "'completion', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('completion', 'meta')"
        ", cache=False), InitPlan(fields=(InitPlan.Field(name='completion', annotation=OpRef(name='init.fields.0.annota"
        "tion'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=N"
        "one, validate=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.1.annotat"
        "ion'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_typ"
        "e=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only"
        "_params=('completion', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=())"
        ", ReprPlan(fields=(ReprPlan.Field(name='completion', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_on"
        "ly=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='96dba9ce96c263a334e485b056977bc8fe339fb1',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'CompleteResult'),
    ),
)
def _process_dataclass__96dba9ce96c263a334e485b056977bc8fe339fb1():
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
                completion=self.completion,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.completion == other.completion and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'completion',
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
            'completion',
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
                self.completion,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            completion: __dataclass__init__fields__0__annotation,
            meta: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'completion', completion)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"completion={self.completion!r}")
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
        "Plans(tup=(CopyPlan(fields=('values', 'has_more', 'total')), EqPlan(fields=('values', 'has_more', 'total')), F"
        "rozenPlan(fields=('values', 'has_more', 'total'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fi"
        "elds=('values', 'has_more', 'total'), cache=False), InitPlan(fields=(InitPlan.Field(name='values', annotation="
        "OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_t"
        "ype=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='has_more', annotati"
        "on=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, "
        "init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPl"
        "an.Field(name='total', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.de"
        "fault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate"
        "=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('values', 'has_more', 'total'), fr"
        "ozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field("
        "name='values', kw_only=True, fn=None), ReprPlan.Field(name='has_more', kw_only=True, fn=None), ReprPlan.Field("
        "name='total', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='86219a5ebea8edd08269a34346c7b252dbfdc171',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'CompleteResult.Completion'),
    ),
)
def _process_dataclass__86219a5ebea8edd08269a34346c7b252dbfdc171():
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
                values=self.values,
                has_more=self.has_more,
                total=self.total,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.values == other.values and
                self.has_more == other.has_more and
                self.total == other.total
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'values',
            'has_more',
            'total',
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
            'values',
            'has_more',
            'total',
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
                self.values,
                self.has_more,
                self.total,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            values: __dataclass__init__fields__0__annotation,
            has_more: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            total: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'values', values)
            __dataclass__object_setattr(self, 'has_more', has_more)
            __dataclass__object_setattr(self, 'total', total)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"values={self.values!r}")
            parts.append(f"has_more={self.has_more!r}")
            parts.append(f"total={self.total!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('max_tokens', 'messages', 'include_context', 'metadata', 'model_preferences', 'sto"
        "p_sequences', 'system_prompt', 'temperature')), EqPlan(fields=('max_tokens', 'messages', 'include_context', 'm"
        "etadata', 'model_preferences', 'stop_sequences', 'system_prompt', 'temperature')), FrozenPlan(fields=('max_tok"
        "ens', 'messages', 'include_context', 'metadata', 'model_preferences', 'stop_sequences', 'system_prompt', 'temp"
        "erature'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('max_tokens', 'messages', 'includ"
        "e_context', 'metadata', 'model_preferences', 'stop_sequences', 'system_prompt', 'temperature'), cache=False), "
        "InitPlan(fields=(InitPlan.Field(name='max_tokens', annotation=OpRef(name='init.fields.0.annotation'), default="
        "None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=No"
        "ne, check_type=None), InitPlan.Field(name='messages', annotation=OpRef(name='init.fields.1.annotation'), defau"
        "lt=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate"
        "=None, check_type=None), InitPlan.Field(name='include_context', annotation=OpRef(name='init.fields.2.annotatio"
        "n'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_type="
        "FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='metadata', annotation=O"
        "pRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init"
        "=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.F"
        "ield(name='model_preferences', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fie"
        "lds.4.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, "
        "validate=None, check_type=None), InitPlan.Field(name='stop_sequences', annotation=OpRef(name='init.fields.5.an"
        "notation'), default=OpRef(name='init.fields.5.default'), default_factory=None, init=True, override=False, fiel"
        "d_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='system_prompt', "
        "annotation=OpRef(name='init.fields.6.annotation'), default=OpRef(name='init.fields.6.default'), default_factor"
        "y=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)"
        ", InitPlan.Field(name='temperature', annotation=OpRef(name='init.fields.7.annotation'), default=OpRef(name='in"
        "it.fields.7.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce="
        "None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('max_tokens', 'messa"
        "ges', 'include_context', 'metadata', 'model_preferences', 'stop_sequences', 'system_prompt', 'temperature'), f"
        "rozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field"
        "(name='max_tokens', kw_only=True, fn=None), ReprPlan.Field(name='messages', kw_only=True, fn=None), ReprPlan.F"
        "ield(name='include_context', kw_only=True, fn=None), ReprPlan.Field(name='metadata', kw_only=True, fn=None), R"
        "eprPlan.Field(name='model_preferences', kw_only=True, fn=None), ReprPlan.Field(name='stop_sequences', kw_only="
        "True, fn=None), ReprPlan.Field(name='system_prompt', kw_only=True, fn=None), ReprPlan.Field(name='temperature'"
        ", kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='f348d1c2b4c68d8a5f863d2d0726bcc1a10a345a',
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
        ('ommlds.specs.mcp.protocol', 'CreateMessageRequest.Params'),
    ),
)
def _process_dataclass__f348d1c2b4c68d8a5f863d2d0726bcc1a10a345a():
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
                max_tokens=self.max_tokens,
                messages=self.messages,
                include_context=self.include_context,
                metadata=self.metadata,
                model_preferences=self.model_preferences,
                stop_sequences=self.stop_sequences,
                system_prompt=self.system_prompt,
                temperature=self.temperature,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.max_tokens == other.max_tokens and
                self.messages == other.messages and
                self.include_context == other.include_context and
                self.metadata == other.metadata and
                self.model_preferences == other.model_preferences and
                self.stop_sequences == other.stop_sequences and
                self.system_prompt == other.system_prompt and
                self.temperature == other.temperature
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'max_tokens',
            'messages',
            'include_context',
            'metadata',
            'model_preferences',
            'stop_sequences',
            'system_prompt',
            'temperature',
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
            'max_tokens',
            'messages',
            'include_context',
            'metadata',
            'model_preferences',
            'stop_sequences',
            'system_prompt',
            'temperature',
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
                self.max_tokens,
                self.messages,
                self.include_context,
                self.metadata,
                self.model_preferences,
                self.stop_sequences,
                self.system_prompt,
                self.temperature,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            max_tokens: __dataclass__init__fields__0__annotation,
            messages: __dataclass__init__fields__1__annotation,
            include_context: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            metadata: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            model_preferences: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            stop_sequences: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
            system_prompt: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
            temperature: __dataclass__init__fields__7__annotation = __dataclass__init__fields__7__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'max_tokens', max_tokens)
            __dataclass__object_setattr(self, 'messages', messages)
            __dataclass__object_setattr(self, 'include_context', include_context)
            __dataclass__object_setattr(self, 'metadata', metadata)
            __dataclass__object_setattr(self, 'model_preferences', model_preferences)
            __dataclass__object_setattr(self, 'stop_sequences', stop_sequences)
            __dataclass__object_setattr(self, 'system_prompt', system_prompt)
            __dataclass__object_setattr(self, 'temperature', temperature)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"max_tokens={self.max_tokens!r}")
            parts.append(f"messages={self.messages!r}")
            parts.append(f"include_context={self.include_context!r}")
            parts.append(f"metadata={self.metadata!r}")
            parts.append(f"model_preferences={self.model_preferences!r}")
            parts.append(f"stop_sequences={self.stop_sequences!r}")
            parts.append(f"system_prompt={self.system_prompt!r}")
            parts.append(f"temperature={self.temperature!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('content', 'model', 'role', 'stop_reason', 'meta')), EqPlan(fields=('content', 'mo"
        "del', 'role', 'stop_reason', 'meta')), FrozenPlan(fields=('content', 'model', 'role', 'stop_reason', 'meta'), "
        "allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('content', 'model', 'role', 'stop_reason', '"
        "meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='content', annotation=OpRef(name='init.fields.0.ann"
        "otation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerc"
        "e=None, validate=None, check_type=None), InitPlan.Field(name='model', annotation=OpRef(name='init.fields.1.ann"
        "otation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerc"
        "e=None, validate=None, check_type=None), InitPlan.Field(name='role', annotation=OpRef(name='init.fields.2.anno"
        "tation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce"
        "=None, validate=None, check_type=None), InitPlan.Field(name='stop_reason', annotation=OpRef(name='init.fields."
        "3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, "
        "field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='meta', annot"
        "ation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_factory=Non"
        "e, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), se"
        "lf_param='self', std_params=(), kw_only_params=('content', 'model', 'role', 'stop_reason', 'meta'), frozen=Tru"
        "e, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='co"
        "ntent', kw_only=True, fn=None), ReprPlan.Field(name='model', kw_only=True, fn=None), ReprPlan.Field(name='role"
        "', kw_only=True, fn=None), ReprPlan.Field(name='stop_reason', kw_only=True, fn=None), ReprPlan.Field(name='met"
        "a', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='e912102995951e0d4e6f2ca6c87afef7998dbaa1',
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
        ('ommlds.specs.mcp.protocol', 'CreateMessageResult'),
    ),
)
def _process_dataclass__e912102995951e0d4e6f2ca6c87afef7998dbaa1():
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
                content=self.content,
                model=self.model,
                role=self.role,
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
                self.content == other.content and
                self.model == other.model and
                self.role == other.role and
                self.stop_reason == other.stop_reason and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'content',
            'model',
            'role',
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
            'content',
            'model',
            'role',
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
                self.content,
                self.model,
                self.role,
                self.stop_reason,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            content: __dataclass__init__fields__0__annotation,
            model: __dataclass__init__fields__1__annotation,
            role: __dataclass__init__fields__2__annotation,
            stop_reason: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            meta: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'content', content)
            __dataclass__object_setattr(self, 'model', model)
            __dataclass__object_setattr(self, 'role', role)
            __dataclass__object_setattr(self, 'stop_reason', stop_reason)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"content={self.content!r}")
            parts.append(f"model={self.model!r}")
            parts.append(f"role={self.role!r}")
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
        "Plans(tup=(CopyPlan(fields=('message', 'requested_schema')), EqPlan(fields=('message', 'requested_schema')), F"
        "rozenPlan(fields=('message', 'requested_schema'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fi"
        "elds=('message', 'requested_schema'), cache=False), InitPlan(fields=(InitPlan.Field(name='message', annotation"
        "=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_"
        "type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='requested_schema',"
        " annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=Fa"
        "lse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_para"
        "ms=(), kw_only_params=('message', 'requested_schema'), frozen=True, slots=False, post_init_params=None, init_f"
        "ns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='message', kw_only=True, fn=None), ReprPlan.Fiel"
        "d(name='requested_schema', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='6e6e51bf59cbf0cf2581169a0255e152c5e3eea8',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'ElicitRequest.Params'),
    ),
)
def _process_dataclass__6e6e51bf59cbf0cf2581169a0255e152c5e3eea8():
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
                message=self.message,
                requested_schema=self.requested_schema,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.message == other.message and
                self.requested_schema == other.requested_schema
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'message',
            'requested_schema',
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
            'message',
            'requested_schema',
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
                self.message,
                self.requested_schema,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            message: __dataclass__init__fields__0__annotation,
            requested_schema: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'message', message)
            __dataclass__object_setattr(self, 'requested_schema', requested_schema)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"message={self.message!r}")
            parts.append(f"requested_schema={self.requested_schema!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('properties', 'required', 'type')), EqPlan(fields=('properties', 'required', 'type"
        "')), FrozenPlan(fields=('properties', 'required', 'type'), allow_dynamic_dunder_attrs=False), HashPlan(action="
        "'add', fields=('properties', 'required', 'type'), cache=False), InitPlan(fields=(InitPlan.Field(name='properti"
        "es', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, overrid"
        "e=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='req"
        "uired', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), defaul"
        "t_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_ty"
        "pe=None), InitPlan.Field(name='type', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='i"
        "nit.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce"
        "=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('properties', 'requ"
        "ired', 'type'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(field"
        "s=(ReprPlan.Field(name='properties', kw_only=True, fn=None), ReprPlan.Field(name='required', kw_only=True, fn="
        "None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='2aa910ce80ff5142d53acb90eddacd79ff77e2e6',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'ElicitRequest.Params.RequestedSchema'),
    ),
)
def _process_dataclass__2aa910ce80ff5142d53acb90eddacd79ff77e2e6():
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
                properties=self.properties,
                required=self.required,
                type=self.type,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.properties == other.properties and
                self.required == other.required and
                self.type == other.type
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'properties',
            'required',
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
            'properties',
            'required',
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
                self.properties,
                self.required,
                self.type,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            properties: __dataclass__init__fields__0__annotation,
            required: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            type: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'properties', properties)
            __dataclass__object_setattr(self, 'required', required)
            __dataclass__object_setattr(self, 'type', type)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"properties={self.properties!r}")
            parts.append(f"required={self.required!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('action', 'content', 'meta')), EqPlan(fields=('action', 'content', 'meta')), Froze"
        "nPlan(fields=('action', 'content', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=("
        "'action', 'content', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='action', annotation=OpRef(na"
        "me='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=Fiel"
        "dType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='content', annotation=OpRef("
        "name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True"
        ", override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field("
        "name='meta', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), d"
        "efault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, che"
        "ck_type=None)), self_param='self', std_params=(), kw_only_params=('action', 'content', 'meta'), frozen=True, s"
        "lots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='action"
        "', kw_only=True, fn=None), ReprPlan.Field(name='content', kw_only=True, fn=None), ReprPlan.Field(name='meta', "
        "kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='32b343c804f755448196e091e71a927c554f37dd',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'ElicitResult'),
    ),
)
def _process_dataclass__32b343c804f755448196e091e71a927c554f37dd():
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
                action=self.action,
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
                self.action == other.action and
                self.content == other.content and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'action',
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
            'action',
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
                self.action,
                self.content,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            action: __dataclass__init__fields__0__annotation,
            content: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            meta: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'action', action)
            __dataclass__object_setattr(self, 'content', content)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"action={self.action!r}")
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
        "Plans(tup=(CopyPlan(fields=('resource', 'annotations', 'type', 'meta')), EqPlan(fields=('resource', 'annotatio"
        "ns', 'type', 'meta')), FrozenPlan(fields=('resource', 'annotations', 'type', 'meta'), allow_dynamic_dunder_att"
        "rs=False), HashPlan(action='add', fields=('resource', 'annotations', 'type', 'meta'), cache=False), InitPlan(f"
        "ields=(InitPlan.Field(name='resource', annotation=OpRef(name='init.fields.0.annotation'), default=None, defaul"
        "t_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_ty"
        "pe=None), InitPlan.Field(name='annotations', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef("
        "name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE,"
        " coerce=None, validate=None, check_type=None), InitPlan.Field(name='type', annotation=OpRef(name='init.fields."
        "2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, "
        "field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='meta', annot"
        "ation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=Non"
        "e, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), se"
        "lf_param='self', std_params=(), kw_only_params=('resource', 'annotations', 'type', 'meta'), frozen=True, slots"
        "=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='resource',"
        " kw_only=True, fn=None), ReprPlan.Field(name='annotations', kw_only=True, fn=None), ReprPlan.Field(name='meta'"
        ", kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='7454ece969de86d110b10ffd38beea3a9310a9e5',
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
        ('ommlds.specs.mcp.protocol', 'EmbeddedResource'),
    ),
)
def _process_dataclass__7454ece969de86d110b10ffd38beea3a9310a9e5():
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
                annotations=self.annotations,
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
                self.resource == other.resource and
                self.annotations == other.annotations and
                self.type == other.type and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'resource',
            'annotations',
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
            'resource',
            'annotations',
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
                self.resource,
                self.annotations,
                self.type,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            resource: __dataclass__init__fields__0__annotation,
            annotations: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            type: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            meta: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'resource', resource)
            __dataclass__object_setattr(self, 'annotations', annotations)
            __dataclass__object_setattr(self, 'type', type)
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
        "Plans(tup=(CopyPlan(fields=('enum', 'description', 'enum_names', 'title', 'type')), EqPlan(fields=('enum', 'de"
        "scription', 'enum_names', 'title', 'type')), FrozenPlan(fields=('enum', 'description', 'enum_names', 'title', "
        "'type'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('enum', 'description', 'enum_names'"
        ", 'title', 'type'), cache=False), InitPlan(fields=(InitPlan.Field(name='enum', annotation=OpRef(name='init.fie"
        "lds.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTAN"
        "CE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='description', annotation=OpRef(name='in"
        "it.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, overri"
        "de=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='en"
        "um_names', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), def"
        "ault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check"
        "_type=None), InitPlan.Field(name='title', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(nam"
        "e='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, co"
        "erce=None, validate=None, check_type=None), InitPlan.Field(name='type', annotation=OpRef(name='init.fields.4.a"
        "nnotation'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, override=False, fie"
        "ld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), k"
        "w_only_params=('enum', 'description', 'enum_names', 'title', 'type'), frozen=True, slots=False, post_init_para"
        "ms=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='enum', kw_only=True, fn=None), R"
        "eprPlan.Field(name='description', kw_only=True, fn=None), ReprPlan.Field(name='enum_names', kw_only=True, fn=N"
        "one), ReprPlan.Field(name='title', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='ed3f07a84fe6b716ebe14a64aa127c890e5ac175',
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
        ('ommlds.specs.mcp.protocol', 'EnumSchema'),
    ),
)
def _process_dataclass__ed3f07a84fe6b716ebe14a64aa127c890e5ac175():
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
                enum=self.enum,
                description=self.description,
                enum_names=self.enum_names,
                title=self.title,
                type=self.type,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.enum == other.enum and
                self.description == other.description and
                self.enum_names == other.enum_names and
                self.title == other.title and
                self.type == other.type
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'enum',
            'description',
            'enum_names',
            'title',
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
            'enum',
            'description',
            'enum_names',
            'title',
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
                self.enum,
                self.description,
                self.enum_names,
                self.title,
                self.type,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            enum: __dataclass__init__fields__0__annotation,
            description: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            enum_names: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            title: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            type: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'enum', enum)
            __dataclass__object_setattr(self, 'description', description)
            __dataclass__object_setattr(self, 'enum_names', enum_names)
            __dataclass__object_setattr(self, 'title', title)
            __dataclass__object_setattr(self, 'type', type)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"enum={self.enum!r}")
            parts.append(f"description={self.description!r}")
            parts.append(f"enum_names={self.enum_names!r}")
            parts.append(f"title={self.title!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('messages', 'description', 'meta')), EqPlan(fields=('messages', 'description', 'me"
        "ta')), FrozenPlan(fields=('messages', 'description', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(acti"
        "on='add', fields=('messages', 'description', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='mess"
        "ages', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, overr"
        "ide=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='d"
        "escription', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), d"
        "efault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, che"
        "ck_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(na"
        "me='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, c"
        "oerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('messages', 'd"
        "escription', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan"
        "(fields=(ReprPlan.Field(name='messages', kw_only=True, fn=None), ReprPlan.Field(name='description', kw_only=Tr"
        "ue, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='593834ff036e045c22468e46324fb0a4b8d3bc4c',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'GetPromptResult'),
    ),
)
def _process_dataclass__593834ff036e045c22468e46324fb0a4b8d3bc4c():
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
                messages=self.messages,
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
                self.messages == other.messages and
                self.description == other.description and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'messages',
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
            'messages',
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
                self.messages,
                self.description,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            messages: __dataclass__init__fields__0__annotation,
            description: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            meta: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'messages', messages)
            __dataclass__object_setattr(self, 'description', description)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"messages={self.messages!r}")
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
        "Plans(tup=(CopyPlan(fields=('name', 'version', 'title')), EqPlan(fields=('name', 'version', 'title')), FrozenP"
        "lan(fields=('name', 'version', 'title'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('na"
        "me', 'version', 'title'), cache=False), InitPlan(fields=(InitPlan.Field(name='name', annotation=OpRef(name='in"
        "it.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType."
        "INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='version', annotation=OpRef(name='"
        "init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldTyp"
        "e.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='title', annotation=OpRef(name='"
        "init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, over"
        "ride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', s"
        "td_params=(), kw_only_params=('name', 'version', 'title'), frozen=True, slots=False, post_init_params=None, in"
        "it_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='name', kw_only=True, fn=None), ReprPlan.Fie"
        "ld(name='version', kw_only=True, fn=None), ReprPlan.Field(name='title', kw_only=True, fn=None)), id=False, ter"
        "se=False, default_fn=None)))"
    ),
    plan_repr_sha1='9d97ac454146b25591e36aae91ffc5110f38cf48',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'Implementation'),
    ),
)
def _process_dataclass__9d97ac454146b25591e36aae91ffc5110f38cf48():
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
                version=self.version,
                title=self.title,
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
                self.title == other.title
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'name',
            'version',
            'title',
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
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            name: __dataclass__init__fields__0__annotation,
            version: __dataclass__init__fields__1__annotation,
            title: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'version', version)
            __dataclass__object_setattr(self, 'title', title)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"name={self.name!r}")
            parts.append(f"version={self.version!r}")
            parts.append(f"title={self.title!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('capabilities', 'client_info', 'protocol_version')), EqPlan(fields=('capabilities'"
        ", 'client_info', 'protocol_version')), FrozenPlan(fields=('capabilities', 'client_info', 'protocol_version'), "
        "allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('capabilities', 'client_info', 'protocol_ver"
        "sion'), cache=False), InitPlan(fields=(InitPlan.Field(name='capabilities', annotation=OpRef(name='init.fields."
        "0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, "
        "coerce=None, validate=None, check_type=None), InitPlan.Field(name='client_info', annotation=OpRef(name='init.f"
        "ields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INST"
        "ANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='protocol_version', annotation=OpRef(n"
        "ame='init.fields.2.annotation'), default=None, default_factory=None, init=True, override=False, field_type=Fie"
        "ldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_para"
        "ms=('capabilities', 'client_info', 'protocol_version'), frozen=True, slots=False, post_init_params=None, init_"
        "fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='capabilities', kw_only=True, fn=None), ReprPla"
        "n.Field(name='client_info', kw_only=True, fn=None), ReprPlan.Field(name='protocol_version', kw_only=True, fn=N"
        "one)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='9ca36653130f8aedf9144445d0200a36ce4e8dc7',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'InitializeRequest.Params'),
    ),
)
def _process_dataclass__9ca36653130f8aedf9144445d0200a36ce4e8dc7():
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
                capabilities=self.capabilities,
                client_info=self.client_info,
                protocol_version=self.protocol_version,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.capabilities == other.capabilities and
                self.client_info == other.client_info and
                self.protocol_version == other.protocol_version
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'capabilities',
            'client_info',
            'protocol_version',
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
            'capabilities',
            'client_info',
            'protocol_version',
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
                self.capabilities,
                self.client_info,
                self.protocol_version,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            capabilities: __dataclass__init__fields__0__annotation,
            client_info: __dataclass__init__fields__1__annotation,
            protocol_version: __dataclass__init__fields__2__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'capabilities', capabilities)
            __dataclass__object_setattr(self, 'client_info', client_info)
            __dataclass__object_setattr(self, 'protocol_version', protocol_version)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"capabilities={self.capabilities!r}")
            parts.append(f"client_info={self.client_info!r}")
            parts.append(f"protocol_version={self.protocol_version!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('capabilities', 'protocol_version', 'server_info', 'instructions', 'meta')), EqPla"
        "n(fields=('capabilities', 'protocol_version', 'server_info', 'instructions', 'meta')), FrozenPlan(fields=('cap"
        "abilities', 'protocol_version', 'server_info', 'instructions', 'meta'), allow_dynamic_dunder_attrs=False), Has"
        "hPlan(action='add', fields=('capabilities', 'protocol_version', 'server_info', 'instructions', 'meta'), cache="
        "False), InitPlan(fields=(InitPlan.Field(name='capabilities', annotation=OpRef(name='init.fields.0.annotation')"
        ", default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, v"
        "alidate=None, check_type=None), InitPlan.Field(name='protocol_version', annotation=OpRef(name='init.fields.1.a"
        "nnotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coe"
        "rce=None, validate=None, check_type=None), InitPlan.Field(name='server_info', annotation=OpRef(name='init.fiel"
        "ds.2.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANC"
        "E, coerce=None, validate=None, check_type=None), InitPlan.Field(name='instructions', annotation=OpRef(name='in"
        "it.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, overri"
        "de=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='me"
        "ta', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_f"
        "actory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type="
        "None)), self_param='self', std_params=(), kw_only_params=('capabilities', 'protocol_version', 'server_info', '"
        "instructions', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPl"
        "an(fields=(ReprPlan.Field(name='capabilities', kw_only=True, fn=None), ReprPlan.Field(name='protocol_version',"
        " kw_only=True, fn=None), ReprPlan.Field(name='server_info', kw_only=True, fn=None), ReprPlan.Field(name='instr"
        "uctions', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), id=False, terse=False, "
        "default_fn=None)))"
    ),
    plan_repr_sha1='69db64334198503eed389c75c9f3f4866c3b3c1f',
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
        ('ommlds.specs.mcp.protocol', 'InitializeResult'),
    ),
)
def _process_dataclass__69db64334198503eed389c75c9f3f4866c3b3c1f():
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
                capabilities=self.capabilities,
                protocol_version=self.protocol_version,
                server_info=self.server_info,
                instructions=self.instructions,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.capabilities == other.capabilities and
                self.protocol_version == other.protocol_version and
                self.server_info == other.server_info and
                self.instructions == other.instructions and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'capabilities',
            'protocol_version',
            'server_info',
            'instructions',
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
            'capabilities',
            'protocol_version',
            'server_info',
            'instructions',
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
                self.capabilities,
                self.protocol_version,
                self.server_info,
                self.instructions,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            capabilities: __dataclass__init__fields__0__annotation,
            protocol_version: __dataclass__init__fields__1__annotation,
            server_info: __dataclass__init__fields__2__annotation,
            instructions: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            meta: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'capabilities', capabilities)
            __dataclass__object_setattr(self, 'protocol_version', protocol_version)
            __dataclass__object_setattr(self, 'server_info', server_info)
            __dataclass__object_setattr(self, 'instructions', instructions)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"capabilities={self.capabilities!r}")
            parts.append(f"protocol_version={self.protocol_version!r}")
            parts.append(f"server_info={self.server_info!r}")
            parts.append(f"instructions={self.instructions!r}")
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
        "ult=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType"
        ".INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='params', annotation=OpRef(name='"
        "init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, over"
        "ride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', s"
        "td_params=(), kw_only_params=('method', 'params'), frozen=True, slots=False, post_init_params=None, init_fns=("
        "), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='params', kw_only=True, fn=None),), id=False, terse="
        "False, default_fn=None)))"
    ),
    plan_repr_sha1='569b85d63cc6487eee0a33485dcb811d0c9db073',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'InitializedNotification'),
        ('ommlds.specs.mcp.protocol', 'ListPromptsRequest'),
        ('ommlds.specs.mcp.protocol', 'ListResourceTemplatesRequest'),
        ('ommlds.specs.mcp.protocol', 'ListResourcesRequest'),
        ('ommlds.specs.mcp.protocol', 'ListRootsRequest'),
        ('ommlds.specs.mcp.protocol', 'ListToolsRequest'),
        ('ommlds.specs.mcp.protocol', 'PingRequest'),
        ('ommlds.specs.mcp.protocol', 'PromptListChangedNotification'),
        ('ommlds.specs.mcp.protocol', 'ResourceListChangedNotification'),
        ('ommlds.specs.mcp.protocol', 'RootsListChangedNotification'),
        ('ommlds.specs.mcp.protocol', 'ToolListChangedNotification'),
    ),
)
def _process_dataclass__569b85d63cc6487eee0a33485dcb811d0c9db073():
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
            method: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            params: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'method', method)
            __dataclass__object_setattr(self, 'params', params)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
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
        ('ommlds.specs.mcp.protocol', 'InitializedNotification.Params'),
        ('ommlds.specs.mcp.protocol', 'JSONRPCNotification.Params'),
        ('ommlds.specs.mcp.protocol', 'JSONRPCRequest.Params'),
        ('ommlds.specs.mcp.protocol', 'ListRootsRequest.Params'),
        ('ommlds.specs.mcp.protocol', 'Notification.Params'),
        ('ommlds.specs.mcp.protocol', 'PingRequest.Params'),
        ('ommlds.specs.mcp.protocol', 'PromptListChangedNotification.Params'),
        ('ommlds.specs.mcp.protocol', 'Request.Params'),
        ('ommlds.specs.mcp.protocol', 'ResourceListChangedNotification.Params'),
        ('ommlds.specs.mcp.protocol', 'Result'),
        ('ommlds.specs.mcp.protocol', 'RootsListChangedNotification.Params'),
        ('ommlds.specs.mcp.protocol', 'ToolListChangedNotification.Params'),
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
        "Plans(tup=(CopyPlan(fields=('error', 'id', 'jsonrpc')), EqPlan(fields=('error', 'id', 'jsonrpc')), FrozenPlan("
        "fields=('error', 'id', 'jsonrpc'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('error', "
        "'id', 'jsonrpc'), cache=False), InitPlan(fields=(InitPlan.Field(name='error', annotation=OpRef(name='init.fiel"
        "ds.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANC"
        "E, coerce=None, validate=None, check_type=None), InitPlan.Field(name='id', annotation=OpRef(name='init.fields."
        "1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, "
        "coerce=None, validate=None, check_type=None), InitPlan.Field(name='jsonrpc', annotation=OpRef(name='init.field"
        "s.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False"
        ", field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params="
        "(), kw_only_params=('error', 'id', 'jsonrpc'), frozen=True, slots=False, post_init_params=None, init_fns=(), v"
        "alidate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='error', kw_only=True, fn=None), ReprPlan.Field(name='id"
        "', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='de9f6517fb38896abee122948901bc5b15dec3fd',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'JSONRPCError'),
    ),
)
def _process_dataclass__de9f6517fb38896abee122948901bc5b15dec3fd():
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
                error=self.error,
                id=self.id,
                jsonrpc=self.jsonrpc,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.error == other.error and
                self.id == other.id and
                self.jsonrpc == other.jsonrpc
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'error',
            'id',
            'jsonrpc',
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
            'jsonrpc',
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
                self.jsonrpc,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            error: __dataclass__init__fields__0__annotation,
            id: __dataclass__init__fields__1__annotation,
            jsonrpc: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'error', error)
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'jsonrpc', jsonrpc)

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
        ('ommlds.specs.mcp.protocol', 'JSONRPCError.Error'),
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
        "Plans(tup=(CopyPlan(fields=('method', 'jsonrpc', 'params')), EqPlan(fields=('method', 'jsonrpc', 'params')), F"
        "rozenPlan(fields=('method', 'jsonrpc', 'params'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fi"
        "elds=('method', 'jsonrpc', 'params'), cache=False), InitPlan(fields=(InitPlan.Field(name='method', annotation="
        "OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_t"
        "ype=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='jsonrpc', annotatio"
        "n=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, i"
        "nit=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPla"
        "n.Field(name='params', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.de"
        "fault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate"
        "=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('method', 'jsonrpc', 'params'), fr"
        "ozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field("
        "name='method', kw_only=True, fn=None), ReprPlan.Field(name='params', kw_only=True, fn=None)), id=False, terse="
        "False, default_fn=None)))"
    ),
    plan_repr_sha1='41e04f82ba09f8641d2d3aa529addac5a91c3d3b',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'JSONRPCNotification'),
    ),
)
def _process_dataclass__41e04f82ba09f8641d2d3aa529addac5a91c3d3b():
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
                method=self.method,
                jsonrpc=self.jsonrpc,
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
                self.jsonrpc == other.jsonrpc and
                self.params == other.params
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'method',
            'jsonrpc',
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
            'jsonrpc',
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
                self.jsonrpc,
                self.params,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            method: __dataclass__init__fields__0__annotation,
            jsonrpc: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            params: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'method', method)
            __dataclass__object_setattr(self, 'jsonrpc', jsonrpc)
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
        "Plans(tup=(CopyPlan(fields=('id', 'method', 'jsonrpc', 'params')), EqPlan(fields=('id', 'method', 'jsonrpc', '"
        "params')), FrozenPlan(fields=('id', 'method', 'jsonrpc', 'params'), allow_dynamic_dunder_attrs=False), HashPla"
        "n(action='add', fields=('id', 'method', 'jsonrpc', 'params'), cache=False), InitPlan(fields=(InitPlan.Field(na"
        "me='id', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, ove"
        "rride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name="
        "'method', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, ov"
        "erride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name"
        "='jsonrpc', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), de"
        "fault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, chec"
        "k_type=None), InitPlan.Field(name='params', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(n"
        "ame='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, "
        "coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('id', 'method"
        "', 'jsonrpc', 'params'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprP"
        "lan(fields=(ReprPlan.Field(name='id', kw_only=True, fn=None), ReprPlan.Field(name='method', kw_only=True, fn=N"
        "one), ReprPlan.Field(name='params', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='6bc5296b50f17194f669b68537a68955b5cd67c1',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'JSONRPCRequest'),
    ),
)
def _process_dataclass__6bc5296b50f17194f669b68537a68955b5cd67c1():
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
                method=self.method,
                jsonrpc=self.jsonrpc,
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
                self.jsonrpc == other.jsonrpc and
                self.params == other.params
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'id',
            'method',
            'jsonrpc',
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
            'jsonrpc',
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
                self.jsonrpc,
                self.params,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            id: __dataclass__init__fields__0__annotation,
            method: __dataclass__init__fields__1__annotation,
            jsonrpc: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            params: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'method', method)
            __dataclass__object_setattr(self, 'jsonrpc', jsonrpc)
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
        "Plans(tup=(CopyPlan(fields=('progress_token',)), EqPlan(fields=('progress_token',)), FrozenPlan(fields=('progr"
        "ess_token',), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('progress_token',), cache=Fals"
        "e), InitPlan(fields=(InitPlan.Field(name='progress_token', annotation=OpRef(name='init.fields.0.annotation'), "
        "default=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=Field"
        "Type.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self', std_params=(), kw_only_param"
        "s=('progress_token',), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPla"
        "n(fields=(ReprPlan.Field(name='progress_token', kw_only=True, fn=None),), id=False, terse=False, default_fn=No"
        "ne)))"
    ),
    plan_repr_sha1='2eb86ba028e9a794403334d3f8779a79daf76446',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'JSONRPCRequest.Params.Meta'),
        ('ommlds.specs.mcp.protocol', 'ListRootsRequest.Params.Meta'),
        ('ommlds.specs.mcp.protocol', 'PingRequest.Params.Meta'),
        ('ommlds.specs.mcp.protocol', 'Request.Params.Meta'),
    ),
)
def _process_dataclass__2eb86ba028e9a794403334d3f8779a79daf76446():
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
                progress_token=self.progress_token,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.progress_token == other.progress_token
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'progress_token',
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
            'progress_token',
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
                self.progress_token,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            progress_token: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'progress_token', progress_token)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"progress_token={self.progress_token!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('id', 'result', 'jsonrpc')), EqPlan(fields=('id', 'result', 'jsonrpc')), FrozenPla"
        "n(fields=('id', 'result', 'jsonrpc'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('id', "
        "'result', 'jsonrpc'), cache=False), InitPlan(fields=(InitPlan.Field(name='id', annotation=OpRef(name='init.fie"
        "lds.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTAN"
        "CE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='result', annotation=OpRef(name='init.fi"
        "elds.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTA"
        "NCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='jsonrpc', annotation=OpRef(name='init."
        "fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override="
        "False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_pa"
        "rams=(), kw_only_params=('id', 'result', 'jsonrpc'), frozen=True, slots=False, post_init_params=None, init_fns"
        "=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='id', kw_only=True, fn=None), ReprPlan.Field(name="
        "'result', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='b1756ca8b1ff3a5e543d69a34384278b5bf730ce',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'JSONRPCResponse'),
    ),
)
def _process_dataclass__b1756ca8b1ff3a5e543d69a34384278b5bf730ce():
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
                result=self.result,
                jsonrpc=self.jsonrpc,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.id == other.id and
                self.result == other.result and
                self.jsonrpc == other.jsonrpc
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'id',
            'result',
            'jsonrpc',
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
            'jsonrpc',
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
                self.jsonrpc,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            id: __dataclass__init__fields__0__annotation,
            result: __dataclass__init__fields__1__annotation,
            jsonrpc: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'id', id)
            __dataclass__object_setattr(self, 'result', result)
            __dataclass__object_setattr(self, 'jsonrpc', jsonrpc)

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
        ('ommlds.specs.mcp.protocol', 'ListPromptsRequest.Params'),
        ('ommlds.specs.mcp.protocol', 'ListResourceTemplatesRequest.Params'),
        ('ommlds.specs.mcp.protocol', 'ListResourcesRequest.Params'),
        ('ommlds.specs.mcp.protocol', 'ListToolsRequest.Params'),
        ('ommlds.specs.mcp.protocol', 'PaginatedRequest.Params'),
        ('ommlds.specs.mcp.protocolold', 'CursorClientRequest'),
    ),
)
def _process_dataclass__f766093bd61562f127e07346cb0cd7c991dfe209():
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
                cursor=self.cursor,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.cursor == other.cursor
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'cursor',
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
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            cursor: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'cursor', cursor)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"cursor={self.cursor!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('prompts', 'next_cursor', 'meta')), EqPlan(fields=('prompts', 'next_cursor', 'meta"
        "')), FrozenPlan(fields=('prompts', 'next_cursor', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action="
        "'add', fields=('prompts', 'next_cursor', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='prompts'"
        ", annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=F"
        "alse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='next_c"
        "ursor', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), defaul"
        "t_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_ty"
        "pe=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='i"
        "nit.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce"
        "=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('prompts', 'next_cu"
        "rsor', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(field"
        "s=(ReprPlan.Field(name='prompts', kw_only=True, fn=None), ReprPlan.Field(name='next_cursor', kw_only=True, fn="
        "None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='1ae342b03dec1f794a463ae9523bac35cfb9f2b9',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'ListPromptsResult'),
    ),
)
def _process_dataclass__1ae342b03dec1f794a463ae9523bac35cfb9f2b9():
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
                prompts=self.prompts,
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
                self.prompts == other.prompts and
                self.next_cursor == other.next_cursor and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'prompts',
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
            'prompts',
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
                self.prompts,
                self.next_cursor,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            prompts: __dataclass__init__fields__0__annotation,
            next_cursor: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            meta: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'prompts', prompts)
            __dataclass__object_setattr(self, 'next_cursor', next_cursor)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"prompts={self.prompts!r}")
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
        "Plans(tup=(CopyPlan(fields=('resource_templates', 'next_cursor', 'meta')), EqPlan(fields=('resource_templates'"
        ", 'next_cursor', 'meta')), FrozenPlan(fields=('resource_templates', 'next_cursor', 'meta'), allow_dynamic_dund"
        "er_attrs=False), HashPlan(action='add', fields=('resource_templates', 'next_cursor', 'meta'), cache=False), In"
        "itPlan(fields=(InitPlan.Field(name='resource_templates', annotation=OpRef(name='init.fields.0.annotation'), de"
        "fault=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valid"
        "ate=None, check_type=None), InitPlan.Field(name='next_cursor', annotation=OpRef(name='init.fields.1.annotation"
        "'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=F"
        "ieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef("
        "name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True"
        ", override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='se"
        "lf', std_params=(), kw_only_params=('resource_templates', 'next_cursor', 'meta'), frozen=True, slots=False, po"
        "st_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='resource_templates',"
        " kw_only=True, fn=None), ReprPlan.Field(name='next_cursor', kw_only=True, fn=None), ReprPlan.Field(name='meta'"
        ", kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='4c5c3eb53eb9a90fed29c35a646c10e37774c651',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'ListResourceTemplatesResult'),
    ),
)
def _process_dataclass__4c5c3eb53eb9a90fed29c35a646c10e37774c651():
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
                resource_templates=self.resource_templates,
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
                self.resource_templates == other.resource_templates and
                self.next_cursor == other.next_cursor and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'resource_templates',
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
            'resource_templates',
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
                self.resource_templates,
                self.next_cursor,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            resource_templates: __dataclass__init__fields__0__annotation,
            next_cursor: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            meta: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'resource_templates', resource_templates)
            __dataclass__object_setattr(self, 'next_cursor', next_cursor)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"resource_templates={self.resource_templates!r}")
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
        "Plans(tup=(CopyPlan(fields=('resources', 'next_cursor', 'meta')), EqPlan(fields=('resources', 'next_cursor', '"
        "meta')), FrozenPlan(fields=('resources', 'next_cursor', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(a"
        "ction='add', fields=('resources', 'next_cursor', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='"
        "resources', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, "
        "override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(na"
        "me='next_cursor', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default"
        "'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None"
        ", check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.2.annotation'), default=OpR"
        "ef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTAN"
        "CE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('resource"
        "s', 'next_cursor', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), Re"
        "prPlan(fields=(ReprPlan.Field(name='resources', kw_only=True, fn=None), ReprPlan.Field(name='next_cursor', kw_"
        "only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), id=False, terse=False, default_fn=No"
        "ne)))"
    ),
    plan_repr_sha1='bbc2e0cc1a9190530489b16dd22c9d2ca324876d',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'ListResourcesResult'),
    ),
)
def _process_dataclass__bbc2e0cc1a9190530489b16dd22c9d2ca324876d():
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
                resources=self.resources,
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
                self.resources == other.resources and
                self.next_cursor == other.next_cursor and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'resources',
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
            'resources',
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
                self.resources,
                self.next_cursor,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            resources: __dataclass__init__fields__0__annotation,
            next_cursor: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            meta: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'resources', resources)
            __dataclass__object_setattr(self, 'next_cursor', next_cursor)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"resources={self.resources!r}")
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
        "Plans(tup=(CopyPlan(fields=('roots', 'meta')), EqPlan(fields=('roots', 'meta')), FrozenPlan(fields=('roots', '"
        "meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('roots', 'meta'), cache=False), Init"
        "Plan(fields=(InitPlan.Field(name='roots', annotation=OpRef(name='init.fields.0.annotation'), default=None, def"
        "ault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check"
        "_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name"
        "='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coe"
        "rce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('roots', 'meta')"
        ", frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Fi"
        "eld(name='roots', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), id=False, terse"
        "=False, default_fn=None)))"
    ),
    plan_repr_sha1='c318546bd4011b1c5ca76807c52d3770f63499aa',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'ListRootsResult'),
    ),
)
def _process_dataclass__c318546bd4011b1c5ca76807c52d3770f63499aa():
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
                roots=self.roots,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.roots == other.roots and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'roots',
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
            'roots',
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
                self.roots,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            roots: __dataclass__init__fields__0__annotation,
            meta: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'roots', roots)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"roots={self.roots!r}")
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
        "Plans(tup=(CopyPlan(fields=('tools', 'next_cursor', 'meta')), EqPlan(fields=('tools', 'next_cursor', 'meta')),"
        " FrozenPlan(fields=('tools', 'next_cursor', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add',"
        " fields=('tools', 'next_cursor', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='tools', annotati"
        "on=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, fiel"
        "d_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='next_cursor', an"
        "notation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory="
        "None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), "
        "InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields"
        ".2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, val"
        "idate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('tools', 'next_cursor', 'meta"
        "'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan."
        "Field(name='tools', kw_only=True, fn=None), ReprPlan.Field(name='next_cursor', kw_only=True, fn=None), ReprPla"
        "n.Field(name='meta', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='db514173f3c63ff671d6739eb7c1b69959eff7ae',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'ListToolsResult'),
    ),
)
def _process_dataclass__db514173f3c63ff671d6739eb7c1b69959eff7ae():
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
                tools=self.tools,
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
                self.tools == other.tools and
                self.next_cursor == other.next_cursor and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'tools',
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
            'tools',
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
                self.tools,
                self.next_cursor,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            tools: __dataclass__init__fields__0__annotation,
            next_cursor: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            meta: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'tools', tools)
            __dataclass__object_setattr(self, 'next_cursor', next_cursor)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"tools={self.tools!r}")
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
        "Plans(tup=(CopyPlan(fields=('data', 'level', 'logger')), EqPlan(fields=('data', 'level', 'logger')), FrozenPla"
        "n(fields=('data', 'level', 'logger'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('data'"
        ", 'level', 'logger'), cache=False), InitPlan(fields=(InitPlan.Field(name='data', annotation=OpRef(name='init.f"
        "ields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INST"
        "ANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='level', annotation=OpRef(name='init.f"
        "ields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INST"
        "ANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='logger', annotation=OpRef(name='init."
        "fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override="
        "False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_pa"
        "rams=(), kw_only_params=('data', 'level', 'logger'), frozen=True, slots=False, post_init_params=None, init_fns"
        "=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='data', kw_only=True, fn=None), ReprPlan.Field(nam"
        "e='level', kw_only=True, fn=None), ReprPlan.Field(name='logger', kw_only=True, fn=None)), id=False, terse=Fals"
        "e, default_fn=None)))"
    ),
    plan_repr_sha1='97ff9fd68f282de030711b91ed393e1d841a9bd9',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'LoggingMessageNotification.Params'),
    ),
)
def _process_dataclass__97ff9fd68f282de030711b91ed393e1d841a9bd9():
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
                data=self.data,
                level=self.level,
                logger=self.logger,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.data == other.data and
                self.level == other.level and
                self.logger == other.logger
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'data',
            'level',
            'logger',
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
            'level',
            'logger',
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
                self.level,
                self.logger,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            data: __dataclass__init__fields__0__annotation,
            level: __dataclass__init__fields__1__annotation,
            logger: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'data', data)
            __dataclass__object_setattr(self, 'level', level)
            __dataclass__object_setattr(self, 'logger', logger)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"data={self.data!r}")
            parts.append(f"level={self.level!r}")
            parts.append(f"logger={self.logger!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('name',)), EqPlan(fields=('name',)), FrozenPlan(fields=('name',), allow_dynamic_du"
        "nder_attrs=False), HashPlan(action='add', fields=('name',), cache=False), InitPlan(fields=(InitPlan.Field(name"
        "='name', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'), defau"
        "lt_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_t"
        "ype=None),), self_param='self', std_params=(), kw_only_params=('name',), frozen=True, slots=False, post_init_p"
        "arams=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='name', kw_only=True, fn=None)"
        ",), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='c324df10f26edffcea75a20f2b4b3730ff2011a7',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'ModelHint'),
    ),
)
def _process_dataclass__c324df10f26edffcea75a20f2b4b3730ff2011a7():
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
                name=self.name,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.name == other.name
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'name',
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
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            name: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"name={self.name!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('cost_priority', 'hints', 'intelligence_priority', 'speed_priority')), EqPlan(fiel"
        "ds=('cost_priority', 'hints', 'intelligence_priority', 'speed_priority')), FrozenPlan(fields=('cost_priority',"
        " 'hints', 'intelligence_priority', 'speed_priority'), allow_dynamic_dunder_attrs=False), HashPlan(action='add'"
        ", fields=('cost_priority', 'hints', 'intelligence_priority', 'speed_priority'), cache=False), InitPlan(fields="
        "(InitPlan.Field(name='cost_priority', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='i"
        "nit.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce"
        "=None, validate=None, check_type=None), InitPlan.Field(name='hints', annotation=OpRef(name='init.fields.1.anno"
        "tation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_"
        "type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='intelligence_prior"
        "ity', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_"
        "factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type"
        "=None), InitPlan.Field(name='speed_priority', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef"
        "(name='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE"
        ", coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('cost_prior"
        "ity', 'hints', 'intelligence_priority', 'speed_priority'), frozen=True, slots=False, post_init_params=None, in"
        "it_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='cost_priority', kw_only=True, fn=None), Rep"
        "rPlan.Field(name='hints', kw_only=True, fn=None), ReprPlan.Field(name='intelligence_priority', kw_only=True, f"
        "n=None), ReprPlan.Field(name='speed_priority', kw_only=True, fn=None)), id=False, terse=False, default_fn=None"
        ")))"
    ),
    plan_repr_sha1='12d4d64254d185f44f5b1864381940b9b65855fd',
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
        ('ommlds.specs.mcp.protocol', 'ModelPreferences'),
    ),
)
def _process_dataclass__12d4d64254d185f44f5b1864381940b9b65855fd():
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
                cost_priority=self.cost_priority,
                hints=self.hints,
                intelligence_priority=self.intelligence_priority,
                speed_priority=self.speed_priority,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.cost_priority == other.cost_priority and
                self.hints == other.hints and
                self.intelligence_priority == other.intelligence_priority and
                self.speed_priority == other.speed_priority
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'cost_priority',
            'hints',
            'intelligence_priority',
            'speed_priority',
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
            'cost_priority',
            'hints',
            'intelligence_priority',
            'speed_priority',
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
                self.cost_priority,
                self.hints,
                self.intelligence_priority,
                self.speed_priority,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            cost_priority: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            hints: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            intelligence_priority: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            speed_priority: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'cost_priority', cost_priority)
            __dataclass__object_setattr(self, 'hints', hints)
            __dataclass__object_setattr(self, 'intelligence_priority', intelligence_priority)
            __dataclass__object_setattr(self, 'speed_priority', speed_priority)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"cost_priority={self.cost_priority!r}")
            parts.append(f"hints={self.hints!r}")
            parts.append(f"intelligence_priority={self.intelligence_priority!r}")
            parts.append(f"speed_priority={self.speed_priority!r}")
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
        ('ommlds.specs.mcp.protocol', 'Notification'),
        ('ommlds.specs.mcp.protocol', 'PaginatedRequest'),
        ('ommlds.specs.mcp.protocol', 'Request'),
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
        "Plans(tup=(CopyPlan(fields=('type', 'description', 'maximum', 'minimum', 'title')), EqPlan(fields=('type', 'de"
        "scription', 'maximum', 'minimum', 'title')), FrozenPlan(fields=('type', 'description', 'maximum', 'minimum', '"
        "title'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('type', 'description', 'maximum', '"
        "minimum', 'title'), cache=False), InitPlan(fields=(InitPlan.Field(name='type', annotation=OpRef(name='init.fie"
        "lds.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTAN"
        "CE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='description', annotation=OpRef(name='in"
        "it.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, overri"
        "de=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='ma"
        "ximum', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), defaul"
        "t_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_ty"
        "pe=None), InitPlan.Field(name='minimum', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name"
        "='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coe"
        "rce=None, validate=None, check_type=None), InitPlan.Field(name='title', annotation=OpRef(name='init.fields.4.a"
        "nnotation'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, override=False, fie"
        "ld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), k"
        "w_only_params=('type', 'description', 'maximum', 'minimum', 'title'), frozen=True, slots=False, post_init_para"
        "ms=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='type', kw_only=True, fn=None), R"
        "eprPlan.Field(name='description', kw_only=True, fn=None), ReprPlan.Field(name='maximum', kw_only=True, fn=None"
        "), ReprPlan.Field(name='minimum', kw_only=True, fn=None), ReprPlan.Field(name='title', kw_only=True, fn=None))"
        ", id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='b441ab0b5764fee0a12bc56970abb7e312910cc7',
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
        ('ommlds.specs.mcp.protocol', 'NumberSchema'),
    ),
)
def _process_dataclass__b441ab0b5764fee0a12bc56970abb7e312910cc7():
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
                type=self.type,
                description=self.description,
                maximum=self.maximum,
                minimum=self.minimum,
                title=self.title,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.type == other.type and
                self.description == other.description and
                self.maximum == other.maximum and
                self.minimum == other.minimum and
                self.title == other.title
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'type',
            'description',
            'maximum',
            'minimum',
            'title',
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
            'type',
            'description',
            'maximum',
            'minimum',
            'title',
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
                self.type,
                self.description,
                self.maximum,
                self.minimum,
                self.title,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            type: __dataclass__init__fields__0__annotation,
            description: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            maximum: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            minimum: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            title: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'type', type)
            __dataclass__object_setattr(self, 'description', description)
            __dataclass__object_setattr(self, 'maximum', maximum)
            __dataclass__object_setattr(self, 'minimum', minimum)
            __dataclass__object_setattr(self, 'title', title)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"type={self.type!r}")
            parts.append(f"description={self.description!r}")
            parts.append(f"maximum={self.maximum!r}")
            parts.append(f"minimum={self.minimum!r}")
            parts.append(f"title={self.title!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('next_cursor', 'meta')), EqPlan(fields=('next_cursor', 'meta')), FrozenPlan(fields"
        "=('next_cursor', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('next_cursor', 'me"
        "ta'), cache=False), InitPlan(fields=(InitPlan.Field(name='next_cursor', annotation=OpRef(name='init.fields.0.a"
        "nnotation'), default=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, fie"
        "ld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='meta', annotati"
        "on=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, "
        "init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_"
        "param='self', std_params=(), kw_only_params=('next_cursor', 'meta'), frozen=True, slots=False, post_init_param"
        "s=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='next_cursor', kw_only=True, fn=No"
        "ne), ReprPlan.Field(name='meta', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='be0d4c91ff874fa3b217062c470cb07d115488f4',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'PaginatedResult'),
    ),
)
def _process_dataclass__be0d4c91ff874fa3b217062c470cb07d115488f4():
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
                self.next_cursor == other.next_cursor and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
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
                self.next_cursor,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            next_cursor: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            meta: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'next_cursor', next_cursor)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
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
        "Plans(tup=(CopyPlan(fields=('progress', 'progress_token', 'message', 'total')), EqPlan(fields=('progress', 'pr"
        "ogress_token', 'message', 'total')), FrozenPlan(fields=('progress', 'progress_token', 'message', 'total'), all"
        "ow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('progress', 'progress_token', 'message', 'total"
        "'), cache=False), InitPlan(fields=(InitPlan.Field(name='progress', annotation=OpRef(name='init.fields.0.annota"
        "tion'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=N"
        "one, validate=None, check_type=None), InitPlan.Field(name='progress_token', annotation=OpRef(name='init.fields"
        ".1.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE,"
        " coerce=None, validate=None, check_type=None), InitPlan.Field(name='message', annotation=OpRef(name='init.fiel"
        "ds.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=Fals"
        "e, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='total', a"
        "nnotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory"
        "=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None))"
        ", self_param='self', std_params=(), kw_only_params=('progress', 'progress_token', 'message', 'total'), frozen="
        "True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name="
        "'progress', kw_only=True, fn=None), ReprPlan.Field(name='progress_token', kw_only=True, fn=None), ReprPlan.Fie"
        "ld(name='message', kw_only=True, fn=None), ReprPlan.Field(name='total', kw_only=True, fn=None)), id=False, ter"
        "se=False, default_fn=None)))"
    ),
    plan_repr_sha1='59fcc1c2ae322b9f1ed648a1e2e49c19fd412726',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'ProgressNotification.Params'),
    ),
)
def _process_dataclass__59fcc1c2ae322b9f1ed648a1e2e49c19fd412726():
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
                progress=self.progress,
                progress_token=self.progress_token,
                message=self.message,
                total=self.total,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.progress == other.progress and
                self.progress_token == other.progress_token and
                self.message == other.message and
                self.total == other.total
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'progress',
            'progress_token',
            'message',
            'total',
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
            'progress',
            'progress_token',
            'message',
            'total',
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
                self.progress,
                self.progress_token,
                self.message,
                self.total,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            progress: __dataclass__init__fields__0__annotation,
            progress_token: __dataclass__init__fields__1__annotation,
            message: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            total: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'progress', progress)
            __dataclass__object_setattr(self, 'progress_token', progress_token)
            __dataclass__object_setattr(self, 'message', message)
            __dataclass__object_setattr(self, 'total', total)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"progress={self.progress!r}")
            parts.append(f"progress_token={self.progress_token!r}")
            parts.append(f"message={self.message!r}")
            parts.append(f"total={self.total!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('name', 'arguments', 'description', 'title', 'meta')), EqPlan(fields=('name', 'arg"
        "uments', 'description', 'title', 'meta')), FrozenPlan(fields=('name', 'arguments', 'description', 'title', 'me"
        "ta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('name', 'arguments', 'description', 't"
        "itle', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='name', annotation=OpRef(name='init.fields."
        "0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, "
        "coerce=None, validate=None, check_type=None), InitPlan.Field(name='arguments', annotation=OpRef(name='init.fie"
        "lds.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=Fal"
        "se, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='descript"
        "ion', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_"
        "factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type"
        "=None), InitPlan.Field(name='title', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='in"
        "it.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce="
        "None, validate=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.4.annota"
        "tion'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, override=False, field_ty"
        "pe=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_onl"
        "y_params=('name', 'arguments', 'description', 'title', 'meta'), frozen=True, slots=False, post_init_params=Non"
        "e, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='name', kw_only=True, fn=None), ReprPla"
        "n.Field(name='arguments', kw_only=True, fn=None), ReprPlan.Field(name='description', kw_only=True, fn=None), R"
        "eprPlan.Field(name='title', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), id=Fa"
        "lse, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='2cbd168804bdb48b75fe63716ebfe24779ae990f',
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
        ('ommlds.specs.mcp.protocol', 'Prompt'),
    ),
)
def _process_dataclass__2cbd168804bdb48b75fe63716ebfe24779ae990f():
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
                name=self.name,
                arguments=self.arguments,
                description=self.description,
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
                self.arguments == other.arguments and
                self.description == other.description and
                self.title == other.title and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'name',
            'arguments',
            'description',
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
            'arguments',
            'description',
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
                self.arguments,
                self.description,
                self.title,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            name: __dataclass__init__fields__0__annotation,
            arguments: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            description: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            title: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            meta: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'arguments', arguments)
            __dataclass__object_setattr(self, 'description', description)
            __dataclass__object_setattr(self, 'title', title)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"name={self.name!r}")
            parts.append(f"arguments={self.arguments!r}")
            parts.append(f"description={self.description!r}")
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
        "Plans(tup=(CopyPlan(fields=('name', 'description', 'required', 'title')), EqPlan(fields=('name', 'description'"
        ", 'required', 'title')), FrozenPlan(fields=('name', 'description', 'required', 'title'), allow_dynamic_dunder_"
        "attrs=False), HashPlan(action='add', fields=('name', 'description', 'required', 'title'), cache=False), InitPl"
        "an(fields=(InitPlan.Field(name='name', annotation=OpRef(name='init.fields.0.annotation'), default=None, defaul"
        "t_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_ty"
        "pe=None), InitPlan.Field(name='description', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef("
        "name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE,"
        " coerce=None, validate=None, check_type=None), InitPlan.Field(name='required', annotation=OpRef(name='init.fie"
        "lds.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=Fal"
        "se, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='title', "
        "annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factor"
        "y=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)"
        "), self_param='self', std_params=(), kw_only_params=('name', 'description', 'required', 'title'), frozen=True,"
        " slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='name"
        "', kw_only=True, fn=None), ReprPlan.Field(name='description', kw_only=True, fn=None), ReprPlan.Field(name='req"
        "uired', kw_only=True, fn=None), ReprPlan.Field(name='title', kw_only=True, fn=None)), id=False, terse=False, d"
        "efault_fn=None)))"
    ),
    plan_repr_sha1='4f6785cb4de4e1c4f9b3424deb3cac45acc75b27',
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
        ('ommlds.specs.mcp.protocol', 'PromptArgument'),
    ),
)
def _process_dataclass__4f6785cb4de4e1c4f9b3424deb3cac45acc75b27():
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
                name=self.name,
                description=self.description,
                required=self.required,
                title=self.title,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.name == other.name and
                self.description == other.description and
                self.required == other.required and
                self.title == other.title
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'name',
            'description',
            'required',
            'title',
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
            'description',
            'required',
            'title',
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
                self.description,
                self.required,
                self.title,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            name: __dataclass__init__fields__0__annotation,
            description: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            required: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            title: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'description', description)
            __dataclass__object_setattr(self, 'required', required)
            __dataclass__object_setattr(self, 'title', title)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"name={self.name!r}")
            parts.append(f"description={self.description!r}")
            parts.append(f"required={self.required!r}")
            parts.append(f"title={self.title!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('content', 'role')), EqPlan(fields=('content', 'role')), FrozenPlan(fields=('conte"
        "nt', 'role'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('content', 'role'), cache=Fals"
        "e), InitPlan(fields=(InitPlan.Field(name='content', annotation=OpRef(name='init.fields.0.annotation'), default"
        "=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=N"
        "one, check_type=None), InitPlan.Field(name='role', annotation=OpRef(name='init.fields.1.annotation'), default="
        "None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=No"
        "ne, check_type=None)), self_param='self', std_params=(), kw_only_params=('content', 'role'), frozen=True, slot"
        "s=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='content',"
        " kw_only=True, fn=None), ReprPlan.Field(name='role', kw_only=True, fn=None)), id=False, terse=False, default_f"
        "n=None)))"
    ),
    plan_repr_sha1='28fa0d9ed0acd7cd675991b58f309cafc8b4701f',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'PromptMessage'),
        ('ommlds.specs.mcp.protocol', 'SamplingMessage'),
    ),
)
def _process_dataclass__28fa0d9ed0acd7cd675991b58f309cafc8b4701f():
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
                content=self.content,
                role=self.role,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.content == other.content and
                self.role == other.role
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'content',
            'role',
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
            'role',
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
                self.role,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            content: __dataclass__init__fields__0__annotation,
            role: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'content', content)
            __dataclass__object_setattr(self, 'role', role)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"content={self.content!r}")
            parts.append(f"role={self.role!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('name', 'title', 'type')), EqPlan(fields=('name', 'title', 'type')), FrozenPlan(fi"
        "elds=('name', 'title', 'type'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('name', 'tit"
        "le', 'type'), cache=False), InitPlan(fields=(InitPlan.Field(name='name', annotation=OpRef(name='init.fields.0."
        "annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, co"
        "erce=None, validate=None, check_type=None), InitPlan.Field(name='title', annotation=OpRef(name='init.fields.1."
        "annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, fi"
        "eld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='type', annotat"
        "ion=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None,"
        " init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self"
        "_param='self', std_params=(), kw_only_params=('name', 'title', 'type'), frozen=True, slots=False, post_init_pa"
        "rams=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='name', kw_only=True, fn=None),"
        " ReprPlan.Field(name='title', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='56b3acf6332e5731d048891a1c79d1648cafd084',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'PromptReference'),
    ),
)
def _process_dataclass__56b3acf6332e5731d048891a1c79d1648cafd084():
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
                name=self.name,
                title=self.title,
                type=self.type,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.name == other.name and
                self.title == other.title and
                self.type == other.type
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'name',
            'title',
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
            'name',
            'title',
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
                self.name,
                self.title,
                self.type,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            name: __dataclass__init__fields__0__annotation,
            title: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            type: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'title', title)
            __dataclass__object_setattr(self, 'type', type)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"name={self.name!r}")
            parts.append(f"title={self.title!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('uri',)), EqPlan(fields=('uri',)), FrozenPlan(fields=('uri',), allow_dynamic_dunde"
        "r_attrs=False), HashPlan(action='add', fields=('uri',), cache=False), InitPlan(fields=(InitPlan.Field(name='ur"
        "i', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override"
        "=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='self', std_"
        "params=(), kw_only_params=('uri',), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns"
        "=()), ReprPlan(fields=(ReprPlan.Field(name='uri', kw_only=True, fn=None),), id=False, terse=False, default_fn="
        "None)))"
    ),
    plan_repr_sha1='276376c0f254cbe1b3a56856fd6c85897139215b',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'ReadResourceRequest.Params'),
        ('ommlds.specs.mcp.protocol', 'ResourceUpdatedNotification.Params'),
        ('ommlds.specs.mcp.protocol', 'SubscribeRequest.Params'),
        ('ommlds.specs.mcp.protocol', 'UnsubscribeRequest.Params'),
    ),
)
def _process_dataclass__276376c0f254cbe1b3a56856fd6c85897139215b():
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
                uri=self.uri,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.uri == other.uri
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'uri',
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
            'uri',
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
                self.uri,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            uri: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'uri', uri)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"uri={self.uri!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('contents', 'meta')), EqPlan(fields=('contents', 'meta')), FrozenPlan(fields=('con"
        "tents', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('contents', 'meta'), cache="
        "False), InitPlan(fields=(InitPlan.Field(name='contents', annotation=OpRef(name='init.fields.0.annotation'), de"
        "fault=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valid"
        "ate=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.1.annotation'), def"
        "ault=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldTyp"
        "e.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('"
        "contents', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(f"
        "ields=(ReprPlan.Field(name='contents', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=No"
        "ne)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='d6f385465a04c65f50e9d9d65b494f089a1a86ac',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'ReadResourceResult'),
    ),
)
def _process_dataclass__d6f385465a04c65f50e9d9d65b494f089a1a86ac():
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
                contents=self.contents,
                meta=self.meta,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.contents == other.contents and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'contents',
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
            'contents',
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
                self.contents,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            contents: __dataclass__init__fields__0__annotation,
            meta: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'contents', contents)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"contents={self.contents!r}")
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
        ('ommlds.specs.mcp.protocol', 'Resource'),
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
        "Plans(tup=(CopyPlan(fields=('uri', 'mime_type', 'meta')), EqPlan(fields=('uri', 'mime_type', 'meta')), FrozenP"
        "lan(fields=('uri', 'mime_type', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('ur"
        "i', 'mime_type', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='uri', annotation=OpRef(name='ini"
        "t.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.I"
        "NSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='mime_type', annotation=OpRef(name="
        "'init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, ove"
        "rride=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name="
        "'meta', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), defaul"
        "t_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_ty"
        "pe=None)), self_param='self', std_params=(), kw_only_params=('uri', 'mime_type', 'meta'), frozen=True, slots=F"
        "alse, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='uri', kw_onl"
        "y=True, fn=None), ReprPlan.Field(name='mime_type', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only"
        "=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='b0645a00c325b97bc04987be710b64012dc86783',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'ResourceContents'),
    ),
)
def _process_dataclass__b0645a00c325b97bc04987be710b64012dc86783():
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
                self.uri == other.uri and
                self.mime_type == other.mime_type and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
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
                self.uri,
                self.mime_type,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            uri: __dataclass__init__fields__0__annotation,
            mime_type: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            meta: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'uri', uri)
            __dataclass__object_setattr(self, 'mime_type', mime_type)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
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
        "Plans(tup=(CopyPlan(fields=('name', 'uri', 'annotations', 'description', 'mime_type', 'size', 'title', 'type',"
        " 'meta')), EqPlan(fields=('name', 'uri', 'annotations', 'description', 'mime_type', 'size', 'title', 'type', '"
        "meta')), FrozenPlan(fields=('name', 'uri', 'annotations', 'description', 'mime_type', 'size', 'title', 'type',"
        " 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('name', 'uri', 'annotations', 'des"
        "cription', 'mime_type', 'size', 'title', 'type', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='"
        "name', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, overr"
        "ide=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='u"
        "ri', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, overrid"
        "e=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='ann"
        "otations', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), def"
        "ault_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check"
        "_type=None), InitPlan.Field(name='description', annotation=OpRef(name='init.fields.3.annotation'), default=OpR"
        "ef(name='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTAN"
        "CE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='mime_type', annotation=OpRef(name='init"
        ".fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, override"
        "=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='size"
        "', annotation=OpRef(name='init.fields.5.annotation'), default=OpRef(name='init.fields.5.default'), default_fac"
        "tory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=No"
        "ne), InitPlan.Field(name='title', annotation=OpRef(name='init.fields.6.annotation'), default=OpRef(name='init."
        "fields.6.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=Non"
        "e, validate=None, check_type=None), InitPlan.Field(name='type', annotation=OpRef(name='init.fields.7.annotatio"
        "n'), default=OpRef(name='init.fields.7.default'), default_factory=None, init=True, override=False, field_type="
        "FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef"
        "(name='init.fields.8.annotation'), default=OpRef(name='init.fields.8.default'), default_factory=None, init=Tru"
        "e, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='s"
        "elf', std_params=(), kw_only_params=('name', 'uri', 'annotations', 'description', 'mime_type', 'size', 'title'"
        ", 'type', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fi"
        "elds=(ReprPlan.Field(name='name', kw_only=True, fn=None), ReprPlan.Field(name='uri', kw_only=True, fn=None), R"
        "eprPlan.Field(name='annotations', kw_only=True, fn=None), ReprPlan.Field(name='description', kw_only=True, fn="
        "None), ReprPlan.Field(name='mime_type', kw_only=True, fn=None), ReprPlan.Field(name='size', kw_only=True, fn=N"
        "one), ReprPlan.Field(name='title', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None))"
        ", id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='e74ff82cad7d3f5367d35009dd9ff5713864cd16',
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
        ('ommlds.specs.mcp.protocol', 'ResourceLink'),
    ),
)
def _process_dataclass__e74ff82cad7d3f5367d35009dd9ff5713864cd16():
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
                annotations=self.annotations,
                description=self.description,
                mime_type=self.mime_type,
                size=self.size,
                title=self.title,
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
                self.name == other.name and
                self.uri == other.uri and
                self.annotations == other.annotations and
                self.description == other.description and
                self.mime_type == other.mime_type and
                self.size == other.size and
                self.title == other.title and
                self.type == other.type and
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
            'name',
            'uri',
            'annotations',
            'description',
            'mime_type',
            'size',
            'title',
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
                self.name,
                self.uri,
                self.annotations,
                self.description,
                self.mime_type,
                self.size,
                self.title,
                self.type,
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
            type: __dataclass__init__fields__7__annotation = __dataclass__init__fields__7__default,
            meta: __dataclass__init__fields__8__annotation = __dataclass__init__fields__8__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'uri', uri)
            __dataclass__object_setattr(self, 'annotations', annotations)
            __dataclass__object_setattr(self, 'description', description)
            __dataclass__object_setattr(self, 'mime_type', mime_type)
            __dataclass__object_setattr(self, 'size', size)
            __dataclass__object_setattr(self, 'title', title)
            __dataclass__object_setattr(self, 'type', type)
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
        "Plans(tup=(CopyPlan(fields=('name', 'uri_template', 'annotations', 'description', 'mime_type', 'title', 'meta'"
        ")), EqPlan(fields=('name', 'uri_template', 'annotations', 'description', 'mime_type', 'title', 'meta')), Froze"
        "nPlan(fields=('name', 'uri_template', 'annotations', 'description', 'mime_type', 'title', 'meta'), allow_dynam"
        "ic_dunder_attrs=False), HashPlan(action='add', fields=('name', 'uri_template', 'annotations', 'description', '"
        "mime_type', 'title', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='name', annotation=OpRef(name"
        "='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldT"
        "ype.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='uri_template', annotation=OpR"
        "ef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_type"
        "=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='annotations', annotati"
        "on=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, "
        "init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPl"
        "an.Field(name='description', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.field"
        "s.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, va"
        "lidate=None, check_type=None), InitPlan.Field(name='mime_type', annotation=OpRef(name='init.fields.4.annotatio"
        "n'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, override=False, field_type="
        "FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='title', annotation=OpRe"
        "f(name='init.fields.5.annotation'), default=OpRef(name='init.fields.5.default'), default_factory=None, init=Tr"
        "ue, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fiel"
        "d(name='meta', annotation=OpRef(name='init.fields.6.annotation'), default=OpRef(name='init.fields.6.default'),"
        " default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, c"
        "heck_type=None)), self_param='self', std_params=(), kw_only_params=('name', 'uri_template', 'annotations', 'de"
        "scription', 'mime_type', 'title', 'meta'), frozen=True, slots=False, post_init_params=None, init_fns=(), valid"
        "ate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='name', kw_only=True, fn=None), ReprPlan.Field(name='uri_tem"
        "plate', kw_only=True, fn=None), ReprPlan.Field(name='annotations', kw_only=True, fn=None), ReprPlan.Field(name"
        "='description', kw_only=True, fn=None), ReprPlan.Field(name='mime_type', kw_only=True, fn=None), ReprPlan.Fiel"
        "d(name='title', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), id=False, terse=F"
        "alse, default_fn=None)))"
    ),
    plan_repr_sha1='ab6a6047bb0be016d16a43384dcc7d3812075dbf',
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
        ('ommlds.specs.mcp.protocol', 'ResourceTemplate'),
    ),
)
def _process_dataclass__ab6a6047bb0be016d16a43384dcc7d3812075dbf():
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
                name=self.name,
                uri_template=self.uri_template,
                annotations=self.annotations,
                description=self.description,
                mime_type=self.mime_type,
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
                self.uri_template == other.uri_template and
                self.annotations == other.annotations and
                self.description == other.description and
                self.mime_type == other.mime_type and
                self.title == other.title and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'name',
            'uri_template',
            'annotations',
            'description',
            'mime_type',
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
            'uri_template',
            'annotations',
            'description',
            'mime_type',
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
                self.uri_template,
                self.annotations,
                self.description,
                self.mime_type,
                self.title,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            name: __dataclass__init__fields__0__annotation,
            uri_template: __dataclass__init__fields__1__annotation,
            annotations: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            description: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            mime_type: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            title: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
            meta: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'uri_template', uri_template)
            __dataclass__object_setattr(self, 'annotations', annotations)
            __dataclass__object_setattr(self, 'description', description)
            __dataclass__object_setattr(self, 'mime_type', mime_type)
            __dataclass__object_setattr(self, 'title', title)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"name={self.name!r}")
            parts.append(f"uri_template={self.uri_template!r}")
            parts.append(f"annotations={self.annotations!r}")
            parts.append(f"description={self.description!r}")
            parts.append(f"mime_type={self.mime_type!r}")
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
        "Plans(tup=(CopyPlan(fields=('uri', 'type')), EqPlan(fields=('uri', 'type')), FrozenPlan(fields=('uri', 'type')"
        ", allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('uri', 'type'), cache=False), InitPlan(fie"
        "lds=(InitPlan.Field(name='uri', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_facto"
        "ry=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None"
        "), InitPlan.Field(name='type', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fie"
        "lds.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, "
        "validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('uri', 'type'), frozen=Tru"
        "e, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='ur"
        "i', kw_only=True, fn=None),), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='57a8e0b95db07424a50c3418127ad13c7b802859',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'ResourceTemplateReference'),
    ),
)
def _process_dataclass__57a8e0b95db07424a50c3418127ad13c7b802859():
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
                uri=self.uri,
                type=self.type,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.uri == other.uri and
                self.type == other.type
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'uri',
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
            'uri',
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
                self.uri,
                self.type,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            uri: __dataclass__init__fields__0__annotation,
            type: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'uri', uri)
            __dataclass__object_setattr(self, 'type', type)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"uri={self.uri!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('uri', 'name', 'meta')), EqPlan(fields=('uri', 'name', 'meta')), FrozenPlan(fields"
        "=('uri', 'name', 'meta'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('uri', 'name', 'me"
        "ta'), cache=False), InitPlan(fields=(InitPlan.Field(name='uri', annotation=OpRef(name='init.fields.0.annotatio"
        "n'), default=None, default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None"
        ", validate=None, check_type=None), InitPlan.Field(name='name', annotation=OpRef(name='init.fields.1.annotation"
        "'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, field_type=F"
        "ieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef("
        "name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True"
        ", override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='se"
        "lf', std_params=(), kw_only_params=('uri', 'name', 'meta'), frozen=True, slots=False, post_init_params=None, i"
        "nit_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='uri', kw_only=True, fn=None), ReprPlan.Fie"
        "ld(name='name', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), id=False, terse=F"
        "alse, default_fn=None)))"
    ),
    plan_repr_sha1='42cd9564620a5e4fd947996819f049abd4f7d609',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'Root'),
    ),
)
def _process_dataclass__42cd9564620a5e4fd947996819f049abd4f7d609():
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
                uri=self.uri,
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
                self.uri == other.uri and
                self.name == other.name and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'uri',
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
            'uri',
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
                self.uri,
                self.name,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            uri: __dataclass__init__fields__0__annotation,
            name: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            meta: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'uri', uri)
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"uri={self.uri!r}")
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
        ('ommlds.specs.mcp.protocol', 'ServerCapabilities'),
        ('ommlds.specs.mcp.protocolold', 'ServerCapabilities'),
    ),
)
def _process_dataclass__0604ae887e3d1ab59338acbd6630052994c6f8d7():
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
                completions=self.completions,
                experimental=self.experimental,
                logging=self.logging,
                prompts=self.prompts,
                resources=self.resources,
                tools=self.tools,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

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

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

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
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

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
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.completions,
                self.experimental,
                self.logging,
                self.prompts,
                self.resources,
                self.tools,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

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

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

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

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

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
        ('ommlds.specs.mcp.protocol', 'ServerCapabilities.Resources'),
        ('ommlds.specs.mcp.protocolold', 'ServerCapabilities.Resources'),
    ),
)
def _process_dataclass__42bc667dce1ec8940899ca3e66ca6e82c18ef4ea():
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
                list_changed=self.list_changed,
                subscribe=self.subscribe,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.list_changed == other.list_changed and
                self.subscribe == other.subscribe
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'list_changed',
            'subscribe',
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
            'list_changed',
            'subscribe',
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
                self.list_changed,
                self.subscribe,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            list_changed: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            subscribe: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'list_changed', list_changed)
            __dataclass__object_setattr(self, 'subscribe', subscribe)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

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

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('level',)), EqPlan(fields=('level',)), FrozenPlan(fields=('level',), allow_dynamic"
        "_dunder_attrs=False), HashPlan(action='add', fields=('level',), cache=False), InitPlan(fields=(InitPlan.Field("
        "name='level', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True"
        ", override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None),), self_param='s"
        "elf', std_params=(), kw_only_params=('level',), frozen=True, slots=False, post_init_params=None, init_fns=(), "
        "validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='level', kw_only=True, fn=None),), id=False, terse=Fals"
        "e, default_fn=None)))"
    ),
    plan_repr_sha1='62d4589233c32ba393d739a4bb30443082ae877d',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'SetLevelRequest.Params'),
    ),
)
def _process_dataclass__62d4589233c32ba393d739a4bb30443082ae877d():
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
                level=self.level,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.level == other.level
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'level',
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
            'level',
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
                self.level,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            level: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'level', level)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"level={self.level!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('description', 'format', 'max_length', 'min_length', 'title', 'type')), EqPlan(fie"
        "lds=('description', 'format', 'max_length', 'min_length', 'title', 'type')), FrozenPlan(fields=('description',"
        " 'format', 'max_length', 'min_length', 'title', 'type'), allow_dynamic_dunder_attrs=False), HashPlan(action='a"
        "dd', fields=('description', 'format', 'max_length', 'min_length', 'title', 'type'), cache=False), InitPlan(fie"
        "lds=(InitPlan.Field(name='description', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name="
        "'init.fields.0.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coer"
        "ce=None, validate=None, check_type=None), InitPlan.Field(name='format', annotation=OpRef(name='init.fields.1.a"
        "nnotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=True, override=False, fie"
        "ld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='max_length', an"
        "notation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory="
        "None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), "
        "InitPlan.Field(name='min_length', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init."
        "fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=Non"
        "e, validate=None, check_type=None), InitPlan.Field(name='title', annotation=OpRef(name='init.fields.4.annotati"
        "on'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, override=False, field_type"
        "=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='type', annotation=OpRe"
        "f(name='init.fields.5.annotation'), default=OpRef(name='init.fields.5.default'), default_factory=None, init=Tr"
        "ue, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='"
        "self', std_params=(), kw_only_params=('description', 'format', 'max_length', 'min_length', 'title', 'type'), f"
        "rozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field"
        "(name='description', kw_only=True, fn=None), ReprPlan.Field(name='format', kw_only=True, fn=None), ReprPlan.Fi"
        "eld(name='max_length', kw_only=True, fn=None), ReprPlan.Field(name='min_length', kw_only=True, fn=None), ReprP"
        "lan.Field(name='title', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='dd48b7dac215da904a7ef4a8083f4f71b413ad91',
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
        ('ommlds.specs.mcp.protocol', 'StringSchema'),
    ),
)
def _process_dataclass__dd48b7dac215da904a7ef4a8083f4f71b413ad91():
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
                description=self.description,
                format=self.format,
                max_length=self.max_length,
                min_length=self.min_length,
                title=self.title,
                type=self.type,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.description == other.description and
                self.format == other.format and
                self.max_length == other.max_length and
                self.min_length == other.min_length and
                self.title == other.title and
                self.type == other.type
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'description',
            'format',
            'max_length',
            'min_length',
            'title',
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
            'description',
            'format',
            'max_length',
            'min_length',
            'title',
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
                self.description,
                self.format,
                self.max_length,
                self.min_length,
                self.title,
                self.type,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            description: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            format: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            max_length: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            min_length: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            title: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            type: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'description', description)
            __dataclass__object_setattr(self, 'format', format)
            __dataclass__object_setattr(self, 'max_length', max_length)
            __dataclass__object_setattr(self, 'min_length', min_length)
            __dataclass__object_setattr(self, 'title', title)
            __dataclass__object_setattr(self, 'type', type)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"description={self.description!r}")
            parts.append(f"format={self.format!r}")
            parts.append(f"max_length={self.max_length!r}")
            parts.append(f"min_length={self.min_length!r}")
            parts.append(f"title={self.title!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


@_register(
    plan_repr=(
        "Plans(tup=(CopyPlan(fields=('text', 'annotations', 'type', 'meta')), EqPlan(fields=('text', 'annotations', 'ty"
        "pe', 'meta')), FrozenPlan(fields=('text', 'annotations', 'type', 'meta'), allow_dynamic_dunder_attrs=False), H"
        "ashPlan(action='add', fields=('text', 'annotations', 'type', 'meta'), cache=False), InitPlan(fields=(InitPlan."
        "Field(name='text', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init"
        "=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.F"
        "ield(name='annotations', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1."
        "default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valida"
        "te=None, check_type=None), InitPlan.Field(name='type', annotation=OpRef(name='init.fields.2.annotation'), defa"
        "ult=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType"
        ".INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='meta', annotation=OpRef(name='in"
        "it.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, overri"
        "de=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std"
        "_params=(), kw_only_params=('text', 'annotations', 'type', 'meta'), frozen=True, slots=False, post_init_params"
        "=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='text', kw_only=True, fn=None), Rep"
        "rPlan.Field(name='annotations', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, fn=None)), i"
        "d=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='d27b4b9b84d6300c78acd44c9664a05f2a6043a7',
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
        ('ommlds.specs.mcp.protocol', 'TextContent'),
    ),
)
def _process_dataclass__d27b4b9b84d6300c78acd44c9664a05f2a6043a7():
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
                annotations=self.annotations,
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
                self.text == other.text and
                self.annotations == other.annotations and
                self.type == other.type and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'text',
            'annotations',
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
            'text',
            'annotations',
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
                self.text,
                self.annotations,
                self.type,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            text: __dataclass__init__fields__0__annotation,
            annotations: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            type: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            meta: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'text', text)
            __dataclass__object_setattr(self, 'annotations', annotations)
            __dataclass__object_setattr(self, 'type', type)
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
        ('ommlds.specs.mcp.protocol', 'TextResourceContents'),
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
        "Plans(tup=(CopyPlan(fields=('input_schema', 'name', 'annotations', 'description', 'output_schema', 'title', 'm"
        "eta')), EqPlan(fields=('input_schema', 'name', 'annotations', 'description', 'output_schema', 'title', 'meta')"
        "), FrozenPlan(fields=('input_schema', 'name', 'annotations', 'description', 'output_schema', 'title', 'meta'),"
        " allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('input_schema', 'name', 'annotations', 'des"
        "cription', 'output_schema', 'title', 'meta'), cache=False), InitPlan(fields=(InitPlan.Field(name='input_schema"
        "', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override="
        "False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='name'"
        ", annotation=OpRef(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=F"
        "alse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='annota"
        "tions', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), defaul"
        "t_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_ty"
        "pe=None), InitPlan.Field(name='description', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef("
        "name='init.fields.3.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE,"
        " coerce=None, validate=None, check_type=None), InitPlan.Field(name='output_schema', annotation=OpRef(name='ini"
        "t.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, overrid"
        "e=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='tit"
        "le', annotation=OpRef(name='init.fields.5.annotation'), default=OpRef(name='init.fields.5.default'), default_f"
        "actory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type="
        "None), InitPlan.Field(name='meta', annotation=OpRef(name='init.fields.6.annotation'), default=OpRef(name='init"
        ".fields.6.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=No"
        "ne, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('input_schema', 'name'"
        ", 'annotations', 'description', 'output_schema', 'title', 'meta'), frozen=True, slots=False, post_init_params="
        "None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='input_schema', kw_only=True, fn=Non"
        "e), ReprPlan.Field(name='name', kw_only=True, fn=None), ReprPlan.Field(name='annotations', kw_only=True, fn=No"
        "ne), ReprPlan.Field(name='description', kw_only=True, fn=None), ReprPlan.Field(name='output_schema', kw_only=T"
        "rue, fn=None), ReprPlan.Field(name='title', kw_only=True, fn=None), ReprPlan.Field(name='meta', kw_only=True, "
        "fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='1579b60ea327cacf2757d1977dffca6a8642801e',
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
        ('ommlds.specs.mcp.protocol', 'Tool'),
    ),
)
def _process_dataclass__1579b60ea327cacf2757d1977dffca6a8642801e():
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
                input_schema=self.input_schema,
                name=self.name,
                annotations=self.annotations,
                description=self.description,
                output_schema=self.output_schema,
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
                self.input_schema == other.input_schema and
                self.name == other.name and
                self.annotations == other.annotations and
                self.description == other.description and
                self.output_schema == other.output_schema and
                self.title == other.title and
                self.meta == other.meta
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'input_schema',
            'name',
            'annotations',
            'description',
            'output_schema',
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
            'input_schema',
            'name',
            'annotations',
            'description',
            'output_schema',
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
                self.input_schema,
                self.name,
                self.annotations,
                self.description,
                self.output_schema,
                self.title,
                self.meta,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            input_schema: __dataclass__init__fields__0__annotation,
            name: __dataclass__init__fields__1__annotation,
            annotations: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            description: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            output_schema: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            title: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
            meta: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'input_schema', input_schema)
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'annotations', annotations)
            __dataclass__object_setattr(self, 'description', description)
            __dataclass__object_setattr(self, 'output_schema', output_schema)
            __dataclass__object_setattr(self, 'title', title)
            __dataclass__object_setattr(self, 'meta', meta)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"input_schema={self.input_schema!r}")
            parts.append(f"name={self.name!r}")
            parts.append(f"annotations={self.annotations!r}")
            parts.append(f"description={self.description!r}")
            parts.append(f"output_schema={self.output_schema!r}")
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
        "Plans(tup=(CopyPlan(fields=('properties', 'required', 'type')), EqPlan(fields=('properties', 'required', 'type"
        "')), FrozenPlan(fields=('properties', 'required', 'type'), allow_dynamic_dunder_attrs=False), HashPlan(action="
        "'add', fields=('properties', 'required', 'type'), cache=False), InitPlan(fields=(InitPlan.Field(name='properti"
        "es', annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'), default_f"
        "actory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type="
        "None), InitPlan.Field(name='required', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='"
        "init.fields.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerc"
        "e=None, validate=None, check_type=None), InitPlan.Field(name='type', annotation=OpRef(name='init.fields.2.anno"
        "tation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_"
        "type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_o"
        "nly_params=('properties', 'required', 'type'), frozen=True, slots=False, post_init_params=None, init_fns=(), v"
        "alidate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='properties', kw_only=True, fn=None), ReprPlan.Field(nam"
        "e='required', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='7f8322f1099d8942449af86391573c8fc14ef849',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
    ),
    cls_names=(
        ('ommlds.specs.mcp.protocol', 'Tool.InputSchema'),
        ('ommlds.specs.mcp.protocol', 'Tool.OutputSchema'),
    ),
)
def _process_dataclass__7f8322f1099d8942449af86391573c8fc14ef849():
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
                properties=self.properties,
                required=self.required,
                type=self.type,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.properties == other.properties and
                self.required == other.required and
                self.type == other.type
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'properties',
            'required',
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
            'properties',
            'required',
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
                self.properties,
                self.required,
                self.type,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            properties: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            required: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            type: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'properties', properties)
            __dataclass__object_setattr(self, 'required', required)
            __dataclass__object_setattr(self, 'type', type)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"properties={self.properties!r}")
            parts.append(f"required={self.required!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

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
        ('ommlds.specs.mcp.protocol', 'ToolAnnotations'),
        ('ommlds.specs.mcp.protocolold', 'ToolAnnotations'),
    ),
)
def _process_dataclass__e22803d32e39ac5461f07f6c2170c01280b5f7b9():
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
                destructive_hint=self.destructive_hint,
                idempotent_hint=self.idempotent_hint,
                open_world_hint=self.open_world_hint,
                read_only_hint=self.read_only_hint,
                title=self.title,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

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

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'destructive_hint',
            'idempotent_hint',
            'open_world_hint',
            'read_only_hint',
            'title',
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
            'destructive_hint',
            'idempotent_hint',
            'open_world_hint',
            'read_only_hint',
            'title',
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
                self.destructive_hint,
                self.idempotent_hint,
                self.open_world_hint,
                self.read_only_hint,
                self.title,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

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

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

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

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass


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
        ('ommlds.specs.mcp.protocolold', 'CallToolRequest'),
    ),
)
def _process_dataclass__2f03740b99dc8066cfcbcc46b7cb91d872fdef60():
    def _process_dataclass(
        *,
        __class__,
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
                arguments=self.arguments,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.name == other.name and
                self.arguments == other.arguments
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'json_rpc_method_name',
            'name',
            'arguments',
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
            'json_rpc_method_name',
            'name',
            'arguments',
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
                self.arguments,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            name: __dataclass__init__fields__1__annotation,
            arguments: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'arguments', arguments)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

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

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

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
        ('ommlds.specs.mcp.protocolold', 'CallToolResult'),
    ),
)
def _process_dataclass__d67af412fc2e5e82d7729f9452c092674a3f36b3():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
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
                meta_=self.meta_,
                content=self.content,
                is_error=self.is_error,
                structured_content=self.structured_content,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

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

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'meta_',
            'json_rpc_method_name',
            'content',
            'is_error',
            'structured_content',
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
            'meta_',
            'json_rpc_method_name',
            'content',
            'is_error',
            'structured_content',
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
                self.meta_,
                self.content,
                self.is_error,
                self.structured_content,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

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

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

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

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

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
        ('ommlds.specs.mcp.protocolold', 'CursorClientResult'),
    ),
)
def _process_dataclass__108625303d9cc86f36aa2da5265e213ac698f51f():
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
                next_cursor=self.next_cursor,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.next_cursor == other.next_cursor
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'next_cursor',
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
            'next_cursor',
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
                self.next_cursor,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            next_cursor: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'next_cursor', next_cursor)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"next_cursor={self.next_cursor!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

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
        ('ommlds.specs.mcp.protocolold', 'Implementation'),
    ),
)
def _process_dataclass__562f8e7e3d1263be9853f4a5c6ffd0a211afb158():
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
                name=self.name,
                version=self.version,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.name == other.name and
                self.version == other.version
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'name',
            'version',
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
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            name: __dataclass__init__fields__0__annotation,
            version: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'name', name)
            __dataclass__object_setattr(self, 'version', version)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

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

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

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
        ('ommlds.specs.mcp.protocolold', 'InitializeRequest'),
    ),
)
def _process_dataclass__dfa967e29d93ab10275d0ebd2618c39c2c967745():
    def _process_dataclass(
        *,
        __class__,
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
                client_info=self.client_info,
                protocol_version=self.protocol_version,
                capabilities=self.capabilities,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

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

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'json_rpc_method_name',
            'client_info',
            'protocol_version',
            'capabilities',
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
            'json_rpc_method_name',
            'client_info',
            'protocol_version',
            'capabilities',
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
                self.client_info,
                self.protocol_version,
                self.capabilities,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

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

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

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

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

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
        ('ommlds.specs.mcp.protocolold', 'InitializeResult'),
    ),
)
def _process_dataclass__6a4c93d451d52a62674673241fca7e7164f79af1():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__2__annotation,
        __dataclass__init__fields__3__annotation,
        __dataclass__init__fields__4__annotation,
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
                meta_=self.meta_,
                server_info=self.server_info,
                protocol_version=self.protocol_version,
                capabilities=self.capabilities,
                instructions=self.instructions,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

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

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

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
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

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
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

        def __hash__(self):
            return hash((
                self.meta_,
                self.server_info,
                self.protocol_version,
                self.capabilities,
                self.instructions,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

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

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

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

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

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
        ('ommlds.specs.mcp.protocolold', 'InitializedNotification'),
        ('ommlds.specs.mcp.protocolold', 'PingClientResult'),
        ('ommlds.specs.mcp.protocolold', 'PingServerResult'),
    ),
)
def _process_dataclass__ed35b9cf3e3cd1bf5b385570823394625579cf9d():
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

        __dataclass___setattr_frozen_fields = {
            'json_rpc_method_name',
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
            'json_rpc_method_name',
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
        ('ommlds.specs.mcp.protocolold', 'ListPromptsRequest'),
        ('ommlds.specs.mcp.protocolold', 'ListToolsRequest'),
    ),
)
def _process_dataclass__a1b41055ff58a2964f0e25aae5ad9515639a4d58():
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
                cursor=self.cursor,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.cursor == other.cursor
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'cursor',
            'json_rpc_method_name',
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
            'json_rpc_method_name',
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
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            cursor: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'cursor', cursor)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"cursor={self.cursor!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

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
        ('ommlds.specs.mcp.protocolold', 'ListPromptsResult'),
    ),
)
def _process_dataclass__4f9887cb1136aa1e731da1375b0df1156e0ab16b():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__init__fields__3__annotation,
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
                meta_=self.meta_,
                next_cursor=self.next_cursor,
                prompts=self.prompts,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

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

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'meta_',
            'next_cursor',
            'json_rpc_method_name',
            'prompts',
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
            'meta_',
            'next_cursor',
            'json_rpc_method_name',
            'prompts',
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
                self.meta_,
                self.next_cursor,
                self.prompts,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

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

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

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

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

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
        ('ommlds.specs.mcp.protocolold', 'ListToolsResult'),
    ),
)
def _process_dataclass__3a00e3d924bc002c85980317fcc32aaac988be1f():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
        __dataclass__init__fields__1__annotation,
        __dataclass__init__fields__1__default,
        __dataclass__init__fields__3__annotation,
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
                meta_=self.meta_,
                next_cursor=self.next_cursor,
                tools=self.tools,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

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

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'meta_',
            'next_cursor',
            'json_rpc_method_name',
            'tools',
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
            'meta_',
            'next_cursor',
            'json_rpc_method_name',
            'tools',
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
                self.meta_,
                self.next_cursor,
                self.tools,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

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

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

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
        ('ommlds.specs.mcp.protocolold', 'Message'),
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
        ('ommlds.specs.mcp.protocolold', 'PingClientRequest'),
        ('ommlds.specs.mcp.protocolold', 'PingServerRequest'),
    ),
)
def _process_dataclass__d7418a8cca2aa773c3a1ef3fa87a07dc73768748():
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
                meta_=self.meta_,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.meta_ == other.meta_
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'meta_',
            'json_rpc_method_name',
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
            'meta_',
            'json_rpc_method_name',
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
                self.meta_,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            meta_: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'meta_', meta_)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"meta_={self.meta_!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

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
        ('ommlds.specs.mcp.protocolold', 'Prompt'),
    ),
)
def _process_dataclass__2aa0c6160b68764b4737f79b76a7211fd320c708():
    def _process_dataclass(
        *,
        __class__,
        __dataclass__init__fields__0__annotation,
        __dataclass__init__fields__0__default,
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
                meta_=self.meta_,
                name=self.name,
                title=self.title,
                description=self.description,
                arguments=self.arguments,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

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

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'meta_',
            'name',
            'title',
            'description',
            'arguments',
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
            'meta_',
            'name',
            'title',
            'description',
            'arguments',
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
                self.meta_,
                self.name,
                self.title,
                self.description,
                self.arguments,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

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

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

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

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

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
        ('ommlds.specs.mcp.protocolold', 'PromptArgument'),
    ),
)
def _process_dataclass__f49ebe3867d8d04657e10bd99b1f1faf792e98ec():
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
                name=self.name,
                title=self.title,
                description=self.description,
                required=self.required,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

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

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'name',
            'title',
            'description',
            'required',
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
            'title',
            'description',
            'required',
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
                self.title,
                self.description,
                self.required,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

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

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

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

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

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
        ('ommlds.specs.mcp.protocolold', 'TextContentBlock'),
    ),
)
def _process_dataclass__981a3fd6730d2d619e2c7c14e7ef8cc88d193ce6():
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

        __dataclass___setattr_frozen_fields = {
            'text',
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
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            text: __dataclass__init__fields__0__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'text', text)

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
        ('ommlds.specs.mcp.protocolold', 'Tool'),
    ),
)
def _process_dataclass__71b741a91f4a3186af46caf3ce63596c7f62fa3f():
    def _process_dataclass(
        *,
        __class__,
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
                meta_=self.meta_,
                name=self.name,
                title=self.title,
                description=self.description,
                annotations=self.annotations,
                input_schema=self.input_schema,
                output_schema=self.output_schema,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

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

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

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
                type(self) is __class__
                or name in __dataclass___setattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot assign to field {name!r}")
            super(__class__, self).__setattr__(name, value)

        __dataclass__set_cls_attr(__class__, '__setattr__', __setattr__, 'raise', set_qualname=True)

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
                type(self) is __class__
                or name in __dataclass___delattr_frozen_fields
            ):
                raise __dataclass__FrozenInstanceError(f"cannot delete field {name!r}")
            super(__class__, self).__delattr__(name)

        __dataclass__set_cls_attr(__class__, '__delattr__', __delattr__, 'raise', set_qualname=True)

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

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

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

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

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

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

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
        ('ommlds.specs.mcp.protocolold', 'WithMeta'),
    ),
)
def _process_dataclass__b672ff406614f672ad0f891cad4e3a1cdeba7586():
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
                meta_=self.meta_,
            )

        __dataclass__set_cls_attr(__class__, '__copy__', __copy__, 'raise', set_qualname=True)

        def __eq__(self, other):
            if self is other:
                return True
            if self.__class__ is not other.__class__:
                return NotImplemented
            return (
                self.meta_ == other.meta_
            )

        __dataclass__set_cls_attr(__class__, '__eq__', __eq__, 'raise', set_qualname=True)

        __dataclass___setattr_frozen_fields = {
            'meta_',
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
            'meta_',
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
                self.meta_,
            ))

        __dataclass__set_cls_attr(__class__, '__hash__', __hash__, 'replace', set_qualname=True)

        def __init__(
            self,
            *,
            meta_: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'meta_', meta_)

        __dataclass__set_cls_attr(__class__, '__init__', __init__, 'raise', set_qualname=True)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"meta_={self.meta_!r}")
            return (
                f"{self.__class__.__qualname__}("
                f"{', '.join(parts)}"
                f")"
            )

        __dataclass__set_cls_attr(__class__, '__repr__', __repr__, 'raise', set_qualname=True)

    return _process_dataclass
