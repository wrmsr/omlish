import typing as ta

from omlish import lang

from .models import Model
from .models import Option
from .models import Request
from .models import Response


RequestT = ta.TypeVar('RequestT', bound='Request')
ResponseT = ta.TypeVar('ResponseT', bound='Response')
NewRequestT = ta.TypeVar('NewRequestT')
OptionT = ta.TypeVar('OptionT', bound='Option')


class WrapperModel(Model[RequestT, OptionT, NewRequestT, ResponseT], lang.Abstract):
    def __init__(self, underlying: Model) -> None:
        super().__init__()
        self._underlying = underlying

    @property
    def underlying(self) -> Model[RequestT, OptionT, NewRequestT, ResponseT]:
        return self._underlying

    @property
    def request_cls(self) -> type[Request]:  # type: ignore[override]
        return self._underlying.request_cls

    @property
    def option_cls_set(self) -> frozenset[type[Option]]:  # type: ignore[override]
        return self._underlying.option_cls_set

    @property
    def new_request_cls(self) -> ta.Any:
        return self._underlying.new_request_cls

    @property
    def response_cls(self) -> type[Response]:  # type: ignore[override]
        return self._underlying.response_cls

    def invoke(self, request: RequestT) -> ResponseT:
        return self._underlying.invoke(request)
