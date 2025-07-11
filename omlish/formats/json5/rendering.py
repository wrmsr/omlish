import io
import re
import typing as ta

from ... import check
from ... import lang
from ..json import Scalar
from ..json.literals import ESCAPE_MAP
from ..json.literals import encode_string
from ..json.rendering import JsonRenderer
from ..json.rendering import JsonRendererOut


##


MULTILINE_STRINGS_ENDL = '\\\n'
MULTILINE_STRINGS_LQ = '"' + MULTILINE_STRINGS_ENDL
MULTILINE_STRINGS_RQ = MULTILINE_STRINGS_ENDL + '"'
MULTILINE_STRINGS_NL = '\\n' + MULTILINE_STRINGS_ENDL

MULTILINE_STRINGS_ESCAPE_MAP = {
    **ESCAPE_MAP,
    '\n': MULTILINE_STRINGS_NL,
}

SOFTWRAP_WS_PAT = re.compile(r'\s+')


class Json5Renderer(JsonRenderer):
    def __init__(
            self,
            out: JsonRendererOut,
            *,
            multiline_strings: bool = False,
            softwrap_length: int | None = None,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(out, **kwargs)

        self._multiline_strings = multiline_strings
        self._softwrap_length = softwrap_length

    def _softwrap_string_chunks(self, chunks: list[str]) -> str:
        multiline_strings = self._multiline_strings
        softwrap_len = check.not_none(self._softwrap_length)

        out = io.StringIO()
        out.write(MULTILINE_STRINGS_LQ)

        l = 0

        def write(s: str) -> None:
            nonlocal l
            if l >= (softwrap_len - (sl := len(s))):
                out.write(MULTILINE_STRINGS_ENDL)
                l = 0

            out.write(s)
            l += sl

        for c in chunks:
            if not c:
                continue

            if c == '\\n' and multiline_strings:
                if (softwrap_len - l) > 2:
                    out.write('\\n\\\n')
                else:
                    out.write('\\\n\\n\\\n')
                l = 0
                continue

            it: ta.Iterable[str | re.Match]
            if c[0] == '\\':
                it = [c]
            else:
                it = lang.iter_pat(SOFTWRAP_WS_PAT, c)

            for x in it:
                if isinstance(x, re.Match):
                    ws = x.group(0)
                    r = softwrap_len - l
                    if len(ws) > r:
                        write(ws[:r])
                        p = r
                        while p < len(ws):
                            write(ws[p:(np := (p + softwrap_len))])
                            p = np

                    else:
                        write(ws)

                else:
                    write(x)

        out.write(MULTILINE_STRINGS_RQ)
        return out.getvalue()

    def _format_string(self, s: str, state: JsonRenderer.State | None = None) -> str:
        num_nls = s.count('\n')
        is_multiline = self._multiline_strings and num_nls

        if (softwrap_len := self._softwrap_length) is not None:
            def process_chunks(chunks: list[str]) -> list[str]:
                naive_len = sum(map(len, chunks))

                if is_multiline:
                    if naive_len < (
                        softwrap_len -
                        len(MULTILINE_STRINGS_LQ) -
                        (num_nls * (len(MULTILINE_STRINGS_NL) - 1)) -
                        len(MULTILINE_STRINGS_RQ)
                    ):
                        return [
                            MULTILINE_STRINGS_LQ,
                            *[
                                MULTILINE_STRINGS_NL if c == '\\n' else c
                                for c in chunks
                            ],
                            MULTILINE_STRINGS_RQ,
                        ]

                elif naive_len < softwrap_len:
                    return [
                        '"',
                        *chunks,
                        '"',
                    ]

                return [self._softwrap_string_chunks(chunks)]

            return encode_string(
                s,
                q='',
                ensure_ascii=self._ensure_ascii,
                process_chunks=process_chunks,
            )

        if is_multiline:
            return encode_string(
                s,
                lq=MULTILINE_STRINGS_LQ,
                rq=MULTILINE_STRINGS_RQ,
                escape_map=MULTILINE_STRINGS_ESCAPE_MAP,
                ensure_ascii=self._ensure_ascii,
            )

        return super()._format_scalar(s, state=state)

    def _format_scalar(self, o: Scalar, state: JsonRenderer.State | None = None) -> str:
        if isinstance(o, str):
            return self._format_string(o)

        else:
            return super()._format_scalar(o, state=state)
