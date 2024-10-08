import abc
import enum
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import reflect as rfl

from .options import Option
from .options import Options


T = ta.TypeVar('T')
U = ta.TypeVar('U')
RequestT = ta.TypeVar('RequestT', bound='Request')
ResponseT = ta.TypeVar('ResponseT', bound='Response')
OptionT = ta.TypeVar('OptionT', bound='Option')


##


class FinishReason(enum.Enum):
    STOP = enum.auto()
    LENGTH = enum.auto()
    TOOL_EXECUTION = enum.auto()
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


@dc.dataclass(frozen=True, kw_only=True)
class Request(lang.Abstract, ta.Generic[T, OptionT]):
    v: T

    options: Options[OptionT] = Options()

    @classmethod
    def new(
            cls,
            v: T,
            *options: OptionT,
            **kwargs: ta.Any,
    ) -> ta.Self:
        return cls(
            v=v,
            options=Options(*options),
            **kwargs,
        )


@dc.dataclass(frozen=True, kw_only=True)
class Response(lang.Abstract, ta.Generic[T]):
    v: T

    usage: TokenUsage | None = None
    reason: FinishReason | None = None


class Model(lang.Abstract, ta.Generic[RequestT, OptionT, ResponseT]):
    request_cls: type[Request]
    option_cls_set: frozenset[type[Option]]
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

        present_attr_ct = lang.ilen(a for a in ('request_cls', 'option_cls_set', 'response_cls') if hasattr(cls, a))
        if present_attr_ct:
            if present_attr_ct != 3:
                raise AttributeError('Must set all model attrs if any set')
            return

        request_ann, option_ann, response_ann = model_base.args

        request_cls: type[Request] = check.issubclass(check.isinstance(request_ann, type), Request)  # noqa
        response_cls: type[Response] = check.issubclass(check.isinstance(response_ann, type), Response)  # noqa

        option_cls_set: frozenset[type[Option]]
        if isinstance(option_ann, rfl.Union):
            option_cls_set = frozenset(check.issubclass(check.isinstance(a, type), Option) for a in option_ann.args)  # noqa
        else:
            option_cls_set = frozenset([check.issubclass(check.isinstance(option_ann, type), Option)])  # noqa

        cls.request_cls = request_cls
        cls.option_cls_set = option_cls_set
        cls.response_cls = response_cls

    @abc.abstractmethod
    def invoke(self, request: RequestT) -> ResponseT:
        raise NotImplementedError

    @ta.final
    def invoke_new(
        self,
        v: T,
        *options: OptionT,
        **kwargs: ta.Any,
    ) -> ResponseT:
        request = self.request_cls.new(
            v,
            *options,
            **kwargs,
        )
        return self.invoke(ta.cast(RequestT, request))

    __call__ = invoke_new
