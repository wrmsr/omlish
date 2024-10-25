import abc
import enum
import typing as ta

from omlish import check
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang
from omlish import reflect as rfl

from .options import Option
from .options import Options


T = ta.TypeVar('T')
U = ta.TypeVar('U')
RequestT = ta.TypeVar('RequestT', bound='Request')
OptionT = ta.TypeVar('OptionT', bound='Option')
NewT = ta.TypeVar('NewT')
ResponseT = ta.TypeVar('ResponseT', bound='Response')


##


class FinishReason(enum.Enum):
    STOP = enum.auto()
    LENGTH = enum.auto()
    TOOL_EXEC = enum.auto()
    CONTENT_FILTER = enum.auto()
    OTHER = enum.auto()


@dc.dataclass(frozen=True)
class TokenUsage(lang.Final):
    input: int
    output: int
    total: int


##


class RequestOption(Option, lang.Abstract):
    pass


##


class RequestContextItem(lang.Abstract):
    pass


RequestContext: ta.TypeAlias = col.TypeMap[RequestContextItem]

EMPTY_REQUEST_CONTEXT: RequestContext = col.TypeMap()


##


@dc.dataclass(frozen=True, kw_only=True)
class Request(lang.Abstract, ta.Generic[T, OptionT, NewT]):
    v: T

    options: Options[OptionT] = dc.xfield(Options(), repr_fn=dc.truthy_repr)
    context: RequestContext = dc.field(default=EMPTY_REQUEST_CONTEXT)

    @classmethod
    def new(
            cls,
            v: NewT,
            *options: OptionT,
            **kwargs: ta.Any,
    ) -> ta.Self:
        return cls(
            v=v,  # type: ignore
            options=Options(*options),
            **kwargs,
        )


@dc.dataclass(frozen=True, kw_only=True)
class Response(lang.Abstract, ta.Generic[T]):
    v: T

    usage: TokenUsage | None = dc.xfield(None, repr_fn=dc.opt_repr)
    reason: FinishReason | None = dc.xfield(None, repr_fn=dc.opt_repr)


class Model(lang.Abstract, ta.Generic[RequestT, OptionT, NewT, ResponseT]):
    request_cls: type[Request]
    option_cls_set: frozenset[type[Option]]
    new_request_cls: ta.Any
    response_cls: type[Response]

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        if lang.is_abstract_class(cls):
            return

        model_bases = [
            rb
            for b in rfl.get_orig_bases(cls)
            if isinstance(rb := rfl.type_(b), rfl.Generic)
            and rb.cls is Model
        ]
        if not model_bases:
            return

        model_base = check.single(model_bases)

        present_attr_ct = lang.ilen(
            a for a in (
                'request_cls',
                'option_cls_set',
                'new_request_cls',
                'response_cls',
            ) if hasattr(cls, a)
        )
        if present_attr_ct:
            if present_attr_ct != 4:
                raise AttributeError('Must set all model attrs if any set')
            return

        request_ann, option_ann, new_request_ann, response_ann = model_base.args

        request_cls: type[Request] = check.issubclass(check.isinstance(request_ann, type), Request)  # noqa
        response_cls: type[Response] = check.issubclass(check.isinstance(response_ann, type), Response)  # noqa
        new_request_cls: ta.Any = new_request_ann

        option_cls_set: frozenset[type[Option]]
        if isinstance(option_ann, rfl.Union):
            option_cls_set = frozenset(check.issubclass(check.isinstance(a, type), Option) for a in option_ann.args)  # noqa
        else:
            option_cls_set = frozenset([check.issubclass(check.isinstance(option_ann, type), Option)])  # noqa

        cls.request_cls = request_cls
        cls.option_cls_set = option_cls_set
        cls.new_request_cls = new_request_cls
        cls.response_cls = response_cls

    @abc.abstractmethod
    def invoke(self, request: RequestT) -> ResponseT:
        raise NotImplementedError

    @ta.final
    def invoke_new(
        self,
        v: NewT,
        *options: OptionT,
        **kwargs: ta.Any,
    ) -> ResponseT:
        request = self.request_cls.new(
            v,
            *options,
            **kwargs,
        )
        return self.invoke(ta.cast(RequestT, request))

    def __call__(
            self,
            v: NewT,
            *options: OptionT,
            **kwargs: ta.Any,
    ) -> ResponseT:
        return self.invoke_new(v, *options, **kwargs)
