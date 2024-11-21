"""
self._logging.log_error(self._logging_context, 'code %d, message %s', code, message)
"""
import abc
import dataclasses as dc
import datetime
import http
import itertools
import sys
import typing as ta


##


class HttpLogging(abc.ABC):
    @dc.dataclass(frozen=True, kw_only=True)
    class Context:
        client: str

    @abc.abstractmethod
    def log_message(
            self,
            ctx: Context,
            fmt: str,
            *args: ta.Any,
    ) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def log_request(
            self,
            ctx: Context,
            request_line: str,
            code: int | http.HTTPStatus | str = '-',
            size: int | str = '-',
    ) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def log_error(
            self,
            ctx: Context,
            fmt: str,
            *args: ta.Any,
    ) -> None:
        raise NotImplementedError


##



class DefaultHttpLogging(HttpLogging):
    def log_request(
            self,
            ctx: HttpLogging.Context,
            request_line: str,
            code: int | http.HTTPStatus | str = '-',
            size: int | str = '-',
    ) -> None:
        if isinstance(code, http.HTTPStatus):
            code = code.value

        self.log_message(
            ctx,
            '"%s" %s %s',
            request_line,
            str(code),
            str(size),
        )

    def log_error(
            self,
            ctx: HttpLogging.Context,
            fmt: str,
            *args: ta.Any,
    ) -> None:
        self.log_message(
            ctx,
            fmt,
            *args,
        )

    #

    # https://en.wikipedia.org/wiki/List_of_Unicode_characters#Control_codes
    _CONTROL_CHAR_TABLE = str.maketrans({
        c: fr'\x{c:02x}'
        for c in itertools.chain(range(0x20), range(0x7f, 0xa0))
    })

    _CONTROL_CHAR_TABLE[ord('\\')] = r'\\'

    def log_message(
            self,
            ctx: HttpLogging.Context,
            fmt: str,
            *args: ta.Any,
    ) -> None:
        message = fmt % args

        sys.stderr.write(
            '%s - - [%s] %s\n' % (  # noqa
                ctx.client,
                datetime.datetime.now().ctime(),  # noqa
                message.translate(self._CONTROL_CHAR_TABLE),
            ),
        )
