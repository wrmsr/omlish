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


class ResponseGenerator(lang.Final, ta.Generic[V, OutputT]):
    def __init__(self, g: ta.Generator[V, None, ta.Sequence[OutputT] | None]) -> None:
        super().__init__()

        self._g = g
        self._is_done = False

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}<{self._g!r}>'

    _outputs: tv.TypedValues[OutputT]

    @property
    def is_done(self) -> bool:
        return self._is_done

    @property
    def outputs(self) -> tv.TypedValues[OutputT]:
        return self._outputs

    def __iter__(self) -> ta.Iterator[V]:
        return self

    def __next__(self) -> V:
        try:
            return next(self._g)
        except StopIteration as e:
            self._is_done = True
            if e.value is not None:
                self._outputs = tv.TypedValues(*check.isinstance(e.value, ta.Sequence))
            else:
                self._outputs = tv.TypedValues()
            raise


StreamResponse: ta.TypeAlias = Response[
    ResourceManaged[
        ResponseGenerator[
            V,
            OutputT,
        ],
    ],
    StreamOutputT,
]


def new_stream_response(
        rs: Resources,
        g: ta.Generator[V, None, ta.Sequence[OutputT] | None],
        outputs: ta.Sequence[StreamOutputT] | None = None,
) -> StreamResponse[V, OutputT, StreamOutputT]:
    return StreamResponse(
        rs.new_managed(
            ResponseGenerator(
                rs.enter_context(
                    contextlib.closing(
                        g,
                    ),
                ),
            ),
        ),
        outputs or [],
    )
