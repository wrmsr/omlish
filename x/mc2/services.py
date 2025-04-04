import abc
import typing as ta

from omlish import check
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang
from omlish import typedvalues as tv


T = ta.TypeVar('T')

RequestOptionT = ta.TypeVar('RequestOptionT', bound='RequestOption')
RequestT = ta.TypeVar('RequestT', bound='Request')
RequestT_contra = ta.TypeVar('RequestT_contra', bound='Request', contravariant=True)

ResponseOutputT = ta.TypeVar('ResponseOutputT', bound='ResponseOutput')
ResponseT = ta.TypeVar('ResponseT', bound='Response')
ResponseT_co = ta.TypeVar('ResponseT_co', bound='Response', covariant=True)


##


class RequestOption(tv.TypedValue, lang.Abstract):
    pass


class ScalarRequestOption(tv.ScalarTypedValue[T], RequestOption, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class Request(tv.TypedValueHolder[RequestOptionT], lang.Abstract):
    options: tv.TypedValues[RequestOptionT] | None = dc.field(
        default=None,
        kw_only=True,
        metadata={
            dc.FieldExtras: dc.FieldExtras(
                repr_fn=lang.opt_repr,
                repr_priority=100,
            ),
        },
    )

    def with_options(self: RequestT, *options: RequestOptionT) -> RequestT:
        return dc.replace(self, options=tv.TypedValues(
            *(self.options or []),
            *options,
        ))

    @property
    def _typed_values(self) -> tv.TypedValues[RequestOptionT] | None:
        return self.options

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
            options=tv.TypedValues(*opt_lst) if opt_lst is not None else None,
            **kwargs,
        )


##


class ResponseOutput(tv.TypedValue, lang.Abstract):
    pass


class ScalarResponseOutput(tv.ScalarTypedValue[T], ResponseOutput, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class Response(tv.TypedValueHolder[ResponseOutputT], lang.Abstract):
    outputs: tv.TypedValues[ResponseOutputT] | None = dc.field(
        default=None,
        kw_only=True,
        metadata={
            dc.FieldExtras: dc.FieldExtras(
                repr_fn=lang.opt_repr,
                repr_priority=100,
            ),
        },
    )

    def with_outputs(self: ResponseT, *outputs: ResponseOutputT) -> ResponseT:
        return dc.replace(self, outputs=tv.TypedValues(
            *(self.outputs or []),
            *outputs,
        ))

    @property
    def _typed_values(self) -> tv.TypedValues[ResponseOutputT] | None:
        return self.outputs


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

        req: RequestT
        if not (args and isinstance(args[0], Request)):
            req = req_cls.new(*args, **kwargs)
            return self.invoke(req)

        req = check.isinstance(args[0], req_cls)
        if not args and not kwargs:
            return self.invoke(req)

        val_args, opt_args = col.partition(args, lambda a: isinstance(a, RequestOption))
        check.empty(val_args)

        if opt_args:
            kwargs['options'] = tv.TypedValues(
                *kwargs.pop('options', req.options or []),
                *opt_args,
            )

        if kwargs:
            req = dc.replace(req, **kwargs)

        return self.invoke(req)

    @ta.final
    def __call__(self, *args: ta.Any, **kwargs: ta.Any) -> ResponseT:
        return self.invoke_new(*args, **kwargs)
