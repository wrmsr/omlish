import abc
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import reflect as rfl

from .options import Option
from .options import Options


T = ta.TypeVar('T')
U = ta.TypeVar('U')
ServiceRequestT = ta.TypeVar('ServiceRequestT', bound='ServiceRequest')
ServiceOptionT = ta.TypeVar('ServiceOptionT', bound='Option')
ServiceNewT = ta.TypeVar('ServiceNewT')
ServiceResponseT = ta.TypeVar('ServiceResponseT', bound='ServiceResponse')


##


class ServiceOption(Option, lang.Abstract):
    pass


##


@dc.dataclass(frozen=True, kw_only=True)
class ServiceRequest(lang.Abstract, ta.Generic[T, ServiceOptionT, ServiceNewT]):
    v: T

    options: Options[ServiceOptionT] = dc.xfield(Options(), repr_fn=dc.truthy_repr)

    @classmethod
    def new(
            cls: type[U],
            v: ServiceNewT,
            *options: ServiceOptionT,
            **kwargs: ta.Any,
    ) -> U:
        return cls(
            v=v,  # type: ignore
            options=Options(*options),
            **kwargs,
        )


@dc.dataclass(frozen=True, kw_only=True)
class ServiceResponse(lang.Abstract, ta.Generic[T]):
    v: T


class Service(lang.Abstract, ta.Generic[ServiceRequestT, ServiceOptionT, ServiceNewT, ServiceResponseT]):
    # Not ClassVar - wrappers for example vary by instance.
    request_cls: type[ServiceRequest]
    option_cls_set: frozenset[type[Option]]
    new_cls: ta.Any
    response_cls: type[ServiceResponse]

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        if lang.is_abstract_class(cls):
            return

        gmro = rfl.ALIAS_UPDATING_GENERIC_SUBSTITUTION.generic_mro(cls)

        service_bases = [
            rb
            for rb in gmro
            if isinstance(rb, rfl.Generic)
            and rb.cls is Service
        ]
        if not service_bases:
            return

        service_base = check.single(service_bases)

        present_attr_ct = lang.ilen(
            a for a in (
                'request_cls',
                'option_cls_set',
                'new_cls',
                'response_cls',
            ) if hasattr(cls, a)
        )
        if present_attr_ct:
            if present_attr_ct != 4:
                raise AttributeError('Must set all service attrs if any set')
            return

        request_ann, option_ann, new_ann, response_ann = service_base.args

        request_cls: type[ServiceRequest] = check.issubclass(check.isinstance(request_ann, type), ServiceRequest)  # noqa
        response_cls: type[ServiceResponse] = check.issubclass(check.isinstance(response_ann, type), ServiceResponse)  # noqa
        new_cls: ta.Any = new_ann

        option_cls_set: frozenset[type[Option]]
        if isinstance(option_ann, rfl.Union):
            option_cls_set = frozenset(check.issubclass(check.isinstance(a, type), Option) for a in option_ann.args)  # noqa
        else:
            option_cls_set = frozenset([check.issubclass(check.isinstance(option_ann, type), Option)])  # noqa

        cls.request_cls = request_cls
        cls.option_cls_set = option_cls_set
        cls.new_cls = new_cls
        cls.response_cls = response_cls

    @abc.abstractmethod
    def invoke(self, request: ServiceRequestT) -> ServiceResponseT:
        raise NotImplementedError

    @ta.final
    def invoke_new(
            self,
            v: ServiceNewT,
            *options: ServiceOptionT,
            **kwargs: ta.Any,
    ) -> ServiceResponseT:
        request = self.request_cls.new(
            v,
            *options,
            **kwargs,
        )
        return self.invoke(ta.cast(ServiceRequestT, request))

    def __call__(
            self,
            v: ServiceNewT,
            *options: ServiceOptionT,
            **kwargs: ta.Any,
    ) -> ServiceResponseT:
        return self.invoke_new(v, *options, **kwargs)
