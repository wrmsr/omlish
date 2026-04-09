# ruff: noqa: UP006 UP007 UP037 UP043 UP045
# @omlish-lite
import dataclasses as dc
import html
import http
import textwrap
import typing as ta

from .handlers import SimpleHttpHandlerResponse


##


@dc.dataclass(frozen=True)
class SimpleHttpHandlerError:
    status: ta.Union[http.HTTPStatus, int]
    message: str
    explain: str

    method: ta.Optional[str] = None

    #

    _STATUS_RESPONSES: ta.ClassVar[ta.Mapping[int, ta.Tuple[str, str]]] = {
        v: (v.phrase, v.description)
        for v in http.HTTPStatus.__members__.values()
    }

    @classmethod
    def build(
            cls,
            status: ta.Union[http.HTTPStatus, int],
            message: ta.Optional[str] = None,
            explain: ta.Optional[str] = None,
            *,
            method: ta.Optional[str] = None,
    ) -> 'SimpleHttpHandlerError':
        try:
            short_msg, long_msg = cls._STATUS_RESPONSES[status]
        except KeyError:
            short_msg, long_msg = '???', '???'
        if message is None:
            message = short_msg
        if explain is None:
            explain = long_msg

        return cls(
            status=status,
            message=message,
            explain=explain,

            method=method,
        )

    #

    _DEFAULT_ERROR_MESSAGE: ta.ClassVar[str] = textwrap.dedent(
        """\
            <!DOCTYPE HTML>
            <html lang="en">
                <head>
                    <meta charset="utf-8">
                    <title>Error response</title>
                </head>
                <body>
                    <h1>Error response</h1>
                    <p>Error code: %(code)d</p>
                    <p>Message: %(message)s.</p>
                    <p>Error code explanation: %(code)s - %(explain)s.</p>
                </body>
            </html>
        """,
    )

    _DEFAULT_ERROR_CONTENT_TYPE: ta.ClassVar[str] = 'text/html;charset=utf-8'

    def build_response(
            self,
            message: ta.Optional[str] = None,
            *,
            content_type: ta.Optional[str] = None,
    ) -> SimpleHttpHandlerResponse:
        if message is None:
            message = self._DEFAULT_ERROR_MESSAGE
        if content_type is None:
            content_type = self._DEFAULT_ERROR_CONTENT_TYPE

        headers: ta.List[ta.Tuple[str, str]] = []

        # Message body is omitted for cases described in:
        #  - RFC7230: 3.3. 1xx, 204(No Content), 304(Not Modified)
        #  - RFC7231: 6.3.6. 205(Reset Content)
        data: ta.Optional[bytes] = None
        if (
            self.status >= http.HTTPStatus.OK and
            self.status not in (
                http.HTTPStatus.NO_CONTENT,
                http.HTTPStatus.RESET_CONTENT,
                http.HTTPStatus.NOT_MODIFIED,
            )
        ):
            # HTML encode to prevent Cross Site Scripting attacks (see bug #1100201)
            content = message.format(
                status=self.status,
                message=html.escape(self.message, quote=False),
                explain=html.escape(self.explain, quote=False),
            )
            body = content.encode('UTF-8', 'replace')

            headers.extend([
                ('Content-Type', content_type),
                ('Content-Length', str(len(body))),
            ])

            if self.method != 'HEAD' and body:
                data = body

        return SimpleHttpHandlerResponse(
            status=self.status,
            headers=dict(headers),
            data=data,
            close_connection=True,
        )
