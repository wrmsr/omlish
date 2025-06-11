import typing as ta

from omlish import check
from omlish import lang
from omlish import typedvalues as tv

from .resources import ResourceManaged
from .services import Response
from .services import ResponseOutput


V = ta.TypeVar('V')
ResponseOutputT = ta.TypeVar('ResponseOutputT', bound=ResponseOutput)
StreamResponseOutputT = ta.TypeVar('StreamResponseOutputT', bound=ResponseOutput)


##


class ResponseGenerator(lang.Final, ta.Generic[V, ResponseOutputT]):
    def __init__(self, g: ta.Generator[V, None, ta.Sequence[ResponseOutputT] | None]) -> None:
        super().__init__()

        self._g = g
        self._is_done = False

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}<{self._g!r}>'

    _outputs: tv.TypedValues[ResponseOutputT]

    @property
    def is_done(self) -> bool:
        return self._is_done

    @property
    def outputs(self) -> tv.TypedValues[ResponseOutputT]:
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
            ResponseOutputT,
        ],
    ],
    StreamResponseOutputT,
]
