import collections.abc
import contextlib
import logging
import sys
import traceback
import types
import typing as ta

from . import consts
from .. import check
from .. import json
from .types import App
from .types import AppLike
from .types import BadRequestException
from .types import BadRequestExceptionT
from .types import Environ
from .types import StartResponse


log = logging.getLogger(__name__)


WrapperAppT = ta.TypeVar('WrapperAppT', bound='WrapperApp')


class WrapperApp(App):

    def __init__(self, app: AppLike, **kwargs) -> None:
        super().__init__(**kwargs)

        self._app = app

    @property
    def app(self) -> AppLike:
        return self._app

    def __enter__(self: WrapperAppT) -> WrapperAppT:
        if hasattr(self._app, '__enter__'):
            self._app.__enter__()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> ta.Any:
        if hasattr(self._app, '__exit__'):
            return self._app.__exit__(exc_type, exc_val, exc_tb)
        else:
            return None

    def __call__(self, environ: Environ, start_response: StartResponse) -> ta.Iterable[bytes]:
        return self._app(environ, start_response)


def read_input(environ: Environ) -> bytes:
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except ValueError:
        request_body_size = 0

    return environ['wsgi.input'].read(request_body_size)


class SimpleDictApp(App):

    class _BadRequestHandledException(Exception):
        pass

    Target = ta.Callable[[ta.Optional[ta.Dict[str, ta.Any]]], ta.Dict[str, ta.Any]]

    def __init__(
            self,
            target: Target,
            encode: ta.Callable[[ta.Any], ta.Any],
            decode: ta.Callable[[ta.Any], ta.Any],
            content_type: str,
            *,
            stream: bool = False,
            stream_separator: bytes = b'\n',
            stream_terminator: bytes = b'\0',
            handle_bad_requests: bool = False,
            on_bad_request: ta.Callable[[ta.Type[BadRequestExceptionT], BadRequestExceptionT, types.TracebackType], None] = None,  # noqa
            **kwargs
    ) -> None:
        super().__init__(**kwargs)

        self._target = check.callable(target)
        self._encode = check.callable(encode)
        self._decode = check.callable(decode)
        self._content_type = check.isinstance(content_type, str)

        self._stream = stream
        self._stream_separator = stream_separator
        self._stream_terminator = stream_terminator

        self._handle_bad_requests = handle_bad_requests
        self._on_bad_request = on_bad_request

    def __call__(self, environ: Environ, start_response: StartResponse) -> ta.Iterable[bytes]:
        request_body = read_input(environ)

        if request_body:
            input = self._decode(request_body)
        else:
            input = None

        @contextlib.contextmanager
        def bad_request_manager():
            if not self._handle_bad_requests:
                yield
                return

            try:
                yield
            except BadRequestException:
                exc_info = sys.exc_info()
                if self._on_bad_request is not None:
                    self._on_bad_request(*exc_info)
                write = start_response(consts.STATUS_BAD_REQUEST, [consts.CONTENT_TEXT], exc_info=exc_info)
                write('\n'.join(traceback.TracebackException(*exc_info).format()).encode('utf-8'))
                raise self._BadRequestHandledException

        try:
            with bad_request_manager():
                output = self._target(input)
        except self._BadRequestHandledException:
            return []

        start_response(consts.STATUS_OK, [(consts.CONTENT_TYPE, self._content_type)])

        if output is None:
            return []

        elif isinstance(output, collections.abc.Iterator):
            if not self._stream:
                raise TypeError(output)

            def inner():
                try:
                    with bad_request_manager():
                        for item in output:
                            yield self._encode(item)
                            yield self._stream_separator
                        yield self._stream_terminator
                except self._BadRequestHandledException:
                    pass

            return inner()

        else:
            return [self._encode(output)]


def simple_json_app(target: SimpleDictApp.Target) -> App:
    return SimpleDictApp(
        target,
        lambda output: json.dumps(output).encode('utf-8'),
        lambda request_body: json.loads(request_body.decode('utf-8')),
        consts.CONTENT_JSON,
    )
