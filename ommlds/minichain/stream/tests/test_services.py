from ...resources import UseResources
from ...services import Request
from ...types import Output
from ..services import StreamOptions
from ..services import StreamResponse
from ..services import new_stream_response


class FooStreamService:
    def invoke(self, request: Request[str, StreamOptions]) -> StreamResponse[str, Output, Output]:
        with UseResources.or_new(request.options) as rs:
            def yield_vs():
                for c in request.v:
                    yield c + '!'
            return new_stream_response(rs, yield_vs())


def test_foo_stream_service():
    with FooStreamService().invoke(Request('hi there!')).v as it:
        lst = list(it)
    assert lst == [c + '!' for c in 'hi there!']
