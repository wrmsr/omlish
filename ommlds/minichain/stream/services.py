import contextlib
import typing as ta

from omlish import check
from omlish import lang
from omlish import typedvalues as tv

from ..resources import ResourceManaged
from ..resources import Resources
from ..resources import ResourcesOption
from ..services import Response
from ..types import Option
from ..types import Output


V = ta.TypeVar('V')
OutputT = ta.TypeVar('OutputT', bound=Output)
StreamOutputT = ta.TypeVar('StreamOutputT', bound=Output)


##


class StreamOption(Option, lang.Abstract):
    pass


StreamOptions: ta.TypeAlias = StreamOption | ResourcesOption


##


class ResponseGenerator(ta.AsyncGenerator[V, OutputT], lang.Final, ta.Generic[V, OutputT]):
    def __init__(self, agr: lang.AsyncGeneratorWithReturn[V, None, ta.Sequence[OutputT] | None]) -> None:
        super().__init__()

        self._agr = agr
        self._is_done = False

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}<{self._agr!r}>'

    _outputs: tv.TypedValues[OutputT]

    @property
    def is_done(self) -> bool:
        return self._is_done

    @property
    def outputs(self) -> tv.TypedValues[OutputT]:
        return self._outputs

    async def asend(self, value) -> V:
        try:
            return await self._agr.asend(value)
        except StopAsyncIteration:
            self._is_done = True
            if (v := self._agr.value.must()) is not None:
                self._outputs = tv.TypedValues(*check.isinstance(v, ta.Sequence))
            else:
                self._outputs = tv.TypedValues()
            raise

    async def athrow(self, typ, val=None, tb=None):
        return await self._agr.athrow(typ, val)

    async def aclose(self):
        await self._agr.aclose()


StreamResponse: ta.TypeAlias = Response[
    ResourceManaged[
        ResponseGenerator[
            V,
            OutputT,
        ],
    ],
    StreamOutputT,
]


async def new_stream_response(
        rs: Resources,
        agr: lang.AsyncGeneratorWithReturn[V, None, ta.Sequence[OutputT] | None],
        outputs: ta.Sequence[StreamOutputT] | None = None,
) -> StreamResponse[V, OutputT, StreamOutputT]:
    return StreamResponse(
        rs.new_managed(
            ResponseGenerator(
                await rs.enter_async_context(
                    contextlib.aclosing(
                        agr,
                    ),
                ),
            ),
        ),
        outputs or [],
    )
