import typing as ta

from omlish import check
from omlish import lang

from ..types import Option
from ..types import Output
from .requests import Request
from .responses import Response
from .services import Service
from .stream import StreamOptions
from .stream import StreamResponse


#

P = ta.ParamSpec('P')

#

WrappedRequestV = ta.TypeVar('WrappedRequestV')
WrappedOptionT = ta.TypeVar('WrappedOptionT', bound=Option)

WrappedResponseV = ta.TypeVar('WrappedResponseV')
WrappedOutputT = ta.TypeVar('WrappedOutputT', bound=Output)

WrappedStreamOutputT = ta.TypeVar('WrappedStreamOutputT', bound=Output)

#

WrappedRequest: ta.TypeAlias = Request[
    WrappedRequestV,
    WrappedOptionT,
]

WrappedResponse: ta.TypeAlias = Response[
    WrappedResponseV,
    WrappedOutputT,
]

WrappedService: ta.TypeAlias = Service[
    WrappedRequest,
    WrappedResponse,
]

#

WrappedStreamOptions: ta.TypeAlias = WrappedOptionT | StreamOptions

WrappedStreamRequest: ta.TypeAlias = Request[
    WrappedRequestV,
    WrappedStreamOptions,
]

WrappedStreamResponse: ta.TypeAlias = StreamResponse[
    WrappedResponseV,
    WrappedOutputT,
    WrappedStreamOutputT,
]

WrappedStreamService: ta.TypeAlias = Service[
    WrappedStreamRequest,
    WrappedStreamResponse,
]


##


class WrapperService(
    lang.AsyncExitStacked,
    lang.Abstract,
    ta.Generic[
        WrappedRequestV,
        WrappedOptionT,
        WrappedResponseV,
        WrappedOutputT,
    ],
):
    def __init__(
            self,
            child: WrappedService,
    ) -> None:
        super().__init__()

        self._child = child

    async def _enter_child_context(self) -> None:
        if isinstance(svc := self._child, ta.AsyncContextManager):
            await self._enter_async_context(svc)

    async def _async_enter_contexts(self) -> None:
        await super()._async_enter_contexts()
        await self._enter_child_context()


class MultiWrapperService(
    lang.AsyncExitStacked,
    lang.Abstract,
    ta.Generic[
        WrappedRequestV,
        WrappedOptionT,
        WrappedResponseV,
        WrappedOutputT,
    ],
):
    def __init__(
            self,
            children: ta.Sequence[WrappedService],
    ) -> None:
        super().__init__()

        self._children = tuple(check.not_empty(children))

    async def _enter_children_contexts(self) -> None:
        for svc in self._children:
            if isinstance(svc, ta.AsyncContextManager):
                await self._enter_async_context(svc)

    async def _async_enter_contexts(self) -> None:
        await super()._async_enter_contexts()
        await self._enter_children_contexts()


#


class WrapperStreamService(
    lang.AsyncExitStacked,
    lang.Abstract,
    ta.Generic[
        WrappedRequestV,
        WrappedOptionT,
        WrappedResponseV,
        WrappedOutputT,
        WrappedStreamOutputT,
    ],
):
    def __init__(
            self,
            child: WrappedStreamService,
    ) -> None:
        super().__init__()

        self._child = child

    async def _enter_child_context(self) -> None:
        if isinstance(svc := self._child, ta.AsyncContextManager):
            await self._enter_async_context(svc)

    async def _async_enter_contexts(self) -> None:
        await super()._async_enter_contexts()
        await self._enter_child_context()


class MultiWrapperStreamService(
    lang.AsyncExitStacked,
    lang.Abstract,
    ta.Generic[
        WrappedRequestV,
        WrappedOptionT,
        WrappedResponseV,
        WrappedOutputT,
        WrappedStreamOutputT,
    ],
):
    def __init__(
            self,
            children: ta.Sequence[WrappedStreamService],
    ) -> None:
        super().__init__()

        self._children = tuple(children)

    async def _enter_children_contexts(self) -> None:
        for svc in self._children:
            if isinstance(svc, ta.AsyncContextManager):
                await self._enter_async_context(svc)

    async def _async_enter_contexts(self) -> None:
        await super()._async_enter_contexts()
        await self._enter_children_contexts()


#


def wrap_service(
        wrapped: WrappedService,
        wrapper: ta.Callable[
            ta.Concatenate[
                WrappedService,
                P,
            ],
            WrapperService[
                WrappedRequestV,
                WrappedOptionT,
                WrappedResponseV,
                WrappedOutputT,
            ],
        ],
        *args: P.args,
        **kwargs: P.kwargs,
) -> WrappedService:
    return ta.cast(ta.Any, wrapper(wrapped, *args, **kwargs))
