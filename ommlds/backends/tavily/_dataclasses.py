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
        "Plans(tup=(CopyPlan(fields=('urls', 'include_images', 'include_favicon', 'extract_depth', 'format', 'timeout')"
        "), EqPlan(fields=('urls', 'include_images', 'include_favicon', 'extract_depth', 'format', 'timeout')), FrozenP"
        "lan(fields=('urls', 'include_images', 'include_favicon', 'extract_depth', 'format', 'timeout'), allow_dynamic_"
        "dunder_attrs=False), HashPlan(action='add', fields=('urls', 'include_images', 'include_favicon', 'extract_dept"
        "h', 'format', 'timeout'), cache=False), InitPlan(fields=(InitPlan.Field(name='urls', annotation=OpRef(name='in"
        "it.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type=FieldType."
        "INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='include_images', annotation=OpRef"
        "(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init=Tru"
        "e, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field"
        "(name='include_favicon', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2."
        "default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valida"
        "te=None, check_type=None), InitPlan.Field(name='extract_depth', annotation=OpRef(name='init.fields.3.annotatio"
        "n'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, field_type="
        "FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='format', annotation=OpR"
        "ef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=T"
        "rue, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fie"
        "ld(name='timeout', annotation=OpRef(name='init.fields.5.annotation'), default=OpRef(name='init.fields.5.defaul"
        "t'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=Non"
        "e, check_type=None)), self_param='self', std_params=(), kw_only_params=('urls', 'include_images', 'include_fav"
        "icon', 'extract_depth', 'format', 'timeout'), frozen=True, slots=False, post_init_params=None, init_fns=(), va"
        "lidate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='urls', kw_only=True, fn=None), ReprPlan.Field(name='incl"
        "ude_images', kw_only=True, fn=None), ReprPlan.Field(name='include_favicon', kw_only=True, fn=None), ReprPlan.F"
        "ield(name='extract_depth', kw_only=True, fn=None), ReprPlan.Field(name='format', kw_only=True, fn=None), ReprP"
        "lan.Field(name='timeout', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='6ead422c0d2c606d1aad27cad5dfa1eb3a805e5b',
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
    ),
    cls_names=(
        ('ommlds.backends.tavily.protocol', 'ExtractRequest'),
    ),
)
def _process_dataclass__6ead422c0d2c606d1aad27cad5dfa1eb3a805e5b():
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
                urls=self.urls,
                include_images=self.include_images,
                include_favicon=self.include_favicon,
                extract_depth=self.extract_depth,
                format=self.format,
                timeout=self.timeout,
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
                self.urls == other.urls and
                self.include_images == other.include_images and
                self.include_favicon == other.include_favicon and
                self.extract_depth == other.extract_depth and
                self.format == other.format and
                self.timeout == other.timeout
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'urls',
            'include_images',
            'include_favicon',
            'extract_depth',
            'format',
            'timeout',
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
            'urls',
            'include_images',
            'include_favicon',
            'extract_depth',
            'format',
            'timeout',
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
                self.urls,
                self.include_images,
                self.include_favicon,
                self.extract_depth,
                self.format,
                self.timeout,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            urls: __dataclass__init__fields__0__annotation,
            include_images: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            include_favicon: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            extract_depth: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            format: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            timeout: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'urls', urls)
            __dataclass__object_setattr(self, 'include_images', include_images)
            __dataclass__object_setattr(self, 'include_favicon', include_favicon)
            __dataclass__object_setattr(self, 'extract_depth', extract_depth)
            __dataclass__object_setattr(self, 'format', format)
            __dataclass__object_setattr(self, 'timeout', timeout)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"urls={self.urls!r}")
            parts.append(f"include_images={self.include_images!r}")
            parts.append(f"include_favicon={self.include_favicon!r}")
            parts.append(f"extract_depth={self.extract_depth!r}")
            parts.append(f"format={self.format!r}")
            parts.append(f"timeout={self.timeout!r}")
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
        "Plans(tup=(CopyPlan(fields=('results', 'failed_results', 'response_time', 'request_id')), EqPlan(fields=('resu"
        "lts', 'failed_results', 'response_time', 'request_id')), FrozenPlan(fields=('results', 'failed_results', 'resp"
        "onse_time', 'request_id'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('results', 'faile"
        "d_results', 'response_time', 'request_id'), cache=False), InitPlan(fields=(InitPlan.Field(name='results', anno"
        "tation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, "
        "field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='failed_resul"
        "ts', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_f"
        "actory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type="
        "None), InitPlan.Field(name='response_time', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(n"
        "ame='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, "
        "coerce=None, validate=None, check_type=None), InitPlan.Field(name='request_id', annotation=OpRef(name='init.fi"
        "elds.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=Fa"
        "lse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_para"
        "ms=(), kw_only_params=('results', 'failed_results', 'response_time', 'request_id'), frozen=True, slots=False, "
        "post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='results', kw_only="
        "True, fn=None), ReprPlan.Field(name='failed_results', kw_only=True, fn=None), ReprPlan.Field(name='response_ti"
        "me', kw_only=True, fn=None), ReprPlan.Field(name='request_id', kw_only=True, fn=None)), id=False, terse=False,"
        " default_fn=None)))"
    ),
    plan_repr_sha1='3f646ce22fdfdf2263a93ac28fa615a485690a8c',
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
        ('ommlds.backends.tavily.protocol', 'ExtractResponse'),
    ),
)
def _process_dataclass__3f646ce22fdfdf2263a93ac28fa615a485690a8c():
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
                results=self.results,
                failed_results=self.failed_results,
                response_time=self.response_time,
                request_id=self.request_id,
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
                self.results == other.results and
                self.failed_results == other.failed_results and
                self.response_time == other.response_time and
                self.request_id == other.request_id
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'results',
            'failed_results',
            'response_time',
            'request_id',
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
            'results',
            'failed_results',
            'response_time',
            'request_id',
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
                self.results,
                self.failed_results,
                self.response_time,
                self.request_id,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            results: __dataclass__init__fields__0__annotation,
            failed_results: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            response_time: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            request_id: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'results', results)
            __dataclass__object_setattr(self, 'failed_results', failed_results)
            __dataclass__object_setattr(self, 'response_time', response_time)
            __dataclass__object_setattr(self, 'request_id', request_id)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"results={self.results!r}")
            parts.append(f"failed_results={self.failed_results!r}")
            parts.append(f"response_time={self.response_time!r}")
            parts.append(f"request_id={self.request_id!r}")
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
        "Plans(tup=(CopyPlan(fields=('url', 'error')), EqPlan(fields=('url', 'error')), FrozenPlan(fields=('url', 'erro"
        "r'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('url', 'error'), cache=False), InitPlan"
        "(fields=(InitPlan.Field(name='url', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_f"
        "actory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type="
        "None), InitPlan.Field(name='error', annotation=OpRef(name='init.fields.1.annotation'), default=None, default_f"
        "actory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type="
        "None)), self_param='self', std_params=(), kw_only_params=('url', 'error'), frozen=True, slots=False, post_init"
        "_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='url', kw_only=True, fn=None"
        "), ReprPlan.Field(name='error', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='c306872e8ff160b080e380e285ae8e74db96cc63',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
    ),
    cls_names=(
        ('ommlds.backends.tavily.protocol', 'ExtractResponse.FailedResult'),
    ),
)
def _process_dataclass__c306872e8ff160b080e380e285ae8e74db96cc63():
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
                url=self.url,
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
                self.url == other.url and
                self.error == other.error
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'url',
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
            'url',
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
                self.url,
                self.error,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            url: __dataclass__init__fields__0__annotation,
            error: __dataclass__init__fields__1__annotation,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'url', url)
            __dataclass__object_setattr(self, 'error', error)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"url={self.url!r}")
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
        "Plans(tup=(CopyPlan(fields=('url', 'raw_content', 'images', 'favicon')), EqPlan(fields=('url', 'raw_content', "
        "'images', 'favicon')), FrozenPlan(fields=('url', 'raw_content', 'images', 'favicon'), allow_dynamic_dunder_att"
        "rs=False), HashPlan(action='add', fields=('url', 'raw_content', 'images', 'favicon'), cache=False), InitPlan(f"
        "ields=(InitPlan.Field(name='url', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_fac"
        "tory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=No"
        "ne), InitPlan.Field(name='raw_content', annotation=OpRef(name='init.fields.1.annotation'), default=None, defau"
        "lt_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_t"
        "ype=None), InitPlan.Field(name='images', annotation=OpRef(name='init.fields.2.annotation'), default=OpRef(name"
        "='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coe"
        "rce=None, validate=None, check_type=None), InitPlan.Field(name='favicon', annotation=OpRef(name='init.fields.3"
        ".annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=True, override=False, f"
        "ield_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(),"
        " kw_only_params=('url', 'raw_content', 'images', 'favicon'), frozen=True, slots=False, post_init_params=None, "
        "init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='url', kw_only=True, fn=None), ReprPlan.Fi"
        "eld(name='raw_content', kw_only=True, fn=None), ReprPlan.Field(name='images', kw_only=True, fn=None), ReprPlan"
        ".Field(name='favicon', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='97f06c15926ba4bb103416285c597e19032efb28',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__2__annotation',
        '__dataclass__init__fields__2__default',
        '__dataclass__init__fields__3__annotation',
        '__dataclass__init__fields__3__default',
    ),
    cls_names=(
        ('ommlds.backends.tavily.protocol', 'ExtractResponse.Result'),
    ),
)
def _process_dataclass__97f06c15926ba4bb103416285c597e19032efb28():
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
                url=self.url,
                raw_content=self.raw_content,
                images=self.images,
                favicon=self.favicon,
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
                self.url == other.url and
                self.raw_content == other.raw_content and
                self.images == other.images and
                self.favicon == other.favicon
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'url',
            'raw_content',
            'images',
            'favicon',
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
            'url',
            'raw_content',
            'images',
            'favicon',
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
                self.url,
                self.raw_content,
                self.images,
                self.favicon,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            url: __dataclass__init__fields__0__annotation,
            raw_content: __dataclass__init__fields__1__annotation,
            images: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            favicon: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'url', url)
            __dataclass__object_setattr(self, 'raw_content', raw_content)
            __dataclass__object_setattr(self, 'images', images)
            __dataclass__object_setattr(self, 'favicon', favicon)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"url={self.url!r}")
            parts.append(f"raw_content={self.raw_content!r}")
            parts.append(f"images={self.images!r}")
            parts.append(f"favicon={self.favicon!r}")
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
        "Plans(tup=(CopyPlan(fields=('query', 'auto_parameters', 'topic', 'search_depth', 'chunks_per_source', 'max_res"
        "ults', 'time_range', 'start_date', 'end_date', 'include_answer', 'include_raw_content', 'include_images', 'inc"
        "lude_image_descriptions', 'include_favicon', 'include_domains', 'exclude_domains', 'country')), EqPlan(fields="
        "('query', 'auto_parameters', 'topic', 'search_depth', 'chunks_per_source', 'max_results', 'time_range', 'start"
        "_date', 'end_date', 'include_answer', 'include_raw_content', 'include_images', 'include_image_descriptions', '"
        "include_favicon', 'include_domains', 'exclude_domains', 'country')), FrozenPlan(fields=('query', 'auto_paramet"
        "ers', 'topic', 'search_depth', 'chunks_per_source', 'max_results', 'time_range', 'start_date', 'end_date', 'in"
        "clude_answer', 'include_raw_content', 'include_images', 'include_image_descriptions', 'include_favicon', 'incl"
        "ude_domains', 'exclude_domains', 'country'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields="
        "('query', 'auto_parameters', 'topic', 'search_depth', 'chunks_per_source', 'max_results', 'time_range', 'start"
        "_date', 'end_date', 'include_answer', 'include_raw_content', 'include_images', 'include_image_descriptions', '"
        "include_favicon', 'include_domains', 'exclude_domains', 'country'), cache=False), InitPlan(fields=(InitPlan.Fi"
        "eld(name='query', annotation=OpRef(name='init.fields.0.annotation'), default=None, default_factory=None, init="
        "True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fi"
        "eld(name='auto_parameters', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fields"
        ".1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, val"
        "idate=None, check_type=None), InitPlan.Field(name='topic', annotation=OpRef(name='init.fields.2.annotation'), "
        "default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_type=Field"
        "Type.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='search_depth', annotation=Op"
        "Ref(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init="
        "True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fi"
        "eld(name='chunks_per_source', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fiel"
        "ds.4.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, v"
        "alidate=None, check_type=None), InitPlan.Field(name='max_results', annotation=OpRef(name='init.fields.5.annota"
        "tion'), default=OpRef(name='init.fields.5.default'), default_factory=None, init=True, override=False, field_ty"
        "pe=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='time_range', annotat"
        "ion=OpRef(name='init.fields.6.annotation'), default=OpRef(name='init.fields.6.default'), default_factory=None,"
        " init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitP"
        "lan.Field(name='start_date', annotation=OpRef(name='init.fields.7.annotation'), default=OpRef(name='init.field"
        "s.7.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, va"
        "lidate=None, check_type=None), InitPlan.Field(name='end_date', annotation=OpRef(name='init.fields.8.annotation"
        "'), default=OpRef(name='init.fields.8.default'), default_factory=None, init=True, override=False, field_type=F"
        "ieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='include_answer', annotat"
        "ion=OpRef(name='init.fields.9.annotation'), default=OpRef(name='init.fields.9.default'), default_factory=None,"
        " init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitP"
        "lan.Field(name='include_raw_content', annotation=OpRef(name='init.fields.10.annotation'), default=OpRef(name='"
        "init.fields.10.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coer"
        "ce=None, validate=None, check_type=None), InitPlan.Field(name='include_images', annotation=OpRef(name='init.fi"
        "elds.11.annotation'), default=OpRef(name='init.fields.11.default'), default_factory=None, init=True, override="
        "False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='inclu"
        "de_image_descriptions', annotation=OpRef(name='init.fields.12.annotation'), default=OpRef(name='init.fields.12"
        ".default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, valid"
        "ate=None, check_type=None), InitPlan.Field(name='include_favicon', annotation=OpRef(name='init.fields.13.annot"
        "ation'), default=OpRef(name='init.fields.13.default'), default_factory=None, init=True, override=False, field_"
        "type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='include_domains', "
        "annotation=OpRef(name='init.fields.14.annotation'), default=OpRef(name='init.fields.14.default'), default_fact"
        "ory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=Non"
        "e), InitPlan.Field(name='exclude_domains', annotation=OpRef(name='init.fields.15.annotation'), default=OpRef(n"
        "ame='init.fields.15.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE,"
        " coerce=None, validate=None, check_type=None), InitPlan.Field(name='country', annotation=OpRef(name='init.fiel"
        "ds.16.annotation'), default=OpRef(name='init.fields.16.default'), default_factory=None, init=True, override=Fa"
        "lse, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_para"
        "ms=(), kw_only_params=('query', 'auto_parameters', 'topic', 'search_depth', 'chunks_per_source', 'max_results'"
        ", 'time_range', 'start_date', 'end_date', 'include_answer', 'include_raw_content', 'include_images', 'include_"
        "image_descriptions', 'include_favicon', 'include_domains', 'exclude_domains', 'country'), frozen=True, slots=F"
        "alse, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='query', kw_o"
        "nly=True, fn=None), ReprPlan.Field(name='auto_parameters', kw_only=True, fn=None), ReprPlan.Field(name='topic'"
        ", kw_only=True, fn=None), ReprPlan.Field(name='search_depth', kw_only=True, fn=None), ReprPlan.Field(name='chu"
        "nks_per_source', kw_only=True, fn=None), ReprPlan.Field(name='max_results', kw_only=True, fn=None), ReprPlan.F"
        "ield(name='time_range', kw_only=True, fn=None), ReprPlan.Field(name='start_date', kw_only=True, fn=None), Repr"
        "Plan.Field(name='end_date', kw_only=True, fn=None), ReprPlan.Field(name='include_answer', kw_only=True, fn=Non"
        "e), ReprPlan.Field(name='include_raw_content', kw_only=True, fn=None), ReprPlan.Field(name='include_images', k"
        "w_only=True, fn=None), ReprPlan.Field(name='include_image_descriptions', kw_only=True, fn=None), ReprPlan.Fiel"
        "d(name='include_favicon', kw_only=True, fn=None), ReprPlan.Field(name='include_domains', kw_only=True, fn=None"
        "), ReprPlan.Field(name='exclude_domains', kw_only=True, fn=None), ReprPlan.Field(name='country', kw_only=True,"
        " fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='bd96288940e857f7d97cf10301452de930241668',
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
        ('ommlds.backends.tavily.protocol', 'SearchRequest'),
    ),
)
def _process_dataclass__bd96288940e857f7d97cf10301452de930241668():
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
                query=self.query,
                auto_parameters=self.auto_parameters,
                topic=self.topic,
                search_depth=self.search_depth,
                chunks_per_source=self.chunks_per_source,
                max_results=self.max_results,
                time_range=self.time_range,
                start_date=self.start_date,
                end_date=self.end_date,
                include_answer=self.include_answer,
                include_raw_content=self.include_raw_content,
                include_images=self.include_images,
                include_image_descriptions=self.include_image_descriptions,
                include_favicon=self.include_favicon,
                include_domains=self.include_domains,
                exclude_domains=self.exclude_domains,
                country=self.country,
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
                self.query == other.query and
                self.auto_parameters == other.auto_parameters and
                self.topic == other.topic and
                self.search_depth == other.search_depth and
                self.chunks_per_source == other.chunks_per_source and
                self.max_results == other.max_results and
                self.time_range == other.time_range and
                self.start_date == other.start_date and
                self.end_date == other.end_date and
                self.include_answer == other.include_answer and
                self.include_raw_content == other.include_raw_content and
                self.include_images == other.include_images and
                self.include_image_descriptions == other.include_image_descriptions and
                self.include_favicon == other.include_favicon and
                self.include_domains == other.include_domains and
                self.exclude_domains == other.exclude_domains and
                self.country == other.country
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'query',
            'auto_parameters',
            'topic',
            'search_depth',
            'chunks_per_source',
            'max_results',
            'time_range',
            'start_date',
            'end_date',
            'include_answer',
            'include_raw_content',
            'include_images',
            'include_image_descriptions',
            'include_favicon',
            'include_domains',
            'exclude_domains',
            'country',
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
            'query',
            'auto_parameters',
            'topic',
            'search_depth',
            'chunks_per_source',
            'max_results',
            'time_range',
            'start_date',
            'end_date',
            'include_answer',
            'include_raw_content',
            'include_images',
            'include_image_descriptions',
            'include_favicon',
            'include_domains',
            'exclude_domains',
            'country',
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
                self.query,
                self.auto_parameters,
                self.topic,
                self.search_depth,
                self.chunks_per_source,
                self.max_results,
                self.time_range,
                self.start_date,
                self.end_date,
                self.include_answer,
                self.include_raw_content,
                self.include_images,
                self.include_image_descriptions,
                self.include_favicon,
                self.include_domains,
                self.exclude_domains,
                self.country,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            query: __dataclass__init__fields__0__annotation,
            auto_parameters: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            topic: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            search_depth: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            chunks_per_source: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            max_results: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
            time_range: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
            start_date: __dataclass__init__fields__7__annotation = __dataclass__init__fields__7__default,
            end_date: __dataclass__init__fields__8__annotation = __dataclass__init__fields__8__default,
            include_answer: __dataclass__init__fields__9__annotation = __dataclass__init__fields__9__default,
            include_raw_content: __dataclass__init__fields__10__annotation = __dataclass__init__fields__10__default,
            include_images: __dataclass__init__fields__11__annotation = __dataclass__init__fields__11__default,
            include_image_descriptions: __dataclass__init__fields__12__annotation = __dataclass__init__fields__12__default,
            include_favicon: __dataclass__init__fields__13__annotation = __dataclass__init__fields__13__default,
            include_domains: __dataclass__init__fields__14__annotation = __dataclass__init__fields__14__default,
            exclude_domains: __dataclass__init__fields__15__annotation = __dataclass__init__fields__15__default,
            country: __dataclass__init__fields__16__annotation = __dataclass__init__fields__16__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'query', query)
            __dataclass__object_setattr(self, 'auto_parameters', auto_parameters)
            __dataclass__object_setattr(self, 'topic', topic)
            __dataclass__object_setattr(self, 'search_depth', search_depth)
            __dataclass__object_setattr(self, 'chunks_per_source', chunks_per_source)
            __dataclass__object_setattr(self, 'max_results', max_results)
            __dataclass__object_setattr(self, 'time_range', time_range)
            __dataclass__object_setattr(self, 'start_date', start_date)
            __dataclass__object_setattr(self, 'end_date', end_date)
            __dataclass__object_setattr(self, 'include_answer', include_answer)
            __dataclass__object_setattr(self, 'include_raw_content', include_raw_content)
            __dataclass__object_setattr(self, 'include_images', include_images)
            __dataclass__object_setattr(self, 'include_image_descriptions', include_image_descriptions)
            __dataclass__object_setattr(self, 'include_favicon', include_favicon)
            __dataclass__object_setattr(self, 'include_domains', include_domains)
            __dataclass__object_setattr(self, 'exclude_domains', exclude_domains)
            __dataclass__object_setattr(self, 'country', country)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"query={self.query!r}")
            parts.append(f"auto_parameters={self.auto_parameters!r}")
            parts.append(f"topic={self.topic!r}")
            parts.append(f"search_depth={self.search_depth!r}")
            parts.append(f"chunks_per_source={self.chunks_per_source!r}")
            parts.append(f"max_results={self.max_results!r}")
            parts.append(f"time_range={self.time_range!r}")
            parts.append(f"start_date={self.start_date!r}")
            parts.append(f"end_date={self.end_date!r}")
            parts.append(f"include_answer={self.include_answer!r}")
            parts.append(f"include_raw_content={self.include_raw_content!r}")
            parts.append(f"include_images={self.include_images!r}")
            parts.append(f"include_image_descriptions={self.include_image_descriptions!r}")
            parts.append(f"include_favicon={self.include_favicon!r}")
            parts.append(f"include_domains={self.include_domains!r}")
            parts.append(f"exclude_domains={self.exclude_domains!r}")
            parts.append(f"country={self.country!r}")
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
        "Plans(tup=(CopyPlan(fields=('query', 'answer', 'images', 'results', 'follow_up_questions', 'auto_parameters', "
        "'response_time', 'request_id')), EqPlan(fields=('query', 'answer', 'images', 'results', 'follow_up_questions',"
        " 'auto_parameters', 'response_time', 'request_id')), FrozenPlan(fields=('query', 'answer', 'images', 'results'"
        ", 'follow_up_questions', 'auto_parameters', 'response_time', 'request_id'), allow_dynamic_dunder_attrs=False),"
        " HashPlan(action='add', fields=('query', 'answer', 'images', 'results', 'follow_up_questions', 'auto_parameter"
        "s', 'response_time', 'request_id'), cache=False), InitPlan(fields=(InitPlan.Field(name='query', annotation=OpR"
        "ef(name='init.fields.0.annotation'), default=None, default_factory=None, init=True, override=False, field_type"
        "=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='answer', annotation=Op"
        "Ref(name='init.fields.1.annotation'), default=None, default_factory=None, init=True, override=False, field_typ"
        "e=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='images', annotation=O"
        "pRef(name='init.fields.2.annotation'), default=OpRef(name='init.fields.2.default'), default_factory=None, init"
        "=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.F"
        "ield(name='results', annotation=OpRef(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.defa"
        "ult'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=N"
        "one, check_type=None), InitPlan.Field(name='follow_up_questions', annotation=OpRef(name='init.fields.4.annotat"
        "ion'), default=OpRef(name='init.fields.4.default'), default_factory=None, init=True, override=False, field_typ"
        "e=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='auto_parameters', ann"
        "otation=OpRef(name='init.fields.5.annotation'), default=OpRef(name='init.fields.5.default'), default_factory=N"
        "one, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), I"
        "nitPlan.Field(name='response_time', annotation=OpRef(name='init.fields.6.annotation'), default=OpRef(name='ini"
        "t.fields.6.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=N"
        "one, validate=None, check_type=None), InitPlan.Field(name='request_id', annotation=OpRef(name='init.fields.7.a"
        "nnotation'), default=OpRef(name='init.fields.7.default'), default_factory=None, init=True, override=False, fie"
        "ld_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), k"
        "w_only_params=('query', 'answer', 'images', 'results', 'follow_up_questions', 'auto_parameters', 'response_tim"
        "e', 'request_id'), frozen=True, slots=False, post_init_params=None, init_fns=(), validate_fns=()), ReprPlan(fi"
        "elds=(ReprPlan.Field(name='query', kw_only=True, fn=None), ReprPlan.Field(name='answer', kw_only=True, fn=None"
        "), ReprPlan.Field(name='images', kw_only=True, fn=None), ReprPlan.Field(name='results', kw_only=True, fn=None)"
        ", ReprPlan.Field(name='follow_up_questions', kw_only=True, fn=None), ReprPlan.Field(name='auto_parameters', kw"
        "_only=True, fn=None), ReprPlan.Field(name='response_time', kw_only=True, fn=None), ReprPlan.Field(name='reques"
        "t_id', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='6e49d9453b568b6b35d19ff897f810414abc4b2a',
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
        ('ommlds.backends.tavily.protocol', 'SearchResponse'),
    ),
)
def _process_dataclass__6e49d9453b568b6b35d19ff897f810414abc4b2a():
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
                query=self.query,
                answer=self.answer,
                images=self.images,
                results=self.results,
                follow_up_questions=self.follow_up_questions,
                auto_parameters=self.auto_parameters,
                response_time=self.response_time,
                request_id=self.request_id,
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
                self.query == other.query and
                self.answer == other.answer and
                self.images == other.images and
                self.results == other.results and
                self.follow_up_questions == other.follow_up_questions and
                self.auto_parameters == other.auto_parameters and
                self.response_time == other.response_time and
                self.request_id == other.request_id
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'query',
            'answer',
            'images',
            'results',
            'follow_up_questions',
            'auto_parameters',
            'response_time',
            'request_id',
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
            'query',
            'answer',
            'images',
            'results',
            'follow_up_questions',
            'auto_parameters',
            'response_time',
            'request_id',
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
                self.query,
                self.answer,
                self.images,
                self.results,
                self.follow_up_questions,
                self.auto_parameters,
                self.response_time,
                self.request_id,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            query: __dataclass__init__fields__0__annotation,
            answer: __dataclass__init__fields__1__annotation,
            images: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            results: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            follow_up_questions: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            auto_parameters: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
            response_time: __dataclass__init__fields__6__annotation = __dataclass__init__fields__6__default,
            request_id: __dataclass__init__fields__7__annotation = __dataclass__init__fields__7__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'query', query)
            __dataclass__object_setattr(self, 'answer', answer)
            __dataclass__object_setattr(self, 'images', images)
            __dataclass__object_setattr(self, 'results', results)
            __dataclass__object_setattr(self, 'follow_up_questions', follow_up_questions)
            __dataclass__object_setattr(self, 'auto_parameters', auto_parameters)
            __dataclass__object_setattr(self, 'response_time', response_time)
            __dataclass__object_setattr(self, 'request_id', request_id)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"query={self.query!r}")
            parts.append(f"answer={self.answer!r}")
            parts.append(f"images={self.images!r}")
            parts.append(f"results={self.results!r}")
            parts.append(f"follow_up_questions={self.follow_up_questions!r}")
            parts.append(f"auto_parameters={self.auto_parameters!r}")
            parts.append(f"response_time={self.response_time!r}")
            parts.append(f"request_id={self.request_id!r}")
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
        "Plans(tup=(CopyPlan(fields=('url', 'description')), EqPlan(fields=('url', 'description')), FrozenPlan(fields=("
        "'url', 'description'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('url', 'description')"
        ", cache=False), InitPlan(fields=(InitPlan.Field(name='url', annotation=OpRef(name='init.fields.0.annotation'),"
        " default=OpRef(name='init.fields.0.default'), default_factory=None, init=True, override=False, field_type=Fiel"
        "dType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='description', annotation=Op"
        "Ref(name='init.fields.1.annotation'), default=OpRef(name='init.fields.1.default'), default_factory=None, init="
        "True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None)), self_param"
        "='self', std_params=(), kw_only_params=('url', 'description'), frozen=True, slots=False, post_init_params=None"
        ", init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='url', kw_only=True, fn=None), ReprPlan."
        "Field(name='description', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='7ea40ca3c340a71cd7f76429b1c7d7df19dd83f5',
    op_ref_idents=(
        '__dataclass__init__fields__0__annotation',
        '__dataclass__init__fields__0__default',
        '__dataclass__init__fields__1__annotation',
        '__dataclass__init__fields__1__default',
    ),
    cls_names=(
        ('ommlds.backends.tavily.protocol', 'SearchResponse.Image'),
    ),
)
def _process_dataclass__7ea40ca3c340a71cd7f76429b1c7d7df19dd83f5():
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
                url=self.url,
                description=self.description,
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
                self.url == other.url and
                self.description == other.description
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'url',
            'description',
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
            'url',
            'description',
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
                self.url,
                self.description,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            url: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            description: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'url', url)
            __dataclass__object_setattr(self, 'description', description)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"url={self.url!r}")
            parts.append(f"description={self.description!r}")
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
        "Plans(tup=(CopyPlan(fields=('title', 'url', 'content', 'score', 'raw_content', 'favicon')), EqPlan(fields=('ti"
        "tle', 'url', 'content', 'score', 'raw_content', 'favicon')), FrozenPlan(fields=('title', 'url', 'content', 'sc"
        "ore', 'raw_content', 'favicon'), allow_dynamic_dunder_attrs=False), HashPlan(action='add', fields=('title', 'u"
        "rl', 'content', 'score', 'raw_content', 'favicon'), cache=False), InitPlan(fields=(InitPlan.Field(name='title'"
        ", annotation=OpRef(name='init.fields.0.annotation'), default=OpRef(name='init.fields.0.default'), default_fact"
        "ory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=Non"
        "e), InitPlan.Field(name='url', annotation=OpRef(name='init.fields.1.annotation'), default=OpRef(name='init.fie"
        "lds.1.default'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, "
        "validate=None, check_type=None), InitPlan.Field(name='content', annotation=OpRef(name='init.fields.2.annotatio"
        "n'), default=OpRef(name='init.fields.2.default'), default_factory=None, init=True, override=False, field_type="
        "FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Field(name='score', annotation=OpRe"
        "f(name='init.fields.3.annotation'), default=OpRef(name='init.fields.3.default'), default_factory=None, init=Tr"
        "ue, override=False, field_type=FieldType.INSTANCE, coerce=None, validate=None, check_type=None), InitPlan.Fiel"
        "d(name='raw_content', annotation=OpRef(name='init.fields.4.annotation'), default=OpRef(name='init.fields.4.def"
        "ault'), default_factory=None, init=True, override=False, field_type=FieldType.INSTANCE, coerce=None, validate="
        "None, check_type=None), InitPlan.Field(name='favicon', annotation=OpRef(name='init.fields.5.annotation'), defa"
        "ult=OpRef(name='init.fields.5.default'), default_factory=None, init=True, override=False, field_type=FieldType"
        ".INSTANCE, coerce=None, validate=None, check_type=None)), self_param='self', std_params=(), kw_only_params=('t"
        "itle', 'url', 'content', 'score', 'raw_content', 'favicon'), frozen=True, slots=False, post_init_params=None, "
        "init_fns=(), validate_fns=()), ReprPlan(fields=(ReprPlan.Field(name='title', kw_only=True, fn=None), ReprPlan."
        "Field(name='url', kw_only=True, fn=None), ReprPlan.Field(name='content', kw_only=True, fn=None), ReprPlan.Fiel"
        "d(name='score', kw_only=True, fn=None), ReprPlan.Field(name='raw_content', kw_only=True, fn=None), ReprPlan.Fi"
        "eld(name='favicon', kw_only=True, fn=None)), id=False, terse=False, default_fn=None)))"
    ),
    plan_repr_sha1='159d324c21b5646307b1510d34746f88b98697be',
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
        ('ommlds.backends.tavily.protocol', 'SearchResponse.Result'),
    ),
)
def _process_dataclass__159d324c21b5646307b1510d34746f88b98697be():
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
                title=self.title,
                url=self.url,
                content=self.content,
                score=self.score,
                raw_content=self.raw_content,
                favicon=self.favicon,
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
                self.title == other.title and
                self.url == other.url and
                self.content == other.content and
                self.score == other.score and
                self.raw_content == other.raw_content and
                self.favicon == other.favicon
            )

        __eq__.__qualname__ = f"{__dataclass__cls.__qualname__}.__eq__"
        if '__eq__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __eq__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__eq__', __eq__)

        __dataclass___setattr_frozen_fields = {
            'title',
            'url',
            'content',
            'score',
            'raw_content',
            'favicon',
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
            'title',
            'url',
            'content',
            'score',
            'raw_content',
            'favicon',
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
                self.title,
                self.url,
                self.content,
                self.score,
                self.raw_content,
                self.favicon,
            ))

        __hash__.__qualname__ = f"{__dataclass__cls.__qualname__}.__hash__"
        setattr(__dataclass__cls, '__hash__', __hash__)

        def __init__(
            self,
            *,
            title: __dataclass__init__fields__0__annotation = __dataclass__init__fields__0__default,
            url: __dataclass__init__fields__1__annotation = __dataclass__init__fields__1__default,
            content: __dataclass__init__fields__2__annotation = __dataclass__init__fields__2__default,
            score: __dataclass__init__fields__3__annotation = __dataclass__init__fields__3__default,
            raw_content: __dataclass__init__fields__4__annotation = __dataclass__init__fields__4__default,
            favicon: __dataclass__init__fields__5__annotation = __dataclass__init__fields__5__default,
        ) -> __dataclass__None:
            __dataclass__object_setattr(self, 'title', title)
            __dataclass__object_setattr(self, 'url', url)
            __dataclass__object_setattr(self, 'content', content)
            __dataclass__object_setattr(self, 'score', score)
            __dataclass__object_setattr(self, 'raw_content', raw_content)
            __dataclass__object_setattr(self, 'favicon', favicon)

        __init__.__qualname__ = f"{__dataclass__cls.__qualname__}.__init__"
        if '__init__' in __dataclass__cls.__dict__:
            raise __dataclass__TypeError(f"Cannot overwrite attribute __init__ in class {__dataclass__cls.__name__}")
        setattr(__dataclass__cls, '__init__', __init__)

        @__dataclass___recursive_repr()
        def __repr__(self):
            parts = []
            parts.append(f"title={self.title!r}")
            parts.append(f"url={self.url!r}")
            parts.append(f"content={self.content!r}")
            parts.append(f"score={self.score!r}")
            parts.append(f"raw_content={self.raw_content!r}")
            parts.append(f"favicon={self.favicon!r}")
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
