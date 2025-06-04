"""
FIXME:
 - late load marshal, late configure generic_replace
"""
import abc
import typing as ta

from omlish import check
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh
from omlish import typedvalues as tv


TypedValueT = ta.TypeVar('TypedValueT', bound=tv.TypedValue)

RequestT = ta.TypeVar('RequestT', bound='Request')
RequestT_contra = ta.TypeVar('RequestT_contra', bound='Request', contravariant=True)

ResponseT = ta.TypeVar('ResponseT', bound='Response')
ResponseT_co = ta.TypeVar('ResponseT_co', bound='Response', covariant=True)


##


class _ServiceTypedValuesHolder(tv.TypedValueGeneric[TypedValueT], lang.Abstract):
    _typed_values_base_cls: ta.ClassVar[type[tv.TypedValue]]

    #

    _typed_values_types: ta.ClassVar[tuple[type[tv.TypedValue], ...]]
    _typed_values_types_set: ta.ClassVar[frozenset[type[tv.TypedValue]]]

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        check.not_in('_typed_values_types', cls.__dict__)
        tvi_set = tv.reflect_typed_values_impls(cls._typed_value_type)
        cls._typed_values_types = tuple(sorted(
            [check.issubclass(c, cls._typed_values_base_cls) for c in tvi_set],
            key=lambda c: c.__qualname__,
        ))
        cls._typed_values_types_set = frozenset(cls._typed_values_types)

    #

    @property
    @abc.abstractmethod
    def _typed_values(self) -> tv.TypedValues[TypedValueT]:
        raise NotImplementedError

    #

    @dc.init
    def _check_typed_value_types(self) -> None:
        for o in self._typed_values:
            if type(o) not in self._typed_values_types_set and not isinstance(o, self._typed_values_types):
                raise TypeError(o)


_SERVICE_TYPED_VALUES_HOLDER_FIELD_METADATA: ta.Mapping = {
    **dc.extra_field_params(
        repr_fn=dc.truthy_repr,
        repr_priority=100,
    ),
    # FIXME:
    msh.FieldMetadata: msh.FieldMetadata(
        options=msh.FieldOptions(
            generic_replace=True,
        ),
    ),
}


##


class RequestOption(tv.TypedValue, lang.Abstract):
    pass


RequestOptionT = ta.TypeVar('RequestOptionT', bound=RequestOption)


@dc.dataclass(frozen=True)
class Request(_ServiceTypedValuesHolder[RequestOptionT], lang.Abstract):
    _typed_values_base_cls = RequestOption

    options: tv.TypedValues[RequestOptionT] = dc.field(
        default=tv.TypedValues.empty(),
        kw_only=True,
        metadata=_SERVICE_TYPED_VALUES_HOLDER_FIELD_METADATA,
    )

    @property
    def _typed_values(self) -> tv.TypedValues[RequestOptionT]:
        return self.options

    def with_options(
            self: RequestT,
            *options: RequestOptionT,
            override: bool = False,
    ) -> RequestT:
        return dc.replace(self, options=tv.TypedValues(
            *self.options,
            *options,
            override=override,
        ))

    #

    @classmethod
    def new(
            cls: type[RequestT],
            *args: ta.Any,
            options: tv.TypedValues[RequestOptionT] | None = None,
            **kwargs: ta.Any,
    ) -> RequestT:
        if not any(isinstance(a, RequestOption) for a in args):
            return cls(*args, **kwargs)

        arg_lst: list[ta.Any] = []
        opt_lst: list[RequestOption] | None = None
        for arg in args:
            if isinstance(arg, RequestOption):
                if opt_lst is None:
                    if options is not None:
                        opt_lst = list(options)
                    else:
                        opt_lst = []
                opt_lst.append(arg)
            else:
                arg_lst.append(arg)

        return cls(
            *arg_lst,
            **lang.opt_kw(options=tv.TypedValues(*opt_lst) if opt_lst is not None else None),
            **kwargs,
        )


##


class ResponseOutput(tv.TypedValue, lang.Abstract):
    pass


ResponseOutputT = ta.TypeVar('ResponseOutputT', bound=ResponseOutput)


@dc.dataclass(frozen=True)
class Response(_ServiceTypedValuesHolder[ResponseOutputT], lang.Abstract):
    _typed_values_base_cls = ResponseOutput

    outputs: tv.TypedValues[ResponseOutputT] = dc.field(
        default=tv.TypedValues.empty(),
        kw_only=True,
        metadata=_SERVICE_TYPED_VALUES_HOLDER_FIELD_METADATA,
    )

    @property
    def _typed_values(self) -> tv.TypedValues[ResponseOutputT]:
        return self.outputs

    def with_outputs(
            self: ResponseT,
            *outputs: ResponseOutputT,
            override: bool = False,
    ) -> ResponseT:
        return dc.replace(self, outputs=tv.TypedValues(
            *self.outputs,
            *outputs,
            override=override,
        ))


##


@ta.runtime_checkable
class Service(ta.Protocol[RequestT_contra, ResponseT_co]):
    def invoke(self, request: RequestT_contra) -> ResponseT_co: ...


##


@lang.protocol_check(Service)
class Service_(lang.Abstract, ta.Generic[RequestT, ResponseT]):  # noqa
    _service_request_cls: ta.ClassVar[type[Request]]
    _service_response_cls: ta.ClassVar[type[Response]]

    def __init_subclass__(
            cls,
            *,
            request: type[Request] | None = None,
            response: type[Response] | None = None,
            **kwargs: ta.Any,
    ) -> None:
        super().__init_subclass__(**kwargs)

        def set_svc_cls(a, v, b):
            if v is None:
                return
            check.not_in(a, cls.__dict__)
            check.issubclass(v, b)
            setattr(cls, a, v)

        set_svc_cls('_service_request_cls', request, Request)
        set_svc_cls('_service_response_cls', response, Response)

    @abc.abstractmethod
    def invoke(self, request: RequestT) -> ResponseT:
        raise NotImplementedError

    @ta.final
    def invoke_new(self, *args: ta.Any, **kwargs: ta.Any) -> ResponseT:
        req_cls: type[RequestT] = check.not_none(self._service_request_cls)  # type: ignore[assignment]

        req: ta.Any
        if not (args and isinstance(args[0], Request)):
            req = req_cls.new(*args, **kwargs)
            return self.invoke(req)

        req = args[0]
        if len(args) < 2 and not kwargs and isinstance(req, req_cls):
            return self.invoke(req)

        if not isinstance(req, req_cls):
            if type(req) not in req_cls.__bases__:
                raise TypeError(req)

        opt_args, val_args = col.partition(args[1:], lambda a: isinstance(a, RequestOption))
        check.empty(val_args)

        if opt_args:
            kwargs['options'] = tv.TypedValues(
                *kwargs.pop('options', req.options or []),
                *opt_args,
            )

        if not isinstance(req, req_cls):
            req_dct = dc.shallow_asdict(req)
            req = req_cls(**{
                **req_dct,
                **kwargs,
            })

        elif kwargs:
            req = dc.replace(req, **kwargs)

        return self.invoke(req)

    @ta.final
    def __call__(self, *args: ta.Any, **kwargs: ta.Any) -> ResponseT:
        return self.invoke_new(*args, **kwargs)
