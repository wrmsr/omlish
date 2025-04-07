import abc
import typing as ta

from omlish import check
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh
from omlish import typedvalues as tv


RequestOptionT = ta.TypeVar('RequestOptionT', bound='RequestOption')
RequestT = ta.TypeVar('RequestT', bound='Request')
RequestT_contra = ta.TypeVar('RequestT_contra', bound='Request', contravariant=True)

ResponseOutputT = ta.TypeVar('ResponseOutputT', bound='ResponseOutput')
ResponseT = ta.TypeVar('ResponseT', bound='Response')
ResponseT_co = ta.TypeVar('ResponseT_co', bound='Response', covariant=True)


##


class RequestOption(tv.TypedValue, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class Request(tv.TypedValueGeneric[RequestOptionT], lang.Abstract):
    _option_types: ta.ClassVar[tuple[type[RequestOption], ...]]
    _option_types_set: ta.ClassVar[frozenset[type[RequestOption]]]

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        check.not_in('_option_types', cls.__dict__)
        tvi_set = tv.reflect_typed_values_impls(cls._typed_value_type)
        cls._option_types = tuple(sorted(
            [check.issubclass(c, RequestOption) for c in tvi_set],  # type: ignore
            key=lambda c: c.__qualname__,
        ))
        cls._option_types_set = frozenset(cls._option_types)

    #

    options: tv.TypedValues[RequestOptionT] = dc.field(
        default=tv.TypedValues.empty(),
        kw_only=True,
        metadata={
            dc.FieldExtras: dc.FieldExtras(
                repr_fn=dc.truthy_repr,
                repr_priority=100,
            ),
            msh.FieldMetadata: msh.FieldMetadata(
                options=msh.FieldOptions(
                    generic_replace=True,
                ),
            ),
        },
    )

    @dc.init
    def _check_option_types(self) -> None:
        for o in self.options:
            if type(o) not in self._option_types_set and not isinstance(o, self._option_types):
                raise TypeError(o)

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


@dc.dataclass(frozen=True)
class Response(tv.TypedValueGeneric[ResponseOutputT], lang.Abstract):
    _output_types: ta.ClassVar[tuple[type[ResponseOutput], ...]]
    _output_types_set: ta.ClassVar[frozenset[type[ResponseOutput]]]

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        check.not_in('_output_types', cls.__dict__)
        tvi_set = tv.reflect_typed_values_impls(cls._typed_value_type)
        cls._output_types = tuple(sorted(
            [check.issubclass(c, ResponseOutput) for c in tvi_set],  # type: ignore
            key=lambda c: c.__qualname__,
        ))
        cls._output_types_set = frozenset(cls._output_types)

    #

    outputs: tv.TypedValues[ResponseOutputT] = dc.field(
        default=tv.TypedValues.empty(),
        kw_only=True,
        metadata={
            dc.FieldExtras: dc.FieldExtras(
                repr_fn=dc.truthy_repr,
                repr_priority=100,
            ),
            msh.FieldMetadata: msh.FieldMetadata(
                options=msh.FieldOptions(
                    generic_replace=True,
                ),
            ),
        },
    )

    @dc.init
    def _check_output_types(self) -> None:
        for o in self.outputs:
            if type(o) not in self._output_types_set and not isinstance(o, self._output_types):
                raise TypeError(o)

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
        if not args and not kwargs and isinstance(req, req_cls):
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
